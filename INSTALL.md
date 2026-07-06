# Installing the SJT skills

This repo is a Claude Code plugin marketplace (`sjt-skills`) of **5 plugins**, installed
with `/plugin` commands. There are no loose skills — every skill now ships inside a plugin.

## Install the plugins (run inside Claude Code)

Install straight from GitHub — grab only what you need, each plugin is independent:

```
/plugin marketplace add bbauersjt/sjt-audit-marketplace
/plugin install fs-review@sjt-skills
/plugin install suralink-binder@sjt-skills
/plugin install cch-axcess-suite@sjt-skills
/plugin install audit-sampling@sjt-skills
/plugin install trial-balance-prep@sjt-skills
```

Installed skills load namespaced, e.g. `fs-review:commercial-fs-review`.

> Working from a local clone instead? Replace the first line with
> `/plugin marketplace add <path-to-this-folder>`.

| Plugin | Contains |
|---|---|
| `fs-review` | commercial-fs-review, ebp-fs-review, govt-fs-review, nonprofit-fs-review |
| `suralink-binder` | suralink, suralink-sync, binder-organize |
| `cch-axcess-suite` | cch-axcess, cch-form-fill, cch-risk-assessment |
| `audit-sampling` | audit-sampling (FS substantive, walkthrough, EBP, single-audit, compliance samples) |
| `trial-balance-prep` | trial-balance-prep (TB roll-forward, code conversion, CCH import tiers, funds) |

**The Suralink and CCH Axcess plugins need the Chrome bridge**, which lives in its own repo:
[`bbauersjt/sjt-chrome-bridge`](https://github.com/bbauersjt/sjt-chrome-bridge). Install it
with `/plugin marketplace add bbauersjt/sjt-chrome-bridge` then
`/plugin install chrome-bridge@sjt-chrome-bridge` (plus the pip + unpacked-extension steps in
that repo's README).

## Uninstall / update

- `/plugin uninstall <name>@sjt-skills`
- `/plugin marketplace update` after edits to a local clone.
