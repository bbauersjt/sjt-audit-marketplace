---
name: fs-ap
category: fs
mandatory: false
description: Accounts payable / accrued liabilities — completeness testing for unrecorded liabilities. Recorded balances rarely tested unless something stands out.
acceptable_methods: [progressive-subsequent]
mandatory_method: progressive-subsequent
required_documents:
  - AP aging at year-end
  - GL balance for AP control account
  - Subsequent disbursements register (post year-end through fieldwork)
---

# Accounts Payable

Default approach: completeness via `progressive-subsequent` — the search for unrecorded liabilities at year-end. Substantive testing of **recorded** AP balances is not standard practice here; only run it if something stands out (large unusual balances, vendor disputes, prior misstatements, etc.) and discuss with the engagement team before doing so.

## Population cleanup — payroll funding

Subsequent disbursements registers contain recurring payroll funding events (transfers to a third-party payroll provider — ADP, Paychex, QuickBooks Payroll Service, Gusto, OnPay, Rippling, etc.). These are not unrecorded-liability candidates; they're scheduled cash outflows for ongoing payroll cycles, not liabilities left unrecorded at year-end. Remove them from the subsequent-disbursements population before sizing the search for unrecorded liabilities, and document the removed amount.
