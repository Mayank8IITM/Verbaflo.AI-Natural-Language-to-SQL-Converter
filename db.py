# db.py
import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# Get database URL (default: SQLite file)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///rental_app.db")

# SQLAlchemy engine (lazy init)
_engine: Optional[Engine] = None

def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL, echo=False, future=True)
    return _engine

# Session for ORM usage
SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)

# Base class for ORM models
Base = declarative_base()

# Run raw SQL queries → returns DataFrame
def run_query(sql: str) -> pd.DataFrame:
    eng = get_engine()
    with eng.connect() as conn:
        df = pd.read_sql_query(text(sql), conn)
    return df
