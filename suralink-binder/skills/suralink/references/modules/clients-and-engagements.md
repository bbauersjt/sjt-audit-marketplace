# Module — Clients & Engagements

**Triggers:** "list my clients", "what clients do we have", "find the client called X",
"what engagements does this client have", "this year's and last year's audit",
"which auditId is X", "look up a client"

## What this does

Reads the firm's **client roster** and each client's **engagements** from the
Suralink backend — not by scraping `Clients.php` (a React app that renders only
one client at a time), but through the v2 API and the `getClientInfo` gateway.

A **client** owns one or more **engagements** (audits). Prior-year and
current-year audits are sibling `auditId`s under one `clientId`.

## Prerequisites

- A Chrome tab logged into Suralink (any Suralink page works).
- `organizationId` — read once with `get_org_id_js()` and reuse.

## Procedure — enumerate the whole roster

1. Read `organizationId` once:
```python
from scripts import suralink, browser
org = run(suralink.get_org_id_js())                  # GUID string
```
2. Page through the roster until exhausted:
```python
clients, offset = [], 0
while True:
    res  = browser.parse_result(run(suralink.list_clients_page_js(org, 100, offset)))
    body = res["body"]
    clients += body["data"]
    offset  += len(body["data"])
    if offset >= body["totalCount"] or not body["data"]:
        break
```
3. Read each client as `{id, customId, name, state, ...}` — `id` is the `clientId`.
   - Guard: `limit` is capped at 100 server-side — page with `offset`.

## Procedure — resolve a client the user named

1. Run:
```python
res  = browser.parse_result(run(suralink.search_clients_js(org, "ExampleCo")))
hits = res["body"]["clients"]            # [{score, highlight, source}, ...]
```
2. Read `source` as the client object; `source.engagementCounts` gives `{total, active, inactive, archived}`.
3. If there are several hits, show the user the names + `customId`s and let them pick.

## Procedure — a client's engagements

1. Run:
```python
js  = suralink.get_client_engagements_js(client_id)   # run sequentially (session-serialized)
out = json.loads(run(js))
# out = {clientId, engagements:[{auditId, name, state, customId}]}
```
2. Read `state` as `Active` / `Inactive` / `Archived`. Each `auditId` is an engagement the `Audit.php` modules operate on.

## Known failure modes

- `get_org_id_js()` returns `''` → not on a Suralink page, or not logged in.
- `search_clients_js` with an empty term → HTTP 400. Use it only with a real term.
- `getClientInfo` `Invalid Csrf Token` / `missingParameter` → rare; re-read
  `window.csrf` and retry. Run gateway calls sequentially anyway — Suralink's
  session serializes them. See `architecture.md` → CSRF handling.
- Engagement rows show **Active** engagements; a client with inactive/archived
  audits reports them in `engagementCounts` (from `search_clients_js`).
