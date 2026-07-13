---
summary: Set up / build out a binder; create section folders (default 2-level or user-defined structure)
leg: kc
triggers:
  - "set up a new binder"
  - "build out the binder"
  - "make the folders"
  - "build the index"
inputs:
  - "Engagement URL"
  - "wrapper name"
calls:
  - scripts.kc.get_binder
  - scripts.catalog.resolve_title_guid
  - scripts.wpm.create_folder
  - scripts.wpm.rename_folder
  - scripts.wpm.move
  - scripts.wpm.folder_get
status: validated (4-tier flow); wip (2-level default + custom groupings)
---
# Module — Set Up New Binder

> **GATE — platform module.** Requires Step 0 (`session-bootstrap.md`) run THIS session +
> the page-context transport (`transport.md`). **Reading this file is NOT initialization.**
> If you have ALREADY made platform calls this session without Step 0 (e.g. you were spawned
> with a token in your prompt, or jumped straight to `chrome_api_call`): **STOP now** — run
> Step 0 in full, switch to the page-context transport, RE-VERIFY BY READ everything you wrote
> while side-entered (200s may be silent no-ops), then resume from the last verified step.
> (SKILL.md → "Initialization gate".)

**Status:** Re-run cautiously on new client types.

## Batch-first — check this table BEFORE looping single calls

Building a binder one call per object is the known runaway failure. Chunk per
`transport.md` → "Bounded execution" (≤10 ops per eval, JS-side timeout, verify by read).

| Doing this N times? | Use instead |
|---|---|
| Move / file N workpapers, leadsheets, or forms | ONE `scripts.wpm.move(client_id, items, hdrs)` — `items` is a LIST; batch it |
| Add N KC forms | ONE `kc_add_forms` batch body via `scripts.catalog.build_add_forms_body` — array body; see `transport.md` → array-body note for the wire path |
| Create N folders | No batch endpoint exists — per-call is correct, but run them in bounded chunks (≤10 per injected eval), not one eval per folder |
| Inventory the binder / find items | `scripts.binder_map.build_map_js` / `fetch_chunk_js` — never a folder-by-folder GET loop |

**Triggers:** "set up a new binder", "build a new binder", "build out the binder", "build the binder for [client]", "populate this engagement", "make the folders", "build the index", "build out [client]'s engagement", any phrasing supplying an engagement and asking for the standard structure.

## What this does

Wrapper folder (client name, NO index) with section folders directly beneath — **two levels is the default**. The section list comes from `binder-template.xlsx` when the user wants the default, from the user verbatim when they bring their own, or is co-developed with the user. Deeper nesting remains fully supported via `parent_folder_id` chains — but ONLY when the user asks for it. Files BS leadsheets from `Unfiled Leadsheets` into their matching section folders with explicit per-folder moves (no auto-cascade exists).

## Prerequisites

- Engagement tab on `engagement.cchaxcess.com`.
- WPM headers from monkey-patch capture.
- `references/data/binder-template.xlsx` — firm's DEFAULT section list (`Sections` sheet: Index + clean Group name; 2-level structure).

## Procedure

### Phase 0 — Pre-flight

