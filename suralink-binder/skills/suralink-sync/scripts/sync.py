"""Diff, path-planning, delete-detection and zip-import helpers for a sync run.

Pure functions + filesystem copies. The browser work (enumerate, download) is
done by the `suralink` skill; this module decides WHAT is new, WHAT was
deleted, and WHERE files go. See ../references/architecture.md.

A "sync" is a FOLDER (the "sync root"). Everything for one engagement lives
inside it, all paths below are relative to it:
    {sync_root}/_suralink_sync.json                                  (state.py)
    {sync_root}/_index.json                                          (index.py)
    {sync_root}/_raw/{NN Category}/{Request}/{file}
    {sync_root}/sorted/{NN Category}/{Request}/{file}
    {sync_root}/sorted/_unsorted/{NN Category}/{Request}/{file}
The sync root is the folder the user points at, or — on a first pull into a
project folder — a `{Year} Suralink Folder` subfolder created inside it
(default_sync_folder(); named by engagement_folder_name()).

`sorted/` is seeded ONCE, on the first pull, as a faithful copy of `_raw/`.
Every later sync routes genuinely-new files into `sorted/_unsorted/` instead -
an inbox the user (or the `binder-organize` skill) files at leisure - so a
`sorted/` the user has reorganized is never disturbed. See `is_seeding` and
`plan_paths`, and ../references/architecture.md "The sorted folder".
"""
import os
import re
import shutil
import time
import zipfile

_ILLEGAL = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

# Inbox subfolder inside sorted/ where post-seed syncs drop new arrivals.
UNSORTED = "_unsorted"


def safe_name(name, fallback="file"):
    """Sanitize a filename - strip characters illegal on Windows/macOS/Linux."""
    name = (name or "").strip()
    cleaned = _ILLEGAL.sub("_", name).strip(" .")
    return cleaned or fallback


def safe_component(name, fallback="Unnamed"):
    """Sanitize a single folder-name component."""
    name = (name or "").strip()
    cleaned = _ILLEGAL.sub("_", name).strip(" .")
    return (cleaned or fallback)[:120]


def normalize_file(raw_file, *, audit_id, request_id, request_name,
                   side="client", category=""):
    """Turn a `getRequest` file object into a flat record."""
    return {
        "fmsId": raw_file.get("fmsId"),
        "fId": str(raw_file.get("id", "")),
        "auditId": str(audit_id),
        "requestId": str(request_id),
        "requestName": request_name or "",
        "origFileName": raw_file.get("origFileName") or "file",
        "fileType": raw_file.get("fileType") or "",
        "fileSize": raw_file.get("fileSize") or 0,
        "portalTs": raw_file.get("ts") or "",
        "side": side,
        "category": category or "",
    }


def diff_new_files(state, fetched):
    """Return the subset of `fetched` whose `fmsId` is not yet in the sync
    state (state.py). These are the genuinely-new files to pull."""
    known = (state or {}).get("files", {})
    return [f for f in fetched if not f.get("fmsId") or f["fmsId"] not in known]


def detect_deletions(state, current_fmsids):
    """Files pulled into this sync folder that the portal no longer holds.
    Returns [(fmsId, record)] for every NON-tombstoned state file whose fmsId is
    absent from `current_fmsids` (what the portal serves now — index.fmsids()).

    One sync folder mirrors one engagement, so every file in the state belongs
    to it — no auditId filter needed. The caller tombstones each via
    state.mark_deleted; the local copy is never removed. See
    ../references/architecture.md "Deleted files".
    """
    current = set(current_fmsids or [])
    gone = []
    for fid, rec in (state or {}).get("files", {}).items():
        if rec.get("deletedInPortal"):
            continue
        if fid not in current:
            gone.append((fid, rec))
    return gone


# --- category numbering ---------------------------------------------------

def number_categories(ordered_names):
    """Given category names in WEBSITE order, return {name: 'NN'} with 1-based,
    zero-padded numbers. Width adapts to the count (min 2 digits).

    Numbering is by website order so the folders sort the way the portal shows
    them - not by Suralink's own internal category ids, which do not sort."""
    width = max(2, len(str(len(ordered_names))))
    return {name: str(i).zfill(width) for i, name in enumerate(ordered_names, 1)}


def numbered_category_folder(category_name, number_map):
    """'Permanent File' -> '04 Permanent File'. Unknown category -> name as-is."""
    num = number_map.get(category_name)
    return f"{num} {category_name}" if num else category_name


# --- path planning --------------------------------------------------------

