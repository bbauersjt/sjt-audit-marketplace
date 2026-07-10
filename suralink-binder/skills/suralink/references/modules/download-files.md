# Module — Download Files

**Triggers:** "download the files", "pull files from this request", "get the client uploads", "grab everything new", "save these files"

## What this does

For one or more requests in an audit: lists the files attached to each, then downloads them through Suralink's `fileProxy` endpoint. This is the engine the `suralink-sync` skill drives.

## Prerequisites

- A Chrome tab logged into `app.suralink.com`, on
  `https://app.suralink.com/auditors/views/Audit.php?auditId={X}` (full
  `/auditors/views/` prefix required — bare apex returns nginx 404).
  Verify with `suralink.verify_audit_js(audit_id)` → `ok:true` — the page must
  reflect the REQUESTED auditId (architecture.md → "Session verification").
- The `auditId`.
- The request `id`(s) — from `list-requests.md`.

## Procedure

### 1. Get the file list for a request
```python
from scripts import suralink, browser
js = suralink.get_request_js(audit_id, request_id)   # gateway getRequest
# run js in the tab, then:
body = browser.parse_result(js_result)["body"]
client_files = suralink.extract_files(body, side="client")  # client uploads
firm_files   = suralink.extract_files(body, side="firm")    # firm-posted files
```
Each file dict: `id` (fId), `fmsId`, `origFileName`, `fileType`, `fileSize`, `ts`.

**Run `getRequest` calls sequentially** — one fetch in flight at a time. Suralink's session serializes gateway calls; parallel calls collide on the session, not the CSRF token. On read-only commands like `getRequest` the token does NOT observably rotate, so a whole-engagement sweep of 28+ requests can run inside ONE `javascript_exec` using an `await`-in-`for-loop` pattern. See `architecture.md` and `browser.py:js_gateway`.

### 2. Download each file
Bytes must NOT travel through Claude's context for a bulk pull. Use the blob method — the file lands in the browser's Downloads folder:
```python
js = suralink.download_file_js(file["id"], audit_id, request_id, file["origFileName"])
# run js in the tab -> {ok:true, bytes, filename}
```
For a single small file whose bytes Claude must write itself, `suralink.fetch_file_b64_js(...)` returns base64 instead — do not use it for bulk.

### 3. Verify
Check each result's `ok` and that `bytes` matches the file's `fileSize` (±a few hundred bytes is normal). A `403` with "User has no access to this engagement" means the `rId` did not match the file's request — recheck the request `id`.

## Known failure modes

- `403 forbidden / no access` → wrong `rId`. `rId` MUST be the request `id` the file belongs to (architecture.md, ID glossary).
- `{"success":true}` instead of bytes → `fId` was `-1` (a UI ping), not a real file id.
- `401` → the Suralink session expired. The user must log in again.
- Browser blocks repeated downloads → space the calls out, or download in smaller batches.

## Validated on

- Audit 2774111 — fileProxy returned an intact 717,607-byte PDF, 2026-05-22.
