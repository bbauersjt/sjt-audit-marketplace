# CCH Axcess TB import formats

The column specs CCH Axcess accepts when importing a trial balance from Excel,
plus the constraints that make an import succeed. Ground truth is
`cch-import-examples.xlsx` in this folder — three sheets, one per tier. Mirror
those exactly; this file explains them.

## The three tiers

Pick the smallest tier the engagement needs. Each tier is a superset of the one
above it.

### Basic — `Basic` sheet

The minimum: account number, name, balance. Use when the engagement has no
grouping set up yet, or the user just wants balances in.

| Account Number | Account Name | Account Balance |
|---|---|---|

### Grouped — `Grouped` sheet

Adds prior-year balance, the 4-digit group + subgroup, and the classification.
This is the normal deliverable for a grouped engagement.

| Account Number | Account Name | Account Balance | Prior Year Balance | Group Index | Group Name | Subgroup Index | Subgroup Name | Classification |
|---|---|---|---|---|---|---|---|---|

### Fund — `Fund` sheet

Grouped + a trailing **Fund Index**. Use for governmental / multi-fund
engagements. Every row carries the fund it belongs to.

| … all Grouped columns … | Fund Index |
|---|---|

## Hard constraints (an import that violates these fails)

- **No freeze panes.** CCH *silently* rejects any workbook with freeze panes.
  `write_cch_import()` sets `ws.freeze_panes = None` for you — never re-add them.
- **Header in row 1, nothing above it.** No client name, title, or date rows.
- **Single balance column** (not separate Debit / Credit).
- **Debits positive, credits negative.** Assets & expenses positive;
  liabilities, equity, revenue negative. If you sourced balances from the CCH
  FP-API (credits-positive) you must flip the sign first.
- **Unique account names.** Duplicate names collide on import.
- **Account number stays text.** Leading zeros and dash prefixes (`100-10000`)
  must survive — the writer applies text format (`@`) to that column.
- **Accounting number format** on balance columns:
  `#,##0.00;(#,##0.00);"-"`.
- **Balances net to zero** — in total, and per fund for a Fund import.

## Classification — the 10-way column

`default-classes.xlsx` is the vocabulary. Never write a value that is not on it:

| Abbrev | Meaning | Abbrev | Meaning |
|---|---|---|---|
| CA | Current Assets | REV | Revenues |
| NA | Non-Current Assets | COR | Cost of Revenue |
| CL | Current Liabilities | OI | Other Income |
| NL | Non-Current Liabilities | OPX | Operating Expenses |
| EQ | Equity | OE | Other Expenses |

The grouping index only carries a **coarse** class
(`Asset / Liability / Equity / Revenue / Expense / Other / Transfer`, and for
EBP `Net Assets / Addition / Deduction`). Resolving that to one of the ten
abbreviations needs two judgment axes the index does not store:

- **Current vs non-current** — for every Asset and Liability. Cash, AR,
  inventory, prepaids, current portions → `CA` / `CL`. PP&E / capital assets,
  long-term investments, intangibles, deferred outflows/inflows, long-term
  debt, net pension/OPEB liabilities, noncurrent compensated absences →
  `NA` / `NL`.
- **Operating vs cost-of-revenue vs other** — for income-statement lines.
  Ordinary operating expense → `OPX`; cost of goods/services → `COR`;
  interest expense, losses, other non-operating → `OE`. Ordinary revenue →
  `REV`; gains, interest/dividend income, other non-operating → `OI`.
  Governmental: expenditures (incl. debt service) read as `OPX`; transfers
  in → `REV`, transfers out → `OPX` (see the govt example).

`tb_io.guess_class(coarse, group_name, account_name)` returns a
`(abbrev, confidence, note)` hint using these rules. Confirm anything it
returns below `high`.

## Fund Index — where it comes from

There is no single rule; infer, then confirm:

1. **Account-number pattern.** Most TBs prefix or suffix the fund:
   `100-10000` (prefix) or `10000-100` (suffix). `tb_io.scan_fund_patterns()`
   reports the dominant pattern, the fund set, and coverage. High coverage +
   one consistent pattern → proceed, stating what you inferred.
2. **Fund names on the TB.** Some client TBs label the fund in a column or in
   the account name rather than the number. Map each name to a fund index with
   the user.
3. **CaseWare engagement copy.** The caseware-crosswalk TB extract's `funds`
   list carries the full consolidation hierarchy (recovered from the CE.dbf
   ENTITY-key prefixes): each entity is tagged `root` / `master` / `child`
   with its `parent` and `fund_type`. Children ARE the funds; their ABBR is
   the Fund Index. Never ask for a screenshot when a `_tb_extract.json`
   exists.

Always ask whether the engagement also needs a **standalone fund import**.
Its 4 required columns (per the firm's fund-import example):

| Fund Type Index | Fund Type Name | Fund Index | Fund Name |
|---|---|---|---|

From a CaseWare extract this builds itself — the two CaseWare layers map
onto CCH's two layers: non-root **masters → fund types**, **children →
funds**:

```python
conv = T.funds_from_cw_extract(extract["funds"])   # rows + warnings
T.write_fund_list("/out/Fund import.xlsx", conv["rows"])
```

Fund types are numbered '01', '02', … in tree order. Surface every entry in
`conv["warnings"]` — orphan funds (no master in CaseWare) are promoted to
their own fund type and the user may want to re-home them (e.g. several
special-revenue funds under one type).

## Writing the files

```python
import sys; sys.path.insert(0, "<skill>/scripts")
import tb_io as T

rows = [ {"account": "100-10000", "name": "Cash - Operating",
          "balance": 1843250, "py_balance": 1714222,
          "group_index": "1000", "group_name": "Cash and Cash Equivalents",
          "subgroup_index": "1010", "subgroup_name": "Operating Cash",
          "classification": "CA", "fund_index": "100"}, ... ]

T.write_cch_import("/out/Fund TB import.xlsx", "fund", rows)   # or "basic" / "grouped"
```

`write_cch_import` returns `{tier, rows, total, by_fund}`. Check `total`
(and each `by_fund` value for a fund import) is `0.00` before handing off.
