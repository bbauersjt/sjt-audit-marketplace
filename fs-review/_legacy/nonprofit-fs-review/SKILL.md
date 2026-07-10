---
name: nonprofit-fs-review
description: Comprehensive technical proof and review of a nonprofit / not-for-profit financial statement package — 501(c)(3) public charities, private foundations, 501(c)(4)/(6) and other exempt orgs, religious organizations, educational institutions, healthcare nonprofits, social service agencies, foundations, associations under U.S. GAAP (FASB/ASC 958). Use this skill WHENEVER the user uploads or references a nonprofit financial statement or audit report and asks for a review, proof, technical review, QC check, math check, cross-reference check, or disclosure review. Trigger even if the user does not say "skill" — nonprofit financials plus any review-style ask should activate it. Also trigger on ASC 958 review, SAS 134+ auditor's report review, net asset classification, functional expense, contributions/grants/contributed services, endowment or UPMIFA review, Single Audit on nonprofits. Do NOT use for governmental entities, commercial for-profits, tax returns, or bookkeeping.
---

# Nonprofit Financial Statement Technical Review

**NONPROFIT FINANCIAL STATEMENT TECHNICAL REVIEW**

*AI Review Prompt — Quality Control Procedures*

Version 1.0  |  For use with Claude or equivalent LLM

**PURPOSE:** This document is a structured prompt instructing an AI model to perform a comprehensive technical proof and review of a nonprofit / not-for-profit organization financial statement package (entities reporting under U.S. GAAP, with ASC 958 as the primary industry-specific framework). The output is intended to assist a preparer in locating issues in the financial statements — either after a first pass or as a final proof before turning the package over to QC. It is not a substitute for human quality control; actual QC is performed by qualified personnel. This prompt focuses on the document itself and what is wrong with it. Paste this prompt into the AI, then provide or attach the financial statements for review. The AI will request additional supporting documents before beginning, adapt its procedures based on entity type and engagement type, and issue warnings where supporting documents are absent.

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

*"**Before I begin the review, I need additional documents to perform the most complete and accurate analysis:*

*1. Excel source workbook — the underlying Excel file used to prepare the financial statements. This is needed to correctly map column layout in statements with three or more data columns — particularly the statement of activities (often split by net asset class with a total column) and the statement of functional expenses (program services, supporting services, total) — where PDF text extraction can flatten the table structure and cause figures to be misattributed to the wrong column. Without the Excel file, math check results on any statement with three or more columns should be treated as provisional.*

*2. Prior year audited financial statements — the issued financial statements for the preceding fiscal year. This is needed to agree beginning net asset balances (without donor restrictions, with donor restrictions), verify prior year comparative figures, check for reclassifications, assess accounting policy consistency, and confirm proper auditor change language if the engagement changed hands.*

*3. If a Single Audit was performed (federal expenditures of $750,000 or more — $1,000,000 for fiscal years beginning on or after October 1, 2024): the Schedule of Expenditures of Federal Awards (SEFA), Schedule of Findings and Questioned Costs (SFQC), and any Summary Schedule of Prior Audit Findings and Corrective Action Plan if not already included in the package.*

*Please provide whichever of these you have available. If any is unavailable, let me know and I will note the limitations and proceed accordingly.**"*

*Important note on file uploads: Claude processes uploaded PDFs and images as vision inputs, and each page of a document consumes image capacity from the conversation's available limit. If you upload the financial statements, the prior year report, and the Excel workbook as separate files, a large package can exhaust that capacity before the review is complete. To avoid this, it is strongly recommended that you combine all files into a single .zip archive and upload the zip rather than uploading files individually. Claude can extract and work with files from a zip archive without the same per-page image consumption.**"*

Wait for a response before proceeding.

## Step 0B — Verify Documents Received

### Excel workbook verification:

- Confirm the workbook relates to the same entity and fiscal year as the financial statements — check entity name, fiscal year end, and whether sheet names correspond to statements present in the PDF

- Confirm the workbook contains tabs relevant to the statements being reviewed (particularly statement of activities by net asset class and statement of functional expenses)

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

**⚠ WARNING:** *EXCEL WORKBOOK NOT PROVIDED: Math checks on financial statements with three or more data columns are subject to column attribution error. Common multi-column nonprofit statements affected include the statement of activities (without donor restrictions / with donor restrictions / total) and the statement of functional expenses (program services columns / supporting services columns / total). PDF text extraction can flatten table layouts in these statements, making it unreliable to confirm which figures belong to which columns. Math check results on the following statements (three or more columns) should be treated as provisional and independently verified by the reviewer: [list all statements present with three or more data columns]. All other procedures are unaffected.*

Then proceed with the review, noting "PROVISIONAL — Excel not provided" on any math check result involving a statement with three or more data columns.

### If the prior year financial statements were not provided:

Ask the following before proceeding:

*"**Prior year financial statements were not provided. Before I proceed, can you tell me: Is this a first-year or first-time audit engagement — i.e., no prior year audited financials exist? Or are prior year audited financials available but not provided at this time?**"*

### If first-year audit or no prior audited financials exist:

- Note this and do not flag missing prior year tie-outs as findings

- Note that beginning net asset balances cannot be agreed to a prior audited report as none exists — expected for a first-year engagement

- Review opening balance disclosures and any predecessor auditor, compilation, or review report language that may be present

- Confirm the auditor's report includes appropriate language under AU-C 510 for opening balances in initial audit engagements

- Proceed with all other procedures normally

### If prior year financials exist but were not provided:

**⚠ WARNING:** *PRIOR YEAR FINANCIALS NOT PROVIDED: The following procedures cannot be completed and should be treated as incomplete pending receipt of the prior year report: beginning net asset tie-out (without donor restrictions, with donor restrictions); prior year comparative figure verification; accounting policy consistency check; reclassification disclosure verification; auditor change / predecessor reference verification. All other procedures will execute normally.*

Proceed with the review, noting "INCOMPLETE — Prior year report not provided" on any procedure that cannot be performed.

# PRELIMINARY: IDENTIFY ENTITY TYPE AND ENGAGEMENT

Before any other procedures, perform the following identification steps:

- Identify the nonprofit entity type and subtype. Consider: 501(c)(3) public charity, 501(c)(3) private foundation, 501(c)(3) private operating foundation, 501(c)(4) social welfare, 501(c)(6) business league/trade association, 501(c)(7) social club, religious organization, educational institution (college/university/school), healthcare nonprofit (hospital, clinic, senior living), social service agency, arts/cultural organization, foundation (community, independent, corporate), associations, or other exempt classification. Note the legal form (nonprofit corporation, trust, unincorporated association) as this affects governance disclosures.

- Confirm the reporting framework. Confirm U.S. GAAP (FASB Accounting Standards Codification), with ASC 958 (Not-for-Profit Entities) as the primary industry-specific guidance. If any other framework appears (tax basis, cash basis, modified cash, contractual basis, IFRS), flag this — the current review procedures are scoped to GAAP.

- Confirm the engagement type. Confirm it is an audit (SAS-based reporting). If the document appears to be a review (SSARS AR-C 90), compilation (AR-C 80), or preparation engagement (AR-C 70), flag this — the report language procedures in Step 2 are scoped to audit reports.

- Determine whether a Single Audit (2 CFR Part 200 / Uniform Guidance) has been performed. Look for: Schedule of Expenditures of Federal Awards (SEFA), Schedule of Findings and Questioned Costs (SFQC), Summary Schedule of Prior Audit Findings, auditor's reports on compliance for each major program and on internal control over compliance. The Single Audit trigger is federal expenditures of $750,000 or more (or $1,000,000 for fiscal years beginning on or after October 1, 2024 per the 2024 Uniform Guidance revisions).

- Determine whether a Yellow Book (GAGAS) audit has been performed even absent a Single Audit. Yellow Book may be required by state law, funder requirements, or organizational charter even without federal funding.

- Identify whether the financial statements are consolidated, combined, or standalone:
  - Consolidated — nonprofit with controlled entities (subsidiaries, controlled foundations, affiliates under ASC 958-810)
  - Combined — affiliated nonprofits presented together without control relationship (permitted under ASC 958-810 in limited circumstances)
  - Standalone — single legal entity

- Identify any controlled for-profit subsidiaries or related foundations, and note whether consolidation/inclusion appears appropriate.

