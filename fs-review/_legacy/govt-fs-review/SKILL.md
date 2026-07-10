---
name: govt-fs-review
description: Comprehensive technical proof and review of a governmental financial statement package — municipality, county, state agency, special district, school district, tribal government, CAFR/ACFR, Single Audit, Yellow Book/GAGAS. Use this skill WHENEVER the user uploads or references a governmental financial statement, audit report, CAFR, ACFR, SEFA, or SFQC and asks for a review, proof, technical review, QC check, math check, cross-reference check, or disclosure review. Trigger even if the user does not say "skill" — a CAFR/ACFR plus any review-style ask ("check this", "proof this", "find issues", "review before QC") should activate it. Also trigger on GASB standards review, Uniform Guidance / 2 CFR Part 200 review, Yellow Book report review, SEFA/SFQC review, or auditor's report language review against SAS No. 134. Do NOT use for commercial financials without federal funds, tax returns, or bookkeeping.
---

# Governmental Financial Statement Technical Review

**GOVERNMENTAL FINANCIAL STATEMENT TECHNICAL REVIEW**

*AI Review Prompt — Quality Control Procedures*

Version 2.0  |  For use with Claude or equivalent LLM

**PURPOSE:** This document is a structured prompt instructing an AI model to perform a comprehensive technical proof and review of a governmental financial statement package. The output is intended to assist a preparer in locating issues in the financial statements — either after a first pass or as a final proof before turning the package over to QC. It is not a substitute for human quality control; actual QC is performed by qualified personnel. This prompt focuses on the document itself and what is wrong with it. Paste this prompt into the AI, then provide or attach the financial statements for review. The AI will request additional supporting documents before beginning, adapt its procedures based on entity type and audit type, and issue warnings where supporting documents are absent.

# AI BEHAVIOR AND OUTPUT FORMATTING

## Narration and Commentary

Keep chat output minimal. Do not narrate each procedure as it is performed, do not provide running commentary on findings or hypotheses, and do not summarize or editorialize on results at the end. While working through the review, announce only the step number and the title of the step (e.g., "Step 1 — Proof Review", "Step 3 — Math Check"). Do not announce sub-steps or internal procedures. All findings and conclusions belong in the Excel report, not in chat. Clarifying questions to the user are permitted where Step 0 or Step 0C require them.

## Excel Report Formatting — Strict Rules

The deliverable is a plain Excel REPORT, not a workpaper. Keep it clean and readable. A few requirements:

- Produce a valid .xlsx file that opens cleanly in Excel with no XML errors, no broken formulas, and no hidden corruption. Test by opening with openpyxl or similar after saving if uncertain.

- Header block on every tab: three plain cells stacked vertically in column A — (1) client name, (2) report/tab name, (3) date of financials. No merging.

- Size column widths so content fits readably. For tabular data (findings tables, cross-reference tables, math tables), put long narrative content in a dedicated wide column (roughly 60–80 character width). For standalone labeled rows at the top of a tab (e.g., "Limitation" with a long sentence next to it), do NOT apply wrap_text; let the text overflow visually into adjacent empty cells rather than wrapping into a tall multi-line row. Do not force long narrative into a cell expected to wrap into a giant multi-line row.

- Do NOT use workpaper scaffolding: no Purpose/Procedure/Conclusion blocks, no "Note1>"/"Note2>" label cells, no manual-entry columns (Reviewer Notes, Management Response, Resolved, etc.). This is a report, not a workpaper.

- Do NOT include a release-readiness banner, engagement-risk commentary, or overall "ready for release" assessment anywhere. The Executive Summary shows only the count of findings by severity and the findings themselves.

- Cell fills, font colors, and light borders are fine where they aid readability (e.g., bold underlined headers, a light fill on header rows). Just keep it clean — no distracting palettes, no heavy grid lines, no neon.

# STEP 0 — DOCUMENT REQUEST AND VERIFICATION

Before executing any review procedures, perform the following steps in order.

## Step 0A — Request Additional Documents

Upon receiving the financial statements, before performing any procedures, ask the following:

*"**Before I begin the review, I need two additional documents to perform the most complete and accurate analysis:*

*1. Excel source workbook — the underlying Excel file used to prepare the financial statements. This is needed to correctly map column layout in statements with three or more data columns, where PDF text extraction can flatten the table structure and cause figures to be misattributed to the wrong column. Statements with only two data columns are generally handled reliably without it. Without the Excel file, math check results on any statement with three or more columns should be treated as provisional.*

*2. Prior year audited financial statements — the issued financial statements for the preceding fiscal year. This is needed to agree beginning balances, verify prior year comparative figures if presented, check for reclassifications, assess accounting policy consistency, and confirm proper auditor change language if the engagement changed hands.*

*Please provide whichever of these you have available. If either is unavailable, let me know and I will note the limitations and proceed accordingly.**"*

*Important note on file uploads: Claude processes uploaded PDFs and images as vision inputs, and each page of a document consumes image capacity from the conversation's available limit. If you upload the financial statements, the prior year report, and the Excel workbook as separate files, a large package can exhaust that capacity before the review is complete. To avoid this, it is strongly recommended that you combine all files into a single .zip archive and upload the zip rather than uploading files individually. Claude can extract and work with files from a zip archive without the same per-page image consumption.**"*

Wait for a response before proceeding.

## Step 0B — Verify Documents Received

### Excel workbook verification:

- Confirm the workbook relates to the same entity and fiscal year as the financial statements — check entity name, fiscal year end, and whether sheet names correspond to statements present in the PDF

- Confirm the workbook contains tabs relevant to the statements being reviewed

- If the workbook appears to relate to a different entity, a different year, or does not contain recognizable financial statement schedules, flag this and ask the user to confirm before proceeding

- If correct, note: "Excel workbook confirmed — [entity name], fiscal year ended [date]. Will use as column reference for statements with three or more data columns."

### Prior year financial statements verification:

- Confirm the prior year report is for the same entity

- Confirm the prior year end date is the fiscal year immediately preceding the current year under review

- Confirm the document appears to be a complete issued financial statement package — not a draft, not a different entity, not a non-consecutive year

- If any check fails, flag it and ask the user to confirm before proceeding

- If correct, note: "Prior year financials confirmed — [entity name], fiscal year ended [date]. Will use for beginning balance tie-out, comparative figure verification, and policy consistency check."

## Step 0C — Proceed with Warnings if Documents Are Missing

### If the Excel workbook was not provided:

**⚠ WARNING:** *EXCEL WORKBOOK NOT PROVIDED: Math checks on financial statements with three or more data columns are subject to column attribution error. PDF text extraction can flatten table layouts in these statements, making it unreliable to confirm which figures belong to which columns. Statements with only two data columns are generally handled correctly without the Excel file. Math check results on the following statements (three or more columns) should be treated as provisional and independently verified by the reviewer: [list all statements present with three or more data columns]. All other procedures are unaffected.*

Then proceed with the review, noting "PROVISIONAL — Excel not provided" on any math check result involving a statement with three or more data columns.

### If the prior year financial statements were not provided:

Ask the following before proceeding:

*"**Prior year financial statements were not provided. Before I proceed, can you tell me: Is this a first-year or first-time audit engagement — i.e., no prior year audited financials exist? Or are prior year audited financials available but not provided at this time?**"*

### If first-year audit or no prior audited financials exist:

- Note this and do not flag missing prior year tie-outs as findings

- Note that beginning balances cannot be agreed to a prior audited report as none exists — expected for a first-year engagement

- Review opening balance disclosures and any predecessor auditor or compilation report language that may be present

- Proceed with all other procedures normally

### If prior year financials exist but were not provided:

