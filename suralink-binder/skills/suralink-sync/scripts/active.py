"""The active-client list - `active-clients.json` at the mirror root.

A plain, human-editable file: the user can open it in any text editor and add
or remove engagements by hand, or ask Claude to. It is per-machine and
independent - each computer keeps its own list. The sync run reads this file
to decide which engagements to touch.

Keyed by `auditId` - one entry per ENGAGEMENT, not per client. So a client's
prior-year and current-year audits can both be active at once (last year and
this year in tow together); they are two entries that share a `clientId`.
`by_client()` groups them for display.

The full firm roster lives in `catalog.json` (catalog.py) - this file is just
the subset being synced. Resolve a client name -> auditId against the catalog,
then add the engagement here.
"""
import json
import os

ACTIVE_NAME = "active-clients.json"

_COMMENT = ("Engagements THIS machine syncs from Suralink. One entry per "
            "engagement (auditId). Sibling auditIds with the same clientId are "
            "the same client's different-year audits. Edit by hand or ask "
            "Claude. Local to this computer; not shared with any other machine.")


def active_path(mirror_root):
    return os.path.join(mirror_root, ACTIVE_NAME)


def load(mirror_root):
    """Return the list of active engagements
    [{auditId, clientId, client, label}, ...]. Creates a starter file
    (empty list) if none exists."""
    p = active_path(mirror_root)
    if not os.path.exists(p):
        save(mirror_root, [])
        return []
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):                 # tolerate a bare list
        return data
    return data.get("engagements", [])


def save(mirror_root, engagements):
    """Write the active list atomically, with the help comment preserved."""
    p = active_path(mirror_root)
    doc = {"_comment": _COMMENT, "engagements": engagements}
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
    os.replace(tmp, p)
    return p


def add(mirror_root, audit_id, client, label="", client_id=""):
    """Add an engagement (no-op if its auditId is already listed).

    `client_id` ties the engagement to its client so sibling-year audits group
    together and the mirror folder can be laid out {Client}/{Label}/.
    """
    audit_id = str(audit_id)
    eng = load(mirror_root)
    if not any(str(e.get("auditId")) == audit_id for e in eng):
        eng.append({"auditId": audit_id, "clientId": str(client_id or ""),
                    "client": client, "label": label})
        save(mirror_root, eng)
    return eng


def remove(mirror_root, audit_id):
    """Remove an engagement. Files already mirrored stay - history is kept."""
    audit_id = str(audit_id)
    eng = [e for e in load(mirror_root)
           if str(e.get("auditId")) != audit_id]
    save(mirror_root, eng)
    return eng


def is_active(mirror_root, audit_id):
    """True if this auditId is on the active list."""
    audit_id = str(audit_id)
    return any(str(e.get("auditId")) == audit_id for e in load(mirror_root))


def by_client(engagements):
    """Group an active list into {clientName: [engagement, ...]} so a sync run
    can report per client (e.g. 'Kymera: Audit 2024, Audit 2025'). Order of
    first appearance is preserved."""
    groups = {}
    for e in engagements:
        groups.setdefault(e.get("client", "") or "(unknown client)", []).append(e)
    return groups
