# Module — Organize a Binder

**Triggers:** "organize", "file the unsorted", "sort the binder", "file what's
new", "organize this engagement", "organize these docs", "build the binder
sections", "file the _unsorted folder"

## What this does

Files audit documents into 4-digit indexed binder sections (see
`../architecture.md`). Reshapes `sorted/` in place; never touches `_raw/`.

## Phase 0 — mount and identify

1. **Mount the folder.** If no folder is mounted, `request_cowork_directory`.
   The user may point at a suralink-sync sync folder (an engagement folder with
   `_raw/` + `sorted/`), a project folder that contains one, or a loose pile of
   documents.
2. **Determine the mode** (`../architecture.md` "Three modes"):
   - **Mode A — sister.** The path is (or contains) a suralink-sync sync folder:
     `_raw/` + `sorted/` with a `_suralink_sync.json` at that folder's root (that
     folder IS the sync — suralink-sync keeps no separate mirror root). This is
     the normal case.
   - **Mode B — warn.** Suralink-shaped files, but no `_suralink_sync.json` and
     no `_raw/`. STOP. Tell the user the folder was not built by `suralink-sync`,
     so there is no chain-of-custody `_raw/` and traceability is degraded. Offer
     to hand off to `suralink-sync` to adopt the engagement first. Only continue
     if the user explicitly says so.
   - **Mode C — pile.** An arbitrary folder of documents. Tell the user
     `suralink-sync` cannot help here. Offer to first snapshot a `_raw/`
     canonical copy inside the folder, then build a `sorted/`. Get an explicit
     OK before copying anything.
3. **Pick the engagement.** In Mode A, if the mount is a parent folder that
   contains one or more sync folders (rather than a single sync folder itself),
   list them and ask which to organize (or do each in turn).

```python
import sys; sys.path.insert(0, "<skill>/scripts")
import taxonomy as T, organize as O, crosswalk as X
import json, os
tx = T.load()
```

## Phase 1 — engagement facts

4. **Client type.** `ct = T.resolve_client_type(tx, client_name)` is a guess
   from the name. **Show it to the user and confirm** — Standard vs EBP changes
   the whole section list.
5. **Single audit?** Ask the user (or infer from the engagement) whether this is
   a single audit. If yes, set `single_audit=True` — it adds the `8000 Single
   Audit` tack-on. Ask too whether they want the optional `8100/8200/8300`
   sub-buckets; default is the one flat `8000` folder.
6. **Fiscal year.** Needed only if the user wants the Perm File date split.
   `O.extract_year(engagement_label)` pulls it from a label like "Audit 2025".
   Confirm with the user.

## Phase 2 — build the work queue

7. **First organize vs later** — `X.is_first_organize(engagement_dir)`:
   - **First** (no `_organize.json`): the work queue is every file in the
     portal-layout body of `sorted/` (exclude `sorted/_unsorted/` if present).
   - **Later**: the work queue is every file under `sorted/_unsorted/` only.
     Files already in section folders are left alone.
8. For each file, gather **signals** — the folder names tell you most of it:
```python
signals = {"category": "<NN Category folder>",   # e.g. "03 Cash"
           "request":  "<Request folder name>",  # e.g. "Bank Reconciliation"
           "filename": "<file name>"}
```
   `category` and `request` come from the file's path within `_raw/` layout
   (`{NN Category}/{Request}/{file}`). If the folder names are thin, read the
   document for more signal and add it as `signals["extra"]`.

## Phase 3 — classify

9. For each file: `c = O.classify(tx, ct, signals, single_audit=...)` and
   `is_sample = O.is_sample(tx, signals)`.
   - `c["confident"] is True` → trust the keyword result.
   - `c["confident"] is False` → **Claude judges**. Look at `c["alternatives"]`,
     read the document if needed, decide. If still genuinely unclear, the file
     goes to `Other` — never guess a section. Ask the user on anything material.
10. **Perm File subfolders.** For each perm-bucket file, first try the ruled
    topical subfolders: `sub = O.perm_subfolder_for(tx, ct, signals)` (EBP files
    to `9100 Plan Documents` / `9200 Service Agreements` / `9300 SOC 1 Reports`
    per the EBP binder template; standard has no rules and always gets `None`).
    Only if that returned `None` AND the user asked for the date split in
    Phase 1: find the document's date — read the document or use
    `O.extract_year(filename)` as a fallback — then
    `sub = O.perm_split(tx, doc_year, fiscal_year)`. Neither applies → leave
    `perm_subfolder=None` (file sits at the `9000 Perm File` root).
11. Plan the destination:
```python
dest_parts = O.plan_destination(tx, c, sample_flag=is_sample,
                                perm_subfolder=sub)   # sub only for perm
# final folder = sorted/ + dest_parts ; filename is NEVER changed
```

## Phase 4 — show the plan, get approval  ← REQUIRED

12. Show the user a table: each file → its destination section (mark samples,
    mark `Other`, mark anything Claude had to judge). Note that section folders
    are created sparsely — only where files land.
13. Get an explicit "yes" before moving anything.

## Phase 5 — execute

14. Load the crosswalk and (Mode A) the manifest:
```python
xw = X.load(engagement_dir, engagement_label)
# Mode A: the sync state sits at the sync-folder root, which IS engagement_dir.
state = json.load(open(os.path.join(engagement_dir, "_suralink_sync.json")))
```
15. For each approved file:
```python
raw_abs = O.raw_counterpart(engagement_dir, file_abs)        # before the move
fms_id, _rec = X.fms_for_raw(state, raw_abs, engagement_dir) # Mode A; else None
dest_dir = os.path.join(engagement_dir, "sorted", *dest_parts)
final = O.move_into(file_abs, dest_dir)
X.record(xw, X.make_entry(
    organized_path=os.path.relpath(final, engagement_dir),
    raw_path=os.path.relpath(raw_abs, engagement_dir),
    orig_name=os.path.basename(file_abs), bucket=c["bucket"], index=c["index"],
    section="/".join(dest_parts), is_sample=is_sample,
    moved_from=os.path.relpath(file_abs, engagement_dir),
    client_type=ct, fms_id=fms_id))
```
   Filenames are kept exactly — only folders change.
16. `X.mark_organized(xw)`; `X.save(engagement_dir, xw)`.

## Phase 6 — prune and report

17. **Offer to prune** the now-empty `_unsorted/` folders:
    `O.prune_empty_dirs(os.path.join(engagement_dir, "sorted", "_unsorted"))`.
    Default offer is yes (empty folders + `_raw/` canon = zero risk), but the
    user decides.
18. **Report.** Per section: how many files filed. Call out the `Other` pile and
    anything Claude judged. And state plainly: *"Files you removed from
    `_unsorted/` before this run were not filed — they are still safe in
    `_raw/`, but ask me to pull them from `_raw/` if you want them in a
    section."*

## Known failure modes

- No `sorted/` folder → the engagement was never synced. Run `suralink-sync`
  first.
- A file in the queue is not under `_raw/` layout (already organized, or a Mode
  C pile) → `raw_counterpart` will be wrong; for already-organized files use the
  crosswalk, and skip them — they are not in the work queue.
- Client type guessed wrong → every section is off. Always confirm Phase 1.
- `Other` is large → the keyword rules in `taxonomy.json` need tuning for this
  client's request names; note it for the user.
