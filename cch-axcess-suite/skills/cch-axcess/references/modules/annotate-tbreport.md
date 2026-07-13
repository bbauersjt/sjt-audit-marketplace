---
summary: Annotate a TB report (REF column + Notes column / Remarks columns)
leg: wpm
triggers:
  - "add a REF to the TB report"
  - "add a REF2 to [row]"
  - "fill in the REF column on the TB report"
  - "add a note to [row] on the TB report / leadsheet"
  - "annotate the TB report"
  - "put a reference next to [fund/group] on the TB"
  - "clear the REF on [row]"
  - "clear the note on [row]"
  - "add a cross-reference / workpaper reference to [row]"
inputs:
  - "Engagement tab (monkeypatch installed BEFORE the report opens)"
  - "TB report GUID; engagementGuid; clientId; engagementId"
  - "Row identity (fund/group/subgroup name or display label)"
  - "Remarks column number 1..N; comment text"
calls:
  - scripts.leadsheet.tbreport_resolve_report_id
  - scripts.leadsheet.tbreport_row_probe_js
  - scripts.leadsheet.tbreport_post_comment
  - scripts.leadsheet.tbreport_delete_comment
  - scripts.reports.add_remarks_column
status: validated
---
# Module — Annotate TB Report REF/Notes columns (workbench-api)

## Terminology — read this first (firm-specific, causes mis-routing)

The firm runs **TWO parallel leadsheet-annotation protocols** — know which surface the user
is on before writing anything:

- **Protocol A — system-generated leadsheet** (the auto-generated WPM `LeadSheet`, one per
  group on the DEFAULT grouping list; alternate lists get none). WRITE SURFACE = comment
  bubbles and tickmarks (FP-API — `annotate-leadsheet.md`). Those flow ONE WAY onto TB
  reports, where they render read-only in the native `cpComments` / `cpTickMarks` columns.
  Use this protocol whenever the user is filed off a system-generated LeadSheet.
- **Protocol B — TB-report leadsheet (the FIRM DEFAULT).** The firm works off TB-report
  leadsheets, not system-generated leads. This module (`annotate-tbreport.md`) covers this
  protocol. Its writable annotation surface is **TWO editable Remarks columns**, which must
  EXIST on the report (see Step 0):
  - **Remarks_1, named "REF"** — cross-references / index refs / "imm" (immaterial) tags /
    tickmark-style annotations.
  - **Remarks_2, named "Notes"** — free notes. Notes on a TB-report lead go in the Notes
    COLUMN, NOT as bubbles.
  Both columns are visible at a glance — that is what makes them usable for workpaper
  cross-references and review notes alike.
- **The mirror is one-directional and does not carry Notes.** System-lead bubbles/tickmarks
  flow system lead → TB report (read-only). REF/Notes column values do NOT appear on the
  system leadsheet and flow nowhere else — they live on the TB report only. Do not expect a
  REF or Notes write to show anywhere but the TB report.
- **Routing vocabulary (TB-report lead, protocol B):** "REF" / "reference" / "cross-ref" /
  "W/P ref" / "imm" → Remarks_1 "REF". "note" / "comment" (on a TB-report lead) → Remarks_2
  "Notes" — a real editable column, not a bubble.
- **Routing vocabulary (system lead, protocol A):** "comment" / "note" / "tickmark" → a
  bubble via `annotate-leadsheet.md` (FP-API). REF/Notes columns don't exist on a system
  lead.
- **Filed-system-lead rule:** if a system-generated LeadSheet is FILED in the binder, that
  user works off system leads (protocol A) — route ALL annotation asks to bubbles
  (`annotate-leadsheet.md`); REF/Notes columns don't exist there.

## Transport

- **workbench-api is NOT reachable with KC localStorage tokens from the KC tab** — fetch
  AND XHR both fail (status 0). The localStorage-primary pattern does NOT apply here.
- **It IS reachable via injected XHR from the ENGAGEMENT tab** using monkeypatch-captured
  headers (Authorization + all-caps IDToken + locale headers + `traceparent`). Confirmed
  200 on GET and the SPA's own POSTs use the same surface.
- Therefore: leg `wpm` (Step 0) — install `scripts.auth_capture.INSTALL_MONKEYPATCH_JS` in
  the engagement tab BEFORE navigating to the report. The patch dies on every page load,
  and **Refresh Report is a hard reload** — do NOT re-capture on the
  report page; capture from the engagement view, or reuse the already-captured WPM bearer
  (accepted by workbench-api — transport matrix, architecture.md).

## Navigation — deep-link, never tree-walk

Individual TB reports ARE URL-addressable:

```
https://engagement.cchaxcess.com/en-US/engagement/{clientId}/tbreports/{reportGuid}/period/{engagementId}/subsidiaryParentId/0
```

Folder depth is irrelevant — a report filed 3+ levels deep opens the same way. Resolve the
`reportGuid` from the WPM listing / binder map (`tbreports/{int}` rows carry it) or the
`tbreports/{clientId}` GET. Do NOT click down the binder tree and do NOT use the integer id
in the URL (`trialbalance/{int}` errors).

## Procedure

### 0. Existence gate — does the target row exist? (FIRST — before the column preflight)

Per SKILL.md failure discipline, confirm the named target EXISTS before building anything.
The REF you're asked to place sits on a specific row (a group total, subgroup, or fund). If
that group/subgroup/fund isn't on this engagement, the ask is ill-posed — surface it and STOP;
do NOT add a Remarks column or warm anything first.

- Read the report's own rows (the report-data GET, or the grouped TB:
  `scripts.groups.get_trialbalance_grouped_all`, FP leg) and check the named row is present.
  `account.group` / `account.financialSubGroup` / `account.fund` carry the names
  (`endpoints/fp_trialbalance.json` — `subGroup` is always null, never match on it).
