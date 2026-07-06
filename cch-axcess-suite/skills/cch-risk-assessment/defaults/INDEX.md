# Defaults — CCH Inherent Risk by Audit Type

Lean default IR per FS area + assertion, mapped from PPC L/M/H to CCH LOW/MOD/SBM. CR defaults to MAX in CCH; RMM derives from IR×CR matrix (see `../references/risk-framework.md`). Tune per engagement.

**These are IR *starting points*, consumed at KBA-502** (`../references/cascade/kba-502.md`). They are not the answer — adjust each per engagement facts and document the basis (KBA-503). An area is only assessed if it was scoped significant and its assertions selected on KBA-400.

**Audit-type code → CCH title:** ASB→Commercial, HOA→Commercial, CNS→Construction, EBP→Employee Benefit Plans, ALG→Governmental, NPO→Not-for-Profit. HOA uses the ASB (Commercial) defaults. Area names in these files map to binding keys via `../scoping/area-map-by-title.md`.

## Files

- **ALG.md** — Audits of Local Governments
- **ASB.md** — ASB Commercial (non-public commercial entities)
- **CNS.md** — Construction Contractors
- **EBP.md** — Employee Benefit Plans
- **HOA.md** — Homeowner / Common Interest Realty Associations
- **NPO.md** — Not-For-Profit
