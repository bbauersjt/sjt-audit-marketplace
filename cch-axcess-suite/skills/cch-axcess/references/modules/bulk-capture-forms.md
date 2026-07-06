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
  - scripts.kc
  - scripts.http_runner.ls_headers_js_expr (ls:kc sentinel)
status: validated
validated_on:
  - "Kymera 2025 EBP — 22 forms, 11.81 MB bundle, 2026-05-21"
---
# Module — Bulk Capture KC Forms to Disk

**Trigger phrases:** "capture all the forms", "pull every form's library", "bundle these forms into a file", "build the program library from this engagement", "bulk capture", "capture-and-discard workflow", "harvest this title's audit programs", any phrasing where the goal is to read N KC forms' full schemas at once and write them somewhere durable.

## What this module does

Given a list of workpaperIds in a KC binder, loop `GET /api/Workpaper/{eng}/{wpId}` for each, bundle the responses into a single JSON Blob, and trigger a Chrome download to disk. The downloaded file becomes the input to a local-Python pass (no per-form JSON ever passes through chat context).

Pairs with `add-audit-programs.md` (to add the forms first) and `remove-kc-form.md` (to clean up after). The three together form the **capture-and-discard campaign** workflow that builds out program-library MDs in sister skills (e.g. `cch-risk-assessment/programs/*.md`).

## Why disk, not context

A 22-form bundle weighed 11.81 MB live on 2026-05-21 (Kymera EBP). Each AUD-8xx response carries 50-200 KB of JSON — `collections`, `elements`, full step library with `childObjectList` sub-steps. Dragging that through chat context would burn budget for nothing, since the parsing is mechanical Python work, not Claude reasoning.

The rule: **raw form JSON never enters Claude's context**. The browser writes one bundle file. Python parses it locally. Claude only reads the summarized step counts + file paths after the parse.

## Prerequisites

- KC tab open on `knowledgecoach.cchaxcess.com/binder/{engagementGuid}/...` with KC tokens populated in `localStorage` (`kc.accessToken`, `kc.idToken`).
- Workpaper IDs for the forms to capture. Sources, in order of preference:
  1. The `AddIndexes` POST capture from the just-fired Add Forms wizard (see `architecture.md` — KC Add Indexes section). Carries `workpaperGuid` for every just-added form.
  2. The Add Forms POST *response* — same wpIds, populated server-side.
  3. `GetBinder.result.workpapers` filtered by name.
- A target download directory accessible to Claude (the user's Downloads folder, mounted via `request_cowork_directory`).

## Procedure

### Step 1 — Confirm token availability

```js
const accessToken = localStorage.getItem('kc.accessToken');
const idToken     = localStorage.getItem('kc.idToken');
if (!accessToken || !idToken) throw new Error('KC tokens missing — open a KC tab first');
```

### Step 2 — Loop GET, bundle, download

```js
const eng = '<engagementGuid>';
const wpIds = [
  {name: 'AUD-801 ...', wpId: '01c38855-...'},
  // one per form
];

const hdrs = {
  'Authorization': 'Bearer ' + accessToken,
  'IdToken': idToken,            // mixed-case on KC; all-caps IDToken on WPM
  'Accept': 'application/json'
};

const fetchOne = async (f) => {
  try {
    const r = await fetch(`https://knowledgecoach.cchaxcess.com/api/Workpaper/${eng}/${f.wpId}`, {headers: hdrs});
    return {name: f.name, wpId: f.wpId, status: r.status, data: r.status === 200 ? await r.json() : await r.text()};
  } catch(e) {
    return {name: f.name, wpId: f.wpId, error: String(e)};
  }
};

// Concurrency 5 — respectful, no throttling observed at this rate
const results = [];
for (let i=0; i<wpIds.length; i+=5) {
  const batch = wpIds.slice(i, i+5);
  results.push(...await Promise.all(batch.map(fetchOne)));
}

