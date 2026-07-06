---
summary: Rename / re-index Workpaper-type rows (PDFs, docs) — distinct from KCForms set-index
leg: wpm
triggers:
  - "re-index these workpapers"
  - "change the indexes on [folder]"
  - "rename workpaper indexes"
  - "renumber the workpapers"
  - "convert from old indexing to new"
  - "fix the indexes on the investments folder"
  - "set workpaper [name] to index [X]"
inputs:
  - "Engagement-view tab with WPM headers capturable"
  - "target folder's locationId"
  - "mapping of documentId -> newIndex"
calls:
  - scripts.wpm.rename_workpaper
  - scripts.auth_capture.INSTALL_MONKEYPATCH_JS
status: validated
validated_on:
  - "APNM 2025 — Investments folder, 10 PDFs renamed N-1-* to 1105-1114, 2026-05-20"
---
# Module — Rename Workpaper Index

> **Index verification (AX-26).** Read display indexes with
> `scripts.wpm.verify_index(row, object_type)` — Reports/KCForms use `index`,
> Workpapers use `documentIndex`; hand-picking the field false-negatives (BT3 B6).
> And NEVER hand-assemble `folderParentLineItems` — `wpm.move()` now refuses them
> (semantics are inverted per type; hand-rolled bodies silent-200, BT3 B5/B12).

**Trigger phrases:** "re-index these workpapers", "change the indexes on [folder]", "rename workpaper indexes", "renumber the workpapers", "convert from old indexing to new", "renumber [N-1-*] to [1105]", "fix the indexes on the investments folder", "set workpaper [name] to index [X]".

## What this module does

Re-indexes (renames the **Index** column of) one or more **Workpaper**-type items in a CCH Axcess binder folder via direct API calls. Handles bulk renames sequentially. **For KCForms-type items use `add-audit-programs.md` Step 8 instead** — the endpoint and payload shape are different.

## Why this is its own module

The KC form set-index endpoint documented in `add-audit-programs.md`:
```
PUT /v1/engagementview/{clientId}
Body: {index, name, objectId, objectType: "KCForms"}
```
**does not work for Workpaper items.** Hitting it with `objectType: "Workpaper"` returns 400 `"Supplied ObjectId and ObjectType does not exists."`

Workpapers have their own endpoint with a different URL, a different payload shape, and a type-coercion trap on the `tags` field. Codified here so future sessions don't waste cycles rediscovering it.

## Endpoint

```
PUT https://workpapermanagementapi.cchaxcess.com/v1/Documents/{clientId}/{documentId}
```

