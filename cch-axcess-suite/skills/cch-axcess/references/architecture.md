# CCH Axcess — Architecture (single source of truth)

This is the ONLY file that documents platform-level facts. Modules cite this file; they do not repeat it. Endpoint shapes live in JSON specs at `endpoints/`. Enums and lists live in `config/`.

If you discover a new fact about the platform, update this file (and the relevant `endpoints/*.json`). Do not paste it into a module.

## Execution model — scripts BUILD JS, the browser EXECUTES (read this once)

This skill's Python scripts are **JS-builders and response-parsers, never HTTP clients.**
No script imports `requests`/`urllib` or fires a network call from Python. A function like
`http_runner.build_fetch_call(...)` returns a **JS string**; that string is handed to
`mcp__Claude_in_Chrome__javascript_tool`, the **browser** runs it, and `parse_result(...)`
parses what comes back. The flow is always: Python builds JS → browser executes → Python parses.

Crucially, **auth is read from `localStorage` at runtime, inside the built JS** — the token
never reaches Python and never crosses the tool channel. This is why the skill works under
Cowork's DLP: the thing DLP blocks (a raw token moving through the tool result) simply never
happens, because the token stays in-page.

Python-side HTTP never happens in this skill. Builders are MANDATORY for writes; inline JS is
allowed only for trivial reads. Route payload construction through the builders (see
`build_write_payload`, which refuses a raw key). `scripts/http_runner.py` carries the named
helpers `build_relay_*` and `build_chunked_read_js` — do not re-improvise these inline.

## Subdomains

| Subdomain | Purpose | Auth |
|---|---|---|
| `engagement.cchaxcess.com` | Engagement / binder Angular SPA. Workpapers, leadsheets, TB, journal entries. | Cookie + Angular interceptor |
| `workpapermanagementapi.cchaxcess.com` | Backend API for engagement app. Folder/workpaper/leadsheet CRUD. | Bearer JWT + custom headers |
| `workbench-api.cchaxcess.com` | Report generation: TB + JE reports. Lists, quotas, enums. Fund TB Setup (FundType / Fund / FundSubType / fundaccountmap). | Bearer JWT + custom headers (WPM-style) |
| `financialprep-api.cchaxcess.com` | Engagement financial data: grouping lists, groups, raw TB rows, journal entries. | Bearer JWT + custom headers (WPM-style) |
| `knowledgecoach.cchaxcess.com` | Knowledge Coach: forms, audit programs, risk summary, disclosure checklists. | Bearer JWT via OIDC handshake |
| `dda.cchaxcess.com` | Data Delivery / engagement data import wizard (Select File → Map → Validate → Complete). URL: `/en-US/import?engagementId={clientId}&ipId={engagementId}`. | Cookie session |
| `pendo.io`, `pendo-static-*.storage.googleapis.com` | Product analytics. **Ignore.** Filter from network captures. | n/a |
| `zuse2-*.cloudapp.azure.com` | OpenTelemetry traces (`/v1/traces`). **Ignore.** Filter from captures. | n/a |

## ID glossary

CCH uses several distinct IDs that look interchangeable but aren't. Mixing them produces silent 4xx/500s.

| ID | What | Source | Used by |
|---|---|---|---|
| `clientId` | Per-client integer | First int in URL `/engagement/{clientId}/...` | WPM endpoints; passed as `engagementId={clientId}` in many bodies (misnamed) |
| `engagementId` | Per-engagement integer | Second int in URL `/engagementview/{engagementId}` | WPM folder GET path slot 3; workbench-api report bodies (as `periodId`) |
| `engagementGuid` | Per-engagement GUID (engagement/workbench side) | engagement-side boot capture; workbench-api echoes it | workbench-api TB create body; KC `/Home/GetPermissions/{engagementGuid}` |
| `kcBinderGuid` (KC `binderId`) | KC's OWN per-binder GUID — **CAN DIFFER from `engagementGuid`** on the same engagement; on older binders the two matched, so "canonical across sister apps" is UNRELIABLE. GetBinder by the engagement guid → 200-wrapped 404 "Binder not found". Discover it from the KC tab's own traffic (`/api/binder/GetBinder/{guid}` fired on KC open) — never assume it equals the engagement guid. | KC `/binder/{binderGuid}/...`; `GetBinder.result.id` | KC API everywhere (form GET/write, submit `binderId`, add-forms) |
| `clientGuid` | Per-client GUID, stable across all client engagements | `GetBinder.result.clientGuid` | (KC delete path historically; KC delete not used by this skill) |
| `workpaperId` (a.k.a. `documentId`) | Per-form GUID | `GetBinder.result.workpapers[].id`, or WPM rows' `documentId`/`fileId` | KC form GET/POST; `wpm.move`/`set_index` objectId |
| `locationId` | Per-folder integer | WPM folder GET responses | WPM move/index endpoints |
| `titleId` | Per-CCH-industry-title GUID | `kc-forms-catalog-rich.xlsx`; `GetBinder.result.lastUsedTitleGuid` | Add-Forms POST body |
| `reportGuid` | Per-report GUID | `workbench-api list responses` (`tbreports/{cid}`, `JournalEntryReport/{cid}`) | Report addressing; `reports/{reportGuid}` is the Move/Set-Index objectId |

**Naming gotcha (platform-wide)**: WPM, workbench-api, and financialprep-api all use the field name `engagementId` in places where the *value* is actually the Axcess `clientId`. Examples:

- `POST workpapermanagementapi/v1/NewEngagementView/folder` body field `engagementId` carries the URL's first int (the clientId), not the URL's second int (the real engagementId).
- `POST workbench-api/v1/trialbalancereport/createReports` body field `engagementId` carries the clientId; the real engagementId rides in `ReportSettings.periodId`.
- `POST workbench-api/v1/JournalEntryReport` body field `engagementId` carries clientId; real engagementId in top-level `periodId`.

Always read by value, not field name. Every endpoint JSON spec annotates this.

## Auth pattern

### ONE central header-builder — localStorage-primary (read this first)

Auth maps to the two Step-0 legs (SKILL.md):

- **KC leg — KC localStorage tokens** are the auth for Knowledge Coach, and serve WPM /
  financialprep-api via the `ls:*` sentinels from any kc-token origin.
- **WPM leg — monkeypatch-captured engagement-tab headers** (bearer + ALL-CAPS `IDToken` +
  locale + `traceparent`) are the auth for workbench-api, and the SAME captured bearer is
  **also accepted by financialprep-api and WPM**. workbench-api remains unreachable from the
  KC tab (fetch AND XHR, status 0, any headers — transport-level).

There is exactly ONE way to build headers per leg; every module cites this section and none
repeats a per-module header recipe.

The tokens live in plaintext **localStorage** on the KC origin and are read at call time:

```js
localStorage.getItem('kc.accessToken')   // JWT — goes in `Authorization: Bearer <...>`
localStorage.getItem('kc.idToken')        // OIDC IdToken
```

Full keyset: `kc.accessToken`, `kc.idToken`, `kc.refreshToken`, `kc.pendoJwt`,
`kc.userReportName`, `kc.userName`, `kc.staffId`, `kc.userId`.

**Header set by family (case is load-bearing — wrong case → 401):**

