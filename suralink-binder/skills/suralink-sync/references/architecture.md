# Suralink Sync — Architecture (the sync model)

The one place the sync design is documented. Modules cite this; they do not repeat it.

## Location & portability — the user picks the root, the skill remembers it

The skill never hard-codes the mirror path. On **first run** the user chooses
any folder as the root via a native `request_cowork_directory` picker. That
choice is saved to a small **pointer file** anchored at the Windows
user-profile root (`~`), NOT `~/Documents` — the latter is OneDrive-redirected
under Known Folder Move:

```
~/.suralink-sync.json     →   {"mirrorRoot": "<host path the user picked>"}
```

On every later run the skill reads the pointer (`location.saved_mirror_root`)
and reuses the root without asking — it just mentions which folder it's using,
and the user can ask to repoint it any time (`location.save_mirror_root`).

**Why the pointer lives in `~/Documents`, not in the skill folder.** The skill
directory is mounted **read-only at runtime** and is git-managed — a config file
inside it would be both unwritable when the skill runs and liable to be
clobbered on the next `git pull` of the skill. The pointer sits outside the repo
entirely, so skill updates can never touch it. `~/Documents` is the anchor
because it reliably exists and `request_cowork_directory` auto-mounts an existing
path without a picker. The root the pointer names can be anywhere (another
drive, a synced projects folder); only the breadcrumb is anchored.

There is deliberately **no fixed "Suralink Mirror" folder name** any more — the
root is whatever the user selected, and the engagement folders inside are
self-describing (`{Label} Suralink Files`).

The same `.skill` works on every computer: each machine has its own pointer and
its own independent mirror, catalog, manifest and active-client list — they
never share state. First run on any machine **auto-creates** the structure under
the chosen root (`location.ensure_structure`).

## The four local files at the mirror root

| File | Kind | Holds | Script |
|---|---|---|---|
| `catalog.json` | config (cacheable) | the WHOLE firm — every client, engagements filled in lazily | `catalog.py` |
| `active-clients.json` | config (editable) | the SUBSET of engagements this machine syncs | `active.py` |
| `_suralink_sync.json` | state (machine-written) | every file ever pulled here, keyed by `fmsId`, incl. tombstones | `manifest.py` |
| `{Client}/{Label} Suralink Files/_index.json` | state (per engagement) | snapshot of what the PORTAL currently holds | `index.py` |

Rule of thumb: **catalog + active = config; manifest + index = state.** Config
is what you intend; state is what is true.

## The mirror folder layout

```
{user-chosen root}/                ← the folder the user picked (pointer-remembered)
  catalog.json                 ← the firm roster (clients → engagements)
  active-clients.json          ← which engagements this machine syncs
  _suralink_sync.json          ← the manifest (file state + tombstones)
  _inbox/                      ← legacy staging dir; current default is ~/Downloads
  {Client Name}/
    {Engagement label} Suralink Files/   ← one folder per engagement — e.g. "Audit 2025 Suralink Files"
      _index.json              ← portal-state snapshot for this engagement
      _raw/                    ← exact portal copy. NEVER renamed or edited.
        {NN Category}/{Request name}/{origFileName}
      sorted/                  ← working view — seeded once, then yours to reshape
        {NN Category}/{Request name}/{origFileName}
        _unsorted/             ← inbox: every NEW file from later syncs lands here
          {NN Category}/{Request name}/{origFileName}
```

**The engagement level matters.** A client can have several audits in tow at
once (last year + this year). Each engagement gets its own
`{Client}/{Label} Suralink Files/` tree, so `Audit 2024 Suralink Files` and
`Audit 2025 Suralink Files` never collide. The ` Suralink Files` suffix is added
by `scripts/sync.py :: engagement_folder_name`, which both `plan_paths` and
`engagement_dir` route through.

`_raw/` is the **chain-of-custody original** — byte-for-byte what the portal
served, original filenames. It is never renamed, edited, moved, or deleted; it
is the audit evidence copy.

## The sorted folder

`sorted/` is the **user's working copy** — the folder the auditor actually works
out of and may reorganize, rename, or annotate freely. It is not a second
chain-of-custody copy; `_raw/` is the only evidence original.

It is built in two phases:

1. **Seed (first pull only).** On an engagement's first sync, `sorted/` is
   seeded as an identical copy of `_raw/` — same `{NN Category}/{Request}/`
   layout. This is why the two look the same to start.
2. **Inbox (every later sync).** After the seed, the skill **never writes into
   the body of `sorted/` again**. Every genuinely-new file from a later sync is
   dropped into **`sorted/_unsorted/`**, keeping the portal `{NN Category}/
   {Request}/` layout *inside* the inbox. So a new planning file lands at
   `sorted/_unsorted/02 Planning/{Request}/{file}`.

This is what lets the user (or the `binder-organize` sister skill) reshape the
body of `sorted/` into any structure without the next sync scattering new files
across the old layout — new arrivals are quarantined in `_unsorted/`, never
mixed into the reorganized files.

`sync.is_seeding(mirror_root, client, label)` is the switch: it returns True iff
the engagement has no `sorted/` folder yet. Compute it **once per engagement,
before any download**, and pass the result to every `plan_paths` call in that
batch — a first run creates `sorted/` partway through, but the whole batch must
still be treated as a seed.

The skill never reads either folder back; `sorted/` and its `_unsorted/` inbox
are purely for the user. Clearing `_unsorted/` (by hand, or via the
`binder-organize` skill) is the user's call — nothing is lost, `_raw/` holds the
canonical copy. The cost is roughly double the disk — the price of an untouched
evidence copy.

**Numbered categories.** Suralink's category ids do not sort in display order,
so category folders are prefixed `01`, `02`, … in **website order** — from the
`suralink` skill's `list_categories_js()`, applied by `sync.number_categories`.

