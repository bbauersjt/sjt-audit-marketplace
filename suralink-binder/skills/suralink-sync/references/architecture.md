# Suralink Sync — Architecture (the sync model)

The one place the sync design is documented. Modules cite this; they do not repeat it.

## A sync is a folder

There is **no global state** — no remembered mirror root, no client roster, no
active-engagement list, and nothing client-specific shipped inside the skill. A
"sync" is just a **folder** that carries its own memory:

```
{sync root}/                         ← the folder the user points at (or one resolved
  _suralink_sync.json                  from a client name), or a {Year} Suralink Folder
  _index.json                          subfolder created inside a project folder
  _raw/                              ← exact portal copy. NEVER renamed or edited.
    {NN Category}/{Request name}/{origFileName}
  sorted/                            ← working view — seeded once, then yours to reshape
    {NN Category}/{Request name}/{origFileName}
    _unsorted/                       ← inbox: every NEW file from later syncs lands here
      {NN Category}/{Request name}/{origFileName}
```

Point the skill at the folder → if `_suralink_sync.json` is there, it knows what
the folder mirrors and what it holds, and just updates. If it's absent, the
folder isn't a sync yet: resolve the engagement live, write the state, pull.
Every machine, and Cowork, works the same way — the folder is self-contained and
portable. See `modules/resolve-target.md` for discovery / resolution / adoption.

## The two files inside a sync folder

| File | Kind | Holds | Script |
|---|---|---|---|
| `_suralink_sync.json` | state | the engagement **binding** + every file pulled here (keyed by `fmsId`, incl. tombstones) + staging/lastSync | `state.py` |
| `_index.json` | state | snapshot of what the PORTAL currently holds for this engagement | `index.py` |

The **binding** records what a name-search used to have to re-derive:
`{orgId, clientId, client, auditId, label, auditUrl}`. It is written once, when
the folder is first set up, and read on every later run — so resolution happens
exactly once per folder, never from a stored list.

**The sync-root folder name.** When a first pull goes into a project folder (the
common case, e.g. `engagements/<client>/`), the files go in a
`{Year} Suralink Folder` subfolder so they never collide with the working files
already there. `scripts/sync.py :: engagement_folder_name` builds the name — it
pulls a 4-digit year out of the label and appends " Suralink Folder"; no year in
the label (e.g. "NMBF FY25") → the sanitized label plus the same suffix.
`sync.default_sync_folder(project_folder, label)` returns that path. If the user
points directly at a dedicated/empty folder, that folder is the sync root as-is.
A client's several audits are just separate folders (`2024 Suralink Folder`,
`2025 Suralink Folder`) — they never collide, and each is its own sync.

`_raw/` is the **chain-of-custody original** — byte-for-byte what the portal
served, original filenames. It is never renamed, edited, moved, or deleted; it
is the audit evidence copy.

## The sorted folder

`sorted/` is the **user's working copy** — the folder the auditor actually works
out of and may reorganize, rename, or annotate freely. It is not a second
chain-of-custody copy; `_raw/` is the only evidence original.

It is built in two phases:

1. **Seed (first pull only).** On the first sync, `sorted/` is seeded as an
   identical copy of `_raw/` — same `{NN Category}/{Request}/` layout. This is
   why the two look the same to start.
2. **Inbox (every later sync).** After the seed, the skill **never writes into
   the body of `sorted/` again**. Every genuinely-new file from a later sync is
   dropped into **`sorted/_unsorted/`**, keeping the portal `{NN Category}/
   {Request}/` layout *inside* the inbox. So a new planning file lands at
   `sorted/_unsorted/02 Planning/{Request}/{file}`.

This is what lets the user (or the `binder-organize` sister skill) reshape the
body of `sorted/` into any structure without the next sync scattering new files
across the old layout — new arrivals are quarantined in `_unsorted/`, never
mixed into the reorganized files.

`sync.is_seeding(sync_root)` is the switch: it returns True iff the folder has no
`sorted/` yet. Compute it **once per run, before any download**, and pass the
result to every `plan_paths` call in that batch — a first run creates `sorted/`
partway through, but the whole batch must still be treated as a seed.

The skill never reads either folder back; `sorted/` and its `_unsorted/` inbox
are purely for the user. Clearing `_unsorted/` (by hand, or via the
`binder-organize` skill) is the user's call — nothing is lost, `_raw/` holds the
canonical copy. The cost is roughly double the disk — the price of an untouched
evidence copy.

**Numbered categories.** Suralink's category ids do not sort in display order,
so category folders are prefixed `01`, `02`, … in **website order** — from the
`suralink` skill's `list_categories_js()`, applied by `sync.number_categories`.

## Resolving a new sync — live, once, then remembered

The one thing a stored client list used to buy was turning a client **name** into
an `auditId` without navigating. That is a single live query now, run only when a
brand-new folder is set up:

