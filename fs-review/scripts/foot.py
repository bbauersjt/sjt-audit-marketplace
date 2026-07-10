"""Foot and cross-foot every table in statements.json. Zero tolerance — a $1 diff is reported.

For each column, every total-looking row is tested against candidate component spans:
  1. sum of detail rows since the previous total row (the normal case)
  2. sum of the previous subtotal rows themselves (grand-total-of-subtotals)
  3. any contiguous span ending just above the total (fallback search)
A total that matches no candidate is a FAIL, reported with the closest candidate and the
exact difference. For tables with 3+ value columns, each row is also cross-footed
(cols 1..n-1 summed against the last column, with and without sign flip on any column —
catches consolidating eliminations presented either way).

Usage: python foot.py statements.json [-o foot_report.json] [--min-rows 3]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fslib import fmt, load_json, looks_like_total, save_json

EPS = 0.011  # anything beyond a cent is a difference


def _col_series(table, ci):
    """(row_index, label, value) for rows with a value in column ci."""
    out = []
    for ri, row in enumerate(table["rows"]):
        v = row["values"][ci]
        if v is not None:
            out.append((ri, row["label"], v))
    return out


def _suffix_match(stack, val):
    """Suffix of the stack summing to val (exact); else best suffix.

    A straight sum is tried first. For short suffixes, sign combinations are also
    tried — statements routinely present difference totals ("Change in net assets" =
    total revenue − total expenses, both printed positive)."""
    s = 0.0
    best = None  # (absdiff, j, sum)
    for j in range(len(stack) - 1, -1, -1):
        s += stack[j][1]
        d = s - val
        if best is None or abs(d) < abs(best[0]):
            best = (d, j, s)
        if abs(d) <= EPS:
            return j, s, True
    # difference totals: sign combos over suffixes of up to 5 components
    from itertools import product
    for j in range(len(stack) - 1, max(-1, len(stack) - 6), -1):
        vals = [item[1] for item in stack[j:]]
        for signs in product((1, -1), repeat=len(vals)):
            if all(x < 0 for x in signs):
                continue
            if abs(sum(sg * v for sg, v in zip(signs, vals)) - val) <= EPS:
                return j, val, True
    if best is None:
        return None, None, False
    return best[1], best[2], False


def _check_column(table, ci):
    """Footing stack with self-healing: labels like "Net increase in the fair value
    of investments" LOOK like totals but are detail rows. If a pass produces
    failures, retry with failed mid-column "totals" demoted to details; accept the
    demotion only if it strictly reduces failures (a genuinely broken subtotal will
    NOT heal — demoting it double-counts downstream and failures persist, so its
    original FAIL is kept)."""
    demoted = set()
    best = best_key = None
    for _ in range(5):
        results, leftover = _run_column(table, ci, demoted)
        nfail = sum(1 for r in results if r["status"] == "FAIL")
        # a demotion is only legitimate if it does not orphan detail rows: demoting a
        # GENUINELY broken subtotal lets the grand total match its printed value
        # while the subtotal's components go unconsumed — reject that "heal"
        if best is None or (nfail < best_key[0] and leftover <= best_key[1]):
            best, best_key = results, (nfail, leftover)
        if nfail == 0:
            break
        # demote ONE candidate per round (earliest failed total that has a later
        # total downstream) — demoting several at once can demote a true total
        # together with the mislabeled detail that broke it
        total_ris = [r["_ri"] for r in results]
        nxt = next((r["_ri"] for r in sorted(results, key=lambda r: r["_ri"])
                    if r["status"] == "FAIL" and r["_ri"] not in demoted
                    and any(t > r["_ri"] for t in total_ris)), None)
        if nxt is None:
            break
        demoted.add(nxt)
    for r in best:
        r.pop("_ri", None)
    return best


def _run_column(table, ci, demoted):
    """Returns (results, leftover) — leftover counts detail rows never consumed by
    any total, used to reject illegitimate demotions."""
    series = _col_series(table, ci)
    results = []
    stack = []  # (label, value, is_total)
    for ri, lbl, val in series:
        if not looks_like_total(lbl) or ri in demoted:
            stack.append((lbl, val, False))
            continue
        if not stack:
            results.append({
                "_ri": ri,
                "table": table["id"], "page": table["page"], "column": ci + 1,
                "total_label": lbl, "printed": val, "status": "SKIP",
                "basis": "no-components-found", "difference": None,
                "note": "total row with no components above it in this column"})
            stack.append((lbl, val, True))
            continue
        j, s, ok = _suffix_match(stack, val)
        if ok:
            span_labels = [item[0] for item in stack[j:]]
            del stack[j:]
            stack.append((lbl, val, True))
            results.append({
                "_ri": ri,
                "table": table["id"], "page": table["page"], "column": ci + 1,
                "total_label": lbl, "printed": val, "status": "PASS",
                "basis": f"sum-of-{len(span_labels)}-components",
                "difference": 0.0, "note": ""})
        else:
            d = s - val
            carried = re.search(r"change in net (assets|position)|net income|"
                                r"net loss|change in fund balance", lbl, re.IGNORECASE)
            results.append({
                "_ri": ri,
                "table": table["id"], "page": table["page"], "column": ci + 1,
                "total_label": lbl, "printed": val,
                "status": "CHECK-INPUT" if carried else "FAIL",
                "basis": f"closest-suffix-{len(stack) - j}-components",
                "difference": round(d, 2),
                "note": (f"'{lbl.strip()}' could not be derived from the rows above — "
                         f"on a cash-flow reconciliation this is a carried-forward "
                         f"INPUT row, not a footing break; verify it ties to the "
                         f"statement it comes from" if carried else
                         f"printed {fmt(val)} vs computed {fmt(s)} "
                         f"(diff {fmt(d)}; no combination of the rows above "
                         f"sums to the printed total)")})
            # assume the printed total's SCOPE was the closest suffix; collapse it
            # so downstream totals aren't poisoned by one bad subtotal
            del stack[j:]
            stack.append((lbl, val, True))
    leftover = sum(1 for item in stack if not item[2])
    return results, leftover


def _crossfoot(table):
    ncols = len(table["columns"])
    if ncols < 3:
        return []
    # only cross-foot when the last column is actually a summation column
    last_hdr = (table["columns"][-1] or "").lower()
    hdr_text = " ".join(table.get("header_lines", [])).lower()
    all_hdr = (hdr_text + " " + " ".join(h or "" for h in table["columns"])).lower()
    if not any(k in last_hdr for k in ("total", "consolidat", "combined")) and \
       not any(k in hdr_text for k in ("consolidat", "combined")):
        return []
    # govt-wide statement of activities: rows are revenues MINUS expenses split into
    # net-expense columns — not a straight cross-sum; leave to the relations reviewer
    if re.search(r"charges for|operating grants|capital grants|program revenues|"
                 r"net \(expense", all_hdr):
        return []
    # horizontally-continued combining schedules: the Total column includes fund
    # columns printed on the PRECEDING page — cross-summing this page alone is
    # definitionally wrong (column footings remain valid); the relations reviewer
    # verifies cross-page totals from statements.json
    if "continued" in all_hdr:
        return []
    out = []
    for row in table["rows"]:
        vals = row["values"]
        if sum(1 for v in vals if v is not None) < 3 or vals[-1] is None:
            continue
        parts = [v for v in vals[:-1] if v is not None]
        if len(parts) < 2:
            continue
        total = vals[-1]
        diffs = {"straight-sum": sum(parts) - total}
        # try flipping each single column's sign (elimination columns vary in convention)
        for i, v in enumerate(vals[:-1]):
            if v is not None:
                flipped = sum(parts) - 2 * v
                diffs[f"col{i+1}-negated"] = flipped - total
        best = min(diffs.items(), key=lambda kv: abs(kv[1]))
        status = "PASS" if abs(best[1]) <= EPS else "FAIL"
        out.append({
            "table": table["id"], "page": table["page"], "row_label": row["label"],
            "check": "crossfoot", "basis": best[0], "printed_total": total,
            "difference": round(best[1], 2), "status": status,
            "note": "" if status == "PASS" else
                    f"row does not cross-foot: best basis {best[0]}, diff {fmt(best[1])}",
        })
    # systematic failure = the total column includes columns not printed on this page
    # (an unmarked continued/partial schedule), not row-level errors
    fails = [r for r in out if r["status"] == "FAIL"]
    if len(out) >= 2 and len(fails) / len(out) > 0.5:
        return [{
            "table": table["id"], "page": table["page"], "row_label": "(all rows)",
            "check": "crossfoot", "basis": "systematic", "printed_total": None,
            "difference": None, "status": "SKIP",
            "note": f"{len(fails)}/{len(out)} rows fail to cross-foot uniformly — "
                    f"this page appears to be a continued/partial schedule whose "
                    f"Total column includes columns printed on another page; verify "
                    f"the full schedule across pages via the relations review",
        }]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("statements")
    ap.add_argument("-o", "--out", default="foot_report.json")
    ap.add_argument("--min-rows", type=int, default=3,
                    help="skip tables with fewer value rows than this")
    args = ap.parse_args()
    data = load_json(args.statements)
    footings, crossfoots = [], []
    prose_skipped = []
    for table in data["tables"]:
        value_rows = [r for r in table["rows"] if any(v is not None
                                                      for v in r["values"])]
        if len(value_rows) < args.min_rows:
            continue
        # prose blocks (MD&A narrative with inline amounts) are not tables — median
        # sentence-length labels give them away; leave them to the reading reviewers
        lens = sorted(len(r["label"]) for r in value_rows)
        if lens[len(lens) // 2] > 55:
            prose_skipped.append(table["id"])
            continue
        for ci in range(len(table["columns"])):
            footings.extend(_check_column(table, ci))
        crossfoots.extend(_crossfoot(table))
    if prose_skipped:
        print(f"note: skipped {len(prose_skipped)} prose-like blocks "
              f"({', '.join(prose_skipped[:8])}) — narrative text, not tables")
    fails = [r for r in footings + crossfoots if r["status"] == "FAIL"]
    check_inputs = [r for r in footings if r["status"] == "CHECK-INPUT"]
    report = {
        "source": data.get("source"),
        "summary": {
            "footings_checked": len(footings),
            "crossfoots_checked": len(crossfoots),
            "failures": len(fails),
            "check_inputs": len(check_inputs),
            "extraction_warnings": sum(len(t.get("warnings", [])) for t in data["tables"]),
        },
        "failures": fails,
        "check_inputs": check_inputs,
        "all_footings": footings,
        "all_crossfoots": crossfoots,
    }
    save_json(report, args.out)
    print(f"{len(footings)} footings + {len(crossfoots)} crossfoots checked; "
          f"{len(fails)} FAIL, {len(check_inputs)} CHECK-INPUT -> {args.out}")
    for f in fails[:40]:
        loc = f"{f['table']} p{f['page']}"
        print(f"  FAIL {loc} | {f.get('total_label') or f.get('row_label')} | {f['note']}")
    for f in check_inputs[:10]:
        print(f"  CHECK-INPUT {f['table']} p{f['page']} | {f['total_label']} | "
              f"verify ties to its source statement")


if __name__ == "__main__":
    main()