| API family | Authorization | IDToken header casing | Also required |
|---|---|---|---|
| knowledgecoach (KC writes) | `Bearer <kc.accessToken>` | **`IdToken`** (mixed: capital-I, lower-d, capital-T) | `Accept: application/json` |
| WPM / financialprep-api | `Bearer <kc.accessToken>` | **`IDToken`** (ALL-CAPS) | `USERLocale: en-US`, `Accept-Language: en-US`, `CountryCode: US`, `Accept: application/json` |
| workbench-api | monkeypatch-captured headers (same shape: Authorization + ALL-CAPS `IDToken` + locale + `traceparent`); the captured WPM bearer is also accepted by financialprep-api | | |

The same `kc.accessToken` + `kc.idToken` pair authenticates WPM, financialprep-api,
and KC — only the `IDToken`/`IdToken` casing (and, for WPM-style, the locale headers)
differs. **workbench-api: no KC-token path** — captured headers (WPM leg) only
(transport matrix below). The
WPM locale headers are NOT optional: omit them and WPM GETs return **200 + empty array
`[]`** for every folder (silent failure that mimics an empty binder).

**Expiry: none to handle — ON A VISIBLE TAB.** `kc.refreshToken` is present, so the app
self-refreshes the access token in place. **Re-read `localStorage` per call** and you
have a current token — no expiry logic, no rotation tracking. ⚠ **The self-refresh is a
page TIMER, and Chrome stalls it on hidden/backgrounded tabs** (see the tab-visibility note
below): on a background KC tab `kc.accessToken` can sit in localStorage STALE past expiry —
re-reading it just re-reads the stale value. If ls-sourced calls start 401ing, don't trust the
localStorage read: touch the tab (activate it / `chrome_navigate` the KC deep-link) so the
app re-mints, then take the fresh bearer from a live `chrome_network_recent` capture —
the wire is the ground truth for freshness, localStorage only tracks it while the tab is
visible. The wire-captured bearer also works from
**curl-from-Bash entirely outside the browser** — KC and WPM both accept it (pure
header-bearer auth; `runbooks/transport.md` → curl section). Write it to a session-scratch
token FILE and expand at call time — never hand-transcribe (a hand-copied JWT 401s).

Builders self-source these tokens at runtime when you pass the `"ls:<family>"`
SENTINEL as the `headers` argument (`"ls:wpm"` / `"ls:fp"` / `"ls:kc"` — see
`http_runner.ls_headers_js_expr`). **Prefer the sentinel for every WPM / FP-API /
KC call** — tokens then never cross the tool channel and no per-session wrapper is needed.
Passing a captured-headers DICT remains
supported and is REQUIRED for workbench-api (see the transport matrix below).

### `__cch_capture` monkey-patch — fallback / bootstrap only

The Angular-interceptor monkey-patch (`scripts/auth_capture.py` →
`window.__cch_capture`) is reduced to **two jobs only**:

1. **Bootstrap capture** on the engagement origin when no KC tab exists yet — the
   provoke that harvests the `engagementGuid` + engagement-side headers (see
   `runbooks/session-bootstrap.md`, Cases B/C). It is irreducible there because the
   engagement-origin token is NOT in readable storage — it lives in the HttpInterceptor
   closure, on the wire only.
2. **Fallback** header source when, for whatever reason, no KC tab is available to read
   `localStorage` from.

When a KC tab exists, **skip the monkey-patch entirely** and read tokens from
localStorage. The patch wipes on every page reload, so it is never the steady-state
mechanism. **Cleanup rule:** a session that stashed a `__cch_capture_dump`-style blob in
localStorage must delete it when done.

#### `cap:<family>` sentinel — the engagement-only-tab leg

The `ls:<family>` sentinels read KC localStorage and are **dead on an engagement-only tab**
(no `kc.*` keys there). The **`cap:<family>`** sentinel is the counterpart: it self-sources
the freshest matching header set from `window.__cch_capture` in-page (the WPM leg), so a
session that only has the engagement tab can still authenticate WPM/FP/workbench calls.
Families: `cap:wpm` / `cap:fp` / `cap:workbench` (host-matched against the capture buffer).
Pass it as the `headers` argument to any `http_runner.build_*` builder exactly like an `ls:*`
sentinel (`http_runner.capture_headers_js_expr`). Requires the `auth_capture` monkeypatch
installed AND a matching API call already fired (else the expr throws in-page). je.py and
wpm_replace.py read `__cch_capture` with the same filter — `cap:*` reconciles that pattern
into the builders so it isn't re-improvised inline.

### Header case (gotcha)

- KC uses `IdToken` (capital-I, lowercase-d, capital-T)
- WPM, workbench-api, financialprep-api all use `IDToken` (all-caps)

These are NOT interchangeable. Wrong case → 401. **Send EXACTLY ONE of the two casings per
call — sending BOTH `IDToken` AND `IdToken` on the same request → 401**. One alone → 200.
The `ls:*` / `cap:*` sentinels already emit a single casing per
family; only a hand-rolled header dict can trip this.

### Transport matrix (the POSITIVE rules, don't rediscover)

| Target API | From KC tab | From engagement tab | Auth source |
|---|---|---|---|
| WPM | **XHR ✓** (fetch ✗) | XHR ✓ | KC localStorage (`ls:wpm`) OR captured WPM bearer |
| financialprep-api | **XHR ✓** (fetch ✗) | XHR ✓ | KC localStorage (`ls:fp`) OR captured WPM bearer |
| KC API | ✓ | — | KC localStorage (`ls:kc`, IdToken casing) |
| workbench-api | **✗ dead** (fetch AND XHR, any headers) | **XHR ✓ with monkeypatch-captured headers** (incl. `traceparent`) — the captured WPM bearer is accepted | captured dict (WPM leg) ONLY |

