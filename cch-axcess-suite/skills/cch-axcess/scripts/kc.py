"""Knowledge Coach API operations.

Every public function returns a JS string ready for mcp__Claude_in_Chrome__javascript_tool.
The Python side never directly hits CCH — calls go through the user's authenticated
browser tab.

Tab requirements: a knowledgecoach.cchaxcess.com tab for same-origin fetch.
Headers requirements: capture KC headers via scripts.auth_capture (localStorage fast path).

Endpoint specs: references/endpoints/kc_*.json (single source of truth for shapes & gotchas).

Operating pattern: one read via JS → decode + analyze in Python → one batch of writes
back through JS. Do not run field walking or planning inside the JS tool — keep that
in Python so it's scripted and re-runnable.

HARD-DELETE POLICY: this module does NOT expose a delete-form endpoint. See
`scripts/wpm.py` header for the incident note. To remove a form, use
`wpm.soft_delete_form` (moves to "User to delete" folder).
"""
import json
import re
from typing import Any
from . import http_runner

KC = "https://knowledgecoach.cchaxcess.com"


def get_binder(eng_guid: str, headers: dict) -> str:
    """JS for: GET /api/binder/GetBinder/{eng}.

    Response is wrapped: {"result": {..., workpapers: [...], clientGuid, ...}}.
    Parse at parsed["result"]["workpapers"] — top-level "workpapers" does not
    exist (returns undefined/0 forms; confirmed 2026-06-03).
    """
    return http_runner.build_fetch_call("GET", f"{KC}/api/binder/GetBinder/{eng_guid}", headers)


def read_form(eng_guid: str, wp_id: str, headers: dict) -> str:
    """JS for: GET /api/Workpaper/{eng}/{wp}

    Caller must json.loads result.elements and result.collections (JSON-encoded strings).
    """
    return http_runner.build_fetch_call("GET", f"{KC}/api/Workpaper/{eng_guid}/{wp_id}", headers)


def add_forms(eng_guid: str, forms: list[dict], headers: dict) -> str:
    """JS for: POST /api/binder/{eng}  (batch native — body is array).

    forms: list of form objects assembled by scripts.catalog.build_add_forms_body().
    `index` field is silently ignored.

    RESPONSE SHAPE (settled live 2026-06-04): {"result": [...], "statusCode": ...,
    "message": ...}. `result` ECHOES every SUCCESSFULLY-added form, each with its
    server-assigned `workpaperId`/`id`/`wState` — it is NOT failures-only and is
    NOT empty on full success. (The old "result lists only flagged/failed forms;
    successes are silent" claim is FALSE — do not reintroduce it.) Confirm an add
    by matching each planned referenceTag to a result[] entry; that entry's
    workpaperId is the new form's id — success is directly visible.

    Do NOT blind-retry the POST. The reason is NOT that successes are invisible
    (they are visible in result[]); it is that a re-POST adds DUPLICATE forms to
    the binder. Read result[] before retrying; on a genuine retry, dedup-diff
    your planned referenceTags against the ones already echoed/in the binder.
    """
    return http_runner.build_fetch_call("POST", f"{KC}/api/binder/{eng_guid}", headers, forms)


def update_property(eng_guid: str, wp_id: str, payload: dict, headers: dict) -> str:
    """JS for: POST /api/Workpaper/UpdateProperty/{eng}/{wp}  (one field per call).

    payload keys: collectionKey, objectKey, propertyKey, value, valueKey,
                  dataEntryExpression, dataEntryExpressionContextObjectKey.
    For batch writes, use update_properties_sequential — never parallelize.

    Note: HTTP 200 does NOT mean accepted. After every write, check the field
    state. CCH silently rejects unknown valueKeys by setting the field to
    state=2 + valueKey='resetanswer'. Use was_rejected() to detect.
    """
    return http_runner.build_fetch_call(
        "POST", f"{KC}/api/Workpaper/UpdateProperty/{eng_guid}/{wp_id}", headers, payload
    )


def update_properties_sequential(eng_guid: str, wp_id: str, payloads: list[dict], headers: dict) -> str:
    """JS for: N sequential POSTs to UpdateProperty. Returns a COMPACT array of {i, status, attempts, ok, bodyDrop} -- NO response body (the ~88KB UpdateProperty echo stays in-page; AX-36). Parse: results=json.loads(js); failures=[r for r in results if not r['ok']]; drops=[r for r in results if r['bodyDrop']].

    Sequential is REQUIRED — parallel POSTs on the same form drop writes.

    Retry-on-body-drop (AX-33, the "stick" fix): UpdateProperty intermittently
    returns a 200 wrapping {"errors":["A non-empty request body is required."],
    "statusCode":400} — the POST body sporadically isn't received and the write
    silently no-ops. Same field/payload: fails one call, succeeds the next. The
    batch runner retries each write (≤5x, ~200ms) until the body no longer matches
    /non-empty request body|Bad Request/. Demonstrated 100% stick on a repeating
    risk row. This is almost certainly the audit-program step-edit flakiness too.

    VERIFY correctly: these writes are PENDING until kc.submit (per-workpaper
    scoped — never empty wpId). The completion sequence is submit → reload → GET
    (NOT the immediate in-page GET, which reads the uncommitted working copy and
    gives false state-3 positives). Drive the completion loop off the diagnostics
    endpoint (POST /api/Workpaper/refresh then
    GET /api/diagnostics/GetWorkpaperDiagnostics) — that is the oracle; the form's
    own diagnosticCount is stale. (200 ≠ applied — architecture.md.)

    SILENT DROPS ARE THE NORM, NOT THE EXCEPTION: KC silently drops ~30-50% of
    write→submit pairs even with convention-correct payloads and 1-2s pacing
    (SFRC 401k 0100 + batch-2 isolated tests, 2026-07-08). Every write set MUST
    run the loop: write → settle ~1.2s → per-wp submit → verify by re-read after
    reload → retry misses (cap ~3). field-conventions.md §5 3a is binding.
    """
    calls = [
        {
            "method": "POST",
            "url": f"{KC}/api/Workpaper/UpdateProperty/{eng_guid}/{wp_id}",
            "body": p,
        }
        for p in payloads
    ]
    return http_runner.build_compact_batch_xhr(calls, headers, retry_on_body_drop=True)


def submit(eng_guid: str, wp_id: str, headers: dict) -> str:
    """JS for: POST /api/Workpaper/submit scoped to ONE workpaper. wp_id is REQUIRED.

    REQUIRED for persistence. UpdateProperty writes sit in a pending working copy;
    a refresh/reload DISCARDS any unsubmitted writes. (The old "persists without
    submit; submit only refreshes counts" claim is FALSE.) Call submit after a
    batch of writes, then verify after reload (never the immediate in-page GET —
    that reads the uncommitted working copy and gives false state-3 positives).

    NEVER submit with an EMPTY workpaperId. The old "submit all pending in
    binder" form ({workpaperId:""}) silently DISCARDS pending writes on other
    forms instead of committing them (isolated-test confirmed, 2026-07-08).
    Only per-workpaper-scoped submits persist — hence the required wp_id.

    Even scoped correctly, KC silently drops ~30-50% of write→submit pairs
    (payloads convention-correct; sleeps reduce but don't eliminate it). The
    binding pattern is write → settle ~1.2s → submit(this fn) → VERIFY by
    re-read after reload → retry misses (cap ~3). field-conventions.md §5 3a.
    """
    if not wp_id:
        raise ValueError("submit requires a workpaperId — empty wpId ('submit all') "
                         "silently discards pending writes on other forms")
    body = {"binderId": eng_guid, "workpaperId": wp_id}
    return http_runner.build_fetch_call("POST", f"{KC}/api/Workpaper/submit", headers, body)


