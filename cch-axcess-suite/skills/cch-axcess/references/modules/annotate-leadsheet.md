---
summary: Annotate a system leadsheet (comment box, inline comments, tickmarks)
leg: wpm
triggers:
  - "add a comment to the leadsheet"
  - "add an inline comment to [account]"
  - "add a tickmark to [account]"
  - "clear tickmarks on [account]"
  - "annotate the [X] leadsheet"
  - "update the comment box on [leadsheet]"
inputs:
  - "KC tab on knowledgecoach.cchaxcess.com (preferred — tokens confirmed for FP-API) OR engagement tab with auth_capture monkey-patch"
  - "clientId; periodId"
  - "Section name or financialGroupId (e.g. Payables / 726342)"
  - "Account number (e.g. 20000-300) or 'comment box' for top-level; comment text or tickmark IDs (1-71)"
calls:
  - scripts.leadsheet.get_groups
  - scripts.leadsheet.get_leadsheet
  - scripts.leadsheet.find_reference_id
  - scripts.leadsheet.patch_comment_box
  - scripts.leadsheet.post_account_comment
  - scripts.leadsheet.delete_account_comment
  - scripts.leadsheet.post_tickmarks
status: validated
---
# Module — Annotate Leadsheet (financialprep-api)

## What this does

Adds, edits, or removes the annotation types on a **system-generated** CCH Axcess
leadsheet: the top-level comment box, inline comments (account-level AND group-level), and
tickmarks. All via `financialprep-api.cchaxcess.com`. (TB-report REF columns are a
different API — see `annotate-tbreport.md`.)

## Terminology + routing (firm-specific — prevents mis-routing)

- The system leadsheet is the WRITE SURFACE for bubbles/tickmarks; they flow ONE WAY onto
  the firm's TB-report leadsheets (render read-only there in `cpComments`/`cpTickMarks`).
  REF column values flow NOWHERE — they live on the TB report only (`annotate-tbreport.md`).
- **Routing vocabulary:** "comment" / "note" / bubble language → THIS module.
  "REF" / "reference" / "cross-ref" / "W/P ref" → `annotate-tbreport.md`. Staff use
  comment/note interchangeably — both mean a bubble, never a Remarks column.
- **Filed-system-lead rule:** if a system LeadSheet is FILED in the binder, that user works
  off system leads — route ALL their annotation asks here (REF columns don't exist for them).
- System leads auto-generate from the DEFAULT grouping list only — alternate group lists
  (common for analytics) have NO system leads, so bubbles for those rows can only be
  written via the default-list lead that contains the account, if any.
- System-lead deep-link: `https://engagement.cchaxcess.com/en-US/engagement/{clientId}/reports/{engagementId}/leadsheets/{financialGroupId}`

## Prerequisites

- **Auth: pass `headers="ls:fp"` to every builder** — runtime localStorage self-sourcing,
  works from a KC tab OR the engagement tab, XHR transport, no monkeypatch (AX-26).
- `clientId`, `periodId`, and the target `financialGroupId` (look it up with `get_groups` if unknown).
- FALLBACK only (no KC tokens reachable): engagement tab with
  `scripts.auth_capture.INSTALL_MONKEYPATCH_JS` installed + one captured FP-API/WPM XHR, then
  `scripts.auth_capture.headers_from_capture(captures, 'financialprep-api')`.

> **Auth note:** pass `headers="ls:fp"` to every builder (runtime localStorage
> self-sourcing — AX-26; works from KC tab AND engagement tab, XHR transport, no
> monkeypatch). Captured-header dicts remain supported. See architecture.md transport matrix.

## Procedure

### 1. Resolve the account referenceId (skip for the comment box)

```python
from scripts import leadsheet, http_runner
js = leadsheet.get_leadsheet(client_id, financial_group_id, period_id, headers)
# -> run in tab via javascript_tool, then:
res = http_runner.parse_result(result_str)
ref_id = leadsheet.find_reference_id(res["body"], "20000-300")   # -> 7358153
```

`referenceId` is `account.id` (a CCH-internal integer), never the account-number string.

### 2-pre. Existing-annotation check (NEW — mandatory before any comment write)

The comment POST is a SILENT UPSERT — it replaces an existing comment without warning.
Before writing, check `row.account.annotation.comment` (or the group row's annotation) in
the `get_leadsheet` response; if non-empty, PROMPT the user with the current text before
overwriting.

### 2a. Inline account comment (create / edit — same call upserts)

```python
js = leadsheet.post_account_comment(client_id, ref_id, period_id, client_id, "W/P 2000-A", headers)
# response body: {"commentReferenceId": <int>} — keep it if you may delete later
```

### 2a-group. Group-level comment (total line) — live-captured 2026-06-04

Bubbles also attach to GROUP rows (e.g. the bold "Total Assets" line):
same POST with `referenceType:"FinancialGroup"` and `referenceId` = the financialGroupId.

```python
# body shape: {"comment": "...", "referenceId": <financialGroupId>,
#              "referenceType": "FinancialGroup", "periodId": <engagementId>,
#              "engagementId": <clientId>}
```
`post_account_comment` hardcodes `referenceType:"Account"` — pass/extend for group rows
(`reference_type` param added in AX-26).

### 2b. Delete an inline comment

(Delete live-confirmed 2026-06-04: `DELETE /v1.0/Annotation/comment/{clientId}/{commentReferenceId}` → 200.)

```python
js = leadsheet.delete_account_comment(client_id, comment_reference_id, headers)
```

### 2c. Top-level comment box (write / clear)

```python
js = leadsheet.patch_comment_box(client_id, 1, period_id, financial_group_id, "See W/P 2000.", headers)
# comment="" clears it
```

### 2d. Tickmarks (set-replace)

```python
js = leadsheet.post_tickmarks(client_id, ref_id, period_id, client_id, [1, 40], headers)
# ids = the COMPLETE desired set; [] clears all. IDs from config/tickmark_ids.json
```

### 3. Verify, then tell the user to refresh

Re-read with `get_leadsheet` to confirm writes. Annotations land under `row.account.annotation`:
```python
# confirmed response shape (2026-06-03):
row["account"]["annotation"] = {
    "tickMarkIds": [1, 40],          # set-replace, [] = none
    "commentReferenceId": 42718,     # from post_account_comment response
    "comment": "T10 inline comment"  # inline account comment text
}
```
Top-level comment box is at `response_body["comments"]["comments"]` (nested key).

> **Tell the user to refresh the page** — annotation changes are not visible until reload.

## Known failure modes

- `No captures match 'financialprep-api'` → no FP/sibling XHR fired yet → navigate to any leadsheet first.
- Account not found → confirm the exact number from `get_leadsheet`; CCH uses a 5-digit prefix (`20000-300`, not `2000-300`).
- Tickmark `ids` is the complete set, not a delta — sending `[1]` when `[1,2]` were set removes mark 2.

## Validated on

- Test binder, client 100173 / eng 390765, 2026-06-03 (T10).
  - get_groups: 200, returns [{financialGroupId, name, number}]
  - get_leadsheet: 200, annotations under `row.account.annotation`
  - patch_comment_box: 200, body `{"result":"Successfully updated Comments","leadSheetComments":{...}}`
  - post_account_comment: 200, body `{"commentReferenceId": 42718}`
  - post_tickmarks: 200, empty body
  - delete_account_comment: 200

## Known gaps

- Workpaper-reference annotation (the third native annotation type) — endpoint not yet captured.
- `commentReferenceId` isn't cleanly surfaced by the leadsheet GET — get it from the POST response in-session.

<!-- END -->