_YEAR = re.compile(r'\b(20\d{2})\b')


def engagement_folder_name(label):
    """Turn an engagement label into an explicit, self-describing folder name.

    The label (from the engagement binding — state.py) is fine as a name but is
    ambiguous sitting next to a client's other folders on disk: nothing marks it
    as the Suralink pull. So the folder name always ends in "Suralink Folder",
    and leads with the engagement year when one can be pulled out of the label
    (the common case):
        "Audit 2025"              -> "2025 Suralink Folder"
        "2024 audit"              -> "2024 Suralink Folder"
        "Example 401(k) 2024 Audit"  -> "2024 Suralink Folder"
    No 4-digit year in the label -> fall back to the sanitized label itself:
        "NMBF FY25"               -> "NMBF FY25 Suralink Folder"
    """
    m = _YEAR.search(label or "")
    stem = m.group(1) if m else safe_component(label, fallback="Engagement")
    return f"{stem} Suralink Folder"


def default_sync_folder(parent_dir, label):
    """The default sync-root folder for a FIRST pull into a folder the user
    pointed at: a `{Year} Suralink Folder` subfolder inside `parent_dir`.

    Putting the pull in its own named subfolder means it never collides with the
    working files already in a project folder (e.g. engagements/<client>/), and
    the name self-describes. `engagement_folder_name(label)` supplies the name
    (year pulled from the label; sanitized-label fallback). If the user points
    directly at a dedicated/empty folder they want to BE the sync root, use that
    path as-is instead of calling this — see resolve-target.md."""
    return os.path.join(os.path.abspath(parent_dir),
                        engagement_folder_name(label))


def is_seeding(sync_root):
    """True if this sync has no `sorted/` folder yet — i.e. its FIRST pull.

    Compute this ONCE per run, before any file is downloaded, and pass the
    result to plan_paths for every file in that batch. A first run creates
    sorted/ partway through, but the whole batch must still be treated as a
    seed — so decide up front, not per file.

    First pull       -> seeding True  -> sorted/ mirrors _raw/ exactly.
    Every later sync -> seeding False -> new files land in sorted/_unsorted/.
    """
    return not os.path.isdir(os.path.join(sync_root, "sorted"))


def plan_paths(request_name, orig_name, category="", seeding=True):
    """Return (raw_rel, sorted_rel): paths for one file, relative to the SYNC
    ROOT (join them against the sync folder — relocate/import_zip do this).

    `_raw/` is ALWAYS the byte-for-byte portal-layout chain-of-custody copy:
        _raw/{NN Category}/{request}/{file}

    `sorted/` depends on `seeding` (compute it once with is_seeding()):
      seeding=True  - first pull. sorted/ mirrors _raw/ so the working copy
                      starts as a faithful portal snapshot:
        sorted/{NN Category}/{request}/{file}
      seeding=False - every later sync. The file is a NEW arrival; it lands in
                      the sorted/_unsorted/ inbox, still in portal layout, so it
                      never collides with a sorted/ the user has reorganized:
        sorted/_unsorted/{NN Category}/{request}/{file}

    `category` should already be numbered (use numbered_category_folder).
    Without a category the {NN Category} segment is simply omitted.
    """
    rq = safe_component(request_name, fallback="Uncategorized")
    fn = safe_name(orig_name)
    parts_raw = ["_raw"]
    parts_sorted = ["sorted"]
    if not seeding:
        parts_sorted.append(UNSORTED)
    if category:
        cat = safe_component(category)
        parts_raw.append(cat)
        parts_sorted.append(cat)
    parts_raw += [rq, fn]
    parts_sorted += [rq, fn]
    return os.path.join(*parts_raw), os.path.join(*parts_sorted)


def dedupe_path(abs_path):
    """If abs_path exists, return a non-colliding variant 'name (2).ext'."""
    if not os.path.exists(abs_path):
        return abs_path
    base, ext = os.path.splitext(abs_path)
    i = 2
    while os.path.exists(f"{base} ({i}){ext}"):
        i += 1
    return f"{base} ({i}){ext}"


def newest_match(staging_dir, orig_name):
    """Find the file the browser dropped in `staging_dir` for `orig_name`.
    Matches browser ' (1)' collision variants. Returns abs path or None."""
    if not staging_dir or not os.path.isdir(staging_dir):
        return None
    stem, ext = os.path.splitext(orig_name)
    cands = []
    for fn in os.listdir(staging_dir):
        s, e = os.path.splitext(fn)
        if e.lower() == ext.lower() and (s == stem or re.match(
                re.escape(stem) + r"(?: \(\d+\))?$", s)):
            cands.append(os.path.join(staging_dir, fn))
    if not cands:
        return None
    return max(cands, key=lambda p: os.path.getmtime(p))


