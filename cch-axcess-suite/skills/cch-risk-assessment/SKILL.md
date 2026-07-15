---
name: cch-risk-assessment
description: The risk-assessment brain for CCH Axcess (Knowledge Coach) audits. Determines the CONTENT of the planning cascade — AUD-100 (engagement tailoring) → KBA-400 (scoping & mapping of significant accounts/transactions/disclosures) → KBA-502 (summary of risk assessments: IR/CR/RMM + planned audit approach) → recommended audit programs (AUD-8xx) — by reading the client's prior financials, prior risk assessment (or an example), and current-year trial balance, and by determining significance against tolerable/performance materiality. Does NOT touch the platform — the sibling skill `cch-axcess` parses the live forms and executes every write; this skill supplies the answers. Use whenever the user is scoping an engagement, deciding significant accounts/classes, setting or overriding IR/CR/RMM or the audit approach, answering AUD-100/KBA-400/KBA-502, picking audit programs and steps, or asks about MAX/SBM/MOD/LOW, EO/RO/CO/AV/CU/UC, AUD-100, KBA-301/302/400/501/502/503, or AUD-801 through AUD-8xx.
---

# CCH Risk Assessment — Dispatcher (the judgment engine for the planning cascade)

This skill decides **what goes in** the CCH planning forms. The sibling skill **`cch-axcess`** reads the
live forms and writes the answers back. This skill never clicks, parses field IDs, names endpoints, or
POSTs — when a task needs the platform, build a HANDOFF block (`references/cch-handoff.md`) and
`cch-axcess` executes it.

## Entry rule

