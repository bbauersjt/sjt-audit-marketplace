---
name: cch-form-fill
description: >-
  Fills CCH Axcess Knowledge Coach planning forms and audit program steps — the non-risk-assessment
  forms (entity information, acceptance, independence, predecessor, strategy, controls/COSO, fraud-inquiry
  logistics, team discussion, completion and review/documentation checklists) and the back-of-file audit
  programs (cash, receivables, investments, inventory, PP&E, payables, accruals/payroll, debt, equity,
  revenue, expense, and the EBP-specific areas), plus the Single Audit module — for governmental,
  nonprofit, commercial, and employee-benefit-plan audits. Determines context- and client-aware answers
  from the binder and engagement references and applies firm-standard confirmable defaults instead of
  generic placeholders. Companion to cch-axcess and cch-risk-assessment. Use whenever filling, completing,
  or answering CCH or Knowledge Coach planning forms, KBA/AID/AUD/COR forms, audit program steps,
  sign-offs, or references — even when the skill is not named.
---

# CCH Form Fill

> Last verified against cch-axcess AX-37 — 2026-07-07.

Fills the CCH Axcess Knowledge Coach planning forms and audit-program step responses that fall outside the risk cascade. Determine context- and client-aware answers, apply firm-standard confirmable defaults, and write them back through cch-axcess.

## First — classify the request (do this before anything else)

Two modes. Pick one **before** loading an engagement or touching a binder:

- **Lookup / question** — the user wants a fact this skill already knows (e.g., "which form owns subsequent events?", "what's the default for EQ review?", "what sample size for participant data?"). **Answer directly from the reference files, then stop.** Topic → owning form is `references/form-content-reference.md` §2 (resolve the per-title ID via §2b); defaults are `references/defaults.md`; per-area procedures are `references/section-library.md`. Do **not** mount a binder, call cch-axcess, run the Operating model, or open a gather batch. A lookup never needs an engagement.
- **Fill / complete forms** — the user wants form fields answered or written for a real engagement. Run the **Operating model** below in full. This is the only mode that touches a binder.

If the mode is ambiguous, ask one line — *"Looking something up, or filling a binder?"* — and do not start the Operating model until you know.

**Escalation rule (critical — this is the common failure):** pulling a fact does NOT initialize an engagement. If a request that started as a lookup turns into a fill ("ok, now fill AUD-901 for my client"), you are **not** initialized — go to Operating model **step 1** and run it from the top (determine entity type → read the binder → complete the gather/confirm batch) before writing anything. Never carry a half-initialized lookup state into a fill; if unsure whether steps 1–3 ran this engagement, run them.

## Scope

Own these:
- Planning/concluding forms: KBA-200 (entity information), KBA-201 (acceptance & continuance), AID-201 (nonattest independence), COR-203 (predecessor), AUD-101 (overall program), KBA-101 (strategy), AUD-201 (opening balances), KBA-302 (understanding the entity), KBA-303 (fraud inquiries — logistics only), AID-837 (minutes), KBA-401/402/40x (controls), KBA-501 (team discussion), KBA-102/103/105 (completion/deficiencies/estimates), KBA-902/903 (review & documentation checklists), AUD-901/909/813/814 (concluding pseudo-programs — IDs are govt; per-title in `references/form-content-reference.md` §2b).
- Back-of-file audit programs: cash, investments, receivables, inventory, prepaids/other assets, PP&E, payables, accruals/payroll, deferred revenue/grants, debt, equity, revenue, expense, interfund/transfers, and the EBP-specific areas (participant data, contributions, benefit payments, participant loans, participant accounts, investment income, administrative expenses).
- The Single Audit (8000) module.

Do not own — defer to `cch-risk-assessment`: AUD-100 tailoring, KBA-301 materiality, KBA-400 scoping, KBA-502/503 risk assessment, and program/assertion selection.

Use `cch-axcess` for every platform read and write.

## Operating model

Run against a mounted engagement folder and a live binder. **Load `references/form-content-reference.md` first and keep it resident for the whole engagement** — it carries the cross-reference recognition index (topic → owning form), the per-title form-ID map (§2b — the same AUD/AID number means different programs on different entity titles), and the per-step disposition cascade you apply to every field. Steps:

1. **Determine entity type.** Resolve the binder title through cch-axcess (`lastUsedTitleGuid`) and corroborate with the trial balance: standard (commercial / nonprofit / government) or EBP. Add the Single Audit module when the TB/SEFA shows federal awards. Type controls which reference files apply.

