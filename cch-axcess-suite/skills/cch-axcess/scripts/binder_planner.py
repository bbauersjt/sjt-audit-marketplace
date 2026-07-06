"""Read binder-program-template xlsx files and compute the set of forms that apply
to an engagement given its condition flags.

Pure Python. No HTTP. The output is fed to scripts.catalog.build_add_forms_body().
"""
import re
from pathlib import Path

import openpyxl

SKILL_ROOT = Path(__file__).parent.parent
DATA_DIR = SKILL_ROOT / "references" / "data"
FORM_ID_RE = re.compile(r"^([A-Z]{3}-\d{3,4}[A-Z]?)\b")

# Templates by client type — extend as new client types get programs
TEMPLATES = {
    "nonprofit":      DATA_DIR / "binder-program-template-nonprofit.xlsx",
    "govt-with-sa":   DATA_DIR / "binder-program-template-govt-with-sa.xlsx",
    "ebp":            DATA_DIR / "binder-program-template-ebp.xlsx",
    # commercial, construction, hoa — to be added
}


def section_for_index(idx: str) -> str | None:
    """Map a form index to its 4-digit binder SECTION index (AX-26).

    Rule: section = first-two-digits * 100 — "0201" -> "0200", "8110" -> "8100" —
    EXCEPT indexes whose hundreds digit rolls into a parent section that the firm
    files flat: "81xx" files to 8000 Single Audit (BT3 B7: the inline FOLDER_MAP
    was missing the "81" entry). Extend EXCEPTIONS as new flat-filed parents appear.
    """
    if not idx or len(idx) < 2:
        return None
    EXCEPTIONS = {"81": "8000"}
    two = idx[:2]
    if two in EXCEPTIONS:
        return EXCEPTIONS[two]
    return two + "00"


def _condition_passes(cond: str | None, flags: dict[str, bool]) -> bool:
    """Conditions look like 'if-single-audit', 'if-new-client', etc. Pass if flag is True or no condition."""
    if not cond:
        return True
    key = cond.replace("if-", "").replace("-", "_")
    return bool(flags.get(key, False))


def plan(client_type: str, flags: dict[str, bool], _return_skipped: bool = False):
    """Return the list of {idx, fid, name, target_folder_idx, cond} rows that apply.

    AX-26: rows that pass the type/section/condition gates but whose NAME doesn't
    match FORM_ID_RE are collected as `skipped` (a form whose id we couldn't parse
    is surfaced, never silently dropped — BT3 B7). With _return_skipped=True the
    return is (rows, skipped); default stays a bare list for back-compat.

    flags keys (default False unless caller sets True):
      single_audit, new_client, firm_prepares_fs,
      cash_receipts_cycle, payroll_cycle, ...  (and so on for other ALC cycles)
    """
    path = TEMPLATES.get(client_type)
    if not path or not path.exists():
        raise ValueError(f"No binder-program template for client_type={client_type!r}")
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    ws = wb["Binder Index"]
    out = []
    skipped = []
    for row in ws.iter_rows(min_row=6, values_only=True):
        if not any(row):
            continue
        # Columns: A=idx, B=name, C=type, D=desc, E=deps, F=notes, G=cond
        idx = (str(row[0]).strip() if row[0] is not None else "")
        name = (str(row[1]).strip() if row[1] is not None else "")
        typ = (str(row[2]).strip() if row[2] is not None else "")
        cond = (str(row[6]).strip() if len(row) > 6 and row[6] is not None else None)
        if idx.startswith("SECTION") or typ != "KC Form":
            continue
        if not _condition_passes(cond, flags):
            continue
        m = FORM_ID_RE.match(name)
        if not m:
            skipped.append({"idx": idx, "name": name, "reason": "name did not match FORM_ID_RE"})
            continue
        out.append({
            "idx": idx,
            "fid": m.group(1),
            "name": name,
            "target_folder_idx": section_for_index(idx),
            "cond": cond,
        })
    return (out, skipped) if _return_skipped else out


def diff_against_unfiled(plan_rows: list[dict], unfiled_items: list[dict]) -> dict:
    """Bucket plan rows into already_in_unfiled / already_filed / to_add.

    unfiled_items: parsed response from wpm.folder_get(folder_id=-4).
    """
    unfiled_by_fid = {}
    for it in unfiled_items:
        m = FORM_ID_RE.match(it.get("name", ""))
        if m:
            unfiled_by_fid[m.group(1)] = it
    already_in_unfiled, to_add = [], []
    for p in plan_rows:
        if p["fid"] in unfiled_by_fid:
            it = unfiled_by_fid[p["fid"]]
            already_in_unfiled.append({**p, "locationId": it.get("locationId"), "documentId": it.get("documentId")})
        else:
            to_add.append(p)
    # Forms already filed elsewhere would need a separate folder-tree scan to detect;
    # caller can compute that if needed. Defaulting to "needs add" if not in Unfiled.
    #
    # AX-26: split to_add into catalog-resolvable vs not. S-suffix (Single Audit)
    # forms resolve from the SA title (catalog.load_sa_title_forms / live
    # GetWorkpaperListForAddForms pull — see kc_title_library.json), NOT the binder's
    # own title. NEVER silently skip an unresolved form — surface `unmatched` to the
    # user by NAME (BT3 B7 silently dropped 22 S-forms).
    from . import catalog as _catalog
    sa_fids = {r["fid"] for r in _catalog.load_sa_title_forms()}
    sa_title_adds = [p for p in to_add if p["fid"] in sa_fids]
    to_add = [p for p in to_add if p["fid"] not in sa_fids]
    return {"already_in_unfiled": already_in_unfiled, "to_add": to_add,
            "sa_title_adds": sa_title_adds}
# <!-- END -->
