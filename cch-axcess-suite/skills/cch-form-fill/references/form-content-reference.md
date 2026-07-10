# cch-form-fill — Cross-Reference Recognition Index + per-step Fill Rule

_The resident, always-on layer (~3–4K tokens). Load this for the whole engagement; it is what lets the engine, while grinding ~20 forms / hundreds of steps, recognize "this belongs on another form — and which one."_

Built 2026-06-25 from a live capture of all 4 standard binders (NPO / Govt-Single-Audit / Commercial / EBP), 98 distinct forms.

---

## 0. Per-step cross-reference rule

Run this on **every step**, before composing an answer. This rule, not the data, is what raises the hit rate — the index does nothing if the engine doesn't consult it each step.

```
For each step/question:
1. TOPIC — derive it from the collection-path key (e.g. .AUD901.SubsequentProcedure → "subsequent events")
   plus the question text.
2. OWNED ELSEWHERE? — scan the Recognition Index (§2) for that topic. Is it owned by a form
   OTHER than the one you're filling?
3. IF YES and it's adequately documented on that owning form this engagement →
   answer with a CROSS-REFERENCE to that form's REAL binder index (resolve via cch-axcess GetBinder),
   not an inline re-answer. Firm phrasing = a WP/KC index ref; match the question's tense.
4. IF the step is ON the owning form itself → answer it substantively; never self-reference.
5. BACKBONE AUTO-REFS — in any AUD-8xx program, the control/sampling/confirmation/disclosure/estimate
   steps ALWAYS carry the backbone refs (§3); emit them without re-deriving.
6. CROSS-AREA SOURCING — if the answer is corroborated by another area's work
   (cash restrictions ← debt/grants; estimate bias ← the area programs' series WP refs), reference that work.
7. GUARDRAILS — only reference a form/WP that EXISTS in this binder (confirm via GetBinder). If the owning
   form isn't in the binder, answer inline or flag. Never reference a topic the owning form doesn't cover this year.
Default to an inline answer only when no owner matches.
```

## 1. Disposition codes
**Write precondition:** only apply this cascade to WRITE fields when `SKILL.md` Operating model steps 1–3 are complete for THIS engagement (entity type determined, binder read, gather/confirm batch surfaced) — or a valid `engagements/<client>/form-fill-context.md` gather artifact exists for this engagement (fleet mode; see `SKILL.md`). If you arrived here from a lookup or are otherwise uninitialized, stop and run `SKILL.md` step 1 first (or, inside a fleet section bot, request the artifact from `0200-planning-risk` and mark the fill pending) — never fill from a lookup-only state.

**Answer cascade — strict order, take the first rung that hits. ~75% of this job is generic answers to boilerplate, so default to FILLING:**
1. **[X] cross-reference** — topic owned by another form (§2) → reference it.
2. **[K] known answer** — a specific answer the gathered info / engagement facts give you (named people, dates, entity facts) → write it.
3. **[C] confirm-default** — the item has a firm default that is almost always *no/none* but where a "yes" is rare AND material: subsequent events, going concern, litigation/contingencies, related party, management bias in estimates, significant/unusual transactions, business combinations, control/compliance deficiencies — plus the KBA-201 "are you aware of any…" integrity/fraud/independence block. Apply the no/none default, but it MUST have been surfaced once in the gathering-phase confirm batch (`defaults.md` → confirm-default list; `knowledge-inventory.md` gather order) so a real exception is caught before write. Never silently write a [C] item that wasn't confirmed.
4. **[D] generic firm-standard default** — otherwise FILL the standard boilerplate, **no confirmation**. Control/COSO forms are affirmations, e.g. "Does the entity commit to monitoring activities?" → "Yes, the entity commits to monitoring activities." Auto-fill it; the user reviews the completed binder.
5. **Leave blank** — ONLY a truly specific item needing genuine engagement input that can be neither referenced, known, defaulted, nor confirmed.

**Expand-gate guard:** never let a [D]/[C] default answer a gate that *expands* a checklist (e.g. AID-201 nonattest "Yes" balloons the prohibited-services list). Answer expand-gates conservatively (No / leave) unless the triggering service or condition is actually known.

Read the section from the **collection-path key**, not bold text; `a=false` ⇒ display-only.

---

## 2. Recognition Index — topic → owning form (with trigger phrasings)

When a step's topic matches a row here and you are NOT on the owning form, cross-reference it.

