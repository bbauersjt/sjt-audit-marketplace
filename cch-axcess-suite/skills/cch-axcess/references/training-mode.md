# Training Mode — Script-First Capture Protocol

> **Gate, checklist, front-matter spec, and module template live in `learn-protocol.md`.**
> Read it first — it owns the CONSENT WALL and the mechanical close-out. This file is the
> long-form manual: capture mechanics, the monkey-patch, the fallback ladder, the
> known-unknowns backlog. Consult it when the checklist alone isn't enough.

Terminal state is a tested `scripts/*.py` function + a `references/endpoints/*.json` spec +
a thin module that calls the script. Markdown describing "how to do the operation by hand"
is a failure state — codify it as code or don't codify it at all.

## The fallback ladder (strict order)

Work DOWN this ladder. Skip a rung only if it's impossible — never because it's easier.

### Rung 1 — API direct (no capture needed)

If `architecture.md` lists the endpoint and a `scripts/*.py` function exists, use it. Done.

### Rung 2 — API capture, then script

Endpoint exists but isn't in the skill yet. Capture once, script it, then use it.

1. Install monkey-patch (`scripts.auth_capture.INSTALL_MONKEYPATCH_JS`) on the relevant tab.
2. Have the user trigger ONE real UI action — the literal action they want Claude to learn. Don't speculate.
3. Read `window.__cch_capture` (`scripts.auth_capture.capture_query_js(host_substring)`).
4. **Replay programmatically to confirm.** Use `scripts.http_runner.build_xhr_call()` or `build_fetch_call()` with the captured headers. Confirm the response matches what the UI did. If it doesn't, capture is incomplete — go back to step 2.
5. **Verify the side effect** with a follow-up GET.
6. **Codify as code first.** Add a function to the appropriate `scripts/*.py`, a JSON spec to `references/endpoints/{operation}.json`, then the thin module. Never write the module without the script.

### Rung 3 — UI clicking (LAST RESORT, always with capture)

If the operation genuinely cannot be done via API — file-upload widgets, multi-step wizards with hidden state — drive the UI through Claude in Chrome. **BUT:** install the monkey-patch first and capture every network call the UI fires. Treat the captures as a draft of the API for the next iteration:

- After the task succeeds, audit the captures.
- If any captured XHR is the operation's real mutation call (not analytics or state-sync), promote it to Rung 2: write the script function and endpoint spec, retire the UI path.
- If the operation is genuinely click-only (no XHR backs it), document the click sequence — but tag the module `status: ui-only` so future sessions try Rung 2 first if CCH ships an API.

## Already known — do NOT rediscover

Everything in `architecture.md` is settled. Read it once before doing anything novel. Do not re-derive subdomain auth patterns, ID-glossary mappings, the misnamed `engagementId` field, PUT-vs-POST for set-index, `IdToken` vs `IDToken` casing, Move-PRESERVES-the-index, the recommendedAnswer trap, or the renderProperty key case-inconsistency. Those are facts. Move on.

If you find them outdated, update `architecture.md` AND the relevant `endpoints/*.json` in one pass. Never leave the two files disagreeing.

## Where new facts go

| Discovery | Destination |
|---|---|
| New endpoint URL/method/body/response shape | `references/endpoints/{operation}.json` (new or updated) |
| Platform-level gotcha (auth, ID, ordering) | `references/architecture.md` |
| Workflow sequence (which calls, what order, conditional logic) | `references/modules/{verb-noun}.md` |
| Enum, denylist, header list | `references/config/*.json` |
| Firm-wide reusable lookup (binder templates, form catalogs, group codes) | `references/data/*.xlsx` + `data/INDEX.md` |
| Engagement-specific state (form indexes, xrefs, decisions log) | user's working folder (`{slug}-xrefs.xlsx`) — never the read-only install |
| Executable operation (API call, parser, planner) | `scripts/*.py` |
| Big captured payload (form bundles, page snapshots) | disk — never context. Module returns a path. |

## Listen-mode log structure (working context only)

While capturing, keep this structure in working memory. **Transcribe into the script + endpoint spec + module afterward — never leave it as the only artifact.**

```
GOAL: <one-line user objective>
ENGAGEMENT: <client> / clientId <X> / engagementGuid <Y> / industry title <Z>

STEPS (only confirmed-successful):
  1. <action>
     - URL: <method> <full URL with placeholders>
     - Required headers (names only, no token values)
     - Body shape (field names + sample values)
     - Response (status, key fields)
     - Verification (follow-up GET)

FAILURES ALONG THE WAY:
  - <what didn't work and why>  → "Known failure modes" in the module.

GOTCHAS:
  - <surprises, race conditions, ordering, case-sensitivity>  → architecture.md or endpoint spec.

REFERENCE DATA NEEDED:
  - <files to add to references/data/>
```

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
| Commercial / EBP / Construction binder-program templates | first engagement of those types triggers it |
| AUD-100 / KBA-302 / KBA-400-driven engagement-condition derivation | "fast-fill planning forms from tailoring answers" |

When a known unknown lands, run the ladder. Don't take shortcuts.

### Document-level sign-off REMOVAL — CAPTURED 2026-07-09 (was the top backlog item)

Done. Rung-2 capture ran live in a BB-supervised session (Coop Consulting, clientId 101229):
`POST /v1/signoff/removeSignOff`, keyed by (objectId, signatureType), a POST state-change not a
DELETE (No-Hard-Delete rule cleared). Shipped as `scripts.wpm.remove_signoff` +
`scripts.wpm.document_get` (per-document sign-off read), `references/endpoints/signoff_remove.json`,
and `references/modules/remove-signoff.md`. **Applying** sign-offs stays human-only (no add script).
The in-form program-STEP un-sign-off (KC leg) was captured in the SAME session — a `.{AREA}.ProgramSteps`
`SignOff` property set to `"[]"` via UpdateProperty (`scripts.kc.clear_program_step_signoff`,
`modules/clear-program-step-signoff.md`). Scope bound (api-ui-parity, BB 2026-07-09): removing ANOTHER
user's document-level sign-off is OUT OF BOUNDS — the UI only removes your own, so the bot must too.
The API keys removal by (objectId, signatureType) with no userId and WOULD remove a colleague's; the
artifacts require confirming the leg is the logged-in user's before removing, and the foreign-removal
path is NOT to be probed (the original Anchondo/KBA-400 case was deliberately left untested). See CHANGELOG AX-42.


<!-- END -->
