---
name: wt-journal-entries
category: wt
mandatory: true
description: Adjusting journal entry (AJE) testing — required by AU-C 240 to address management override of controls. Static n=5 with specific selection rules.
acceptable_methods: [static-sample]
mandatory_method: static-sample
n: 5
required_documents:
  - Full general journal for the period (all manual / non-system JEs / AJEs)
  - JE detail with date, account, amount, description, type, posted-by, approval status, line count
---

# AJEs (Adjusting Journal Entries)

Static sample, **n = 5**. Mandatory under AU-C 240.

## Selection rules — AJE-specific

- **Focus toward year-end.** Most selections (3–4 of 5) should be from the last month / two months of the period
- **Spread the rest** — pull 1 or 2 from elsewhere in the year
- **Don't pick the same type of entry twice** unless that's the only way to hit n=5
- **Avoid bloat.** Skip entries with tons of lines that are routine and audited elsewhere — payroll allocations, standard depreciation, recurring accruals — **unless they're required to hit n=5**
- **Include any unusually large or one-time entries.** Year-end true-ups, one-shot reclasses, unusual accounts touched
- **Provide the entire entry** in the pull file — all lines, full debit/credit detail, the description, the posted-by — not just a summary line

## Population scoping

- Population: manual / non-system AJEs only (system-generated entries excluded with documentation)
- Voided / reversed entries removed before selecting
- If the population is large and dominated by routine entries, **note that to the user** and confirm risk criteria — don't blow up the sample to compensate

## Notes
- One of very few mandatory FS samples — never skip on a full-scope FS audit
- Risk criteria (period-end, round-dollar, unusual accounts, posted by senior personnel, weekend / off-hours) should be discussed with the engagement team before pulling
- If risk criteria are well-defined, weight selections toward entries meeting them; otherwise apply the AJE-specific rules above
