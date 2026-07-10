"""The categorization engine for binder-organize.

Pure functions plus filesystem moves. Decides WHICH binder section a file
belongs in, whether it is a sample, and WHERE it should land - then moves it.
It never touches `_raw/`; it only ever moves files inside `sorted/`.

The skill module (references/modules/organize.md) drives these helpers and
makes the judgment calls the keyword rules cannot. See ../references/architecture.md.
"""
import os
import re
import shutil

YEAR_RE = re.compile(r"(?:19|20)\d{2}")


# --- text signals ---------------------------------------------------------

def _norm(s):
    return (s or "").lower()


def signal_text(signals):
    """Flatten a signals dict into one lowercased search string.

    `signals` may carry any of: category (the NN Category folder name),
    request (the Suralink request folder name), filename, extra (anything
    else - e.g. text Claude pulled from the document)."""
    return " ".join(_norm(signals.get(k, ""))
                    for k in ("category", "request", "filename", "extra"))


def _hits(text, keywords):
    return [kw for kw in keywords if kw.lower() in text]


# --- classification -------------------------------------------------------

def is_sample(taxonomy, signals):
    """True if the file's signals trip a samples keyword. A sample is still
    filed into its real section - this flag only adds the 'Samples' subfolder."""
    return bool(_hits(signal_text(signals), taxonomy["samples"]["keywords"]))


def classify(taxonomy, client_type, signals, single_audit=False):
    """Map one file's signals to a binder bucket by keyword scoring.

    Returns a dict:
      bucket       'section' | 'perm' | 'single_audit' | 'other'
      index        4-digit index, or None for 'other'
      name         section name
      score        number of keywords matched (0 for 'other')
      matched      the keywords that matched
      confident    True iff there was a single clear winner
      alternatives up to 3 runner-up buckets, for the user to override with

    'confident' False is the signal for the organize module to STOP and let
    Claude judge (read the doc, ask the user). Keyword rules get the obvious
    ones; Claude handles the rest.
    """
    text = signal_text(signals)
    ct = taxonomy["client_types"][client_type]
    cands = []  # (score, bucket, index, name, hits)

    perm_hits = _hits(text, taxonomy["perm_file"]["keywords"])
    if perm_hits:
        cands.append((len(perm_hits), "perm", taxonomy["perm_file"]["index"],
                      taxonomy["perm_file"]["name"], perm_hits))

    if single_audit:
        sa_hits = _hits(text, taxonomy["single_audit"]["keywords"])
        if sa_hits:
            idx, name = taxonomy["single_audit"]["section"]
            cands.append((len(sa_hits), "single_audit", idx, name, sa_hits))

    name_by_idx = {i: n for i, n in ct.get("sections", [])}
    for idx, kws in ct.get("keywords", {}).items():
        hits = _hits(text, kws)
        if hits:
            cands.append((len(hits), "section", idx,
                          name_by_idx.get(idx, idx), hits))

    if not cands:
        return {"bucket": "other", "index": None,
                "name": taxonomy["catch_all"]["name"], "score": 0,
                "matched": [], "confident": False, "alternatives": []}

    cands.sort(key=lambda c: -c[0])
    top = cands[0]
    runner = cands[1][0] if len(cands) > 1 else 0
    alts = [{"bucket": c[1], "index": c[2], "name": c[3],
             "score": c[0], "matched": c[4]} for c in cands[1:4]]
    return {"bucket": top[1], "index": top[2], "name": top[3],
            "score": top[0], "matched": top[4],
            "confident": top[0] > runner, "alternatives": alts}


# --- perm-file date split -------------------------------------------------

def extract_year(text):
    """Latest 4-digit 19xx/20xx year found in a string, or None.

    Used two ways: pull the fiscal year from an engagement label ('Audit 2025'
    -> 2025), and guess a document's year from its name. For a reliable doc
    date Claude should read the document - this is only a fallback."""
    if not text:
        return None
    yrs = [int(m.group(0)) for m in YEAR_RE.finditer(str(text))]
    return max(yrs) if yrs else None


def perm_split(taxonomy, doc_year, fiscal_year):
    """Which Perm File subfolder a document belongs in, when the date split is
    switched on. Returns the subfolder name, or None to leave it at the 9000
    root (undated, or split disabled).

      doc_year < fiscal_year   -> 'Carryforward'  (you should already have it)
      doc_year >= fiscal_year  -> 'New This Year'
      doc_year is None         -> None            (stays at root)
    """
    ds = taxonomy["perm_file"].get("date_split", {})
    if doc_year is None or fiscal_year is None:
        return None
    if doc_year < int(fiscal_year):
        return ds.get("carryforward", "Carryforward")
    return ds.get("current", "New This Year")


