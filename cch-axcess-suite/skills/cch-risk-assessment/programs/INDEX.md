# Programs Library — Index

Per-FS-area audit program references. Each MD captures the firm's step library for one CCH AUD-8xx program, with assertion tags, tailoring defaults, typical responses, and typical workpaper references.

## Template

**`cash.md` is the canonical template.** Every program MD follows the same structure: Form anatomy → How a program ties together (cross-form workflow) → Primary Audit Objectives → Tailoring Questions → Complete Step Library (V=visible, L=library) → Step→Assertion coverage matrix → PlannedAuditApproach mapping → Default Step Selection per audit type → Typical Workpaper References → API specifics → TODO.

## How a program ties together (universal chain)

```
Tailoring Questions → drives IsApplicable on each step
        ↓
Program Steps Library (.{AREA}.ProgramSteps)
   - All steps; visible:true = in active program, visible:false = sidebar/library
   - Each step has Assertion="EO;RO;CO;..." (semicolon-separated valueKey)
        ↓
RelevantAssertion (.{AREA}.RelevantAssertion)
   - Per assertion row: selected, ir, cr, rmm, PlannedAuditApproach, ProgramSteps
   - ProgramSteps = read-only rollup from steps whose Assertion includes this row's key
        ↓
Audit Approach checkboxes (Combined / Substantive Analytical / Substantive In-depth)
```

**Links you write:** the `Assertion` valueKey on each step (semicolon-separated).
**Links CCH computes:** the `ProgramSteps` column on RelevantAssertion (rollup).
**Things gating step availability:** the `IsApplicable` flag, driven by tailoring questions.

## Universal conventions

**`_conventions.md` — read this before building any new program MD.** Captures cross-program rules:
- Step → Assertion → RMM linkage convention (semicolon-joined, full-state writes).
- Fraud Awareness (AU-C 240) + Information as Audit Evidence (AU-C 500) — both need explicit assertion + risk linkage to clear CCH diagnostics.
- Management Override linkage convention.
- PlannedAuditApproach decision algorithm (Combined / Analytical / In-depth).
- IR / CR / RMM write ordering (selected→ir; RMM from recommendedAnswer).
- N/A assertion per area (Cash→AV, Investments→CU, PPE→CU, AP/OL/Equity→RO).
- Risk-area programs (JE2, RPTRNS2, FAIRVALUE2, COMMIT, CONCENT) and their universal defaults.

## Programs are keyed by AREA (binding key), not by AUD number

The AUD-8xx **numbers below are the NPO (Not-for-Profit) title's numbering** and are **not** universal — the same number maps to different areas across titles (AUD-804 = Split-Interest in NPO but Inventory in Commercial, Other Assets in EBP, Nonexchange Revenue in Governmental). A program MD is keyed by its **binding key** (CASH, AR, PPE…); resolve the AUD number for the engagement's title via **`scoping/area-map-by-title.md`**. Cash is AUD-801 in every title (the one constant).

## Status

(AUD # column = **NPO title** numbering — see caveat above; resolve other titles via `scoping/area-map-by-title.md`.)

| Program | AUD # (NPO) | dataBindingKey | Status |
|---|---|---|---|
| Cash | AUD-801 | CASH | **Complete inventory** — 20 steps captured, linking verified |
| Investments | AUD-802 | INVEST | **Complete inventory** |
| Accounts Receivable & Revenue | AUD-803 | AR | Skeleton |
| Split-Interest Agreements | AUD-804 | SPLITINTX | Skeleton (NPO-specific) |
| Contributions, Support, Program Revenue | AUD-805 | REVANDRECEIVABLESX | Skeleton (NPO-specific) |
| Inventory & COGS | AUD-806 | INVENTORY | Skeleton |
| Prepaids & Other Assets | AUD-807 | PP | Skeleton |
| Intangibles | AUD-808 | INTANG | Skeleton |
| Property & Equipment | AUD-809 | PPE | Skeleton |
| Accounts Payable | AUD-810 | AP | Skeleton |
| Payroll & Related Liabilities | AUD-811 | OL | Skeleton |
| Income Taxes / UBI | AUD-812 | INCTAX | Skeleton |
| Debt & Debt Service | AUD-813 | DEBT | Skeleton |
| Equity / Net Assets | AUD-814 | EQUITY | Skeleton |
| Other Income/Expense | AUD-815 | OTHREV | Skeleton |
| Journal Entries | AUD-816 | JE2 | Skeleton |
| Related Party Transactions | AUD-817 | RPTRNS2 | Skeleton |
| Fair Value Measurements | AUD-818 | FAIRVALUE2 | **Complete inventory** |
| Commitments & Contingencies | AUD-819 | COMMIT | Skeleton |
| Accounting Estimates | AUD-820 | ESTIMATES | Skeleton |
| Concentrations | AUD-821 | CONCENT | Skeleton |
| Business Combinations | AUD-822 | BUSINESS | Skeleton |

## How to capture a new program

1. On a live engagement, navigate to: `/binder/{eng}/workpaper-ref/{titleId}/workpaper/{currentWpId}/AUD_800_CUSTOM/{dbk}` (SPA resolves to wpId — may take 5–15s).
2. GET `/api/Workpaper/{eng}/{wpId}` and parse collections.
3. Inventory `.{dbk}.ProgramSteps` rows (Name, Assertion, IsApplicable, IsProgramStepRequired, visible).
4. Confirm `.{dbk}.RelevantAssertion` shape (should always be 6 assertions: EO, RO, CO, AV, CU, UC).
5. Capture tailoring questions from `.{dbk}.TailoringQuestions`.
6. Fill the program MD using `cash.md`'s structure.
7. Update the status table here.

## Industry-specific notes

- **NPO** has AUD-804 (Split-Interest) and AUD-805 (Contributions/Support) — these don't exist in commercial titles.
- **EBP** has its own forms (Contributions, Participant Data, Benefit Payments, Investments, Notes Receivable from Participants) — different AUD-8xx series, capture separately when an EBP engagement is open.
- **CNS** has Construction Contract-related Accounts — separate AUD-8xx, captures TBD.
- **HOA** has Replacement Reserves — separate AUD-8xx, captures TBD.
- **ALG** has Governmental Funds / Proprietary Funds revenue, Debt Service, Landfills, Grants — separate AUD-8xx, captures TBD.

The skeletons above cover the common cross-title program set. Add new MDs as industry-specific forms are encountered.

## Why this matters

The skill's long-term value comes from these program MDs being filled out completely. When complete, Claude can:

- Apply firm-standard default step selection to a new engagement's programs in one pass
- Suggest typical responses to tailoring questions per audit type
- Pre-fill the typical workpaper reference for each step
- Verify step→assertion linkages match the firm's norm

Until then, each MD is partial. Use what's there; flag what isn't.
