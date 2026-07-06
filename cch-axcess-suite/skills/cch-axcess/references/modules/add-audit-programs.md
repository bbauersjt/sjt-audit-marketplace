---
summary: Add the audit programs for an engagement (NFP/Govt/EBP); file leadsheets
leg: kc
triggers:
  - "add audit programs"
  - "build out KC forms"
  - "file the leadsheets"
  - "add the [client type] programs"
inputs:
  - "Engagement URL"
  - "client type"
  - "condition flags"
calls:
  - scripts.binder_planner.plan
  - scripts.binder_planner.diff_against_unfiled
  - scripts.catalog.lookup_by_form_id
  - scripts.catalog.lookup_by_reference_tag
  - scripts.catalog.build_add_forms_body
  - scripts.kc.add_forms
  - scripts.wpm.move
  - scripts.wpm.set_index
  - scripts.wpm.folder_get
status: validated
validated_on:
  - "APNM 2025 NFP — 2026-05-07"
  - "Kymera 2025 EBP — 2026-05-21"
---
# Module — Add Audit Programs (KC Forms) to a Binder

> **S-suffix / Single Audit forms (AX-26).** `diff_against_unfiled` returns a
> `sa_title_adds` bucket — these add CROSS-TITLE from the Single Audits title
> (`catalog.SA_TITLE_GUID`; live list via GetWorkpaperListForAddForms — see
> `endpoints/kc_title_library.json`). NEVER silently skip an unresolved form — name
> every unmatched form to the user (BT3 B7 dropped 22 silently).

> **Index verification (AX-26).** Read display indexes with
> `scripts.wpm.verify_index(row, object_type)` — Reports/KCForms use `index`,
> Workpapers use `documentIndex`; hand-picking the field false-negatives (BT3 B6).
> And NEVER hand-assemble `folderParentLineItems` — `wpm.move()` now refuses them
> (semantics are inverted per type; hand-rolled bodies silent-200, BT3 B5/B12).

**Triggers:** "add audit programs", "build out the KC forms", "add the [client type] audit programs", "file the audit programs", "set up the audit programs", "file the auto-populated baseline."

## Prerequisites

- Wrapper folder + section folders exist (run `setup-binder-from-index.md` first if not; default structure is 2-level — wrapper > sections).
- KC auto-populated baseline already in Unfiled KC Forms (CCH title-default behavior — happens on engagement creation).
- A `binder-program-template-{client-type}.xlsx` exists (currently nonprofit, govt-with-sa, ebp).
- `kc-forms-catalog-rich.xlsx` has the industry title's form metadata.
- Engagement tab on `engagement.cchaxcess.com` and KC tab on `knowledgecoach.cchaxcess.com` both open.

## Procedure

### 1. Resolve condition flags

Ask the user (or read from engagement memory):
- `single_audit` — Uniform Guidance Single Audit applies?
- `new_client` — genuine new audit client (predecessor exists)? *Default False — the firm's Axcess migration means most are first-time-builds but NOT new clients.*
- `firm_prepares_fs` — firm prepares the financials?
- ALC cycles (cash_receipts_cycle, payroll_cycle, etc.) — default all True until KBA-400 Scoping flow exists.

### 2. Build the plan

```python
from scripts import binder_planner, catalog, kc, wpm
plan_rows = binder_planner.plan(client_type, flags)
```

### 3. Capture auth headers (both subdomains)

- KC: localStorage fast path — pass `headers="ls:kc"` to the builders (AX-26 sentinel).
- WPM: monkey-patch on the engagement tab, trigger one UI action, read capture.

### 4. Diff against current state

```python
js = wpm.folder_get(client_id, eng_id, folder_id=-4, headers=wpm_hdrs)  # Unfiled KC Forms
# run via Chrome tool, parse
buckets = binder_planner.diff_against_unfiled(plan_rows, unfiled_items)
# buckets: {already_in_unfiled, to_add, sa_title_adds}
#   to_add        -> forms from the binder's OWN title (Step 5a)
#   sa_title_adds -> S-suffix forms that live in the Single Audits title (Step 5b, cross-title)
# NEVER silently drop a form: any plan row not in to_add/sa_title_adds/already_in_unfiled
# must be surfaced to the user BY NAME (BT3 B7 dropped 22 S-forms).
```

### 5a. Add the binder's-own-title forms (one batched POST)

