---
summary: Annotate a TB report (REF column / Remarks columns)
leg: wpm
triggers:
  - "add a REF to the TB report"
  - "add a REF2 to [row]"
  - "fill in the REF column on the TB report"
  - "annotate the TB report"
  - "put a reference next to [fund/group] on the TB"
  - "clear the REF on [row]"
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
status: validated (transport + columnId + referenceType live-captured 2026-06-04)
---
# Module — Annotate TB Report REF/Remarks columns (workbench-api)

## Terminology — read this first (firm-specific, causes mis-routing)

- **Firm "leadsheet" = a TB report** (`Report` type, AccountDetail) that the firm generates
  and files. Its ONLY writable annotation is the **REF column** — a `Remarks`-type column
  that must EXIST on the report (see Step 0). REF text is visible at a glance — that is
  what makes it usable for workpaper cross-references.
- **System leadsheet = the auto-generated WPM `LeadSheet`** (one per group on the DEFAULT
  grouping list; alternate lists get none). It is the WRITE SURFACE for comment bubbles and
  tickmarks (FP-API — `annotate-leadsheet.md`). Those flow ONE WAY onto TB reports, where
  they render read-only in the native `cpComments` / `cpTickMarks` columns.
- **REF values do NOT appear on the system leadsheet.** The mirror is one-directional
  (system lead → TB report). Do not expect a REF write to show anywhere but the TB report.
- **Routing vocabulary:** "REF" / "reference" / "cross-ref" / "W/P ref" → THIS module.
  "comment" / "note" / any bubble language → `annotate-leadsheet.md` (FP-API). Never
  create a "Notes" Remarks column to satisfy a comment ask.
- **Filed-system-lead rule:** if a system-generated LeadSheet is FILED in the binder, that
  user works off system leads (they don't generate TB-report leadsheets) — route ALL
  annotation asks to bubbles (`annotate-leadsheet.md`); REF columns don't exist there.

## Transport (live-captured 2026-06-04 — supersedes all prior claims)

- **workbench-api is NOT reachable with KC localStorage tokens from the KC tab** — fetch
  AND XHR both fail (status 0). The localStorage-primary pattern does NOT apply here.
- **It IS reachable via injected XHR from the ENGAGEMENT tab** using monkeypatch-captured
  headers (Authorization + all-caps IDToken + locale headers + `traceparent`). Confirmed
  200 on GET and the SPA's own POSTs use the same surface.
- Therefore: leg `wpm` (Step 0) — install `scripts.auth_capture.INSTALL_MONKEYPATCH_JS` in
  the engagement tab BEFORE navigating to the report. The patch dies on every page load,
  and **Refresh Report is a hard reload** (TT1-2 terminal wall) — do NOT re-capture on the
  report page; capture from the engagement view, or reuse the already-captured WPM bearer
  (accepted by workbench-api — validated 2026-06-05; transport matrix, architecture.md).

## Navigation — deep-link, never tree-walk (live-captured 2026-06-04)

Individual TB reports ARE URL-addressable:

```
https://engagement.cchaxcess.com/en-US/engagement/{clientId}/tbreports/{reportGuid}/period/{engagementId}/subsidiaryParentId/0
```

Folder depth is irrelevant — a report filed 3+ levels deep opens the same way. Resolve the
`reportGuid` from the WPM listing / binder map (`tbreports/{int}` rows carry it) or the
`tbreports/{clientId}` GET. Do NOT click down the binder tree and do NOT use the integer id
in the URL (`trialbalance/{int}` errors — that was BT3's dead end).

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
  did you mean <closest matches>, or should one be added?" This is the TT1 failure class;
  catching it here is the entire point of this step. Only once the row is confirmed do you
  proceed to the column preflight.

### 0b. Preflight — REF column present? Existing value? (mandatory)

After resolving the report, GET `tbreportedit/{clientId}/{engagementGuid}/{reportGuid}`:

- **No `type:"Remarks"` entry in `reportFormat.columns`** (or `columns: []` = CCH defaults)
  → the report has NO REF column. The native `cpComments` column you may see in the DOM is
  NOT a REF column and cannot be written via this API. OFFER to add one:
  `scripts.reports.add_remarks_column(...)` (PATCH `/v1/trialbalancereport/editReports`,
  createReports-shaped body, full columns array; new column = `Remarks_{N}`, name "REF",
  `engagementId: clientId` quirk). Or stop and tell the user to add it in the UI
  (Edit report → Columns → add remarks column). The page must be reloaded after.
- **Existing value at the target cell** → prompt the user before overwriting (the POST is a
  silent upsert). Read current values via the row probe or the report data GET.
- Column NAME is irrelevant to the API: `columnId` is positional — `Remarks_1` → columnId 1,
  `Remarks_2` → 2 — and is RENAME-PROOF (captured: column renamed to "REF" still posts
  columnId 1). Identify the target column by `Remarks_{N}` id, never by header text.

### 1. Resolve the integer reportId (skip if known)

The `tbreportcomment` endpoints address the report by its WPM `documentId` integer
(`tbreports/{int}`). Read it from the WPM listing/binder map. `tbreportedit` does NOT
return a usable `id` field.

### 2. Resolve the row reference (ag-grid DOM probe — the ONE legitimate DOM read)

Scroll the target row into view first (AG Grid virtualizes; unpainted rows probe as
missing). **If the probe returns nothing AFTER the row is scrolled into view and the
Step 0 existence gate passed, the label doesn't match a real row — surface it and STOP;
do not re-probe variant labels in a loop (that is the 2-fail path, not progress).** The
probe returns `rowType` and ids; map to the POST's `referenceType` by ROW LEVEL
(live-captured 2026-06-04 — the old blanket Group→FinancialSubGroup mapping is WRONG):

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
        column_id=1,                    # positional: Remarks_1. Rename-proof.
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

Re-GET (200 ≠ applied). REF changes are not visible until page reload.

## Field-naming gotcha (differs from FP-API)

| API | POST response id field | DELETE path tail |
|---|---|---|
| FP-API (bubble comment) | `commentReferenceId` | `/Annotation/comment/{clientId}/{commentReferenceId}` |
| workbench-api (TB report REF) | `reportCommentReferenceId` | `/trialbalancereportcomment/{clientId}/{reportId}/{reportCommentReferenceId}/{columnId}` |

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
