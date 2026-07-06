"""Fund accounting operations (governmental / NFP clients).

Every public function returns a JS string ready for mcp__Claude_in_Chrome__javascript_tool.
The Python side never directly hits CCH - calls go through the user's authenticated
engagement.cchaxcess.com browser tab via XHR (cross-origin to workbench-api).

Tab requirements: an engagement.cchaxcess.com tab logged into the target engagement.
Headers requirements: capture engagement-side headers via scripts.auth_capture (monkey-patch).
The same captured header set works for WPM, workbench-api, and financialprep-api.

Endpoint specs: references/endpoints/funds_*.json (single source of truth for shapes & gotchas).

Operating pattern: list -> mutate in Python -> upsert the whole list back.
Almost every mutation is whole-list replacement, not incremental. Caller must
include every existing item plus the new ones. The one exception is
account-to-fund assignment (assign_account / unassign_account), which is
incremental.

ID note: the URL path and request body field both say `engagementId` but the
value is actually the Axcess clientId (first integer in the engagement URL).
Same misnaming as WPM and other workbench-api endpoints - see architecture.md.
"""
import json
from typing import Any, Optional
from . import http_runner

WORKBENCH = "https://workbench-api.cchaxcess.com"


# --- LIST (GET) -----------------------------------------------------------

def list_fund_types(client_id: int, headers: dict) -> str:
    """JS for: GET /v1/FundType/{clientId}

    Returns a BARE ARRAY (no envelope) of rows shaped:
        [{fundTypeId, fundTypeIndex, fundTypeName}, ...]

    Field names are PREFIXED here but BARE in the PUT body - run the parsed
    response through normalize_fund_types() before feeding it to
    merge_for_upsert() or upsert_fund_types().
    """
    return http_runner.build_xhr_call(
        "GET", f"{WORKBENCH}/v1/FundType/{client_id}", headers
    )


def list_funds(client_id: int, headers: dict) -> str:
    """JS for: GET /v1/Fund/{clientId}

    Returns a BARE ARRAY of rows shaped:
        [{fundId, fundGuid, fundName, fundIndex, sortOrder,
          fundType: {fundTypeId, fundTypeIndex, fundTypeName},
          fundSubType: {...} | null}, ...]

    Field names are prefixed AND fundType/fundSubType are embedded objects
    (not FKs). Run through normalize_funds() to flatten to the PUT shape.
    """
    return http_runner.build_xhr_call(
        "GET", f"{WORKBENCH}/v1/Fund/{client_id}", headers
    )


def list_fund_sub_types(client_id: int, headers: dict) -> str:
    """JS for: GET /v1/FundSubType/{clientId}

    Returns an OBJECT envelope shaped:
        {fundSubTypes: [{fundSubTypeId, fundSubTypeName, fundSubTypeIndex,
                         fundTypeId, sortOrder}, ...]}

    Note fundTypeId is bare even in the GET response. Run through
    normalize_fund_sub_types() to convert to PUT shape.
    """
    return http_runner.build_xhr_call(
        "GET", f"{WORKBENCH}/v1/FundSubType/{client_id}", headers
    )


def get_fund_account_map(client_id: int, headers: dict) -> str:
    """JS for: GET /v1/Fund/{clientId}/fundaccountmap

    Returns an OBJECT envelope shaped:
        {fundAccountMapDtos: [{accountId, accountGuid, accountName,
                               accountNumber,
                               fund?: {fundId, fundGuid, fundName,
                                       fundIndex, sortOrder}}, ...],
         engagementId: int}

    The `fund` key is ABSENT for unassigned accounts (not null). Use
    split_assigned() to partition assigned vs unassigned.
    """
    return http_runner.build_xhr_call(
        "GET", f"{WORKBENCH}/v1/Fund/{client_id}/fundaccountmap", headers
    )


# --- UPSERT (whole-list PUT) ----------------------------------------------

