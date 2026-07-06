# Training Mode — Script-First Capture Protocol

> **Entry point:** read `learn-protocol.md` first — it's the short, mechanical checklist for adding a new operation, and it owns the CONSENT WALL. This file is the long-form manual (capture mechanics, monkey-patch internals, the fallback ladder, the known-unknowns backlog) you consult when the checklist alone isn't enough.


This document is for Claude sessions extending the cch-axcess skill — ONLY after the consent wall in SKILL.md routing was answered yes, or the user explicitly said "listen for this" / "we're doing something new" / similar. An unmatched ask alone does NOT open this file: the wall fires first, and the user's no (or silence) ends it. Capture artifacts are rebuild inputs written to the session working folder + complaint log — never into this install (see learn-protocol.md).

**Terminal state of training mode is NOT "a new markdown module." It is:**

1. A tested function in `scripts/*.py` that performs the operation, and
2. A JSON spec in `references/endpoints/*.json` describing the endpoint, and
3. A thin module in `references/modules/*.md` that calls the script.

Markdown that describes "how to do the operation by hand" is a failure state. Codify it as code or don't codify it at all.

## The fallback ladder (strict order)

When the user asks for an operation, Claude works DOWN this ladder. Skip a rung only if it's impossible — never because it's easier.

### Rung 1 — API direct (no capture needed)

If `references/architecture.md` lists the endpoint and a `scripts/*.py` function exists, use it. Done.

### Rung 2 — API capture, then script

Endpoint exists but isn't in the skill yet. Capture once, script it, then use it.

1. Install monkey-patch (`scripts.auth_capture.INSTALL_MONKEYPATCH_JS`) on the relevant tab.
2. Have the user trigger ONE real UI action — the literal action they want Claude to learn. Don't speculate.
3. Read `window.__cch_capture` (`scripts.auth_capture.capture_query_js(host_substring)`).
4. **Replay programmatically to confirm.** Use `scripts.http_runner.build_xhr_call()` or `build_fetch_call()` with the captured headers. Confirm the response matches what the UI did. If it doesn't, capture is incomplete — go back to step 2.
5. **Verify the side effect** with a follow-up GET. Production modules end with verification too.
6. **Codify as code first.** Add a function to the appropriate `scripts/*.py`. Add a JSON spec to `references/endpoints/{operation}.json`. Then write the thin module. Never write the module without the script.

### Rung 3 — UI clicking (LAST RESORT, always with capture)

If the operation genuinely cannot be done via API — file upload widgets, multi-step wizards with hidden state — drive the UI through Claude in Chrome tools. **BUT:** install the monkey-patch first, and capture every network call the UI fires during the operation. Treat the captures as a draft of the API for the next iteration:

- After the task succeeds, audit the captures.
- If any captured XHR is the operation's "real" mutation call (not just analytics or state-sync), promote it to Rung 2: write the script function, write the endpoint spec, retire the UI path from the module.
- If the operation is genuinely click-only (truly, no XHR backs it), document the click sequence in the module — but tag it `ui-only: true` in the module front-matter so future Claude sessions know to try Rung 2 first if CCH ships an API.

## Already known — do NOT rediscover

Everything in `references/architecture.md` is settled. Read it once before doing anything novel. Do not re-derive subdomain auth patterns, ID glossary mappings, the misnamed `engagementId` field, PUT-vs-POST for set-index, IdToken vs IDToken case, Move-PRESERVES-the-index (set-index only for genuinely new null-index forms — AX-14/25), the recommendedAnswer trap, or the renderProperty key case-inconsistency. Those are facts. Move on.

If you find them outdated, update `architecture.md` AND the relevant `endpoints/*.json` in one pass. Do not leave the two files disagreeing.

## Where new facts go

