---
summary: Build a CCH-importable trial balance file (column spec, sign convention, import constraints)
triggers:
  - "format this TB for CCH import"
  - "make this trial balance importable"
  - "CCH rejected my TB import"
  - "build a CCH import file"
  - "TB import format"
leg: none
inputs:
  - "Account data (numbers, names, balances; fund column if fund TB)"
  - "A real CCH TB export from the same engagement (ground truth for columns)"
calls: []
status: wip
---
# Module — CCH TB Import Format

## What this does

- Documents what CCH Axcess will and will not accept when importing a trial balance from Excel, so import files are built from known constraints instead of improvised.

## Known constraints

- **No freeze panes — hard reject.** CCH silently rejects any workbook with
  `freeze_panes` set. Never add them to an import file, even as "good practice".
- **No title/decoration rows.** Header row, then data. Nothing above the header.
- **Sign convention: DEBITS POSITIVE, CREDITS NEGATIVE** — the standard TB convention,
  and what CCH TB exports/imports actually use.
  Separately, the **FP-API trialbalance endpoint serves balances
  credits-positive** (`endpoints/fp_trialbalance.json`) — that is API-internal
  convention, NOT the import convention. Building an import file from API rows
  requires a sign flip. Do not conflate the two again.
- **Single balance column** (not separate Dr/Cr columns).
- **Unique account names** required.
- **Accounting number format** on the balance column; plain text on account number
  (leading zeros survive).
- Fund TBs carry the fund as part of the account-number prefix structure — see
  `manage-funds.md` for the fund hierarchy the numbers must match.

## Column spec + classification (captured in trial-balance-prep)

The firm's importable TB layout and the classification vocabulary are captured in the **`trial-balance-prep`** skill:

- **Column order/headers** — three tiers (Basic / Grouped / Fund) in
  `trial-balance-prep/references/cch-import-examples.xlsx`, documented in that
  skill's `references/cch-import-formats.md`. Mirror the tier the engagement needs.
- **CLASSIFICATION valid values** — the firm's 10-way list:
  `CA NA CL NL EQ REV COR OI OPX OE` (`trial-balance-prep/references/
  default-classes.xlsx`). These ARE the accepted abbreviations. They map onto the API's
  `accountTypeClassificationId` in `references/config/group_account_types.json`
  (1=Current Assets=CA, 2=Non-Current Assets=NA, 3=Current Liabilities=CL, …).
- Still confirm against a **real export from the target engagement** when one exists
  — a specific engagement's export can carry extra columns (e.g. merged date
  sub-rows) beyond these tiers.
- `trial-balance-prep` builds the import file (`tb_io.write_cch_import`); a CCH-side `generate_import_file()` here remains optional.

## Procedure

### 1. Get ground truth
Export the TB from the target engagement (or have the user provide a prior export).
That file IS the column spec — mirror headers and order exactly. Sanity-check its signs:
debits positive. If an export shows credits-positive, suspect a prior inverted import
and raise it with the user before mirroring anything.

### 2. Build the file
`xlsx` skill; apply every Known constraint above. No freeze panes, no extra rows.
If sourcing balances from the FP API (`tb-backup-package.md` does this), FLIP the sign.

### 3. Verify before handoff
Re-open the produced file: check `ws.freeze_panes is None`, header row is row 1,
balances net to zero per fund and in total, debits positive.

## Known failure modes

- **Silent rejection on import** → freeze panes present → remove `ws.freeze_panes`.
- **Import succeeds, balances inverted** → signs taken from the FP API (credits-positive)
  or from an export that was itself imported inverted → flip to debits-positive and
  re-verify against source documents, not against the tainted export.
- **"Class"/classification values rejected** → values were invented (the valid list is
  uncaptured) → pull the list from a real export; flag for the next rebuild.

## See also

- `endpoints/fp_trialbalance.json` — FP-API row schema incl. the credits-positive note.
- `references/config/group_account_types.json` — API classification IDs (not import strings).
- `manage-funds.md` — fund hierarchy that fund-TB account numbers must match.
- The firm's `trial-balance-prep` skill — builds the CCH import file (Basic /
  Grouped / Fund tiers), converts legacy grouping codes, assigns classifications,
  and handles funds. Holds the captured column spec and class vocabulary.

<!-- END -->
