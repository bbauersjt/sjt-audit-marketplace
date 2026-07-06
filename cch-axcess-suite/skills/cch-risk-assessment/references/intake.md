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
2. Keep **classes of transactions** distinct from **account balances**: revenue streams, payroll, purchases/disbursements, and contributions are transaction classes that get scoped and tested even when no single balance-sheet line is large. A small net balance can sit on top of a large gross transaction flow — scope on the flow, not the residual.
3. Sum each area: current-year balance, prior-year balance (from prior TB or FS), and **absolute** dollar change. Significance is tested on the **larger of** the current balance or the gross activity in the class.
4. Produce a working scope sheet: area · CY balance · PY balance · change · gross activity (for transaction classes) · significant Y/N · basis. This is the artifact that justifies the KBA-400 scoping and should be saved to the engagement folder.

> Deriving balances is judgment, not just arithmetic — when an account is ambiguous (e.g., "Other"), classify by what's actually in it (read the detail if available) and note the call. Flag anything you're unsure of for the user rather than burying it.

## Step 3 — Materiality / tolerable

Significance is measured against a threshold. Get it, don't guess it.

- **Ask the user** for tolerable misstatement (often = performance materiality) and overall/planning materiality, or
- **Read project notes / KBA-301** if materiality has already been set this year. KBA-301 (or KBA-301E for EBP) is the CCH home for overall materiality, performance materiality, and the clearly-trivial threshold.
- If only overall materiality is available, **performance materiality** is typically a haircut of it (commonly ~50–75%); confirm the firm's percentage with the user rather than assuming. *(Firm-tunable — see `scoping/significance.md`.)*
- Record which number you used and where it came from. The whole significance call rests on it.

For EBP, materiality is usually set on net assets available for benefits; for governmental, materiality is applied by opinion unit. Note the basis.

## Step 4 — Significance call

Apply `scoping/significance.md`. In short: an area/class/disclosure is **significant** if its balance or gross activity **exceeds tolerable**, OR if it is **qualitatively significant** regardless of size (the always-significant list — e.g., cash, revenue, related parties, journal entries, areas with fraud risk or significant estimates, required disclosures). Significant areas get scoped on KBA-400, get a relevant-assertion set, get IR/CR/RMM on KBA-502, and get an audit program.

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

Default to the prior year's scoping and IR, then **challenge each one** against this year's TB and facts:
- New or newly-material area this year → add to scope.
- Area that fell below tolerable and has no qualitative driver → consider de-scoping (document why).
- Changed facts (new debt, new revenue stream, new estimate, control change, restatement) → revisit IR and significant-risk flags.
- Never carry a prior IR forward blind — the basis must hold this year (KBA-503).

## Open / firm-tunable (confirm with user, then codify)

- The exact performance-materiality % and clearly-trivial % the firm uses (parametrized in `scoping/significance.md`).
- Whether the firm scopes transaction classes separately from balances on KBA-400 or folds them into the balance-sheet area (affects how many KBA-400 rows you create).
- The always-significant qualitative list is a sensible default (see `scoping/significance.md`); confirm the firm's house list.
