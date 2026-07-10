"""Disclosure PRESENCE heuristics — keyword probes per required note topic.

For each topic: if the trigger pattern appears anywhere in the package (or the topic is
always applicable) but NONE of the expected disclosure keywords appear, emit a
candidate. These are candidates for the disclosure reviewer to adjudicate against the
framework's disclosures module — a hit means "go confirm this note really is missing",
never "missing disclosure" on its own; a silent topic means only that this crude probe
found the keywords, not that the disclosure is adequate.

Usage:
  python disclosure_scan.py <package.pdf> --framework commercial|nonprofit|govt|ebp
                            [-o disclosure_scan.json]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fslib import save_json

# (topic, trigger regex or None=always applicable, [expected keywords, any one suffices])
COMMON = [
    ("subsequent-events", None,
     ["subsequent event"]),
    ("use-of-estimates", None,
     ["use of estimates", "estimates and assumptions", "actual results could differ"]),
    ("leases", r"right.of.use|lease liabilit|operating lease|finance lease",
     ["lease term", "discount rate", "asc 842", "maturities of lease",
      "future minimum lease", "gasb 87"]),
    ("debt-maturities", r"notes? payable|long.term debt|bonds? payable|line of credit",
     ["maturit", "principal payment", "due in 20", "aggregate annual", "debt service"]),
    ("fair-value-hierarchy", r"fair value",
     ["level 1", "level 2", "level 3", "unobservable", "net asset value"]),
    ("receivable-allowance", r"receivable",
     ["allowance", "credit loss", "uncollectible", "fully collectible",
      "considered collectible"]),
    ("cash-concentration", r"cash",
     ["federally insured", "fdic", "ncua", "concentration of credit",
      "custodial credit", "collateraliz", "insured limit"]),
    ("related-party", None,
     ["related party", "related-party", "related organization", "affiliate"]),
    ("commitments-contingencies", None,
     ["commitment", "contingenc", "litigation", "legal proceeding"]),
]

FRAMEWORK = {
    "commercial": [
        ("income-taxes", None,
         ["income tax", "deferred tax", "pass-through", "s corporation",
          "no provision for federal"]),
        ("revenue-recognition", None,
         ["revenue recognition", "performance obligation", "asc 606",
          "revenue from contracts", "revenue is recognized", "recognized over time",
          "recognized at a point in time"]),
        ("inventory-method", r"inventor",
         ["first-in", "fifo", "lifo", "weighted average", "lower of cost",
          "net realizable"]),
        ("depreciation-policy", r"property and equipment|property, plant",
         ["straight-line", "useful li", "estimated li", "depreciation method"]),
    ],
    "nonprofit": [
        ("liquidity-availability", None,
         ["liquidity", "financial assets available", "availability of"]),
        ("net-asset-composition", None,
         ["with donor restrictions", "without donor restrictions"]),
        ("functional-allocation", None,
         ["allocated", "functional", "allocation method"]),
        ("contributed-nonfinancial", r"in.kind|contributed service|donated",
         ["contributed nonfinancial", "contributed service", "in-kind",
          "asu 2020-07", "donated"]),
        ("endowment", r"endowment",
         ["upmifa", "underwater", "spending polic", "board-designated endowment"]),
        ("tax-status", None,
         ["501(c)", "exempt from federal income tax", "internal revenue code"]),
        ("revenue-recognition", None,
         ["revenue recognition", "performance obligation", "contribution",
          "condition"]),
    ],
    "govt": [
        ("pension", r"pension",
         ["net pension liability", "discount rate", "proportionate share",
          "actuarial"]),
        ("opeb", r"opeb|other postemployment",
         ["total opeb liability", "net opeb", "healthcare cost trend"]),
        ("fund-balance-classification", r"fund balance",
         ["nonspendable", "committed", "assigned", "unassigned"]),
        ("capital-assets-policy", r"capital assets",
         ["capitalization threshold", "straight-line", "useful li",
          "estimated li"]),
        ("deposits-investments-risk", r"deposit|investment",
         ["custodial credit risk", "interest rate risk", "credit risk"]),
        ("interfund", r"interfund|due to other funds|due from other funds",
         ["interfund"]),
    ],
    "ebp": [
        ("plan-description", None,
         ["plan description", "eligib", "vesting", "plan document"]),
        ("tax-status", None,
         ["determination letter", "opinion letter", "prototype", "qualified"]),
        ("party-in-interest", None,
         ["party-in-interest", "parties-in-interest", "exempt party"]),
        ("risks-uncertainties", None,
         ["risks and uncertainties", "market risk", "reasonably possible"]),
        ("fully-benefit-responsive", r"stable value|guaranteed investment",
         ["fully benefit-responsive", "contract value"]),
        ("certification-scope", r"103\(a\)\(3\)\(c\)|certif",
         ["certified", "certification", "qualified institution"]),
    ],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--framework", required=True,
                    choices=["commercial", "nonprofit", "govt", "ebp"])
    ap.add_argument("-o", "--out", default="disclosure_scan.json")
    args = ap.parse_args()

    import pdfplumber
    pages = []
    with pdfplumber.open(args.input) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            pages.append((i, (page.extract_text() or "")))
    full = "\n".join(t for _, t in pages).lower()

    probes = COMMON + FRAMEWORK[args.framework]
    candidates, checked = [], []
    for topic, trigger, expected in probes:
        trig_hit = None
        if trigger:
            m = re.search(trigger, full, re.IGNORECASE)
            if not m:
                checked.append({"topic": topic, "status": "not-applicable",
                                "reason": "trigger not present"})
                continue
            for pno, t in pages:
                mm = re.search(trigger, t, re.IGNORECASE)
                if mm:
                    trig_hit = {"page": pno,
                                "excerpt": t[max(0, mm.start() - 40):mm.end() + 40]
                                .replace("\n", " ")[:120]}
                    break
        found = [k for k in expected if k.lower() in full]
        if found:
            checked.append({"topic": topic, "status": "keywords-present",
                            "matched": found[:3]})
        else:
            candidates.append({
                "topic": topic,
                "trigger": trig_hit or "always applicable",
                "expected_any_of": expected,
                "detail": f"'{topic}' appears applicable but none of its expected "
                          f"disclosure keywords were found anywhere in the package — "
                          f"confirm whether the disclosure is missing or worded "
                          f"unusually",
            })
    report = {"source": args.input, "framework": args.framework,
              "summary": {"topics_probed": len(probes),
                          "candidates": len(candidates)},
              "candidates": candidates, "checked": checked}
    save_json(report, args.out)
    print(f"{len(probes)} topics probed, {len(candidates)} presence candidates "
          f"-> {args.out}")
    for c in candidates:
        print(f"  [missing?] {c['topic']}")


if __name__ == "__main__":
    main()
