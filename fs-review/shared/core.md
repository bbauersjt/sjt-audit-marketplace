# Core Behavior and Output Formatting (all frameworks)

## Narration and Commentary

1. Keep chat output minimal — do not narrate each procedure as it runs, do not give running commentary on findings or hypotheses, do not summarize or editorialize on results at the end.
2. Announce only the phase being started (e.g., "Phase 1 — deterministic pipeline", "Phase 2 — review fan-out"). Do not announce sub-steps or internal procedures.
3. All findings and conclusions go in the Excel report, not chat.
4. Clarifying questions to the user are permitted where the intake flow requires them.

## Excel Report Formatting — Strict Rules

The deliverable is a plain Excel REPORT, not a workpaper.

1. Produce a valid .xlsx file that opens cleanly in Excel — no XML errors, no broken formulas, no hidden corruption. Test by opening with openpyxl or similar after saving if uncertain.
2. Header block on every tab: three plain cells stacked vertically in column A — (1) client name, (2) report/tab name, (3) date of financials. No merging.
3. Size column widths so content fits readably. For tabular data (findings tables, cross-reference tables, math tables), put long narrative content in a dedicated wide column (roughly 60–80 character width). For standalone labeled rows at the top of a tab (e.g., "Limitation" with a long sentence next to it), do NOT apply wrap_text — let the text overflow visually into adjacent empty cells rather than wrapping into a tall multi-line row.
4. Do NOT use workpaper scaffolding: no Purpose/Procedure/Conclusion blocks, no "Note1>"/"Note2>" label cells, no manual-entry columns (Reviewer Notes, Management Response, Resolved, etc.).
5. Do NOT include a release-readiness banner, engagement-risk commentary, or overall "ready for release" assessment anywhere. The Executive Summary shows only the count of findings by severity and the findings themselves.
6. Cell fills, font colors, and light borders are fine where they aid readability (e.g., bold underlined headers, a light fill on header rows) — keep it clean: no distracting palettes, no heavy grid lines, no neon.

## Findings

Every finding is classified on a four-level severity scale. Use these labels consistently everywhere — in reviewer output, in the findings JSON, and in every tab of the deliverable workbook:

- **Critical** — the document is wrong on its face or noncompliant with a required standard: statements that do not balance or foot, a misstated or contradicted figure, a missing or defective required element of the auditor's report, or a missing required disclosure a reader would rely on.

- **Significant** — a likely error or omission that requires preparer action before release: figures that do not tie between locations, an apparently required disclosure that is absent or deficient, report language that departs from the applicable standard.

- **Moderate** — an inconsistency, classification question, or presentation issue that should be corrected but does not by itself misstate the statements.

- **Minor** — typographical, formatting, or stylistic issues.

### Findings JSON contract

Every reviewer must emit its findings in this JSON contract:

```json
{"findings": [{"id": "P-01", "step": "proof|report-language|math|xref|disclosure|industry|supplemental|final", "category": "...", "severity": "Critical|Significant|Moderate|Minor", "location": "page/statement/note", "description": "...", "recommendation": "..."}]}
```

- `id` — step-prefixed and sequentially numbered (P- proof, R- report-language, M- math, X- xref, D- disclosure, I- industry, S- supplemental, F- final).
- `step` — one of the enumerated step slugs.
- `category` — short label for the kind of issue (e.g., "footing", "tie-out", "missing disclosure", "typo").
- `severity` — one of the four labels above, exactly as spelled.
- `location` — where in the document the issue sits: page, statement, or note.
- `description` — what is wrong, including the presented figure and the expected/recalculated figure where applicable.
- `recommendation` — the recommended correction.

These fields map one-to-one to the findings table columns in the deliverable workbook (see `references/output-spec.md`).

1. Do not opine on anything you could not verify.
2. A procedure that cannot be performed because a document was not provided is marked "Limitation — [document] not provided" in its procedures row (result column).
3. Record the limitation in `meta.limitations` so it prints on the Executive Summary.