**⚠ WARNING:** *PRIOR YEAR FINANCIALS NOT PROVIDED: The following procedures cannot be completed and should be treated as incomplete pending receipt of the prior year report: beginning balance tie-out; prior year comparative figure verification; accounting policy consistency check; reclassification disclosure verification; auditor change language verification. All other procedures will execute normally.*

Proceed with the review, noting "INCOMPLETE — Prior year report not provided" on any procedure that cannot be performed.

# PRELIMINARY: IDENTIFY AUDIT TYPE AND ENTITY

Before any other procedures, perform the following identification steps:

- Identify the entity type (municipality, county, state agency, special district, tribal government, school district, nonprofit receiving federal funds, etc.) and note which standards apply: GASB, GAAS, GAGAS/Yellow Book, Uniform Guidance/Single Audit.

- Determine whether a Yellow Book (GAGAS) audit has been performed. Look for: Government Auditing Standards report, report on compliance and internal control over financial reporting, and related language throughout.

- Determine whether a Single Audit (2 CFR Part 200 / Uniform Guidance) has been performed. Look for: Schedule of Expenditures of Federal and Nonfederal Awards (SEFA), Schedule of Findings and Questioned Costs (SFQC), Summary Schedule of Prior Audit Findings, auditor's reports on compliance for each major program and on internal control over compliance, and Data Collection Form references.

**NOTE:** *All subsequent steps should be adapted to the identified entity type and audit type.*

# STEP 1 — FULL PROOF

Perform a comprehensive proofread of the entire document:

## Table of Contents vs. Actual Document

- Confirm every item listed in the TOC exists in the document with a matching title and matching page number. Flag any discrepancy.

## Page Numbers

- Confirm page numbers are sequential, correctly formatted, and consistent in style throughout.

- Check that introductory/statistical sections use different numbering conventions where required (e.g., roman numerals for the introductory section in a CAFR/ACFR).

## Report Titles

- Confirm every report and statement heading in the document exactly matches the TOC entry, including capitalization and punctuation.

## Page Breaks

- Confirm there are no awkward or missing page breaks — statements should not be split mid-table unless unavoidable, and no orphaned headings should appear at the bottom of a page.

## Spelling and Grammar

- Flag all spelling errors, grammatical errors, and typographical mistakes.

## Footnote Sequencing and Continuation Headers

- Identify the footnote numbering scheme used (numeric: 1, 2, 3; alphabetic: A, B, C; or mixed). Confirm notes are numbered sequentially without gaps, duplicates, or out-of-order entries. Flag any skipped number/letter, any repeated number/letter, and any note that appears out of sequence.

- Confirm every footnote cross-reference within the document (e.g., "see Note 5", "as described in Note 11") points to a note that exists and covers the content implied by the reference. Flag any reference to a note that does not exist or does not address the topic referenced.

- For multi-page notes, check "continued" headers at the top of each continuation page. The continuation header must cite the correct note number/letter being continued. Flag: (a) missing continuation header where a note spans pages; (b) continuation header citing the wrong note number; (c) continuation header present but the prior page's note actually ended on that page (i.e., a new note starts on the current page, and no continuation is actually occurring).

- Apply the same sequencing and continuation checks to other numbered/lettered sequences in the document where applicable: finding numbers in the Schedule of Findings and Questioned Costs, subheadings within a note (a, b, c or i, ii, iii), and continuation headers on multi-page schedules (e.g., "Combining Statement — continued" must accurately describe what is being continued).

## Consistency of Language

- Flag any inconsistency in how the entity, funds, programs, or accounts are named throughout the document.

- The entity should be referred to by a single consistent name. Fund names, program names, and account titles must be consistent throughout all reports, statements, footnotes, and supplementary schedules.

## Consistency of Dates and Fiscal Year References

- All references to the fiscal year end date, the audit period, and prior year must be internally consistent. Flag any mismatched dates.

## Formatting Consistency

## Punctuation and Possessive Consistency

Check for consistent use of the following punctuation conventions throughout the entire document, including all reports, statements, footnotes, schedules, and supplementary information:

- Serial comma (Oxford comma) usage — determine whether the document uses or omits the serial comma and flag any inconsistency. Do not flag the choice itself, only departures from the chosen convention.

- Possessive form of "Auditor" — identify whether the document uses "Auditor's" (singular possessive) or "Auditors'" (plural possessive) and flag any inconsistency. Do not flag the choice itself, only departures from the chosen convention. Note: both forms can be correct depending on context; the objective is internal consistency, not grammatical prescription.

- Flag any other punctuation convention where usage is inconsistent within the document — including hyphenation of compound terms, use of em dashes vs. en dashes vs. hyphens, and use of periods in abbreviations.

Check for consistent use of all of the following:

- Fonts and font sizes across all sections (headers, body text, table text, footnotes)

- Paragraph spacing and line spacing

- Indentation and table alignment

- Dollar sign placement (should appear at top of column and at totals, not on every line unless style requires it)

- Underlines and double underlines on totals and grand totals in financial statements

- Thousands separators and decimal consistency

- Parentheses vs. minus signs for negative numbers — must be consistent throughout

- Column header style and alignment

## Capitalization Conventions

- Confirm consistent capitalization of account titles, fund names, and report titles.

## Widows and Orphans

- Flag single lines of text separated from their paragraph by a page break.

**NOTE:** *Flag anything else that would be identified during a professional proofread of a formally published financial document.*

# STEP 2 — REPORT LANGUAGE AND STANDARDS COMPLIANCE

For each audit report present, validate the language against current applicable standards. At minimum, the following reports may be present and must each be reviewed:

- Independent Auditor's Report on the Financial Statements (GAAS / SAS)

- Report on Internal Control Over Financial Reporting and on Compliance and Other Matters (Yellow Book — if applicable)

- Report on Compliance for Each Major Federal Program and Report on Internal Control Over Compliance (Single Audit — if applicable)

## For Each Report — General Requirements

Apply the following to every audit report present in the document before proceeding to the report-specific checklists below.

- Confirm the report is addressed to the correct party (governing body, board, or appropriate oversight body — not to management).

- Confirm the report is dated correctly — the report date should be on or after the date sufficient appropriate evidence was obtained, and should not precede the financial statement date.

- Confirm the entity name in the report heading exactly matches the entity name used throughout the financial statements.

- Confirm the report language conforms to the most current applicable standards: SAS No. 134 and subsequent SASs for the financial statement opinion; GAGAS 2018 Yellow Book (or current revision) for the Yellow Book report; 2 CFR Part 200 Subpart F for Single Audit reports.

- Confirm no paragraph is present that is not required or permitted under the applicable standard. Flag any paragraph whose heading or substance does not correspond to a required, conditionally required, or permitted paragraph under the applicable standard.

- Confirm the internal cross-references within each report are accurate — references to other reports in the same package, to the SFQC, to the SEFA, and to specific financial statements must all be verified.

## Independent Auditor's Report on the Financial Statements (GAAS / SAS)

Verify every required paragraph is present, in the correct order, and correctly worded given the facts of the engagement. Also verify that no non-required paragraphs are present. Work through the report sequentially.

### Required paragraphs — verify each is present and correct

- Report title — must include the word "Independent" and identify it as an auditor's report. Flag any title that omits "Independent" or otherwise deviates from standard form.

- Addressee paragraph — confirm the report is addressed to the appropriate party (governing body or its equivalent). Flag if addressed to management only.

- Introductory paragraph — confirm it identifies: (1) the entity audited; (2) the financial statements audited by title; (3) the date or period covered by each statement. Confirm every statement title cited exactly matches the printed title in the document.

- Management's Responsibility section — confirm it states that management is responsible for: (1) preparation and fair presentation of the financial statements in accordance with the applicable financial reporting framework; (2) design, implementation, and maintenance of internal control relevant to preparation and fair presentation. Confirm the applicable framework is correctly identified (e.g., accounting principles generally accepted in the United States of America; GASB standards).

