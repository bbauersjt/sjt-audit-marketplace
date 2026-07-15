# Handoff Protocol → `cch-axcess`

This skill carries domain knowledge. `cch-axcess` carries platform mechanics. When a task needs both, this skill builds a structured handoff block; `cch-axcess` reads it and executes the writes.

## Block format

```
HANDOFF → cch-axcess
Module: <module file in cch-axcess/references/modules/>
Form: <KC form ID, e.g. AUD-801 (Cash)>
Engagement: <engagement-guid>
Writes:
  - <collection> / <objectKey> / <propertyKey> = "<value>" (<valueKey>)
  - ...
Reason: <one-line rationale — becomes the workpaper breadcrumb>
```

**Name KBA-502 as the Form for IR/CR/RMM/approach writes — NOT the AUD-8xx program.** KBA-502 owns the
per-assertion IR / CR / RMM / planned-approach grid (collectionKey `.{AREA}.RelevantAssertion`, posted
against **KBA-502's wpId**); the program's grid is the **derived / read-through** view — a write aimed at
the program's wpId lands in a working copy the KBA-502-owned recompute discards on refresh. So a HANDOFF
that sets IR/CR for ANY area names **KBA-502** as the form, with the area carried in the collectionKey.
`cch-axcess` resolves the exact writable workpaperId and the field mechanics; this skill just names the
form + the values. (See `cascade/kba-502.md`.)

**Cascade order:** hand off the forms in funnel order — AUD-100 → KBA-400 → KBA-502/programs. Each stage's
output (areas, assertions, risk levels) is the next stage's input. Don't write IR before KBA-400 has set
the assertions `selected`.

## Examples

### Set materiality — first-year / re-set ONLY (KBA-301 write)

Only when materiality is being **set** this year (new engagement or re-benchmarked). If KBA-301 already
carries this year's numbers, it's a read (SKILL.md Step 0.3), not a HANDOFF. Method: `references/intake.md`
(the KBA-301 benchmark → PM → TM → PAJE derivation).

```
HANDOFF → cch-axcess
Module: fill-kc-form.md
Form: KBA-301 (Materiality) — KBA-301E for EBP
Engagement: <guid>
Writes:
  - Benchmark = <e.g. Total revenues/contributions> — pick the benchmark yielding the LARGER materiality
  - Benchmark % = <within the form's printed range; top of range is acceptable, above it is not>
  - Planning materiality = <benchmark × %>
  - "Financial statements taken as a whole" line (step-8 add-item): TM = 75% of planning materiality, rounded DOWN to nearest $100
  - PAJE / passed-adjustment threshold = max(10% of TM, $5,000)   (EBP: max(20% of TM, $5,000); $5,000 floor mandatory)
Reason: First-year benchmark set per intake.md KBA-301 method. TM ("performance materiality") is the number
        the audit is scoped/concluded against. (Govt: a PM/TM set per opinion unit.)
```

### Apply NPO Cash IR defaults (writes to KBA-502 — the programs are derived)

```
HANDOFF → cch-axcess
Module: fill-kc-form.md
Form: KBA-502 (Summary of Risk Assessments) — the IR/CR/RMM/approach WRITE TARGET (NOT the AUD-801 program)
Engagement: <guid>
Writes (per relevant assertion, on KBA-502's wpId; write order ir → cr → rmm → approach; AV is N/A for Cash;
        `selected` not required — grid presence already reflects KBA-400):
  - .CASH.RelevantAssertion / EO / ir = "Mod" (MOD), cr = "Max" (MAX), rmm = "Mod" (MOD), PlannedAuditApproach = "Substantive: In-depth" (INDEPTH)
  - .CASH.RelevantAssertion / RO / ir = "Low" (LOW), cr = "Max" (MAX), rmm = "Low" (LOW), PlannedAuditApproach = "Substantive: In-depth" (INDEPTH)
  - .CASH.RelevantAssertion / CO / ir = "Low" (LOW), cr = "Max" (MAX), rmm = "Low" (LOW), PlannedAuditApproach = "Substantive: In-depth" (INDEPTH)
  - .CASH.RelevantAssertion / CU / ir = "Mod" (MOD), cr = "Max" (MAX), rmm = "Mod" (MOD), PlannedAuditApproach = "Substantive: In-depth" (INDEPTH)
  - .CASH.RelevantAssertion / UC / ir = "Low" (LOW), cr = "Max" (MAX), rmm = "Low" (LOW), PlannedAuditApproach = "Substantive: In-depth" (INDEPTH)
  - (per-area submit → refresh on KBA-502's wpId before the next area; RMM=IR because CR=MAX)
Reason: PPC-derived NPO Cash defaults (defaults/NPO.md) applied AS-IS. CR=MAX, controls not tested. Basis → KBA-503.
```

### Answer AUD-100 (engagement tailoring → areas + controls)

```
HANDOFF → cch-axcess
Module: fill-kc-form.md
Form: AUD-100 (Engagement-Level Tailoring Questions)
Engagement: <guid>
Writes:
  - <Y/N tailoring answers per entity facts>
  - Audit areas multiselect = [CASH; AR; REVANDRECEIVABLESX; PPE; AP; OL; EQUITY; ...]
  - Operating effectiveness = "No"   (substantive approach; CR stays MAX)
Reason: Areas from intake scope sheet; controls not relied upon. Fixed-point fill (gated follow-ups).
```

### Select relevant assertions on KBA-400 (per significant area)

```
HANDOFF → cch-axcess
Module: fill-kc-form.md
Form: KBA-400 (Scoping & Mapping)
Engagement: <guid>
Writes:
  - Scoping determinations: <answer each live option>
  - Relevant assertions: CASH → EO;RO;CO;CU;UC | AR → EO;RO;CO;AV;CU;UC | ...
Reason: Assertion sets per significance scope sheet (all applicable for significant areas).
```

### Engagement-specific concern — response steps, NOT an IR bump

IR comes from `defaults/{CODE}.md` as-is — **never MAX, never elevated**.
An engagement fact that raises concern (fraud flag, suspended control, estimate) is addressed by the
significant-risk flag + **targeted response steps** on the program; any actual IR deviation is queued to
the firm principal, not written.

```
HANDOFF → cch-axcess
Module: populate-program.md
Form: AUD-801 (Cash) — program workpaper
Engagement: <guid>
Writes:
  - Activate + link targeted response steps for EO (wire-transfer testing expanded to cover the exposure window)
Reason: Wire-transfer dual-control suspended for a period during the year — addressed via targeted
        response, IR stays at the NPO default (MOD). Any IR override → queue to the firm principal.
```

### Flag a Significant Risk

```
HANDOFF → cch-axcess
Module: fill-kc-form.md
Form: AUD-801 (Cash) — Identified Risks table
Engagement: <guid>
Writes:
  - Add row to the area's AssertionLevelRisk table:
    - RiskName = "Cash skimming at field offices"
    - TypeOfRisk = "Significant, Fraud"
    - IR = "SBM" (SBM)
    - CR = "Max" (MAX)
    - LinkedSteps = [801.AS.1, 801.BR.1-8, 801.FA.1]
Reason: AU-C 240 fraud risk on cash collection — multiple field offices with limited segregation of duties.
```

### Add audit steps to a program

```
HANDOFF → cch-axcess
Module: populate-program.md   (full pipeline: step selection + risk-linking + responses + sign-off.
                                Use toggle-program-step.md if this is steps-in/out ONLY, with none of
                                the rest. Use add-audit-programs.md only if the AUD-8xx form itself
                                isn't yet in the binder.)
Form: AUD-801 (Cash) — program workpaper
Engagement: <guid>
Writes:
  - Add step "Confirm cash balances directly with financial institutions"
  - Linked Assertions = [EO, RO, CO, AV, CU, UC]
  - Linked Risks = [Management Override, RMM-EO, RMM-RO, RMM-CO, RMM-CU, RMM-UC]
  - Workpaper Reference = "1030"
Reason: Standard confirmation step per programs/cash.md defaults for NPO.
```

## Split rule — what lives where

| Learning type | Goes in |
|---|---|
| "For NPO Cash, IR for EO defaults MOD" | This skill — `defaults/NPO.md` |
| "AUD-801's IR field locator / valueKey / write payload" | `cch-axcess` (mechanics) |
| "When IR is Significant, the SR flag goes on the area's risk table" | This skill — `references/risk-framework.md` (workflow logic) |
| "The submit POST / endpoint / verify cycle" | `cch-axcess` |
| "The firm's standard cash program for NPO always includes positive confirmation" | This skill — `programs/cash.md` |

If unsure: would a different firm with a different program library still need to know this? Yes → mechanics, goes in `cch-axcess`. No → domain, stays here. **This skill names the program + the answer in plain terms; it does not write endpoints, valueKey codes, or HTTP bodies.**

## Listen-mode coordination

When a user demonstrates a task that crosses both skills (e.g., "we're going to fill out the cascade for the first time"), this skill captures the domain learnings; `cch-axcess` captures the mechanical learnings. Both codify in parallel at session end. Avoid duplicating learnings.
