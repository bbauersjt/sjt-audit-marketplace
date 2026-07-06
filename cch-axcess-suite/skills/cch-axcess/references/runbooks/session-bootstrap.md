---
summary: Warm an auth leg (wpm or kc) on demand. Called from SKILL.md Step 0; warm ONLY the leg the module declares.
triggers:
  - "(internal) leg warmup for SKILL.md Step 0"
inputs:
  - "Seeded clientId + engagementId (Step 0.1 — from URL/project memory/user-opened engagement view)"
  - "The leg the module declares: wpm | kc"
calls:
  - mcp__Claude_in_Chrome__list_connected_browsers
  - mcp__Claude_in_Chrome__select_browser
  - mcp__Claude_in_Chrome__tabs_context_mcp
  - mcp__Claude_in_Chrome__tabs_create_mcp
  - mcp__Claude_in_Chrome__tabs_close_mcp
  - mcp__Claude_in_Chrome__navigate
  - mcp__Claude_in_Chrome__javascript_tool
  - scripts.session.discover_session_js
  - scripts.session.tab_probe_js
  - scripts.session.claim_tab_js
  - scripts.auth_capture.INSTALL_MONKEYPATCH_JS
  - scripts.http_runner.ls_headers_js_expr (ls:kc sentinel)
  - scripts.auth_capture.capture_query_js
status: validated
---
# Runbook — Leg Warmup (lazy; per-leg)

Two auth legs, warmed **independently** and **only when a module declares the need**
(SKILL.md Step 0.2). Don't warm both "to be safe" — that was the entire cold-start
delay in Cowork. Check warmth before asking the user for anything, and never re-ask
within a session.

| Leg | Holds | Serves | Warm test |
|---|---|---|---|
| `wpm` | monkeypatch-captured engagement-tab headers (bearer + IDToken + locale + traceparent) | WPM, financialprep-api, workbench-api (WPM-bearer reuse — validated 2026-06-05) | `window.__cch_capture_installed` true AND a `workpapermanagementapi` capture with an Authorization header exists |
| `kc` | `engagementGuid` + `kc.accessToken`/`kc.idToken` in localStorage + a KC-origin tab | KC API; also WPM/FP via `ls:wpm`/`ls:fp` sentinels | a claimed `knowledgecoach.cchaxcess.com` tab (its localStorage carries the tokens; self-refreshing) |

