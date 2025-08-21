SCHEMA_DDL = """
-- DATABASE: rental_app

CREATE TABLE users (
  user_id INTEGER PRIMARY KEY,
  first_name VARCHAR,
  last_name VARCHAR,
  email VARCHAR UNIQUE,
  phone VARCHAR,
  role TEXT CHECK(role IN ('landlord','tenant','admin')),
  created_at TIMESTAMP
);

CREATE TABLE properties (
  property_id INTEGER PRIMARY KEY,
  landlord_id INTEGER,
  title VARCHAR,
  description TEXT,
  property_type TEXT CHECK(property_type IN ('apartment','house','studio','villa')),
  address VARCHAR,
  city VARCHAR,
  state VARCHAR,
  country VARCHAR,
  bedrooms INTEGER,
  bathrooms INTEGER,
  rent_price DECIMAL(12,2),
  status TEXT CHECK(status IN ('available','booked','inactive')),
  listed_at TIMESTAMP,
  FOREIGN KEY (landlord_id) REFERENCES users(user_id)
);

CREATE TABLE bookings (
  booking_id INTEGER PRIMARY KEY,
  property_id INTEGER,
  tenant_id INTEGER,
  start_date DATE,
  end_date DATE,
  status TEXT CHECK(status IN ('pending','confirmed','cancelled','completed')),
  created_at TIMESTAMP,
  FOREIGN KEY (property_id) REFERENCES properties(property_id),
  FOREIGN KEY (tenant_id) REFERENCES users(user_id)
);

CREATE TABLE payments (
  payment_id INTEGER PRIMARY KEY,
  booking_id INTEGER,
  tenant_id INTEGER,
  amount DECIMAL(12,2),
  payment_date DATE,
  status TEXT CHECK(status IN ('initiated','successful','failed','refunded')),
  method TEXT CHECK(method IN ('credit_card','debit_card','bank_transfer','upi','cash')),
  FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),
  FOREIGN KEY (tenant_id) REFERENCES users(user_id)
);

CREATE TABLE reviews (
  review_id INTEGER PRIMARY KEY,
  property_id INTEGER,
  tenant_id INTEGER,
  rating INTEGER,
  comment TEXT,
  created_at TIMESTAMP,
  FOREIGN KEY (property_id) REFERENCES properties(property_id),
  FOREIGN KEY (tenant_id) REFERENCES users(user_id)
);

CREATE TABLE property_photos (
  photo_id INTEGER PRIMARY KEY,
  property_id INTEGER,
  photo_url VARCHAR,
  uploaded_at TIMESTAMP,
  FOREIGN KEY (property_id) REFERENCES properties(property_id)
);

CREATE TABLE favorites (
  tenant_id INTEGER,
  property_id INTEGER,
  added_at TIMESTAMP,
  PRIMARY KEY (tenant_id, property_id),
  FOREIGN KEY (tenant_id) REFERENCES users(user_id),
  FOREIGN KEY (property_id) REFERENCES properties(property_id)
);
"""