def program_step_signoff_payload(area_key: str, step_object_key: str, entries=None) -> dict:
    """UpdateProperty payload for a program-step SignOff cell — the IN-FORM (pt=3) sign-off /
    N/A marker. DISTINCT from the document-level WPM sign-off (that one is wpm.remove_signoff).

    The `SignOff` property on a `.{AREA}.ProgramSteps` step object is a JSON-ARRAY-IN-A-STRING
    (captured live, Coop AUD-808, 2026-07-09):
      - sign-off:  [{"userId","userReportName","date","staffId","type":0}]
      - N/A mark:  [{"userId","date","staffId","type":1}]   (note: N/A carries no userReportName)
      - CLEARED :  "[]"                                       (un-sign OR un-N/A — same empty clear)

    entries=None → CLEAR (value "[]"). Passing a list sets it, but a bot rarely should:
    populate_program.js already applies step sign-offs; applying is not this op's purpose.
    area_key e.g. "AP" — the AUD-8xx NUMBER is NOT in the key (.AP.ProgramSteps, never
    .AP808.ProgramSteps; same rule as build_write_payload).
    """
    if entries:
        import json as _json
        value = _json.dumps(entries)
    else:
        value = "[]"
    return {
        "collectionKey": f".{area_key}.ProgramSteps",
        "objectKey": step_object_key,
        "propertyKey": "SignOff",
        "value": value,
        "valueKey": "",
        "dataEntryExpression": "",
        "dataEntryExpressionContextObjectKey": "",
    }


def clear_program_step_signoff(eng_guid: str, wp_id: str, area_key: str,
                               step_object_key: str, headers: dict) -> str:
    """JS for: clear ONE program-step sign-off OR N/A marker (SignOff = "[]") via UpdateProperty.

    The KC-leg un-sign-off — counterpart to wpm.remove_signoff (document level). ONE clear works
    for both a sign-off (type 0) and an N/A mark (type 1). PENDING until kc.submit(eng_guid, wp_id),
    then verify after reload — 200 != applied, and the write-drop converge loop applies
    (field-conventions.md §5 3a). Get step_object_key + area_key from the form read (the step's
    objectKey and its `.{AREA}.ProgramSteps` collectionKey)."""
    return update_property(eng_guid, wp_id,
                           program_step_signoff_payload(area_key, step_object_key), headers)


def toggle_program_step(eng_guid: str, wp_id: str, visible_step_keys: list[str], headers: dict) -> str:
    """JS for: POST /api/Workpaper/UpdateProgramStep with full-state replacement.

    visible_step_keys: every step key (and child step key) that should be visible AFTER the call.
    Empty list -> clears all. To add one, pass current_visible + [new_key]. NO trailing semicolon.
    """
    body = {
        "binderId": eng_guid,
        "workpaperId": wp_id,
        "value": ";".join(visible_step_keys),
    }
    return http_runner.build_fetch_call("POST", f"{KC}/api/Workpaper/UpdateProgramStep", headers, body)


# --- Decoders --------------------------------------------------------------

def decode_form(form_response: dict) -> dict:
    """Parse the JSON-encoded `elements` and `collections` strings inside result.

    Returns {name, ceid, dataBindingKey, titleId, elements: [...], collections: [...]}.

    Accepts the parsed RESPONSE DICT or its raw JSON string (AX-26 — BT3 B8 hit a
    confusing str/dict TypeError here).
    """
    if isinstance(form_response, str):
        form_response = json.loads(form_response)
    if not isinstance(form_response, dict) or "result" not in form_response:
        raise TypeError(
            "decode_form expects the read_form response dict (or its JSON string) "
            f"with a 'result' key — got {type(form_response).__name__}"
            + (f" with keys {sorted(form_response)[:6]}" if isinstance(form_response, dict) else ""))
    r = form_response["result"]
    return {
        "name": r.get("name"),
        "ceid": r.get("ceid"),
        "dataBindingKey": r.get("dataBindingKey"),
        "titleId": r.get("titleId"),
        "elements": json.loads(r.get("elements") or "[]"),
        "collections": json.loads(r.get("collections") or "[]"),
    }


def walk_fields(decoded_form: dict) -> list[dict]:
    """Flatten a decoded form into a list of writable fields.

    Each entry: {collection_path, object_key, type, properties: {key_lower: {
        key_original, value, valueKey, state, isValueDefault, propertyType,
        recommendedAnswer, floatieItemList}}}.
    """
    out = []
    for col in decoded_form.get("collections", []):
        path = col.get("path")
        for obj in col.get("objectList", []) or []:
            if obj.get("deleted") or obj.get("visible") is False:
                continue
            props = {}
            for p in obj.get("renderProperties") or []:
                k = (p.get("key") or "").lower()
                props[k] = {
                    "key_original": p.get("key"),
                    "value": p.get("value"),
                    "valueKey": p.get("valueKey"),
                    "state": p.get("state"),
                    "isValueDefault": p.get("isValueDefault"),
                    "propertyType": p.get("propertyType"),
                    "recommendedAnswer": p.get("recommendedAnswer"),
                    "floatieItemList": p.get("floatieItemList"),
                }
            out.append({
                "collection_path": path,
                "object_key": obj.get("key"),
                "type": obj.get("type"),
                "properties": props,
            })
    return out


# --- Field-state predicates ------------------------------------------------

def is_answered(prop: dict) -> bool:
    """A field is answered iff state==3 AND isValueDefault is not True.

    `prop` is one entry of walk_fields()[i]['properties'][key_lower] OR an
    inventory_form() field record.
    state==2 means "not answered yet"; state==3 + isValueDefault==True means
    the default ships pre-filled — treat as not-yet-answered for QA purposes.

    AX-26 fix: inventory records carry isValueDefault=None (absent), and
    `None is False` is always False — the old check false-negatived EVERY
    inventory record (BT3 B8). Only an EXPLICIT isValueDefault=True demotes
    an answered state.
    """
    if not prop:
        return False
    return prop.get("state") == 3 and prop.get("isValueDefault") is not True


def was_rejected(prop_before: dict, prop_after: dict) -> bool:
    """Detect CCH's silent-rejection pattern after an UpdateProperty.

    CCH returns 200 even when the value/valueKey is unknown. The signature is a
    `reset*` valueKey: `resetanswer` (single-choice, comes back at state 2) or
    `resetcheckbox` (multi-choice, comes back at state 3). Detect on the prefix,
    not the state. Pass the property BEFORE and AFTER (re-read via read_form).

    Most common cause: free text written to a choice field whose option list was
    empty at read time — classify_property now tags these as select/multiselect
    via their sentinel value so build_write_payload skips them instead.
    """
    if not prop_after:
        return True
    return (prop_after.get("valueKey") or "").lower().startswith("reset")