- Auditor's Responsibility section — confirm it states: (1) the auditor's responsibility is to express an opinion based on the audit; (2) the audit was conducted in accordance with auditing standards generally accepted in the United States of America (and, if applicable, Government Auditing Standards); (3) those standards require the auditor to plan and perform the audit to obtain reasonable assurance; (4) an audit involves performing procedures to obtain evidence, assessing risk of material misstatement, evaluating accounting policies and estimates, and evaluating overall presentation. Confirm all four elements are present.

- Opinion paragraph — confirm: (1) the opinion type is clearly stated (unmodified, qualified, adverse, or disclaimer); (2) the financial reporting framework is correctly named; (3) all financial statements cited in the introductory paragraph are included in the opinion; (4) the opinion language matches the SAS No. 134 form for the opinion type expressed. If qualified or adverse, confirm the basis for modification paragraph precedes the opinion paragraph and clearly describes the matter.

- Basis for Qualified or Adverse Opinion paragraph (conditionally required) — required if the opinion is other than unmodified. Confirm it immediately precedes the opinion paragraph, clearly describes the matter giving rise to the modification, and quantifies the effect if practicable. Flag if present with an unmodified opinion.

- Emphasis-of-Matter paragraph (conditionally required) — required when the auditor considers it necessary to draw users' attention to a matter appropriately presented or disclosed that is fundamental to users' understanding. Confirm: (1) it follows the opinion paragraph; (2) it states the matter is not a modification of the opinion; (3) it references the specific note or disclosure. Flag if the financial statements contain a going concern disclosure, a significant uncertainty, a restatement, or a change in accounting principle with no corresponding emphasis-of-matter paragraph.

- Other-Matter paragraph (conditionally required) — required when the auditor communicates a matter other than those presented or disclosed in the financial statements. Common required instances in governmental audits: (1) if the report covers required supplementary information (RSI) — must include the standard RSI paragraph; (2) if supplementary information (SI) is included — must state whether SI was subjected to audit procedures and the auditor's conclusion; (3) if other information (OI) is included — must include the required OI paragraph. Verify each of these paragraphs is present if the corresponding content exists in the document, and absent if it does not.

- RSI other-matter paragraph (conditionally required) — if RSI is present, confirm the paragraph: (1) identifies the RSI by type (e.g., pension schedules, budgetary comparison); (2) states that RSI is required by the applicable standard-setter; (3) states whether limited procedures were applied or whether the auditor was unable to apply limited procedures; (4) does not express an opinion on RSI. If RSI is absent, confirm this paragraph is also absent and that appropriate disclosure of the omission is made.

- SI other-matter paragraph (conditionally required) — if supplementary information is presented, confirm the paragraph: (1) identifies the SI; (2) states the purpose for which it is presented; (3) states whether the SI was subjected to audit procedures applied to the basic financial statements; (4) states the auditor's conclusion on whether it is fairly stated in all material respects in relation to the financial statements as a whole. Flag if SI is present but this paragraph is absent.

- OI paragraph (conditionally required) — if other information is included in the document, confirm the paragraph states that: (1) the other information was not subjected to audit, review, or compilation procedures; (2) the auditor does not express an opinion or provide any assurance on it. Flag if OI is present but this paragraph is absent.

- Report on summarized comparative information (conditionally required) — if prior year comparative figures are presented but not audited in the current engagement, confirm that the prior year figures are labeled "unaudited" on the face of the statements and that the report addresses their status. If comparative statements are presented and the predecessor auditor's report is not reissued, confirm the current auditor's report references the predecessor in accordance with AU-C 710.

- Government Auditing Standards paragraph (conditionally required) — if the audit was conducted under both GAAS and GAGAS, confirm that: (1) the Auditor's Responsibility section states the audit was conducted in accordance with Government Auditing Standards; (2) the report contains the required other-matter paragraph referencing the separate Yellow Book report on internal control and compliance; (3) the title of that separate report is correctly cited and matches the actual report present in the document.

### Paragraph order verification

- Confirm the paragraphs appear in the following order: (1) Report title; (2) Addressee; (3) Introductory paragraph; (4) Management's Responsibility; (5) Auditor's Responsibility; (6) Basis for Modification (if applicable); (7) Opinion; (8) Emphasis-of-Matter (if applicable); (9) Other-Matter paragraphs (if applicable); (10) Signature and date. Flag any deviation from this order.

### No-extra-paragraphs check

- Review every paragraph present in the report. For each paragraph, identify which required or permitted paragraph it corresponds to. Flag any paragraph that does not correspond to a required, conditionally required, or explicitly permitted paragraph under SAS No. 134 and subsequent SASs. Common erroneous additions include: management representation language that belongs in a letter, not the report; scope limitations that are not reflected in a modified opinion; commentary on internal control that belongs only in the Yellow Book report.

## Report on Internal Control Over Financial Reporting and on Compliance and Other Matters (Yellow Book — if applicable)

If a Yellow Book audit was performed, this report is required. Verify every required paragraph is present, in the correct order, and correctly conditioned on whether findings were noted. Work through the report sequentially.

### Required paragraphs — verify each is present and correct

- Report title — confirm it identifies this as a report on internal control over financial reporting and on compliance and other matters.

- Addressee paragraph — confirm addressed to the governing body or appropriate party, consistent with the financial statement opinion.

- Introductory / scope paragraph — confirm it: (1) references the financial statement audit; (2) identifies the standards under which the audit was conducted (GAAS and GAGAS); (3) states that the report does not constitute an audit of internal control or compliance and no opinion is expressed thereon.

- Internal Control Over Financial Reporting section — confirm it: (1) describes management's responsibility for internal control; (2) describes the auditor's consideration of internal control sufficient to plan the audit; (3) correctly uses the defined terms "material weakness" and "significant deficiency" (not other terms); (4) states whether material weaknesses or significant deficiencies were identified. The language must be conditioned correctly: if deficiencies were noted, they must be described or referenced to the SFQC; if none were noted, the standard no-findings language must be present. Flag any use of non-standard terminology (e.g., "reportable condition," "control deficiency" without the defined modifier).

- Compliance and Other Matters section — confirm it: (1) states that as part of obtaining reasonable assurance, the auditor tested compliance with laws, regulations, contracts, and grant agreements; (2) states that the audit does not provide a legal determination of compliance; (3) is correctly conditioned on findings — if instances of noncompliance or other matters were identified, they must be described or referenced to the SFQC; if none, the standard no-findings language must be present.

- Purpose and limitations paragraph — confirm it states that the purpose of the report is solely to describe the scope of testing of internal control and compliance and the results, and is not suitable for any other purpose. Confirm this paragraph is present — its omission is a common error.

- Reference to financial statement opinion — confirm the report references the related financial statement opinion and its date.

- Reference to Schedule of Findings and Questioned Costs (conditionally required) — if findings were noted, confirm the report references the SFQC by its correct title, and that the SFQC is present in the document. If no findings, confirm no erroneous reference to the SFQC appears.

### Paragraph order verification

- Confirm paragraphs appear in the following order: (1) Title; (2) Addressee; (3) Introductory/scope paragraph; (4) Internal Control section; (5) Compliance section; (6) Purpose and limitations paragraph; (7) Signature and date. Flag any deviation.

### No-extra-paragraphs check

- Review every paragraph present. Flag any paragraph not corresponding to a required or permitted element under GAGAS. Common errors: inclusion of opinion language (this report provides no opinion); inclusion of detailed findings text that belongs only in the SFQC; repetition of financial statement titles from the opinion report beyond what is required for context.

## Report on Compliance for Each Major Federal Program and Report on Internal Control Over Compliance (Single Audit — if applicable)