| Discovery | Destination |
|---|---|
| New endpoint URL/method/body/response shape | `references/endpoints/{operation}.json` (NEW file or update existing) |
| Platform-level gotcha (auth, ID, ordering) | `references/architecture.md` |
| Workflow sequence (which calls in what order with what conditional logic) | `references/modules/{verb-noun}.md` |
| Enum, denylist, header list | `references/config/*.json` |
| Firm-wide reusable lookup (binder templates, form catalogs, group codes) | `references/data/*.xlsx` + `data/INDEX.md` |
| Engagement-specific state (form indexes, xrefs, decisions log) | user's working folder (`{slug}-xrefs.xlsx`) — never the read-only install |
| Executable operation (API call, parser, planner) | `scripts/*.py` |
| Big captured payload (form bundles, page snapshots) | Disk — never context. Module returns a path. |

## Module template (use exactly this shape)

```markdown
# Module — <Verb Noun>

**Triggers:** "phrase 1", "phrase 2", "phrase 3"

## What this does

<one paragraph, max>

## Prerequisites

- <list>

## Procedure

### 1. <First step>
```python
from scripts import <module>
js = <module>.<function>(...)   # description of what call returns
```

### 2. <Second step>
...

### N. Verify
<re-call something, confirm side effect>

## Known failure modes

- <symptom> → <cause> → <fix>

## Validated on

- <client / engagement / date>
```

**Hard rule:** no JavaScript snippet longer than 5 lines inside a module body. If the JS is non-trivial, it lives in a script. The module shows the Python call that produces the JS.

## Listen-mode log structure (working context only)

While capturing, keep this structure in working memory. **Transcribe into the script + endpoint spec + module afterward — never leave it as the only artifact.**

```
GOAL: <one-line user objective>
ENGAGEMENT: <client> / clientId <X> / engagementGuid <Y> / industry title <Z>

STEPS (only confirmed-successful):
  1. <action>
     - URL: <method> <full URL with placeholders>
     - Required headers (names only, no token values)
     - Body shape (with field names + sample values)
     - Response (status, key fields)
     - Verification (follow-up GET)

FAILURES ALONG THE WAY:
  - <what didn't work and why>  → goes to "Known failure modes" in the module.

GOTCHAS:
  - <surprises, race conditions, ordering, case-sensitivity>  → goes to architecture.md or endpoint spec.

REFERENCE DATA NEEDED:
  - <files to add to references/data/>
```

## When you're done with training mode

Hard checklist — every box must be checked before exiting:

- [ ] `scripts/*.py` function written and replayed successfully.
- [ ] `references/endpoints/{operation}.json` created or updated.
- [ ] `references/architecture.md` updated if new platform-level facts.
- [ ] `references/config/*.json` updated if new enums/denylists.
- [ ] `references/modules/{verb-noun}.md` written using the template above. No more than 5-line JS snippets inside.
- [ ] `references/modules/INDEX.md` updated with the new entry.
- [ ] `references/data/INDEX.md` updated if new data files added.
- [ ] User confirmed all new artifacts before disk writes.

Production stability is the contract — when training mode closes, the next Claude session loading this skill should be able to do the new task by reading ~1KB of module text and calling a script function, not by re-reading a 15KB how-to.

## Known unknowns (open work items)

| Capability | Listen for |
|---|---|
| Roll forward a prior-year engagement | "roll forward", "carry forward", "open last year's binder", "create from prior year" |
| Import a trial balance | "import the trial balance", "load the TB", "client sent the trial balance" |
| Disclosure checklist generation | "disclosure checklist", "DCL", "ASC 958 disclosures" |
| Bulk UpdateProperty / paste-fill from prior year | "fill down", "paste from prior year", "bulk fill" |
| Restore from Recycle Bin | "restore that workpaper", "undelete", "recycle bin" |
| Engagement letter templates | "engagement letter", "MLC", "draft a confirmation letter" |
| Risk Summary / KBA-502 deep flow | "risk summary", "tag a risk to a program" |
| Single Audit cascade (AID-301S etc.) | "single audit", "uniform guidance", "major program determination" |
| Commercial / EBP / Construction binder-program templates | First engagement of those types triggers it |
| AUD-100 / KBA-302 / KBA-400-driven engagement-condition derivation | "fast-fill planning forms from tailoring answers" |

When a known unknown lands, run the ladder. Don't take shortcuts.


<!-- END -->