- Identify whether the entity has an endowment and is subject to UPMIFA (Uniform Prudent Management of Institutional Funds Act) requirements — nearly all states have adopted UPMIFA.

**NOTE:** *All subsequent steps should be adapted to the identified entity type, net asset structure, and whether Single Audit / Yellow Book procedures apply.*

# STEP 1 — FULL PROOF

Perform a comprehensive proofread of the entire document:

## Table of Contents vs. Actual Document

- Confirm every item listed in the TOC exists in the document with a matching title and matching page number. Flag any discrepancy.

## Page Numbers

- Confirm page numbers are sequential, correctly formatted, and consistent in style throughout.

## Report Titles

- Confirm every report and statement heading in the document exactly matches the TOC entry, including capitalization and punctuation.

## Page Breaks

- Confirm there are no awkward or missing page breaks — statements should not be split mid-table unless unavoidable, and no orphaned headings should appear at the bottom of a page. The statement of functional expenses frequently spans multiple pages; confirm continuation headers and column headers repeat appropriately.

## Spelling and Grammar

- Flag all spelling errors, grammatical errors, and typographical mistakes.

## Footnote Sequencing and Continuation Headers

- Identify the footnote numbering scheme used (numeric: 1, 2, 3; alphabetic: A, B, C; or mixed). Confirm notes are numbered sequentially without gaps, duplicates, or out-of-order entries. Flag any skipped number/letter, any repeated number/letter, and any note that appears out of sequence.

- Confirm every footnote cross-reference within the document (e.g., "see Note 5", "as described in Note 11") points to a note that exists and covers the content implied by the reference. Flag any reference to a note that does not exist or does not address the topic referenced.

- For multi-page notes, check "continued" headers at the top of each continuation page. The continuation header must cite the correct note number/letter being continued. Flag: (a) missing continuation header where a note spans pages; (b) continuation header citing the wrong note number; (c) continuation header present but the prior page's note actually ended on that page.

- Apply the same sequencing and continuation checks to finding numbers in the Schedule of Findings and Questioned Costs (if a Single Audit is present), subheadings within a note, and continuation headers on multi-page schedules (e.g., "Statement of Functional Expenses — continued").

## Consistency of Language

- Flag any inconsistency in how the entity, programs, affiliated entities, or accounts are named throughout the document.

- The entity should be referred to by a single consistent name (e.g., "the Organization", "the Foundation", "the Association"). Program names, fund names, and account titles must be consistent throughout all reports, statements, footnotes, and supplementary schedules.

- Confirm program names in the statement of functional expenses column headers match program descriptions in the notes or narrative sections.

## Consistency of Dates and Fiscal Year References

- All references to the fiscal year end date, the audit period, and prior year must be internally consistent. Flag any mismatched dates.

- Many nonprofits use June 30 or other non-calendar fiscal year ends; confirm date references throughout the document correspond to the stated fiscal year.

## Formatting Consistency

## Punctuation and Possessive Consistency

Check for consistent use of the following punctuation conventions throughout the entire document:

- Serial comma (Oxford comma) usage — determine whether the document uses or omits the serial comma and flag any inconsistency. Do not flag the choice itself, only departures from the chosen convention.

- Possessive form of "Auditor" — identify whether the document uses "Auditor's" or "Auditors'" and flag any inconsistency.

- Collective reference to the entity — confirm the entity is consistently referred to as "the Organization," "the Foundation," "the Association," or similar throughout.

- Terminology consistency under ASC 958: the current required terminology is "net assets without donor restrictions" and "net assets with donor restrictions" (ASU 2016-14, effective 2018). Flag any use of legacy terminology ("unrestricted net assets," "temporarily restricted net assets," "permanently restricted net assets") except where historical reference is appropriate.

- Flag any other punctuation convention where usage is inconsistent within the document.

Check for consistent use of all of the following:

- Fonts and font sizes across all sections

- Paragraph spacing and line spacing

- Indentation and table alignment

- Dollar sign placement (should appear at top of column and at totals)

- Underlines and double underlines on totals

- Thousands separators and decimal consistency

- Parentheses vs. minus signs for negative numbers

- Column header style and alignment

## Capitalization Conventions

- Confirm consistent capitalization of account titles, program names, and report titles.

## Widows and Orphans

- Flag single lines of text separated from their paragraph by a page break.

**NOTE:** *Flag anything else that would be identified during a professional proofread of a formally published financial document.*

# STEP 2 — REPORT LANGUAGE AND STANDARDS COMPLIANCE

Validate every audit report against current applicable standards. For a nonprofit audit, the following reports may be present:

- Independent Auditor's Report on the Financial Statements (GAAS / SAS)
- Report on Internal Control Over Financial Reporting and on Compliance and Other Matters (Yellow Book — if applicable)
- Report on Compliance for Each Major Federal Program and Report on Internal Control Over Compliance (Single Audit — if applicable)

## For Each Report — General Requirements

Apply the following to every audit report present before proceeding to report-specific checklists.

- Confirm the report is addressed to the correct party — typically the board of directors, board of trustees, or governing body. Flag if addressed to management only.

- Confirm the report is dated correctly — on or after the date sufficient appropriate evidence was obtained, and not preceding the financial statement date.

- Confirm the entity name in the report heading exactly matches the entity name used throughout the financial statements — including the exact legal form.

- Confirm the report language conforms to current standards: SAS No. 134 and subsequent SASs for the financial statement opinion; GAGAS 2018 Yellow Book (or current revision) for the Yellow Book report; 2 CFR Part 200 Subpart F for Single Audit reports.

- Confirm no paragraph is present that is not required or permitted under the applicable standard.

- Confirm internal cross-references within each report are accurate.

## Independent Auditor's Report — Required Paragraphs Under SAS 134+

Verify every required paragraph is present, in the correct order, and correctly worded. Work through the report sequentially.

### Required sections — verify each is present and correct

- Report title — must include the word "Independent."

- Addressee — confirm addressed to the board of directors, board of trustees, or governing equivalent.

- Opinion section — under SAS 134, the opinion paragraph appears near the beginning of the report. Confirm: (1) the section is labeled "Opinion"; (2) it identifies the entity; (3) it identifies the financial statements by title and date/period covered; (4) the opinion type is clearly stated; (5) the financial reporting framework is named (accounting principles generally accepted in the United States of America); (6) all financial statements cited are included in the opinion. Confirm every statement title cited exactly matches the printed title in the document.

- Basis for Opinion section — confirm it states: (1) the audit was conducted in accordance with GAAS (and, if applicable, Government Auditing Standards); (2) the auditor's responsibilities are described in a subsequent section; (3) the auditor is required to be independent and meet other ethical responsibilities; (4) the auditor believes audit evidence obtained is sufficient and appropriate.

- Basis for Qualified or Adverse Opinion or Disclaimer (conditionally required) — required if the opinion is other than unmodified. Confirm it precedes the Opinion section, clearly describes the matter, and quantifies the effect if practicable.

- Responsibilities of Management for the Financial Statements section — confirm it states management's responsibility for: (1) preparation and fair presentation per the applicable framework; (2) design, implementation, and maintenance of internal control; (3) evaluation of conditions that raise substantial doubt about the entity's ability to continue as a going concern within one year after the date the financial statements are available to be issued.

- Auditor's Responsibilities for the Audit of the Financial Statements section — confirm it states the objectives (reasonable assurance, free from material misstatement from fraud or error, issue an opinion), defines reasonable assurance, and describes the audit procedures: professional judgment and skepticism; risk identification and assessment; understanding of internal control; evaluation of policies and estimates; evaluation of presentation; conclusion on going concern; communication with those charged with governance.

- Substantial Doubt About the Entity's Ability to Continue as a Going Concern section (conditionally required, SAS 134/132) — if substantial doubt exists and management has disclosed it, confirm this section is present, references the going concern note, and states the opinion is not modified.

- Emphasis-of-Matter paragraph (conditionally required) — required when the auditor draws attention to a matter fundamental to understanding. Common nonprofit triggers: restatement of prior period; change in accounting principle; significant subsequent event; major change in operations or program services.

- Other-Matter paragraph (conditionally required) — common nonprofit instances: (1) supplementary information accompanying the basic statements (e.g., consolidating schedules, schedules of operating expenses, schedules of indirect cost calculations) — requires the standard SI paragraph; (2) other information (OI) included in a document containing audited financial statements — requires the standard OI paragraph under AU-C 720; (3) reference to predecessor auditor.