If a Single Audit was performed under 2 CFR Part 200, this report is required. Verify every required paragraph is present, correctly conditioned, and in correct order. Work through the report sequentially.

### Required paragraphs — verify each is present and correct

- Report title — confirm it identifies this as a report on compliance for each major federal program and on internal control over compliance.

- Addressee paragraph — confirm addressed to the governing body or appropriate party.

- Opinion or disclaimer on compliance for each major federal program — confirm: (1) each major program is identified by name and CFDA/ALN number; (2) the opinion type for each program is clearly stated; (3) if a qualified opinion or disclaimer is expressed for any program, a Basis for Qualification paragraph precedes the relevant opinion and describes the matter. Confirm the list of major programs in the report matches the list on the SEFA exactly — by name and ALN number.

- Basis for Qualified or Disclaimer of Opinion (conditionally required) — required if compliance opinion on any program is other than unmodified. Confirm it precedes the relevant opinion, describes the specific compliance requirement at issue, and quantifies questioned costs if applicable.

- Management's Responsibility paragraph — confirm it describes management's responsibility for compliance with federal statutes, regulations, and terms of federal awards.

- Auditor's Responsibility paragraph — confirm it states: (1) the auditor's responsibility is to express an opinion on compliance; (2) the audit was conducted in accordance with GAAS, GAGAS, and 2 CFR Part 200; (3) those standards require planning and performance to obtain reasonable assurance about whether noncompliance could have a direct and material effect on a major program.

- Internal Control Over Compliance section — confirm it: (1) describes management's responsibility for internal control over compliance; (2) describes the auditor's consideration of internal control over compliance; (3) uses the correct defined terms "material weakness" and "significant deficiency" in internal control over compliance; (4) is correctly conditioned — if deficiencies were identified they must be described or referenced to the SFQC; if none, standard no-findings language must appear.

- Purpose and limitations paragraph — confirm it states the purpose is solely to describe the scope of testing of compliance and internal control over compliance and is not suitable for any other purpose. Confirm this paragraph is present — its omission is a common error.

- Dollar threshold for major program determination — confirm the threshold used to identify major programs is stated and is correct for the entity's total federal expenditures per the SEFA.

- Low-risk auditee determination — confirm whether the report states the entity qualifies or does not qualify as a low-risk auditee. If low-risk status is claimed, confirm the entity met all four criteria under 2 CFR §200.520. If not stated, confirm whether it should be and flag the omission.

- Reference to Schedule of Findings and Questioned Costs — confirm the report references the SFQC and that the SFQC is present. If no findings, confirm appropriate no-findings language is present and no erroneous SFQC reference appears.

### Paragraph order verification

- Confirm paragraphs appear in the following order: (1) Title; (2) Addressee; (3) Opinion section (with Basis for Modification if applicable); (4) Management's Responsibility; (5) Auditor's Responsibility; (6) Internal Control Over Compliance section; (7) Purpose and limitations; (8) Signature and date. Flag any deviation.

### No-extra-paragraphs check

- Review every paragraph. Flag any paragraph not corresponding to a required or permitted element under 2 CFR Part 200 Subpart F and the AICPA's Uniform Guidance audit guidance. Common errors: inclusion of program descriptions that belong only on the SEFA; repetition of Yellow Book internal control language that is not required in this report; opinion language covering non-major programs (the compliance opinion covers only major programs).

## Cross-Report Consistency

After completing the individual report reviews, perform the following cross-report checks:

- Confirm all report dates are consistent. The financial statement opinion date, the Yellow Book report date, and the Single Audit report date should all be the same date or explained if different.

- Confirm the findings described or referenced in the Yellow Book report are fully consistent with those in the Single Audit report and with the SFQC — no finding should appear in one report but not another when it should.

- Confirm the entity name, fiscal year, and financial statement titles are stated consistently across all reports.

- Confirm that if any report expresses a modified opinion or notes findings, the financial statement opinion is assessed for consistency — significant compliance findings or control deficiencies that would affect fair presentation should be reflected in the financial statement opinion if appropriate.

- Confirm the Yellow Book other-matter paragraph in the financial statement opinion correctly cites the title of the Yellow Book report as it actually appears in the document.

- Confirm the Single Audit report's list of major programs matches the SEFA exactly — same program names, same ALN numbers, same dollar amounts where cited.

## SEFA (if applicable)

- Confirm it includes all required elements: federal grantor, pass-through grantor (if applicable), program name, CFDA/ALN number, pass-through entity identifying number, total expenditures, and a note regarding the basis of presentation.

- Confirm total federal expenditures on the SEFA is consistent with the applicable threshold determination stated in the Single Audit report.

- For each award listed on the SEFA, confirm the ALN number format is correct (two-digit agency prefix, period, three-digit program number).

- Assess whether the program name listed is consistent with the actual program associated with that ALN number — flag any program name that does not match or closely approximate the official program title in the Assistance Listings.

- Assess whether the federal agency listed as the grantor is consistent with the ALN prefix — flag any combination where the agency and ALN prefix do not correspond (e.g., a health-related program number listed under the Department of Transportation, or any other implausible agency/program pairing).

- For pass-through awards, assess whether the pass-through grantor is a plausible intermediary for that type of federal program.

- Flag any ALN number that does not appear to exist or that corresponds to a program of a materially different nature than described. Use your knowledge of federal programs to assess reasonableness and flag anything warranting verification.

- Confirm cluster identification — verify that programs grouped as a cluster on the SEFA are correctly identified per the current Compliance Supplement.

## Schedule of Findings and Questioned Costs (if applicable)

- Confirm all findings from the Yellow Book and Single Audit reports are represented.

- Confirm each finding contains all required elements: condition, criteria, cause, effect, and recommendation.

