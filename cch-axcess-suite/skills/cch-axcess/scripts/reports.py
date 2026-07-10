"""Workbench-API report generation + supporting financialprep-api helpers.

Two CCH subdomains involved (both documented in architecture.md):
  - workbench-api.cchaxcess.com         — report creation, listing, quotas, enums
  - financialprep-api.cchaxcess.com     — supporting metadata (grouping lists, group IDs)

All calls cross-origin from engagement.cchaxcess.com → XHR (fetch fails CORS
preflight; same rule as WPM). Headers are the WPM-style set:
Authorization, IDToken (all caps), USERLocale, Accept-Language, CountryCode,
Accept, Content-Type.

Created reports land in Unfiled Reports in the binder. Filing them (Move +
Set-Index into the right folder) is a separate step handled by scripts/wpm.py
— these functions intentionally do not auto-file.

Naming gotcha (same as WPM, see architecture.md): both create POST bodies use
the field name `engagementId` to carry the clientId value. The real engagementId
rides in `periodId` (TB: nested in ReportSettings; JE: top-level).
"""
from . import http_runner

WB = "https://workbench-api.cchaxcess.com"
FP = "https://financialprep-api.cchaxcess.com"

# JE type integer IDs — confirmed positionally on 2026-05-24.
# POST body [1,4,2,3] in UI order AJE,RJE,TJE,PAJE produced reports named
# AJE_AJE, AJE_RJE, AJE_TJE, AJE_PAJE in sequential reportId order.
# Source of truth: references/config/je_types.json.
JE_TYPE_IDS = {"AJE": 1, "TJE": 2, "PAJE": 3, "RJE": 4}

# TB Report detail levels — keys CCH accepts for the ReportType field.
# Source of truth: GET /v1/trialbalancereport/reporttypesandsettings.
TB_REPORT_TYPES = {"SummaryByGroup", "SummaryBySubGroup", "AccountDetail"}

# TB Report column types — partial enum. Captured types on 2026-05-24:
# Unadjusted, Aje, Final, Remarks. Brett also saw an "Adjusted" option in the
# UI (excluded from his selection so it didn't reach the wire). Reclassified,
# Tax, and variance variants likely exist too — to be mapped in a future
# all-columns-selected capture pass.
# Source of truth: references/config/tb_column_types.json.
TB_COLUMN_TYPES = {"Unadjusted", "Aje", "Final", "Remarks", "Adjusted"}


# ──────────────────────────────────────────────────────────────────────────
# Create operations
# ──────────────────────────────────────────────────────────────────────────

