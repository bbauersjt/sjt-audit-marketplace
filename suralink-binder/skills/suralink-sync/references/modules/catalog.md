# Module — The Client Catalog

**Triggers:** "refresh the catalog", "rebuild the client list", "list all my
clients", "the client list is stale / out of date", "find the client called X",
"which clients do we have"

## What this does

Builds and maintains `catalog.json` at the mirror root — a parseable local copy
of the firm's whole client roster, and (lazily) each client's engagements. It
is what client **names** resolve against when adding to the sync or navigating
to a client. See `../architecture.md` "catalog.json".

## Prerequisites

- Mirror mounted and built (see `run-sync.md` Setup steps 1–2).
- The `suralink` skill importable; a Chrome tab logged into Suralink.

## Procedure — build / refresh the roster

```python
from scripts import catalog, location
import suralink, browser                       # the suralink skill

org = run(suralink.get_org_id_js())            # firm GUID

rows, offset = [], 0
while True:
    res  = browser.parse_result(run(suralink.list_clients_page_js(org, 100, offset)))
    body = res["body"]
    rows += body["data"]
    offset += len(body["data"])
    if offset >= body["totalCount"] or not body["data"]:
        break

catalog.set_roster(mirror_root, org, rows)     # writes catalog.json
```
`set_roster` preserves any per-client engagement caches already collected.

## Procedure — resolve a client the user named

```python
cat  = catalog.load(mirror_root)
hits = catalog.find_clients(cat, "Kymera")     # name OR customId, substring, ci
```
- One hit → use it.
- Several → show the user names + `customId`s, let them pick.
- **None → the catalog may be stale.** Refresh the roster (above) and retry. If
  still nothing, fall back to a live `suralink.search_clients_js(org, term)` —
  and tell the user the catalog did not have it.

## Procedure — fill in a client's engagements

The roster does not carry engagements until a client is touched:
```python
js  = suralink.get_client_engagements_js(client_id)   # run sequentially (session-serialized)
eng = json.loads(run(js))["engagements"]
catalog.set_engagements(mirror_root, client_id, eng)  # caches into catalog.json
```

## When to refresh automatically

Refresh the roster without being asked when: (a) a name will not resolve, or
(b) the user asks to navigate to / sync a client that is not in the catalog —
refresh, retry, and if it still is not found, **prompt the user** (the client
may be misnamed, sensitive/hidden, or under a different firm login).

## Known failure modes

- `get_org_id_js()` → `''` — not on a Suralink page, or not logged in.
- Roster paging stops early — `limit` is capped at 100; always page by `offset`.
- `getClientInfo` `Invalid Csrf Token` — rare; re-read `window.csrf` and
  retry. Run gateway calls sequentially anyway — Suralink's session
  serializes them. See the `suralink` skill's `architecture.md`.

## Validated on

- Firm `f65b4c53…` — 249-client roster, 2026-05-23.
