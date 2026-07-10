# Suralink — Architecture (single source of truth)

This is the ONLY file that documents platform-level facts. Modules cite this file; they do not repeat it. Endpoint shapes live in JSON specs at `endpoints/`.

If you discover a new fact about the platform, update this file (and the relevant `endpoints/*.json`). Do not paste it into a module.

## Hosts

| Host | Purpose | Style | Auth |
|---|---|---|---|
| `app.suralink.com` | Legacy jQuery/PHP app. Pages render the UI; AJAX runs through "gateways". | `Audit.php?auditId=`, `Clients.php`, etc. + `/gateways/{a-t}Gateway.php` | Session cookie |
| `api.suralink.com` | Modern REST API. JSON in/out. | `/v2/...` | Session cookie (CORS allows the `app.suralink.com` origin with credentials) |

## Auth pattern

**Cookie-based. There is no bearer token.** The user logs into `app.suralink.com` in Chrome; the session cookie authorizes both hosts. Every call must be made with `credentials:'include'`.

- `api.suralink.com` without cookies → `401`.
- Cross-origin `fetch()` from an `app.suralink.com` tab to `api.suralink.com` **works** — Suralink sends the CORS headers to allow it with credentials.

Prerequisite: a Chrome tab logged into Suralink. If a call returns `401`, the session expired — the user must log in again. The skill cannot log in for them.

### Session verification — assert the auditId, not just "a page loaded"

The cheap verification read after navigating to an audit MUST assert that the page reflects the **requested** `auditId` — both the URL `auditId=` param and `window.auditId` must equal it. "A Suralink page loaded" is NOT a pass. Use `scripts/suralink.py :: verify_audit_js(audit_id)` before any real work on an audit.

Why (observed 2026-07-09, SCDC 401k): a **reused stale tab's** login bounce carried a `returnTo` pointing at a *different* auditId (2871416) than the one requested (2852254) — the tab's last-visited audit, not the target. Logging back in through that bounce lands on the wrong audit, and a naive liveness check green-lights it. After any login bounce, re-navigate to the requested `Audit.php?auditId={X}` explicitly; never trust the bounce's `returnTo`.

**Login-bounce signatures** (tab lands on `accounts.suralink.com/login`):
- `...&logout=true` in the query = the session was **invalidated** (explicit logout / server-side kill) — distinct from an idle-timeout bounce, which lacks `logout=true`. Either way the user must log in again; the skill cannot.
- The bounce's `returnTo` param encodes the tab's stale prior location — parse it only to *detect* the mismatch (`verify_audit_js` surfaces it as `returnToAuditId`), never to navigate.
- Expired-session transient (observed 2026-07-09): navigating an expired tab to `Audit.php` can bounce through `app.suralink.com/logout.php?...&sessionExpired=true&returnTo=...` — on the APP host, not `accounts.`. It resolves to the logged-in `Audit.php` once the session cookie lands. `verify_audit_js` correctly returns `ok:false` for it, but does NOT tag it `logoutBounce` (that flag keys off the non-app host). Treat any `ok:false` as "not ready" and re-check after the user logs in — don't special-case this transient.