- `get_org_id_js()` → the firm org id (from the logged-in session).
- `search_clients_js(org_id, term)` → a name-indexed search; pick the client.
- `get_client_engagements_js(clientId)` → the client's audits; pick the year.

The result is written into the folder's binding and never looked up again.
Nothing is cached firm-wide and nothing client-specific ships with the skill —
so no roster of client names ever lives in a distributed file. See
`modules/resolve-target.md`.

## The state file — `_suralink_sync.json`

State written by the machine: the binding, plus every file pulled into this
folder, keyed by `fmsId`. A file is **new** iff its `fmsId` is absent. A file
record:

```json
{"{fmsId}": {
  "fId": "...", "auditId": "9990001", "requestId": "9990006",
  "origFileName": "...", "fileSize": 96840, "fileType": "pdf",
  "requestName": "Payroll Summary", "side": "client",
  "portalTs": "2026-04-20 09:43:55", "pulledAt": "2026-05-22T14:03:00Z",
  "rawPath": "_raw/...",
  "deletedInPortal": true, "deletedDetectedAt": "2026-05-25T..Z"   ← tombstone
}}
```

`rawPath` is the `_raw/` location relative to the sync root. It does **not**
track where a file sits inside `sorted/`: the user (and `binder-organize`) move
files around in `sorted/` freely, so any `sorted/` path would go stale. Dedup is
by `fmsId`, never by path, so this costs nothing.

### Deleted files — tombstone, never delete

The portal has no per-file "deleted" flag; a deleted file simply **drops out** of
the request's file list (see the `suralink` skill's architecture). So deletion is
detected by **absence**: `sync.detect_deletions` diffs the state's file records
against the fresh portal `fmsId` set (from the index). One folder mirrors one
engagement, so every record belongs to it — no auditId filtering needed.

A file found missing is **tombstoned** — `deletedInPortal` + `deletedDetectedAt`
are set on its record (`state.mark_deleted`). The local copy in `_raw/` (and in
`sorted/`) is **never removed** — chain of custody; an auditor must not lose a
file a client later retracts. A tombstoned file stays "known", so if it reappears
under the same `fmsId` it is not blindly re-pulled (recording it again clears the
tombstone). Each sync run reports the tombstones it set.

## The index — `_index.json`

A parseable snapshot of what the **portal currently holds** for this engagement:
categories → requests → files (`fmsId`, `fId`, name, size, type, timestamp). It
is the reference list other operations run against — group downloads, the sync
diff, deletion detection — so they do not each re-crawl the portal.

**Freshness.** The index stores a `binderSignature` — a cheap fingerprint of the
`suralink` skill's `map_binder_js` output (per-request file / new-file counts).
Any operation that uses the index first re-scrapes `map_binder` (one DOM read —
free, no gateway call, no throttle) and calls `index.is_stale`. If the signature
moved, the index is rebuilt from a fresh `getRequest` enumeration; if not, it is
trusted as-is and its `checkedAt` is re-stamped. So the reference list is always
verified-current at the moment of use, without a full crawl every time. (The
`loadIAN` timeline is **not** used for this — it is unreliable and throttles; the
binder scrape is the freshness gate.)

## The sync run (idempotent)

Against ONE resolved sync folder (`resolve-target.md` supplies `sync_root`, `st`,
binding):
1. `suralink` skill: navigate the tab to the binding's `auditUrl` (the full
   `/auditors/views/Audit.php?auditId={X}` path), scrape `map_binder`.
2. If the index is stale (or absent), re-enumerate: `getRequest` per request →
   rebuild `_index.json`.
3. Diff the index `fmsId`s against the state → the **new-files** set.
4. `detect_deletions` → state files no longer in the index → **tombstone** set.
5. Show the user the new files (and any deletions) and get an explicit OK.
6. Decide `seeding = sync.is_seeding(sync_root)` ONCE. Download approved files via
   the `suralink` skill, file them into `_raw/` + `sorted/` — seeding True puts
   the sorted copy in `sorted/` proper; seeding False (every later sync) puts it
   in `sorted/_unsorted/`. Record each in the state.
7. Tombstone the deletions; stamp and save the state and the index.

Re-running only ever pulls genuinely new files — the state file makes it idempotent.

## History backfill

"Pull down history if it's not there" is just a sync run whose state holds few/no
records: the diff in step 3 marks every portal file as new, so the whole
back-catalogue is pulled. No separate mode — the same idempotent run does a first
full pull and every incremental pull after. A first pull is a seeding run (no
`sorted/` yet), so its files land in `sorted/` proper, not `_unsorted/`.

## Adopting an old-model folder

A folder that already holds a `_raw/` tree but no `_suralink_sync.json` (a pull
from the earlier mirror-root model, or files copied in) is **adopted** rather than
re-downloaded: resolve the engagement live, rebuild file records from disk with
`sync.scan_raw_for_records`, reconcile them to portal `fmsId`s with
`sync.reconcile_to_fmsids`, and write a fresh state file. The next run is then a
normal incremental. See `modules/resolve-target.md` Step 4.
