---
name: ebp-rollovers
category: ebp
mandatory: false
description: Participant rollovers in — testing for proper documentation of qualified source, accurate crediting to participant accounts, and compliance with plan document provisions on accepted rollover types. Pull when rollover activity is material to the FS.
acceptable_methods: [substantive]
mandatory_method: null
required_documents:
  - Rollover detail / register for the plan year (by participant, with date, amount, source plan)
  - Rollover acceptance forms / source plan documentation
  - Plan document provisions on accepted rollover sources
  - GL detail for rollover contribution account
---

# EBP — Rollovers

Sampling unit: rollover-in event (one rollover from a source plan/IRA into the plan for one participant).

## Notes
- Pull when the plan permits rollovers in and rollover activity is material to the FS
- Confirm plan document permits the rollover sources accepted (some plans restrict to direct rollovers from qualified plans only)
- Key attributes: source plan qualification documentation, direct vs. indirect rollover, proper crediting to participant account, recordkeeping
- Distinguish from contributions — rollovers are not subject to 415/402(g) limits but source documentation requirements are stricter
- For rollover *outs*, test under `ebp-distributions` (those are distributions that happen to be rolled over)