- **Not found → STOP and ask:** "there is no '<Cash>' group/subgroup/fund on this TB report —
  did you mean <closest matches>, or should one be added?" Catching it here is the entire
  point of this step. Only once the row is confirmed do you
  proceed to the column preflight.

### 0b. Preflight — REF/Notes columns present? Existing value? (mandatory)

After resolving the report, GET `tbreportedit/{clientId}/{engagementGuid}/{reportGuid}`:

- **No `type:"Remarks"` entries in `reportFormat.columns`** (or `columns: []` = CCH defaults)
  → the report has NEITHER Remarks column. The native `cpComments` column you may see in
  the DOM is NOT a Remarks column and cannot be written via this API. OFFER to add the
  firm-standard pair: `scripts.reports.add_remarks_column(...)` (PATCH
  `/v1/trialbalancereport/editReports`, createReports-shaped body, full columns array) —
  call it once for `name="REF"` and once more for `name="Notes"` (each call appends the
  next free `Remarks_{N}`, `engagementId: clientId` quirk on both). Or stop and tell the
  user to add them in the UI (Edit report → Columns → add remarks column, twice). The page
  must be reloaded after.
- **Only ONE `type:"Remarks"` entry exists** → the report is missing its second column
  (older report, or built before the two-column standard). OFFER to add the missing one via
  `add_remarks_column` with the appropriate `name`.
- **Existing value at the target cell** → prompt the user before overwriting (the POST is a
  silent upsert). Read current values via the row probe or the report data GET.
- Column NAME is irrelevant to the API: `columnId` is positional — `Remarks_1` → columnId 1,
  `Remarks_2` → columnId 2 — and is RENAME-PROOF (a column renamed to "REF" still
  posts columnId 1). Identify the target column by `Remarks_{N}` id, never by header text.
  By firm convention `Remarks_1` = "REF", `Remarks_2` = "Notes", but always confirm against
  the actual `name` field on this report rather than assuming the convention held.

### 1. Resolve the integer reportId (skip if known)

The `tbreportcomment` endpoints address the report by its WPM `documentId` integer
(`tbreports/{int}`). Read it from the WPM listing/binder map. `tbreportedit` does NOT
return a usable `id` field.

### 2. Resolve the row reference (ag-grid DOM probe — the ONE legitimate DOM read)

Scroll the target row into view first (AG Grid virtualizes; unpainted rows probe as
missing). **If the probe returns nothing AFTER the row is scrolled into view and the
Step 0 existence gate passed, the label doesn't match a real row — surface it and STOP;
do not re-probe variant labels in a loop.** The
probe returns `rowType` and ids; map to the POST's `referenceType` by ROW LEVEL:

| Row level | POST `referenceType` | `referenceGuid`? |
|---|---|---|
| Fund row | `Fund` | REQUIRED |
| Group total row (e.g. "5000 Expenditures") | **`FinancialGroup`** | omit |
| Subgroup row | `FinancialSubGroup` | omit |

The native SPA POST for a group-total row carries `referenceType:"FinancialGroup"` and
`referenceId` = the financialGroupId. `400 "Invalid Comment Reference Type"` → you sent the
wrong level for the row (or the raw probe `rowType` string).

### 3. Write (create or edit — both are the same upsert POST)

```python
js = leadsheet.tbreport_post_comment(
        client_id, report_id, client_id,
        column_id=1,                    # positional: Remarks_1="REF". Use 2 for Remarks_2="Notes". Rename-proof.
        reference_id=row_reference_id,
        reference_type=reference_type,  # per the Step-2 LEVEL mapping
        period_id=engagement_id,        # periodId carries the ENGAGEMENT id (naming gotcha)
        comment="E-1",
        headers=captured_headers,       # monkeypatch-captured, incl. traceparent
        reference_guid=reference_guid)  # Fund rows only
# response: {"reportCommentReferenceId": <int>} — store for delete
```

### 4. Delete

`leadsheet.tbreport_delete_comment(client_id, report_id, report_comment_reference_id, column_id, headers)`
→ `DELETE /v1/trialbalancereportcomment/{clientId}/{reportId}/{reportCommentReferenceId}/{columnId}`

### 5. Verify, then tell the user to refresh

Re-GET (200 ≠ applied — architecture.md). REF/Notes changes are not visible until page reload.

## Field-naming gotcha (differs from FP-API)

| API | POST response id field | DELETE path tail |
|---|---|---|
| FP-API (bubble comment) | `commentReferenceId` | `/Annotation/comment/{clientId}/{commentReferenceId}` |
| workbench-api (TB report REF/Notes) | `reportCommentReferenceId` | `/trialbalancereportcomment/{clientId}/{reportId}/{reportCommentReferenceId}/{columnId}` |

## Known failure modes

- Status 0 on every call → you are not on the engagement-tab surface with captured headers
  (KC-tab transport is dead for workbench-api; page reload wiped the monkeypatch).
- `400 "Invalid Comment Reference Type"` → wrong referenceType for the row LEVEL (Step 2).
- Missing `referenceGuid` on a Fund row → POST rejected.
- Write "succeeded" but nothing visible → user hasn't reloaded; or you wrote to a Remarks
  column index that doesn't exist (preflight, Step 0).
- Report won't open from the tree → use the deep-link URL; never tree-walk.

## See also
`references/endpoints/wb_tbreportcomment.json` (REF CRUD + reportId resolution),
`references/endpoints/wb_editreports.json` (add/rename/remove REF column — Step 0),
`references/endpoints/tb_create_report.json` (column object shape),
`annotate-leadsheet.md` (bubbles/tickmarks twin).

<!-- END -->
