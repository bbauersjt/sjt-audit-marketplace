# Module — Resolve Target (which folder, which engagement)

**Not a user-intent module** — `run-sync.md`, `download-group.md` and
`import-zip.md` all call this first to answer two questions: **which folder is
the sync root**, and **which Suralink engagement does it mirror**. Read it when
setting up or locating a sync.

The whole point: no stored client list, no active-engagement list, no remembered
root. The folder carries its own identity; a brand-new folder resolves its
engagement live, once, and remembers it.

## Step 1 — find the sync root

Work from what the user gave you:

1. **User pointed at / named a folder** (a mounted Cowork folder, or a path) →
   that folder is the starting point. Mount it if needed
   (`request_cowork_directory`), then go to Step 2.
2. **User named a client** ("sync Example Client"), no folder → **discover**:
   ```python
   from scripts import state, sync
   ```
   - Scan the folders actually available this session for existing syncs:
     `state.find_syncs(folder)` on each mounted project folder (Cowork), and on
     `./engagements/<client>` if an `engagements/` folder exists relative to the
     session. `find_syncs` returns any dir holding a `_suralink_sync.json`, at
     the folder or one/two levels down (so a `{Year} Suralink Folder` subfolder
     is found).
   - Also look for a **folder whose name matches the client** even if it has no
     sync yet (e.g. `engagements/<client>/`) — a natural place for a new
     sync.
   - **Confirm with the user** what you found: an existing sync → "update this
     one?"; a matching folder without a sync → "set up a new sync in here?".
     Never sync or create silently.
3. **Nothing obvious found** → ask the user for the folder (offer the native
   `request_cowork_directory` picker, or take a path). Then Step 2.

Be responsive to what exists — most Cowork runs are just "look through the
mounted project folder," which is where `find_syncs` does the work.

## Step 2 — is this folder already a sync?

```python
st = state.load(sync_root)          # None if the folder is not a sync yet
```

- **`st` is not None** → the folder is a sync. Read its binding
  (`state.get_binding(st)`) — you now have `auditId` + the `auditUrl`. Confirm
  the folder with the user in passing ("updating the sync in `…/2025 Suralink
  Folder`") and hand back to the caller's pull loop. **Done — no resolution, no
  search.**
- **`st` is None but the folder already holds a `_raw/` tree** (an old-model pull,
  or files copied in) → **ADOPT it** (Step 4) instead of re-downloading.
- **`st` is None and the folder is empty/new** → resolve the engagement live
  (Step 3), create the sync root, write the binding (Step 5).

## Step 3 — resolve the engagement LIVE (new sync only)

One name-search against Suralink; nothing is read from any stored list.

```python
import suralink, browser   # from the suralink skill (already loaded)
org_id = browser.parse_result(run(suralink.get_org_id_js()))          # the firm org id
hits   = browser.parse_result(run(suralink.search_clients_js(org_id, term)))  # name-indexed search
```
1. **Pick the client.** `search_clients_js` returns scored hits (each `source` is
   the client object, incl. `engagementCounts`). One clear hit → confirm it.
   Several → show name + customId + counts and let the user choose. A client
   flagged `isSensitive` → surface that; do not proceed without an explicit OK.
   No hit → tell the user (misspelled? wrong firm login?) and stop.
2. **Pick the engagement.** For the chosen `clientId`:
   ```python
   eng = json.loads(run(suralink.get_client_engagements_js(client_id)))
   # eng["engagements"] = [{auditId, name, state, customId}, ...]
   ```
   Sibling audits (Audit 2024 / Audit 2025) come back as separate rows. Show them
   and let the user pick the one this folder is for. `name` is the label.

## Step 4 — ADOPT an existing `_raw/` folder (no re-download)

When a folder already has a `_raw/` tree but no state file (a pull from the
old, pre-folder-state model, or files dropped in):

1. Resolve the engagement (Step 3) so you have the binding.
2. Rebuild file records from disk: `records = sync.scan_raw_for_records(sync_root)`.
3. Enumerate the portal once (`map_binder` + `get_request` per request → normalized
   file records — see `run-sync.md` Step 2) to get `portal_files` with real fmsIds.
4. `matched, unmatched = sync.reconcile_to_fmsids(records, portal_files)`.
5. Write a fresh state file:
   ```python
   st = state.default_state()
   state.set_binding(st, org_id=org_id, client_id=client_id, client=client_name,
                     audit_id=audit_id, label=label)
   for rec, portal in matched:
       state.record_file(st, portal["fmsId"], {**portal, "rawPath": rec["rawPath"]})
   state.save(sync_root, st)
   ```
   Report any `unmatched` (on-disk files with no portal match — kept, just not
   fmsId-bound) so the user knows. The next run is then a normal incremental.

## Step 5 — create the sync root for a brand-new sync

- If the user pointed at a **dedicated / empty** folder they want to BE the sync,
  use it directly as `sync_root`.
- If the folder is a **project folder** with other working files (the common case,
  e.g. `engagements/<client>/`), put the pull in its own subfolder:
  `sync_root = sync.default_sync_folder(project_folder, label)` →
  `{project_folder}/{Year} Suralink Folder`. Confirm the location with the user.
- Write the binding, then hand to the caller's first-pull loop:
  ```python
  st = state.default_state()
  state.set_binding(st, org_id=org_id, client_id=client_id, client=client_name,
                    audit_id=audit_id, label=label)
  state.save(sync_root, st)
  ```

## Result

The caller (run-sync / download-group / import-zip) now has: `sync_root`, the
loaded/created `st`, and the binding (`auditId`, `auditUrl`). Everything from
here is folder-relative and identical whether the folder is under an engagements
tree, a mounted Cowork folder, or anywhere else.
