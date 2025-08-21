import os
import json
import re
from typing import Optional, Dict, Any

import google.generativeai as genai
from dotenv import load_dotenv

from prompts import SCHEMA_DDL, FEWSHOTS, INSTRUCTIONS

# Load environment variables
load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY not set. Please add it to your .env file.")

# Configure Gemini API
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

# Allowed and banned SQL elements
ALLOWED_TABLES = {
    'users', 'properties', 'bookings', 'payments',
    'reviews', 'property_photos', 'favorites'
}
BANNED_KEYWORDS = {
    'insert', 'update', 'delete', 'drop',
    'truncate', 'alter', 'create', 'attach', 'pragma'
}


def _json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extract the first JSON object from text."""
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _sanitize_sql(sql: str) -> str:
    """Remove unsafe elements and ensure single-statement SQL."""
    sql = sql.strip().strip(';')
    sql = sql.replace('`', '')

    # Prevent multi-statements
    if ';' in sql:
        sql = sql.split(';')[0]

    return sql


def _is_select_only(sql: str) -> bool:
    """Ensure only SELECT queries are allowed."""
    s = sql.strip().lower()
    if not s.startswith('select'):
        return False
    return all(kw not in s for kw in BANNED_KEYWORDS)


def _references_only_allowed_tables(sql: str) -> bool:
    """Check query only references whitelisted tables."""
    s = sql.lower()
    tables = re.findall(r"(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)", s)
    return all(t in ALLOWED_TABLES for t in tables)


def _ensure_limit(sql: str, default_limit: int = 200) -> str:
    """Ensure a LIMIT is present to prevent huge outputs."""
    if " limit " not in sql.lower():
        return f"{sql}\nLIMIT {default_limit}"
    return sql


def build_prompt(user_query: str) -> str:
    """Builds a rich prompt with schema, fewshots, and instructions."""
    examples = "\n\n".join(
        f"NL: {ex['nl']}\nSQL:\n{ex['sql']}" for ex in FEWSHOTS
    )
    return f"""{INSTRUCTIONS}

SCHEMA (SQLite DDL):
{SCHEMA_DDL}

Examples:
{examples}

User question:
{user_query}

Return ONLY JSON as specified.
"""


def nl_to_sql(user_query: str) -> Optional[Dict[str, Any]]:
    """Convert natural language query into a safe SQL statement."""
    prompt = build_prompt(user_query)
    try:
        resp = model.generate_content(prompt)
        txt = getattr(resp, "text", None)

        if not txt:
            return None

        data = _json_from_text(txt)
        if not data or "sql" not in data:
            return None

        sql = _sanitize_sql(data["sql"])
        if not _is_select_only(sql):
            return None
        if not _references_only_allowed_tables(sql):
            return None

        # Add LIMIT for safety
        data["sql"] = _ensure_limit(sql)
        return data

    except Exception as e:
        print(f"Error in nl_to_sql: {e}")
        return None
