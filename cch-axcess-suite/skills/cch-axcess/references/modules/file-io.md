---
summary: Upload/download an EXISTING binder file, or replace it via download→edit→re-upload (original stays recoverable, no index/name collision). NOT for building a NEW Excel workpaper (→ workpapers skill) or an in-place UNRECOVERABLE overwrite (→ replace-workpaper).
leg: wpm
triggers:
  - "add this file to the binder"
  - "upload this workpaper / Excel / PDF to the engagement"
  - "download this workpaper / report to my folder"
  - "pull this file out of the binder"
  - "download it, I'll edit it, then put it back"
  - "replace this workpaper with my edited copy"
  - "swap in a new version of this file"
inputs:
  - "Local file path (upload) OR target folder path (download)"
  - "Target binder folder + index (upload) / document to fetch (download)"
calls:
  - mcp__Claude_in_Chrome__file_upload  (upload — drives the page <input type=file>)
  - scripts.wpm.move
  - scripts.wpm.rename_workpaper
  - scripts.wpm.download_url / scripts.wpm.download_to_browser_js
  - scripts.wpm.evict_for_replace / scripts.wpm.claim_original_slot
  - scripts.wpm.check_index_available
status: validated   # live end-to-end on Playground binder 2026-05-31
---
# Module — Workpaper File I/O (upload / download / replace)

> **Index verification.** Read display indexes with `scripts.wpm.verify_index(row, object_type)` —
> Reports/KCForms use `index`, Workpapers use `documentIndex` (architecture.md → `index` vs
> `documentIndex`); hand-picking the field false-negatives. And NEVER hand-assemble the move body /
> `folderParentLineItems` — `wpm.move()` owns the per-type mapping and refuses raw bodies (the
> semantics are inverted per type; architecture.md → Move payload semantics).

All three flows live-validated on the Playground binder (client 100173, eng 390765) 2026-05-31.

## Prerequisites

- Engagement-view tab on `engagement.cchaxcess.com/.../engagementview/{engagementId}`.
- WPM headers captured (monkey-patch via `auth_capture`; reuse the same set for all three calls). Re-capture if a call starts returning 401/404 — the JWT rotates within a session.
- For the URL/IDs: `clientId` (URL first int), `engagementId` (URL second int), and — for download — `clientGuid` from KC `GetBinder.result.clientGuid` (also the `clientId` GUID field in `GET knowledgecoach/api/engagement/{engagementGuid}`).

## ⚠️ The PII-filter constraint (why bytes never cross the tool boundary)

The Cowork javascript_tool BLOCKS base64 in BOTH its return value and (assume) its input. So the skill cannot:
- read a downloaded blob's bytes back through the tool, or
- inject a local file's bytes into the page to build an upload `FormData`.

Both flows therefore lean on browser-native mechanisms (the `file_upload` tool for upload; a native `<a download>` for download) rather than passing bytes through JS. Plan around this — do not try to `btoa()`/return file content.

---

## 1. UPLOAD — add a file to the binder

> **BRIDGE PRIMARY (preferred):** `chrome_upload(local_path=<Windows host path>, url="https://workpapermanagementapi.cchaxcess.com/v1/Documents/{clientId}", field_name="file", headers={Authorization, IDToken})` — verified full pipeline (upload -> `wpm.move` into section -> set index). Do NOT set Content-Type. Capture headers via `chrome_network_recent`. The `file_upload`/base64-XHR flow below is the LINKED-TAB FALLBACK.

Endpoint (informational): `POST workpapermanagementapi.cchaxcess.com/v1/Documents/{clientId}` — `multipart/form-data`, single field `file`. You do NOT build this POST yourself.

**▶ Run the name-collision preflight BEFORE uploading** — the collision is enforced at the
upload POST itself (400 "File name already exists for an active workpaper."), not just at the
rename step (confirmed 2026-06-03). See AX-02 below.

```
# a) Find the page's hidden file input (the drop-zone backs onto a real <input type=file>):
find  ->  "file input element for uploading workpapers"      # returns a ref, e.g. ref_985
# b) Push the local file at it — Angular SHOULD fire the multipart POST on the change event:
file_upload(ref, ["C:\\...\\local\\file.xlsx"])              # native upload, no picker dialog
# file_upload needs the WINDOWS HOST path — bash-sandbox and outputs/ paths are rejected.
```

