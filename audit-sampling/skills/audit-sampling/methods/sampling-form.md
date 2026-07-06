---
name: sampling-form
type: substantive (statistical / non-statistical)
needs_tm: true
---

# Sampling Form

## Concept
Firm sampling form (statistical or non-statistical) where n is computed from a set of inputs — population, expected misstatement, tolerable misstatement, risk of incorrect acceptance / inherent and control risk, sometimes confidence factor.

## Size determination
TODO — drop in firm sampling form logic. Typical inputs:
- Population $ (cleaned)
- Tolerable misstatement (TM)
- Expected misstatement
- Risk factor / confidence factor (driven by RoMM, control reliance)
- Stratification thresholds (if any)

Output: n (and threshold for individually significant items, if MUS).

## When to use
- Substantive testing where coverage methods aren't acceptable or produce a worse n
- When stratification or formal statistical inference is needed
- When firm methodology requires the sampling form for the assertion under test

## When NOT to use
- Pure compliance / attribute objectives (use compliance-sample)
- Populations small enough that 100% testing is more efficient

## Population assumptions
- TM provided
- RoMM / control reliance assessment available (or a default per firm guidance)
- Cleaned population reconciled to source

## Notes
The sampling form often produces a smaller n than 60% coverage in fragmented populations and a larger n than test-to-below-TM in highly skewed populations. Compute and compare per the default MO.
