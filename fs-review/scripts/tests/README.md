# Pipeline regression test

`make_test_fs.py` (needs `reportlab`) generates two fixtures:

- `test_fs.pdf` — a synthetic construction-contractor package with **five planted math
  errors** (E1–E5, documented in the script docstring: $1 footing slip, $100 PY
  fat-finger, $1,000 broken debt-note tie, bad WIP over/underbilling row, short-footed
  WIP column) and **eleven planted proof errors** on the notes page (P1–P10 in the
  script: skipped Note 3, out-of-order note headings, dangling "Note 9" reference,
  mixed Auditor's/Auditors', mixed serial comma, capitalization drift on a repeated
  heading, stale year 2023, DRAFT marker, mixed date formats, "recievables"
  misspelling, one Times-Roman line in a Helvetica document).
- `test_fs_py.pdf` — the "issued" 2024 statement with the TRUE prior-year figures, so
  the CY package's comparative column disagrees on three cascading lines.

Expected results after any change to the scripts:

```
python make_test_fs.py
python ..\extract_tables.py test_fs.pdf -o statements.json        # 0 warnings, 4 tables
python ..\foot.py statements.json                                 # exactly 3 FAIL (E1, E2, E5),
                                                                  # 0 crossfoots (no total column)
python ..\xref.py statements.json --min 5000                      # 1 near-miss (E3, $1,000 LTD)
python ..\tie_wip.py statements.json                              # auto-detects WIP; FAILs on
                                                                  # Job 103 (E4) + price footing (E5)
python ..\proof_scan.py test_fs.pdf --cy 2025 --statements statements.json
                                                                  # exactly 11 candidates:
                                                                  # notes×3, possessive, serial-comma,
                                                                  # casing, years (stale 2023),
                                                                  # draft-markers, date-formats,
                                                                  # spelling ("recievables" only),
                                                                  # fonts (the Times-Roman line only)
                                                                  # (2029/2031 maturities and "payables"
                                                                  # must NOT flag)
python ..\disclosure_scan.py test_fs.pdf --framework commercial   # 8 presence candidates
                                                                  # (revenue-recognition, leases,
                                                                  # fair-value, receivable-allowance
                                                                  # must show keywords-present/n-a)
python ..\extract_tables.py test_fs_py.pdf -o py_statements.json  # 0 warnings, 1 table
python ..\compare_py.py statements.json py_statements.json --py 2024 --cy 2025
                                                                  # 11 checked: 8 agree, 3 MISMATCH
                                                                  # (total opex / income from ops /
                                                                  # net income), 0 not found,
                                                                  # 0 beginning-balance rows
```

More failures = false positives introduced; fewer = a planted error slipped. Both are
regressions.