**▶ Verify the POST actually fired** — don't assume. Confirm a new Workpaper appeared in Unfiled
(`-1`) via `wpm.folder_get`. The Angular change handler is unreliable: it sometimes doesn't fire,
or the page navigates instead (AX-01).

**▶ VERIFIED fallback when the auto-POST doesn't fire (live 2026-06-03, T07):** the file_upload
tool still places the File into the `<input>`. In-page JS reads that File off the input and POSTs
`multipart/form-data` to `/v1/Documents/{clientId}` with the captured WPM headers — the bytes
never cross the tool boundary, so the base64/PII constraint above does NOT block this:

```js
const inp = document.querySelector('input[type=file]');
const f = inp.files[0];
const fd = new FormData();
fd.append('file', new File([f], 'TARGET_NAME.xlsx'));   // rename here if needed
// XHR POST to /v1/Documents/{clientId} with captured WPM headers (NOT Content-Type —
// the browser sets the multipart boundary). 200 → response carries the new documentId.
```

The monkeypatch captures the WPM header set from background page polls without needing a folder
click. This is the documented default when the change-event POST doesn't fire — verify which case
you're in via the folder_get(-1) count check above.

The file lands in **Unfiled Workpapers** (folder `-1`), `type:"Workpaper"`, `index:null`, with a fresh `documentId` (== its `locationId`) and `parentLocationId:-1`.

**Place + index it** (see `scripts/wpm.py`):

**▶ Name-collision preflight (AX-02).** A `(index, name)` is reserved across the WHOLE binder,
including the `User to delete` folder (index `9999`) — a stale copy parked there will block your
new file's name with `400 "File name already exists for an active workpaper."` Before claiming
the name, `folder_get` the target folder AND `9999` and scan for the same name; if a blocker
exists, `evict_for_replace` it first (bumps its index+name) to free the slot.

```python
from scripts import wpm
# move from Unfiled (-1) into the target section folder:
js = wpm.move(client_id, [{"object_type":"Workpaper",
                           "own_loc": -1,                 # current parentLocationId
                           "dest_loc": target_folder_loc, # section folder locationId
                           "object_id": document_id}], headers)
# assign an index (Workpaper type uses rename_workpaper, NOT set_index):
#   current_doc = the Workpaper row from a folder_get of the target folder
js = wpm.rename_workpaper(client_id, document_id, "3100", current_doc, headers)
```

**▶ Active-user lock (AX-03).** Right after an upload, `rename_workpaper` can return
`400 "There is an active user. Changes cannot be saved."` — a transient lock. Poll
`folder_get` / retry the rename until it clears (short backoff) rather than aborting; do NOT
re-upload (that just makes a duplicate).

The "Upload" panel in the UI shows "Uploaded successfully" + an *Assign Index* prompt — the API path above does the same thing headlessly.

## 2. DOWNLOAD — pull a file out to a local folder

Endpoint: `GET workpapermanagementapi.cchaxcess.com/v1/documents/{clientGuid}/file/{clientId}/{documentId}` → raw file bytes (live-confirmed: returns the exact xlsx, PK magic, correct byte size).

Mind the leading GUID: it is the per-CLIENT GUID (`clientGuid`), **not** the document's `fileId` (that field reads all-zeros on the metadata endpoint) and **not** `firmId`. `wpm.download_url(client_id, client_guid, document_id)` builds it correctly.

Because bytes can't come back through the tool, replicate the UI: XHR the URL as a Blob and trigger a native browser download.

```python
js = wpm.download_to_browser_js(client_id, client_guid, document_id, "C-1 Cash.xlsx", headers)
# run via javascript_tool; returns 'ok bytes=N'. The file saves to the browser's
# Downloads folder. Then relocate it to the user's target mounted folder
# (mount Downloads with request_cowork_directory if it isn't already):
#   cp ~/Downloads/"C-1 Cash.xlsx"  <target mounted folder>
# NOTE: use cp, not mv — the bash sandbox CANNOT unlink files on a mounted
# folder (rm -> "Operation not permitted"), so the Downloads original persists;
# tell the user it's there to clear. Validated end-to-end 2026-05-31: a 101KB TB
# workpaper downloaded, opened cleanly in openpyxl, copied to the target mount.
```