| Topic | Trigger phrasings in a step | Owning form (by entity) | Carries / notes |
|---|---|---|---|
| **Subsequent events** | "subsequent event(s)", "after the (FS/balance-sheet) date", "through the report date", "subsequent period" | **AUD-901** (AUD-901S = compliance/SA) | itself → AID-837/845 (minutes), COR-901 (rep) |
| **Going concern** | "going concern", "substantial doubt", "ability to continue", "liquidity / debt maturities" | **AUD-902** (GC program) + **AUD-909** + library **AUD-905/906** | live AUD-101 routes GC → AUD-902; phrasing.md has the GC conclusion wording |
| **Fraud — evaluation/response** | "fraud", "fraud risk", "management override", "improper revenue recognition", "misappropriation" | **AUD-903** | inquiries → KBA-303; brainstorming → KBA-501 |
| **Fraud/noncompliance inquiries (named people)** | "inquiries of management/TCWG/internal audit about fraud" | **KBA-303** (KBA-303S) | [A] no default; other forms citing fraud inquiries point here |
| **Laws & regs / NOCLAR** | "noncompliance", "laws and regulations", "illegal acts", "violations of grants/contracts" | **AUD-904** | → KBA-303 |
| **Accounting estimates / management bias** | "estimate", "allowance", "reserve", "impairment", "useful life", "fair value", "valuation", "management bias" | **AUD-820** (program) + **KBA-105** (bias review) | EBP fair value → **AUD-818**; bias usually cited as series WP refs |
| **Related parties** | "related party", "related-party transaction", "party-in-interest" (EBP), "arm's length" | **AUD-817** NPO / **AUD-815** Commercial / **AUD-814** Govt / **AUD-813** EBP | entity-specific program ID |
| **Commitments & contingencies** | "commitment", "contingency", "litigation", "claims", "guarantees" | **AUD-819** (multi) / **AUD-817** NPO | |
| **Management representation** | "representation letter", "management representations" | **COR-901** | ← KBA-102, KBA-104, AUD-901 |
| **Minutes (governance)** | "minutes", "board/governing-body meetings" | **AID-837** Govt / **AID-845** NPO | answer = the minutes-memo WP index |
| **Control deficiencies** | "deficiency", "significant deficiency", "material weakness" | **KBA-103** (103S / 104S compliance) | lesser → COR-912; rolls up to KBA-102 |
| **Misstatements / omitted disclosures** | "misstatement", "uncorrected/corrected", "passed adjustment", "omitted disclosure", "SUM" | **KBA-104** | rolls up to KBA-102 |
| **Materiality** | "materiality", "performance materiality", "trivial threshold", "benchmark" | **KBA-301** (301E EBP / 301S SA) | |
| **Engagement completion / significant matters** | "significant matter", "engagement completion", "significant findings" | **KBA-102** (102S) | aggregator; pulls COR-901, KBA-103/104/105 |
| **Independence / nonattest** | "independence", "nonattest services", "safeguards", "GAGAS independence" | **AID-201** | |
| **Risk of material misstatement (summary)** | "RMM", "risk of material misstatement", "assessed risk", "inherent/control risk" | **KBA-502** (502S) + **KBA-503** (503S, IR basis) | every program ties here |
| **Understanding the entity & environment** | "understanding the entity", "industry/regulatory/economic", "business operations", "objectives & strategies" | **KBA-302** (302S) | [M] narrative home |
| **Entity-level controls / COSO** | "entity-level controls", "COSO", "control environment", "five components" | **KBA-401** (401S) | |
| **General IT controls** | "general IT controls", "ITGC", "information systems", "IT environment" | **KBA-402** (402S); **AID-401S** (SA ITGC) | |
| **Activity-level controls / walkthroughs** | "walkthrough", "transaction cycle", "control activities", "subprocesses" | **KBA-403/405/406/407/408/409/410/411** by cycle | |
| **Scoping / significant accounts & disclosures** | "scoping", "significant account/class/disclosure", "mapping" | **KBA-400** (400S = UG requirement matrix) | |
| **Acceptance & continuance** | "acceptance", "continuance", "predecessor auditor", "client integrity" | **KBA-201** | |
| **Team discussion / brainstorming** | "team discussion", "brainstorming", "professional skepticism", "fraud presumptions" | **KBA-501** | |
| **Specialist** | "specialist", "auditor's/management's specialist" | **AUD-601 / AUD-602** | referenced from AUD-101/202 |
| **Component / group audit** | "component", "group audit", "component auditor", "SAS-149" | **AUD-603/604**; SAS-149 sections in AUD-101 | |
| **Review & supervision / approval** | "review", "supervision", "detail/concurring/EQ review", "approval", "EQR" | **KBA-902** (review & approval) / **KBA-903** (EQR/documentation); **KBA-902S** | the supervision/review home |
| **Audit documentation completeness** | "documentation", "file assembly", "AU-C 230", "60-day" | **KBA-904** (903S/904 compliance) | |
| **Opening balances / initial audit** | "opening balances", "initial/first-year audit", "predecessor balances" | **AUD-201** | |
| **SEFA (single audit)** | "SEFA", "schedule of expenditures of federal awards" | **KBA-901S** | |
| **A compliance requirement (single audit)** | "allowable costs", "eligibility", "reporting", "procurement", "period of performance", … | the matching **AUD-8xxS** program + **KBA-400S** matrix | |
| **EBP — participant data/accounts** | "participant data", "eligibility", "allocations", "demographic" | **AUD-814A** | |
| **EBP — benefit payments** | "benefit payment", "distribution", "hardship withdrawal" | **KBA-404** controls + the benefit-payments program | |
| **EBP — plan tax status** | "tax status", "determination letter", "Form 5500", "qualification" | **AUD-810** | |
| **EBP — §103(a)(3)(C) limited scope** | "limited scope", "certification", "103(a)(3)(C)", "certified investments" | **COR-201A** (eng letter) + **AUD-802B** (certified investments) | |