def relocate(staged_path, sync_root, raw_rel, sorted_rel):
    """Copy a staged download into the sync folder (_raw + sorted), then remove
    the staged original (best-effort). Copy-based, cross-filesystem safe. Never
    overwrites in _raw.

    `raw_rel` / `sorted_rel` are the sync-root-relative paths from plan_paths;
    they are joined against `sync_root`.

    The sorted copy's filename is kept aligned with the (possibly de-duped)
    _raw name, then the sorted side is de-duped too - so a sorted/_unsorted/
    inbox never silently overwrites an earlier, not-yet-filed arrival.

    `sorted_rel` carries the _unsorted/ segment already when this is a post-seed
    sync - see plan_paths. Returns {raw, sorted, bytes, stagedRemoved}; `raw`
    and `sorted` are paths relative to `sync_root`."""
    raw_abs = dedupe_path(os.path.join(sync_root, raw_rel))
    sorted_dir = os.path.dirname(os.path.join(sync_root, sorted_rel))
    sorted_abs = dedupe_path(os.path.join(sorted_dir, os.path.basename(raw_abs)))
    os.makedirs(os.path.dirname(raw_abs), exist_ok=True)
    os.makedirs(sorted_dir, exist_ok=True)
    shutil.copy2(staged_path, raw_abs)
    shutil.copy2(raw_abs, sorted_abs)
    removed = True
    try:
        os.remove(staged_path)
    except OSError:
        removed = False
    return {
        "raw": os.path.relpath(raw_abs, sync_root),
        "sorted": os.path.relpath(sorted_abs, sync_root),
        "bytes": os.path.getsize(raw_abs),
        "stagedRemoved": removed,
    }


