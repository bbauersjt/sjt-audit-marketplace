# Investments Including Programmatic Investments — AUD-802 Audit Program

**CCH form:** AUD-802 Audit Program Investments Including Programmatic Investments
**dataBindingKey:** `INVEST`
**Default-applies-to:** all six audit types (ALG, ASB, CNS, EBP, HOA, NPO).

> **Captured live 2026-05-21 from APNM 2025 NPO.** 115 library steps, 39 tailoring questions, 11 audit objectives. Far richer than `cash.md` — this program covers debt/equity securities, alt investments (equity method, joint ventures, derivatives, asset-backed), digital/crypto assets, programmatic investments, investment pools, NPO-specific contributed investments and restricted endowments.

## How a program ties together

Same chain as `cash.md` — Tailoring Questions drive `IsApplicable` → Step Library (`.INVEST.ProgramSteps`) → step's `Assertion="EO;CO;..."` valueKey links to `.INVEST.RelevantAssertion` rollup → PlannedAuditApproach checkbox per assertion. See `cash.md` for the chain explanation.

**Adding/removing steps from the active program** = full-state-replacement POST. See `cch-axcess/references/modules/toggle-program-step.md`.

## Form anatomy

| # | Section | Collection path | Notes |
|---|---|---|---|
| 0 | Assertion legend | `.Common.FinancialAssertion` | EO/RO/CO/AV/CU/UC reference |
| 1 | Materiality | `.INVEST.MaterialitySummary` | FS-level materiality allocated to area |
| 2 | Primary Audit Objectives | `.INVEST.AuditObjective` | 11 standard objectives |
| 3 | Control Testing | `.INVEST.ConTestingEffControlQuestion` | 5 questions about controls testing |
| 4 | FS-Level Risks | `.INVEST.AuditFinancialLevelRisks` | Management Override + engagement-specific |
| 5 | Identified Risks | `.INVEST.AssertionLevelRisk` | Engagement-added significant risks |
| 6 | **Per-Assertion Grid** | `.INVEST.RelevantAssertion` | 6 assertions |
| 7 | Substantive Analytical Info | `.INVEST.InfoPerformSubsAnalyticalProc` | Free-text + WP refs |
| 8 | Flow Tailoring Questions | `.INVEST.FlowTailoringQuestions` | 2 flow-driver questions |
| 9 | Tailoring Questions | `.INVEST.TailoringQuestions` | 39 Y/N drivers (heavy gating) |
| 10 | **Step Library** | `.INVEST.ProgramSteps` | 115 steps |
| 11 | Results | `.INVEST.ResultsQuestion` | 4 per-engagement findings |
| 12 | Findings | `.INVEST.FindingsFlow`, `.INVEST.FindingsUserEntry` | Issue documentation |
| 13 | Risk Modification | `.INVEST.RiskModification` | Per-engagement adjustments |

## Primary Audit Objectives (11)

1. Debt and equity investments reflected in the SFP include investments on hand and in custody of third parties, and evidence of ownership exists.
2. Investment transactions and related realized/unrealized income or loss are recorded correctly as to account, amount, period; properly allocated by fund.
3. Investments are properly classified and presented per applicable framework; disclosures clearly expressed and at appropriate amounts.
4. Restrictions on contributed investments have been complied with.
5. Restrictions on investment income, net realized gains, and net recognized unrealized gains (donor/legal) have been complied with.
6. Investments and related income/gains/losses are reported in the appropriate net asset class.
7. Net assets with donor restrictions are reclassified as without donor restrictions when restrictions are met.
8. Debt and equity investments are carried at cost (minus impairment) or fair value, as appropriate.
9. Recorded and disclosed fair values for investments are clearly expressed and at appropriate amounts.
10. Investments and derivatives are identified, measured, recorded, classified, and presented per the applicable framework.
11. Accounting estimates are properly identified, authorized, recognized, measured, presented, and disclosed.

## Tailoring Questions (39)

Top-level visible (always shown). Gated questions (visible: false) appear when a parent is answered Yes.

