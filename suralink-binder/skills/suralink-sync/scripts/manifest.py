"""The manifest - `_suralink_sync.json` at the mirror root.

Machine-written state: every file ever pulled on THIS computer, keyed by its
Suralink `fmsId`. It is the single source of truth for "have I already got
this file?". It is local and independent - each machine keeps its own.

The active-client list is NOT here - that lives in `active-clients.json`
(see active.py). The catalog is NOT here either - that is `catalog.json`
(see catalog.py). The manifest is STATE; those two are CONFIG.

Deleted files. When a file that was pulled later disappears from the portal
(detected by absence - see ../references/architecture.md and sync.detect_deletions),
its manifest record is TOMBSTONED: `deletedInPortal` + `deletedDetectedAt` are
set. The local copy is NEVER removed - chain of custody. A tombstoned file
stays "known" so it is not re-pulled if it reappears under the same fmsId.

See ../references/architecture.md.
"""
import json
import os
from datetime import datetime, timezone

MANIFEST_NAME = "_suralink_sync.json"


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def manifest_path(mirror_root):
    return os.path.join(mirror_root, MANIFEST_NAME)


def default_manifest(mirror_root):
    return {
        "version": 4,
        "lastSync": None,
        "mirrorRoot": os.path.abspath(mirror_root),
        # stagingDir is the HOST-side path (e.g. C:\Users\…\Downloads or
        # …\Suralink Mirror\_inbox) — what the user sees and configures
        # Chrome's download location to. Stable across sandbox sessions.
        # Sandbox/runtime path is derived from the live mount, not stored.
        "stagingDir": None,
        "files": {},
    }


def load(mirror_root):
    """Load the manifest. Returns a fresh default (NOT yet written) if none
    exists - first run on a new machine starts clean.

    Performs in-place migrations on older versions:
    - v3 → v4: rename `lastSyncAt` → `lastSync` if both exist (the older
      field was dead — readers/writers had drifted to `lastSync`).
    """
    p = manifest_path(mirror_root)
    if not os.path.exists(p):
        return default_manifest(mirror_root)
    with open(p, "r", encoding="utf-8") as f:
        m = json.load(f)
    m.setdefault("files", {})
    m.setdefault("stagingDir", None)
    # Migration: drop legacy `lastSyncAt`. The current field is `lastSync`.
    if "lastSyncAt" in m:
        if m.get("lastSync") is None and m["lastSyncAt"]:
            m["lastSync"] = m["lastSyncAt"]
        m.pop("lastSyncAt", None)
    m["mirrorRoot"] = os.path.abspath(mirror_root)
    return m


def save(mirror_root, manifest):
    """Write the manifest atomically (temp file + replace)."""
    p = manifest_path(mirror_root)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    os.replace(tmp, p)
    return p


def is_known(manifest, fms_id):
    """True if this file (by fmsId) has already been pulled on this machine.
    A tombstoned (deleted-in-portal) file still counts as known."""
    return bool(fms_id) and fms_id in manifest.get("files", {})


def record_file(manifest, fms_id, info):
    """Add/replace a file record. `pulledAt` is stamped automatically.
    Recording a file clears any prior tombstone (it is present again)."""
    info = dict(info)
    info["pulledAt"] = _now()
    info.pop("deletedInPortal", None)
    info.pop("deletedDetectedAt", None)
    manifest.setdefault("files", {})[fms_id] = info
    return manifest


def mark_deleted(manifest, fms_id):
    """Tombstone a file: it was pulled before but is no longer in the portal.
    Sets deletedInPortal + deletedDetectedAt; the local copy is left untouched.
    No-op if the fmsId is unknown or already tombstoned. Returns True if it
    newly tombstoned the record."""
    rec = manifest.get("files", {}).get(fms_id)
    if not rec or rec.get("deletedInPortal"):
        return False
    rec["deletedInPortal"] = True
    rec["deletedDetectedAt"] = _now()
    return True


def is_deleted(manifest, fms_id):
    """True if this file is tombstoned (deleted in the portal)."""
    rec = manifest.get("files", {}).get(fms_id)
    return bool(rec and rec.get("deletedInPortal"))


def files_for_audit(manifest, audit_id):
    """Every manifest record belonging to one engagement, {fmsId: record}.
    Used by sync.detect_deletions to diff against a fresh portal enumeration."""
    audit_id = str(audit_id)
    return {fid: r for fid, r in manifest.get("files", {}).items()
            if str(r.get("auditId")) == audit_id}


def tombstones(manifest):
    """Every tombstoned file record, {fmsId: record}. For reporting."""
    return {fid: r for fid, r in manifest.get("files", {}).items()
            if r.get("deletedInPortal")}


def stamp_sync(manifest):
    manifest["lastSync"] = _now()
    return manifest


def set_staging(manifest, host_path):
    """Record the HOST-side staging directory — the path the user sees on
    their computer (e.g. `C:\\Users\\bbauer\\Downloads` or
    `~/Documents/Suralink Mirror/_inbox`). Do NOT pass a sandbox path
    like `/sessions/<sid>/mnt/...` — those rotate per session and break
    the manifest across runs.

    The runtime (wait_for_download) takes the sandbox path directly from
    the caller, not from here.
    """
    manifest["stagingDir"] = host_path if host_path else None
    return manifest
