# sjt-skills — distributable plugin marketplace

The firm's shareable subset of the canonical skills folder
(`Documents\Code\skills` on the build machine — see its `MANIFEST.md` for full
provenance). Everything here is a **plugin** indexed by
`.claude-plugin/marketplace.json`; install with `/plugin` commands (see `INSTALL.md`).

| Plugin folder | Skills | Notes |
|---|---|---|
| `fs-review/` | commercial-fs-review, ebp-fs-review, govt-fs-review, nonprofit-fs-review | FS technical proof & review before QC |
| `suralink-binder/` | suralink, suralink-sync, binder-organize | Suralink portal pull + indexed binder filing |
| `cch-axcess-suite/` | cch-axcess, cch-form-fill, cch-risk-assessment | CCH Axcess / Knowledge Coach automation |
| `audit-sampling/` | audit-sampling | Sample identification, planning, and pulls |
| `audit-workspace/` | audit-workspace-setup, caseware-crosswalk, trial-balance-prep, writing-styles | Engagement onboarding + TB conversion — the "Cowork Audit Workspace Setup" handout runs on this |

**2026-07-06:** `audit-sampling` and `trial-balance-prep` were converted from loose skill
folders to plugins (added `.claude-plugin/plugin.json` + `skills/<name>/` layout and
registered them in `marketplace.json`) so they install like the other three.
`trial-balance-prep` was refreshed from the canonical copy at the same time
(caseware-crosswalk-aware SKILL.md + `tb_io.py`).

**2026-07-10 (later):** `trial-balance-prep` folded into `audit-workspace` — the plugin
now carries the whole CaseWare→CCH conversion pipeline (extract → grouping conversion →
TB/fund imports). The standalone `trial-balance-prep` plugin is gone; **uninstall
`trial-balance-prep@sjt-skills` after updating** or the skill loads twice. The skill
itself is unchanged and still triggers on any TB job, onboarding or not.

**2026-07-10:** added the `audit-workspace` plugin (audit-workspace-setup +
caseware-crosswalk + writing-styles) — everything the "Cowork Audit Workspace Setup"
handout (in `../handouts/`) needs. `caseware-crosswalk`'s TB extract now pulls the L/S
grouping **names** (from MP.dbf) alongside the codes, plus the full code→name legend —
so grouping conversion to the firm 4-digit index never needs guesses or pastes.
`trial-balance-prep` consumes that extract directly. Also refreshed `fs-review` to the
v2 rebuild (single orchestrator + shared modules + deterministic math scripts) and
`cch-axcess-suite` to the 7/9 canonical state.