## catalog.json — the firm roster

A parseable local copy of the firm's clients and their engagements. Two tiers:

- The **client roster** (clientId, customId, name, state) — cheap to build
  (a few paged `/v2/.../clients` calls), always fully populated.
- Per-client **engagements** (auditId, label, state) — populated **lazily**,
  the first time a client is touched (one `getClientInfo` gateway call), and
  cached with an `engagementsFetchedAt` timestamp. Populating engagements for
  all ~hundreds of clients up front would be hundreds of gateway calls.

The catalog is what client **names** resolve against. When the user says "sync
Kymera" or "track this client", `catalog.find_clients` turns the name into a
`clientId`; `getClientInfo` (cached into the catalog) turns that into auditIds.
If a name cannot be resolved, refresh the catalog and retry — see
`modules/catalog.md` and `manage-active-clients.md`.

## active-clients.json — the editable sync list

One entry per **engagement** (keyed by `auditId`), each carrying its
`clientId`, `client` name and `label`:

```json
{"engagements": [
  {"auditId": "2774111", "clientId": "1126793",
   "client": "Kymera Independent Physicians 401(k) Plan", "label": "Audit 2025"},
  {"auditId": "2245615", "clientId": "1126793",
   "client": "Kymera Independent Physicians 401(k) Plan", "label": "Audit 2024"}
]}
```

Because it is engagement-keyed, the same client's prior-year and current-year
audits are simply two entries that share a `clientId` — both can be active and
synced together. `active.by_client()` groups them for display. Plain and
human-editable; managed via `scripts/active.py`.

## The manifest — `_suralink_sync.json`

Machine-written **state** — every file ever pulled on this computer, keyed by
`fmsId`. A file is **new** iff its `fmsId` is absent. A file record:

```json
{"{fmsId}": {
  "fId": "...", "auditId": "2774111", "requestId": "93605893",
  "origFileName": "...", "fileSize": 96840, "fileType": "pdf",
  "requestName": "Payroll Summary", "side": "client",
  "portalTs": "2026-04-20 09:43:55", "pulledAt": "2026-05-22T14:03:00Z",
  "rawPath": ".../_raw/...",
  "deletedInPortal": true, "deletedDetectedAt": "2026-05-25T..Z"   ← tombstone
}}
```

The manifest records `rawPath` — the canonical `_raw/` location. It does **not**
track where a file sits inside `sorted/`: the user (and the `binder-organize`
skill) move files around in `sorted/` freely, so any `sorted/` path would go
stale. Dedup is by `fmsId`, never by path, so this costs nothing.

### Deleted files — tombstone, never delete

The portal has no per-file "deleted" flag; a deleted file simply **drops out**
of the request's file list (see the `suralink` skill's architecture). So
deletion is detected by **absence**: `sync.detect_deletions` diffs the manifest
records for an engagement against the fresh portal `fmsId` set (from the
engagement index).

A file found missing is **tombstoned** — `deletedInPortal` + `deletedDetectedAt`
are set on its manifest record (`manifest.mark_deleted`). The local copy in
`_raw/` (and in `sorted/`) is **never removed** — chain of custody; an auditor
must not lose a file a client later retracts. A tombstoned file stays "known",
so if it reappears under the same `fmsId` it is not blindly re-pulled (recording
it again clears the tombstone). Each sync run reports the tombstones it set.

## The per-engagement index — `_index.json`

A parseable snapshot of what the **portal currently holds** for one engagement:
categories → requests → files (`fmsId`, `fId`, name, size, type, timestamp).
It is the reference list other operations run against — group downloads, the
sync diff, deletion detection — so they do not each re-crawl the portal.

**Freshness.** The index stores a `binderSignature` — a cheap fingerprint of
the `suralink` skill's `map_binder_js` output (per-request file / new-file
counts). Any operation that uses the index first re-scrapes `map_binder` (one
DOM read — free, no gateway call, no throttle) and calls `index.is_stale`. If
the signature moved, the index is rebuilt from a fresh `getRequest`
enumeration; if not, it is trusted as-is and its `checkedAt` is re-stamped. So
the reference list is always verified-current at the moment of use, without a
full crawl every time. (The `loadIAN` timeline is **not** used for this — it is
unreliable and throttles; the binder scrape is the freshness gate.)

## The sync run (idempotent)

For each engagement in `active-clients.json`:
1. `suralink` skill: navigate the tab to
   `https://app.suralink.com/auditors/views/Audit.php?auditId={X}` (full path),
   scrape `map_binder`.
2. If the engagement index is stale (or absent), re-enumerate: `getRequest` per
   request → rebuild `_index.json`.
3. Diff the index `fmsId`s against the manifest → the **new-files** set.
4. `detect_deletions` → manifest files no longer in the index → **tombstone** set.
5. Show the user the new files (and any deletions) and get an explicit OK.
6. Decide `seeding = sync.is_seeding(mirror_root, client, label)` ONCE for the
   engagement. Download approved files via the `suralink` skill, file them into
   `_raw/` + `sorted/` — seeding True puts the sorted copy in `sorted/` proper;
   seeding False (every later sync) puts it in `sorted/_unsorted/`. Record each
   in the manifest.
7. Tombstone the deletions; stamp and save the manifest and the index.

Re-running only ever pulls genuinely new files — the manifest makes it idempotent.

## History backfill

"Pull down history if it's not there" is just a sync run against an engagement
whose manifest has few/no records for it: the diff in step 3 marks every portal
file as new, so the whole back-catalogue is pulled. No separate mode — the same
idempotent run does a first full pull and every incremental pull after. A
backfill on a never-synced engagement is a seeding run (no `sorted/` yet), so
its files land in `sorted/` proper, not `_unsorted/`.