- Confirm finding reference numbers are consistently used throughout all documents (SFQC, auditor's reports, Summary Schedule of Prior Audit Findings, Corrective Action Plan).

- Confirm questioned costs, if any, are presented correctly and are internally consistent.

## Summary Schedule of Prior Audit Findings (if applicable)

- Confirm all prior findings are addressed and the current status of each is accurately described.

## MD&A (Management's Discussion and Analysis)

- If present, confirm it includes all required elements under GASB standards.

- If absent, confirm whether it is required and that appropriate language regarding its omission is included in the auditor's report.

## RSI (Required Supplementary Information)

- Confirm all RSI required by applicable GASB standards is present (pension schedules, OPEB schedules, infrastructure condition data if applicable, budgetary comparison information if required as RSI, etc.).

- Confirm the auditor's report contains appropriate language regarding RSI — including the standard paragraph that RSI was not audited, limited procedures were applied, or RSI was not subjected to auditing procedures, as applicable.

- If required RSI is omitted, confirm appropriate disclosure of omission is made in the notes and referenced in the auditor's report.

## Supplementary Information (SI)

- Confirm any SI included is properly labeled as such.

- Confirm the auditor's report appropriately states whether SI was subjected to audit procedures or is presented for additional analysis only.

## Other Information (OI)

- Confirm any OI is properly labeled and that the auditor's report includes the required paragraph addressing OI.

## Prior Year Figures, Comparative Presentations, and Auditor Changes

- If prior year comparative figures are presented, request the prior year issued financial statements if not already provided.

- Agree all beginning balances — fund balances, net position, and other carryforward figures — to the prior year's ending audited figures, regardless of whether a full comparative presentation is made. Flag any beginning balance that cannot be confirmed without the prior year document.

- If the prior year financial statements are provided, confirm all comparative figures agree to the prior year issued report.

- Identify any reclassifications of prior year figures and confirm they are disclosed with an explanation.

- Review accounting policies for consistency with the prior year; if any policy appears to have changed or been newly adopted, flag it and confirm whether the change is disclosed and the effect described.

- If auditors have changed from the prior year and comparative statements are presented, confirm the auditor's report contains proper reference to the predecessor auditor — including the predecessor firm name, date of their report, and type of opinion issued — in accordance with AU-C 710.

- If prior year figures are presented as unaudited, confirm they are labeled as such on the face of the statements and that appropriate disclosure is made.

- Flag any situation where prior year figures appear without audit attribution and without an unaudited label.

## Final Language Checks

- Confirm all names of financial statements cited anywhere in the audit reports exactly match the printed titles of those statements in the document.

- Confirm all years and dates referenced in opinions and reports are correct for the audit period.

# STEP 3 — FULL MATH CHECK

## Excel Source File — Reference Protocol

If an Excel workbook was provided and verified in Step 0, apply the following protocol throughout the math check:

### What the Excel is for:

- Establishing the correct column order and mapping each figure to its column header before performing any arithmetic

- Resolving ambiguous subtotals — where it is unclear from the PDF which line items are intended to sum to a given subtotal, use the Excel to confirm the intended scope of the sum

- Explaining discrepancies — hidden rows, figures displayed as rounded integers but stored as decimals internally, and other Excel-specific artifacts that would cause the printed document to appear not to foot when the underlying data is consistent

- Calibrating your understanding of how the numbers add up before applying that understanding to the PDF

### What the Excel is NOT for:

- Proofing the Excel itself — do not audit formulas, flag Excel errors, or comment on the workbook's construction

- Gospel — the Excel may contain formula errors. If the PDF and Excel disagree on a total, do not automatically defer to the Excel. Flag the discrepancy and note that either the PDF or the Excel may be wrong, and that the preparer should verify

- Overriding a genuine error — if a figure in the PDF does not foot and the Excel agrees with the incorrect total, the error still exists in the printed document and must be flagged

### Formatting conventions and subtotal scope:

The Excel establishes which figures are intended to sum to a given subtotal — but it does not establish whether that subtotal is presented correctly in the printed document. If the formatting conventions used in the printed document — underlines, double underlines, indentation, spacing, section headers — suggest that a subtotal should capture a different set of line items than what the Excel is actually summing, flag it. Note the ambiguity as a finding: state what the formatting implies should be included, what the Excel actually sums, and that the preparer should confirm whether the presentation is consistent with the intended calculation. If the same formatting convention is used elsewhere in the document to mean something different than how it is used here, that inconsistency is itself a finding regardless of whether the math is correct.

### Column mapping procedure (required for any statement with three or more data columns):

Before performing any arithmetic on a statement with three or more data columns, explicitly write out the column map in this format:

*Column 1: [Header name] | Column 2: [Header name] | ... | Column N: [Total column header]*

*Confirmed against: Excel tab **"**[tab name]**"*

Then state which columns are intended to sum to which totals — horizontally across rows and vertically down columns — before calculating anything. Do not perform arithmetic until this mapping is written out and confirmed against the Excel.

### Rounding — zero tolerance:

Every column in the printed document must foot to the printed total exactly as a reader would verify on a 10-key. A difference of any amount — including $1 — is a finding. If the Excel shows that figures are stored with decimal precision and displayed as rounded integers, note this as the likely cause and flag it for the preparer to resolve by adjusting one displayed line item to force the printed figures to foot. Rounding is an explanation, not an excuse. Flag it regardless. If a column does not foot and the difference cannot be explained by rounding, note that hidden rows in the Excel workbook may account for the discrepancy — flag this for the preparer to verify.

### PDF extraction caveat — when Excel is not provided:

When the Excel workbook has NOT been provided and a math finding arises on a statement with three or more data columns, the finding MAY be an artifact of PDF extraction rather than a real error in the document. PDF text extraction can flatten table layouts, misattribute figures to adjacent columns, or drop values entirely — especially on dense multi-column combining schedules. Before flagging a multi-column math finding as a document error in this situation, do the following:

- Re-extract using layout-preserving methods (e.g., pdftotext -layout) and, where available, render the page to an image and visually confirm the figures in the affected rows and columns.

- If after visual confirmation the figures still do not foot, flag the finding — but include a note that it was confirmed visually and recommend the preparer verify against the Excel source.

- If visual confirmation cannot be performed or is inconclusive, flag the finding as POTENTIAL and add a standard note: "This finding arose on a multi-column statement; Excel source was not provided for column mapping verification. May reflect a PDF extraction limitation rather than an error in the document. Recommend providing the Excel workbook to confirm." Do NOT report a potential-extraction finding with the same certainty as a verified finding.

- This caveat applies ONLY to statements with three or more data columns and ONLY when Excel was not provided. Findings on two-column statements, single-column schedules, note disclosures, and cross-references are not subject to this caveat and should be flagged normally.

## Math Check Procedures

**NOTE:** *The underlying schedules were prepared in Excel. Do not assume subtotals are correct. Hidden rows, rounding errors, or formula errors may cause presented totals to differ from the actual sum of visible line items. Recalculate everything from individual line items.*

### Foot every column:

- Add every number in every column of every financial statement, schedule, and table.

- Confirm the sum equals the subtotal or total presented. Do not rely on the printed total — recalculate independently.

### Cross-foot every row:

- Confirm that each row total equals the sum of the columns that are intended to sum across.

- In combining statements, government-wide statements, and multi-fund schedules, confirm all columns add correctly across each row and down each column.

### Subtotals and totals at every level:

- Where totals are built from subtotals, verify each subtotal independently, then verify the total as the sum of the subtotals.

### Budget vs. Actual Schedules:

- Confirm variance columns are correctly calculated (actual minus budget, or budget minus actual — consistently applied).

- Confirm beginning and ending fund balances in budgetary statements tie to other statements.

### Debt Schedules:

- Foot all maturity schedules. Confirm totals agree to the applicable note disclosure and to the face of the financial statements.

### Pension / OPEB Schedules:

- Foot all RSI schedules. Confirm calculated amounts are internally consistent.

### SEFA:

- Foot total federal expenditures by program and in aggregate.

### SFQC (if applicable):

- Confirm questioned cost amounts are internally consistent within the schedule and with references in the auditor's report.

**NOTE:** *Flag every instance where a figure does not recalculate correctly, with the location, the presented figure, and the recalculated figure.*

# STEP 4 — CROSS-REFERENCE AND CONSISTENCY CHECK

Identify every number that appears in more than one location in the document and confirm all instances agree. At minimum, check:

## Fund Balances / Net Position

- Confirm ending balances on the balance sheet / statement of net position agree to: the statement of changes in fund balance / statement of activities, any combining statements, MD&A narrative (if applicable), and any footnote references.

## Revenue and Expenditure Totals

- Confirm totals on the face of statements agree to any combining statements and any narrative references in MD&A.

## Depreciation

- If a statement of cash flows is present, confirm depreciation per the statement of activities agrees to depreciation as a reconciling item on the statement of cash flows.

## Long-Term Debt

- Confirm the total outstanding balance per the debt footnote agrees to the face of the financial statements.

- Confirm the current portion of long-term debt on the balance sheet agrees to the amount maturing in the next year per the maturity schedule in the footnotes.

## Capital Assets

- Confirm beginning balances, additions, disposals, and ending balances in the capital assets note roll-forward are internally consistent.

- Confirm ending net capital asset balance agrees to the face of the statements.

## Pension and OPEB

- Confirm net pension liability / net OPEB liability balances per the notes agree to the face of the financial statements.

- Confirm deferred inflows and outflows per the notes agree to the statement of net position.

## Cash and Investments

- Confirm total cash and investments per the cash and investments note agrees to cash balances on the face of the financial statements.

## Receivables and Payables

- Confirm any detail schedules of receivables or payables agree to the face of the financial statements.

## Budget

- Confirm original and final budget amounts on the budgetary comparison schedule agree to any narrative references and to any separate budget disclosure in footnotes.

## Federal Expenditures

- Confirm total federal expenditures on the SEFA (if applicable) are consistent with any reference to total federal expenditures in the auditor's reports or notes.

## Prior Year Figures

- Confirm prior year comparative figures (if presented) are internally consistent with each other throughout the document.

- Where prior year audited statements are available for reference, confirm comparative figures agree.

- Confirm beginning balances agree to prior year ending audited balances. Flag any that cannot be confirmed without the prior year report.

## Footnote Figures

- Confirm every figure cited in the footnotes agrees to the corresponding line item on the face of the financial statements.

- Confirm all cross-references between footnotes are accurate.

**NOTE:** *Identify any other figure appearing in multiple locations and confirm consistency. Flag every discrepancy with location, expected figure, and actual figure found.*

## Paired-Account Relationship Analysis

Beyond checking the plausibility of individual balances, assess whether accounts that logically travel together are in fact both present, both absent, or in a sensible proportion. Many disclosure omissions and classification errors surface through what is missing rather than what is wrong on its face. Work through the following paired-relationship checks. For each pair, the rule is the same: if one account is present at a material level, the other should also be present (or its absence explained). If both are present, assess whether their relationship is plausible.

The list below is representative, not exhaustive. Apply experienced reviewer judgment to identify other paired relationships not listed here.

### Operations and expenses

- **Salaries and wages → payroll tax expense and accrued payroll taxes.** Compensation of any meaningful size should be accompanied by payroll tax expense (employer FICA, Medicare) and typically an accrued payroll tax liability at period end. Compensation with no payroll tax expense is a flag. Payroll tax expense implausibly low relative to compensation is a flag. Note: governmental employees may be covered by Social Security or by a qualified retirement system in lieu of Social Security (Section 218 agreements, mandatory coverage, etc.) — confirm treatment is consistent with stated policy.

- **Salaries and wages → pension contribution expense and OPEB expense.** Governmental employees are typically covered by defined benefit pension plans and often have OPEB benefits. Material payroll with no pension or OPEB expense disclosure is a flag.

- **Salaries and wages → compensated absences liability.** Governmental entities with employees typically accrue compensated absences (vacation, sick) under GASB 101 (or legacy GASB 16). Flag absence.

- **Contract labor → absence of payroll tax on that amount.** Confirm contract labor is classified separately from employee compensation.

- **Charges for services → cost of providing those services.** Program revenue with no corresponding direct cost warrants confirmation.

- **Proprietary fund operations → operating vs. non-operating classification.** Confirm classification is consistent with disclosed policy.

### Capital assets

- **Land → buildings and/or infrastructure.** Land by itself without buildings or infrastructure is unusual for an operating government (possible for land banks, conservation holdings — confirm). Buildings without land is unusual except for leased-ground structures.

- **Buildings / equipment / vehicles / infrastructure → depreciation expense and accumulated depreciation.** Any depreciable asset class on the government-wide statements or proprietary funds should have corresponding depreciation expense and accumulated depreciation. Gross capital assets with zero depreciation is a flag (unless using the modified approach for infrastructure, which must be disclosed).

- **Vehicles → fuel / maintenance / vehicle-related expenditures.** Governmental fleets generate ongoing operating expenditures; flag absence relative to vehicle holdings.

- **Construction in progress → absence of depreciation on CIP.** CIP should not be depreciated.

- **Infrastructure assets → either depreciation OR modified approach disclosures.** If the modified approach is used, confirm required disclosures (condition assessments, estimated vs. actual preservation costs).

### Debt and financing

- **Bonds payable / notes payable / lease obligations → interest expense.** Interest-bearing debt should generate interest expense on government-wide statements and proprietary funds (and debt service expenditures in governmental funds). Flag debt with no corresponding interest.

- **Long-term debt → current portion.** Long-term debt with zero current portion is a flag unless the maturity schedule confirms no principal due in the next year.

- **Debt service fund activity → debt principal and interest on debt note.** Amounts paid from a debt service fund should correspond to debt activity in the note.

- **Interest expense → interest payable / accrued interest.** Material interest typically has some accrual at period end.

- **Conduit debt obligations → disclosure (GASB 91).** If the entity issues conduit debt, confirm required disclosures.

### Leases (GASB 87) and SBITAs (GASB 96)

- **Lease expense / expenditure → right-to-use lease asset and lease liability.** Under GASB 87, meaningful lease activity implies both a right-to-use asset and lease liability (unless all leases are short-term under 12 months).

- **SBITA expense → subscription asset and subscription liability under GASB 96.**

- **Leased real estate described in operations → corresponding GASB 87 recognition.**

### Receivables and revenue

- **Property tax receivable → property tax revenue.** Governmental funds with property tax levies should have both receivable and revenue.

- **Grants receivable → grant revenue (and unearned revenue / deferred inflow for grants where eligibility has not been met).**

- **Charges for services → corresponding receivables where billing and collection are not simultaneous.**

### Federal grants and Single Audit

- **Federal grant revenue → SEFA entry.** Federal grant revenue should correspond to entries on the SEFA.

- **Federal expenditures at Single Audit threshold → Single Audit reports.** If federal expenditures meet or exceed the Single Audit threshold ($750,000 / $1,000,000 per 2024 UG revisions), confirm Single Audit reports are present.

- **Subrecipient payments → SEFA disclosure of pass-through amounts.**

- **Indirect cost recovery → indirect cost rate disclosure.**

### Payables and accruals

- **Accounts payable → corresponding expenditure activity.**

- **Accrued compensation → salaries and wages.**

- **Retainage payable → construction expenditures / CIP.**

### Fund balance and net position

- **Restricted fund balance → legal or contractual restriction disclosure.** Restricted fund balance categories must correspond to disclosed restrictions (bond covenants, grantor restrictions, enabling legislation).

- **Committed fund balance → formal action of the government's highest level of decision-making authority.** Confirm disclosed.

- **Assigned fund balance → policy regarding who has authority to assign.** Confirm disclosed.

- **Net position components → restricted net position must be explained; unrestricted net position may be negative (deficit); net investment in capital assets formula should be validatable.**

- **Transfers out (one fund) → transfers in (another fund).** Must net to zero in the total of all funds.

### Investments and cash

- **Investments → investment income and GASB 40/72 disclosures.** Material investments should produce interest/dividend/realized/unrealized gain activity and require deposit and investment risk disclosures.

- **Restricted cash → nature of restriction disclosure and corresponding restricted net position or liability.**

- **Pooled cash → participant fund allocations.**

### Pensions and OPEB (GASB 68, 73, 75)

- **Covered payroll disclosure → net pension liability / net OPEB liability.** Covered payroll drives pension and OPEB calculations; confirm consistency.

- **Net pension liability → pension expense, deferred inflows, deferred outflows.** All four elements typically appear together.

- **Net OPEB liability → OPEB expense, deferred inflows, deferred outflows.**

- **Cost-sharing plan → proportionate share disclosures under GASB 68/75.**

### Component units

- **Component unit described in notes → discrete or blended presentation on government-wide statements.** Described component units must be presented somewhere.

- **Blended component unit → funds within the primary government presentation.**

- **Component unit transactions with primary government → interentity receivables / payables and transfers.**

### Insurance and risk management (GASB 10)

- **Operating activity → general liability / workers' comp coverage.** Governments carry liability coverage through insurance, self-insurance, or risk pools; confirm disclosure.

- **Self-insurance program → claims liability and IBNR accrual.**

### Procedural guidance

For each relationship flagged:

- State what account is present and what the expected paired account would be

- State whether the paired account is absent, present but implausibly sized, or present and reasonable

- Classify as a disclosure / completeness question, a classification question, or a reasonableness question

- Note that the reviewer should confirm — many of these flags have legitimate explanations (Section 218 coverage alternatives, modified approach for infrastructure, newly formed entity, etc.). The objective is to surface the relationship for review, not to assert an error.

**NOTE:** *Apply this analysis in combination with the logical and contextual consistency checks below. A finding may appear in either or both sections; flag it once with a cross-reference.*

## Logical and Contextual Consistency

Beyond verifying that figures tie to their counterparts, assess whether the financial statements make logical and contextual sense as a whole. This step is not about mathematical agreement but about whether numbers, disclosures, and narrative are internally coherent and plausible given the entity's described circumstances. Flag anything that a knowledgeable reader would find implausible, inconsistent, or unexplained. Examples of issues to identify include, but are not limited to:

- Cash and bank balance reasonableness — where a footnote discloses bank balances (e.g., for collateralization or FDIC coverage purposes) and the financial statements present a reconciled cash balance, the two figures are not expected to agree; however, they should be in a plausible relationship. A bank balance that is materially higher than the reconciled book balance (e.g., bank balance of $20 million against a reconciled cash balance of $10 million) warrants a flag for the preparer to confirm the relationship is explained and reasonable — unreconciled items of that magnitude are unusual without explanation. Apply similar scrutiny to any footnote disclosure of a gross figure that appears implausibly disproportionate to the related statement balance.

- Revenue and expenditure plausibility — assess whether revenues and expenditures are reasonable for the entity type, size, and programs described. Flag significant revenues with no corresponding program disclosure, or major program expenditures with no corresponding revenue source.

- Debt and obligation plausibility — assess whether disclosed debt balances, interest rates, and maturity schedules are mutually consistent and plausible. Flag interest rates that appear anachronistic for the type or vintage of debt disclosed, or maturity concentrations that appear inconsistent with the described debt instruments.

- Fund balance and net position consistency with narrative — if the MD&A or other narrative describes a deficit, surplus, or significant change, confirm that the described condition is reflected in the financial statements. Flag any material discrepancy between narrative claims and presented results.

- Footnote disclosures that contradict statement presentations — flag any footnote that describes an accounting treatment, balance, or condition that appears inconsistent with how the related items are presented on the face of the statements, even if no individual figure fails to tie.

- Capital asset activity reasonableness — assess whether additions, disposals, and depreciation amounts are plausible given the entity's disclosed asset base, useful life policies, and any capital project disclosures. Flag depreciation that appears implausibly high or low relative to the gross asset balance and stated useful lives.

- Pension and OPEB obligation reasonableness — assess whether the net pension liability or net OPEB liability is plausible relative to the entity's workforce size, disclosed plan participation, and the plan's funded status. Flag any situation where the liability appears disproportionately large or small without explanation.

- Federal expenditures and program scope plausibility — assess whether SEFA expenditures are plausible given the entity type and described programs. Flag federal expenditures that appear implausibly large or small for the program type, or programs whose described scope is inconsistent with the magnitude of expenditures reported.

- General implausibility — apply experienced reviewer judgment to flag any balance, ratio, trend, or disclosure that, while potentially mathematically consistent, would strike a knowledgeable reader as unusual, unexplained, or inconsistent with the entity's described operations, size, or circumstances.

# STEP 5 — GAAP/GASB DISCLOSURE AND TECHNICAL REVIEW

Perform a full technical review for compliance with applicable financial reporting standards:

## GASB Standards Applicable to Entity Type

- Identify applicable GASB standards for the entity type and confirm the financial statements are presented in accordance with those standards, including but not limited to:

- Government-wide vs. fund-level reporting (GASB 34 and subsequent)

- Measurement focus and basis of accounting (accrual for government-wide; modified accrual for governmental funds; accrual for proprietary and fiduciary funds)

- Fund types used are appropriate and correctly classified

- Proprietary fund statement presentation (statement of net position, revenues expenses and changes in net position, statement of cash flows using the direct method)

- Required reconciliations between fund financial statements and government-wide statements are present and appear complete

- Fiduciary fund presentation if applicable

## GASB Standards — Effective Date Review

- Identify the fiscal year end date of the financial statements.

- List all GASB statements that became effective for periods beginning on or before that fiscal year end. For each, assess whether it is applicable to the entity type and, if so, confirm that the financial statements reflect adoption.

- Do not rely on management's boilerplate disclosure that no new standards have a significant impact — evaluate each standard independently based on the entity's presented balances and disclosures.

- Flag any standard that appears applicable and shows no evidence of adoption or disclosure.

- If the report is being issued significantly after the fiscal year end, also note any GASB standards that became effective in the intervening period and assess whether they should have been adopted prior to issuance.

## Completeness of Financial Statements

- Before confirming completeness, perform the following identification and inference procedure. Do not assume a fixed template — derive the expected statement package from the document itself.

### Step 1 — Identify the entity's reporting model

Review the auditor's report opinion paragraph, the summary of significant accounting policies, the entity description, and the table of contents to determine which of the following reporting components apply to this entity:

- Government-wide reporting — required for all general-purpose governments reporting under GASB 34. Indicators: the entity is described as a city, county, town, village, school district, state agency, special district, or similar; the SSAP references government-wide and fund financial statements; the auditor's opinion references government-wide statements.

- Governmental fund reporting — required where governmental activities exist. Indicators: general fund is referenced; property tax or intergovernmental revenue is reported; fund balance (not net position) language appears.

- Proprietary fund reporting — required where enterprise or internal service funds exist. Indicators: utility, water, sewer, electric, transit, airport, or similar operations are described; charges for services revenue is significant; the SSAP references proprietary funds or business-type activities.

- Fiduciary fund reporting — required where pension trust, investment trust, private-purpose trust, or custodial funds exist. Indicators: a pension or OPEB trust is administered by the entity; the entity holds assets for others; agency or custodial fund activity is disclosed in the notes.

- Component units — required where legally separate entities meeting the criteria of GASB 61 exist. Indicators: a development authority, housing authority, foundation, or similar entity is described in the notes as a component unit; the SSAP addresses component unit inclusion or exclusion.

### Step 2 — Confirm required statements are present

Based on the reporting components identified in Step 1, confirm that all of the following applicable statements are present in the document. Flag any that are absent and identify whether the absence appears to be an omission or whether the document provides a reasonable explanation:

- Government-wide statements (if applicable): Statement of Net Position; Statement of Activities. Both are required if government-wide reporting applies. The absence of either when government-wide reporting is indicated by the notes, SSAP, or auditor's report is a significant finding.

- Governmental fund statements (if applicable): Balance Sheet — Governmental Funds; Statement of Revenues, Expenditures, and Changes in Fund Balances — Governmental Funds. Required reconciliations to government-wide statements must also be present.

- Budgetary comparison (if applicable): a budgetary comparison schedule or statement for the general fund and each major special revenue fund with a legally adopted annual budget. May appear as RSI or as a basic statement depending on the entity's accounting policy; confirm presentation is consistent with the SSAP disclosure.

- Proprietary fund statements (if applicable): Statement of Net Position — Proprietary Funds; Statement of Revenues, Expenses, and Changes in Fund Net Position — Proprietary Funds; Statement of Cash Flows — Proprietary Funds (direct method required). All three are required when enterprise or internal service funds exist.

- Fiduciary fund statements (if applicable): Statement of Fiduciary Net Position; Statement of Changes in Fiduciary Net Position. Required when pension trust, investment trust, private-purpose trust, or custodial funds exist. Note: custodial funds present a Statement of Changes in Assets and Liabilities rather than a Statement of Changes in Fiduciary Net Position under GASB 84 — confirm the correct format is used.

- Combining statements (if applicable): where nonmajor funds exist, combining statements are typically required as supplementary information to present individual fund detail. Confirm combining statements are present for all nonmajor governmental funds, all nonmajor enterprise funds, all internal service funds, and all fiduciary funds — if any such funds are referenced in the notes or individual fund schedules but no combining statement is presented, flag as a potential omission.

### Step 3 — Cross-check statements against all document references

Confirm that the statements present in the document are consistent with all references to statements throughout the document. Specifically:

- The auditor's opinion paragraph cites specific statement titles — confirm every cited statement is physically present in the document with a matching title. Flag any cited statement that cannot be located.

- The SSAP describes fund types or activity categories (e.g., "the City maintains enterprise funds for water and sewer operations") — confirm that corresponding statements are present. A description of activity in the notes without a corresponding statement is a potential omission.

- The MD&A (if present) describes financial statement components — confirm every component described is presented. A component discussed in the MD&A but absent from the statements is a significant finding.

- Reconciliations between fund and government-wide statements — if government-wide statements are present, confirm that the required reconciliations (balance sheet to statement of net position; statement of revenues, expenditures, and changes in fund balances to statement of activities) are also present. Missing reconciliations when government-wide statements exist is a finding.

## Required Footnote Disclosures

Confirm the footnotes include all required disclosures for every balance and transaction type presented, including at minimum:

- Summary of Significant Accounting Policies (SSAP) — confirm it addresses: basis of presentation, measurement focus, basis of accounting, budget basis, cash and investments policy, receivables, capital assets policies and useful lives, long-term debt policies, compensated absences, pension/OPEB, fund balance/net position classifications, and any other significant policies

- Cash and investments — confirm compliance with GASB 40 (deposit and investment risk disclosures) and GASB 72 (fair value) as applicable

- Receivables — any significant receivables disclosed

- Capital assets — roll-forward schedule, depreciation methods and useful lives

- Long-term debt — complete roll-forward, maturity schedule, interest rates, covenant disclosures if applicable

- Pension — full GASB 68 disclosures (or GASB 73 if not in a qualifying plan)

- OPEB — full GASB 75 disclosures if applicable

- Interfund transactions — receivables/payables and transfers disclosed and explained

- Fund balance classification details (GASB 54) if applicable

- Net position components — restricted amounts should be explained

- Commitments and contingencies

- Subsequent events — confirm a subsequent events note is present and complete through an appropriate date

- Risk management disclosures if applicable

- Leases — GASB 87 disclosures if applicable; if equipment or vehicle lease expenditures are present but no lease note exists, flag for preparer to confirm all leases qualify for the short-term exemption or prepare required disclosures

- Any other disclosures required for balances or transactions present in the financial statements

## Accounting Policy Changes

- Review accounting policies disclosed in the current year SSAP against those in the prior year report if available.

- Flag any policy that appears to have been added, removed, or modified without disclosure of a change in accounting principle.

- If a new standard adoption appears to explain the change, confirm that the adoption is explicitly disclosed.

## Going Concern Indicators — Document-Based Assessment

Review the financial statements and footnotes for indicators that would typically trigger a going concern evaluation. You cannot conclude on whether a going concern paragraph is required — flag the following if present and note that the engagement team should confirm the evaluation was performed:

- Fund deficits or negative net position of material size

- Disclosure of plans to recover deficits through future transfers, rate negotiations, or other mechanisms that depend on future events

- Footnote language about significant litigation, contingent liabilities, or loss contingencies described as other than remote

- Significant reliance on a single revenue source with no disclosure of renewal status

- Debt covenant disclosures or maturity concentrations that appear to create near-term liquidity pressure

- Any management disclosure explicitly referencing financial difficulty or recovery plans

## Accounting Standards — General

- Review all presented balances and transactions for apparent conformity with GAAP/GASB.

- Flag any amounts or presentations that appear to deviate from applicable standards, including unusual classifications, balances inconsistent with disclosed accounting policies, or presentations that differ from standard practice for the entity type.

## Going Concern and Subsequent Events

- Confirm a subsequent events note is present and appears complete through an appropriate date.

- If the report is issued significantly after year-end, flag the extended subsequent events window and note that the evaluation period is unusually long.

## Yellow Book Technical Requirements (if applicable)

- Confirm compliance with GAGAS reporting requirements, including independence, required communications, and finding format requirements.

## Single Audit Technical Requirements (if applicable)

- Confirm compliance with 2 CFR Part 200 Subpart F requirements, including SEFA presentation, finding format, and required reports.

# STEP 6 — FINAL PROOF CHECKLIST

Apply the judgment of an experienced governmental audit preparer performing a final proof. The goal is to surface document-level issues a preparer would want to resolve before handing off to QC, not to conclude on engagement quality, firm risk, or release readiness.

## Internal Consistency of Narrative

- Does the MD&A narrative (if present) accurately describe the financial results shown in the statements?

- Are any narrative claims inconsistent with the numbers?

## Opinion Appropriateness

- Given the complete contents of the document, does the opinion type appear appropriate?

- Are there any matters disclosed in the footnotes or supplementary information that would appear to require modification of an opinion that is currently unmodified?

## Finding Consistency

- If findings are present in the SFQC, are they fully and consistently reflected throughout all auditor reports?

- Is the language in each finding professionally written and complete?

## Sensitive Disclosures

- Are there any disclosures that appear legally or politically sensitive that should be reviewed by engagement leadership before release?

## Cover Page and Transmittal

- If a transmittal letter or cover page is present, confirm it is addressed correctly, dated correctly, and signed or attributed appropriately.

## Statistical Section (if an ACFR)

- Confirm required tables and ten-year trend data are present and appear complete.

- Confirm figures in the statistical section that appear elsewhere in the document are consistent.

# STEP 7 — OUTPUT FORMAT

After completing all review steps, produce a structured Excel report with the following tabs. Apply the formatting rules described in the AI Behavior and Output Formatting section at the top of this prompt (no fills, no borders except section-heading underlines, no merged cells, three plain header cells upper-left, no Purpose/Procedure scaffolding, no release-readiness language).

## Tab 1 — Executive Summary

- All findings compiled in a single table, sorted by severity: Critical, Significant, Moderate, Minor

- A summary at the top showing only the count of findings by severity (Critical / Significant / Moderate / Minor). Do NOT include any release-readiness language, engagement-risk language, or overall assessment.

- Each finding row includes: Finding ID, Step, Category, Severity, Location in document, Description, Recommended Correction. Do not include Reviewer Notes, Management Response, or Resolved columns — this is a report, not a workpaper.

- This tab is self-contained — a reader should be able to find every issue without jumping to the detail tabs.

## Tab 2 — Proof Review

- All Step 1 procedures listed line by line with Pass / Fail / Flag result and notes

## Tab 3 — Report Language

- All Step 2 procedures organized by report, with Pass / Fail / Flag result and notes

## Tab 4 — Math Check

- All Step 3 procedures with per-document figure, recalculated figure, difference, and result

- Multi-column statements include the column map at the top of each section

- Provisional results clearly labeled where Excel was not available

## Tab 5 — Cross-Reference

- All Step 4 procedures with location 1, location 2, value, and result

- Include a sub-section for paired-account relationship findings

- Include a sub-section for logical and contextual consistency findings

## Tab 6 — GAAP/GASB Review

- All Step 5 procedures organized by standard/requirement with Pass / Fail / Flag result and notes

## Tab 7 — Final Proof Checklist

- All Step 6 items with result, finding reference, and notes. No blank manual-entry columns.

**NOTE:** *Severity classification throughout: Critical, Significant, Moderate, Minor. Use these labels consistently in all tabs.*

**NOTE:** *Present all findings organized by step in the detail tabs. For each issue, note: location in the document, description of the issue, and recommended correction. The Executive Summary tab should be self-contained enough that a reader can see every issue without needing to open the detail tabs.*

*— End of Prompt —*