- ALWAYS XHR for cross-origin; `fetch()` fails CORS preflight everywhere it was tested.
- workbench-api is the odd one out: KC tokens are NOT accepted from the KC tab; the
  engagement tab + captured headers works (GET and the SPA's own POSTs). One captured WPM
  header set serves workbench-api AND financialprep-api AND WPM — capture once, reuse across
  all three.
- ⚠ **Refresh-Report hard-reload trap:** report pages kill the monkeypatch on Refresh
  Report (full page reload, like the report-settings save). Do NOT chase re-capture on a
  report page — capture from the engagement view, or reuse the WPM bearer you already
  captured.

## Platform-stable operational facts

These have been confirmed live. Do not rediscover them.

### Tab visibility, throttling & token refresh (autonomous work)

The single variable that governs whether a backgrounded KC/engagement tab keeps working is
**`document.visibilityState`**, NOT window focus:

- **`'visible'`** = the tab is the **selected tab in a non-minimized window**. Window focus is
  irrelevant (`document.hasFocus()===false` is fine). A visible tab runs evals instantly and
  its token-refresh timer keeps firing.
- **`'hidden'`** = another tab is selected in that window, or the window is minimized → Chrome
  throttles aggressively: timer clamping, tab freeze, the **token-refresh timer stalls** (token
  ages to expiry → 401 — and the EXPIRED token stays in `localStorage`, so `ls:` sentinel reads
  serve it as if current; recovery = touch the tab to re-mint, then capture the fresh bearer via
  `chrome_network_recent`, per the auth section above), and in-page evals time out (45s is the
  linked-tab CDP limit; the bridge's `chrome_eval` defaults to 30s — the 45s figure is NOT a
  bridge property).

Practical solution for autonomous work: **park the KC tab as the lone/selected tab in its own
non-minimized window off to the side**, then work in Cowork (a separate window). It
self-maintains — evals stay fast, the ~30-min token renews. JS visibility-spoofing does NOT help
(the throttle decision is browser-process level). Nuclear option: launch Chrome with
`--disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-renderer-backgrounding`.

**Throttle killer — silent-audio keep-alive (detect → apply → MANDATORY teardown).** When a tab
that must keep working is throttled — `chrome_eval` timing out, `visibilityState:'hidden'`, the
token aging — do NOT flail: go straight to the keep-alive. A 0-gain Web-Audio oscillator makes
Chrome treat the tab as AUDIBLE, exempting it from freeze even backgrounded.
- **Apply:** `chrome_eval(http_runner.build_keepalive_js(True), target=tab)`. Idempotent (reuses
  `window.__cchKeepAlive`). It calls `ctx.resume()`; if it returns `state=suspended (NO gesture
  yet …)`, the tab has had no user gesture and the keep-alive will NOT take — surface that (ask the
  user to click the tab once), don't assume it worked.
- **⛔ TEAR IT DOWN when done:** `chrome_eval(http_runner.build_keepalive_js(False), target=tab)`
  before you leave the tab / finish the engagement. A leaked oscillator keeps the tab
  **permanently throttle-exempt** — leave them around and you accumulate tabs that can never
  throttle again (resource leak). The teardown is not optional; it pairs with every apply.

- **API writes LAND regardless of focus.** Focus/visibility only affects token REFRESH over
  time, never whether an individual write commits. (The AUD-100 multiselect reset persisted with
  a fresh token + `hasFocus:true` — that's a write-mechanism issue needing `build_write_payload`,
  not a focus issue.)
- **Reload rules:** a **visible** reload re-mints the token cleanly (~30 min). A **hidden,
  near-expiry** reload is **forbidden** → it can land on `knowledgecoach.cchaxcess.com/accessdenied`
  with **all `kc.*` localStorage wiped** (auth fully lost, manual re-auth required). Never reload
  a near-dead-token tab to "fix" it.
- **Programmatic token refresh (future / durable fix):** the OIDC token endpoint is
  `login.cchaxcess.com/ps/auth/v1.0/core/connect/token`, client_id
  `Prod.WKIDaaS.AuthFlow.KnowledgeCoach`. CORS is OPEN from the KC origin, but a bare
  `grant_type=refresh_token` POST 500s — the SPA uses **iframe silent-renew**
  (`/connect/authorize?prompt=none` → code → token, PKCE). To make refresh programmatic, capture
  the SPA's ACTUAL renew call and replicate it exactly (don't guess params). This removes the
  focus/visibility dependency entirely — until then, the visible-tab parking above is the answer.

### In-page GET shows the WORKING COPY, not committed state

An in-page `chrome_eval`/`javascript_tool` XHR GET of `/api/Workpaper/{eng}/{wp}` returns the
**uncommitted WORKING COPY**, not committed state: write `NewOrRecurring=New` → the immediate
re-GET shows `state 3, valueKey "new"` — but that reflects the pending working copy, not what is
persisted. **NEVER verify a write by the immediate post-write GET** — it reads back your own
unsubmitted change and yields false state-3 positives. True committed state requires the full cycle:
**write → `POST /api/Workpaper/submit` (per-workpaper scoped — empty workpaperId silently DISCARDS
other forms' pending writes) → reload → GET** (and, as the completion oracle, the
diagnostics endpoint — see the field model below). A refresh discards any unsubmitted writes, so a
working-copy "state 3" that was never submitted simply vanishes. And even a correctly submitted
write can silently vanish — KC drops ~30–50% of write→submit pairs — so the re-read
is not optional: the mandatory loop is write → ~1.2s → per-wp submit → verify-by-read → retry ≤3×
(field-conventions.md §5 3a).

### Transport by origin — BRIDGE primary for ALL origins (KC via chrome_api_call)

**Route by the TARGET origin, then by VERB.** The chrome-bridge local MCP is the primary transport for
**every** origin (see `runbooks/transport.md`). `chrome_network_recent(host)` auto-captures the bearer
off live API calls via webRequest — **no monkeypatch, no provoke** — and the bridge result channel is
**NOT DLP-filtered** on any origin (return form/TB JSON directly; skip download-to-disk).

**The bridge DOES work for Knowledge Coach — via `chrome_api_call` (the service-worker fetch verb).**
`knowledgecoach.cchaxcess.com` ships a strict CSP (no `unsafe-eval`) that blocks the bridge's **in-page**
verbs (`chrome_eval` in MAIN and ISOLATED worlds, and in-page `fetch`) — so those are N/A on KC. But
`chrome_api_call` fetches from the extension **service worker**, which is **not subject to the page CSP**
and is CORS-bypassed for `*.cchaxcess.com`; it drives the full KC pipeline (GET form, GetBinder,
`UpdateProperty`, spawn, `submit`, refresh, diagnostics) — no CSP error, no
linked tab. Pass the captured KC bearer + `IdToken` in headers. Decide transport by origin then verb:
KC → `chrome_api_call` (bridge) primary, linked tab fallback; engagement/WPM/workbench/FP → bridge
primary, linked tab fallback.

### DOM is a viewport, not a database

**Inventory and verification are done by API, ALWAYS. The DOM is only ever consulted
for the row-identity of a specific, currently-VISIBLE row** (e.g. the ag-grid probe in
`annotate-tbreport.md`). Never read "what's in the binder / folder / form" from the DOM.

> **Scope — this rule is about BINDER/FOLDER inventory** (what workpapers/forms exist), which
> is lazy-loaded and AG-Grid-virtualized → a DOM walk undercounts. It does **NOT** cover
> KC-FORM **field enumeration**: for a single rendered KC form, the DOM (`kc_dom_parser`) is the
> better *fillable-field detector* — the GET over-reports fillable fields ~2:1 (phantom Comment
> columns + `visible:true`-but-unrendered rows). There, the flow is **DOM-first for what's
> fillable + an API `objectList:[]` side-check for empty add-grids** (see `fill-kc-form.md`).
> Writes and state-verification still go through the API/in-page GET. No contradiction: binder
> inventory = API; form-field detection = DOM; writes/verify = API.

The engagement binder UI is **master-detail and every folder is lazy-loaded**. When you
"stage" a folder by clicking it, the browser fires
`GET /v1/NewEngagementView/{clientId}/{locationId}/{engagementId}` and renders the
result — the unstaged folder's contents were never in the page at all. So:

- **There is no "stage" verb. Staging IS the GET.** Fire it yourself and you get identical
  data with no click and no render. A click's only unique value is at bootstrap, where it
  harvests engagement-side HEADERS (see session-bootstrap Cases B/C); after that, every
  folder is one GET.
- **"No forms visible" never means an empty binder.** It means your view is unstaged. Fresh
  binders are ALWAYS seeded with unfiled KC forms — read them with `folder_get(-4)`. The
  phrase "parse the unfiled forms" is **banned**; it's "GET folder -4."
- **Unfiled was never special** — it is lazy-loaded exactly like every other folder.

**Virtualization caveat (latent defect):** even a STAGED folder renders only its *viewport*
rows (AG Grid virtualization). A DOM row-walk of a long folder UNDERCOUNTS. This is why API
inventory is mandatory, and why the one legitimate DOM use — a single-row identity probe —
must first scroll the target row into view (see `annotate-tbreport.md`).

