"""TB grouping operations (financialprep-api).

Each engagement has one or more "financial lists" (a.k.a. grouping lists).
Each list contains "financial groups" (the actual TB groupings - codes like
1000 Cash, 1400 Prepaid). Each account is assigned to exactly ONE group per
list (no unassigned state - the TB tab autosaves every reassignment).

Hierarchy:
    Engagement
      +-- financialList (one or many, one marked isDefault)
            +-- financialGroup (many)
                  +-- account assignment (1 per (account, list))

Field naming quirks:
- The financialList index field is `number` (not `index` like Funds use).
- Groups carry both accountTypeId (1..5) and accountTypeClassificationId
  (1..10). The classification is the subdivision of the type. The
  abbreviation (`A`, `L`, `E`, `R`, `X`) is what truly drives system
  behavior; UI shows the name, but the server consumes the int ID derived
  from that name. See references/config/group_account_types.json.
- "Unassign" doesn't exist on the TB grouping side. Every account is in
  some group at all times for a given list. To "remove" an account from a
  custom group, reassign it back to whatever Global group the server picks.

Auth/transport: same engagement-side captured headers as WPM / workbench-api.
Cross-origin from engagement.cchaxcess.com -> financialprep-api.cchaxcess.com
must use XHR (build_xhr_call). build_xhr_call auto-adds Content-Type on
body writes.

Endpoint specs: references/endpoints/groups_*.json.
"""
import json
from . import http_runner

FP = "https://financialprep-api.cchaxcess.com"


# --- LIST (GET) -----------------------------------------------------------

def list_financial_lists(client_id: int, headers: dict) -> str:
    """JS for: GET /v1.0/financialList/{clientId}

    Returns {financialLists: [{id, number, name, isDefault, ...}]}.
    The `id` is the integer financialListId used everywhere else.
    `number` is the user-facing index (FS, 03, etc.).
    """
    return http_runner.build_xhr_call("GET", f"{FP}/v1.0/financialList/{client_id}", headers)


def list_group_account_types(client_id: int, headers: dict) -> str:
    """JS for: GET /v1.0/FinancialGroup/{clientId}/groupaccounttypes

    Returns array of accountType objects, each carrying a nested
    `classifications` array. Use this to resolve accountTypeId +
    accountTypeClassificationId for create/update_financial_group, or read
    from the bundled static map at references/config/group_account_types.json
    (same data, no network call).
    """
    return http_runner.build_xhr_call("GET", f"{FP}/v1.0/FinancialGroup/{client_id}/groupaccounttypes", headers)


def list_financial_groups(client_id: int, financial_list_id: int, headers: dict) -> str:
    """JS for: GET /v1.0/FinancialGroup/{clientId}/{financialListId}

    Returns the groups for a single list with their codes, names, type
    metadata, and current account counts.

    RESPONSE SHAPE: the body is a RAW JSON ARRAY of group objects — there is no
    {financialGroups:[...]} wrapper. After http_runner.parse_result, `body` is
    the list itself (use `body` / `len(body)`, not `body["financialGroups"]`).
    """
    return http_runner.build_xhr_call("GET", f"{FP}/v1.0/FinancialGroup/{client_id}/{financial_list_id}", headers)


def get_trialbalance_grouped(client_id: int, financial_list_id: int, period_id: int, headers: dict) -> str:
    """JS for: GET /v1.0/financialTrialBalance/{clientId}/{financialListId}/trialbalance/{periodId}

    Returns the TB rows annotated with each account's current group in the
    given list. Used as the read step before a PATCH (assign_account_to_group).

    ⚠️ PAGINATION: this endpoint returns only the FIRST 50 accounts unless
    ?skip&take are supplied (the body's `accountCount` is the true total). For any
    engagement with >50 TB accounts this single call SILENTLY MISSES the rest. For
    bulk-assign / full reads use get_trialbalance_grouped_all() instead, which loops
    all pages. This function is kept for small/known-small reads only.

    Row schema (account.group / account.financialSubGroup — NOT account.subGroup,
    which is always null / account.fund / periods.current.*) and the API's
    CREDITS-POSITIVE sign convention: endpoints/fp_trialbalance.json.
    """
    return http_runner.build_xhr_call("GET", f"{FP}/v1.0/financialTrialBalance/{client_id}/{financial_list_id}/trialbalance/{period_id}", headers)