(Other doc routes are red herrings: `/v1/Documents/{cid}/{docId}` returns metadata JSON, `/v1/Documents/{cid}/{docId}/{index}` is an index-collision check, and the metadata's `documentUrl` returns an HTML viewer page — none serve bytes.)

## 3. REPLACE — download → edit → re-upload, no collision

The problem (live-reproduced): after re-uploading an edited copy, assigning it the original file's **(index, name)** returns
`400 "This combination of Index and Name already exists."` — even after the original is moved/soft-deleted, because the WPM index registry keeps the original's `(index, name)` reservation.

### ✅ DEFAULT path — soft-delete the original, then upload the replacement (index-bump eviction)

**This is the path to use** (Brett 2026-05-31): it never deletes and never overwrites, so the original always survives as its own recoverable document and no one can be blamed for lost data. The replacement comes in as a NEW document that takes the original's slot; the original is retired beside it.

```python
# original: the row being replaced (name, index, documentId, type) from folder_get
# 1) (optional) soft_delete the original into "User to delete":
wpm.soft_delete_workpaper(client_id, original_loc, user_del_loc, original_docid, headers)
# 2) EVICT — bump the original's (index,name) so the slot frees:
#    index "3100" -> "3100.DEL", name -> name + " (replaced)"
wpm.evict_for_replace(client_id, original_row, headers)
# 3) upload the edited copy (section 1), move it into the folder
# 4) CLAIM — the replacement takes the original's exact index + name:
wpm.claim_original_slot(client_id, new_row, "3100", original_name, headers)
```

Live result on Playground: EVICT 200, CLAIM 200, both files coexist —
`new @ "3100", original @ "3100.DEL (replaced)"`. The collision is gone, the original is preserved.

`wpm.check_index_available(client_id, document_id, index, headers)` pre-tests whether a target index is free (`{documentIndexExistsStatusCode:200}`).

### ⚠️ Native "Upload new version" — captured, but consent-gated (AX-33)

The workpaper row's `…` menu has **Upload new version** (an OVERWRITE: prior content survives only in
CCH version history, not as an independent workpaper). It fires **NO DELETE call** (not the
Kymera-style hazard) but is destructive-in-spirit. **The default is still the soft-delete→evict→claim
path above** — use it unless the user *explicitly* wants a true in-place version.

The in-place path **is now scripted** via `PUT /v1/Documents/file/{clientId}/{documentId}` —
see **`replace-workpaper.md`** — behind a **mandatory consent gate every time** (state it's
unrecoverable, show the exact TARGET-by-index/name/folder + REPLACEMENT-by-file plan, get an explicit
yes; a "just do it" does NOT waive the plan+yes). The replacement file's base name MUST equal the
workpaper's **current display name** or WPM 400s "File name does not match existing workpaper name".
Don't hand them off to the UI anymore — route to `replace-workpaper.md`.

> **Upload transport (F1, updated AX-34):** `chrome_upload` (bridge, service worker) is the VERIFIED
> PRIMARY upload path — full pipeline POST `/v1/Documents/{clientId}` -> `wpm.move` -> set index (no
> Content-Type; capture headers via `chrome_network_recent`). The in-page **base64-XHR** flow above is the
> LINKED-TAB FALLBACK (used when the bridge is down). The old 'chrome_upload fails CORS, never use it' rule
> is SUPERSEDED. (See `transport.md` -> "Uploads — chrome_upload is the primary path".)


## Known failure modes / gotchas

- **Upload "succeeded" but no Workpaper in Unfiled** = Angular change handler didn't fire (AX-01). Verify with `folder_get(-1)`; run the VERIFIED FormData fallback in the UPLOAD section.
- **`400 "File name already exists for an active workpaper."`** = name reserved somewhere in the binder, often the `User to delete` folder (`9999`) (AX-02). Enforced at the upload POST itself, not just rename (confirmed 2026-06-03) — run the preflight BEFORE uploading; `evict_for_replace` the blocker.
- **`400 "There is an active user. Changes cannot be saved."`** = transient post-upload lock (AX-03). Poll/retry the rename; do NOT re-upload.
- **401/404 mid-session** = the captured JWT rotated; re-capture headers and retry.
- **Workpaper indexing uses `rename_workpaper` (PUT /v1/Documents)** — `set_index` (the KCForms path) silently no-ops on Workpapers.
- **`rename_workpaper` needs the ACTUAL folder_get row** — synthetic dicts 400 (`rollForwardOption`, `documentId` missing). PUT success body is EMPTY; verify via follow-up folder_get.
- A freshly-uploaded Workpaper has `index:null` until you assign one; it sorts last.
- Download lands in the browser Downloads dir, not directly in the mounted folder — always relocate it afterward.


<!-- END -->
