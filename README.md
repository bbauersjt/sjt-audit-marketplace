# SJT Audit Skills — Claude Code marketplace

A [Claude Code](https://docs.claude.com/en/docs/claude-code) plugin marketplace from **SJT Group CPA**, cataloging the firm's audit skills as installable plugins.

## Add the marketplace

```
/plugin marketplace add bbauersjt/sjt-audit-marketplace
```

## Install plugins

```
/plugin install sjt-cch-axcess@sjt-audit-skills
/plugin install sjt-cch-risk-assessment@sjt-audit-skills
/plugin install sjt-cch-form-fill@sjt-audit-skills
/plugin install sjt-audit-sampling@sjt-audit-skills
/plugin install sjt-binder-organize@sjt-audit-skills
/plugin install sjt-workpapers@sjt-audit-skills
/plugin install sjt-workpaper-formatter@sjt-audit-skills
/plugin install sjt-commercial-fs-review@sjt-audit-skills
/plugin install sjt-nonprofit-fs-review@sjt-audit-skills
/plugin install sjt-govt-fs-review@sjt-audit-skills
/plugin install sjt-ebp-fs-review@sjt-audit-skills
```

Each plugin lives in its own repository under [github.com/bbauersjt](https://github.com/bbauersjt). The catalog is defined in [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json).
