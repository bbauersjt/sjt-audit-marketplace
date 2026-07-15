---
name: suralink-sync
description: Keeps a local, organized folder in step with a Suralink auditor-portal engagement. Use when the user says "sync Suralink", "pull new files from Suralink", "update my local copy", "check Suralink for new uploads", "what's new in Suralink", "sync this folder", "sync <client>", or points at a folder (a mounted Cowork project folder, or an engagements/<client> folder) and wants its Suralink files kept current. Orchestration layer — it drives the `suralink` skill to read the portal and download files, then organizes them into the target folder and records everything in a small state file inside that folder. Depends on the `suralink` skill being installed.
---

# Suralink Sync — Dispatcher

Keeps a chosen **folder** in step with one Suralink engagement. It does not touch
the portal directly — it drives the **`suralink`** skill for that, and adds the
orchestration: figuring out which folder to sync, what is new, what was deleted,
where files go, and remembering all of it **inside the folder itself**.
**Requires the `suralink` skill** — if it is not installed, stop and tell the user.

## The model in one paragraph

**A "sync" is a folder.** Everything the skill needs to remember lives in one
self-describing state file (`_suralink_sync.json`) at the folder's root: which
Suralink engagement it mirrors, and every file already pulled. There is **no
global state** — no client list, no active-engagement list, no remembered mirror
root, and nothing client-specific shipped with the skill. You point the skill at
a folder (or name a client and it finds the folder); if the folder already holds
a sync it just **updates** it, and if not it **resolves the engagement live**
(one name-search against Suralink), writes the binding, and does the first pull.
That is what makes it clean in Cowork and clean to distribute.

## ⚠ REQUIRED FIRST STEP — load the `suralink` skill

**Before reading any module or writing any code, invoke the `suralink` skill.**
It owns every JS builder and browser helper this skill depends on (`suralink.py`,
`browser.py`, `map_binder_js`, `get_request_js`, `search_clients_js`,
`get_org_id_js`, `get_client_engagements_js`, `trigger_bulk_zip_js`,
`download_file_js`, …). Without it, portal navigation, client resolution and file
enumeration are impossible.

```
Skill("anthropic-skills:suralink")
```

Do this unconditionally on every run — even if you think you already have the
functions in context. Then proceed to the module routing below.

**Transport is inherited from the `suralink` skill and is BRIDGE-FIRST:** its
Step 0 makes `chrome_bridge_status` the first browser call of the session —
bridge up → bridge verbs (`chrome_list_tabs`, `chrome_eval`, `chrome_navigate`)
for the whole run; otherwise the linked Claude-in-Chrome tab as the fallback.
Never start with a linked-tab call before checking the bridge.

---

Route the request to ONE module below, read only that module, then call the
`scripts/*.py` functions it names.

## Modules — match the row, read that one file

| User wants to… | Module | Triggers |
|---|---|---|
| Pull new files / update a folder / first-time set up a sync / sync a named client | `references/modules/run-sync.md` | "sync Suralink", "sync this folder", "sync <client>", "pull new files", "update my copy", "what's new", "pull the history", first run |
| Download one group of files (a request, or a category) | `references/modules/download-group.md` | "download just this request", "pull the Payroll category" |
| First whole-engagement sync via one bulk zip | `references/modules/import-zip.md` | "initial sync", "import the Suralink zip", "bulk download" |

`run-sync.md` is the workhorse — first-time full backfill, adoption of an
existing `_raw/` folder, and every incremental run. On a fresh full pull it
offers the `import-zip.md` route first (the bulk zip is much faster; its UI
clicking is a sanctioned exception to backend-over-UI).

All three modules first resolve **which folder** and **which engagement** via
`references/modules/resolve-target.md` — the discovery (find the folder from a
client name), live one-time engagement resolution, and adoption logic live there,
not in each module. It is a shared sub-procedure, not a user-intent route.

## Where the pieces live

| Concept | Script |
|---|---|
| Per-sync state file (`_suralink_sync.json`) — engagement binding + files/tombstones; plus `find_syncs` discovery | `scripts/state.py` |
| Per-sync portal-state index (`_index.json`) + freshness | `scripts/index.py` |
| Diff, delete-detection, path planning (all relative to the sync folder), folder naming, group select, zip import, adoption scan | `scripts/sync.py` |
| Download-wait helpers — `wait_for_download` (single file), `wait_for_zip` (bulk-zip EOCD validation, mount-cache safe), `newest_zip_matching` | `scripts/sync.py` |

The full model — the folder-as-sync-unit, the state file, discovery, live
resolution, adoption, freshness, tombstones, and the `sorted/` seed-then-inbox
behaviour — is in `references/architecture.md`. Read it once.

## Five rules

1. **A sync is a folder; its memory lives inside it.** The target is whatever
   folder the user names (a mounted Cowork project folder, an `engagements/<client>`
   folder, or a `{Year} Suralink Folder` subfolder inside one). Its
   `_suralink_sync.json` holds the engagement binding + everything pulled. No
   global config, no remembered root, nothing to migrate. On a first pull into a
   project folder, the files go in a `{Year} Suralink Folder` subfolder
   (`sync.default_sync_folder`) so they never collide with the working files
   already there; `sync.engagement_folder_name` names it from the label.
2. **The state file is the truth for what is HELD.** It records every file pulled
   into this folder, keyed by `fmsId`. A file is "new" iff its `fmsId` is absent.
   Dedup is by `fmsId`, never by path.
3. **The index is the truth for what the PORTAL HOLDS.** `_index.json` snapshots
   the portal's file list, freshness-checked against a cheap `map_binder` scrape
   before every use. Index vs state = "what's new" and "what was deleted".
4. **`_raw/` is sacred; `sorted/` is the user's.** `_raw/` is a byte-for-byte
   chain-of-custody copy — never renamed, edited, or deleted. `sorted/` is the
   user's working copy: **seeded once** as an identical copy of `_raw/` on the
   first pull, then never written into again — every NEW file from a later sync
   lands in the **`sorted/_unsorted/`** inbox instead (portal layout preserved).
   This lets the user reshape `sorted/` freely without later syncs scattering new
   files across it. Portal-deleted files are **tombstoned** in the state file,
   never removed from disk. See `architecture.md` "The sorted folder".
5. **Resolve live, never from a stored list.** Client name → engagement is a live
   Suralink query (`get_org_id_js` → `search_clients_js` → `get_client_engagements_js`),
   done ONCE when a new folder is set up, then cached in that folder's binding.
   Never build, ship, or persist a firm-wide client roster — client names must not
   live in any file outside the engagement folder they belong to.
