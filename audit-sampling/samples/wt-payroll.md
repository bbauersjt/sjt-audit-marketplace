---
name: wt-payroll
category: wt
mandatory: false
description: Payroll walkthrough — substantive testing of payroll expense. Static n=5 — individuals if possible, else 5 paydays.
acceptable_methods: [static-sample]
mandatory_method: static-sample
n: 5
required_documents:
  - Payroll register for the period (by employee or by pay period)
  - GL payroll expense account detail
  - Employee master file (active employees during the period)
---

# Payroll Walkthrough

Static sample, **n = 5**.

## Selection logic

**Default: select 5 individuals** across the period — one paycheck (or one period's earnings) per individual. Spread across:
- Different pay classes / departments if applicable
- A mix of larger and smaller earners (skew larger but include some coverage)
- Include 1 termed employee if the population includes recent terminations

**Fallback: if individual-level selection isn't workable** (e.g., only payroll register summaries available, no per-employee detail), **select 5 paydays** instead. Note in the pull file that staff should pick one individual from each selected payday register during fieldwork.

## Selection bias rules
- Skew toward larger earners but include some mid / smaller items
- Avoid trivially small items (1-day terminations, off-cycle reversals) unless required
- Avoid negatives (corrections, prior-period reversals)

## Omission rule
**Skip this sample when significant controls testing of payroll is happening elsewhere.** Walkthrough is incompatible with controls testing in the same area — pick one or the other, not both.

## Notes
- Bonus / commission populations often pulled separately
- Executive comp may need to be a separate stratum
- For controls testing of hire / rate change / termination events, that's a separate procedure (`control-sample`) and triggers the omission rule above
