# Module — Run Sync

**Triggers:** "sync Suralink", "pull new files", "update my local copy", "check
for new uploads", "what's new in Suralink", "sync these clients", "pull down the
history", "set up the sync"

## What this does

One idempotent pass over the active engagements: refreshes each engagement's
portal snapshot (`_index.json`), finds files not yet in the mirror, finds files
deleted in the portal, gets the user's OK, downloads the new ones, tombstones
the deleted ones. Re-running only ever pulls genuinely new files. A first run
against a never-synced engagement pulls its whole history — same pass, no
special mode.

**Newly-activated engagements get a full pull.** If the user adds an
engagement to the active list and then asks to sync it, treat that as a request
for the whole history — full scope, do not ask the user to narrow it. Do still
offer the bulk-zip route (step 4): a fresh full pull is exactly where the zip
earns its clicks.

## Setup — runs automatically every run (idempotent)

1. **Resolve the root — remembered, or ask once.**
   - Mount the pointer anchor: `request_cowork_directory` for
     `location.MOUNT_HINT_CONFIG_ANCHOR` (`~/Documents` — the profile ROOT
     `~` is NOT mountable in Cowork; it holds Claude's own session storage
     and the harness refuses it, so the anchor is the always-mountable local
     Documents folder; fallback `MOUNT_HINT_CONFIG_ANCHOR_FALLBACK` is also
     `~/Documents`). The pointer itself lives in the shared
     `_claude-config` subfolder (`location.CONFIG_SUBDIR`) — if that subfolder
     does not exist yet, `~/Documents` still mounts and `save_mirror_root`
     creates it. Read it: `saved = location.saved_mirror_root(anchor_mount)`.
   - **If `saved` is set** → that is the root. Mount it with
     `request_cowork_directory(saved)`. Don't prompt — just tell the user once,
     in passing: *"Files saved to `…\Audit Clients` — to change the target
     directory, just ask."* If the user asks to
     change it, follow **Changing the root** below (warn + offer to move) — do
     NOT just overwrite the pointer.
   - **If `saved` is None (first run)** → **launch the native folder picker by
     calling `request_cowork_directory` with NO `path` argument** — that opens
     the OS folder browser so the user actually chooses where the mirror lives
     (passing a path would only mount that path, not let them pick). Only in a
     remote session, where an omitted path is rejected, fall back to
     `request_cowork_directory(location.MOUNT_HINT_PICKER_DEFAULT)` (the
     local profile root, not OneDrive). **Prefer a local folder under the
     user profile over a OneDrive-redirected one** — OneDrive mirrors chug
     when later mounted as project folders; mention this if the user is
     about to pick a OneDrive path, but it is their call. Then persist
     the **host** path they picked:
     `location.save_mirror_root(anchor_mount, host_root)`.
   - **Tell the user where the settings file went.** After saving, say in
     plain language that a small settings file was written to their actual
     local user folder, with the literal path — e.g. *"Saved your folder
     choice to `C:\Users\<you>\Documents\_claude-config\.suralink-sync.json`
     — your shared Claude config folder, alongside other skills' configs."* Most users don't realise OneDrive's Known
     Folder Move has taken over their Documents/Desktop, so name the real
     location explicitly rather than just saying "your user folder".
   - Also mount `~/Downloads` (where Chrome drops files by default), no
     questions asked — it saves the inevitable "wait, where did the zip go?"
     round-trip. Do NOT ask the user "did you redirect Chrome?" — just mount it.
2. **Build the skeleton.** `location.ensure_structure(mirror_root)` (mirror_root
   = the mounted sandbox path of the resolved root).
3. **`suralink` skill** — confirm installed; add its `scripts/` to `sys.path`,
   `import suralink, browser`.
4. **Transport + Chrome tab** — the `suralink` skill's Step 0 already picked
   the transport (`chrome_bridge_status`: bridge preferred, linked tab
   fallback). Confirm a tab is logged into `app.suralink.com` — on the
   bridge find it with `chrome_list_tabs`; linked-tab, the linked tab itself.
5. **Staging.** Load the manifest. If `stagingDir` is unset OR points at the
   mirror's `_inbox` (the old default that requires the user to change
   Chrome's download location), set it to the **host path** of `~/Downloads`
   via `manifest.set_staging(m, host_downloads_path)`. The host path is what
   the user sees on their computer — the Windows path returned by
   `request_cowork_directory`, not a `/sessions/.../mnt/...` sandbox path.
   The runtime wait helper takes the sandbox path directly from the caller;
   the manifest just records what Chrome is configured to use.
