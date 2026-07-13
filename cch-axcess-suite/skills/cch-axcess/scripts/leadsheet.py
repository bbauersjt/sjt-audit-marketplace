"""Leadsheet & TB-report annotation operations.

Two surfaces, ONE engagement-surface token set (Authorization + IDToken,
WPM-style — NOT KC tokens). Capture from any financialprep-api / workbench-api /
WPM XHR via auth_capture; pass the resulting `headers` dict to these functions.

  financialprep-api.cchaxcess.com  — system-generated leadsheet annotations
      comment box, inline account comments, tickmarks
  workbench-api.cchaxcess.com      — TB-report REF / REF2 column annotations

All functions return a JS string for mcp__Claude_in_Chrome__javascript_tool and
go through http_runner.build_xhr_call — cross-origin from engagement.cchaxcess.com
requires XHR (fetch fails CORS preflight; see architecture.md).

REFRESH RULE: every write below requires a page reload to show in the UI. Always
tell the user to refresh after a write.

Cross-API visibility is ONE-DIRECTIONAL: FP-API
bubbles/tickmarks written on the system-lead surface appear on TB reports after
refresh (read-only there, cpComments/cpTickMarks). Workbench REF values appear
NOWHERE but the TB report itself.
"""
from __future__ import annotations

from typing import Optional

from scripts import http_runner

FP = "https://financialprep-api.cchaxcess.com"
WB = "https://workbench-api.cchaxcess.com"


# ===========================================================================
# FP-API — system leadsheet reads
# ===========================================================================

def get_groups(client_id: int, headers: dict) -> str:
    """GET /v1.0/leadsheet/{clientId}/1/groups — all leadsheet groups.

    Response: array of group objects carrying financialGroupId, name, number.
    Use to resolve a section name/number -> financialGroupId (e.g. Payables 726342).
    """
    return http_runner.build_xhr_call("GET", f"{FP}/v1.0/leadsheet/{client_id}/1/groups", headers)


def get_leadsheet(client_id: int, financial_group_id: int, period_id: int, headers: dict) -> str:
    """GET /v1.0/leadsheet/{clientId}/1/groups/{financialGroupId}?periodId={periodId}

    Full leadsheet data. Parse with http_runner.parse_result, then use
    find_reference_id() to map an account number -> referenceId.

    Shape: subGroupBalances[].account[].account.id (=referenceId, integer),
    .number (account number string e.g. '20000-300'), .name; top-level
    `comments` is the current comment-box text.
    """
    url = f"{FP}/v1.0/leadsheet/{client_id}/1/groups/{financial_group_id}?periodId={period_id}"
    return http_runner.build_xhr_call("GET", url, headers)


def find_reference_id(parsed_body: dict, account_number: str) -> Optional[int]:
    """Resolve an account number string -> referenceId from a parsed get_leadsheet body.

    referenceId is account.id (CCH internal integer), NOT the account number.
    Match is exact, then dash-insensitive ('20000-300' vs '20000300').
    Returns None if not found. Note CCH uses a 5-digit prefix: '20000-300'.
    """
    if not isinstance(parsed_body, dict):
        return None
    want = account_number.replace("-", "")
    for sub in parsed_body.get("subGroupBalances", []) or []:
        for row in sub.get("account", []) or []:
            acct = row.get("account", {}) or {}
            num = str(acct.get("number", ""))
            if num == account_number or num.replace("-", "") == want:
                return acct.get("id")
    return None


# ===========================================================================
# FP-API — top-level comment box
# ===========================================================================

def patch_comment_box(client_id: int, financial_list_id: int, period_id: int,
                      financial_group_id: int, comment: str, headers: dict,
                      comments_height: int = 70, comments_width: int = 300) -> str:
    """PATCH /v1.0/leadsheet/Comments — write/clear the top-level comment box.

    Pass comment='' to clear. engagementId in the body is the clientId.
    Single call (no triple-fire). REFRESH required.
    """
    body = {
        "engagementId": client_id,
        "financialListId": financial_list_id,
        "periodId": period_id,
        "financialGroupId": financial_group_id,
        "comments": comment,
        "commentsHeight": comments_height,
        "commentsWidth": comments_width,
        "isConsolidated": False,
        "subsidiaryParentId": 0,
    }
    return http_runner.build_xhr_call("PATCH", f"{FP}/v1.0/leadsheet/Comments", headers, body)


# ===========================================================================
# FP-API — inline account comment
# ===========================================================================

def post_account_comment(client_id: int, reference_id: int, period_id: int,
                         engagement_id: int, comment: str, headers: dict,
                         reference_type: str = "Account") -> str:
    """POST /v1.0/Annotation/comment/{clientId} — upsert an inline comment (bubble).

    Server upserts by referenceId+periodId; editing is a re-POST (no delete-first).
    THE UPSERT IS SILENT — check for an existing comment and prompt the user first
    (see annotate-leadsheet.md step 2-pre).
    Response body: {"commentReferenceId": <int>} — store it for delete.

    reference_type levels:
      "Account"        — account row; reference_id = account.id (see find_reference_id)
      "FinancialGroup" — group/total row; reference_id = financialGroupId
    """
    body = {
        "comment": comment,
        "referenceId": reference_id,
        "referenceType": reference_type,
        "periodId": period_id,
        "engagementId": engagement_id,
    }
    return http_runner.build_xhr_call("POST", f"{FP}/v1.0/Annotation/comment/{client_id}", headers, body)


