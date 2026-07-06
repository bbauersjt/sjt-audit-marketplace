---
name: compliance-sample
type: attribute / compliance
needs_tm: false
---

# Compliance Sample

## Concept
Attribute-based sample for testing compliance with a regulatory requirement, contract term, or grant condition. n is driven by tolerable rate of deviation, expected deviation rate, and confidence level — not by dollars.

## Size determination
- **Population ≥ 250**: n = **25**
- **Population < 250**: n = **max(5, ceil(population × 10%))**

**Floor of 5** — no compliance sample falls below 5 regardless of population size.

This is the standalone compliance method — used when the test has no companion control or substantive objective. Typical use: state OSA compliance (vehicle usage, etc.) — anything that does **not** impact the financial statements.

If the same population is also being tested as part of a combined test (controls/compliance dual purpose), use `controls-compliance-dual` instead — don't double-count under both methods.

## When to use
- Standalone non-financial compliance — state OSA, regulatory attribute tests that don't tie to FS
- EBP eligibility / demographic testing where the test is purely attribute (no controls reliance, no substantive overlay)
- Any test with a yes/no compliance attribute and no companion controls / substantive objective

## When NOT to use
- Substantive dollar testing (use coverage / test-to-TM / sampling-form)
- Tests of operating effectiveness of internal controls (use control-sample, though there's overlap — see combined-compliance-control)

## Population assumptions
- Population