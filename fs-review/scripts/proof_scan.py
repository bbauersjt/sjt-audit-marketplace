"""Deterministic proof scan — mechanizes the text-layer checks of the proof review.

The model adjudicates this output instead of trying to notice inconsistencies across
60 pages by reading. Candidates are CANDIDATES: several checks have legitimate
explanations (a "2019" in a debt-issuance date is fine; "the Company" and "the Plan"
can coexist in an EBP sponsor note). Every candidate carries page + excerpt so
adjudication is a lookup, not a re-read.

Checks:
  toc              TOC entries vs printed page numbers vs actual page content
  page-numbers     printed page number sequence (gaps, duplicates, style)
  notes            note heading sequence (gaps/dupes/order) + every "Note X" reference
                   resolves to an existing note + continuation markers inventory
  entity-refs      distribution of collective entity references (the Company/LLC/...)
  possessive       Auditor's vs Auditors' mixed usage
  serial-comma     mixed serial-comma convention
  casing           repeated headings/labels appearing with different capitalization
  years            year histogram + stale (< PY) and future years with context
  draft-markers    DRAFT / TBD / bracket placeholders / #REF! / XX,XXX etc.
  date-formats     mixed date styles (December 31, 2025 vs Dec. 31, 2025 vs 12/31/25)
  number-style     per-table parens vs minus for negatives (needs --statements)
  fonts            text runs in a font/size rare for the document (cut-paste artifacts)
  spelling         high-confidence misspellings (lowercase, infrequent, not in the
                   accounting whitelist; needs pyspellchecker, else skipped with note)

Usage:
  python proof_scan.py <package.pdf> --cy 2025 [-o proof_scan.json]
                       [--statements statements.json]
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fslib import save_json


def get_pages(pdf_path):
    """One pass: page texts + font runs. A run is consecutive chars sharing
    (fontname, size); rare runs are cut-paste / un-styled-edit candidates."""
    import pdfplumber
    pages, page_runs = [], []
    font_counter = Counter()
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            pages.append((i, page.extract_text() or ""))
            runs, cur_key, cur_text = [], None, []
            for ch in page.chars:
                key = (ch.get("fontname", ""), round((ch.get("size") or 0) * 2) / 2)
                font_counter[key] += 1
                if key == cur_key:
                    cur_text.append(ch.get("text", ""))
                else:
                    if cur_key is not None:
                        runs.append((cur_key, "".join(cur_text)))
                    cur_key, cur_text = key, [ch.get("text", "")]
            if cur_key is not None:
                runs.append((cur_key, "".join(cur_text)))
            page_runs.append((i, runs))
    return pages, font_counter, page_runs


def _font_family(fontname):
    """Normalize to a family: strip subset prefix and weight/style suffixes so
    headings (bold, larger sizes) of the document's own family never flag."""
    base = (fontname or "").split("+")[-1]
    base = re.sub(r"[-,]?(Bold|Italic|Oblique|Light|Medium|Semibold|Black|Regular|"
                  r"BoldItalic|It|MT|PS)+$", "", base, flags=re.IGNORECASE)
    return base.lower()


def check_fonts(font_counter, page_runs, cands):
    total = sum(font_counter.values()) or 1
    fam_counter = Counter()
    for (fname, _), n in font_counter.items():
        fam_counter[_font_family(fname)] += n
    rare_fams = {f for f, n in fam_counter.items() if n / total < 0.02}
    profile = {f: n for f, n in fam_counter.most_common(6)}
    emitted = 0
    for pno, runs in page_runs:
        for key, text in runs:
            alpha = re.sub(r"[^A-Za-z]", "", text)
            # sentence-length runs only: short runs are titles/superscripts, not
            # cut-paste artifacts
            if _font_family(key[0]) in rare_fams and len(alpha) >= 20:
                if emitted < 15:
                    cands.append(_cand(
                        "fonts", pno,
                        f"text in {key[0].split('+')[-1]} {key[1]}pt — rare for this "
                        f"document (<1% of characters); possible pasted/un-styled text",
                        text))
                emitted += 1
    if emitted > 15:
        cands.append(_cand("fonts", 0, f"{emitted - 15} more rare-font runs "
                           f"suppressed — rerun with fonts check if needed"))
    return {"dominant_fonts": profile}