def get_trialbalance_grouped_all(client_id: int, financial_list_id: int, period_id: int, headers: dict, page_size: int = 300) -> str:
    """JS for: paginated read of the grouped TB — loops ?skip&take until all rows are in.

    The base endpoint caps at 50 accounts per call; this loops `skip` in `page_size`
    steps until a short page is returned (or `accountCount` is reached) and merges
    the pages. Resolution of the row array is shape-agnostic: it takes the body if
    it is an array, else body.accounts / body.balances / body.trialBalance, else the
    first array-valued property — so it survives the exact key name not being known.

    Returns a single JS Promise resolving to JSON:
        {status, accountCount, count, balances:[...]}   (count == merged length)
    """
    base = f"{FP}/v1.0/financialTrialBalance/{client_id}/{financial_list_id}/trialbalance/{period_id}"
    import json as _json
    base_js = _json.dumps(base)
    from . import http_runner as _hr
    hdr_js = _hr._headers_js(headers)
    return (
        "(() => new Promise(async (resolve) => {\n"
        "  const base = " + base_js + ";\n"
        "  const h = " + hdr_js + ";\n"
        "  const PAGE = " + str(int(page_size)) + ";\n"
        "  const getPage = (skip) => new Promise((res) => {\n"
        "    const x = new XMLHttpRequest();\n"
        "    x.open('GET', base + '?skip=' + skip + '&take=' + PAGE, true);\n"
        "    for (const k in h) x.setRequestHeader(k, h[k]);\n"
        "    x.onreadystatechange = () => { if (x.readyState === 4) res({status: x.status, text: x.responseText}); };\n"
        "    x.send(null);\n"
        "  });\n"
        "  let skip = 0, all = [], accountCount = null, status = null;\n"
        "  while (true) {\n"
        "    const r = await getPage(skip); status = r.status;\n"
        "    let body; try { body = JSON.parse(r.text); } catch (e) {\n"
        "      resolve(JSON.stringify({status, error: 'parse', text: (r.text||'').substring(0,200)})); return; }\n"
        "    let arr = Array.isArray(body) ? body\n"
        "      : (body.accounts || body.balances || body.trialBalance || (Object.values(body).find(v => Array.isArray(v)) || []));\n"
        "    if (body && !Array.isArray(body) && body.accountCount != null) accountCount = body.accountCount;\n"
        "    all = all.concat(arr);\n"
        "    if (!arr.length || arr.length < PAGE) break;\n"
        "    if (accountCount != null && all.length >= accountCount) break;\n"
        "    skip += PAGE; if (skip > 100000) break;\n"
        "  }\n"
        "  resolve(JSON.stringify({status, accountCount, count: all.length, balances: all}));\n"
        "}))()"
    )


# --- CREATE / UPDATE (POST) -----------------------------------------------

def create_financial_list(client_id: int, number: str, name: str, headers: dict) -> str:
    """JS for: POST /v1.0/financialList

    Creates a new grouping list. The server returns the new id directly in the
    response body as {"id": <int>} (no re-GET needed).
    Body uses `number` for the index field, not `index`.

    ⚠️ `number` must be DIGITS ONLY — non-numeric (e.g. 'ZZ') -> 400
    "Invalid characters. Only Number are accepted." Use '01', '09', etc.

    Body shape:
        {"number": str (digits), "name": str, "engagementId": int}
    """
    body = {"number": number, "name": name, "engagementId": client_id}
    return http_runner.build_xhr_call("POST", f"{FP}/v1.0/financialList", headers, body)