def upsert_fund_types(
    client_id: int, fund_types: list[dict], headers: dict
) -> str:
    """JS for: PUT /v1/FundType

    Whole-list replacement. Caller MUST include every existing fund type
    (with its id) plus any new ones (omit id, or pass id=None).

    fund_types: list of {id?, index, name}. For new entries, omit the id
    key entirely - FundType is the outlier that does NOT accept id=0 like
    Fund and FundSubType do.

    Body shape sent:
        {"engagementId": clientId, "fundTypes": [{id?, index, name}, ...]}
    """
    cleaned = []
    for ft in fund_types:
        row = {"index": ft["index"], "name": ft["name"]}
        if ft.get("id"):  # truthy id only - omit for new entries
            row = {"id": ft["id"], **row}
        cleaned.append(row)
    body = {"engagementId": client_id, "fundTypes": cleaned}
    return http_runner.build_xhr_call(
        "PUT", f"{WORKBENCH}/v1/FundType", headers, body
    )


def upsert_funds(client_id: int, funds: list[dict], headers: dict) -> str:
    """JS for: PUT /v1/Fund

    Whole-list replacement. Caller MUST include every existing fund
    (with its id) plus any new ones (id=0 for new).

    funds: list of {id, index, name, fundTypeId, fundSubTypeId?}. For new
    entries pass id=0 (Fund follows the id=0-means-new convention, unlike
    FundType).

    Body shape sent:
        {"engagementId": clientId, "funds": [{id, index, name, fundTypeId, fundSubTypeId?}, ...]}
    """
    cleaned = []
    for f in funds:
        row = {
            "id": f.get("id", 0),
            "index": f["index"],
            "name": f["name"],
            "fundTypeId": f["fundTypeId"],
        }
        if f.get("fundSubTypeId") is not None:
            row["fundSubTypeId"] = f["fundSubTypeId"]
        cleaned.append(row)
    body = {"engagementId": client_id, "funds": cleaned}
    return http_runner.build_xhr_call(
        "PUT", f"{WORKBENCH}/v1/Fund", headers, body
    )


def upsert_fund_sub_types(
    client_id: int, fund_sub_types: list[dict], headers: dict
) -> str:
    """JS for: PUT /v1/FundSubType

    Whole-list replacement. Caller MUST include every existing sub-type
    (with its id) plus any new ones (id=0 for new).

    fund_sub_types: list of {id, index, name, fundTypeId}.

    Body shape sent:
        {"engagementId": clientId, "fundSubTypes": [{id, index, name, fundTypeId}, ...]}
    """
    cleaned = [
        {
            "id": st.get("id", 0),
            "index": st["index"],
            "name": st["name"],
            "fundTypeId": st["fundTypeId"],
        }
        for st in fund_sub_types
    ]
    body = {"engagementId": client_id, "fundSubTypes": cleaned}
    return http_runner.build_xhr_call(
        "PUT", f"{WORKBENCH}/v1/FundSubType", headers, body
    )


# --- INCREMENTAL ASSIGNMENT (PUT, one fund at a time) ---------------------

def assign_account(
    client_id: int, fund_id: int, account_ids: list[int], headers: dict
) -> str:
    """JS for: PUT /v1/Fund/{clientId}/fundassignment

    Assigns one or more accounts to a fund. Incremental, NOT whole-list.
    Each call only touches the accounts in account_ids; other assignments
    stay put.

    Body shape sent:
        {"fundId": fundId, "accountId": [accountId, ...]}
    """
    body = {"fundId": fund_id, "accountId": list(account_ids)}
    return http_runner.build_xhr_call(
        "PUT", f"{WORKBENCH}/v1/Fund/{client_id}/fundassignment", headers, body
    )


def unassign_account(
    client_id: int, account_ids: list[int], headers: dict
) -> str:
    """JS for: PUT /v1/Fund/{clientId}/fundassignment with fundId omitted.

    Returns the accounts in account_ids to the Unassigned pool. The fundId
    field is dropped entirely from the body - server reads its absence as
    'no fund'.

    Body shape sent:
        {"accountId": [accountId, ...]}
    """
    body = {"accountId": list(account_ids)}
    return http_runner.build_xhr_call(
        "PUT", f"{WORKBENCH}/v1/Fund/{client_id}/fundassignment", headers, body
    )


