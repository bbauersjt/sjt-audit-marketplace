# Cash — AUD-801 Audit Program

**CCH form:** AUD-801 Audit Program Cash
**dataBindingKey:** `CASH`
**Default-applies-to:** all six audit types (ALG, ASB, CNS, EBP, HOA, NPO).

> **Template pattern for every program MD.** Same structure should be used for all `programs/{area}.md`.
> This file is JUDGMENT: which steps, which assertions, which approach, what the firm's typical responses
> are. **All platform mechanics — field locators, valueKey codes, endpoint URLs, write payloads, submit/verify
> — live in `cch-axcess` (`fill-kc-form.md` for RelevantAssertion/IR/CR/RMM property writes,
> `populate-program.md` for the full step build-out pipeline, `toggle-program-step.md` for steps-in/out only,
> + `field-conventions`).** Name the program + the values in a HANDOFF; let `cch-axcess` execute.

## How a program ties together (conceptual model)

CCH's audit-program model links six collections per area. Understanding the chain is what lets this skill
decide the right HANDOFF; the write mechanics themselves belong to `cch-axcess`.

```
Tailoring Questions   ───► drive IsApplicable on each step
        │
        ▼
Program Steps Library
   - All available steps live here (in-program vs sidebar/library)
   - Each step carries its Assertion set (the CCH 6: EO, RO, CO, AV, CU, UC)
        │
        ▼
RelevantAssertion (per area)
   - Per assertion: selected (relevant?), IR, CR, RMM, planned approach, and a read-only
     rollup of the steps whose Assertion set includes this assertion
        │
        ▼
Planned approach per assertion: Combined / Substantive Analytical / Substantive In-depth
   - Combined available only when CR < MAX
```

**Linking a step to assertions** = set the step's Assertion set to the relevant codes (subset of EO, RO,
CO, AV, CU, UC); the RelevantAssertion rollup updates automatically.

**Linking RMMs to a step (Link to Risk)** = set the step's risk links to the matching `RMM-{assertion}` for
each assertion on the step (skip N/A assertions like AV for Cash), preserving any existing FS-level risks.
Full-state replacement, not incremental.

**`IsApplicable` is computed, not set** — it's driven by the tailoring-question answers. Library steps with
IsApplicable=False are gated until the relevant tailoring question is answered Yes. **`IsProgramStepRequired`**
flags steps the firm/title considers mandatory when applicable.

> The exact property keys, valueKey formats, the add-step mechanism, and the submit/verify cycle are
> `cch-axcess`'s — read them there, don't restate them here.

## Form anatomy (sections, in plain terms)

| # | Section | Notes |
|---|---|---|
| 0 | Assertion legend | EO/RO/CO/AV/CU/UC reference |
| 1 | Materiality | FS-level materiality allocated to area |
| 2 | Primary Audit Objectives | 5 standard objectives, mapped to assertions |
| 3 | Control Testing | questions about controls testing |
| 4 | FS-Level Risks | Management Override + engagement-specific |
| 5 | Identified Risks | engagement-added significant risks |
| 6 | **Per-Assertion Grid** | DERIVED view (6 assertions) — reads through the IR/CR/RMM/approach set on KBA-502 (the write target); never write it here |
| 7 | Substantive Analytical Info | free-text + WP refs |
| 8 | Tailoring Questions | the Y/N drivers |
| 9 | **Step Library** | all steps; in-program vs library |
| 10 | Results | per-engagement findings |
| 11 | Findings | issue documentation |
| 12 | Risk Modification | per-engagement adjustments |

## Primary Audit Objectives

| # | Objective | Assertions |
|---|---|---|
| 1 | Cash exists and is owned by the entity as of the statement of financial position date. | EO, RO |
| 2 | Cash receipts and cash disbursements are recorded correctly as to account, amount, and period. | EO, CO, AV, CU, UC |
| 3 | Cash balances include funds at all locations, funds with custodians, and deposits in transit. | EO, CO, CU |
| 4 | Cash is properly classified and presented in the financial statements in accordance with the applicable financial reporting framework. | EO, CO, AV, UC |

