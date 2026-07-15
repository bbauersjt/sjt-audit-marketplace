# Intake — Documents, Identification, Limitations (all frameworks)

1. Do not block the review waiting for documents — start immediately with what was
   provided and record limitations for anything missing.
1.1. Exception: if no financial statement package at all can be located, ask for it.

## Documents

1. **The FS package (PDF)** is the only required input.
   1.1. The deterministic extraction pipeline (`shared/steps/math-protocol.md`) handles
        column mapping on multi-column statements — the source Excel workbook is NOT
        required and must not be requested as a precondition.
   1.2. If the user volunteers the Excel workbook, use it as a secondary input to
        `extract_tables.py` (it accepts .xlsx) and to resolve any extraction warnings.
2. **Prior year issued financial statements** — useful, not required.
   2.1. If provided: extract it too (`extract_tables.py <py.pdf> -o py_statements.json`)
        and run `compare_py.py` — it agrees every comparative figure in the CY package
        to the PY issued package mechanically; the cross-reference reviewer adjudicates
        its MISMATCH and NOT-FOUND candidates. Then agree beginning balances (retained
        earnings / net assets / net position / capital accounts / AOCI), check policy
        consistency and reclassification disclosure, and confirm predecessor-auditor
        language if the engagement changed hands.
   2.2. If not provided: ask ONE non-blocking question alongside starting the review —
        is this a first-year audit (no prior audited statements exist)?
     - First-year audit: do not flag missing prior-year tie-outs; confirm AU-C 510
       opening-balance report language instead.
     - Prior year exists but not provided: record the limitation — beginning-balance
       tie-out, comparative verification, policy-consistency check, and
       predecessor-reference verification are incomplete pending the prior report —
       and proceed with everything else.
3. Framework-specific documents (e.g., EBP certification, draft Form 5500) are listed in
   the framework's `identify.md`; request them the same non-blocking way.
4. Every limitation recorded here goes into the report `meta.limitations` and prints on
   the Executive Summary tab.

## Identify the engagement

Determine, from the report/opinion pages and statement titles:

1. **Framework** — governmental (GASB terms: net position, fund balance, MD&A, ACFR),
   nonprofit (ASC 958: net assets with/without donor restrictions, statement of
   activities/functional expenses), EBP (net assets available for benefits, ERISA,
   SAS 136 / AU-C 703 report), else commercial (U.S. GAAP / FASB ASC). Load the matching
   `frameworks/<type>/` modules.
   1.1. If the stated framework is something else entirely (tax basis, cash basis, FRF
        for SMEs, IFRS): these procedures are scoped to GAAP frameworks — flag it and
        confirm with the reviewer before proceeding.
2. **Engagement type** — confirm an audit (opinion language).
   2.1. A review (AR-C 90), compilation (AR-C 80), or preparation (AR-C 70) changes the
        report-language procedures — flag and confirm scope.
3. **Entity specifics** — run the framework's `identify.md`.
4. **Industry overlays** — scan the statements, notes, and supplementary schedules for
   industry signals and load every matching module in `shared/industries/`. Signals
   include (not exhaustive):
   - **Construction contractor** → `shared/industries/construction.md`: contract
     receivables, costs and estimated earnings in excess of billings (or billings in
     excess of...), schedule of contracts in progress / completed contracts, retainage,
     backlog, percentage-of-completion language.
   - Real estate (rental revenue, investment property), manufacturing (inventory
     classes, standard cost), restaurants/retail (sales tax, gift cards, franchise
     fees) — load the module if it exists; if no module exists yet, note the industry
     in the engagement profile and apply extra reviewer judgment to industry-specific
     schedules.

## Extraction confidence

1. After running `extract_tables.py`, review its warnings before anything else.
1.1. A warning means a line's figures may be misattributed — verify those lines visually
     (render the page) and correct `statements.json` if needed BEFORE footing. An
     extraction problem is never a finding; a finding must be verified against the
     printed document.
