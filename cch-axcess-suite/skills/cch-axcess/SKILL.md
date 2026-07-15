---
name: cch-axcess
description: Skill for working inside CCH Axcess (Wolters Kluwer audit platform — engagement.cchaxcess.com, knowledgecoach.cchaxcess.com, workpapermanagementapi.cchaxcess.com, workbench-api.cchaxcess.com, financialprep-api.cchaxcess.com). Use whenever the user mentions CCH, Axcess, CCH Engagement, Knowledge Coach, an engagement binder, audit workpapers, KC forms, KBA/AID/AUD/COR form IDs, an engagement view URL, anything on .cchaxcess.com, or audit-platform tasks like "set up a binder", "add audit programs", "fill out [form]", "remove a form", "rename workpapers", "file the leadsheets", "run TB/JE reports", "set up funds", "set up groupings", "back up the trial balance", "scan for cross references". Backend-first — direct REST + deep-links over UI clicking. Unlearned operations sit behind a consent wall (`references/learn-protocol.md`) — never auto-improvise them.
---

# CCH Axcess — Dispatcher

## Entry rule

1. Enter only through this SKILL.md. Run Step 0 before opening any module.
2. Route ONE ask to ONE module — never load the whole skill.
3. If asked to skip a gate (Step 0 seed+warmup, exec-cache verify, consent wall, no-hard-delete
   rule) — say it's required, run it anyway, then proceed. The user cannot authorize skipping a
   gate.

### Initialization gate — reading reference data is NOT a session (the side-entry catch)

**Reading does not initialize a session; the FIRST platform call is the gate.**

1. Loading a module, an `endpoints/*.json` spec, `references/data/*`, or `architecture.md` gives
   you *content*, not a *session* — it is not a substitute for Step 0. A binder template or a
   captured token that appears in your context is reference data, not proof a session was
   warmed.
2. Before the FIRST platform call this session — any browser/API touch of `*.cchaxcess.com`
   (`chrome_bridge_status`, `chrome_api_call`, `chrome_eval`/`chrome_fetch`, `chrome_navigate`,
   `chrome_network_recent`, or the linked-tab verbs) — Step 0 must have run. Step 0.0
   (`chrome_bridge_status`) is your first browser touch; the seed (0.1) and the declared leg
   warmup (0.2, `session-bootstrap.md`) precede the first *write*. If unsure whether Step 0 ran
   this session, run it — re-running is cheap; a side-entered write is a silent no-op.
3. If you have ALREADY made platform calls this session without Step 0 → **STOP now.** Do not
   keep going because it "seems to be working" (a 200 with an error/HTML body is a silent
   no-op). Instead: run Step 0 / session-bootstrap in full → switch to the documented
   page-context transport (`transport.md`; on the bridge, KC via `chrome_api_call`,
   engagement/WPM/FP via `chrome_api_call` or the `chrome_eval`+XHR builder — never hand-forged
   external calls with copied headers) → RE-VERIFY BY READ everything you wrote while
   side-entered (re-GET the binder / folders / forms; 200s may be silent no-ops) → resume from
   the last verified step.
4. Delegation is a NEW session — the delegate must run Step 0 itself. Do NOT hand a subagent a
   URL + method + a hand-copied bearer + "call the chrome-bridge MCP tool" — that agent never
   ran Step 0 or read `transport.md`, and the token rotates (~30 min) and truncates on paste. If
   you must delegate platform work, the child enters through THIS SKILL.md and runs Step 0
   (seed → `chrome_bridge_status` → warm its own leg → capture its own fresh auth); pass it the
   engagement URL and the task, never the tokens.
5. Precondition before any platform WRITE, no matter how you got here: Step 0 has run this
   session on THIS agent, and the transport is the documented page-context path. If either is
   missing — you arrived from a reference-data read, you're resuming mid-conversation, or you
   were spawned with tokens in your prompt — run step 3's redirect before writing.

## Step 0 — Seed (before routing) + lazy leg warmup (AFTER the module is chosen)