## Tailoring Questions (6)

| # | Question | Drives |
|---|---|---|
| 1 | Use analytical procedures (alone or combined) as a substantive procedure? | Enables Cash Analytical Procedures, Analytical Procedures steps |
| 2 | Plan on requesting cutoff bank statements? | Modifies Subsequent Bank Stmts step; enables Request Cutoff Statements step |
| 3 | Entity has interest-bearing cash accounts? | Enables Interest Bearing Cash Accounts step |
| 4 | Cash accounts at more than one financial institution? | Enables Confirmation-related steps |
| 5 | Petty cash material? | Enables Petty Cash step |
| 6 | (additional, varies by engagement) | — |

## Complete Step Library (20 steps)

**Legend:** **V** = currently visible in program, **L** = library (sidebar; can be added). **Req** =
required when applicable. **App** = applicable (False means gated by a tailoring question).

| # | Status | Step Name | Assertions | Req | App | Notes |
|---|---|---|---|---|---|---|
| 0 | L | Cash Analytical Procedures | EO;RO;CO;AV;CU | T | F | Gated by Q1 (analytical procedures) |
| 1 | V | Account Summary | EO;CO;CU | T | T | Always — listing of all cash accounts; linked to Management Override |
| 2 | L | Significant Accounting Estimates | AV | T | T | If AV risk elevated |
| 3 | L | Open or Closed Accounts | EO;RO;CO | T | T | Accounts opened/closed during period |
| 4 | L | Cash Confirmations-Preparation | EO;RO;CO;AV;CU | T | T | Prep work before confirmation send |
| 5 | L | Request Cutoff Statements | EO;RO;CO;AV;CU | T | F | Gated by Q2 (cutoff statements) |
| 6 | V | Subsequent Bank Statements | EO;CO;AV;CU | T | T | Always — review month-after statement; linked to Management Override |
| 7 | V | Bank Reconciliations | EO;CO;AV;CU;UC | f | T | Always — references AID-803 |
| 8 | L | Interest Bearing Cash Accounts | EO;RO;CO;AV;CU | T | F | Gated by Q3 (interest-bearing) |
| 9 | L | Bank Transfer Schedule | EO;CO;AV;CU;UC | T | F | Gated by Q4 (multiple institutions) |
| 10 | L | Petty Cash | EO;CO;AV;CU | T | F | Gated by Q5 (petty cash material) |
| 11 | L | Confirmations - Follow Up | (none) | T | T | Follow-up on non-responses |
| 12 | L | Confirmations - Testing | EO;RO;CO;AV;UC | T | T | Test confirmation results |
| 13 | V | Restrictions on Cash | RO;UC | f | T | Inquire about donor/legal restrictions (key for NPO) |
| 14 | V | Fraud Awareness | (none) | f | T | Always — alert for fraud indicators |
| 15 | L | Additional Procedures | EO;RO;CO;AV;UC | T | T | Catch-all for engagement-specific extra steps |
| 16 | V | Agree to Support | AV;UC | f | T | Tie FS amounts to support |
| 17 | V | Disclosures Testing | EO;CO;AV;UC | f | T | 3 sub-items: occurrence, completeness, presentation |
| 18 | V | Information To Be Used As Audit Evidence | (none) | f | T | AU-C 500 evaluation |
| 19 | L | Analytical Procedures | (none) | T | F | Gated by Q1 (alternate analytical step) |

## Step → Assertion coverage matrix (default-visible set)

| Assertion | Covered by steps |
|---|---|
| EO | 1 Account Summary, 6 Sub Bank Stmts, 7 Bank Recs, 17 Disclosures |
| RO | 13 Restrictions on Cash |
| CO | 1 Account Summary, 6 Sub Bank Stmts, 7 Bank Recs, 17 Disclosures |
| AV | 6 Sub Bank Stmts, 7 Bank Recs, 16 Agree to Support, 17 Disclosures |
| CU | 1 Account Summary, 6 Sub Bank Stmts, 7 Bank Recs |
| UC | 7 Bank Recs, 13 Restrictions, 16 Agree to Support, 17 Disclosures |

