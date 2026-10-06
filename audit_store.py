import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH=Path(__file__).resolve().parent.parent/"data"/"miyar_reviews.sqlite3"

def _conn():
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(DB_PATH)
    c.execute("""CREATE TABLE IF NOT EXISTS reviews(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      audit_id TEXT NOT NULL,
      action TEXT NOT NULL,
      created_at TEXT NOT NULL
    )""")
    return c

def save_review(audit_id,action):
    with _conn() as c:
        c.execute("INSERT INTO reviews(audit_id,action,created_at) VALUES(?,?,?)",(audit_id,action,datetime.now(timezone.utc).isoformat()))

def latest_review(audit_id):
    with _conn() as c:
        row=c.execute("SELECT action,created_at FROM reviews WHERE audit_id=? ORDER BY id DESC LIMIT 1",(audit_id,)).fetchone()
    return {"action":row[0],"created_at":row[1]} if row else None
