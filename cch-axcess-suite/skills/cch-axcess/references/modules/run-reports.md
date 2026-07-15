---
summary: Run a TB report or a Journal Entry report (AJE/RJE/TJE/PAJE); create TB-report-based leadsheets
leg: wpm
triggers:
  - "run a TB report"
  - "create a trial balance report"
  - "make me a TB workpaper"
  - "generate the TB"
  - "run AJEs"
  - "run journal entries report"
  - "create an AJE workpaper"
  - "make the RJE/TJE/PAJE report"
  - "run JE reports"
  - "create a journal entry report"
inputs:
  - "Engagement tab on engagement.cchaxcess.com"
  - "workbench-api / financialprep-api / WPM headers (shared capture)"
  - "engagement_guid for TB (from scripts.kc.get_binder if unknown)"
calls:
  - scripts.reports
  - scripts.wpm.move
  - scripts.wpm.set_index
status: validated
---
# Module — Run Trial Balance + Journal Entry Reports

> **Index verification & Move body.** Use `scripts.wpm.verify_index(row, object_type)` for display
> indexes and `wpm.move()` for the move body — never hand-pick the index field or hand-assemble
> `folderParentLineItems`. Rules live in architecture.md → `index` vs `documentIndex` and → Move
> payload semantics.

**Triggers:** "run a TB report", "create a trial balance report", "make me a TB workpaper", "generate the TB", "run AJEs", "run journal entries report", "create an AJE workpaper", "make the RJE/TJE/PAJE report", "run JE reports", "create a journal entry report".

## What this does

- Creates Trial Balance or Journal Entry reports via `workbench-api.cchaxcess.com` and files them into Unfiled Reports.
- Moving them into the correct binder folder and assigning a final workpaper index is a separate step using `scripts.wpm.move` + `scripts.wpm.set_index`.

Two report families:

- **Trial Balance** — single POST per report. Supports group filtering (one, several, or all current+future), three detail levels (group / group+sub-group / group+sub-group+account), and the standard settings flags.
- **Journal Entries** — single POST creates N workpapers (one per JE type via `SeparateReports`) or one combined workpaper (via `CombinedReports`). Type set is `{AJE, TJE, PAJE, RJE}`.

## Prerequisites

- **Leg: `wpm` warm (Step 0); Rules 0–3 apply (SKILL.md).** TB/JE report CREATES go to `workbench-api` — engagement-tab monkeypatch-captured headers (incl. `traceparent`); the captured WPM bearer is accepted by workbench-api and FP-API (transport matrix, architecture.md). No KC-token path. FP-API/WPM steps (filing, set_index) take the `"ls:wpm"`/`"ls:fp"` sentinel from any kc-token tab, or the same captured headers. ⚠ Refresh-Report hard-reloads kill the monkeypatch — capture from the engagement view or reuse the captured bearer; never re-capture on a report page.
- `engagement_guid` for TB reports — pull from `scripts.kc.get_binder(...).result.id` if not already known.

## Procedure

### Trial Balance

```python
from scripts import reports

# Optional pre-flight
js = reports.check_tb_report_limit(client_id, hdrs)
js = reports.tb_report_settings(hdrs)              # enum keys

# Discover grouping lists + group IDs (only if filtering)
js = reports.get_grouping_lists(client_id, hdrs)
js = reports.get_financial_groups(client_id, grouping_list_id, hdrs)

# Create — full TB
js = reports.create_tb_report(
    client_id, engagement_id, engagement_guid, "Grouped TB", hdrs,
    report_type="SummaryByGroup",
)

# Create — sliced (single group, account detail + JE detail)
# NOTE: journal_entry_details=True adds JE columns to the report body.
# For LEADSHEETS always pass journal_entry_details=False — the JE detail checkbox
# must be UNCHECKED. See "Leadsheet Batch" section below.
js = reports.create_tb_report(
    client_id, engagement_id, engagement_guid, "Investments", hdrs,
    report_index="1100",
    groups=[755937],
    report_type="AccountDetail",
    journal_entry_details=False,   # UNCHECKED for leadsheets (True = adds JE detail columns)
)

# Fund engagements (govt/NFP) — scope the report's funds:
#   fund_settings=reports.build_fund_settings('all' | 'none' | [fundId, ...])
# Omit (default None) on non-fund engagements. Wire shapes + mode semantics:
# references/config/fund_settings.json.

# Verify
js = reports.list_tb_reports(client_id, hdrs)
# look for the new reportGuid + reportName
```

### Journal Entries

```python
from scripts import reports

# Pre-flight quota check (limit 100/engagement)
js = reports.can_create_je(client_id, hdrs)

# Create — AJEs only
js = reports.create_je_report(
    client_id, engagement_id, "AJEs", hdrs,
    report_index="0901",
    je_types=("AJE",),
)

# Create — all four types as separate workpapers (one POST → 4 reports)
js = reports.create_je_report(
    client_id, engagement_id, "JEs", hdrs,
    je_types=("AJE", "RJE", "TJE", "PAJE"),
    combined=False,
)
# Resulting names: JEs_AJE, JEs_RJE, JEs_TJE, JEs_PAJE

# Or combined into one workpaper (one body produces one report)
js = reports.create_je_report(
    client_id, engagement_id, "All Adjustments", hdrs,
    je_types=("AJE", "RJE"),
    combined=True,
    combined_postfix=None,   # or a custom suffix string
)

# Verify
js = reports.list_je_reports(client_id, hdrs)
```

