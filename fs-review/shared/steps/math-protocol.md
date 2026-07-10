# Math Protocol — the deterministic pipeline

All arithmetic is done by scripts, never by the model. Do not mentally foot, cross-foot,
or recompute anything from PDF text — run the pipeline and adjudicate its output.
Rounding tolerance on footings is ZERO: a $1 difference is a finding. Rounding is an
explanation, not an excuse.

## Pipeline

Run from the plugin's `scripts/` directory (Python 3.10+, `pdfplumber` + `openpyxl`):

```
python extract_tables.py <package.pdf> -o statements.json      # every table, geometric column mapping
python foot.py statements.json -o foot_report.json             # foots + cross-foots everything, zero tolerance
python xref.py statements.json -o xref_report.json             # amounts index + near-miss broken-tie candidates
python proof_scan.py <package.pdf> --cy <FY> --statements statements.json -o proof_scan.json
                                                               # text-layer proof candidates (see steps/proof.md)
python disclosure_scan.py <package.pdf> --framework <f> -o disclosure_scan.json
                                                               # disclosure PRESENCE candidates for the disclosure reviewer
python tie_wip.py statements.json -o wip_report.json           # construction only — WIP schedule recompute
python compare_py.py statements.json py_statements.json --py <PY> --cy <FY> -o py_compare.json
                                                               # PY package provided only — comparative agreement
python report.py findings.json -o "<Client> FS Review.xlsx"    # final deliverable (after merge)
```

Work in a scratch folder; only the final .xlsx is a deliverable.

## Adjudicating foot_report.json

For each `FAIL`:
1. Verify against the printed page (render/read the actual page — never trust extraction
   alone). If extraction misread the line, fix `statements.json` and re-run.
2. If the printed figure really does not foot, it is a finding. Severity: use the size
   and location — a $1–$2 rounding slip on a statement column is typically Moderate
   (still a finding: the preparer must force the printed column to foot); larger breaks
   or breaks that change subtotal relationships are Significant/Critical.
3. `SKIP` / `AMBIGUOUS` rows (no component span found): the total's components may span
   pages or the label heuristic missed — verify those manually against statements.json
   values (still no mental re-adding of PDF text; sum the extracted values).
4. Then work `steps/statement-relations.md` — the structural relations (balance sheet
   balances, IS build-down, equity rollforward, cash-flow ties) — using extracted
   values, and confirm each holds.

## Adjudicating xref_report.json

- `near_misses` are candidate broken ties (same caption, different amount, different
  page). Verify each against the document; a confirmed mismatch is a finding with both
  locations and both figures.
- Use `amounts_index` to execute the tie list in `steps/xref.md` and the framework's
  cross-reference additions: for each required tie, look the amount up in the index and
  confirm it appears in both expected locations. An amount that should tie but appears
  with different values in the two locations is a finding; an expected disclosure amount
  that appears nowhere else may be a completeness question.

## Multi-column statements (consolidating / combining / segment / WIP)

Column mapping is geometric (right-edge clustering) and no longer needs the source
Excel. Before relying on results for a 3+ column statement, sanity-check the printed
column headers against `columns` in statements.json for that table. If extraction
emitted warnings for the table, resolve them visually first.

## When extraction fails a page

If a page produces garbage (scanned image, unusual layout), do NOT fall back to mental
math on raw text. Render the page, read the figures visually, hand-build that table in
statements.json (or a small CSV), and re-run foot.py. The zero-tolerance rule only means
something if every number that gets compared came through a deterministic path.
