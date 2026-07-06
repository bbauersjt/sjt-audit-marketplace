---
name: binder-organize
description: Files audit documents into 4-digit indexed binder sections that match the firm's CCH Axcess binders - so when you work cash, everything for cash is in the 1000 folder. Use when the user says "organize the binder", "file the unsorted", "sort these docs", "organize this engagement", "file what's new", "build the binder sections", or wants a folder of audit files sorted into binder sections. Sister skill to suralink-sync - it files the sorted/_unsorted/ inbox that suralink-sync fills. Also organizes any loose pile of audit documents. Never touches the _raw/ chain-of-custody copy; only reshapes sorted/.
---

# Binder Organize — Dispatcher

Files audit documents into **4-digit indexed binder sections** matching the
firm's CCH Axcess binders. Sister skill to **`suralink-sync`**: that skill pulls
files from the Suralink portal and drops new arrivals into a `sorted/_unsorted/`
inbox; this skill files that inbox.

It reshapes `sorted/` **in place** and **never touches `_raw/`** — the
chain-of-custody original. Because `_raw/` holds the canonical copy, every move
in `sorted/` is safe.

## One module

| User wants to… | Module |
|---|---|
| Organize an engagement / file the `_unsorted/` inbox / sort a pile of docs | `references/modules/organize.md` |

Read that module, then call the `scripts/*.py` functions it names.

## Where the pieces live

| Concept | File |
|---|---|
| The taxonomy — section lists, keyword rules, perm/samples handling | `references/taxonomy.json` |
| Load + query the taxonomy; resolve client type | `scripts/taxonomy.py` |
| Classification engine; perm split; destination planning; file moves | `scripts/organize.py` |
| The crosswalk (`_organize.json`) — traceability back to `_raw/` / `fmsId` | `scripts/crosswalk.py` |

The organize model — the three modes, first-vs-later organize, the crosswalk,
perm-file and samples handling, the `Other` catch-all — is in
`references/architecture.md`. Read it once.

## Six rules

1. **`_raw/` is sacred.** Never read it back, move it, or edit it. Every move
   happens inside `sorted/`.
2. **Never rename files.** Only folders carry the index. A file keeps its
   original name — `_raw/` holds the true original regardless.
3. **The taxonomy is data.** Sections, keywords, perm and samples rules live in
   `references/taxonomy.json`, seeded from the `cch-axcess` binder templates.
   Retune that file; do not hard-code taxonomy in scripts.
4. **Folders are sparse.** A section folder is created only when a file lands in
   it. A thin engagement yields a thin binder.
5. **Never guess a section.** A file that fits nothing goes to the non-indexed
   `Other` folder. Confirm the plan with the user before moving anything.
6. **Traceability is mandatory.** Every move is recorded in `_organize.json`,
   pinning the new location back to `_raw/` and (sister mode) the `fmsId`.

## Depends on

The day-job mode (Mode A) expects a `suralink-sync` mirror. The skill also runs
standalone on any folder of audit documents (Mode C) — see `architecture.md`.