**Cross-serving (don't double-warm):** a warm KC leg serves WPM/FP via the `ls:*`
sentinels — skip the engagement-tab capture for those calls. A warm WPM leg never
serves KC-form writes. GUID is NOT required for reads/annotations/WPM ops
(validated 2026-06-05); workbench **creates** need it — seed/boot-capture first,
full KC warmup only if it isn't there.

## Shared preliminaries (run once, first warmup only)

**0. Detect the bridge FIRST (before any browser op).** Call `chrome_bridge_status` (chrome-bridge
plugin). Server up + reachable -> **BRIDGE** transport for this session: **skip steps 1-2** (tab pick /
tab claim — `chrome_list_tabs` sees every real tab), KC ops go via `chrome_api_call`, engagement/WPM/FP/
workbench via `chrome_api_call` (or `chrome_eval`). Absent / errors / no server -> **LINKED-TAB** transport:
do steps 1-2 below. Remember the choice. (Full map: `runbooks/transport.md`.)

**1. Pick the browser without the whack-a-mole.** *(LINKED-TAB transport only.)* `list_connected_browsers`.
- If project/global memory holds a saved `axcessDeviceId` and it appears in the list as
  on-this-computer → `select_browser` it **silently** (no prompt). This is the default
  path once remembered.
- Else if exactly one on-this-computer browser is connected → use it, and **offer once**
  to save its `deviceId` to global memory as `axcessDeviceId` so future cold starts skip
  this. On decline, record the decline and don't re-ask.
- Else (several on-this-computer browsers, or only idle/other-machine ones) → ask the user
  which once, then save it as above.
- Empty list ⇒ Chrome isn't running here — ask the user to launch it (one sentence). Don't
  walk through extension install/sign-in unless the user says it was never set up.

**2. Reuse the Axcess tab group; claim a tab (stops 50-tab/50-group sprawl).**

> **LINKED-TAB-only — skip the whole of step 2 on the BRIDGE.** The tab-group / `tabs_context_mcp`
> / `tab_probe_js` / `claim_tab_js` machinery below exists because the linked Claude-in-Chrome tab
> group can't see the user's own tabs. On the bridge, `chrome_list_tabs` sees every real tab, so
> none of this applies (`runbooks/transport.md` → Tab discovery is trivial on the bridge). KC-origin
> work is BRIDGE-FIRST via `chrome_api_call`, so step 2 (tab claim) runs only on the linked-tab fallback — skip it on the bridge.

There is ONE MCP tab group per browser — `tabs_context_mcp` (call it **without**
`createIfEmpty` first) returns that group's tab IDs (IDs only, no URLs). Mint one short
`ownerToken` for this chat and:
- **Find a CCH tab.** For each returned tab ID, run `scripts.session.tab_probe_js()` via
  `javascript_tool(tabId)`. A tab is **reusable** when `isCch` is true and its claim is
  free — `ownerToken` is null, equals yours, or `ownerAgeSec > CLAIM_STALE_SEC` (a live
  chat refreshes its claim, so a fresh foreign claim = another chat is driving it; skip it).
  Prefer the tab kind matching the leg you're warming (`kc` / `engagement`).
- **Reuse it.** Adopt the first reusable CCH tab: run `scripts.session.claim_tab_js(token)`
  in it, record that `tabId` as **this session's tab**, and pass it explicitly on every
  later Chrome call.
- **The user's own tabs are INVISIBLE to the group.** `tabs_context_mcp` only sees the MCP
  tab group — a live KC/engagement tab the user already has open sits outside it and won't be
  found. Before creating a new tab, ask the user ONCE: "Already have the binder open in a
  Chrome tab?" If yes, prefer adopting it; otherwise have the user keep that tab focused and
  skip the cold-start navigation.
- **Only create when contended/absent.** If there's no group, call `tabs_context_mcp`
  again with `createIfEmpty:true`. If a group exists but every CCH tab is claimed by another
  live chat, `tabs_create_mcp` a fresh tab and `navigate` it. Creating-new is the fallback,
  not the default. Sharing a tab for backend/API work is safe — the extension serializes
  calls; the claim only matters for UI actions.

**3. One discovery call.** Run `scripts.session.discover_session_js()` in the active tab via
`javascript_tool`. Returns filter-safe:
`{host, clientId, engagementId, engagementGuid, hasKcTokens, kcTabUrl, ready_to_write, needs[]}`.
It tells you which legs are ALREADY warm — skip everything below that's already true.

## Warming the `kc` leg

> **KC-origin ops are BRIDGE-FIRST via `chrome_api_call`** (service-worker fetch — CSP-exempt + CORS-
> bypassed for `*.cchaxcess.com`). Validated live 2026-06-23: read, `UpdateProperty`, `submit`, refresh,
> diagnostics all over `chrome_api_call`, no CSP error, no linked tab. The bridge's IN-PAGE verbs
> (`chrome_eval`/`chrome_fetch`) remain CSP-blocked on KC — don't use them there. The linked Claude-in-
> Chrome tab is the FALLBACK (bridge/extension down). On the bridge, KC data is NOT DLP-filtered — return
> JSON directly; the download-to-disk path is the linked-tab fallback only.

**Warm the kc leg (bridge):** capture the KC bearer + `IdToken` via `chrome_network_recent(host_filter="knowledgecoach")`
(a logged-in KC tab self-refreshes the token; a one-shot `chrome_navigate` to the KC deep-link re-mints it
if stale). Pass them in `headers` on every `chrome_api_call`. No tab-claim machinery needed (bridge sees
all tabs). On a 401, re-pull `chrome_network_recent` and retry once.

**Warm the kc leg (linked-tab fallback):**
- **Adopted a `kind:"kc"` tab?** Done — its URL carries the GUID, its localStorage carries the tokens
  (self-refreshing; re-read per call). Re-run discovery there to confirm.
- **Known binder (GUID + any workpaperId): ZERO clicks.** `navigate` the claimed tab to the FULL KC
  deep-link `https://knowledgecoach.cchaxcess.com/binder/{engagementGuid}/workpaper/{workpaperId}` — the
  SSO cookie lands `kc.*` tokens in readable localStorage on render. **Gotcha:** a bare
  `/binder/{engagementGuid}` (no `/workpaper/...`) renders `/not-found` — always include a workpaperId. A
  fresh binder always has unfiled KC forms: `folder_get(-4)` returns them; each form's `documentId` IS its
  KC `workpaperId` — feed any one into the deep-link. Store one in project memory the first time.
- **No GUID anywhere?** The engagement-tab boot capture delivers it, or read it from
  `GET financialprep-api.cchaxcess.com/v1.0/engagement/{clientId}` once FP is reachable.
- **Headers (linked tab):** pass `headers="ls:kc"` to the builders (runtime localStorage self-sourcing;
  `Authorization: Bearer <kc.accessToken>`, `IdToken: <kc.idToken>` — exact case).

## Warming the `wpm` leg

The engagement-origin token is NOT in readable storage — it lives in the HttpInterceptor
closure, on the wire only. The monkeypatch is the only mechanism; one provoke is
irreducible (all bypasses tested DEAD — do not re-chase: idle views fire nothing in 12s,
cookie-only calls are rejected, the token isn't in the Angular tree to depth 5).

- **CASE B — starting from the engagement LIST (preferred): the provoke is the entry click
  you already make.** Install `scripts.auth_capture.INSTALL_MONKEYPATCH_JS` on the list
  page → click INTO the engagement. The click is an SPA route change, so the patch
  SURVIVES it, and the boot XHRs deliver the WPM + FP headers AND the `engagementGuid` in
  one shot. No tree-click needed.
- **CASE C — already parked on an engagement VIEW, cold (boot fired pre-patch): ONE
  synthetic tree-node click.** Install the patch, then fire a synthetic
  `mousedown`/`mouseup`/`click` on the **"Unfiled Knowledge Coach Forms"** node (always
  present) to provoke a fresh boot XHR. Avoid this case by starting from the LIST.
- The patch **wipes on every full page reload** (URL change), so the wpm leg starts cold
  each fresh load; the cost is ONE click, asked ONCE. Do NOT re-trigger capture on later
  tasks in the same session. ⚠ **Refresh-Report trap:** report pages hard-reload on
  Refresh Report and kill the patch — capture from the engagement view, or reuse the
  already-captured WPM bearer (it's accepted by workbench-api and financialprep-api;
  architecture.md transport matrix).
- Read captures with `scripts.auth_capture.capture_query_js(host_substring)` /
  `window.__cch_capture`.

## 401 mid-task (the ONLY re-auth rule)

A 401 (or auth-shaped failure) on a call → re-warm the **failing leg only**, retry the
call **once**, then surface to the user. No proactive re-auth, no mid-task re-bootstrap,
no touching the healthy leg.

## Data channel — deterministic by TRANSPORT (not origin)

The data channel is fixed by which TRANSPORT carries the call:

- **Any origin on the BRIDGE (`chrome_api_call` / `chrome_eval`) -> NOT filtered.** Return JSON directly;
  skip download-to-disk. KC reads over `chrome_api_call` come back as real JSON (validated 2026-06-23 —
  GetBinder + form reads, no `[BLOCKED]`). If a payload is too large to return inline it auto-saves to the
  tool-results tree (or use `chrome_eval(out_path=...)`); read it from disk.
- **KC on the LINKED-TAB fallback -> DLP-FILTERED.** A raw KC form/TB blob comes back `[BLOCKED...]`, so on
  the fallback read KC forms by **download-to-disk** (pattern: `bulk-capture-forms.md` Step 2; mount the
  browser's Downloads folder via `request_cowork_directory` yourself; never ask the user to save-and-report).

`filtered` is set by TRANSPORT: bridge = false (any origin, incl. KC), linked-tab = true for KC.

## Hand back to the module

Return the warmed leg's handles (headers source or `ls:*` sentinel, plus GUID if acquired)
+ `filtered: true|false`. The module does the work.

<!-- END -->