> `read_network_requests` (the Chrome-extension network log) is ruled out for capture — it
> misses the app's own XHRs. The `__cch_capture` monkey-patch is the only capture mechanism.

### HTTP 200 = accepted, not applied — re-GET after every write

**An HTTP 200 means the request was ACCEPTED, never that the write was APPLIED. No write
is reported successful until a state-confirming read of the same object passes.** This is
unconditional — this is an audit tool, and a silently-wrong workpaper write dwarfs the cost
of one extra GET. The re-GET is batchable: a single re-GET of a collection confirms a whole
batch of writes against it.

Three known silent-200s are just instances of this one rule:

- `UpdateProperty` returns 200 on a nonexistent collectionKey; the field's `state` stays 0
  `build_write_payload` now refuses a raw key.
- `set_index` returns 200 but the wrong field stays null — the real display field is `index`,
  not `documentIndex` (table below).
- `add_forms` returns 200; the truth is in `result[]` (which ECHOES successful adds — see
  `endpoints/kc_add_forms.json`).

**`index` vs `documentIndex` — which field carries the display index:**

| Object type | Display-index field | Notes |
|---|---|---|
| KCForms, Report | **`index`** | `set_index` must read back `index`; `documentIndex` is null/irrelevant here |
| Workpaper (integer-docId rows) | **`documentIndex`** | the Workpaper rows are the ones that carry `documentIndex` |

Reading the wrong field is the classic false-negative: the write applied, you checked the
field that was never going to change, and "concluded" failure.

### WPM surface — confirmed facts

- **Locale headers are load-bearing**: `USERLocale: en-US`, `Accept-Language: en-US,en;q=0.9`, `CountryCode: US` are REQUIRED on every WPM call. Without them GETs return **status 200 + empty array `[]`** for every folder — a silent failure that mimics an empty binder. `scripts.wpm` merges `http_runner.WPM_LOCALE_HEADERS` automatically.
- **`folder_get` returns a FLAT JSON array** — no `{lineItems}` / `{result}` wrapper.
- **Move PRESERVES the index and the locationId** (both stable across moves). Set-Index after Move exists for newly-added forms (null/empty index), not because Move clears anything. No re-GET needed after Move.
- **Folder create** (`POST /v1/NewEngagementView/folder`) returns the new locationId as a plain integer string.
- **Folder move semantics are inverted vs KCForms**: Folder uses `locationId=OWN, parentLocationId=DEST`; LeadSheet/KCForms/Report/Workpaper use the swap. `scripts.wpm._move_line_item` owns this — never hand-assemble.
- **Workpaper `documentId` == its `locationId`** (integer string), not a GUID. KC forms use GUID documentIds.
- **Workpaper PUT** (`/v1/Documents/{clientId}/{documentId}`) returns an EMPTY body on success — verify via follow-up GET.
- **GetBinder (KC) response is wrapped**: parse at `result.workpapers`, not top-level.
- **wpId lookup — GetBinder FIRST.** Any time you need a form's (or any workpaper's)
  `workpaperId`, `GET .../api/binder/GetBinder/{engagementGuid}` from the KC tab (`ls:kc` auth)
  — `result.workpapers[].id` is the source, carrying every workpaper with name + wpId. **Never
  walk WPM folders to find a form's workpaper.** Modules cite
  this, not their own copy.

### Form lifecycle

| Op | Endpoint | See |
|---|---|---|
| Add KC forms (batch) | `POST knowledgecoach.cchaxcess.com/api/binder/{eng}` | `endpoints/kc_add_forms.json` |
| Move object | `PUT workpapermanagementapi.cchaxcess.com/v1/NewEngagementView/{clientId}/folder/parent` | `endpoints/wpm_move.json` |
| Set form index | `PUT workpapermanagementapi.cchaxcess.com/v1/engagementview/{clientId}` | `endpoints/wpm_set_index.json` |
| Read form | `GET knowledgecoach.cchaxcess.com/api/Workpaper/{eng}/{wp}` | `endpoints/kc_read_form.json` |
| Write one property | `POST knowledgecoach.cchaxcess.com/api/Workpaper/UpdateProperty/{eng}/{wp}` | `endpoints/kc_update_property.json` |
| Submit pending | `POST knowledgecoach.cchaxcess.com/api/Workpaper/submit` | `endpoints/kc_submit.json` |
| Get binder forms | `GET knowledgecoach.cchaxcess.com/api/binder/GetBinder/{eng}` | `endpoints/kc_get_binder.json` |
| Get folder contents | `GET workpapermanagementapi.cchaxcess.com/v1/NewEngagementView/{clientId}/{folderId}/{engagementId}` | `endpoints/wpm_folder_get.json` |
| Toggle program step | `POST knowledgecoach.cchaxcess.com/api/Workpaper/UpdateProgramStep` | `endpoints/kc_toggle_step.json` |
| Soft-delete KC form | Move to "User to delete" folder via `wpm.soft_delete_form` | `modules/remove-kc-form.md` |

> **KC-form hard delete is NOT supported by this skill.** A `DELETE /v1/KnowledgeCoach/.../deleteform/...` returns 200 but corrupts the binder — `lastUsedTitleGuid` goes null and 30+ unrelated workpapers become invisible, with an empty Recycle Bin. To remove a form, use the soft-delete pattern in `modules/remove-kc-form.md`.

### KC form field model

A decoded form's `collections[i].objectList[j]` is a ROW; its `renderProperties` are the fields. `scripts.kc.inventory_form` classifies them; `classify_property` owns the rules; `build_write_payload` emits the correct write shape. Prefer these over the untyped `walk_fields`.

> **Field/valueKey conventions: see `references/config/field-conventions.md` (the registry).** It is the canonical map of every field-kind, valueKey convention, enum, per-prop rule, and collection-targeting rule — the code consumes it because the conventions are DATA not discoverable from the form GET.

- **`propertyType` (int) is the field-kind discriminator**, refined by `floatieType` + option-list length + a value sentinel:
  `0` = Answer (`select` if floatieType `Radio` / non-empty list / value sentinel `"Choose an item"` (valueKey `defaultanswer`); `multiselect` if `CheckBox` / sentinel `"Choose all that apply."`; else free text) · `1` = text (comment/description) · `2` = label (read-only Question/Name/HTML) · `3` = signoff (performedby/dates on program steps) · `5` = linked (system keys, IDs, cross-form values — read-only). Writable kinds: text, select, multiselect, signoff.
