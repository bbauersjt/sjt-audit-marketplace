---
name: ebp-fs-review
description: Comprehensive technical proof and review of an employee benefit plan (EBP) financial statement package and audit report — defined contribution (401(k), 403(b), profit sharing, ESOP), defined benefit, health & welfare, and multiemployer plans, covering ERISA Section 103(a)(3)(C) ("limited scope") and full scope audits. Use this skill WHENEVER the user uploads or references an EBP financial statement, ERISA plan audit report, Form 5500, or supplemental schedules and asks for a review, proof, QC check, math check, cross-reference, or disclosure review. Trigger even without "skill" — an EBP financial statement plus any review-style ask ("check this", "proof this", "find issues") should activate it. Also trigger on SAS 136 / AU-C 703 review, ASC 962/960/965 disclosure review, Section 103(a)(3)(C) certification review, or Schedule of Assets / Reportable Transactions / Delinquent Contributions review. Do NOT use for governmental pension plans under GASB, non-EBP commercial financials, tax returns, or bookkeeping.
---

# Employee Benefit Plan Financial Statement Technical Review

Not a substitute for human QC — output assists a preparer locating issues before handoff to QC.

# AI BEHAVIOR AND OUTPUT FORMATTING

## Narration and Commentary

- Keep chat output minimal.
- Do not narrate each procedure as it is performed.
- Do not provide running commentary on findings or hypotheses.
- Do not summarize or editorialize on results at the end.
- While working through the review, announce only the step number and title (e.g., "Step 1 — Proof Review", "Step 3 — Math Check"). Do not announce sub-steps or internal procedures.
- All findings and conclusions belong in the Excel report, not in chat.
- Clarifying questions to the user are permitted only where Step 0 requires them.

## Excel Report Formatting — Strict Rules

The deliverable is a plain Excel REPORT, not a workpaper. Keep it clean and readable. A few requirements:

- Produce a valid .xlsx file that opens cleanly in Excel with no XML errors, no broken formulas, and no hidden corruption. Test by opening with openpyxl or similar after saving if uncertain.

- Header block on every tab: three plain cells stacked vertically in column A — (1) plan name, (2) report/tab name, (3) plan year-end date. No merging.

- Size column widths so content fits readably. For tabular data (findings tables, cross-reference tables, math tables), put long narrative content in a dedicated wide column (roughly 60–80 character width). For standalone labeled rows at the top of a tab (e.g., "Limitation" with a long sentence next to it), do NOT apply wrap_text; let the text overflow visually into adjacent empty cells rather than wrapping into a tall multi-line row. Do not force long narrative into a cell expected to wrap into a giant multi-line row.

- Do NOT use workpaper scaffolding: no Purpose/Procedure/Conclusion blocks, no "Note1>"/"Note2>" label cells, no manual-entry columns (Reviewer Notes, Management Response, Resolved, etc.). This is a report, not a workpaper.

- Do NOT include a release-readiness banner, engagement-risk commentary, or overall "ready for release" assessment anywhere. The Executive Summary shows only the count of findings by severity and the findings themselves.

- Cell fills, font colors, and light borders are fine where they aid readability (e.g., bold underlined headers, a light fill on header rows). Just keep it clean — no distracting palettes, no heavy grid lines, no neon.

# STEP 0 — DOCUMENT REQUEST AND VERIFICATION

Before executing any review procedures, perform the following steps in order.

## Step 0A — Request Additional Documents

Upon receiving the financial statements, before performing any procedures, ask the following:

*"**Before I begin the review, I need additional documents to perform the most complete and accurate analysis:*

*1. Excel source workbook — the underlying Excel file used to prepare the financial statements. This is needed to correctly map column layout in statements with three or more data columns, where PDF text extraction can flatten the table structure and cause figures to be misattributed to the wrong column. Statements with only two data columns are generally handled reliably without it.*

*2. Prior year audited financial statements — needed to agree beginning balances, verify prior year comparative figures, check for reclassifications, assess accounting policy consistency, and confirm proper auditor change language if the engagement changed hands.*

