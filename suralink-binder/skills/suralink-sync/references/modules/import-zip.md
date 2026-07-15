# Module — Import Bulk Zip (fast initial sync)

**Triggers:** "initial sync", "first sync of an engagement", "import the
Suralink zip", "bulk download", "grab the whole engagement at once"

## What this does

For a first / whole-engagement sync, importing one bulk zip is faster than
pulling files one by one. Suralink hands the whole selection over as a single
zip; this module imports that zip into the **sync folder** (`sync_root`), with
numbered category folders, and reconciles the sync state.

`run-sync.md` is the general workhorse; on a **fresh full pull it offers this
zip route first**, because the bulk zip is much faster. It resolves the target
(`resolve-target.md`) and hands this module the `sync_root`, `st`, and binding.

## Step 0 — make sure Claude can SEE the zip  ← REQUIRED FIRST

`import_zip` reads the zip off disk, so the zip must sit in a folder Claude
has mounted. **Always call `request_cowork_directory` with `~/Downloads`
up front, no questions asked.** Chrome's default download location is the
user's Downloads folder; assume that's where the zip will land. Mounting
costs nothing on a re-run (the user approves once and Cowork remembers).
Do NOT ask the user "did you redirect Chrome's downloads?" — just mount
Downloads. Step 3 reads the zip from whichever mounted folder it landed in.

## Step 1 — trigger the bulk zip — CLAUDE DRIVES THE UI

The bulk-zip export is the **one sanctioned exception** to this skill family's
backend-over-UI doctrine. Its trigger could never be captured as a replayable
backend call — it evaded every fetch / XHR / form / anchor / iframe hook (see
the `suralink` skill's `architecture.md`). **"Cannot be scripted" does NOT mean
Claude cannot do it.** Claude operates the UI directly here — clicks the actual
buttons. This is the only place in the skill where Claude uses the interface
instead of a backend call; doing so is correct and expected, not a fallback.

With the tab on the engagement's
`https://app.suralink.com/auditors/views/Audit.php?auditId={X}` (full path —
bare `app.suralink.com/Audit.php` returns nginx 404), Claude fires the
whole select-all → Download → layout-pick sequence as a SINGLE call:

```python
run(suralink.trigger_bulk_zip_js("categories_requests"))
```

That helper handles the gotchas so a fresh model doesn't have to rediscover
them:

- Uses `multiSelectDownload(1)` (the global Suralink function), not a click
  on `#multiDownloadButton`, for the popup-open step.
- Clicks the **WRAPPER** div `#multiDownloadCategory_wrapper`, not the
  inner `#multiDownloadCategory_Btn` anchor. The click handler is bound on
  the wrapper; clicking the anchor silently closes the popup with no
  effect. The two other layout options are
  `#multiDownloadCategoryOnly_wrapper` and `#multiDownloadFolder_wrapper`
  — same pattern.
- Fires the click via jQuery so delegated handlers run.

Then Claude waits for the zip. Suralink builds it server-side, then Chrome
downloads it — total time is a minute or more for a 100+ MB engagement.

**DO NOT poll on "filename present + no `.crdownload` sibling".** Cowork's
mount caches directory metadata; a naive poll routinely sees a stale,
half-written size, no `.crdownload`, and false-positives a truncated zip
as complete.
**Use `sync.wait_for_zip` instead** — it forces `os.sync()` each tick,
validates the end-of-central-directory by calling `zipfile.ZipFile()`, and
requires the size to be stable for several consecutive checks. Truncated
zips raise `BadZipFile`; the helper keeps waiting.

```python
import time
from scripts import sync

t0 = time.time()
run(suralink.trigger_bulk_zip_js("categories_requests"))

# Wait for the FILENAME to appear (server build is 1-3 min). Use
# `since_mtime=t0` so a leftover zip from a prior failed run is ignored.
zp = None
for _ in range(60):
    zp = sync.newest_zip_matching(download_dir, "ShortClientName",
                                  since_mtime=t0)
    if zp:
        break
    time.sleep(5)
if not zp:
    raise RuntimeError("zip filename never appeared")

# Wait for the BYTES to actually finish. Set a CONSERVATIVE floor from the
# engagement's expected total (sum of fileSize across all client files in
# the index). Half the uncompressed total is a safe floor for the Suralink
# bulk zip's compression of PDFs / Office files.
expected = sum(int(f.get("fileSize") or 0) for f in index.all_files(idx))
zip_path = sync.wait_for_zip(zp, min_bytes_expected=expected // 2,
                             timeout=600)
if not zip_path:
    raise RuntimeError("zip never finished or never validated")
```

The filename pattern is `{Client}_{Audit}_..._{N}files_{jobId}.zip` — match
on a short client name and the `_files_` substring; the `jobId` varies per
run. The zip lands laid out `{Category}/{Request name}/{file}`.
(If the user would rather click it themselves they may — but Claude does
not need to wait on them to do it.)

## Step 2 — read the category order

Categories must be numbered in **website order**. With the tab on `Audit.php`:
```python
import suralink                       # the suralink skill's scripts
ordered = json.loads(run(suralink.list_categories_js()))   # category names, in order
```

## Step 3 — import the zip

Resolve the zip's path inside the folder connected in Step 0 (newest matching
`.zip`), then:
```python
from scripts import sync, state
seeding = sync.is_seeding(sync_root)   # True for a first pull
records = sync.import_zip(zip_path, sync_root, ordered, seeding=seeding)
```
`sync_root`, `st` and the binding come from `resolve-target.md` (via
`run-sync.md`). `import_zip` is **re-entrant** — files already at the right path
with the right uncompressed size are skipped, so a killed-mid-extract run (large
zip + bash timeout) is recovered by simply calling `import_zip` again with the
same arguments. The returned record list is correct either way.

