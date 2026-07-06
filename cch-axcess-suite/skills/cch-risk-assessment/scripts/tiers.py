#!/usr/bin/env python3
"""Area-selection tier lookup for cch-risk-assessment.

Which audit-area boxes to check on AUD-100, by engagement type, under the
4-tier selection model. Prints only the requested slice.

Tiers (broadest -> narrowest inclusion):
  1 always   - auto-select, no test
  2 exists   - select if the item exists at all (any amount)
  3 material - group the TB, compare to tolerable; select if it clears
  4 prompt   - fallback / judgment call (see condition)

select_group = a mutually-exclusive set: pick exactly ONE member
(e.g. EBP_INVESTMENTS = 802A non-certified XOR 802B certified[default]).

Source of truth: data/seed/area_tier.csv (joined to areas.csv).
Usage:
    python tiers.py <AUDIT_TYPE> [--tier N] [--json]
    python tiers.py --types
AUDIT_TYPE in: ASB CNS EBP ALG NPO   (HOA deferred - rides ASB)
"""
import argparse, json, sys
from _db import get_db

TYPES = ["ASB", "CNS", "EBP", "ALG", "NPO"]
RULE = {"1": "always", "2": "exists", "3": "material", "4": "prompt"}


def main():
    p = argparse.ArgumentParser(description="cch-risk-assessment area-selection tiers")
    p.add_argument("audit_type", nargs="?")
    p.add_argument("--tier")
    p.add_argument("--json", action="store_true")
    p.add_argument("--types", action="store_true")
    a = p.parse_args()

    if a.types or not a.audit_type:
        print(" ".join(TYPES)); return
    at = a.audit_type.upper()
    if at == "HOA":
        print("HOA: deferred - rides Commercial/ASB; not yet tiered (firm has ~2)."); return
    if at not in TYPES:
        sys.exit(f"unknown audit type {at!r}; valid: {' '.join(TYPES)} (HOA deferred)")

    sql = ("SELECT t.binding_key,t.tier,t.rule,t.select_group,t.condition,t.note,"
           "a.plain_name,a.aud_form FROM area_tier t "
           "JOIN areas a ON a.audit_type=t.audit_type AND a.binding_key=t.binding_key "
           "WHERE t.audit_type=?")
    args = [at]
    if a.tier:
        sql += " AND t.tier=?"; args.append(str(a.tier))
    sql += " ORDER BY t.tier, t.select_group DESC, a.aud_form"

    con = get_db()
    rows = [dict(r) for r in con.execute(sql, args).fetchall()]
    con.close()

    if a.json:
        print(json.dumps(rows, indent=2)); return

    print(f"# {at} - area selection ({len(rows)} areas)")
    cur = None
    for r in rows:
        if r["tier"] != cur:
            cur = r["tier"]
            print(f"\n## Tier {cur} - {RULE.get(cur, '?')}")
        sg = f"  [{r['select_group']}: pick one]" if r["select_group"] else ""
        cond = f"  <{r['condition']}>" if r["condition"] else ""
        note = f"  -- {r['note']}" if r["note"] else ""
        print(f"{r['aud_form']:>9}  {r['binding_key']:<18} {r['plain_name']}{sg}{cond}{note}".rstrip())


if __name__ == "__main__":
    main()
