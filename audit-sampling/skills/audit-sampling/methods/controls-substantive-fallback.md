---
name: controls-substantive-fallback
type: substantive (fallback)
needs_tm: false
assumed_n: 25
---

# Controls Substantive Fallback (Convert to Controls Test)

## Concept
A pivot from a pure substantive approach to a controls-reliance approach when no substantive-only method can produce a defensible sample of reasonable size.

The procedure is structured as a tests-of-controls sample (n = 25 ceiling per controls sampling tables), and reliance on the controls supports the financial statement assertion. Each selection is also examined substantively, but the audit conclusion rests on control operating effectiveness — not on dollar coverage or untested-tail-below-TM logic.

Used when the other three substantive methods (60% coverage, test-to-below-TM, sampling form) all produce samples larger than 25. Rather than pulling an oversized substantive sample, switch the engagement approach: test controls and rely on them.

## Size determination
**n = 25** — always. No formula, no population dependency.

## When to use in the default MO comparison
Included in the four-way comparison as **always n = 25**. The skill compares:
- 60% coverage → n_60
- Test-to-below-TM → n_TM
- Sampling form → n_form
- Controls substantive fallback → 25

And picks the smallest. This method "wins" only when the others all exceed 25 — i.e., when the population is fragmented enough that pure substantive methods produce large samples. Winning means the engagement pivots to controls reliance for that assertion; staff and reviewers should understand a controls test is being performed, not just a substantive one.

## Selection logic
Selections are still substantive in nature — pick from the cleaned population using a method that supports the substantive assertion (typically random or stratified random across the population). This is not a true tests-of-controls procedure; the n=25 ceiling comes from controls-style sampling tables, but the procedure performed on each selection is substantive.

## When NOT to use
- When a coverage / TM-based method produces a smaller n
- When the assertion truly requires a controls test (use `control-sample`)
- When the assertion is compliance-based (use `compliance-sample`)