def delete_account_comment(client_id: int, comment_reference_id: int, headers: dict) -> str:
    """DELETE /v1.0/Annotation/comment/{clientId}/{commentReferenceId}.

    commentReferenceId comes from the post_account_comment response. REFRESH required.
    """
    url = f"{FP}/v1.0/Annotation/comment/{client_id}/{comment_reference_id}"
    return http_runner.build_xhr_call("DELETE", url, headers)


# ===========================================================================
# FP-API — tickmarks
# ===========================================================================

def post_tickmarks(client_id: int, reference_id: int, period_id: int,
                   engagement_id: int, ids: list, headers: dict) -> str:
    """POST /v1.0/Annotation/tickmarks/{clientId} — SET-REPLACE tickmarks on an account.

    `ids` must be the COMPLETE desired set (IDs 1-71 — see config/tickmark_ids.json).
    Add = current+new; remove = remaining; clear = []. originalIds is always null.
    REFRESH required.
    """
    body = {
        "ids": list(ids),
        "engagementId": engagement_id,
        "referenceId": reference_id,
        "referenceType": "Account",
        "periodId": period_id,
        "originalIds": None,
    }
    return http_runner.build_xhr_call("POST", f"{FP}/v1.0/Annotation/tickmarks/{client_id}", headers, body)


# ===========================================================================
# workbench-api — TB report REF / REF2 column annotations
# ===========================================================================

def tbreport_resolve_report_id(client_id: int, engagement_guid: str,
                               report_guid: str, headers: dict) -> str:
    """GET /v1/trialbalancereport/tbreportedit/{clientId}/{engGuid}/{reportGuid}.

    This is the Step-0 REF-COLUMN PREFLIGHT read (reportFormat.columns), NOT a
    reportId source: the tbreportedit body has NO usable id field.
    The integer reportId = the report's WPM documentId ('tbreports/{int}'
    row) — resolve it from the binder map / WPM listing, not from this response.
    reportGuid comes from the report URL.
    """
    url = f"{WB}/v1/trialbalancereport/tbreportedit/{client_id}/{engagement_guid}/{report_guid}"
    return http_runner.build_xhr_call("GET", url, headers)


def tbreport_row_probe_js(match_text: str) -> str:
    """In-page ag-grid DOM probe (no API call) -> a TB-report row's identity.

    Finds the visible row whose text contains match_text (e.g. 'Fund: 300') and
    returns {referenceId, referenceGuid, referenceType, name, index}.
    referenceGuid is present only on Fund rows (omit it for FinancialGroup (group/total) AND FinancialSubGroup).
    """
    mt = match_text.replace("\\", "\\\\").replace('"', '\\"')
    return (
        "(() => {\n"
        '  const rows = Array.from(document.querySelectorAll(".ag-row"));\n'
        '  const el = rows.find(r => r.textContent.includes("' + mt + '"));\n'
        '  if (!el) return JSON.stringify({error: "row not found: ' + mt + '"});\n'
        '  const k = Object.keys(el).find(x => x.startsWith("__AG_"));\n'
        "  const d = k && el[k] && el[k].renderedRow && el[k].renderedRow.rowNode\n"
        "            ? el[k].renderedRow.rowNode.data : null;\n"
        '  if (!d) return JSON.stringify({error: "ag-grid row data not reachable"});\n'
        "  return JSON.stringify({\n"
        "    referenceId: d.id,\n"
        "    referenceGuid: d.financialGroupOrSubGroupGuid || null,\n"
        "    referenceType: d.rowType,\n"
        "    name: d.name, index: d.index\n"
        "  });\n"
        "})()"
    )


def tbreport_post_comment(client_id: int, report_id: int, engagement_id: int,
                          column_id: int, reference_id: int, reference_type: str,
                          period_id: int, comment: str, headers: dict,
                          reference_guid: Optional[str] = None) -> str:
    """POST /v1/trialbalancereportcomment/{clientId}/{reportId} — write/edit REF or REF2.

    column_id: 1 = REF, 2 = REF2 (positional; heading names don't matter).
    reference_guid: include for Fund rows, omit (None) for FinancialSubGroup rows.
    Response body: {"reportCommentReferenceId": <int>} — store for delete
    (note: different field name from FP-API's commentReferenceId). REFRESH required.
    """
    body = {
        "reportId": report_id,
        "engagementId": engagement_id,
        "columnId": column_id,
        "referenceId": reference_id,
        "referenceType": reference_type,
        "periodId": period_id,
        "comment": comment,
    }
    if reference_guid is not None:
        body["referenceGuid"] = reference_guid
    url = f"{WB}/v1/trialbalancereportcomment/{client_id}/{report_id}"
    return http_runner.build_xhr_call("POST", url, headers, body)


def tbreport_delete_comment(client_id: int, report_id: int,
                            report_comment_reference_id: int, column_id: int,
                            headers: dict) -> str:
    """DELETE /v1/trialbalancereportcomment/{clientId}/{reportId}/{reportCommentReferenceId}/{columnId}.

    report_comment_reference_id comes from tbreport_post_comment. column_id is positional: Remarks_1 -> 1, Remarks_2 -> 2 (rename-proof).
    REFRESH required.
    """
    url = (f"{WB}/v1/trialbalancereportcomment/{client_id}/{report_id}"
           f"/{report_comment_reference_id}/{column_id}")
    return http_runner.build_xhr_call("DELETE", url, headers)
# <!-- END -->
