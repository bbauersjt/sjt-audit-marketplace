# Deliverable Workbook — Output Specification

Canonical spec for the deliverable Excel report rendered by `scripts/report.py`. Tab names and step numbering may vary slightly by framework — e.g., the EBP framework adds supplemental-schedule and Form 5500 tabs — but the header block, findings table columns, severity ordering, and no-scaffolding rules below apply to every framework.

## Workbook Formatting — Strict Rules

The deliverable is a plain Excel REPORT, not a workpaper. Keep it clean and readable. A few requirements:

- Produce a valid .xlsx file that opens cleanly in Excel with no XML errors, no broken formulas, and no hidden corruption. Test by opening with openpyxl or similar after saving if uncertain.

- Header block on every tab: three plain cells stacked vertically in column A — (1) client name, (2) report/tab name, (3) date of financials. No merging.

- Size column widths so content fits readably. For tabular data (findings tables, cross-reference tables, math tables), put long narrative content in a dedicated wide column (roughly 60–80 character width). For standalone labeled rows at the top of a tab (e.g., "Limitation" with a long sentence next to it), do NOT apply wrap_text; let the text overflow visually into adjacent empty cells rather than wrapping into a tall multi-line row. Do not force long narrative into a cell expected to wrap into a giant multi-line row.

- Do NOT use workpaper scaffolding: no Purpose/Procedure/Conclusion blocks, no "Note1>"/"Note2>" label cells, no manual-entry columns (Reviewer Notes, Management Response, Resolved, etc.). This is a report, not a workpaper.

- Do NOT include a release-readiness banner, engagement-risk commentary, or overall "ready for release" assessment anywhere. The Executive Summary shows only the count of findings by severity and the findings themselves.

- Cell fills, font colors, and light borders are fine where they aid readability (e.g., bold underlined headers, a light fill on header rows). Just keep it clean — no distracting palettes, no heavy grid lines, no neon.

## Tabs

After completing all review steps, produce a structured Excel report with the following tabs. Apply the formatting rules above (no merged cells, three plain header cells upper-left, no Purpose/Procedure scaffolding, no release-readiness language).

### Tab 1 — Executive Summary

- All findings compiled in a single table, sorted by severity: Critical, Significant, Moderate, Minor

- A summary at the top showing only the count of findings by severity (Critical / Significant / Moderate / Minor). Do NOT include any release-readiness language, engagement-risk language, or overall assessment.

- Each finding row includes: Finding ID, Step, Category, Severity, Location in document, Description, Recommended Correction. Do not include Reviewer Notes, Management Response, or Resolved columns — this is a report, not a workpaper. (These columns map one-to-one to the findings JSON contract in `shared/core.md`.)

- This tab is self-contained — a reader should be able to find every issue without jumping to the detail tabs.

### Tab 2 — Proof Review

- All proof procedures (`shared/steps/proof.md` + framework proof additions) listed line by line with Pass / Fail / Flag result and notes

### Tab 3 — Report Language

- All report-language procedures (`frameworks/<f>/report-language.md`) organized by section (required paragraphs, order, no-extra-paragraphs, SI, OI, prior year / auditor change; for governmental — organized by report) with Pass / Fail / Flag result and notes

### Tab 4 — Math Check

- All math procedures (pipeline footings/cross-footings plus `shared/steps/statement-relations.md` relations) with per-document figure, recalculated figure, difference, and result

- Multi-column statements (consolidating, combining, segment) include the column map at the top of each section

### Tab 5 — Cross-Reference

- All cross-reference procedures (`shared/steps/xref.md` + framework additions) with location 1, location 2, value, and result

- Include a sub-section for paired-account relationship findings

- Include a sub-section for logical and contextual consistency findings

### Tab 6 — Disclosure Review

- All disclosure procedures (`frameworks/<f>/disclosures.md`) organized by standard/topic (ASC for commercial and nonprofit, GASB for governmental, ASC 962/960/965 for EBP) with Pass / Fail / Flag result and notes

### Tab 7 — Industry Review (only when an industry overlay ran)

- Industry-overlay procedures (e.g., `industries/construction.md` — WIP recomputes, schedule-to-statement ties) with result and notes

### Tab 8 — Supplemental Schedules (EBP only)

- Supplemental schedule and Form 5500 reconciliation procedures (`frameworks/ebp/supplemental.md`) with result and notes

### Final tab — Final Proof Checklist

- All final-checklist items (`shared/steps/final-checklist.md`) with result, finding reference, and notes. No blank manual-entry columns.

**NOTE:** *Severity classification throughout: Critical, Significant, Moderate, Minor. Use these labels consistently in all tabs.*

**NOTE:** *A procedure that could not be performed because a document was not provided shows "Limitation — [document] not provided" as its result — never a silent Pass or an unexplained blank.*

**NOTE:** *Present all findings organized by step in the detail tabs. For each issue, note: location in the document, description of the issue, and recommended correction. The Executive Summary tab should be self-contained enough that a reader can see every issue without needing to open the detail tabs.*