ACCT_WHITELIST = {
    "asc", "asu", "fasb", "gasb", "gaap", "gagas", "aicpa", "erisa", "upmifa",
    "sefa", "opeb", "cecl", "ebitda", "sofp", "acfr", "cafr", "hud", "usda",
    "subrecipient", "subrecipients", "subaward", "subawards", "grantor", "grantors",
    "payor", "payors", "interfund", "intraentity", "postemployment", "postretirement",
    "unamortized", "undiscounted", "uncollectible", "overbillings", "underbillings",
    "retainage", "carryforward", "carryforwards", "noncontrolling", "noncurrent",
    "nonspendable", "unassigned", "decommissioning", "derecognition", "remeasurement",
    "reclassifications", "unobservable", "nonfinancial", "multiemployer",
    "nonqualified", "paydown", "paydowns", "netted", "accreted", "sublease",
    "subleases", "leasehold", "chargebacks", "disaggregation", "presentational",
    "payables", "prepaids", "accruals", "rollforward", "rollforwards", "drawdown",
    "drawdowns", "remittances", "recoupment", "truing", "unbilled", "unvested",
    "nonvested", "forfeitures", "curtailments", "attributions", "expensed",
    "expensing", "utilizations", "withholdings", "accrete", "amortizations",
    "designations", "restrictively", "unexpended", "unspent", "reperformance",
}


def check_spelling(pages, cands, profile):
    try:
        from spellchecker import SpellChecker
    except ImportError:
        profile["spelling"] = "SKIPPED — pyspellchecker not installed"
        return
    spell = SpellChecker()
    occ = defaultdict(list)  # word -> [(page, ctx)]
    for pno, text in pages:
        for m in re.finditer(r"\b[a-z]{5,}\b", text):
            w = m.group(0)
            if w in ACCT_WHITELIST:
                continue
            ctx = text[max(0, m.start() - 50):m.end() + 50].replace("\n", " ")
            occ[w].append((pno, ctx))
    infrequent = [w for w, o in occ.items() if len(o) <= 3]
    unknown = spell.unknown(infrequent)
    emitted = 0
    for w in sorted(unknown):
        if emitted >= 25:
            cands.append(_cand("spelling", 0,
                               f"{len(unknown) - 25} more unknown words suppressed"))
            break
        pno, ctx = occ[w][0]
        sugg = spell.correction(w)
        cands.append(_cand("spelling", pno,
                           f'possible misspelling "{w}"'
                           + (f' (did you mean "{sugg}"?)' if sugg and sugg != w
                              else ""), ctx))
        emitted += 1
    profile["spelling"] = f"{len(unknown)} unknown infrequent words"


def _lines(text):
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def _cand(check, page, detail, excerpt=""):
    return {"check": check, "page": page, "detail": detail, "excerpt": excerpt[:160]}


# ---------- printed page numbers ----------

PAGENUM_RE = re.compile(r"^\s*[-–—]?\s*(\d{1,3})\s*[-–—]?\s*$")


def printed_page_map(pages):
    """pdf page -> printed page number (from an isolated number in top/bottom lines)."""
    mapping = {}
    for pno, text in pages:
        lns = _lines(text)
        for ln in (lns[:2] + lns[-2:]) if lns else []:
            m = PAGENUM_RE.match(ln)
            if m:
                mapping[pno] = int(m.group(1))
                break
    return mapping


def check_page_numbers(pages, cands):
    mapping = printed_page_map(pages)
    nums = [mapping[p] for p in sorted(mapping)]
    for a, b, pa, pb in zip(nums, nums[1:], sorted(mapping), sorted(mapping)[1:]):
        if b != a + 1:
            cands.append(_cand("page-numbers", pb,
                               f"printed page numbers jump {a} -> {b} "
                               f"(pdf pages {pa} -> {pb})"))
    return mapping


# ---------- TOC ----------

TOC_LINE = re.compile(r"^(.{4,80}?)(?:\.{2,}|\s{3,})\s*(\d{1,3})\s*$")