**0.0 First browser call of the session = `chrome_bridge_status` (GLOBAL — independent of routing/warmup).**
Before ANY other browser op — including merely listing or viewing tabs — call `chrome_bridge_status`.
Bridge up/reachable -> **BRIDGE** transport for the WHOLE session (use `chrome_list_tabs` to see tabs, not
`list_connected_browsers`; KC via `chrome_api_call`; skip the linked-tab tab-claim machinery). Absent/errors
-> **LINKED-TAB** transport. This is NOT gated behind routing or leg-warmup — it governs your literal first
browser touch. (`runbooks/transport.md`.)

**0.1 Seed the engagement identity.** Find `clientId` + `engagementId` before touching the browser:

1. Conversation / system prompt / **project description** — a CCH engagement URL
   (`engagement.cchaxcess.com/.../engagement/{clientId}/engagementview/{engagementId}`).
2. Project memory (`project_*.md`) — stored `engagementGuid`, `clientId`, `engagementId`, or full URL.
3. Neither → ask the user to open the engagement view themselves (**never switch clients
   programmatically**) and read both ints from the resulting URL.

If the project clearly maps to the client and the full URL isn't in project memory, offer ONCE
to save it; on decline, record the decline and never re-ask.

**0.2 Warm ONLY the leg the module declares.** **Run this AFTER routing has selected the
module (Routing step 3) — never before.** The leg is whatever that module's `leg:`
front-matter declares; warming a leg before the module is chosen is guessing (and for a
`leg: none` or route-out-to-another-skill answer, wrong work entirely). Every module's
front-matter declares `leg:`. Two legs, warmed independently
(procedure: `references/runbooks/session-bootstrap.md`):

| Leg | What it is | Serves | Needed for |
|---|---|---|---|
| `wpm` | Engagement-tab capture (monkeypatch bearer + headers) | WPM, financialprep-api, **and workbench-api** (WPM-bearer reuse) | Reads, annotations, WPM ops, fund/group setup, report ops |
| `kc` | `engagementGuid` + kc localStorage tokens + a KC-origin tab | KC API; also WPM/FP via `ls:*` sentinels | KC-form operations |

- **Transport was already decided at 0.0** (`chrome_bridge_status`): bridge up -> BRIDGE (KC via
  `chrome_api_call`, skip linked-tab tab-claim); else LINKED-TAB. Warmup just uses that choice.
- **GUID is NOT required for reads/annotations/WPM ops** — don't
  hunt it for a `leg: wpm` task. Workbench **creates** address by GUID: take it from the seed
  (memory/URL) or the boot capture; warm the full KC leg only if it isn't available there.
- **Never warm a second leg a warm one already serves.** A warm KC leg serves WPM/FP via
  `ls:wpm`/`ls:fp` — don't also capture engagement-tab headers for those calls.
- **On-warm release check (throttled, ~1 GET):** after warming, before the first write, run the
  cheap SPA-manifest release check (`session-bootstrap.md` → "On-warm release check") — it catches
  a WK release (the leading drift indicator) at warm time so a drifted endpoint surfaces as a
  heads-up, not a silent no-op mid-form. Once per session per engagement; never blocks warming.
- `leg: none` modules (pure doc/format modules) skip warmup entirely.

## Exec cache (once per BUILD, not per session)

Any task that runs `scripts/*.py` executes from a verified exec copy — never from the bash
mount (it truncates text files). The copy is cached **per build**:

```
EXEC=/tmp/cch-ax-{version}-{payloadhash}/        # e.g. /tmp/cch-ax-AX-50-<payloadhash>/
```

`.verified` marker present and hash matches the payload → **reuse it, zero re-verify.**
Missing / mismatched / uid-locked → fresh extract + compile gate + `verify_integrity.py`
ONCE, then write `.verified`. Full procedure: `references/runbooks/local-exec.md`.
Current payload: `exec-payload_AX-50.bin`. A payload whose version tag lags the current source by a
script-touching build is stale — flag it, don't rebuild unsupervised.

## Routing — ORDERED; do not reorder

