# Risk Framework — CCH

The canonical reference for CCH Knowledge Coach's risk model on KBA-502 and downstream audit programs.

## CCH 4-level risk model

Both **Inherent Risk (IR)** and **Control Risk (CR)** are set at one of four levels per assertion per audit area:

| Level | Code | Meaning |
|---|---|---|
| Maximum | **MAX** | Highest. Default for CR until controls are tested and a lower assessment is supported. |
| Slightly Below Maximum | **SBM** | High but not the ceiling. Reserved for IR when factors are clearly elevated (fraud risk, estimation uncertainty, complexity) but not at MAX. |
| Moderate | **MOD** | Normal judgment / volume for the area. |
| Low | **LOW** | Routine, low-volume, no estimation, no fraud incentive. |

**API values:** `valueKey` enum is uppercase (`MAX`, `SBM`, `MOD`, `LOW`); display `value` is title-case (`Max`, `SBM`, `Mod`, `Low`).

## Risk of Material Misstatement (RMM) matrix

RMM is derived (not directly set) from IR × CR. CCH computes:

| IR \ CR | MAX | SBM | MOD | LOW |
|---|---|---|---|---|
| **MAX** | Max | Max | Max | Mod |
| **SBM** | SBM | SBM | SBM | Mod |
| **MOD** | Mod | Mod | Mod | Low |
| **LOW** | Low | Low | Low | Low |

Reading the matrix:
- IR=LOW always → RMM=Low (substantive risk floors at low).
- IR=MOD requires CR=LOW to drop RMM to Low.
- IR=SBM never drops below SBM unless CR=LOW (then Mod).
- IR=MAX requires CR=LOW to come down to Mod.

## CCH 6 assertions

| Code | Name | Notes |
|---|---|---|
| **EO** | Existence or Occurrence | Recorded assets/transactions actually exist / occurred. |
| **RO** | Rights or Obligations | Entity holds rights to assets / obligations are entity's. |
| **CO** | Completeness | All transactions/balances that should be recorded are recorded. |
| **AV** | Accuracy, Valuation, or Allocation | Amounts are correct; valuation method is appropriate. Combines PPC "Valuation" + "Accuracy" portion of A/CL/P. |
| **CU** | Cutoff | Transactions recorded in correct period. (PPC called this "CO".) |
| **UC** | Understandability, Classification, Presentation, and Disclosure | Information understandable, properly classified and disclosed. Combines PPC "Classification/Presentation" + "P/D". |

## PPC → CCH translation

Used when porting the PPC PCAS Inherent Risk workbook defaults to CCH defaults files.

**Risk-level mapping:**
- PPC **L** → CCH **LOW**
- PPC **M** → CCH **MOD**
- PPC **H** → CCH **SBM** (**never MAX** — the defaults top out at SBM; a fraud-risk or estimate driver is handled by the significant-risk flag + response, not an IR of MAX)

**Assertion mapping:**
- PPC **E/O** → CCH **EO**
- PPC **R/O** → CCH **RO**
- PPC **C** → CCH **CO**
- PPC **V** → CCH **AV** (take max with A/CL/P if both scored)
- PPC **A/CL/P** → CCH **AV** + **UC** (Accuracy portion → AV; Classification/Presentation portion → UC)
- PPC **CO** → CCH **CU**
- PPC **P/D** → CCH **UC**

## Significant Risk

In CCH, a "Significant Risk" is **not** a risk level in this 4-level matrix. It is a separate designation set on identified risks (the Identified Risks & Significant Accounting Estimates table on each AUD-8xx program form, and on KBA-502 risk rows). Significant Risk triggers SAS 145 / AU-C 315.32 treatment:

1. Risk of fraud per AU-C 240 (revenue presumed; management override always).
2. Recent significant economic / accounting development.
3. High transaction complexity.
4. Significant related-party transactions outside normal course.
5. High subjectivity in measurement (wide estimate range).
6. Significant non-routine transactions outside normal course.

When one of these is identified, mark the risk Significant on the Identified Risks table (surfaced on KBA-502 and the area's AUD-8xx program) and address it with a substantive response (targeted response steps). **Do NOT push the grid IR up to "match" the flag** — IR stays at the `defaults/{CODE}.md` value (never MAX); the Significant flag and its response carry the elevated treatment, and any true IR deviation is a firm-principal call.

## Linked-risk references on AUD-8xx forms

Each audit step on an AUD-8xx program form can be linked to one or more identified risks via the "LINK TO RISK" column. Standard rows seen so far:
- `Management Override` — the always-present fraud risk per AU-C 240.
- `RMM-EO`, `RMM-RO`, `RMM-CO`, `RMM-AV`, `RMM-CU`, `RMM-UC` — the per-assertion RMM rows from this program's risk grid.
- Custom-named identified risks added on this engagement (e.g., "Revenue Recognition Cutoff").

A step is "linked" when its inherent-risk-relevant assertion's RMM row is referenced from the LINK TO RISK cell. This is how CCH tracks coverage — every Significant or non-Low RMM assertion must have at least one linked step.

## Audit-approach checkboxes (KBA-502, per-assertion row)

Three checkboxes on each KBA-502 assertion row determine the planned audit approach:

- **Combined** — controls + substantive (only available if CR is set below MAX).
- **Substantive: Analytical** — substantive analytical procedures.
- **Substantive: In-depth** — substantive tests of details.

At least one must be checked per assertion. The selection drives which steps cch-axcess pulls into AUD-8xx by default.

## Data ownership (architectural note)

**KBA-502 owns the editable per-assertion IR/CR/RMM/PlannedAuditApproach grid — write there**, with
collectionKey `.{AREA}.RelevantAssertion` posted against **KBA-502's wpId**. The AUD-8xx program's grid is
the **derived / read-through** view: a write aimed at the program's wpId lands in a working copy the
KBA-502-owned recompute discards on refresh. KBA-502's bulk form GET does not embed the RelevantAssertion
child rows (`OverallAuditAreas[].childObjectList` returns `[]`) and `inventory_form` over-filters the form,
so a GET-only read shows just `Comment`. The grid is real (defined in KBA-502's `elements`) and the UI
writes it against KBA-502's wpId. KBA-502 also owns `.KBA502.FinancialLevelRisks` (FS-level risk
rows; only the row-level `Comment` is directly writable there — 14 of 15 properties are pt5-linked).

The relevant-assertion **selection** happens upstream on **KBA-400** (`.KBA400.AuditareaRelevantAssertions`: AuditAreaName + Assertion + comment), which drives which assertion rows render (and are writable) per area on KBA-502. So the chain is: KBA-400 selects assertions → CCH recommends programs → IR/CR/RMM/approach written on **KBA-502** → the program grids read through; program step→assertion linkage + sign-off feeds back and clears KBA-502's "Relevant Assertion Unaddressed".

## Where the risk assessment is documented (supporting forms)

- **KBA-301 / KBA-301E (EBP)** — overall materiality, performance materiality, tolerable, clearly-trivial threshold. The threshold significance is tested against (`scoping/significance.md`). Read it here or get it from the user before scoping.
- **KBA-503 — Basis for Inherent Risk Assessment.** The documented rationale behind each IR set on KBA-502. Every non-default IR needs a basis that holds this year; write it here as you set the level on KBA-502, don't backfill.
- **KBA-302** — understanding the entity and environment; feeds the qualitative significance and risk drivers.
