---
name: commercial-fs-review
description: Comprehensive technical proof and review of a non-public commercial financial statement package — C-corps, S-corps, partnerships, LLCs, LLPs, closely-held entities, private company audits under U.S. GAAP (FASB/ASC). Use this skill WHENEVER the user uploads or references a commercial/private-company financial statement or audit report and asks for a review, proof, technical review, QC check, math check, cross-reference check, or disclosure review. Trigger even if the user does not say "skill" — private-company financials plus any review-style ask ("check this", "proof this", "find issues", "review before QC") should activate it. Also trigger on ASC/FASB standards review, SAS No. 134+ auditor's report review, going concern / debt covenant review, ASC 606 or ASC 842 review, related party or partner/member capital review. Do NOT use for governmental entities, SEC registrants / public companies, Single Audits, tax returns, or bookkeeping.
---

# Commercial (Non-Public) Financial Statement Technical Review

**Purpose:** Perform a technical proof and review of a non-public commercial financial statement package (corporations, partnerships, LLCs, closely-held entities reporting under U.S. GAAP) to locate issues for the preparer — after a first pass or as a final proof before QC. Not a substitute for human quality control.

# AI BEHAVIOR AND OUTPUT FORMATTING

## Narration and Commentary

1. Keep chat output minimal.
2. Do not narrate each procedure as it is performed.
3. Do not provide running commentary on findings or hypotheses.
4. Do not summarize or editorialize on results at the end.
5. Announce only the step number and title when starting each step (e.g., "Step 1 — Proof Review", "Step 3 — Math Check"). Do not announce sub-steps or internal procedures.
6. Put all findings and conclusions in the Excel report — never in chat.
7. Clarifying questions to the user are permitted only where Step 0 or Step 0C require them.

## Excel Report Formatting — Strict Rules

The deliverable is a plain Excel REPORT, not a workpaper. Requirements:

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

*"**Before I begin the review, I need two additional documents for the most complete and accurate analysis:*

*1. Excel source workbook — the underlying Excel file used to prepare the financial statements. Needed to correctly map column layout in statements with three or more data columns (e.g., consolidating schedules, segment reporting, multi-entity combining statements), where PDF text extraction can flatten the table structure and misattribute figures to the wrong column. Statements with only two data columns (current year / prior year) are generally handled reliably without it. Without the Excel file, math check results on any statement with three or more columns are provisional.*

*2. Prior year audited financial statements — the issued financial statements for the preceding fiscal year. Needed to agree beginning balances (retained earnings, partner/member capital accounts, AOCI), verify prior year comparative figures, check for reclassifications, assess accounting policy consistency, and confirm proper auditor-change language if the engagement changed hands.*

*Please provide whichever of these you have available. If either is unavailable, let me know and I will note the limitations and proceed accordingly.**"*

*File upload note: uploaded PDFs and images consume image capacity from the conversation's available limit, page by page. Uploading the financial statements, the prior year report, and the Excel workbook as separate files can exhaust that capacity before the review is complete on a large package. Combine all files into a single .zip archive and upload the zip instead — files can be extracted and used from a zip without the same per-page consumption.*"*

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

**⚠ WARNING:** *EXCEL WORKBOOK NOT PROVIDED: Math checks on financial statements with three or more data columns are subject to column attribution error. PDF text extraction can flatten table layouts in these statements (common on consolidating schedules, segment reports, and combining statements for multi-entity groups), making it unreliable to confirm which figures belong to which columns. Statements with only two data columns (current year / prior year) are generally handled correctly without the Excel file. Math check results on the following statements (three or more columns) should be treated as provisional and independently verified by the reviewer: [list all statements present with three or more data columns]. All other procedures are unaffected.*

Then proceed with the review, noting "PROVISIONAL — Excel not provided" on any math check result involving a statement with three or more data columns.

### If the prior year financial statements were not provided:

Ask the following before proceeding:

*"**Prior year financial statements were not provided. Before I proceed, can you tell me: Is this a first-year or first-time audit engagement — i.e., no prior year audited financials exist? Or are prior year audited financials available but not provided at this time?**"*

### If first-year audit or no prior audited financials exist:

- Note this and do not flag missing prior year tie-outs as findings

- Note that beginning balances cannot be agreed to a prior audited report as none exists — expected for a first-year engagement

- Review opening balance disclosures and any predecessor auditor, compilation, or review report language that may be present

- Confirm the auditor's report includes appropriate language under AU-C 510 for opening balances in initial audit engagements

- Proceed with all other procedures normally

### If prior year financials exist but were not provided:

**⚠ WARNING:** *PRIOR YEAR FINANCIALS NOT PROVIDED: The following procedures cannot be completed and should be treated as incomplete pending receipt of the prior year report: beginning balance tie-out (retained earnings, capital accounts, AOCI); prior year comparative figure verification; accounting policy consistency check; reclassification disclosure verification; auditor change / predecessor reference verification. All other procedures will execute normally.*

Proceed with the review, noting "INCOMPLETE — Prior year report not provided" on any procedure that cannot be performed.

# PRELIMINARY: IDENTIFY ENTITY TYPE AND ENGAGEMENT

Before any other procedures, perform the following identification steps:

- Identify the entity type (C corporation, S corporation, general partnership, limited partnership, LLC taxed as partnership, LLC taxed as corporation, single-member LLC, LLP, professional corporation, closely-held private company, employee-owned/ESOP, etc.). Note how this affects equity presentation, tax disclosures, and required footnotes.

- Identify the reporting framework. Confirm U.S. GAAP (FASB Accounting Standards Codification) is the stated framework. If any other framework appears (tax basis, cash basis, modified cash, contractual basis, IFRS, IFRS for SMEs, FRF for SMEs), flag this and note that the current review procedures are scoped to GAAP — the reviewer should confirm whether the engagement is actually being reported under a different framework.

- Confirm the engagement is an audit (opinion language, SAS-based reporting). If the document appears to be a review (SSARS AR-C 90), compilation (AR-C 80), or preparation engagement (AR-C 70), flag this — the report language procedures in Step 2 are scoped to audit reports.

- Identify whether the financial statements are consolidated, combined, or standalone:
  - Consolidated — parent with subsidiaries it controls; eliminations required
  - Combined — entities under common control or ownership; presentation of combined results without a parent-subsidiary relationship; eliminations still required for intercompany
  - Standalone — single legal entity, no subsidiaries

- Identify whether variable interest entity (VIE) analysis under ASC 810 appears relevant (common in private company structures with related-party real estate LLCs, management companies, etc.). Note whether the private company VIE accounting alternative under ASU 2018-17 has been elected.

- Identify whether any private company alternatives (PCC) have been elected — goodwill amortization (ASU 2014-02), simplified hedge accounting (ASU 2014-03), common-control leasing arrangements VIE scope exception (ASU 2014-07 / ASU 2018-17), intangible assets acquired in business combinations (ASU 2014-18). Note elections and confirm required disclosures.

**NOTE:** *All subsequent steps should be adapted to the identified entity type, equity structure, and any PCC alternatives elected.*

# STEP 1 — FULL PROOF

Perform a comprehensive proofread of the entire document:

## Table of Contents vs. Actual Document

- Confirm every item listed in the TOC exists in the document with a matching title and matching page number. Flag any discrepancy.

## Page Numbers

- Confirm page numbers are sequential, correctly formatted, and consistent in style throughout.

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

- Apply the same sequencing and continuation checks to other numbered/lettered sequences in the document where applicable: subheadings within a note (a, b, c or i, ii, iii), and continuation headers on multi-page schedules (e.g., "Consolidating Statement — continued" must accurately describe what is being continued).

## Consistency of Language

- Flag any inconsistency in how the entity, subsidiaries, product lines, segments, or accounts are named throughout the document.

- The entity should be referred to by a single consistent name (e.g., "the Company", "the Partnership", "the LLC") — confirm the chosen collective reference is applied consistently. Subsidiary names, segment names, and account titles must be consistent throughout all reports, statements, footnotes, and supplementary schedules.

## Consistency of Dates and Fiscal Year References

- All references to the fiscal year end date, the audit period, and prior year must be internally consistent. Flag any mismatched dates.