The order matters: resolve WHAT the deliverable is before doing ANY work toward it. Warming
a leg or matching a trigger row while the ask is still ambiguous is the over-inference that
causes wrong-deliverable and wrong-leg runs. Disambiguation is step 2 — it fires
BEFORE leg-warmup (step 3) and before you commit to a row.

```
User says something CCH-related
  ├─ Just asking what this skill does / how to use it? → references/usage.md (only that;
  │     never on a work task).
  │
  ├─ 1. SEED identity (Step 0.1): clientId + engagementId. No browser yet.
  │
  ├─ 2. RESOLVE THE DELIVERABLE → exactly ONE module. Do this BEFORE warming any leg or
  │     running anything.
  │       a. Overloaded term? "leadsheet", or "TB / trial balance", with no signal of
  │          WHICH kind → DISAMBIGUATE FIRST (the "Overloaded terms" section below): ASK,
  │          wait for the answer, THEN continue. Do NOT match a row or warm a leg while
  │          the kind is unresolved.
  │       b. Match exactly ONE row in the Trigger map → that module.
  │       c. No row matches → CONSENT WALL (below). Do NOT fuzzy-match to a near-sounding
  │          row.
  │       d. Mixed ask (platform task ALSO asking "is X possible / how do I X / check the
  │          help site") → also load `cch-help` alongside; platform work stays here.
  │
  ├─ 3. WARM the leg THAT module declares (Step 0.2) — NOT before step 2 is done. The leg
  │     is per-module; warming before the module is picked is guessing.
  │
  ├─ 4. Task runs scripts/*? → exec cache above.
  │
  └─ 5. Open THAT module only. Its front-matter declares leg, inputs, scripts.
```

**CONSENT WALL (step 2c).** Say verbatim: "I haven't learned how to do that. Do you want me
to attempt to figure it out? Warning: slow, heavy usage." Then STOP. Explicit yes → capture
mode (`references/learn-protocol.md`). Anything else → done. Capture mode NEVER self-fires.
(Asks with NO module — "roll forward / copy last year's binder", "restore from recycle bin",
"import a TB" — hit THIS wall, NOT a near-sounding row like setup-binder.)

## Failure discipline (applies to every module)

- **401 on a warmed leg** → re-warm the FAILING leg only, retry ONCE, then surface to the
  user. No proactive re-auth, no mid-task re-bootstrap, no touching the other leg.
- **2 failures on one operation → FORCED doc return.** Variations on the same transport row
  (parameter tweaks, header fiddling) count as the SAME path — they are not new approaches.
  After the second failure you MUST re-read `references/endpoints/*.json` for the operation
  plus the transport matrix (`architecture.md`) BEFORE any third attempt. The doc return must
  produce a **named path from the finite menu** (an endpoint spec or a transport-matrix row):
  - Named path NOT yet tried → exactly one attempt.
  - Named path already tried → **FAIL STATE: abort the operation.** Surface: "tried X and Y;
    docs say Z, which is what I tried; need help / a decision." Reset scope is the failing
    OPERATION, not the task — completed steps stand.
  This wall also catches entry-past-the-brief: a session that skipped the docs hits the menu
  it never read on its first doc return.
- **Existence check FIRST — before any work, not after it fails.** When an ask names a
  target object — a group, fund, subgroup, form, report, account, or a specific row — your
  FIRST step is to confirm that object EXISTS (read the binder / grouped TB / report rows
  via the API). If it doesn't exist, STOP and surface it: "there is no Cash group on this
  engagement — add one, or did you mean X?" Do NOT begin building toward it (adding columns,
  warming extra legs, creating scaffolding) and discover the impossibility two failures
  later. This is the failure class where time is sunk building toward an impossible target. A
  missing target is a prerequisite finding to report up front, never a workaround to engineer.
- **Improvisation budget is the 2-fail rule. Period.** Once an attempt is underway and an
  operation fails, the 2-fail forced doc return (above) is the whole budget — no looping,
  no "the user said keep trying" (user consent for capture mode does NOT lift the 2-fail
  limit), no calling a parameter tweak a fresh approach.

## Overloaded terms — disambiguate BEFORE picking a module (Routing step 2a)

