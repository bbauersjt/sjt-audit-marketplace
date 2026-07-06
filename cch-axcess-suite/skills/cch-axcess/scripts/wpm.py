"""Workpaper Management API operations.

Cross-origin from engagement.cchaxcess.com — every call uses XHR (fetch fails
CORS preflight). The Move PUT has Folder vs everything-else swap semantics —
use the helpers below, never assemble the body by hand. See
references/endpoints/wpm_move.json.

Tab requirements: an engagement.cchaxcess.com tab — OR a KC tab: KC tab tokens
(kc.accessToken + kc.idToken) work for ALL WPM reads and writes (confirmed
2026-06-03), header names per WPM case (Authorization + IDToken).
Headers requirements: capture WPM headers via scripts.auth_capture monkeypatch.
Locale headers (USERLocale / Accept-Language / CountryCode) are REQUIRED on
every WPM call — without them GETs return status 200 with an EMPTY ARRAY
(silent failure). Every helper below merges http_runner.WPM_LOCALE_HEADERS
automatically; hand-rolled XHRs must merge them too.

----- HARD-DELETE POLICY (read before adding anything new) -----

HARD DELETE IS NOT A CAPABILITY OF THIS SKILL.

Past incident (Kymera 2025 EBP, 2026-05-28): two DELETE calls to
/v1/KnowledgeCoach/.../deleteform/... corrupted the binder — `lastUsedTitleGuid`
went null and ALL workpapers became invisible (not just the two deleted).
Recycle Bin did NOT recover them. Binder had to be rebuilt from scratch.

Rule: NEVER hard-delete anything in CCH from this skill — forms, folders,
leadsheets, reports. If a user requests a delete, soft-delete: move the
object into a "User to delete" folder (index 9999) and let them clean up
from the UI on their own time.

If a future training-mode capture session sees a DELETE call, DO NOT
script it. Wrap it as a soft-delete instead, or refuse the operation.
Forbidden endpoints (never wrap, never call):
  - DELETE knowledgecoach.cchaxcess.com/api/.../deleteform/...
  - DELETE workpapermanagementapi.cchaxcess.com/v1/NewEngagementView/{clientId}/folder/{folderId}
  - DELETE workpapermanagementapi.cchaxcess.com/v1/Documents/{clientId}/{documentId}

Fund-accounting DELETEs in `funds.py` predate this policy and are scoped
to that one feature; do not extend the pattern elsewhere.
"""
from . import http_runner

WPM = "https://workpapermanagementapi.cchaxcess.com"

def _h(headers):
    """Locale-complete header set for WPM (see module docstring).

    Accepts a dict (captured headers — locale merged in) OR an "ls:<family>"
    sentinel (passed through; ls:wpm already emits locale headers at runtime)."""
    if isinstance(headers, str):
        return headers
    return http_runner.with_wpm_locale(headers)


USER_DELETE_FOLDER_NAME = "User to delete"
USER_DELETE_FOLDER_INDEX = "9999"


def folder_get(client_id: int | str, eng_id: int | str, folder_id: int | str, headers: dict) -> str:
    """JS for: GET /v1/NewEngagementView/{clientId}/{folderId}/{engagementId}.

    folder_id can be a real locationId OR a pseudo: -1 Unfiled WPs, -2 Reports,
    -3 Leadsheets, -4 KC Forms.

    Response body is a FLAT JSON ARRAY of rows — there is NO {lineItems:[...]}
    or {result:[...]} wrapper. Parse with json.loads(body) directly.
    Locale headers are merged automatically; without them the server returns
    200 + [] for every folder (confirmed 2026-06-03).
    """
    return http_runner.build_xhr_call(
        "GET",
        f"{WPM}/v1/NewEngagementView/{client_id}/{folder_id}/{eng_id}",
        _h(headers),
    )


def folder_tree(client_id: int | str, headers: dict) -> str:
    """JS for: GET /v1/NewEngagementView/folders/{clientId}.

    Returns the full binder folder tree as a nested JSON structure:
      {engagementId, root: [{locationId, parentLocationId, index, name, locationGuid,
                              children: [...recursive...]}]}

    Use this to discover locationIds for any folder (section folders, "User to delete",
    etc.) without having to scan individual folder IDs. Walk `root[0].children` for
    top-level binder sections.

    Confirmed working: Kymera 401(k) 2025 (client 99286), 2026-05-28.
    """
    return http_runner.build_xhr_call(
        "GET",
        f"{WPM}/v1/NewEngagementView/folders/{client_id}",
        _h(headers),
    )


