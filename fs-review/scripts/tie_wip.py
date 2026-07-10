"""Recompute a construction contracts-in-progress (WIP/job) schedule row by row.

Maps schedule columns by header keywords, then for every job recomputes each
percentage-of-completion relation that the present columns allow:

  total estimated cost   = costs to date + estimated cost to complete
  estimated gross profit = contract price - total estimated cost
  percent complete       = costs to date / total estimated cost
  revenues earned        = percent complete x contract price
  gross profit to date   = revenues earned - costs to date
  over/(under)billings   = billings to date - revenues earned

Also foots every column and reports the balance-sheet tie candidates: sum of
underbillings (costs and estimated earnings in excess of billings) and sum of
overbillings (billings in excess of costs and estimated earnings).

Recompute diffs <= $2 are reported as "rounding" (percent-complete rounding in the
source schedule commonly moves earned revenue by a dollar or two); anything larger is
FAIL. Column footings remain zero-tolerance.

Usage:
  python tie_wip.py statements.json [--table p012t1] [-o wip_report.json]
  (no --table: auto-detects schedules whose headers look like a WIP schedule)
  Column mapping is printed — VERIFY it against the schedule before trusting results.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fslib import fmt, load_json, looks_like_total, save_json

ROUNDING = 2.0  # $; recompute slack for percent-rounding artifacts

# column -> header keyword sets (any keyword matches, checked in order given)
COLMAP = {
    "contract_price": ["contract price", "contract amount", "total contract",
                       "contract revenues", "adjusted contract"],
    "costs_to_date": ["costs incurred", "cost incurred", "costs to date", "cost to date"],
    "est_cost_to_complete": ["cost to complete", "costs to complete", "estimated cost to",
                             "remaining cost"],
    "total_est_cost": ["total estimated cost", "estimated total cost", "total cost"],
    "est_gross_profit": ["estimated gross profit", "estimated earnings",
                         "gross profit at completion"],
    "pct_complete": ["percent complete", "% complete", "percentage of completion",
                     "percentage complete"],
    "revenues_earned": ["revenues earned", "revenue earned", "earned revenue",
                        "revenues recognized", "revenue recognized", "earned to date"],
    "gp_to_date": ["gross profit earned", "gross profit to date", "earnings to date",
                   "gross profit recognized"],
    "billings": ["billings to date", "billed to date", "billings", "progress billings"],
    "over_under": ["over", "under", "excess of billings", "billings in excess",
                   "costs in excess"],
}


def _tokens(text):
    import re
    return set(re.findall(r"[a-z%]+", text.lower()))


def _map_columns(table):
    """Match each extracted per-column header (table['columns']) against COLMAP.
    Phrase match beats token-subset match; each field maps to at most one column."""
    scores = []  # (quality, field, col_index)
    for ci, header in enumerate(table["columns"]):
        h = (header or "").lower()
        htoks = _tokens(h)
        if not htoks:
            continue
        for field, keys in COLMAP.items():
            for k in keys:
                if k in h:
                    scores.append((2, field, ci))
                    break
                ktoks = _tokens(k) - {"to", "of", "at", "in"}
                if ktoks and ktoks <= htoks:
                    scores.append((1, field, ci))
                    break
    scores.sort(key=lambda s: -s[0])
    mapping, used_cols = {}, set()
    for _, field, ci in scores:
        if field not in mapping and ci not in used_cols:
            mapping[field] = ci
            used_cols.add(ci)
    return mapping


def _looks_like_wip(table):
    return len(_map_columns(table)) >= 3


def _get(row, colmap, field):
    ci = colmap.get(field)
    if ci is None or ci >= len(row["values"]):
        return None
    return row["values"][ci]


def _check(name, printed, computed, results, job):
    if printed is None or computed is None:
        return
    d = printed - computed
    if abs(d) <= 0.011:
        status = "PASS"
    elif abs(d) <= ROUNDING:
        status = "ROUNDING"
    else:
        status = "FAIL"
    results.append({"job": job, "relation": name, "printed": printed,
                    "computed": round(computed, 2), "difference": round(d, 2),
                    "status": status})


def analyze(table, colmap):
    results = []
    totals = {f: 0.0 for f in colmap}
    njobs = 0
    for row in table["rows"]:
        if not any(v is not None for v in row["values"]):
            continue
        if looks_like_total(row["label"]):
            continue
        job = row["label"] or "(unlabeled job)"
        njobs += 1
        price = _get(row, colmap, "contract_price")
        ctd = _get(row, colmap, "costs_to_date")
        ctc = _get(row, colmap, "est_cost_to_complete")
        tec = _get(row, colmap, "total_est_cost")
        egp = _get(row, colmap, "est_gross_profit")
        pct = _get(row, colmap, "pct_complete")
        rev = _get(row, colmap, "revenues_earned")
        gpd = _get(row, colmap, "gp_to_date")
        bil = _get(row, colmap, "billings")
        ou = _get(row, colmap, "over_under")

        if tec is not None and ctd is not None and ctc is not None:
            _check("total est cost = costs to date + est cost to complete",
                   tec, ctd + ctc, results, job)
        tec_eff = tec if tec is not None else (ctd + ctc if ctd is not None and
                                               ctc is not None else None)
        if egp is not None and price is not None and tec_eff is not None:
            _check("est gross profit = contract price - total est cost",
                   egp, price - tec_eff, results, job)
        pct_eff = pct
        if pct_eff is not None and pct_eff > 1.5:  # printed as 87.5 not 0.875
            pct_eff = pct_eff / 100.0
        if pct_eff is None and ctd is not None and tec_eff:
            pct_eff = ctd / tec_eff
        if rev is not None and pct_eff is not None and price is not None:
            _check("revenues earned = % complete x contract price",
                   rev, pct_eff * price, results, job)
        if gpd is not None and rev is not None and ctd is not None:
            _check("gross profit to date = revenues earned - costs to date",
                   gpd, rev - ctd, results, job)
        if ou is not None and bil is not None and rev is not None:
            _check("over/(under)billings = billings - revenues earned",
                   ou, bil - rev, results, job)
        for f in colmap:
            v = _get(row, colmap, f)
            if v is not None:
                totals[f] += v

    # foot printed total row(s) against summed details — zero tolerance
    foot = []
    for row in table["rows"]:
        if looks_like_total(row["label"]):
            for f, ci in colmap.items():
                pv = row["values"][ci] if ci < len(row["values"]) else None
                if pv is None:
                    continue
                d = pv - totals[f]
                foot.append({"column": f, "printed_total": pv,
                             "sum_of_jobs": round(totals[f], 2),
                             "difference": round(d, 2),
                             "status": "PASS" if abs(d) <= 0.011 else "FAIL"})
    bs_ties = {}
    if "over_under" in colmap:
        over = under = 0.0
        for row in table["rows"]:
            if looks_like_total(row["label"]):
                continue
            v = _get(row, colmap, "over_under")
            if v is None:
                continue
            if v >= 0:
                over += v
            else:
                under += v
        bs_ties = {
            "overbillings_should_tie_to": "billings in excess of costs and estimated "
                                          "earnings on uncompleted contracts (liability)",
            "overbillings_total": round(over, 2),
            "underbillings_should_tie_to": "costs and estimated earnings in excess of "
                                           "billings on uncompleted contracts (asset)",
            "underbillings_total": round(abs(under), 2),
        }
    fails = [r for r in results if r["status"] == "FAIL"] + \
            [f for f in foot if f["status"] == "FAIL"]
    return {"table": table["id"], "page": table["page"], "title": table["title"],
            "column_mapping": colmap, "jobs": njobs,
            "recompute_checks": results, "column_footings": foot,
            "balance_sheet_ties": bs_ties,
            "summary": {"checks": len(results) + len(foot), "failures": len(fails),
                        "rounding_notes": sum(1 for r in results
                                              if r["status"] == "ROUNDING")}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("statements")
    ap.add_argument("--table", help="table id (default: auto-detect WIP-looking tables)")
    ap.add_argument("-o", "--out", default="wip_report.json")
    args = ap.parse_args()
    data = load_json(args.statements)
    targets = [t for t in data["tables"]
               if (args.table and t["id"] == args.table) or
                  (not args.table and _looks_like_wip(t))]
    if not targets:
        print("No WIP-looking schedule found. Pass --table <id>; ids available:")
        for t in data["tables"]:
            print(f"  {t['id']} p{t['page']}: {t['title'][:70]}")
        sys.exit(1)
    reports = []
    for t in targets:
        colmap = _map_columns(t)
        if len(colmap) < 3:
            print(f"{t['id']}: only mapped {list(colmap)} — headers too sparse, "
                  f"map columns manually and re-run with an edited statements.json")
            continue
        rep = analyze(t, colmap)
        reports.append(rep)
        print(f"{t['id']} p{t['page']}: {rep['jobs']} jobs, "
              f"{rep['summary']['checks']} checks, "
              f"{rep['summary']['failures']} FAIL, "
              f"{rep['summary']['rounding_notes']} rounding notes")
        print(f"  column mapping (VERIFY): {rep['column_mapping']}")
        for r in rep["recompute_checks"]:
            if r["status"] == "FAIL":
                print(f"  FAIL {r['job'][:40]} | {r['relation']} | printed "
                      f"{fmt(r['printed'])} vs computed {fmt(r['computed'])}")
        for f in rep["column_footings"]:
            if f["status"] == "FAIL":
                print(f"  FAIL footing {f['column']}: printed {fmt(f['printed_total'])} "
                      f"vs jobs sum {fmt(f['sum_of_jobs'])}")
    save_json({"source": data.get("source"), "schedules": reports}, args.out)
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()