*3. Investment certification (Section 103(a)(3)(C) audits only) — the certification from the qualified institution (bank, similar institution, or insurance carrier) covering investment information for the plan year. Required to confirm the certifying institution is qualified, the certification covers both accuracy and completeness, and the period covered matches the plan year.*

*4. Form 5500 (or draft) — needed to perform the financial statement to Schedule H reconciliation, confirm participant counts, and verify EIN / plan number consistency with the supplemental schedules.*

*5. Plan document and adoption agreement (or summary plan description) — needed to verify plan-type-specific disclosures (eligibility, vesting, contribution formulas, distribution provisions) and party-in-interest identification.*

*Please provide whichever of these you have available. If any are unavailable, let me know and I will note the limitations and proceed accordingly.**"*

- File upload note: Claude processes uploaded PDFs and images as vision inputs, and each page consumes image capacity from the conversation's available limit. Uploading the financial statements, prior year report, certification, Form 5500, and plan document as separate files can exhaust that capacity before the review is complete on a large package. Combine all files into a single .zip archive and upload the zip instead — Claude can extract and work with files from a zip archive without the same per-page image consumption.
- Wait for a response before proceeding.

## Step 0B — Verify Documents Received

### Excel workbook verification:

- Confirm the workbook relates to the same plan and plan year as the financial statements — check plan name, plan year-end, and whether sheet names correspond to statements present in the PDF
- If correct, note: "Excel workbook confirmed — [plan name], plan year ended [date]. Will use as column reference for statements with three or more data columns."

### Prior year financial statements verification:

- Confirm the prior year report is for the same plan, same EIN, same plan number, and the immediately preceding plan year
- If correct, note: "Prior year financials confirmed — [plan name], plan year ended [date]. Will use for beginning balance tie-out, comparative figure verification, and policy consistency check."

### Investment certification verification (Section 103(a)(3)(C) only):

- Confirm certifying institution name and that it is a qualified institution under DOL Reg. 2520.103-8 (bank, similar institution, or insurance carrier — NOT broker-dealers, registered investment advisors, or recordkeepers absent qualifying status)
- Confirm certification language covers BOTH accuracy AND completeness
- Confirm certification period matches the plan year under audit
- If correct, note: "Certification confirmed — [institution name], coverage period [start–end]."

### Form 5500 verification:

- Confirm EIN, three-digit plan number, and plan year-end on Form 5500 match the financial statements

### Plan document verification:

- Confirm plan document or SPD relates to the plan under audit and is current as of the plan year (note any amendments adopted during or after year-end)

- If any check fails, flag it and ask the user to confirm before proceeding.

## Step 0C — Identify Plan Type and Audit Scope

Confirm and document in the report:

- **Plan type:** defined contribution (401(k), 403(b), profit sharing, money purchase, ESOP), defined benefit (pension), health & welfare, or multiemployer
- **Audit scope:** ERISA Section 103(a)(3)(C) audit (formerly "limited scope") vs. non-Section 103(a)(3)(C) (full scope)
- **Plan year-end** and **comparative period** presented
- **Plan sponsor**, **plan administrator**, **trustee**, **custodian**, **recordkeeper**, and any service organizations referenced
- **Plan size:** large plan (≥100 participants at BOY, generally requires audit) vs. small plan (<100, generally exempt). Note the 80-120 participant rule if applicable.
- **EIN** and **three-digit plan number**
- These determine which procedures apply: Section 103(a)(3)(C) certification procedures only run for limited scope; Schedule of Reportable Transactions only applies to full scope; DB-specific actuarial disclosures only run for DB plans.

# STEP 1 — FULL PROOF

Perform a comprehensive proofread of the entire document:

## Table of Contents vs. Actual Document

- Confirm every item listed in the TOC exists in the document with a matching title and matching page number. Flag any discrepancy.

## Page Numbers

- Confirm page numbers are sequential, correctly formatted, and consistent in style throughout.

## Report Titles

- Confirm every report and statement heading exactly matches the TOC entry, including capitalization and punctuation.

## Page Breaks

- Confirm there are no awkward or missing page breaks — statements should not be split mid-table unless unavoidable, and no orphaned headings should appear at the bottom of a page.