- Government Auditing Standards paragraph (conditionally required) — if the audit was conducted under both GAAS and GAGAS, confirm: (1) the Auditor's Responsibilities section states the audit was conducted in accordance with Government Auditing Standards; (2) the report contains the required other-matter paragraph referencing the separate Yellow Book report; (3) the title cited matches the actual Yellow Book report present.

- Supplementary Information paragraph (conditionally required) — if SI is presented, confirm it identifies the SI, states the purpose, states whether it was subjected to audit procedures applied to the basic statements, and states the conclusion.

- Other Information paragraph (conditionally required under AU-C 720) — if other information is included, confirm per AU-C 720 (revised) requirements.

- Signature, firm city and state, and report date — confirm all present.

### Paragraph / section order verification under SAS 134

- Confirm sections appear in the correct order: (1) Report title; (2) Addressee; (3) Opinion; (4) Basis for Opinion; (5) Substantial Doubt About Going Concern (if applicable); (6) Emphasis-of-Matter (if applicable); (7) Responsibilities of Management; (8) Auditor's Responsibilities; (9) Other-Matter / SI / OI (if applicable); (10) Signature, firm city/state, date. Flag any deviation — particularly legacy reports where the opinion appears at the end.

### No-extra-paragraphs check

- Flag any paragraph that does not correspond to a required, conditionally required, or explicitly permitted paragraph. Common erroneous additions: management representation language; scope limitations not reflected in the opinion; commentary on internal control that belongs only in the Yellow Book report.

## Report on Internal Control Over Financial Reporting and on Compliance and Other Matters (Yellow Book — if applicable)

If a Yellow Book audit was performed, this report is required. Verify every required paragraph is present, in the correct order, and correctly conditioned on whether findings were noted.

### Required paragraphs — verify each is present and correct

- Report title — confirm it identifies this as a report on internal control over financial reporting and on compliance and other matters.

- Addressee — confirm consistent with the financial statement opinion.

- Introductory / scope paragraph — confirm it: (1) references the financial statement audit; (2) identifies GAAS and GAGAS; (3) states the report does not constitute an audit of internal control or compliance and no opinion is expressed.

- Internal Control Over Financial Reporting section — confirm: (1) describes management's responsibility; (2) describes the auditor's consideration of internal control sufficient to plan the audit; (3) correctly uses the defined terms "material weakness" and "significant deficiency"; (4) is correctly conditioned — if deficiencies were noted, they must be described or referenced to the SFQC; if none, the standard no-findings language must be present.

- Compliance and Other Matters section — confirm: (1) states the auditor tested compliance with laws, regulations, contracts, and grant agreements (significant for nonprofits with grant funding); (2) states the audit does not provide a legal determination of compliance; (3) is correctly conditioned on findings.

- Purpose and limitations paragraph — confirm it states the report's purpose is solely to describe the scope of testing and is not suitable for any other purpose. Its omission is a common error.

- Reference to financial statement opinion — confirm the report references the related opinion and its date.

- Reference to SFQC (conditionally required) — if findings were noted, confirm the report references the SFQC by correct title and that the SFQC is present.

### Paragraph order verification and no-extra-paragraphs check

- Confirm paragraphs appear in order: (1) Title; (2) Addressee; (3) Introductory/scope; (4) Internal Control; (5) Compliance; (6) Purpose and limitations; (7) Signature and date.

- Flag any paragraph not corresponding to a required or permitted element under GAGAS.

## Report on Compliance for Each Major Federal Program and Report on Internal Control Over Compliance (Single Audit — if applicable)

If a Single Audit was performed under 2 CFR Part 200, this report is required. Verify required paragraphs, conditioning, and order.

### Required paragraphs — verify each is present and correct

- Report title — confirm it identifies this as a report on compliance for each major federal program and on internal control over compliance.

- Addressee.

- Opinion or disclaimer on compliance for each major federal program — confirm: (1) each major program is identified by name and Assistance Listing Number (ALN, formerly CFDA); (2) opinion type for each program is clearly stated; (3) if qualified or disclaimed, a Basis for Qualification paragraph precedes the relevant opinion. Confirm the list of major programs matches the SEFA exactly.

- Basis for Qualified or Disclaimer of Opinion (conditionally required).

- Management's Responsibility — confirm it describes responsibility for compliance with federal statutes, regulations, and award terms.

- Auditor's Responsibility — confirm it states: (1) responsibility to express an opinion on compliance; (2) the audit was conducted in accordance with GAAS, GAGAS, and 2 CFR Part 200; (3) those standards require obtaining reasonable assurance about whether noncompliance could have a direct and material effect on a major program.

- Internal Control Over Compliance section — confirm correct conditioning and use of "material weakness" and "significant deficiency" terminology.

- Purpose and limitations paragraph — confirm present.

- Dollar threshold for major program determination — confirm stated and correct for the entity's total federal expenditures per the SEFA.

- Low-risk auditee determination — confirm whether the report states the entity qualifies. If claimed, confirm the entity met all four criteria under 2 CFR §200.520.

- Reference to SFQC — confirm present.

### Paragraph order verification and no-extra-paragraphs check

- Confirm correct order per 2 CFR Part 200 Subpart F.

- Flag any paragraph not corresponding to a required or permitted element.

## Cross-Report Consistency

- Confirm all report dates are consistent.

- Confirm findings in the Yellow Book report are fully consistent with the Single Audit report and SFQC.

- Confirm the entity name, fiscal year, and financial statement titles are consistent across all reports.

- Confirm the Yellow Book other-matter paragraph in the financial statement opinion correctly cites the Yellow Book report title as it actually appears.

- Confirm the Single Audit report's list of major programs matches the SEFA exactly.

## SEFA (if applicable)

- Confirm required elements: federal grantor, pass-through grantor (if applicable), program name, Assistance Listing Number (ALN), pass-through entity identifying number, total expenditures, note on basis of presentation, indirect cost rate note (10% de minimis or negotiated rate per 2 CFR 200).

- Confirm total federal expenditures on the SEFA is consistent with the Single Audit threshold determination.

- For each award, confirm ALN format is correct (two-digit agency prefix, period, three-digit program number).

- Assess whether the program name is consistent with the actual program associated with the ALN — flag mismatches.

- Assess whether the federal agency listed is consistent with the ALN prefix — flag any combination where agency and ALN prefix do not correspond.

- For pass-through awards, assess whether the pass-through grantor is a plausible intermediary.

- Flag any ALN that does not appear to exist or corresponds to a materially different program.

- Confirm cluster identification per the current Compliance Supplement.

- Confirm subrecipient vs. contractor determination is disclosed if applicable, and amounts passed through to subrecipients are identified per 2 CFR 200.332.

## Schedule of Findings and Questioned Costs (if applicable)

- Confirm all findings from the Yellow Book and Single Audit reports are represented.

- Confirm each finding contains required elements: condition, criteria, cause, effect, questioned costs (if any), context, repeat finding designation, and recommendation. For Single Audit findings, confirm reference to the specific compliance requirement and major program.