All 6 assertions have at least one step in the default-visible set. RO coverage relies entirely on step 13
(Restrictions on Cash) — for engagements with no donor/legal restrictions, consider adding step 4
(Confirmations-Prep) or 12 (Confirmations-Testing).

## Audit Approach (planned approach) — three choices per assertion

| Display | When |
|---|---|
| **Combined** | Controls tested and support CR < MAX |
| **Substantive: Analytical** | Active program includes analytical procedure steps |
| **Substantive: In-depth** | Active program is tests-of-details based |

**Firm default decision logic.** For each assertion, walk the active steps:
1. **Any analytical-nature step active?** (step 0 / step 19) → mark Analytical.
2. **Any tests-of-details step active?** (Account Summary, Bank Recs, Confirmations — most cash steps) → mark In-depth.
3. **CR < MAX?** (controls tested) → optionally mark Combined alongside.

For Cash with the firm's default 8-step set (no analytical steps, CR=MAX): **In-depth only on all 5
applicable assertions** (EO, RO, CO, CU, UC). AV is N/A for Cash. If Q1 enables analytical steps (0/19),
also mark Analytical.

> The approach valueKey codes and the write/confirm mechanics are in `cch-axcess`. Set `selected = Yes`
> before IR or it resets on submit — `cch-axcess` enforces the write order.

## Default Step Selection (firm defaults)

The 8 visible steps below are the **firm-standard default Cash step set** across all 6 audit types,
providing assertion coverage for EO, RO, CO, AV, CU, UC without analytical procedures.

| Step # | Step Name | ALG | ASB | CNS | EBP | HOA | NPO |
|---|---|---|---|---|---|---|---|
| 1 | Account Summary | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 6 | Subsequent Bank Statements | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 7 | Bank Reconciliations | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 13 | Restrictions on Cash | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 14 | Fraud Awareness | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 16 | Agree to Support | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 17 | Disclosures Testing | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 18 | Info as Audit Evidence | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 0/19 | Analytical Procedures | — | — | — | — | — | — (only when Q1 = Yes) |
| 3 | Open or Closed Accounts | — | — | — | — | — | — (add when accounts opened/closed materially) |
| 4/11/12 | Confirmation steps | — | — | — | — | — | — (add when Q4 = Yes or fraud risk elevated) |

## Typical Responses (owned by `cch-form-fill`)

Per-step Workpaper Reference / Comments text is **`cch-form-fill`'s to own** — to avoid the two drifting,
the single home for Cash response defaults lives there, in `cch-form-fill/references/section-library.md`
(the 1000-series / `FS` / `AID-803` reference conventions, the "Restrictions on Cash — no restrictions
noted" default, and which steps leave a blank engagement-specific WP ref). Pull the response text from that
file. This program MD owns only the step **selection** above; it does not carry the response table.

## Platform mechanics

All API specifics for this program — GET/resolve the workpaperId, the RelevantAssertion/IR/CR/RMM/approach
write payloads, the step build-out pipeline (tailoring → step selection → risk-linking → responses →
sign-off), and the submit-and-verify cycle — are in `cch-axcess` (`references/modules/fill-kc-form.md` for
property writes, `references/modules/populate-program.md` for the full step build-out, `references/modules/
toggle-program-step.md` for steps-in/out only, and `references/config/field-conventions.md`). This file does
not restate them; the HANDOFF names AUD-801 and the values, and `cch-axcess` executes.

## TODO

- [ ] Capture step Description text (full procedure) for each of the 20 steps.
- [ ] Confirm typical workpaper references against the firm's binder template.
- [ ] Fill in Default Step Selection nuances per audit type where they diverge.
