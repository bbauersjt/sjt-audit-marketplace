---
name: single-audit
type: workflow-driven
needs_tm: false
---

# Single Audit

Not a sizing formula in itself — this is a marker that the sample follows the full single-audit workflow in `references/single-audit-workflow.md`.

## When to use
- Any single-audit major-program sample where sizing depends on cross-program control minimums, IDC handling, and per-program substantive sizing
- Always for `sa-major-program-transactions` and other SA samples that operate at the program level

## Size determination
**See `references/single-audit-workflow.md`.** The workflow handles:
- Major program identification and population
- Program materiality (5% of program expenditures)
- Cross-program control minimums (≥ 25 occurrences each for material payroll / disbursements control sets)
- Per-program substantive sample sizing (25 if RMM medium-or-lower AND controls expected reliable, else 40)
- IDC selections (≥ 1 per material program, max 2)

## When NOT to use
- Non-single-audit contexts — use `compliance-sample`, `control-sample`, `controls-substantive-dual`, or a substantive method as appropriate
