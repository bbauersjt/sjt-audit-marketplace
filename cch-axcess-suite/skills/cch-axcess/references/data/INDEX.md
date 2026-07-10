# Reference Data Catalogue

> **GATE — reading reference data is NOT a session.** Pulling a binder template, form catalog,
> group code, or xref table from here gives you *content*, not an initialized platform session —
> it does NOT get you past Step 0. Before the FIRST platform call you still owe Step 0
> (`session-bootstrap.md`) THIS session + the page-context transport (`transport.md`). If reading
> a datum here tempted you to jump straight into `chrome_api_call`/folder-creates and you have
> ALREADY made platform calls without Step 0: **STOP now** — run Step 0 in full, switch to the
> page-context transport, RE-VERIFY BY READ everything written while side-entered (200s may be
> silent no-ops), then resume from the last verified step. (SKILL.md → "Initialization gate".)

Static lookup material that modules and scripts consult: binder templates, form catalogs, group codes, engagement-specific xref tables. **Stored in native editable formats (xlsx for tabular, .md for prose). Modules never inline contents.**

## Storage rules

- **Tabular / lookup** -> xlsx. Edit directly in Excel; scripts read via `openpyxl`.
- **Structured config / schemas / enums** -> JSON in `references/config/` (NOT here - that's skill-wide config, not data).
- **Engagement-specific state** (runtime) -> xlsx written to the **user's working folder** (`{slug}-xrefs.xlsx`, sheets `Form Index`, `Cross-References`, `Decisions Log`), NOT into this read-only install. (This catalogue documents the SCHEMA; the file lives with the user.)
- **Captured raw payloads** (form bundles, screenshots) -> write to user's mounted folder; return the path. Never load into context.
- **Don't load whole sheets into context.** Query the cell/row you need, return the answer, summarize.

## Reading pattern

Use `openpyxl` from scripts. Always strip cell values - source sheets often carry copy-paste whitespace:

\`\`\`python
import openpyxl
wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
ws = wb["<sheet>"]
for row in ws.iter_rows(values_only=True):
    cleaned = [str(c).strip() if c is not None else "" for c in row]
\`\`\`

Script <-> data ownership:

| File | Consumer |
|---|---|
| `binder-template.xlsx` | `scripts/binder_planner.py` (planned future helper); currently read inline by `setup-binder-from-index.md` |
| `binder-program-template-*.xlsx` | `scripts/binder_planner.py` |
| `kc-forms-catalog-rich.xlsx` | `scripts/catalog.py` |
| `engagement-xrefs/*.xlsx` | `scripts/xref.py` |
| `tb-group-codes.xlsx` | (no script yet - referenced by `setup-binder-from-index.md`) |

## Available reference data

### binder-template.xlsx
Firm's DEFAULT binder section list for an FS audit — 2-level structure (wrapper > sections; the old 01/02/03/04 parent tier was removed 2026-06-04, AX-16).
- `Sections` - A=4-digit index, B=clean group name (no index prefix). 30 rows, 0100–9000.
- `About` - structure notes. Deeper nesting is user-specified only (see setup-binder-from-index.md Phase 1 step 5-pre).

### binder-program-template-nonprofit.xlsx
Per-client-type binder-program template for NFP audits. Tabs: `Binder Index` (with condition column G), `Cross-References`, `Recommended Order`, `Port Log`.

### binder-program-template-govt-with-sa.xlsx
Same shape as nonprofit, tailored for Govt with Single Audit.

### binder-program-template-ebp.xlsx
Same shape as nonprofit, tailored for Employee Benefit Plan audits (401(k)/403(b)/DB/H&W). EBP-specific forms: KBA-200 *Plan* Information, COR-201A (ERISA 103(a)(3)(C)) engagement letter, COR-203 Plan Consent, KBA-301E Materiality, KBA-404 Benefit Payments ALC, KBA-405 Investments ALC, KBA-406 Participant Data ALC, KBA-407 Loans/Hardships ALC, AUD-202 EBP Planning, and the AUD-80x EBP audit programs. Defaults to 401(k) DC plan under 103(a)(3)(C) (most common); flags switch to full scope, DB, or H&W. **Planning forms + audit programs only — no testwork/leadsheets.** Programs sit at `[index]-PROG` per the firm's section convention; the leadsheet at `[index]` is added by the auditor when work begins. For the full per-workpaper numbering (lead `XX00`, main `XX01/XX02`, supporting `XX01.1/.2`), see the **AUTHORITATIVE** convention in `references/modules/rename-workpaper-index.md`.

### kc-forms-catalog-rich.xlsx
1,660 KC forms across 6 industry titles with API metadata. Columns: `name`, `description`, `group`, `referenceTag`, `dataBindingKey`, `titleID`, `majorProgramKey`, `rfSettings`, `copySettings`, `updateSettings`.

### tb-group-codes.xlsx
TB group taxonomy: Natural (commercial/NFP) and Governmental columns. Use Govt column when `Funds Setup` button is present in the engagement view.

### seed/KC Forms Binder Index - Govt with SA.xlsx
Reference seed - Nansemond Indian Nation FY2025. Used for porting Govt-flavored templates. **Do not edit.**

### engagement-xrefs/{slug}.xlsx
Per-engagement state.
- `Form Index` - {form_id: assigned_index}.
- `Cross-References` - one row per (source form, referenced form).
- `Decisions Log` - bulk triage rules so the same xref questions aren't re-asked next session.

## Adding new data

When a new reference is needed (commercial / EBP / construction templates, new group taxonomy, etc.):
1. Create the xlsx with the same column shape as the closest existing template.
2. Register it here (filename + purpose + consuming script).
3. Update the consuming `scripts/*.py`.
 the engagement's right sidebar; Natural otherwise. See `setup-binder-from-index.md` Phase 0 for the detection logic.

- `sa-title-forms.tsv` — the 84 forms of the Knowledge-Based Single Audits title (SAS.2024.1, titleGuid 531eb5ad-5eae-4f12-ac51-ea998bb8472e), captured 2026-06-04. Columns: form index | referenceTag | full name | section prefix. Offline fallback for catalog.load_sa_title_forms(); prefer a live GetWorkpaperListForAddForms pull (endpoints/kc_title_library.json).

### fixtures/ — captured live payloads for offline verification (no tokens; do not edit)
- `fixtures/aid201-form-get.json` — full AID-201 form GET (SFRC 401k, 2026-07-08). Proves the nested-row shape: `TypeofNonauditService` = 17 flat objects but 112 rows / 195 fillable fields across `childObjectList` depths 0–3 (field-conventions.md §4 note); regression fixture for `kc.decode_form` → `kc.inventory_form` nested walking.
- `fixtures/aud100-unnecessary-form-diag.json` — AUD-100 `GetWorkpaperDiagnostics` result showing the `type:"Unnecessary KnowledgeCoach Form"` shape (`unnecessaryWorkpaperReferenceTag: AID_200_NONAUD_SERVI_INDEP_CKLST`) that fires when AID-201 is added on a no-nonattest engagement (add-audit-programs.md gotcha; field-conventions.md §5 item 4).

<!-- END -->