# Few-shot exemplars to improve robustness for Text-to-SQL in SQLite.
FEWSHOTS = [
  {
    "nl": "Who are the top 10 tenants by total rent paid?",
    "sql": "SELECT u.user_id, u.first_name, u.last_name, SUM(p.amount) AS total_rent\n"
           "FROM payments p\n"
           "JOIN users u ON p.tenant_id = u.user_id\n"
           "WHERE p.status = 'successful'\n"
           "GROUP BY u.user_id\n"
           "ORDER BY total_rent DESC\n"
           "LIMIT 10"
  },
  {
    "nl": "List all currently available 2BHKs under $2500 in London.",
    "sql": "SELECT property_id, title, city, bedrooms, rent_price\n"
           "FROM properties\n"
           "WHERE status = 'available'\n"
           "  AND city = 'London'\n"
           "  AND bedrooms = 2\n"
           "  AND rent_price < 2500\n"
           "ORDER BY rent_price ASC"
  },
  {
    "nl": "What’s the average rating of apartments vs houses?",
    "sql": "SELECT p.property_type, ROUND(AVG(r.rating), 2) AS avg_rating\n"
           "FROM reviews r\n"
           "JOIN properties p ON r.property_id = p.property_id\n"
           "WHERE p.property_type IN ('apartment','house')\n"
           "GROUP BY p.property_type"
  },
  {
    "nl": "Which landlords generated the most revenue this year?",
    "sql": "SELECT u.user_id AS landlord_id, u.first_name, u.last_name, ROUND(SUM(p.amount), 2) AS revenue\n"
           "FROM payments p\n"
           "JOIN bookings b ON p.booking_id = b.booking_id\n"
           "JOIN properties pr ON b.property_id = pr.property_id\n"
           "JOIN users u ON pr.landlord_id = u.user_id\n"
           "WHERE p.status = 'successful'\n"
           "  AND strftime('%Y', p.payment_date) = strftime('%Y', 'now')\n"
           "GROUP BY u.user_id\n"
           "ORDER BY revenue DESC\n"
           "LIMIT 10"
  },
  {
    "nl": "What’s the occupancy rate of properties in Bradford last quarter?",
    "sql": "-- Occupancy rate = total booked property-days / total available property-days in last quarter.\n"
           "-- Approximation using bookings.status in ('confirmed','completed').\n"
           "WITH q AS (\n"
           "  SELECT\n"
           "    -- Compute last quarter start/end (approx via current date)\n"
           "    CASE\n"
           "      WHEN CAST(strftime('%m','now') AS INT) IN (1,2,3) THEN date(strftime('%Y','now') || '-10-01','-1 year')\n"
           "      WHEN CAST(strftime('%m','now') AS INT) IN (4,5,6) THEN strftime('%Y','now') || '-01-01'\n"
           "      WHEN CAST(strftime('%m','now') AS INT) IN (7,8,9) THEN strftime('%Y','now') || '-04-01'\n"
           "      ELSE strftime('%Y','now') || '-07-01'\n"
           "    END AS q_start,\n"
           "    CASE\n"
           "      WHEN CAST(strftime('%m','now') AS INT) IN (1,2,3) THEN date(strftime('%Y','now') || '-12-31','-1 year')\n"
           "      WHEN CAST(strftime('%m','now') AS INT) IN (4,5,6) THEN strftime('%Y','now') || '-03-31'\n"
           "      WHEN CAST(strftime('%m','now') AS INT) IN (7,8,9) THEN strftime('%Y','now') || '-06-30'\n"
           "      ELSE strftime('%Y','now') || '-09-30'\n"
           "    END AS q_end\n"
           "), props AS (\n"
           "  SELECT property_id\n"
           "  FROM properties\n"
           "  WHERE city = 'Bradford'\n"
           "), days AS (\n"
           "  SELECT p.property_id, CAST((julianday(q.q_end) - julianday(q.q_start) + 1) AS INT) AS total_days\n"
           "  FROM props p CROSS JOIN q\n"
           "), booked AS (\n"
           "  SELECT b.property_id,\n"
           "         MAX(0, CAST((julianday(MIN(q.q_end, b.end_date)) - julianday(MAX(q.q_start, b.start_date)) + 1) AS INT)) AS overlap_days\n"
           "  FROM bookings b CROSS JOIN q\n"
           "  WHERE b.property_id IN (SELECT property_id FROM props)\n"
           "    AND b.status IN ('confirmed','completed')\n"
           "    AND b.end_date >= (SELECT q_start FROM q)\n"
           "    AND b.start_date <= (SELECT q_end FROM q)\n"
           "  GROUP BY b.property_id, b.booking_id\n"
           "), agg AS (\n"
           "  SELECT property_id, SUM(CASE WHEN overlap_days < 0 THEN 0 ELSE overlap_days END) AS booked_days\n"
           "  FROM booked\n"
           "  GROUP BY property_id\n"
           ")\n"
           "SELECT\n"
           "  ROUND( (SUM(COALESCE(a.booked_days,0)) * 1.0) / (SUM(d.total_days) * 1.0), 4) AS occupancy_rate\n"
           "FROM days d\n"
           "LEFT JOIN agg a ON d.property_id = a.property_id"
  }
]

INSTRUCTIONS = """You are an expert Text-to-SQL generator for the following SQLite schema.
- Output **ONLY** JSON as: {"sql": "...", "confidence": 0.0, "notes": "short reasoning"}
- The SQL must be **SELECT-only** (no INSERT/UPDATE/DELETE/DDL).
- Use only tables/columns that exist in the provided schema.
- Prefer SQLite-compatible functions (e.g., strftime) and standard ANSI SQL.
- When ambiguous, choose a reasonable, simple interpretation.
- For revenue, use payments where status = 'successful'.
- For occupancy, consider bookings with status IN ('confirmed','completed').
- If the question is truly unanswerable from the schema, return {"sql": null, "confidence": 0.0, "notes": "unanswerable"}.

Map domain language to schema:
- "2BHK" → bedrooms = 2; "3BHK" → bedrooms = 3, etc.
- "available now/currently available" → properties.status = 'available'.
- "last quarter" means the previous fiscal quarter relative to now.
- Money is in 'rent_price' and 'payments.amount'.
- Tenants and landlords are both in 'users' (role field).

Return small, efficient queries and include a LIMIT if result could be large.
"""
