# Significance methodology

How to decide whether an account, class of transactions, or disclosure is **significant** — i.e., gets scoped on KBA-400, gets a relevant-assertion set, gets IR/CR/RMM on KBA-502, and gets an audit program (AUD-8xx). This is the gate the whole cascade hangs on.

A significant account/class is one with a **reasonable possibility of containing a material misstatement** (AU-C 315). That resolves to two independent tests — pass **either** and it's significant:

## Test 1 — Quantitative (vs tolerable)

The area's **measure** exceeds **tolerable misstatement** (≈ performance materiality).

- **Measure** = the **larger of** (a) the period-end balance or (b) the gross activity / class of transactions flowing through it during the year. A small net balance over a large gross flow is scoped on the flow.
- **Threshold** = tolerable misstatement, obtained per `references/intake.md` Step 3. Do not invent it.
- Areas below tolerable with no qualitative driver (Test 2) are **not** significant — document them as scoped-out (immaterial) so the file shows the call was made.

## Test 2 — Qualitative (always-significant, regardless of size)

Significant irrespective of dollar amount when any apply (AU-C 315 / 240):

- **Fraud risk** attaches to the area — revenue recognition is **presumed** a fraud risk (AU-C 240); management override of controls is an always-present FS-level fraud risk.
- **Significant accounting estimate** with high measurement uncertainty (allowances, fair value, useful lives, impairment, accruals, actuarial).
- **Related-party** transactions outside the normal course.
- **Significant unusual / non-routine** transactions outside the normal course (business combinations, new debt, one-off large transactions).
- **Required disclosure** that is material to users even when the related balance is small (going concern, commitments & contingencies, concentrations, subsequent events, debt covenants, restrictions).
- **Regulatory / compliance** sensitivity (governmental compliance requirements, ERISA party-in-interest, UBI).
- **Known issue** from prior year, current-year facts, or the project notes (restatement, deficiency, covenant pressure).

### Always-significant list (house default — confirm with firm)

These are scoped on essentially every engagement of the relevant type and should default to significant unless there's a clear reason otherwise:

| Always significant | Applies to |
|---|---|
| Cash | all |
| Revenue / Support & Contributions | all (revenue = presumed fraud risk) |
| Journal entries | all (management override) |
| Related-party transactions | all |
| Significant estimates in play | all (where the entity has them) |
| Commitments & contingencies (disclosure) | all |
| Concentrations (disclosure) | all where present |
| Investments | NPO, EBP, governmental, any entity holding them |
| Net assets / equity | all |
| Debt | where present (covenants, classification) |
| Participant data, contributions, benefit payments, investments | EBP |
| Net position by opinion unit; compliance/SEFA | governmental / Single Audit |

> This list is a defensible default grounded in AU-C 240/315 and PPC practice. The firm may scope tighter or looser — confirm the house list with the user and codify any change here.

## Firm-tunable parameters

Set these once with the user; they parametrize Tests 1 and the always-significant list. Defaults shown are common but **must be confirmed** — they directly move what gets audited.

| Parameter | Common default | Notes |
|---|---|---|
| Performance materiality as % of overall | 50–75% | Lower for higher-risk / first-year. Confirm firm policy. |
| Tolerable misstatement basis | = performance materiality | Some firms set a separate tolerable per area. |
| Clearly-trivial threshold (CTT) | 3–5% of overall materiality | Below CTT, misstatements aren't accumulated. KBA-301. |
| Transaction classes scoped separately? | Yes | Whether gross flows get their own KBA-400 row vs folded into the balance area. |

## Output

For each area produce: **significant Y/N · which test triggered it · the measure used · the basis note.** That note becomes the KBA-400 scoping rationale and supports KBA-503 (basis for IR). Save the scope sheet to the engagement folder.

## What significance does NOT decide

Significance decides *whether* an area is in scope and the *relevant assertions* (`references/cascade/kba-400.md`), not *how high* the risk is. IR/CR/RMM levels are a separate judgment on KBA-502 — a significant area can still carry LOW inherent risk on most assertions. Don't conflate "significant" with "high risk."
