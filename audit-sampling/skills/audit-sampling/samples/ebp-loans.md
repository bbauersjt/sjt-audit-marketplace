---
name: ebp-loans
category: ebp
mandatory: false
description: Participant loans — testing for proper authorization, terms within plan limits, repayment, and default treatment. Required when the plan permits loans.
acceptable_methods: [controls-substantive-dual, compliance-sample]
mandatory_method: null
required_documents:
  - Loan register / outstanding loan detail at year-end
  - New loan activity for the period
  - Plan document loan provisions
  - Loan repayment / amortization schedules
---

# EBP — Participant Loans

Sampling unit: loan (or new-loan event for new-loan testing).

## Notes
- Required when the plan permits loans — confirm with plan document
- Test both new originations and outstanding balances
- IRC §72(p) limits ($50,000 / 50% of vested balance, 5-year term, level amortization) are key compliance attributes
- Defaulted loans require deemed distribution and 1099-R
