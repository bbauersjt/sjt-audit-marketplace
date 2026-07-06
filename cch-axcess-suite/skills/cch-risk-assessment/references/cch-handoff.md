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

**Name the AUD-8xx program as the Form for IR/CR/RMM/approach writes — NOT KBA-502.** The editable
per-assertion IR / CR / RMM / planned-approach grid lives on each **AUD-8xx program workpaper** (the area's
`RelevantAssertion` collection). **KBA-502 is a read-through summary** with no per-assertion grid of its
own — it rolls those values up and owns only the FS-level risks. So a HANDOFF that sets IR/CR for an area
names that area's program (Cash = AUD-801, etc.). `cch-axcess` resolves the exact writable workpaperId and
the field mechanics; this skill just names the program + the values. (Verified 2026-05-30 — see
`cascade/kba-502.md`. Do not tag these as "confirm writable surface" — it's resolved.)

**Cascade order:** hand off the forms in funnel order — AUD-100 → KBA-400 → KBA-502/programs. Each stage's
output (areas, assertions, risk levels) is the next stage's input. Don't write IR before KBA-400 has set
the assertions `selected`.

## Examples

### Apply NPO Cash IR defaults (writes to the AUD-801 program)

```
HANDOFF → cch-axcess
Module: fill-kc-form.md
Form: AUD-801 (Cash) — the area's AUD-8xx PROGRAM workpaper (NOT KBA-502)
Engagement: 6b99b20e-cf08-4537-850f-a7f159eec1bc
Writes (per assertion, write order: selected → ir → rmm; CR left MAX; AV is N/A for Cash):
  - CASH RelevantAssertion / EO / selected = "Yes" (YES)
  - CASH RelevantAssertion / EO / ir = "Mod" (MOD)
  - CASH RelevantAssertion / RO / selected = "Yes" (YES)
  - CASH RelevantAssertion / RO / ir = "Low" (LOW)
  - CASH RelevantAssertion / CO / selected = "Yes" (YES)
  - CASH RelevantAssertion / CO / ir = "Low" (LOW)
  - CASH RelevantAssertion / CU / selected = "Yes" (YES)
  - CASH RelevantAssertion / CU / ir = "Mod" (MOD)
  - CASH RelevantAssertion / UC / selected = "Yes" (YES)
  - CASH RelevantAssertion / UC / ir = "Low" (LOW)
  - (then read each row's CCH-recommended rmm and write it back)
Reason: PPC-derived NPO Cash defaults (defaults/NPO.md). CR=MAX, controls not tested. Basis → KBA-503.
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

### Single override after engagement-specific judgment

```
HANDOFF → cch-axcess
Module: fill-kc-form.md
Form: AUD-801 (Cash) — program workpaper
Engagement: 6b99b20e-cf08-4537-850f-a7f159eec1bc
Writes:
  - CASH RelevantAssertion / EO / ir = "SBM" (SBM)
Reason: Default MOD raised to SBM — wire-transfer dual-control suspended Aug–Oct 2025 (CFO transition). Elevated fraud risk.
```

### Flag a Significant Risk

```
HANDOFF → cch-axcess
Module: fill-kc-form.md
Form: AUD-801 (Cash) — Identified Risks table
Engagement: 6b99b20e-cf08-4537-850f-a7f159eec1bc
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
Module: fill-kc-form.md   (or add-audit-programs.md / toggle-program-step.md per the ask)
Form: AUD-801 (Cash) — program workpaper
Engagement: 6b99b20e-cf08-4537-850f-a7f159eec1bc
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