def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def check_toc(pages, page_map, cands):
    inv = {v: k for k, v in page_map.items()}
    entries = []
    for pno, text in pages[:6]:
        found = [(m.group(1).strip(), int(m.group(2)))
                 for ln in _lines(text) if (m := TOC_LINE.match(ln))]
        if len(found) >= 3:
            entries = [(pno, t, pg) for t, pg in found]
            break
    for toc_page, title, printed in entries:
        target_pdf = inv.get(printed)
        if target_pdf is None:
            cands.append(_cand("toc", toc_page,
                               f'TOC entry "{title}" points to printed page {printed}, '
                               f"but no page carries that printed number"))
            continue
        page_text = _norm(dict(pages)[target_pdf])
        if _norm(title) not in page_text:
            cands.append(_cand("toc", target_pdf,
                               f'TOC entry "{title}" (printed p.{printed}) — matching '
                               f"title not found on that page; verify title/page"))
    return len(entries)


# ---------- notes ----------

NOTE_HEAD = re.compile(r"^\s*NOTE\s+(\d{1,2}|[A-Z])\b\s*[—–\-:.]?\s*(.*)$",
                       re.IGNORECASE)
# "3) Investments" / "10) Long-Term Debt" heading style
NOTE_HEAD_PAREN = re.compile(r"^\s*(\d{1,2})\)\s+([A-Z].*)$")
NOTE_REF = re.compile(r"\bNotes?\s+(\d{1,2}|[A-Z])\b(?!\s*[—–\-:.]?\s*[A-Z]{2,})")
CONTINUED = re.compile(r"\(?\bcontinued\b\)?", re.IGNORECASE)


def check_notes(pages, cands):
    heads = []  # (num, page, title)
    for pno, text in pages:
        for ln in _lines(text):
            m = NOTE_HEAD.match(ln)
            if m and (ln.isupper() or m.group(2)[:1].isupper() or not m.group(2)):
                heads.append((m.group(1).upper(), pno, m.group(2).strip()))
                continue
            m = NOTE_HEAD_PAREN.match(ln)
            if m:
                heads.append((m.group(1), pno, m.group(2).strip()))
    numeric = [(int(n), p, t) for n, p, t in heads if n.isdigit()]
    if numeric:
        seen = Counter(n for n, _, _ in numeric)
        for n, cnt in sorted(seen.items()):
            if cnt > 1:
                pgs = [p for x, p, _ in numeric if x == n]
                cands.append(_cand("notes", pgs[1],
                                   f"Note {n} heading appears {cnt} times "
                                   f"(pages {pgs}) — duplicate or continuation "
                                   f"header without 'continued'"))
        lo, hi = min(seen), max(seen)
        for n in range(lo, hi + 1):
            if n not in seen:
                cands.append(_cand("notes", 0, f"Note {n} is skipped "
                                   f"(sequence runs {lo}..{hi})"))
        order = [n for n, _, _ in numeric]
        dedup = [n for i, n in enumerate(order) if i == 0 or n != order[i - 1]]
        if dedup != sorted(dedup):
            cands.append(_cand("notes", 0, f"note headings out of order: {order}"))
    exists = {n for n, _, _ in heads}
    for pno, text in pages:
        for m in NOTE_REF.finditer(text):
            if m.group(1).upper() not in exists:
                ctx = text[max(0, m.start() - 60):m.end() + 60].replace("\n", " ")
                cands.append(_cand("notes", pno,
                                   f'reference to "Note {m.group(1)}" but no such '
                                   f"note heading exists", ctx))
    cont = [(pno, ln) for pno, text in pages for ln in _lines(text)[:4]
            if CONTINUED.search(ln)]
    return {"note_headings": [{"note": n, "page": p, "title": t} for n, p, t in heads],
            "continuation_markers": [{"page": p, "line": l} for p, l in cont]}


# ---------- conventions ----------

ENTITY_TERMS = ["the Company", "the Organization", "the Corporation", "the Partnership",
                "the LLC", "the District", "the City", "the County", "the Authority",
                "the Plan", "the Association", "the Foundation", "the Church",
                "the School", "the Agency", "the Entity", "the Firm", "the Trust"]


