# Fair Value Measurements and Disclosures — AUD-818 Audit Program

**CCH form:** AUD-818 Audit Program Fair Value Measurements and Disclosures
**dataBindingKey:** `FAIRVALUE2`
**Default-applies-to:** all six audit types when fair-value-measured assets/liabilities are present.

> 15 library steps, 6 tailoring questions, 4 audit objectives. Much narrower than `investments.md` — this program is the FV-methodology overlay for any area that uses fair value (most often Investments via AUD-802).

## How a program ties together

Same chain as `cash.md`. Six TQs gate which of the 15 steps become `IsApplicable`. The 15 steps share `.FAIRVALUE2.RelevantAssertion` (6 assertions; AV is dominant here — FV is fundamentally an AV concern).

**Adding/removing steps from the active program** = `cch-axcess/references/modules/toggle-program-step.md`.

## Form anatomy

| # | Section | Collection path |
|---|---|---|
| 0 | Assertion legend | `.Common.FinancialAssertion` |
| 1 | Materiality | `.FAIRVALUE2.MaterialitySummary` |
| 2 | Primary Audit Objectives (4) | `.FAIRVALUE2.AuditObjective` |
| 3 | Control Testing (5 Qs) | `.FAIRVALUE2.ConTestingEffControlQuestion` |
| 4 | FS-Level Risks | `.FAIRVALUE2.AuditFinancialLevelRisks` |
| 5 | Identified Risks | `.FAIRVALUE2.AssertionLevelRisk` |
| 6 | **Per-Assertion Grid** | `.FAIRVALUE2.RelevantAssertion` |
| 7 | Substantive Analytical Info | `.FAIRVALUE2.InfoPerformSubsAnalyticalProc` |
| 8 | Tailoring Questions | `.FAIRVALUE2.TailoringQuestions` |
| 9 | **Step Library** | `.FAIRVALUE2.ProgramSteps` (15 rows) |
| 10 | Results | `.FAIRVALUE2.ResultsQuestion` |
| 11 | Findings | `.FAIRVALUE2.FindingsFlow`, `.FAIRVALUE2.FindingsUserEntry` |
| 12 | Risk Modification | `.FAIRVALUE2.RiskModification` |

## Primary Audit Objectives (4)

1. Transactions subject to FV measurement are identified, authorized, and recorded correctly as to account, amount, period.
2. Financial and other information is presented in accordance with the applicable framework.
3. (Not captured.)
4. Accounting estimates in this audit area are properly identified, authorized, recognized, measured, presented, and disclosed.

## Tailoring Questions (6)

| # | Visible | Key | Question | Gates |
|---|---|---|---|---|
| 0 | T | FairValue2_TQ_ThirdParty | Did the entity retain a third-party pricing agency? | Step 1 |
| 1 | T | FairValue2_TQ_SpecialistEstFV | Was a specialist engaged to estimate FV? | Steps 3, 4 |
| 2 | T | FairValue2_TQ_ImpendingTrans | Plan to use an impending transaction as the basis for FV estimate? | Step 7 |
| 3 | T | FairValue2_TQ_FVMeasureDiffDate | FV measurement made on different date from FS date? | Step 9 |
| 4 | T | FairValue2_TQ_CollateralImpFactor | Collateral important to FV/carrying amount? | Step 10 |
| 5 | T | FairValue2_TQ_AnalyticalProcedures | Use analytical procedures? | Step 14 |

> All 6 TQs are `defaultanswer` (unanswered) on a fresh/unstarted AUD-818 — verify on the engagement whether the form has actually been tailored yet before assuming these values are meaningful.

## Complete Step Library (15 steps)

**Legend:** All 15 steps default to `IsApplicable: True` per the GET — interesting, suggesting the form doesn't gate as aggressively as AUD-802. TQ answers may still affect which are practically meaningful even if not gated to `False`. All 15 default to `visible: false` on a fresh form.

