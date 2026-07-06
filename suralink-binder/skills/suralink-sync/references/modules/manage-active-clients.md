# Module — Manage Active Engagements

**Triggers:** "track this client", "add an engagement to the sync", "stop
syncing X", "which clients am I syncing", "sync last year too", "add this
year's and last year's audit"

## What this does

Edits `active-clients.json` at the mirror root — the engagement list the sync
run touches. Engagement-keyed (`auditId`), so a client's prior-year and
current-year audits can both be active at once. Resolves client **names** to
auditIds via the catalog. The user can also edit the file by hand.

## Prerequisites

Mirror mounted and built (`run-sync.md` Setup steps 1–2). For name resolution:
the `suralink` skill importable and a Chrome tab logged into Suralink.

## List what is tracked
```python
from scripts import active, catalog
eng = active.load(mirror_root)                 # [{auditId, clientId, client, label}]
groups = active.by_client(eng)                 # {clientName: [engagement, ...]}
```

## Add an engagement

**If the user gave a Suralink audit URL** — the `auditId` is the `?auditId=`
value. Look it up in the catalog for the client/label
(`catalog.find_engagement`), then add.

**If the user named a client:**
1. `catalog.find_clients(catalog.load(mirror_root), name)`.
2. No hit → refresh the catalog (`catalog.md`) and retry; still nothing →
   **prompt the user** (misnamed? sensitive/hidden? wrong firm login?).
3. Got the `clientId` → fetch its engagements:
   `suralink.get_client_engagements_js(client_id)` → cache with
   `catalog.set_engagements(...)`.
4. Show the user the client's engagements (e.g. *Audit 2025*, *Audit 2024*) and
   let them pick which to track — they may want **both** last year and this
   year. Add each:
```python
active.add(mirror_root, audit_id, client="Client name",
           label="Audit 2025", client_id=client_id)
```

## Remove an engagement
```python
active.remove(mirror_root, audit_id)
```
Removal only stops future syncing — files already in the mirror stay, and the
manifest keeps their records. Tell the user that.

## Note

`active-clients.json` is local to this machine. It is config — what you intend
to sync; the catalog is the firm roster, the manifest is what was actually
pulled. Adding an engagement here does not sync it — run `run-sync.md` for that.
