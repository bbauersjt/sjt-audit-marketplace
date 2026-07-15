---
summary: Bulk-capture N KC forms' full schemas to disk (e.g. seed a sister skill)
leg: kc
triggers:
  - "capture all the forms"
  - "pull every form's library"
  - "bundle these forms into a file"
  - "build the program library from this engagement"
  - "bulk capture"
  - "capture-and-discard workflow"
  - "harvest this title's audit programs"
inputs:
  - "KC tab on knowledgecoach.cchaxcess.com/binder/{eng}/... with KC tokens in localStorage"
  - "list of {name, wpId} for forms to capture"
  - "user-mounted download directory"
calls:
  - scripts.kc.bulk_capture_forms_js
status: validated
---
# Module — Bulk Capture KC Forms to Disk

**Trigger phrases:** "capture all the forms", "pull every form's library", "bundle these forms into a file", "build the program library from this engagement", "bulk capture", "capture-and-discard workflow", "harvest this title's audit programs", any phrasing where the goal is to read N KC forms' full schemas at once and write them somewhere durable.

## What this module does

- Given a list of workpaperIds in a KC binder, loop `GET /api/Workpaper/{eng}/{wpId}` for each, bundle the responses into a single JSON Blob, and trigger a Chrome download to disk.
- The downloaded file becomes the input to a local-Python pass. **Raw form JSON never enters Claude's context** — the browser writes one bundle file, Python parses it locally, Claude only reads the summarized step counts + file paths after the parse.
- Pairs with `add-audit-programs.md` (add the forms first) and `remove-kc-form.md` (clean up after). The three together form the **capture-and-discard campaign** workflow that builds out program-library MDs in sister skills (e.g. `cch-risk-assessment/programs/*.md`).

## Prerequisites

- KC tab open on `knowledgecoach.cchaxcess.com/binder/{engagementGuid}/...` with KC tokens populated in `localStorage` (`kc.accessToken`, `kc.idToken`).
- Workpaper IDs for the forms to capture. Sources, in order of preference:
  1. The `AddIndexes` POST capture from the just-fired Add Forms wizard (see `architecture.md` — KC Add Indexes section). Carries `workpaperGuid` for every just-added form.
  2. The Add Forms POST *response* — same wpIds, populated server-side.
  3. `GetBinder.result.workpapers` filtered by name.
- A target download directory accessible to Claude (the user's Downloads folder, mounted via `request_cowork_directory`).

## Procedure

### Step 1 — Fetch, bundle, download (one built call)

```python
from scripts import kc
wp_ids = [{"name": "AUD-801 ...", "wpId": "01c38855-..."}]  # one per form
js = kc.bulk_capture_forms_js(eng_guid, wp_ids, "<engagement-slug>-forms-bundle.json", concurrency=5)
# Run js in the KC tab (chrome_api_call bridge, or linked-tab JS tool).
```

The built JS reads `kc.accessToken`/`kc.idToken` from localStorage itself (open a KC tab first — it throws if they're missing), loops `GET /api/Workpaper/{eng}/{wpId}` at the given concurrency (5 observed safe), bundles every response, stashes it on `window.__bundle`, and triggers the Chrome download. Raw form JSON never enters context.

### Step 2 — Get past Chrome's multi-download prompt

If a prior download fired in the same tab, Chrome blocks the second with a `"Allow this site to download multiple files?"` banner — the user clicks **Allow**. If they miss it, re-trigger from the stashed bundle (no re-fetch):

```js
const b = new Blob([JSON.stringify(window.__bundle,null,2)],{type:'application/json'});
const a = Object.assign(document.createElement('a'),{href:URL.createObjectURL(b),download:'<filename>'});
document.body.appendChild(a); a.click();
```

### Step 3 — Process locally

Move (or just read in-place) the bundle into the sister-skill's `captures/` folder. Run a Python script that:

1. Loads the bundle.
2. For each form: parses `result.collections` (it's a JSON-encoded string — `JSON.parse` it).
3. Walks each collection by `path`:
   - `*.AuditObjective*` → primary audit objectives + assertion mapping
   - `*TailoringQuestion*` → tailoring questions + default answers (lowercase- or mixed-case; match `.toLowerCase()`)
   - `*RelevantAssertion*` → per-assertion grid (usually empty pre-engagement)
   - `*ProgramSteps*`, `*Procedure*`, `*SubstantiveProcedure*` → step library (walk `childObjectList` for sub-steps)
4. Extracts each step's `renderProperties` by case-insensitive key match (`description`, `linkedassertions`, `linkedrisks`, `workpaperreference`).
5. Writes structured markdown sections into the target MDs.

Reference implementation: `cch-risk-assessment/captures/process_bundle.py` (when present).

### Step 4 — Clean up the binder

Loop `remove-kc-form.md` over each captured wpId. Verify via `GetBinder` that the AUD-8xx (or whichever filter) count is back to baseline.

## Path-pattern gotchas in `collections[i].path`

Step-library collections are NOT always named `*.ProgramSteps`. Observed variants:

| Path pattern | Example form | Notes |
|---|---|---|
| `.{DBK}.ProgramSteps` | AUD-801 CASH | Standard naming |
| `.{FORM-ID}.taxstatusprocedure` | AUD-810 | "procedure" suffix |
| `.{FORM-ID}.MinutesSubstantiveprocedure` | AUD-815 | "Substantiveprocedure" infix |
| `.{workpaperGuid}.EstimatesSubstantiveProcedure` | AUD-818 | **Path prefix is the workpaperGuid, not the DBK.** The parser must not assume DBK as the prefix — match by suffix (`procedure`, `programstep`, etc.) instead. |

When writing the step-collection matcher, use:
```python
if ("programstep" in path_lower
    or path_lower.endswith("procedure")
    or "substantiveprocedure" in path_lower):
    ...
```

## Cross-reference

- `add-audit-programs.md` — Step 1 of the campaign: get the forms into the binder.
- `remove-kc-form.md` — Step 3 of the campaign: clean up. **KC tokens (`kc.accessToken` + `IDToken` all-caps) work directly for WPM `DELETE` calls** — no separate WPM header capture needed when driving from a KC tab. Single Bearer is interchangeable; only the IdToken header-name case differs across the two subdomains.
- The mechanical bits here (auth, bundling, download trigger, path-pattern matching) apply to any industry title (NPO/EBP/ASB/ALG). The *destination layout* — which MD file an AUD-8xx form maps to — is domain-specific and lives in the calling skill (e.g. `cch-risk-assessment`), not here.


<!-- END -->
