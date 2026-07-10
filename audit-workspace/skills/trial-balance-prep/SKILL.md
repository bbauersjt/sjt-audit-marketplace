---
name: trial-balance-prep
description: Prepare any client trial balance for the firm's grouping index and for CCH Axcess import. One skill covering four jobs — (1) import/roll a current-year TB against a prior-year reference (map accounts, assign account numbers and leadsheets, QuickBooks-aware); (2) convert legacy grouping/leadsheet codes to the firm's 4-digit index, driven by a grouped Caseware TB or a copied leadsheet legend; (3) build a CCH-importable file in the right tier (Basic / Grouped / Fund) with correct classifications and sign convention; (4) fund handling — build a fund TB from a Caseware / pasted grouped TB and, if needed, a standalone fund import. When the prior year lives in a CaseWare engagement folder copy, pulls accounts, L/S groupings, funds, and balances via the caseware-crosswalk skill's TB extract instead of asking for pastes or screenshots. Trigger even without the word "skill": "import this trial balance", "match this TB to last year", "roll forward the TB", "assign account numbers", "convert these grouping codes", "update the L/S codes to the new 4-digit index", "remap the legacy leadsheet codes", "format this TB for CCH import", "make this TB importable", "build a grouped/fund TB", "create a fund import", "the client sent their TB in a different format", or a Caseware/QuickBooks TB handed over to be brought onto the firm's index.
---

# Trial Balance Prep

Takes whatever TB a client (or a prior system) hands you and prepares it for the
firm's 4-digit grouping index and for CCH Axcess import. It does four jobs; a run
usually chains a couple of them.

- **A — Import / roll forward** a current-year TB against a prior-year reference:
  map accounts, assign account numbers and leadsheets, reconcile. QuickBooks-aware.
- **B — Convert legacy grouping codes** to the firm's 4-digit index, learning what
  the old codes meant from this client's own legend (a grouped Caseware TB or a
  copied leadsheet group).
- **C — Build a CCH import file** in the right tier (Basic / Grouped / Fund) with
  correct classifications, sign convention, and CCH constraints.
- **D — Funds** — build a fund TB (type › fund) from a Caseware or pasted grouped
  TB, and, if the engagement needs it, a standalone fund import.

## Figure out which jobs this run needs

Read what the user gave you before asking much:

