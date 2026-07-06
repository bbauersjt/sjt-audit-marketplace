---
name: fs-capitalizable-search
category: fs
mandatory: false
description: Search expense accounts (R&M, software, IT, small equipment, etc.) for capitalizable items that should have been capitalized but were instead expensed. Directed completeness test for fixed asset additions.
acceptable_methods: [static-sample]
mandatory_method: static-sample
required_documents:
  - GL detail for repairs & maintenance accounts
  - GL detail for software / IT / technology expense accounts
  - GL detail for any other expense accounts at risk for capitalizable items (small equipment, furniture & fixtures expense, leasehold improvements expensed, etc.)
  - Entity's capitalization policy threshold (if available)
---

# Capitalizable Items Search (R&M / Software / Other)

Directed completeness test — looks for capital items hiding in expense accounts. Pairs with `fs-fixed-asset-additions` (which tests recorded additions). Variable n driven by threshold and account scope.

## Threshold

**threshold = max(entity cap policy, 10% × TM)**

If the engagement team has not specified a cap policy, decide what to do based on whether the default would bind:

- **10% × TM ≥ $5,000** — proceed silently using 10% × TM. The $5,000 default doesn't bind, so there's no reason to interrupt the user.
- **10% × TM < $5,000 AND R&M activity is material** (R&M expense > TM, or otherwise notable in the engagement context) — pause and ask the user for the entity's cap policy. Default to $5,000 if the user has nothing better to provide.
- **10% × TM < $5,000 AND R&M activity is not material** — proceed silently using $5,000.

The principle: don't bug the user about cap policy when it won't change the threshold or when the test isn't going to find much anyway.

## Account scope and selection rules

Three populations, treated differently:

### 1. R&M / repairs / maintenance accounts — STRICT

Pull **every transaction over the threshold**, no judgment. R&M is the highest-risk hiding place for capitalizable items, and the cost of false positives (a few extra items pulled) is low compared to the cost of missing a capital item that should have been recorded. Don't try to filter by description — let the auditor evaluate during fieldwork.

### 2. Software / IT / technology expense accounts — JUDGMENTAL

Apply the same threshold, but **screen by description / memo before selecting**. Pull only items whose description suggests capitalizable nature:

- Multi-year licenses or perpetual licenses
- Internal-use software development (build vs. buy, custom code, implementation labor)
- Hardware purchases miscoded to software expense
- Implementation / configuration costs that may be capitalizable under ASC 350-40

Skip items that are clearly opex:

- SaaS subscriptions (monthly / annual recurring fees)
- Maintenance / support fees
- Training, consulting clearly unrelated to development

When in doubt, pull and let the auditor decide. Err toward inclusion if the description is ambiguous — false negatives here defeat the purpose of the test.

### 3. Other expense accounts at risk — JUDGMENTAL

Same approach as software. Common risk areas:

- Small equipment / furniture / fixtures (often a "small eq/furn/soft" account in nonprofits)
- Office supplies (occasionally hides large item purchases)
- Leasehold improvements expensed
- Equipment lease accounts (operating vs. finance lease misclassification)
- Contract services / professional fees that touch on construction or asset development

Apply the threshold, then screen description / memo for capitalizable signals. Pull what the description warrants.

## Population scoping

- Filter to debit (expense-side) entries during the period — exclude credits, refunds, reclasses
- Apply general voided / reversed cleanup before the threshold filter
- Exclude items already reclassified to FA accounts during the period (an offsetting reclass means the entity caught it)

## Output

For each pulled item, surface:

- Date, account, vendor / payee, amount
- **Description / memo prominently** — this is what the reviewer needs to evaluate capitalization
- Reason pulled: "R&M strict scope" / "Software — keyword match" / "Other — judgment"

## Notes

- Highest-impact when an entity has aggressive expensing or weak capitalization controls.
- If R&M expense is small relative to TM, the strict-scope sample may be empty — that's fine. Document the threshold applied and the population reviewed.
- Coordinate with `fs-fixed-asset-additions`. Between the two samples, the auditor gets coverage of both directions: recorded additions tested for valid capitalization, and expense accounts searched for missed capitalization.