# --- DELETE (single-row, dependency-aware) ---------------------------------
# Restored 2026-06-03: these functions were referenced by manage-funds.md and
# the endpoint specs (validated live 2026-05-25, clientId 90773) but were
# missing from this file (s3 handoff P1). Fund-accounting DELETEs are the ONE
# sanctioned hard-delete surface in this skill — see the HARD-DELETE POLICY in
# wpm.py; do not extend the pattern elsewhere.
#
# Delete order when draining everything: Funds first, then FundSubTypes, then
# FundTypes — dependents block parents (400 + {messages:[...]}).


def check_delete_eligible_fund_type(client_id: int, fund_type_id: int, headers: dict) -> str:
    """JS for: GET /v1/FundType/{clientId}/iseligiblefordelete/{fundTypeId}.

    Response body is a bare JSON boolean: "true" | "false".
    """
    return http_runner.build_xhr_call(
        "GET", f"{WORKBENCH}/v1/FundType/{client_id}/iseligiblefordelete/{fund_type_id}", headers
    )


def delete_fund_type(client_id: int, fund_type_id: int, headers: dict) -> str:
    """JS for: DELETE /v1/FundType/{clientId}/{fundTypeId}.

    200 on success; 400 + {messages:[...]} while funds/sub-types remain assigned.
    """
    return http_runner.build_xhr_call(
        "DELETE", f"{WORKBENCH}/v1/FundType/{client_id}/{fund_type_id}", headers
    )


def delete_fund(client_id: int, fund_id: int, headers: dict) -> str:
    """JS for: DELETE /v1/Fund/{clientId}/{fundId}.

    No eligibility pre-flight needed — assigned accounts cascade to Unassigned.
    """
    return http_runner.build_xhr_call(
        "DELETE", f"{WORKBENCH}/v1/Fund/{client_id}/{fund_id}", headers
    )


def check_delete_eligible_fund_sub_type(client_id: int, sub_type_id: int, headers: dict) -> str:
    """JS for: GET /v1/FundSubType/{clientId}/iseligiblefordelete/{subTypeId}.

    Response body is a bare JSON boolean: "true" | "false".
    """
    return http_runner.build_xhr_call(
        "GET", f"{WORKBENCH}/v1/FundSubType/{client_id}/iseligiblefordelete/{sub_type_id}", headers
    )


def delete_fund_sub_type(client_id: int, sub_type_id: int, headers: dict) -> str:
    """JS for: DELETE /v1/FundSubType/{clientId}/{subTypeId}.

    200 on success; 400 + {messages:[...]} while funds remain assigned to it.
    """
    return http_runner.build_xhr_call(
        "DELETE", f"{WORKBENCH}/v1/FundSubType/{client_id}/{sub_type_id}", headers
    )


# --- Helpers --------------------------------------------------------------

def merge_for_upsert(existing: list[dict], new: list[dict], match_key: str = "index") -> list[dict]:
    """Build a whole-list payload for an upsert by merging new rows onto
    existing rows. Rows in `new` matching an existing row by match_key
    replace the existing entry (preserving its id). Rows in `new` that don't
    match are appended without an id.

    IMPORTANT: `existing` must be in PUT shape (bare `id` / `index` / `name`
    keys, not prefixed GET shape). Run normalize_fund_types(),
    normalize_funds(), or normalize_fund_sub_types() on the GET response
    first.

    Example (full read-mutate-write loop):
        existing_raw = http_runner.parse_result(<get js result>)["body"]
        existing = funds.normalize_fund_types(existing_raw)
        new = [{"index": "03", "name": "Capital Projects"}]
        body = funds.merge_for_upsert(existing, new, match_key="index")
        js = funds.upsert_fund_types(client_id, body, headers)
    """
    by_key = {row[match_key]: row for row in existing}
    out = list(existing)
    for n in new:
        key = n.get(match_key)
        if key in by_key:
            idx = out.index(by_key[key])
            merged = {**by_key[key], **n}
            out[idx] = merged
        else:
            out.append(n)
    return out


# --- Normalizers: GET response -> PUT body shape --------------------------

