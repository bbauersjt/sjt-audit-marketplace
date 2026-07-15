# Module — Binder Map & Activity Timeline

**Triggers:** "map the binder", "binder index", "what's the structure of this engagement", "what's new", "recent uploads", "activity timeline", "the clock feed", "check for new files"

## What this does

Two fast, whole-engagement reads that avoid crawling request-by-request:

- **Binder map** — the full structure (categories → requests) in one DOM scrape.
- **Activity timeline** — Suralink's "clock" feed: every upload/change event.

## Binder map

1. Ensure the tab is on `/auditors/views/Audit.php?auditId={X}`.
2. Run:
```python
from scripts import suralink
js = suralink.map_binder_js()
```
3. Read the result: `{auditId, categories:[{catId, name, order, requests:[{id, displayNum, name, state, newFiles, newComments, created, due}]}]}` — categories already in website order.
   - Use this as the **enumeration of record** instead of looping `get_request_js` over every request. It works uniformly across clients (a DOM scrape, not per-request API shapes).
   - Guard: it does NOT carry file-level ids — run `get_request_js` for a specific request only when `fmsId`/`fId` are needed.

## Activity timeline (the clock feed)

1. Run:
```python
js = suralink.load_ian_js(audit_id)        # gateway loadIAN — run sequentially
```
2. Parse the result with `browser.parse_result()`.
3. Read `data.ianData.messages[]` — one entry per activity event, newest first. Messages with a non-empty `files[]` are uploads; each file object carries `id` (fId), `fmsId`, `origFileName`, `fileSize`, `requestId`, `ts`.
   - This is the fast **"what's new"** check — one call, no binder crawl. The `suralink-sync` skill flattens it with `sync.ian_files()` and diffs against the manifest by `fmsId`.

## How they combine

1. Run `map_binder_js` for the structure (requestId → category, request name).
2. Run `load_ian_js` for what changed.
3. Cross-reference the two by `requestId`: the timeline tells you which files are new; the binder map tells you which category/request folder they belong in.

## Known failure modes

- Empty binder map / timeline → tab not on `Audit.php`, or session expired (`401`).
- Wrong-audit data → the tab was on a DIFFERENT auditId than requested (stale tab
  or login-bounce `returnTo`). Run `suralink.verify_audit_js(audit_id)` before the
  scrape and require `ok:true` (architecture.md → "Session verification").
- `loadIAN` is a gateway call — run sequentially (Suralink session serializes
  gateway calls; CSRF is read live per call but rarely actually rotates).
- The timeline includes firm-side files too, not only client uploads — filter on
  `userType` / the manifest diff if you only want client files.