def check_conventions(pages, cands):
    full = "\n".join(t for _, t in pages)
    ent = {t: len(re.findall(re.escape(t) + r"\b", full)) for t in ENTITY_TERMS}
    ent = {k: v for k, v in ent.items() if v}
    majors = {k: v for k, v in ent.items() if v >= 3}
    if len(majors) > 1:
        cands.append(_cand("entity-refs", 0,
                           f"multiple collective entity references in regular use: "
                           f"{majors} — confirm each refers to a distinct party "
                           f"(e.g., Plan vs. sponsor Company is fine; Company vs. "
                           f"LLC for the same entity is a finding)"))
    sing = [(p, m.start()) for p, t in pages for m in re.finditer(r"Auditor's", t)]
    plur = [(p, m.start()) for p, t in pages for m in re.finditer(r"Auditors'", t)]
    if sing and plur:
        cands.append(_cand("possessive", plur[0][0],
                           f"mixed possessive: Auditor's on pages "
                           f"{sorted({p for p, _ in sing})} vs Auditors' on pages "
                           f"{sorted({p for p, _ in plur})}"))
    flat = re.sub(r"\s+", " ", full)  # list phrases wrap across lines
    nodigits = lambda lst: [w for w in lst if not re.search(r"\d", w)]
    with_serial = nodigits(re.findall(r"\w+, \w+, (?:and|or) \w+", flat))
    without = nodigits(re.findall(r"\w+, \w+ (?:and|or) \w+", flat))
    without = [w for w in without if not any(w in s for s in with_serial)]
    if len(with_serial) >= 2 and len(without) >= 2:
        cands.append(_cand("serial-comma", 0,
                           f"mixed serial-comma usage: {len(with_serial)} with vs "
                           f"{len(without)} without — e.g. \"{without[0]}\""))
    return {"entity_refs": ent, "auditor_possessive":
            {"Auditor's": len(sing), "Auditors'": len(plur)}}


# ---------- casing ----------

def _headingish(ln):
    return (2 <= len(ln.split()) <= 8 and len(ln) <= 70 and not ln.endswith(".")
            and not re.search(r"\d{3}", ln) and ln[:1].isalpha())


def check_casing(pages, statements, cands):
    groups = defaultdict(list)  # casefolded -> [(variant, page)]
    for pno, text in pages:
        for ln in _lines(text):
            if _headingish(ln):
                groups[_norm(ln)].append((ln, pno))
    if statements:
        for t in statements.get("tables", []):
            for row in t.get("rows", []):
                lbl = row.get("label", "").strip()
                if lbl and 2 <= len(lbl.split()) <= 8:
                    groups[_norm(lbl)].append((lbl, t.get("page", 0)))
    for key, occ in groups.items():
        variants = defaultdict(list)
        for v, p in occ:
            variants[v].append(p)
        if len(variants) > 1 and sum(len(ps) for ps in variants.values()) >= 3:
            desc = "; ".join(f'"{v}" on pages {sorted(set(ps))[:6]}'
                             for v, ps in variants.items())
            # Title-Case vs Sentence-case pairs are often intentional house style
            # (title-case note headings vs sentence-case line items) — annotate so
            # the adjudicator can batch-dismiss if that is the document's convention
            vs = [v.rstrip(" $") for v in variants]
            titleish = any(v.istitle() or v == v.title() for v in vs)
            sentenceish = any(v[:1].isupper() and v[1:].islower() is False and
                              v != v.title() and not v.isupper() for v in vs)
            note = (" (Title Case vs sentence case — commonly an intentional "
                    "heading-vs-line-item convention; flag only if the document "
                    "is inconsistent about it)" if titleish and sentenceish else "")
            cands.append(_cand("casing", 0,
                               f"same text with different capitalization: {desc}{note}"))


# ---------- years / dates / markers ----------

MONTHS_FULL = r"January|February|March|April|May|June|July|August|September|October|November|December"
MONTHS_ABBR = r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
DRAFT_PATTERNS = [
    (re.compile(r"\bDRAFT\b"), "DRAFT marker"),
    (re.compile(r"\bTBD\b"), "TBD placeholder"),
    (re.compile(r"\bX{2,}[,.]?X*\b"), "XX placeholder figure"),
    (re.compile(r"#(REF|VALUE|NAME|DIV/0)!?"), "Excel error artifact"),
    (re.compile(r"\[[A-Za-z ]{2,30}\]"), "square-bracket fill-in"),
    (re.compile(r"\?{2,}"), "??? placeholder"),
]