| # | Visible | Key | Question (abbreviated) | Gates |
|---|---|---|---|---|
| 0 | T | Securities | Investments in debt/equity securities & mutual funds? | Most marketable-securities steps |
| 1 | T | SecuritiesonHand | Investment instruments on hand? | Step 5 |
| 2 | T | IndependentThird | Instruments held by independent 3rd parties? | Steps 6, 7, 8 |
| 3 | T | PreferredShares | Investments in preferred shares/debt securities? | Step 9 |
| 4 | T | Digital | Investments in digital/crypto assets? | Q5, Q6, steps 21–29 |
| 5 | F | DigitalCrypto | Crypto classified as "held to maturity"? | (gated by Q4) |
| 6 | F | CryptoAssets | Crypto classified as "held for self-custody"? | (gated by Q4) |
| 7 | T | SalesFinancial | Transfers/sales of financial instruments during period? | Steps 30–33 |
| 8 | T | Corporations | Closely-held corps/partnerships, equity method? | Q9–Q11, steps 34–49 |
| 9 | F | FinancialStatements | Carrying amount reflects unrecognized factors? | (gated by Q8) |
| 10 | F | DateOfEntity | Time lag between entity & investee FS? | (gated by Q8) |
| 11 | F | Transactions | Subsequent events of investee? | (gated by Q8) |
| 12 | T | JointVentures | Any interests in joint ventures? | Q13–Q23, steps 50–75 |
| 13 | F | CeasedControl | Ceased joint control? | (gated by Q12) |
| 14 | F | Operator | Operator/manager of JV? | (gated by Q12) |
| 15 | F | Subsidiary | JV became subsidiary/closely held? | (gated by Q12) |
| 16 | F | Contribute | Contributed/sold assets to JV? | (gated by Q12) |
| 17 | F | Purchase | Purchased assets from JV? | (gated by Q12) |
| 18 | F | AuditorApply | Another auditor applied procedures? | (gated by Q12) |
| 19 | F | ProportionateConsolidation | JV accounted using proportionate consolidation? | (gated by Q12) |
| 20 | F | EquityMethod | JV accounted using equity method? | (gated by Q12) |
| 21 | F | FairValueAssets | Carrying amount unrecognized factors (JV)? | (gated by Q12) |
| 22 | F | LagBetween | Time lag JV FS? | (gated by Q12) |
| 23 | F | BeforeTheDate | Subsequent events of JV? | (gated by Q12) |
| 24 | T | DerHedge | Derivatives or hedging activities? | Steps 76–80 |
| 25 | T | InvestmentPool | Entity operates an investment pool? | Steps 81–82 |
| 26 | T | PoolManagement | Investor in third-party-managed pool? | Steps 83–85 |
| 27 | T | RestrictedInvestments | Restrictions on investments? | Steps 86–88 |
| 28 | T | RestrictedNATransfers | Reclassification of restricted NA? | Step 89 |
| 29 | T | AssetBacked | Investments in asset-backed securities? | Step 90 |
| 30 | T | Endowment | Donor-restricted endowments? | Steps 91–92 |
| 31 | T | OtherInvestments | "Other Investments"? | Steps 93–94 |
| 32 | T | Programmatic | Programmatic investments (loans/equity/guarantees)? | Q33, Q34, steps 95–101 |
| 33 | F | Loans | Programmatic investments as loans? | (gated by Q32) |
| 34 | F | EquityInterests | Programmatic investments as equity? | (gated by Q32) |
| 35 | T | FairValueRules | Securities/derivatives valued under FV rules? | (drives AUD-818 linkage) |
| 36 | T | Components | Investments determined to be components of a group? | Steps 102–105 |
| 37 | T | SAS149 | SAS-149 early implemented? | Step 103 |
| 38 | T | Analytical | Use analytical procedures? | Step 114 |

## Complete Step Library (115 steps)

**Legend:** `Idx` = position in `.INVEST.ProgramSteps`. `App` = `IsApplicable` (T=ungated/always-on, F=gated by a TQ). All steps start `visible: false` (library); UI Add toggles to `visible: true`. The step `key` is a GUID (not listed below — pull from `.INVEST.ProgramSteps[i].key`).

### Core / always-applicable steps (App=T, default candidates)