### File the reports (separate step)

Created reports land in Unfiled Reports (`folder_id = -2`). To file into the binder:

```python
from scripts import wpm
unfiled = wpm.folder_get(client_id, eng_id, -2, hdrs)
# find the new report's locationId and integer reportId from the unfiled listing
# WPM returns rows with: locationId (str), documentId="tbreports/{integer}"
# e.g. {"locationId": "3100799", "documentId": "tbreports/31596", "name": "Notes Receivable Lead"}

# object_id for BOTH move and set_index is "tbreports/{integer}" (NOT "reports/{guid}")
# Using "reports/{guid}" returns 200 but silently no-ops on move.
items = [{"object_type": "Report",
          "own_loc": rpt_loc,
          "dest_loc": destination_folder_loc,
          "object_id": "tbreports/31596"}]   # integer id, not guid
wpm.move(client_id, items, hdrs)
wpm.set_index(client_id, [{"index": "1200", "name": rpt_name,
                            "object_id": "tbreports/31596",   # integer id, not guid
                            "object_type": "Report"}], hdrs)
```

The TB create's `report_index` parameter only stamps the index attribute on the workpaper — it does NOT auto-file. Move + Set-Index is required to place it in a folder.

**objectId gotcha:** Both `wpm.move` and `wpm.set_index` require `objectId = "tbreports/{integer_report_id}"`. Using `"reports/{report_guid}"` returns 200 on move but is a silent no-op — the report stays in Unfiled. The integer report id comes from the create response (`id` field) or from the WPM unfiled listing (`documentId` field).

### Custom columns (TB)

```python
# Build columns explicitly — overrides CCH defaults.
# See references/config/tb_column_types.json for known column types.
cols = [
    {"id": "Unadjusted_PriorPeriod_1", "type": "Unadjusted", "name": "Unadjusted Balance",
     "abbrev": "UNADJ", "variance": None, "order": 1,
     "periodId": prior_period_id, "periodEndDate": "2024-12-31", "isDeleted": False},
    {"id": "Unadjusted_Current", "type": "Unadjusted", "name": "Unadjusted Balance",
     "abbrev": "UNADJ", "variance": None, "order": 2,
     "periodId": engagement_id, "periodEndDate": "2025-12-31", "isDeleted": False},
    {"id": "Aje_Current", "type": "Aje", "name": "Adjusted Journal Entry",
     "abbrev": "AJE", "variance": None, "order": 3,
     "periodId": engagement_id, "periodEndDate": "2025-12-31", "isDeleted": False},
    {"id": "Final_Current", "type": "Final", "name": "Final Balance",
     "abbrev": "FINAL", "variance": None, "order": 4,
     "periodId": engagement_id, "periodEndDate": "2025-12-31", "isDeleted": False},
    # Remarks columns ALSO need engagementId in the column dict (set to clientId — same naming quirk)
]
```

---

### Leadsheet Batch

**▶ TB report vs leadsheet — pick the ReportType deliberately:**
- **TB report** (the whole-TB deliverable) → `report_type="SummaryByGroup"` (group totals). Default.
- **Leadsheet** → DETAIL. `report_type="AccountDetail"` **plus** `include_sum_of_account_groups=True`
  + `hide_unused_groups_and_subgroups=True` + `hide_accounts_with_zero_balances=True`. A leadsheet
  shows accounts under each group with the group subtotal; group-totals-only is wrong for a leadsheet.
- **⚠️ EVERY leadsheet — single or batch — MUST pass `columns=build_leadsheet_columns(...)`.**
  `columns=[]` (CCH defaults) produces a leadsheet with NO Remarks columns — annotation is then
  impossible until they're added. The firm layout is UNADJ/AJE/RJE/FINAL/
  REF/Notes + FINAL-PY — TWO Remarks columns (REF, Notes), firm standard.
  Include the PY column ONLY when a comparative TB exists (prior_period_id +
  prior_end_date); if you can't establish the prior period, ASK the user whether a comparative
  TB is imported rather than silently omitting it.

**⚠️ CRITICAL: Always pass `journal_entry_details=False` for leadsheets.** The default is `True`, which adds JE detail columns and makes the report look like a transaction listing instead of a leadsheet.

Full batch workflow:

