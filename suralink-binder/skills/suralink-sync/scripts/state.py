"""The per-sync state file — `_suralink_sync.json`, living INSIDE the sync folder.

A "sync" IS a folder. Everything the skill needs to remember about it lives in
this one file at the folder's root — there is NO global state anywhere: no
client roster, no active-engagement list, no remembered mirror root, no config
pointer. Point the skill at a folder; if this file is present it tells the skill
exactly what the folder mirrors and what it already holds. Absent → the folder
is not a sync yet (resolve one live and write it — see resolve-target.md).

This is what makes the skill distributable: nothing client-specific is ever
stored centrally or shipped with the skill. Each synced folder is entirely
self-describing and travels with its own memory.

Contents
--------
    {
      "version": 5,
      "binding": {                 # which Suralink engagement this folder is
        "orgId":    "...",
        "clientId": "...",
        "client":   "Client name",
        "auditId":  "...",
        "label":    "Audit 2025",
        "auditUrl": "https://app.suralink.com/auditors/views/Audit.php?auditId=..."
      },
      "stagingDir": "C:\\Users\\...\\Downloads",   # HOST path Chrome downloads to
      "lastSync":   "2026-07-14T...Z",
      "files": {                   # every file pulled here, keyed by fmsId
        "<fmsId>": { ...record..., "pulledAt": "...", ["deletedInPortal": true] }
      }
    }

The companion `_index.json` (index.py) snapshots what the PORTAL currently
holds; THIS file records what has been PULLED to disk. Diffing the two is how
"what's new" and "what was deleted" are computed.

Deleted files are TOMBSTONED here (`deletedInPortal` + `deletedDetectedAt`), never
removed from disk — chain of custody. A tombstoned file stays "known" so it is
not re-pulled if it reappears under the same fmsId.
"""
import json
import os
from datetime import datetime, timezone

STATE_NAME = "_suralink_sync.json"
VERSION = 5


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --- the file ------------------------------------------------------------

def state_path(sync_root):
    """Absolute path of the state file at the root of one sync folder."""
    return os.path.join(os.path.abspath(sync_root), STATE_NAME)


def default_state(binding=None):
    """A fresh, unsaved state dict. `binding` is the engagement this folder
    mirrors (see set_binding); pass it on first creation or fill it later."""
    return {
        "version": VERSION,
        "binding": dict(binding or {}),
        "stagingDir": None,
        "lastSync": None,
        "files": {},
    }


def load(sync_root):
    """Load a folder's state, or None if the folder is not a sync (no state
    file). `None` is the definitive "this folder has never been synced" signal
    the resolver keys on."""
    p = state_path(sync_root)
    if not os.path.exists(p):
        return None
    with open(p, "r", encoding="utf-8") as f:
        s = json.load(f)
    s.setdefault("version", VERSION)
    s.setdefault("binding", {})
    s.setdefault("stagingDir", None)
    s.setdefault("files", {})
    return s


def exists(sync_root):
    """True iff this folder already carries a sync (a state file)."""
    return os.path.exists(state_path(sync_root))


def save(sync_root, state):
    """Write the state file atomically (temp + replace)."""
    os.makedirs(os.path.abspath(sync_root), exist_ok=True)
    p = state_path(sync_root)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True)
    os.replace(tmp, p)
    return p


# --- the binding (which engagement this folder mirrors) ------------------

def get_binding(state):
    """The engagement binding dict {orgId, clientId, client, auditId, label,
    auditUrl}, or {} if not set yet."""
    return (state or {}).get("binding", {}) or {}


def set_binding(state, *, org_id=None, client_id=None, client=None,
                audit_id=None, label=None, audit_url=None):
    """Set/patch the engagement binding. Only the fields passed are changed;
    others are left as-is. `audit_url` defaults to the standard Audit.php view
    for `audit_id` when the id is given and no url is passed."""
    b = state.setdefault("binding", {})
    if org_id is not None:
        b["orgId"] = str(org_id)
    if client_id is not None:
        b["clientId"] = str(client_id)
    if client is not None:
        b["client"] = client
    if label is not None:
        b["label"] = label
    if audit_id is not None:
        b["auditId"] = str(audit_id)
        if audit_url is None and not b.get("auditUrl"):
            b["auditUrl"] = audit_view_url(audit_id)
    if audit_url is not None:
        b["auditUrl"] = audit_url
    return state