If the original return value was lost (e.g. process killed before it could
serialize) and you don't want to re-run the extract, rebuild the record list
from disk:
```python
records = sync.scan_raw_for_records(sync_root)
```
Then proceed with reconciliation in Step 4 — the records have the same
shape `import_zip` returns (minus the `skipped` flag).

`import_zip` extracts every file to
`{sync_root}/_raw/{NN Category}/{Request}/{file}`. The `sorted/` copy follows
`seeding`: a first pull (the normal case) seeds `sorted/` proper; if the folder
already has a `sorted/` folder, the files land in `sorted/_unsorted/` instead
(see `../architecture.md` "The sorted folder").

## Step 4 — reconcile the state + build the index

`import_zip` records carry no `fmsId` (zip filenames omit it). To keep future
incremental syncs deduping correctly, enumerate the engagement and bind each
imported file to its portal `fmsId`:

- Enumerate every request: `map_binder_js` for the request list, then
  `get_request_js` per request → `extract_files(body, "client")`. The 40-odd
  gateway calls can run as **one sequential JS sweep** — await each, read
  `window.csrf` live per call, never in parallel (see the `suralink`
  architecture). A large result is best written to a file in the mounted
  download folder rather than returned through the tool channel.
- **Use `sync.reconcile_to_fmsids(records, portal_files)`** — it handles the
  matching correctly: greedy fmsId-uniqueness, tiebreak by sanitized request
  folder name, then size delta. Returns `(matched_pairs, unmatched_records)`.

  Why a helper instead of inline filename+size matching: two files in an
  engagement can share a filename AND size, which naive filename matching
  collapses both to one fmsId, leaving the state one entry short.
  `reconcile_to_fmsids` claims each fmsId at most once and uses the
  request-folder context to break ties.

  Note on request names: the **raw** portal `requestName` does NOT always
  byte-match the request folder Suralink writes into the zip. But after
  `safe_component()` sanitization (which both `import_zip` and the helper
  apply), they DO align — that's why `reconcile_to_fmsids` works.
- For each matched pair: `state.record_file(st, portal["fmsId"], {…, "rawPath": <matched _raw/ path>, …})`.
- Build the index from the same enumeration (`index.build(...)` →
  `index.save(sync_root, idx)`), so the next `run-sync.md` has a fresh reference
  list.
- `state.stamp_sync(st)`, `state.save(sync_root, st)`.

## Known failure modes

- **Claude cannot find / read the zip** → the download folder was not connected
  (Step 0). Connect `~/Downloads` and retry.
- **Truncated extract / "File is not a zip file" from `import_zip`** → almost
  always means Step 1's wait gave up early. The mount lies about file size and
  `.crdownload` presence. ALWAYS use `sync.wait_for_zip(zp,
  min_bytes_expected=...)` — never trust a single `ls` / `stat`. If you skipped
  the floor argument, set it. If you stopped polling because "no `.crdownload`
  and size looks stable", that's the bug.
- Zip not laid out `Category/Request/file` → a different structure option was
  picked in the popup. Re-download with **Categories / Requests**.
- A category in the zip is not in `ordered` → its folder is left un-numbered;
  re-scrape `list_categories_js` with the tab on the right audit.
- Reconciliation leaves files with no `fmsId` → the match was attempted on
  request name. Re-match on filename + size (Step 4).
- Bytes never reach Claude's context — `import_zip` reads the zip on disk.