- Pay special attention to partnerships and S corporations with non-calendar tax years that may differ from the financial reporting year — confirm all date references are consistent with the stated reporting period.

## Formatting Consistency

## Punctuation and Possessive Consistency

Check for consistent use of the following punctuation conventions throughout the entire document, including all reports, statements, footnotes, schedules, and supplementary information:

- Serial comma (Oxford comma) usage — determine whether the document uses or omits the serial comma and flag any inconsistency. Do not flag the choice itself, only departures from the chosen convention.

- Possessive form of "Auditor" — identify whether the document uses "Auditor's" (singular possessive) or "Auditors'" (plural possessive) and flag any inconsistency. Do not flag the choice itself, only departures from the chosen convention.

- Collective reference to the entity — confirm the entity is consistently referred to as "the Company," "the Partnership," "the LLC," or similar throughout. Flag any inconsistency (e.g., switching between "the Company" and "the LLC" for the same entity).

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

- Confirm consistent capitalization of account titles, subsidiary names, segment names, and report titles.

## Widows and Orphans

- Flag single lines of text separated from their paragraph by a page break.

**NOTE:** *Flag anything else that would be identified during a professional proofread of a formally published financial document.*

# STEP 2 — REPORT LANGUAGE AND STANDARDS COMPLIANCE

Validate the independent auditor's report against current applicable standards (SAS No. 134 and subsequent SASs). For commercial non-public audits, there is typically a single report — the Independent Auditor's Report on the Financial Statements. Other reports (on internal control, on supplementary information, etc.) may appear as supplemental sections or separate reports depending on engagement scope.

## General Requirements

Apply the following to the audit report before proceeding to the detailed paragraph checklist.

- Confirm the report is addressed to the correct party — typically those charged with governance (board of directors, stockholders, members, or partners) and/or management as appropriate for the entity's governance structure. For closely-held entities without a formal board, confirm the addressee is appropriate (e.g., stockholders, members, partners).

- Confirm the report is dated correctly — the report date should be on or after the date sufficient appropriate evidence was obtained, and should not precede the financial statement date.

- Confirm the entity name in the report heading exactly matches the entity name used throughout the financial statements — including the exact legal form (Inc., LLC, LP, L.P., LLP, Corporation, Company).

- Confirm the report language conforms to SAS No. 134 and subsequent SASs (SAS 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145 as applicable). Flag any language that appears to follow the pre-SAS 134 form (e.g., old "Management's Responsibility"/"Auditor's Responsibility" structure without the "Basis for Opinion" section, opinion paragraph appearing at the end rather than near the top).

- Confirm no paragraph is present that is not required or permitted under the applicable standard. Flag any paragraph whose heading or substance does not correspond to a required, conditionally required, or permitted paragraph.

- Confirm the internal cross-references within the report are accurate — references to specific financial statements, specific notes, or supplementary information must all be verified.

## Independent Auditor's Report — Required Paragraphs Under SAS 134+

Verify every required paragraph is present, in the correct order, and correctly worded given the facts of the engagement. Also verify that no non-required paragraphs are present. Work through the report sequentially.

### Required sections — verify each is present and correct

- Report title — must include the word "Independent" and identify it as an auditor's report. Flag any title that omits "Independent" or otherwise deviates from standard form.

- Addressee — confirm the report is addressed to the appropriate party (stockholders, members, partners, board of directors, or governing equivalent). Flag if addressed to management only.

- Opinion section — under SAS 134, the opinion paragraph appears near the beginning of the report, not at the end. Confirm: (1) the section is labeled "Opinion"; (2) it identifies the entity audited; (3) it identifies the financial statements audited by title and the date/period covered; (4) the opinion type is clearly stated (unmodified, qualified, adverse, or disclaimer); (5) the financial reporting framework is correctly named (accounting principles generally accepted in the United States of America); (6) all financial statements cited are included in the opinion. Confirm every statement title cited exactly matches the printed title in the document.

- Basis for Opinion section — confirm it states: (1) the audit was conducted in accordance with auditing standards generally accepted in the United States of America (GAAS); (2) the auditor's responsibilities are described in a subsequent section; (3) the auditor is required to be independent and to meet other ethical responsibilities; (4) the auditor believes audit evidence obtained is sufficient and appropriate. This section is required under SAS 134 — its absence is a significant finding.

- Basis for Qualified or Adverse Opinion or Disclaimer (conditionally required) — required if the opinion is other than unmodified. Confirm it precedes the Opinion section under SAS 134 restructuring, clearly describes the matter giving rise to the modification, and quantifies the effect if practicable. Flag if present with an unmodified opinion.

- Responsibilities of Management for the Financial Statements section — confirm it states that management is responsible for: (1) preparation and fair presentation of the financial statements in accordance with the applicable financial reporting framework; (2) design, implementation, and maintenance of internal control relevant to preparation and fair presentation; (3) evaluation of whether there are conditions or events that raise substantial doubt about the entity's ability to continue as a going concern within one year after the date the financial statements are available to be issued. The going concern responsibility language is required under SAS 134 — flag its absence.

- Auditor's Responsibilities for the Audit of the Financial Statements section — confirm it states: (1) the objectives are to obtain reasonable assurance about whether the financial statements as a whole are free from material misstatement, whether due to fraud or error, and to issue an auditor's report that includes an opinion; (2) reasonable assurance is a high level of assurance but not absolute; (3) misstatements can arise from fraud or error and are considered material if they could reasonably be expected to influence the economic decisions of users. Confirm the section also describes: exercise of professional judgment and skepticism; identification and assessment of risks of material misstatement; obtaining an understanding of internal control; evaluating accounting policies and estimates; evaluating overall presentation; concluding on going concern; and communicating with those charged with governance.