2. **Read the binder.** Through cch-axcess: `GetBinder` to list workpapers, then `read_form` + field inventory on each target form. Forms cascade — fields appear only after driver questions are answered, so read, answer drivers, re-read to a fixed point. Some forms are empty until a driver activates them (e.g., COR-203 needs a new-engagement flag).

3. **Gather knowledge, then confirm the exceptions in one batch.** Work `references/knowledge-inventory.md`. Glean every available fact from the mounted folder (PBCs, financials, trial balance, prior file, permanent file, policy memo) before asking anything. Then, in one batched pass: (a) collect the genuine knowns that have no default — named management, fraud-inquiry interviewees, dates, predecessor, nonattest designated individual, new-vs-continuing; and (b) confirm the **confirm-default** items — those that default to no/none but where a "yes" would be material (subsequent events, going concern, litigation/contingencies, related party, estimate bias, significant/unusual transactions, business combinations, control deficiencies, and the acceptance "are you aware of any…" block), each shown pre-set to its default for the user to flag exceptions. Ask the fewest questions possible. **This up-front batch is mandatory and is the gate before any write — it is not satisfied by per-form questions later. Complete it before writing the first field.**

4. **Apply the disposition cascade.** Use `references/form-content-reference.md` (§1) and `references/defaults.md`. For each field take the first rung that hits: **[X]** cross-reference → **[K]** known (from gather) → **[C]** confirm-default (apply the no/none default — already confirmed in step 3) → **[D]** generic firm-standard default (**auto-filled, no confirmation**) → **blank** (truly specific only). Generic boilerplate is the ~75% auto-fill default; the user reviews the completed binder, not each answer. Never let a default answer a checklist-*expanding* gate (e.g. AID-201 nonattest) — answer those conservatively unless the condition is known.

5. **Determine responses.** Use `references/section-library.md` (per-area procedures, wave-offs, distilled answers), `references/approach-decision.md` (when to conclude coverage is sufficient), and `references/phrasing.md` (wording and global rules). Build each answer from: the procedures performed (coverage), any materiality wave-off (stated), and the silent presumed-not-performed omissions (not stated).

6. **Handle defer-to-user areas.** For complex commercial capital structures and governmental OPEB/pensions with deferred outflows/inflows, do not auto-fill. Flag the area for the user and assist only under direction.

7. **Write back.** Build payloads and write through cch-axcess sequentially, verifying each with a re-read. Per-step sign-offs on AUD-8xx program steps are API-writable (`cch-axcess` `populate-program.md` + `field-conventions.md` — token goes in `valueKey`); the OVERALL/form-level sign-off (`kcc-workpaper-signoff`) is off-limits to the API and stays manual, through the UI.

**Write precondition (applies no matter how you got here):** before writing ANY field, steps 1–3 must be complete for this engagement — entity type determined, binder read, gather/confirm batch surfaced. If any is missing (you arrived from a lookup, or you are resuming mid-conversation), stop and run steps 1–3 first. Do not write from a partially-initialized state.

**Fleet mode — pre-built gather context:** when running inside the audit fleet (`bots/`), the
`0200-planning-risk` bot runs steps 1–3 ONCE per engagement and persists the result as
**`engagements/<client>/form-fill-context.md`** — entity type + platform, the gleaned [L] facts,
the [A] answers (named people, dates, predecessor, designated individual), the [C] confirm-batch
outcomes with a confirmed-on date, and the constants (reviewers, testing-WP indexes, report date).
A context artifact that matches THIS engagement (client + period) **satisfies steps 1–3**: read it
and go straight to per-form work — never re-run the gather or re-ask the confirm batch. If the
artifact is missing or stale, do **not** self-initialize from inside a section bot — report that
`0200-planning-risk` must supply it and mark the fill pending (fleet rule: `bots/RULES.md` §H).
Section bots contribute their own section's coverage + evidence refs as [K] inputs to step
responses. The concluding [C] items are re-confirmed at the end by `0600-concluding` from the
section status reports (`bots/RULES.md` §S) — update the artifact when any of them flips.

## Universal rules

Apply on every entity and every form:

