---
summary: Pick the transport for browser work by TARGET ORIGIN, then by VERB. chrome-bridge is PRIMARY for ALL origins — engagement/WPM/workbench/FP via in-page verbs, and knowledgecoach (KC) via chrome_api_call (the service-worker fetch verb, CSP-exempt). The linked Claude-in-Chrome tab is the FALLBACK everywhere (used when the bridge/extension is unavailable). The bridge's IN-PAGE verbs (chrome_eval, chrome_fetch) stay CSP-blocked on KC — for KC use chrome_api_call. The rest of the skill stays transport-agnostic.
triggers:
  - "(internal) transport selection — consulted from SKILL.md Step 0 and session-bootstrap.md"
status: BRIDGE=primary for ALL origins — engagement/WPM/workbench/FP via in-page verbs (validated 2026-06-17/19) + KC via chrome_api_call/SW-fetch (validated live 2026-06-23, read+write+submit+diagnostics); LINKED-TAB=fallback everywhere (CSP only blocks the bridge's IN-PAGE verbs on KC, never chrome_api_call)
---
# Runbook — Transport selection (route by origin, then verb)

## Bridge is PRIMARY everywhere; linked tab is the FALLBACK

Detect the bridge ONCE per session (below). If it's up, it is the preferred transport for **every**
origin — including knowledgecoach. The linked Claude-in-Chrome tab is the fallback used only when the
bridge/extension is unavailable.

The ONE origin-specific rule is a VERB rule, not an origin ban:

- **knowledgecoach.cchaxcess.com (KC origin)** → use **`chrome_api_call`** (the service-worker fetch
  verb). It is **CSP-exempt** (the SW context is not subject to the page CSP) and **CORS-bypassed**
  for hosts in the extension `host_permissions` (`*.cchaxcess.com`). It drives the full KC pipeline —
  GET form, GetBinder, `UpdateProperty`, spawn, `submit`, refresh, diagnostics — verified live
  2026-06-23. Pass the captured KC bearer + **`IdToken`** (capital-I/lower-d/capital-T) in `headers`
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
| **KC-origin read/write** (KC form GET, GetBinder, `UpdateProperty`, spawn, `submit`, diagnostics) | **`chrome_api_call(url, method, headers, body)`** — SW fetch, CSP-exempt + CORS-bypassed; pass KC bearer + `IdToken` in headers | the linked Claude-in-Chrome tab on a `knowledgecoach.cchaxcess.com` tab (same endpoints/builders) |
| Find the CCH tab | `chrome_list_tabs` -> pick by URL (returns id+url+title for ALL real tabs, incl. the user's own) | `tabs_context_mcp` + `tab_probe_js` + `claim_tab_js` (session.py) |
| Run JS in page (engagement origin only) | `chrome_eval(code, target=tabId)` | `mcp__Claude_in_Chrome__javascript_tool(code, tabId)` |
| Backend API call (any origin) | `chrome_api_call(url, headers=captured)` — SW, CORS-bypassed for *.cchaxcess.com (cleanest); OR `chrome_eval` + http_runner XHR builder for engagement-origin in-page | `javascript_tool` running the same builder |
| Same-origin GET (text) | `chrome_fetch` (engagement origin) / `chrome_api_call` (any) | `javascript_tool` + `build_fetch_call` |
| Download a file (binary) | `chrome_download(url, out_path, target)` — writes the file to disk | `wpm.download_to_browser_js` -> Downloads folder (then mount it) |
| Upload a file | **`chrome_upload(local_path, url, field_name="file", headers=captured)`** — verified full WPM upload pipeline (see below) | in-page FormData/base64 XHR via `javascript_tool` (file-io.md) |
| Navigate / open / close tab | `chrome_navigate` / `chrome_open_tab` / `chrome_close_tab` | `navigate` / `tabs_create_mcp` / `tabs_close_mcp` |
| Capture the bearer | `chrome_network_recent(host_filter)` — webRequest auto-captures it off live API calls; **no monkeypatch, no provoke**. User-scoped; reuse across the batch | install monkeypatch (auth_capture.py) + provoke one boot XHR |
| KC localStorage auth | pass tokens from `chrome_network_recent` to `chrome_api_call` for KC | `javascript_tool` with the `ls:*` sentinel |

## chrome_api_call body — must be pre-serialized JSON

`chrome_api_call` forwards `body` to the SW as-is. For a JSON POST the body must be a **JSON string**
(the verb does not auto-serialize a dict; the current `server.py` types `body: str` and rejects a dict).
The skill's payload builders return dicts — **`json.dumps` them before the call**. (Bridge fix pending:
`server.py` to accept a dict and `json.dumps` it; until shipped, json.dumps at the call site. A bare
strict-JSON object passed inline can be coerced/rejected by the arg layer — pass it as a serialized
string.)

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
  KC reads return real JSON (validated 2026-06-23: GetBinder + form reads came back as full JSON, no
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
  error, no linked tab — validated 2026-06-23). Source + setup: the chrome-bridge plugin (see its README).
- **Route by origin, then verb:** KC origin -> `chrome_api_call` (bridge) PRIMARY, linked-tab fallback;
  engagement/WPM/workbench/FP -> bridge PRIMARY, linked-tab fallback. `session-bootstrap.md` and the
  per-module steps describe the LINKED-TAB flow as the fallback (and for any bridge-down session) — that
  path always works, so the skill is never broken.

<!-- END -->
