# Binder Organize — Architecture

The one place the organize model is documented. The module cites this; it does
not repeat it.

## What this skill is

`binder-organize` takes the files in a Suralink-sync mirror (or any folder of
audit documents) and files them into **4-digit indexed binder sections** that
match the firm's CCH Axcess binders. The point is simple: when you are working
cash, you open `1000 Cash & Equivalents` and everything the client gave you for
cash is sitting there.

It is the **sister skill to `suralink-sync`**. `suralink-sync` pulls files from
the portal and drops new arrivals into a `sorted/_unsorted/` inbox.
`binder-organize` is what files that inbox.

## The two folders it respects

This skill works inside a suralink-sync engagement folder:

```
{Client}/{Label}/
  _raw/        ← chain-of-custody original. binder-organize NEVER touches it.
  sorted/      ← the working copy. binder-organize reshapes THIS, in place.
    _unsorted/ ← the inbox of new arrivals. binder-organize's work queue.
  _index.json  ← suralink-sync's portal snapshot
  _organize.json ← this skill's crosswalk (see below)
```

`_raw/` is sacred — never read back, never moved, never edited. Every move this
skill makes happens inside `sorted/`. Because `_raw/` is the canonical copy,
moving files around in `sorted/` is always safe — nothing can be lost.

## The taxonomy is data

All section definitions, keyword rules, perm-file and samples handling live in
`references/taxonomy.json`, seeded from the `cch-axcess` skill's binder
templates. The skill ships its own copy — it does **not** read the `cch-axcess`
skill at runtime — so the firm can retune categories without touching either
skill. Edit `taxonomy.json`, not code.

Three index sets:
- **Standard** — commercial / nonprofit / government. One shared section list.
- **EBP** — employee benefit plans (401(k), 403(b), pension, H&W).
- **Single Audit** — a tack-on (`8000`) appended to either of the above when the
  engagement is a single audit.

## The work model — first organize vs later

The crosswalk file `_organize.json` is the flag:

- **First organize** (no `_organize.json` yet). The whole portal-layout body of
  `sorted/` is the work queue — suralink-sync seeded it as a copy of `_raw/`, so
  everything in it is unfiled. The skill reshapes `sorted/` from portal layout
  into indexed section folders.
- **Later organize** (`_organize.json` exists). Only `sorted/_unsorted/` is the
  work queue — the new arrivals since the last run. Files already filed into
  section folders are left exactly where the user put them.

Either way the destination is the same `sorted/` tree of indexed section folders.

## Sections, and the four special cases

**Regular sections.** A file is filed into `sorted/{NNNN Section}/` — e.g.
`sorted/1200 Receivables, net/`. Folder name is `index + name`. **Sparse**:
a section folder is created only when a file actually lands in it. A thin
engagement yields a thin binder.

**Planning is consolidated.** CCH's four planning-zone sections collapse to two:
`0200 Planning` (strategy, understanding, risk assessment, org charts —
everything planning) and `0400 Internal Controls` (control memos, walkthroughs).

**Perm File is a flat dump.** `9000 Perm File` gets every permanent-file
document with no sub-sorting — perm files are built differently for every
client. Optional (off by default, the user must ask): a date split into
`9000 Perm File/Carryforward` (documents dated before the engagement fiscal
year — what you should already have) and `9000 Perm File/New This Year`
(current FY or later). Undated documents stay at the `9000` root.

**Samples keep their flag.** A file flagged as a sample is filed into its real
substantive section, then dropped in a `Samples` subfolder —
`sorted/1200 Receivables, net/Samples/`. The sample status rides in the folder
structure, so it survives and the section context is never lost.

**The catch-all.** A document that fits no section goes to a non-indexed
`Other` folder. No number, so it sorts last. Better an honest `Other` than a
wrong section.

## The crosswalk — `_organize.json`

Every file the skill moves is recorded, pinning its new organized location back
to the untouched `_raw/` original and (in sister mode) to suralink-sync's
manifest `fmsId`. That chain is the traceability: the binder is reshaped and
re-foldered, but every file still traces to the exact sync that delivered it.
It also carries `firstOrganizeDone`, the first-vs-later flag. See
`scripts/crosswalk.py`.

## The inbox is the user's to clear

`binder-organize` does **not** auto-run after a sync. The user inspects
`sorted/_unsorted/` to see what is new at a glance, then asks the skill to
organize. The skill **moves** files out of `_unsorted/` (never copies — `_raw/`
is the canon, so moving is safe), which leaves empty folders behind. After
filing, the skill offers to prune those empty `_unsorted/` folders so next
sync's inbox reads clean. The user can decline.

A file the user deletes from `_unsorted/` before organizing is simply not
filed — it is still safe in `_raw/`, but it will not land in a section unless
the user asks the skill to pull it from `_raw/`. The skill says so on every run.

## Three modes

| Mode | Folder is… | Behaviour |
|---|---|---|
| **A — sister** | a suralink-sync mirror engagement (`_raw/` + `sorted/` + `_suralink_sync.json`) | The day job. Organize `sorted/`; link the crosswalk to the manifest `fmsId`. |
| **B — warn** | Suralink files, but no manifest / no `_raw/` | The folder did not come from suralink-sync — traceability is degraded. Warn the user; offer to hand off to `suralink-sync` to adopt the engagement and lay down a proper `_raw/` + manifest first. |
| **C — pile** | any folder of audit documents, nothing to do with Suralink | suralink-sync cannot help. Offer to snapshot a `_raw/` canonical copy first, then build a `sorted/` of indexed sections. Crosswalk is keyed by file hash instead of `fmsId`. |