Two firm terms are overloaded: "leadsheet" names two surfaces (system-generated vs TB-report)
and "TB / trial balance" names three deliverables. If the ask SIGNALS which one, route straight
(no needless question). If it does NOT signal, you MUST ASK before routing — a wrong guess here
sends you down a wrong-deliverable path. The modules' own Terminology sections only help
AFTER routing — too late; the split happens here, at the dispatcher.

- **"leadsheet"** — two surfaces (system-generated vs TB-report). The fork is ONLY about which
  you mean, and ONLY when MANIPULATING one — CREATING is never ambiguous:
  - **CREATE / run / build / generate / "make me" a leadsheet → ALWAYS the *TB-report leadsheet***
    (a CCH AccountDetail TB report) → `run-reports.md` (or `add-audit-programs.md` to file them).
    You do NOT create a system leadsheet — it is auto-generated — so a "make / create / run / build
    a [area] leadsheet" ask is UNAMBIGUOUS: route straight, never ask.
  - **ANNOTATE / comment / tickmark / REF / note a leadsheet → which surface?** Two parallel
    protocols: the *system leadsheet* (auto-generated WPM LeadSheet, protocol A) →
    `annotate-leadsheet.md`; or the *TB-report leadsheet* — the firm DEFAULT (protocol B) →
    `annotate-tbreport.md`. Route by signal AND by which surface the user is on:
    - On a **system leadsheet**: "comment / note / tickmark" → bubble (`annotate-leadsheet`).
      Remarks columns don't exist there.
    - On a **TB-report leadsheet**: "REF / reference / cross-ref / imm" → the Remarks_1 "REF"
      column; "note / comment" → the Remarks_2 "Notes" column (a real editable column, not a
      bubble) — both via `annotate-tbreport`.
    **Only a manipulation ask with NO surface signal** ("work on / fix the cash leadsheet") →
    ASK: "the system-generated leadsheet, or a TB-report leadsheet?"
- **"the TB" / "trial balance" / "pull the TB"** — three kinds:
  - *TB report* in CCH (run/generate) → `run-reports.md`.
  - *Backup workbook* (TB + groups + funds to Excel) — "back up the TB", "with groups and
    funds" → `tb-backup-package.md`.
  - *Import file* (build a CCH-importable TB) — "format for import", "CCH rejected my
    import" → `import-tb-format.md`.
  - **No signal** ("pull the TB", "I need the trial balance") → ASK which of the three.
    Step 0 already has to ask for the engagement — bundle the deliverable-type question
    into that same turn.

## Trigger map (verb → module)