- Emphasis-of-Matter paragraph (conditionally required) — required when the auditor considers it necessary to draw users' attention to a matter appropriately presented or disclosed that is fundamental to users' understanding. Confirm: (1) the paragraph is labeled "Emphasis of Matter"; (2) it references the specific note or disclosure; (3) it states the opinion is not modified with respect to the matter. Common commercial triggers: substantial doubt about going concern (if disclosed and the auditor concurs with management's plans); restatement of prior period financial statements; change in accounting principle; significant subsequent event; significant transaction with a related party that is fundamental to understanding; a major casualty or loss. Flag if any of these conditions appear in the financial statements but no emphasis-of-matter paragraph is present.

- Other-Matter paragraph (conditionally required) — required when the auditor communicates a matter other than those presented or disclosed in the financial statements. Common commercial instances: (1) supplementary information (SI) accompanying the basic financial statements (e.g., consolidating schedules, schedules of operating expenses) — requires the standard SI paragraph; (2) other information (OI) included in a document containing audited financial statements (e.g., a letter from management, selected financial data) — requires the standard OI paragraph under AU-C 720; (3) restriction on use of the auditor's report; (4) reference to predecessor auditor for prior period comparative statements not reissued.

- Substantial Doubt About the Entity's Ability to Continue as a Going Concern section (conditionally required, SAS 134/SAS 132) — if the auditor concludes that substantial doubt exists and management has made appropriate disclosures, a separate section (not an emphasis-of-matter paragraph in the traditional sense) is required. Confirm: (1) it is labeled "Substantial Doubt About the Entity's Ability to Continue as a Going Concern"; (2) it draws attention to the going concern disclosure in the notes; (3) it states the opinion is not modified with respect to the matter. If the going concern disclosure exists but this section is absent, flag it.

- Supplementary Information paragraph (conditionally required) — if consolidating schedules, schedules of operating expenses, or other SI are presented, confirm the paragraph: (1) identifies the SI; (2) states the purpose for which it is presented; (3) states whether the SI was subjected to the auditing procedures applied in the audit of the basic financial statements; (4) states the auditor's conclusion on whether the SI is fairly stated in all material respects in relation to the financial statements as a whole. Flag if SI is present but this paragraph is absent.

- Other Information paragraph (conditionally required under AU-C 720) — if other information is included in a document containing the audited financial statements, confirm the paragraph addresses the OI per AU-C 720 (revised) requirements: management's responsibility for OI; auditor's responsibility to read the OI and consider whether there is a material inconsistency or material misstatement of fact; auditor's conclusion.

- Report on summarized comparative information / predecessor auditor reference (conditionally required under AU-C 700 and AU-C 725) — if prior year comparative figures are presented but not audited in the current engagement, confirm appropriate labeling and report language. If auditors changed and the predecessor auditor's report is not reissued, confirm the current auditor's report references the predecessor in accordance with AU-C 725 — including the predecessor firm name, date of the predecessor's report, type of opinion issued, and any emphasis-of-matter or other-matter paragraphs from the predecessor's report.

- Signature, firm city and state, and report date — confirm the report includes the auditor's signature (firm name), city and state (required under SAS 134), and the report date. Flag if the city and state are omitted (common pre-SAS 134 form lacked this requirement but it is now required).

### Paragraph / section order verification under SAS 134

- Confirm sections appear in the following order: (1) Report title; (2) Addressee; (3) Opinion; (4) Basis for Opinion; (5) [Material uncertainty / Substantial doubt about going concern section, if applicable]; (6) [Emphasis-of-Matter, if applicable]; (7) Responsibilities of Management for the Financial Statements; (8) Auditor's Responsibilities for the Audit of the Financial Statements; (9) [Other-Matter / Report on Supplementary Information / Other Information, if applicable]; (10) Signature, firm city/state, date. Flag any deviation. Pay particular attention to reports that still use the legacy ordering where the opinion paragraph appears at the end — that is a finding under SAS 134.

### No-extra-paragraphs check

- Review every paragraph and section present in the report. For each, identify which required or permitted element it corresponds to. Flag any paragraph that does not correspond to a required, conditionally required, or explicitly permitted paragraph under SAS No. 134 and subsequent SASs. Common erroneous additions include: management representation language that belongs in a letter, not the report; scope limitations not reflected in a modified opinion; commentary on internal control (not required or permitted for private company audits unless a separate ICFR engagement); references to governmental audit standards (GAGAS) that do not apply to commercial engagements.

## Supplementary Information — If Presented as a Separate Report

If consolidating schedules, schedules of operating expenses, or other supplementary information are presented in a separately-titled section (rather than covered only within the main auditor's report as an other-matter paragraph), confirm:

- The SI is clearly labeled and distinguished from the basic financial statements

- Each SI schedule has a title matching any reference in the SI paragraph of the auditor's report

- Any "Independent Auditor's Report on Supplementary Information" is properly structured with required elements

## Other Information (AU-C 720)

- Identify any other information present in the document (e.g., CEO's letter, selected financial data, narrative descriptions not part of the financial statements or notes).

- Confirm the auditor's report includes the required Other Information paragraph under AU-C 720 (revised) if OI is present.

- Confirm the OI does not contain any material inconsistency with the financial statements or any material misstatement of fact apparent on review.

## Prior Year Figures, Comparative Presentations, and Auditor Changes

- If prior year comparative figures are presented, request the prior year issued financial statements if not already provided.

- Agree all beginning balances — retained earnings, partner/member capital accounts, accumulated other comprehensive income (AOCI), treasury stock, and any other equity carryforwards — to the prior year's ending audited figures, regardless of whether a full comparative presentation is made. Flag any beginning balance that cannot be confirmed without the prior year document.

- If the prior year financial statements are provided, confirm all comparative figures agree to the prior year issued report.

- Identify any reclassifications of prior year figures and confirm they are disclosed with an explanation.

- Review accounting policies for consistency with the prior year; if any policy appears to have changed or been newly adopted, flag it and confirm whether the change is disclosed and the effect described under ASC 250.

- If auditors have changed from the prior year and comparative statements are presented, confirm the auditor's report contains proper reference to the predecessor auditor — including the predecessor firm name, date of their report, type of opinion issued, and any emphasis-of-matter or other-matter paragraphs — in accordance with AU-C 725.

- If prior year figures are presented as unaudited, confirm they are labeled as such on the face of the statements and that appropriate disclosure is made.

- Flag any situation where prior year figures appear without audit attribution and without an unaudited label.

## Final Language Checks

- Confirm all names of financial statements cited anywhere in the audit report exactly match the printed titles of those statements in the document.

- Confirm all years and dates referenced in the report are correct for the audit period.

- Confirm the entity's legal form (Inc., LLC, LP, LLP, etc.) is stated consistently between the report and the statements.

# STEP 3 — FULL MATH CHECK

## Excel Source File — Reference Protocol

If an Excel workbook was provided and verified in Step 0, apply the following protocol throughout the math check:

### What the Excel is for:

- Establishing the correct column order and mapping each figure to its column header before performing any arithmetic — especially important for consolidating statements, combining statements, and segment reporting schedules

- Resolving ambiguous subtotals — where it is unclear from the PDF which line items are intended to sum to a given subtotal, use the Excel to confirm the intended scope of the sum

- Explaining discrepancies — hidden rows, figures displayed as rounded integers but stored as decimals internally, and other Excel-specific artifacts that would cause the printed document to appear not to foot when the underlying data is consistent

- Calibrating your understanding of how the numbers add up before applying that understanding to the PDF

### What the Excel is NOT for:

- Proofing the Excel itself — do not audit formulas, flag Excel errors, or comment on the workbook's construction

- Gospel — the Excel may contain formula errors. If the PDF and Excel disagree on a total, do not automatically defer to the Excel. Flag the discrepancy and note that either the PDF or the Excel may be wrong, and that the preparer should verify

- Overriding a genuine error — if a figure in the PDF does not foot and the Excel agrees with the incorrect total, the error still exists in the printed document and must be flagged

### Formatting conventions and subtotal scope:

- The Excel establishes which figures are intended to sum to a given subtotal — it does NOT establish whether that subtotal is presented correctly in the printed document.
- If the printed document's formatting conventions (underlines, double underlines, indentation, spacing, section headers) suggest a subtotal should capture a different set of line items than what the Excel actually sums, flag it. State: what the formatting implies should be included, what the Excel actually sums, and that the preparer should confirm which is intended.
- If the same formatting convention is used elsewhere in the document to mean something different than here, that inconsistency is itself a finding regardless of whether the math is correct.

### Column mapping procedure (required for any statement with three or more data columns):

1. Before performing any arithmetic on a statement with three or more data columns (consolidating statements, combining statements, segment reports, multi-period comparatives), write out the column map in this format:
   *Column 1: [Header name] | Column 2: [Header name] | ... | Column N: [Total column header]*
   *Confirmed against: Excel tab "[tab name]"*
2. State which columns are intended to sum to which totals — horizontally across rows and vertically down columns — before calculating anything.
3. For consolidating statements, identify which column is the elimination column and confirm the sign convention (eliminations typically appear as negative adjustments).
4. Do not perform arithmetic until this mapping is written out and confirmed against the Excel.

### Rounding — zero tolerance:

1. Every column in the printed document must foot to the printed total exactly. A difference of any amount — including $1 — is a finding.
2. If the Excel shows figures stored with decimal precision and displayed as rounded integers, flag it and note this as the likely cause; resolution requires the preparer to adjust one displayed line item to force the printed figures to foot. Rounding is an explanation, not an excuse — flag it regardless.
3. If a column does not foot and the difference cannot be explained by rounding, flag it and note that hidden rows in the Excel workbook may account for the discrepancy — the preparer must verify.

### PDF extraction caveat — when Excel is not provided:

When the Excel workbook has NOT been provided and a math finding arises on a statement with three or more data columns, the finding MAY be an artifact of PDF extraction rather than a real error in the document. PDF text extraction can flatten table layouts, misattribute figures to adjacent columns, or drop values entirely — especially on dense consolidating or combining schedules. Before flagging a multi-column math finding as a document error in this situation, do the following:

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

- In consolidating statements, combining statements, and segment reports, confirm all columns add correctly across each row and down each column. For consolidating statements, confirm: (entity 1 + entity 2 + ... + eliminations = consolidated).

### Subtotals and totals at every level:

- Where totals are built from subtotals, verify each subtotal independently, then verify the total as the sum of the subtotals.

### Balance Sheet / Statement of Financial Position:

- Confirm total assets equals total liabilities and equity.

- Confirm current vs. non-current classification totals foot to the grand totals.

### Income Statement / Statement of Operations:

- Confirm gross profit = revenue − cost of sales (if presented with this structure).

- Confirm operating income = gross profit − operating expenses.

- Confirm income before taxes = operating income + other income/(expense).

- Confirm net income = income before taxes − income tax expense.

- Confirm any per-share data (if presented — rare in private companies but occurs in ESOPs and some closely-held structures): weighted average shares, basic EPS, diluted EPS all internally consistent.

### Statement of Stockholders'/Members'/Partners' Equity:

- Foot every column of equity rollforward (common stock, APIC, retained earnings, treasury stock, AOCI for corporations; member contributions, distributions, income allocations, ending capital for LLCs; partner capital accounts with separate columns per partner or class for partnerships).

- Confirm beginning balance + changes = ending balance for each equity component.

- Confirm the ending equity total equals the total equity on the balance sheet.

- For partnerships and multi-member LLCs, confirm income/loss allocations across partners/members sum to total net income/loss on the income statement.

- For S corporations, confirm AAA, PTI, OAA, and other S-corp-specific equity accounts (if disclosed) rollforward correctly.

### Statement of Cash Flows:

- Confirm operating, investing, and financing totals sum to net change in cash.

- Confirm net change in cash + beginning cash = ending cash, and ending cash ties to the balance sheet.

- Confirm the indirect method reconciliation starts with net income that matches the income statement.

- Confirm any supplemental disclosures (interest paid, taxes paid, non-cash investing/financing) are internally consistent with the notes.

### Debt Schedules:

- Foot all maturity schedules. Confirm totals agree to the applicable note disclosure and to the face of the financial statements.

- Confirm current portion of long-term debt + long-term debt = total debt per the note and the balance sheet.

### Capital Asset / Fixed Asset Schedules:

- Foot beginning balances, additions, disposals, and ending balances.

- Confirm accumulated depreciation rollforward ties.

- Confirm net PP&E ties to the balance sheet.

### Lease Schedules (ASC 842):

- Foot right-of-use asset rollforward and lease liability rollforward.

- Confirm the maturity schedule of lease payments ties to the lease liability note disclosure.

### Inventory Schedules:

- Foot any disclosed inventory components (raw materials, WIP, finished goods, reserves).

### Consolidating / Combining Schedules:

- Confirm each subsidiary column foots independently.

- Confirm eliminations column is internally consistent (assets eliminated against liabilities; intercompany revenues eliminated against intercompany expenses).

- Confirm the consolidated/combined column equals the sum of component entities plus eliminations.

**NOTE:** *Flag every instance where a figure does not recalculate correctly, with the location, the presented figure, and the recalculated figure.*

# STEP 4 — CROSS-REFERENCE AND CONSISTENCY CHECK

Identify every number that appears in more than one location in the document and confirm all instances agree. At minimum, check:

## Equity / Net Assets

- Confirm ending balances on the balance sheet agree to the statement of stockholders'/members'/partners' equity ending balances, to any equity-related note disclosures, and to any narrative references.

- For partnerships and LLCs, confirm partner/member capital ending balances in any detailed capital account note agree to the statement of equity.

## Revenue and Expense Totals

- Confirm totals on the face of statements agree to any segment disclosure, product-line disclosure, or geographic disclosure in the notes.

- Confirm revenue recognition note disclosures (ASC 606) reconcile to the income statement revenue total — disaggregation of revenue should sum to total revenue.

## Depreciation and Amortization

- Confirm depreciation expense per the income statement (or per the notes if disclosed separately) agrees to depreciation as a reconciling item on the statement of cash flows and to the accumulated depreciation change in the PP&E rollforward.

- Confirm amortization of intangibles, deferred financing costs, and right-of-use assets (if applicable) are internally consistent across the income statement, cash flow statement, and relevant notes.

## Long-Term Debt

- Confirm the total outstanding balance per the debt footnote agrees to the face of the financial statements (long-term debt + current portion).

- Confirm the current portion of long-term debt on the balance sheet agrees to the amount maturing in the next year per the maturity schedule in the footnotes.

- Confirm interest expense per the income statement is plausible given the disclosed interest rates and balances — this is a reasonableness check rather than a tie-out, flag material inconsistencies.

## Capital / Fixed Assets

- Confirm beginning balances, additions, disposals, and ending balances in the capital assets note roll-forward are internally consistent.

- Confirm ending net PP&E balance agrees to the face of the statements.

- Confirm depreciation expense in the PP&E rollforward ties to depreciation in the cash flow statement and to any disclosure in the income statement.

## Leases (ASC 842)

- Confirm right-of-use asset and lease liability balances per the lease note agree to the face of the balance sheet.

- Confirm the total undiscounted lease payments per the maturity schedule reconcile to the present-value lease liability via the disclosed discount factor.

- Confirm operating lease expense and finance lease components per the note agree to any income statement line items or disclosures.

## Intangibles and Goodwill

- Confirm goodwill rollforward (if applicable) ties to the balance sheet.

- Confirm intangible asset rollforward (gross, accumulated amortization, net) ties to the balance sheet.

- If the PCC goodwill amortization alternative has been elected, confirm amortization is being recorded and the useful life disclosed.

- Confirm impairment charges (if any) are disclosed consistently across the note, income statement, and cash flow statement.

## Income Taxes

- For C corporations: confirm current and deferred tax provision on the income statement agrees to the tax note; confirm deferred tax assets/liabilities per the balance sheet tie to the components disclosed in the tax note; confirm any valuation allowance is disclosed with reconciling detail.

- For S corporations, partnerships, and LLCs taxed as partnerships: confirm pass-through tax disclosures are appropriate — typically no federal income tax provision (other than state-level pass-through entity taxes, built-in gains tax for S-corps, or other entity-level taxes that may apply). Flag any federal income tax provision on an entity that appears to be taxed as a pass-through unless entity-level taxes are specifically explained.

- For state and local income taxes: confirm the state tax provision is disclosed and plausible.

- Confirm uncertain tax positions (ASC 740-10) are addressed — either with disclosed unrecognized tax benefits or with a statement that none exist.

## Cash and Investments

- Confirm total cash and cash equivalents per the balance sheet agrees to the cash flow statement ending cash.

- Confirm restricted cash (if any) is reconciled between the balance sheet and cash flow statement per ASU 2016-18.

- Confirm investments (if any) tie to any fair value disclosures (ASC 820) with consistent Level 1/2/3 classifications.

## Receivables

- Confirm accounts receivable, allowance for credit losses (CECL under ASC 326 if adopted, or legacy allowance), and net receivables per the balance sheet tie to any detail schedule in the notes.

- Confirm related-party receivables (if any) disclosed in the related-party note tie to any separate balance sheet line item or parenthetical disclosure.

## Payables

- Confirm accounts payable and accrued expenses tie to any detail disclosure in the notes.

- Confirm related-party payables (if any) are disclosed consistently.

## Revenue Recognition (ASC 606)

- Confirm disaggregated revenue disclosures sum to total revenue on the income statement.

- Confirm contract assets, contract liabilities, and deferred revenue balances per the note agree to the balance sheet.

- Confirm beginning and ending contract liability balances roll forward with revenue recognized from the beginning balance, as disclosed.

## Commitments and Contingencies

- Confirm any accrued loss contingencies tie to any related balance sheet line item.

- Confirm commitments (purchase commitments, employment agreements, guarantees) are internally consistent with any related note or schedule.

## Related Party Transactions (ASC 850)

- Confirm every related-party balance disclosed is reflected on the balance sheet in the expected line item.

- Confirm every related-party transaction disclosed (revenues, expenses, management fees, rent, loans) is reflected on the income statement and cash flow statement as appropriate.

- Confirm intercompany balances for consolidated statements are fully eliminated.

## Prior Year Figures

- Confirm prior year comparative figures (if presented) are internally consistent with each other throughout the document.

- Where prior year audited statements are available for reference, confirm comparative figures agree.

- Confirm beginning balances (retained earnings, capital accounts, AOCI) agree to prior year ending audited balances. Flag any that cannot be confirmed without the prior year report.

## Footnote Figures

- Confirm every figure cited in the footnotes agrees to the corresponding line item on the face of the financial statements.

- Confirm all cross-references between footnotes are accurate.

**NOTE:** *Identify any other figure appearing in multiple locations and confirm consistency. Flag every discrepancy with location, expected figure, and actual figure found.*

## Paired-Account Relationship Analysis

- Beyond checking the plausibility of individual balances, assess whether accounts that logically travel together are both present, both absent, or in a sensible proportion (disclosure omissions and classification errors often surface through what is missing).
- Rule for each pair below: if one account is present at a material level, the other should also be present (or its absence explained). If both are present, assess whether their relationship is plausible.
- The list below is representative, not exhaustive — apply experienced reviewer judgment to identify other paired relationships not listed here.

### Operations and expenses

- **Payroll expense → payroll tax expense and accrued payroll taxes.** Salaries/wages/compensation of any meaningful size should be accompanied by payroll tax expense (employer FICA, Medicare, FUTA, SUTA) and typically an accrued payroll tax liability at period end. Payroll with no payroll tax expense is a flag. Payroll tax expense that is implausibly low relative to compensation (rule of thumb: employer payroll taxes run roughly 7.65%–10% of wages below wage-base limits) is a flag.

- **Payroll expense → retirement plan expense or disclosure.** Entities with significant W-2 employees typically offer some form of retirement benefit (401(k), SIMPLE, SEP, pension). Absence of any retirement plan note is not necessarily a finding, but is worth confirming for entities of meaningful size.

- **Payroll expense → workers' compensation insurance expense.** Entities with employees (in virtually all states) carry workers' comp coverage. Flag absence for entities with significant payroll.

- **Contract labor / 1099 expense → absence of payroll tax on that amount.** Confirm contract labor is classified separately from W-2 payroll and is not generating payroll tax expense.

- **Cost of goods sold / cost of sales → inventory.** An entity reporting COGS should generally have inventory on the balance sheet (unless it is a pure service or drop-ship model). COGS with zero inventory warrants confirmation that the business model does not require inventory. Inventory on the balance sheet with no COGS on the income statement is also a flag.

- **Inventory → inventory reserves / obsolescence allowance.** Entities with meaningful inventory typically have some reserve or reserve policy disclosed. Absence is not automatically a finding but is worth flagging for larger inventory balances.

- **Revenue → cost of revenue / cost of sales.** Revenue with no direct cost presented (and no explanation that the entity is pure services without identifiable direct costs) is a flag.

- **Sales revenue → sales tax payable (for applicable jurisdictions and industries).** Retail, restaurant, and similar entities with taxable sales should show sales tax payable or a statement that sales tax is collected and remitted.

### Property, plant, and equipment

- **Land → buildings and/or building improvements.** Land by itself without buildings or improvements is unusual for an operating entity (possible for pure real estate holding or undeveloped land — confirm). Buildings without land is also unusual except in leased-ground or air-rights situations — confirm.

- **Buildings / equipment / vehicles → depreciation expense and accumulated depreciation.** Any depreciable asset class should have corresponding depreciation expense and accumulated depreciation. Gross PP&E with zero depreciation expense is a flag unless assets were all placed in service at year end.

- **Vehicles → auto / fuel / vehicle insurance expense.** Vehicles on the balance sheet should correspond to related operating expenses on the income statement. Flag absence.

- **Land and buildings → property tax expense and/or real estate tax expense.** Owned real estate generates property tax. Flag absence.

- **Real property → property insurance expense.** Owned real property should carry insurance; flag absence.

- **Construction in progress → absence of depreciation on CIP balance.** CIP should not be depreciated until placed in service. Flag if depreciation appears to be running on CIP.

- **Leasehold improvements → operating lease presence (ASC 842) or ownership of the underlying property.** Leasehold improvements imply a lease; confirm corresponding lease liability and ROU asset exist.

### Debt and financing

- **Notes payable / long-term debt → interest expense.** Any interest-bearing debt should generate interest expense. Flag debt with no corresponding interest expense. Conversely, interest expense with no debt on the balance sheet is a flag (possible off-balance-sheet financing, related-party debt undisclosed, or missing current portion).

- **Line of credit → interest expense and, typically, unused line fees.** LOC should generate interest on drawn balances; confirm both.

- **Debt → debt issuance costs (deferred financing costs) presentation.** For material debt, confirm treatment of financing costs (direct reduction of debt under ASU 2015-03 for term debt; asset presentation permitted for revolving credit).

- **Convertible debt / mezzanine debt → ASC 470 / ASC 480 classification disclosure.** Flag convertible or hybrid instruments without corresponding classification disclosure.

- **Long-term debt → current portion on balance sheet.** Long-term debt with zero current portion is a flag unless the maturity schedule confirms no principal is due within 12 months.

- **Interest expense → interest payable (accrued interest).** Material interest expense typically has some accrual at period end unless all debt pays interest monthly on period-end dates.

### Leases (ASC 842)

- **Rent / lease expense on income statement → ROU asset and lease liability on balance sheet.** Under ASC 842, operating lease expense implies both ROU asset and lease liability (unless all leases are short-term under 12 months, which should be disclosed as a practical expedient election).

- **ROU asset → lease liability.** These are paired by construction; material imbalance warrants review (prepaid rent, lease incentives, initial direct costs can create differences but should be explainable).

- **Leased real estate described in operations → corresponding ROU asset and lease liability.** If MD&A, nature of business, or notes describe leased premises, confirm lease accounting is reflected.

### Receivables and revenue

- **Accounts receivable → credit loss allowance (CECL under ASC 326).** Material receivables should have a disclosed credit loss allowance or a statement that none is necessary. Zero allowance on material AR warrants confirmation.

- **Revenue (ASC 606) → contract assets and contract liabilities.** Entities with any timing difference between performance and billing typically have contract assets or contract liabilities. Their absence on meaningful revenue is worth confirming.

- **Deferred revenue → revenue recognition timing disclosure.** Deferred revenue on the balance sheet should correspond to disclosed performance obligations and revenue recognition pattern.

### Payables and accruals

- **Accounts payable → corresponding expense accounts.** AP of meaningful size implies operating expense activity; zero AP with significant operating expenses is unusual.

- **Accrued compensation → payroll expense.** Accrued bonuses, vacation, PTO should reconcile to compensation policies disclosed.

- **Accrued professional fees → professional fees expense on income statement.**

### Equity, contributions, and distributions

- **Distributions/dividends on statement of equity → cash outflow on financing section of cash flow statement.** Should tie exactly.

- **Stock issuances / capital contributions → cash inflow from financing activities.** Should tie exactly.

- **Treasury stock or member redemptions → cash outflow on financing activities.** Should tie exactly.

### Taxes

- **Pre-tax income → tax provision (C corporations).** Material pre-tax income with zero or immaterial tax provision is a flag unless fully explained by NOL utilization, valuation allowance release, or similar (which should be disclosed in the rate reconciliation).

- **Deferred tax assets (NOL carryforwards) → valuation allowance assessment.** Material DTAs should have disclosed valuation allowance analysis.

- **State tax provision → multi-state operations disclosure.** Material state taxes imply multi-state nexus; confirm consistency with any described operating footprint.

- **S-corp / partnership / LLC pass-through → absence of federal income tax provision.** Pass-through entities should have no federal income tax provision (other than state-level PTE taxes, built-in gains tax, or other entity-level taxes). Flag any federal income tax provision on an entity that appears to be taxed as a pass-through unless entity-level taxes are specifically explained.

### Insurance and risk

- **Operating activity → general liability, D&O, E&O insurance expense.** Material operating entities carry some form of liability insurance; absence is worth confirming for larger entities.

### Investments and cash

- **Investments on balance sheet → investment income on income statement.** Material investments should produce interest, dividend, or realized/unrealized gain activity.

- **Restricted cash → nature of restriction disclosure.** Restricted cash requires disclosure of the nature of the restriction.

### Intangibles and goodwill

- **Goodwill → prior business combination disclosure.** Goodwill on the balance sheet implies a prior acquisition — confirm ASC 805 business combination disclosure exists (even if historical), or confirm policy on goodwill amortization (if PCC alternative elected) / impairment.

- **Amortizable intangibles → amortization expense and accumulated amortization.** Gross intangibles with zero amortization is a flag unless all are indefinite-lived.

### Related party signals

- **Related-party receivables or payables → corresponding income/expense disclosure.** Related-party balances typically accompany related-party transactions; confirm both disclosed.

- **Management fees paid to related party → related party note.** Any related-party expense should be captured in the ASC 850 disclosure.

### Procedural guidance

For each relationship flagged:

- State what account is present and what the expected paired account would be

- State whether the paired account is absent, present but implausibly sized, or present and reasonable

- Classify as a disclosure / completeness question, a classification question, or a reasonableness question

- Note that the reviewer should confirm — many of these flags have legitimate explanations (pure service models, leased-ground arrangements, year-end placements, newly formed entity with no prior period activity, etc.). The objective is to surface the relationship for review, not to assert an error.

**NOTE:** *Apply this analysis in combination with the logical and contextual consistency checks below. A finding may appear in either or both sections; flag it once with a cross-reference.*

## Logical and Contextual Consistency

- Beyond verifying that figures tie to their counterparts, assess whether the financial statements make logical and contextual sense as a whole — not mathematical agreement, but whether numbers, disclosures, and narrative are internally coherent and plausible given the entity's described circumstances.
- Flag anything that a knowledgeable reader would find implausible, inconsistent, or unexplained. Non-exhaustive list of issues to check:

- Revenue plausibility — assess whether revenue is reasonable for the entity type, industry, and scale described. Flag significant revenue streams with no corresponding disclosure (revenue recognition policy, major customers, segments).

- Gross margin plausibility — assess whether gross margin is reasonable for the described industry. Flag gross margins that appear implausibly high or low relative to industry norms without explanation (e.g., 90% gross margin on a manufacturing entity, negative gross margin without disclosed restructuring).

- Cash and bank balance reasonableness — where cash balances appear disproportionate to operations (e.g., cash balance far exceeding total revenue for an operating entity, or cash near zero for an entity with disclosed positive operating cash flow), flag for reasonableness.

- Debt and interest plausibility — assess whether disclosed debt balances, interest rates, and maturity schedules are mutually consistent and plausible. Flag interest rates that appear anachronistic for the type or vintage of debt disclosed (e.g., 3% rate on a loan dated 2023 when market rates were materially higher), or interest expense that is inconsistent with the disclosed average balance × rate.

- Debt covenants — if debt covenants are disclosed, assess whether the disclosed financial metrics (leverage ratio, DSCR, minimum EBITDA, working capital, tangible net worth) appear consistent with the reported financial results. Flag any apparent covenant violation that is not disclosed as a waiver, subsequent-event cure, or going-concern indicator. If the entity is in apparent compliance, no finding is required — this is only to flag apparent violations without corresponding disclosure.

- Going concern indicators — flag any of the following if present without corresponding disclosure of management's plans and the auditor's evaluation: negative working capital of material size; recurring losses from operations; negative cash flow from operations; stockholders'/members'/partners' deficit; debt covenant violations; loan maturities within 12 months without disclosed refinancing; loss of major customer; material adverse legal judgments; material reliance on a single customer or supplier.

- Capital asset activity reasonableness — assess whether additions, disposals, and depreciation amounts are plausible given the entity's disclosed asset base, useful life policies, and any capital project disclosures. Flag depreciation that appears implausibly high or low relative to the gross asset balance and stated useful lives.

- Lease activity reasonableness (ASC 842) — assess whether lease ROU assets, lease liabilities, and lease expense are plausible given the described operations. Flag entities with significant real estate or equipment operations and no lease disclosures (potential missed application of ASC 842).

- Related party reasonableness — assess whether related-party transactions are plausibly arms-length or, if non-arms-length, whether they are disclosed as such. Flag material related-party transactions with no disclosure of terms. For common private company structures (operating company + related-party real estate LLC), flag absence of either (a) consolidation/VIE analysis or (b) the PCC common-control leasing scope exception election.

- Equity rollforward plausibility — for partnerships and LLCs, assess whether partner/member capital allocations are consistent with the disclosed allocation provisions in the entity agreement (if disclosed in the notes). Flag income/loss allocations that appear inconsistent with disclosed sharing percentages.

- Distributions and draws — for pass-through entities, assess whether distributions/draws disclosed on the equity statement are plausible relative to tax allocations. Flag distributions materially in excess of taxable income allocations without explanation, or zero distributions for a profitable pass-through without explanation (owners typically receive tax distributions at minimum).

- Tax provision reasonableness — for C corporations, assess whether the effective tax rate disclosed in the tax note reconciliation is plausible. Flag ETRs that are significantly different from the statutory rate with inadequate reconciling explanation. For S corps and partnerships, flag the presence of any federal income tax provision.

- General implausibility — apply experienced reviewer judgment to flag any balance, ratio, trend, or disclosure that, while potentially mathematically consistent, would strike a knowledgeable reader as unusual, unexplained, or inconsistent with the entity's described operations, size, industry, or circumstances.

# STEP 5 — GAAP (ASC) DISCLOSURE AND TECHNICAL REVIEW

Perform a full technical review for compliance with applicable FASB Accounting Standards Codification (ASC) requirements.

## ASC Standards Applicable to Entity Type

- Identify applicable ASC standards for the entity type and confirm the financial statements are presented in accordance with those standards. Standards to consider include but are not limited to:

- ASC 205 — Presentation of Financial Statements; confirm the required basic financial statements are present (see Completeness of Financial Statements below)

- ASC 210 — Balance Sheet; current vs. non-current classification

- ASC 220 — Income Statement / Comprehensive Income; if AOCI components exist, confirm Statement of Comprehensive Income (or combined presentation) is included

- ASC 230 — Statement of Cash Flows; confirm direct or indirect method is consistently applied, required reconciliations present

- ASC 250 — Accounting Changes and Error Corrections; confirm any change in principle, estimate, or correction of an error is appropriately disclosed with comparative effects

- ASC 260 — Earnings Per Share (only if applicable — rare for private companies without public market)

- ASC 280 — Segment Reporting (only if applicable — rare for private companies but sometimes presented voluntarily)

- ASC 305/310/326 — Cash, Receivables, Credit Losses (CECL under ASC 326 effective for private companies — confirm adoption and disclosure)

- ASC 321/320/325 — Investments in equity/debt securities

- ASC 323/325 — Equity method investments

- ASC 330 — Inventory; confirm costing method disclosed (FIFO, LIFO, weighted average, specific identification) and presentation

- ASC 350 — Intangibles (including goodwill); confirm whether PCC alternative to amortize goodwill has been elected (ASU 2014-02) and whether the simplified impairment test has been elected (ASU 2017-04)

- ASC 360 — Property, Plant, and Equipment; confirm depreciation methods and useful lives disclosed; impairment analysis if indicators exist

- ASC 410 — Asset Retirement and Environmental Obligations (if applicable)

- ASC 450 — Contingencies; confirm loss contingency accruals and disclosures for reasonably possible losses

- ASC 460 — Guarantees; confirm disclosure of any guarantees

- ASC 470 — Debt; classification of current vs. long-term, covenant disclosures, debt modifications/extinguishments

- ASC 480 — Distinguishing Liabilities from Equity; classification of mandatorily redeemable instruments

- ASC 505 — Equity; confirm all equity transactions appropriately disclosed

- ASC 606 — Revenue from Contracts with Customers (fully effective for all private companies); confirm: revenue recognition policy disclosure, performance obligation identification, disaggregation of revenue, contract balance disclosures, significant judgments

- ASC 705 — Cost of Sales and Services

- ASC 710/712/715 — Compensated absences, nonretirement postemployment benefits, retirement benefits (if defined benefit plans — rare in private companies but occurs)

- ASC 718 — Stock Compensation (if any equity-based compensation exists; use practical expedient for nonpublic entities)

- ASC 740 — Income Taxes; deferred tax accounting for C corporations, uncertain tax positions for all entity types

- ASC 805 — Business Combinations (if applicable); PCC alternatives under ASU 2014-18

- ASC 810 — Consolidation and VIE analysis; for private companies, confirm whether the PCC scope exception for common-control leasing arrangements (ASU 2014-07 / ASU 2018-17) has been elected

- ASC 815 — Derivatives and Hedging; if hedging activity exists, confirm whether the simplified hedge accounting PCC alternative (ASU 2014-03) has been elected for plain-vanilla interest rate swaps

- ASC 820 — Fair Value Measurement; Level 1/2/3 disclosures for recurring and non-recurring measurements

- ASC 825 — Financial Instruments; fair value disclosures for financial instruments

- ASC 830 — Foreign Currency (if applicable)

- ASC 842 — Leases (fully effective for all private companies); confirm ROU assets and lease liabilities on balance sheet, maturity schedule, practical expedient elections, related-party lease disclosures

- ASC 850 — Related Party Disclosures; confirm complete disclosure of nature of relationships, transactions, balances, and terms

- ASC 855 — Subsequent Events; confirm evaluation period disclosed and events disclosed or confirmed none identified

- ASC 860 — Transfers and Servicing (if applicable)

- ASC 926-952 — Industry-specific guidance where applicable

## ASC Standards — Recently Effective and PCC Alternatives

- Identify the fiscal year end date of the financial statements.

- Confirm the following recently effective standards for private companies are adopted as applicable: ASC 326 Credit Losses (CECL) — effective for annual periods beginning after December 15, 2022; ASC 842 Leases — effective for annual periods beginning after December 15, 2021; ASU 2020-06 on convertible instruments and contracts in an entity's own equity.

- List Private Company Council (PCC) alternatives potentially applicable: goodwill amortization (ASU 2014-02), simplified hedge accounting (ASU 2014-03), common-control leasing VIE scope exception (ASU 2014-07 / ASU 2018-17), intangibles in business combinations (ASU 2014-18), share-based payment practical expedients (ASU 2021-07). For each, assess whether the entity's fact pattern suggests consideration, and confirm either that the alternative is elected and disclosed, or that it is not elected.

- Do not rely on management's boilerplate disclosure that no new standards have a significant impact — evaluate each standard independently based on the entity's presented balances and disclosures.

- Flag any standard that appears applicable and shows no evidence of adoption or disclosure.

## Completeness of Financial Statements

Before confirming completeness, perform the following identification and inference procedure. Do not assume a fixed template — derive the expected statement package from the document itself.

### Step 1 — Identify the entity's required statement package

Under U.S. GAAP, a complete set of financial statements for a commercial entity generally includes:

- Balance Sheet (Statement of Financial Position) — required

- Income Statement (Statement of Operations / Statement of Income) — required

- Statement of Comprehensive Income — required if any items of other comprehensive income exist; may be combined with the income statement or presented separately

- Statement of Stockholders'/Members'/Partners' Equity — required

- Statement of Cash Flows — required

- Notes to the Financial Statements — required

Additional schedules may be presented as supplementary information:

- Consolidating balance sheet and income statement (for consolidated groups)

- Combining schedules (for entities under common control presented on a combined basis)

- Schedules of operating expenses, cost of goods sold, general and administrative expenses

- Segment disclosures (if voluntarily presented)

### Step 2 — Confirm required statements are present

Based on the entity's circumstances, confirm all required statements are present. Flag any absent statement:

- If the entity has any items of other comprehensive income (foreign currency translation, unrealized gains/losses on available-for-sale securities, pension/OPEB adjustments, effective cash flow hedges), confirm a Statement of Comprehensive Income is presented (either combined with the income statement or separately). If AOCI appears on the balance sheet but no statement of comprehensive income exists, flag it.

- Confirm the statement of equity appropriately reflects the entity's legal form — stockholders' equity for corporations, members' equity for LLCs, partners' capital for partnerships.

- For consolidated or combined entities, confirm consolidating/combining schedules are presented if the auditor's report references them as SI.

### Step 3 — Cross-check statements against all document references

Confirm that the statements present in the document are consistent with all references to statements throughout the document. Specifically:

- The auditor's opinion paragraph cites specific statement titles — confirm every cited statement is physically present in the document with a matching title. Flag any cited statement that cannot be located.

- The summary of significant accounting policies describes activities or balances that imply certain statements are required (e.g., "the Company's functional currency is the U.S. dollar; foreign operations are translated using..." implies other comprehensive income). Confirm corresponding statements are present.

- Any note that discusses a balance or activity implies that balance is present on the relevant statement. A note discussing stock-based compensation with no equity statement line item for it is a potential omission.

## Required Footnote Disclosures

Confirm the footnotes include all required disclosures for every balance and transaction type presented, including at minimum:

- Summary of Significant Accounting Policies — confirm it addresses: nature of operations and description of the entity; basis of presentation (consolidated, combined, standalone); principles of consolidation (if applicable); use of estimates; cash and cash equivalents definition; revenue recognition (ASC 606 policies, performance obligations, significant judgments); accounts receivable and credit losses (CECL); inventory (method and valuation); property and equipment (depreciation methods, useful lives); leases (ASC 842 policies, practical expedients); intangibles and goodwill; impairment policies; income taxes (including treatment for pass-through entities); advertising costs; shipping and handling; fair value measurements; recent accounting pronouncements; any PCC alternatives elected

- Nature of Business / Organization — description of the entity's operations, legal form, ownership structure, and key locations

- Cash and cash equivalents — definition, any restrictions, concentrations at financial institutions above FDIC limits

- Accounts receivable — aging or risk disclosures, allowance rollforward if material, CECL disclosures under ASC 326

- Inventory — components (raw materials, WIP, finished goods), LIFO reserve if applicable

- Property and Equipment — components, accumulated depreciation, depreciation expense, capitalization policies

- Intangibles and Goodwill — components, amortization (including PCC alternative if elected), impairment assessment

- Leases (ASC 842) — components of lease cost, weighted average remaining lease term, weighted average discount rate, maturity analysis, ROU assets and lease liabilities by classification, related-party leases

- Long-term Debt — components, interest rates, maturity schedule (next 5 years + thereafter), covenant disclosures, collateral

- Line of Credit — maximum availability, outstanding balance, interest rate, maturity, covenants, collateral

- Equity / Capital Accounts — for corporations: authorized, issued, outstanding shares; for LLCs and partnerships: description of ownership classes, allocation provisions, distribution provisions, mandatory vs. discretionary distributions

- Stock-Based Compensation (if any) — plan description, activity, assumptions used in valuation, expense recognized

- Income Taxes — for C corporations: current and deferred components, rate reconciliation, deferred tax assets/liabilities by type, valuation allowance rollforward, NOL and credit carryforwards; for pass-throughs: disclosure of pass-through status, any entity-level taxes (state PTE, built-in gains, etc.); for all entities: uncertain tax positions (ASC 740-10) including any unrecognized tax benefits

- Revenue from Contracts with Customers (ASC 606) — disaggregated revenue, contract balances (contract assets, contract liabilities), significant payment terms, significant judgments, remaining performance obligations (if material)

- Retirement Plans — description of defined contribution plan and employer contributions; if defined benefit, full ASC 715 disclosures

- Related Party Transactions (ASC 850) — relationships, transactions, balances, terms. Common in closely-held entities: common-control real estate LLCs, management fees, related-party loans, shareholder/member loans

- Commitments and Contingencies — loss contingencies (accrued and reasonably possible), purchase commitments, employment agreements, guarantees, legal proceedings

- Concentrations — customer concentrations, supplier concentrations, geographic concentrations, credit concentrations

- Fair Value Measurements — recurring and non-recurring, Level 1/2/3 classifications, reconciliations for Level 3

- Subsequent Events — evaluation date, events disclosed or statement that none were identified. Confirm the evaluation date is through the date the financial statements were available to be issued (not just through the auditor's report date)

- Recent Accounting Pronouncements — pronouncements issued but not yet adopted, with expected effect

- Any other disclosures required for balances or transactions present in the financial statements

## Accounting Policy Changes

- Review accounting policies disclosed in the current year against those in the prior year report if available.

- Flag any policy that appears to have been added, removed, or modified without disclosure of a change in accounting principle under ASC 250.

- If a new standard adoption explains the change (e.g., first-year ASC 842 adoption), confirm that the adoption is explicitly disclosed with the transition method and cumulative effect if any.

## Going Concern — Document-Based Assessment

Under ASU 2014-15 (ASC 205-40), management is required to evaluate whether there are conditions or events that raise substantial doubt about the entity's ability to continue as a going concern within one year after the date the financial statements are available to be issued. Flag the following if present and note that the engagement team should confirm the evaluation was performed and appropriately disclosed:

- Recurring losses from operations or negative operating cash flows

- Working capital deficit or current-liability excess

- Stockholders'/members'/partners' deficit (negative total equity)

- Debt covenant violations or waivers

- Loan maturities within 12 months of financial statement issuance date without disclosed refinancing or extension

- Loss of a major customer or supplier

- Material legal judgments or settlements

- Disclosure language in the notes referencing financial difficulty, liquidity concerns, or recovery plans

- Any management disclosure explicitly addressing going concern evaluation under ASC 205-40 — confirm it discusses both conditions raising substantial doubt and management's plans to alleviate it
- If going concern language appears in the notes, confirm the auditor's report contains the corresponding Substantial Doubt About the Entity's Ability to Continue as a Going Concern section (or emphasis-of-matter paragraph in older SAS 132 structure) referencing the note.

## Subsequent Events (ASC 855)

- Confirm a subsequent events note is present.

- Confirm the evaluation date is disclosed and is through the date the financial statements were available to be issued. For private companies, this date typically matches or is close to the auditor's report date.

- If the report is issued significantly after fiscal year end, flag the extended subsequent events window and confirm all material subsequent events are appropriately classified as Type I (recognized) or Type II (non-recognized / disclosed only).

## Consolidation and VIE (ASC 810)

- For consolidated financial statements, confirm the principles of consolidation note describes the entities consolidated and the basis (voting interest model, VIE model).

- For private companies with common-control leasing arrangements or other common-control related parties, assess whether VIE analysis appears to have been considered. If the PCC common-control scope exception (ASU 2018-17) has been elected, confirm required disclosures are made.

- Confirm all intercompany balances and transactions are eliminated in consolidation.

- If combined statements are presented instead of consolidated, confirm the combined basis is appropriate (entities under common control) and eliminations are appropriately applied.

## Accounting Standards — General

- Review all presented balances and transactions for apparent conformity with U.S. GAAP.

- Flag any amounts or presentations that appear to deviate from applicable standards, including unusual classifications, balances inconsistent with disclosed accounting policies, or presentations that differ from standard practice.

## Entity-Type-Specific Technical Review

### Corporations (C-corp and S-corp)

- Confirm authorized, issued, and outstanding share data for each class of stock is disclosed

- Confirm par or stated value disclosed

- Confirm treasury stock method disclosed (cost or par method) and presentation consistent with method

- For S corporations: confirm pass-through tax treatment disclosed; consider whether AAA, OAA, PTI disclosures are appropriate (not required by GAAP but commonly included for closely-held S-corps)

- For S corporations with built-in gains: confirm disclosure of BIG tax exposure and any provision recorded

### Partnerships

- Confirm description of partnership agreement key provisions (allocation of profits/losses, capital account maintenance, distribution provisions, mandatory vs. discretionary distributions, priority returns)

- Confirm capital accounts maintained for each partner or class (general partner, limited partners, preferred/common classes) with separate rollforwards if material

- Confirm allocations of income/loss follow the disclosed provisions

- For limited partnerships: confirm GP and LP interests distinguished; confirm any preferred return or priority distribution mechanics

### LLCs

- Confirm description of operating agreement key provisions (allocation, distribution, voting, transfer restrictions)

- Confirm LLC taxed-as-partnership vs. taxed-as-corporation election disclosed

- Confirm member equity structured consistently with the disclosed tax classification — partnership-taxed LLC should show members' capital with allocations; corporation-taxed LLC should show equity like a corporation

- Confirm manager-managed vs. member-managed structure disclosed if relevant to governance

### Closely-Held / Family-Owned Entities

- Confirm related-party disclosures fully capture family-member transactions and balances

- Assess whether common structures (operating company + related-party real estate LLC; management company; shareholder/member loans) are fully disclosed

- Confirm any buy-sell agreements, key-person insurance, or succession provisions with financial statement impact are disclosed

### ESOP-Owned Companies

- Confirm ESOP participation and repurchase obligation disclosed (ASC 718-40)

- Confirm share valuation and redemption value disclosures

- Confirm deferred compensation related to unallocated shares

### Entities with Equity-Based Compensation

- Confirm plan disclosures under ASC 718

- For non-public entities, confirm the practical expedients for expected term and use of calculated value are applied if elected

- Confirm grants, vesting, exercises, and forfeitures are rolled forward

# STEP 6 — FINAL PROOF CHECKLIST

Apply the judgment of an experienced commercial audit preparer performing a final proof. Goal: surface document-level issues to resolve before handoff to QC — do not conclude on engagement quality, firm risk, or release readiness.

## Internal Consistency of Narrative

- If any management narrative, letter, or description accompanies the financial statements, confirm it is consistent with the presented results.

- Flag any narrative claim inconsistent with the numbers.

## Opinion Appropriateness

- Given the complete contents of the document, does the opinion type appear appropriate?

- Are there any matters disclosed in the footnotes (significant uncertainties, going concern indicators, material restatements, major subsequent events, departures from GAAP) that would appear to require modification or emphasis in a currently unmodified report?

## Going Concern Section / Emphasis-of-Matter Consistency

- If going concern language appears in the notes, confirm the auditor's report contains the corresponding Substantial Doubt section.

- If a restatement, change in accounting principle, or significant subsequent event is disclosed, confirm the auditor's report contains an appropriate emphasis-of-matter paragraph.

## Sensitive Disclosures

- Are there any disclosures that appear legally or reputationally sensitive that should be reviewed by engagement leadership before release?

## Cover Page and Transmittal

- If a transmittal letter, cover page, or table of contents is present, confirm it is addressed correctly, dated correctly, and attributed appropriately.

## Supplementary Schedules

- Confirm any supplementary schedules (consolidating, combining, operating expense detail) are properly labeled, properly referenced in the auditor's report, and mathematically consistent with the basic statements.

## Unusual or Uncommon Items

- Flag anything in the document that is unusual or uncommon for a private company financial statement and warrants specific attention by the reviewer. Examples: defined benefit pension plans (rare in private companies); derivative and hedging activity; foreign operations and translation; discontinued operations; impairment charges; business combinations completed during the year; equity method investments; VIE consolidations under the voting-interest model (as opposed to PCC scope exception); restricted cash or escrow arrangements; noncontrolling interests; redeemable equity instruments (ASC 480); SaaS or cloud computing arrangements (ASC 350-40); digital assets; any non-standard or industry-specific accounting treatment.

# STEP 7 — OUTPUT FORMAT

After completing all review steps, produce a structured Excel report with the following tabs. Apply the formatting rules in the AI Behavior and Output Formatting section above (no fills, no borders except section-heading underlines, no merged cells, three plain header cells upper-left, no Purpose/Procedure scaffolding, no release-readiness language).

## Tab 1 — Executive Summary

- All findings compiled in a single table, sorted by severity: Critical, Significant, Moderate, Minor

- A summary at the top showing only the count of findings by severity (Critical / Significant / Moderate / Minor). Do NOT include any release-readiness language, engagement-risk language, or overall assessment.

- Each finding row includes: Finding ID, Step, Category, Severity, Location in document, Description, Recommended Correction. Do not include Reviewer Notes, Management Response, or Resolved columns — this is a report, not a workpaper.

- This tab is self-contained — a reader should be able to find every issue without jumping to the detail tabs.

## Tab 2 — Proof Review

- All Step 1 procedures listed line by line with Pass / Fail / Flag result and notes

## Tab 3 — Report Language

- All Step 2 procedures organized by section (required paragraphs, order, no-extra-paragraphs, SI, OI, prior year / auditor change) with Pass / Fail / Flag result and notes

## Tab 4 — Math Check

- All Step 3 procedures with per-document figure, recalculated figure, difference, and result

- Multi-column statements (consolidating, combining, segment) include the column map at the top of each section

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