def normalize_fund_types(get_body) -> list[dict]:
    """Convert GET /v1/FundType response to a list of {id, index, name}.

    Accepts either the parsed body (bare array) or a dict (in case future
    server versions add an envelope).
    """
    rows = get_body if isinstance(get_body, list) else (get_body or {}).get("fundTypes", [])
    return [
        {
            "id": r["fundTypeId"],
            "index": r["fundTypeIndex"],
            "name": r["fundTypeName"],
        }
        for r in rows
    ]


def normalize_funds(get_body) -> list[dict]:
    """Convert GET /v1/Fund response to a list of
    {id, index, name, fundTypeId, fundSubTypeId?}.

    Flattens the embedded fundType / fundSubType objects to their integer FKs.
    """
    rows = get_body if isinstance(get_body, list) else (get_body or {}).get("funds", [])
    out = []
    for r in rows:
        row = {
            "id": r["fundId"],
            "index": r["fundIndex"],
            "name": r["fundName"],
            "fundTypeId": (r.get("fundType") or {}).get("fundTypeId"),
        }
        sub = r.get("fundSubType")
        if sub:
            row["fundSubTypeId"] = sub.get("fundSubTypeId")
        out.append(row)
    return out


def normalize_fund_sub_types(get_body) -> list[dict]:
    """Convert GET /v1/FundSubType response to a list of
    {id, index, name, fundTypeId}.
    """
    rows = (get_body or {}).get("fundSubTypes", []) if isinstance(get_body, dict) else (get_body or [])
    return [
        {
            "id": r["fundSubTypeId"],
            "index": r["fundSubTypeIndex"],
            "name": r["fundSubTypeName"],
            "fundTypeId": r["fundTypeId"],
        }
        for r in rows
    ]


def split_assigned(get_body) -> tuple[list[dict], list[dict]]:
    """Partition the fundaccountmap GET response into (assigned, unassigned).

    `assigned` rows have `fund_id` (extracted from the embedded fund object).
    `unassigned` rows do not. Both keep accountId / accountNumber / accountName
    for caller convenience.

    Returns (assigned, unassigned). Order preserved within each bucket.
    """
    rows = (get_body or {}).get("fundAccountMapDtos", []) if isinstance(get_body, dict) else (get_body or [])
    assigned, unassigned = [], []
    for r in rows:
        base = {
            "account_id": r["accountId"],
            "account_number": r.get("accountNumber"),
            "account_name": r.get("accountName"),
        }
        if r.get("fund"):
            assigned.append({**base, "fund_id": r["fund"]["fundId"], "fund_index": r["fund"].get("fundIndex"), "fund_name": r["fund"].get("fundName")})
        else:
            unassigned.append(base)
    return assigned, unassigned


def check_unfunded_accounts(get_body) -> dict:
    """Unfunded-accounts guard (AX-33). On a fund-accounting engagement, an account
    assigned to NO fund is **silently dropped** from every fund-based statement/report —
    Axcess raises no error, the account just vanishes from the presentation. After fund
    setup / assignment, run this on the fundaccountmap GET and surface any unassigned
    accounts to the user; do NOT auto-assign (the correct fund is a judgment call).

    Returns {"ok": bool, "unfunded": [{account_number, account_name, account_id}, ...],
             "reason": str}. ok=False when ANY account is unassigned.
    """
    _assigned, unassigned = split_assigned(get_body)
    if unassigned:
        listed = ", ".join(str(u.get("account_number") or u.get("account_name")) for u in unassigned[:8])
        more = "" if len(unassigned) <= 8 else f" (+{len(unassigned) - 8} more)"
        return {"ok": False, "unfunded": unassigned,
                "reason": (f"{len(unassigned)} account(s) are assigned to NO fund: {listed}{more}. "
                           "Axcess silently drops unfunded accounts from fund-based statements — "
                           "STOP and prompt the user to assign each to a fund (or confirm the "
                           "omission is intended). Do NOT auto-assign.")}
    return {"ok": True, "unfunded": [], "reason": "every account is assigned to a fund"}


