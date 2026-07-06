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
| `trial-balance-prep/` | trial-balance-prep | TB roll-forward, grouping conversion, CCH import files |

**2026-07-06:** `audit-sampling` and `trial-balance-prep` were converted from loose skill
folders to plugins (added `.claude-plugin/plugin.json` + `skills/<name>/` layout and
registered them in `marketplace.json`) so they install like the other three.
`trial-balance-prep` was refreshed from the canonical copy at the same time
(caseware-crosswalk-aware SKILL.md + `tb_io.py`).

Note: `trial-balance-prep` can pull prior-year CaseWare TBs via the separate
`caseware-crosswalk` skill when it is present on the machine; without it, the skill
falls back to asking for pastes/exports. `caseware-crosswalk` is not distributed in
this repo yet.
