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
  - scripts.session.extract_asset_manifest
  - scripts.session.compare_manifest
  - scripts.auth_capture.INSTALL_MONKEYPATCH_JS
  - scripts.http_runner.ls_headers_js_expr (ls:kc sentinel)
  - scripts.auth_capture.capture_query_js
status: validated
---
# Runbook — Leg Warmup (lazy; per-leg)

> **GATE — this runbook IS Step 0's warmup; reading it is not running it.** Every platform call
> (any `*.cchaxcess.com` browser/API touch) needs this actually EXECUTED this session on THIS
> agent. If you have ALREADY made platform calls this session without having run it: **STOP now**
> — run it in full here, switch to the page-context transport (`transport.md`), RE-VERIFY BY READ
> everything you wrote while side-entered (200s may be silent no-ops), then resume from the last
> verified step. A subagent doing platform work runs its OWN warmup and captures its OWN fresh
> auth — never inherit a hand-passed token (they rotate ~30 min, truncate on paste). (SKILL.md →
> "Initialization gate".)

Two auth legs, warmed **independently** and **only when a module declares the need**
(SKILL.md Step 0.2). Don't warm both "to be safe" — that was the entire cold-start
delay in Cowork. Check warmth before asking the user for anything, and never re-ask
within a session.

## Persist vs ephemeral — the memory contract (memory-first bootstrap)

What may be cached across chats vs what must be captured fresh every session. This is the
whole answer to "can we skip the bootstrap next time" (complaint 2026-06-10):

- **PERSISTABLE — check memory FIRST, write back on first discovery.** Stable identifiers
  only: `clientId`, `engagementId`, the full engagement-view URL, `engagementGuid`, one KC
  `workpaperId` (enables the zero-click KC deep-link warm) → project memory;
  `axcessDeviceId` → global memory. When Step 0 / discovery surfaces one of these that
  memory doesn't hold, offer ONCE to save it (SKILL.md 0.1); on decline, record the decline
  and never re-ask.
- **NON-PERSISTABLE — never cache tokens or headers across chats.** The wpm monkeypatch
  capture (bearer/IDToken/traceparent) wipes on every full page reload and the bearer
  rotates (~30 min); kc localStorage tokens self-refresh and are re-read live per call
  (`ls:kc` / `chrome_network_recent`). ⚠ Self-refresh only runs on a VISIBLE tab — on a
  backgrounded KC tab `kc.accessToken` sits STALE past expiry and `ls:kc` serves it as if
  current; on 401s, touch/activate the tab (or `chrome_navigate` the KC deep-link) to
  re-mint, then take the fresh bearer from a live `chrome_network_recent` capture
  (architecture.md → auth section / AX-33; SFRC 2026-07-08). A cached token buys nothing
  and a pasted one is side-entry by construction (SKILL.md → Initialization gate).
- **What memory-first actually saves:** with GUID + workpaperId in memory the kc leg warms
  with ZERO clicks (deep-link); the wpm leg always costs its one provoke click per fresh
  load — that click is irreducible, don't chase bypasses.

| Leg | Holds | Serves | Warm test |
|---|---|---|---|
| `wpm` | monkeypatch-captured engagement-tab headers (bearer + IDToken + locale + traceparent) | WPM, financialprep-api, workbench-api (WPM-bearer reuse — validated 2026-06-05) | `window.__cch_capture_installed` true AND a `workpapermanagementapi` capture with an Authorization header exists |
| `kc` | `engagementGuid` + `kc.accessToken`/`kc.idToken` in localStorage + a KC-origin tab | KC API; also WPM/FP via `ls:wpm`/`ls:fp` sentinels | a claimed `knowledgecoach.cchaxcess.com` tab (its localStorage carries the tokens; self-refreshing while VISIBLE — stale-past-expiry on a background tab, see NON-PERSISTABLE note) |

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

## On-warm release check (cheap, throttled — catches drift BEFORE it stalls a write)

On by default: a one-GET release detector, run once the transport is up and BEFORE the module
fires writes. Drift almost always rides a WK release and the SPA asset manifest is the leading
indicator, so this is the highest-signal thing you can do at warm time — catch the release the
moment you start work instead of discovering it when a 55-field form fill silently no-ops.

**Throttle — once per work session, not per warm.** The baseline + timestamp live in the
ENGAGEMENT WORKING FOLDER as `.cch-release-baseline.json` (never the read-only install — AX-33
state rule). Skip the whole check when its `checked_at` is within
`session.RELEASE_CHECK_THROTTLE_SEC` (default 4h): the first bot to warm in the engagement pays
the one GET, every other bot skips until the window lapses. To turn it off for an engagement,
write that file with `{"off": true}`.

**Procedure (bridge; ~1 unauthenticated GET, read-only):**
1. **Throttle gate.** Host-`Read` `<working folder>/.cch-release-baseline.json`. Missing → first
   run (seed below, no alarm). `off:true` → skip. `checked_at` within the window → skip.
2. **Fetch the index.** `chrome_api_call` GET `session.SPA_INDEX_URLS[leg]` (engagement index for
   `wpm`, KC index for `kc`) — public HTML, no auth, bridge channel unfiltered.
3. **Compare.** `session.extract_asset_manifest(body)` → current; `session.compare_manifest(stored,
   current)`.
4. **First run** (no stored manifest for this origin) → host-`Write` `{ "origin_manifests": {
   "<leg>": current }, "checked_at": "<ISO>" }`. No alarm — you have nothing to diff yet.
5. **`changed:false`** → refresh `checked_at`, proceed.
6. **`changed:true`** → SURFACE one line: *"CCH SPA release since last check (+N/−M assets) —
   endpoint shapes may have drifted; verify-by-read the first writes, and on the maintainer setup
   run `cch-drift --layer bundle` then `--layer all` before trusting writes."* Update the stored
   manifest + `checked_at`, then **proceed** — a release is a heads-up, NOT a hard stop. Don't halt
   the engagement; raise vigilance and let the deeper diagnostic (`cch-drift`) run out-of-band.

Never blocks warming, never touches the install. It augments the maintainer cron (weekly
`--layer all` + monthly `--layer write`) with warm-time latency-to-detection — the release lands
in your lap at the start of the session, not at the next morning's cron.

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

## Session recovery — stale auth mid-task (401/403/419, login redirect, missing XSRF)

The governing rule is SKILL.md's failure discipline: **re-warm the FAILING leg only, retry
ONCE, then surface** — one failing family ≠ all dead, and a param/header tweak is not a fresh
approach. Recovery specifics for this runbook:

1. Identify WHICH family is failing (engagement / WPM / workbench / FP / KC) before touching
   anything. Never hand-forge headers or reuse another family's tokens.
2. **Ask the user, in one line,** to refresh the bridged Chrome tab and log back in if
   prompted; if the failing leg is KC, have them **click into Knowledge Coach once** — KC
   tokens are minted only when KC is actually opened (and the KC `binderId` is discovered
   from that open — architecture.md ID glossary).
3. Re-warm the failing leg per Step 0 — a FULL fresh capture for that leg, never one header
   patched into an old capture.
4. **Verify with one cheap read** (e.g. GetBinder) before resuming writes, and resume from
   the last VERIFIED step — re-verify the last write before continuing past it.
5. Two clean bootstrap failures → STOP: report endpoint + status + what completed, and what
   the user should check (VPN/SSO timeout, tenant switch, closed tab).

## Hand back to the module

Return the warmed leg's handles (headers source or `ls:*` sentinel, plus GUID if acquired)
+ `filtered: true|false`. The module does the work.

<!-- END -->