def create_financial_group(client_id: int, financial_list_id: int, index: str, name: str,
                           account_type_id: int, classification_id: int, headers: dict,
                           anchor_group_id: int = 0) -> str:
    """JS for: POST /v1.0/FinancialGroup — create ONE group (insert-after anchor).

    Creates a new group inside a financialList. Use list_group_account_types
    or config/group_account_types.json to resolve type+classification IDs.

    ANCHOR RULE:
      `financialGroupId` on this POST is an INSERT-AFTER ANCHOR, not a flag.
        - anchor_group_id = 0  -> ONLY valid for the first group into an EMPTY list.
        - anchor_group_id > 0  -> the PRECEDING group's financialGroupId; the new
                                  group is inserted after it.
      Sending 0 into a NON-empty list -> HTTP 400 "Invalid financial group."
      To create several groups you must CHAIN: create one, read the returned
      `financialGroupId`, pass it as `anchor_group_id` for the next create.
      build_chain_create_groups_js() does the whole chain in one browser call.

    Display order: groups render LIFO (each insert lands at top) until
    reordered — see build_reorder_groups_js() to sort a list ascending.

    Group NAME is the unique key (NOT index): a duplicate name -> HTTP 400
    "Group name exists."

    Returns (response body): {financialGroupId, financialGroupGuid}.

    Body shape:
        {engagementId, consolidatedEngagementId:null, index, name,
         accountTypeId, accountTypeClassificationId, positionId:0,
         financialListId, financialGroupId: <anchor_group_id>}
    """
    body = {
        "engagementId": client_id,
        "consolidatedEngagementId": None,
        "index": index,
        "name": name,
        "accountTypeId": account_type_id,
        "accountTypeClassificationId": classification_id,
        "positionId": 0,
        "financialListId": financial_list_id,
        "financialGroupId": anchor_group_id,
    }
    return http_runner.build_xhr_call("POST", f"{FP}/v1.0/FinancialGroup", headers, body)


def update_financial_group(client_id: int, financial_list_id: int, financial_group_id: int,
                           index: str, name: str, account_type_id: int, classification_id: int,
                           anchor_group_id: int, headers: dict, position: int = 1) -> str:
    """JS for: PUT /v1.0/FinancialGroup — edit (rename / reclassify / re-index) an EXISTING group.

    Editing a group is a **PUT**, NOT a POST. (A POST with a non-zero
    financialGroupId does NOT update — it CREATES a duplicate group anchored
    after that id.)

    The PUT requires, beyond the edited fields:
      - the full account-type trio: `accountType` STRING (resolved here from
        account_type_id) + accountTypeId + accountTypeClassificationId; and
      - a POSITION anchor: positionFinancialGroupId + positionId. Omitting it ->
        400 "Invalid group location."

    To edit a group WITHOUT moving it: pass `anchor_group_id` = the id of the
    group currently directly ABOVE it, with position=1 (after). Read
    list_financial_groups first to find that current predecessor. (If the target
    is already first, anchor on the group below it with position=0.)

    `index` and `name` must each stay unique within the list (duplicate ->
    400 "Index number exists" / "Group name exists").
    """
    body = {
        "engagementId": client_id,
        "consolidatedEngagementId": None,
        "financialGroupId": financial_group_id,
        "index": index,
        "name": name,
        "accountType": _ACCOUNT_TYPE_ID_TO_NAME.get(account_type_id),
        "accountTypeId": account_type_id,
        "accountTypeClassificationId": classification_id,
        "financialListId": financial_list_id,
        "positionFinancialGroupId": anchor_group_id,
        "positionId": position,
    }
    return http_runner.build_xhr_call("PUT", f"{FP}/v1.0/FinancialGroup", headers, body)


# --- ASSIGN ACCOUNT TO GROUP (PATCH) --------------------------------------

