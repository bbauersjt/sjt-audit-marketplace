# Installing the SJT skills

This repo holds two kinds of things:

1. **4 plugins** indexed by a marketplace (`sjt-skills`) — installed with `/plugin` commands.
2. **2 loose skills** — installed by copying into your personal skills dir (`~/.claude/skills/`).

`install.ps1` does the loose-skill copy for you and prints the plugin commands. Or follow
the manual steps below.

---

## Part 1 — the plugins (run inside Claude Code)

Install straight from GitHub:

```
/plugin marketplace add bbauersjt/sjt-audit-marketplace
/plugin install fs-review@sjt-skills
/plugin install suralink-binder@sjt-skills
/plugin install cch-axcess-suite@sjt-skills
/plugin install chrome-bridge@sjt-skills
```

Installed skills load namespaced, e.g. `fs-review:commercial-fs-review`.

> Working from a local clone instead? Replace the first line with
> `/plugin marketplace add <path-to-this-folder>`.

| Plugin | Contains |
|---|---|
| `fs-review` | commercial-fs-review, ebp-fs-review, govt-fs-review, nonprofit-fs-review |
| `suralink-binder` | suralink, suralink-sync, binder-organize |
| `cch-axcess-suite` | cch-axcess, cch-form-fill, cch-risk-assessment |
| `chrome-bridge` | MCP transport into an authenticated Chrome session (the relay + MV3 extension the Suralink and CCH plugins use). Install on its own if you just want the bridge. |

**`chrome-bridge` needs two manual steps** the plugin can't do for you: `pip install -r
requirements.txt` in `chrome-bridge-plugin/`, and loading `chrome-bridge-plugin/extension/`
as an unpacked extension in Chrome. See `chrome-bridge-plugin/README.md`.

## Part 2 — the 2 loose skills (run in PowerShell)

```powershell
.\install.ps1
```

This copies each loose skill folder into `%USERPROFILE%\.claude\skills\`, where Claude Code
picks them up as personal skills. Re-run any time to refresh (it overwrites).

Loose skills: `audit-sampling`, `trial-balance-prep`.

## Uninstall / update

- Plugins: `/plugin uninstall <name>@sjt-skills`, or `/plugin marketplace update` after edits.
- Loose skills: delete the folder from `%USERPROFILE%\.claude\skills\`, or re-run `install.ps1`.