def audit_id(state):
    """The bound auditId, or None."""
    return get_binding(state).get("auditId")


def audit_view_url(audit_id):
    """The canonical Suralink engagement view URL. The full `/auditors/views/`
    path is REQUIRED — a bare `Audit.php?…` returns nginx 404."""
    return ("https://app.suralink.com/auditors/views/Audit.php?auditId="
            + str(audit_id))


# --- staging + timestamps ------------------------------------------------

def set_staging(state, host_path):
    """Record the HOST-side staging dir (what the user sees on their computer,
    e.g. C:\\Users\\…\\Downloads). Never a `/sessions/.../mnt/...` sandbox path —
    those rotate per session. The runtime wait helper takes the sandbox path
    directly from the caller; this just records Chrome's configured target."""
    state["stagingDir"] = host_path or None
    return state


def stamp_sync(state):
    state["lastSync"] = _now()
    return state


# --- the file records (what has been PULLED here) ------------------------

def is_known(state, fms_id):
    """True if this file (by fmsId) has already been pulled into this folder.
    A tombstoned (deleted-in-portal) file still counts as known."""
    return bool(fms_id) and fms_id in (state or {}).get("files", {})


def record_file(state, fms_id, info):
    """Add/replace a file record. `pulledAt` is stamped automatically.
    Recording a file clears any prior tombstone (it is present again)."""
    info = dict(info)
    info["pulledAt"] = _now()
    info.pop("deletedInPortal", None)
    info.pop("deletedDetectedAt", None)
    state.setdefault("files", {})[fms_id] = info
    return state


def mark_deleted(state, fms_id):
    """Tombstone a file: pulled before, no longer in the portal. Local copy is
    left untouched. No-op if unknown or already tombstoned. Returns True if it
    newly tombstoned the record."""
    rec = state.get("files", {}).get(fms_id)
    if not rec or rec.get("deletedInPortal"):
        return False
    rec["deletedInPortal"] = True
    rec["deletedDetectedAt"] = _now()
    return True


def is_deleted(state, fms_id):
    """True if this file is tombstoned (deleted in the portal)."""
    rec = state.get("files", {}).get(fms_id)
    return bool(rec and rec.get("deletedInPortal"))


def tombstones(state):
    """Every tombstoned file record, {fmsId: record}. For reporting."""
    return {fid: r for fid, r in (state or {}).get("files", {}).items()
            if r.get("deletedInPortal")}


# --- discovery -----------------------------------------------------------

def find_syncs(folder, max_depth=2):
    """Find existing sync roots at or under `folder`.

    A sync root is any directory that contains a `_suralink_sync.json`. This is
    the discovery primitive: point at a mounted project folder (or an
    engagements/<client> folder) and see whether it already holds a sync — a
    match means "update this one", no match means "set up a new sync here".

    Scans `folder` itself (depth 0) and descends up to `max_depth` levels — so a
    project folder holding a `2025 Suralink Folder/` subfolder is found. Returns
    absolute sync-root paths, shallowest first (so the folder itself, if it is a
    sync, ranks before any nested one). Skips dotfolders and the `_raw`/`sorted`
    working trees so a deep scan stays cheap.
    """
    folder = os.path.abspath(folder)
    found = []
    if not os.path.isdir(folder):
        return found
    _SKIP = {"_raw", "sorted", "__pycache__"}

    def walk(d, depth):
        try:
            entries = sorted(os.listdir(d))
        except OSError:
            return
        if STATE_NAME in entries and os.path.isfile(os.path.join(d, STATE_NAME)):
            found.append(d)
        if depth >= max_depth:
            return
        for name in entries:
            if name.startswith(".") or name in _SKIP:
                continue
            sub = os.path.join(d, name)
            if os.path.isdir(sub):
                walk(sub, depth + 1)

    walk(folder, 0)
    # shallowest first
    found.sort(key=lambda p: p.count(os.sep))
    return found
