---
summary: Move AUD-8xx program steps in / out — bring steps in or send to library ONLY (full-state replacement); NOT tailoring answers / risk-linking / responses / sign-off (that whole build-out is populate-program)
leg: kc
triggers:
  - "add steps to the [Cash/Investments/AR/etc.] program"
  - "pull in steps for [area]"
  - "remove this step from the program"
  - "send this step back to the library"
  - "select these audit steps"
  - "tailor the program steps"
  - "build out the AUD-8xx step list"
  - "update visible steps on [AUD-8xx]"
inputs:
  - "Engagement GUID"
  - "AUD-8xx workpaperId"
  - "KC tab on form with KC tokens in localStorage"
  - "list of desired step keys"
calls:
  - scripts.kc.toggle_program_step
status: validated
---
# Module — Toggle Program Steps (Add / Remove from Audit Program)

> **wpId lookup — GetBinder FIRST.** See `architecture.md` → "WPM surface — confirmed facts".

**Trigger phrases:** "add steps to the [Cash/Investments/AR/etc.] program", "pull in steps for [area]", "remove this step from the program", "send this step back to the library", "select these audit steps", "tailor the program steps", "build out the AUD-8xx step list", "update visible steps on [AUD-8xx]".

## What this module does

Move program steps between the **library** (sidebar, `visible: false`) and the **active program** (`visible: true`) on any AUD-8xx form via one POST. Same mechanism for adds, removes, and reorders — it's **full-state replacement**, not incremental.

## Prerequisites

- The engagement's KC binder has the AUD-8xx form already added and indexed (run `add-audit-programs.md` first if not).
- A Chrome tab open on the KC form: `https://knowledgecoach.cchaxcess.com/binder/{eng}/workpaper/{wpId}`.
- KC auth tokens reachable from `localStorage` (see `references/architecture.md` — KC auth / READ-WRITE fork). No monkey-patch needed for this endpoint.

## API call

```
POST https://knowledgecoach.cchaxcess.com/api/Workpaper/UpdateProgramStep
Headers:
  Authorization: Bearer <kc.accessToken from localStorage>
  IdToken: <kc.idToken from localStorage>
  Accept: application/json
  Content-Type: application/json
Body:
{
  "binderId":    "<engagement GUID>",
  "workpaperId": "<AUD-8xx workpaperId>",
  "value":       "<stepKey1>;<stepKey2>;..."   // full desired visible-set
}
```

**Critical: `value` is full-state replacement.** Every POST replaces the entire active-step set. To add one step, send (current visible keys + new key). To remove one step, send (current visible keys minus that key). To clear all, send `""`.

**No trailing semicolon** in the observed format (`a;b` not `a;b;`). Different convention from `.{AREA}.ProgramSteps / Risks` (which uses trailing semi). Don't confuse the two.

## Building the value string

For each step you want visible, include:

1. The step row's `key` from `.{AREA}.ProgramSteps[].key`.
2. Plus the `key` of every entry in that step's `childObjectList` (sub-steps) that should also be visible.

For example, adding step #0 "Debt and Equity Investments – Detailed Analysis" the body's `value` was `"<childSubStepKey>;<parentStepKey>"` — two GUIDs because that step has one sub-step in its `childObjectList`. Both went visible together.

Order in the value string doesn't appear to matter — the server canonicalizes server-side.

## Procedure

### Step 1 — Fetch current form state

```js
const eng = '<engagement-guid>';
const wp  = '<AUD-8xx workpaperId>';
const r = await fetch(`https://knowledgecoach.cchaxcess.com/api/Workpaper/${eng}/${wp}`, {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('kc.accessToken')}`,
    'IdToken':       localStorage.getItem('kc.idToken'),
    'Accept':        'application/json'
  }
});
const form = (await r.json()).result;
const cols = JSON.parse(form.collections);
const ps   = cols.find(c => c.path.endsWith('.ProgramSteps'));
```

### Step 2 — Compute the desired visible-step set

```js
// Currently visible (these are the ones already in the program)
const currentlyVisible = [];
for (const row of ps.objectList) {
  if (row.visible === true) {
    currentlyVisible.push(row.key);
    for (const child of (row.childObjectList || [])) currentlyVisible.push(child.key);
  }
}

