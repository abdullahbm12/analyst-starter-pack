import os
import sqlite3
import pandas as pd

DB_PATH = "data/gm.db"
DATA_DIR = "data"

TABLE_FILES = {
    "users": "users.csv",
    "sessions": "sessions.csv",
    "quotes": "quotes.csv",
    "bookings": "bookings.csv",
    "fulfillment": "fulfillment.csv",
    "finance": "finance.csv",
}

# Rebuild DB from scratch each time (simple + repeatable)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

con = sqlite3.connect(DB_PATH)

# Load CSVs into tables
for table, fname in TABLE_FILES.items():
    path = os.path.join(DATA_DIR, fname)
    df = pd.read_csv(path)

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    df.to_sql(table, con, index=False, if_exists="replace")
    print(f"Loaded {table}: {len(df):,} rows")

# Add a few helpful indexes (makes queries faster)
idx_sql = [
    "CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_quotes_session ON quotes(session_id);",
    "CREATE INDEX IF NOT EXISTS idx_bookings_user ON bookings(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_bookings_session ON bookings(session_id);",
    "CREATE INDEX IF NOT EXISTS idx_finance_booking ON finance(booking_id);",
]
cur = con.cursor()
for s in idx_sql:
    cur.execute(s)
con.commit()

# Quick sanity checks
checks = [
    ("users", "SELECT COUNT(*) FROM users;"),
    ("sessions", "SELECT COUNT(*) FROM sessions;"),
    ("quotes", "SELECT COUNT(*) FROM quotes;"),
    ("bookings", "SELECT COUNT(*) FROM bookings;"),
    ("fulfillment", "SELECT COUNT(*) FROM fulfillment;"),
    ("finance", "SELECT COUNT(*) FROM finance;"),
]
for name, q in checks:
    n = cur.execute(q).fetchone()[0]
    print(f"DB check {name}: {n:,}")

con.close()
print(f"Done. Created {DB_PATH}")
