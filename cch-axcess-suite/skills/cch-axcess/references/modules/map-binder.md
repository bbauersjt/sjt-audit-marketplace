---
summary: Map the binder — full low-token inventory of folders + filed items (find a workpaper/form)
leg: wpm
triggers:
  - "map the binder"
  - "map the contents of the binder"
  - "binder map"
  - "inventory the binder"
  - "what's in this binder"
  - "where is workpaper X / form Y"
  - "pull the binder structure"
inputs:
  - "Engagement URL (clientId + engagementId)"
  - "engagement.cchaxcess.com tab on the target binder"
calls:
  - scripts.auth_capture.INSTALL_MONKEYPATCH_JS
  - scripts.binder_map.build_map_js
  - scripts.binder_map.fetch_chunk_js
status: validated
---

# Module — Map Binder

## What this does

- Produces a single low-token, greppable map of an entire engagement binder — every folder plus every filed item (KCForms / LeadSheet / Report / Workpaper) with its index, name, status and id.
- Resolve "where is X" by grepping the file instead of walking folders one-by-one.
- Structure is read live, so it adapts to any binder layout.

## Prerequisites

- WPM headers (the map walks `workpapermanagementapi`). Per architecture.md, KC
  localStorage tokens are PRIMARY auth for WPM — so a **KC tab is the simplest source**
  and an engagement tab is **NOT required just for headers**. Two equivalent ways in:
  - **KC tab present (preferred):** `build_map_js` self-sources `kc.accessToken` +
    `kc.idToken` from localStorage and sends them WPM-style (`Authorization` + all-caps
    `IDToken` + locale headers) — no monkeypatch, no folder click. Tokens never leave
    the browser.
  - **Engagement tab only (fallback):** install the monkeypatch
    (`scripts.auth_capture.INSTALL_MONKEYPATCH_JS`) and trigger ONE WPM call (click any
    folder) so a header set lands in `window.__cch_capture`; the map JS auto-discovers
    the freshest `workpapermanagementapi` headers from it.
- clientId (first int in URL) and engagementId (second int) — from whichever tab is on
  the binder.

## Procedure

### 1. Get WPM headers
If a KC tab is open, skip straight to step 2 (localStorage-primary, no click). Only on an
engagement-tab-only session: install the monkeypatch, then have the user click any folder
once (fires a WPM call).

### 2. Build the map

> **Transport:** on the BRIDGE run the map JS via `chrome_eval` (engagement origin, `leg: wpm` — not CSP-blocked) or pull folders directly with `chrome_api_call`; the in-page `javascript_tool` path below is the LINKED-TAB fallback.
```python
from scripts import binder_map
js = binder_map.build_map_js(client_id, eng_id, download_filename="<slug>-binder-map")
```
Run `js` via `mcp__Claude_in_Chrome__javascript_tool`. It walks the binder and returns
ONLY compact counts (`folderCount`, `itemCount`, `byType`, `mapChars`). The full map is
stashed on `window.__binder_map` and downloaded as `<slug>-binder-map.txt` (+ `.tsv`)
if `download_filename` is set. Downloads need the user's OK.

### 3. Persist as reference (no-download alternative)
If a browser download isn't wanted, pull the stash in slices and write to disk:
```python
js = binder_map.fetch_chunk_js("tsv", start, 1200)   # loop until start>=total
```
Save to the user's working folder (the mounted Cowork directory) as `{slug}-binder-map.tsv` so future runs can grep it directly. **Never write engagement state into this read-only install** — `references/data/` ships reference data the *user* may edit, but the agent does not self-write the install at runtime (SKILL.md "READ-ONLY cache").

### N. Verify
Spot-check `itemCount` / `byType` against the Engagement View, and confirm a known
workpaper appears (`grep` the `.tsv`).

## Known failure modes

- **Map shows folders but zero documents** → the contents call hit the wrong endpoint.
  Folder CONTENTS = `GET /v1/NewEngagementView/{clientId}/{locationId}/{engagementId}`.
  The sibling `/v1/NewEngagementView/folder/{clientId}/{locationId}/` returns child
  FOLDERS only and silently omits every filed document. See architecture.md.
- **`error: No WPM capture`** → monkeypatch not installed, or no WPM call fired yet.
  Install it and click a folder once.
- **Doubled file extension in names** → handled; the renderer dedupes automatically. WPM rows carry the extension in both `name` (e.g. `"Payroll Register.xlsx"`) and `fileExtension` (`"xlsx"`) — `build_map_js` strips the duplicate before writing the map. If consuming the raw TSV directly: strip a trailing `.{ext}` from `name` when `fileExtension` is non-empty.

<!-- END -->
