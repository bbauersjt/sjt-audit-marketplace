"""Load and query references/taxonomy.json - the binder taxonomy.

The taxonomy is data, not code: section lists, keyword rules, perm-file and
samples handling all live in taxonomy.json so the firm can retune them without
editing this skill. This module just reads and answers questions about it.

See ../references/architecture.md.
"""
import json
import os

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAXONOMY_PATH = os.path.join(SKILL_ROOT, "references", "taxonomy.json")


def load(path=None):
    """Load taxonomy.json. Raises if missing - the skill cannot run without it."""
    with open(path or TAXONOMY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def client_type_keys(taxonomy):
    """The defined client-type keys, e.g. ['standard', 'ebp']."""
    return list(taxonomy.get("client_types", {}).keys())


def default_client_type(taxonomy):
    """The client type flagged is_default (fallback 'standard')."""
    for k, v in taxonomy.get("client_types", {}).items():
        if v.get("is_default"):
            return k
    return "standard"


def resolve_client_type(taxonomy, client_name, hint=None):
    """Best-guess the client type from the client/engagement name.

    `hint` - if the caller already knows ('ebp' / 'standard'), it wins.
    Otherwise match each type's detect_keywords against the lowercased name;
    first type with a hit wins. No hit -> the default type.

    This is only a GUESS - the organize module shows it to the user for
    confirmation before anything is filed.
    """
    if hint and hint in taxonomy.get("client_types", {}):
        return hint
    name = (client_name or "").lower()
    for key, ct in taxonomy.get("client_types", {}).items():
        for kw in ct.get("detect_keywords", []):
            if kw.lower() in name:
                return key
    return default_client_type(taxonomy)


def sections(taxonomy, client_type):
    """[(index, name), ...] - the regular workflow + substantive sections for a
    client type. Does NOT include Perm File (9000) or Single Audit (8000) -
    those are handled specially (see perm_file / single_audit in taxonomy.json).
    """
    ct = taxonomy["client_types"][client_type]
    return [tuple(s) for s in ct.get("sections", [])]


def folder_name(taxonomy, index, name):
    """'0200' + 'Planning' -> '0200 Planning'. A None index (the catch-all)
    returns the bare name, so 'Other' has no number and sorts last."""
    if index is None:
        return name
    return taxonomy.get("folder_name_format", "{index} {name}").format(
        index=index, name=name)


def all_destination_folders(taxonomy, client_type, single_audit=False):
    """Every section folder name that COULD exist for this client type, in
    index order. For display only - real folders are created sparsely, when a
    file actually lands in them."""
    out = [folder_name(taxonomy, i, n) for i, n in sections(taxonomy, client_type)]
    if single_audit:
        i, n = taxonomy["single_audit"]["section"]
        out.append(folder_name(taxonomy, i, n))
    pf = taxonomy["perm_file"]
    out.append(folder_name(taxonomy, pf["index"], pf["name"]))
    out.append(taxonomy["catch_all"]["name"])
    return out