```python
from scripts import reports, groups, wpm

# 1. Get financial groups
lists_js = reports.get_grouping_lists(client_id, hdrs)
# run in Chrome -> parse response -> grab the default list id
# e.g. grouping_list_id = 1, list_id = <the financialList id>

groups_js = groups.list_financial_groups(client_id, grouping_list_id, hdrs)
# run in Chrome -> parse response -> all_groups list

# 2. Partition into leadsheet sections
sections = reports.group_by_leadsheet(all_groups)
# Returns: [{"section_index": "1100", "section_name": "Investments", "group_ids": [...]}, ...]

# 3. Build the firm-standard leadsheet columns (6, or 7 with comparative;
#    TWO Remarks columns: REF + Notes)
# current_period_id = engagement_id (e.g. 9900001)
# prior_period_id   = PY engagement_id (e.g. 9900002)
cols = reports.build_leadsheet_columns(
    current_period_id=9900001,
    current_end_date="2025-12-31",
    client_id=9900003,
    prior_period_id=9900002,      # OMIT prior_* when no comparative TB is imported
    prior_end_date="2024-12-31",
)

# 4. Create one leadsheet per section
for section in sections:
    name = f"{section['section_name']} Lead"
    js = reports.create_tb_report(
        client_id, engagement_id, engagement_guid, name, hdrs,
        report_index=section["section_index"],
        groups=section["group_ids"],
        report_type="AccountDetail",          # ← leadsheets are DETAIL, not SummaryByGroup
        include_sum_of_account_groups=True,    # group subtotal lines
        hide_unused_groups_and_subgroups=True, # drop empty groups
        journal_entry_details=False,           # ← MUST be False; True adds JE columns
        columns=cols,
    )
    # run in Chrome -> capture integer report id from response["id"]

# 5. File each leadsheet (reports land in Unfiled, -2)
unfiled_js = wpm.folder_get(client_id, eng_id, -2, hdrs)
# parse locationId and integer documentId ("tbreports/{int}") for each new report

for (rpt_loc, rpt_int_id, section_name, section_idx, dest_folder_loc) in new_reports:
    obj_id = f"tbreports/{rpt_int_id}"   # integer id, NOT guid — see objectId gotcha
    wpm.move(client_id, [{"object_type": "Report",
                           "own_loc": rpt_loc,
                           "dest_loc": dest_folder_loc,
                           "object_id": obj_id}], hdrs)
    wpm.set_index(client_id, [{"index": section_idx,
                                "name": section_name + " Lead",
                                "object_id": obj_id,
                                "object_type": "Report"}], hdrs)
```

**Standard column layout** (`build_leadsheet_columns` output, TWO Remarks columns —
firm standard):

| Order | Abbrev | Name | Type | Period |
|-------|--------|------|------|--------|
| 1 | UNADJ | Unadjusted Balance | Unadjusted | CY |
| 2 | AJE | Adjusted Journal Entry | Aje | CY |
| 3 | RJE | Reclassifying Journal Entry | Rje | CY |
| 4 | FINAL | Final Balance | Final | CY |
| 5 | RM1 | **REF** | Remarks | CY |
| 6 | RM2 | **Notes** | Remarks | CY |
| 7 | FINAL | Final Balance | Final | PY (only if comparative TB) |

NO Adjusted column. TWO Remarks columns are the firm standard for a TB-report leadsheet
(protocol B — see annotate-tbreport.md's two-protocol split): Remarks_1 "REF" for
cross-references/index refs/"imm" tags/tickmark-style annotations, Remarks_2 "Notes" for
free notes. Both are editable columns, not bubble comments. Bubble comments
(annotate-leadsheet.md) remain the write surface for the OTHER protocol — the
system-generated leadsheet — and are never used to satisfy a TB-report note/REF ask.
To retrofit either Remarks column onto an existing report: `reports.add_remarks_column`
(editReports PATCH — see annotate-tbreport.md Step 0), once per missing column.
columnId for Remarks_N is N, positional, rename-proof (Remarks_1 → 1, Remarks_2 → 2).

Both Remarks columns require `engagementId: client_id` in the column dict (CCH naming quirk —
other column types must NOT carry that field).

## Known failure modes

- **400 with `EngagementId` validation error** → path slot got the wrong ID. The URL uses clientId; the body's `engagementId` field also carries clientId. The engagementId rides in `periodId`.
- **`groups=[]` with `includeSelectedGroups=true`** → CCH 200s but creates an empty report. Pass `groups=None` for "all" instead.
- **JE quota exceeded** (`canCreate: false`, limit 100/engagement) → delete old reports first.
- **Stale headers** → 401 with a generic body on workbench-api. Re-run the monkey-patch capture.
- **Custom columns 400** → missing required field on Remarks columns (must include `engagementId`) or stray `engagementId` on non-Remarks columns (must be omitted). See `endpoints/tb_create_report.json` for full column object shape.

## See also (endpoint specs)

- `references/endpoints/tb_create_report.json` — TB report create body
- `references/endpoints/je_create_report.json` — JE report create body
- `references/endpoints/tb_report_settings.json` — TB enum dictionary
- `references/config/fund_settings.json` — `fundSettings` sub-object wire shape for fund engagements
- `references/config/je_types.json` — JE type ID enum (AJE=1, TJE=2, PAJE=3, RJE=4)


<!-- END -->