**Validated live 2026-07-09** (chrome-bridge browser, auditId 2871416): `verify_audit_js(2871416)` → `{ok:true, urlAuditId 2871416, pageAuditId 2871416, path /auditors/views/Audit.php}` on a freshly logged-in Audit.php tab; before login the expired-session navigation returned `ok:false` as designed. (Note: the fleet's live session lives in the **chrome-bridge** browser — logging into Suralink on another browser surface does NOT make the bridge session live.)

## Transport — bridge PRIMARY, linked tab FALLBACK

Detect ONCE per session — the **first browser call is `chrome_bridge_status`** (see SKILL.md
Step 0). Server up → **BRIDGE** for the whole session; tool absent / errors → **LINKED-TAB**
(the Claude-in-Chrome flow). Both transports run the same `scripts/` JS builders inside the
same logged-in Suralink tab — cookies authorize everything either way; only the tool differs.

| Operation | BRIDGE (preferred) | LINKED-TAB (fallback) |
|---|---|---|
| Find the Suralink tab | `chrome_list_tabs` → pick by `app.suralink.com` URL (sees ALL real tabs) | `tabs_context_mcp` / the user's linked tab |
| Run a JS builder | `chrome_eval(code, target=tabId)` | `mcp__Claude_in_Chrome__javascript_tool(code, tabId)` |
| Navigate / open tab | `chrome_navigate` / `chrome_open_tab` | `navigate` / `tabs_create_mcp` |
| Big JSON out of the tab | `chrome_eval(..., out_path=...)` — straight to disk, one call | Blob ferry to `~/Downloads` (see below) |
| Download a file (fileProxy) | `download_file_js` via `chrome_eval` → Downloads folder (same mechanism, validated). `chrome_download(url, out_path)` straight to the mirror is *expected* to work (cookie jar rides along) but **not yet validated on fileProxy** — validate once, then prefer it | `download_file_js` via `javascript_tool` → Downloads folder |
| Network capture (training mode) | `capture.py` monkeypatch via `chrome_eval`; `chrome_network_recent` is also available and survives pushState | `capture.py` monkeypatch (`read_network_requests` is unreliable — see gotchas) |

## ID glossary

Suralink uses several IDs that look interchangeable but are not. Mixing them produces silent `403`/`404`/`500`.

| ID | What | Source | Used as |
|---|---|---|---|
| `auditId` | Per-engagement integer (e.g. `2774111`). The "audit". | URL `Audit.php?auditId={X}`; JS global `window.auditId` | `aId` in fileProxy; `requestListId` in v2 calls; path slot in v2 paths |
| `organizationId` | Per-firm GUID (the CPA firm). Stable across all that firm's engagements. | inline `<script>` var `organizationId` (regex it out — see below); v2 query param; `data.organizationId` on responses | `organizationId` query param; org-scoped v2 paths (`/v2/organization/{organizationId}/...`) |
| `clientId` | Per-client integer (e.g. `1126793`). One client owns many engagements (audits). | `Clients.php` DOM `clientRow_{clientId}`; v2 `/clients` object field `id`; client dropdown `topMenuClient_{clientId}` | gateway `getClientInfo` param `clientId` — the key that maps a client to its engagements |
| request `id` | **The canonical request identifier** — 8-digit integer (e.g. `91772336`, `93605893`). | DOM `<li id="request_{id}_min">`; gateway `getRequest` response field `id`; gateway `getRequest` *input* param `requestId` | `rId` in fileProxy; `{requestId}` path slot in `/v2/request/{id}/...` |
| request `requestId` (response field) | A short 2-char internal display index. **NOT a real id.** | `data.requestId` on a `getRequest` response | nothing — ignore it |
| file `id` | Per-file integer (e.g. `198983476`). | `getRequest` response `files.firm[].id` / `files.client[].id` | `fId` in fileProxy |
| file `fmsId` | Per-file GUID (file-management-system id). | `getRequest` response file objects | identity / dedup key |

**Naming trap (critical):** the 8-digit canonical request id is passed to the *gateway* under the param name `requestId`, but inside a gateway *response* the field named `requestId` is a different, 2-char value. Always treat the 8-digit number — the one in the `<li id="request_..._min">` and in the response field `id` — as the request identity. Never send the 2-char `requestId` field anywhere.

## The v2 REST API (`api.suralink.com`)

Confirmed live. JSON responses are usually `{success, data}` or a bare object/array. All calls cookie-authed, `credentials:'include'`.

| Op | Endpoint | See |
|---|---|---|
| **Download a file** | `GET /v2/fileProxy?fId={fileId}&aId={auditId}&rId={requestId}` | `endpoints/v2_fileProxy.json` |
| **List all clients** (paged) | `GET /v2/organization/{organizationId}/clients?limit&offset` | `endpoints/v2_clients.json` |
| Search clients | `GET /v2/organization/{organizationId}/clients/search?searchTerm={term}` | `endpoints/v2_clients_search.json` |
| Request history | `GET /v2/request/{requestId}/history?limit&offset&organizationId&requestListId={auditId}` | `endpoints/v2_request_history.json` |
| Request item detail | `GET /v2/organization/{organizationId}/requestList/{auditId}/requestItem/{itemId}` | — |
| Request item comments | `GET /v2/organization/{organizationId}/requestListId/{auditId}/requestItemId/{itemId}/comment?limit&offset` | — |
| Assignable users | `GET /v2/engagement/{auditId}/assignableUsers?requestItemId={itemId}` | — |

### fileProxy — the download endpoint (most important)

`GET https://api.suralink.com/v2/fileProxy?fId={fileId}&aId={auditId}&rId={requestId}`

- Returns the **raw file bytes** with the file's real content-type (e.g. `application/pdf`). Verified: a 717,607-byte PDF came back intact.
- `rId` **must** be the canonical 8-digit request `id` that the file belongs to. A wrong `rId` → `403 {"error":"forbidden","message":"User has no access to this engagement"}`.
- `fId=-1` is a no-op ping that returns `{"success":true}` — the UI fires it before a real download. The skill does not need it.
- No `Content-Disposition: attachment` header — the URL alone displays inline. To save to disk, fetch as a blob (see `scripts/suralink.py`).
- **`c` param (native attachment download).** Suralink's own single-file download sets the hidden downloader iframe's `src` to `fileProxy?c={token}&aId&rId&fId` — the `c` param makes the response download as an attachment. The skill does **not** need it: `download_file_js` fetches the blob and saves it with an `<a download>`, which is equivalent and keeps bytes out of Claude's context.

## The legacy gateway API (`app.suralink.com/gateways/*Gateway.php`)

`POST` with a `application/x-www-form-urlencoded` body. There are 20 gateway files, `aGateway.php` … `tGateway.php` — **the letter is interchangeable**; the same command works through any of them. Pick one (the skill uses `aGateway.php`).

Body fields on every gateway call:

| Field | Value |
|---|---|
| `secret` | `aud1tMgr!` — static, required on every call |
| `controller` | e.g. `/Controllers/Auditors/Audit` |
| `command` | e.g. `getRequest` |
| `csrf_token` + `csrf_hash_offset` | CSRF pair — page-specific, must be read live from the page (see `scripts/suralink.py:csrf_js`) |
| (operation params) | e.g. `requestId`, `auditId`, `fromAudit`, `limitedData` |

Response: JSON `{success, data}`.

### Confirmed gateway commands

| Controller | Command | Params | Returns |
|---|---|---|---|
| `/Controllers/Auditors/Audit` | `getRequest` | `requestId` (8-digit id), `auditId`, `fromAudit=true`, `limitedData=true` | `data` = full request detail incl. `files.firm[]`, `files.client[]`, `filesAggregate` |
| `/Controllers/Auditors/Audit` | `viewRequest` | `auditId`, `requestId` | request view payload |
| `/Controllers/Auditors/Clients` | `getClientInfo` | `clientId` | `data = {groupId, html}` — `html` is the client's engagement-table fragment. See "Clients & engagements" below. |
| `/Controllers/Shares/IAN` | `loadIAN` | `ianType=1`, `showMine=-1`, `auditId`, **`lastId`** (required — `0` for the full feed) | `data.ianData = {newestId, messages[], ...}` — the activity timeline. Omitting `lastId` → `missingParameter`. |
| `/Controllers/Shared/Misc` | `changeUserSetting` | UI-state params | UI state — **ignore, not useful** |

### File object shape (from `getRequest` `data.files.firm[]` / `.client[]`)

`{ id, fmsId, createdTime, requestType, userType, userId, fileSize, deltaValue, origFileName, fileType, stateChange, ts, providedByName, providedDate, downloads[], user{} }`

`firm` = files the audit firm posted; `client` = files the client uploaded. For an audit file pull you almost always want `client`.

### Deleted / retracted files
A file deleted in the portal simply **drops out** of `getRequest`'s `files.client[]` / `files.firm[]` — there is no per-file `deleted` flag on the request detail. The reliable signal is therefore **absence**: a file whose `fmsId` was seen on a prior enumeration but is missing from a fresh one has been deleted or retracted. (The `loadIAN` timeline also carries `isDeleted` on its file objects, but the timeline is not a dependable whole-engagement source — see the `loadIAN` row above.) The `suralink-sync` skill acts on this by tombstoning, never by deleting the local copy.

## Enumeration

### Requests in an audit
The `Audit.php?auditId={X}` page renders every request as `<li id="request_{id}_min">`. Per-`li` data attributes include `data-newcontentfiles` (count of new files), `data-newcontentcomments`, `data-statesortid`, `data-creationdate`, `data-duedate`, `data-firstletter` (category letter). Enumerate by reading the live DOM (see `scripts/suralink.py:list_requests_js`).

### Clients / engagements
Do **not** scrape `Clients.php` for the roster — it is a React app that only renders one client at a time. Use the backend instead; see "Clients & engagements" below.

## Clients & engagements

A **client** (a CPA-firm customer) owns one or more **engagements** (audits). The roster and the client→engagement mapping are backend calls, not a DOM scrape.

### organizationId — read it once per session
Every `/v2/organization/...` call needs the firm GUID. It is not a window global, but it is assigned in an inline `<script>`. Extract it:
`document.querySelectorAll('script:not([src])')` → regex `organizationId["']?\s*[:=]\s*["']([0-9a-f-]{30,})["']`. Stable for the whole session. `scripts/suralink.py :: get_org_id_js()`.

### The client roster — `GET /v2/organization/{org}/clients`
Paged: `?limit&offset`. Response `{totalCount, offset, limit, data:[...], nextPage}`. **`limit` is capped at 100** server-side regardless of what you ask. Each client: `{id (clientId), customId, name, state, contactFirstName, contactLastName, contactEmail, departmentId, isSensitive, lastLogin, isAssigned}`. Page with `offset` (0, 100, 200, …) until `offset + data.length >= totalCount`. See `endpoints/v2_clients.json`.

`clients/search?searchTerm={term}` is the name-indexed search (`{totalHits, hitsCount, clients:[{score, highlight, source}]}`, `source` is the client object incl. `engagementCounts {total, active, inactive, archived}`). Empty `searchTerm` → `400`. Use it for "find the client called X"; use the paged `/clients` for "enumerate everything".

### A client's engagements — gateway `getClientInfo`
The roster does **not** carry engagements. For one client, gateway `getClientInfo {clientId}` → `data.html`, an HTML fragment. Parse it:
- Engagement rows: `tr[id="clientRow_{clientId}_engagements_row_{auditId}"]` — the `auditId` is in the row id.
- Row class carries the state: `Active` / `Inactive` / `Archived`.
- `.engagementName` cell = the label (e.g. `Audit 2025`); `.customId` cell = the engagement's customId.
- Skip the placeholder row `..._row_empty`.

This is how the same client's prior-year and current-year audits are told apart — they are sibling `auditId`s under one `clientId`. `scripts/suralink.py :: get_client_engagements_js()`.

### Bulk-zip download — UI-only (not scripted)
Suralink can hand a whole selection over as one zip: select-all → `Download` → the "Download Multiple" popup → `#multiDownloadCategory_Btn` (the `Categories / Requests` option; siblings `#multiDownloadCategoryOnly_Btn`, `#multiDownloadFolder_Btn`). It is driven by page globals `downloadArchivedFilesFromPortal` / `getClientArchiveDownloadUrl` and the endpoint family `/v2/client/client-archive/.../requestItem/.../downloadZip`, delivered through a hidden iframe. **The trigger evaded every capture hook** (fetch, XHR, form-submit, anchor-click, window.open, iframe-src) across multiple sessions — it cannot currently be scripted. The bulk zip stays a user-initiated fast path (`suralink-sync` `import-zip.md`); for fully-scripted bulk pulls use the per-file `fileProxy` loop (`download-files.md`).

## Deep-link URL patterns

```
Audit / request list:  https://app.suralink.com/auditors/views/Audit.php?auditId={auditId}
A single request:      https://app.suralink.com/auditors/views/Audit.php?auditId={auditId}&requestId={requestId}
Client list:           https://app.suralink.com/auditors/views/Clients.php
```
**The `/auditors/views/` prefix is required.** A bare
`https://app.suralink.com/Audit.php?auditId=…` returns nginx 404, not a
redirect — there is no fallback at the apex. When a module says "navigate
to `Audit.php?auditId={X}`", read it as "navigate to that full URL".
Navigating between requests with `&requestId=` is a client-side `pushState` — it does NOT reload the page.

## Known gotchas

- **`read_network_requests` (linked-tab tool) is unreliable here.** Its buffer clears on the `pushState` request-id changes. Use the capture monkey-patch in `scripts/capture.py` instead, and never have the user do a full page reload mid-capture (a reload wipes the patch). On the bridge, `chrome_network_recent` is an additional option that survives pushState.
- **The Cowork content filter blocks raw URLs/tokens** in tool output. When surfacing captured data, emit sanitized derivatives (paths with IDs masked, param names not values) — see `training-mode.md`.
- A full browser reload kills any installed monkey-patch. Re-install after any reload.
- **Gateway calls run sequentially** (one fetch in flight at a time). Suralink's session serializes them; two in flight collide on the session, not the CSRF token. `window.csrf` is read LIVE per call so any rotation is harmless. Note: on read-only commands like `getRequest` the token does NOT observably rotate — a whole-engagement sweep of 28+ requests uses a single `window.csrf` snapshot. The older lore here ("CSRF rotates per call") was overstated. Keep the sequential rule anyway — it's correct for the right reason.

## Getting large data out of the tab

The Cowork tool channel truncates JS return values at roughly 1 KB of display.
A whole-engagement enumeration (28-90 requests with files) is many KB, and
chunked round-trips (15+ JS execs to page through a `slice(i, i+n)`) are slow
and brittle.

**On the BRIDGE, skip the ferry entirely:** `chrome_eval(js, target=tabId, out_path=...)`
writes the full result straight to disk in one call — no Downloads staging, no wait loop.
The Blob ferry below is the **linked-tab** path (and it remains the mechanism behind
`download_file_js` on both transports).

**Linked-tab pattern: Blob ferry to the Downloads folder.** On the JS side,
serialize the result as JSON, wrap it in a `Blob`, trigger a synthetic
`<a download>` click — Chrome saves it to the user's Downloads folder. On
the Python side, read the file with `json.load`. One round-trip per dump,
no truncation, no chunking.

Helpers:
- `suralink.dump_to_download_js(payload_expr, filename)` — JS-side, dumps
  a JS expression as JSON to `~/Downloads/{filename}`.
- `suralink-sync` skill's `sync.wait_and_read_json(download_dir, filename)`
  — Python-side, blocks until the file exists and parses it.

The same Blob-anchor mechanism powers `download_file_js` for fileProxy
downloads — this is just the JSON variant. Prefer it over chunked reads
for any payload larger than ~500 bytes.

## What's NOT in here

Workflows (the sequence of calls) live in module files. The gateway command that bulk-loads a request list on `Audit.php` load is **not yet captured** — see `training-mode.md` "Known unknowns". Enumeration currently goes through the DOM, which is reliable.
