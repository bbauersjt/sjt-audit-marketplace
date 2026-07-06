# Output Format

Sampling produces **two Excel workbooks** — a Pull file (sterile, for fieldwork) and a Review file (sterile reference for reviewers and for putting scope on workpapers).

---

## File 1 — Pull file

**Naming**: `<client>_<engagement-period>_sample_pull.xlsx`

**Purpose**: Hand to audit staff. Sterile. No methodology, no thresholds — selections only.

**One tab per sample.** Each tab:

1. **Heading** in A1 — bold, plain text: `<sample name>` (e.g., "AJEs", "Vendors", "Cash Receipts")
2. Blank row
3. **Selections table** — bold headers with thin black bottom border; auto-sized columns; `#,##0` or `$#,##0` number format; trimmed columns only (drop internal IDs unless needed for traceability, status flags, blank columns, raw timestamps when a clean date column exists)

**Do NOT include**: population reconciliation, methodology, thresholds, TM, strata, random seed, any PPC.

---

## File 2 — Review file

**Naming**: `<client>_<engagement-period>_sample_review.xlsx`

**Purpose**: Sterile reference. Lets the team put scope on workpapers, lets reviewers evaluate sampling methodology, and shows coverage. **No workpaper structure** — no Purpose / Procedure / Conclusion / Notes anywhere.

### Tab 1 — Summary sheet (named `Summary`)

One row per sample. Columns:

| Column | Notes |
|--------|-------|
| Sample name | |
| Method used | Method name that won the comparison |
| Sample size (n) | |
| Population count (cleaned) | After cleanup |
| Population $ (cleaned) | Blank for non-dollar samples (controls, compliance) |
| Sample $ | Sum of selected items; blank for non-dollar samples |
| Dollar coverage % | Sample $ ÷ Population $; blank for non-dollar samples |
| Occurrence coverage % | n ÷ Population count; shown for all samples |
| TM / threshold used | Blank if not applicable |
| Strata | "Yes / No" or brief description |
| Substantive gate met | For controls-substantive-dual or other gated methods: which requirement was satisfied (e.g., "60% coverage", "Tail < TM", "n ≥ 25"); blank otherwise |

Header row: bold, thin black bottom border. No fills. Auto-sized columns. No PPC.

### Tabs 2+ — One tab per sample

**Tab heading**: A1 = bold plain text `<sample name>` (e.g., "Accounts Receivable"). No client/date header block.

**Methodology block** directly below the heading (starting A2 or A3 after a blank row). Plain rows — no PPC labels, no red bold. Just label: value pairs in column A / column B:

```
Method:              [method name]
Sample size (n):     [n]
Population count:    [count after cleanup]
Population $:        [total after cleanup] (or "N/A — attribute test")
Coverage %:          [dollar coverage %] (or "N/A")
Occurrence %:        [n ÷ population count]
TM used:             [value or "N/A"]
Threshold:           [value or "N/A"]
Strata:              [description or "None"]
Random seed:         [seed or "N/A"]
Removals:            [count and reason summary, e.g., "3 items removed: 2 duplicates, 1 out-of-period"]
Substantive gate:    [requirement met, e.g., "60% coverage achieved (62.4%)" — or "N/A"]
```

Blank row after methodology block.

**Population table** with selections highlighted:
- Full cleaned population, all columns
- Selected items highlighted in **yellow** (fill: `FFFF00`)
- Bold headers, thin black bottom border
- Auto-sized columns; `#,##0` / `$#,##0` number format

Column order: a `Selected` indicator column first ("X" for selected, blank otherwise), then all population columns in their natural order.

**No conclusion. No PPC. No Notes.**

---

## Rendering notes

- Use the `xlsx` skill for both workbooks
- Apply user style rules (Aptos Narrow 11, no fills except the yellow selection highlight in File 2, thin black borders on headers only, auto-sized columns) to **both files**
- Surface both files to the user with download links after generation

---

## Shorthand triggers

| User says | Produce |
|-----------|---------|
| "pull me a sample of X" | File 1 only; mention File 2 is available |
| "for the review" / "review file" | File 2 only |
| "both files" / "full output" | Both |
| "dump this" / "plain tab" / "put this on a new tab" | Single-tab sterile data dump in current workbook — no methodology block |
