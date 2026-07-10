"""Build the cross-reference amounts index from statements.json.

Two outputs, both for the reviewing model to adjudicate:
  - amounts index: every distinct amount (>= --min) with every location it appears,
    so any tie ("does the debt note agree to the balance sheet?") is a lookup, not a
    page re-read. Amounts appearing in 2+ tables are the candidate tie set.
  - near misses: pairs of amounts on different pages that are close but NOT equal
    (within --near dollars or 0.5%) with similar row labels — the classic broken tie.

Usage: python xref.py statements.json [-o xref_report.json] [--min 1000] [--near 100]
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fslib import load_json, save_json

STOP = {"the", "of", "and", "in", "for", "to", "a", "net", "total", "less", "year",
        "ended", "current", "december", "june", "31", "30"}


def _label_tokens(label):
    return {t for t in re.findall(r"[a-z]+", label.lower()) if t not in STOP and len(t) > 2}


def _similar(l1, l2):
    a, b = _label_tokens(l1), _label_tokens(l2)
    if not a or not b:
        return False
    return len(a & b) / min(len(a), len(b)) >= 0.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("statements")
    ap.add_argument("-o", "--out", default="xref_report.json")
    ap.add_argument("--min", type=float, default=1000.0)
    ap.add_argument("--near", type=float, default=100.0)
    args = ap.parse_args()
    data = load_json(args.statements)

    occ = defaultdict(list)
    for t in data["tables"]:
        for row in t["rows"]:
            for ci, v in enumerate(row["values"]):
                if v is None or abs(v) < args.min:
                    continue
                occ[round(abs(v), 2)].append({
                    "page": t["page"], "table": t["id"], "title": t["title"][:60],
                    "label": row["label"], "column": ci + 1, "value": v,
                })

    multi = {}
    for amt, locs in occ.items():
        pages = {l["page"] for l in locs}
        if len(locs) > 1:
            multi[f"{amt:,.2f}"] = {"occurrences": len(locs), "pages": sorted(pages),
                                    "locations": locs}

    # near misses: similar labels, different pages, close-but-unequal amounts
    amts = sorted(occ.keys())
    near = []
    for i, a in enumerate(amts):
        for b in amts[i + 1:]:
            d = b - a
            if d > max(args.near, a * 0.005):
                break
            if d < 0.005:
                continue
            for la in occ[a]:
                for lb in occ[b]:
                    if la["page"] != lb["page"] and _similar(la["label"], lb["label"]):
                        near.append({
                            "amount_1": la["value"], "at_1": la,
                            "amount_2": lb["value"], "at_2": lb,
                            "difference": round(d, 2),
                            "note": f"'{la['label'][:50]}' p{la['page']} vs "
                                    f"'{lb['label'][:50]}' p{lb['page']} differ by {d:,.2f}",
                        })

    report = {"source": data.get("source"),
              "summary": {"distinct_amounts": len(occ),
                          "amounts_in_multiple_locations": len(multi),
                          "near_misses": len(near)},
              "near_misses": near,
              "amounts_index": multi}
    save_json(report, args.out)
    print(f"{len(occ)} amounts indexed; {len(multi)} appear in 2+ places; "
          f"{len(near)} near-misses -> {args.out}")
    for n in near[:25]:
        print("  NEAR-MISS", n["note"])


if __name__ == "__main__":
    main()