def wait_for_download(staging_dir, orig_name, timeout=30):
    """Block until a download for `orig_name` finishes. Returns path or None."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        p = newest_match(staging_dir, orig_name)
        if p and not p.endswith(".crdownload") and not os.path.exists(p + ".crdownload"):
            return p
        time.sleep(0.5)
    return None


def wait_for_zip(path, *, min_bytes_expected=None, timeout=600, settle=3,
                 poll=5, on_tick=None):
    """Block until `path` is a COMPLETE zip — not just "exists with no
    .crdownload sibling".

    Why this exists — Cowork's FUSE mount caches file metadata, so a naive
    "stop when *.zip exists and *.crdownload doesn't" loop will often see a
    stale half-written size, conclude the download is done, and proceed to
    extract a truncated archive. This poll closes that gap with three
    overlapping signals:

      1. `os.sync()` each tick to flush the mount cache before reading.
      2. `zipfile.ZipFile(path)` opens cleanly — i.e. the end-of-central-
         directory marker is present. Truncated zips raise BadZipFile.
      3. Size is stable for `settle` consecutive ticks AND, if
         `min_bytes_expected` is given, at least that many bytes are on
         disk. The floor catches the rare case where a zip's EOCD is
         already on disk but the body is still being written behind it.

    Returns the absolute path on success, None on timeout.

    `min_bytes_expected` should be a CONSERVATIVE floor — for a categories/
    requests zip, ~50% of the uncompressed-total from
    index.all_files()/fileSize is safe (Suralink's bulk zip compresses PDFs
    and Office files modestly). Set it from the engagement index, not from
    the zip filename's "{N}files" hint.

    `on_tick(elapsed_s, bytes_on_disk, zip_ok)` is an optional callback for
    progress reporting — called once per poll.

    A typical caller pairs this with `newest_zip_matching` and a
    pre-trigger timestamp so an old leftover zip from a prior failed run
    is never mistaken for the one currently being built:

        t0 = time.time()
        run(suralink.trigger_bulk_zip_js("categories_requests"))
        # wait for filename to appear (server build can take 1-3 min)
        for _ in range(60):
            zp = sync.newest_zip_matching(download_dir, "ClientShortName",
                                          since_mtime=t0)
            if zp: break
            time.sleep(5)
        ok = sync.wait_for_zip(zp, min_bytes_expected=expected//2)
    """
    import zipfile
    deadline = time.time() + timeout
    t0 = time.time()
    stable_count = 0
    last_size = -1
    while time.time() < deadline:
        try:
            os.sync()
        except Exception:
            pass  # not available everywhere; the open() below still validates
        size = os.path.getsize(path) if os.path.exists(path) else 0
        zip_ok = False
        if size > 0 and (min_bytes_expected is None or size >= min_bytes_expected):
            # Open + close the archive to validate the central directory.
            # zipfile reads the EOCD at the tail; a truncated zip raises.
            try:
                with zipfile.ZipFile(path) as z:
                    # Cheap sanity: at least one entry, names parse.
                    if z.namelist():
                        zip_ok = True
            except (zipfile.BadZipFile, OSError):
                zip_ok = False
        if on_tick:
            try:
                on_tick(time.time() - t0, size, zip_ok)
            except Exception:
                pass
        if zip_ok and size == last_size:
            stable_count += 1
            if stable_count >= settle:
                return path
        else:
            stable_count = 0
        last_size = size
        time.sleep(poll)
    return None


def newest_zip_matching(download_dir, name_substr, since_mtime=0.0):
    """Pick the newest .zip in `download_dir` whose filename contains
    `name_substr` (case-insensitive) and whose mtime is strictly newer than
    `since_mtime`. Pair with `wait_for_zip` so an old leftover zip from a
    prior failed run is not mistaken for the current one.

    Returns abs path or None.
    """
    if not download_dir or not os.path.isdir(download_dir):
        return None
    needle = (name_substr or "").lower()
    best = None
    best_m = since_mtime
    for fn in os.listdir(download_dir):
        if not fn.lower().endswith(".zip"):
            continue
        if needle and needle not in fn.lower():
            continue
        p = os.path.join(download_dir, fn)
        try:
            m = os.path.getmtime(p)
        except OSError:
            continue
        if m > best_m:
            best_m = m
            best = p
    return best


def wait_and_read_json(download_dir, filename, timeout=20, delete=True):
    """Companion to `suralink.dump_to_download_js`. Block until the named
    JSON file appears under `download_dir` (the user's mounted Downloads
    folder), parse it, and optionally delete it.

    `filename` is the same name passed to dump_to_download_js. `delete`
    defaults to True so the ferry file doesn't pile up. Returns the parsed
    JSON, or None on timeout.
    """
    import json
    path = os.path.join(download_dir, filename)
    deadline = time.time() + timeout
    while time.time() < deadline:
        if os.path.exists(path) and not os.path.exists(path + ".crdownload"):
            try:
                with open(path) as f:
                    obj = json.load(f)
                if delete:
                    try: os.remove(path)
                    except Exception: pass
                return obj
            except Exception:
                pass  # still being written
        time.sleep(0.3)
    return None


# --- group selection ------------------------------------------------------

def select_files(index, *, request_id=None, request_name=None,
                  category=None):
    """Pick a SUBSET of an engagement index's files - the engine behind group
    downloads (one request, or one whole category).

    Pass exactly one filter:
      request_id   - all files under that request id
      request_name - all files under requests whose name matches (substring,
                     case-insensitive)
      category     - all files under requests in that category (substring, ci)

    Returns a flat list of file records, each annotated with requestId /
    requestName / category (same shape as index.all_files()).
    """
    out = []
    rn = (request_name or "").strip().lower()
    cat = (category or "").strip().lower()
    for r in (index or {}).get("requests", []):
        if request_id is not None and str(r.get("requestId")) != str(request_id):
            continue
        if rn and rn not in (r.get("requestName", "") or "").lower():
            continue
        if cat and cat not in (r.get("category", "") or "").lower():
            continue
        for f in r.get("files", []):
            out.append({**f, "requestId": r["requestId"],
                        "requestName": r["requestName"],
                        "category": r["category"]})
    return out


# --- bulk zip import ------------------------------------------------------

def import_zip(zip_path, sync_root, ordered_categories,
               seeding=True, progress=None):
    """Extract a Suralink bulk 'categories / requests' zip into the sync folder.

    Suralink's bulk download (structure option: categories/requests) produces a
    zip laid out  {Category}/{Request name}/{file}. This extracts it into
    `sync_root`, numbering each category by WEBSITE order.

    `seeding` (compute with is_seeding()): the bulk zip is the fast FIRST-pull
    route, so this is normally True and the extracted files seed both _raw/ and
    sorted/ identically:
        {sync_root}/_raw/{NN Category}/{Request name}/{file}
        {sync_root}/sorted/{NN Category}/{Request name}/{file}
    If a zip is ever imported into a sync that already has a sorted/ folder,
    pass seeding=False and the files land in sorted/_unsorted/ instead.

    `ordered_categories` is the category-name list in website order, from the
    `suralink` skill's list_categories_js().

    RE-ENTRANT. If extraction is killed midway (large zip + bash timeout), just
    call this again with the same zip and arguments: files already present at
    the correct path AND correct uncompressed size are skipped. Records are
    still returned for skipped files, so a re-run returns the full record
    list either way. To rebuild records from disk WITHOUT touching the zip
    (e.g. the original return value was lost), use `scan_raw_for_records`.

    `progress` is an optional callable `progress(done, total, fname)` invoked
    after each file. Useful when running under a tight timeout — print or
    checkpoint so a kill leaves a known watermark.

    Returns a list of records:
        {category, requestName, fileName, rawPath, bytes, skipped}
    `skipped` is True iff the file was already on disk at the right size.
    Records carry no fmsId - the caller reconciles fmsIds from a getRequest
    enumeration so the sync state can dedup future syncs (see import-zip.md).
    """
    number_map = number_categories(ordered_categories)
    base_root = os.path.abspath(sync_root)
    records = []
    with zipfile.ZipFile(zip_path) as z:
        infos = [i for i in z.infolist() if not i.filename.endswith("/")]
        total = len(infos)
        for done, info in enumerate(infos, 1):
            name = info.filename
            parts = name.split("/")
            if len(parts) >= 3:
                category, request, fname = parts[0], parts[1], parts[-1]
            elif len(parts) == 2:
                category, request, fname = parts[0], "", parts[1]
            else:
                category, request, fname = "", "", parts[0]
            cat_folder = numbered_category_folder(category, number_map)
            raw_rel, sorted_rel = plan_paths(request, fname,
                                             category=cat_folder,
                                             seeding=seeding)
            raw_abs = os.path.join(base_root, raw_rel)
            sorted_abs = os.path.join(base_root, sorted_rel)
            os.makedirs(os.path.dirname(raw_abs), exist_ok=True)
            os.makedirs(os.path.dirname(sorted_abs), exist_ok=True)
            expected = info.file_size
            # Idempotent extract: skip if raw exists at correct size.
            # If the existing file is the WRONG size, it is a partial write
            # from a killed previous run — overwrite, do NOT dedupe (a
            # dedupe would leave the partial behind under the intended name
            # and write the real one as "(1)", which breaks scan_raw_for_records).
            raw_ok = (os.path.exists(raw_abs)
                      and os.path.getsize(raw_abs) == expected)
            if raw_ok:
                skipped_raw = True
            else:
                with z.open(info) as src, open(raw_abs, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                skipped_raw = False
            # Idempotent sorted copy — same overwrite-on-wrong-size rule.
            sorted_ok = (os.path.exists(sorted_abs)
                         and os.path.getsize(sorted_abs) == expected)
            if not sorted_ok:
                shutil.copy2(raw_abs, sorted_abs)
            records.append({
                "category": cat_folder,
                "requestName": request,
                "fileName": fname,
                "rawPath": os.path.relpath(raw_abs, base_root),
                "bytes": os.path.getsize(raw_abs),
                "skipped": skipped_raw,
            })
            if progress:
                try:
                    progress(done, total, fname)
                except Exception:
                    pass
    return records


def scan_raw_for_records(sync_root):
    """Rebuild the import_zip record list FROM DISK, without touching any zip.

    Walks `{sync_root}/_raw/` and produces records in the same shape as
    `import_zip` (minus the `skipped` flag — these are all "discovered on
    disk"). Two uses: (1) recover a killed-mid-extract import and keep going
    with reconciliation; (2) ADOPT a folder that already holds a `_raw/` tree
    from the old (pre-folder-state) model — scan it, reconcile the records to
    portal fmsIds, and write a fresh state file so no re-download is needed.

    Records:
        {category, requestName, fileName, rawPath, bytes}
    `category` is the numbered folder name (e.g. "01 Sample Files for Michael")
    and `requestName` is the unnumbered Suralink request label.
    """
    base_root = os.path.abspath(sync_root)
    raw_root = os.path.join(base_root, "_raw")
    out = []
    if not os.path.isdir(raw_root):
        return out
    for cat_folder in sorted(os.listdir(raw_root)):
        cat_path = os.path.join(raw_root, cat_folder)
        if not os.path.isdir(cat_path):
            continue
        for req_folder in sorted(os.listdir(cat_path)):
            req_path = os.path.join(cat_path, req_folder)
            if not os.path.isdir(req_path):
                # File directly under category (rare): treat request as "".
                if os.path.isfile(req_path):
                    out.append({
                        "category": cat_folder,
                        "requestName": "",
                        "fileName": req_folder,
                        "rawPath": os.path.relpath(req_path, base_root),
                        "bytes": os.path.getsize(req_path),
                    })
                continue
            for fname in sorted(os.listdir(req_path)):
                fpath = os.path.join(req_path, fname)
                if not os.path.isfile(fpath):
                    continue
                out.append({
                    "category": cat_folder,
                    "requestName": req_folder,
                    "fileName": fname,
                    "rawPath": os.path.relpath(fpath, base_root),
                    "bytes": os.path.getsize(fpath),
                })
    return out


def reconcile_to_fmsids(records, portal_files):
    """Bind imported zip files to their portal `fmsId`s.

    `records`      - the list returned by `import_zip` or `scan_raw_for_records`
                     (each has at least `fileName`, `requestName` = the
                     sanitized request-folder basename on disk, `rawPath`,
                     `bytes`).
    `portal_files` - flat list of portal file records (from `index.all_files`):
                     each has `fmsId`, `origFileName`, `fileSize`, `requestName`,
                     `category`, etc.

    Returns `[(record, portal_record)]` for every record that found a match.
    Records that could not be bound are reported in the companion `unmatched`
    list via the *_pairs / *_unmatched return tuple.

    Algorithm — matches a known failure mode head-on:
    1. Group portal records by `origFileName`. A filename can collide (two
       distinct files with the same name in different requests — observed
       on real engagements).
    2. For each disk record, pick a portal candidate that has not been
       claimed yet (greedy fmsId-uniqueness).
    3. When multiple unclaimed candidates exist, tiebreak first on
       request-folder-name match (sanitized — Suralink's zip folder names
       are post-`safe_component()`, so compare AFTER sanitization on both
       sides; raw names will NOT byte-match), then on absolute size delta.

    This catches the same-filename-same-size case that naive
    filename+size matching collapses to a single fmsId.

    Returns `(matched_pairs, unmatched_records)` where matched_pairs is a
    list of `(record, portal_record)` tuples.
    """
    by_name = {}
    for p in portal_files:
        by_name.setdefault(p.get("origFileName"), []).append(p)
    matched, unmatched, used = [], [], set()
    for rec in records:
        cands = [p for p in by_name.get(rec.get("fileName") or rec.get("origFileName"), [])
                 if p.get("fmsId") and p["fmsId"] not in used]
        if not cands:
            unmatched.append(rec); continue
        if len(cands) == 1:
            best = cands[0]
        else:
            disk_req = safe_component(rec.get("requestName") or "")
            disk_size = int(rec.get("bytes", 0) or 0)
            def score(p):
                req_match = safe_component(p.get("requestName") or "") == disk_req
                size_delta = abs(int(p.get("fileSize", 0) or 0) - disk_size)
                return (0 if req_match else 1, size_delta)
            best = min(cands, key=score)
        matched.append((rec, best))
        used.add(best["fmsId"])
    return matched, unmatched


def ian_files(ian_body):
    """Flatten a `loadIAN` response into per-file activity records.

    ian_body = the parsed gateway response (browser.parse_result()['body']).
    Returns a list of:
      {fmsId, fId, requestId, origFileName, fileSize, ts, stateChange, isRead}
    one per (non-deleted) file appearing in the timeline. Diff this against the
    sync state with diff_new_files() to get the genuinely new uploads.

    NOTE: the timeline is a convenience feed, not a dependable whole-engagement
    source (see the `suralink` skill). For a reliable "what's new" use the
    binder map + the per-engagement index instead.
    """
    out = []
    try:
        msgs = ian_body["data"]["ianData"]["messages"] or []
    except Exception:
        return out
    for m in msgs:
        files = m.get("files")
        if not isinstance(files, list):
            continue
        for f in files:
            if str(f.get("isDeleted", "0")) == "1":
                continue
            out.append({
                "fmsId": f.get("fmsId"),
                "fId": str(f.get("id", "")),
                "requestId": str(m.get("requestId", "")),
                "origFileName": f.get("origFileName") or "file",
                "fileSize": f.get("fileSize") or 0,
                "ts": f.get("ts") or m.get("ts") or "",
                "stateChange": m.get("stateChange", ""),
                "isRead": m.get("isRead", ""),
            })
    return out