def create_folder(client_id: int | str, folder_index: str, folder_name: str,
                  parent_folder_id: int | None, headers: dict) -> str:
    """JS for: POST /v1/NewEngagementView/folder.

    parent_folder_id=None creates a top-level folder. Returns the new locationId
    as plain text. Note the misnamed `engagementId` body field — it carries clientId.

    NAMING CONVENTION (double-index bug, fixed 2026-06-04): folder_name must be the
    CLEAN descriptive name with NO index prefix — folder_index carries the index and
    the binder UI renders both ("01 | 01 Front of File" was the bug). Wrapper folder:
    NO index (folder_index="" — changed 2026-06-04 AX-16; empty index unverified live,
    fallback branch in setup-binder-from-index.md), folder_name="[ShortClientName] [Year]".
    """
    body = {
        "engagementId": client_id,
        "folderIndex": folder_index,
        "folderName": folder_name,
        "parentFolderId": parent_folder_id,
    }
    return http_runner.build_xhr_call("POST", f"{WPM}/v1/NewEngagementView/folder", _h(headers), body)


def rename_folder(client_id: int | str, location_id: int | str, folder_index: str,
                  folder_name: str, headers: dict) -> str:
    """JS for: PUT /v1/NewEngagementView/{clientId}/folder — rename / re-index a folder.

    Captured live 2026-06-03 (Properties-dialog monkeypatch; 24 folders batch-renamed
    at 200 from a KC tab — see endpoints/wpm_folder_rename.json). The load-bearing
    field is `oldLocationId`: attempts with `locationId` return 400 "Parent not
    found"; PUT/PATCH on /folder/{locId} return 405. The misnamed `engagementId`
    body field carries clientId (same convention as create_folder). folder_name must
    be the CLEAN name with NO index prefix (see create_folder docstring).
    """
    body = {
        "oldLocationId": location_id,
        "engagementId": client_id,
        "folderIndex": folder_index,
        "folderName": folder_name,
    }
    return http_runner.build_xhr_call("PUT", f"{WPM}/v1/NewEngagementView/{client_id}/folder", _h(headers), body)


# NOTE: hard DELETE on folders is intentionally NOT exposed. See the
# "HARD-DELETE POLICY" block at the top of this file. Use
# `soft_delete_folder()` to move a folder into "User to delete" instead.


def _move_line_item(object_type: str, client_id: int | str, own_loc: int | str,
                    dest_loc: int | str, object_id: str | None) -> dict:
    """Build ONE folderParentLineItems entry with the type-correct semantics.

    For LeadSheet / KCForms / Report: locationId=DEST, parentLocationId=OWN.
    For Folder: locationId=OWN, parentLocationId=DEST, objectId=None.

    WORKPAPER TYPE (confirmed 2026-05-28, Kymera EBP):
    Uploaded Excel/PDF files have type="Workpaper" in the API response.
    When moving them, use objectType="Workpaper" and periodId=None (NOT "LeadSheet"
    and NOT periodId=""). Using "LeadSheet" returns 200 but silently no-ops.
    """
    if object_type == "Folder":
        return {
            "engagementId": client_id,
            "locationId": own_loc,
            "parentLocationId": dest_loc,
            "objectId": None,
            "objectType": "Folder",
            "periodId": None,
        }
    else:
        return {
            "engagementId": client_id,
            "locationId": dest_loc,
            "parentLocationId": own_loc,
            "objectId": object_id,
            "objectType": object_type,
            "periodId": None if object_type == "Workpaper" else "",
        }


