---
summary: Fill out a KC form / fast-fill / scan for cross-references
leg: kc
triggers:
  - "fill out [form]"
  - "answer the questions on [form]"
  - "fast-fill"
  - "scan [form] for cross-references"
  - "complete AUD-100 / KBA-302 for [client]"
inputs:
  - "Form ID"
  - "engagement"
  - "answer plan"
calls:
  - scripts/kc_dom_parser.js (paste into KC tab — defines window.kcDom; DOM field detector)
  - scripts.kc.read_form
  - scripts.kc.decode_form
  - scripts.kc.inventory_form
  - scripts.kc.classify_property
  - scripts.kc.build_write_payload
  - scripts.kc.legal_dropdown_values
  - scripts.kc.is_answered
  - scripts.kc.was_rejected
  - scripts.kc.update_properties_sequential
  - scripts.kc.submit   # per-workpaper scoped (eng_guid, wp_id, headers)
  - scripts.kc.build_spawn_payload
  - scripts.kc.addable_empty_grids
  - scripts.kc.enrich_repeating_choice
  - scripts.kc.resolve_choice_options_from_templates
  - scripts.kc.rendered_binding_keys
  - scripts.kc.is_heading_object
  - scripts.kc.find_dropdown_options
  - scripts.kc.existing_repeating_rows
  - scripts.xref.extract_form_refs
  - scripts.xref.load_engagement_form_index
  - scripts.xref.resolve
status: validated
---
# Module — Fill KC Forms

> **wpId lookup — GetBinder FIRST.** See `architecture.md` → "WPM surface — confirmed facts".

**Triggers:** "fill out [form ID]", "answer the questions on [form]", "fast-fill the planning forms", "inject answers into [form]", "scan [form] for cross-references", "walk the planning forms", "complete AUD-100 / KBA-302 for [client]".

**Capabilities:** read a form, get a typed inventory of every field, resolve cross-references against the engagement's form index, write answers (sequential), submit.

## Field detection: DOM-first, API side-check

Doctrine facts canonical in `architecture.md` (do not re-derive):
- The DOM is the fillable-field detector for a rendered form (the GET over-reports fillable ~2:1); the API GET is the write substrate.
- An in-page GET reads the **uncommitted working copy** (false state-3) — never proof of persistence.