def assign_account_to_group(client_id: int, account_row: dict, target_group: dict, headers: dict) -> str:
    """JS for: PATCH /v1.0/financialTrialBalance/{clientId}/balances/{accountId}

    Reassigns one account to a different group within one financialList.
    There is no separate unassign - every account is always in SOME group;
    reassigning to a different group is the only mutation.

    account_row: the row as returned by get_trialbalance_grouped (the row
        carries id, engagementId, accountName, accountNumber, financialListId,
        periodId, and the current group). Pass it through largely unchanged.
    target_group: the group object to swap in. Minimum shape:
        {financialGroupId, index, name, classification, financialGroupType,
         classificationGuid, type: {accountTypeId, name, acctType, ...}}
        For groups returned by list_financial_groups, this is the full row.
        For known groups, can be assembled by hand.

    Body shape:
        {...account_row, group: target_group}

    Note: the captured wire body carries ~30 fields. The server may accept
    fewer; this function does NOT trim - it preserves the input row + swaps
    the group. If you need to build the body from minimal inputs, use
    build_patch_body() below.

    The new group reads back at `row.account.group`, NOT top-level `row.group`.
    To verify an assignment, re-GET the grouped TB and check
    `row.account.group.financialGroupId`.

    GUARDRAIL: `financialListId` MUST be present on the body — omitting it
    returns 400 ("FinancialListId ... request data invalid"), it does NOT
    silently fall back to the default list. Regroups are per-list independent,
    so the only real risk is passing the WRONG list id. Before a bulk regroup,
    resolve the target list and assert it is not isDefault unless intended.
    For many accounts use build_bulk_assign_js() (one browser call, N PATCHes).
    """
    body = {**account_row, "group": target_group}
    account_id = account_row.get("id") or account_row.get("accountId")
    return http_runner.build_xhr_call(
        "PATCH", f"{FP}/v1.0/financialTrialBalance/{client_id}/balances/{account_id}", headers, body
    )


def build_patch_body(account_id: int, client_id: int, financial_list_id: int, period_id: int,
                     account_name: str, account_number: str, target_group: dict) -> dict:
    """Assemble the PATCH body for assign_account_to_group.

    `target_group` MUST be the FULL group row from a FRESH
    list_financial_groups GET (window.__groups) — including the UUID `id` and
    `engagementFinancialGroupMapId`. The endpoint 400s "Financial Group does
    not exist" without them, and group UUIDs CHURN on TB import — never cache group
    objects across a TB import; re-GET immediately before any bulk assignment.
    """
    required = {"id", "engagementFinancialGroupMapId"}
    missing = required - set(target_group or {})
    if missing:
        raise ValueError(
            f"target_group is missing {sorted(missing)} — pass the FULL group row from a "
            f"FRESH list_financial_groups GET (group UUIDs churn on TB import; the minimal "
            f"body 400s 'Financial Group does not exist').")
    return {
        "id": account_id,
        "engagementId": client_id,
        "consolidatedEngagementId": None,
        "accountName": account_name,
        "accountNumber": account_number,
        "financialListId": financial_list_id,
        "periodId": str(period_id),
        "isTemplateOrTemplateEngagement": False,
        "group": target_group,
    }


# --- Helpers --------------------------------------------------------------

# Pre-baked type/classification map - mirrors what GET groupaccounttypes
# returns. Saves a round-trip if you already know the type+classification
# by name or abbreviation.
TYPE_CLASSIFICATIONS = {
    # (accountTypeId, classificationId, accountTypeAbbreviation, classificationName)
    (1, 1): {"type": "Asset", "abbr": "A", "classification": "Current Assets"},
    (1, 2): {"type": "Asset", "abbr": "A", "classification": "Non-Current Assets"},
    (2, 3): {"type": "Liability", "abbr": "L", "classification": "Current Liabilities"},
    (2, 4): {"type": "Liability", "abbr": "L", "classification": "Non-Current Liabilities"},
    (3, 5): {"type": "Equity", "abbr": "E", "classification": "Equity"},
    (4, 6): {"type": "Revenue", "abbr": "R", "classification": "Revenues"},
    (4, 7): {"type": "Revenue", "abbr": "R", "classification": "Cost of Revenue"},
    (4, 8): {"type": "Revenue", "abbr": "R", "classification": "Other Income"},
    (5, 9): {"type": "Expense", "abbr": "X", "classification": "Operating Expenses"},
    (5, 10): {"type": "Expense", "abbr": "X", "classification": "Other Expenses"},
}