def move(client_id: int | str, items: list[dict], headers: dict) -> str:
    """JS for: PUT /v1/NewEngagementView/{clientId}/folder/parent  (batch native).

    items: list of {object_type, own_loc, dest_loc, object_id}.
    object_type in {Folder, LeadSheet, KCForms, Report}.

    For LeadSheet/KCForms/Report, object_id is documentId (or 'reports/{type}'
    for Report). For Folder, object_id is ignored (None).

    Move PRESERVES any existing index and does NOT change the locationId
    (both confirmed live 2026-06-03 — earlier docs claiming the opposite were
    wrong). Move-then-Set-Index is still the right sequence for newly-added
    forms, which arrive in Unfiled with a null/empty index: Set-Index runs
    after Move to assign the target index. No re-GET needed after Move.
    """
    _VALID_TYPES = {"Folder", "LeadSheet", "KCForms", "Report", "Workpaper"}
    for i in items:
        missing = {"object_type", "own_loc", "dest_loc"} - set(i)
        if missing:
            raise ValueError(
                f"move() item missing {sorted(missing)}: {i!r}. Pass the SIMPLE item shape "
                "{object_type, own_loc, dest_loc, object_id} — NEVER hand-assemble "
                "folderParentLineItems (locationId/parentLocationId semantics are INVERTED "
                "per type and hand-rolled bodies silent-200 — BT3 B5 and B12).")
        if "locationId" in i or "parentLocationId" in i:
            raise ValueError(
                "move() received a hand-assembled folderParentLineItems entry "
                f"({i!r}). Pass {{object_type, own_loc, dest_loc, object_id}} — the "
                "builder derives locationId/parentLocationId with the type-correct "
                "(inverted) semantics. Hand-rolled bodies silent-200 (BT3 B5/B12).")
        if i["object_type"] not in _VALID_TYPES:
            raise ValueError(f"move() unknown object_type {i['object_type']!r} — one of {sorted(_VALID_TYPES)}")
    body = {
        "engagementId": client_id,
        "folderParentLineItems": [
            _move_line_item(i["object_type"], client_id, i["own_loc"], i["dest_loc"], i.get("object_id"))
            for i in items
        ],
    }
    return http_runner.build_xhr_call(
        "PUT", f"{WPM}/v1/NewEngagementView/{client_id}/folder/parent", _h(headers), body
    )


def set_index(client_id: int | str, items: list[dict], headers: dict) -> str:
    """JS for: N sequential PUTs to /v1/engagementview/{clientId} (no batch support).

    items: list of {index, name, object_id, object_type}.
    object_type in {KCForms, LeadSheet, Report}.

    USE PUT, NOT POST. POST returns 200 but is a silent no-op.

    STALE INDEX GOTCHA (confirmed 2026-05-28, Kymera EBP):
    If a WPM location is hard-deleted via the UI (e.g., user empties "User to delete"
    folder), the WPM index registry entry for that (index, name) pair persists.
    Any later set_index call with the same index+name returns 400:
      "This combination of Index and Name already exists."

    Fix: first PUT the stale objectId to a throwaway index/name to evict it:
      set_index(client_id, [{"index": "9998", "name": "<OLD NAME> OLD",
                             "object_id": "tbreports/<OLD_INT_ID>",
                             "object_type": "Report"}], headers)
    Then retry the real set_index — it will succeed.
    """
    calls = [
        {
            "method": "PUT",
            "url": f"{WPM}/v1/engagementview/{client_id}",
            "body": {
                "index": i["index"],
                "name": i["name"],
                "objectId": i["object_id"],
                "objectType": i["object_type"],
            },
        }
        for i in items
    ]
    return http_runner.build_batch_xhr(calls, _h(headers), concurrency=1)


def rename_workpaper(client_id: int | str, document_id: str,
                     new_index: str, current_doc: dict, headers: dict,
                     new_name: str | None = None) -> str:
    """JS for: PUT /v1/Documents/{clientId}/{documentId} — re-index a Workpaper.

    Different endpoint and body shape than KCForms set_index. Use this for
    Workpaper-type rows only (PDFs/docs); for KCForms use `set_index`.

    current_doc MUST be an actual Workpaper-type row from a recent `folder_get`
    — do NOT construct a synthetic dict. Required fields this helper does not
    inject (`rollForwardOption` int, `documentId` str) will 400 if absent:
      400 "Not Valid Options for RollForwardOption" / "Not Valid Request for
      DocumentId". The PUT requires the full document body; this helper patches:
      1. `documentIndex` swapped to new_index (and `name` if new_name given).
      2. `tags` converted from string "[]" to array [].
      3. The 2 fields folder_get omits (`fileName`, `setNotesToDoNotRollForward`)
         injected with defaults. (The other setdefault lines below are harmless
         belt-and-braces — those 11 fields ARE present in the GET, confirmed
         2026-06-03.)

    Response body on success is EMPTY (status 200) — it does NOT echo the
    document. Verify with a follow-up folder_get, never the PUT response.
    Sequential only (don't parallelize same-row PUTs).
    """
    body = dict(current_doc)
    body["documentIndex"] = new_index
    if new_name is not None:
        body["name"] = new_name
    tags = body.get("tags")
    if isinstance(tags, str):
        try:
            import json as _json
            body["tags"] = _json.loads(tags) if tags else []
        except Exception:
            body["tags"] = []
    body.setdefault("children", [])
    body.setdefault("documentType", 1)
    body.setdefault("fileName", body.get("name"))
    body.setdefault("formStatus", None)
    body.setdefault("isKcV2", False)
    body.setdefault("isLinksFrozen", None)
    body.setdefault("isReportNameChanged", None)
    body.setdefault("kcFormType", 0)
    body.setdefault("kcTitleName", None)
    body.setdefault("kcTitleYear", None)
    body.setdefault("setNotesToDoNotRollForward", False)
    body.setdefault("sortOrder", 0)
    return http_runner.build_xhr_call(
        "PUT", f"{WPM}/v1/Documents/{client_id}/{document_id}", _h(headers), body
    )


