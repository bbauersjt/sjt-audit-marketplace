# Section library — procedures, wave-offs, and distilled answers

For each section, four elements produce the distilled answer:
- **Presumed-performed (mandatory)** — procedures always performed to cover the RMM.
- **Materiality wave-offs (stated)** — procedures dropped because the residual is immaterial; stated via materiality.
- **Presumed-NOT-performed (silent)** — conventionally not performed; not explained.
- **Distilled answer** — the line entered in the box (coverage plus any wave-off; never the silent omissions).

See `approach-decision.md` for the reasoning model.

## Universal procedures (every area)
- **Lead-out / agree to support (always step 1, EVERY balance-sheet account):** tie the client's supporting schedule/records to the TB to the FS, and the TB to underlying support (bank/custodian statements, agreements, amortization schedules, etc.). Everything else builds on this.
- **Agree the activity through to records (every rollforward section):** where an account has activity (investments, PP&E, debt, grants/deferred), agree the full activity through to the records — beginning plus activity equals ending, and it should all match.
- **Test from a list that ties to the TB (ALWAYS — every entity, every sample):** every selection — distributions, expenses, single-audit, participant data, etc. — must be pulled from a population list that agrees to the TB / the number being opined on. Agree the list to the TB first, then select from it; otherwise the data being opined on has not been tested.
- **Mandatory-but-corroborative analytics:** where a program requires an analytic but substantive testing is the real evidence, the analytic is performed but corroborative — the answer references the substantive coverage, which overrides it.
- **Defer-to-user areas (assist, don't auto-fill):** some areas have a simple default path AND a complex variant that cannot be shortcut from defaults. The simple path is filled normally; the complex variant is deferred to the user — do not default-fill or guess. The user must understand it well enough to instruct; assist under direction but never fill autonomously. Current defer-to-user areas: **complex commercial capital structures** (issuances, conversions, leveraged ESOPs, M&A, S-corp distribution traps) and **govt OPEB / pensions plus deferred outflows/inflows** (actuarial accounting spanning many areas).

---

## Cash & Equivalents (1000) — all types ✓
**What could go wrong (all that is relevant):** recorded cash balance correct (existence/accuracy); reconciling items valid and complete; **classification** (cash equivalents vs. investments — e.g., money markets); **restrictions** (contractual/legal minimums recorded and disclosed as restricted cash); **disclosure** of FDIC / custodial-credit-risk / uncollateralized deposits. No estimates, no valuation. Low-risk area.

> **Rule: not a fraud account.** Test theft of cash under disbursements, not cash — the recorded cash balance is still stated correctly; the error is in how the reduction was recorded.

- **Mandatory:**
  - Obtain all bank reconciliations plus statements (every account).
  - Agree reconciled balances to GL; agree bank balances in the recons to statements (ending and beginning-of-next-month).
  - Test **recorded** reconciling items — scope a selection, trace to subsequent clearance (validate it was a real outstanding check / deposit in transit at year-end).
  - Test for **unrecorded** reconciling items — scope items clearing the subsequent month; inspect check images / deposit marks / evidence of when cut or deposited.
  - Disclosure: FDIC / custodial credit risk / uncollateralized deposits (govt: collateralization / GASB deposit-risk emphasis).
  - **Restrictions and classification** are *corroborated* in cash but **sourced from other areas** — grants/deferred revenue, permanent file, debt, NPO endowments (usually planning/PF). Default: **"no restricted balances noted per testing in other areas and inquiry of management"** unless the financials/TB indicate otherwise.
- **Materiality wave-offs (stated):**
  - Stale-dated checks — N/A unless material; if materially old, investigate reappropriation (unclaimed property). Generally immaterial.
  - Stale-dated deposits in transit — should not exist; rarely relevant, so N/A.
- **Presumed-NOT-performed (silent):**
  - Fraud/theft procedures over cash — addressed in disbursements, not a cash procedure.
  - **Bank confirmations — not sent currently; rely on statements.** ⚠ Becoming required soon; moves to mandatory when firm policy changes.
- **Distilled answer (draft):** "Obtained all bank statements and reconciliations; agreed reconciled balances to the general ledger and bank balances to the statements for all accounts. Tested recorded reconciling items by tracing to subsequent clearance and tested for unrecorded items in the subsequent-period clearings. Per testing in other areas and inquiry of management, no restricted balances were noted. No estimates or valuation; residual misstatement risk is immaterial." (WP ref: inferred from where cash testwork actually lives — typically 1000)
- **Approach-question line** (will substantive suffice?) — see `approach-decision.md`.
- **Type notes:** approximately the same all four types. Govt: deposit/collateralization disclosures more prominent. EBP cash minimal.

## AR / Receivables ✓
- **Mandatory:** confirm; trace to subsequent collections; cutoff.
- **NPO completeness — CRITICAL:** multi-year **unconditional promises to give (pledges)** must be recorded in full when made. NPOs frequently record only the current-year cash and omit future unconditional payments, producing **unrecorded revenue/receivable.** Examine grant/pledge agreements, cash flows, and **subsequent receipts for unrecorded pledges.** Recurring material issue. (Mirror risk in Revenue.)
- **Materiality wave-off:** allowance not separately tested — untraced AR is immaterial and subsequent collections substantiate net realizable value, so testing the allowance cannot detect a material collectibility misstatement.
- **Answer:** "AR confirmed and traced to subsequent collections; untraced balances immaterial. NCN to separately test the allowance — subsequent collections substantiate net realizable value. [NPO: unconditional pledges examined for completeness via agreements and subsequent receipts.]"

*(AP and all liabilities — see "Liabilities" block below, after the asset sections.)*

## Investments (1100) — STANDARD (commercial / nonprofit / government) ✓
**What could go wrong:** existence/ownership; **valuation (fair value)**; completeness of activity and income (gains/losses, dividends/interest); classification (current vs. LT); restrictions; disclosure. Primarily substantive.

- **Mandatory:**
  - Lead-out: agree investment balances (TB/FS) to **custodian/broker statements**.
  - **Rollforward — the crux:** opening plus activity equals ending. Agree opening and ending balances to balance sheet; agree activity (realized/unrealized gains and losses, dividend/interest income) to income statement. This tie-out to the statements is the real evidence.
  - **Verify valuations to independent third-party sources** (required on every audit except limited-scope EBP): Level 1 and 2 tie to third-party pricing sources; Level 3 evaluate the inputs (broad, rare). Carried at FV.
  - Analytics — performed (program-required) but **corroborative only**; overridden by the substantive tie-out.
  - Disclosures — we draft them (future maturities, current vs. LT [usually current, not HTM], FV); low risk because we prepare them; agreed to support.
  - Restrictions/endowments — corroborated here, **sourced from other areas** (PF, agreements, prior FS, planning); mainly NPO. Default none noted unless TB/FS/agreements indicate.
- **Materiality wave-offs / exceptions:**
  - Level 3 / derivatives / alternative investments — N/A unless present (then FV/valuation or specialist work).
- **Presumed-NOT-performed (silent):**
  - Investment confirmations — not sent; rely on statements. ⚠ Becoming required soon (like cash).
- **Distilled answer:** "Agreed investment balances to custodian/broker statements and performed a rollforward — opening and ending balances agreed to the balance sheet, and activity (realized/unrealized gains and losses and investment income) agreed to the income statement. Valuations verified to independent third-party pricing sources (Level 3 inputs evaluated where applicable). Disclosures prepared and agreed to support; no restricted balances noted per other-area testing and inquiry. Analytics performed and corroborative; substantive agreement is the primary evidence." (WP ref inferred)
- **Type notes:** NPO — donor-restricted / endowment investments (restrictions from PF/agreements/planning). Govt — GASB fair-value-hierarchy and investment-risk disclosures; if grant-funded, cash-management compliance (SA).

## Investments (1100) — EBP ✓
**Fork = ERISA §103(a)(3)(C) certification.**
- **Limited scope (common):** tie investments **and** investment income to the **certification** from the qualified institution; trust the cert — no valuation verification, no third-party-source testing. Drives the limited-scope opinion. Minimal testwork.
- **Full scope (rare):** treated as a normal investment audit, equal to the standard entry above (rollforward, **verify valuations to third-party sources**, tie income to statements).
- **Presumed-NOT-performed (limited scope):** valuation testing, third-party verification — N/A, covered by the certification.
- **Distilled answer (limited scope):** "Investments and investment income agreed to the certification provided by the qualified institution under ERISA §103(a)(3)(C); certified information not audited."
- **Distilled answer (full scope):** equals standard investments line above.

## Inventory (1300) — STANDARD (commercial-main; rare govt/npo) ✓
**What could go wrong:** existence (do they have it); cost/accuracy (does it cost what they say); **valuation / recoverability — NRV** (can they recover the cost — slow-moving / obsolete / stale-dated).
- **Mandatory:**
  - **Observe material inventories** — the main thing (existence).
  - Agree costs to records (substantive).
  - Evaluate **valuation and recoverability (lower of cost or NRV)** — check slow-moving / obsolete / stale-dated; analytics plus inquiry to support that the inventory can be sold and cost recovered (obsolete items carried at unrecoverable cost).
- **Situational:** the NRV/recoverability analytic is light when there is no obsolescence risk; it matters when there is (slow-moving, declining markets) — substantive when the risk is real.
- **Distilled answer:** "Observed material inventories; agreed costs to records. Evaluated valuation and net realizable value, including slow-moving, obsolete, and stale-dated inventory, via analytics and inquiry — no material recoverability concerns noted." (WP ref inferred)
- **Type notes:** commercial-main; rare/immaterial in govt/npo (area often N/A).

## Property, Plant & Equipment / Capital Assets (1500) — all types ✓
**What could go wrong:** additions valid (occurrence/accuracy); depreciation correct plus **estimate reasonableness** (useful life, method); **unrecorded disposals** (net-basis risk); impairment (usually N/A); capitalization vs. expense. Material but low-risk, easy to test.
- **Mandatory:**
  - **Rollforward:** agree beginning balances; **substantively test additions** (always); recalculate depreciation; evaluate reasonableness of useful lives and depreciation method (estimates).
  - Consider unrecorded disposals (net basis).
  - Consider / sometimes test **expensed fixed-asset additions** (capitalization policy).
- **Presumed-NOT-performed (silent):**
  - Impairment testing — usually N/A; assets out-depreciate impairment risk.
  - Security / collateralization — a **debt** matter, not PP&E.
- **Materiality wave-offs:** expensed additions — rarely material, so light/N/A.
- **Distilled answer:** "Performed a rollforward — agreed beginning balances, substantively tested additions, recalculated depreciation, and evaluated the reasonableness of useful lives and methods. Considered unrecorded disposals and capitalization of additions; no impairment indicators noted (assets out-depreciate impairment risk)." (WP ref inferred)
- **Type notes:** govt — capital assets plus depreciation (same); infrastructure/modified approach rare. Ties to **debt** (collateral) where applicable.

## Prepaids & Other Assets (1400 / 1600) — STANDARD ✓
**What could go wrong:** existence/accuracy; recoverability — depends entirely on what they are. Usually simple, low-risk.
- **Mandatory:** substantive testing of prepaids (agree to support; recompute amortization/expense) and other assets per their nature.
- **Cross-area:** **ROU (right-of-use) assets — handled with lease liabilities** (debt/lease section), not here. **Goodwill** (rare, complicated) — test recorded value plus impairment; uncommon.
- **Distilled answer:** "Prepaids and other assets tested substantively and agreed to support; amounts recomputed/amortized as applicable. No complex valuation noted." (WP ref inferred)
- **Type notes:** light across all types; contents-dependent.

---

# LIABILITIES

## AP / Purchases (2000) — all types ✓
**What could go wrong:** **completeness** (unrecorded liabilities) — the crux. Recorded AP overstatement is not a real risk. Related-party vendors.
- **Mandatory:** **search for unrecorded liabilities** (the crux); recorded AP **reviewed analytically** — not substantively tested, so analytics cover reasonableness (big swings explained; recorded balance reasonable, no unusual items); **RPT search** via vendor-type testing; cutoff.
- **Presumed-NOT-performed (silent):** AP confirmation — AP is not confirmed.
- **Distilled answer:** "AP risk is completeness — addressed via the search for unrecorded liabilities and cutoff. Recorded payables reviewed analytically and found reasonable with no unusual items; related-party vendors considered in vendor testing." (WP ref inferred)

## Accrued Expenses (2100) + Payroll ✓
**What could go wrong:** **completeness** — an expected accrual that should exist but is not recorded (recognized from other areas). Testing recorded accruals is simple; the work is what is *missing*. Estimates (accrued payroll, PTO).
- **Mandatory (general accruals):** test recorded accruals (agree to support — simple); **consider expected accruals from other areas** for completeness (debt to accrued interest; etc.); estimable accruals in a tight window — analytics/recalc acceptable.
- **Payroll (accrued plus base expense):**
  - Analytics on base payroll expense; **tie base expense to the 941s / year-end payroll reports** and reconcile.
  - **Estimate accrued payroll** from period-end paydays times total payroll, **including payroll taxes** (e.g., a Jan-7 check on a 12/31 YE — accrue the earned portion).
  - **Accrued PTO:** obtain schedule; analytic for anything unusual; compare to policy (max hours, payout terms); recalc liability from payroll reports.
  - Tie into payroll walkthroughs; test payrates to walkthroughs; agree payrates to the payroll register used for the accrual.
- **Distilled (accruals):** "Recorded accruals agreed to support; expected accruals considered for completeness based on activity in other areas (e.g., accrued interest from debt). Estimable accruals recalculated within a supportable range."
- **Distilled (payroll):** "Base payroll expense reviewed analytically and reconciled to the 941s/year-end payroll reports. Accrued payroll estimated from period-end paydays including payroll taxes; accrued PTO recalculated from payroll reports and compared to policy. Payrates agreed to the payroll register and tested to walkthroughs." *(payroll = the anchored-analytic case in approach-decision)*

## Deferred Revenue (2200) + Grant / SEFA testing ✓
**What could go wrong:** deferred revenue accuracy/completeness (usually small, easy); the big piece is **revenue testing**. For **govt/NPO with grants this is where grant accounting plus the SEFA numbers are tested** (grants receivable, deferred revenue — the actual amounts, not the single-audit compliance).
- **Mandatory:**
  - Deferred revenue — substantive test of what is there (usually small) plus analytics.
  - **Grant/SEFA rollforward (govt/NPO):** agree beginning grants receivable/deferred; test rollforward activity (**beg + expenditures − receipts = ending receivable/(deferred)**); tie all activity through to records; standard AR collection test where receivable; **agree revenue to qualifying expenditures** (reimbursement-grant accounting); verify grant accounting and tie to substantive work elsewhere.
- **Distilled:** "Deferred revenue tested substantively and analytically. Grant activity rolled forward — beginning receivable/deferred agreed, expenditures and receipts tied through to records, ending balances recomputed (beg + expenditures − receipts), and revenue agreed to qualifying expenditures. Grant accounting verified and tied to related substantive testing." (WP ref inferred)
- **Type notes:** key area for govt/NPO with grant revenue; minimal commercial/EBP.

## Long-Term Debt (2400) + Leases ✓
**What could go wrong:** the **terms — the words in the loan doc** (the hard part): covenant compliance, RPT / off-balance-sheet guarantees, current vs. LT classification, convertible debt (debt vs. equity — commercial). The accounting is simple. Completeness of unrecorded debt/leases (large payments hard to miss).
- **Mandatory:**
  - **Rollforward** balances; agree to lender statements and **agree to the terms (loan docs)**.
  - Tie interest expense to statements; tie balances and interest to **amortization schedules**; recalc; recompute **accrued interest**.
  - **Covenant compliance** — in compliance, or **waiver** obtained; otherwise default to consider **reclassification to current**.
  - Disclosures: **future maturities**, current vs. LT, guarantees, collateral.
  - Completeness: expense analytic for indicators of an **unrecorded lease/debt**.
  - **Leases / ROU** handled here.
- **Presumed-NOT-performed (silent):** debt confirmation — not usually confirmed.
- **Distilled:** "Debt rolled forward and agreed to lender statements and loan agreements; interest expense and accrued interest recomputed and tied to amortization schedules. Covenant compliance confirmed [or waiver obtained]; balances classified current/long-term accordingly. Future maturities and disclosures prepared. No indicators of unrecorded debt or leases noted." (WP ref inferred)
- **Type notes:** commercial — convertible/complex instruments (debt-vs-equity classification) the trickier disclosure. Ties to PP&E (collateral).

## Other Liabilities (2500) ✓
Catch-all — no dedicated program; picked up in other areas (accruals, contingencies), occasional fiduciary. Low risk.
- **Distilled:** "Other liabilities addressed through the related programs (accruals, contingencies); nothing material or unusual noted." (WP ref inferred)

## Interfund / Intercompany (1900 / 2900) ✓
Simple, no program. **Agree to the other side of the accounting records** (offsetting fund/entity); in consolidation they agree and eliminate. Essentially a confirmation — but the same people keep both sets of books, so verify it balances.
- **Distilled:** "Interfund/intercompany balances agreed to the offsetting side of the accounting records and eliminate/agree; no exceptions." (WP ref inferred)
- **Type notes:** govt interfund (1900/2900); commercial intercompany in consolidation.

## Transfers (7000) — govt ✓
Simple — tie them out. From another government/department — if they balance, confirm the other side; internal — even less concern (they balance). Any real issue in a transfer lives in another area.
- **Distilled:** "Transfers agreed and tied to the offsetting side; balances eliminate/agree. No exceptions." (WP ref inferred)

## Govt OPEB / Pensions & Deferred Outflows/Inflows — DEFER-TO-USER (govt)
Spans accruals plus **deferred outflows/inflows of resources** plus many areas (net pension/OPEB liability, GASB 68/75 actuarial reports). Actuarial accounting. Do **not** default-fill — **prompt the user** for how to complete it (the user can supply responses; assist under direction).

---

# EQUITY & INCOME STATEMENT

## Equity / Net Assets / Fund Balance (3000) ✓
**Universal:** tie **opening equity to prior-year audited FS closing equity** (equity must reconcile). Beyond that it ranges from trivial to one of the hardest areas.
- **Govt / NPO:** roll forward **by class/fund**; restrictions (restricted contributions, releases) tested in the **income statement**, agreed to **laws** (govt) and **endowment balances** (NPO); reconcile to other substantively-tested areas; heavy **permanent-file** work. The difficulty is **identifying restrictions** (in laws, grant/donor agreements, how the client tracks them), not the arithmetic.
- **EBP:** trivial — no equity transactions; it is just **Net Assets Available for Benefits**.
- **Commercial — FORK:**
  - **Simple** (opening plus net income minus distributions): test distributions, reconcile, done. This is the common case — fill it normally.
  - **Complex — defer-to-user (assist, don't auto-fill).** Capital issuances, debt conversions, **ESOPs (esp. leveraged ESOPs)**, buybacks, preferred vs. common, M&A, pro-rata distribution requirements and their FS impact, **S-corp distribution/status traps** (personal expense on the company card booked as a distribution, jeopardizing S-corp status), "IOU" contributions. Here the boxes become real nuanced understanding — highest-risk-transaction territory. Do **not** default-fill; the user must understand it well enough to instruct, and assist under direction only.
- **Distilled (simple):** "Opening equity agreed to the prior-year audited financial statements. [Govt/NPO: rolled forward by class; restrictions agreed to laws/agreements and tied to income-statement testing.] Distributions tested and equity reconciled." (WP ref inferred)
- **Distilled (complex commercial):** defer-to-user — assist when directed; not a default-fill.

## Revenue (4000) ✓
**Ideal = substantive.** Revenue is diverse — much ties to balance-sheet area testing; the rest is substantive or controls-fallback, **always with analytics** (income/expense analytics matter most here).
- **What could go wrong:** **completeness** (the big one — unrecorded revenue), occurrence, cutoff, the mandatory improper-revenue-recognition fraud presumption.
- **Always:** analytics on revenue and expense plus balance-sheet ratios (days-in-AR, AR turnover, GP margin).
- **Tie to other areas:** federal grants to SEFA/grant testing (plus SA); investment income to investments; **occupancy to leases** (agree to leases plus lease rollforward).
- **By type:**
  - **Federal grants** — substantive; tie into SA/SEFA if applicable.
  - **Private grants** — substantive, always (even if controls tested). *(Exception only if a large number of individually-immaterial grants with no material total.)*
  - **Govt taxes / appropriations** — substantive.
  - **Commercial trade revenue / NPO genuine retail sales** — **controls-fallback plus heavy analytics** (population too fragmented for a clean substantive sample).
  - **Everything else** — substantive or controls-fallback, with analytics.
- **NPO completeness — CRITICAL:** multi-year **unconditional pledges** recorded in full when made; examine grants, cash flows, and **subsequent receipts for unrecorded pledges** (recurring NPO issue — mirror of the AR risk).
- **Improper-revenue-recognition fraud presumption:** mandatory but **low real risk** for NPO/govt/EBP (no incentive; EBP custodians do not fabricate returns) — **default addressed/rebutted via substantive plus analytics.** **Commercial exception:** real where the client needs to show income (covenant pressure, loan, going-concern pressure) — elevate there.
- **Distilled:** "Revenue tested substantively where feasible (grants, taxes, appropriations) and via controls-reliance plus analytics for high-volume trade/retail revenue; revenue and expense reviewed analytically (incl. AR turnover, days-in-AR, margins). Grant/SEFA, investment income, and occupancy revenue tied to their related-area testing. Completeness addressed — pledge/grant agreements and subsequent receipts examined for unrecorded revenue. Improper-revenue-recognition fraud risk addressed via substantive testing and analytics [commercial: elevated where income incentives exist]." (WP ref inferred)
- **Type notes:** govt — nonexchange (taxes, appropriations, grants) substantive. NPO — **pledge/contribution completeness is the headline risk** plus program revenue. Commercial — ASC 606. EBP — n/a here (contributions / investment income covered in the EBP areas).

## Expense (5000) ✓
**Key:** most significant expense is already **substantively tested in its balance-sheet area** — payroll (accrued/payroll), interest (debt), depreciation (PP&E), investment income/expense (investments). What is left is small.
- **Mandatory:**
  - **Payroll base:** substantive — reconcile to **941s / YTD payroll records**; plus analytics (avg salary per employee; payroll and benefits tied to substantive payroll).
  - **Remaining expense:** heavy **analytics with targeted corroboration** — **major-vendor / professional-fee** testing semi-substantively; **identify legal expenses**; review classifications for **capitalizable items expensed** (R&M to fixed assets).
  - **SA / Yellow Book:** supported by **controls testing plus analytics plus expanded walkthroughs** (incl. major-vendor testing); SA controls create a convenient lower risk for payroll/disbursements.
- **Distilled:** "Significant expenses are substantively tested in their related balance-sheet areas (payroll, interest, depreciation, investment expense). Payroll reconciled to 941s and YTD payroll records and reviewed analytically. Remaining expenses reviewed analytically with targeted corroboration — major vendors and professional/legal fees tested semi-substantively, and classifications reviewed for capitalizable items. [SA/YB: supported by controls testing and expanded walkthroughs.]" (WP ref inferred)

## Other Income & Expense (6000) ✓
Catch-all, not a programmed area — **house rules / partner judgment**. Substantively tested per its nature; usually immaterial. Investment income — tied to investment testing; obscure items (e.g., **cash surrender value of life insurance** — tied to statements) agreed to support.
- **Distilled:** "Other income/expense tested substantively per its nature and agreed to support (investment income tied to investments; other items, e.g., cash surrender value, agreed to statements). Immaterial; extent per partner judgment." (WP ref inferred)

---

# EBP-SPECIFIC AREAS
(Cash, Other Assets, Accrued/Payable mirror standard. Investments = the certified/non-certified fork in the Investments section. Net Assets Available for Benefits = trivial, no equity transactions.)

## EBP central concept — it is a COMPLIANCE audit (drives everything)
An EBP "audit" is really a **compliance audit against the IRS-approved plan document** (like a program-specific / single audit, but for the benefit plan). The plan document is IRS-approved, so non-compliance arises from **execution errors**: wrong dates/demo data, the system stops matching, a payroll's contribution file never gets uploaded. The custodian (with a clean SOC-1) produces materially-correct financials — that is not where the risk is. The risk, and the real point, is **compliance with the plan document**, and **all testing runs against that document** (vesting, eligibility, deferrals, match, distributions, loans). The AICPA "CPA opinion" framing is real but secondary; the substance is compliance.

## Participant Data (6000) — EBP — THE CRUX ✓
**The controls test that touches everything.** Census-data accuracy (birthdate, hire/term dates, hours, payrate, deferral % from the election form, match) drives eligibility, vesting, deferrals, match, distributions, loans, and contribution remittance. **This is the failure point** — the custodian/certifier (clean SOC-1) is not the risk; the risk is whether the data the client feeds them is accurate. **Every other EBP test relies on this baseline.**
- **What could go wrong (systematic/processing errors):** wrong birthdate — late/early enrollment, wrong catch-up eligibility, wrong distribution penalties; wrong payrate — wrong deferral/match; system miscalculated deferral or match; missed/late remittance; wrong eligibility/vesting.
- **Mandatory (controls compliance test):**
  - Sample **≥ 25** (baseline control sample), **40 if high risk** (any plan large enough to need an audit needs the 25).
  - For **each** participant, test **every data element** for a payroll period:
    - Hire and term dates to hard docs.
    - Payrate to authorizations.
    - Deferral % to the **election form** (and confirm a form exists).
    - Trace the contribution **into the plan, into their account, into their elected investments**.
    - Birthdate to I-9 / driver's license / birth certificate.
    - Test the payroll period; recompute deferral and match.
  - Goal: **no errors** — data right, system processed right (deferral, match, eligibility, vesting).
- **Result:** sets the **baseline reliability of the census data**, which every other EBP test relies on.
- **Type note:** EBP-unique anchor; limited vs. full scope does not change it (plan-side data, not custodian investments).

## Contributions (4000) + Contributions Receivable (1300) — EBP ✓
- **Controls test:** all 25 demo-selected participants' contributions tested for the period.
- **Timeliness (the major test):** get every payroll; total deferrals, contributions, loan and interest payments; identify the payday; **trace each remittance into the plan timely** (auditor login or cert — test every payday). Late remittance — **prohibited transaction / delinquent contribution.**
- **TB ties:** total contributions traced per period to deferral and match revenue; loan repayments to loan rollforward; **participant loan interest to interest income** (quirk: participant interest is income to the plan, credited back to their account).
- **Demo support:** the demo participants' contributions being in and traced supports that everyone else's is materially right.
- **Contributions receivable:** cert statements are **cash basis — there is ALWAYS an unrecorded receivable to document and conclude on.** Usually **immaterial by math** (one payroll of 24–26 is below materiality). **Exception:** large bonus / profit-sharing contribution (e.g., year-end 10%-of-salary profit share) — likely material, so record.
- **Delinquencies:** if genuine — **report in the FS** (per IRS regs); document where, plus lost-earnings impact, unrecorded receivables, fines/contingencies; possibly accrue. Not common.
- **Distilled:** "Contributions tested for the demo sample; all payrolls' remittances traced into the plan and tested for timeliness — none late [or: late noted at X, reported delinquent]. Totals tied to deferral/match revenue; loan repayments and interest tied to the loan rollforward and interest income. Unrecorded year-end receivable concluded immaterial [or recorded]." (WP ref inferred)

## Benefit Payments / Distributions (5000) — EBP ✓
- **Relies on demo** (birthdate, vesting); if demo not reliable, substantively test those.
- Controls/compliance **plus substantive** — one sample meeting all: **10% of total transactions or 25**, pulled from a **list agreed to total distributions**.
- **Per selection:** distribution form completed/signed/**authorized**; **spousal consent** if required; amounts and taxes calced right; correct withholding; right amount distributed; **see the check/EFT per instructions**; hardships backed by hardship documentation.
- **Forfeitures:** the distributions list includes forfeitures (tied to TB — sometimes shown as a pseudo-participant "Forfeitures" with an investment balance in assets). **Target some if material** (good coverage, not all — a material forfeiture means a material distribution already picked up); test the forfeiture was **applied per the plan document**. Relies on census reliability.
- **Distilled:** "Distributions sampled (≥25 / 10% of transactions) from a list agreed to total distributions; each tested for authorized/signed forms, spousal consent where required, correct calculation and withholding, and payment per instructions (hardships supported); eligibility/vesting per the tested census. Forfeitures included and tested for application per the plan document. No exceptions." (WP ref inferred)

## Notes Receivable from Participants (1200) — EBP ✓
- **Rollforward** (like debt): tie beginning and ending to TB; tie **interest income.**
- **New loans** = distributions-style sample (controls/compliance/substantive) plus the rollforward layer.
- **IRS nuance:** defaults **deemed timely** (within the statutory period if unpaid); loan agreements **signed per the plan document**; **reasonable interest rate** — must act like a real loan (repaid on schedule) or the IRS recharacterizes it as a taxable distribution (same logic as commercial owner "loans").
- **Distilled:** "Participant loans rolled forward (beginning/ending tied to TB; interest tied to interest income); new loans tested like distributions for eligibility, signed agreements per the plan doc, reasonable rate, and amortization; defaults deemed timely. No exceptions." (WP ref inferred)

## Participant Accounts (2100) — EBP ✓
- A list of every participant's accounts and investments from the **cert**, **tying in total to cert totals** — it is a TB made of individual accounts. Everything tested (loans, contributions, distributions, demo) ties into the individual accounts.
- **Allocation testing** (low risk): recompute a sample's **earnings vs. overall plan earnings** across their funds; confirm each got a **proportionate share** (the $1,200/$1,200 proportionate test, not $1,400/$1,000).
- **Distilled:** "Participant account listing agreed in total to the certification; a sample's earnings allocations recomputed against overall plan earnings by fund and found proportionate. No exceptions." (WP ref inferred)

## Investment Income (4100) — EBP ✓
- **Limited scope (§103(a)(3)(C)):** tie to the cert — done.
- **Full scope:** equals standard investments — rollforward, **verify valuations to third-party sources**, income analytics vs. indexes.

## Administrative Expenses (5100) — EBP ✓
Usually immaterial — analytics fine; in the cert. If material — relate to obtained agreements.
- **Distilled:** "Administrative expenses reviewed analytically and per the certification; immaterial [or, if material: agreed to plan agreements]."

## EBP quirks (always)
- **By-participant analytics:** required but low-value — distributions swing widely (a high-balance participant leaves). Tested substantively regardless; the analytic comes out far off, explained by the substantive testing plus the specific cause. Adequately tested substantively.
- **SOC-1 analysis:** required by AICPA — obtain the **cert letter in the required format**, cite in the FS (not for full scope). Pro-forma but mandatory.
- **Required supplemental schedules:** **Schedule H schedule of investments — always.** Others when applicable: schedule of **delinquent contributions** (sometimes), 5%-transactions for non-participant-directed investments (rare), others rare.
- **Agree the Form 5500 to the financials pre-issuance.**
- **Rollovers in:** trace in, agree the docs — simple, usually few.
- **Party-in-interest / prohibited transactions:** sponsor and custodian disclosed as parties in interest (generic). Prohibited-transaction questions mirror RPT — **generic / none** (if one existed it would be evident). No real program step; default response.

---

# PLANNING & CONCLUDING (narratives & pseudo-programs)

## Related Party Transactions (AUD-814 Govt · AUD-817 NPO · AUD-815 Commercial · AUD-813 EBP) ✓
_Form ID is per entity title — confirm against `form-content-reference.md` §2b before cross-referencing._
**Reality:** RPTs almost always exist. The form is mostly generic — it indicates RPT was *considered*; the real point is **they are disclosed in the FS.**
- **Who are they?** — identified per the **board / planning** documentation.
- **Previously undisclosed related parties identified? how responded?** — **generic: "We did not identify any previously undisclosed related parties."** (The question targets *deliberately concealed* RPs — genuinely rare.)
- **Arms-length assertion documented?** — **generic: "No such disclosure made"** (the notes do not claim arms-length, so there is nothing to substantiate). Only changes if the FS actually asserts arms-length.
- **Disclosure** — point at the **financials.** RPTs surface anywhere (transfers, AP/AR, debt); cross-referencing every lead is unnecessary — disclosure in the FS is sufficient. User can add a specific RPT workpaper if one exists.
- **Distilled:** "Related parties identified per the board and planning documentation; no previously undisclosed related parties identified. Related-party transactions disclosed in the financial statements (no arms-length assertion made)." (WP ref — FS)

## Controls / COSO (KBA-401 entity-level) ✓ — generic
**COSO entity-level form takes generic, per-management responses.** Each principle: "Per management, they demonstrate/maintain [the principle]" (e.g., commitment to communication of control objectives: "Per management, they display a commitment to communication of control objectives").
- **The substantive control documentation is separate** — the firm's actual **control narratives in the walkthrough / activity-level workpapers**: specific, testable segregation-of-duties / access / authorization documentation. *Example:* "[CFO] reviews all bank reconciliations monthly (initials noted on recons at [WP]); read-only bank access, no wire/signatory rights ([bank] permissions); password changed within 90 days; cannot post JEs in [system], only approve those made by [controller/clerk]. Designed effectively; if operating as designed would prevent or detect misappropriation absent significant collusion." This is a **workpapers-skill output**, not the COSO form.
- **Distilled (COSO principle):** "Per management, [the entity demonstrates/maintains the principle]." Generic across all principles.

## Understanding the Entity (KBA-302) ✓
Mostly **gathered from user questions plus permanent-file review** (carried forward and updated); memo format. **Not a default-fill area** — it is information gathering. Surface **ambiguous items** for the user and help draft, but the content comes from the user/PF.

## FS Review (AUD-909) ✓
Concluding analytical review plus presentation/fund mechanics.
- **Toggles:** consent request **No**; aware of info re prior FS **No**; ICFR report **No**; **change in accounting principle — ASK** (comes up sometimes; a genuine material change is disclosed prominently in the FS with a prior-period restatement, but may be assessed before the FS are final, so confirm); use analytics **Yes**; component units / fund types / SI / RSI — entity facts.
- **Procedures:** understanding the FS reporting process; presentation on the correct basis (govt-wide accrual / fund modified-accrual); major-fund determination; fund-to-government-wide reconciliation. Generic, signed off.
- **Distilled:** generic / inferred; final analytical review documented; disclosures and review evidence **reference the FS package (0700)**.

## SEFA Presentation Checklist (KBA-901S) ✓
- **Default all Yes; cross-reference the SEFA.** The SEFA and ALNs are reviewed thoroughly on review, so the checklist is pro-forma — a peer reviewer only cares if something is actually wrong. The one real input is the **10% de minimis election**.
- **Distilled:** "Yes — see SEFA at [ref]."

## Concluding / FS-review steps (generic → reference the FS package)
Concluding review steps (FS review, final analytical review, review/approval and documentation checklists) take a **generic response or a reference to the FS package at 0700**, which carries the disclosure checklists and the preparer / 1st- and 2nd-partner review sign-offs. A generic answer or an FS-package reference is sufficient on these steps; no need to separately re-document them.

---

## Back-of-file checklist — STANDARD (Commercial / Nonprofit / Government)
Cash is approximately the same across all four types; most areas are shared com/npo/govt with govt-specific items flagged. Work top to bottom.

| Sec | Area | Type notes |
|---|---|---|
| 1000 | Cash & Equivalents | same across all 4 types |
| 1100 | Investments | ~same com/npo/govt; **EBP separate** |
| 1200 | Receivables, net (AR) | govt: nonexchange / grants receivable nuance |
| 1300 | Inventory | commercial main; rare govt/npo |
| 1400 | Prepaid Expenses | w/ Other Assets; ROU→leases, goodwill rare |
| 1500 | Property, Plant & Equipment | govt: capital assets + depreciation |
| 1600 | Other Assets | with Prepaids |
| 1900 | Interfund — Asset | govt; agree to other side |
| 2000 | Payables | completeness; never confirm |
| 2100 | Accrued Expenses | incl. **payroll**; completeness from other areas |
| 2200 | Deferred Revenue | **grant/SEFA rollforward** (govt/npo) |
| 2300 | Other Current Liabilities | catch-all (w/ Other Liab) |
| 2400 | Long-Term Debt | + leases/ROU; covenants are the work |
| 2500 | Other Liabilities | catch-all |
| 2900 | Interfund — Liability | govt; agree to other side |
| 3000 | Equity / Net Assets / Fund Balance | EBP trivial; **commercial complex = defer-to-user** |
| 4000 | Revenue | NPO pledge completeness = headline; fraud-presumption rebutted exc. commercial pressure |
| 5000 | Expense | mostly tested in BS areas; payroll + analytics |
| 6000 | Other Income & Expense | catch-all / partner judgment |
| 7000 | Transfers | govt — tie out / confirm other side |
| — | Govt OPEB/Pensions + Deferred Outflows/Inflows | **⚠ defer-to-user** — actuarial; prompt user, do not auto-fill |

## Back-of-file checklist — EBP
| Sec | Area | Notes |
|---|---|---|
| 1000 | Cash | mirrors standard |
| 1100 | Investments | certified (103(a)(3)(C)) = trust cert; full-scope = standard |
| 1200 | Notes Receivable from Participants | rollforward + distributions-style; IRS loan rules |
| 1300 | Contributions Receivable | cash-basis cert → always an unrecorded receivable; usually immaterial |
| 1400 | Other Assets | mirrors standard |
| 2000 | Accrued Liabilities & Amounts Payable | mirrors standard |
| 2100 | Participant Accounts | "TB made of individual accounts"; allocation testing |
| 3000 | Net Assets Available for Benefits | trivial — no equity transactions |
| 4000 | Contributions | timeliness/late-remittance is the major test |
| 4100 | Investment Income | limited=tie to cert; full=standard |
| 5000 | Benefit Payments | controls+substantive sample (≥25/10%); off the census |
| 5100 | Administrative Expenses | usually immaterial; analytics/cert |
| 6000 | Participant Data | **THE CRUX** — controls test (≥25/40); baseline for all EBP tests |
