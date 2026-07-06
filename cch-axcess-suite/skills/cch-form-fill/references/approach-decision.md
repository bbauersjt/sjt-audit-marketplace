# Audit-approach decision model — coverage of RMM

How the firm decides and justifies the approach per financial-statement (FS) area, and produces the terse, defensible one-liner the checklists require. The objective on these large checklists is to defensibly express that the required work was performed.

## The one question (everything else is downstream)
> Did the **pool of procedures** address every reasonably-possible way this area could be **materially misstated** — giving reasonable assurance no material misstatement remains — either by substantively absorbing the full inherent risk (controls assumed absent) **or** by adequately testing controls?

The question is **not** "are analytics effective / are substantive procedures effective." Tool choice (substantive detail, analytics, controls reliance) is just *how* coverage is achieved. The justification expresses the **coverage**, not the tool. Cash is justified not because analytics add little, but because the substantive work already covers every way cash could go materially wrong — nothing material is left for another procedure to catch.

## "What could go wrong" — the assertion model in plain terms
Inherent risk = the risk of material misstatement **in the complete absence of controls.** If controls are not tested, controls are assumed absent, so substantive procedures must cover the **whole** risk. The "assertions" are simply the ways a balance/class goes wrong, stated plainly rather than as IR×CR machinery:

- **Recorded but wrong / should not be there** — existence/occurrence, accuracy, cutoff, classification.
- **Should be recorded but is not** — **completeness.** The one easiest to miss: testing recorded expenses proves the recorded ones are correct; it does **not** prove that all expenses were recorded.
- **Estimated amount is off** — valuation/estimates (allowance, impairment, fair value, accruals).
- Rights/obligations; presentation & disclosure.

Per area: which of these are the *real* material risks? Did a procedure address **each**? Is anything left over **immaterial**?

## How the approach falls out (it is a result, not the decision)
- Substantive detail covers existence/accuracy/valuation of **recorded** items.
- **Completeness** needs its own move — search for unrecorded items, reconciliation to an independent total, or an analytic that would actually reveal something missing.
- **Estimates** need targeted work, **or** a substantive procedure that overrides the need (trace AR to subsequent collections → proves no material unrecorded allowance, so testing the allowance itself is not considered necessary, NCN).
- **Controls reliance** is the fallback when a defensibly-sized substantive sample is not feasible (fragmented population) — then the conclusion rests on controls having caught errors (`audit-sampling/methods/controls-substantive-fallback.md` — requires the audit-sampling skill).
- Analytics earn their place only where they genuinely contribute to covering a risk (e.g., anchored to a substantively/control-tested driver). They are a tool, not the point.

## The answer (format)
Terse. State that the material RMM was covered and that the residual is immaterial / NCN. A few words distilling the judgment.
- **Cash:** "All material balances agreed to reconciliations and supporting bank statements; reconciling items tested. No reasonable likelihood of a remaining material misstatement."
- **AR:** "AR confirmed and traced to subsequent collections; untraced balances immaterial. NCN to separately test the allowance — subsequent collections substantiate net realizable value."
- **Expenses:** "Recorded expenses tested for occurrence and accuracy; completeness addressed via [search for unrecorded / period analytic]."
- Distilled register example: *"NCN to test allowance; AR not traced to subsequent collection is immaterial."*

## Materiality — the wave-off engine
Materiality is the argument that turns "here is a way it could go wrong" into **"but it cannot be material → N/A."** If the residual exposure to a risk is immaterial, the procedure addressing it **cannot detect a material misstatement** — performing it serves no purpose, so it is N/A.

- **Allowance example:** subsequent receipts traced on all but an immaterial amount of AR → the untraced slice cannot be material even if 100% uncollectible → testing the allowance cannot detect a material collectibility misstatement → **N/A.** This removes the entire allowance/collectibility step block.
- **General form:** "Residual exposure to [risk] is immaterial ([why]); the procedure cannot detect a material misstatement → N/A."
- Pairs with the **N/A-top-line rule**: the materiality reason is stated **once** at the head of the N/A block; sub-steps get a plain "N/A."

This is how a few words of materiality judgment apply N/A to hundreds of steps.

## Three procedure buckets per section (do not confuse them)
1. **Presumed-performed / mandatory** — always done to cover the RMM (AP: search for unrecorded liabilities, cutoff). This is the coverage the answer expresses.
2. **Presumed-NOT-performed (silent baseline omissions)** — conventionally not done; need **no** justification. You only ever explain why you *would* do one, never why you did not. *(AP confirmation is conventionally not performed; you would document a reason to confirm, never a reason not to.)*
3. **Materiality wave-offs (stated)** — a procedure you would otherwise do, dropped **because the residual is immaterial** → state it via materiality. *(Allowance testing when subsequent receipts are traced on all but an immaterial slice.)*

The distilled answer = the coverage (bucket 1) + any materiality wave-off (bucket 3). It does **not** explain bucket 2.

---

## Per section — captured in section-library.md
**Method:** per section, identify the procedures, the presumed-mandatory work, the materiality wave-offs, and the presumed-not-performed items → distill the terse answer. This is firm judgment, captured section by section, in `section-library.md`.
For each area: the real **what-could-go-wrong**, the **procedure(s) that cover each**, and the **terse justification**. The approach label (substantive/analytic/controls) is whatever that coverage adds up to. The driver is RMM coverage, not a pre-assigned approach.

| FS area | Real risks (what could go wrong) | Covered by | Terse justification |
|---|---|---|---|
| Cash | existence/accuracy of balances | agree to recs → bank statements; test reconciling items | *(captured above)* |
| AR / Receivables | existence; **valuation/allowance**; completeness | confirm; **trace to subsequent collections**; cutoff | *(captured above)* |
| Expenses | occurrence/accuracy; **completeness** | test recorded; **search for unrecorded / period analytic** | *(captured above)* |

The complete per-area set — every FS area (standard + EBP) with mandatory procedures, wave-offs, and the distilled one-liner — is captured in `section-library.md`. The rows above show the pattern only.
