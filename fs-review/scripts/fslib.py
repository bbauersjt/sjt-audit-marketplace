"""Shared helpers for the fs-review deterministic pipeline."""
from __future__ import annotations

import json
import re
from pathlib import Path

# Money token: optional $, optional parens (negative), digits with commas, optional decimals,
# optional trailing footnote marker stripped upstream. A bare dash/em-dash is "no value" (None
# placeholder kept so columns stay aligned).
MONEY_RE = re.compile(
    r"""^\$?\s*
        (?P<neg>\()?\s*
        \$?\s*
        (?P<num>\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)
        \s*(?P<negclose>\))?
        \s*%?$""",
    re.VERBOSE,
)
DASH_RE = re.compile(r"^[-–—]+$")


def parse_money(token: str):
    """Return float for a money-like token, 0.0 for a dash placeholder, None if not numeric."""
    t = token.strip()
    if not t:
        return None
    if DASH_RE.match(t):
        return 0.0
    m = MONEY_RE.match(t)
    if not m:
        return None
    val = float(m.group("num").replace(",", ""))
    if m.group("neg") and m.group("negclose"):
        val = -val
    elif m.group("neg") or m.group("negclose"):
        # unbalanced paren — likely split across tokens; treat as negative but flag upstream
        val = -val
    return val


def is_money_token(token: str) -> bool:
    t = token.strip()
    return bool(t) and (MONEY_RE.match(t) is not None or DASH_RE.match(t) is not None)


def fmt(v) -> str:
    if v is None:
        return ""
    if abs(v - round(v)) < 1e-9:
        return f"({abs(v):,.0f})" if v < 0 else f"{v:,.0f}"
    return f"({abs(v):,.2f})" if v < 0 else f"{v:,.2f}"


# "net ..." only for genuine result/total forms — "Net investment in capital assets",
# "Net pension liability" etc. are line items, not totals
TOTAL_WORDS = re.compile(
    r"^\s*(total|subtotal|gross profit|"
    r"net [a-z ]{0,24}(income|loss|earnings|revenue|gain)s?\b|"
    r"net (increase|decrease|change)\b|"
    r"net cash (provided|used)|"
    r"net (assets|position)\s*[,–—-]|"
    r"change in net|end of year|ending balance|"
    r"balance[s]?,?\s+(at\s+)?end)",
    re.IGNORECASE,
)


BEGINNING_RE = re.compile(r"beginning", re.IGNORECASE)


def looks_like_total(label: str) -> bool:
    lbl = label.strip()
    if not lbl:
        return False
    # "Net assets, beginning of year" / "Balance, beginning" are INPUT rows, not totals
    if BEGINNING_RE.search(lbl):
        return False
    if TOTAL_WORDS.match(lbl):
        return True
    # e.g. "TOTAL ASSETS", "TOTAL LIABILITIES AND STOCKHOLDERS' EQUITY"
    if lbl.isupper() and "TOTAL" in lbl:
        return True
    return False


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def save_json(obj, path):
    Path(path).write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")
    return str(path)
