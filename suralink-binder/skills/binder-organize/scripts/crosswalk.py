"""The crosswalk - `_organize.json`, one per engagement.

Every file the organize skill moves is recorded here, pinning its new
organized location back to the untouched `_raw/` original and (in sister mode)
to the suralink-sync manifest's `fmsId`. That chain is the traceability: a
renamed-folder, reorganized binder you can still trace to the exact sync that
delivered each file.

`_organize.json` lives at the engagement folder root, beside suralink-sync's
`_index.json`. Its presence is also the "have I organized this engagement
before?" flag - see is_first_organize(). See ../references/architecture.md.
"""
import json
import os
from datetime import datetime, timezone

CROSSWALK_NAME = "_organize.json"


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _norm_rel(p):
    return os.path.normcase(os.path.normpath(p)) if p else p


def path(engagement_dir):
    return os.path.join(engagement_dir, CROSSWALK_NAME)


def exists(engagement_dir):
    return os.path.exists(path(engagement_dir))


def is_first_organize(engagement_dir):
    """True if this engagement has never been organized. On a first organize the
    whole portal-layout body of `sorted/` is the work queue; afterwards only the
    `sorted/_unsorted/` inbox is."""
    return not exists(engagement_dir)


def default(engagement_label=None):
    return {"version": 1, "engagement": engagement_label, "lastOrganize": None,
            "firstOrganizeDone": False, "files": []}


def load(engagement_dir, engagement_label=None):
    """Load the crosswalk, or a fresh default if none exists yet."""
    p = path(engagement_dir)
    if not os.path.exists(p):
        return default(engagement_label)
    with open(p, "r", encoding="utf-8") as f:
        d = json.load(f)
    d.setdefault("files", [])
    return d


def save(engagement_dir, data):
    """Write the crosswalk atomically (temp file + replace)."""
    p = path(engagement_dir)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    os.replace(tmp, p)
    return p


def make_entry(*, organized_path, raw_path, orig_name, bucket, index,
               section, is_sample, moved_from, client_type, fms_id=None):
    """Build one crosswalk record. Paths should be engagement-relative."""
    return {
        "organizedPath": organized_path,
        "rawPath": raw_path,
        "fmsId": fms_id,
        "origName": orig_name,
        "bucket": bucket,
        "index": index,
        "section": section,
        "isSample": bool(is_sample),
        "movedFrom": moved_from,
        "clientType": client_type,
        "organizedAt": _now(),
    }


def record(data, entry):
    """Append a file record to the crosswalk."""
    data.setdefault("files", []).append(entry)
    return data


def mark_organized(data):
    """Stamp the run: firstOrganizeDone + lastOrganize timestamp."""
    data["firstOrganizeDone"] = True
    data["lastOrganize"] = _now()
    return data


def find_by_fms(data, fms_id):
    if not fms_id:
        return None
    for e in data.get("files", []):
        if e.get("fmsId") == fms_id:
            return e
    return None


def find_by_organized(data, organized_path):
    tgt = _norm_rel(organized_path)
    for e in data.get("files", []):
        if _norm_rel(e.get("organizedPath", "")) == tgt:
            return e
    return None


def fms_for_raw(manifest, raw_abs, mirror_root):
    """Match a `_raw/` file to its suralink-sync manifest record.

    The manifest stores `rawPath` mirror-relative; this re-derives that and
    looks it up. Returns (fmsId, record) or (None, None) - None when the file
    is not from a suralink-sync mirror (standalone / non-Suralink mode), which
    is expected and fine.
    """
    try:
        target = _norm_rel(os.path.relpath(os.path.abspath(raw_abs),
                                           os.path.abspath(mirror_root)))
    except ValueError:
        return None, None
    for fid, rec in manifest.get("files", {}).items():
        if _norm_rel(rec.get("rawPath", "")) == target:
            return fid, rec
    return None, None
