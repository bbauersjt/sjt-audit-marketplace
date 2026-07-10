"""Agree prior-year comparative figures in the CY package to the PY issued package.

Extract both packages first (extract_tables.py), then:

  python compare_py.py cy_statements.json py_statements.json --py 2024 --cy 2025 -o py_compare.json

For every row label in the CY package that carries a value in a PY-year column
(column header contains the PY year — falls back to the LAST value column when no
header names a year, the comparative convention), the script looks the label up in
the PY package's own primary columns and reports:

  AGREES        the CY comparative value appears under that label in the PY package
  MISMATCH      label exists in the PY package but with different value(s) — candidate
                comparative error or unlabeled reclassification
  NOT-FOUND     label has no match in the PY package — renamed line, reclass, or
                new/removed caption (adjudicate; renames are common and benign)

Matching is by normalized label, so a reworded caption lands in NOT-FOUND rather than
silently passing. Beginning-balance checks (retained earnings / net assets / capital
roll into CY) are the adjudicator's job using this output plus the equity statements.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fslib import fmt, load_json, save_json


def _norm(label):
    s = re.sub(r"\(.*?\)", " ", label.lower())          # drop parentheticals
    s = re.sub(r"\b(19|20)\d{2}\b", " ", s)             # drop years
    s = re.sub(r"[^a-z]+", " ", s).strip()
    return s


def _year_cols(table, year, exclude_year=None):
    """Column indexes whose header names the given year (and, when exclude_year is
    given, does NOT also name that year — centered 'December 31, 2025 and 2024'
    title lines can bleed year tokens into a neighboring column's header)."""
    hits = []
    for i, h in enumerate(table.get("columns", [])):
        h = h or ""
        if re.search(rf"\b{year}\b", h):
            if exclude_year and re.search(rf"\b{exclude_year}\b", h):
                continue
            hits.append(i)
    return hits


BEGIN_RE = re.compile(r"beginning of (the )?year|beginning balance|"
                      r"balance[s]?,? (at )?beginning|, beginning", re.IGNORECASE)
END_RE = re.compile(r"end of (the )?year|ending balance|balance[s]?,? (at )?end|"
                    r", end(ing)?\b", re.IGNORECASE)


def _beginning_balance_ties(cy_data, py_data):
    """CY beginning-balance rows must equal SOME PY ending-balance value.
    Candidate generator: comparative columns mean a begin row also carries the
    PY-beginning figure, which legitimately matches nothing in the PY package —
    the adjudicator sorts that out with both documents open."""
    py_end = []  # (label, value, page)
    for t in py_data.get("tables", []):
        for row in t.get("rows", []):
            if END_RE.search(row.get("label", "")):
                for v in row["values"]:
                    if v is not None:
                        py_end.append((row["label"], round(v, 2), t["page"]))
    py_end_vals = {v for _, v, _ in py_end}
    ties = []
    for t in cy_data.get("tables", []):
        for row in t.get("rows", []):
            if not BEGIN_RE.search(row.get("label", "")):
                continue
            for ci, v in enumerate(row["values"]):
                if v is None:
                    continue
                v = round(v, 2)
                if v in py_end_vals or -v in py_end_vals:
                    status, note = "AGREES", ""
                else:
                    close = min(py_end, key=lambda e: abs(e[1] - v), default=None) \
                        if py_end else None
                    status = "NO-MATCH"
                    note = (f"closest PY ending balance: {fmt(close[1])} "
                            f"('{close[0][:40]}' p{close[2]})" if close else
                            "no ending-balance rows found in PY package")
                ties.append({"page": t["page"], "label": row["label"],
                             "column": ci + 1, "cy_value": v,
                             "status": status, "note": note})
    return ties


def _py_value_index(py_data, py_year):
    """PY package: normalized label -> set of values from its primary-year columns
    (columns naming py_year, else all value columns)."""
    idx = defaultdict(set)
    for t in py_data.get("tables", []):
        cols = _year_cols(t, py_year)
        for row in t.get("rows", []):
            key = _norm(row.get("label", ""))
            if not key:
                continue
            vals = row["values"]
            use = [vals[c] for c in cols if c < len(vals)] if cols else vals
            for v in use:
                if v is not None:
                    idx[key].add(round(v, 2))
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cy_statements")
    ap.add_argument("py_statements")
    ap.add_argument("--py", type=int, required=True, help="prior fiscal year, e.g. 2024")
    ap.add_argument("--cy", type=int, required=True,
                    help="current fiscal year, e.g. 2025 (used to disambiguate columns)")
    ap.add_argument("--min", type=float, default=0.0,
                    help="ignore CY comparative values below this magnitude")
    ap.add_argument("-o", "--out", default="py_compare.json")
    args = ap.parse_args()
    cy = load_json(args.cy_statements)
    py = load_json(args.py_statements)
    py_idx = _py_value_index(py, args.py)

    results = []
    for t in cy.get("tables", []):
        cols = _year_cols(t, args.py, exclude_year=args.cy)
        fallback = not cols
        if fallback:
            ncols = len(t.get("columns", []))
            if ncols != 2:
                continue  # only a classic 2-column comparative justifies guessing
            cols = [1]
        for row in t.get("rows", []):
            key = _norm(row.get("label", ""))
            if not key:
                continue
            for c in cols:
                v = row["values"][c] if c < len(row["values"]) else None
                if v is None or abs(v) < args.min:
                    continue
                v = round(v, 2)
                if key not in py_idx:
                    status = "NOT-FOUND"
                    note = "label not found in PY package (rename/reclass/new caption?)"
                elif v in py_idx[key] or -v in py_idx[key]:
                    status, note = "AGREES", ""
                else:
                    status = "MISMATCH"
                    note = (f"CY package shows {fmt(v)}; PY package has "
                            f"{sorted(py_idx[key])} under this label")
                results.append({"table": t["id"], "page": t["page"], "column": c + 1,
                                "column_header": (t.get("columns") or [""])[c]
                                if c < len(t.get("columns", [])) else "",
                                "fallback_column": fallback,
                                "label": row["label"], "cy_comparative_value": v,
                                "status": status, "note": note})

    mism = [r for r in results if r["status"] == "MISMATCH"]
    notf = [r for r in results if r["status"] == "NOT-FOUND"]
    bb = _beginning_balance_ties(cy, py)
    bb_bad = [b for b in bb if b["status"] != "AGREES"]
    report = {"cy_source": cy.get("source"), "py_source": py.get("source"),
              "py_year": args.py,
              "summary": {"checked": len(results), "agrees": len(results) -
                          len(mism) - len(notf), "mismatches": len(mism),
                          "not_found": len(notf),
                          "beginning_balance_rows": len(bb),
                          "beginning_balance_no_match": len(bb_bad)},
              "mismatches": mism, "not_found": notf,
              "beginning_balances": bb, "all": results}
    save_json(report, args.out)
    print(f"{len(results)} comparative values checked: "
          f"{report['summary']['agrees']} agree, {len(mism)} MISMATCH, "
          f"{len(notf)} not found; {len(bb)} beginning-balance values, "
          f"{len(bb_bad)} without a PY ending match -> {args.out}")
    for r in mism[:30]:
        print(f"  MISMATCH p{r['page']} {r['label'][:50]} | {r['note']}")
    for b in bb_bad[:15]:
        print(f"  BB NO-MATCH p{b['page']} {b['label'][:50]} = {fmt(b['cy_value'])} "
              f"| {b['note']}")


if __name__ == "__main__":
    main()
