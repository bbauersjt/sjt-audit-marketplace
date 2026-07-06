---
summary: Exec cache — run skill scripts from a per-build verified /tmp copy, never the truncating mount; recover a short read via rename round-trip then host-Read/.bin-extract
triggers:
  - "(internal) consulted from SKILL.md Step 4 / exec cache before running any scripts/*.py"
status: foundation
---
# Runbook — Exec Cache (per-BUILD verified copy; never run from the mount)

**Why this exists.** The bash sandbox reaches this install through a mount
(`…/mnt/.claude/skills/cch-axcess`). That mount serves **text files truncated** —
cut at a stale byte length, mid-line, mid-token — while serving **binary files
(zip/xlsx) intact**. Confirmed live 2026-06-04: all 16 `.py` files corrupt through
the mount, all 7 `.xlsx` and every zip intact, while host `Read` showed every file
complete on disk. So `python3` against the mount can run corrupt code, and
`cat`/`grep`/`cp` against it can return corrupt text. Host `Read` is the **arbiter
of truth** for file content; the mount is transport only — trustworthy ONLY for
binaries.

**What changed vs the per-session procedure:** the verified copy is now cached
**per build**, keyed by payload version + hash. Verification (compile gate +
`verify_integrity.py`) runs ONCE per build, not once per session.

## Procedure (first action of any task that will RUN skill scripts)

1. **Compute the cache key from the payload binary** (binaries survive the mount):

   ```bash
   PAYLOAD="<mount-path-to>/cch-axcess/exec-payload_AX-36.bin"   # version in the filename
   VER=$(basename "$PAYLOAD" | sed 's/exec-payload_\(.*\)\.bin/\1/')
   HASH=$(sha256sum "$PAYLOAD" | cut -c1-12)
   EXEC=/tmp/cch-ax-${VER}-${HASH}
   ```

   The payload filename is **versioned per build** and must match the top CHANGELOG
   entry. Missing payload = install predates this mechanism → fallback R below.

2. **Cache hit → use it, zero verify.** If `$EXEC/.verified` exists and is readable
   by you, the copy was already gated this build — run from it immediately. Skip
   steps 3–4.

3. **Cache miss / hash mismatch / uid-locked → fresh extract.** (A prior session's
   dir you can't write into counts as uid-locked — make a fresh dir by appending
   `-$(id -u)` or a timestamp.)

   ```bash
   mkdir -p $EXEC && cd $EXEC && unzip -q "$PAYLOAD"
   ```

4. **Full gate, ONCE per build.** `py_compile` every `.py`, `json.load` every
   `.json` — write the few-line checker fresh into `/tmp`, do NOT source it from
   the mount. Then `python3 $EXEC/scripts/verify_integrity.py` IN THE COPY. Pass →
   `touch $EXEC/.verified`. Any failure = stop loudly and use fallback R for the
   failing files; never run anything that failed the gate, and never write
   `.verified` on a failed gate.

5. **Run everything from `$EXEC`.** All `python3` invocations, all `sys.path`
   imports, every `cat`-into-JS — from the copy, never the mount path.

6. **The exec copy is disposable scratch.** Nothing is ever written into the
   install; deliverables go to the user's folder; findings go to the complaint log.

## Fast cache-bust — when the DISK is correct but the mount view is stale (the common case)

A bash read showing a truncated tail almost always means the **disk is complete and the
virtiofs page cache is stale** (you host-edited the file, bash sees the pre-edit length). Don't
host-Read→Write→cp for this — first try the **rename round-trip**, which invalidates the cached
inode with no content I/O and no host round-trip:

```bash
mv path/to/file path/to/file.cb && mv path/to/file.cb path/to/file
tail -1 path/to/file   # now serves the true tail; confirm the <!-- END --> marker
```

Validated 2026-06-19: cleared stale-truncated views that a 70s wait did not. Use this as the
first recovery for any file YOU edited this session; fall back to R below only if the rename
round-trip still shows a short tail (i.e. the disk file really is short).

## R — Repair fallback (ONLY if payload missing or gate fails, or rename-bust didn't clear it)

For each failing file: host-`Read` the true file from the install's HOST path (the
skill `location` in the available-skills listing), host-`Write` it to a mounted
scratch folder (outputs) under a filename the mount has NEVER seen (`foo.v2.py`),
then `cp` into `$EXEC` under the real name. Re-verify. Never "repair" from the
mount's own view — that copies the truncation. Staleness applies to YOUR OWN host
edits too: once bash has seen a mounted path, later host edits to that SAME path are
served at the pre-edit byte length — always transfer via a never-seen filename.
A repaired exec dir gets `.verified` only after the full gate passes on it.

## Scope

- Needed for: any module that loads `scripts/*` (nearly every operational task).
- Not needed for: pure documentation reads — the agent loads modules/architecture
  via the host `Read` tool anyway (host reads are always true).
- `/tmp` persists across sessions on a shared workspace VM — that persistence is
  exactly what the per-build cache exploits. Extracted dirs from prior sessions
  WITHOUT a `.verified` marker: treat as cache misses.

<!-- END -->
