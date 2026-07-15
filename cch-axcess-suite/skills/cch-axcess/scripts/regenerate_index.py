"""Regenerate SKILL.md Trigger map + references/modules/INDEX.md dispatch
table from each module's YAML front-matter.

SOURCE-REPO TOOL ONLY. Run during a batch rebuild (or any time you add/edit a
module in the source repo). Modules are the source of truth for triggers, leg,
inputs, scripts called. SKILL.md and modules/INDEX.md are derived. At runtime
the install is a read-only cache — there is nothing to regenerate there.

Usage:
    python3 scripts/regenerate_index.py [--check]

--check exits non-zero if regeneration would change either file (CI guardrail).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
MODULES_DIR = SKILL_ROOT / "references" / "modules"
SKILL_MD = SKILL_ROOT / "SKILL.md"
INDEX_MD = MODULES_DIR / "INDEX.md"

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
TRIGGER_MAP_START = "<!-- TRIGGER_MAP_START -->"
TRIGGER_MAP_END = "<!-- TRIGGER_MAP_END -->"
INDEX_TABLE_START = "<!-- INDEX_TABLE_START -->"
INDEX_TABLE_END = "<!-- INDEX_TABLE_END -->"


def _parse_simple_yaml(text: str) -> dict:
    """Minimal YAML reader for the front-matter shape this skill uses.

    Supports: scalar keys, list-of-strings keys. Anything else: raise.
    """
    out: dict = {}
    current_key = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith(" ") or raw.startswith("\t"):
            line = raw.strip()
            if not line.startswith("- "):
                raise ValueError(f"unexpected indented line: {raw!r}")
            if current_key is None:
                raise ValueError(f"orphan list item: {raw!r}")
            val = line[2:].strip().strip('"').strip("'")
            out.setdefault(current_key, []).append(val)
        else:
            if ":" not in raw:
                raise ValueError(f"missing colon: {raw!r}")
            k, _, v = raw.partition(":")
            key = k.strip()
            val = v.strip()
            current_key = key
            if val == "" or val == "[]":
                # bare key (block list follows) OR an inline empty list `key: []`.
                # Must map to [] here — treating "[]" as a scalar string instead
                # gets iterated char-by-char, rendering `[`, `]` in the INDEX.
                out[key] = []
            else:
                # strip a trailing inline comment ("wpm   # what Step 0 warms")
                val = re.sub(r"\s+#.*$", "", val)
                out[key] = val.strip('"').strip("'")
    return out


def _short_summary(module_path: Path, fm: dict) -> str:
    """Derive a short, user-facing trigger description from the front-matter."""
    if "summary" in fm:
        return str(fm["summary"])
    triggers = fm.get("triggers") or []
    if triggers:
        return triggers[0]
    return module_path.stem.replace("-", " ")


def collect_modules(modules_dir: Path = MODULES_DIR) -> list[dict]:
    rows: list[dict] = []
    missing_leg: list[str] = []
    for md in sorted(modules_dir.glob("*.md")):
        if md.name == "INDEX.md":
            continue
        text = md.read_text(encoding="utf-8")
        m = FRONTMATTER_RE.match(text)
        if not m:
            # Skip silently — modules without front-matter aren't part of the
            # generated index yet. Run learn-protocol.md to add it.
            continue
        try:
            fm = _parse_simple_yaml(m.group(1))
        except ValueError as e:
            print(f"WARN: skipping {md.name}: {e}", file=sys.stderr)
            continue
        leg = fm.get("leg") or ""
        if not leg:
            missing_leg.append(md.name)
        rows.append({
            "file": md.name,
            "triggers": fm.get("triggers") or [],
            "leg": leg,
            "inputs": fm.get("inputs") or [],
            "calls": fm.get("calls") or [],
            "status": fm.get("status") or "",
            "summary": _short_summary(md, fm),
        })
    if missing_leg:
        print("WARN: module(s) missing the mandatory `leg:` front-matter "
              f"(wpm|kc|none): {', '.join(missing_leg)}", file=sys.stderr)
    return rows


def render_trigger_map(rows: list[dict], link_prefix: str = "references/modules/") -> str:
    lines = ["| What the user wants | Module |", "|---|---|"]
    for r in rows:
        lines.append(f"| {r['summary']} | `{link_prefix}{r['file']}` |")
    return "\n".join(lines)


def render_index_table(rows: list[dict]) -> str:
    lines = ["| File | Leg | Triggers | Inputs | Calls | Status |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        trig = "; ".join(f'"{t}"' for t in r["triggers"])
        inp = "; ".join(r["inputs"])
        calls = ", ".join(f"`{c}`" for c in r["calls"])
        lines.append(f"| `{r['file']}` | {r['leg']} | {trig} | {inp} | {calls} | {r['status']} |")
    return "\n".join(lines)


def splice(text: str, start: str, end: str, new_block: str) -> str:
    """Replace content between start and end markers, inclusive of markers."""
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    replacement = f"{start}\n{new_block}\n{end}"
    if pattern.search(text):
        return pattern.sub(replacement, text)
    # No markers yet — append at end with a heading.
    return text.rstrip() + f"\n\n## Generated\n\n{replacement}\n"


def regenerate(check: bool) -> int:
    rows = collect_modules()
    if not rows:
        print("No modules with front-matter found. Add front-matter per learn-protocol.md.",
              file=sys.stderr)
        return 1

    trigger_map = render_trigger_map(rows)
    index_table = render_index_table(rows)

    skill_text = SKILL_MD.read_text(encoding="utf-8")
    index_text = INDEX_MD.read_text(encoding="utf-8")

    new_skill = splice(skill_text, TRIGGER_MAP_START, TRIGGER_MAP_END, trigger_map)
    new_index = splice(index_text, INDEX_TABLE_START, INDEX_TABLE_END, index_table)

    skill_changed = new_skill != skill_text
    index_changed = new_index != index_text

    if check:
        if skill_changed or index_changed:
            print("regenerate_index: drift detected (run without --check to fix)",
                  file=sys.stderr)
            return 2
        print("regenerate_index: SKILL.md and modules/INDEX.md in sync.")
        return 0

    if skill_changed:
        SKILL_MD.write_text(new_skill, encoding="utf-8")
        print(f"updated {SKILL_MD.name}")
    if index_changed:
        INDEX_MD.write_text(new_index, encoding="utf-8")
        print(f"updated {INDEX_MD.name}")
    if not (skill_changed or index_changed):
        print("regenerate_index: no changes.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true",
                   help="Exit non-zero if regeneration would change files (CI guardrail).")
    args = p.parse_args()
    return regenerate(check=args.check)


if __name__ == "__main__":
    sys.exit(main())
# <!-- END -->