- **Lead-out first (every balance-sheet account):** tie the client's supporting schedule/records to the TB and the TB to the FS; tie the TB to underlying support (statements, agreements, amortization schedules). Everything builds on this.
- **Agree activity through to records (every rollforward):** beginning + activity = ending, tied all the way through.
- **Test from a list that ties to the TB (every sample):** pull every selection from a population list that agrees to the TB or the number being opined on. Agree the list first, then select.
- **Mandatory-but-corroborative analytics:** where a program requires an analytic but substantive testing is the real evidence, perform the analytic but reference the substantive coverage that overrides it.
- **WP references are inferred from the binder, not hardcoded:** locate the workpaper by content and use its real index; the 4-digit scheme is a guide, since indexing varies.
- **Cross-area sourcing:** some answers are corroborated in one section but sourced from another (e.g., cash restrictions from grants/debt/PF). Reference the other-area work.

## Response construction

For each form/area:

1. Identify what could be materially misstated (the relevant assertions: recorded-but-wrong, completeness, valuation/estimates, presentation/disclosure).
2. State the coverage — the mandatory procedures that address each risk.
3. State any materiality wave-off — a procedure dropped because the residual exposure is immaterial.
4. Omit the presumed-not-performed steps silently.
5. For N/A blocks: put the explanation once at the header/gating step ("Steps are N/A — [reason]"); each sub-step gets "N/A".

See `references/approach-decision.md` for the coverage/materiality model and `references/phrasing.md` for the wording rules.

## Reference map

Read the file that fits the task:

- `references/form-content-reference.md` — **always-on; load first, keep resident.** The cross-reference recognition index (topic → owning form), the **per-title form-ID map (§2b — the same AUD/AID number maps to different programs on different entity titles)**, the per-step disposition cascade (§1), the AUD-8xx backbone auto-refs, and heading/N-A grounding.
- `references/knowledge-inventory.md` — the deduplicated list of what must be known per section, and how each item is sourced.
- `references/defaults.md` — the firm's default answers ([D] auto-fill / [C] confirm-default).
- `references/approach-decision.md` — coverage-of-RMM model, materiality wave-off, the three procedure buckets, controls-fallback.
- `references/phrasing.md` — global wording rules (narrative vs. WP reference, N/A top-line, list-ties-to-TB) and captured response wording.
- `references/section-library.md` — per-area procedures, wave-offs, and distilled answers for every back-of-file FS area (standard + EBP), plus the planning/concluding narratives (related party, controls/COSO, understanding the entity, FS review, SEFA).
- `references/cross-type-core.md` — what is shared across types and the per-type delta map.
- `references/type-commercial.md`, `references/type-npo.md`, `references/type-ebp.md` — per-type specifics.
- `references/sa-module.md` — the Single Audit module.
- `references/planning-sections/section-01.md` … `section-06.md` — the planning/concluding section maps (knowledge requirements, batched questions, defaults). These are the governmental(+SA) maps and **also serve as the govt per-type reference (there is no separate `type-govt.md`)**; the structure carries to the other types.

## Procedure to fill a form

**Precondition:** Operating model steps 1–3 are complete for this engagement (see the Write precondition above). If not — including if you arrived from a lookup — run them first. Never fill from a lookup-only or uninitialized state.

1. Locate the form's workpaper id via cch-axcess `GetBinder`.
2. Read and inventory the fillable fields (DOM-confirmed; cascade to a fixed point). Derive each field's section/topic from its **collection-path key**, not bold text (`a=false` ⇒ display-only, don't fill).
3. **Run the per-step cross-reference rule first** (`form-content-reference.md` §0): derive the topic from the collection-path key + question text; if it is **owned by another form** (§2 recognition index) and documented there this engagement, answer with a cross-reference to that form's real binder index (resolve the per-title ID via §2b, then the index via `GetBinder`) rather than re-answering; if you are on the owning form, answer substantively. In any AUD-8xx program emit the backbone auto-refs (§3) without re-deriving. Heed the §2a false-positive guard — a topic keyword alone is not a cross-reference unless the section-key agrees and this form isn't the owner.
4. Otherwise map the field via the disposition cascade ([X]/[K]/[C]/[D]/blank — Operating model step 4); gather or confirm inputs only for [C]/[A] items **the step-3 batch did not already cover** — this per-form check is a top-up, never a substitute for the up-front batch.
5. Build the payloads (one title per add when adding forms; sequential writes).
6. Write through cch-axcess; re-read to verify.
7. Sign off: per-step sign-offs on AUD-8xx program steps are API-writable (`cch-axcess` `populate-program.md`); the overall/form-level sign-off stays manual, through the UI.
