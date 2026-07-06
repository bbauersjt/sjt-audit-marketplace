#!/usr/bin/env python3
"""Rebuild data/cch_ra.db in place from data/seed/*.csv and report row counts.

Run after hand-editing any seed CSV, then commit the rebuilt .db.
"""
from _db import build, get_db, TABLES

if __name__ == "__main__":
    path = build()
    con = get_db()
    for t in TABLES:
        n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"{t}: {n} rows")
    con.close()
    print(f"-> {path}")
