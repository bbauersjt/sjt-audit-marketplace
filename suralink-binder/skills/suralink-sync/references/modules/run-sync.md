# Module — Run Sync

**Triggers:** "sync Suralink", "sync this folder", "sync <client>", "pull new
files", "update my local copy", "check for new uploads", "what's new in
Suralink", "pull down the history", "set up the sync"

## What this does

One idempotent pass over a **single sync folder**: refresh its portal snapshot
(`_index.json`), find files not yet in the folder, find files deleted in the
portal, get the user's OK, download the new ones, tombstone the deleted ones.
Re-running only ever pulls genuinely-new files. A first pull into a new folder
pulls the whole history — same pass, no special mode.

The folder carries its own identity and memory (`_suralink_sync.json`). There is
no active-engagement list to iterate — you sync the folder the user points at, or
the one you resolve from a client name (see `resolve-target.md`). Batch "sync
everything" is intentionally not a feature.

## Setup — every run

1. **Load the `suralink` skill** (SKILL.md required first step) and confirm the
   transport (its Step 0: bridge preferred, linked tab fallback). Confirm a tab
   is logged into `app.suralink.com`.
2. **Resolve the target** — follow `resolve-target.md`. It returns:
   - `sync_root` — the folder this sync lives in (mounted),
   - `st` — the loaded (existing) or freshly-created state,
   - the binding (`auditId`, `auditUrl`, client, label).
   That module handles discovery ("sync Example Client" → find the folder),
   first-time live resolution, and adoption of an existing `_raw/` folder. Do not
   duplicate it here.
   ```python
   from scripts import state, sync, index
   import suralink, browser        # from the suralink skill
   binding = state.get_binding(st)
   ```
3. **Staging.** If `st["stagingDir"]` is unset, set it to the **host path** of
   `~/Downloads` (where Chrome drops files) via
   `state.set_staging(st, host_downloads_path)`. Also mount `~/Downloads` so the
   wait helpers can see the file — no need to ask the user "did you redirect
   Chrome?". The host path is what the user sees on their computer, not a
   `/sessions/.../mnt/...` sandbox path; the runtime wait helper takes the sandbox
   path directly from the caller.

## Procedure

### 1. Refresh the index (freshness-gated)
- Navigate the Chrome tab to `binding["auditUrl"]` (the full
  `https://app.suralink.com/auditors/views/Audit.php?auditId={auditId}` — **the
  `/auditors/views/` path is required**; a bare `Audit.php?…` returns nginx 404).
- Scrape the binder: `binder = json.loads(run(suralink.map_binder_js()))`.
- `idx = index.load(sync_root)`.
- If `index.is_stale(idx, binder)` (true also when there is no index yet):
  re-enumerate — for each request in `binder`, run
  `suralink.get_request_js(auditId, request_id)` **sequentially** (one fetch in
  flight; `window.csrf` is read live per call). The whole sweep fits in ONE
  `javascript_exec` using a for-loop with awaited fetches. Then
  `browser.parse_result`, `suralink.extract_files(body, "client")`,
  `sync.normalize_file(...)`, and
  `idx = index.build(auditId, binding["client"], binding["label"], binder, {requestId: [recs]})`.
  If a result payload is larger than ~500 bytes: on the **bridge**,
  `chrome_eval(js, target=tabId, out_path=...)` writes it straight to disk;
  **linked-tab**, ferry via the Blob helper —
  `suralink.dump_to_download_js("window.__myVar", "filename.json")` then
  `sync.wait_and_read_json(download_dir, "filename.json")`.
- Else `index.touch_freshness(idx, binder)` — current, no crawl.
- `index.save(sync_root, idx)`.

### 2. Diff — new files and deletions
```python
new_files = sync.diff_new_files(st, index.all_files(idx))
deleted   = sync.detect_deletions(st, index.fmsids(idx))
```

### 3. Confirm — and on a fresh full pull, offer the zip route first  ← REQUIRED
Show: `new_files` as a table (request, filename, size) and `deleted` as a list
(these will be tombstoned, local copies kept). Both empty → report "nothing new"
and stop.

**Fresh full pull → always offer the bulk zip first.** If the sync holds few/no
files (so `new_files` is essentially the whole history), then *before* any
per-file downloading, ask whether to do the **manual bulk-zip pull** — much
faster, at the cost of a few UI clicks. Yes → hand off to `import-zip.md` (passing
`sync_root`) and skip Step 4. No → per-file download in Step 4. The bulk zip's UI
clicking is a **sanctioned exception** to backend-over-UI on a fresh whole-folder
pull.

Get an explicit "yes" before any downloading begins.

### 4. Download + file each approved new file
Decide **once, before the loop**, whether this is the seeding pull — it controls
whether new files seed `sorted/` or land in `sorted/_unsorted/` (see
`../architecture.md` "The sorted folder"):
```python
seeding = sync.is_seeding(sync_root)   # True iff no sorted/ yet
```
Then for each approved file:
```python
js = suralink.download_file_js(rec["fId"], rec["auditId"],
                               rec["requestId"], rec["origFileName"])
staged = sync.wait_for_download(st["stagingDir"], rec["origFileName"])
raw_rel, sorted_rel = sync.plan_paths(rec["requestName"], rec["origFileName"],
                                      category=numbered_cat, seeding=seeding)
placed = sync.relocate(staged, sync_root, raw_rel, sorted_rel)
state.record_file(st, rec["fmsId"], {**rec, "rawPath": placed["raw"]})
```
`numbered_cat` comes from `sync.numbered_category_folder` over
`sync.number_categories(idx["categories"])`. Verify `placed["bytes"]` ≈
`rec["fileSize"]`. Pull in modest batches. Do **not** recompute `seeding` inside
the loop — the first file creates `sorted/`, and the rest of the batch must still
be treated as part of the same seed.

### 5. Tombstone the deletions
```python
for fms_id, _rec in deleted:
    state.mark_deleted(st, fms_id)
```
Never delete the local file — the tombstone is the record.

### 6. Finish
```python
state.stamp_sync(st)
state.save(sync_root, st)
```
Report: new files pulled, total bytes, deletions tombstoned, anything skipped.
When the run was **not** a seeding pull, tell the user the new files landed in
`sorted/_unsorted/` for them to file.

## Known failure modes

- `401` on a portal call → Suralink session expired. Stop, ask the user to log
  in, re-run.
- `staged` is None → the download did not land where `wait_for_download` is
  watching. Confirm Chrome's actual download folder (usually `~/Downloads`) is
  mounted and passed as the wait dir.
- `403` on a download → wrong `rId`; it must be the request id the file belongs
  to (the `suralink` skill's ID glossary).
- `getRequest` `Invalid Csrf Token` → rare; re-read `window.csrf` and retry.
  Running calls sequentially (one fetch at a time) is the standing rule.
- **Bulk-zip route extracts a truncated archive** → Claude polled Downloads too
  eagerly; Cowork's mount caches size/`.crdownload`. Use `sync.wait_for_zip` with
  a `min_bytes_expected` floor (forces `os.sync()`, validates the EOCD, requires
  N stable reads). See `import-zip.md` Step 1.