# --- AX-26 preflight: placeholder-TB halt ---------------------------------------
def preflight_account_map(accounts: list[dict]) -> dict:
    """Halt-check before ANY account-assignment step (funds OR groups).

    BT3 incident: B2/B3 ran fund/group assignments against a 1-dummy-account map
    ("0 Delete") without warning. Rule: if the map looks like a placeholder TB,
    STOP and prompt the user to import the real TB first.

    Returns {"ok": bool, "reason": str, "account_count": int}.
    Callers MUST prompt the user (do not proceed) when ok=False.
    """
    n = len(accounts or [])
    if n == 0:
        return {"ok": False, "account_count": 0,
                "reason": "Account map is EMPTY — no TB imported. Prompt the user to import the TB before any assignment step."}
    def _dummy(a):
        name = str(a.get("accountName") or a.get("name") or "").strip().lower()
        num = str(a.get("accountNumber") or a.get("number") or "").strip()
        return name in {"delete", "0 delete", "dummy", "placeholder"} or num in {"0", "00", "000"}
    if n <= 2 and any(_dummy(a) for a in accounts):
        return {"ok": False, "account_count": n,
                "reason": f"Account map has only {n} account(s) and at least one looks like a placeholder "
                          "('Delete'/number '0'). This is a pre-import dummy TB — prompt the user: "
                          "import the real TB before running assignments (BT3 incident rule)."}
    return {"ok": True, "account_count": n, "reason": "account map looks real"}


def check_fund_references(account_rows, defined_funds, fund_id_key="fundId", fund_range=None):
    """Referential-integrity preflight for fund assignment (AX-31).

    Halts before assigning accounts to funds when an account references a fund that is
    NOT in the engagement's defined Fund hierarchy (an orphan / out-of-range fund — e.g.
    fund 999 when only 100-500 are defined). The whole-list Fund PUT and the account-fund
    assignment would otherwise accept it silently and mis-map the account (no native
    error). This is the AX-31 gap fix: preflight_account_map catches an EMPTY/placeholder
    map; this catches a real map that points accounts at undefined funds.

    account_rows: account-fund map rows; each carries a fund id under `fund_id_key`, or
        nested under `fund` ({'id'|'fundId'}). Rows with NO fund id are Unassigned and
        skipped (that's a grouping concern, not a fund-reference error).
    defined_funds: the Fund list from list_funds()/normalize_funds() — each with an `id`
        (and usually `fundIndex`/`fundName`).
    fund_range: optional (min, max) of acceptable fund INDEX values; when given, a fund
        whose numeric index falls outside is also flagged (softer numbering-range check).

    Returns {"ok": bool, "reason": str, "orphans": [{"account":..., "fundId":...}, ...]}.
    Caller MUST prompt the user and NOT proceed when ok=False — the fix is the user's
    (define the fund, or correct the account's fund), never an auto-reassign.
    """
    defined_ids = set()
    for f in defined_funds or []:
        fid = f.get("id", f.get("fundId"))
        if fid is not None:
            defined_ids.add(str(fid))
    lo, hi = (fund_range or (None, None))
    orphans = []
    for a in account_rows or []:
        fid = a.get(fund_id_key)
        if fid is None:
            fund = a.get("fund")
            if isinstance(fund, dict):
                fid = fund.get("id", fund.get("fundId"))
        if fid in (None, "", 0, "0"):
            continue  # unassigned — not a fund-reference error
        bad = str(fid) not in defined_ids
        if not bad and lo is not None and hi is not None:
            try:
                fx = int(fid)
                bad = fx < lo or fx > hi
            except (TypeError, ValueError):
                bad = False
        if bad:
            orphans.append({
                "account": a.get("accountNumber") or a.get("number") or a.get("accountName"),
                "fundId": fid,
            })
    if orphans:
        listed = ", ".join(f"{o['account']}->fund {o['fundId']}" for o in orphans[:8])
        more = "" if len(orphans) <= 8 else f" (+{len(orphans) - 8} more)"
        return {"ok": False, "orphans": orphans,
                "reason": (f"{len(orphans)} account(s) reference a fund NOT in the engagement's "
                           f"defined Fund list: {listed}{more}. Out-of-range / orphan fund "
                           "reference — STOP and prompt the user to either define the fund or "
                           "correct the account's fund. Do NOT assign (the PUT silently mis-maps).")}
    return {"ok": True, "orphans": [],
            "reason": "all account fund references resolve to defined funds"}

# <!-- END -->