- **`floatieItemList` is ALWAYS `{isCustomizable, list}`** — never a bare array — and is present on EVERY field, so presence ≠ dropdown. Options live at `.list`; an empty list usually means a **convention-driven prop**, NOT free text — the valueKey is DATA the code carries (see `config/field-conventions.md`), so do NOT treat an empty `floatieItemList` as free-text/unwritable. When the list IS populated, the item's `key` is the `valueKey`. **The valueKey convention is UPPERCASE/compound:** yes/no props take `YES`/`NO` (lowercase `yes` is REJECTED → `resetanswer`); yes/no/NA props take the compound `YESNONA-YES` / `YESNONA-NO` / `YESNONA-NA`.
- **Write payload by kind:** text → `value`=text, `valueKey=""`. select → one `valueKey` from the field's own options. multiselect → `value`+`valueKey` semicolon-joined in ONE POST, full-state replacement (server strips a trailing semicolon). **signoff → the token (initials) goes in `valueKey`, NOT `value`** — a free-text write (valueKey="") is silently ignored (state stays 0).
- **Choice field with an EMPTY option list** (sentinel-detected select/multiselect, floatieType null, `.list` empty): options load only after a gating selection. Writing free text gets reset-rejected — **skip** it (or resolve options first). `build_write_payload` raises rather than emit free text.
- **Addable / repeating-table template rows** (object keys like `…-1`, e.g. `Analysis-1`, some `FinancialStatementUsers-N`): **the seeded `-1` row IS writable** — write to it directly. Only ADDITIONAL rows beyond the seeded one need a `build_spawn_payload` add first (and **spawn IS REST** — the spawned new GUID arrives empty, then fill by GUID). Note `inventory_form`'s `addable_grids` detector MISSES seeded-template grids, so do not rely on it to tell you a seeded `-1` row exists — read the raw collections.
- **Answered = `state==3 && isValueDefault==false`** (for signoff: `state==3 && valueKey!=""`). Fresh forms are `state 0` everywhere. **Writes land in a PENDING working copy — they are NOT committed until `POST /api/Workpaper/submit` (`{binderId, workpaperId:""}`), which is REQUIRED.** A reload/refresh DISCARDS any unsubmitted writes. So always verify AFTER reload (never the immediate post-write GET, which reads the pending working copy and gives false state-3 positives), and **settle ~1.5s** before that post-reload verify.
- **Tailoring gating = `objectList[i].visible`, and it's RECURSIVE.** Writing a choice makes the server recompute `visible` on dependent rows AND can populate a previously-empty option list on another choice (e.g. a controls-testing multiselect whose options appear only after audit areas are set). A single "TQs first, then the rest" pass misses the second wave. Fill choices in a **fixed-point loop** (write visible unanswered choices with options → re-read → repeat until none) BEFORE writing text/sign-offs. Treat a `reset*` valueKey as not-answered so a reset checkbox is retried once its options exist.
- **Silent rejection:** UpdateProperty returns 200 even when rejected; signature is a `valueKey` starting with `reset` — `resetanswer` (single-choice, state 2) or `resetcheckbox` (multi-choice, state 3). `scripts.kc.was_rejected` keys on the `reset` prefix.
- **KBA-502 OWNS the IR/CR/RMM/approach grid and is the WRITE target.** Write `collectionKey ".{AREA}.RelevantAssertion"` against **KBA-502's wpId**; the AUD-8xx program's grid is the DERIVED view — program-targeted writes land in a working copy the KBA-502-owned recompute discards on refresh. The grid is invisible to the bulk GET (`OverallAuditAreas[].childObjectList: []`) and to `inventory_form` (66/68 columns dropped) — write blind per the registry and verify via the diagnostics oracle. KBA-502's FinancialLevelRisks rows remain mostly pt5-linked (only `Comment` directly writable).
- **`inventory_form` over-filters grid forms — read raw `result.collections`.** For grid-style forms (KBA-4xx / KBA-5xx, e.g. `.KBA400.Scoping`, KBA-401 `*Findings`/`*TQ`) `inventory_form` drops collections whose cells bind by `columnID` (empty `bindingKey`) and under-reports the fillable surface. Bypass it and read raw `result.collections`, targeting the INPUT collection.
### Data import (dda.cchaxcess.com)

Engagement TB/data import wizard. The **Map** step maps arbitrary file columns to CCH fields, so the import file format is flexible.