6. **Active list.** `active.load(mirror_root)`. If empty, run
   `manage-active-clients.md` first.

## Changing the root (repoint) — WARN, then offer to move  ← REQUIRED

When the user wants to point the sync at a different folder, do NOT just
overwrite the pointer. The entire mirror — `catalog.json`,
`active-clients.json`, the `_suralink_sync.json` manifest, and every
`{Client}/{Year} Suralink Folder/` tree — lives **under the current root**.

1. **Warn, explicitly:** *"Heads up — the new folder starts empty. Your active
   client list, the catalog, the manifest of what's been pulled, and every
   downloaded file all live under the current folder. If I just repoint, the
   next sync sees an empty mirror and re-pulls every engagement from scratch —
   unless I move your existing files to the new folder first."*
2. **Offer to move the folders.** Ask: move everything to the new location, or
   start fresh there?
   - **Move (recommended):** launch the picker (no-path
     `request_cowork_directory`) for the **new** root and mount it; the **old**
     root is already mounted. Then:
     ```python
     res = location.migrate_root(old_mount, new_mount)   # cross-drive safe
     location.save_mirror_root(anchor_mount, new_host_path)
     location.ensure_structure(new_mount)
     ```
     Report `res["moved"]` / `res["skipped"]`. A name in `skipped` means it
     already existed at the destination — surface it; do not silently overwrite
     (pass `overwrite=True` only on the user's explicit OK).
   - **Start fresh:** only `save_mirror_root` + `ensure_structure` on the new
     root. Tell the user the old folder is untouched and the next sync will
     re-pull everything into the new one.
3. Continue the run against the new root.

## Procedure

### 1. Load state
```python
from scripts import manifest, sync, active, index, catalog, location
mirror_root = location.ensure_structure(mounted_path)
m   = manifest.load(mirror_root)
eng = active.load(mirror_root)        # [{auditId, clientId, client, label}, ...]
```
Make the `suralink` skill importable (`sys.path` + `import suralink, browser`).
`active.by_client(eng)` groups the run per client for reporting — when the user
named specific clients, sync only those entries.

### 2. Per engagement — refresh the index (freshness-gated)
For each engagement:
- Navigate the Chrome tab to
  `https://app.suralink.com/auditors/views/Audit.php?auditId={auditId}`.
  **The full `/auditors/views/` path is required** — a bare
  `https://app.suralink.com/Audit.php?…` returns nginx 404.
- Scrape the binder: `binder = json.loads(run(suralink.map_binder_js()))`.
- `eng_dir = sync.engagement_dir(mirror_root, client, label)`;
  `idx = index.load(eng_dir)`.
- If `index.is_stale(idx, binder)` (true also when there is no index yet):
  re-enumerate — for each request in `binder`, run
  `suralink.get_request_js(auditId, request_id)` **sequentially** (one fetch
  in flight at a time; `window.csrf` is read live per call and doesn't
  rotate on `getRequest` in practice — see `suralink` skill's `browser.py`).
  The whole sweep fits inside ONE `javascript_exec` using a for-loop with
  awaited fetches — faster than round-tripping per request. Then
  `browser.parse_result`, `suralink.extract_files(body, "client")`,
  `sync.normalize_file(...)`, and
  `idx = index.build(auditId, client, label, binder, {requestId: [recs]})`.
  If the result payload is larger than ~500 bytes: on the **bridge**,
  `chrome_eval(js, target=tabId, out_path=...)` writes it straight to disk —
  no ferry, no wait loop. **Linked-tab**, ferry it via the Blob helper rather
  than chunked JS reads: JS-side
  `suralink.dump_to_download_js("window.__myVar", "filename.json")` dumps
  to `~/Downloads`; Python-side `sync.wait_and_read_json(download_dir,
  "filename.json")` reads it. See the `suralink` skill's
  `architecture.md` "Getting large data out of the tab".
- Else: `index.touch_freshness(idx, binder)` — it is current, no crawl needed.
- `index.save(eng_dir, idx)`.

### 3. Diff — new files and deletions
```python
new_files = sync.diff_new_files(m, index.all_files(idx))
deleted   = sync.detect_deletions(m, auditId, index.fmsids(idx))
```

### 4. Confirm — and on a fresh full pull, offer the zip route first  ← REQUIRED
Show, per engagement: `new_files` as a table (request, filename, size) and
`deleted` as a list (these will be tombstoned, local copies kept). If both are
empty, report "nothing new" for that engagement and stop.

**Fresh full pull → always offer the bulk zip first.** If the engagement is
essentially unsynced (the manifest holds few/no files for it, so `new_files` is
its whole history), then *before* any per-file downloading, ask the user
whether they would rather do the **manual bulk-zip pull** — it is much faster,
even though it needs a few clicks in the Suralink UI. If **yes** → hand off to
`import-zip.md` (user clicks select-all → Download → Categories/Requests; Claude
imports and reconciles the zip) and skip step 5. If **no** → continue with the
per-file download in step 5. The bulk zip's UI clicking is a **sanctioned
exception** to this skill's backend-over-UI doctrine — on a fresh
whole-engagement pull, speed wins.

Get an explicit "yes" before any downloading begins.

Engagement folder naming — `sync.engagement_folder_name(label)` turns the
active-clients.json label into `{Year} Suralink Folder` (year pulled out of
the label; falls back to the sanitized label + suffix if no year is found).
Both `sync.engagement_dir` and `sync.plan_paths` route through it, so this
never needs to be computed by hand.

### 5. Download + file each approved new file
Decide **once per engagement, before the loop**, whether this is the seeding
pull — it controls whether new files seed `sorted/` or land in the
`sorted/_unsorted/` inbox (see `../architecture.md` "The sorted folder"):
```python
seeding = sync.is_seeding(mirror_root, client, label)   # True iff no sorted/ yet
```
Then for each approved file:
```python
js = suralink.download_file_js(rec["fId"], rec["auditId"],
                               rec["requestId"], rec["origFileName"])
staged = sync.wait_for_download(m["stagingDir"], rec["origFileName"])
raw_rel, sorted_rel = sync.plan_paths(client, label, rec["requestName"],
                                      rec["origFileName"], category=numbered_cat,
                                      seeding=seeding)
placed = sync.relocate(staged, mirror_root, raw_rel, sorted_rel)
manifest.record_file(m, rec["fmsId"], {**rec, "rawPath": placed["raw"]})
```
`numbered_cat` comes from `sync.numbered_category_folder` over
`sync.number_categories(idx["categories"])`. Verify `placed["bytes"]` ≈
`rec["fileSize"]`. Pull in modest batches. Do **not** recompute `seeding` inside
the loop — the first file creates `sorted/`, and the rest of the batch must
still be treated as part of the same seed.

### 6. Tombstone the deletions
```python
for fms_id, _rec in deleted:
    manifest.mark_deleted(m, fms_id)
```
Never delete the local file — the tombstone is the record. See
`../architecture.md` "Deleted files".

### 7. Finish
```python
manifest.stamp_sync(m)
manifest.save(mirror_root, m)
```
Report per engagement, grouped by client: new files pulled, total bytes,
deletions tombstoned, anything skipped. When the run was **not** a seeding pull,
tell the user the new files landed in `sorted/_unsorted/` for them to file.

## Known failure modes

- `401` on a portal call → Suralink session expired. Stop, ask the user to log
  in, re-run.
- `staged` is None → the download did not land where `wait_for_download` is
  watching. Confirm Chrome's actual download folder (usually `~/Downloads`)
  is mounted via `request_cowork_directory` and passed as the wait dir.
- `403` on a download → wrong `rId`; it must be the request id the file belongs
  to (the `suralink` skill's architecture, ID glossary).
- `getRequest` `Invalid Csrf Token` → rare; re-read `window.csrf` and retry
  the call. Running calls sequentially (one fetch at a time) is the standing
  rule regardless; CSRF rotation on `getRequest` itself has not been
  reproduced. See `suralink` skill's `browser.py:js_gateway` for the
  full picture.
- **Bulk-zip route extracts a truncated archive** → Claude polled the
  Downloads folder too eagerly. Cowork's mount caches file size and
  `.crdownload` presence, so a simple "filename present, no `.crdownload`,
  size stable" loop will false-positive a half-streamed zip. **The fix is
  `sync.wait_for_zip` with a `min_bytes_expected` floor** (it forces
  `os.sync()` each tick, validates the EOCD via `zipfile.ZipFile`, and
  requires N consecutive stable reads). See `import-zip.md` Step 1 for the
  full pattern. The Animal Protection NM Audit 2025 run saw the bug twice
  before this helper existed.

## Validated on

- (pending live validation of the multi-engagement / index / tombstone path)