def create_tb_report(
    client_id: int | str,
    engagement_id: int | str,
    engagement_guid: str,
    report_name: str,
    headers: dict,
    *,
    report_index: str = "",
    groups: list[int] | None = None,
    grouping_list_id: int = 1,
    report_type: str = "SummaryByGroup",
    trial_balance: str = "Financial",
    include_net_income: bool = False,
    include_sum_of_account_groups: bool = False,
    hide_unused_groups_and_subgroups: bool = False,
    hide_accounts_with_zero_balances: bool = False,
    journal_entry_details: bool = True,
    show_classified_report: bool = False,
    columns: list[dict] | None = None,
    fund_settings: dict | None = None,
) -> str:
    """JS for: POST workbench-api/v1/trialbalancereport/createReports.

    `groups=None` → include all current and future groups.
    `groups=[ids]` → include only those FinancialGroup IDs
                     (discoverable via get_financial_groups).

    `fund_settings` — pass build_fund_settings(...) on fund engagements
    (governmental/NFP); None (default) omits fund scoping — correct for
    non-fund engagements. Wire shapes: references/config/fund_settings.json.

    `report_type` must be one of TB_REPORT_TYPES.
    `trial_balance` is the named TB on the engagement; default 'Financial'
    works for non-consolidated engagements.

    `report_index` populates the workpaper's index attribute but does NOT
    auto-file the report into a binder folder — Move + Set-Index after.

    `columns`: optional list of column dicts to customize the report's
        columns. If None, CCH uses the engagement's defaults. Each dict has
        shape:
            {
                "id": str,               # composite id, e.g. "Unadjusted_Current"
                "type": str,             # see TB_COLUMN_TYPES
                "name": str,
                "abbrev": str,           # short label, e.g. "UNADJ", "AJE", "FINAL"
                "variance": None,        # or a variance config object
                "order": int,            # 1-based column position
                "periodId": int,         # engagement period id
                "periodEndDate": str,    # "YYYY-MM-DD"
                "isDeleted": bool,       # False for active columns
                "engagementId": int,     # ONLY present on type='Remarks'
            }
        See references/config/tb_column_types.json for known column types.

    Body field `engagementId` carries the clientId value (naming gotcha).
    `ReportSettings.periodId` carries the real engagementId.
    """
    if report_type not in TB_REPORT_TYPES:
        raise ValueError(
            f"report_type must be one of {sorted(TB_REPORT_TYPES)}, got {report_type!r}"
        )

    include_all = groups is None
    body = {
        "engagementGuid": engagement_guid,
        "engagementId": client_id,            # misnamed — carries clientId
        "reportGuid": None,                    # null = create new
        "reportIndex": report_index,
        "reportName": report_name,
        "includeSelectedGroups": not include_all,
        "IncludeCurrentandFutureGroups": include_all,
        "TrialBalance": trial_balance,
        "GroupingListId": grouping_list_id,
        "FinancialGroupsIncluded": [] if include_all else list(groups),
        "TaxGroupsIncluded": None,
        "ReportType": report_type,
        "reportFormat": {"columns": list(columns) if columns else []},
        "consolidatedEngagementId": None,
        "ReportSettings": {
            "IncludeNetIncome": include_net_income,
            "HideAccountsWithZeroBalances": hide_accounts_with_zero_balances,
            "HideUnusedGroupsAndSubgroups": hide_unused_groups_and_subgroups,
            "subsidiariesInRows": False,
            "subsidiariesInColumns": False,
            "isConsolidateEng": False,
            "periodId": engagement_id,         # the real engagementId
            "journalEntryDetails": journal_entry_details,
            "showClassifiedReport": show_classified_report,
            "IncludeSumOfAccountGroups": True if include_sum_of_account_groups else None,
        },
        "fundSettings": fund_settings,
    }
    return http_runner.build_xhr_call(
        "POST", f"{WB}/v1/trialbalancereport/createReports", headers, body
    )


def build_fund_settings(funds) -> dict | None:
    """fundSettings sub-object for the TB createReports body (fund engagements).

    funds='default'/None → None (omit fund scoping — non-fund engagements)
    funds='all'          → include all current and future funds
    funds='none'         → run a fund engagement as a normal (non-fund) TB
    funds=[fundId, ...]  → include only those funds (internal ids from
                           scripts.funds.list_funds -> 'id' / fundaccountmap)

    Wire shapes captured + validated live 2026-05-31 (all 3 modes POST 200);
    byte-for-byte spec: references/config/fund_settings.json. fundOptions is
    pinned to 'fundsInRows' (CCH ignores the value — confirmed inert).
    Restored 2026-07-07: the function was dropped in a rebuild while its spec
    and validation record survived. JE reports take no fund options — leave
    create_je_report's fundSettings null.
    """
    if funds in (None, "default"):
        return None
    base = {"fundOptions": "fundsInRows", "fundsIncluded": [],
            "doNotIncludeFunds": False, "includeSelectedFunds": False,
            "includeCurrentandFutureFunds": False}
    if funds == "all":
        base["includeCurrentandFutureFunds"] = True
        return base
    if funds == "none":
        base["doNotIncludeFunds"] = True
        return base
    if isinstance(funds, (list, tuple)) and funds:
        base["fundsIncluded"] = [int(f) for f in funds]
        base["includeSelectedFunds"] = True
        return base
    raise ValueError(
        f"funds must be 'default'/None, 'all', 'none', or a non-empty list of "
        f"fund ids, got {funds!r}"
    )