def _list_items(prop: dict) -> list:
    """Pull the option list out of a renderProperty's floatieItemList.

    floatieItemList is ALWAYS an object `{isCustomizable, list}` on live KC
    forms (verified across 1535 fields / 10 default NPO forms) — NEVER a bare
    array. The options live under `.list`. The defensive array branch only
    covers hypothetical older shapes.
    """
    fl = (prop or {}).get("floatieItemList")
    if isinstance(fl, dict):
        return fl.get("list") or []
    if isinstance(fl, list):
        return fl
    return []


def legal_dropdown_values(prop: dict) -> list[dict]:
    """Return the legal {value, valueKey} pairs for a choice property.

    Reads `floatieItemList.list`. Each option item is `{key, value, isCustom}`;
    the item's `key` is what UpdateProperty wants as `valueKey`. Yes/No fields use
    the UPPERCASE convention: write `YES`/`NO` (and `YESNONA-YES/-NO/-NA` for the
    Yes/No/N-A variant). Lowercase `yes` is REJECTED (→ resetanswer); the old
    "lowercase valueKey='yes' is accepted" claim is DISPROVEN. Note many convention-
    driven props ship with an EMPTY floatieItemList — the valueKey is not
    discoverable from the form GET and must come from the field registry. An empty
    list here means the field is free text OR a convention-driven choice, not
    necessarily a dropdown.
    """
    out = []
    for it in _list_items(prop):
        if not isinstance(it, dict):
            continue
        v = it.get("value") or it.get("Value") or it.get("displayValue")
        vk = it.get("key") or it.get("valueKey") or it.get("ValueKey")
        if v is None and vk is None:
            continue
        out.append({"value": v, "valueKey": vk})
    return out