| Idx | Step Name | Assertions |
|---|---|---|
| 0 | Debt and Equity Investments – Detailed Analysis | EO;RO;CO;AV;CU;UC |
| 1 | Investments - Arithmetical Accuracy | AV |
| 2 | Investments - Opening Balances | EO;AV;CU;UC |
| 3 | Reconciliations of Statements or Data Feeds from Custodians | EO;CO;AV |
| 4 | Master Netting Arrangements | EO;RO;CO;AV |
| 6 | Investments Held by Third Parties | EO;RO;CO;AV;CU;UC |
| 7 | Investments Held by Third Parties - Alternative Procedures | EO;RO;CO;AV;CU;UC |
| 9 | Terms of Preferred Shares and Debt Securities | EO;RO;AV;UC |
| 10 | Authorization of Investment Transactions | RO;CU;UC |
| 11 | Authorized Investments | EO |
| 12 | Bank, Broker, or Custodian Reports | EO;RO;CO;AV;CU;UC |
| 13 | Tracing Payments | EO;RO;AV;CU;UC |
| 14 | Amortization of Premium or Discount | EO;RO;CO;AV;CU;UC |
| 15 | Realized and Unrealized Gains and/or Losses | EO;RO;CO;AV;CU;UC |
| 16 | Investment Income | EO;RO;AV;CU;UC |
| 17 | Classification of Securities | UC |
| 18 | Pledged or Assigned | UC |
| 19 | Donated Securities | EO;CO;AV |
| 20 | Donated Financial Assets Sold | CO;AV;UC |
| 34 | Investments Valued Based on Investee's Financial Results - Not Components of a Group NOT Acc... | AV |
| 86 | Contributed Investments - Donor Correspondence | RO;UC |
| 87 | Contributed Investments - Minutes | RO;UC |
| 107 | Evaluation of Impairment Loss for All Investments | AV |
| 108 | Significant Accounting Estimates | AV |
| 109 | Fraud Awareness | AV |
| 110 | Additional Procedures | EO;CO;AV |
| 111 | Agree to Support | AV |
| 112 | Information To Be Used As Audit Evidence | — |
| 113 | Disclosures Testing | EO;CO;AV;UC |
| 114 | Analytical Procedures | — |

### TQ-gated steps (App=F)

| Idx | Step Name | Assertions | Gated by |
|---|---|---|---|
| 5 | Investment Instruments on Hand | EO;RO | Q1 SecuritiesonHand |
| 8 | Service Organization | EO;RO;CO;AV;CU;UC | Q2 IndependentThird (variant) |
| 21–29 | Digital/Crypto Assets (9 steps) | varies | Q4 Digital + Q5/Q6 |
| 30–33 | Transfers or Sales (4 steps) | varies | Q7 SalesFinancial |
| 35–49 | Equity Method (15 steps) | varies | Q8 Corporations |
| 50–75 | Joint Ventures (26 steps) | varies | Q12 JointVentures |
| 76–80 | Derivatives and Hedging (5 steps) | varies | Q24 DerHedge |
| 81–82 | Investment Pools (entity operates) | AV | Q25 InvestmentPool |
| 83–85 | Investment Pools (3rd-party managed) | EO/AV | Q26 PoolManagement |
| 88 | Dispositions of Restricted | RO;UC | Q27 RestrictedInvestments |
| 89 | Reclassification of Restricted Net Assets | RO;UC | Q28 RestrictedNATransfers |
| 90 | Asset-Backed Securities | EO;RO;CO;AV | Q29 AssetBacked |
| 91 | Restricted Endowments - Procedures | CO;AV | Q30 Endowment |
| 92 | Restricted Endowments - Deficiencies | AV;UC | Q30 Endowment |
| 93 | Other Investments - Management Policy | AV | Q31 OtherInvestments |
| 94 | Other Investments - Accounting | AV | Q31 OtherInvestments |
| 95 | Programmatic - Policies | EO | Q32 Programmatic |
| 96 | Programmatic - Investment Transactions | CO;AV | Q32 Programmatic |
| 97 | Programmatic - Disclosures | UC | Q32 Programmatic |
| 98 | Programmatic - Form of Loans | — | Q33 Loans |
| 99 | Programmatic - Form of Equity | — | Q34 EquityInterests |
| 100 | Programmatic - Impairment Loss | RO;AV | Q32 Programmatic |
| 101 | Programmatic - Guarantee Debt | — | Q32 Programmatic |
| 102 | Components of a Group (Pre-SAS-149) | — | Q36 Components |
| 103 | Components of a Group (SAS-149) | — | Q37 SAS149 |
| 104 | Components of a Group - Referred-to Auditor | — | Q36 Components |
| 105 | Components of a Group - Equity Method | — | Q36 Components |
| 106 | Fair Value Valuations and Accounting Estimates | — | Q35 FairValueRules |