# ============================================================================
# Download / replace path (file-io.md) — live-validated 2026-06-03 (T08).
# ============================================================================


def download_url(client_id: int | str, client_guid: str, document_id: str) -> str:
    """URL serving raw file bytes for a Workpaper document.

    Leading GUID is the per-CLIENT GUID (KC GetBinder.result.clientGuid) — NOT
    the document fileId (reads all-zeros) and NOT firmId.
    """
    return f"{WPM}/v1/documents/{client_guid}/file/{client_id}/{document_id}"


def download_to_browser_js(client_id: int | str, client_guid: str, document_id: str,
                           save_name: str, headers: dict) -> str:
    """JS: XHR the file as a Blob and trigger a native browser download.

    Returns 'ok bytes=N' on success. The file lands in the browser's Downloads
    folder — mount it with request_cowork_directory and copy (cp, not mv) to the
    target folder. Bytes never cross the tool boundary (PII-filter safe).
    """
    import json as _json
    h_js = http_runner._headers_js(_h(headers))
    return (
        "(() => new Promise((resolve) => {\n"
        "  const x = new XMLHttpRequest();\n"
        "  x.open('GET', " + _json.dumps(download_url(client_id, client_guid, document_id)) + ", true);\n"
        "  const h = " + h_js + ";\n"
        "  for (const k in h) x.setRequestHeader(k, h[k]);\n"
        "  x.responseType = 'blob';\n"
        "  x.onload = () => {\n"
        "    if (x.status !== 200) { resolve('fail status=' + x.status); return; }\n"
        "    const url = URL.createObjectURL(x.response);\n"
        "    const a = document.createElement('a');\n"
        "    a.href = url; a.download = " + _json.dumps(save_name) + ";\n"
        "    document.body.appendChild(a); a.click(); a.remove();\n"
        "    setTimeout(() => URL.revokeObjectURL(url), 5000);\n"
        "    resolve('ok bytes=' + x.response.size);\n"
        "  };\n"
        "  x.onerror = () => resolve('fail network');\n"
        "  x.send(null);\n"
        "}))()"
    )


def evict_for_replace(client_id: int | str, original_row: dict, headers: dict) -> str:
    """JS: bump the original's (index, name) to free its slot for a replacement.

    index "3100" -> "3100.DEL", name -> name + " (replaced)". original_row MUST
    be an actual folder_get row (see rename_workpaper). 200 with empty body on
    success; verify via folder_get.
    """
    old_index = original_row.get("documentIndex") or original_row.get("index") or ""
    return rename_workpaper(
        client_id, original_row["documentId"], f"{old_index}.DEL", original_row,
        headers, new_name=f'{original_row.get("name", "")} (replaced)',
    )


def claim_original_slot(client_id: int | str, new_row: dict, index: str,
                        name: str, headers: dict) -> str:
    """JS: give the replacement document the original's exact (index, name).

    new_row: the replacement's actual folder_get row. Run AFTER evict_for_replace
    has freed the slot, or the PUT 400s with the index/name-exists error.
    """
    return rename_workpaper(client_id, new_row["documentId"], index, new_row,
                            headers, new_name=name)


def check_index_available(client_id: int | str, document_id: str, index: str,
                          headers: dict) -> str:
    """JS: GET /v1/Documents/{clientId}/{documentId}/{index} — index-collision probe.

    Response {documentIndexExistsStatusCode: 200} = index is free.
    """
    return http_runner.build_xhr_call(
        "GET", f"{WPM}/v1/Documents/{client_id}/{document_id}/{index}", _h(headers)
    )


# ============================================================================
# Soft-delete helpers — the only delete pattern this skill exposes.
# ============================================================================


