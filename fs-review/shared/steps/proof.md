# Proof Review (all frameworks)

1. Run `scripts/proof_scan.py` first — it mechanizes the text-layer checks in this
   module: TOC tie-out, printed page-number sequence, note numbering/references/
   continuation inventory, entity-reference and possessive consistency, serial comma,
   heading/label capitalization drift, stale and future years, draft markers, date-format
   mix, per-table negative-number style, rare-font runs (cut-paste artifacts), and
   high-confidence misspellings.
2. Adjudicate its `proof_scan.json` candidates against the printed document first (each
   carries page + excerpt; candidates have legitimate explanations — e.g., "the Plan" and
   "the Company" coexisting in an EBP package).
3. Then read the document for what only reading can catch: grammar and wording, spelling
   the scan can't judge (proper nouns, capitalized terms), page breaks, widows/orphans,
   spacing/alignment, whether a note reference's TARGET actually covers the topic
   referenced, and everything in the checklist below.
3.1. Do not re-derive by reading what the scan already checked mechanically.
4. Perform a comprehensive proofread of the entire document using the checklist below.

## Table of Contents vs. Actual Document
1. Confirm every item listed in the TOC exists in the document with a matching title and matching page number. Flag any discrepancy.

## Page Numbers
1. Confirm page numbers are sequential, correctly formatted, and consistent in style throughout.

## Report Titles
1. Confirm every report and statement heading in the document exactly matches the TOC entry, including capitalization and punctuation.

## Page Breaks
1. Confirm there are no awkward or missing page breaks — statements should not be split mid-table unless unavoidable, and no orphaned headings should appear at the bottom of a page.

## Spelling and Grammar
1. Flag all spelling errors, grammatical errors, and typographical mistakes.

## Footnote Sequencing and Continuation Headers
1. Identify the footnote numbering scheme used (numeric: 1, 2, 3; alphabetic: A, B, C; or mixed).
2. Confirm notes are numbered sequentially without gaps, duplicates, or out-of-order entries. Flag any skipped number/letter, any repeated number/letter, and any note that appears out of sequence.
3. Confirm every footnote cross-reference within the document (e.g., "see Note 5", "as described in Note 11") points to a note that exists and covers the content implied by the reference. Flag any reference to a note that does not exist or does not address the topic referenced.
4. For multi-page notes, check "continued" headers at the top of each continuation page. The continuation header must cite the correct note number/letter being continued. Flag: (a) missing continuation header where a note spans pages; (b) continuation header citing the wrong note number; (c) continuation header present but the prior page's note actually ended on that page (a new note starts on the current page, and no continuation is actually occurring).
5. Apply the same sequencing and continuation checks to other numbered/lettered sequences in the document where applicable: subheadings within a note (a, b, c or i, ii, iii), and continuation headers on multi-page schedules (e.g., "Consolidating Statement — continued" must accurately describe what is being continued).

## Consistency of Language
1. Flag any inconsistency in how the entity, subsidiaries, product lines, segments, or accounts are named throughout the document.
2. The entity should be referred to by a single consistent name (e.g., "the Company", "the Organization", "the District", "the Plan", "the Partnership", "the LLC", as applicable) — confirm the chosen collective reference is applied consistently. Subsidiary names, segment names, and account titles must be consistent throughout all reports, statements, footnotes, and supplementary schedules.

## Consistency of Dates and Fiscal Year References
1. All references to the fiscal year end date, the audit period, and prior year must be internally consistent. Flag any mismatched dates.
2. Pay special attention to partnerships and S corporations with non-calendar tax years that may differ from the financial reporting year — confirm all date references are consistent with the stated reporting period.

## Punctuation and Possessive Consistency
Check for consistent use of the following throughout the entire document, including all reports, statements, footnotes, schedules, and supplementary information:
1. Serial comma (Oxford comma) usage — determine whether the document uses or omits the serial comma and flag any inconsistency. Do not flag the choice itself, only departures from the chosen convention.
2. Possessive form of "Auditor" — identify whether the document uses "Auditor's" (singular possessive) or "Auditors'" (plural possessive) and flag any inconsistency. Do not flag the choice itself, only departures from the chosen convention.
3. Collective reference to the entity — confirm the entity is consistently referred to as "the Company," "the Organization," "the District," "the Plan," "the Partnership," "the LLC," or similar, as applicable, throughout. Flag any inconsistency (e.g., switching between "the Company" and "the LLC" for the same entity).
4. Flag any other punctuation convention where usage is inconsistent within the document — including hyphenation of compound terms, use of em dashes vs. en dashes vs. hyphens, and use of periods in abbreviations.

## Formatting Consistency
Check for consistent use of all of the following:
1. Fonts and font sizes across all sections (headers, body text, table text, footnotes).
2. Paragraph spacing and line spacing.
3. Indentation and table alignment.
4. Dollar sign placement (should appear at top of column and at totals, not on every line unless style requires it).
5. Underlines and double underlines on totals and grand totals in financial statements.
6. Thousands separators and decimal consistency.
7. Parentheses vs. minus signs for negative numbers — must be consistent throughout.
8. Column header style and alignment.

## Capitalization Conventions
1. Confirm consistent capitalization of account titles, subsidiary names, segment names, and report titles.

## Widows and Orphans
1. Flag single lines of text separated from their paragraph by a page break.

**NOTE:** *Flag anything else that would be identified during a professional proofread of a formally published financial document.*
