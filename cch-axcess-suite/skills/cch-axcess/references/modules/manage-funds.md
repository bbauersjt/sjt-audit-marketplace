---
summary: Manage fund accounting setup (FundType, Fund, FundSubType, account map)
leg: wpm
triggers:
  - "set up funds"
  - "add fund types"
  - "create fund"
  - "assign accounts to fund"
  - "fund TB setup"
  - "governmental fund setup"
  - "fund sub-type"
inputs:
  - "Engagement URL"
  - "clientId"
  - "fund hierarchy edits"
calls:
  - scripts.funds.list_fund_types
  - scripts.funds.list_funds
  - scripts.funds.list_fund_sub_types
  - scripts.funds.get_fund_account_map
  - scripts.funds.upsert_fund_types
  - scripts.funds.upsert_funds
  - scripts.funds.upsert_fund_sub_types
  - scripts.funds.preflight_account_map
  - scripts.funds.check_fund_references
  - scripts.funds.assign_account
  - scripts.funds.unassign_account
  - scripts.funds.delete_fund_type
  - scripts.funds.delete_fund
  - scripts.funds.delete_fund_sub_type
status: validated
---
# Module — Manage Funds (Fund TB Setup)

> **Placeholder-TB halt (AX-26, mandatory).** Before ANY account-assignment step, pull the
> account map and run `scripts.funds.preflight_account_map(accounts)`. If `ok=False`, STOP
> and prompt the user ("looks like no TB has been imported — import it first?"). Never
> proceed on a dummy map (BT3 incident).
>
> **Fund-reference halt (AX-31, mandatory).** Also run
> `scripts.funds.check_fund_references(account_rows, defined_funds)` — `defined_funds` from
> `list_funds()`. If `ok=False`, an account points at a fund NOT in the defined Fund list
> (an out-of-range / orphan fund). STOP and surface the offending accounts to the user; the
> fix is theirs (define the fund, or correct the account's fund). NEVER auto-reassign and
> never proceed — the whole-list PUT mis-maps it silently with no native error.

**Triggers:** "set up funds", "add fund types", "create fund", "assign accounts to fund", "fund sub-type", "fund accounting", "governmental fund setup", "fund TB setup", "load the fund mapping", "build the funds", "delete fund type", "remove a fund"

## What this does

Manages the Fund Accounting hierarchy on a CCH engagement: Fund Types (top tier), Fund Sub-Types (optional middle tier), Funds (the records), and the Account-to-Fund assignment map. Applies to governmental and NFP engagements where the TB is segmented by fund. Not the same feature as the firm's 4-digit grouping index — that's a separate workpaper-side concept.

## Prerequisites

- Engagement open at `engagement.cchaxcess.com` (any view inside the target engagement).
- Captured engagement headers (via `scripts.auth_capture.INSTALL_MONKEYPATCH_JS` + `capture_query_js("workbench-api")`).
- Known `clientId` (first integer in the engagement URL, NOT the GUID).

## Procedure

### 1. Read current state and normalize

GET responses use *prefixed* field names (`fundTypeId`, `fundTypeIndex`, ...) and embed objects rather than FKs. PUT expects *bare* names. Always run the parsed GET body through the matching `normalize_*` before mutating.

```python
from scripts import funds, http_runner
raw = http_runner.parse_result(<list_fund_types js result>)["body"]
existing_types = funds.normalize_fund_types(raw)
# parallel helpers: normalize_funds, normalize_fund_sub_types, split_assigned
```

### 2. Add or update via whole-list upsert

```python
new_types = funds.merge_for_upsert(existing_types, [{"index": "03", "name": "Capital Projects"}], match_key="index")
js = funds.upsert_fund_types(client_id, new_types, headers)
```

Same pattern for `upsert_funds` and `upsert_fund_sub_types`. Empty-array PUT is a silent no-op (server safety); use the DELETE endpoints to actually remove rows.

### 3. Assign / unassign accounts (incremental)

```python
js = funds.assign_account(client_id, fund_id=1595, account_ids=[7036327, 7036328], headers=headers)
js = funds.unassign_account(client_id, account_ids=[7036327], headers=headers)
raw = http_runner.parse_result(<get_fund_account_map js result>)["body"]
assigned, unassigned = funds.split_assigned(raw)
```

### 4. Delete (single-row, dependency-aware)

```python
# FundType / FundSubType - check eligibility first (optional but matches UI)
js = funds.check_delete_eligible_fund_type(client_id, fund_type_id, headers)
# response body is a bare boolean: "true" or "false"
js = funds.delete_fund_type(client_id, fund_type_id, headers)
# 200 on success; 400 with {messages: [...]} if dependents remain

# Fund - no pre-flight needed; accounts cascade to Unassigned
js = funds.delete_fund(client_id, fund_id, headers)

# Fund Sub-Type
js = funds.check_delete_eligible_fund_sub_type(client_id, sub_type_id, headers)
js = funds.delete_fund_sub_type(client_id, sub_type_id, headers)
```

**Delete order when nuking everything:** drain Funds (DELETE each), then drain FundSubTypes, then drain FundTypes. Otherwise the eligibility checks return false and DELETEs return 400.

### 5. Verify

After every mutation, re-GET the relevant list and confirm the change landed. The server returns 200 even when an empty-array PUT silently does nothing, so verification GETs are mandatory.

## Known failure modes

- **`id=0` on FundType returns 400/500.** For new FundType entries omit the `id` key entirely. Fund and FundSubType take `id=0`. `scripts.funds.upsert_fund_types` handles this; only matters if hand-rolling the body.
- **Whole-list PUT silently deletes rows.** Omitting an existing row from `upsert_*` deletes it. Always start from a fresh `list_*` call, normalize, mutate, then write back.
- **Empty-array PUT is a no-op.** `{fundTypes: []}` / `{funds: []}` / `{fundSubTypes: []}` return 200 but DON'T clear the collection. Use DELETE per row.
- **Feeding raw GET output into `merge_for_upsert` produces gibberish.** GET shapes use prefixed names; merge keys off `index` which doesn't exist on the GET row. Always normalize first.
- **GET response envelopes are NOT uniform.** FundType returns a bare array. FundSubType returns `{fundSubTypes:[]}`. fundaccountmap returns `{fundAccountMapDtos:[], engagementId}`. The `normalize_*` helpers absorb the differences; only matters if hand-parsing.
- **Unassign with `fundId: null` doesn't work.** The field must be ABSENT, not null. `unassign_account` builds the body without the key — only matters if hand-rolling.
- **DELETE on a FundType/FundSubType with dependents returns 400.** Drain the dependents first (delete or re-assign), or call `check_delete_eligible_*` to confirm. Error body: `{messages: ["You cannot delete this fund type while fund(s) or fund subtype(s) remain assigned to it."]}`.
- **`engagementId` field is misnamed.** Carries the clientId, not the engagementId. Same trap as the rest of workbench-api — see architecture.md.
- **Cross-origin fetch fails.** Calls from `engagement.cchaxcess.com` to `workbench-api.cchaxcess.com` must use XHR, not fetch. `scripts.funds` uses `http_runner.build_xhr_call` for this reason.
- **Content-Type on writes.** Captured headers from a GET-only state lack Content-Type. `http_runner.build_xhr_call` auto-injects; only matters if hand-rolling.

## Open follow-ups (not yet captured)

- **Rename was not captured directly.** Likely uses the same `upsert_*` PUT (caller sends an existing row with the new `name`), but unverified.
- **Sub-type assignment via the Fund Sub-Type tab UI** was not captured directly. The data model says it routes through `PUT /v1/Fund` with `fundSubTypeId` set; the UI may fire a different endpoint when used from that tab.

## Validated on

- Captured + replayed live 2026-05-25 on clientId 90773, engagement page 356643. Built the full hierarchy from empty (2 fund types, 2 funds, 2 sub-types, sub-type stamped on fund 01, 2 account assignments + 1 unassign), then deleted everything via `scripts.funds.delete_*` (including a dependency-blocked DELETE that returned the expected 400 + drain + retry). All paths returned the expected status codes and state.

<!-- END -->