def resolve_classification(classification_name: str) -> tuple[int, int]:
    """Resolve a classification display name -> (accountTypeId, classificationId).

    Raises ValueError if the name doesn't match. Case-insensitive match.
    """
    target = classification_name.strip().lower()
    for (tid, cid), info in TYPE_CLASSIFICATIONS.items():
        if info["classification"].lower() == target:
            return tid, cid
    raise ValueError(f"Unknown classification name: {classification_name!r}. "
                     f"Valid: {[v['classification'] for v in TYPE_CLASSIFICATIONS.values()]}")


# ==========================================================================
# BULK / COMPOSITE OPERATIONS  (one browser call runs the whole sequence)
# --------------------------------------------------------------------------
# The single-step builders above each emit ONE XHR. Order-dependent or
# many-row operations (chained group create, group reorder, bulk regroup,
# subgroup create) are cleaner and far less round-trippy as a SINGLE async
# JS expression that fires each request in sequence in the browser and
# returns a compact result array. These builders generate that expression.
#
# Each returns a string you pass straight to the Chrome javascript_tool.
# Returns are SMALL (status + new ids only) — keep auth tokens in-page;
# never return localStorage token values (PII filter blocks the call).
# ==========================================================================

def _inline_xhr_js(headers: dict) -> str:
    """JS snippet that defines `_xhr(method, url, body)` -> Promise<{status, body}>.

    Mirrors http_runner.build_xhr_call (XHR for cross-origin; auto Content-Type
    on body writes) but reusable inside an async loop. `headers` may be a dict
    (baked as a literal) OR an "ls:<family>" sentinel for runtime localStorage
    self-sourcing.
    """
    from . import http_runner as _hr
    return (
        "const _H = " + _hr._headers_js(headers) + ";\n"
        "const _hasCT = Object.keys(_H).some(k => k.toLowerCase() === 'content-type');\n"
        "const _xhr = (method, url, body) => new Promise((resolve) => {\n"
        "  const x = new XMLHttpRequest();\n"
        "  x.open(method, url, true);\n"
        "  for (const k in _H) x.setRequestHeader(k, _H[k]);\n"
        "  if (body !== null && body !== undefined && !_hasCT) x.setRequestHeader('Content-Type', 'application/json');\n"
        "  x.onreadystatechange = () => { if (x.readyState === 4) resolve({status: x.status, body: x.responseText}); };\n"
        "  x.send((body === null || body === undefined) ? null : JSON.stringify(body));\n"
        "});\n"
    )


def build_chain_create_groups_js(client_id: int, financial_list_id: int,
                                 groups: list[dict], headers: dict,
                                 start_anchor: int = 0) -> str:
    """One browser call: create N groups in order, threading the insert-after anchor.

    `groups`: list of dicts, each {index, name, account_type_id, classification_id}.
    `start_anchor`: 0 if the list is EMPTY; otherwise the financialGroupId of the
        existing group you want the first new group inserted after.

    The chain reads each create's returned `financialGroupId` and uses it as the
    anchor for the next. STOPS on the first non-2xx (avoids cascading 400s).
    Because creates land LIFO, follow with build_reorder_groups_js() if you want
    ascending display order.

    Returns (JSON array): [{index, name, status, financialGroupId, body}, ...].
    """
    payload = [
        {
            "index": g["index"],
            "name": g["name"],
            "accountTypeId": g["account_type_id"],
            "classificationId": g["classification_id"],
        }
        for g in groups
    ]
    return (
        "(async () => {\n"
        + _inline_xhr_js(headers)
        + "  const FP = " + json.dumps(FP) + ";\n"
        + "  const cid = " + json.dumps(client_id) + ";\n"
        + "  const listId = " + json.dumps(financial_list_id) + ";\n"
        + "  const groups = " + json.dumps(payload) + ";\n"
        + "  let anchor = " + json.dumps(start_anchor) + ";\n"
        + "  const out = [];\n"
        + "  for (const g of groups) {\n"
        + "    const body = {engagementId: cid, consolidatedEngagementId: null, index: g.index, name: g.name, accountTypeId: g.accountTypeId, accountTypeClassificationId: g.classificationId, positionId: 0, financialListId: listId, financialGroupId: anchor};\n"
        + "    const r = await _xhr('POST', FP + '/v1.0/FinancialGroup', body);\n"
        + "    let newId = null; try { newId = JSON.parse(r.body).financialGroupId; } catch (e) {}\n"
        + "    out.push({index: g.index, name: g.name, status: r.status, financialGroupId: newId, body: r.body});\n"
        + "    if (r.status >= 200 && r.status < 300 && newId) { anchor = newId; } else { break; }\n"
        + "  }\n"
        + "  return JSON.stringify(out);\n"
        + "})()"
    )