## Default Step Selection (firm defaults — TBD)

> **Not yet locked.** APNM 2025's AUD-802 is unpopulated. Firm default for NPO investments needs a working session against an actively-tailored engagement to capture which subset the firm treats as universally-applied. Pending capture.

**Starting baseline candidates for NPO with marketable securities held by third-party custodian** (e.g., APNM's RBC accounts + ACF beneficial interest):

| Idx | Step | Why |
|---|---|---|
| 0 | Debt and Equity Investments – Detailed Analysis | Core analytical detail of investment activity |
| 1 | Arithmetical Accuracy | Cross-check totals from broker stmts |
| 2 | Opening Balances | Roll-forward tie-out |
| 3 | Reconciliations of Stmts/Data Feeds from Custodians | RBC stmts tie to GL |
| 6 | Investments Held by Third Parties | Confirmations from RBC + ACF |
| 12 | Bank, Broker, or Custodian Reports | Substantive reliance on broker statements |
| 15 | Realized and Unrealized Gains/Losses | Income statement tie-in |
| 16 | Investment Income | Dividends + interest tie-in |
| 17 | Classification of Securities | Net asset class allocation |
| 86 | Contributed Investments - Donor Correspondence | If donated securities present |
| 87 | Contributed Investments - Minutes | Board-level documentation |
| 91/92 | Restricted Endowments | If Q30 = Yes (verify ACF account treatment) |
| 109 | Fraud Awareness | Universal |
| 111 | Agree to Support | Tie to FS |
| 112 | Information To Be Used As Audit Evidence | AU-C 500 evaluation |
| 113 | Disclosures Testing | FS disclosures |
| 114 | Analytical Procedures | If Q38 = Yes (typical) |

Plus FV-side coverage from AUD-818 if Q35 (FairValueRules) = Yes.

## Audit Approach (PlannedAuditApproach)

Same 3-checkbox model as Cash (`COMBINED` / `ANALYTICAL` / `INDEPTH`). For RBC-held marketable securities under NPO with CR=MAX: `INDEPTH` on all applicable assertions, plus `ANALYTICAL` if Q38=Yes and step 114 is added.

## API specifics

- **GET form:** `GET /api/Workpaper/{eng}/{wpId}` (KC tokens from localStorage; see `cch-axcess/references/auth-discovery.md`).
- **dataBindingKey:** `INVEST`
- **Step library:** `.INVEST.ProgramSteps` (115 rows; `visible: true` = active, `visible: false` = library).
- **Add/remove steps:** POST `/api/Workpaper/UpdateProgramStep` with full-state `value` string (semicolon-joined step keys, plus all `childObjectList[].key` for parent steps with sub-steps). See `cch-axcess/references/modules/toggle-program-step.md`.
- **Per-assertion grid:** `.INVEST.RelevantAssertion` (6 rows).
- **IR/CR/RMM/PlannedAuditApproach writes:** See `cash.md` "API specifics" and `cch-axcess/references/modules/fill-kc-form.md`. Same pattern, swap `.CASH.` for `.INVEST.`.

## Title-variant: EBP — AUD-802A Audit Program Investments (Non-Certified / ERISA Plan)

> **Captured live 2026-05-21 from Kymera Physicians 401k Plan (EBP title `1b32bc1a-e119-4cc9-91fe-b2cb22f4e966`).** Same dataBindingKey `INVEST` as NFP, but the EBP variant of this program is materially different. Treat as a separate step library. Within CCH the form is labeled **AUD-802A** (vs NFP's AUD-802), distinguishing it from **AUD-802B** which covers limited-scope / certified plans.

**EBP also has a related form, AUD-802B Audit Program Investments (Certified)**, with dataBindingKey `LIMITED`. AUD-802B covers ERISA Section 103(a)(3)(C) limited-scope audits where the trustee provides a certified investment statement. Capture deferred — most Kymera-style 401k engagements use AUD-802B in practice. Add when an active limited-scope EBP engagement is opened.

### EBP form anatomy

Same 17-collection schema as NFP. Counts differ:

| Collection | NFP (AUD-802) | EBP (AUD-802A) | Notes |
|---|---|---|---|
| AuditObjective | 11 | 8 | EBP focuses on plan-asset/income/disclosure objectives; no net-asset-class objectives |
| TailoringQuestions | 39 | 17 | EBP is leaner; trust/insurance/derivative variants drive most gating |
| ProgramSteps | 115 | 42 | EBP has 36% as many steps; type-specific instrument procedures replace NFP's restriction/programmatic-investment branches |
| RelevantAssertion | 6 | 6 | Identical |
| FlowTailoringQuestions | 2 | 1 | One less flow-driver |

### EBP Primary Audit Objectives (8)

Captured 2026-05-21; values per `.INVEST.AuditObjective` rows 0–7. Distinct from NFP's 11 — EBP omits the net-asset-class reclassification objectives and the donor-restriction-compliance objectives, adds plan-document compliance.

### EBP Tailoring Questions (17)

All 17 are top-level visible. No gated/cascading questions in this version. Significantly different mix from NFP — focused on plan-asset types and ERISA-specific instrument forms.

| # | Key | Question (abbreviated) |
|---|---|---|
| 0 | SecuritiesonHand | Securities on hand? |
| 1 | IndependentThird | Investments held by independent third parties? |
| 2 | TransferCategories | Transfers between categories? |
| 3 | ExTradedFunds | Mutual funds or ETFs? |
| 4 | CCT | Common Collective Trusts? |
| 5 | MasterTrust | Master Trusts? |
| 6 | GIC | Contracts with insurance companies (deposit admin / participation / pooled separate)? |
| 7 | GICINV | GICs / deposit admin / immediate participation guarantees? |
| 8 | PooledAccounts | Pooled separate accounts? |
| 9 | JntVentr | Closely held corps/partnerships/joint ventures? |
| 10 | Omnibus | Investments held in omnibus account? |
| 11 | InvLifeIns | Trust-owned life insurance (TOLI)? |
| 12 | DerHedge | Derivatives or hedging activities? |
| 13 | SecLendingAct | Securities lending activities? |
| 14 | AssetBacked | Asset-backed securities? |
| 15 | FairValueRules | Securities/derivatives valued under FV rules? |
| 16 | Analytical | Use analytical procedures? |

### EBP Step Library (42 steps)

All 42 default to `IsApplicable: True` (much less aggressive TQ-gating than NFP's variant). Steps are ERISA-flavored throughout.

| Idx | Step Name | Assertions |
|---|---|---|
| 0 | Investment Policies | EO;CO;AV;UC |
| 1 | Detailed Analysis | EO;RO;CO;AV;CU;UC |
| 2 | Securities On Hand | EO;RO |
| 3 | Investments Held by Third Parties | EO;RO;CO;AV;CU;UC |
| 4 | Analytical Procedures – Schedule of Investments | EO;RO;CO;AV;CU;UC |
| 5 | Reasonableness of Investment Income | EO;RO;CO;AV;CU;UC |
| 6 | Disclosure of Unrealized Gains or Losses | UC |
| 7 | Investments Held by Third Parties – Alternative Procedures | EO;RO;CO;AV;CU;UC |
| 8 | Service Organization | — |
| 9 | Liens, Pledges, or Other Security Interest | EO;RO;AV;UC |
| 10 | Investment Transactions | EO;RO;AV;CU |
| 11 | Manager's Compensation | EO;AV |
| 12 | Securities in Transit | EO;RO;CO;AV |
| 13 | Transfers between Categories | UC |
| 14 | Investments in Mutual Funds and ETFs | EO;RO;CO;AV;UC |
| 15 | Investments in Common or Collective Trusts (CCTs/CCTs) | EO;RO;CO;AV;UC |
| 16 | Investments in Master Trusts | — |
| 17 | Contracts with Insurance Companies | EO;RO;CO;AV;UC |
| 18 | Traditional GICs, Deposit Administration | EO;RO;CO;AV;UC |
| 19 | Benefit Responsive Synthetic GICs | EO;RO;AV |
| 20 | Pooled Separate Accounts | EO;RO;CO;AV;UC |
| 21 | Real Estate, Closely Held Corps, Partnerships | EO;RO;CO;AV;CU;UC |
| 22 | Investments Held Within an Omnibus Account | EO;RO;CO;AV;CU;UC |
| 23 | Trust Owned Life Insurance Policies (TOLI) | EO;RO;CO;AV;UC |
| 24 | Derivatives and Hedging - Understanding | EO;RO;CO;AV |
| 25 | Derivatives and Hedging - Management's Calculation | AV |
| 26 | Derivatives and Hedging - Reconciliations or Data Feeds | EO;CO;AV |
| 27 | Derivatives and Hedging - Master Netting Arrangements | EO;RO;CO;AV |
| 28 | Derivatives and Hedging - Procedures | EO;RO;CO;AV;CU;UC |
| 29 | Securities Lending Activities | — |
| 30 | Asset-Backed Securities | EO;RO;CO;AV |
| 31 | Fair Value Valuations and Accounting Estimates | — |
| 32 | CCTs, Pooled Separate Accounts, Master LPs | AV |
| 33 | Adequacy of Disclosure | UC |
| 34 | Significant Accounting Estimates | AV |
| 35 | Fraud Awareness | AV |
| 36 | **Compliance with ERISA and Plan Documents** | RO |
| 37 | Additional Procedures | EO;CO;AV |
| 38 | Agree to Support | AV |
| 39 | Disclosures Testing | EO;CO;AV;UC |
| 40 | Information To Be Used As Audit Evidence | — |
| 41 | Analytical Procedures | — |

**Key EBP-only step**: Idx 36 "Compliance with ERISA and Plan Documents" — RO assertion. Required for any non-limited-scope EBP audit; tests prohibited-transaction rules, party-in-interest, plan-document compliance, etc.

### EBP firm-default step selection — TBD

> **Not yet captured.** Suggested starting baseline for a typical mid-size 401k DC plan, non-certified investments: Idx 0, 1, 3, 4, 5, 6, 10, 14 (if mutual funds), 24–28 (if derivatives — usually No for plain-vanilla 401k), 35, 36, 37, 38, 39, 40, 41. Adjust per actual portfolio's TQ answers.

### EBP — relationship to AUD-802B (Limited Scope / Certified)

When the plan is audited under ERISA 103(a)(3)(C) (the former "limited scope" exemption — qualified institutions certify investments), use AUD-802B Audit Program Investments (Certified), dbk `LIMITED`. The limited-scope audit substantially trims investment procedures since the certified trustee assumes responsibility for FV. Capture this form separately; it lives in its own collection space (`.LIMITED.*`) and is not a variant of `.INVEST.*`.

## TODO (deferred capture)

- [ ] **NFP**: Apply firm-default step set against APNM, confirm which steps are universally needed for NPO investments, lock the table above.
- [ ] **NFP**: Per-step typical workpaper references (analog of Cash 1000-series → Investments are in 1100-series workpaper section).
- [ ] **EBP**: Capture AUD-802B (LIMITED — Certified) on a real limited-scope engagement.
- [ ] **EBP**: Lock firm-default step set after tailoring against Kymera or another active 401k engagement.
- [ ] **ASB**: Capture commercial-title variant of AUD-802 (separate session).
- [ ] **ALG**: Capture governmental-title variant of AUD-802 (separate session).
- [ ] Test sub-step inclusion edge cases (parent without children, child without parent).
- [ ] Document `.INVEST.FlowTailoringQuestions` (purpose unclear from GET alone).
