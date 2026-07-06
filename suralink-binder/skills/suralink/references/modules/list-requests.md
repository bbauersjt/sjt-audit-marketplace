# Module — List Requests

**Triggers:** "what requests are in this audit", "show the request list", "what's outstanding", "what has new files"

## What this does

Enumerates the requests (PBC items) inside one audit by reading the live
`Audit.php` DOM. No gateway calls — pure scrape, fast and CSRF-free.

For **clients / engagements** (the firm roster, finding a client, a client's
prior-year vs current-year audits) see `clients-and-engagements.md` — that is a
backend operation, not a DOM scrape.

For the **whole binder** (categories + requests in one structured object)
prefer `binder-and-activity.md :: map_binder_js` over this flat list.

## Prerequisites

- A Chrome tab logged into `app.suralink.com`, on
  `https://app.suralink.com/auditors/views/Audit.php?auditId={X}`. The full
  `/auditors/views/` prefix is required — `app.suralink.com/Audit.php?…`
  returns nginx 404.

## Procedure — requests in an audit

### 1. Make sure the tab is on the audit
Navigate the tab to `https://app.suralink.com/auditors/views/Audit.php?auditId={auditId}` if it is not already.

### 2. Scrape the request list
```python
from scripts import suralink
js = suralink.list_requests_js()   # -> JSON array of request rows
```
Run `js` in the tab. Each row: `{id, newFiles, newComments, created, due, category}`.
`id` is the canonical 8-digit request id. `newFiles > 0` flags requests with unseen client files.

## Known failure modes

- Empty request list → tab is not on `Audit.php`, or the page has not finished rendering. Wait and re-run.
- `window.csrf missing` errors do not apply here — this module makes no gateway calls.

## Validated on

- Audit 2774111 (Kymera 401(k) Plan) — 56 request rows scraped, 2026-05-22.
