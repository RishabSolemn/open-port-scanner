# models.py
import sqlite3
from pathlib import Path
import json
from datetime import datetime, timezone

DB_PATH = Path("scanner.db")

def _connect():
    con = sqlite3.connect(DB_PATH, timeout=5, isolation_level=None)
    # Autocommit mode (isolation_level=None) + WAL for better concurrency
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA synchronous=NORMAL;")
    return con

def init_db():
    with _connect() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS targets(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host TEXT NOT NULL,
            ports TEXT,             -- JSON list of ints or NULL => default ports
            email TEXT NOT NULL
        )""")
        con.execute("""
        CREATE TABLE IF NOT EXISTS results(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_id INTEGER NOT NULL,
            opened TEXT,            -- JSON list
            scanned_at TEXT NOT NULL,
            FOREIGN KEY(target_id) REFERENCES targets(id)
        )""")
        # Helpful index for results lookups (optional)
        con.execute("CREATE INDEX IF NOT EXISTS idx_results_target ON results(target_id);")

def add_target(host: str, ports, email: str):
    with _connect() as con:
        con.execute(
            "INSERT INTO targets(host, ports, email) VALUES(?,?,?)",
            (host, json.dumps(ports) if ports else None, email)
        )

def list_targets():
    with _connect() as con:
        cur = con.execute("SELECT id, host, ports, email FROM targets")
        return [
            {"id": r[0], "host": r[1],
             "ports": json.loads(r[2]) if r[2] else None,
             "email": r[3]}
            for r in cur.fetchall()
        ]

def save_result(target_id: int, opened):
    with _connect() as con:
        con.execute(
            "INSERT INTO results(target_id, opened, scanned_at) VALUES(?,?,?)",
            (target_id, json.dumps(opened), datetime.now(timezone.utc).isoformat())
        )
