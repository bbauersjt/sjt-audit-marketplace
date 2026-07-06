# Module — Binder Map & Activity Timeline

**Triggers:** "map the binder", "binder index", "what's the structure of this engagement", "what's new", "recent uploads", "activity timeline", "the clock feed", "check for new files"

## What this does

Two fast, whole-engagement reads that avoid crawling request-by-request:

- **Binder map** — the full structure (categories → requests) in one DOM scrape.
- **Activity timeline** — Suralink's "clock" feed: every upload/change event.

## Binder map

```python
from scripts import suralink
js = suralink.map_binder_js()      # tab must be on /auditors/views/Audit.php?auditId={X}
```
Returns `{auditId, categories:[{catId, name, order, requests:[{id, displayNum,
name, state, newFiles, newComments, created, due}]}]}` — categories already in
website order. This is the **enumeration of record**: use it instead of looping
`get_request_js` over every request. It works uniformly across clients (a DOM
scrape, not per-request API shapes). It does NOT carry file-level ids — run
`get_request_js` for a specific request only when `fmsId`/`fId` are needed.

## Activity timeline (the clock feed)

```python
js = suralink.load_ian_js(audit_id)        # gateway loadIAN — run sequentially
# parse the result with browser.parse_result()
```
Returns `data.ianData.messages[]` — one entry per activity event, newest first.
Messages with a non-empty `files[]` are uploads; each file object carries `id`
(fId), `fmsId`, `origFileName`, `fileSize`, `requestId`, `ts`.

This is the fast **"what's new"** check — one call, no binder crawl. The
`suralink-sync` skill flattens it with `sync.ian_files()` and diffs against the
manifest by `fmsId`.

## How they combine

`map_binder_js` gives the structure (requestId → category, request name).
`load_ian_js` gives what changed. Cross-reference by `requestId`: the timeline
tells you which files are new; the binder map tells you which category/request
folder they belong in.

## Known failure modes

- Empty binder map / timeline → tab not on `Audit.php`, or session expired (`401`).
- `loadIAN` is a gateway call — run sequentially (Suralink session serializes
  gateway calls; CSRF is read live per call but rarely actually rotates).
- The timeline includes firm-side files too, not only client uploads — filter on
  `userType` / the manifest diff if you only want client files.

## Validated on

- Audit 2774111 — binder map: 9 categories / 28 requests; timeline: 116 messages.
