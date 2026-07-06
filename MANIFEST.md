# Skills — canonical set

Consolidated 2026-07-06 from 4 exports (Desktop `Work.zip`, `WorkPCSkills.zip`; repo
`personal-work.zip`, `work-skills.zip`). This folder is now the single source of truth —
clone it to each setup instead of maintaining parallel copies.

## Layout — this folder is also a plugin marketplace (`sjt-skills`)

`.claude-plugin/marketplace.json` indexes three distributable plugins. The skills they
contain live **only** inside the plugin (one copy — moved, not duplicated); the loose
skill folders at the root are not part of any plugin.

| Plugin folder | Contains |
|---|---|
| `fs-review/` | commercial-fs-review, ebp-fs-review, govt-fs-review, nonprofit-fs-review |
| `suralink-binder/` | suralink, suralink-sync, binder-organize |
| `cch-axcess-suite/` | cch-axcess, cch-form-fill, cch-risk-assessment |

Install locally: `/plugin marketplace add <path-to-this-folder>` then
`/plugin install fs-review@sjt-skills` (etc.). Installed skills load namespaced, e.g.
`fs-review:commercial-fs-review`. The marketplace file is inert until installed — the loose
skills are unaffected by it.

22 skills. Each was chosen by content comparison across all 4 sources; where versions
differed, the newer/authoritative one was kept. `content-hash` is a sha256 prefix of the
skill's full file tree — if two setups show the same hash, they are byte-identical.

**2026-07-06 merge:** `legacy-grouping-converter` and `trial-balance-import` were
consolidated into **`trial-balance-prep`** — one skill covering TB import/roll-forward,
legacy grouping-code conversion, CCH import files (Basic / Grouped / Fund tiers),
classifications, and funds. The two old folders were removed. See the "Merged" section.

| Skill | Source kept | Content date | content-hash | Note |
|---|---|---|---|---|
| audit-sampling | Work.zip /Work | 2026-06-07 | 246945923747 | newer than repo copy (sample edits) |
| binder-organize | Work.zip /Work | 2026-06-07 | ebfb59a93075 | identical everywhere |
| cch-answerconnect | Work.zip /Work | 2026-06-07 | 088bfd711c10 | Desktop-only skill |
| cch-axcess | Work.zip /Work | 2026-06-30 | 360c4062933d | major rewrite (100 files/1.6MB) vs old 77/642KB |
| cch-form-fill | Work.zip /Work | 2026-06-26 | 747f13b084be | kept — companion to cch-axcess; not in firm registry |
| cch-help | Work.zip /Work | 2026-06-07 | 89745b5b3d52 | newer than repo copy |
| cch-risk-assessment | Work.zip /Work | 2026-06-30 | da370f7ceca3 | major rewrite (57 files/1.5MB) vs old 35/100KB |
| commercial-fs-review | WorkPCSkills /Work | 2026-06-07 | aadc62c7a15d | identical everywhere present |
| ebp-fs-review | Work.zip /Work | 2026-06-07 | 6f015784d2e5 | identical everywhere |
| ebp-sites | work-skills.zip | 2026-05-29 | b517fa58a1ef | repo-only skill |
| fix-page-breaks | work-skills.zip | 2026-05-29 | fe6cd58c7d81 | repo-only skill |
| gl-analytics | work-skills.zip | 2026-05-29 | 49973be45803 | repo-only skill |
| govt-fs-review | Work.zip /Work | 2026-06-07 | 0b5eb618c148 | identical everywhere |
| i-wanna-complain | WorkPCSkills /Work | 2026-06-07 | b492d55ea63d | WorkPCSkills-only skill |
| nonprofit-fs-review | Work.zip /Work | 2026-06-07 | 438d4bf56c51 | identical everywhere |
| quickbooks-report-formatter | WorkPCSkills /Work | 2026-06-07 | 97f5de5ab033 | identical; supersedes workpaper-formatter |
| step-signoff | work-skills.zip | 2026-05-29 | 2f74c70b2b0b | repo-only skill |
| suralink | Work.zip /Work | 2026-06-07 | 3b9d3ffc2a9f | identical everywhere |
| suralink-sync | Work.zip /Work | 2026-06-07 | 6e69984524e1 | newer than repo copy |
| trial-balance-prep | merged | 2026-07-06 | — | merge of trial-balance-import + legacy-grouping-converter (see below) |
| workpapers | Work.zip /Personal | 2026-06-30 | b853571accf7 | "engine" refactor; depends on writing-styles |
| writing-styles | Work.zip /Personal | 2026-06-30 | 7f725db8a277 | required by workpapers engine |

## Merged

- **trial-balance-prep** (2026-07-06) = `trial-balance-import` + `legacy-grouping-converter`.
  One skill for preparing any client TB for the firm's 4-digit index and CCH import.
  Adds CCH import tiers (Basic / Grouped / Fund) from `cch-import-examples.xlsx`, the
  10-way classification vocabulary (`default-classes.xlsx`), and fund handling
  (Fund-tier TB + optional standalone fund import). The legacy converter's
  `grouping_io.py` became `tb_io.py`; both grouping-index files carried over.
  Cross-references in `cch-risk-assessment` and `cch-axcess` were repointed.

## Deprecated / dropped

- **workpaper-formatter** — superseded by `workpapers` (its own SKILL.md calls the old one
  "a deprecation stub"). Was only in the repo zips. Not carried over.

## Present upstream but NOT in any of your 4 zips (not added)

The firm's live skill registry also lists **qbo-audit-report-pull** and **govt-fs-draft**,
which none of your exports contained. Left out — pull them separately if you want them.
