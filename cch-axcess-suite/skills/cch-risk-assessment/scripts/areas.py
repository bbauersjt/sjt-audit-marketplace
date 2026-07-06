#!/usr/bin/env python3
"""Area lookup dispatcher for cch-risk-assessment.

Prints only the requested slice so the model never reads the whole table.
Source of truth is data/seed/areas.csv; data/cch_ra.db is built by build_db.py.

Usage:
    python areas.py <AUDIT_TYPE> [--risk] [--balance] [--distinctive] [--json]
    python areas.py --types
    python areas.py <AUDIT_TYPE> --area CASH
AUDIT_TYPE in: ASB HOA CNS EBP ALG NPO
"""
import argparse, json, sys
from _db import get_db

TYPES = ["ASB", "HOA", "CNS", "EBP", "ALG", "NPO"]


def main():
    p = argparse.ArgumentParser(description="cch-risk-assessment area lookup")
    p.add_argument("audit_type", nargs="?")
    p.add_argument("--types", action="store_true")
    p.add_argument("--risk", action="store_true")
    p.add_argument("--balance", action="store_true")
    p.add_argument("--distinctive", action="store_true")
    p.add_argument("--area")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    if a.types or not a.audit_type:
        print(" ".join(TYPES)); return
    at = a.audit_type.upper()
    if at not in TYPES:
        sys.exit(f"unknown audit type {at!r}; valid: {' '.join(TYPES)}")

    sql = "SELECT binding_key,plain_name,aud_form,category,distinctive FROM areas WHERE audit_type=?"
    args = [at]
    if a.risk:        sql += " AND category='risk'"
    if a.balance:     sql += " AND category='balance'"
    if a.distinctive: sql += " AND distinctive='1'"
    if a.area:        sql += " AND binding_key=?"; args.append(a.area.upper())
    sql += " ORDER BY aud_form"

    con = get_db()
    rows = [dict(r) for r in con.execute(sql, args).fetchall()]
    con.close()

    if a.json:
        print(json.dumps(rows, indent=2)); return
    print(f"# {at} - {len(rows)} areas")
    for r in rows:
        flag = " *" if r["distinctive"] == "1" else ""
        tag = "[risk]" if r["category"] == "risk" else ""
        print(f"{r['aud_form']:>8}  {r['binding_key']:<20} {r['plain_name']}{flag} {tag}".rstrip())


if __name__ == "__main__":
    main()