def create_je_report(
    client_id: int | str,
    engagement_id: int | str,
    report_name: str,
    headers: dict,
    *,
    report_index: str = "",
    je_types: tuple[str, ...] = ("AJE",),
    combined: bool = False,
    combined_postfix: str | None = None,
) -> str:
    """JS for: POST workbench-api/v1/JournalEntryReport.

    `je_types`: any subset of JE_TYPE_IDS keys — 'AJE', 'TJE', 'PAJE', 'RJE'.
    `combined=False` → SeparateReports: one workpaper per type, each named
                       '{report_name}_{TYPE}' (e.g. 'AJEs_AJE', 'AJEs_RJE').
    `combined=True`  → CombinedReports: single workpaper containing all
                       selected types. Wire shape is
                       `[{"postFix": <combined_postfix>, "jeTypes": [...ids]}]`.
                       `combined_postfix` overrides the report-name suffix
                       (default null → CCH picks one).

    Body field `engagementId` carries clientId. `periodId` carries the
    engagementId.
    """
    unknown = [t for t in je_types if t not in JE_TYPE_IDS]
    if unknown:
        raise ValueError(
            f"unknown je_types {unknown}; legal values: {sorted(JE_TYPE_IDS)}"
        )
    ids = [JE_TYPE_IDS[t] for t in je_types]
    body = {
        "engagementId": client_id,            # misnamed — carries clientId
        "reportGuid": None,
        "periodId": engagement_id,
        "reportIndex": report_index,
        "reportName": report_name,
        "SeparateReports": [] if combined else ids,
        "CombinedReports": (
            [{"postFix": combined_postfix, "jeTypes": ids}] if combined else []
        ),
        "fundSettings": None,
    }
    return http_runner.build_xhr_call(
        "POST", f"{WB}/v1/JournalEntryReport", headers, body
    )


# ──────────────────────────────────────────────────────────────────────────
# Listing operations (verification + status)
# ──────────────────────────────────────────────────────────────────────────

def list_tb_reports(client_id: int | str, headers: dict) -> str:
    """JS for: GET workbench-api/v1/trialbalancereport/tbreports/{clientId}.

    Response is an array of {reportId, reportName, reportGuid, reportIndex,
    engagementId, engagementGuid}. Use after a create POST to confirm the new
    reportGuid appears.
    """
    return http_runner.build_xhr_call(
        "GET", f"{WB}/v1/trialbalancereport/tbreports/{client_id}", headers
    )


def list_je_reports(client_id: int | str, headers: dict) -> str:
    """JS for: GET workbench-api/v1/JournalEntryReport/{clientId}.

    Response shape mirrors list_tb_reports. SeparateReports POSTs produce one
    entry per type, named '{report_name}_{TYPE}'.
    """
    return http_runner.build_xhr_call(
        "GET", f"{WB}/v1/JournalEntryReport/{client_id}", headers
    )


# ──────────────────────────────────────────────────────────────────────────
# Pre-flight: quotas + enums
# ──────────────────────────────────────────────────────────────────────────

def tb_report_settings(headers: dict) -> str:
    """JS for: GET workbench-api/v1/trialbalancereport/reporttypesandsettings.

    Returns the global enum dictionary for the TB create body:
    trialBalanceReportTypes, trialBalanceReportSettings,
    trialBalanceReportSelection. No clientId in URL — same enum for all
    engagements.
    """
    return http_runner.build_xhr_call(
        "GET", f"{WB}/v1/trialbalancereport/reporttypesandsettings", headers
    )


def check_tb_report_limit(client_id: int | str, headers: dict) -> str:
    """JS for: GET workbench-api/v1/trialbalancereport/{clientId}/checktbreportlimit.

    TB quota check. Shape mirrors can_create_je (count, limit, canCreate).
    """
    return http_runner.build_xhr_call(
        "GET", f"{WB}/v1/trialbalancereport/{client_id}/checktbreportlimit", headers
    )


def can_create_je(client_id: int | str, headers: dict) -> str:
    """JS for: GET workbench-api/v1/JournalEntryReport/{clientId}/cancreate.

    Returns {count, limit, canCreate}. JE limit observed at 100 per engagement.
    """
    return http_runner.build_xhr_call(
        "GET", f"{WB}/v1/JournalEntryReport/{client_id}/cancreate", headers
    )


# ──────────────────────────────────────────────────────────────────────────
# Leadsheet helpers
# ──────────────────────────────────────────────────────────────────────────

