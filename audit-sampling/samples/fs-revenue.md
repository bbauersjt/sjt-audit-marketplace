---
name: fs-revenue
category: fs
mandatory: false
description: Revenue / sales transactions — substantive testing of recognition, occurrence, accuracy, and cutoff.
acceptable_methods: [substantive]
mandatory_method: null
required_documents:
  - Revenue / sales journal for the period
  - GL revenue account balance(s)
  - Population of revenue transactions with date, customer, amount, invoice/reference
---

# Revenue

Sampling unit: revenue transaction (invoice or recognition entry).

## Notes
- Cutoff testing is often a separate sample — selections from a window around year-end (e.g., last 2 weeks pre / first 2 weeks post)
- Stratify by revenue stream if the entity has multiple distinct streams with different recognition patterns
- Recurring / subscription revenue often better tested via reperformance / disaggregated analytic — confirm sampling approach is the right tool
- If the substantive comparison lands on `controls-substantive-fallback`, the receipts walkthrough (`wt-receipts`) becomes redundant — apply the omission rule
