---
name: wt-vendors
category: wt
mandatory: false
description: Vendor walkthrough — substantive testing of significant vendors via vendors-over-TM total spend with the largest invoice pulled per vendor. Replaces the older static disbursements walkthrough — this is what we do far more often.
acceptable_methods: [static-sample]
mandatory_method: static-sample
required_documents:
  - Check register / cash disbursements journal for the period
  - General ledger detail (to identify vendors and total spend per vendor)
---

# Vendors Walkthrough

Static-sample-style with **MD-specific selection logic** — n is variable.

## Selection logic

1. **Identify vendors** via the check register or GL whose **total expenditures for the period exceed TM**
2. For each such vendor, **pull the single largest invoice** as the selection
3. n = number of vendors over the TM threshold (one invoice per vendor)

## Selection bias rules
- Apply the no-negatives rule (skip vendor totals that are net-negative — typically refunds / credits)
- Voided / reversed payments excluded from the vendor total before applying the TM threshold
- If the population of vendors-over-TM is very large or very small, surface to the user — TM may need adjustment or the threshold may need a sanity check

## Population scoping
- Trade vendors only — exclude payroll, debt service, intercompany, tax payments unless those are tested as part of this sample by design
- Ensure vendor totals reconcile to the relevant GL accounts before applying the TM filter

## Omission rule
**Skip this sample when significant controls testing of vendor disbursements is happening elsewhere.** Walkthrough and controls testing of the same area are redundant — pick one.

## Notes
- Naming: called "Vendors" rather than "Disbursements" because that's the term staff recognize in the field
- For controls testing of the disbursement approval process, that's a separate procedure under `control-sample` — triggers the omission rule above