def ensure_user_delete_folder(client_id: int | str, parent_folder_id: int | None,
                              existing_folder_listing: list[dict],
                              headers: dict) -> str | None:
    """Return JS to create the 'User to delete' folder under parent_folder_id,
    OR return None if it already exists in `existing_folder_listing`.

    existing_folder_listing: parsed body of `folder_get` on the parent.
    If None is returned: caller scans the listing for the existing locationId.
    If a JS string is returned: caller runs it via the Chrome tool and the
    response IS the new locationId as plain integer text.

    Pinned to index '9999' so it sorts last in the binder.
    """
    for f in existing_folder_listing or []:
        if (f.get("name") or "").strip().lower() == USER_DELETE_FOLDER_NAME.lower() and f.get("type") == "Folder":
            return None
    return create_folder(client_id, USER_DELETE_FOLDER_INDEX, USER_DELETE_FOLDER_NAME, parent_folder_id, headers)


def soft_delete_form(client_id: int | str, parent_folder_location_id: int | str,
                     user_delete_folder_id: int | str, document_id: str,
                     headers: dict) -> str:
    """JS to move a KC form into the firm's 'User to delete' folder.

    USE INSTEAD OF a hard delete. The user reviews the folder in the UI and
    deletes from there when they're confident.

    parent_folder_location_id = the form's CURRENT PARENT FOLDER's INTEGER
    locationId — NOT the form's own GUID. Passing the form GUID returns
    400 "Error converting value '...' to type System.Nullable<Int64>" (BT3 B15).
    Find the parent loc on the form's binder-map / GetBinder / folder_get row.
    Negative pseudo-folders (-4 Unfiled, -1, -2) are VALID sources.

    Caller responsibilities:
      1. Ensure the 'User to delete' folder exists — use `ensure_user_delete_folder`.
      2. After move, call `set_index` so the moved form sorts under '9999.N'.
    """
    loc = str(parent_folder_location_id)
    if not loc.lstrip("-").isdigit():
        raise ValueError(
            f"parent_folder_location_id must be the parent FOLDER's integer locationId, "
            f"got {parent_folder_location_id!r} (a GUID here = the BT3 B15 400). "
            f"Read it from the form's binder-map/folder_get row.")
    items = [{
        "object_type": "KCForms",
        "own_loc": parent_folder_location_id,
        "dest_loc": user_delete_folder_id,
        "object_id": document_id,
    }]
    return move(client_id, items, headers)


def soft_delete_folder(client_id: int | str, folder_location_id: int | str,
                       user_delete_folder_id: int | str, headers: dict) -> str:
    """JS to move a folder (with everything inside it) into 'User to delete'.

    Replaces the historic hard delete — preserves contents so a bad call is
    recoverable without the Recycle Bin. User cleans up from the UI.
    """
    items = [{
        "object_type": "Folder",
        "own_loc": folder_location_id,
        "dest_loc": user_delete_folder_id,
        "object_id": None,
    }]
    return move(client_id, items, headers)


def soft_delete_workpaper(client_id: int | str, workpaper_location_id: int | str,
                          user_delete_folder_id: int | str, document_id: str,
                          headers: dict) -> str:
    """JS to move a Workpaper-type row (PDF/doc) into 'User to delete'.

    For non-KC workpapers. KCForms use `soft_delete_form`. Uploaded files have
    integer-string documentIds (== locationId) and move as objectType
    "Workpaper" — using "LeadSheet"/"KCForms" returns 200 but silently no-ops.
    """
    items = [{
        "object_type": ("LeadSheet" if str(document_id).startswith("leadsheet")
                        else "Report" if str(document_id).startswith("reports/")
                        else "Workpaper" if str(document_id).isdigit()
                        else "KCForms"),
        "own_loc": workpaper_location_id,
        "dest_loc": user_delete_folder_id,
        "object_id": document_id,
    }]
    return move(client_id, items, headers)


# --- AX-26: field-aware index verification --------------------------------------
INDEX_FIELD_BY_TYPE = {
    "Report": "index",
    "KCForms": "index",
    "LeadSheet": "index",
    "Workpaper": "documentIndex",
}


def verify_index(row: dict, object_type: str):
    """Read the DISPLAY index off a WPM row using the type-correct field.

    Reports/KCForms/LeadSheets surface it as `index`; uploaded Workpapers as
    `documentIndex`. Reading the wrong one false-negatives (`documentIndex` is
    ALWAYS null on Report rows — BT3 B6 set an index that was already set).
    NEVER pick the field by hand — call this.
    """
    try:
        field = INDEX_FIELD_BY_TYPE[object_type]
    except KeyError:
        raise ValueError(f"verify_index: unknown object_type {object_type!r} — one of {sorted(INDEX_FIELD_BY_TYPE)}")
    return row.get(field)

# <!-- END -->