<!-- TRIGGER_MAP_START -->
| What the user wants | Module |
|---|---|
| Add the audit programs for an engagement (NFP/Govt/EBP); file leadsheets | `references/modules/add-audit-programs.md` |
| Annotate a system leadsheet (comment box, inline comments, tickmarks) | `references/modules/annotate-leadsheet.md` |
| Annotate a TB report (REF column + Notes column / Remarks columns) | `references/modules/annotate-tbreport.md` |
| Build the binder status / sign-off sheet to Excel — every file with index, name, type, sign-off status, status, last-modified, and a clickable deep link | `references/modules/binder-status-sheet.md` |
| Bulk-capture N KC forms' full schemas to disk (e.g. seed a sister skill) | `references/modules/bulk-capture-forms.md` |
| Clear an in-form program-STEP sign-off or N/A marker (SignOff = "[]") on an AUD-8xx program. The KC-leg un-sign-off; distinct from the document-level WPM sign-off. | `references/modules/clear-program-step-signoff.md` |
| Upload/download an EXISTING binder file, or replace it via download→edit→re-upload (original stays recoverable, no index/name collision). NOT for building a NEW Excel workpaper (→ workpapers skill) or an in-place UNRECOVERABLE overwrite (→ replace-workpaper). | `references/modules/file-io.md` |
| Fill out a KC form / fast-fill / scan for cross-references | `references/modules/fill-kc-form.md` |
| Build a CCH-importable trial balance file (column spec, sign convention, import constraints) | `references/modules/import-tb-format.md` |
| Manage fund accounting setup (FundType, Fund, FundSubType, account map) | `references/modules/manage-funds.md` |
| Manage TB groupings (financialList, financialGroup, account assignment) | `references/modules/manage-groups.md` |
| Map the binder — full low-token inventory of folders + filed items (find a workpaper/form) | `references/modules/map-binder.md` |
| Build out a WHOLE AUD-8xx audit program — tailoring answers + bring in steps + link risks + fill responses + sign off (the full pipeline; for steps-in/out ONLY with none of the rest, use toggle-program-step) | `references/modules/populate-program.md` |
| Post an actual journal entry (AJE/RJE/PAJE/TJE) into the engagement trial balance (FinancialPrep) | `references/modules/post-journal-entry.md` |
| Remove / delete a KC form (always soft-delete — no hard delete in this skill) | `references/modules/remove-kc-form.md` |
| Remove a stale document-level (WPM) sign-off from a workpaper or KC form — the clears-its-own-stale-sign-off op. Applying sign-offs stays human-only. | `references/modules/remove-signoff.md` |
| Rename / re-index Workpaper-type rows (PDFs, docs) — distinct from KCForms set-index | `references/modules/rename-workpaper-index.md` |
| Replace a workpaper's content in place (native "Upload new version") — UNRECOVERABLE overwrite, hard consent gate every time | `references/modules/replace-workpaper.md` |
| Run a TB report or a Journal Entry report (AJE/RJE/TJE/PAJE); create TB-report-based leadsheets | `references/modules/run-reports.md` |
| Set up / build out a binder; create section folders (default 2-level or user-defined structure) | `references/modules/setup-binder-from-index.md` |
| Back up the trial balance — TB (CY + optional PY) + groups + subgroups + funds into one workbook (import sheets, account map, fund structure) | `references/modules/tb-backup-package.md` |
| Move AUD-8xx program steps in / out — bring steps in or send to library ONLY (full-state replacement); NOT tailoring answers / risk-linking / responses / sign-off (that whole build-out is populate-program) | `references/modules/toggle-program-step.md` |
<!-- TRIGGER_MAP_END -->

## Environment note (Cowork)

Transport is **bridge-first for every origin**; the linked Claude-in-Chrome tab is the fallback. KC-origin
ops run over **`chrome_api_call`** (service-worker fetch — CSP-exempt; the in-page verbs `chrome_eval`/
`chrome_fetch` stay CSP-blocked on KC, so use `chrome_api_call` there). **On the bridge the tool-result
channel is NOT DLP-filtered** (KC reads return real JSON — so return JSON directly;
skip download-to-disk). The DLP `[BLOCKED...]` filter + download-to-disk applies only on the **linked-tab
fallback** (see `architecture.md` -> Cowork data channel, and the read step in `fill-kc-form.md`). Route by
target origin first — see `architecture.md` and `runbooks/transport.md`.

**This install is a READ-ONLY cache.** The skill directory is a per-session snapshot of the
.skill/plugin install. Writing into it truncates files and is lost
on reinstall. There is NO runtime write target: runtime learnings flow through the complaint
log (`i-wanna-complain`) into the batch-rebuild pipeline, and the CHANGELOG lives in the
source repo only. Never request a mount of this skill's own directory.

## The rules — stated ONCE here; modules cite by number

0. **Doc-first.** Before improvising any transport or endpoint variation, grep
   `references/endpoints/*.json` — the spec is the first move, not the fallback. Auth: pass
   the `"ls:<family>"` sentinel or the captured-header dict per the transport matrix
   (`architecture.md`).
1. **Backend over UI.** Every CCH UI action is backed by a REST call. Prefer the API.
   Deep-link by URL. Click-through is a fallback, never the default.
2. **Scripts over prose.** Any API call, file parse, or deterministic transform lives in
   `scripts/`. Modules describe *what*, *when*, and *which leg/scripts to load* — not *how*.
   JS inside a module body must be ≤5 lines; past that it lives in a script.
3. **CHANGELOG-on-change (source repo only).** Edits to this skill happen in the source
   repo during a batch rebuild; every structural change gets one line in
   `references/CHANGELOG.md` there. At runtime nothing is written into the install —
   findings go to the complaint log instead.

