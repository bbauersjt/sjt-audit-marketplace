---
summary: Back up the trial balance — TB (CY + optional PY) + groups + subgroups + funds into one workbook (import sheets, account map, fund structure)
triggers:
  - "back up the trial balance"
  - "TB backup package"
  - "export the TB package"
  - "pull the TB with groups and funds into a workbook"
  - "two-year TB backup"
  - "make a TB backup before the import"
leg: wpm
inputs:
  - "clientId (Step 0 seed)"
  - "Grouping list (name or financialListId; resolved via groups.list_financial_lists)"
  - "Period ids: CY periodId == engagementId; PY periodId from the FP engagement GET or the user"
  - "Output folder (user-visible working folder)"
calls:
  - scripts.groups.list_financial_lists
  - scripts.groups.list_financial_groups
  - scripts.groups.get_trialbalance_grouped_all
  - scripts.funds.list_fund_types
  - scripts.funds.list_funds
  - scripts.funds.list_fund_sub_types
  - scripts.tb_backup.parse_tb
  - scripts.tb_backup.build_workbook
  - scripts.tb_backup.verify_workbook
status: wip
---

# Module — TB Backup Package

## What this does

- Produces one workbook backing up an engagement's trial balance state: a sterile, import-ready TB sheet per period (CY + optional PY), an Account Map (account → group → subgroup → fund, balances for both years), the Groups inventory, the Fund Structure, and a consolidated all-fields tab (default on).
- Use it to back an engagement up before touching it, and for re-import after a failed/inverted import.

## Prerequisites

- Leg: `wpm` warm (Step 0). Rules 0–3 apply (SKILL.md). No GUID needed — reads only.
- Grouping list resolved against `financialList/{clientId}` (Rule 0: the authoritative
  inventory — not `financialgrouptemplate`).
- Exec cache set up (scripts run; `runbooks/local-exec.md`).

## Procedure

> ⚠ **Status is `wip` — not yet run end-to-end live.** Before starting, tell the user this
> op is newly scripted and their run is also its first live validation; offer to spot-check
> the output against the CCH TB. Don't present it as battle-tested.


### 1. Resolve the grouping list + periods
```python
from scripts import groups
js = groups.list_financial_lists(client_id, "ls:fp")   # or captured WPM-leg dict
```
CY `periodId` == the URL's `engagementId`. For a PY pull, take the prior periodId from
`GET financialprep-api/v1.0/engagement/{clientId}` (named period fields) or ask the user.
PY is optional — confirm with the user whether they want one period or two.

### 2. Pull the TB per period (paginated — never the single-page call)
```python
js = groups.get_trialbalance_grouped_all(client_id, list_id, period_id, "ls:fp")
```
Parse each result with `tb_backup.parse_tb(result)` — it hard-stops on a partial merge
(`count != accountCount`). Row schema + the credits-positive sign convention:
`endpoints/fp_trialbalance.json`. Subgroup key is `account.financialSubGroup` —
`account.subGroup` is always null; never read it.

### 3. Pull groups + funds
```python
js = groups.list_financial_groups(client_id, list_id, "ls:fp")
from scripts import funds
js = funds.list_fund_types(client_id, captured_headers)   # workbench-api: WPM-leg headers
js = funds.list_funds(client_id, captured_headers)
js = funds.list_fund_sub_types(client_id, captured_headers)
```
Non-fund engagement → skip the funds pulls; the sheet is omitted automatically.

### 4. Build the workbook
```python
from scripts import tb_backup
summary = tb_backup.build_workbook(out_path, engagement_name,
    tb_by_period={"CY-FINAL": rows_cy, "PY-FINAL": rows_py},   # first key = CY
    groups=parsed_groups, fund_types=ft, funds=f, fund_sub_types=fst)
```
Import sheets follow `import-tb-format.md` constraints (header row 1, no freeze panes,
single balance column, text account numbers) and are sign-flipped to **debits-positive**.
The All Fields tab keeps RAW API values and says so in row 1.

### 5. Verify
```python
tb_backup.verify_workbook(out_path, tb_by_period)   # format constraints + row counts
```
Also check `summary["sheets"]["Import …"]["net"]` ≈ 0 per period (a TB should net to
zero; a non-zero net is a finding to REPORT, not normalize away). Deliver to the
user-visible folder.

## Known failure modes

- **Partial TB (parse_tb raises)** → single-page endpoint used or pagination loop broke →
  re-pull with `get_trialbalance_grouped_all`; do not build from a short merge.
- **Every subgroup blank** → something read `account.subGroup` → it's
  `account.financialSubGroup` (`fp_trialbalance.json`).
- **Balances inverted vs the client's TB** → raw API values used without the flip →
  import sheets/Account Map must be debits-positive (`import-tb-format.md`).
- **Funds pulls 401/empty on a non-fund engagement** → expected; omit the sheet, don't
  chase auth.

<!-- END -->
