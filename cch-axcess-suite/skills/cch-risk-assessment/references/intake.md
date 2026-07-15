# Intake — reading the client to drive the cascade

**Goal of this module:** turn the client's documents into the three things the cascade needs — (1) a list of audit **areas in play**, (2) which of them are **significant**, and (3) the **materiality/tolerable** threshold significance is measured against. Everything downstream (AUD-100 areas, KBA-400 scoping, KBA-502 risk table, recommended programs) is built on this. Do this before touching any form.

This skill produces the *content*. `cch-axcess` reads/writes the live forms. Read the live TB report and any existing planning forms through `cch-axcess` (`run-reports.md`, `fill-kc-form.md`) when they already exist on the engagement.

## Inputs (in priority order)

1. **Current-year trial balance** — required. The spine of significance. Grouped (mapped to leadsheet/area codes) or ungrouped (raw GL accounts).
2. **Prior-year financial statements** — the issued FS and notes. Tells you the real reporting captions, the disclosures actually made, and the entity's accounting policies.
3. **Prior-year risk assessment** — last year's KBA-400/KBA-502 (or the prior firm's equivalent). The single best predictor of this year's scoping and IR. Roll forward, then challenge.
   - **If no prior RA:** use a same-title example engagement (a similar client of the same audit type) as the pattern, and lean harder on `defaults/{CODE}.md`.
   - **If neither:** build from the TB + FS + `defaults/{CODE}.md` alone, and flag for reviewer that scoping is first-year/de novo.
4. **Materiality** — tolerable misstatement / performance materiality. Ask the user, or read it from project notes / KBA-301 if already set. Do not invent it. See "Materiality" below.
5. **Project notes / prior workpapers** — engagement-specific facts (known issues, new transactions, restrictions, covenant terms). Always check before finalizing.

## Step 1 — Establish the area structure

Map the entity's accounts to the firm's audit areas. The area set is title-specific — see `scoping/area-map-by-title.md` for the canonical list per audit type and the AUD-8xx program each maps to.

- **Grouped TB:** the grouping/leadsheet codes already imply areas. Roll them up to area level. (If the TB uses legacy codes, the `trial-balance-prep` skill maps them to the 4-digit index first.)
- **Ungrouped TB:** you must derive the area for each account yourself before you can total anything — see Step 2.

## Step 2 — Ungrouped TB: derive transaction-class balances

When the TB is a raw account list with no area mapping, group it yourself into the title's areas so you can total each one.

1. Classify each account to an audit area by account name + normal balance + sign. Use `scoping/area-map-by-title.md` for the target area list and the firm's standard 4-digit taxonomy (`cch-axcess/references/data/tb-group-codes.xlsx` — Natural columns for commercial/NFP, Governmental columns when the engagement shows a Funds Setup button).
2. Keep classes of transactions distinct from account balances: revenue streams, payroll, purchases/disbursements, and contributions are transaction classes that get scoped and tested even when no single balance-sheet line is large. Scope on the gross flow, not the net residual.
3. Sum each area: current-year balance, prior-year balance (from prior TB or FS), and absolute dollar change. Test significance on the larger of the current balance or the gross activity in the class.
4. Produce a working scope sheet: area · CY balance · PY balance · change · gross activity (for transaction classes) · significant Y/N · basis. This is the artifact that justifies the KBA-400 scoping — save it to the engagement folder.
5. When an account is ambiguous (e.g., "Other"), classify by what's actually in it (read the detail if available) and note the call — don't guess. Flag anything you're unsure of for the user rather than burying it.

## Step 3 — Materiality / tolerable

Significance is measured against a threshold. Get it, don't guess it.

- **Ask the user** for tolerable misstatement (often = performance materiality) and overall/planning materiality, or
- **Read project notes / KBA-301** if materiality has already been set this year. KBA-301 (or KBA-301E for EBP) is the CCH home for overall materiality, performance materiality, and the clearly-trivial threshold.
- If only overall materiality is available, **performance materiality** is typically a haircut of it (commonly ~50–75%); confirm the firm's percentage with the user rather than assuming. *(Firm-tunable — see `scoping/significance.md`.)*
- **PAJE / passed-adjustment threshold = max(10% of TM, $5,000)** (EBP: max(20% of TM, $5,000)). The **$5,000 floor is mandatory on every engagement** — compute the percentage, then take the greater of it and $5,000; never record the raw percentage when it falls below $5,000.
- Record which number you used and where it came from. The whole significance call rests on it.