**PROHIBITED — hard delete.** This skill does NOT hard-delete anything in CCH and will not
learn to (a single KC-form delete can corrupt a binder). "Remove" =
`wpm.soft_delete_*` → the object lands in a `User to delete` folder (index `9999`) for the
user to clear from the UI. If a capture surfaces a DELETE call, do NOT script it (see
`scripts/wpm.py` header). Sole legacy exception: `scripts.funds` fund-setup DELETEs —
scoped, do not extend.

**CONSENT-GATED — in-place workpaper replace.** `replace-workpaper.md` (`wpm_replace`) overwrites
a workpaper's content via "Upload new version" — destructive-in-spirit (prior content survives
only in CCH version history). It fires NO DELETE (not the hard-delete hazard) but is UNRECOVERABLE, so
it sits behind a **mandatory consent gate every run**: state it can't be undone, show the exact
TARGET (index+name+folder) + REPLACEMENT (file) plan, get an explicit yes. A user "just do it"
does NOT waive the plan+yes. Default to the soft-delete→evict→claim path (`file-io.md`) unless the
user explicitly wants a true in-place version.

## Operating doctrine — pointers (read the cited file before acting)

- **Bounded platform execution — hard rules.** ≤10 operations per injected eval (never one
  giant "walk" payload); every eval wrapped in a JS-side timeout (`Promise.race`, 30–60s) so it
  ALWAYS returns; verify each chunk by read; a one-line progress note between chunks; batch ops
  over call loops; validate responses by BODY shape, never HTTP status (CCH 200s with error/HTML
  bodies). An eval that can hang forever wedges the agent — only a kill recovers it.
  `transport.md` → "Bounded execution".
- **JS/DOM-first for KC forms.** The DOM (`kc_dom_parser`, `window.kcDom`) is the fillable-field
  DETECTOR; the GET is the write SUBSTRATE + the empty-add-grid (`objectList:[]`) check; writes go
  through the builders, then **submit** to commit; verify via reload + re-GET (committed state) —
  the immediate post-write GET reads the uncommitted working copy. `fill-kc-form.md` +
  `architecture.md` → "In-page GET shows the working copy" and the "DOM is a viewport" scope note.
- **Throttle / auth for autonomous runs.** Tab **visibilityState** (selected tab in a non-minimized
  window), NOT window focus, governs throttling + token refresh. Park the KC tab as the lone tab in
  its own window; never hidden-reload a near-expiry tab. `architecture.md` → "Tab visibility,
  throttling & token refresh".
- **Truncation guard — fused completeness check + named recovery (always-on).**
  A short read here is a known **transport artifact** (bash/virtiofs cache lag on a host-edited text
  file; an over-the-bridge text return that came back clipped) — the true disk file is complete. It
  is NEVER a corrupt file, so do **not** enter a debug loop. Two parts:
  - **DETECT (fused, ~free).** After any **bash read of the mount** or any **over-the-bridge text
    pull**, confirm completeness *in the same step* — the file ends with its `<!-- END -->` marker
    (or matches its expected size/`objectList`/closing token). Fuse it into the read you already do
    (`tail`/`wc -c` in the consuming command; a glance at returned JSON) — measured cost is ~0 extra
    tool calls / ~1% tokens. **Skip this for host `Read/Write/Edit` (true disk) and binary pulls
    (zips serve intact)** — they can't short-read.
  - **RECOVER (go straight to the right action — detection alone is not enough).** On a short read,
    route by what it is, don't loop:
    - host-edited **text file** clipped in a bash read → re-read via the host **Read** tool (true
      disk), or bust the stale cache with a **rename round-trip** (`mv f f.cb && mv f.cb f`), then re-read;
    - a **script you need to RUN** → extract it from the versioned `.bin` into `/tmp` (binaries cross
      intact) and run from there — never `bash cp` the `.py` from the mount;
    - a **bridge text-return** that came back short → re-pull, or download-to-disk and read the file.
  - Verify the recovered copy ends with `<!-- END -->`, then proceed. (Full procedure: `local-exec.md`.)

