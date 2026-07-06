"""The per-engagement file index - `_index.json` inside each engagement folder.

A parseable local SNAPSHOT of the portal's current file list for one
engagement: every category, every request, every file (fmsId, fId, name, size,
timestamp). It is the reference list other operations run against - download
scripts, group pulls, the sync diff - so they do not each re-crawl the portal.

  - The manifest (`manifest.py`) records what has been PULLED to disk.
  - This index records what the PORTAL currently HOLDS.
  Diffing the two is how "what's new" and "what was deleted" are computed.

Freshness. The index carries a cheap `binderSignature` - a fingerprint of the
`suralink` skill's map_binder_js output (per-request file/new-file counts). Any
operation that relies on the index first re-scrapes map_binder (one DOM read,
free, no gateway/throttle) and calls `is_stale`; if the signature moved, the
index is rebuilt from a fresh enumeration. So the reference list is always
verified current at the moment it is used.

Browser work is the `suralink` skill's job; this module structures and stores
the result and computes freshness.
"""
import hashlib
import json
import os
from datetime import datetime, timezone

INDEX_NAME = "_index.json"


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def index_path(engagement_dir):
    """`_index.json` lives at the root of one engagement folder
    ({mirror}/{Client}/{Label}/)."""
    return os.path.join(engagement_dir, INDEX_NAME)


def load(engagement_dir):
    """Load an engagement's index, or None if it has never been built."""
    p = index_path(engagement_dir)
    if not os.path.exists(p):
        return None
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def save(engagement_dir, index):
    """Write `_index.json` atomically."""
    os.makedirs(engagement_dir, exist_ok=True)
    p = index_path(engagement_dir)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    os.replace(tmp, p)
    return p


def binder_signature(binder_map):
    """A cheap, stable fingerprint of a map_binder_js result.

    map_binder gives {categories:[{requests:[{id, newFiles, newComments, ...}]}]}.
    The signature folds in each request id + its newFiles/newComments counts -
    enough to notice an upload, a deletion, or a new request without a full
    file enumeration. Recompute it from a fresh scrape and compare with
    is_stale().
    """
    parts = []
    for cat in (binder_map or {}).get("categories", []):
        for r in cat.get("requests", []):
            parts.append("%s:%s:%s" % (r.get("id", ""),
                                       r.get("newFiles", 0),
                                       r.get("newComments", 0)))
    parts.sort()
    blob = "|".join(parts).encode("utf-8")
    return hashlib.sha1(blob).hexdigest()


def is_stale(index, fresh_binder_map):
    """True if the portal has moved since the index was built - i.e. the index
    must be rebuilt before it is trusted. True also if there is no index yet."""
    if not index:
        return True
    old = (index.get("freshness") or {}).get("binderSignature")
    return old != binder_signature(fresh_binder_map)


def build(audit_id, client, label, binder_map, request_files):
    """Assemble an index from a binder map and per-request file lists.

    `binder_map`     - map_binder_js result (category/request structure).
    `request_files`  - {requestId: [file dicts]} where each file dict is a
                       normalized record (fmsId, fId, origFileName, fileSize,
                       fileType, portalTs, side). The caller produces these by
                       running get_request_js per request via the `suralink`
                       skill.

    Returns the index dict; the caller saves it with save().
    """
    categories, requests, total = [], [], 0
    for cat in (binder_map or {}).get("categories", []):
        cat_name = cat.get("name", "")
        categories.append(cat_name)
        for r in cat.get("requests", []):
            rid = str(r.get("id", ""))
            files = request_files.get(rid, []) or []
            total += len(files)
            requests.append({
                "requestId": rid,
                "requestName": r.get("name", ""),
                "displayNum": r.get("displayNum", ""),
                "category": cat_name,
                "state": r.get("state", ""),
                "files": files,
            })
    return {
        "auditId": str(audit_id),
        "client": client,
        "label": label,
        "builtAt": _now(),
        "freshness": {"binderSignature": binder_signature(binder_map),
                      "checkedAt": _now()},
        "categories": categories,
        "fileCount": total,
        "requests": requests,
    }


def touch_freshness(index, binder_map):
    """Re-stamp the freshness block after a no-change check (index still valid,
    just confirmed current). Returns the index."""
    index["freshness"] = {"binderSignature": binder_signature(binder_map),
                          "checkedAt": _now()}
    return index


def all_files(index):
    """Flatten the index to a list of file records, each annotated with its
    requestId / requestName / category."""
    out = []
    for r in (index or {}).get("requests", []):
        for f in r.get("files", []):
            out.append({**f,
                        "requestId": r["requestId"],
                        "requestName": r["requestName"],
                        "category": r["category"]})
    return out


def fmsids(index):
    """The set of every fmsId the portal currently holds for this engagement.
    Diff against the manifest to find new files (in index, not manifest) and
    deletions (in manifest for this auditId, not in index)."""
    return {f.get("fmsId") for f in all_files(index) if f.get("fmsId")}