def check_years_dates_markers(pages, cy, cands):
    hist = Counter()
    for pno, text in pages:
        for m in re.finditer(r"\b(19|20)\d{2}\b", text):
            yr = int(m.group(0))
            hist[yr] += 1
            ctx = text[max(0, m.start() - 70):m.end() + 40].replace("\n", " ")
            # dating qualifiers PRECEDE a year ("due 2029", "issued in 2019") —
            # search only the leading context so trailing text can't mask a stale year
            before = text[max(0, m.start() - 70):m.end() + 6].replace("\n", " ")
            dated = re.search(
                r"due|matur|through|expir|issued|dated|acquired|adopted|origin|"
                r"effective|ASU|SAS|No\.|since|began|formed|incorporated|payable",
                before, re.IGNORECASE)
            if yr > cy + 1 and not dated:
                cands.append(_cand("years", pno,
                                   f"future year {yr} with no dating context", ctx))
            elif yr < cy - 1 and not dated:
                cands.append(_cand("years", pno,
                                   f"stale year {yr} (CY {cy}) with no dating context "
                                   f"— possible un-rolled prior-year text", ctx))
        for pat, name in DRAFT_PATTERNS:
            for m in pat.finditer(text):
                ctx = text[max(0, m.start() - 50):m.end() + 50].replace("\n", " ")
                cands.append(_cand("draft-markers", pno, name, ctx))
    full = "\n".join(t for _, t in pages)
    fullm = len(re.findall(rf"\b({MONTHS_FULL}) \d{{1,2}}, (19|20)\d{{2}}", full))
    abbrm = len(re.findall(rf"\b({MONTHS_ABBR})\.? \d{{1,2}}, (19|20)\d{{2}}", full))
    slash = len(re.findall(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", full))
    styles = {"month-name": fullm, "abbreviated": abbrm, "slash": slash}
    used = {k: v for k, v in styles.items() if v}
    if len(used) > 1:
        cands.append(_cand("date-formats", 0, f"mixed date formats: {used}"))
    return {"year_histogram": dict(sorted(hist.items())), "date_styles": styles}


# ---------- number style per table ----------

def check_number_style(statements, cands):
    for t in statements.get("tables", []):
        parens = minus = 0
        for row in t.get("rows", []):
            for raw in row.get("raw", []):
                if raw.startswith("(") and raw.endswith(")"):
                    parens += 1
                elif raw.startswith("-") and len(raw) > 1:
                    minus += 1
        if parens and minus:
            cands.append(_cand("number-style", t.get("page", 0),
                               f"table {t['id']}: negatives shown both as parentheses "
                               f"({parens}) and minus signs ({minus})"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--cy", type=int, required=True,
                    help="current fiscal year of the package, e.g. 2025")
    ap.add_argument("--statements", help="statements.json for label/number checks")
    ap.add_argument("-o", "--out", default="proof_scan.json")
    args = ap.parse_args()

    pages, font_counter, page_runs = get_pages(args.input)
    statements = None
    if args.statements:
        from fslib import load_json
        statements = load_json(args.statements)

    cands = []
    page_map = check_page_numbers(pages, cands)
    toc_n = check_toc(pages, page_map, cands)
    notes_info = check_notes(pages, cands)
    conv_info = check_conventions(pages, cands)
    check_casing(pages, statements, cands)
    yd_info = check_years_dates_markers(pages, args.cy, cands)
    if statements:
        check_number_style(statements, cands)
    font_info = check_fonts(font_counter, page_runs, cands)
    conv_info.update(font_info)
    check_spelling(pages, cands, conv_info)

    by_check = Counter(c["check"] for c in cands)
    report = {"source": args.input, "cy": args.cy,
              "summary": {"candidates": len(cands), "by_check": dict(by_check),
                          "toc_entries_checked": toc_n,
                          "printed_pages_mapped": len(page_map)},
              "profile": {**conv_info, **yd_info,
                          "note_headings": notes_info["note_headings"],
                          "continuation_markers": notes_info["continuation_markers"]},
              "candidates": cands}
    save_json(report, args.out)
    print(f"{len(cands)} proof candidates -> {args.out} | by check: {dict(by_check)}")
    for c in cands[:40]:
        print(f"  [{c['check']}] p{c['page']}: {c['detail']}")


if __name__ == "__main__":
    main()