## What's scripted (don't reinvent — full function lists in `references/modules/INDEX.md`)

| Script | Covers |
|---|---|
| `scripts.session` | cold-start discovery: `discover_session_js` (filter-safe session state) |
| `scripts.auth_capture` | token/header capture: KC localStorage + engagement monkeypatch |
| `scripts.kc` | KC forms: read, decode, typed `inventory_form`, `build_write_payload`, `build_spawn_payload`, write/submit, program steps |
| `scripts.wpm` | folders/workpapers: get, move, set_index, rename, soft-delete (`soft_delete_*`) |
| `scripts.reports` | TB + JE reports: create, list, settings, quotas, leadsheet columns |
| `scripts.funds` | Fund TB setup: list/upsert/delete types-funds-subtypes, account map |
| `scripts.groups` | TB groupings: lists, groups, account assignment, classification |
| `scripts.tb_backup` | TB backup package: multi-period TB + groups + funds pulls → workbook |
| `scripts.xref` | cross-references: extract, resolve against engagement form index |
| `scripts.binder_map` | binder inventory: `build_map_js`, `fetch_chunk_js` |
| `scripts.binder_planner` | program/leadsheet planning: `plan`, `diff_against_unfiled` |
| `scripts.catalog` | KC forms catalog: lookup by reference tag, build add-forms body |
| `scripts.je` | post a real AJE/RJE/PAJE/TJE into the TB (FinancialPrep): `build_post_je_js` (CREATE-only, balance-checked, URL-guarded) |
| `scripts.wpm_replace` | in-place "Upload new version" overwrite: `build_replace_version_js` (consent-gated — see `replace-workpaper.md`) |
| `scripts.kc_dom_parser` | (JS, `window.kcDom`) leg:kc DOM field detector for KC forms — paste into the KC tab |
| `scripts.http_runner` | XHR/fetch builders + batch + result parsing; `ls:*` (KC localStorage) and `cap:*` (engagement `__cch_capture`) auth sentinels. `build_batch_xhr` sends `Content-Type: application/json` on body-bearing writes (its omission 415'd every KC write). |
| `scripts.verify_integrity` | truncation guard (END-marker check; run once per build at extract) |

**Field/valueKey conventions live in `references/config/field-conventions.md` (the registry) —
`classify_property` / `build_write_payload` consume it** (look up the valueKey convention by prop
key when `floatieItemList` is empty, instead of guessing). KC writes are PENDING until `submit`
(required for persistence — a refresh discards unsubmitted writes); verify state AFTER reload, not
the immediate GET.

If a capability isn't listed in INDEX.md's function inventory, it's not implemented — that's
a consent-wall stop, not a license to improvise. Don't call a function you haven't confirmed
exists.

## What lives where

| Need | File |
|---|---|
| Pick the browser transport (chrome-bridge vs linked tab) | `references/runbooks/transport.md` |
| Warm a cold leg (browser/tab pick, capture, KC deep-link) | `references/runbooks/session-bootstrap.md` |
| Exec cache: per-build verified copy | `references/runbooks/local-exec.md` |
| Module dispatch + full function inventory | `references/modules/INDEX.md` |
| One procedure | `references/modules/{name}.md` |
| Platform facts (subdomains, IDs, auth, transport matrix, route-by-origin, gotchas) | `references/architecture.md` |
| Endpoint spec (URL/method/headers/body/response) | `references/endpoints/{operation}.json` |
| Enums, denylists, header lists | `references/config/*.json` |
| Executable operations | `scripts/*.py` |
| Reference data (templates, catalogs, group codes, xrefs) | `references/data/*.xlsx` + `INDEX.md` |
| Capture mode (behind the consent wall ONLY) | `references/learn-protocol.md` |

> **Editing this file (source repo only):** never reconstruct it from a `bash cat` view (the
> mount serves a stale/truncated snapshot). Edit via the host Edit tool on true on-disk
> content, and run `python3 scripts/verify_integrity.py` after — this file must end with its
> `<!-- END -->` marker or it shipped truncated.

<!-- END -->