Headers: same as the rest of WPM — `Authorization: Bearer <JWT>`, `IDToken: <token>` (all-caps `IDToken`, distinct from KC's `IdToken`), `USERLocale`, `Accept-Language`, `CountryCode`, `Accept: application/json`, `Content-Type: application/json`.

Body: the **full Workpaper object** with `documentIndex` swapped to the new value. 43 fields required — the slim 4-field KCForms shape is rejected.

## Procedure

### Step 1 — Build WPM auth headers

**Primary: KC localStorage tokens.** Build the WPM header set from `kc.accessToken`/`kc.idToken` (all-caps `IDToken` for WPM) per the central builder in `architecture.md` ("Auth pattern"). A KC tab is sufficient — no engagement tab or monkey-patch needed. Tokens self-refresh, so re-read per call.

**Fallback only (no KC tab):** install the XHR monkey-patch on the engagement-view tab (`scripts.auth_capture.INSTALL_MONKEYPATCH_JS`) and trigger one folder navigation to capture a live header set.

### Step 2 — GET the target folder

```
GET /v1/NewEngagementView/{clientId}/{folderLocationId}/{engagementId}
```

Returns an array of items. Filter by `type === "Workpaper"`. Each item has the document data needed for the PUT (`documentId`, `name`, `locationId`, `locationGuid`, `fileExtension`, `fileId`, `signOffs`, etc.).

To find `folderLocationId`: click the target folder in the left tree with the capture patch installed, then read the URL of the resulting GET.

### Step 3 — Build the PUT body

Take the Workpaper object from the folder GET. Three things to fix before sending:

1. **Set `documentIndex`** to the new index value (this is the field the server persists as the displayed Index).
2. **Convert `tags` from string to array.** Folder GET returns `tags: "[]"` (a string). PUT requires `tags: []` (an actual array). Failure to convert returns 400 `"Error converting value '[]' to type 'System.Collections.Generic.List`1[System.String]'."`
3. **Add the 2 fields missing from the folder GET response** — `fileName` and `setNotesToDoNotRollForward` (the PUT requires them; the GET omits them). The other defaults below are belt-and-braces only: those 11 fields ARE present in the GET (confirmed 2026-06-03), and `rename_workpaper` uses `setdefault` so passing the real row through is always safe. What is NOT safe is a synthetic dict — required fields like `rollForwardOption` and `documentId` 400 if absent, so always start from an actual `folder_get` row:

```js
const body = Object.assign({
  children: [],
  documentType: 1,
  fileName: t.name,         // duplicate of `name`
  formStatus: null,
  isKcV2: false,
  isLinksFrozen: null,
  isReportNameChanged: null,
  kcFormType: 0,
  kcTitleName: null,
  kcTitleYear: null,
  setNotesToDoNotRollForward: false,
  sortOrder: 0
}, workpaperFromGet, {
  documentIndex: newIndex,
  tags: []                  // override the string version
});
```

The `index` field can be left as the old value — the server uses `documentIndex` for the persisted index. (The UI sends the old `index` unchanged in its successful PUT; harmless.)

### Step 4 — Fire PUTs sequentially

One PUT per workpaper:

```
PUT https://workpapermanagementapi.cchaxcess.com/v1/Documents/{clientId}/{documentId}
Body: <body from Step 3>
```

**Sequential, not parallel.** Concurrent PUTs are not verified safe (same race-condition caveat as KC form writes). Status 200 = success. The response body is EMPTY — it does NOT echo the document (confirmed 2026-06-03). Verify with a follow-up folder GET (Step 5), never the PUT response.

### Step 5 — Verify

Re-trigger the folder GET (click away from the folder and back, or call the GET directly). Confirm the items' new indexes appear in the response. UI verification: refresh the folder view in the engagement-view tab — the Index column should reflect the new values.

## Known failure modes

- **400 "ObjectId/ObjectType does not exsits" [sic]** — wrong endpoint. You used `/v1/engagementview/{clientId}` with the KCForms-shaped payload. Switch to `/v1/Documents/{clientId}/{documentId}` and the full Workpaper body.
- **400 "Error converting value '[]' to type 'System.Collections.Generic.List'"** — `tags` came in as a string. Convert to array.
- **400 with a `validation errors` envelope** — a required field is missing or the wrong type (synthetic dict instead of a real folder_get row: `rollForwardOption`, `documentId`). The error body names the field; pass the actual row through.
- **Folder cache** — clicking the same folder twice in the left tree does NOT refire the GET (the SPA caches the listing). To force a fresh GET, click a different folder first, then click back. Useful when verifying writes.
- **`tags` defaults can't be `[""]` either** — must be a clean empty array `[]` if the workpaper has no tags. If tags exist, parse the stringified JSON from the GET (`JSON.parse(t.tags)`) and resend as a real array.

## Comparison: Workpaper vs. KCForms set-index

| Aspect | KCForms (use `add-audit-programs.md`) | Workpapers (this module) |
|---|---|---|
| Endpoint | `PUT /v1/engagementview/{clientId}` | `PUT /v1/Documents/{clientId}/{documentId}` |
| Body shape | 4 fields: `{index, name, objectId, objectType: "KCForms"}` | Full document (43 fields, `tags` as array, `documentIndex` as the writable index) |
| Index field | `index` | `documentIndex` |
| objectType value | `"KCForms"` | n/a (URL-routed by documentId) |
| Order matters | Set-Index AFTER Move (new forms arrive with null index; Move preserves existing index) | n/a — rename in place |

## Validated on

- **APNM 2025 (NFP), 2026-05-20** — Investments folder (locationId 2964799). 10 PDFs renamed from `N-1-1` through `N-1-10` to `1105` through `1114`. First write via UI Properties dialog (to capture the request shape); remaining 9 via direct PUT replay. All 9 returned 200 after fixing the `tags` field. Visual verification: Index column updated immediately.


<!-- END -->