def build_bulk_assign_js(client_id: int, patch_bodies: list[dict], headers: dict) -> str:
    """One browser call: reassign N accounts to groups (order-independent).

    `patch_bodies`: list of full PATCH bodies, each as produced by
        {**account_row, 'group': target_group} or build_patch_body(...).
        Each MUST carry `id` (accountId) and `financialListId`.

    Fires every PATCH in sequence; does NOT stop on error (collects all so you
    can see which rows failed). Verify after via the grouped TB at
    `row.account.group.financialGroupId`.

    Returns (JSON array): [{accountId, status}, ...].
    """
    items = []
    for b in patch_bodies:
        acct_id = b.get("id") or b.get("accountId")
        items.append({"accountId": acct_id, "body": b})
    return (
        "(async () => {\n"
        + _inline_xhr_js(headers)
        + "  const FP = " + json.dumps(FP) + ";\n"
        + "  const cid = " + json.dumps(client_id) + ";\n"
        + "  const items = " + json.dumps(items) + ";\n"
        + "  const out = [];\n"
        + "  for (const it of items) {\n"
        + "    const r = await _xhr('PATCH', FP + '/v1.0/financialTrialBalance/' + cid + '/balances/' + it.accountId, it.body);\n"
        + "    out.push({accountId: it.accountId, status: r.status});\n"
        + "  }\n"
        + "  return JSON.stringify(out);\n"
        + "})()"
    )


# --- GROUP REORDER (PUT) --------------------------------------------------

# classification display name -> id (mirror of TYPE_CLASSIFICATIONS)
_CLASSIFICATION_NAME_TO_ID = {
    info["classification"]: cid for (tid, cid), info in TYPE_CLASSIFICATIONS.items()
}

# accountTypeId -> accountType STRING (the `accountType`/`acctType` the PUT wants)
_ACCOUNT_TYPE_ID_TO_NAME = {
    tid: info["type"] for (tid, cid), info in TYPE_CLASSIFICATIONS.items()
}


def _group_put_type_fields(group: dict) -> dict:
    """Derive the account-type trio the reorder PUT requires from a group row.

    CRITICAL: the reorder PUT — UNLIKE the create
    POST — requires ALL THREE of `accountType` (the type STRING, e.g. 'Asset'),
    `accountTypeId`, and `accountTypeClassificationId`. Omitting any -> 400
    ("Invalid account type." / "Invalid account type classification.").

    The list_financial_groups GET row does NOT expose them flat: accountType +
    accountTypeId live under `group['type']` (acctType / accountTypeId), and the
    classification is given only by NAME (`group['classification']`) — its int
    id must be resolved (here via _CLASSIFICATION_NAME_TO_ID). Explicit flat
    fields on the input dict win if present.
    """
    t = group.get("type") or {}
    account_type = group.get("accountType") or t.get("acctType") or t.get("name")
    account_type_id = group.get("accountTypeId") or t.get("accountTypeId")
    cls_id = group.get("accountTypeClassificationId")
    if cls_id is None:
        cls_id = _CLASSIFICATION_NAME_TO_ID.get(group.get("classification"))
    return {
        "accountType": account_type,
        "accountTypeId": account_type_id,
        "accountTypeClassificationId": cls_id,
    }


def _reorder_put_body(client_id: int, financial_list_id: int, group: dict,
                      anchor_group_id: int, position: int) -> dict:
    body = {
        "engagementId": client_id,
        "consolidatedEngagementId": None,
        "financialGroupId": group["financialGroupId"],
        "index": group["index"],
        "name": group["name"],
        "financialListId": financial_list_id,
        "positionFinancialGroupId": anchor_group_id,
        "positionId": position,
    }
    body.update(_group_put_type_fields(group))
    return body


