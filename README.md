# SJT Group CPA — audit skills marketplace

A Claude Code plugin marketplace (`sjt-skills`) of audit tools, plus a couple of loose skills.

## Install

Inside Claude Code:

```
/plugin marketplace add bbauersjt/sjt-audit-marketplace
/plugin install fs-review@sjt-skills
/plugin install suralink-binder@sjt-skills
/plugin install cch-axcess-suite@sjt-skills
```

Install only what you need — each plugin is independent. Full steps, the loose-skill
installer, and the `chrome-bridge` setup notes are in [INSTALL.md](INSTALL.md).

## What's here

| Plugin | Contains |
|---|---|
| `fs-review` | Technical proof & review of financial statements — commercial, nonprofit, governmental, EBP |
| `suralink-binder` | Suralink portal pull, local mirror sync, and 4-digit indexed binder filing |
| `cch-axcess-suite` | CCH Axcess / Knowledge Coach automation, risk assessment, and form filling |

The `suralink-binder` and `cch-axcess-suite` plugins talk to Chrome through the **Chrome
bridge**, which ships as its own repo: [bbauersjt/sjt-chrome-bridge](https://github.com/bbauersjt/sjt-chrome-bridge).

Loose skills (copied into `~/.claude/skills/` via `install.ps1`): `audit-sampling`, `trial-balance-prep`.

---
© SJT Group CPA
