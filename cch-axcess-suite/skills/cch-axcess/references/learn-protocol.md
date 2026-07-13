# Learn Protocol — capture mode (BEHIND THE CONSENT WALL — never self-fires)

**Entry is gated.** Capture mode runs ONLY after the consent wall in SKILL.md routing:
the ask matched no trigger row, you said verbatim *"I haven't learned how to do that. Do
you want me to attempt to figure it out? Warning: slow, heavy usage."*, you STOPPED, and
the user explicitly said yes. An explicit user command ("learn this", "listen for this",
"capture this and script it", "watch and script it") counts as that yes. Anything short
of an explicit yes = do not enter. There is no auto-learn path.

**Terminal state of capture mode is a tested function + an endpoint spec + a thin module —
NOT a prose how-to.** Markdown that documents the steps "by hand" is a failure state.

> **Where artifacts go (read this — the install is READ-ONLY).** The installed skill
> directory is a per-session cache; writing into it truncates files and is wiped on reinstall. Capture artifacts are **rebuild inputs, not runtime
> installs**: write them to the user-visible working folder for this session (ask which if
> none is connected), and log the capture in the complaint log (`i-wanna-complain`) so the
> batch-rebuild pipeline folds them into the skill source repo at the next build. Do NOT
> request a mount of the skill's own directory. The new operation becomes part of the
> shipped skill at the NEXT release — not mid-session.

For the full manual (capture mechanics, monkey-patch, fallback ladder, gotchas), see
`training-mode.md`. This file is the **uniform-style checklist** to run when capture
mode closes.

## When capture mode may run (all three required)

1. Consent obtained at the wall (above) — or the user's explicit "learn this" command.
2. The ask matches no trigger row in SKILL.md.
3. It isn't one of these (which are NOT capture mode): an existing module's procedure
   failing (that's the 2-fail doc-return rule — debug it), a known endpoint failure
   documented in architecture.md, or a trivial typo in a module (complaint-log it).

A missing sub-operation in an existing module (e.g. add-audit-programs lacks a
roll-forward step) takes the same wall: say what's missing, ask, then capture.

## Order of operations

1. **Capture** the operation live. Drive it through Claude in Chrome with
   `scripts.auth_capture.INSTALL_MONKEYPATCH_JS` already installed. Have the user do the
   action ONCE. Read `window.__cch_capture`.
2. **Replay** programmatically with `http_runner.build_xhr_call` / `build_fetch_call`.
   Confirm the side effect with a follow-up GET. If it doesn't match, capture is
   incomplete — go back to step 1.
3. **Codify as code first** — a `{module}.py` function, then an `{operation}.json`
   endpoint spec, then the thin module MD — all written to the session working folder
   as rebuild inputs. Never write the module before the script works. (Import shipped
   scripts by path injection against the VERIFIED exec copy per `runbooks/local-exec.md`,
   not the bash mount.)
4. **Apply the No-Hard-Delete rule.** If the captured call is a DELETE on a
   form/folder/leadsheet/report/document, do NOT script it. Either wrap as a soft-delete
   via the `wpm.soft_delete_*` helpers or refuse the operation. See `scripts/wpm.py` header.
5. **Write the module** using the template below. YAML front-matter is mandatory —
   including the `leg:` field (`wpm` | `kc` | `none`) so Step 0 knows what to warm.
6. **Record new platform facts** in the capture notes (destined for architecture.md at
   the next build) — auth quirks, ordering rules, ID handling, body-shape gotchas.
7. **Log the complaint-log entry** pointing at the artifacts. That entry is what gets the
   operation into the next batch rebuild — no entry, no graduation, the work evaporates.

## Exit checklist (hard — every box)

- [ ] Consent wall was actually shown and answered yes (or explicit user "learn this").
- [ ] `{module}.py` function written and replayed live against the real engagement.
- [ ] `{operation}.json` endpoint spec created.
- [ ] `{verb-noun}.md` module written with YAML front-matter incl. `leg:`.
- [ ] No DELETE call was scripted (`grep -E 'DELETE' {module}.py`).
- [ ] User confirmed all new artifacts before disk writes.
- [ ] Complaint-log entry written, pointing at every artifact, flagged "capture — fold
      into next rebuild".

If any box is unchecked, capture mode is still open.

## Module front-matter (mandatory, mechanically parsed)

```yaml
---
summary: One-line trigger-map description
triggers:
  - "phrase 1"
  - "phrase 2"
leg: wpm        # wpm | kc | none — what Step 0 warms
inputs:
  - "Engagement URL"
  - "clientId"
calls:
  - scripts.wpm.move
  - scripts.wpm.set_index
status: validated   # or: wip | ui-only
validated_on:
  - "<engagement> — <date>"
---
```

The trigger map and INDEX are derived from these blocks by `scripts/regenerate_index.py`
(source repo, at build time). Drift between the INDEX and front-matter means the
regenerator wasn't run.

## Module body template

```markdown
---
(front-matter above)
---

# Module — <Verb Noun>

## What this does
<one paragraph>

## Prerequisites
- Leg: <wpm|kc> warm (Step 0). Rules 0–3 apply (SKILL.md).
- <module-specific items only>

## Procedure
### 1. <step>
\`\`\`python
from scripts import <module>
js = <module>.<function>(...)
\`\`\`
### 2. <step>
...
### N. Verify (HTTP 200 = accepted, not applied — re-GET; architecture.md)

## Known failure modes
- <symptom → cause → fix>
```

**Hard rule:** no JS snippet inside a module body longer than 5 lines. If the JS is
non-trivial, it lives in `scripts/` and the module shows the Python call that produces it.

## See also

- `training-mode.md` — capture mechanics, monkey-patch, fallback ladder, known-unknowns backlog.
- `architecture.md` — platform-stable facts. Read once per session.
- `runbooks/local-exec.md` — per-build verified exec cache; never run scripts from the bash mount.

<!-- END -->