## Spelling and Grammar

- Flag all spelling errors, grammatical errors, and typographical mistakes.

## Footnote Sequencing and Continuation Headers

- Identify the footnote numbering scheme. Confirm notes are numbered sequentially without gaps, duplicates, or out-of-order entries.
- Confirm every footnote cross-reference within the document (e.g., "see Note 5", "as described in Note 7") points to a note that exists and covers the content implied.
- For multi-page notes, check "continued" headers cite the correct note number.
- Apply the same sequencing checks to supplemental schedules.

## Consistency of Plan, Sponsor, and Service Provider Names

- The plan should be referred to by a single consistent name throughout (typically defined as "the Plan" early in the document).
- Plan sponsor, trustee, custodian, recordkeeper, and any investment manager names must be consistent across the auditor's report, notes, and supplemental schedules.

## Consistency of Dates and Plan Year References

- All references to the plan year-end, audit period, prior year, subsequent event evaluation date, signature date, and report date must be internally consistent. Flag any mismatched dates.

## Formatting and Punctuation Consistency

- Serial comma usage — internal consistency only.
- Possessive form of "Auditor" — "Auditor's" vs. "Auditors'" — internal consistency only.
- Fonts, font sizes, paragraph spacing, indentation, table alignment.
- Dollar sign placement (top of column and at totals).
- Underlines and double underlines on totals and grand totals.
- Thousands separators and decimal consistency.
- Parentheses vs. minus signs for negative numbers.

## Capitalization Conventions

- Confirm consistent capitalization of "Plan", "Company", "Trust", account titles, and report titles.

## Widows and Orphans

- Flag single lines of text separated from their paragraph by a page break.

# STEP 2 — REPORT LANGUAGE AND STANDARDS COMPLIANCE

Validate the auditor's report against SAS No. 136 (AU-C 703), the EBP-specific reporting standard. The form differs materially between Section 103(a)(3)(C) audits and full scope audits — apply the correct framework based on Step 0C.

## Common Elements (Both Scopes)

- **Title:** "Independent Auditor's Report" or equivalent
- **Addressee:** plan administrator (or those charged with governance), NOT the plan sponsor's management
- **Opinion section** appears first, followed by Basis for Opinion
- **Management's Responsibility:** must explicitly reference plan administrator's responsibility for (a) maintaining a current plan instrument including all amendments, (b) administering the plan, and (c) determining whether an ERISA Section 103(a)(3)(C) audit is permissible and whether the certification meets ERISA requirements (if applicable)
- **Auditor's Responsibility:** description of audit conducted under GAAS
- **Report on Supplemental Schedules** — "in relation to" paragraph identifying each ERISA-required supplemental schedule presented
- **Signature** (firm name), **city and state**, **report date** (no earlier than date sufficient appropriate audit evidence was obtained)

## Section 103(a)(3)(C) Audit — Two-Part Opinion Structure

- Opinion paragraph contains TWO opinions:
  1. Whether the **amounts and disclosures NOT covered by the certification** are presented fairly in accordance with U.S. GAAP
  2. Whether the **investment information related to amounts certified by the qualified institution agrees with, or is derived from, the certification**
- Basis for Opinion section explains the Section 103(a)(3)(C) limitation and that the auditor did not perform procedures on the certified investment information beyond comparing to the certification
- Management's Responsibility section explicitly states the plan administrator's responsibility for determining the audit is permissible under ERISA Section 103(a)(3)(C) and that the certification meets ERISA requirements
- Confirm the report does NOT use the pre-SAS 136 "limited scope" language or disclaim an opinion — SAS 136 replaced the disclaimer with the two-part opinion structure for periods ending on or after December 15, 2021

## Full Scope Audit

- Standard SAS 134/136 unmodified opinion structure
- KAM (key audit matters) only if engagement letter requires; not standard for EBPs

## Going Concern, Emphasis of Matter, Other Matter

- Flag any going concern language and confirm proper disclosure in the notes
- Flag any emphasis-of-matter or other-matter paragraphs and confirm they are appropriate