def perm_subfolder_for(taxonomy, client_type, signals):
    """Ruled topical Perm File subfolder for a perm-bucket file, or None (root).

    Client types with rules under perm_file.subfolders (EBP: 9100 Plan
    Documents / 9200 Service Agreements / 9300 SOC 1 Reports, per the EBP
    binder template) get topical filing; a type with no rules (standard) always
    returns None. Scored like classify() — most keyword hits wins; ties go to
    the first rule in template order. A topical match WINS over the optional
    date split; date-split (if the user asked for it) applies only to files
    this returns None for.
    """
    rules = taxonomy["perm_file"].get("subfolders", {}).get(client_type, [])
    if not isinstance(rules, list):
        return None
    text = signal_text(signals)
    best, best_hits = None, 0
    for rule in rules:
        hits = len(_hits(text, rule.get("keywords", [])))
        if hits > best_hits:
            best, best_hits = rule["name"], hits
    return best


# --- destination planning -------------------------------------------------

def folder_name(taxonomy, index, name):
    """'0200' + 'Planning' -> '0200 Planning'. None index -> bare name."""
    if index is None:
        return name
    return taxonomy.get("folder_name_format", "{index} {name}").format(
        index=index, name=name)


def plan_destination(taxonomy, classification, sample_flag=False,
                     perm_subfolder=None):
    """Relative folder parts (under the engagement's `sorted/`) for one file.

    The filename is NEVER changed - the caller appends the original name.

      section / single_audit -> ['1200 Receivables, net']  (+ ['Samples'])
      perm                   -> ['9000 Perm File']         (+ [perm_subfolder])
      other                  -> ['Other']

    Samples get a 'Samples' subfolder for section/single_audit buckets only.
    Perm File is flat by default; perm_subfolder carries either a ruled topical
    subfolder (perm_subfolder_for) or the optional date split (perm_split).
    """
    b = classification["bucket"]
    if b == "perm":
        parts = [folder_name(taxonomy, classification["index"],
                             classification["name"])]
        if perm_subfolder:
            parts.append(perm_subfolder)
        return parts
    if b == "other":
        return [taxonomy["catch_all"]["name"]]
    parts = [folder_name(taxonomy, classification["index"],
                         classification["name"])]
    if sample_flag and b in ("section", "single_audit"):
        parts.append(taxonomy["samples"]["subfolder"])
    return parts


# --- filesystem ops -------------------------------------------------------

def dedupe_path(abs_path):
    """Non-colliding 'name (2).ext' variant if abs_path already exists."""
    if not os.path.exists(abs_path):
        return abs_path
    base, ext = os.path.splitext(abs_path)
    i = 2
    while os.path.exists(f"{base} ({i}){ext}"):
        i += 1
    return f"{base} ({i}){ext}"


def raw_counterpart(engagement_dir, sorted_file_abs):
    """The `_raw/` path matching a not-yet-organized file in `sorted/`.

    A file the organize skill has not moved yet sits in mirror layout - either
    `sorted/{NN Cat}/{Request}/{file}` (first-organize seed) or
    `sorted/_unsorted/{NN Cat}/{Request}/{file}` (a later sync's arrival). Both
    mirror `_raw/{NN Cat}/{Request}/{file}`. This strips the sorted/ (and any
    _unsorted/) prefix and re-roots under _raw/. Returns an absolute path
    (may not exist - caller checks). Once a file has been organized its path no
    longer mirrors _raw/, so use the crosswalk for those, not this.
    """
    sorted_root = os.path.join(engagement_dir, "sorted")
    rel = os.path.relpath(os.path.abspath(sorted_file_abs),
                          os.path.abspath(sorted_root))
    parts = rel.split(os.sep)
    if parts and parts[0] == "_unsorted":
        parts = parts[1:]
    return os.path.join(engagement_dir, "_raw", *parts)


def move_into(src_abs, dest_dir_abs):
    """Move a file into dest_dir_abs, keeping its name (de-duped on collision).
    Creates the destination folder. Returns the final absolute path."""
    os.makedirs(dest_dir_abs, exist_ok=True)
    dest = dedupe_path(os.path.join(dest_dir_abs, os.path.basename(src_abs)))
    shutil.move(src_abs, dest)
    return dest


def prune_empty_dirs(root_abs):
    """Remove empty folders under root_abs (depth-first), root itself kept.
    Returns the list of removed directories. Used to sweep an emptied
    `_unsorted/` after an organize run."""
    removed = []
    root_abs = os.path.abspath(root_abs)
    for dirpath, _dirs, _files in os.walk(root_abs, topdown=False):
        if os.path.abspath(dirpath) == root_abs:
            continue
        try:
            if not os.listdir(dirpath):
                os.rmdir(dirpath)
                removed.append(dirpath)
        except OSError:
            pass
    return removed