## 2a. False-positive guard — keyword ≠ cross-reference (validated 2026-06-25 cold test)

A topic-map (§2) cross-ref fires ONLY when the step's **section-key/context** matches the topic's domain AND this form is **not itself the topic's owner**. An explicit in-text form-ID (`r`) is always reliable — emit it. Do NOT route on an incidental keyword:

- "Subsequent **Bank Statements**" in a cash `ProgramSteps` section is a cutoff procedure — **not** subsequent events; route to AUD-901 only when the section-key is a `Subsequent*` section.
- "remained alert for **fraud**" / "previously unrecognized fraud risk" on AUD-909 are that form's own review steps — **not** → AUD-903.
- "**representation**," "**misstatement**," "**subsequent**," "**related party**" appearing in passing inside a form that owns or only mentions them → generic, not a cross-ref.

Rule of thumb: in-text `r` → always cross-ref; topic-keyword alone → cross-ref only if the section-key agrees and the form isn't the owner; otherwise generic.

## 2b. Form-ID is per-title — the SAME number is a DIFFERENT program on different entity titles

CCH reuses AUD/AID/COR/KBA numbers across entity titles. **Never assume a number's meaning without checking the entity type.** When §2 sends you to a form, resolve its real ID for THIS title here, then confirm it exists via `GetBinder`.

| Program / topic | Govt | NPO | Commercial | EBP |
|---|---|---|---|---|
| Related party / party-in-interest | AUD-814 | AUD-817 | AUD-815 | AUD-813 |
| Journal entries | AUD-813 | AUD-816 | AUD-814 | AUD-812 |
| Net assets / equity | AUD-811 (net position/fund balance) | AUD-814 (net assets) | AUD-812 (equity) | NAAB — trivial |
| Revenue / contributions | nonexchange (substantive) | AUD-805 (contributions) | AUD-803 (ASC 606 rev/AR) | AUD-803 gate (contributions) |
| Inventory | rare | rare | AUD-804 | n/a |
| Split-interest agreements | n/a | AUD-804 | n/a | n/a |
| Income tax / plan tax status | n/a | AUD-812 (UBI/tax) | AUD-810 (income tax) | AUD-810 (plan tax status) |
| VIE / consolidation | n/a | n/a | AUD-817 | n/a |
| Estimates / fair value | AUD-822 / AUD-815 (FV) | AUD-820 / AUD-818 (FV) | AUD-820 / AUD-816 (FV) | AUD-818 / AUD-816 (FV) |
| Commitments & contingencies | AUD-821 | AUD-819 | AUD-819 | AUD-817 |
| Participant data | — | — | — | AUD-814A(-D) |
| Benefit payments | — | — | — | AUD-809 |
| Investments | AUD-802 | AUD-802 | AUD-802A (802B = derivatives/hedging) | AUD-802A non-certified/ERISA / AUD-802B certified |

*Verified/corrected 2026-07-07 against the live KC title library (GetWorkpaperListForAddForms:
GOV.2025.1, NFP.2026.1, COM.2025.1, EBP.2025.1) — the earlier rows carried six wrong/unresolved
cells (JE Commercial+EBP, Govt equity, EBP+Commercial FV, Commitments Govt/NPO/EBP). Numbers
shift on title re-versions: reconcile with `cch-risk-assessment/scoping/area-map-by-title.md`
(same live verification) and re-pull when editions change.*

**Collision watch — the wrong-pull traps (resolve by entity title every time):**
- **AUD-813** = Journal Entries on Govt/NPO concluding, but = related-party / party-in-interest on **EBP**.
- **AUD-814** = Related Party on Govt, but = Net Assets on **NPO** (and AUD-814A = participant data on EBP).
- **AUD-817** = related party on NPO, = **VIE on Commercial**, = commitments & contingencies on **EBP**.
- **AUD-810** = income taxes on Commercial, but = plan tax status on **EBP**.
- **AUD-804** = inventory on Commercial, but = split-interest on **NPO**.
- **AUD-812** = equity on Commercial, but = UBI/tax on **NPO**.
- **AUD-803** = ASC-606 revenue on Commercial, but = contributions gate on **EBP**.

