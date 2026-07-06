---
name: ebp-participant-data
category: ebp
mandatory: true
description: Combined participant data testing — covers demographic accuracy, eligibility, and individual contribution testing in a single stratified sample. n=25 always.
acceptable_methods: [static-sample]
mandatory_method: static-sample
n: 25
required_documents:
  - Census file used by the plan / recordkeeper
  - HR / payroll system data (DOB, DOH, DOT, hours, compensation) for the workforce
  - Plan document (eligibility, contribution, vesting provisions)
  - Contribution register / detail by participant per pay period
---

# EBP — Participant Data (Combined)

This is a single combined sample covering **demographic accuracy, eligibility, and individual contribution testing**. **n = 25 always.** Mandatory on EBP audits.

## Selection logic — stratified

The 25 selections are built from required mini-strata, then a contributing-participants split. Adjust counts within the stated ranges to total exactly 25.

1. **Newly eligible** — 2–3 participants hired the year before who became eligible during the audit period
2. **New hires** — 2 employees hired during the audit period
3. **Terms** — 3 employees terminated during the audit period
4. **Contributing participants** — the remainder (~17–18) split into 3 strata of contributing participants:
   - **Low contributors** — but **never less than $500** in contributions for the period
   - **Medium contributors** — middle band
   - **High contributors** — top band
   - Split the ~17–18 roughly evenly across the three strata; if the population is uneven, surface that to the user before pulling

## Selection bias rules

- Spread within each stratum — don't cluster on a single department / location
- Avoid trivially small contributors below the $500 floor (the floor is intentional — testing $20 contributions teaches us nothing)
- For terms, prefer ones with terminal contributions or distributions in the period

## What gets tested on each selection

- **Demographic accuracy**: DOB, DOH, DOT, hours, compensation
- **Eligibility**: was the participant correctly classified as eligible / ineligible at the right time
- **Individual contribution testing**: deferral elections applied correctly, employer match calculated correctly, contributions remitted timely

A single selection serves all three objectives — that's the whole point of the combined sample.

## Population assumptions
- Cleaned employee population reconciled to the census file
- Active and terminated participants in the audit period both eligible for selection
- Rehires get treated as either a new hire or a continuing participant depending on plan rehire provisions

## Notes
- This MD replaces the prior `ebp-demographic` and absorbs `ebp-eligibility` and `ebp-contributions` as testing objectives within the same selection
- Auto-enrollment / EACA / QACA features layer additional attributes onto the eligibility piece — capture default deferral rate and notice timing for relevant selections
