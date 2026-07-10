---
summary: Manage TB groupings (financialList, financialGroup, account assignment)
leg: wpm
triggers:
  - "create grouping list"
  - "build the grouping codes"
  - "add a TB group"
  - "assign account to group"
  - "leadsheet grouping"
  - "add a subgroup"
  - "assign account to subgroup"
load_from_jump:
  - "from scripts import groups, http_runner"
  - "config/group_account_types.json  # classification name -> ids (read instead of network)"
inputs:
  - "Engagement URL -> clientId (1st int), periodId (2nd int)"
  - "captured financialprep-api headers (auth_capture monkey-patch)"
calls:
  - scripts.groups.list_financial_lists
  - scripts.groups.list_financial_groups
  - scripts.groups.create_financial_list
  - scripts.groups.create_financial_group
  - scripts.groups.build_chain_create_groups_js
  - scripts.groups.build_reorder_groups_js
  - scripts.groups.move_financial_group
  - scripts.groups.get_trialbalance_grouped
  - scripts.groups.build_bulk_assign_js
  - scripts.groups.assign_account_to_group
  - scripts.groups.build_patch_body
  - scripts.groups.update_financial_group
  - scripts.groups.resolve_classification
  - scripts.groups.create_financial_subgroup
  - scripts.groups.build_chain_create_subgroups_js
  - scripts.groups.assign_account_to_subgroup
status: validated
validated_on:
  - "create + reorder chains + account assignment: clientId 100173 — 2026-05-30/31"
---
# Module — Manage TB Groups (financialprep-api)

> **Placeholder-TB halt (AX-26, mandatory).** Before ANY account-assignment step, pull the
> account map and run `scripts.funds.preflight_account_map(accounts)`. If `ok=False`, STOP
> and prompt the user ("looks like no TB has been imported — import it first?"). Never
> proceed on a dummy map (BT3 incident).

> **Fresh groups before bulk assign (AX-26).** Group UUIDs and
> `engagementFinancialGroupMapId` CHURN when a TB is imported. Re-GET
> `list_financial_groups` immediately before any bulk assignment and pass the FULL
> fresh row to `build_patch_body` (it now refuses partial rows). Never cache group
> objects across a TB import.

Build/seed/reorder a grouping list and assign accounts. Fund accounting is a different leaf
(`manage-funds.md`, workbench-api).

## Load from the jump
```python
from scripts import groups, http_runner          # config/group_account_types.json for class ids
```
Need: monkey-patched financialprep-api headers, `clientId`, `periodId` (for assignment).

## Optimum path
1. **List first** — never assume empty.
   ```python
   groups.list_financial_lists(client_id, headers)
   groups.list_financial_groups(client_id, list_id, headers)
   ```
2. **Create list** if missing (`number` = user-facing index, NOT `index`):
   `groups.create_financial_list(client_id, number="03", name="Natural Classification", headers=headers)`
3. **Batch-create via anchor chain** — `groups`=list of `{index, name, account_type_id, classification_id}`;
   threads each new id as the next insert-after anchor (one call):
   `groups.build_chain_create_groups_js(client_id, list_id, groups_to_add, headers, start_anchor=0)`
4. **▶ MANDATORY — reorder ascending.** Creates land newest-on-top (LIFO); without this they
   display in reverse index order (AX-07). Pass the `list_financial_groups` rows straight through:
   `groups.build_reorder_groups_js(client_id, list_id, ordered_groups, headers, sort_by_index=True)`
5. **Assign accounts** — GET the grouped TB rows, swap each row's group, batch in ONE call
   (sequential PATCHes crash the KC tab — AX-09/10):
   ```python
   rows = groups.get_trialbalance_grouped(client_id, list_id, period_id, headers)   # parse rows in Chrome
   bodies = [{**account_row, "group": target_group} for account_row, target_group in assignments]
   groups.build_bulk_assign_js(client_id, bodies, headers)
   # one account:  groups.assign_account_to_group(client_id, account_row, target_group, headers)
   # no full row:  groups.build_patch_body(account_id, client_id, list_id, period_id, name, number, target_group)
   ```
6. **Verify** — re-GET the grouped TB. Assignment reads back at
   **`row.account.group.financialGroupId`** (NOT top-level `row.group` — see AX-11). Confirm
   ascending order and that assigned groups' `totalChildren` moved.

## Branches
- Target list exists → skip step 2, reuse its id.
- First group into an EMPTY list → anchor `0`; otherwise anchor = preceding group id (chain helper handles it).
- Rename/re-index existing group → PUT (`update_financial_group`) with full account-type trio + position anchor. POST-with-own-id is wrong (duplicates).

## Error branches
| Symptom / error | Cause | Fix |
|---|---|---|
| Groups in reverse index order | skipped step 4 | run `build_reorder_groups_js(sort_by_index=True)` |
| Assignment "didn't apply" | read back at `row.group` (always stale) | check `row.account.group.financialGroupId` (AX-11 — the old "no-op" false alarm) |
| `400 Invalid financial group.` | anchor `0` into non-empty list | anchor on preceding group id |
| `400 Group name exists.` | name is the unique key (not index) | dedupe name within list |
| `400 Invalid account type / classification.` on reorder PUT | reorder needs full trio (accountType str + accountTypeId + classificationId) | pass GET rows through (helper derives the trio) |
| `400 EngagementId` on assign PATCH | body missing the engagementId=clientId mapping | use rows from `get_trialbalance_grouped`, or `build_patch_body()` (AX-08) |
| KC tab `Runtime.evaluate timed out` after N PATCHes | sequential XHR in KC tab | one-call `build_bulk_assign_js()` |

## Subgroups (financialsubgroup — child level under a group)

A subgroup is a child level below a financialGroup (TB Sub-Group column; UI: Account Groupings
→ Financial → select core group → Actions → Add). **There is NO subgroup GET** (the endpoint
404s) — read subgroup membership from the grouped TB at **`row.account.financialSubGroup`** (NOT
`row.account.subGroup`, which is silently null — see architecture.md FP-trialbalance gotcha).

Status: captured 2026-05-30/31 — not yet round-trip live-validated the way group create/reorder is.

1. **Create subgroups under a parent group** — same insert-after anchor rule as groups, on its
   own field (`0` = first subgroup under the parent; else the preceding sibling's
   `financialSubGroupId`). Chain N in one call:
   ```python
   groups.build_chain_create_subgroups_js(client_id, list_id, parent_group_id, subgroups, headers, start_anchor=0)
   # subgroups = [{"index": "1010", "name": "Operating cash"}, ...]
   # one subgroup: groups.create_financial_subgroup(client_id, list_id, parent_group_id, index, name, headers, anchor_subgroup_id=0)
   ```
2. **▶ PRECONDITION — parent group first.** The account MUST already be assigned to the
   subgroup's PARENT group before a subgroup assign, or the PATCH 400s "Invalid financial
   sub-group." Flow: `assign_account_to_group(parent)` → then `assign_account_to_subgroup`.
   ```python
   groups.assign_account_to_subgroup(client_id, account_id, list_id, financial_subgroup_id, headers)
   ```
3. **Verify** — re-GET the grouped TB; assignment reads back at `row.account.financialSubGroup`.

See `endpoints/groups_financial_groups.json` (single-group `create_financial_group` /
`move_financial_group` building blocks) and `groups_account_assignment.json` (`patch_subgroup`).

## See also
`references/endpoints/groups_financial_lists.json` (financialList CRUD),
`groups_financial_groups.json` (anchor + reorder PUT trio rule),
`groups_account_assignment.json`, `config/group_account_types.json`.

<!-- END -->
