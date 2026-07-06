---
name: 60-percent-coverage
type: coverage / substantive
needs_tm: true
---

# 60% Coverage

## Concept
Sample the top items by absolute dollar value until cumulative coverage hits 60% of the population total. The remaining 40% is left untested on the assumption the concentration of risk is in the largest items.

## Size determination
1. Sort cleaned population by absolute amount descending
2. Cumulative-sum dollars
3. Select all items down to (and including) the row where cumulative coverage first reaches or exceeds 60% of population total
4. **Check the untested 40%**: if the remaining (untested) population $ exceeds TM, **pull 3 additional items** from the smaller-items population (the untested remainder). These 3 should follow general selection bias rules — skew larger but include some coverage. Document the +3 in the documentation file.
5. n = number of items in the 60% block + any +3 additions

## When to use
- Substantive testing of skewed populations where a small number of items dominate the dollars
- Balance testing (AR, AP, accruals) where a coverage approach is acceptable

## When NOT to use
- Compliance / control objectives — use a compliance or control method instead
- Highly fragmented populations with no concentration — coverage produces a huge n; a sampling form may be smaller
- Populations where the assertion requires a specific confidence level (use sampling-form)

## Population as