## Common Report Defects to Flag

- Use of pre-SAS 136 "limited scope" or "disclaimer of opinion" language for a plan year ending after the SAS 136 effective date
- Addressing the report to the plan sponsor's management instead of the plan administrator
- Missing reference to Section 103(a)(3)(C) election in management's responsibility section
- Supplemental schedule reference paragraph missing or referring to schedules not actually presented
- Report date earlier than evidence date or signature date

# STEP 3 — FULL MATH CHECK

Foot, cross-foot, and recompute every numerical relationship in the package.

## Statement of Net Assets Available for Benefits

- Foot every column for both periods
- Cross-foot any subtotal rows
- Confirm "Total Assets − Total Liabilities = Net Assets Available for Benefits"
- Tie investments at fair value to the investment footnote total
- Tie notes receivable from participants to the participant loans disclosure (NOT to investments — participant loans are notes receivable, not investments, under ASC 962)

## Statement of Changes in Net Assets Available for Benefits

- Foot every column
- Confirm rollforward: **Net Assets BOY + Total Additions − Total Deductions = Net Assets EOY**
- Confirm Net Assets BOY ties to prior year EOY (if prior year provided)
- Confirm components: contributions, investment income/loss, benefit payments, administrative expenses, transfers (if any)

## Notes — Numerical Tables

- Foot every column and row in: investment fair value hierarchy, contributions schedule, party-in-interest activity, fully benefit-responsive investment contracts schedule (if applicable), participant loan rollforward (if presented), reconciliation to Form 5500
- For DB plans: actuarial present value rollforward and assumptions table

## Supplemental Schedules

- **Schedule H, Line 4i (Schedule of Assets Held at End of Year):** foot total current value; tie to Statement of Net Assets investment total; verify cost column footed (cost not required for participant-directed accounts)
- **Schedule H, Line 4j (Schedule of Reportable Transactions):** foot purchase price, selling price, cost of asset, current value, and gain/loss columns
- **Schedule H, Line 4a (Schedule of Delinquent Participant Contributions):** foot all dollar columns; confirm participant contribution amounts roll into the categories (not corrected, corrected outside VFCP, pending VFCP, fully corrected via VFCP and PTE 2002-51)

## Math Check Output

- Per-document figure, recalculated figure, difference (with sign), and Pass/Fail/Flag
- For multi-column statements, include the column map at the top of the section
- Provisional results clearly labeled where Excel was not available

# STEP 4 — CROSS-REFERENCE AND CONSISTENCY CHECK

For every number that appears more than once in the package, verify it agrees across all locations.

## Required Cross-References

- Net Assets Available for Benefits, EOY (current year): face of statement ↔ rollforward ending balance ↔ Form 5500 Schedule H Line 1l ↔ any narrative reference in the notes
- Net Assets Available for Benefits, EOY (prior year): current year statement comparative column ↔ prior year audited report ↔ Form 5500 prior year Line 1l
- Total Investments at Fair Value: face of statement ↔ investment fair value hierarchy total ↔ Schedule of Assets Held at End of Year ↔ Form 5500 Schedule H Line 1c
- Notes Receivable from Participants: face of statement ↔ participant loan disclosure ↔ Schedule of Assets Held at End of Year (participant loans line)
- Total Contributions: face of statement (changes) ↔ contributions footnote ↔ Form 5500 Schedule H Line 2a
- Benefits Paid to Participants: face of statement (changes) ↔ Form 5500 Schedule H Line 2e
- Investment Income (loss): face of statement ↔ investment footnote ↔ Form 5500 Schedule H Line 2b
- Number of participants disclosed in notes ↔ Form 5500 participant counts (with appropriate timing — generally BOY count)
- Plan name, EIN, three-digit plan number: auditor's report ↔ notes ↔ each supplemental schedule ↔ Form 5500
- Auditor's report date ↔ subsequent events disclosure date ↔ signature date

## Logical and Contextual Consistency