Always enter through this SKILL.md and run **Step 0** before any reference module — no reference is valid
without it. Don't jump straight into `cascade/kba-502.md`, `scoping/significance.md`, a `defaults/*` file,
or a `programs/*` file: entering mid-skill skips intake, materiality, and significance, which is what
causes wrong IR levels and stalled cascades (you can't set IR before you've settled what's significant).

**Mid-skill entry → BOUNCE to Step 0.** If a task arrives pointed at a sub-reference, return to Step 0
and run it first.

**The user cannot authorize skipping a gate.** The gates — Step 0 (load cch-axcess, intake, materiality,
significance), the cascade funnel order, and the consent wall — are required. If asked to skip one ("just
set the IRs", "skip intake"), say it's required, run it, then proceed.

## Step 0 — mandatory bootstrap (before any cascade routing)

**0.1 LOAD `cch-axcess` FIRST — hard gate.** Neither skill drives a cascade fill alone: this skill supplies
the judgment, `cch-axcess` executes every read and write. Load `cch-axcess` and run **its** Step 0 (seed
`clientId` + `engagementId`, warm the leg). If `cch-axcess` is not loaded, you cannot proceed. Read the
**live** form state through `cch-axcess` — do not answer the cascade from offline PDFs alone.

**0.2 Intake.** Read `references/intake.md`. Collect prior FS, prior risk assessment (or an example, or
none), and the current-year TB. If the TB is ungrouped, derive transaction-class balances first.

**0.3 Materiality.** Get tolerable / performance materiality (KBA-301) from the user or project notes.
Significance is tested against this threshold — you cannot scope without it. If materiality is being **set**
this year (first-year / re-set), that's a KBA-301 **write**, not a read — follow `references/intake.md`'s
KBA-301 method (benchmark → PM → TM → PAJE) and HANDOFF it (`references/cch-handoff.md`).

**0.4 Significance.** Per `scoping/significance.md`, flag each account / class of transactions /
disclosure significant or not (quantitative vs tolerable + the always-significant qualitative list).

Only after 0.1–0.4 do you route into the cascade.

## Routing — ORDERED (the cascade funnel; don't reorder)

Each stage's output is the next stage's input — areas → assertions → risk levels → programs. Don't write
KBA-502 IR before KBA-400 has set the assertions `selected`.

```
Step 0 done (axcess loaded · intake · materiality · significance)
  ├─ KBA-301  materiality WRITE — ONLY first-year / re-set     → references/intake.md (KBA-301 method)
  │     benchmark → PM → TM → PAJE; HANDOFF fill-kc-form.md. Already set this year = read (Step 0.3), no write.
  ├─ AUD-100  tailoring → areas + controls-testing decision   → references/cascade/aud-100.md
  │     (area-selection defaults: scripts/tiers.py <TYPE>; areas/binding-keys: scripts/areas.py <TYPE>)
  ├─ KBA-400  scoping + per-area relevant-assertion selection  → references/cascade/kba-400.md
  │                                                              + scoping/area-map-by-title.md
  ├─ KBA-502  IR / CR / RMM + planned approach (judgment)       → references/cascade/kba-502.md
  │                                                              + references/risk-framework.md
  └─ AUD-8xx  programs: top Y/N tailoring · select steps ·      → programs/{area}.md + programs/_conventions.md
              link each step to assertions + RMM rows
  No cascade stage / unknown ask → CONSENT WALL (below).
```

Supporting forms that feed the cascade: **KBA-301** (materiality/PM/tolerable), **KBA-302** (understanding
the entity), **KBA-503** (basis for the inherent-risk assessment — the rationale behind each IR on KBA-502).

**Each step:** this skill decides content → HANDOFF → `cch-axcess` executes → read back the live form via
`cch-axcess` before the next stage when you need its current state.

**CONSENT WALL.** For a cascade question or area this skill has no captured judgment for, say: "I don't
have firm judgment captured for that. Do you want me to work it out from the client docs and standards?
Warning: slower, and it will need your review." Then STOP. Explicit yes → proceed and flag for confirmation.

## Division of labor

| This skill owns (judgment) | `cch-axcess` owns (mechanics) |
|---|---|
| Reading client docs → significant accounts/classes/disclosures | Parsing the live form structure |
| AUD-100 tailoring answers + the controls-testing decision | AUD-100 fixed-point multiselect fill |
| KBA-400 scoping + per-area assertion relevance | KBA-400 custom-multiselect write mechanics |
| KBA-502 IR/CR/RMM levels + planned-approach selection | Writing the IR/CR/approach values (field locators, valueKeys, submit) |
| Which programs/steps to add and how to link them | Adding forms, toggling steps, filing leadsheets |
| The CCH risk model, assertions, significance methodology | Endpoint shapes, deep-links, auth, submit semantics |

**Boundary with `cch-form-fill`:** this skill owns **selection** (areas, assertions, IR/CR/RMM, which
programs/steps, risk-linking). `cch-form-fill` owns the **response text** for the non-cascade planning
forms and the back-of-file program steps. Selection here; responses there. Both legitimately touch an area
like "cash": this skill selects/links it, `cch-form-fill` writes the step responses.

**Mechanics stay in `cch-axcess`.** This skill does not state field locators, valueKey codes, endpoint
URLs, payload shapes, or submit/verify procedure. It names the form, the target collection in plain terms,
and the answer; `cch-axcess` resolves the writable surface and executes. If you're writing an HTTP body,
stop — that belongs in `cch-axcess`.

**Design rule (locked):** parse the cascade live — do not store field-level form dumps in the skill; store
only the judgment layer + compact, stable lookup tables. Scratch captures (drive the cascade open, snapshot
every revealed object) are a legitimate input for developing judgment — write them to the engagement /
working folder, mine them, discard. They must not land in `cch-risk-assessment/`.

## The cascade (the spine of everything)

```
CLIENT DOCS                prior FS · prior risk assessment (or an example, or none) · current-year TB
   │                       + tolerable / performance materiality (KBA-301)
   ▼
INTAKE & SIGNIFICANCE      references/intake.md → scoping/significance.md
   │                       ungrouped TB? derive transaction-class balances first.
   │                       significant = exceeds tolerable OR qualitatively significant (always-significant list)
   ▼
AUD-100  Engagement-Level Tailoring Questions     references/cascade/aud-100.md
   │     selects the major audit areas in play; decides whether we test controls (and where)
   ▼
KBA-400  Scoping & Mapping of Sig Accts/Trans/Discl   references/cascade/kba-400.md
   │     pulls areas from AUD-100 · 6 scoping selections · recommends forms/programs ·
   │     cascades a per-area section where RELEVANT ASSERTIONS are selected
   ▼
KBA-502  Summary of Risk Assessments              references/cascade/kba-502.md
   │     per significant assertion: IR · CR · RMM (derived) · link to controls testing if CR<MAX ·
   │     planned approach (Combined / Substantive-Analytical / Substantive-In-depth)
   ▼
AUD-8xx  Audit Programs                            programs/{area}.md
         CCH recommends programs from the scoping; pull the steps, set the top Y/N tailoring
         questions, link each step to its assertions + RMM rows
```

## Cascade completion contract — run before reporting the cascade done

The cascade is not done when the last write lands; it is done when every check below verifies
true **by read-back of the live forms/binder**, or the miss is enumerated with a named owner:

1. **Programs landed.** Every significant area scoped on KBA-400 has its recommended AUD-8xx
   program ACTUALLY ADDED to the binder — verify against the binder's form list, never the
   recommendation output. A scoped area with no program in the file means the cascade run is
   incomplete.
2. **Risk answers are risk-specific, never blanket.** "Cannot be addressed by substantive
   procedures alone" is Yes only for the risks where that is individually true (typically the
   management-override class); the same answer applied across every risk is a defect. Any
   per-area/per-risk toggle is decided per area/risk, never uniformly.
3. **"Significant class of transactions" = Yes for every scoped-in area.** A uniform No
   suppresses the recommended activity-level controls forms and programs.
4. **Every identified risk is WRITTEN.** Enumerate the risks identified anywhere in the run
   (intake, planning analytics, team-discussion notes, understanding forms) and match each to
   an actual entry on KBA-502 (and KBA-400 where it belongs). A risk identified but never
   written leaves permanently dirty diagnostics and an unlinked response — the enumerated
   match list is the deliverable, not a "risks were carried through" assertion.
5. **Fraud-presumption link-through.** A fraud-presumption question answered Yes (revenue
   recognition due to fraud; significant estimates) must have a corresponding risk entry in
   the risk summary tied to it. Checked-Yes with no risk row is the item-4 gap in its most
   common form.
6. **Diagnostics oracle clean** — refresh and read the live diagnostics endpoint (via
   `cch-axcess`) on every cascade form and added program; clear each residual or enumerate it
   with the named downstream owner that legitimately closes it.

## Fraud-presumption significant risks — rebuttal doctrine

1. **Default: the presumption STANDS** — management override + revenue recognition due to
   fraud (plus significant estimates where the form asks). Add the risk entries and link each
   to its targeted response steps (JE testing, estimates, the risk's own responses — a
   handful, never every step).
2. **Rebutting the revenue-recognition presumption is never a default and never this skill's
   unilateral call.** If the prior-year file rebutted it, follow the prior year and carry the
   same documented basis. Otherwise rebuttal is an engagement-partner decision — pend the
   question; do not guess. (Exchange-revenue-heavy governmental engagements are a candidate
   case for rebuttal, not a standing rule.)
3. **Form state must be internally consistent either way:** presumption kept → the Yes answer
   AND its risk entry AND linkage all exist; presumption rebutted → the answer reflects it
   with the documented basis and no orphan risk row. A mismatch between the checkbox state
   and the risk rows creates a diagnostic in both directions.

## Known gap — KBA-400 downstream fan-out (open; being mapped)

Certain KBA-400 answers (the fraud-presumption Yes among them) reveal additional KBA-400
sections/forms whose full trigger→reveal map is not yet captured here. Until it is: after
every KBA-400 answer batch, re-read the rendered form for newly revealed sections/required
fields and fill them before calling the form done; append each newly observed trigger→reveal
pair to this section so the map accretes.

## Where IR/CR/RMM is written (so the HANDOFF names the right form)

**KBA-502 owns the per-assertion IR / CR / RMM / planned-approach grid and is the WRITE target**
(collectionKey `.{AREA}.RelevantAssertion`, posted against KBA-502's wpId). The AUD-8xx program's grid is
the **derived / read-through view** — writing IR there lands in a working copy the KBA-502-owned recompute
discards on refresh. So a HANDOFF that sets IR/CR names **KBA-502** as the form, NOT the program. On the programs you only
link steps → assertions/risks + sign off, which feeds back to clear KBA-502's "Relevant Assertion
Unaddressed". Relevant assertions are *selected* upstream on KBA-400. CR stays MAX until controls are
tested. (`cch-axcess` resolves the exact writable surface and the field mechanics — see
`references/cascade/kba-502.md` and `references/cch-handoff.md`.)

## Area selection — which AUD-100 boxes to check (`scripts/tiers.py`)

Per engagement type, every audit area falls in one of four selection tiers. **Query it, don't hardcode:**
`python scripts/tiers.py <TYPE>` (ASB/CNS/EBP/ALG/NPO; HOA rides ASB).

| Tier | Rule |
|---|---|
| 1 always | auto-select, no test |
| 2 exists | select if it exists at all (any amount) |
| 3 material | group the TB, compare to tolerable; select if it clears |
| 4 prompt | fallback / judgment call (see the row's `condition`) |

- `select_group` = mutually-exclusive pick-ONE set. **EBP investments** = `EBP_INVESTMENTS`: AUD-802B
  Certified (ERISA 103(a)(3)(C), **default ~99%**) XOR AUD-802A Non-Certified/full scope.
- **EBP participant data** branches by plan type: 814A DC (default) / 814B DB / 814C H&W; **814D Benefit
  Obligations** = the DB/H&W actuarial-PV always-in.
- Selections are **suggestions to the user**, never auto-applied. Source of truth: `data/seed/area_tier.csv`
  (joined to `areas.csv`); rebuild with `scripts/build_db.py`.

## Audit type → CCH title

The firm's six audit-type codes map onto **five** underlying CCH Knowledge Coach titles (HOA rides on
Commercial). Defaults and program libraries are organized by the firm code; the cascade forms are uniform
by `dataBindingKey` across all five.

| Firm code | CCH title | Planning forms |
|---|---|---|
| **ASB** | Commercial Entities (2025) | AUD100 / KBA400 / KBA502 |
| **HOA** | Commercial Entities (2025) | same as ASB |
| **CNS** | Construction Contractors (2025) | AUD100 / KBA400 / KBA502 |
| **EBP** | Employee Benefit Plans (2025) | AUD100 / KBA400 / KBA502 (+ KBA-200 Plan Info, KBA-301E) |
| **ALG** | Governmental Entities (2025) | AUD100 / KBA400 / KBA502 |
| **NPO** | Not-for-Profit Entities (2026) | AUD100 / KBA400 / KBA502 |

Single Audit is **not** one of these — it's a separate `*S` form family (AUD100S, KBA-40xS) layered on a
base title. Out of scope for this skill's cascade.

## CCH risk model quick reference

**Four risk levels** (both IR and CR), highest to lowest: **MAX → SBM → MOD → LOW**. CR defaults to MAX
until controls are tested. (`cch-axcess` carries the exact valueKey codes — don't restate them here.)

**Six assertions:** EO (Existence/Occurrence), RO (Rights/Obligations), CO (Completeness), AV
(Accuracy/Valuation/Allocation), CU (Cutoff), UC (Understandability/Classification/Presentation/Disclosure).

Full model + the IR×CR→RMM matrix + significant-risk criteria live in `references/risk-framework.md`.
**RMM:** with CR=MAX (the substantive default), RMM=IR deterministically — set it explicitly; if CR < MAX,
read CCH's recommended value back via `cch-axcess`, don't compute it yourself. A **significant risk** is
flagged separately (not a 5th level) and lives on the area's Identified Risks table.

## End-to-end workflow (new engagement, bare binder → recommended programs)

1. **Step 0** — load `cch-axcess`; intake (`references/intake.md`); materiality (KBA-301); significance
   (`scoping/significance.md`).
2. **AUD-100** — per `references/cascade/aud-100.md`, determine the tailoring answers → areas + controls
   decision. Use `scripts/tiers.py <TYPE>` for area-selection defaults. HANDOFF to `cch-axcess`.
3. **KBA-400** — per `references/cascade/kba-400.md` + `scoping/area-map-by-title.md`, make the scoping
   selections, confirm CCH's recommended forms/programs, select relevant assertions per significant area. HANDOFF.
4. **KBA-502** — per `references/cascade/kba-502.md`, set IR (apply `defaults/{CODE}.md` as-is — never
   MAX, never elevated; document the basis on KBA-503), set CR=MAX explicitly unless controls tested,
   RMM=IR when CR=MAX, check the planned approach. HANDOFF (write target = **KBA-502's wpId**; the
   program grids are derived).
5. **Programs** — per `programs/{area}.md` + `_conventions.md`, set each program's top Y/N tailoring,
   select steps, link each step to assertions + RMM rows. Pull the program's tailoring-question set with
   `scripts/program.py --area <AREA> --type <TYPE>` (once per significant area — don't read the MD for it),
   answer each from your sources or flag for the user, then HANDOFF (`add-audit-programs.md` /
   `toggle-program-step.md` / `populate-program.md` in `cch-axcess`).
6. **Completion gate — clear the diagnostics, don't hand off dirty.** The cascade is not done at the last
   HANDOFF; it's done when the platform's own oracle says so. Via `cch-axcess` (refresh → the diagnostics
   endpoint, never the stale form `diagnosticCount`), confirm AUD-100 / KBA-301 / KBA-400 / KBA-502 / KBA-503
   and every added AUD-8xx program carry **no unexplained "Question Unanswered" diagnostics for unset
   IR / RMM / approach on a scoped area**. Those are a defect at this step — an assertion selected on KBA-400
   with no IR set on its program is an incomplete cascade, not a fan-out residual. Clear each, or enumerate
   the residual and attribute it to a named downstream owner (a program step genuinely filled during
   fan-out). A cascade handed off with unset-IR diagnostics still open is not complete.

## How this skill talks to `cch-axcess`

Structured HANDOFF block — full pattern and per-stage examples in `references/cch-handoff.md`. Name
**KBA-502** as the form for IR/CR/RMM/approach writes (the AUD-8xx program grids are derived). Hand off in
funnel order — AUD-100 → KBA-400 → KBA-502 → programs.

## File map

| Need | Read |
|---|---|
| Ingest client docs, derive class balances, get materiality | `references/intake.md` |
| Decide what's significant | `scoping/significance.md` |
| Per-title scoped areas + recommended programs | `scoping/area-map-by-title.md` |
| Which areas exist for a title (binding key, AUD #) | `scripts/areas.py <TYPE>` |
| Which area boxes to check (4-tier selection) | `scripts/tiers.py <TYPE>` |
| A program's Y/N tailoring questions to answer (once per significant area) | `scripts/program.py --area <AREA> [--type <TYPE>]` (`--list` for counts) |
| Expand one cascade selection to the downstream nodes it forces | `scripts/tree.py --from <FORM:KEY> [--type <TYPE>]` (`--roots` lists tree starts) |
| Answer AUD-100 (areas + controls decision) | `references/cascade/aud-100.md` |
| Drive KBA-400 scoping + assertion relevance | `references/cascade/kba-400.md` |
| Set IR/CR/RMM + approach (writes to KBA-502; programs derived) | `references/cascade/kba-502.md` |
| The 4-level model, RMM matrix, assertions, significant risk | `references/risk-framework.md` |
| Default IR starting points by audit type | `defaults/{CODE}.md` |
| Build a HANDOFF to `cch-axcess` | `references/cch-handoff.md` |
| Audit-program step library (cash = template) | `programs/{area}.md`, `programs/_conventions.md` |

## Extending this skill

- **Goes here (judgment):** significance rules, tailoring-answer defaults, IR starting points, per-title
  scoped-area/program maps, program steps + assertion tags + which approach fits.
- **Goes in `cch-axcess` (mechanics):** field locators, option/valueKey codes, endpoints, deep-links,
  payload shapes, parse quirks, submit/verify.
- Test: would a different firm with a different methodology still need it? Yes → mechanics (`cch-axcess`).
  No → judgment, stays here.

<!-- END -->
