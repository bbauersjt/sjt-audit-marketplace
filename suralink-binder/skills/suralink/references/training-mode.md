# Training Mode — Script-First Capture Protocol

For Claude sessions extending the `suralink` skill — either because the user said "listen for this" / "we're doing something new", or because a Suralink task has no matching module.

**Terminal state of training mode is NOT a markdown how-to.** It is:

1. A tested function in `scripts/*.py` that performs the operation, and
2. A JSON spec in `references/endpoints/*.json`, and
3. A thin module in `references/modules/*.md` that calls the script.

Markdown describing how to do the operation by hand is a failure state.

## The fallback ladder (strict order)

Work DOWN this ladder. Skip a rung only if it is impossible, never because it is easier.

### Rung 1 — already known
The endpoint is in `architecture.md` and a `scripts/*.py` function exists. Use it.

### Rung 2 — capture, then script
1. Install the capture patch: run `scripts/capture.py :: INSTALL_CAPTURE_JS` in the tab.
2. Have the user perform ONE real UI action — the exact thing to learn. Do not speculate.
3. Read it back with `scripts/capture.py :: summarize_capture_js()`, then `read_command_js(i)` for the call of interest.
4. **Replay programmatically to confirm** — build the call with `browser.js_gateway()` or `browser.js_get_json()` and check the response matches the UI.
5. **Verify the side effect** with a follow-up read.
6. **Codify:** add a function to `scripts/*.py`, a spec to `references/endpoints/*.json`, update `architecture.md` if a platform fact was learned, then write the thin module.

### Rung 3 — UI clicking (last resort)
Only if the operation genuinely cannot be done by HTTP. Drive the UI with Claude in Chrome tools, but keep the capture patch installed and promote any real mutation call to Rung 2 afterward.

## Capture environment — hard-won facts

- **A full page reload wipes the capture patch.** Re-install after any reload. Never ask the user to reload mid-capture.
- **`read_network_requests` is unreliable** — its buffer clears on Suralink's `pushState` request-id changes. The `window.__sl` monkey-patch in `capture.py` is the reliable channel.
- **The Cowork content filter blocks raw URLs, query strings and tokens** in tool output ("[BLOCKED: Cookie/query string data]"). Never dump a captured URL or response body directly. Use `summarize_capture_js()` / `read_command_js()`, which emit only sanitized derivatives (ids masked, param names not values). When extracting anything else, strip `?...` query strings and mask long alphanumeric runs first.
- Suralink is cookie-authed — there is never a bearer token to capture. The only "secret" is the static gateway value `aud1tMgr!` and the rotating `window.csrf` pair, both already known.

## Already known — do NOT rediscover

Everything in `architecture.md`: the two hosts, cookie auth, the interchangeable gateway letter, the static `aud1tMgr!` secret, `window.csrf` holding `csrf_token` + `csrf_hash_offset` (rotating), the request `id` vs `requestId` trap, fileProxy's `rId` requirement, fileProxy's `fId=-1` ping. Those are settled facts.

## Known unknowns (open work items)

| Capability | Listen for |
|---|---|
| The gateway/API call that bulk-loads a request list on `Audit.php` open | "refresh the list", first time enumeration via DOM is not enough |
| v2 request-item detail — does `/v2/organization/{org}/requestList/{aud}/requestItem/{itemId}` return the file list? (would replace the `getRequest` gateway call) | confirm during any download work |
| Upload a file to a request (respond to a PBC item) | "upload to Suralink", "send the client a file", "respond to the request" |
| Mark a request fulfilled / change request state | "mark it received", "close the request", "accept the file" |
| Categories & subcategories — the human names behind `data-firstletter` | "group by category", "which section" |

When a known unknown lands, run the ladder. Do not shortcut to a markdown how-to.

### Resolved / closed

- **Client & engagement enumeration** — done. See `architecture.md` "Clients &
  engagements" and `modules/clients-and-engagements.md`. (`list_clients_js`, the
  old best-effort `Clients.php` DOM scrape, is superseded — `Clients.php` is a
  React app and cannot be scraped as a roster.)
- **Bulk-zip export endpoint** — the select-all → Download → zip trigger evades
  every capture hook (fetch, XHR, form-submit, anchor-click, window.open,
  iframe-src). Treat it as **UI-only, not scriptable**; do not re-attempt without
  a genuinely new approach. Fully scripted bulk pulls use the per-file
  `fileProxy` loop instead.

## Module template

```markdown
# Module — <Verb Noun>
**Triggers:** "phrase", "phrase", "phrase"
## What this does
<one paragraph>
## Prerequisites
- <list>
## Procedure
### 1. <step>
` ` `python
from scripts import suralink
js = suralink.<function>(...)
` ` `
### N. Verify
<confirm the side effect>
## Known failure modes
- <symptom> -> <cause> -> <fix>
```

Hard rule: no JavaScript snippet longer than ~5 lines inside a module. Non-trivial JS lives in a script; the module shows the Python call that produces it.
