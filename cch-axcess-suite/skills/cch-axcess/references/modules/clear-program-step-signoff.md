---
summary: Clear an in-form program-STEP sign-off or N/A marker (SignOff = "[]") on an AUD-8xx program. The KC-leg un-sign-off; distinct from the document-level WPM sign-off.
leg: kc
triggers:
  - "un-sign-off a step"
  - "clear the sign-off on this step"
  - "remove the step sign-off"
  - "un-mark the step N/A"
  - "clear the N/A on the program step"
  - "take my initials off that audit-program step"
inputs:
  - "KC tab on the AUD-8xx workpaper with kc tokens in localStorage (ls:kc)"
  - "engagementGuid + workpaperId"
  - "the step's objectKey + its area key (from the .{AREA}.ProgramSteps collectionKey)"
calls:
  - scripts.kc.clear_program_step_signoff
  - scripts.kc.program_step_signoff_payload
  - scripts.kc.submit
status: validated
---
# Module — Clear Program-Step Sign-Off / N/A (in-form, KC)

## What this does
Removes ONE in-form program-STEP sign-off **or** N/A marker on an AUD-8xx program by setting the
step's `SignOff` property to `"[]"` via `UpdateProperty`. This is the KC-leg counterpart to the
document-level `remove-signoff.md` (WPM). **Different things — don't cross them:** this is a step
cell inside a KC form; that one is the workpaper's binder-level sign-off.

## The SignOff property shape
`SignOff` on a `.{AREA}.ProgramSteps` step object is a JSON-ARRAY-IN-A-STRING:
- **sign-off:** `[{"userId","userReportName","date","staffId","type":0}]`
- **N/A mark:** `[{"userId","date","staffId","type":1}]`  (N/A carries no `userReportName`)
- **cleared:** `"[]"`  — un-sign and un-N/A are the SAME empty-array clear.

Applying a step sign-off is done by `populate_program.js` (the program-fill flow) — this module is
the CLEAR only.

## Prerequisites
- Leg: `kc` warm (Step 0). Rules 0–3 apply (SKILL.md). Use `ls:kc` auth (KC-tab localStorage).
- The step's `objectKey` and area key. Read the form (`kc.read_form`/`inventory_form`) and take the
  step's `objectKey` + its `.{AREA}.ProgramSteps` collectionKey. The AUD-8xx NUMBER is NOT in the
  key — `.AP.ProgramSteps`, never `.AP808.ProgramSteps`.

## Procedure
### 1. Clear the cell
```python
from scripts import kc
js = kc.clear_program_step_signoff(eng_guid, wp_id, "AP", step_object_key, "ls:kc")
```
### 2. Submit (REQUIRED to persist) + verify
```python
js = kc.submit(eng_guid, wp_id, "ls:kc")   # per-workpaper scoped — never empty wpId
```
Verify after reload via the diagnostics oracle, NOT the in-page GET (uncommitted working copy reads
false-clean). **200 ≠ applied**, and KC silently drops ~30–50% of write→submit pairs — run the
converge loop: write → ~1.2s → submit → re-read committed state → rewrite misses (field-conventions.md §5 3a).

## Known failure modes
- **Read-back looks clear but reverted after reload** — the clear wasn't submitted (or was dropped).
  Submit per-workpaper, then verify off diagnostics after reload; retry the miss.
- **Wrong collectionKey** — embedding the form number (`.AP808.ProgramSteps`) → the write no-ops.
- **eval hang on a backgrounded KC tab** — never fire the in-page fetch on a throttled/hidden
  KC tab; act on the active tab (or curl the captured bearer off-browser).

## See also
- `remove-signoff.md` — the DIFFERENT document-level (WPM) sign-off removal.
- `references/endpoints/kc_update_property.json` — the underlying endpoint (this is a specific payload of it).
- `populate-program.md` / `toggle-program-step.md` — applying step sign-offs / step visibility.

<!-- END -->
