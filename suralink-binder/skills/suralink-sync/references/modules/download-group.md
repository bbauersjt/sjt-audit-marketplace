# Module — Download a Group of Files

**Triggers:** "download just this request", "pull the Payroll category",
"get all the files in category X", "download request 9's files",
"grab this one request"

## What this does

Downloads a **subset** of an engagement's files — one request, or one whole
category — into the mirror, filed and recorded exactly like a full sync. The
middle ground between one file and the whole engagement.

It runs off the engagement's `_index.json` (the portal-state snapshot), so it
first makes sure that index is fresh.

## Prerequisites

- Mirror mounted; the `suralink` skill importable; a Chrome tab on the
  engagement's
  `https://app.suralink.com/auditors/views/Audit.php?auditId={X}` (full
  `/auditors/views/` path is required — bare `Audit.php` returns nginx 404).
- The engagement is known (in `catalog.json` / `active-clients.json`), so its
  `client` and `label` are available for the folder layout.

## Procedure

### 1. Ensure the index is fresh
```python
from scripts import index, sync, manifest, catalog, location
import suralink, browser

eng_dir = sync.engagement_dir(mirror_root, client, label)
idx     = index.load(eng_dir)
binder  = json.loads(run(suralink.map_binder_js()))
if index.is_stale(idx, binder):
    # rebuild: getRequest per request, then index.build(...) — see run-sync.md step 2
    idx = rebuild_index(...)
    index.save(eng_dir, idx)
```

### 2. Select the group
```python
picked = sync.select_files(idx, request_id="91772322")     # one request, OR
picked = sync.select_files(idx, category="Payroll")        # one category, OR
picked = sync.select_files(idx, request_name="Payroll summary")
```

### 3. Diff against the manifest, confirm  ← REQUIRED
```python
m   = manifest.load(mirror_root)
new = sync.diff_new_files(m, picked)
```
Show the user the new files (request, filename, size). Get an explicit "yes".
If everything in the group is already held, say so and stop.

### 4. Download + file each approved file
Same as `run-sync.md` step 5: decide `seeding = sync.is_seeding(mirror_root,
client, label)` **once** before the loop, then per file
`suralink.download_file_js(...)`, `sync.wait_for_download`,
`sync.plan_paths(client, label, requestName, origFileName,
category=numbered_category, seeding=seeding)`, `sync.relocate`,
`manifest.record_file`. Then `manifest.stamp_sync` + `manifest.save`.

A group download is normally run on an already-synced engagement, so `seeding`
is usually False and the files land in the `sorted/_unsorted/` inbox — tell the
user that in the closing report. See `../architecture.md` "The sorted folder".

## Known failure modes

- Empty `picked` → the filter matched no request/category; check the name
  against `idx["categories"]` / the request list.
- A category spans many requests — confirm the file count with the user before
  a large pull.

## Validated on

- (pending live validation)
