---
name: fs-review
description: Comprehensive technical proof and review of ANY financial statement package before QC — commercial/private-company (U.S. GAAP, C-corps, S-corps, partnerships, LLCs, closely-held), nonprofit (ASC 958, charities, foundations, religious/educational/healthcare orgs), governmental (GASB, ACFR, Single Audit, Yellow Book), and employee benefit plans (ERISA, 401(k)/403(b)/DB/H&W, SAS 136, ERISA 103(a)(3)(C)). Use WHENEVER the user uploads or references a financial statement or audit report and asks for a review, proof, technical review, QC check, math check, footing, cross-reference check, or disclosure review — trigger even without the word "skill" ("check this", "proof this", "find issues", "review before QC"). Also triggers on auditor's report/opinion review (SAS 134+/136, GAGAS), going concern, ASC 606/842 review, WIP/job schedule review for contractors, SEFA/schedule of findings, Form 5500 reconciliation. Do NOT use for SEC registrants, tax returns, or bookkeeping.
---

# Financial Statement Technical Review — Orchestrator

You are the orchestrator. You do not perform review procedures yourself — you run the
deterministic pipeline, dispatch focused subagents that each load only their module, and
merge their findings into one Excel report. All module paths below are relative to this
skill's plugin root (`skills/fs-review/`).

## Phase 0 — Intake and identification (you)

Read `shared/steps/intake.md` and follow it: locate the package, note limitations
(non-blocking), and identify:
- **framework** ∈ commercial | nonprofit | govt | ebp → selects `shared/frameworks/<f>/`
- **industry overlays** → every matching module in `shared/industries/`
  (construction signals → `construction.md` and plan to run `tie_wip.py`)
- read the framework's `identify.md` and record the entity profile (entity type,
  consolidation, PCC elections / plan type / audit scope, etc.) — pass this profile to
  every subagent.

## Phase 1 — Deterministic pipeline (you; zero model arithmetic)

Read `shared/steps/math-protocol.md`. In a scratch folder:

```
python <plugin>/scripts/extract_tables.py "<package.pdf>" -o statements.json
python <plugin>/scripts/foot.py statements.json -o foot_report.json
python <plugin>/scripts/xref.py statements.json -o xref_report.json
python <plugin>/scripts/proof_scan.py "<package.pdf>" --cy <FY> --statements statements.json -o proof_scan.json
python <plugin>/scripts/disclosure_scan.py "<package.pdf>" --framework <f> -o disclosure_scan.json
python <plugin>/scripts/tie_wip.py statements.json -o wip_report.json   # construction only
# when the prior-year issued package was provided:
python <plugin>/scripts/extract_tables.py "<py.pdf>" -o py_statements.json
python <plugin>/scripts/compare_py.py statements.json py_statements.json --py <PY> --cy <FY> -o py_compare.json
```

Resolve extraction warnings (verify flagged lines visually, correct statements.json,
re-run) BEFORE dispatching reviewers. Never hand a reviewer unverified extraction.

## Phase 2 — Parallel review fan-out (subagents)

Launch ALL applicable reviewers in ONE message (general-purpose agents). Every prompt
includes: the package path, the engagement profile from Phase 0, the scratch-folder
paths, an instruction to read `shared/core.md` first, and: "Return ONLY the findings
JSON defined in core.md, plus a procedures list for your tab."

| Reviewer | Loads | Also gets |
|---|---|---|
| Proof | `shared/steps/proof.md` | `proof_scan.json`, framework `specifics.md` → Proof additions |
| Report language | `frameworks/<f>/report-language.md` | the report/opinion pages |
| Math adjudicator | `shared/steps/math-protocol.md`, `shared/steps/statement-relations.md` | `foot_report.json`, `statements.json`, framework Math additions |
| Cross-reference | `shared/steps/xref.md`, `shared/steps/paired-accounts.md` | `xref_report.json`, `py_compare.json` if PY provided, framework Cross-reference additions |
| Disclosures | `frameworks/<f>/disclosures.md` | entity profile, `disclosure_scan.json` (presence candidates to adjudicate first — a candidate means "confirm this note is really missing", never a finding by itself) |
| Industry (per overlay) | `shared/industries/<i>.md` | `wip_report.json` for construction |
| EBP supplemental (ebp only) | `frameworks/ebp/supplemental.md` | supplemental schedules, Form 5500 if provided |

Subagents adjudicate script output; they never do arithmetic on PDF text. If a reviewer
reports a numeric discrepancy that did not come from a script report, send it back.

## Phase 3 — Final checklist, merge, render (you)

1. Run `shared/steps/final-checklist.md` yourself — it needs the whole picture
   (opinion appropriateness, going-concern/EoM consistency, narrative consistency).
2. Merge all findings: dedupe (same location + same figure = one finding,
   cross-referenced), re-sequence IDs by step prefix (P/R/M/X/D/I/S/F), sort by
   severity. Build `findings.json` per `shared/core.md` (include `meta.limitations`
   from intake).
3. Render: `python <plugin>/scripts/report.py findings.json -o "<Client> FS Review.xlsx"`
   — the spec is `references/output-spec.md`; report.py conforms to it. Verify it
   reopened cleanly (report.py self-checks).

## Behavior

- Chat output stays minimal (see `shared/core.md`): announce phases, not procedures;
  findings live in the Excel report, not chat.
- Findings must be verified against the printed document — an extraction artifact is
  never a finding. Zero tolerance on footing differences ($1 is a finding).
- If the package is a review/compilation/preparation engagement or a non-GAAP
  framework, flag scope per `intake.md` and confirm before running report-language
  procedures.
