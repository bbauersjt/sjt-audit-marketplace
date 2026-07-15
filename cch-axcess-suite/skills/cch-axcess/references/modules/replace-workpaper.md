---
summary: Replace a workpaper's content in place (native "Upload new version") — UNRECOVERABLE overwrite, hard consent gate every time
leg: wpm
triggers:
  - "replace this workpaper with [file]"
  - "upload a new version of [workpaper]"
  - "overwrite [workpaper] with my edited copy"
  - "swap in this version in place"
inputs:
  - "engagement (clientId)"
  - "target workpaper (documentId) + its current display name"
  - "replacement file (local path / bytes)"
calls:
  - scripts.wpm.folder_get      # read the target's CURRENT display name
  - scripts.wpm_replace.build_replace_version_js
status: validated
---
# Module — Replace Workpaper (in-place new version)

## What this does
- Overwrites a workpaper's content in place via `PUT /v1/Documents/file/{clientId}/{documentId}` (native "Upload new version"). Same documentId; the prior content survives ONLY in CCH version history.
- **Distinct** from the default replace (soft-delete→evict→claim, which keeps the original as an independent recoverable document) — use that default unless the user explicitly wants a true in-place version.

## ⛔ MANDATORY CONSENT GATE — every time, no exceptions
This operation can **unrecoverably replace** a workpaper. Before ANY replace, you MUST:
1. **State plainly that this is an in-place overwrite that cannot be undone.**
2. **Show the exact plan** — for EACH replacement, list:
   - the **TARGET** being overwritten: its index + display name + folder/location (its address), and
   - the **REPLACEMENT** going in: the file name + source (its address).
3. **Ask "Are you sure?" and get an explicit YES.** Anything short of an explicit yes = do not proceed.

No silent, batched, or implied replace — the confirmation fires on every run, even mid-batch. (User
consent does not let you skip showing the plan; a user "just do it" still requires the plan + a yes.)

## Procedure
### 1. Read the target's CURRENT display name (load-bearing)
```python
from scripts import wpm
# folder_get the workpaper's folder; find the row by documentId; take row['name'].
```
The replacement File's **base name MUST equal this current display name** (not the original upload
name, not the stored blob which is crypto) or WPM 400s "File name does not match existing workpaper
name." Keep the file's real extension.

### 2. CONSENT GATE (above) — show the plan, get the yes. STOP if no.

### 3. Build + PUT (only after yes)
```python
from scripts import wpm_replace
js = wpm_replace.build_replace_version_js(client_id, document_id, file_b64, match_filename)
# run via chrome_eval(target=<engagement tab>, VISIBLE). 200 empty = replaced; 400 = name mismatch.
```

### 4. Verify
Re-`folder_get`; confirm the latestVersionNumber incremented. (Success body is empty.)

## Known failure modes
- **400 "File name does not match existing workpaper name."** → the file's base name ≠ current display
  name. Re-read the display name (step 1) and rename the File to match exactly.
- **Background/hidden tab** → write may drop or eval may time out. Use a visible engagement tab.
- **CORS** → use in-page XHR (not fetch) for the cross-origin engagement→WPM PUT.

## No-hard-delete relationship
Not a delete (fires no DELETE call), but destructive-in-spirit. Allowed, but
ONLY behind the consent gate above.

<!-- END -->
