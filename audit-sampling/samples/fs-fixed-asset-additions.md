---
name: fs-fixed-asset-additions
category: fs
mandatory: false
description: Capital / fixed asset additions — substantive testing of property, equipment, software, and other capitalized additions for existence, valuation, and authorization.
acceptable_methods: [substantive]
mandatory_method: null
required_documents:
  - Fixed asset additions schedule (or roll-forward) for the period
  - GL detail for fixed asset accounts (additions side — debits during the period)
  - Invoices and payment evidence for selected additions (during fieldwork)
---

# Capital / Fixed Asset Additions

Sampling unit: individual addition (an invoice or capitalized line item).

## Population

Debits to fixed asset accounts during the period — additions only. Exclude:

- Depreciation entries (those credit accumulated depreciation, not the FA accounts directly)
- Disposals (asset retirements)
- Reclassifications between FA accounts (offsetting + and − within FA in the same period)
- Opening balance adjustments / prior-period roll-forward fixes

If a client-provided roll-forward / additions schedule exists, reconcile it to GL additions before sampling. A material variance is a population integrity issue — escalate to the user before pulling.

## Method

Standard `substantive` four-way comparison (see `methods/substantive.md`). Smallest n wins.

## Selection logic

Per the winning method's rules. General selection bias rules in `references/general-rules.md` apply — skew toward larger items, avoid trivially small items unless filling out a fallback sample, include any unusual or one-time large additions.

## Notes

- Pairs with `fs-capitalizable-search`, which looks the *other* direction — for capital items hidden in expense accounts. The two samples are complementary, not redundant: one tests recorded additions, the other tests for missing ones.
- For software, distinguish capitalizable internal-use software development (ASC 350-40) from licensed / SaaS subscriptions (typically expensed). The classification affects whether it should appear in this sample at all.
- For donated assets, valuation testing may need a separate procedure — flag to the user if material.