- **openpyxl-written `.xlsx` is rejected** with "File upload failed. Please check the file is not protected in Excel" — CCH's Excel parser is picky about programmatically-generated workbooks. **CSV imports cleanly** — use CSV to sidestep the Excel-protection check.
- A **Class** column (account-type classification abbreviation, e.g. `CA` = Current Assets) is **only required when importing groups** — classes are tied to groups (can't create a group without a class), which is why it's gated. A plain TB import doesn't need classes; the valid class list can be pulled from the Classes screen later.

### Report lifecycle

| Op | Endpoint | See |
|---|---|---|
| Create TB report | `POST workbench-api.cchaxcess.com/v1/trialbalancereport/createReports` | `endpoints/tb_create_report.json` |
| Create JE report | `POST workbench-api.cchaxcess.com/v1/JournalEntryReport` | `endpoints/je_create_report.json` |
| List TB reports | `GET workbench-api.cchaxcess.com/v1/trialbalancereport/tbreports/{clientId}` | `scripts.reports.list_tb_reports` |
| List JE reports | `GET workbench-api.cchaxcess.com/v1/JournalEntryReport/{clientId}` | `scripts.reports.list_je_reports` |
| TB enum dictionary | `GET workbench-api.cchaxcess.com/v1/trialbalancereport/reporttypesandsettings` | `endpoints/tb_report_settings.json` |
| TB quota check | `GET workbench-api.cchaxcess.com/v1/trialbalancereport/{clientId}/checktbreportlimit` | `scripts.reports.check_tb_report_limit` |
| JE quota check | `GET workbench-api.cchaxcess.com/v1/JournalEntryReport/{clientId}/cancreate` | returns `{count, limit:100, canCreate}` |
| Grouping lists (report flow) | `GET financialprep-api.cchaxcess.com/v1.0/financialgrouptemplate/engagement/{clientId}` | `scripts.reports.get_grouping_lists` |
| Grouping lists (authoritative — what EXISTS) | `GET financialprep-api.cchaxcess.com/v1.0/financialList/{clientId}` | `scripts.groups.list_financial_lists` |
| Financial groups | `GET financialprep-api.cchaxcess.com/v1.0/FinancialGroup/{clientId}/{groupingListId}` | `scripts.reports.get_financial_groups` |
| Grouped TB rows (paginated; full `balances[]` row schema) | `GET financialprep-api.cchaxcess.com/v1.0/financialTrialBalance/{clientId}/{financialListId}/trialbalance/{periodId}` | `endpoints/fp_trialbalance.json`; `scripts.groups.get_trialbalance_grouped_all` |

**▶ FP trialbalance sign + key gotchas.** The FP-API serves balances
**credits-positive** — that is API-internal convention, NOT the TB import/export convention
(debits positive; see `modules/import-tb-format.md`). Flip signs when building import files
from API rows. And the subgroup key on a `balances[]` row is **`account.financialSubGroup`** —
`account.subGroup` exists but is **silently null**. Full row schema:
`endpoints/fp_trialbalance.json`.

**▶ Two grouping-list endpoints — don't confuse them.** `financialgrouptemplate/...`
feeds the report-creation picker (`reports.get_grouping_lists`). `financialList/{clientId}` is
the authoritative inventory of lists that actually exist on the engagement
(`groups.list_financial_lists`). To answer "does grouping list X exist?" use **`financialList`**.

**JE type IDs are positional, not alphabetical:** `AJE=1, TJE=2, PAJE=3, RJE=4`. See `references/config/je_types.json`.

**JE separate-mode naming:** `POST /v1/JournalEntryReport` with `SeparateReports: [1, 4]` creates reports named `{reportName}_AJE` and `{reportName}_RJE`. reportIds are issued sequentially in array order.

**Reports land in Unfiled Reports.** Filing into a binder folder requires Move + Set-Index via WPM. The TB create's `reportIndex` parameter stamps the workpaper's index attribute but does NOT auto-file.

**Report objectId for Move + Set-Index must be `tbreports/{integer_id}`, NOT `reports/{guid}`.** The integer id is the `id` field in the create response, or `documentId` in the WPM unfiled listing. Using `reports/{guid}` returns 200 on Move but is a silent no-op — the report stays in Unfiled.

**Token-triggered auth: install monkeypatch, then click "Trial Balance Report" button.** The create-report dialog triggers `GET /checktbreportlimit`, `GET /reporttypesandsettings`, `GET /tbreports/{clientId}`, and `GET /JournalEntryReport/{clientId}` with fresh tokens — all usable for subsequent XHR replays against workbench-api, WPM, and financialprep-api. Navigating to `/reports/{engId}/trialbalance/financial` + clicking the dialog button is the fastest token-refresh path for report work. Full page reloads (URL changes) wipe the monkeypatch.

**Flat folder list via `/v1/NewEngagementView/folders/{clientId}`.** Returns the full folder skeleton compactly (~4KB). **The body is WRAPPED: `{engagementId, root: [...]}` — the folder array is under `root`** (rows carry `locationId`, `locationGuid`, `index`, `name`, `parentLocationId`, `children`). The regex shortcut for locationIds still works on raw responseText and remains useful on the linked-tab transport, where `JSON.parse()` of the huge root-folder (`folderId=0`) CONTENTS endpoint times out CDP's 45s limit. Pattern: `"index"\s*:\s*"1100"[^{}]{0,400}"locationId"\s*:\s*"?(\d+)"?`.

### Fund TB Setup (governmental / NFP only)

| Op | Endpoint | See |
|---|---|---|
| List Fund Types | `GET workbench-api.cchaxcess.com/v1/FundType/{clientId}` | `endpoints/funds_fund_types.json` |
| Upsert Fund Types (whole-list PUT) | `PUT workbench-api.cchaxcess.com/v1/FundType` | `endpoints/funds_fund_types.json` |
| List Funds | `GET workbench-api.cchaxcess.com/v1/Fund/{clientId}` | `endpoints/funds_funds.json` |
| Upsert Funds (whole-list PUT) | `PUT workbench-api.cchaxcess.com/v1/Fund` | `endpoints/funds_funds.json` |
| List Fund Sub-Types | `GET workbench-api.cchaxcess.com/v1/FundSubType/{clientId}` | `endpoints/funds_fund_sub_types.json` |
| Upsert Fund Sub-Types (whole-list PUT) | `PUT workbench-api.cchaxcess.com/v1/FundSubType` | `endpoints/funds_fund_sub_types.json` |
| Read account-fund map | `GET workbench-api.cchaxcess.com/v1/Fund/{clientId}/fundaccountmap` | `endpoints/funds_account_map.json` |
| Assign/unassign accounts (incremental PUT) | `PUT workbench-api.cchaxcess.com/v1/Fund/{clientId}/fundassignment` | `endpoints/funds_account_map.json` |

**FundType new-entry id convention is the outlier.** New Fund and FundSubType records use `id: 0`; new FundType records OMIT the `id` key entirely. Sending `id: 0` to `PUT /v1/FundType` returns a 4xx. See `endpoints/funds_fund_types.json`.

**Fund/Sub-Type/FundType PUTs are whole-list replace, not incremental.** Caller must include every existing row (with its server-issued id) plus any new ones. Omitting an existing row deletes it.

**Account-fund unassign requires field absence, not null.** `PUT /v1/Fund/{clientId}/fundassignment` with `fundId: null` is NOT equivalent to omitting `fundId` — only the absent-key form sends accounts back to Unassigned.

**`engagementId` body field carries clientId on all Fund endpoints.** Same misnaming as the rest of workbench-api.

**Body-bearing writes need `Content-Type: application/json`.** Captured headers pulled from a recent GET don't carry Content-Type; replaying through `XHR.setRequestHeader` without it returns 415. `build_xhr_call`, `build_fetch_call`, AND `build_batch_xhr` (the path every KC form write goes through via `update_properties_sequential`) all auto-inject Content-Type when a body is present and the header isn't already set. Set it yourself whenever hand-rolling XHR outside the fixed helpers.

**The KC tab crashes on many sequential XHRs.** Looping N per-call XHRs through the
`knowledgecoach.cchaxcess.com` tab (e.g. one PATCH per account assignment) reliably hangs it —
`CDP Runtime.evaluate timed out after 45000ms`, forcing a reload. For any multi-write operation,
build ONE in-page JS call that does the whole batch internally (e.g. `build_bulk_assign_js`,
`build_chain_create_groups_js`) instead of N tool-layer round-trips. This is the same reason bulk
group assignment must go through the batched helper, not a Python loop.

### Ordering rules (do not violate)

1. **Set-Index only for genuinely NEW (null-index) forms.** Move PRESERVES the index (locationId stable); it does NOT clear anything. A Set-Index after Move is needed only when the form arrived with a null index (e.g. just added), never to "restore" an index Move supposedly wiped.
2. **PUT for Set-Index, not POST.** POST returns 200 but is a silent no-op.
3. **Sequential writes to one form, not parallel.** Concurrent UpdateProperty POSTs to the same form drop writes (server-side race).
4. **Submit after batch writes — PER-WORKPAPER, and submit COMMITS (persistence), not just counts.** Writes sit in a pending working copy; `POST /api/Workpaper/submit` `{binderId, workpaperId:"<wpId>"}` is what actually persists them, and a reload discards anything unsubmitted. An EMPTY workpaperId ("submit all pending in binder") silently DISCARDS pending writes on other forms — never use it. Even a scoped submit silently drops ~30–50% of writes, so always follow with verify-by-read + retry (field-conventions.md §5 3a). (Submit also refreshes the engagement-view diagnostic/missing-form counts, but that is secondary — the primary job is persistence.)
5. **Answer TQs before dependent descriptions.** Writing `*TQ = No` after populating that section's descriptions resets the descriptions to state=2. See "TQ-cascade" below.

### Pseudo-folder IDs (WPM)

In `GET /v1/NewEngagementView/{clientId}/{folderId}/{engagementId}`, negative `folderId` = pseudo:
- `-1` Unfiled Workpapers
- `-2` Unfiled Reports
- `-3` Unfiled Leadsheets
- `-4` Unfiled KC Forms

**You cannot MOVE an object INTO a virtual unfiled node** (`-3`/`-1`/etc.): a move targeting one
returns `400 "items can be moved to their respective unfiled nodes only"`. To relocate something
out of a real folder, create (or pick) a **real** destination folder first, then move — never
target a pseudo node as the move destination. (Pseudo nodes are read-only buckets the system fills.)

### Form schema patterns (KC)

- `result.elements` and `result.collections` are JSON-encoded **strings** — `json.loads` them.
- `result.collections[i].objectList[j].renderProperties[k]` — per-column. **Match `key` case-insensitively** (`Question`/`question` both occur). When writing back via UpdateProperty, **preserve original case** in `propertyKey`.
- Field is **answered** iff `state == 3` and `isValueDefault == False`. `state: 0` + `isValueDefault: true` with a `value` like "Yes" is the system's `recommendedAnswer`, NOT a real answer.
- Dropdowns: legal values in `floatieItemList.list` — always check before writing. Some fields only accept Yes/No (no N/A).

#### Floatie lookups — where renderProperties drops them

A renderProperty's `floatieItemList.list` is **frequently EMPTY** on row-level table dropdowns and on convention-driven props — even when options exist. **Empty does NOT mean free-text or unwritable**; on these props the valueKey is convention data the code carries (see `config/field-conventions.md`). When the list is empty, the actual option list may also live in the form's `elements` tree:

1. Walk `elements` for an object with `bindingKey == <PROPERTY_KEY>.toUpperCase()` (e.g., property key `"relevant"` → element bindingKey `"RELEVANT"`).
2. Read `element.floatieList` (a global ref string, e.g. `"global.yesno"`) and `element.floatieItemList.list`.
3. **The valueKey sent to UpdateProperty is UPPERCASE/compound, NOT the lowercase display key:** yes/no props → `YES`/`NO` (lowercase `yes` is rejected → `resetanswer`); yes/no/NA props → `YESNONA-YES` / `YESNONA-NO` / `YESNONA-NA`. Same convention as everywhere else in KC.

Helper: `scripts.kc.find_dropdown_options(decoded_form, property_key)`.

#### The `resetanswer` signal — silent write rejection

`UpdateProperty` returns HTTP 200 even when CCH rejects the value. The rejection signature on a re-read (or in the response body, which echoes the updated form) is:

| field | value |
|---|---|
| `state` | `2` |
| `valueKey` | `"resetanswer"` |
| `value` | `"Choose an item"` |
| `isValueDefault` | `True` |

After every write, check the field state. 200 is not "accepted" — only state==3 + isValueDefault==False is.

Helper: `scripts.kc.was_rejected(prop_before, prop_after)`.

#### KBA-302-class row dropdowns — SOLVED (UPPERCASE valueKey + INPUT collection)

These Radio properties tied to `floatieList: "global.yesno"` on **row-level table objects** write
via standard `UpdateProperty` when you (a) use the **UPPERCASE / compound valueKey convention**
(`YES`/`NO`, or `<OPTSET>-<VALUE>` such as `YESNONA-YES`), and (b) target the **INPUT collection**
(`*Findings` / `*TQ`), NOT the display collection. A 200 + `resetanswer` on these means wrong key
or wrong collection, not a missing endpoint.

Affected collections in KBA-302 (NFP title `2026=Knowledge-Based Audits of Not-for-Profit Entities`)
— all writable via the above:

```
.KBA302.IndustryCondition          .KBA302.RegulatoryEnv
.KBA302.OtherExternalFactors       .KBA302.BusinessOperation
.KBA302.Governance                 .KBA302.Investment
.KBA302.FinancingFactors           .KBA302.FinancialReports
.KBA302.GroupWideControl           .KBA302.ConsolidationFactors
.KBA302.EntitiesObjectives         .KBA302.MeasurementandReview
.KBA302.IncentivesandPressure      .KBA302.Oppurtunities
.KBA302.AttitudesRationalizations  .KBA302.FRFIncentives
.KBA302.FRFOppurtunities           .KBA302.FRFAttitudes
.KBA302.IllegalActs
```

Fill them directly — do NOT skip them as "supplementary." Section-level `*Understanding`,
`*ProPerformed`, `*Comment` description fields are filled in addition, not instead.

#### TQ-cascade

KBA-302 (and likely other KBA forms) has section-level tailoring questions (`*TQ` paths) that gate dependent narrative fields. Writing `*TQ = No` after you've populated that section's `*Understanding` / `*ProPerformed` / `*Comment` fields will **reset those descriptions to state=2** (treated as N/A by CCH; no diagnostic generated, but the text is gone).

Ordering rule:

1. Answer TQs FIRST.
2. Skip description writes for any section whose TQ is No (they're going to N/A anyway).
3. Write descriptions only for sections where TQ is Yes.

### Cross-reference extraction

- Pattern: `\b([A-Z]{3}-\d{3,4}[A-Z]?)\b`
- Denylist (config/xref_denylist.json): `SAS-*`, `AU-*`, `ASC-*`, `IFRS-*`, `RES-*`, `RPT-*`. These are accounting/auditing standards, not KC forms.

### Move payload semantics (the genuinely confusing part)

For `objectType` in `{"LeadSheet", "KCForms", "Report"}`:
- `locationId` = **DESTINATION** parent
- `parentLocationId` = the **object's own** current locationId

For `objectType == "Folder"`:
- `locationId` = the **folder's own** current locationId
- `parentLocationId` = **DESTINATION** parent

The semantics swap between Folder and everything else. `scripts/wpm.py` hard-codes the correct mapping per type — module code never assembles the move body by hand.

### Auto-file cascade

When a leadsheet is moved to a parent folder containing a sub-folder whose index matches the leadsheet's index, CCH auto-files it AND cascades — every other unfiled leadsheet in the binder with a matching sub-folder also gets auto-filed in one operation. Single move can have wide effects. Verify after.

### Deep-link URL patterns

```
Engagement view: https://engagement.cchaxcess.com/en-US/engagement/{clientId}/engagementview/{engagementId}
Reports:         https://engagement.cchaxcess.com/en-US/engagement/{clientId}/reports/{engagementId}/{reportType}
TB report:       https://engagement.cchaxcess.com/en-US/engagement/{clientId}/tbreports/{reportGuid}/period/{engagementId}/subsidiaryParentId/0
                 (individual TB reports ARE deep-linkable — by GUID, never the integer id; folder depth irrelevant.)
System leadsheet: https://engagement.cchaxcess.com/en-US/engagement/{clientId}/reports/{engagementId}/leadsheets/{financialGroupId}
Recycle Bin:     https://engagement.cchaxcess.com/en-US/engagement/{clientId}/wpRecycleBin
KC form:         https://knowledgecoach.cchaxcess.com/binder/{engagementGuid}/workpaper/{workpaperId}
```

Report types observed: `trialbalance`, `financials`, `fsr`, `tsr`, `ratioanalysis`. Trial balance has a `/financial` sub-route: `/reports/{engagementId}/trialbalance/financial`. Loading this page is required before the workbench-api `createReports` button is reachable — going straight to Unfiled Reports doesn't expose the dialog.

### SSO handshake (do NOT forge)

```
https://knowledgecoach.cchaxcess.com/home/callback?code={oauth-code}&state={deep-link}&session_state={...}
```

The `code` is single-use. Never replay a callback URL. To navigate KC programmatically, trigger the engagement-app button that fires the SSO handshake.

## Relationship to the published Wolters Kluwer "Audit Engagement API"

Wolters Kluwer publishes a developer portal at `developers.cchaxcess.com` that lists an **Audit Engagement API v1**. It is **NOT the same surface this skill uses.**

| | This skill captures | WK publishes |
|---|---|---|
| Style | REST | GraphQL |
| Host | `workbench-api`, `financialprep-api`, `workpapermanagementapi`, `knowledgecoach` (4 subdomains) | `api.cchaxcess.com/audit/engagement/v1` |
| Surface | Report creation, workpaper CRUD, KC form read/write, TB rows, JE data, grouping data | 7 read-only query operations: `clients`, `engagementDetails`, `engagementTemplates`, `engagementTypes`, `engagementViewDetails`, `engagementsList`, `trialBalanceImportStatus` |
| Purpose | Internal Angular SPA backend — what the CCH Axcess Engagement web app itself talks to | Third-party integration — designed for outside tools to query metadata |

**Implications:**
- The published API can't do what this skill needs: it has no create/update operations, no workpaper or form access, no journal entry reads. It's a read-only metadata window.
- The internal endpoints this skill captures are undocumented and not promised to be stable across CCH Angular updates. If a procedure breaks, re-capture before assuming a regression.
- Don't waste cycles searching for a public spec for the operations in this skill. There isn't one. The endpoint JSON specs in `references/endpoints/` ARE the source of truth.

## Drift monitoring — `tools/cch-drift` (maintainer tooling — NOT shipped with this skill)

Because the surface above is unversioned, the skill MAINTAINER runs a standalone checker
(`Documents/Code/tools/cch-drift/` on the maintainer's machine — deliberately outside this
distributable skill; if you installed this skill and that path doesn't exist, this section
isn't for you). It is pure Python over
the chrome-bridge WebSocket — no agent in the loop — and runs three read-only layers: bridge
health + extension pin; SPA asset-manifest version watch on the engagement and KC origins (a
changed bundle set = WK shipped a release → expect drift, re-run everything); and per-endpoint
shape probes asserting this file's invariants (wrapped-vs-flat bodies, `financialSubGroup`,
JSON-encoded-string form fields, the report enum dictionary, the KC title refTag set as a
new-edition detector), each with a structural fingerprint diffed against a stored baseline.
Exit codes: 0 green / 1 drift / 2 infra-down. On a FAIL or a version WARN: fix the matching
`endpoints/*.json` + this file BEFORE the next engagement run, log the change in the CHANGELOG
(source repo), then `--update-baseline`.

A fourth layer, `--layer bundle`, **lifts the endpoint MAP out of the SPA JS** (fetch the
bundles, extract every `/v1`·`/api` path literal, diff the set vs baseline). It's the cheap half
of "stop re-capturing after every release": on a version WARN it points a human at exactly which
endpoints moved, so the fix is a reviewed diff, not a hand re-capture. It lifts the *map* only —
the app's own code can't be lifted and fired standalone (it's entangled with the running app's
injector/auth/component state), and payload bodies are past reliable static extraction, so the
api/write layers still validate contract + semantics. NOT run under `all` (it fetches every JS
asset); run it after a version WARN.

## Annotations (leadsheet & TB report)

Two annotation surfaces, two transports (matrix above): **financialprep-api takes the
`"ls:fp"` sentinel** (KC localStorage, any tab); **workbench-api takes monkeypatch-captured
headers from the engagement tab only**. All calls go out as XHR. **Every write requires a
page refresh to appear in the UI.** No triple-fire (single call).

**The mirror is ONE-DIRECTIONAL:** FP-API bubbles/tickmarks
(written on the system-lead surface) render read-only on TB reports (`cpComments`/
`cpTickMarks`); workbench Remarks-column values (REF, Notes) appear NOWHERE but the TB
report. Two parallel protocols, routed by which surface the user is on:
- **System leadsheet (protocol A):** "comment"/"note"/"tickmark" → FP-API bubble
  (`annotate-leadsheet.md`). Remarks columns don't exist on this surface.
- **TB-report leadsheet (protocol B, the firm DEFAULT):** "REF"/"reference"/"cross-ref"/
  "imm" → the Remarks_1 "REF" column; "note"/"comment" → the Remarks_2 "Notes" column — a
  real editable column, not a bubble (`annotate-tbreport.md`).
A filed system lead ⇒ that user is bubble-only (see annotate-tbreport.md terminology block).

### financialprep-api.cchaxcess.com — system leadsheet

Three native annotation types: top-level comment box, inline account comments, tickmarks. (A fourth, workpaper-reference, is not yet captured.) Scripts: `scripts.leadsheet.*`; module: `references/modules/annotate-leadsheet.md`.

| Operation | Method | Path | Spec |
|---|---|---|---|
| List leadsheet groups | GET | `/v1.0/leadsheet/{clientId}/1/groups` | `endpoints/fp_leadsheet_get.json` |
| Get leadsheet (per-account referenceIds) | GET | `/v1.0/leadsheet/{clientId}/1/groups/{financialGroupId}?periodId={periodId}` | `endpoints/fp_leadsheet_get.json` |
| Comment box write/clear | PATCH | `/v1.0/leadsheet/Comments` | `endpoints/fp_annotation_comment.json` |
| Account comment upsert | POST | `/v1.0/Annotation/comment/{clientId}` | `endpoints/fp_annotation_comment.json` |
| Account comment delete | DELETE | `/v1.0/Annotation/comment/{clientId}/{commentReferenceId}` | `endpoints/fp_annotation_comment.json` |
| Tickmarks set/clear | POST | `/v1.0/Annotation/tickmarks/{clientId}` | `endpoints/fp_annotation_comment.json` |

- `referenceId` = `account.id` from the leadsheet GET (`subGroupBalances[].account[].account.id`) — a CCH-internal integer, NOT the account-number string. Account numbers use a 5-digit prefix (`20000-300`).
- Account comment POST returns `{"commentReferenceId": <int>}` — store for DELETE. Edit = re-POST (server upserts by referenceId+periodId).
- Tickmarks POST is **set-replace** — send the complete desired set; `[]` clears. ID catalog (1-71) in `references/config/tickmark_ids.json`.

### workbench-api.cchaxcess.com — TB report REF/Notes (Remarks_1/Remarks_2)

Remarks-column annotations on TB reports. Separate API; Remarks-column values live on the
TB report ONLY (one-directional mirror — see above). Firm standard is
TWO Remarks columns per TB-report leadsheet: Remarks_1 named "REF" (cross-refs/index/imm
tags), Remarks_2 named "Notes" (free notes). **Step-0 preflight is mandatory**: the report
must HAVE the Remarks column(s) it needs (`tbreportedit` GET → `reportFormat.columns`; add
one via `editReports` PATCH — `endpoints/wb_editreports.json`, once per missing column).
Scripts: `scripts.leadsheet.tbreport_*`, `scripts.reports.add_remarks_column`; module:
`references/modules/annotate-tbreport.md`.

| Operation | Method | Path | Spec |
|---|---|---|---|
| Remarks-column preflight (Step 0) | GET | `/v1/trialbalancereport/tbreportedit/{clientId}/{engGuid}/{reportGuid}` — body has NO usable id; integer reportId = WPM documentId | `endpoints/wb_tbreportcomment.json` |
| Add/rename/remove a Remarks column | PATCH | `/v1/trialbalancereport/editReports` | `endpoints/wb_editreports.json` |
| Create/edit REF or Notes | POST | `/v1/trialbalancereportcomment/{clientId}/{reportId}` | `endpoints/wb_tbreportcomment.json` |
| Delete REF or Notes | DELETE | `/v1/trialbalancereportcomment/{clientId}/{reportId}/{reportCommentReferenceId}/{columnId}` | `endpoints/wb_tbreportcomment.json` |

- `columnId` is positional and tied to the column's `Remarks_{N}` id — `Remarks_1` → 1, `Remarks_2` → 2. RENAME-PROOF (heading text irrelevant).
- Row identity from the ag-grid row node — no API call (`scripts.leadsheet.tbreport_row_probe_js`). `referenceType` is BY ROW LEVEL: Fund row → `Fund` (+`referenceGuid` REQUIRED); group-total row → `FinancialGroup`; subgroup row → `FinancialSubGroup` (both omit `referenceGuid`).
- POST returns `{"reportCommentReferenceId": <int>}` — note the field name differs from FP-API's `commentReferenceId`.

## What's NOT in here

Workflows (the sequence of these endpoints) live in module files. Engagement-specific runtime data (form indexes, cross-references, decisions) is written to the **user's working folder** (e.g. `{engagement}-xrefs.xlsx`), NOT into this read-only install. Bearer tokens never live anywhere — always capture fresh.


<!-- END -->
