# Module — Download a Group of Files

**Triggers:** "download just this request", "pull the Payroll category",
"get all the files in category X", "download request 9's files",
"grab this one request"

## What this does

Downloads a **subset** of a sync's files — one request, or one whole category —
into the sync folder, filed and recorded exactly like a full sync. The middle
ground between one file and the whole engagement.

It runs off the sync's `_index.json` (the portal-state snapshot), so it first
makes sure that index is fresh.

## Prerequisites

- The `suralink` skill loaded; the transport chosen (bridge / linked tab).
- The target resolved via `resolve-target.md` → `sync_root`, `st`, and the
  binding (so `auditUrl` and the folder are known). A Chrome tab on the
  binding's `auditUrl` (full `/auditors/views/Audit.php?auditId={X}` path).

## Procedure

### 1. Ensure the index is fresh
```python
from scripts import index, sync, state
import suralink, browser

binding = state.get_binding(st)
idx     = index.load(sync_root)
binder  = json.loads(run(suralink.map_binder_js()))
if index.is_stale(idx, binder):
    # rebuild: getRequest per request, then index.build(...) — see run-sync.md step 1
    idx = rebuild_index(...)
    index.save(sync_root, idx)
```

### 2. Select the group
```python
picked = sync.select_files(idx, request_id="91772322")     # one request, OR
picked = sync.select_files(idx, category="Payroll")        # one category, OR
picked = sync.select_files(idx, request_name="Payroll summary")
```

### 3. Diff against the sync state, confirm  ← REQUIRED
```python
new = sync.diff_new_files(st, picked)
```
Show the user the new files (request, filename, size). Get an explicit "yes".
If everything in the group is already held, say so and stop.

### 4. Download + file each approved file
Same as `run-sync.md` Step 4: decide `seeding = sync.is_seeding(sync_root)`
**once** before the loop, then per file `suralink.download_file_js(...)`,
`sync.wait_for_download`, `sync.plan_paths(requestName, origFileName,
category=numbered_category, seeding=seeding)`,
`sync.relocate(staged, sync_root, raw_rel, sorted_rel)`, `state.record_file`.
Then `state.stamp_sync(st)` + `state.save(sync_root, st)`.

A group download is normally run on an already-synced folder, so `seeding` is
usually False and the files land in the `sorted/_unsorted/` inbox — tell the user
that in the closing report. See `../architecture.md` "The sorted folder".

## Known failure modes

- Empty `picked` → the filter matched no request/category; check the name
  against `idx["categories"]` / the request list.
- A category spans many requests — confirm the file count with the user before
  a large pull.
