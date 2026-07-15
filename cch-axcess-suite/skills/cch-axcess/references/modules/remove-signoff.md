---
summary: Remove a stale document-level (WPM) sign-off from a workpaper or KC form — the clears-its-own-stale-sign-off op. Applying sign-offs stays human-only.
leg: wpm
triggers:
  - "remove the sign-off"
  - "un-sign [form]"
  - "clear the stale sign-off"
  - "take [preparer]'s sign-off off [workpaper]"
  - "the form's flagged modified-after-signoff"
  - "pull the sign-off so it re-reviews"
inputs:
  - "Engagement-view (or KC) tab with WPM headers capturable (cap:wpm) or KC localStorage (ls:wpm)"
  - "the workpaper's documentId (objectId) + objectTypeId + which leg (preparer/reviewer)"
  - "clientId, clientGuid, engagementGuid"
calls:
  - scripts.wpm.remove_signoff
  - scripts.wpm.document_get
  - scripts.auth_capture.INSTALL_MONKEYPATCH_JS
status: validated
---
# Module — Remove Sign-Off (document-level, WPM)

## What this does
- Removes ONE document-level sign-off (preparer or reviewer) from a workpaper or KC form via `POST /v1/signoff/removeSignOff`.
- Rule: when a form is modified, the prior sign-off is stale and comes off (KC's modified-after-signoff diagnostic already flags the form; removing the sign-off is the clean resolution).
- **Applying sign-offs is HUMAN-ONLY.** There is no add path in this module or in `wpm.py` by design. The add endpoints (`POST /v1/signoff/preparer`, `POST /v1/signoff/reviewer`) are recorded in `references/endpoints/signoff_remove.json` for completeness only.
- **In-form program-STEP sign-offs are a DIFFERENT thing** — those are KC UpdateProperty pt=3 cells (the `kc.py` leg), not this WPM document-level sign-off. Don't cross them.

## Prerequisites
- Leg: `wpm` warm (Step 0). Rules 0–3 apply (SKILL.md).
- The target's `documentId`, `objectTypeId`, and leg (preparer=1 / reviewer=2). Get them from a
  `wpm.folder_get` row (`documentId`, `signOffs[]`) or `wpm.document_get` (denormalized
  `preparedBy*`/`reviewedBy*` fields). **Never hardcode objectTypeId** — KC forms are 4 (GUID
  objectId), uploaded workpapers are 1 (numeric-string objectId).

## Procedure
### 1. Identify the sign-off to remove
```python
from scripts import wpm
js = wpm.document_get(client_id, document_id, "cap:wpm")   # or folder_get for the whole folder
```
Read the leg: `preparedBy1*` present → a preparer sign-off (signatureType 1); `reviewedBy1*`
present → reviewer (2). A cleared leg reads null name / null datetime / all-zero UserId.

### 2. Remove it
```python
js = wpm.remove_signoff(client_id, object_id, object_type_id, wpm.SIGNATURE_PREPARER,
                        client_guid, engagement_guid, "cap:wpm")
```

### 3. Verify (HTTP 200 = accepted, not applied — re-GET; architecture.md)
The 200 body echoes the remaining `{"signoffDetails":[...]}`. Confirm independently:
```python
js = wpm.document_get(client_id, document_id, "cap:wpm")   # removed leg's fields now null
```

## Known failure modes
- **Never remove another user's sign-off (out of bounds)** — the body has NO userId; removal is
  keyed by `(objectId, signatureType)`, so the API clears whichever sign-off holds that leg,
  including a colleague's. The binder UI only lets you remove your OWN, so this operation must too
  (api-ui-parity). Step 1 is MANDATORY: confirm the leg's `userId` is the CURRENT
  logged-in user; if it's someone else's, STOP — do not remove it via API, and do not probe
  whether the API allows it. Using the API to exceed the UI creates untested, corrupt state.
- **Wrong objectTypeId** — echo the row's own value; a KC form (4) and an uploaded workpaper (1)
  are not interchangeable.
- **401 mid-batch** — WPM bearer rotated (~30 min); re-capture (cap:wpm re-reads the freshest
  captured bearer; a fresh navigation/keepalive refreshes it).

## See also
- `references/endpoints/signoff_remove.json` — wire spec + add-endpoint reference.
- `toggle-program-step.md` — the DIFFERENT in-form KC step sign-off (pt=3), not this.

<!-- END -->
