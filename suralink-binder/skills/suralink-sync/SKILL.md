---
name: suralink-sync
description: Keeps a local, organized mirror of files from the Suralink auditor portal. Use when the user says "sync Suralink", "pull new files from Suralink", "update my local copy", "check Suralink for new uploads", "what's new in Suralink", "track this client", "refresh the client catalog", or wants a local folder kept in step with their Suralink engagements. Orchestration layer — it drives the `suralink` skill to read the portal and download files, then organizes them into a mirror folder and logs everything in a manifest. Depends on the `suralink` skill being installed.
---

# Suralink Sync — Dispatcher

Keeps a **local mirror** of chosen Suralink engagements. It does not touch the
portal directly — it drives the **`suralink`** skill for that, and adds the
orchestration: a client catalog, an active-engagement list, what is new, what
was deleted, where files go, and a manifest of everything held. **Requires the
`suralink` skill** — if it is not installed, stop and tell the user.

## ⚠ REQUIRED FIRST STEP — load the `suralink` skill

**Before reading any module or writing any code, invoke the `suralink` skill.**
The `suralink` skill owns every JS builder and browser helper this skill depends
on (`suralink.py`, `browser.py`, `map_binder_js`, `get_request_js`,
`trigger_bulk_zip_js`, `download_file_js`, etc.). Without it loaded, portal
navigation and file enumeration are impossible.

```
Skill("anthropic-skills:suralink")
```

Do this unconditionally on every run — even if you think you already have the
functions in context. Then proceed to the module routing below.

---

Route the request to ONE module below, read only that module, then call the
`scripts/*.py` functions it names.

## Modules — match the row, read that one file

| User wants to… | Module | Triggers |
|---|---|---|
| Pull new files / update the mirror / sync one or many clients | `references/modules/run-sync.md` | "sync Suralink", "pull new files", "update my copy", "what's new", "pull the history", first run |
| Add / remove which engagements are tracked | `references/modules/manage-active-clients.md` | "track this client", "add an engagement", "stop syncing X", "sync last year too" |
| Build / refresh / inspect the local client catalog | `references/modules/catalog.md` | "refresh the catalog", "list all clients", "find the client called X" |
| Download one group of files (a request, or a category) | `references/modules/download-group.md` | "download just this request", "pull the Payroll category" |
| First whole-engagement sync via one bulk zip | `references/modules/import-zip.md` | "initial sync", "import the Suralink zip", "bulk download" |

`run-sync.md` is the workhorse — first-time full backfill and every incremental
run. On a fresh full pull it offers the `import-zip.md` route first (the bulk
zip is much faster; its UI clicking is a sanctioned exception to backend-over-UI).

## Where the pieces live

| Concept | Script |
|---|---|
| Mirror location convention + bootstrap | `scripts/location.py` |
| Client catalog (`catalog.json`) — firm roster + engagements | `scripts/catalog.py` |
| Active-engagement list (`active-clients.json`) | `scripts/active.py` |
| Manifest (`_suralink_sync.json`) — file state + tombstones | `scripts/manifest.py` |
| Per-engagement portal-state index (`_index.json`) + freshness | `scripts/index.py` |
| Diff, delete-detection, path planning, group select, zip import | `scripts/sync.py` |
| Download-wait helpers — `wait_for_download` (single file), `wait_for_zip` (bulk-zip EOCD validation, mount-cache safe), `newest_zip_matching` | `scripts/sync.py` |

The sync model — the four local files, the `{Client}/{Label}/` layout, freshness,
tombstones, the `sorted/` seed-then-inbox behaviour — is in
`references/architecture.md`. Read it once.

## Five rules

1. **No hard-coded paths — the root is the user's choice, remembered.** On first run the user picks any folder as the mirror root (a native `request_cowork_directory` picker; remote-session fallback is the local profile root); the choice is saved to a pointer file at `~/Documents/_claude-config/.suralink-sync.json` and reused on every later run. The pointer is anchored at `~/Documents/_claude-config` (the shared per-user Claude config folder), NOT the profile ROOT (`~`) — in Cowork the profile root is NOT mountable (it holds Claude's own session storage and `request_cowork_directory` refuses it), whereas `~/Documents` always mounts. On a fresh machine the `_claude-config` subfolder may not exist yet; mount `~/Documents` (always present) and create it. All of this user's skill configs live in `_claude-config` together. The pointer lives OUTSIDE the skill dir (which is read-only at runtime and git-managed), so skill updates never touch it. If a saved root exists, use it and just mention it once ("files saved to X — to change the target directory, just ask") — no prompt; the user can ask to repoint it any time. **Repointing warns first and offers to move the mirror** (`location.migrate_root`): the catalog, active list, manifest and files live under the old root, so a bare repoint re-bootstraps empty and re-pulls everything. See run-sync.md "Changing the root". Each machine keeps its own pointer + its own independent mirror, catalog, manifest and active list; first run auto-creates everything. See `scripts/location.py`. Engagement folders are named `{Label} Suralink Files` (e.g. `Audit 2025 Suralink Files`).
2. **The manifest is the truth for what is HELD.** It records every file pulled on this machine, keyed by `fmsId`. A file is "new" iff its `fmsId` is absent. Dedup is by `fmsId`, never by path.
3. **The per-engagement index is the truth for what the PORTAL HOLDS.** `_index.json` snapshots the portal's file list, freshness-checked against a cheap `map_binder` scrape before every use. Index vs manifest = "what's new" and "what was deleted".
4. **`_raw/` is sacred; `sorted/` is the user's.** `_raw/` is a byte-for-byte chain-of-custody copy — never renamed, edited, or deleted. `sorted/` is the user's working copy: **seeded once** as an identical copy of `_raw/` on the first pull, then never written into again — every NEW file from a later sync lands in the **`sorted/_unsorted/`** inbox instead (portal layout preserved inside it). This lets the user reshape `sorted/` freely without later syncs scattering new files across it. Portal-deleted files are **tombstoned** in the manifest, never removed from disk. See `architecture.md` "The sorted folder".
5. **Config vs state.** `catalog.json` + `active-clients.json` are config; `_suralink_sync.json` + `_index.json` are state. Keep them distinct.

## Track engagements, not clients

The active list is keyed by `auditId` — one entry per engagement. A client's
prior-year and current-year audits are sibling entries sharing a `clientId`;
both can be active and synced together.
