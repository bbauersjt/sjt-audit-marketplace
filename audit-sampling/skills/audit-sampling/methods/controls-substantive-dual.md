---
name: controls-substantive-dual
type: dual-purpose (controls + substantive)
needs_tm: false
---

# Controls / Substantive Dual

## Concept
A single sample serving both a tests-of-controls objective and a substantive objective. Most commonly used in **EBP audits** where the same selection (e.g., distributions, contributions, loans) is tested for both control operating effectiveness and substantive accuracy.

## Size determination
- **Population ≥ 250**: n = **25**
- **Population < 250**: n = **max(5, ceil(population × 10%))**

**Floor of 5.** Cap of 25 (the 10% scaling never produces n > 25 because populations ≥ 250 use the fixed 25).

The sample must also satisfy the substantive sampling criteria for the assertion under test (the procedure performed on each selection covers both the control attribute and the substantive question). See **Substantive adequacy gate** below.

## Substantive adequacy gate

After computing n above, the sample must meet **at least one** of the four substantive test requirements before it can be accepted. If none are met, bump n (add selections — typically chase the highest remaining dollars to gain coverage or knock the untested tail under TM) until at least one is satisfied.

1. **60% coverage** — selections cover ≥ 60% of cleaned population dollars
2. **Test-to-below-TM** — untested dollar tail (population total minus dollars covered by selections) ≤ TM
3. **Sampling form** — n meets or exceeds the firm sampling form result (TODO until firm sampling form supplied — currently skip this requirement, mirroring `methods/substantive.md`)
4. **Controls-substantive fallback** — n ≥ 25

Document which requirement was met. If n was bumped above the controls sizing (max(5, 10%) or 25) to satisfy the gate, document the bump and the driver.

## When to use
- EBP distributions, contributions, loans testing where both control and substantive objectives apply
- Any test where a single selection from a single population can satisfy both objectives

## When NOT to use
- Pure compliance attribute testing without a substantive component (use `compliance-sample`)
- Tests of controls only (use `control-sample`)
- When the populations or sampling units differ between objectives — pull separate samples

## Population assumptions
- Sampling unit identical for both objectives
- Population count drives n; dollar magnitude is irrelevant for sizing under this method (substantive evaluation still occurs at the selection level)
- Cleaned population reconciled to source

## Selection logic
Random selection across the cleaned population, subject to general selection bias rules (avoid trivially small items, avoid negatives unless MD says otherwise, etc.). Stratification optional per sample MD.

## Notes
- This is a different method from the single-audit dual-purpose sample (`controls-compliance-dual`) — the SA version is more complex and program-specific.
