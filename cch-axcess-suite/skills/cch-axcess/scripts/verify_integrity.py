#!/usr/bin/env python3
"""verify_integrity.py — deterministic truncation detector for the cch-axcess skill.

WHY THIS EXISTS
The recurring failure was a critical Markdown file (SKILL.md, architecture.md)
landing on disk truncated — usually because an editing session read the stale,
truncated bash-mount view of a file and wrote that truncated copy back as the
real file. Truncation was then "detected" by human judgment, which is slow and
unreliable.

THE GUARD
Every sentinel-protected file ends with a fixed marker line:

    <!-- END -->

Code files carry it as a trailing comment: `# <!-- END -->` (.py) or
`// <!-- END -->` (.js). This matters for .py especially — a truncation that
lands inside a trailing comment block still COMPILES (kc.py shipped that way
on 2026-06-04), so the marker is the only deterministic tell.

A write that gets cut off cannot land the marker, so a missing marker == the
file is truncated. This script checks the marker (and a per-file minimum byte
floor as a second signal) for every path listed in the manifest.

Run it as the LAST step of any editing session, and from the learn-protocol
exit checklist. Exit code is nonzero if anything fails, so it can gate a deploy.

CAVEAT — run this where file reads are TRUE. In an active Cowork editing session
the `mcp__workspace__bash` mount can serve a STALE/truncated snapshot of a file
that was just edited via the host tools, which makes this script false-FAIL on a
file that is actually complete on disk. The host `Read` tool is the arbiter. If
this script reports a failure mid-edit, host-Read the file's tail before believing
it. In a fresh/settled session (the real deploy target) bash reads are true and
this gate is reliable.

USAGE
    python3 scripts/verify_integrity.py            # check every manifested file
    python3 scripts/verify_integrity.py --stamp F  # append the END marker to F
                                                    # (ONLY after host-Read shows F complete)
                                                    # and add F to the manifest

NEVER --stamp a file you have not confirmed complete via the host Read tool.
Stamping a truncated file blesses the truncation as "complete" and defeats the
guard. The manifest only lists files a human/agent has verified intact.
"""
import sys
import os

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(SKILL_ROOT, "references", "integrity-manifest.txt")
MARKER = "<!-- END -->"
# Per-file byte floor: a file far under its known size is suspect even if the
# marker somehow survived. 0 = marker-only check.
MIN_BYTES = 200


def _manifest_paths():
    if not os.path.exists(MANIFEST):
        return []
    out = []
    with open(MANIFEST, encoding="utf-8") as fh:
        for line in fh:
            rel = line.strip()
            if rel and not rel.startswith("#"):
                out.append(rel)
    return out


def check():
    rels = _manifest_paths()
    if not rels:
        print("integrity: manifest empty or missing — nothing protected yet.")
        print(f"  manifest: {MANIFEST}")
        return 0
    failures = []
    for rel in rels:
        path = os.path.join(SKILL_ROOT, rel.replace("/", os.sep))
        if not os.path.exists(path):
            failures.append((rel, "MISSING FILE"))
            continue
        raw = open(path, "rb").read()
        if b"\x00" in raw:
            n = raw.count(b"\x00")
            failures.append((rel, f"NULL BYTES ({n}) — overlay-install/mount corruption"))
            continue
        data = raw.decode("utf-8")
        size = len(raw)
        tail = data.rstrip().splitlines()[-1].strip() if data.strip() else ""
        ok_tails = (MARKER, "# " + MARKER, "// " + MARKER)  # .py/.js carry it as a comment
        if tail not in ok_tails:
            failures.append((rel, f"NO END MARKER (last line: {tail!r:.60})"))
        elif size < MIN_BYTES:
            failures.append((rel, f"under {MIN_BYTES}B floor ({size}B) — likely truncated"))
    # Null-byte sweep over ALL skill .py/.md/.json files (not just manifested):
    # the installer overlay defect (2026-06-03) zero-pads any file that SHRANK
    # between versions, and Python refuses to import a NUL-containing source.
    import glob
    for pattern in ("scripts/**/*.py", "references/**/*.md", "references/**/*.json", "SKILL.md"):
        for path in glob.glob(os.path.join(SKILL_ROOT, pattern), recursive=True):
            rel = os.path.relpath(path, SKILL_ROOT).replace(os.sep, "/")
            if rel in rels:
                continue  # already checked above
            raw = open(path, "rb").read()
            if b"\x00" in raw:
                nb = raw.count(b"\x00")
                failures.append((rel, f"NULL BYTES ({nb}) — overlay-install/mount corruption"))
    print(f"integrity: checked {len(rels)} manifested file(s) + null-byte sweep.")
    for rel, why in failures:
        print(f"  FAIL  {rel}  —  {why}")
    if not failures:
        print("  all OK — every protected file ends with the END marker.")
        return 0
    print(f"\n{len(failures)} file(s) FAILED. Do NOT deploy. Host-Read each failing")
    print("file; if its tail really is cut, restore from _skill-backups/ and re-verify.")
    print("NULL-BYTE failures after a skill install = the installer overlay defect:")
    print("uninstall (delete the cached skill folder) and reinstall fresh — never")
    print("install a .skill over an existing copy.")
    return 1


def stamp(rel):
    path = os.path.join(SKILL_ROOT, rel.replace("/", os.sep))
    if not os.path.exists(path):
        print(f"stamp: no such file: {path}")
        return 1
    data = open(path, encoding="utf-8").read()
    ok_tails = (MARKER, "# " + MARKER, "// " + MARKER)
    if data.rstrip().splitlines()[-1].strip() in ok_tails:
        print(f"stamp: {rel} already ends with the marker.")
    else:
        prefix = "# " if rel.endswith(".py") else ("// " if rel.endswith(".js") else "")
        sep = "" if data.endswith("\n") else "\n"
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(sep + prefix + MARKER + "\n")
        print(f"stamp: appended END marker to {rel}.")
    rels = _manifest_paths()
    if rel not in rels:
        with open(MANIFEST, "a", encoding="utf-8") as fh:
            fh.write(rel + "\n")
        print(f"stamp: added {rel} to the manifest.")
    return 0


# [recovery 2026-06-01: stamp() tail + main() reconstructed from docstring USAGE spec; verify]
def main(argv):
    if len(argv) >= 2 and argv[0] == "--stamp":
        return stamp(argv[1])
    return check()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
# <!-- END -->
