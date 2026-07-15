---
summary: Pick the transport for browser work by TARGET ORIGIN, then by VERB. chrome-bridge is PRIMARY for ALL origins — engagement/WPM/workbench/FP via in-page verbs, and knowledgecoach (KC) via chrome_api_call (the service-worker fetch verb, CSP-exempt). The linked Claude-in-Chrome tab is the FALLBACK everywhere (used when the bridge/extension is unavailable). The bridge's IN-PAGE verbs (chrome_eval, chrome_fetch) stay CSP-blocked on KC — for KC use chrome_api_call. The rest of the skill stays transport-agnostic.
triggers:
  - "(internal) transport selection — consulted from SKILL.md Step 0 and session-bootstrap.md"
status: BRIDGE=primary for ALL origins — engagement/WPM/workbench/FP via in-page verbs + KC via chrome_api_call/SW-fetch (read+write+submit+diagnostics); LINKED-TAB=fallback everywhere (CSP only blocks the bridge's IN-PAGE verbs on KC, never chrome_api_call)
---
# Runbook — Transport selection (route by origin, then verb)

> **GATE — the page-context transport below is the ONLY sanctioned path; using it presumes Step 0
> ran.** Reading this file is not initialization. Do NOT hand-forge external HTTP calls with copied
> headers — execute in the bridged tab's page context (`chrome_api_call` SW-fetch / `chrome_eval`+XHR)
> so session/XSRF ride along. (ONE documented exception: KC/WPM auth is pure header-bearer — no
> cookies, no XSRF — so the **curl-from-Bash wire-captured-bearer path** below is sanctioned, and
> is the PREFERRED KC pattern when the user's tabs are throttled.) If you have ALREADY made platform calls this session without Step 0
> (`session-bootstrap.md`): **STOP now** — run Step 0 in full, switch to this transport, RE-VERIFY BY
> READ everything written while side-entered (200s may be silent no-ops), then resume from the last
> verified step. (SKILL.md → "Initialization gate".)

## Bounded execution — HARD RULES for every injected eval (any origin, any transport)

These are hard rules, not style preferences — skipping one wedges or silently fails the agent.
They apply to every `chrome_eval` / `javascript_tool` payload that executes
platform operations.

1. **≤10 operations per injected eval.** Never assemble one giant payload ("the walk") that
   creates/moves/writes everything in a single eval. Split the op list into chunks of at most
   10 and run them as separate evals.
2. **Mandatory JS-side timeout — every eval must ALWAYS return.** Wrap the work in
   `Promise.race` against a 30–60s timer (default ~45s) so the tool round returns *something*
   even when a call hangs. An eval that can hang forever blocks the agent mid-tool-call: it
   goes silent AND unreachable (queued messages only deliver at the next tool round) and only
   a kill recovers it. Pattern:
   ```js
   const r = await Promise.race([runOps(), new Promise(res => setTimeout(() => res({timedOut: true}), 45000))]);
   return JSON.stringify(r);
   ```
3. **Verify each chunk BY READ before sending the next.** Re-GET what the chunk claims to have
   written; resume from the last verified op after any failure — never blind-repeat writes.
4. **One-line progress note between chunks.** On delegated/background runs this is the
   heartbeat the parent session's supervision feeds on; silence reads as a stall.
5. **Batch ops beat call loops.** Before chunking N single calls, check whether a batch call
   exists for the operation (`wpm.move` takes an `items` LIST — 2 PUTs filed 19 objects live;
   `kc_add_forms` takes the whole form array). Chunk the batch payload, don't loop singles.

**Validate every response by BODY SHAPE, never by HTTP status.** CCH answers **200 with an
error or HTML body** when the transport or auth is wrong — a silent no-op that looks like
success. Real examples: a body starting `<!DOCTYPE html` (login/error page where JSON was
expected), or a JSON error wrapper (`{"message": "An error has occurred..."}`,
`{"result": null, "statusCode": ...}`). A write's 200 means *accepted*, not *applied*
(architecture.md) — success = the expected JSON shape in the body AND a re-GET showing the
change. Anything "written" during a 200-error stretch gets RE-VERIFIED BY READ before you
build on it.

## Bridge is PRIMARY everywhere; linked tab is the FALLBACK

Detect the bridge ONCE per session (below). If it's up, it is the preferred transport for **every**
origin — including knowledgecoach. The linked Claude-in-Chrome tab is the fallback used only when the
bridge/extension is unavailable.

The ONE origin-specific rule is a VERB rule, not an origin ban:

- **knowledgecoach.cchaxcess.com (KC origin)** → use **`chrome_api_call`** (the service-worker fetch
  verb). It is **CSP-exempt** (the SW context is not subject to the page CSP) and **CORS-bypassed**
  for hosts in the extension `host_permissions` (`*.cchaxcess.com`). It drives the full KC pipeline —
  GET form, GetBinder, `UpdateProperty`, spawn, `submit`, refresh, diagnostics. Pass the captured
  KC bearer + **`IdToken`** (capital-I/lower-d/capital-T) in `headers`
  (the SW has no in-page auth). The bridge's **in-page** verbs (`chrome_eval`, `chrome_fetch`) ARE
  CSP-blocked on KC (no `unsafe-eval`, blocked in MAIN and ISOLATED worlds) — never use them on KC;
  `chrome_api_call` is the KC bridge path. Linked-tab fallback if the bridge is down.
- **engagement / WPM / workbench-api / financialprep-api** → **BRIDGE PRIMARY**, linked-tab fallback.
  Cross-origin engagement→WPM/FP in-page calls fail fetch CORS preflight, so for in-page work KEEP the
  `chrome_eval`+XHR builder; or use `chrome_api_call` (SW, CORS-bypassed) directly with captured headers.

## Detect (first browser op of the session)

Call `chrome_bridge_status` (MCP tool, chrome-bridge plugin).
- Returns a `role` and the server is up → **BRIDGE** transport (all origins).
- Tool absent / errors / no server → **LINKED-TAB** transport (the Claude-in-Chrome flow, unchanged
  from prior versions). Remember the choice for the session.

## Operation -> tool map

> Bridge column is preferred for ALL origins when the bridge is up. KC-origin ops use **`chrome_api_call`**
> in the bridge column (NOT `chrome_eval`/`chrome_fetch`, which are CSP-blocked on KC). Linked-tab column
> is the fallback.

| Operation | BRIDGE (preferred) | LINKED-TAB (fallback) |
|---|---|---|
| **KC-origin read/write** (KC form GET, GetBinder, `UpdateProperty`, spawn, `submit`, diagnostics) | **`chrome_api_call(url, method, headers, body)`** — SW fetch, CSP-exempt + CORS-bypassed; pass KC bearer + `IdToken` in headers. **Throttled-tab sessions: curl-from-Bash with the wire-captured bearer** (section below) | the linked Claude-in-Chrome tab on a `knowledgecoach.cchaxcess.com` tab (same endpoints/builders) |
| Find the CCH tab | `chrome_list_tabs` -> pick by URL (returns id+url+title for ALL real tabs, incl. the user's own) | `tabs_context_mcp` + `tab_probe_js` + `claim_tab_js` (session.py) |
| Run JS in page (engagement origin only) | `chrome_eval(code, target=tabId)` | `mcp__Claude_in_Chrome__javascript_tool(code, tabId)` |
| Backend API call (any origin) | `chrome_api_call(url, headers=captured)` — SW, CORS-bypassed for *.cchaxcess.com (cleanest); OR `chrome_eval` + http_runner XHR builder for engagement-origin in-page | `javascript_tool` running the same builder |
| Same-origin GET (text) | `chrome_fetch` (engagement origin) / `chrome_api_call` (any) | `javascript_tool` + `build_fetch_call` |
| Download a file (binary) | `chrome_download(url, out_path, target)` — writes the file to disk | `wpm.download_to_browser_js` -> Downloads folder (then mount it) |
| Upload a file | **`chrome_upload(local_path, url, field_name="file", headers=captured)`** — verified full WPM upload pipeline (see below) | in-page FormData/base64 XHR via `javascript_tool` (file-io.md) |
| Navigate / open / close tab | `chrome_navigate` / `chrome_open_tab` / `chrome_close_tab` | `navigate` / `tabs_create_mcp` / `tabs_close_mcp` |
| Capture the bearer | `chrome_network_recent(host_filter)` — webRequest auto-captures it off live API calls; **no monkeypatch, no provoke**. User-scoped; reuse across the batch | install monkeypatch (auth_capture.py) + provoke one boot XHR |
| KC localStorage auth | pass tokens from `chrome_network_recent` to `chrome_api_call` for KC | `javascript_tool` with the `ls:*` sentinel |

## chrome_api_call body — dict OR string both work (fix shipped)

`chrome_api_call` accepts `body` as a JSON **string or a dict** — `server.py` `json.dumps`'s a dict
before forwarding, and the extension self-serializes non-string bodies as a second net (verified in
code; the old "server rejects a dict / json.dumps at the call site" rule is OBSOLETE).
Passing the builders' dict output directly is fine. If an arg layer ever mangles an inline JSON
object, pass it pre-serialized — but that is a fallback, not the rule.

**⚠ Top-level JSON ARRAY bodies are NOT covered — do not fight `chrome_api_call` on them.** Some
endpoints take a bare JSON array as the whole body (the KC **add-forms batch**
`POST knowledgecoach.cchaxcess.com/api/binder/{guid}` — body is `[ {form}, {form}, … ]`, not an
object). The tool's
`body.str` validation **rejects a Python list** (`Input should be a valid string`), and passing the
array as a **stringified** JSON literal **double-encodes** — the array arrives on the wire as a JSON
*string*, and the server returns **400** (a 200 here is likewise the wrong shape — validate by body,
not status). Resolution used in-run: POST it via an **in-page same-origin XHR** on a tab already on
the KC origin (`chrome_eval`, controlling `JSON.stringify` yourself so the raw array — not a quoted
string — hits the wire) with a freshly-captured KC bearer. **Flagged for revalidation / a proper
`array_body` path** — until then, array-bodied writes take the in-page-XHR route, never a bare
`chrome_api_call(body=[...])`.

## curl-from-Bash with a wire-captured bearer — the preferred KC auth pattern

KC and WPM auth is **pure header-bearer** — no cookies, no XSRF — so a captured token works from
ANY HTTP client, entirely outside the browser. On a session where the user's KC tabs are throttled
background tabs, this is the RELIABLE KC path (GetBinder + the full
read/UpdateProperty/submit/refresh/diagnostics pipeline over curl from Git Bash, same
endpoint/payload shapes as the skill's builders).

1. **Token source = the wire, not localStorage.** `chrome_network_recent(host_filter="cchaxcess")`
   — the user's OWN KC/engagement browsing mints fresh `auditprod` bearers (~32-minute life) that
   BOTH KC and WPM accept. `kc.accessToken` in localStorage goes STALE on throttled background
   tabs (the refresh timer stalls — architecture.md → tab-visibility section), and re-reading it just re-reads the
   stale value; the wire capture is the ground truth for freshness.
2. **Write the token to a FILE — never hand-transcribe.** A hand-copied JWT 401'd
   `chrome_api_call` live (transcription error, not a platform problem). Land the capture in a
   session-scratch token file and expand it at call time
   (`curl -H "Authorization: Bearer $(cat "$TOKFILE")" ...`) — no transcription step exists to
   fail. Scratch only: the token never goes into any workspace file (secrets rule).
3. **Verify with one cheap GET** (e.g. KC `GetBinder`) before building on it — a 401 here means
   transcription or staleness; re-capture, don't debug the platform.
4. **Headers by leg:** KC = `Authorization: Bearer <at>` + `IdToken: <it>`; WPM adds `IDToken`
   (ALL-CAPS) + `USERLocale: en-US` + `CountryCode: US`. Same bearer serves both legs; send
   exactly ONE IdToken casing per call (architecture.md header-case gotcha).

Why curl wins under throttling: `chrome_api_call` remains fine with a file-sourced token, but
in-page `chrome_eval` fetch on a throttled background KC tab **hangs the bridge channel** — never
eval on the user's throttled tabs — and curl touches NONE of the user's open tabs (no
foreground-grab, no collision with the user's own live KC session). Build payloads in Python as
usual; only the send changes.

## Uploads — chrome_upload is the primary path (verified end-to-end)

`chrome_upload` performs the full CCH Axcess workpaper upload over the SW (verified live: workpaper
uploaded, filed, indexed, with a working TB link):
1. **Auth** — `chrome_network_recent(auth_only, host_filter:"cchaxcess")` -> freshest WPM `Authorization`
   bearer + `IDToken` (WPM uses all-caps `IDToken`). User-scoped; reuse across the batch.
2. **Folder map** — `chrome_api_call GET /v1/NewEngagementView/folders/{clientId}` -> `locationId` per index.
3. **Upload** — `chrome_upload(local_path=<Windows host path>, url="https://workpapermanagementapi.cchaxcess.com/v1/Documents/{clientId}", field_name="file", headers={Authorization, IDToken})`. Do NOT set Content-Type (browser sets the multipart boundary). -> 200 with the new `documentId`; lands in Unfiled Workpapers (locationId -1).
4. **File into section** — `wpm.move` the documentId into its section folder (locationId from step 2).
5. **Set index** — `PUT /v1/Documents` to set the displayed index.

> Fallback (bridge down, or a cross-origin chrome_upload ever refused): in-page XHR with the file
> embedded as **base64**, building the Blob/FormData in-page and XHR-ing it with the captured WPM bearer
> (`cap:wpm` sentinel). See `file-io.md` (upload) and `replace-workpaper.md` (replace). The earlier
> blanket "chrome_upload fails CORS, never use it" rule is SUPERSEDED — chrome_upload is the verified
> primary; base64-XHR is the fallback.

## Transport-specific facts

- **Data channel — NOT DLP-filtered on the bridge, for ALL origins (incl. KC).** Over `chrome_api_call`,
  KC reads return real JSON (GetBinder + form reads come back as full JSON, no
  `[BLOCKED]`). So on the bridge set `filtered = false` for KC too: return JSON directly; **skip the
  download-to-disk dance**. The DLP `[BLOCKED...]` filter + download-to-disk applies ONLY to the
  **linked-tab** channel (fallback): there KC reads are filtered = true and big forms come back by
  download-to-disk per `fill-kc-form.md`. Net: `filtered` is set by TRANSPORT — bridge = false (any
  origin), linked-tab = true for KC.
- **Big payloads on the bridge.** If a result is too large to return inline, write it to disk:
  `chrome_eval(..., out_path=...)` for text/JSON. (`chrome_api_call` has no `out_path` yet — a large KC
  GET auto-saves to the tool-results tree; read it from there. Bridge enhancement pending.)
- **Tab discovery is trivial on the bridge.** `chrome_list_tabs` sees every real tab (including the
  user's own), so the "single unnameable MCP tab group / your tabs are invisible / claim-stamp" machinery
  is **LINKED-TAB-only** — skip it on the bridge.
- **Auth hygiene.** `chrome_network_recent` returns the bearer into the model context (acceptable per the
  engagement owner). To keep the token in-page instead, use the `ls:*` (KC) / monkeypatch (engagement)
  path through the linked tab.
- **Visibility / throttle.** Tab visibilityState (selected tab in a non-minimized window), NOT window
  focus, governs throttling + token refresh; never hidden-reload a near-expiry tab. architecture.md ->
  "Tab visibility, throttling & token refresh".

## Status / what is wired

- The bridge transport and every verb are **built and validated live** on Axcess: engagement/WPM/FP/
  workbench (reads, `chrome_eval`, authenticated XHR, binary `chrome_download`, tab ops, bearer capture)
  AND **KC via `chrome_api_call`** (read + `UpdateProperty` + `submit` + refresh + diagnostics, no CSP
  error, no linked tab). Source + setup: the chrome-bridge plugin (see its README).
- **Route by origin, then verb:** KC origin -> `chrome_api_call` (bridge) PRIMARY, linked-tab fallback;
  engagement/WPM/workbench/FP -> bridge PRIMARY, linked-tab fallback. `session-bootstrap.md` and the
  per-module steps describe the LINKED-TAB flow as the fallback (and for any bridge-down session) — that
  path always works, so the skill is never broken.

<!-- END -->