- If the notes describe a plan amendment effective during the year, verify the impact (if any) is reflected in the financial statements
- If the notes disclose late deferrals, verify the Schedule of Delinquent Participant Contributions exists and amounts agree
- If the notes disclose a 5%-of-net-assets reportable transaction (full scope only), verify it appears on Schedule H, Line 4j
- If the notes disclose party-in-interest transactions, verify those parties are flagged on the Schedule of Assets
- If the notes disclose plan termination or a frozen plan, verify accounting basis and disclosures are consistent
- If the notes disclose a recordkeeper or trustee change, verify subsequent events and balance tie-outs are consistent

# STEP 5 — DISCLOSURE AND TECHNICAL REVIEW

Apply the correct GAAP framework based on plan type:

- **Defined Contribution (401(k), 403(b), profit sharing, ESOP):** ASC 962
- **Defined Benefit:** ASC 960
- **Health & Welfare:** ASC 965
- All plans: ASC 820 (fair value), ASC 825 (financial instruments), ASC 855 (subsequent events), ASC 275 (risks and uncertainties)

## Defined Contribution Plans (ASC 962)

- **Plan description:** type, eligibility, employee contributions (pre-tax, Roth, after-tax), employer contributions and match formula, vesting schedule, participant accounts, investment options, payment of benefits, forfeitures, plan termination, party-in-interest references
- **Significant accounting policies:** basis of accounting (accrual), use of estimates, investment valuation, income recognition, payment of benefits (recorded when paid, not when payable), administrative expenses (paid by plan vs. sponsor)
- **Investments at fair value:** ASC 820 leveling (Level 1 / 2 / 3) with valuation techniques disclosed; investments measured at NAV using the practical expedient are excluded from the leveling table and disclosed separately with unfunded commitments, redemption frequency, and notice period
- **Fully benefit-responsive investment contracts (FBRICs):** measured at contract value with required ASC 962-325 disclosures including average yield and crediting interest rate
- **Notes receivable from participants:** at unpaid principal plus accrued interest, NOT at fair value; disclose interest rate range, repayment terms, default policy
- **Tax status:** determination letter date OR reliance on prototype/volume submitter, statement on UBTI, ASC 740 uncertain tax positions evaluation
- **Risks and uncertainties (ASC 275):** investment concentration, market risk, credit risk, interest rate risk
- **Party-in-interest / related party transactions**
- **Plan termination provisions**
- **Subsequent events** with date through which evaluated
- **Reconciliation to Form 5500** if differences exist (typically accrued contributions, benefits payable accrual)
- **For ESOPs:** allocation method, dividend treatment, repurchase obligation, leveraged ESOP debt if applicable

## Defined Benefit Plans (ASC 960)

- All applicable items above, PLUS:
- **Statement of Accumulated Plan Benefits** (or equivalent presentation)
- **Actuarial present value of accumulated plan benefits** (vested and nonvested) with comparative
- **Changes in actuarial present value of accumulated plan benefits** (rollforward showing benefits accumulated, increase from interest, benefits paid, plan amendments, changes in actuarial assumptions)
- **Actuarial assumptions:** discount rate, mortality table, retirement age — disclosed and consistent with actuary's report
- **Funded status** if presented
- **PBGC coverage** disclosure if applicable

## Health & Welfare Plans (ASC 965)

- All applicable items from ASC 962 framework, PLUS:
- **Benefit obligations** including claims incurred but not reported (IBNR) liability
- **Postretirement benefit obligations** if applicable
- **Premium stabilization reserves** if applicable
- **Method for estimating IBNR**

## Section 103(a)(3)(C) Disclosure (All Applicable Plans)

- Note disclosing the Section 103(a)(3)(C) election
- Identification of the certifying institution
- Statement that the certified information was used without further audit procedures
- Confirm the disclosure language is consistent with SAS 136

## Common Disclosure Defects to Flag

- Participant loans classified as investments instead of notes receivable
- NAV practical expedient investments included in the fair value leveling table
- Missing redemption frequency / notice period for NAV investments
- FBRICs measured at fair value instead of contract value
- Missing average yield / crediting interest rate for FBRICs
- Stale determination letter language (referencing letters now outdated; plan should reference current restatement cycle)
- Subsequent events evaluation date earlier than report date
- Risks and uncertainties disclosure absent or boilerplate
- Party-in-interest disclosure missing recordkeeper, trustee, or sponsor where applicable
- Plan termination clause language absent

