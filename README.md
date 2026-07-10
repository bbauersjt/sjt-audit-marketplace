# SJT Group CPA — audit skills marketplace

A Claude Code plugin marketplace (`sjt-skills`) of audit tools, plus a Chrome bridge download
and staff handouts.

## Install

```
/plugin marketplace add bbauersjt/sjt-audit-marketplace
/plugin install fs-review@sjt-skills
/plugin install suralink-binder@sjt-skills
/plugin install cch-axcess-suite@sjt-skills
/plugin install audit-sampling@sjt-skills
/plugin install audit-workspace@sjt-skills
```

Install only what you need — each plugin is independent. Full steps are in [INSTALL.md](INSTALL.md);
provenance in [MANIFEST.md](MANIFEST.md).

| Plugin | Skills |
|---|---|
| `fs-review` | fs-review (one orchestrator: commercial, nonprofit, governmental, EBP) |
| `suralink-binder` | suralink, suralink-sync, binder-organize |
| `cch-axcess-suite` | cch-axcess, cch-form-fill, cch-risk-assessment |
| `audit-sampling` | audit-sampling |
| `audit-workspace` | audit-workspace-setup, caseware-crosswalk, trial-balance-prep, writing-styles |

## Also here

- **`chrome-bridge.zip`** — the Chrome bridge (local MCP server + Chrome extension) the
  portal-facing skills (Suralink, CCH Axcess) need. **A download, not a plugin** — unzip and
  follow the README inside (pip install → `register_server.ps1` → load the extension unpacked).
- **`handouts/`** — staff walkthroughs; *Cowork Audit Workspace Setup* runs on the
  `audit-workspace` plugin.

See [CHANGELOG.md](CHANGELOG.md) for release notes.

---
© SJT Group CPA
