---
name: fs-ar
category: fs
mandatory: false
description: Trade accounts receivable — substantive testing of recorded balances; for nonprofits with grant income, progressive-subsequent for completeness as well.
acceptable_methods: [substantive, progressive-subsequent]
mandatory_method: null
required_documents:
  - AR aging at year-end
  - AR detail by customer (sub-ledger detail)
  - GL balance for the AR control account
  - Cash receipts journal post year-end through fieldwork (for substantive subsequent receipts and for progressive-subsequent)
---

# Accounts Receivable

Sampling unit: customer-level balance, not individual invoice — unless the population is so fragmented that customer-level concentration is meaningless.

## Both samples can fire

`substantive` and `progressive-subsequent` are **not alternatives** here — both can trigger on the same engagement and produce **separate samples**:

- `substantive` covers recorded balances (existence / valuation)
- `progressive-subsequent` covers completeness — required for nonprofits with grant / contribution receivables to