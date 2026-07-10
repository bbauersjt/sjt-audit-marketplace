---
summary: Build out a WHOLE AUD-8xx audit program — tailoring answers + bring in steps + link risks + fill responses + sign off (the full pipeline; for steps-in/out ONLY with none of the rest, use toggle-program-step)
leg: kc
triggers:
  - "build out the [area] audit program"
  - "populate the audit program"
  - "answer the tailoring questions and pull in the steps"
  - "link the program steps to risk"
  - "fill responses and sign off the program steps"
  - "tailor and complete AUD-8xx"
inputs:
  - "AUD-8xx workpaperId + engagementGuid"
  - "area key (CASH/AR/PPE/AP/EQUITY/...)"
  - "tailoring answers, response text, preparer initials"
calls:
  - scripts/populate_program.js (paste into KC tab — defines window.kcPop)
  - scripts.kc.toggle_program_step
status: validated
validated_on:
  - "AUD-801 Cash, AUD-803 AR, AUD-809 PP&E, AUD-810 AP, AUD-814 Net Assets — Claude Playground NFP 2026-05-31"
---
# Module — Populate an AUD-8xx Audit Program

**Triggers:** "build out the [area] program", "populate the audit program", "tailor and complete AUD-8xx", "link steps to risk", "fill responses and sign off the steps".

Drives the whole program-build for ONE AUD-8xx workpaper: tailoring questions → bring in the non-N/A steps → link each parent step's risk → fill step responses → preparer sign-off. The engine is `scripts/populate_program.js` (`window.kcPop`).

## Why a bounded pipeline, not one call (READ THIS)

A single "do it all" JS call **will trip the in-page eval timeout** (45s on the linked-tab CDP transport; the bridge's `chrome_eval` defaults to 30s) on a real program (AR is 56 parents / 147 step rows ≈ 300 writes) and throw a red "Runtime.evaluate timed out" error mid-run. To a user that looks broken. So the procedure is deliberately split into **bounded, self-verifying steps** that each finish well under the timeout, and drops self-heal on re-verify. Never wrap it in one mega call.

Two hard platform facts force the shape:
1. **Writes must be paced — and pacing alone is NOT sufficient.** Back-to-back `UpdateProperty` to one form silently drop (HTTP 200, no persist). The old ~300ms floor is WRONG: ~60% still dropped at ~350ms, and ~30–50% drop even with 1–2s gaps (batch-2 + SFRC 401k 0100, 2026-07-08). Pace ~1.2s AND run the mandatory write → per-workpaper submit → verify-by-read → retry ≤3× loop (field-conventions.md §5 3a) — which this module's verify+repair pipeline already embodies. → fire ≤ ~35 writes per call.
2. **`UpdateProgramStep` (API) does NOT re-render the Angular UI.** The Risks-checkbox and Comment-box DOM that risk-linking + heading detection read only appear after a page **reload**. → reload between step 2 and step 3.

## Procedure

Prereq: an authenticated `knowledgecoach.cchaxcess.com` tab on the program's `/workpaper/{wpId}` URL (not bare `/binder/{eng}` — that redirects and 401s). KC tokens are the localStorage fast path.

1. **Inject the engine.** Paste `scripts/populate_program.js` into the tab (defines `window.kcPop`).
2. **TQs + visibility:** `await kcPop.tqAndVisible({binder, wp, area, tqYesCount, initials, gibberish})`. Answers the first N visible tailoring questions = Yes (the TQ→`IsApplicable` cascade then marks unneeded steps N/A) and sets the visible step-set to every applicable parent + applicable child.
3. **RELOAD the tab, then RE-PASTE the engine.** (Required — see fact #2.)
4. **Build payloads:** `await kcPop.build({binder, wp, area, ...})`. Reads the form + rendered DOM → ordered payload list: one Risks link per parent (RMM codes matching the parent's checked assertions **that are present in this engagement** + the Management Override financial-level risk), plus a response (`Comment`) and `SignOff` on every non-heading step. Steps with no rendered response box are headings → skipped. Returns `{parents, steps, headings, presentRMM, mgmt, payloadCount}`.
5. **Fire to completion (resumable, idempotent):** loop
   ```js
   v = await kcPop.verify();                 // returns badIdx = not-yet-stuck payloads
   await kcPop.repair(v.badIdx.slice(0,35)); // fire ~35, paced
   ```
   until `verify().bad === 0`. Re-runs are safe (writing the same value again is a no-op), so dropped writes self-heal — this is what keeps it from ever looking broken.

## Risk-link rule (as configured)

Per parent step: link the `RMM-{assertion}` for each assertion already checked on the step **only if that code is present** in the engagement's risk set (read live from the DOM — unknown codes 500), plus the Management Override (`FINANCIALLEVELRISKS-N`) on every step. Areas with no assertion-level RMMs identified get Management Override alone. Sub-procedures carry no assertions and are not risk-linked (linkage lives at the parent/step level).

## Gotchas (all confirmed live 2026-05-31; AX-33 additions noted)

- **SignOff needs BOTH `value` and `valueKey` = initials.** valueKey-only is silently ignored.
- **Sign-off property NAME varies per collection** (`performedby` vs `SignOff`) — AX-33: read the
  actual `propertyType:3` key off the step before signing; never assume one name across forms.
- **Assertions are CLIENT-RENDER-ONLY** — KBA-502 stores nothing; the `/api/Workpaper` GET reads
  them empty. Read a parent step's checked assertions from the **DOM**
  (`input[name="ProgramSteps|{key}|Assertion||{code}"].checked`) and write `Risks = RMM-{ASSERTION}`
  codes. (Corroborated by `cch-risk-assessment` `cascade_edge.csv`: "502 UI shows only KBA-400-picked
  assertions; nothing stored on 502.") DOM-first is mandatory for assertion linkage.
- **Risks property** = full-state replacement, `value`/`valueKey` semicolon-joined WITH trailing semi; only DOM-present codes (else 500 "Index was outside the bounds").
- **Overall / form sign-off is OFF LIMITS** — structurally skip `kcc-workpaper-signoff(-group)`; only
  per-step sign-offs are in scope. `UpdateProgramStep` = **full-state replacement**; answering "No"
  does NOT auto-remove a visible step (it flags Not Applicable) — remove via the visible-key toggle.
- **The "stick" fix covers step-edit flakiness too (AX-33).** The same intermittent
  `non-empty request body` 400-in-a-200 that hit KBA writes almost certainly drove the step-edit
  drops; `kcPop`/`update_properties_sequential` retry until the write echoes clean. Still verify+repair.
- **Token rotation:** KC access token expires after a few minutes idle → 401. A tab reload refreshes it (and is needed anyway in step 3). See architecture.md "Tab visibility, throttling & token refresh" — keep the KC tab the selected tab in its own window for autonomous runs.
- Heading detection + present-RMM codes are DOM-derived, not in the `/api/Workpaper` GET.

## Validated on

AUD-801 / 803 / 809 / 810 / 814 (Claude Playground, 2026 NFP) — TQ cascade → N/A filtering → step visibility → risk links → responses → sign-offs, every payload verified, 0 residual drops.


<!-- END -->