Applied to filling:
1. Enumerate fillable controls via `scripts/kc_dom_parser.js` (`window.kcDom`).
2. Side-check empty `objectList:[]` add-grids via `inventory_form()['addable_grids']` (a passive DOM parse can't see them).
3. Write via the builders.
4. **Submit → reload → verify via the diagnostics endpoint.**
5. The DOM does NOT re-render out-of-band API writes without a reload — use it for the initial enumeration and the post-reload check only.

## Read in JS, analyze in Python

1. One read → analyze in Python → one batch of writes back through JS.
2. Token-bearing calls run in the browser; JSON parsing, classification, content composition, and verification live in Python so the analysis is scripted and re-runnable.

```python
from scripts import kc
js = kc.read_form(eng_guid, wp_id, headers)   # bridge: chrome_api_call (KC origin); linked-tab fallback: javascript_tool
form = kc.decode_form(result)                  # parse the JSON-encoded elements/collections
inv  = kc.inventory_form(form)                 # typed, classified inventory  <-- use this
payloads = [...]                               # built from inv['writable'] via build_write_payload
js = kc.update_properties_sequential(eng_guid, wp_id, payloads, headers)
```

**Data channel — bridge vs linked-tab.**
- Bridge (`chrome_api_call`): KC reads come back as **real JSON, NOT DLP-filtered** — `kc.read_form`'s payload returns inline (or auto-saves to the tool-results tree if very large; read it from disk there).
- Linked-tab fallback: the channel IS DLP-filtered (`[BLOCKED...]` on the probe) — read by download-to-disk: bundle the response into a Blob and trigger a native browser download (pattern: `bulk-capture-forms.md` Step 2), then **immediately call `request_cowork_directory` on the browser's Downloads folder** (resolve the user from the session env, e.g. `C:\Users\<user>\Downloads`) and Read the file.
- Do not ask the user to save-and-report — mounting Downloads is the skill's job.

`inventory_form()` replaces the old `walk_fields()` planning flow. `walk_fields()` still exists (untyped) — do not hand-roll payloads from it; `inventory_form()` classifies every field and `build_write_payload()` emits the correct shape per kind.

## Field-kind taxonomy

- **The authoritative field/valueKey registry is `references/config/field-conventions.md`.** There is no `field-conventions.json`; the same conventions are hard-coded in `scripts/kc.py` (`classify_property` + `build_write_payload`) — a convention change must land in BOTH the registry and kc.py.
- It is the ONE canonical map of every field-kind, valueKey convention, option-set/enum, per-prop convention, and collection-targeting rule.
- **valueKey conventions are DATA, not discoverable from the form GET** — `floatieItemList` is EMPTY on convention-driven props, so the code/registry must carry them. Look up the convention by prop key in the registry; do NOT guess a valueKey from the floatie.

Every field's kind comes from `propertyType` (int), refined by `floatieType` + the option-list length. `classify_property()` owns this; `inventory_form()` applies it.

| kind | from | writable | write via |
|---|---|---|---|
| `text` | pt=1, or pt=0 with no option list / no choice sentinel | yes | free text, `valueKey=""` |
| `select` | pt=0 + floatieType `Radio`, non-empty list, or sentinel `"Choose an item"`/`defaultanswer` | yes | one `valueKey` from `options` — **skip if `options` empty** |
| `multiselect` | pt=0 + floatieType `CheckBox`, or sentinel `"Choose all that apply."` | yes | semicolon-joined `valueKey`s, one POST — **skip if `options` empty** |
| `signoff` | pt=3 (performedby / dates on program steps) | yes | token (initials) in **`valueKey`**, NOT `value` |
| `label` | pt=2 (Question text, Name, HTML) | **no** — display only | — |
| `linked` | pt=5 (system keys, IDs, cross-form linked values) | **no** | — |

`build_write_payload()` handles all of this: sign-off tokens go to `valueKey`; a choice field with an empty `options` list raises (skip it — don't free-text it). Skip any writable field whose row is an **addable template** (see failure modes).

Two facts that make this reliable:

- **Options live at `prop['floatieItemList']['list']`** — `floatieItemList` is always an object `{isCustomizable, list}`, never a bare array. Each item is `{key, value, isCustom}`; the item's **`key` is the `valueKey`** to send. `legal_dropdown_values()` / `inventory_form()` already extract this. An empty list = free text, not a dropdown — `floatieItemList` is present on every field, so its mere presence means nothing.
- **A form OBJECT (row) bundles the kinds:** a tailoring row is `Question`(label) + `Answer`(answer) + `Comment`(text) + system fields. `inventory_form()` groups fields under their object and surfaces the object's `visible` flag (the gating signal — see below).

## Procedure

### 1. Read + inventory
```python
from scripts import kc
js   = kc.read_form(eng_guid, wp_id, headers)   # bridge: chrome_api_call (KC origin); linked-tab fallback: javascript_tool
form = kc.decode_form(result)
inv  = kc.inventory_form(form)
# inv['fillable'] = a real, answerable UI control  <-- FILL FROM THIS
# inv['writable'] = flat list of writable field records (superset; diagnostic/escape hatch)
# inv['hidden_writable'] = dropped: rendered column but object.visible==False (hidden driver rows)
# inv['heading_answers']  = dropped: stray answer box on a bold section-heading row
# inv['sections'][i]['rows'][j] = {object_key, type, visible, label, fields[], children[]}
# inv['stats'] = {by_kind, writable, fillable, hidden_writable, heading_answers, answered, fields}
```
A field is answered iff `kc.is_answered(prop)` (state==3 AND not default). On a fresh form everything is state 0.

**Fill from `inv['fillable']`, not `inv['writable']`.** `kc._is_fillable` applies
THREE gates — each catches a distinct phantom class:

1. **rendered (column).** `collections` carries every property the form *could*
   hold, including latent ones the layout never shows. Each AUD-100 tailoring row
   has a `Comment` property, but the table renders only QUESTION + ANSWER columns.

> **TQComments gotcha:** the engagement-level TQ *comment*
> writes through propertyKey **`"Description"`**, NOT `"Answer"`.
   Writing `Comment` returns 200/state→3 yet has **no UI box** — stored-but-invisible
   data. `kc.rendered_binding_keys(form)` is the lowercased bindingKey set from
   `elements`; a property is rendered only if its key is in it. NOTE: `elements`
   describes only COLUMNS / table-templates, never individual rows — so this gate is
   column-granular and CANNOT see a hidden row (gate 2 does). Empty set (layout
   unparsable) ⇒ nothing filtered, fall back to `writable`.

2. **row_visible (`object.visible != False`).** Drops hidden DRIVER rows. AUD-100
   `OperatingEffectiveness` ("intend to test controls over financial reporting?")
   ships `object.visible=False`, renders NOWHERE in the UI, yet accepts API writes
   AND silently gates the controls-areas multiselect (`OperatingAuditAreas`) into
   view. Gate 1 misses it (its Answer maps to the rendered ANSWER column). `visible`
   is STATEFUL — gated rows flip to True as you answer their driver, so the
   fixed-point loop naturally re-includes them on the next read. CONSEQUENCE: the
   filler will NOT set hidden drivers, so a pure auto-fill won't surface the
   controls multiselect — that's correct (a human can't reach it via the UI either;
   don't force off-path states).

3. **not heading_row.** `kc.is_heading_object` flags a row whose Question/label is
   styled `PfxTableTextBold` (bold section heading). AUD-100 "Entity/Engagement
   Complexity / General Tailoring Considerations" are headings that still carry a
   stray writable answer box — skip it. CAUTION: keys off a CSS class, not a
   semantic flag → possible false positives on other forms. Dropped boxes are
   surfaced in `inv['heading_answers']` (and stay in `writable`) for review.

**Known limitation + the working path for grid forms.** `inventory_form` over-filters grid forms:
grid columns that bind by `columnID` with an empty `bindingKey` are dropped (KBA-502 drops 66/68 this
way; on KBA-4xx/5xx it also hides real INPUT collections like `.KBA400.Scoping` and KBA-401's
`*Findings`/`*TQ`). **For KBA-4xx/5xx grid forms, read the raw `result.collections`** (the
inventory under-reports them) and target the INPUT collection directly, writing valueKeys per the
registry conventions in `references/config/field-conventions.md` (section 4, INPUT vs DISPLAY). Do
NOT trust `inventory_form`'s `fillable` count alone on grid-heavy / risk forms (KBA-502/503,
KBA-400 scoping). **KBA-502 special case:** even the raw bulk GET does NOT embed its
RelevantAssertion child rows (`OverallAuditAreas[].childObjectList` returns `[]`, even after refresh
— they're cross-form bindings the SPA renders per area). The grid is real: read KBA-502's `elements`
OverallAuditAreas columns and write blind by AREA collectionKey (`.{AREA}.RelevantAssertion`)
against KBA-502's wpId, then verify via the diagnostics oracle.

**Addable empty grids (identify + warn):** some tables are add-row grids whose
collection ships EMPTY (`objectList: []`) — the UI shows a "type to add" cell but
there's no row object, so `fillable` is 0 and the form can look "done" when it
isn't (KBA-103 deficiency/noncompliance grids; watch KBA-400 scoping). Check
`inventory_form()['addable_grids']` (and `stats['addable_grids']`): a non-empty
list means "this form has add-row grids you have NOT filled." **Warn the user;
do not silently report complete** — but you CAN now fill them on request.
**Filling:** spawn IS REST. CREATE a row with
`kc.build_spawn_payload(collection_path, value)` — UpdateProperty with empty
identity keys + the collection path in `dataEntryExpression`. SignalR is a
recalc backchannel only, not the write path. Then re-read the form to get the new GUID and fill
remaining columns with `build_write_payload` keyed by it. One spawn == one row; loop
by a known target count (the trailing UI add-box has no collection object and never
disappears, so "until no add-row remains" never terminates). **Seeded-template
detection caveat:** `addable_grids` misses grids that ship a seeded template row
(obj key ending `-1`/`_1`) — that seeded row IS writable in place; ADDITIONAL rows
spawn as above. So a grid can look "done" because the seeded row exists, or look
"empty" when only the seed is present — check for the `…-1`/`…_1` seeded row, not
just `objectList:[]`. Full walkthrough + double-occurrence caveat:
`references/deferred/empty-grid-row-spawn.md`.

### 2. Scan cross-references
```python
from scripts import xref
refs = xref.extract_form_refs(form, exclude=current_form_id)   # denylist-filtered
form_index = xref.load_engagement_form_index(engagement_slug)
resolved, unresolved = xref.resolve(refs, form_index)
```
Unresolved → ask the user once (add / skip / not-used), persist the decision in an engagement xref workbook **in the user's working folder** (`{slug}-xrefs.xlsx`, a "Decisions Log" sheet) — never into this read-only install.

### 3. Fill choices to a fixed point, THEN text/sign-offs — order is critical

- Gating is recursive: a select can reveal another select, and a multiselect's options can stay **empty until a gating answer populates them** (e.g. AUD-100 `OperatingAuditAreas` — controls-testing areas — populates only after audit areas/operating-effectiveness are set).
- A single "TQs first, then the rest" pass MISSES these — the second wave of revealed choices never gets written. **Loop to a fixed point**: 

```
repeat (cap ~8 iterations):
    read_form -> inventory_form
    targets = visible writable choices (select|multiselect) that are NOT answered
              and HAVE options   (skip empty-option choices; build_write_payload raises on them)
    if no targets: break
    write each target (build_write_payload), sequentially
then:
    read_form once more
    write all visible writable text + signoff fields
    submit
```

`answered` for this loop must treat a `reset*` valueKey as NOT answered (so a previously reset checkbox gets retried once its options exist). Use `kc.is_answered` plus `not kc.was_rejected(...)`.

Build each payload from the inventory record:
```python
p_text   = kc.build_write_payload(text_field, "GIBBERISH ANSWER")              # valueKey=""
p_select = kc.build_write_payload(select_field, "Yes")                          # resolves valueKey from options
p_multi  = kc.build_write_payload(ms_field, ["Cash", "Accounts Receivable and Revenue"])  # or valueKey=["CASH","AR"]
p_signoff= kc.build_write_payload(signoff_field, "ABC")                         # token -> valueKey
```
`build_write_payload` raises if the field isn't writable, a choice value can't be resolved, or a sentinel-detected choice has no options yet — trust it over a hand-built dict, and let the loop pick the field up on a later iteration once its options populate.

### 4. Write sequentially + submit
```python
js = kc.update_properties_sequential(eng_guid, wp_id, payloads, headers)  # concurrency=1, enforced
js = kc.submit(eng_guid, wp_id, headers)   # per-workpaper — NEVER empty wpId (discards other forms' pending writes)
```
**Why sequential?** Parallel POSTs to the same form drop writes (server race).

**Expect silent drops even when everything is right — CONVERGE, don't count retries.**
- KC drops a **rotating subset** of rapid sequential UpdateProperty writes: every write echoes state 3, but the commit loses some of them — ~30–50% of write→submit pairs with convention-correct payloads.
- Inter-write sleeps (1–2s) reduce but do NOT eliminate the loss.
- The per-write echo is NEVER proof; only the committed read is.
- Standard fill procedure for every write set is the **converge loop**:

```
repeat (2–4 rounds converges in practice):
    write the outstanding payloads (settle ~1.2s each) -> per-workpaper submit
    re-read the COMMITTED state (after refresh/reload)
    outstanding = cells whose committed value does not match intent
    if outstanding is empty: break
```

One committed re-read covers the whole set — verify in batch, rewrite ONLY the dropped cells
(never blind-repeat the full set), and loop until the committed read matches intent. A write not
verified state-3-after-reload was NOT made. Because the drop set ROTATES between rounds, a fixed
"retry the misses ≤3×" pass under-delivers on large write sets — converge to match-intent instead.
(field-conventions.md §5 3a.)

**Always set `Content-Type: application/json` on every body-bearing KC write.** Without it (`build_batch_xhr` omits it; the single-call builders inject it), the server returns **415 Unsupported Media Type** and the write never lands — this is a missing-header failure, not a body-drop; do not chase it with a body-drop retry loop.

**Why submit?** Submit **COMMITS** the pending working copy. Writes sit in a pending working copy and
are **DISCARDED on reload** if you never submit. The immediate re-GET shows `state==3` because it
reads the uncommitted working copy (a false state-3) — that is NOT proof of persistence. The correct
verify sequence is **write → `kc.submit` → reload → re-GET** (and confirm via the diagnostics endpoint,
Step 5).

**Route multiselects (and ALL writes) through the builder.** CheckBox **multiselects** (e.g. AUD-100
audit-area scoping) MUST go through `build_write_payload` (semicolon-joined valueKeys, full-state
replacement) — a naive write returns 200 then resets to `state 2 / resetcheckbox`. Do NOT assume
single selects and free text "write fine via naive UpdateProperty" — naive writes 415'd for lack of
the Content-Type header. Build every payload via `build_write_payload` and send it with the
Content-Type header set.

### 5. Verify — AFTER submit + reload, via the diagnostics endpoint
The immediate in-page GET reads the uncommitted working copy (false state-3), so verify only AFTER
`kc.submit` + a reload. The authoritative completion oracle is the diagnostics endpoint:

```
POST /api/Workpaper/refresh/{eng}/{wp}            # then
GET  /api/diagnostics/GetWorkpaperDiagnostics/{eng}/{wp}   # → result.diagnostics[]
```

Drive the completion loop off `result.diagnostics[]` (loop until empty / your target set clears).
After submit+reload you can also re-call `read_form` → `inventory_form` to confirm each written field
is `answered` (state==3, not default) or that free-text `value` matches — but the diagnostics endpoint
is the oracle.

**The form's `diagnosticCount` is STALE — do not trust it.** It does not reflect the committed state;
use the diagnostics ENDPOINT (refresh → GetWorkpaperDiagnostics → `result.diagnostics[]`) for both
KBA-4xx and AUD-8xx forms. A `type:"Missing KnowledgeCoach Form"` diagnostic means a Yes-answer needs
a dependent form — flip it to No or add the form.

**Diagnostics are a completion CHECK, not the fill spec — zero diagnostics ≠ complete.** KC emits
"Question Unanswered" for only a SUBSET of the fields a form expects; drive the fill off the rendered
form's `elements`/labels, then use diagnostics as the backstop. Field classes that produce NO
diagnostic yet are required in substance — walk every form for them before calling it done:

1. **"Procedures performed to obtain the above understanding (include workpaper reference):"** —
   on every understanding-memo form (KBA-302/401 and their S-form counterparts). Silent; always
   required.
2. **"Did any factors or understanding above significantly change from the prior year? If 'yes',
   describe the change here:"** — same forms; describe-only boxes with no yes/no toggle. Silent;
   answer even when the answer is "no significant change."
3. **Memo-format TQ reveals** — a "…document his or her understanding in a memorandum format?" TQ
   answered Yes REVEALS per-area/per-principle description fields that then become required
   (e.g. 8 area memos on KBA-302S; 17 principle memos on KBA-401S). Sequence: answer the TQs →
   submit → **RE-READ the form** → fill the revealed set → submit → verify. Stopping at the first
   diagnostics-clean read leaves every revealed field blank.
4. **Add-row grids / per-program add buttons** (e.g. KBA-503S per-major-program
   compliance-requirement tables) — no diagnostic exists until the row/table is spawned; the
   required content is invisible to the oracle. Spawn from the form's add-controls, then fill.

**valueKey resolution — from the form's OWN template, never a registry/other-form default.**
Option valueKeys vary by form family (S-forms use lowercase `yes`/`no` and
`yesnona-yes`/`-no`/`-na`; FS-side forms differ). `build_write_payload` refuses an empty-option
choice — pass `decoded_form=` so it resolves from the form's rowTemplates
(`resolve_choice_options_from_templates`), or enrich first. One reset-reject (state 2 /
`resetanswer`) means the key was guessed — resolve from the template; never guess twice. A choice
still empty after template resolution is a **dynamic cross-form multiselect** (options rendered by
the SPA from another container, e.g. a major-program list): resolve via the DOM (`kc_dom_parser`)
or leave it for a UI fill — it cannot be written blind through the API.

**Detect silent rejection.** `UpdateProperty` returns HTTP 200 even when CCH rejects the value/valueKey. The signature is `state` regressing to 2 with `valueKey=='resetanswer'` — use `kc.was_rejected(before, after)`. Selects rarely reject when the `valueKey` is taken straight from the field's own `options` (the floatie `key`); they reject when you guess a code or wrong case.

## Multi-value / multiselect

- **CheckBox multiselect** (e.g., AUD-100 audit-area scoping): one POST, `value` and `valueKey` semicolon-joined, **full-state replacement** (send the complete desired set each time). The server normalizes a trailing semicolon off. `build_write_payload(field, [...])` does the join.
- **Risks** on `.{AREA}.ProgramSteps`: full-state replacement, semicolon-joined valueKeys **with** trailing semi. See `references/config/enums.json`. Sending an unknown code returns 500 "Index was outside the bounds of the array" — verify codes first.
- **PlannedAuditApproach** on `.{AREA}.RelevantAssertion`: one canonical valueKey per checkbox (COMBINED / ANALYTICAL / INDEPTH), one POST each.
- **Custom ("add custom value") multiselect entries** (e.g. KBA-400 `CtrlConTestWp`/C09, which has an add-custom box): the custom value's valueKey is NOT free-form — the server derives it as `"KEY_" + value` upper-cased with non-alphanumerics → `_` (typing "Control Memo" POSTs `KEY_CONTROL_MEMO`). Pass `build_write_payload(field, None, valueKey=[<option keys>], custom="Control Memo")` — `custom_value_key()` derives the key and appends it. **FALSE-POSITIVE TRAP:** an invented token (e.g. `ZZ_CUSTOM_9931`) is accepted into the working copy so the GET right after the write looks fine, but it is DROPPED on the next refresh/reload and never persists. Confirm a custom value truly stuck by re-reading AFTER `POST /api/Workpaper/refresh`, not by the immediate GET.

## Known failure modes

- **Sign-off written as free text** → ignored, state stays 0. Sign-off (pt=3) stores its token in **`valueKey`**, not `value`. `build_write_payload` handles it. Note: the display `value` field is echoed back verbatim (kc.py line 688 passes the same token to both) but only `valueKey` matters for state — a raw free-text write that only populates `value` stays at state 0 with no error.

- **Choice field written as free text** → 200 back, but CCH rejects it by resetting to `valueKey='resetanswer'` (select) or `valueKey='resetcheckbox'` (multiselect). `was_rejected(before, after)` detects this by prefix. Root cause: free-texting a sentinel-detected choice whose option list was empty at read time. Fix: the fixed-point loop will skip empty-option fields (build_write_payload raises on them) and re-visit once options populate.

- **`build_reset_payload` is FORBIDDEN.** Resetting a required toggle via the API leaves `state==3` with a blank value; KC's diagnostic engine never re-fires, so the form reads COMPLETE while empty. Do not reintroduce. To genuinely clear a section, remove + re-add the form so KC rebuilds from scratch.

- **Addable grid (objectList empty) looks done but isn't** — `inventory_form()['addable_grids']` surfaces these. The UI shows a "type to add" cell, `fillable` is 0, and the form can falsely appear complete. Warn the user; do not silently report complete. **Filling IS supported** via `build_spawn_payload` (creates a row over REST) → re-read → `build_write_payload` on the new GUID. Loop by a known target count; the trailing UI add-box never disappears so "until no add-row remains" never terminates. Full walkthrough: `references/deferred/empty-grid-row-spawn.md`.

- **Repeating-row choice field has empty options** → `enrich_repeating_choice(field, decoded_form)` pulls options from `rowTemplates` before passing to `build_write_payload`. Without it, `build_write_payload` raises on the empty list.

- **Custom multiselect value (add-custom) uses a server-derived key** — NOT the free-text string. The server derives it as `"KEY_" + value.upper().replace(non-alnum, "_")`. Pass `build_write_payload(field, None, valueKey=[<option_keys>], custom="My Value")` and let `custom_value_key()` do the derivation. An invented key is accepted into the working copy, survives the immediate GET, but is DROPPED on the next refresh/reload — confirm persistence only after `POST /api/Workpaper/refresh`, not by the immediate re-read.

- **Per-area risk sub-grids — WRITABLE via UpdateProperty.** Write to the
  **`*Findings` / `*TQ` flow collections** with UPPERCASE / YESNONA valueKeys (`YES`/`NO`,
  `YESNONA-YES/-NO/-NA`) — NOT the `EntityEnv*` DISPLAY collections (those reject with `resetanswer`).
  These render from `elements` as Generic nodes bound `<parent>[current].<child>` (e.g.
  `OverallAuditAreas[current].RelevantAssertion`), but the input target is the flow collection, not the
  display rollup. **KBA-502 OWNS the IR/CR/RMM/PlannedAuditApproach grid and is its WRITE target.** Write
  `collectionKey ".{AREA}.RelevantAssertion"` against **KBA-502's wpId**; the AUD-8xx program's grid is
  the DERIVED view — writes aimed at the program's wpId land in a working copy the KBA-502-owned
  recompute discards on refresh (reverts / appears unwritable). See
  `references/config/field-conventions.md` §3 (per-prop conventions) and §4 (INPUT vs DISPLAY).

<!-- END -->