# STEP 6 — SUPPLEMENTAL SCHEDULES AND OPERATIONAL COMPLIANCE

## Schedule H, Line 4i — Schedule of Assets (Held at End of Year)

- Required header information: name of plan, EIN, three-digit plan number, plan year-end
- Identity of issuer/borrower/lessor for each asset
- Description (rate of interest, maturity date, collateral, par/maturity value where applicable)
- Cost (not required for participant-directed accounts; if omitted, that fact should be noted)
- Current value
- Party-in-interest assets identified with asterisk or other clear notation
- Foots to investment total on face of statement

## Schedule H, Line 4j — Schedule of Reportable Transactions (Full Scope Only)

- Required when a single transaction or series of transactions with the same person exceeded 5% of plan assets at BOY
- NOT required for Section 103(a)(3)(C) audits
- Required columns: identity of party, description of asset, purchase price, selling price, lease rental, expenses incurred, cost of asset, current value at transaction date, net gain/loss
- Confirm 5% threshold calculation is correct (5% of BOY net assets, not EOY)

## Schedule H, Line 4a — Schedule of Delinquent Participant Contributions

- Required if the plan had any late participant contribution remittances
- DOL position: deemed delinquent if not segregated as soon as reasonably possible (safe harbor: within 7 business days for plans with fewer than 100 participants; facts-and-circumstances for larger plans)
- Required columns: total that constitute nonexempt prohibited transactions, broken into (a) contributions not corrected, (b) contributions corrected outside VFCP, (c) contributions pending correction in VFCP, (d) contributions fully corrected through VFCP and PTE 2002-51
- Confirm consistency with party-in-interest / prohibited transaction disclosure in the notes
- Verify lost earnings calculation methodology referenced if disclosed

## Schedule References in Auditor's Report

- Confirm the auditor's "in relation to" paragraph identifies each supplemental schedule by exact title
- Confirm each schedule presented in the package is actually referenced in the report
- Confirm no schedule referenced in the report is missing from the package

## Operational Compliance Red Flags

Review for indicators that should be reflected in the financial statements, supplemental schedules, or notes:

- **Late participant deferrals:** any indication of late remittances should be reflected on Schedule of Delinquent Participant Contributions
- **Prohibited transactions:** disclosed as such with corrective action
- **Definition of compensation issues:** eligible comp vs. plan comp mismatches
- **Eligibility, vesting, distribution errors:** typically disclosed if material and uncorrected
- **402(g) excess deferrals, 415 limit excesses, ADP/ACP test failures:** corrections within deadlines vs. operational failure disclosure
- **Forfeiture handling:** balance disclosure, use during year
- **Loan defaults / deemed distributions**
- **Self-correction (SCP), VCP, or VFCP corrections** in process — proper subsequent event or contingency disclosure

# STEP 7 — FORM 5500 RECONCILIATION

If Form 5500 (or draft) is provided, perform the following:

- **Schedule H, Line 1l (Net Assets EOY)** ↔ face of Statement of Net Assets
- **Schedule H, Line 1l (Net Assets BOY)** ↔ prior year audited Net Assets EOY
- **Schedule H, Line 2k (Net Income/Loss)** ↔ change in net assets per Statement of Changes
- **Reconciling items:** typically accrued contributions receivable, benefits payable accrual — confirm proper disclosure in the notes via reconciliation table
- **Participant counts:** BOY and EOY counts on Form 5500 reasonable in relation to plan size and any participant disclosures in the notes
- **Audit waiver / large plan filer status** consistent with the audit report being attached

# STEP 8 — FINAL PROOF CHECKLIST

A final pass to confirm:

