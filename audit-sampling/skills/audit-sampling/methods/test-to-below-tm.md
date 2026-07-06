---
name: test-to-below-tm
type: coverage / substantive
needs_tm: true
---

# Test to Below TM

## Concept
Sample the largest items individually until the remaining untested population is below tolerable misstatement (TM) — i.e., even if the entire untested remainder were misstated, it could not exceed TM. Often produces the smallest n in highly skewed populations.

## Size determination
TODO — confirm firm-specific rules. Default pattern:
1. Sort cleaned population by absolute amount descending
2. Cumulative-sum the items NOT yet selected (i.e., the remainder)
3. Select items from the top until `population_total − cumulative_selected_total ≤ TM`
4. n = number of items selected

Equivalently: keep selecting from the top until the untested tail is ≤ TM.

## When to use
- Highly skewed populations where a few large items account for most of the dollars
- Balance or transaction stream testing where TM is the relevant threshold
- When 60% coverage would be larger than the TM-based cutoff

## When NOT to use
- Compliance / control objectives
- Populations where TM is not the relevant threshold (use sampling-form or compliance-sample)
- Populations without meaningful concentration — the n will balloon

## Population assumptions
- TM provided by user (whole-dollar amount, confirmed units)
- Voided / reversed entries excluded
- Sampling at the unit specified by the sample MD
- Negative items: TODO — confirm whether absolute value applies, or whether negatives are scoped separately
