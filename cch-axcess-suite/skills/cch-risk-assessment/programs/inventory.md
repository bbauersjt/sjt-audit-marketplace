# Inventories and Cost of Sales — AUD-806 Audit Program

**CCH form:** AUD-806 Inventories and Cost of Sales
**dataBindingKey:** `INVENTORY`
**Area summary:** Inventory existence, valuation, cutoff; COGS

> **Skeleton — not yet captured from a live engagement.** Use `cash.md` as the canonical template pattern. To populate this MD, open AUD-806 in CCH on a real engagement, GET the form via API, and follow the cash.md structure (Form anatomy → Primary Audit Objectives → Tailoring Questions → Step Library → coverage matrix → Default Selection → typical WP refs).

## How a program ties together

Same chain as cash.md — Tailoring Questions drive `IsApplicable` → Step Library (`.INVENTORY.ProgramSteps`) → step's `Assertion="EO;CO;..."` valueKey links to `.INVENTORY.RelevantAssertion` rollup → PlannedAuditApproach checkbox per assertion.

## Sections to capture (TBD)

- [ ] Form anatomy (per-area collections under `.INVENTORY.*`)
- [ ] Primary Audit Objectives
- [ ] Tailoring Questions + firm defaults
- [ ] Complete Step Library (all steps + V/L status + Assertions + Req + App)
- [ ] Step → Assertion coverage matrix
- [ ] Default Step Selection per audit type (ALG/ASB/CNS/EBP/HOA/NPO)
- [ ] Typical workpaper references per step
- [ ] PlannedAuditApproach standard mapping per RMM level
- [ ] API specifics confirmed (workpaperId resolution, write paths)

## Capture procedure

1. On a live engagement, navigate to the form: `/binder/{eng}/workpaper-ref/{titleId}/workpaper/{currentWpId}/AUD_800_CUSTOM/INVENTORY` (SPA resolves to wpId).
2. GET `/api/Workpaper/{eng}/{wpId}` and parse collections.
3. Inventory `.INVENTORY.ProgramSteps` rows: Name, Assertion, IsApplicable, IsProgramStepRequired, visible.
4. Confirm assertion list on `.INVENTORY.RelevantAssertion`.
5. Capture tailoring questions from `.INVENTORY.TailoringQuestions`.
6. Fill this MD using `cash.md`'s structure.

## TODO

- [ ] First capture pass against a real AUD-806 on an active engagement