- Confirm finding reference numbers are used consistently throughout (SFQC, auditor's reports, Summary Schedule of Prior Audit Findings, Corrective Action Plan).

- Confirm questioned cost amounts are internally consistent.

## Summary Schedule of Prior Audit Findings (if applicable)

- Confirm all prior findings are addressed and current status is accurately described (fully corrected, partially corrected, not corrected, no longer applicable).

## Other Information (AU-C 720)

- Identify any other information present (e.g., letter from the executive director, organizational narrative, impact statements).

- Confirm the auditor's report includes the required Other Information paragraph if OI is present.

- Confirm the OI does not contain material inconsistency with the financial statements.

## Prior Year Figures, Comparative Presentations, and Auditor Changes

- If prior year comparative figures are presented, request the prior year issued financial statements if not already provided.

- Agree all beginning balances — net assets without donor restrictions, net assets with donor restrictions, any other equity carryforwards — to the prior year's ending audited figures.

- If the prior year financial statements are provided, confirm all comparative figures agree.

- Identify any reclassifications of prior year figures and confirm they are disclosed.

- Review accounting policies for consistency with the prior year; flag changes and confirm appropriate disclosure under ASC 250.

- If auditors have changed, confirm proper reference to the predecessor under AU-C 725.

- If prior year figures are presented as unaudited, confirm labeling and disclosure.

## Final Language Checks

- Confirm all financial statement titles cited anywhere in the audit reports exactly match printed titles in the document.

- Confirm all years and dates referenced are correct.

- Confirm the entity's legal form is stated consistently between the report and the statements.

# STEP 3 — FULL MATH CHECK

## Excel Source File — Reference Protocol

If an Excel workbook was provided and verified in Step 0, apply the following protocol throughout the math check:

### What the Excel is for:

- Establishing the correct column order and mapping each figure to its column header before performing any arithmetic — critical for the statement of activities (net asset classes) and statement of functional expenses (program and supporting services columns)

- Resolving ambiguous subtotals — where it is unclear from the PDF which line items sum to a subtotal

- Explaining discrepancies — hidden rows, rounding of decimals to integers, and other Excel-specific artifacts

- Calibrating understanding of how the numbers add up before applying to the PDF

### What the Excel is NOT for:

- Proofing the Excel itself — do not audit formulas, flag Excel errors, or comment on workbook construction

- Gospel — if the PDF and Excel disagree on a total, do not automatically defer to the Excel. Flag the discrepancy

- Overriding a genuine error — if a PDF figure does not foot and the Excel agrees with the incorrect total, the error still exists in the printed document and must be flagged

### Formatting conventions and subtotal scope:

The Excel establishes what is intended to sum to a given subtotal — it does not establish whether that subtotal is presented correctly. If document formatting (underlines, indentation, headers) suggests a subtotal should capture a different set of line items than the Excel actually sums, flag the ambiguity. If the same formatting convention is used elsewhere to mean something different, that inconsistency is itself a finding.

### Column mapping procedure (required for any statement with three or more data columns):

Before performing any arithmetic on a statement with three or more data columns, explicitly write out the column map in this format:

*Column 1: [Header name] | Column 2: [Header name] | ... | Column N: [Total column header]*

*Confirmed against: Excel tab **"**[tab name]**"*

For the statement of activities, identify which columns represent net assets without donor restrictions, with donor restrictions, and total. For the statement of functional expenses, identify each program service column, each supporting services column (typically management and general, fundraising, membership development), and the total column. State which columns sum to which totals before calculating anything.

### Rounding — zero tolerance:

Every column must foot to the printed total exactly. Any difference — including $1 — is a finding. If the Excel shows decimal precision displayed as rounded integers, flag it for the preparer to resolve. Rounding is an explanation, not an excuse. If a column does not foot and the difference cannot be explained by rounding, note that hidden rows may account for the discrepancy.

### PDF extraction caveat — when Excel is not provided:

When the Excel workbook has NOT been provided and a math finding arises on a statement with three or more data columns, the finding MAY be an artifact of PDF extraction — especially dense statements like functional expenses. Before flagging:

- Re-extract using layout-preserving methods (e.g., pdftotext -layout) and visually confirm from a rendered page image where possible.

- If after visual confirmation the figures still do not foot, flag the finding with a note that visual confirmation was performed and recommend the preparer verify against Excel.

- If visual confirmation cannot be performed, flag as POTENTIAL with a standard note: "This finding arose on a multi-column statement; Excel source was not provided for column mapping verification. May reflect a PDF extraction limitation rather than an error in the document. Recommend providing the Excel workbook to confirm."

- This caveat applies ONLY to statements with three or more data columns and ONLY when Excel was not provided.

## Math Check Procedures

**NOTE:** *The underlying schedules were prepared in Excel. Do not assume subtotals are correct. Hidden rows, rounding, or formula errors may cause totals to differ from the actual sum of visible line items. Recalculate from individual line items.*

### Foot every column and cross-foot every row:

- Add every number in every column of every statement, schedule, and table.

- Confirm sums equal subtotals and totals presented. Do not rely on printed totals — recalculate independently.

- In multi-column statements, confirm all columns add correctly across each row and down each column.

### Statement of Financial Position:

- Confirm total assets = total liabilities + total net assets.

- Confirm net assets total = sum of net assets without donor restrictions + net assets with donor restrictions.

- Confirm classified presentation (if used) — current vs. non-current — foots to grand totals.

### Statement of Activities:

- Confirm for each net asset class: revenues, support, and gains − expenses and losses − net assets released from restrictions (as applicable) = change in net assets for that class.

- Confirm net assets released from restrictions is presented as a reduction to one net asset class and a corresponding addition to the other, netting to zero in the total column.

- Confirm change in net assets ties to the statement of cash flows reconciliation (indirect method) if applicable.

- Confirm beginning net assets + change in net assets = ending net assets for each class, and that those ending balances tie to the statement of financial position.

### Statement of Functional Expenses:

- Foot each functional column (each program, management and general, fundraising, membership development as applicable).

- Cross-foot each natural expense line (e.g., salaries total across all functions = total salaries on the statement of activities or summary).

- Confirm the total column ties to total expenses on the statement of activities.

- Confirm allocations of shared costs (occupancy, IT, insurance) are applied consistently across functions.

### Statement of Cash Flows:

- Confirm operating, investing, and financing sections sum to net change in cash.

- Confirm net change + beginning cash = ending cash, and ending cash ties to the statement of financial position.

- For indirect method, confirm the reconciliation starts with change in net assets matching the statement of activities.

- Confirm any supplemental disclosures (interest paid, noncash contributions of securities, in-kind gifts) are internally consistent with the notes.

### Contributions Schedules:

- Foot contributions by donor class / restriction type, contributions receivable aging, and pledge schedules.

- Confirm pledges receivable discounted present-value matches disclosed discount rate calculation.

### Endowment Schedules (if applicable):

- Foot endowment rollforward by net asset class (contributions, investment returns, appropriations for expenditure, other changes).

- Confirm ending endowment balances tie to the statement of financial position.

### Investment Schedules:

- Foot investment rollforwards; confirm realized gains/losses + unrealized gains/losses + interest/dividends = total investment return disclosed.

### Debt Schedules:

- Foot maturity schedules; confirm totals agree to the note and to the face of the statements.

### SEFA (if applicable):

- Foot total federal expenditures by program and in aggregate, passed-through to subrecipients totals, and cluster totals.

### SFQC (if applicable):

- Confirm questioned cost amounts are internally consistent.

**NOTE:** *Flag every instance where a figure does not recalculate correctly, with the location, the presented figure, and the recalculated figure.*

# STEP 4 — CROSS-REFERENCE AND CONSISTENCY CHECK

Identify every number that appears in more than one location in the document and confirm all instances agree. At minimum, check:

## Net Assets

- Confirm ending net asset balances by class on the statement of financial position agree to: the statement of activities ending balances; any endowment footnote rollforward; any narrative references; any composition-of-net-assets-with-donor-restrictions note disclosure.

## Revenues, Support, and Expenses

- Confirm revenue and support totals on the statement of activities agree to any breakdown in the notes (contributions, grants, program service fees, investment return, etc.).

- Confirm total expenses on the statement of activities agrees to the total column on the statement of functional expenses.

- Confirm functional expense category totals in narrative sections or the notes tie to the statement of functional expenses.

## Depreciation

- Confirm depreciation expense on the statement of functional expenses ties to depreciation as a reconciling item on the statement of cash flows and to the accumulated depreciation change in the PP&E rollforward.

## Long-Term Debt

- Confirm the total outstanding balance per the debt footnote agrees to the face of the statements.

- Confirm the current portion agrees to the amount maturing within 12 months per the maturity schedule.

## Capital / Fixed Assets

- Confirm PP&E rollforward (beginning, additions, disposals, depreciation, ending) is internally consistent.

- Confirm ending net PP&E balance ties to the statement of financial position.

## Contributions and Pledges Receivable

- Confirm contributions receivable per the note agrees to the statement of financial position.

- Confirm contributions revenue per the statement of activities agrees to any disaggregation in the notes (by restriction, by donor type, by program).

- Confirm the present-value discount on multi-year pledges is calculated on the disclosed discount rate and ties to the disclosed net pledge balance.

## Grants (Conditional vs. Unconditional)

- Confirm conditional grants are disclosed but not recognized as revenue (ASC 958-605), while unconditional grants are recognized.

- Confirm grants receivable and refundable advances on the statement of financial position tie to grant-related note disclosures.

## Investments and Endowment

- Confirm total investments per the investment note tie to the statement of financial position.

- Confirm endowment balances per the endowment note tie to net asset composition and to the statement of financial position.

- Confirm investment return components (dividends, interest, realized gains, unrealized gains, investment fees) tie to the statement of activities.

## Contributed Services and In-Kind Contributions (ASC 958-605 / ASU 2020-07)

- Confirm contributed nonfinancial assets (GIK, in-kind rent, contributed services) are recognized where they meet ASC 958-605 criteria.

- Confirm disaggregation and valuation disclosures under ASU 2020-07 for contributed nonfinancial assets.

- Confirm in-kind contributions appear as both revenue and corresponding expense on the statement of activities (except for assets placed into inventory or capitalized).

## Leases (ASC 842)

- Confirm right-of-use asset and lease liability balances per the lease note agree to the statement of financial position.

- Confirm lease maturity schedule reconciles to present-value lease liability via disclosed discount rate.

- Confirm lease expense allocations across functional categories on the statement of functional expenses.

## Cash and Restricted Cash

- Confirm total cash and cash equivalents per the statement of financial position agrees to cash flow statement ending cash.

- Confirm restricted cash (if any) is reconciled per ASU 2016-18.

- Confirm any cash restrictions are consistent with net asset classifications.

## Liquidity Disclosure (ASC 958-210-50)

- Confirm the quantitative information about financial assets available to meet cash needs for general expenditures within one year ties to balances on the statement of financial position after considering stated reductions (donor restrictions, board designations, operating reserves).

## Related Party Transactions (ASC 850)

- Confirm every related-party balance is reflected on the statement of financial position in the expected line item.

- Confirm every related-party transaction is reflected on the statement of activities.

- Confirm intercompany balances are eliminated in consolidated statements.

## Federal Expenditures (if Single Audit)

- Confirm total federal expenditures per the SEFA is consistent with references in the auditor's reports and notes.

- Confirm major program expenditures on the SEFA match the major programs identified in the Single Audit report.

## Prior Year Figures

- Confirm prior year comparative figures are internally consistent throughout the document.

- Confirm beginning net asset balances agree to prior year ending audited balances.

## Footnote Figures

- Confirm every figure in the footnotes agrees to the corresponding line item on the face of the statements.

- Confirm all cross-references between footnotes are accurate.

**NOTE:** *Identify any other figure appearing in multiple locations and confirm consistency. Flag every discrepancy with location, expected figure, and actual figure found.*

## Paired-Account Relationship Analysis

Beyond checking the plausibility of individual balances, assess whether accounts that logically travel together are in fact both present, both absent, or in a sensible proportion. Many disclosure omissions and classification errors surface through what is missing rather than what is wrong on its face. Work through the following paired-relationship checks. For each pair, the rule is the same: if one account is present at a material level, the other should also be present (or its absence explained). If both are present, assess whether their relationship is plausible.

The list below is representative, not exhaustive. Apply experienced reviewer judgment to identify other paired relationships not listed here.

### Operations and expenses

- **Salaries and wages → payroll tax expense and accrued payroll taxes.** Compensation of any meaningful size should be accompanied by payroll tax expense (employer FICA, Medicare, FUTA, SUTA) and typically an accrued payroll tax liability at period end. Compensation with no payroll tax expense is a flag. Payroll tax expense implausibly low relative to compensation (rule of thumb: roughly 7.65%–10% of wages below wage-base limits) is a flag. Note: 501(c)(3) organizations are exempt from FUTA at the federal level, which reduces the expected ratio slightly but does not eliminate employer payroll tax entirely.

- **Salaries and wages → retirement plan expense or disclosure.** Nonprofits of meaningful size typically offer some retirement benefit (403(b), 401(k), SIMPLE, defined benefit). Absence of any retirement plan note is worth confirming.

- **Salaries and wages → workers' compensation insurance expense.** Nonprofits with employees carry workers' comp (except in a small number of statutory exceptions). Flag absence.

- **Contract labor / independent contractor expense → absence of payroll tax on that amount.** Confirm contract labor is classified separately and is not generating payroll tax.

- **Program service revenue → absence or presence of direct program costs.** Program service revenue with no corresponding direct program costs warrants confirmation.

- **Investment income → investment management fees.** Material investment portfolios typically incur management or advisory fees; confirm presence.

### Property, plant, and equipment

- **Land → buildings and/or building improvements.** Land by itself without buildings is unusual for an operating nonprofit (possible for a land trust or conservation organization — confirm). Buildings without land is unusual except in leased-ground situations.

- **Buildings / equipment / vehicles → depreciation expense and accumulated depreciation.** Any depreciable asset class should have corresponding depreciation expense on the statement of functional expenses and accumulated depreciation on the statement of financial position. Gross PP&E with zero depreciation is a flag unless all assets were placed in service at year end.

- **Vehicles → auto / fuel / vehicle insurance expense.** Flag absence if vehicles are on the balance sheet.

- **Land and buildings → property tax expense or PILOT (payments in lieu of taxes).** 501(c)(3) organizations are often exempt from property tax on mission-use property, but may pay property tax on unrelated property, may make PILOTs, or may have exempt status that should be noted. Absence of any property tax discussion for a significant real estate holder is worth flagging.

- **Real property → property insurance expense.** Owned real property should carry insurance; flag absence.

- **Construction in progress → absence of depreciation on CIP balance.** CIP should not be depreciated.

- **Leasehold improvements → operating lease presence (ASC 842).** Leasehold improvements imply a lease; confirm corresponding lease liability and ROU asset.

### Debt and financing

- **Notes payable / long-term debt → interest expense.** Any interest-bearing debt should generate interest expense. Debt with no interest expense is a flag. Interest expense with no debt on the statement of financial position is a flag.

- **Line of credit → interest expense and unused line fees.**

- **Long-term debt → current portion.** Long-term debt with zero current portion is a flag unless the maturity schedule confirms no principal is due within 12 months.

- **Interest expense → interest payable.** Material interest expense typically has some accrual at period end.

- **Tax-exempt bonds → bond-related disclosures.** Many nonprofits (hospitals, universities, cultural institutions) have tax-exempt bond financing; if present, confirm compliance disclosures, arbitrage considerations, and related covenants.

### Leases (ASC 842)

- **Occupancy / rent / lease expense on statement of functional expenses → ROU asset and lease liability on statement of financial position.** Operating lease expense implies both ROU asset and lease liability unless all leases are short-term under 12 months (practical expedient disclosure).

- **ROU asset → lease liability.** Paired by construction; material imbalance warrants review.

- **Leased space described in operations → corresponding ROU asset and lease liability.**

### Receivables and contributions

- **Grants receivable / contributions receivable → allowance for uncollectible pledges.** Material pledges should have a disclosed uncollectible pledge reserve or statement that none is necessary.

- **Multi-year pledges → present-value discount.** Pledges payable beyond one year should be discounted; confirm discount is disclosed and applied.

- **Contributions receivable → contribution revenue on the statement of activities.** Receivable balances and revenue recognition should be consistent with donor pledge timing.

- **Conditional promises to give → disclosure without revenue recognition.** Conditional promises should be disclosed but not recognized until conditions are met (ASC 958-605).

### Payables and accruals

- **Accounts payable → corresponding expense activity.**

- **Accrued compensation → salaries and wages expense.** Accrued bonuses, vacation, PTO should reconcile to compensation policies.

- **Refundable advances (conditional grants) → grant agreement conditions disclosed.**

- **Split-interest agreement liabilities → related investments and present-value measurement.**

### Net assets and designations

- **Releases from restrictions on statement of activities → corresponding use of restricted assets.** Amounts released should correspond to purpose satisfaction or time passage disclosed in the note on net asset composition.

- **Board-designated funds → disclosure within net assets without donor restrictions.** If the entity has operating reserves, quasi-endowment, or other board designations, these should be disclosed.

- **Endowment corpus → net assets with donor restrictions composition.** Permanent endowment corpus should appear in net assets with donor restrictions (under ASU 2016-14).

### Investments and cash

- **Investments on statement of financial position → investment income on statement of activities.** Material investments should produce interest, dividend, or realized/unrealized gain activity.

- **Restricted cash → nature of restriction disclosure.** Restricted cash requires disclosure of the nature of restriction and whether restrictions are donor-imposed or other.

- **Endowment investments → UPMIFA policy disclosure, spending policy, underwater endowment disclosure.**

### Intangibles and goodwill

- **Goodwill → prior business combination (ASC 958-805 applies to NFP combinations and acquisitions).**

- **Amortizable intangibles → amortization expense and accumulated amortization.**

### Program and functional allocation

- **Program services revenue → program expense allocation on statement of functional expenses.** Each identified program should have meaningful activity on both sides.

- **Shared costs (occupancy, IT, insurance, depreciation) → methodology disclosure.** Functional allocation of shared costs requires a methodology disclosure under ASC 958-720-45-15.

- **Fundraising activities described → fundraising column on statement of functional expenses.** If the organization describes fundraising activities (special events, capital campaigns, annual appeal), confirm a fundraising function column exists with meaningful amounts. A nonprofit of any size with zero fundraising expense is highly unusual.

- **Fundraising expense → contribution revenue.** Contribution revenue with zero fundraising expense, or fundraising expense disproportionately small relative to contribution revenue, warrants confirmation.

- **Joint activities disclosure (ASC 958-720-45).** If a fundraising activity is presented as having both program and fundraising components (allocated joint cost), confirm required disclosures.

### Related party signals

- **Related-party receivables or payables → corresponding revenue/expense disclosure.**

- **Management fees paid to related party or affiliate → related party note.**

- **Officer/director compensation or transactions → board disclosure.** Compensation or transactions with officers, directors, or key employees are required disclosures.

### Federal award and grant signals (if applicable)

- **Federal grant revenue → SEFA entry.** Federal grant revenue on the statement of activities should correspond to entries on the SEFA.

- **Federal expenditures ≥ Single Audit threshold → Single Audit reports.** If federal expenditures exceed the Single Audit threshold ($750,000 / $1,000,000), confirm Single Audit reports are present.

- **Indirect cost recovery revenue → indirect cost rate disclosure and SEFA note.**

- **Grant advances and refundable advances → conditional grant liability.**

### Procedural guidance

For each relationship flagged:

- State what account is present and what the expected paired account would be

- State whether the paired account is absent, present but implausibly sized, or present and reasonable

- Classify as a disclosure / completeness question, a classification question, or a reasonableness question

- Note that the reviewer should confirm — many of these flags have legitimate explanations (pure pass-through grant model, all leased premises captured as short-term, newly formed entity, etc.). The objective is to surface the relationship for review, not to assert an error.

**NOTE:** *Apply this analysis in combination with the logical and contextual consistency checks below. A finding may appear in either or both sections; flag it once with a cross-reference.*

## Logical and Contextual Consistency

Beyond verifying that figures tie to their counterparts and that paired accounts are present, assess whether the financial statements make logical and contextual sense as a whole. This step is not about mathematical agreement but about whether numbers, disclosures, and narrative are internally coherent and plausible given the entity's described circumstances. Flag anything a knowledgeable reader would find implausible, inconsistent, or unexplained.

- **Mission and program alignment.** Assess whether reported program expenses are consistent with the entity's described mission and programs. An organization describing extensive programs with minimal program expense is a flag; an organization with significant program expense in areas not described in the mission or notes is a flag.

- **Functional expense ratio plausibility.** Assess whether the ratio of program expense to total expense (program ratio) is plausible for the entity's type. Very high ratios (e.g., 98%+ program, near-zero management and general and fundraising) are often the result of allocation rather than actual operations and warrant scrutiny. Very low program ratios may indicate operational inefficiency or mis-allocation.

- **Contribution volume vs. fundraising cost.** Assess whether contribution revenue is plausible given fundraising expense and the described fundraising activities.

- **Grant revenue vs. described grants.** If grants from specific funders or government sources are described in the notes or narrative, confirm corresponding revenue.

- **Investment returns vs. described portfolio.** Assess whether investment returns are plausible for the disclosed portfolio allocation and size given prevailing market returns for the period.

- **Endowment spending vs. policy.** Confirm endowment appropriations for expenditure are consistent with the disclosed spending policy (e.g., 4–5% of trailing averaged endowment value).

- **Underwater endowment disclosure.** If endowment investments have declined below donor-stipulated historical dollar value, confirm underwater endowment disclosure is made per ASC 958-205-45.

- **Going concern indicators.** Flag negative unrestricted net assets, recurring operating deficits, reliance on a single funder, major pending grant expirations, or management disclosure of financial difficulty.

- **Capital asset reasonableness.** Assess whether additions, disposals, and depreciation amounts are plausible given the asset base and useful life policies. Flag depreciation implausibly high or low relative to gross asset balance.

- **Lease reasonableness.** Flag entities with significant operations described and minimal or no lease disclosures — potential missed ASC 842 application.

- **Related party reasonableness.** Flag material related-party transactions without disclosure of terms, especially with officers, directors, board members, or related organizations.

- **Allocation methodology consistency.** Compare functional allocations across natural expense categories; allocations that appear inconsistent (e.g., occupancy heavily allocated to program while utilities are heavily allocated to G&A) warrant review.

- **Contributed services threshold (ASC 958-605).** Contributed services are recognized only if they create or enhance nonfinancial assets OR require specialized skills and would otherwise be purchased. Flag if substantial volunteer activity is described but no contributed service revenue is recognized — confirm the service did not meet the recognition threshold (typical for most volunteer activity).

- **Tax-exempt status and UBIT.** If the entity has unrelated business income (rental income from debt-financed property, advertising revenue, commercial activity not related to mission), confirm UBIT disclosure and any tax provision for unrelated business income.

- **General implausibility.** Apply experienced reviewer judgment to flag any balance, ratio, trend, or disclosure that would strike a knowledgeable reader as unusual, unexplained, or inconsistent with the entity's described operations.

# STEP 5 — GAAP (ASC) DISCLOSURE AND TECHNICAL REVIEW

Perform a full technical review for compliance with applicable FASB Accounting Standards Codification (ASC) requirements, with emphasis on ASC 958 (Not-for-Profit Entities).

## ASC 958 — Core Nonprofit Standards

Under ASC 958 and the underlying ASU framework (ASU 2016-14, ASU 2018-08, ASU 2020-07), verify:

- Statement of Financial Position presents total assets, total liabilities, and net assets with two classes: (1) net assets without donor restrictions; (2) net assets with donor restrictions. Legacy three-class presentation (unrestricted / temporarily restricted / permanently restricted) is no longer permitted.

- Statement of Activities presents changes in each net asset class, with releases from restrictions shown as a reduction of one class and an increase in the other (netting to zero in total).

- Statement of Functional Expenses is required (or functional expense information must be provided, typically via this statement; a matrix format showing natural expenses by function is standard). Entity must classify expenses by both natural and functional categories.

- Statement of Cash Flows is required; direct or indirect method permitted.

- Disclosures required by ASU 2016-14:
  - Composition of net assets with donor restrictions (by purpose restriction, time restriction, perpetual in nature)
  - Board designations, appropriations, and similar actions affecting net assets without donor restrictions
  - Qualitative information about liquidity
  - Quantitative information about financial assets available to meet cash needs for general expenditures within one year of the balance sheet date
  - Methods used to allocate costs among program and support functions (ASC 958-720-45-15)
  - Investment expenses netted against investment return, with disclosure

- ASU 2018-08 (contributions vs. exchange transactions): confirm the entity has determined whether grants and contracts are contributions (nonreciprocal) or exchange transactions, and has applied ASC 958-605 or ASC 606 accordingly.

- ASU 2020-07 (gifts-in-kind / contributed nonfinancial assets): confirm disclosures for contributed nonfinancial assets — disaggregation by category, qualitative information on each category, policies on monetization vs. utilization, valuation techniques and inputs.

## Other Applicable ASC Topics

- ASC 205 — Presentation of Financial Statements

- ASC 210 — Balance Sheet; if classified presentation used, confirm current vs. non-current classification

- ASC 230 — Statement of Cash Flows; direct or indirect method consistently applied

- ASC 250 — Accounting Changes and Error Corrections

- ASC 320/321/325 — Investments; fair value measurement under ASC 820

- ASC 326 — Credit Losses (CECL); applicable to contributions receivable and other financial instruments held at amortized cost

- ASC 330 — Inventory (if applicable, e.g., merchandise sold, gift shop, publications)

- ASC 350 — Intangibles, including goodwill (applicable to NFP M&A transactions under ASC 958-805)

- ASC 360 — Property, Plant, and Equipment; collections exemption under ASC 958-360 for qualifying collection items held for public exhibition, education, or research

- ASC 450 — Contingencies; loss contingency accruals and disclosures

- ASC 460 — Guarantees

- ASC 470 — Debt; including tax-exempt bond financing disclosures

- ASC 606 — Revenue from Contracts with Customers (for exchange transactions such as program service fees, subscription revenue, ticket sales)

- ASC 715 — Retirement Benefits (if defined benefit plans; 403(b) tax-sheltered annuity disclosures as applicable)

- ASC 718 — Stock Compensation (rare in nonprofits except controlled for-profit subsidiaries)

- ASC 740 — Income Taxes; disclosure of tax-exempt status, any UBIT provision, uncertain tax positions (ASC 740-10)

- ASC 805 / 958-805 — Business Combinations and acquisitions by nonprofit entities

- ASC 820 — Fair Value Measurement; Level 1/2/3 disclosures

- ASC 842 — Leases

- ASC 850 — Related Party Disclosures

- ASC 855 — Subsequent Events

- ASC 958 subtopics:
  - 958-205 — Presentation
  - 958-210 — Balance Sheet / Liquidity Disclosure
  - 958-225 — Income Statement (Statement of Activities)
  - 958-230 — Cash Flows
  - 958-310 — Receivables (pledges, grants)
  - 958-320 — Investments
  - 958-325 — Investments — Other
  - 958-360 — PP&E and Collections
  - 958-405 — Liabilities (split-interest agreements)
  - 958-450 — Contingencies
  - 958-470 — Debt
  - 958-605 — Revenue Recognition for Contributions
  - 958-715 — Retirement
  - 958-720 — Other Expenses (functional allocation)
  - 958-805 — NFP Business Combinations
  - 958-810 — Consolidation
  - 958-815 — Derivatives and Hedging
  - 958-840 / 958-842 — Leases (legacy / current)

## Completeness of Financial Statements

Before confirming completeness, perform the following identification and inference procedure.

### Step 1 — Identify the entity's required statement package

Under U.S. GAAP (ASC 958), a complete set of NFP financial statements includes:

- Statement of Financial Position — required

- Statement of Activities — required

- Statement of Functional Expenses — required for all NFPs (either as a separate statement, within the statement of activities, or in the notes)

- Statement of Cash Flows — required

- Notes to the Financial Statements — required

Additional schedules may be presented as supplementary information:

- Consolidating or combining schedules (for NFP groups)

- Schedules of operating expenses by program

- Schedule of grants awarded

- Schedule of board-designated reserves

### Step 2 — Confirm required statements are present

- Confirm all four required statements are present.

- Confirm the functional expense presentation meets ASC 958-720-45 requirements (matrix of natural expenses by functional category, or equivalent presentation).

- Confirm net assets are presented in two classes only (without donor restrictions; with donor restrictions).

### Step 3 — Cross-check statements against all document references

- The auditor's opinion paragraph cites specific statement titles — confirm every cited statement is physically present with a matching title.

- The summary of significant accounting policies describes activities that imply certain content; confirm corresponding statements and disclosures exist.

- If the notes discuss an endowment, confirm endowment disclosures are present.

- If the notes or narrative describe federal grants, confirm Single Audit reports are present when the threshold is met.

## Required Footnote Disclosures

Confirm footnotes include all required disclosures:

- **Summary of Significant Accounting Policies** — addresses: nature of operations (mission, programs, geographic reach, tax-exempt classification); basis of presentation (consolidated or combined basis if applicable); principles of consolidation; use of estimates; cash and cash equivalents; contributions receivable and allowance; inventory (if applicable); investments and fair value measurement; property and equipment (depreciation methods, useful lives, capitalization threshold); collections policy (if applicable); leases (ASC 842); revenue recognition for contributions vs. exchange transactions (ASU 2018-08); contributed nonfinancial assets (ASU 2020-07); functional allocation methodology; income taxes (tax-exempt status, UBIT policy); recent accounting pronouncements

- **Nature of Business / Organization** — description of operations, legal form, tax-exempt classification (501(c)(3) public charity, private foundation, etc.), mission, programs

- **Liquidity and Availability of Financial Assets** (ASC 958-210-50) — quantitative and qualitative information about financial assets available within one year

- **Contributions Receivable / Pledges Receivable** — aging, present-value discount, allowance for uncollectible pledges, conditional vs. unconditional

- **Investments** — types, fair value, Level 1/2/3, net asset value NAV practical expedient, alternative investments, related-party investments

- **Endowment** (ASC 958-205-45) — composition by net asset class, changes during period, spending policy, investment policy, underwater endowments (if any), relevant law (UPMIFA)

- **Property and Equipment** — components, accumulated depreciation, depreciation expense, capitalization threshold, collection items (if collection exemption applied)

- **Leases (ASC 842)** — components of lease cost by function, weighted average remaining lease term and discount rate, maturity analysis, ROU assets and lease liabilities by classification, related-party leases

- **Long-term Debt** — components, interest rates, maturity schedule, covenants, collateral, tax-exempt bond disclosures if applicable

- **Line of Credit** — availability, outstanding, interest rate, maturity, covenants

- **Net Asset Composition** — detailed composition of net assets with donor restrictions (by purpose, by time, perpetual); board designations within net assets without donor restrictions

- **Net Assets Released from Restrictions** — by purpose (satisfaction of donor restrictions) and by time

- **Contributions and Revenue Recognition** — conditional vs. unconditional, donor-restricted vs. unrestricted, disaggregation if material

- **Contributed Nonfinancial Assets** (ASU 2020-07) — disaggregation, valuation, monetization vs. utilization policies, restrictions, valuation techniques

- **Grants from Federal, State, Local Governments** — nature of grants, amounts, compliance requirements

- **Concentrations** — donor concentrations, grantor concentrations, program concentrations, geographic concentrations, credit concentrations

- **Functional Allocation** — methodology used to allocate shared costs across functions (ASC 958-720-45-15)

- **Retirement Plans** — defined contribution plan description and employer contributions; if defined benefit, full ASC 715 disclosures; 403(b) plan disclosures

- **Income Taxes** — tax-exempt status under IRC §501(c)(3) or other applicable section, classification (public charity vs. private foundation), any UBIT, any uncertain tax positions (ASC 740-10), state tax considerations

- **Related Party Transactions** — transactions with officers, directors, trustees, key employees, and related organizations; common nonprofit structures include affiliated foundations, supporting organizations, controlled entities

- **Commitments and Contingencies** — loss contingencies, grant commitments, employment agreements, guarantees, legal proceedings; compliance requirements for federal and state awards

- **Subsequent Events** — evaluation date, events disclosed or statement that none identified

- **Recent Accounting Pronouncements** — pronouncements not yet adopted

- **Split-Interest Agreements** (if applicable) — charitable gift annuities, charitable remainder trusts, perpetual trusts held by third parties, pooled income funds, with required valuation and liability disclosures

- **Any other disclosures required for balances or transactions present**

## Accounting Policy Changes

- Review accounting policies against prior year if available.

- Flag any policy added, removed, or modified without disclosure of a change under ASC 250.

- If a new standard adoption explains the change (e.g., first-year ASC 842 adoption, ASU 2020-07), confirm the adoption is explicitly disclosed.

## Going Concern — Document-Based Assessment

Under ASU 2014-15 (ASC 205-40), management is required to evaluate substantial doubt within one year after the date the financial statements are available to be issued. Flag the following if present:

- Recurring deficits in net assets without donor restrictions or operations

- Negative net assets without donor restrictions (unrestricted deficit)

- Reliance on a single major donor, grantor, or funding source with disclosure of uncertain renewal

- Loan maturities within 12 months without disclosed refinancing

- Loss of a major program funder or expiration of a significant grant

- Covenant violations or waivers

- Management disclosure referencing financial difficulty or recovery plans

- Pension underfunding of material size

If going concern language appears in the notes, confirm the auditor's report contains the corresponding Substantial Doubt section.

## Subsequent Events (ASC 855)

- Confirm a subsequent events note is present with evaluation date disclosed.

- Confirm the evaluation date is through the date the financial statements were available to be issued.

- Confirm material subsequent events are appropriately classified as Type I (recognized) or Type II (non-recognized / disclosed only).

## Consolidation and Combined Presentations (ASC 958-810)

- For consolidated statements, confirm the principles of consolidation note describes entities consolidated and the basis (control, majority voting interest, economic interest + control via board appointment).

- For combined statements, confirm appropriateness (affiliated entities without consolidation basis, or historical basis).

- For NFP with controlled for-profit subsidiaries, confirm consolidation.

- Confirm all intercompany balances and transactions are eliminated.

- Confirm supporting organizations, affiliated foundations, or similar relationships are appropriately addressed (consolidated, combined, or disclosed).

## Yellow Book Technical Requirements (if applicable)

- Confirm compliance with GAGAS reporting requirements, including independence, required communications, and finding format requirements.

## Single Audit Technical Requirements (if applicable)

- Confirm compliance with 2 CFR Part 200 Subpart F requirements, including SEFA presentation, finding format, and required reports.

- Confirm major program determination used the correct threshold.

- Confirm the low-risk auditee determination is documented if claimed.

## Accounting Standards — General

- Review all presented balances and transactions for apparent conformity with U.S. GAAP.

- Flag any amounts or presentations that appear to deviate from applicable standards.

## Entity-Type-Specific Technical Review

### Public Charities (501(c)(3))

- Confirm tax-exempt status disclosed

- Confirm public support test discussion is NOT required in the GAAP statements (that is a Form 990 Schedule A matter, not a financial statement disclosure), but note language referring to the entity's public charity classification is common

### Private Foundations (501(c)(3))

- Confirm distinction between operating and non-operating foundation disclosed if relevant

- Confirm excise tax on net investment income (Section 4940) disclosed if applicable

- Confirm minimum distribution requirement (Section 4942) — not a financial statement disclosure, but reference may appear

- Confirm self-dealing and other Chapter 42 restrictions disclosed if relevant

### Religious Organizations

- Many religious organizations are exempt from Form 990 filing but still issue GAAP statements for donors, lenders, or governance; confirm tax-exempt status accurately described

- Confirm clergy housing allowance and related benefits disclosures if material

### Educational Institutions

- Tuition and fees revenue recognition (ASC 606 for exchange portion; ASC 958-605 if contribution element present)

- Scholarship allowance presentation (typically as a reduction of tuition revenue or as an expense, depending on funding source)

- Room and board, auxiliary enterprise disclosures

- Student loan receivables and allowances

### Healthcare Nonprofits

- Patient service revenue under ASC 606 with bad debt as a reduction of revenue (not an expense) per ASU 2014-09 guidance

- Third-party payor settlement estimates, cost report settlements

- Charity care disclosure (ASU 2010-23); not recognized as revenue but disclosed

- Medicare/Medicaid compliance and potential settlements

### Social Service Agencies

- Grant revenue recognition (typically contributions under ASU 2018-08, with conditional vs. unconditional analysis; some fee-for-service elements may be exchange transactions under ASC 606)

- Program-specific restrictions and compliance

### Foundations (community, independent, corporate)

- Endowment disclosures central (composition, spending policy, underwater endowment)

- Donor-advised funds (if any) appropriately reflected with corresponding note disclosure; DAF assets are the foundation's assets, not the donor's

- Agency endowments (where the foundation holds funds for another organization's benefit) may require different treatment — confirm

### Associations (501(c)(6), trade, professional)

- Member dues — ASC 606 analysis (are dues exchange or contribution?); disaggregation

- Deferred member dues disclosure

- Unrelated business income if applicable (advertising, trade show non-member revenue)

# STEP 6 — FINAL PROOF CHECKLIST

Apply the judgment of an experienced nonprofit audit preparer performing a final proof. The goal is to surface document-level issues a preparer would want to resolve before handing off to QC.

## Internal Consistency of Narrative

- If any management letter, mission statement, or narrative accompanies the financial statements, confirm it is consistent with the presented results.

- Flag any narrative claim inconsistent with the numbers.

## Opinion Appropriateness

- Given the complete contents, does the opinion type appear appropriate?

- Are there any matters disclosed in the footnotes (significant uncertainties, going concern indicators, material restatements, major subsequent events, GAAP departures) that would appear to require modification or emphasis in a currently unmodified report?

## Going Concern and Emphasis-of-Matter Consistency

- If going concern language appears in the notes, confirm the auditor's report contains the corresponding Substantial Doubt section.

- If a restatement, change in accounting principle, or significant subsequent event is disclosed, confirm an appropriate emphasis-of-matter paragraph.

## Finding Consistency (if Single Audit)

- If findings are present in the SFQC, confirm they are fully and consistently reflected throughout all auditor reports.

- Confirm finding language is professionally written and complete.

## Sensitive Disclosures

- Are there any disclosures that appear legally, politically, or reputationally sensitive that should be reviewed by engagement leadership? Common nonprofit-specific sensitivities: executive compensation disclosures, related-party transactions with board members, donor-specific restrictions, unusual grants, political or lobbying activity.

## Cover Page and Transmittal

- If a transmittal letter, cover page, or table of contents is present, confirm it is addressed correctly, dated correctly, and attributed appropriately.

## Supplementary Schedules

- Confirm any supplementary schedules (consolidating, operating expense detail, schedules of grants) are properly labeled, referenced in the auditor's report, and mathematically consistent.

## Unusual or Uncommon Items

- Flag anything in the document that is unusual or uncommon for a nonprofit financial statement and warrants specific attention. Examples: split-interest agreements; donor-advised funds with unusual characteristics; agency endowments; beneficial interests in perpetual trusts; defined benefit pension plans; variable annuity or unit trust arrangements; controlled for-profit subsidiaries; significant alternative investments (hedge funds, private equity, real estate); collections accounted for under the ASC 958-360 exemption; tax-exempt bond financing; political or lobbying activity; foreign grantmaking; disaster relief activity; any transaction or balance that is unusual for the entity type or industry.

# STEP 7 — OUTPUT FORMAT

After completing all review steps, produce a structured Excel report with the following tabs. Apply the formatting rules described in the AI Behavior and Output Formatting section at the top of this prompt (no fills, no borders except section-heading underlines, no merged cells, three plain header cells upper-left, no Purpose/Procedure scaffolding, no release-readiness language).

## Tab 1 — Executive Summary

- All findings compiled in a single table, sorted by severity: Critical, Significant, Moderate, Minor

- A summary at the top showing only the count of findings by severity. Do NOT include any release-readiness language, engagement-risk language, or overall assessment.

- Each finding row includes: Finding ID, Step, Category, Severity, Location in document, Description, Recommended Correction. Do not include Reviewer Notes, Management Response, or Resolved columns.

- This tab is self-contained — a reader should be able to find every issue without jumping to the detail tabs.

## Tab 2 — Proof Review

- All Step 1 procedures listed line by line with Pass / Fail / Flag result and notes

## Tab 3 — Report Language

- All Step 2 procedures organized by report (financial statement opinion; Yellow Book if applicable; Single Audit if applicable), with Pass / Fail / Flag result and notes

## Tab 4 — Math Check

- All Step 3 procedures with per-document figure, recalculated figure, difference, and result

- Multi-column statements (statement of activities, statement of functional expenses) include the column map at the top of each section

- Provisional results clearly labeled where Excel was not available

## Tab 5 — Cross-Reference

- All Step 4 procedures with location 1, location 2, value, and result

- Include a sub-section for paired-account relationship findings

- Include a sub-section for logical and contextual consistency findings

## Tab 6 — GAAP/ASC Review

- All Step 5 procedures organized by ASC topic / requirement with Pass / Fail / Flag result and notes

## Tab 7 — Final Proof Checklist

- All Step 6 items with result, finding reference, and notes. No blank manual-entry columns.

**NOTE:** *Severity classification throughout: Critical, Significant, Moderate, Minor. Use these labels consistently in all tabs.*

**NOTE:** *Present all findings organized by step in the detail tabs. For each issue, note: location in the document, description of the issue, and recommended correction. The Executive Summary tab should be self-contained enough that a reader can see every issue without needing to open the detail tabs.*

*— End of Prompt —*