Cells marked "—", "n/a", "(folded; confirm)" are not separately captured for that title — the program is folded elsewhere or does not apply; confirm via `GetBinder` before referencing.

## 3. Backbone auto-references — every AUD-8xx substantive program

Recognize the program spine and emit these without re-deriving (they recur on hundreds of steps):

- `ConTestingEffControlQuestion` → **KBA-502** (risk) + [D] no control reliance / substantive.
- sampling step → **AUD-701**; confirmation step → **AID-701 / AID-702**.
- `ResultsQuestion` disclosures → **KBA-901** (**KBA-901S** SEFA on compliance programs).
- estimates tail → **AUD-820** (NPO/Commercial) · **AUD-822** (Govt) · **AUD-818** (EBP fair value).
- risk basis → **KBA-503**.
- `-S` compliance programs use **KBA-502S / AUD-701S** and drop the Results/KBA-901 tail.

## 4. Hubs — the highest-volume reference targets (expect to point here often)

**KBA-502** (risk, ~every program) · **AUD-701 / AID-701 / AID-702** (sampling/confirmation) · **KBA-901/901S** (disclosures/SEFA) · **AUD-820/822/818** (estimates) · **KBA-102/102S** (completion aggregator) · **COR-901** (rep letter) · **KBA-902/903** (review/supervision) · **AID-201** (independence) · **AID-837/845** (minutes).

## 5. Universal fill patterns (so the engine recognizes a form's shape fast)

- **AUD-8xx programs (~all substantive):** `OverallTailoring` [D substantive] · `AuditObjective` display-only **don't fill** · `ConTestingEffControl` [X→KBA-502]+[D] · `TailoringQuestions` [L from TB, drives N/A-gating] · `ProgramSteps` [M coverage — "material RMM covered, residual immaterial/NCN"] · `ResultsQuestion` [D none]+[X→KBA-901].
- **Control cycles (KBA-403–411):** `CycleMemorandum` [M] · `CycleSufficientEvidence` [D Yes] · `EvaluateSubprocesses` [M/D present & functioning] · `Conclude` display-only.
- **Review/documentation checklists (KBA-902/903/904 +S):** [D] attestations throughout; sign-offs [A]; whole blocks TQ-gated (concurring/EQR/GAGAS/component/KAM).

## 6. Headings & N/A-gating (detection grounding)

- Section structure = the **collection-path key**, not bold text (~95% of forms carry no bold headings).
- **Heading-with-answer** (a bold heading that itself takes an answer) is rare and concentrated in **AUD-100, AUD-101/101S, KBA-401S** — handle those as special cases; elsewhere bold = display-only.
- **N/A-gating is pervasive:** a driver toggle (predecessor, related parties, H&W plan, integrated audit, SAS-149, de-minimis) gates a block; when it's the default No, N/A the block with the reason once at the top.

## 7. Entity-type deltas

- **Govt-Single-Audit** — full `-S` compliance twin suite (AUD-100S/101S, AUD-7xxS/8xxS, KBA-4xxS, KBA-901S SEFA, KBA-902S/903S); compliance programs key off the UG requirement matrix (KBA-400S) and KBA-502S/AUD-701S.
- **EBP** — AUD-202 (planning), AUD-814A (participant data), AUD-813 (party-in-interest), AUD-810 (tax status), COR-201A (§103(a)(3)(C) letter), KBA-404/406/410, KBA-301E; estimates → AUD-818.
- **Commercial** — AUD-807 (PP&E), AUD-808 (AP), AUD-812 (equity), AUD-815 (related party superset).
- **NPO** — AUD-805 (contributions/support/program rev), AUD-816 (JEs), AUD-818 (fair value), AUD-820 (estimates), AUD-821 (concentrations), AUD-909 (FS review).

---

## Loading model

- **Always-on:** this file — the recognition index (§2), the per-title form-ID map (§2b), and the per-step rule (§0). Load first; keep resident.
- **On-demand, per task:** the per-area files already shipped in `references/` — `section-library.md`, `planning-sections/section-01…06.md`, `type-commercial.md` / `type-npo.md` / `type-ebp.md`, `sa-module.md`, `defaults.md`, `approach-decision.md`, `phrasing.md`, `knowledge-inventory.md`. Pull the one that fits the form/area you are on.
- There are no external `captures/` files to load at run time — everything the engine needs ships in `references/`.