def build_leadsheet_columns(
    current_period_id: int,
    current_end_date: str,
    client_id: int,
    *,
    prior_period_id: int | None = None,
    prior_end_date: str | None = None,
) -> list[dict]:
    """Build the firm-standard leadsheet column set (TWO Remarks columns —
    locked 2026-07-09, supersedes the single-REF-column layout from 2026-06-04).

    Layout (TB-report leadsheet, the firm's DEFAULT surface — protocol B in
    annotate-tbreport.md's two-protocol split):
      1. UNADJ    — Unadjusted Balance (CY)
      2. AJE      — Adjusted Journal Entry (CY)
      3. RJE      — Reclassifying Journal Entry (CY)
      4. FINAL    — Final Balance (CY)
      5. Remarks_1 — NAMED "REF"   ← cross-references / index refs / "imm" tags /
                     tickmark-style annotations. Requires engagementId = clientId.
      6. Remarks_2 — NAMED "Notes" ← free notes. Requires engagementId = clientId.
      7. FINAL    — Final Balance (PY) — ONLY when a comparative TB exists
                    (pass prior_period_id + prior_end_date; omit both otherwise).
                    Always comes AFTER both Remarks columns.

    TWO editable Remarks columns are now the firm standard for TB-report leads:
    REF (cross-refs/index/imm) and Notes (free notes) — both live IN THE COLUMNS,
    not as bubble comments. Bubble comments (annotate-leadsheet.md) remain the
    write surface for the OTHER protocol — the system-generated leadsheet — and
    mirror read-only onto TB reports; they are not used for TB-report notes.

    client_id goes into each Remarks column's engagementId field (CCH naming
    quirk) — set on BOTH Remarks columns, omitted from every other column.
    Remarks_1 → tbreportcomment columnId 1; Remarks_2 → columnId 2 (positional,
    rename-proof — captured 2026-06-04, reconfirmed 2026-07-09).

    `order` stays sequential 1..6 (no PY column) or 1..7 (with PY column) —
    the PY Final column's order shifts to 7 only when it is included.
    """
    cy = {"periodId": current_period_id, "periodEndDate": current_end_date, "isDeleted": False}
    cols = [
        {**cy, "id": "Unadjusted_Current", "type": "Unadjusted", "name": "Unadjusted Balance",          "abbrev": "UNADJ", "variance": None, "order": 1},
        {**cy, "id": "Aje_Current",        "type": "Aje",        "name": "Adjusted Journal Entry",      "abbrev": "AJE",   "variance": None, "order": 2},
        {**cy, "id": "Rje_Current",        "type": "Rje",        "name": "Reclassifying Journal Entry", "abbrev": "RJE",   "variance": None, "order": 3},
        {**cy, "id": "Final_Current",      "type": "Final",      "name": "Final Balance",               "abbrev": "FINAL", "variance": None, "order": 4},
        {**cy, "id": "Remarks_1",          "type": "Remarks",    "name": "REF",                         "abbrev": "RM1",   "variance": None, "order": 5, "engagementId": client_id},
        {**cy, "id": "Remarks_2",          "type": "Remarks",    "name": "Notes",                       "abbrev": "RM2",   "variance": None, "order": 6, "engagementId": client_id},
    ]
    if prior_period_id is not None and prior_end_date is not None:
        py = {"periodId": prior_period_id, "periodEndDate": prior_end_date, "isDeleted": False}
        cols.append({**py, "id": "Final_PriorPeriod_1", "type": "Final", "name": "Final Balance",
                     "abbrev": "FINAL", "variance": None, "order": 7})
    return cols