def move_financial_group(client_id: int, financial_list_id: int, group: dict,
                         anchor_group_id: int, position: int, headers: dict) -> str:
    """JS for: PUT /v1.0/FinancialGroup — move ONE group relative to an anchor.

    Distinct from create's POST. `group` is a group row (list_financial_groups
    GET shape — financialGroupId, index, name, nested type{}, classification
    name). The account-type trio is derived via _group_put_type_fields().
    financialGroupIds are STABLE across reorders.

    `anchor_group_id`: the group to position relative to (positionFinancialGroupId).
    `position`: 0 = before/above the anchor, 1 = after/below the anchor.

    For a full ascending sort use build_reorder_groups_js() instead.
    """
    body = _reorder_put_body(client_id, financial_list_id, group, anchor_group_id, position)
    return http_runner.build_xhr_call("PUT", f"{FP}/v1.0/FinancialGroup", headers, body)


def build_reorder_groups_js(client_id: int, financial_list_id: int,
                            ordered_groups: list[dict], headers: dict,
                            sort_by_index: bool = True) -> str:
    """One browser call: reorder a list into a target display order.

    `ordered_groups`: the groups to order — rows from list_financial_groups
        (financialGroupId, index, name, nested type{}, classification name).
        The required account-type trio is derived via _group_put_type_fields(),
        so you can pass the GET rows straight through. If sort_by_index=True
        (default), they are sorted ascending by `index` here; otherwise the given
        order is taken as the desired order.

    Algorithm:
        For i = 1..n-1, PUT move[i] with positionId=1 (after) and
        positionFinancialGroupId = move[i-1].financialGroupId. Chaining each
        group after its predecessor floats element 0 to the top and lands the
        rest in order. (Single PUTs via move_financial_group also work.)
        PUT body MUST carry accountType + accountTypeId +
        accountTypeClassificationId (see _group_put_type_fields).

    Returns (JSON array): [{index, financialGroupId, status, body}, ...].
    """
    groups = list(ordered_groups)
    if sort_by_index:
        def _key(g):
            ix = str(g.get("index", ""))
            return (0, int(ix)) if ix.isdigit() else (1, ix)
        groups = sorted(groups, key=_key)
    # pre-build each move's PUT body in Python (resolves the type trio + anchor chain)
    moves = [
        {
            "index": groups[i]["index"],
            "body": _reorder_put_body(
                client_id, financial_list_id, groups[i],
                anchor_group_id=groups[i - 1]["financialGroupId"], position=1,
            ),
        }
        for i in range(1, len(groups))
    ]
    return (
        "(async () => {\n"
        + _inline_xhr_js(headers)
        + "  const FP = " + json.dumps(FP) + ";\n"
        + "  const moves = " + json.dumps(moves) + ";\n"
        + "  const out = [];\n"
        + "  for (const m of moves) {\n"
        + "    const r = await _xhr('PUT', FP + '/v1.0/FinancialGroup', m.body);\n"
        + "    out.push({index: m.index, financialGroupId: m.body.financialGroupId, status: r.status, body: r.body});\n"
        + "  }\n"
        + "  return JSON.stringify(out);\n"
        + "})()"
    )


# --- SUBGROUPS (financialsubgroup) ----------------------------------------
# TB SUB-GROUP column — a child level under a financialGroup.
# There is NO GET /v1.0/financialsubgroup/{cid}/{listId}
# (404) — read subgroup membership from the grouped TB at
# `row.account.financialSubGroup`. UI path: Account Groupings -> Financial tab
# -> select core group -> Actions -> Add (KB #000229923).