def find_dropdown_options(decoded_form: dict, property_key: str) -> list[dict]:
    """Walk the elements tree to find dropdown options for a property by key.

    Use when `legal_dropdown_values(prop)` returns []. The elements tree
    contains shared option lists referenced by property metadata. Match is
    case-insensitive on the property key.

    Returns [] if no match. The result shape mirrors `legal_dropdown_values`.
    """
    target = (property_key or "").lower()
    out: list[dict] = []

    def _walk(node: Any) -> None:
        if isinstance(node, dict):
            key = (node.get("key") or node.get("propertyKey") or "")
            if isinstance(key, str) and key.lower() == target:
                items = node.get("floatieItemList") or node.get("optionList") or node.get("options") or []
                for it in items:
                    if not isinstance(it, dict):
                        continue
                    v = it.get("value") or it.get("Value") or it.get("displayValue")
                    vk = it.get("valueKey") or it.get("ValueKey") or it.get("key")
                    if v is None and vk is None:
                        continue
                    out.append({"value": v, "valueKey": vk})
            for v in node.values():
                _walk(v)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(decoded_form.get("elements") or [])
    # De-dup while preserving order
    seen = set()
    deduped = []
    for o in out:
        key = (o.get("value"), o.get("valueKey"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(o)
    return deduped


def rendered_binding_keys(decoded_form: dict) -> set:
    """Set of lowercased bindingKeys actually placed in the form's elements layout.

    The `collections` data model carries EVERY property a form could hold,
    including latent ones the rendered layout never shows. AUD-100 is the
    canonical case: each tailoring row has a `Comment` property, but the
    tailoring table renders only QUESTION + ANSWER columns (no Comment cell).
    Writing a latent property succeeds at the API (HTTP 200, state -> 3,
    isValueDefault -> False) yet produces STORED-BUT-INVISIBLE data — no UI box,
    a reviewer never sees it, and it can leak into form exports.

    The `elements` tree IS the layout: every `bindingKey` in it is a control the
    UI renders (subject to hideCondition / object.visible). A writable property
    is only truly fillable if its key matches a rendered bindingKey
    (case-insensitive). bindingKeys are mixed-case in the wild
    (QUESTION/ANSWER/DESCRIPTION but Name/ps) — compare lowercased.

    Returns lowercased keys. An EMPTY set means the layout could not be parsed;
    callers must then NOT filter (fall back to `writable`), never treat
    everything as non-rendered.
    """
    els = decoded_form.get("elements")
    if isinstance(els, str):
        try:
            els = json.loads(els or "[]")
        except Exception:
            els = []
    out: set = set()

    def _walk(n):
        if isinstance(n, dict):
            bk = n.get("bindingKey")
            if isinstance(bk, str) and bk:
                out.add(bk.lower())
            for v in n.values():
                _walk(v)
        elif isinstance(n, list):
            for it in n:
                _walk(it)

    _walk(els or [])
    return out


def addable_empty_grids(decoded_form: dict) -> list:
    """Identify addable GRID tables and the editable column(s) they expose.

    THE GAP this surfaces (KBA-103, validated 2026-05-30): KC renders some
    tables - e.g. the control-deficiency / noncompliance grids - as add-row
    lists whose collection ships with an EMPTY objectList ([]). inventory_form
    walks EXISTING row objects only, so an empty grid contributes ZERO fillable
    fields even though the UI paints a "type to add" cell. The row's shape lives
    in `elements` as a Table's rowTemplate cells, not in `collections`, so the
    parser never sees it. Without this helper the form looks fully blank/done
    when it is not.

    Returns one descriptor per addable Table:
      {table_id, can_insert, editable_columns: [{columnID, bindingKey, type}],
       note}
    `editable_columns` = rowTemplate cells a user can type into (isBlocked
    falsy, no dataEntryExpression, real bindingKey); blocked / computed /
    drilldown cells are excluded. Multiple rowTemplate variants are unioned and
    deduped by bindingKey, so this can slightly OVER-list columns vs the one
    active variant - fine for a warning.

    WARN-ONLY - do NOT treat these as auto-fillable, but a new grid row CAN be
    created over REST: use build_spawn_payload (POST UpdateProperty with the three
    identity keys EMPTY and the collection PATH in dataEntryExpression). The old
    "creation is SignalR-only / NOT REST" claim is FALSE — that misdiagnosis came
    from writes naming a specific non-existent objectKey (which IS a silent HTTP-200
    no-op), not the empty-keys + dataEntryExpression append form. After spawning, the
    new GUID row arrives empty; re-read so inventory_form picks it up, then fill its
    cells by GUID (text direct; choices via resolve_choice_options_from_templates).
    """
    els = decoded_form.get("elements")
    if isinstance(els, str):
        try:
            els = json.loads(els or "[]")
        except Exception:
            els = []

    def _cells(rt):
        # Templates ship cells either directly (rowTemplates[].cells) or nested
        # one level down (rowTemplates[].rows[].cells) - handle both shapes.
        if rt.get("cells"):
            return rt.get("cells")
        out = []
        for row in rt.get("rows") or []:
            out.extend(row.get("cells") or [])
        return out

    grids = []

    def _walk(node):
        if isinstance(node, dict):
            if node.get("type") == "Table":
                editable, seen_bk = [], set()
                for rt in node.get("rowTemplates") or []:
                    if str(rt.get("type") or "") in ("TableHeader", "Header"):
                        continue
                    for cell in _cells(rt):
                        bk = cell.get("bindingKey")
                        if not bk or bk.lower() in seen_bk:
                            continue
                        if cell.get("isBlocked") or cell.get("dataEntryExpression"):
                            continue
                        seen_bk.add(bk.lower())
                        editable.append({"columnID": cell.get("columnID"),
                                         "bindingKey": bk, "type": cell.get("type")})
                if node.get("canInsert") and editable:
                    grids.append({
                        "table_id": node.get("id"),
                        "can_insert": True,
                        "editable_columns": editable,
                        "note": "addable grid - spawn a row over REST via "
                                "build_spawn_payload (empty identity keys + collection "
                                "path in dataEntryExpression), then fill the new GUID "
                                "row's cells by GUID",
                    })
            for v in node.values():
                _walk(v)
        elif isinstance(node, list):
            for it in node:
                _walk(it)

    _walk(els or [])
    return grids


# --- Typed field model (the parser) ----------------------------------------
#
# Field-kind taxonomy, derived from 1535 fields across the 10 default NPO forms
# (AUD-100/101, KBA-101/102/103/105/200/400/502/503). The discriminator is
# `propertyType` (int), refined by `floatieType` + option-list length:
#
#   propertyType  floatieType   list      -> kind         writable
#   0             Radio         small     -> select        yes  (single-choice, e.g. Yes/No)
#   0             CheckBox      big       -> multiselect    yes  ("choose all that apply")
#   0             None          empty     -> text           yes  (free-text answer)
#   0             None          non-empty -> select         yes  (fallback dropdown)
#   1             None          empty     -> text           yes  (comment / description / narrative)
#   2             None          empty     -> label          no   (Question text / Name / HTML display)
#   3             None          empty     -> signoff        yes  (performedby / dates on program steps)
#   5             *             *         -> linked         no   (system keys, IDs, cross-form linked values)
#
# Each form OBJECT (row) typically bundles a label (pt2) + an answer (pt0) +
# a comment (pt1) + system fields (pt5). The object is the natural unit; its
# `visible` flag is how tailoring questions gate dependent rows.

WRITABLE_KINDS = {"text", "select", "multiselect", "signoff"}


def classify_property(prop: dict) -> tuple[str, bool]:
    """Return (kind, writable) for one renderProperty. See taxonomy above."""
    pt = prop.get("propertyType")
    ft = prop.get("floatieType")
    n = len(_list_items(prop))
    if pt == 2:
        return "label", False
    if pt == 5:
        return "linked", False
    if pt == 1:
        return "text", True
    if pt == 3:
        return "signoff", True
    if pt == 0:
        val = str(prop.get("value") or "")
        vk = (prop.get("valueKey") or "").lower()
        if ft == "Radio":
            return "select", True
        if ft == "CheckBox":
            return "multiselect", True
        # Sentinel fallback: a choice field can have an EMPTY option list at read
        # time (options load on gating) — floatieType is null and n==0, but the
        # value/valueKey still mark it as a choice. Writing free text to these is
        # rejected (valueKey -> resetanswer / resetcheckbox). Detect and keep them
        # choices so build_write_payload skips them when options are absent.
        if val == "Choose all that apply." or "checkbox" in vk:
            return "multiselect", True
        if val == "Choose an item" or vk == "defaultanswer":
            return "select", True
        if n > 0:
            return "select", True
        return "text", True
    return f"unknown(pt={pt},ft={ft})", False


def _strip_html(s: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", s or "").strip()


# Bold section-heading style applied to a Question/label cell. A row whose label
# carries this class is a heading; if it ALSO has a writable Answer/description
# cell, that cell is a STRAY box attached to a heading, not a real question
# (AUD-100 "Entity/Engagement Complexity/General Tailoring Considerations").
_HEADING_LABEL_CLASS = "pfxtabletextbold"


def is_heading_object(obj: dict) -> bool:
    """True if this row's Question/label cell is styled as a bold section heading.

    Such rows sometimes render a writable Answer/description cell anyway — a stray
    box that a human reads as a heading, not an input. Detected so the fill engine
    skips it (see _is_fillable / inventory_form['heading_answers']).

    CAUTION: this keys off a CSS class (`PfxTableTextBold`), NOT a semantic
    isHeading flag (objType is the same on heading and normal rows). Validated on
    AUD-100; confirm against new forms before trusting — a normal question that
    happens to bold its label would be a false positive (it stays in `writable`
    and is surfaced in `heading_answers` for exactly this review).
    """
    for p in obj.get("renderProperties") or []:
        if p.get("propertyType") == 2:  # label (Question text / HTML display)
            if _HEADING_LABEL_CLASS in str(p.get("value") or "").lower():
                return True
    return False


_KBA401_DISPLAY_KEYS = {"present", "controlsimplemented", "functioning", "risk"}


def _kba401_class(f: dict):
    """KBA-401 write-targeting class (field-conventions.md §4). KBA-401 only.

    'display'       -> EntityEnv<Comp> matrix columns (present/controlsimplemented/
                       functioning/risk): UpdateProperty SILENTLY REJECTS these (state
                       never commits -> wasted writes + stuck diagnostic). Never write.
    'overall_input' -> EntityEnvOverall{Assessment,Effective} yesno: real INPUT that
                       inventory's rendered gate over-filters (grid cols bind by
                       columnID with empty bindingKey), e.g. the sixth
                       EntityEnvOverallAssessment yesno that clears the last diagnostic.
    """
    cp = f.get("collection_path") or ""
    if ".KBA401.EntityEnvOverall" in cp:
        return "overall_input" if (f.get("key") or "") == "yesno" else None
    if ".KBA401.EntityEnv" in cp and (f.get("key") or "") in _KBA401_DISPLAY_KEYS:
        return "display"
    return None


def _is_fillable(f: dict) -> bool:
    """Whether a writable field is a real, answerable UI control.

    Three gates, each catching a distinct class of phantom (all confirmed live on
    AUD-100):
      (a) rendered    — its column is placed by the `elements` layout. Drops latent
                        COLUMNS the layout never shows (the AUD-100 per-row
                        `.Comment` class: 91 writable, 0 rendered).
      (b) row_visible — object.visible is not False (None = no gate = shown). Drops
                        hidden driver ROWS: AUD-100 `OperatingEffectiveness`
                        (object.visible=False) renders NOWHERE in the UI yet accepts
                        API writes and silently gates the controls-areas multiselect
                        into view. (a) cannot catch this — `elements` describes only
                        columns, never rows, so a hidden row's Answer still maps to
                        the rendered ANSWER column.
      (c) heading_row — not a section-heading row's stray answer box (see
                        is_heading_object).
    """
    _kc = _kba401_class(f)
    if _kc == "display":
        return False  # KBA-401 EntityEnv matrix display column -> UpdateProperty rejects
    if _kc == "overall_input":
        # bypass the (a) rendered over-filter; still honor row_visible + heading gates
        return f.get("row_visible") is not False and not f.get("heading_row")
    return (bool(f.get("rendered"))
            and f.get("row_visible") is not False
            and not f.get("heading_row"))


def _seal_field(rec: dict) -> str:
    """Integrity seal over a field record's write-identity (AX-26).

    build_write_payload verifies it, refusing records whose collection_path /
    object_key / key_original / kind were mutated AFTER inventory_form() built
    them (the BT3 B9 guard hole: a valid record with a hand-edited
    collection_path sailed through the key-presence check)."""
    import hashlib
    basis = "|".join(str(rec.get(k)) for k in ("collection_path", "object_key", "key_original", "kind"))
    return hashlib.sha256(basis.encode()).hexdigest()[:16]


def _field_record(prop: dict, collection_path: str, object_key: str, rendered_keys=None,
                  object_visible=None, heading_row=False) -> dict:
    kind, writable = classify_property(prop)
    rec = {
        "key": (prop.get("key") or "").lower(),
        "key_original": prop.get("key"),
        "kind": kind,
        "writable": writable,
        "state": prop.get("state"),
        "answered": is_answered(prop),
        "is_default": prop.get("isValueDefault"),
        "value": prop.get("value"),
        "valueKey": prop.get("valueKey"),
        "collection_path": collection_path,
        "object_key": object_key,
        "repeating": repeating_row_kind(collection_path, object_key),
    }
    # Layout-aware fillability: only a real UI control if the elements layout
    # renders a cell bound to this key. Empty/None rendered_keys => layout not
    # parsed => do NOT filter (treat as rendered). See rendered_binding_keys().
    rec["rendered"] = (not rendered_keys) or (rec["key"] in rendered_keys)
    # Row-level gates (see _is_fillable). row_visible mirrors object.visible
    # (True/False/None); heading_row tags a stray answer box on a heading row.
    rec["row_visible"] = object_visible
    rec["heading_row"] = heading_row
    rec["fillable"] = _is_fillable(rec) if writable else False
    if kind in ("select", "multiselect"):
        rec["options"] = legal_dropdown_values(prop)
    rec["_seal"] = _seal_field(rec)
    return rec


def inventory_form(decoded_form: dict) -> dict:
    """Typed, low-token inventory of a decoded KC form (see decode_form).

    Returns:
      {name, ceid, dataBindingKey, titleId,
       sections: [{path, rows: [{object_key, type, visible, label, fields[], children[]}]}],
       writable: [field, ...],          # every writable field (escape hatch / diagnostic)
       fillable: [field, ...],          # FILL FROM THIS — writable AND a real UI control
       hidden_writable: [field, ...],   # dropped: rendered column but object.visible=False
       heading_answers: [field, ...],   # dropped: stray answer box on a heading row
       stats: {by_kind, writable, fillable, hidden_writable, heading_answers, answered, fields}}

    A field record carries: key, key_original, kind, writable, state, answered,
    is_default, value, valueKey, collection_path, object_key, repeating, rendered
    (column placed by layout), row_visible (object.visible), heading_row, fillable,
    and (for choices) options=[{value, valueKey}]. Feed a `fillable` record straight
    into build_write_payload(). FILL FROM `fillable`, NOT `writable` — `fillable`
    excludes latent columns, hidden driver rows, and heading boxes (see _is_fillable).
    This is the preferred entry point over walk_fields() — it classifies, so callers
    stop hand-rolling per-form payload logic.

    Nested rows ARE walked: handle_object recurses childObjectList, so rows carry
    children[] and `fillable` includes nested fields at every depth. Do NOT size
    work from len(objectList) on a raw GET — AID-201's TypeofNonauditService is
    17 flat objects but 112 rows / 195 fillable fields across depths 0-3
    (fixture: references/data/fixtures/aid201-form-get.json, verified 2026-07-08).
    """
    sections, writable_flat = [], []
    by_kind: dict[str, int] = {}
    answered = total = 0
    rendered_keys = rendered_binding_keys(decoded_form)
    addable_grids = addable_empty_grids(decoded_form)

    def handle_object(obj: dict, path: str):
        nonlocal answered, total
        if obj.get("deleted"):
            return None
        fields, label_bits = [], []
        ovis = obj.get("visible")
        heading = is_heading_object(obj)
        for p in obj.get("renderProperties") or []:
            rec = _field_record(p, path, obj.get("key"), rendered_keys,
                                object_visible=ovis, heading_row=heading)
            total += 1
            by_kind[rec["kind"]] = by_kind.get(rec["kind"], 0) + 1
            if rec["answered"]:
                answered += 1
            if rec["writable"]:
                writable_flat.append(rec)
            if rec["kind"] == "label" and rec["value"]:
                label_bits.append(_strip_html(str(rec["value"])))
            fields.append(rec)
        return {
            "object_key": obj.get("key"),
            "type": obj.get("type"),
            "visible": obj.get("visible"),
            "label": " ".join(label_bits)[:200],
            "fields": fields,
            "children": [c for c in (handle_object(ch, path)
                         for ch in (obj.get("childObjectList") or [])) if c],
        }

    for col in decoded_form.get("collections", []):
        path = col.get("path")
        rows = [r for r in (handle_object(o, path)
                for o in (col.get("objectList") or [])) if r]
        sections.append({"path": path, "rows": rows})

    return {
        "name": decoded_form.get("name"),
        "ceid": decoded_form.get("ceid"),
        "dataBindingKey": decoded_form.get("dataBindingKey"),
        "titleId": decoded_form.get("titleId"),
        "sections": sections,
        "writable": writable_flat,
        "fillable": [f for f in writable_flat if _is_fillable(f)],
        # Diagnostics — writable+rendered fields the row-level gates DROP. Review
        # these when a UI count disagrees, and to catch heading false positives.
        "hidden_writable": [f for f in writable_flat
                            if f.get("rendered") and f.get("row_visible") is False],
        "heading_answers": [f for f in writable_flat
                            if f.get("rendered") and f.get("heading_row")],
        # WARN: addable grid tables whose collection is empty ([]) - the UI shows
        # a "type to add" cell but there's no row object to fill, so these are
        # NOT counted in `fillable`. A non-empty list here means the form is NOT
        # actually complete even if every existing field is answered. Rows ARE
        # spawnable over REST via build_spawn_payload (see addable_empty_grids
        # docstring) — then fill the new GUID row's cells by GUID.
        "addable_grids": addable_grids,
        "stats": {"by_kind": by_kind, "writable": len(writable_flat),
                  "addable_grids": len(addable_grids),
                  "fillable": sum(1 for f in writable_flat if _is_fillable(f)),
                  "hidden_writable": sum(1 for f in writable_flat
                                         if f.get("rendered") and f.get("row_visible") is False),
                  "heading_answers": sum(1 for f in writable_flat
                                         if f.get("rendered") and f.get("heading_row")),
                  "answered": answered, "fields": total},
    }


def custom_value_key(text: str) -> str:
    """Derive the valueKey KC assigns to a user-entered CUSTOM multiselect value.

    A multiselect with an "add custom value" box (e.g. KBA-400 CtrlConTestWp /
    C09) lets the auditor type a free-text option. The server does NOT accept an
    arbitrary valueKey for it — it derives the key as ``"KEY_" + value`` with the
    text upper-cased and runs of non-alphanumerics collapsed to "_".

    Observed live 2026-05-30 (KBA-400, Other Income C09): typing "Control Memo"
    POSTs valueKey "KEY_CONTROL_MEMO". A REST write that invents its own token
    instead (e.g. "ZZ_CUSTOM_9931" / "ZZQX_CUSTOM_9931") is accepted into the
    working copy — so an immediate GET looks fine — but it is DROPPED on the next
    server refresh/reload and never persists. This was the "custom value didn't
    stick" bug. ALWAYS derive the key with this function, and confirm a custom
    value truly stuck by re-reading AFTER POST /api/Workpaper/refresh (not by the
    GET right after the write — that's the false-positive trap).

    NOTE: the space->underscore + upper-case rule is validated for alphanumeric
    values with spaces; the non-alphanumeric collapse is a generalization. If a
    punctuated custom value fails to persist through a refresh, capture the UI's
    actual POST and adjust here.
    """
    norm = re.sub(r"[^A-Za-z0-9]+", "_", str(text).strip()).strip("_").upper()
    return "KEY_" + norm


def build_write_payload(field: dict, value, valueKey=None, custom=None) -> dict:
    """Assemble an UpdateProperty payload from an inventory_form() field record.

    - text: free text. valueKey is "".
    - signoff: token (initials) goes in `valueKey`, not `value` (free-text write
      is silently ignored). Pass the token as `value` or `valueKey`.
    - select: pass a display `value` (resolved to its valueKey via the field's
      options) OR pass valueKey directly.
    - multiselect: pass `value` as a list of display strings OR a list of
      valueKeys via `valueKey`. Emitted semicolon-joined (full-state replacement;
      confirmed live — the server normalizes any trailing semicolon).
    - multiselect CUSTOM values: pass `custom` as a free-text string or list to
      append "add custom value" entries; each gets valueKey = custom_value_key(c).
      Combine with the standard selection (e.g. valueKey=[<option keys>],
      custom=["Control Memo"]); for a custom-only write pass valueKey=[] so the
      option resolution doesn't try to match the free text. Do NOT pass a custom
      value through `value`/`valueKey` as if it were a real option — it won't be
      in `options`, resolves to "", and (with an invented key) won't persist.

    Raises ValueError if the field isn't writable, a choice can't be resolved, or
    a sentinel-detected choice has no loadable options (skip it, don't free-text).

    GUARD — `field` MUST be an inventory record, never a hand-assembled key. Passing
    a bare collectionKey string (or a dict missing the inventory fields) is the B13
    antipattern: it lets a caller invent a collectionKey by hand, the server accepts
    it with a silent HTTP 200 (the silent-200 class), and the write never lands. The
    only safe source of `field` is `inventory_form(decode_form(read_form(...)))`. This
    function refuses anything else at the gate (signature break is intended — the
    skill owns every caller).

    AREA SHORT NAME, not the form number: a program-step collection path is
    `.CASH.ProgramSteps`, NEVER `.CASH801.ProgramSteps`. The AUD-8xx form number does
    not appear in the collection key. Because `field.collection_path` comes verbatim
    from inventory_form(), routing every write through this builder makes that mistake
    structurally impossible too.
    """
    if not isinstance(field, dict):
        raise ValueError(
            "build_write_payload requires an inventory-field RECORD, not a raw "
            f"{type(field).__name__} (e.g. a hand-assembled collectionKey string). "
            "Get the field from inventory_form(decode_form(read_form(...))) — never "
            "hand-assemble a collectionKey (silent-200 antipattern, B13)."
        )
    _required = ("kind", "collection_path", "object_key", "key_original")
    _missing = [k for k in _required if k not in field]
    if _missing:
        raise ValueError(
            f"build_write_payload was handed a dict missing inventory fields "
            f"{_missing} — this looks like a hand-assembled payload, not an "
            "inventory_form() field record. Source fields from "
            "inventory_form(decode_form(read_form(...))); do NOT hand-assemble a "
            "collectionKey (silent-200 antipattern, B13)."
        )
    if field.get("_seal") != _seal_field(field):
        raise ValueError(
            f"field {field.get('key_original')!r} fails the integrity seal — its "
            "collection_path/object_key/key/kind were modified after inventory_form() "
            "built it (or the record was hand-assembled with a fake seal). Re-source "
            "the record from inventory_form(); never edit write-identity fields "
            "(silent-200 antipattern, B13/B9-guard-hole).")
    kind = field["kind"]
    if kind not in WRITABLE_KINDS:
        raise ValueError(f"field {field.get('key_original')!r} is {kind} — not writable")

    if kind == "signoff":
        # Sign-off (pt=3, e.g. `performedby`) stores its token in valueKey, NOT
        # value. A free-text write (valueKey="") is silently ignored — state
        # stays 0. Pass the initials as `value` or `valueKey`; both get the token.
        token = valueKey if valueKey not in (None, "") else value
        token = "" if token is None else str(token)
        return {
            "collectionKey": field["collection_path"],
            "objectKey": field["object_key"],
            "propertyKey": field["key_original"],
            "value": token,
            "valueKey": token,
            "dataEntryExpression": "",
            "dataEntryExpressionContextObjectKey": "",
        }

    if kind in ("select", "multiselect") and not field.get("options"):
        raise ValueError(
            f"choice field {field.get('key_original')!r} has no loadable options "
            f"(sentinel-detected; option list empty at read time) — SKIP it or "
            f"resolve options first. Do NOT write free text: it is reset-rejected."
        )

    if kind == "multiselect":
        opts = field.get("options", [])
        if valueKey is not None:
            vks = valueKey if isinstance(valueKey, (list, tuple)) else [valueKey]
            by_vk = {o["valueKey"]: o["value"] for o in opts}
            vals = [by_vk.get(vk, "") for vk in vks]
        else:
            chosen = value if isinstance(value, (list, tuple)) else [value]
            by_v = {(o["value"] or "").lower(): o for o in opts}
            picked = [by_v.get(str(c).lower()) for c in chosen]
            if any(p is None for p in picked):
                raise ValueError(f"value(s) {value!r} not all in options for "
                                 f"{field.get('key_original')!r}")
            vals = [p["value"] for p in picked]
            vks = [p["valueKey"] for p in picked]
        if custom:
            customs = custom if isinstance(custom, (list, tuple)) else [custom]
            for c in customs:
                c = str(c).strip()
                if not c:
                    continue
                vals.append(c)
                vks.append(custom_value_key(c))
        return {
            "collectionKey": field["collection_path"],
            "objectKey": field["object_key"],
            "propertyKey": field["key_original"],
            "value": ";".join(vals),
            "valueKey": ";".join(vks),
            "dataEntryExpression": "",
            "dataEntryExpressionContextObjectKey": "",
        }

    if kind == "select" and valueKey is None:
        match = next((o for o in field.get("options", [])
                      if (o["value"] or "").lower() == str(value).lower()), None)
        if not match:
            raise ValueError(f"value {value!r} not in options for "
                             f"{field.get('key_original')!r}: "
                             f"{[o['value'] for o in field.get('options', [])]}")
        valueKey, value = match["valueKey"], match["value"]
    elif kind == "select" and valueKey is not None:
        # valueKey supplied directly — backfill the display `value` from the
        # matching option (mirrors the multiselect branch). A select POST with
        # value=None serializes to value:null, which the server reads as a reset
        # → resetanswer. Find the option whose valueKey matches and adopt its
        # display value; if no option matches, leave `value` as-is.
        match = next((o for o in field.get("options", [])
                      if o.get("valueKey") == valueKey), None)
        if match is not None:
            value = match["value"]

    return {
        "collectionKey": field["collection_path"],
        "objectKey": field["object_key"],
        "propertyKey": field["key_original"],
        "value": value,
        "valueKey": valueKey if valueKey is not None else "",
        "dataEntryExpression": "",
        "dataEntryExpressionContextObjectKey": "",
    }


# --- Addable repeating-list rows ------------------------------------------
#
# KC renders many list/narrative answers as "Type here to add new item" rows.
# Two shapes (both verified live on KBA-200):
#
#   TEMPLATE list  - ships pre-seeded with ONE empty object keyed `{collKey}-1`
#                    (hyphen + digits, base == the collection key). Single-cell:
#                    a `description`/`Description` (pt1 text) OR a `chooseitem`
#                    (pt0 select). FILL the existing `-1` directly via
#                    UpdateProperty - it commits immediately and reads back clean.
#   GRID list      - ships EMPTY (objectList []). CREATE a GUID-keyed row with
#                    build_spawn_payload (see below), then fill its cells
#                    (`text1..textN`, pt0) by the returned GUID objectKey.
#
# ROW CREATION IS REST (corrected 2026-05-30, was previously believed SignalR-only).
# To append a row: POST UpdateProperty with the three identity keys EMPTY and the
# collection PATH in `dataEntryExpression` (build_spawn_payload). The server
# creates a fresh GUID row and lands `value` in its first writable cell. The old
# "silent no-op" finding was a misdiagnosis - those writes named a specific
# NON-EXISTENT objectKey instead of the empty-keys + dataEntryExpression append
# form. After spawning, re-read the form to get the GUID, then fill remaining
# columns with normal build_write_payload writes keyed by that GUID.
#
# STOPPING RULE: each spawn creates exactly one row (plus the UI's perpetual
# trailing add-box, which has NO object in `collections` and so is never picked
# up by inventory_form) - so a fill loop must be driven by a known target count,
# NOT by "until no empty add-row remains" (that never terminates).


def build_spawn_payload(collection_path: str, value: str = "", value_key: str = "") -> dict:
    """Assemble an UpdateProperty payload that CREATES (appends) a new row in an
    addable repeating list / grid - the operation the empty-grid blocker needed.

    Confirmed live (KBA-200, 2026-05-30, ThirdPartyInfo200 + BankingEntities200):
    posting UpdateProperty with collectionKey/objectKey/propertyKey all EMPTY and
    the collection PATH in `dataEntryExpression` makes the server create a fresh
    GUID-keyed row and land `value` in its first writable cell -

        {collectionKey:"", objectKey:"", propertyKey:"",
         value:<first-cell text>, valueKey:<first-cell option key, for a choice>,
         dataEntryExpression:".KBA200.ThirdPartyInfo200",
         dataEntryExpressionContextObjectKey:""}

    Returns HTTP 200 {result, statusCode}. Re-read the form to pick up the new
    row's GUID, then fill remaining columns via build_write_payload keyed by it.

    `collection_path`  the table's collection path - the `path` of an
                       addable_empty_grids() entry (e.g. ".KBA200.ThirdPartyInfo200").
    `value`            seeds the first text cell.
    `value_key`        use instead of `value` for a choice-first list (option key).

    One call == one row; call N times for N rows (see STOPPING RULE above).

    GRID double-occurrence (KBA-103): a spawned grid row can appear in BOTH a
    semantic-keyed data collection (`...UserEntry`) and a generic `text1..textN`
    display mirror. Pass the DATA collection path here and verify the spawned GUID
    against that occurrence, not the mirror (the mirror reads 0/default).
    """
    return {
        "collectionKey": "",
        "objectKey": "",
        "propertyKey": "",
        "value": "" if value is None else str(value),
        "valueKey": "" if value_key is None else str(value_key),
        "dataEntryExpression": collection_path,
        "dataEntryExpressionContextObjectKey": "",
    }

_GUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def repeating_row_kind(collection_path: str, object_key: str):
    """Classify an object as an EXISTING addable repeating-list row.

    Returns:
      "template" -> pre-seeded narrative/selector row keyed `{collKey}-{N}`
                    (hyphen + digits, base == the collection's key). Distinct
                    from fixed question rows that use an underscore (`_N`).
      "grid"     -> GUID-keyed row created in a multi-column grid list.
      None       -> not a repeating row (fixed `_N` rows, single objects).

    `collection_path` is the field record's collection_path (e.g.
    ".KBA200.FinancialStatementUsers"); the collection key is its last segment.
    Identifies EXISTING rows only — to CREATE a new row use build_spawn_payload
    (spawn IS REST), then re-read to pick up its GUID and fill by GUID.
    """
    if not object_key:
        return None
    coll_key = (collection_path or "").rsplit(".", 1)[-1]
    if coll_key and re.match(rf"^{re.escape(coll_key)}-\d+$", object_key):
        return "template"
    if _GUID_RE.match(object_key):
        return "grid"
    return None


def resolve_choice_options_from_templates(decoded_form: dict, property_key: str) -> list:
    """Resolve options for a repeating-row choice (e.g. `chooseitem`) whose
    inline `floatieItemList` is empty at read time.

    For repeating rows the options are NOT on the renderProperty; they live in
    the elements `Table` rowTemplate cells, keyed by column role (`bindingKey`)
    rather than the property key. Matches the cell whose bindingKey equals
    `property_key` (case-insensitive) and returns its options as
    [{value, valueKey}] - same shape as legal_dropdown_values().

    Example (KBA-200 change-comparison selectors): the `chooseitem` rows resolve
    to N/A (`naComparedToPY`), Similar to Previous Year (`similarComparedToPY`),
    Significant change from Previous year (`significantchangeComparedToPY`).

    NOTE: multi-column GRID select cells carry an empty cell bindingKey and so
    are NOT resolved here (their options key off columnID); resolve those from
    the live renderProperty once the row's options have loaded.
    """
    target = (property_key or "").lower()
    out: list = []

    def _opts(fl):
        items = fl.get("list") if isinstance(fl, dict) else fl
        for it in items or []:
            if not isinstance(it, dict):
                continue
            v = it.get("value") or it.get("Value") or it.get("displayValue")
            vk = it.get("key") or it.get("valueKey") or it.get("ValueKey")
            if v is None and vk is None:
                continue
            out.append({"value": v, "valueKey": vk})

    def _walk(node):
        if isinstance(node, dict):
            if node.get("type") == "Table":
                for rt in node.get("rowTemplates") or []:
                    for row in rt.get("rows") or []:
                        for cell in row.get("cells") or []:
                            if (cell.get("bindingKey") or "").lower() == target:
                                fl = cell.get("floatieItemList") or cell.get("floatieList")
                                if fl:
                                    _opts(fl)
            for v in node.values():
                _walk(v)
        elif isinstance(node, list):
            for it in node:
                _walk(it)

    _walk(decoded_form.get("elements") or [])
    seen, deduped = set(), []
    for o in out:
        k = (o.get("value"), o.get("valueKey"))
        if k in seen:
            continue
        seen.add(k)
        deduped.append(o)
    return deduped


def enrich_repeating_choice(field: dict, decoded_form: dict) -> dict:
    """Attach resolved options to a repeating-row choice field that has none.

    A repeating `chooseitem` reads as a select with an empty option list
    (sentinel "Choose an item"/`defaultanswer`). build_write_payload would
    refuse it. Call this first to pull options from the rowTemplates, then the
    field feeds build_write_payload normally. Mutates and returns `field`.
    """
    if field.get("kind") in ("select", "multiselect") and not field.get("options"):
        opts = resolve_choice_options_from_templates(decoded_form, field.get("key_original"))
        if opts:
            field["options"] = opts
    return field


def build_reset_payload(field: dict) -> dict:
    """REMOVED 2026-05-30 — the token reset is FORBIDDEN. Do not reintroduce.

    This used to emit a reset payload (select -> valueKey "resetanswer",
    multiselect -> "resetcheckbox", text/signoff -> ""). The choice-token reset
    is LOSSY in a way that corrupts the form's completeness state:

      Resetting a touched required toggle blanks it (isValueDefault -> true) but
      leaves `state == 3`. KC's diagnostic engine keys "Question Unanswered" off
      `state`, so the blanked field NEVER re-fires its diagnostic and the
      right-side counter never returns. The field reads COMPLETE while empty.
      Confirmed live 2026-05-30 (KBA-400): a full 96-radio token-reset left the
      form blank with ZERO diagnostics, and **a Submit did NOT reconcile it** —
      KC still reported the empty form as ready. A reviewer would see a clean,
      done form over blank answers. That is a peer-review / QC defect, so the
      capability is scrapped rather than shipped.

    KC required toggles are write-once by design — fill them, don't un-fill them.
    To genuinely clear a section, remove + re-add the form (KBA-100 area toggles)
    so KC rebuilds it from scratch; do not blank fields in place via the API.
    (`was_rejected()` still reads a `reset*` valueKey as not-answered — that is
    read-side rejection DETECTION and is unaffected by this removal.)
    """
    raise NotImplementedError(
        "build_reset_payload is forbidden: the resetanswer/resetcheckbox token "
        "leaves state==3, so a blanked required field falsely reads COMPLETE and "
        "Submit does not reconcile it (peer-review defect, confirmed live "
        "2026-05-30). KC toggles are write-once; do not blank them via the API."
    )


def existing_repeating_rows(inventory: dict, collection_path: str) -> list:
    """Enumerate the EXISTING fillable rows of one addable repeating list.

    Returns a list of {object_key, repeating, answer_field, empty} in document
    order, where `answer_field` is the row's primary writable field record
    (the single-cell `description`/`Description`/`chooseitem`, or the first
    writable text column of a grid row) and `empty` is True when that field is
    still at its default. Feed `answer_field` to build_write_payload (after
    enrich_repeating_choice for choices) to fill the row.

    To fill a list with N values: map values onto these rows in order. Values
    beyond the number of existing rows are OVERFLOW - they need a new row: spawn
    it over REST with build_spawn_payload, then fill it by the returned GUID
    (re-read the form to pick up the GUID first). Never write an empty
    value to a trailing template (a blank write to a choice is reset-rejected,
    and a blank text write just clears it); leave unused rows untouched.
    """
    rows = []
    for sec in inventory.get("sections", []):
        if sec.get("path") != collection_path:
            continue
        for row in sec.get("rows", []):
            ok = row.get("object_key")
            kind = repeating_row_kind(collection_path, ok)
            if not kind:
                continue
            answer = None
            for f in row.get("fields", []):
                if not f.get("writable"):
                    continue
                if f["kind"] in ("text", "select", "multiselect"):
                    answer = f
                    break
            rows.append({
                "object_key": ok,
                "repeating": kind,
                "answer_field": answer,
                "empty": bool(answer and answer.get("is_default")),
            })
    return rows


def bulk_capture_forms_js(eng_guid: str, wp_ids: list, download_filename: str, concurrency: int = 5) -> str:
    """JS to fetch N forms in batches, bundle them, and trigger a browser
    download. The Python side never sees the raw form JSON — too large.

    wp_ids: list of {"name": str, "wpId": str}.
    download_filename: e.g. 'kymera-2025-forms-bundle.json'.
    concurrency: 5 has been observed safe; lower if the server starts rate-limiting.

    Stashes the bundle in `window.__bundle` before triggering the download so
    a blocked-download prompt can be retried without re-fetching.
    """
    import json as _json
    return (
        '(async () => {\n  const eng = ' + _json.dumps(eng_guid)
        + ';\n  const wpIds = ' + _json.dumps(wp_ids)
        + ';\n  const N = ' + str(int(concurrency))
        + ";\n  const hdrs = {\n    'Authorization': 'Bearer ' + localStorage.getItem('kc.accessToken'),\n    'IdToken':       localStorage.getItem('kc.idToken'),\n    'Accept':        'application/json'\n  };\n  const fetchOne = async (f) => {\n    try {\n      const r = await fetch(`https://knowledgecoach.cchaxcess.com/api/Workpaper/${eng}/${f.wpId}`, {headers: hdrs});\n      return {name: f.name, wpId: f.wpId, status: r.status, data: r.status === 200 ? await r.json() : await r.text()};\n    } catch (e) { return {name: f.name, wpId: f.wpId, error: String(e)}; }\n  };\n  const results = [];\n  for (let i = 0; i < wpIds.length; i += N) {\n    results.push(...await Promise.all(wpIds.slice(i, i+N).map(fetchOne)));\n  }\n  const bundle = {capturedAt: new Date().toISOString(), engagementGuid: eng, forms: results};\n  window.__bundle = bundle;\n  const blob = new Blob([JSON.stringify(bundle, null, 2)], {type: 'application/json'});\n  const a = document.createElement('a');\n  a.href = URL.createObjectURL(blob);\n  a.download = "
        + _json.dumps(download_filename)
        + ';\n  document.body.appendChild(a); a.click(); document.body.removeChild(a);\n  return `bundled ${results.length} forms`;\n})()'
    )


# --- Per-area risk sub-grids (IR/CR/RMM / approach) ------------------------
#
# KBA-502 is a ROLLUP (one writable Comment); it is NOT where IR/CR/RMM/approach
# live. The per-area assertion/risk grid (selected/ir/cr/rmm/PlannedAuditApproach)
# is written on the AUD-8xx program at `.{AREA}.RelevantAssertion` — see the field
# registry (references/config/field-conventions.md) for the props, valueKeys, and
# the INPUT-vs-DISPLAY collection-targeting rules. Use build_write_payload against
# the inventory_form records for that collection.
# <!-- END -->
