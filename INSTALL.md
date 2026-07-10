# Installing the SJT skills

Everything in this repo is a **plugin** indexed by the `sjt-skills` marketplace — installed
with `/plugin` commands inside Claude Code.

```
/plugin marketplace add <path-or-github-url-of-this-repo>
/plugin install fs-review@sjt-skills
/plugin install suralink-binder@sjt-skills
/plugin install cch-axcess-suite@sjt-skills
/plugin install audit-sampling@sjt-skills
/plugin install audit-workspace@sjt-skills
```

Installed skills load namespaced, e.g. `fs-review:commercial-fs-review`,
`audit-sampling:audit-sampling`.

| Plugin | Skills |
|---|---|
| `fs-review` | fs-review (v2 — one orchestrator covering commercial, nonprofit, governmental, EBP) |
| `suralink-binder` | suralink, suralink-sync, binder-organize |
| `cch-axcess-suite` | cch-axcess, cch-form-fill, cch-risk-assessment |
| `audit-sampling` | audit-sampling |
| `audit-workspace` | audit-workspace-setup, caseware-crosswalk, trial-balance-prep, writing-styles |

`audit-workspace` is what the **Cowork Audit Workspace Setup** handout (in
`handouts/` at the repo root) runs on — install it before following that handout.
It also carries the whole CaseWare→CCH conversion pipeline (crosswalk/TB extract →
grouping conversion → TB and fund imports).

> If you also have a personal copy of `audit-sampling` or `trial-balance-prep` in
> `%USERPROFILE%\.claude\skills\` (from an earlier loose-skill install), delete it after
> installing the plugin so the skill doesn't load twice. Likewise, if you installed the
> old standalone `trial-balance-prep@sjt-skills` plugin, uninstall it — that skill now
> ships inside `audit-workspace`.

## Chrome bridge — separate download, NOT a plugin

The portal-facing skills (suralink, cch-axcess, ebp-sites) need the Chrome bridge:
a local MCP server + Chrome extension. It is **not** installed with `/plugin` —
download `chrome-bridge.zip` from the repo root, unzip it somewhere permanent, and
follow the README inside (pip install → `register_server.ps1` → load the extension
unpacked in Chrome).

## Uninstall / update

- `/plugin uninstall <name>@sjt-skills`
- After pulling repo changes: `/plugin marketplace update sjt-skills`