def add_remarks_column(client_id: int, engagement_guid: str, report_guid: str,
                       current_settings: dict, headers: dict,
                       name: str = "REF") -> str:
    """Build JS for PATCH /v1/trialbalancereport/editReports — add a Remarks
    column to an EXISTING report. Live-captured 2026-06-04.

    The firm standard is TWO Remarks columns on a TB-report leadsheet — "REF"
    (cross-refs/index/imm tags) and "Notes" (free notes), see
    build_leadsheet_columns. Call this ONCE per missing column when retrofitting
    an existing report that lacks one or both: `name="REF"` for the first,
    `name="Notes"` for the second (this function auto-assigns the next free
    Remarks_{N} regardless of `name` — call it twice to add both).

    current_settings = the full tbreportedit GET response body for this report (REQUIRED —
    the PATCH body must carry the complete createReports-shaped settings + ALL columns;
    a column omitted from the array is REMOVED). This function appends Remarks_{N} with
    the next free N, names it `name`, sets engagementId=client_id (CCH quirk), and
    re-emits everything else unchanged.

    Rename = change `name` on the entry and re-PATCH. Remove = omit the entry.
    The page must be RELOADED after for columns to render; tbreportcomment columnId for
    Remarks_{N} is N (positional, rename-proof).
    """
    import copy
    body = copy.deepcopy(current_settings)
    body["engagementGuid"] = engagement_guid
    body["engagementId"] = client_id          # naming gotcha: carries clientId
    body["reportGuid"] = report_guid
    fmt = body.setdefault("reportFormat", {})
    cols = fmt.setdefault("columns", [])
    import re as _re
    existing_n = [int(m.group(1)) for c in cols
                  for m in [_re.match(r"Remarks_(\d+)$", str(c.get("id") or ""))] if m]
    n = (max(existing_n) + 1) if existing_n else 1   # max+1, NOT count+1 (count collides after a removal)
    # current period id: from a CURRENT-period column only (PY columns also carry periodId)
    cy_cols = [c for c in cols
               if c.get("periodId") and "_PriorPeriod" not in str(c.get("id") or "")]
    if not cy_cols:
        raise ValueError("current_settings has no columns with periodId — fetch tbreportedit first; "
                         "if columns is [] the report uses CCH defaults and the FULL default column "
                         "set must be built explicitly (build_leadsheet_columns) before adding REF.")
    ref_col = {"id": f"Remarks_{n}", "type": "Remarks", "name": name, "abbrev": f"RM{n}",
               "variance": None, "order": (max(c.get("order", 0) for c in cols) + 1),
               "periodId": cy_cols[0]["periodId"], "periodEndDate": cy_cols[0].get("periodEndDate"),
               "isDeleted": False, "engagementId": client_id}
    cols.append(ref_col)
    from . import http_runner
    url = "https://workbench-api.cchaxcess.com/v1/trialbalancereport/editReports"
    return http_runner.build_xhr_call("PATCH", url, headers, body)


def group_by_leadsheet(
    groups: list[dict],
    income_range: tuple[int, int] = (4000, 4999),
    expense_range: tuple[int, int] = (5000, 5999),
) -> list[dict]:
    """Partition a flat financial-group list into leadsheet sections.

    Rules (derived from Kymera EBP, 2026-05-28):
      - Groups whose index falls in income_range  → one section, keyed at income_range[0]
      - Groups whose index falls in expense_range → one section, keyed at expense_range[0]
      - All other groups → section key = floor(index / 100) * 100
        (so 1101 and 1102 both roll up under 1100, 1201 under 1200, etc.)

    Returns a list of section dicts, each with:
      {
        "section_index": str,     # e.g. "1100", "4000"
        "section_name":  str,     # name of the lowest-order group in the section
        "group_ids":     list[int],
      }
    sorted by section_index ascending.
    """
    income_lo,  income_hi  = income_range
    expense_lo, expense_hi = expense_range

    sections: dict[int, dict] = {}
    for g in sorted(groups, key=lambda x: int(x["index"])):
        idx = int(g["index"])
        if income_lo <= idx <= income_hi:
            key = income_lo
        elif expense_lo <= idx <= expense_hi:
            key = expense_lo
        else:
            key = (idx // 100) * 100

        if key not in sections:
            sections[key] = {"section_index": str(key), "section_name": g["name"], "group_ids": []}
        sections[key]["group_ids"].append(g["financialGroupId"])

    return sorted(sections.values(), key=lambda s: int(s["section_index"]))


# ──────────────────────────────────────────────────────────────────────────
# Discovery helpers — make groups=[...] / grouping_list_id usable
# ──────────────────────────────────────────────────────────────────────────

def get_grouping_lists(client_id: int | str, headers: dict) -> str:
    """JS for: GET financialprep-api/v1.0/financialgrouptemplate/engagement/{clientId}.

    Returns the engagement's available grouping lists (report-flow picker). Pass
    one's id as `grouping_list_id` to create_tb_report. NOTE: this is the
    report-flow endpoint; to check whether a grouping list EXISTS on the
    engagement, use scripts.groups.list_financial_lists (financialList) — see
    architecture.md, AX-04.
    """
    return http_runner.build_xhr_call(
        "GET", f"{FP}/v1.0/financialgrouptemplate/engagement/{client_id}", headers
    )


def get_financial_groups(
    client_id: int | str, grouping_list_id: int | str, headers: dict
) -> str:
    """JS for: GET financialprep-api/v1.0/FinancialGroup/{clientId}/{groupingListId}.

    Returns the financial groups for a grouping list — use to pick group IDs
    for the `groups=[...]` argument of create_tb_report.
    """
    return http_runner.build_xhr_call(
        "GET", f"{FP}/v1.0/FinancialGroup/{client_id}/{grouping_list_id}", headers
    )
# <!-- END -->