| Idx | Step Name | Assertions | App | Notes |
|---|---|---|---|---|
| 0 | Understanding of Fair Value Measurements | EO;CO;AV | T | Always — methodology baseline |
| 1 | External Pricing and Valuation Services | AV;UC | T | When Q0 = Yes (3rd-party pricing) |
| 2 | Understanding of Valuation Technique | CO;AV;UC | T | Always |
| 3 | Specialized Skills or Knowledge for Engagement Team | AV | T | When Q1 = Yes |
| 4 | Management's Specialist | AV | T | When Q1 = Yes (AU-C 500/620) |
| 5 | Fair Value Procedures | AV | T | Core substantive |
| 6 | Measurements and Disclosures | AV;UC | T | Always |
| 7 | Impending Transactions | AV | T | When Q2 = Yes |
| 8 | Subsequent Transactions | AV | T | If post-balance-sheet transactions inform FV |
| 9 | Different Measurement Date | AV | T | When Q3 = Yes |
| 10 | Collateral | EO;RO;AV;UC | T | When Q4 = Yes |
| 11 | Those Charged with Governance Informed | AV | T | Communication step |
| 12 | Disclosures Testing | — | T | Always |
| 13 | Information To Be Used As Audit Evidence | — | T | AU-C 500 |
| 14 | Analytical Procedures | — | T | When Q5 = Yes |

## Default Step Selection (firm defaults — TBD)

> **Not yet locked** — pending working capture against a tailored engagement.

**Starting baseline for NPO with marketable securities priced via broker statements (Level 1 dominant) + a beneficial interest in a community foundation (likely Level 3 / NAV):**

| Idx | Step | Why |
|---|---|---|
| 0 | Understanding of FV Measurements | Document approach (Level 1 broker pricing + Level 3 NAV for community foundation interest) |
| 2 | Understanding of Valuation Technique | Technique varies by holding; document |
| 5 | Fair Value Procedures | Substantive FV testing of broker stmts + community-foundation NAV statement |
| 6 | Measurements and Disclosures | Disclosure tie-in (Level 1/2/3 hierarchy) |
| 11 | Those Charged with Governance Informed | If FV estimates are material to FS |
| 12 | Disclosures Testing | FV hierarchy disclosure |
| 13 | Information To Be Used As Audit Evidence | Custodian stmt + community-foundation audited FS evaluation |

Add as engagement warrants:
- Step 1 if the custodian's pricing is via an external pricing service (research before answering Q0).
- Step 4 if the community foundation's NAV statement is treated as management's specialist work (AU-C 500/620 evaluation).
- Step 14 if analytical procedures are planned.

## Audit Approach

Same 3-checkbox model as Cash. For Level 1 broker-priced securities → `INDEPTH`. Add `ANALYTICAL` if step 14 is used. `COMBINED` only if controls are tested and CR < MAX (rare for FV at a small NPO).

## API specifics

- **dataBindingKey:** `FAIRVALUE2` (note the trailing "2" — distinct from older legacy `FAIRVALUE`).
- **Step library:** `.FAIRVALUE2.ProgramSteps` (15 rows).
- **Add/remove:** Same `POST /api/Workpaper/UpdateProgramStep` mechanism; see `cch-axcess/references/modules/toggle-program-step.md`.
- **Per-assertion grid:** `.FAIRVALUE2.RelevantAssertion` (6 rows).
- **IR/CR/RMM/Approach:** See `fill-kc-form.md`. Swap `.CASH.` → `.FAIRVALUE2.`.

## Linkage to AUD-802

`AUD-802 TQ #35` (FairValueRules: "Are there investments in securities or derivative instruments valued based on Fair Value rules?") drives whether AUD-818 work is needed. For an NPO holding broker-priced marketable securities and/or a beneficial-interest-type asset, this is typically functionally Yes. **Verify on the engagement** whether AUD-802 Q35 actually reads Yes/No consistent with the real portfolio — a "No" answer alongside FV-measured holdings on the TB is a mismatch worth flagging for engagement-team review, not something to assume either way from this template.

## TODO (deferred capture)

- [ ] Capture objective #3 (filtered in API output).
- [ ] Lock firm default step set after a tailored engagement is worked.
- [ ] Per-step typical workpaper references.
- [ ] Verify whether AUD-818 is auto-pulled into the binder when AUD-802 TQ #35 = Yes, or whether it must be added separately.