### KBA-301 method (the firm's benchmark → PM → TM derivation)

When materiality is being **set** (not just read back), follow the firm's method — don't do ad-hoc
reasonableness math:

1. **Benchmark selection — take the one that yields the LARGER materiality, then justify it.** Compute the
   candidate benchmarks the form offers for the entity (e.g. total revenues/contributions and total assets),
   and choose whichever produces the greater overall materiality, stating the one-paragraph rationale tied to
   the entity's users and objectives. Bigger materiality is the firm's default posture where the benchmark
   choice is otherwise defensible.
2. **Benchmark percentage stays inside the form's stated acceptable range.** KBA-301's benchmark table prints
   a rule-of-thumb range per benchmark; pick a percentage **within** it. The **top of the range is
   acceptable** (the firm routinely maxes it); **above the range is not** — never exceed the stated range.
3. **Performance materiality / TM is an explicit line item, not skipped.** The firm does not leave PM/TM
   unentered: on KBA-301 add the **"financial statements taken as a whole"** line (the step-8 "click to add
   new item" control), set **TM = 75% of planning materiality, rounded DOWN to the nearest hundred**. This TM
   ("performance materiality") is the number the rest of the audit is scoped and concluded against — planning
   materiality itself drives almost nothing downstream. Govt computes a PM/TM set per opinion unit.
4. **PAJE = max(10% of TM, $5,000)** — the $5,000 floor is mandatory (above). It is computed off TM, so TM
   must exist first; a PAJE derived before TM is set is wrong.

For EBP, materiality is usually set on net assets available for benefits; for governmental, materiality is applied by opinion unit. Note the basis.

## Step 4 — Significance call

Apply `scoping/significance.md`. An area/class/disclosure is significant if:
1. Its balance or gross activity exceeds tolerable, OR
2. It is qualitatively significant regardless of size (the always-significant list — e.g., cash, revenue, related parties, journal entries, areas with fraud risk or significant estimates, required disclosures).

Significant areas get scoped on KBA-400, get a relevant-assertion set, get IR/CR/RMM on KBA-502, and get an audit program.

## Step 5 — Hand the result to the cascade

The intake output feeds, in order:

| Intake output | Drives |
|---|---|
| Areas in play + controls posture | AUD-100 area selection + controls-testing decision (`references/cascade/aud-100.md`) |
| Significant areas | KBA-400 scoping selections (`references/cascade/kba-400.md`) |
| Relevant assertions per area | KBA-400 per-area assertion section → KBA-502 rows |
| Materiality / tolerable | KBA-301 (threshold) + KBA-502 significance |
| Prior-year IR + engagement facts | KBA-502 IR (start from `defaults/{CODE}.md`) + KBA-503 basis |
| Significant areas → programs | Recommended AUD-8xx programs (`scoping/area-map-by-title.md`) |

## Roll-forward discipline (when a prior RA exists)

Default to the prior year's scoping and IR, then challenge each one against this year's TB and facts:
1. New or newly-material area this year → add to scope.
2. Area that fell below tolerable and has no qualitative driver → consider de-scoping (document why).
3. Changed facts (new debt, new revenue stream, new estimate, control change, restatement) → revisit IR and significant-risk flags.
4. Never carry a prior IR forward blind — the basis must hold this year (KBA-503).

## Open / firm-tunable (confirm with user, then codify)

- The exact performance-materiality % and clearly-trivial % the firm uses (parametrized in `scoping/significance.md`).
- Whether the firm scopes transaction classes separately from balances on KBA-400 or folds them into the balance-sheet area (affects how many KBA-400 rows you create).
- The always-significant qualitative list is a sensible default (see `scoping/significance.md`); confirm the firm's house list.