// Build the desired set:
//   - ADD:     currentlyVisible ∪ {newStep.key, ...newStep.childObjectList.map(c=>c.key)}
//   - REMOVE:  currentlyVisible \ {targetStep.key, ...targetStep.childObjectList.map(c=>c.key)}
//   - REPLACE: pick the exact list you want
```

### Step 3 — POST UpdateProgramStep

```js
const body = {
  binderId:    eng,
  workpaperId: wp,
  value:       desiredKeys.join(';')   // empty string is legal — clears all visible
};
await fetch('https://knowledgecoach.cchaxcess.com/api/Workpaper/UpdateProgramStep', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('kc.accessToken')}`,
    'IdToken':       localStorage.getItem('kc.idToken'),
    'Accept':        'application/json',
    'Content-Type':  'application/json'
  },
  body: JSON.stringify(body)
});
```

Server returns 200 and the page's internal state updates immediately. No explicit `/api/Workpaper/submit` was observed to be required for step-toggle to persist (the page fires a `Workpaper/refresh` automatically after the POST).

### Step 4 — Verify

Re-GET the form, walk `.{AREA}.ProgramSteps`, and confirm `row.visible === true` for every key in your desired set and `false` for every key not in it.

```js
const verify = (await (await fetch(`https://knowledgecoach.cchaxcess.com/api/Workpaper/${eng}/${wp}`, { headers: {...} })).json()).result;
const verifyCols = JSON.parse(verify.collections);
const verifyPs = verifyCols.find(c => c.path.endsWith('.ProgramSteps'));
const nowVisible = verifyPs.objectList.filter(r => r.visible === true).map(r => r.key);
// Compare to desiredKeys.
```

If a step you sent didn't go visible, check that it isn't gated by `IsApplicable === false` — the step library contains steps that are tailoring-question-gated. Steps with `IsApplicable === false` may silently be ignored by the toggle (this is unverified — flag for capture if encountered).

## Filling in step content after toggling visible

Toggling a step visible doesn't fill in its per-step fields — those still go through the
per-property `POST /api/Workpaper/UpdateProperty/{eng}/{wp}` documented in `fill-kc-form.md`.
Plan: toggle visible first, then UpdateProperty in sequence.

**A program step's only fillable per-step fields are `SignOff`, `Comment`, and `Comments`.**
**There is
NO `WpReference`-like field on a program step** — no workpaper-reference field exists at the
step level at all. (`Assertion`/`Risks` belong to the step's risk sub-structures, not the step
itself; they are not per-step fillable fields and were never a WP-ref.) If a user asks you to
set a step's WP reference, **say it doesn't exist** — do not silently drop the request. The
per-step write fields are SignOff / Comment / Comments, full stop.

For each newly-visible step, the firm convention is just:
1. Set `SignOff` (the step's sign-off token).
2. Set `Comment` / `Comments` per program defaults (the response/notes text).

## Known failure modes

- **Sub-steps left out of the value.** If a parent step is selected without its `childObjectList` keys included, the sub-steps render in the UI but may not be "officially" visible — unverified. Safe default: always include parent + all children.
- **Trailing semicolon (`a;b;`) on `value`.** Untested. The Risks property *requires* a trailing semi but the UpdateProgramStep `value` was sent without one in the live capture. Stick with no-trailing-semi until tested.
- **Concurrent writes.** Not stress-tested. Treat sequentially like UpdateProperty calls.
- **`IsApplicable: false` steps.** Sending a step gated by an unanswered tailoring question may be silently rejected. If the verify GET shows the step still `visible: false` after a POST, answer the gating TQ first (via `fill-kc-form.md`), then retry the toggle.

## Cross-area applicability

The endpoint takes binder + workpaper IDs only — there is nothing area-specific in the URL or body shape. Verified for `.INVEST.ProgramSteps`. Highly likely to work identically for every AUD-8xx form (`.CASH.ProgramSteps`, `.AR.ProgramSteps`, etc.) since they all share the same collection schema. First-use in any new area should still verify post-POST.

**Collection-path area token = area SHORT NAME, never the form number.** The path is
`.CASH.ProgramSteps` — **NOT** `.CASH801.ProgramSteps`.
The AUD-8xx form number does not appear in the collection key; using it produces a nonexistent
collectionKey that UpdateProperty accepts with a silent 200 (the silent-200 class — see
architecture.md). `build_write_payload` refuses a hand-assembled key for exactly this reason.

<!-- END -->