- A QuickBooks TB + a prior-year firm TB → **A**, usually finished with **C**.
- A TB whose grouping/leadsheet column holds old letter/number codes → **B**.
- "Make this importable / format for CCH" → **C** (preceded by A or B if the TB
  isn't mapped/grouped yet).
- Multiple funds, or a governmental / multi-fund client, or a Caseware export →
  **D**, layered onto B/C.

Confirm the plan in one line before doing the work. When the request is
unambiguous (a lone QB TB + PY reference "to import"), just proceed.

## CaseWare source? Extract first — don't ask

If the prior year (or the TB itself) lives in a **CaseWare Working Papers folder
copy** — the user points at one, mentions "the CaseWare file", or a folder in play
contains `*SH.dbf`/`*am.dbf` — do **not** ask for pasted grouped TBs, leadsheet
legends, folder-tree screenshots, or exports. Run the **`caseware-crosswalk`
skill's TB extract** against that folder:

```
python <skills>/caseware-crosswalk/scripts/cw_tb_extract.py "<caseware folder>" [--out DIR]
```

(If `_tb_extract.json` already sits in the folder, just read it.) It supplies,
per account: number, name, L/S code (`leadsheet`), extra groupings (`group2` is
the firm 4-digit index where the file was already converted), fund + fund name,
BS/IS type, and final balances for the file year + 4 prior (`cy_final`,
`py1_final`…). Plus a `funds` list (number, name, master/child) and AJE detail.
Credits are negative — already the CCH sign convention.

Feed it into the jobs:
- **Job A** — the extract *is* the PY reference: match on `account`/`description`,
  inherit `leadsheet`, use `cy_final` as the PY balance column.
- **Job B** — the extract *is* the legend: each unique `leadsheet` code with the
  account names carrying it gives the code's meaning for this client. The
  engagement's `_crosswalk.json` (crosswalk mode of the same skill) names the
  lead documents too — `<code>-LEAD` → "Revenue lead schedule" etc. — use those
  as the code labels when present. If `group2` is already 4-digit, job B may be
  a no-op; verify against the firm index instead of converting.
- **Job D** — the extract's `funds` list is the fund set; account `fund` prefixes
  give the Fund Index. No screenshot needed. Fund *type* layering (general /
  special revenue / enterprise…) is not in the extract — still confirm types
  with the user or the prior FS.

Only fall back to asking when no CaseWare folder copy (with its DBF files) is
available.

## Inputs

1. **The TB to work on** — Excel, `.xlsm`, CSV, TSV, or pasted. Any source system.
2. **A prior-year reference TB** (for job A) — the firm-format structure to match
   against. Used for leadsheet inheritance, rename detection, number recovery.
   The PY balance need not appear in the output. If the user asks to import/roll
   and gives only the CY TB, check for a CaseWare folder copy to extract from
   (see above) before asking for the PY reference.
3. **The legend** (for job B) — a grouped or summary TB for the same client where
   each group row reads `<old code>  <group name>`, or a copied leadsheet group.
   This is how the skill learns what each old code means *for this client*. A
   CaseWare TB extract serves as the legend (see above); otherwise ask for it
   before converting if only the account-level TB was given.
4. **Entity type** — EBP (defined-contribution plan) vs standard (commercial /
   nonprofit / governmental). Drives which grouping index and which sheet.
   Propose from the TB if obvious; confirm before converting.
5. **Fund info** (for job D) — often inferable from the TB or a CaseWare TB
   extract; only ask for a folder-tree screenshot when neither exists (see job D).

## Upfront questions — batch once

Ask only what this run needs, in a single prompt:

1. **Output** — CCH import file (which tier: Basic / Grouped / Fund), the firm's
   sterile 4-column file, or a review workpaper?
2. **Client name, workpaper name, date of financials** — only for workpaper output.
3. **Leadsheet assignment** (job A) — carry PY L/S codes forward? A common
   preference: "carry and propose, but don't bother flagging obvious ones."
4. Whether a **prior-year client-format TB** is available for amount-based
   disambiguation (job A).
5. **Period** of the current-year TB (full year, interim, specific date).
6. For a multi-fund engagement: **does it also need a standalone fund import?**

---

## Job A — Import / roll forward against a prior-year reference

### A1. Inspect both TBs
Read both files first and report a compact structure summary before writing
anything. For each: account numbers present? numbering ranges by type? a
leadsheet column (`Leadsheet`/`L/S`/`Lead`/`LS`)? grouping? single balance vs
Dr/Cr? sign convention (are liab/equity/revenue negative or positive)? subtotal
/ header / footer rows mixed in?

**QuickBooks specifics:**
- Numbers are often embedded in the name string (`11111 BkAm Checking`, or
  `11100 BANK ACCOUNTS:11111 BkAm Checking`). Parse the leaf with
  `^(\d{4,6})\s+(.*)$`.
- Rows are nested colon paths (`Parent:Child:Leaf`). Zero-balance rollup parents
  are display artifacts — drop them. A parent row *with* a balance is either a
  legit sub-account parent (PY had it too — normal) or a true misposting to a
  rollup (new — concerning). Tell them apart by whether PY had that account with
  a balance.
- QB TBs usually have separate Dr/Cr columns → signed balance = `debit - credit`.

Flag any imbalance immediately (does the balance column sum to zero?).

### A2. Map accounts (priority order)
1. Exact account-number match (highest confidence even if names differ).
2. Exact name match (case-insensitive, trimmed, normalized).
3. High-confidence fuzzy name match ("Accts Receivable" ↔ "Accounts Receivable").
4. Amount-based disambiguation via a PY client-format TB, if provided.
5. Name match for unnumbered CY rows → recover the PY number.

Record for each: source row, matched PY # and name, method, confidence.
Unmatched → new-accounts list (A3).

**Renames — defer to CY, flag only category jumps.** When CY matches PY by number
but names differ, use the CY name silently. Flag only renames that cross
Asset / Liability / Equity / Revenue / Expense / Payroll boundaries given the
number's range (e.g. a 59xxx payroll account renamed to "Professional Fees").
Within-type renames are silent.

**Absurdly nested names — ask.** If the CY QB path is 4+ levels deep and PY had a
clean single-level name, pause and ask: keep full path / use CY leaf / use PY
name. For 1–3 level paths that de-path cleanly, just take the leaf.

### A3. Assign account numbers to new accounts
For truly-unnumbered CY accounts (no embedded number, no PY name match): infer the
type from the name, find the best sub-range, assign the next free number, log the
rationale. If no sub-range fits or it's full, pause and propose. A CY account that
arrived *with* a number but has no PY match is a new client-numbered account — use
their number, log as client-provided.

### A4. Assign leadsheets (if opted in)
Mapped accounts inherit the matched PY leadsheet. New accounts take the leadsheet
of neighbors in the same sub-range (±100 / ±500): unanimous → silent; dominant
(≥67%) → propose with rationale; mixed → propose the plurality and surface it.
If PY had no leadsheet column but the user wants leadsheets, ask for a mapping.
Log every assignment.

---

## Job B — Convert legacy grouping codes to the 4-digit index

The firm switched grouping indexes. Old balance-sheet leads were single/double
letters (`A` assets, `AA`/`BB`/`SS` liabilities & equity); income-statement leads
were 1–2 digit numbers (`10` revenue, `40` expenses), sometimes with sub-codes
(`B.1`). The new index is 4-digit (`1000`, `1100`, `2000`…).

**Context-driven, never a fixed table.** The old codes were never applied
consistently across clients — the same letter means different things on different
engagements. Every run is grounded in *this client's own legend*. There is no
master old→new table and you must never build one as if permanent. The convention
table at the end is only a weak fallback for when no legend exists.

### B1. Detect the code format
`python scripts/tb_io.py inspect "<TB>" ["<legend>"]` lists the unique codes and
classifies the column:
- **new** — all 4-digit → already converted; say so and stop.
- **legacy** — letters / 1–2 digit / sub-codes → proceed.
- **mixed** — both styles or unrecognized values → do not auto-resolve; list the
  offending rows and ask how to proceed.
- **empty** — nothing to convert.

### B2. Build the legend (old code → meaning)
The script parses the grouped/summary TB into `{old_code: label}` best-effort.
**Always open the legend yourself and confirm it** — a mislabelled code poisons the
match. Per unique code, take the meaning from: the parsed label → else the account
names carrying that code → else mark unresolved.

### B3. Convert by code (not by row)
Every account sharing an old code gets the same new index. Load the right index
(`load_index()`; for EBP drop the `6000`/`9000` audit rows; for standard pick
`Natural` or `Governmental`). For each unique code, match its meaning against the
index `Group Name`:
- single clear winner → assign it (high);
- several plausible → pick closest, record alternatives (medium, surface);
- none fit but the meaning clearly sits in a range → generate the next free code
  in that range (medium, surface);
- meaning/range unclear → unresolved (low, surface).

The matched Group Name is **sticky** — it becomes the new index's description.
Sub-codes (`B.1`) each expand to their own 4-digit code within the parent's range.
Never reuse a 4-digit code for two meanings in one run.

---

## Job C — Build the CCH import file

Read `references/cch-import-formats.md` for the full column specs and constraints.
Summary:

**Pick the tier:** **Basic** (account #, name, balance), **Grouped** (+ PY, group
& subgroup index/name, classification), or **Fund** (+ Fund Index). Each is a
superset of the one above.

**Classification** — the 10-way column (`CA NA CL NL EQ REV COR OI OPX OE` from
`default-classes.xlsx`). The grouping index only carries a coarse class, so
resolving it needs two judgment calls it does not store: **current vs non-current**
(every asset & liability) and **operating vs cost-of-revenue vs other** (every
income-statement line). `tb_io.guess_class(coarse, group_name, account_name)`
returns a `(abbrev, confidence, note)` hint; confirm anything below `high`. Never
write a value that isn't in `default-classes.xlsx`.

**Hard constraints** (violate one and the import fails):
- No freeze panes (silent reject). Header in row 1, nothing above it.
- Single balance column; **debits positive, credits negative**.
- Unique account names; account number stays text (leading zeros / dash prefixes).
- Accounting number format on balances; balances net to zero (per fund too).

`tb_io.write_cch_import(out_path, tier, rows)` bakes every constraint in and
returns `{tier, rows, total, by_fund}` — check `total` (and each `by_fund`) is
`0.00` before delivery.

---

## Job D — Funds

Produce the **Fund** tier when the engagement has multiple funds. The two Caseware
grouping layers map to **type › fund** (outer folder = fund type, inner = fund).

### D1. Determine the Fund Index — infer, then confirm
`tb_io.scan_fund_patterns(accounts)` reports the dominant pattern, fund set, and
coverage. Sources, in order of what you were given:
1. **CaseWare TB extract** — if a CaseWare folder copy exists, the extract's
   `funds` list (number + name) and per-account `fund` column ARE the fund set
   and Fund Index. Use them; don't ask.
2. **Account-number pattern** — `100-10000` (prefix) or `10000-100` (suffix). High
   coverage + one consistent pattern → proceed, stating what you inferred.
3. **Fund names on the TB** — some client TBs name the fund in a column or in the
   account name instead of the number. Map each name to an index with the user.
4. **Comparative / pasted Caseware TB** — if the user gave a grouped or pasted
   Caseware TB, infer the fund from it too.
5. **Caseware folder tree screenshot** — last resort, only when no folder copy
   with DBFs exists: ask the user for a screenshot of the tree, then read the
   two layers as type › fund.

Match confidence to behavior: confident → state the inference and proceed;
uncertain → confirm; no signal → ask upfront. Don't invent a fund silently.

### D1a. Drop dormant funds — always, for anything imported into CCH
Legacy files (CaseWare especially) carry years of dead funds. Before writing any
CCH deliverable, run `tb_io.drop_dormant_funds(rows)`: it drops every fund whose
accounts are **all zero in both the CY balance and the PY balance**, and returns
the dropped fund indexes. A fund with zero CY but real PY amounts survives — its
comparative is live. Dormant funds also stay out of the standalone fund import
(D2). Don't ask permission; just report the dropped funds in one line of the run
summary ("dropped N dormant funds: 003, 016, …") so nothing vanishes silently.
This is an import rule only — extracts, crosswalks, and review workbooks still
show everything.

### D2. Standalone fund import (ask)
Always ask whether the engagement also needs a **fund import** — 4 required columns:
Fund Type Index / Fund Type Name / Fund Index / Fund Name. From a CaseWare TB
extract this builds itself: the `funds` list carries the consolidation hierarchy
(root/master/child + `fund_type`), and CaseWare's two layers map onto CCH's two —
masters → fund types, children → funds:

```python
conv = tb_io.funds_from_cw_extract(extract["funds"])
tb_io.write_fund_list(out_path, conv["rows"])
```

Surface `conv["warnings"]` — orphan funds (no master in CaseWare) get promoted to
their own fund type; ask whether to re-home them (e.g. several special-revenue
funds under one type). Without a CaseWare extract, gather types/funds from the TB
or prior FS and build the rows by hand.

---

## Outputs

- **CCH import** (Basic / Grouped / Fund) — sterile, via `write_cch_import`. The
  primary deliverable for "import into CCH". No decoration, no extra sheets.
- **Firm sterile file** — the older 4-column layout `L/S | Account # | Account
  Name | Balance (CY)`, sorted ascending by number, non-zero rows only, balances
  netting to `0.00`. Use when the user asks for the firm's plain import file
  rather than a CCH-tier file.
- **Grouping-conversion review** (job B) — `write_output()` writes a decorated
  three-sheet workbook: **Code Map** (old code → new index, meaning, class,
  source, confidence, notes), **Converted TB** (per account, with a TOTAL), and
  **Conversion Log**. This is the reviewable deliverable, distinct from the sterile
  import file.
- **Workpaper** (job A, on request) — follows firm workpaper standards: plain
  header block (client / workpaper name / date, bold black), underlined bold
  section headings (no fills, no borders otherwise), bold-red `Purpose:` /
  `Procedure:` / `Conclusion:` / `Note1:` labels **only when the user confirms
  workpaper mode**. Sheets: Trial Balance (L/S, Acct#, Name, PY, CY, Variance,
  Var %), Reconciliation Log, New Accounts, Exceptions.
- **Fund import** (job D, on request) — `funds_from_cw_extract()` + `write_fund_list()`.

## Surface ambiguities — batch, then finalize

Collect uncertain calls into one prompt before writing output. Surface: name
matching two PY accounts equally; ambiguous account type; exhausted numbering
range; a material PY balance with no CY match (possible closure or miss — zero-in-
PY-and-absent is noise, log don't surface); Dr ≠ Cr; sign-convention flip;
category-crossing rename; absurd nesting vs shortened PY name; new misposted parent
balance; legacy codes with no confident meaning; meanings that matched several or
no Group Names; sub-codes split without a clear distinction; a meaning that crosses
a statement boundary (likely a bad legend); low-confidence classifications; and any
fund that could not be inferred confidently. No silent guesses below high confidence.

## Calling the script

`scripts/tb_io.py` is pure Python (`openpyxl` only). It moves data and enforces
mechanical rules; the semantic decisions are yours.

```python
import sys; sys.path.insert(0, "<skill>/scripts")
from tb_io import (load_tb, load_legend, load_index, detect_format,
                   load_classes, guess_class, scan_fund_patterns, infer_fund,
                   drop_dormant_funds, write_cch_import, funds_from_cw_extract,
                   write_fund_list, write_output)

tb      = load_tb("<CY TB>")
classes = load_classes("<skill>/references/default-classes.xlsx")
index   = load_index("<skill>/references/standard-group-codes.xlsx", sheet="Governmental")

# build `rows` from your mapping/conversion decisions, then:
rows, dropped = drop_dormant_funds(rows)        # fund tier: dump dead funds; report `dropped`
res = write_cch_import("<out>/Fund TB import.xlsx", "fund", rows)   # check res["total"] == 0.0
```

Quick inspection from bash: `python scripts/tb_io.py inspect "<TB>" ["<legend>"]`
(prints code format, unique codes, parsed legend, and fund inference).

## Old-code conventions (fallback prior only — the legend always wins)

| Old code shape | Likely concept | Range |
|---|---|---|
| `A` | Cash | 1000 |
| `B` | Receivables | 1200 (standard) / 1300 (EBP contributions receivable) |
| `N` | Investments | 1100 |
| `L` | Prepaids | 1400 (standard) |
| `U` | PP&E / capital assets | 1500 (standard) |
| `O` | Other assets | 1600 (standard) / 1400 (EBP) |
| `AA` | Long-term debt | 2400 (standard) |
| `BB` | Payables | 2000 |
| `CC` | Accrued liabilities | 2100 (standard) / 2000 (EBP) |
| `RR` | Deferred revenue | 2200 (standard) |
| `SS` | Equity / net assets / fund balance | 3000 |
| 1–2 digit, low prefix (`10`–`19`) | revenue / additions | 4xxx |
| 1–2 digit, mid/high (`20`+, `40`+) | expense / deductions | 5xxx (EBP) / 5xxx–6xxx (standard) |
| `.1` / `.2` suffix | subgroup of the parent | expand within the parent range |

EBP note: old EBP income-statement codes are idiosyncratic — `10`s are additions,
`40`s are deductions, `20`s vary. Lean on the legend.

## Critical rules

- **The legend is the source of truth**; the convention table is only a fallback.
- **Convert by code, not by row.** Never invent a permanent old→new table.
- **Never write to `references/`** — the index, class list, and CCH example files
  are hand-maintained.
- **Classification only from `default-classes.xlsx`.** Confirm sub-`high` guesses.
- **CCH imports: no freeze panes, header row 1, debits positive, balances net to
  zero (per fund).** `write_cch_import` enforces these — don't undo them.
- **Never guess a fund silently** — infer and confirm. With a CaseWare folder
  copy, the caseware-crosswalk TB extract is the fund source; only ask for a
  tree screenshot when no DBFs exist.
- **No silent low-confidence guesses** anywhere — batch them for the user.

## Validation checklist before delivery

- [ ] Balance column nets to `0.00` (±$0.01), and per fund for a fund import.
- [ ] Every row has an account number (or it's flagged for manual assignment).
- [ ] Every row has an L/S code (if leadsheet mode) / group + subgroup + class
      (if grouped/fund tier).
- [ ] Classifications all appear in `default-classes.xlsx`.
- [ ] CCH import file: `ws.freeze_panes is None`, header in row 1, account numbers
      are text, debits positive.
- [ ] No zero-balance rows in a sterile import.
- [ ] Fund tier: dormant funds dropped (`drop_dormant_funds`), the dropped list
      reported, and the fund import limited to surviving funds.
- [ ] Category-crossing renames, misposted parents, and low-confidence
      conversions/classifications surfaced.
