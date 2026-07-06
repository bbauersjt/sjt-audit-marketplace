---
name: wt-credit-cards
category: wt
mandatory: false
description: Credit card walkthrough — substantive testing of card activity for proper authorization, business purpose, and classification. Variable n driven by card count and selected months.
acceptable_methods: [static-sample]
mandatory_method: static-sample
required_documents:
  - General ledger detail (to identify credit card accounts and statements)
  - Credit card statements for the period (all cardholders)
---

# Credit Cards Walkthrough

Static-sample-style with **MD-specific selection logic** — n is variable.

## Selection logic

1. **Look in the GL.** Identify each distinct credit card statement / cardholder represented in the credit card expense or liability accounts. Each card is its own selection stream
2. **Per card identified, pick 2 different months** — typically a routine month and one period-end / off-pattern month, or simply 2 spread months
3. **Pull all charges on the statement for those 2 months** as the selection set
4. n = sum of all charges across all selected cards × 2 months each

## Selection bias rules
- Default is to pull **all** charges in the selected months for each card
- If a single card has an unmanageable volume in a given month, surface to the user before trimming — don't silently sample within the month

## Population scoping
- Only credit card transactions — not P-card or fuel card unless commingled in the same accounts
- Voided / reversed charges removed before pulling
- Refunds / merchandise returns: include only if needed to reconcile the statement totals; otherwise exclude per the no-negatives bias rule

## Notes
- Personal-use risk is the typical concern
- If the entity has many cards and the GL shows them lumped together, ask the user how to identify distinct cards (cardholder name, last-4, statement reference)
- If only one card exists, pick 2 months from that single card