def create_financial_subgroup(client_id: int, financial_list_id: int, parent_group_id: int,
                              index: str, name: str, headers: dict,
                              anchor_subgroup_id: int = 0) -> str:
    """JS for: POST /v1.0/financialsubgroup — create ONE subgroup under a parent group.

    Same insert-after anchor rule as groups, on its own field:
      anchor_subgroup_id = 0  -> first subgroup under this parent.
      anchor_subgroup_id > 0  -> the preceding sibling subgroup's
                                 financialSubGroupId.

    Returns (response body): {financialGroupId, financialSubGroupId,
    financialSubGroupGuid}. Use build_chain_create_subgroups_js() for several.

    Body shape:
        {engagementId, consolidatedEngagementId:null, index, name,
         financialGroupId:<parent>, positionId:0,
         positionFinancialSubGroupId:<anchor>, financialListId}
    """
    body = {
        "engagementId": client_id,
        "consolidatedEngagementId": None,
        "index": index,
        "name": name,
        "financialGroupId": parent_group_id,
        "positionId": 0,
        "positionFinancialSubGroupId": anchor_subgroup_id,
        "financialListId": financial_list_id,
    }
    return http_runner.build_xhr_call("POST", f"{FP}/v1.0/financialsubgroup", headers, body)


def assign_account_to_subgroup(client_id: int, account_id: int, financial_list_id: int,
                               financial_subgroup_id: int, headers: dict) -> str:
    """JS for: PATCH /v1.0/financialTrialBalance/{clientId}/financialsubgroup

    Assigns one account to a subgroup. Reads back at
    `row.account.financialSubGroup` on the grouped TB. `financialListId` is
    required (same guardrail as the group PATCH).

    ⚠️ PRECONDITION: the account MUST already be in
    the subgroup's PARENT group first. Assigning a subgroup to an account whose
    group != the subgroup's parent -> 400 "Invalid financial sub-group." So the
    flow is: assign_account_to_group(parent) -> then assign_account_to_subgroup().

    Body shape:
        {accountId, engagementId, consolidatedEngagementId:null,
         financialSubGroupId, financialListId}
    """
    body = {
        "accountId": account_id,
        "engagementId": client_id,
        "consolidatedEngagementId": None,
        "financialSubGroupId": financial_subgroup_id,
        "financialListId": financial_list_id,
    }
    return http_runner.build_xhr_call(
        "PATCH", f"{FP}/v1.0/financialTrialBalance/{client_id}/financialsubgroup", headers, body
    )


def build_chain_create_subgroups_js(client_id: int, financial_list_id: int, parent_group_id: int,
                                    subgroups: list[dict], headers: dict,
                                    start_anchor: int = 0) -> str:
    """One browser call: create N subgroups under one parent, threading the anchor.

    `subgroups`: list of dicts {index, name}. `start_anchor`: 0 for the first
    subgroup under the parent, else the preceding sibling's financialSubGroupId.

    Returns (JSON array): [{index, name, status, financialSubGroupId, body}, ...].
    """
    payload = [{"index": s["index"], "name": s["name"]} for s in subgroups]
    return (
        "(async () => {\n"
        + _inline_xhr_js(headers)
        + "  const FP = " + json.dumps(FP) + ";\n"
        + "  const cid = " + json.dumps(client_id) + ";\n"
        + "  const listId = " + json.dumps(financial_list_id) + ";\n"
        + "  const parent = " + json.dumps(parent_group_id) + ";\n"
        + "  const subs = " + json.dumps(payload) + ";\n"
        + "  let anchor = " + json.dumps(start_anchor) + ";\n"
        + "  const out = [];\n"
        + "  for (const s of subs) {\n"
        + "    const body = {engagementId: cid, consolidatedEngagementId: null, index: s.index, name: s.name, financialGroupId: parent, positionId: 0, positionFinancialSubGroupId: anchor, financialListId: listId};\n"
        + "    const r = await _xhr('POST', FP + '/v1.0/financialsubgroup', body);\n"
        + "    let newId = null; try { newId = JSON.parse(r.body).financialSubGroupId; } catch (e) {}\n"
        + "    out.push({index: s.index, name: s.name, status: r.status, financialSubGroupId: newId, body: r.body});\n"
        + "    if (r.status >= 200 && r.status < 300 && newId) { anchor = newId; } else { break; }\n"
        + "  }\n"
        + "  return JSON.stringify(out);\n"
        + "})()"
    )
# <!-- END -->