1. **Confirm target engagement** (read breadcrumb; don't trust a stale tab).
2. **Determine entity type — in THIS order:**
   - **2a. Authoritative: KC title.** `scripts.kc.get_binder` → parse `result.lastUsedTitleGuid` → `scripts.catalog.resolve_title_guid()` → e.g. "2025 - Knowledge-Based Audits of Governmental Entities". The user picks this title at binder creation, so it is never null on a real engagement. Parse the binder FIRST — every new binder comes seeded with KC forms in Unfiled KC Forms (`-4`); their presence confirms the binder is live, but form refs (AUD-100/KBA-1xx) are SHARED across entity types and must NOT be used to infer type.
   - **2b. Corroborate: TB account structure.** Fund-prefixed account numbers, `Fund Balance`, `Property Tax`, `Gas Tax`, `Intergovernmental`, `Public Safety/Works`, `Federal Grant` → governmental, definitively. Read the TB BEFORE asking the user anything.
   - **2c. Confirming signal only:** the `Funds Setup` right-sidebar button (govt/consolidated-NFP). Never primary.
   - **NEVER infer entity type from the client name.**
   - **Conflict = blocker.** If the KC title/form set disagrees with TB structure (e.g. commercial title, governmental TB), STOP and surface the conflict — the binder may have been created under the wrong title. Do not declare entity type "confirmed" until 2a and 2b agree.
3. **Inventory existing structure.** If anything beyond the four Unfiled pseudo-folders, ask the user: abort / build alongside / delete-and-rebuild. **If any folder slated for deletion has workpapers**, offer to move them to `Unfiled Workpapers` first.
4. **Capture WPM auth.** Monkey-patch the tab, trigger one UI action (`Unfiled Workpapers` click works), read capture.

### Phase 1 — Choose the structure, then determine applicable sections

**5-pre. Structure selection (ask once, before any mapping):**
   - **User asks for the default** → serve the `Sections` sheet of `binder-template.xlsx`
     as-is (trimmed by the FS mapping below). Two levels: wrapper > sections.
   - **User provides their own grouping list** → use it verbatim. Validate only:
     indexes unique and sortable (4-digit convention recommended), names clean
     (no index prefixes). Don't editorialize their list.
   - **User wants to work it out** → co-develop: start from the default trimmed by FS
     line items, present the tree, iterate until they approve (Phase 2 gate).
   - **Depth:** default is ALWAYS 2 levels. Build deeper tiers ONLY when the user
     explicitly specifies a nested structure — then create parents first and chain
     `parent_folder_id` (capability retained; just never the default).

5. **Open the Financial Statements report**, not the TB. URL: `https://engagement.cchaxcess.com/en-US/engagement/{clientId}/reports/{engagementId}/financials`. FS is ~2 KB; line items map 1:1 to leadsheet names.
6. **Extract line items** under ASSETS / LIABILITIES / EQUITY / REVENUES / EXPENSES.
7. **Map to section indexes** from `binder-template.xlsx`'s `Sections` tab (default-structure path only — skip when the user supplied their own list). Standard BS mapping: Cash→1000, Investments→1100, Receivables→1200, Inventory→1300, Prepaid→1400, PP&E→1500, Other Assets→1600, Interfund(Asset)→1900, Payables→2000, Accrued→2100, Deferred Rev→2200, Other CL→2300, LTD→2400, Other Liab→2500, Interfund(Liab)→2900, Equity→3000.
8. **Always include regardless of FS (default-structure path):** the planning sections `0100`–`0700`; `0900 TB`; `3000 Equity`; `4000 Revenue`; `5000 Expense`; `9000 Perm File`.
9. **Single Audit (`8000`) — opt-in by signal.** Scan TB account/group names for `federal`, `federal grant`, `state grant revenue`, `deferred grant revenue`, `grants receivable`. None → skip 8000 silently. Any → ASK the user.
10. **STOP and prompt the user if any of:**
    - TB doesn't balance.
    - Many groups blank or "Ungrouped".
    - Expected BS groups (Cash, Receivables, Payables, Equity) entirely missing → likely non-default grouping.

### Phase 2 — Show plan, get approval

11. **Render the tree** with `(always)` vs `(from FS)` annotations. When proposing per-workpaper indexes inside a back-of-file section (lead / main / supporting), follow the AUTHORITATIVE convention in `rename-workpaper-index.md` (`XX00-PROG` program, `XX00` lead, `XX01/XX02` main, `XX01.1/.2` supporting).
12. **Propose wrapper name.** folderName `[ShortClientName] [Year]`, **NO folderIndex at all** (empty string — nothing forces sort order at the top level). Drop legal suffixes. Suggest acronym if obvious. User can override. ⚠ Empty folderIndex is UNVERIFIED against the API — see Known failure modes.
13. **Get user go-ahead** before writing anything.

### Phase 3 — Build via API

> **NAMING CONVENTION (double-index regression):** `folderName` is
> the CLEAN descriptive name with NO index prefix — `folderIndex` carries the index
> and the binder UI renders both, so "01 Front of File" as a name displays as
> "01 | 01 Front of File". `binder-template.xlsx`'s Group-name column is already
> clean — use it verbatim. Wrong names are remediable: `scripts.wpm.rename_folder`.

```python
from scripts import wpm
# 14. Wrapper first — client name only, NO index
js = wpm.create_folder(client_id, "", wrapper_name, parent_folder_id=None, headers=wpm_hdrs)
# response body is the new locationId as plain integer text

# 15. Section folders — DEFAULT: every approved section directly under the wrapper
for index, name in section_rows:   # Sections sheet, or the user's approved list
    wpm.create_folder(client_id, index, name, parent_folder_id=wrapper_loc, headers=wpm_hdrs)
#    (small delay ~80ms between calls is polite, not required)

# 16. ONLY if the user specified a nested structure: create their parent tiers first,
#     then pass each parent's locationId — arbitrary depth via parent_folder_id chains.

# 17. Auto-file unfiled BS leadsheets
js = wpm.folder_get(client_id, eng_id, -3, wpm_hdrs)   # Unfiled Leadsheets
# For each leadsheet whose index matches a created section (BS only — skip 4xxx/5xxx):
#    Move DIRECTLY to that section folder's locationId — there is NO auto-cascade
#    (moving to a parent does NOT distribute downward).
items = [{"object_type": "LeadSheet", "own_loc": ls["locationId"], "dest_loc": section_map[ls["index"]], "object_id": ls["documentId"]}
         for ls in bs_leadsheets]
wpm.move(client_id, items, wpm_hdrs)
```

Build `section_map` (section index → locationId) from the create_folder responses in step 15 (each returns the new locationId as plain integer text).

**Skip 4xxx and 5xxx leadsheets** — handled separately by future revenue/expense module.

### Phase 4 — Verify

18. Re-GET the wrapper: child count == approved section count (default path). Each BS section contains its auto-filed leadsheet. `Unfiled Leadsheets` (`-3`) contains only 4xxx/5xxx. (User-specified nesting: verify each tier instead.)
19. Reload the engagement view URL in the tab and screenshot for the user.

## Known failure modes

See `architecture.md` for platform-level. Module-specific:

- Folder cache: clicking the same folder twice doesn't refire GET. Click away then back to force a fresh GET.
- Workpapers with an active user behave differently on delete (CCH dialog warns). Untested — surface and ask before proceeding.
- Recycle Bin endpoint not yet captured. Bin URL: `/en-US/engagement/{clientId}/wpRecycleBin`.
- **Double-indexed folder names** ("01 | 01 Front of File") → index prefix embedded in `folderName` → strip prefixes and fix with `scripts.wpm.rename_folder(client_id, loc_id, index, clean_name, headers)`. The load-bearing body field is `oldLocationId` (see `endpoints/wpm_folder_rename.json`).
- **Empty wrapper folderIndex rejected** (UNVERIFIED — the no-index wrapper has not been tried live) → if `create_folder(client_id, "", …)` 400s, create with index `00`, then `rename_folder` to clear the index; if THAT also fails, keep `00`, tell the user, and log the finding so this bullet gets resolved.
- **Entity type declared from client name or KC form refs** → both are non-signals → re-run Phase 0 step 2 (titleGuid → catalog, corroborate with TB).

<!-- END -->