```python
catalog_rows = [catalog.lookup_by_form_id(p['fid'], title_guid) for p in buckets['to_add']]
body = catalog.build_add_forms_body(catalog_rows)
js = kc.add_forms(eng_guid, body, kc_hdrs)
# Response is {"result": [...], "statusCode", "message"}. `result` ECHOES every
# SUCCESSFULLY-added form (each with its server-assigned workpaperId) — NOT
# failures-only, NOT empty on full success (settled live 2026-06-04). Confirm by
# matching each planned referenceTag to a result[] entry. NEVER blind-retry the
# POST — not because successes are invisible (they're in result[]) but because
# every extra POST adds duplicate forms (live incident 2026-06-03); a re-GET of
# Unfiled (-4) still satisfies the re-GET-after-write doctrine.
```

### 5b. Add Single Audit (S-suffix) forms — CROSS-TITLE (only if `sa_title_adds` non-empty)

```python
# S-forms live in the Knowledge-Based Single Audits title, NOT the binder's own title.
# Resolve from that title's library (live: GetWorkpaperListForAddForms/{binderGuid}/{SA_TITLE_GUID},
# ls:kc — endpoints/kc_title_library.json) or the offline fallback catalog.load_sa_title_forms().
# add_forms with the SA titleGuid (catalog.SA_TITLE_GUID); same POST shape, cross-title.
sa_rows = catalog.load_sa_title_forms()   # or the live pull
# build the add body against SA_TITLE_GUID for the fids in buckets['sa_title_adds'], then kc.add_forms
```
Tell the user which S-forms were added (and name any plan row left unresolved).

Re-GET Unfiled (-4) to pick up server-assigned `locationId` values for ALL new rows (5a + 5b).

### 6. Move everything (one batched PUT)

Combine `already_in_unfiled` + newly-added forms into one move call:
```python
# target_folder_idx is the 4-DIGIT section index (AX-26: binder_planner.section_for_index —
# "0201"→"0200", "81xx"→"8000" Single Audit exception). Build target_folder_locations keyed
# by the section's 4-digit index from folder_get of the wrapper.
items = [
    {"object_type": "KCForms", "own_loc": r["locationId"], "dest_loc": target_folder_locations[r["target_folder_idx"]], "object_id": r["documentId"]}
    for r in all_forms_to_file
]
js = wpm.move(client_id, items, wpm_hdrs)
```

LeadSheet/KCForms/Report use the **swap semantics** baked into `wpm.move` — never assemble the body by hand.

### 7. Set indexes (sequential PUTs)

```python
items = [{"index": r["idx"], "name": r["name"], "object_id": r["documentId"], "object_type": "KCForms"} for r in all_forms_to_file]
js = wpm.set_index(client_id, items, wpm_hdrs)  # serializes internally
```

**Sequence: Move first, Set-Index second.** Move preserves existing indexes and locationIds (confirmed 2026-06-03); Set-Index is needed because newly-added forms arrive with a null/empty index.

### 8. File the Trial Balance report

```python
# Find TB in Unfiled Reports (-2)
js = wpm.folder_get(client_id, eng_id, -2, wpm_hdrs)
# Move + Set-Index in two calls
wpm.move(client_id, [{"object_type": "Report", "own_loc": tb_loc, "dest_loc": folder_0900_loc, "object_id": "reports/trialbalance"}], wpm_hdrs)
wpm.set_index(client_id, [{"index": "0900", "name": "Trial Balance", "object_id": "reports/trialbalance", "object_type": "Report"}], wpm_hdrs)
```

### 9. Verify

Re-GET each target folder. Confirm form list + indexes match plan. GET `-4` and confirm Unfiled KC Forms count = 0 (or matches deferred-by-flag count).

## Validated on

- APNM 2025 NFP — 26 forms, 2026-05-07
- Kymera 2025 EBP — 22 forms, 2026-05-21

## Known failure modes

See `architecture.md`. Module-specific:

- Add-Forms body's `index` field is silently ignored. Don't rely on it.
- Server silently skips forms whose `referenceTag` is unrecognized — always verify post-add Unfiled count matches expected.
- **Move-then-Set-Index is the correct sequence** — but not for the reason previously documented here. Move PRESERVES any existing index and does NOT change the locationId (both confirmed live 2026-06-03). Newly-added forms arrive in Unfiled with a null/empty index, so Set-Index must run after Move to assign the target index. No re-GET needed after Move — the locationId is stable.
- **`diff_against_unfiled` false-negative** — if a form was filed (moved out of Unfiled) but then soft-deleted back into a folder, it won't appear in Unfiled and the diff will re-add it. Check the binder map if the post-add count looks off.

<!-- END -->
