"""The client catalog - `catalog.json` at the mirror root.

A parseable local roster of the firm's clients and, per client, its engagements
(audits). Distinct from `active-clients.json`:

  - catalog.json     = the WHOLE firm. Every client; engagements filled in as
                       they are needed. The reference Claude resolves names
                       against ("sync Kymera" -> which auditId?).
  - active-clients.json = the SUBSET this machine syncs.

The catalog is created on first need and refreshed on request (or automatically
when a name cannot be resolved - see manage-active-clients.md / catalog.md).

Two tiers, because populating engagements for every client would be hundreds of
gateway calls:
  - the client ROSTER (id, customId, name, state) - cheap, always fully filled.
  - per-client ENGAGEMENTS - filled lazily, the first time a client is touched,
    and cached with a timestamp.

The browser work (enumerating clients, reading engagements) is done by the
`suralink` skill; this module only stores and queries the result.
"""
import json
import os
from datetime import datetime, timezone

CATALOG_NAME = "catalog.json"

_COMMENT = ("The firm's client roster, cached locally. clients[].engagements is "
            "filled in lazily the first time a client is used. Refresh with the "
            "catalog module, or ask Claude. Local to this machine.")


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def catalog_path(mirror_root):
    return os.path.join(mirror_root, CATALOG_NAME)


def default_catalog():
    return {"_comment": _COMMENT, "generatedAt": None,
            "organizationId": None, "clients": []}


def load(mirror_root):
    """Load catalog.json. Returns a fresh empty catalog (NOT yet written) if
    none exists - the caller decides when to build it."""
    p = catalog_path(mirror_root)
    if not os.path.exists(p):
        return default_catalog()
    with open(p, "r", encoding="utf-8") as f:
        cat = json.load(f)
    cat.setdefault("clients", [])
    return cat


def save(mirror_root, catalog):
    """Write catalog.json atomically."""
    p = catalog_path(mirror_root)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)
    os.replace(tmp, p)
    return p


def exists(mirror_root):
    return os.path.exists(catalog_path(mirror_root))


def set_roster(mirror_root, org_id, client_rows):
    """Replace the client roster from a fresh enumeration.

    `client_rows` is the list of client objects from the `suralink` skill's
    list_clients_page_js (each {id, customId, name, state, ...}). Existing
    per-client engagement caches are preserved by clientId where the client is
    still present. Returns the saved catalog.
    """
    old = load(mirror_root)
    old_eng = {str(c.get("clientId")): c for c in old.get("clients", [])}
    clients = []
    for r in client_rows:
        cid = str(r.get("id") or r.get("clientId") or "")
        prev = old_eng.get(cid, {})
        clients.append({
            "clientId": cid,
            "customId": str(r.get("customId") or ""),
            "name": (r.get("name") or "").strip(),
            "state": r.get("state") or "",
            "engagementsFetchedAt": prev.get("engagementsFetchedAt"),
            "engagements": prev.get("engagements", []),
        })
    cat = {"_comment": _COMMENT, "generatedAt": _now(),
           "organizationId": org_id, "clients": clients}
    save(mirror_root, cat)
    return cat


def set_engagements(mirror_root, client_id, engagements):
    """Cache one client's engagement list (from get_client_engagements_js).

    `engagements` is a list of {auditId, name, state, customId}. Stamps
    engagementsFetchedAt. Returns the saved catalog. If the client is not in
    the roster yet, a stub row is added so the engagements are not lost.
    """
    client_id = str(client_id)
    cat = load(mirror_root)
    row = next((c for c in cat["clients"]
                if str(c.get("clientId")) == client_id), None)
    if row is None:
        row = {"clientId": client_id, "customId": "", "name": "",
               "state": "", "engagements": []}
        cat["clients"].append(row)
    row["engagements"] = engagements
    row["engagementsFetchedAt"] = _now()
    save(mirror_root, cat)
    return cat


def find_clients(catalog, query):
    """Return roster rows whose name or customId matches `query` (case-
    insensitive substring). Use to resolve a client the user named."""
    q = (query or "").strip().lower()
    if not q:
        return []
    return [c for c in catalog.get("clients", [])
            if q in (c.get("name", "") or "").lower()
            or q == (c.get("customId", "") or "").lower()]


def find_engagement(catalog, audit_id):
    """Locate one engagement by auditId. Returns {client, clientId, engagement}
    or None. `engagement` is the {auditId, name, state, ...} dict."""
    audit_id = str(audit_id)
    for c in catalog.get("clients", []):
        for e in c.get("engagements", []):
            if str(e.get("auditId")) == audit_id:
                return {"client": c.get("name", ""),
                        "clientId": c.get("clientId"),
                        "engagement": e}
    return None


def all_engagements(catalog):
    """Flatten every known (client, engagement) pair in the catalog."""
    out = []
    for c in catalog.get("clients", []):
        for e in c.get("engagements", []):
            out.append({"clientId": c.get("clientId"),
                        "client": c.get("name", ""),
                        "customId": c.get("customId", ""),
                        "engagement": e})
    return out