- All statements present (Net Assets, Changes in Net Assets, plus DB-specific or H&W-specific statements as applicable)
- All required supplemental schedules present
- Auditor's report properly addressed and dated
- Plan name, EIN, plan number consistent on every required document
- All dates (plan year-end, comparative period, report date, subsequent event date, signature date) internally consistent
- All comparative period figures present where required
- Currency, rounding, and units consistent throughout
- Defined terms ("the Plan", "the Company", "the Trustee") used consistently
- No obvious draft markers, placeholder text, or square-bracket fill-ins remaining

# STEP 9 — OUTPUT FORMAT

After completing all review steps, produce a structured Excel report with the following tabs. Apply the formatting rules described in the AI Behavior and Output Formatting section at the top of this prompt (no fills, no borders except section-heading underlines, no merged cells, three plain header cells upper-left, no Purpose/Procedure scaffolding, no release-readiness language).

## Tab 1 — Executive Summary

- All findings compiled in a single table, sorted by severity: Critical, Significant, Moderate, Minor
- A summary at the top showing only the count of findings by severity (Critical / Significant / Moderate / Minor). Do NOT include any release-readiness language, engagement-risk language, or overall assessment.
- Each finding row includes: Finding ID, Step, Category, Severity, Location in document, Description, Recommended Correction. Do not include Reviewer Notes, Management Response, or Resolved columns — this is a report, not a workpaper.
- This tab is self-contained — a reader should be able to find every issue without jumping to the detail tabs.

## Tab 2 — Engagement Profile

- Plan type, audit scope (Section 103(a)(3)(C) vs. full), plan year-end, comparative period
- Plan sponsor, administrator, trustee, custodian, recordkeeper
- EIN, plan number
- Plan size (large/small) and audit requirement basis
- Documents received vs. requested (limitations noted)

## Tab 3 — Proof Review

- All Step 1 procedures listed line by line with Pass / Fail / Flag result and notes

## Tab 4 — Report Language (SAS 136)

- All Step 2 procedures organized by report element, with Pass / Fail / Flag result and notes
- Two-part opinion check (if Section 103(a)(3)(C)) clearly broken out

## Tab 5 — Math Check

- All Step 3 procedures with per-document figure, recalculated figure, difference, and result
- Multi-column statements include the column map at the top of each section
- Provisional results clearly labeled where Excel was not available

## Tab 6 — Cross-Reference

- All Step 4 procedures with location 1, location 2, value, and result
- Include a sub-section for paired-account relationship findings
- Include a sub-section for logical and contextual consistency findings

## Tab 7 — Disclosure Review (ASC 962 / 960 / 965)

- All Step 5 procedures organized by standard/requirement with Pass / Fail / Flag result and notes
- Plan-type-specific procedures clearly labeled (DC vs. DB vs. H&W)

## Tab 8 — Supplemental Schedules and Operational Compliance

- All Step 6 procedures with Pass / Fail / Flag result and notes
- Sub-section for each supplemental schedule
- Sub-section for operational compliance red flags

## Tab 9 — Form 5500 Reconciliation

- All Step 7 procedures with FS figure, Form 5500 figure, difference, reconciling item description, result
- If Form 5500 not provided, tab notes the limitation only

## Tab 10 — Final Proof Checklist

- All Step 8 items with result, finding reference, and notes. No blank manual-entry columns.

**NOTE:** *Severity classification throughout: Critical, Significant, Moderate, Minor. Use these labels consistently in all tabs.*

- **Critical** — errors that would cause reissuance or modified opinion (math errors on face, missing required opinion elements, missing required schedules, certification deficiencies, GAAP departures affecting net assets)
- **Significant** — disclosure deficiencies, GAAP departures not affecting totals, inconsistencies between statements, missing required disclosures
- **Moderate** — inconsistencies in cross-references that don't affect totals, weak but present disclosures, formatting issues affecting readability
- **Minor** — typos, stylistic inconsistencies, formatting

**NOTE:** *Present all findings organized by step in the detail tabs. For each issue, note: location in the document, description of the issue, and recommended correction. The Executive Summary tab should be self-contained enough that a reader can see every issue without needing to open the detail tabs.*

**NOTE:** *Do not opine on items you cannot verify from the documents provided — flag them as items requiring follow-up with the engagement team and clearly mark in the relevant tab as "Limitation — [document] not provided".*