const bundle = {
  capturedAt: new Date().toISOString(),
  engagement: '<friendly name>',
  engagementGuid: eng,
  titleGuid: '<from binder URL>',
  forms: results
};

// Stash on window for retry if Chrome's multi-download prompt blocks the first attempt
window.__bundle = bundle;

const blob = new Blob([JSON.stringify(bundle, null, 2)], {type:'application/json'});
const a = document.createElement('a');
a.href = URL.createObjectURL(blob);
a.download = '<engagement-slug>-forms-bundle.json';
document.body.appendChild(a);
a.click();
document.body.removeChild(a);
```

### Step 3 — Get past Chrome's multi-download prompt

If a prior download fired in the same tab (e.g. an earlier form-bundle or POST-shape archive download), Chrome will block the second with a `"Allow this site to download multiple files?"` banner. The user must click **Allow**. If they miss it, re-trigger from `window.__bundle`:

```js
const blob = new Blob([JSON.stringify(window.__bundle, null, 2)], {type:'application/json'});
const a = document.createElement('a');
a.href = URL.createObjectURL(blob);
a.download = '<filename>';
document.body.appendChild(a);
a.click();
```

### Step 4 — Process locally

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

### Step 5 — Clean up the binder

Loop `remove-kc-form.md` over each captured wpId. Verify via `GetBinder` that the AUD-8xx (or whichever filter) count is back to baseline.

## Path-pattern gotchas in `collections[i].path`

Step-library collections are NOT always named `*.ProgramSteps`. Observed variants (EBP 2025):

| Path pattern | Example form | Notes |
|---|---|---|
| `.{DBK}.ProgramSteps` | AUD-801 CASH | Standard naming |
| `.{FORM-ID}.taxstatusprocedure` | AUD-810 | "procedure" suffix |
| `.{FORM-ID}.MinutesSubstantiveprocedure` | AUD-815 | "Substantiveprocedure" infix |
| `.{workpaperGuid}.EstimatesSubstantiveProcedure` | AUD-818 | **Path prefix is the workpaperGuid, not the DBK.** Discovered 2026-05-21. The parser must not assume DBK as the prefix — match by suffix (`procedure`, `programstep`, etc.) instead. |

When writing the step-collection matcher, use:
```python
if ("programstep" in path_lower
    or path_lower.endswith("procedure")
    or "substantiveprocedure" in path_lower):
    ...
```

## Why this lives in `cch-axcess` (and not the sister skill)

The mechanical bits — auth, bundling, Chrome download trigger, path-pattern matching — are CCH Axcess platform concerns. They apply to any campaign across any industry title (NPO / EBP / ASB / ALG).

The *destination layout* — which MD file an AUD-8xx form maps to, what section structure to write — is domain-specific and lives in the calling skill (e.g. `cch-risk-assessment`).

## Validated on

- Kymera Physicians 401k Plan (EBP 2025), 2026-05-21: 22 EBP AUD-8xx forms captured in one bundle (11.81 MB). All 22 GETs returned 200. Local Python parser extracted 1,171 program steps and 102 tailoring questions across 18 target MD files (5 newly-created for EBP-only areas: `notes-receivable-participants.md`, `benefit-payments.md`, `tax-status-plan.md`, `changes-in-provider.md`, `participant-data.md`, `minutes-documents.md`). Subsequent batch DELETE cycle cleaned all 22 forms back to baseline; GetBinder verified zero AUD-8xx remaining.

## Cross-reference

- `add-audit-programs.md` — Step 1 of the campaign: get the forms into the binder.
- `remove-kc-form.md` — Step 3 of the campaign: clean up. Bonus learning from Kymera 2026-05-21: **KC tokens (`kc.accessToken` + `IDToken` all-caps) work directly for WPM `DELETE` calls** — no separate WPM header capture needed when driving from a KC tab. Single Bearer is interchangeable; only the IdToken header-name case differs across the two subdomains.


<!-- END -->
