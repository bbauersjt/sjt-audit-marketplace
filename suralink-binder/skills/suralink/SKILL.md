---
name: suralink
description: Skill for navigating the Suralink auditor portal (app.suralink.com, api.suralink.com) via its backend API. Use whenever the user mentions Suralink, a Suralink audit/engagement, a Suralink request list, PBC items in Suralink, an auditId / Audit.php URL, downloading client files from Suralink, or "pull files from the portal". Backend-first — direct REST + gateway calls over UI clicking. Cookie-authenticated; the user must be logged into Suralink in a Chrome tab. Includes a script-first capture mode where new operations become Python functions, not docs.
---

# Suralink — Dispatcher

Route the request to ONE module below, read only that module, then call the
`scripts/*.py` functions it names. Do not read everything.

## Modules — match the row, read that one file

| User wants to… | Module | Triggers |
|---|---|---|
| Map the binder / check what's new | `references/modules/binder-and-activity.md` | "map the binder", "what's new", "recent uploads", "activity timeline" |
| List the requests / PBC items in an audit | `references/modules/list-requests.md` | "what requests are in", "show the request list", "what's outstanding" |
| Download client files from an audit | `references/modules/download-files.md` | "download the files", "pull files from this request", "get the client uploads" |
| List clients / resolve a client / find its engagements | `references/modules/clients-and-engagements.md` | "list my clients", "what engagements", "find the client X", "which auditId is X" |
| A new operation, none of the above | `references/training-mode.md` | capture the call, then codify it into a script |

Prefer `binder-and-activity.md` for whole-engagement reads — one scrape, no per-request crawl.

## Two rules

1. **Backend over UI.** Every Suralink screen is backed by an HTTP call — the `api.suralink.com/v2` REST API or a legacy `app.suralink.com/gateways/*Gateway.php` call. Prefer it; click-through is a last resort. (One sanctioned exception: the bulk-zip export, which only the UI can trigger — see the `suralink-sync` skill.)
2. **Scripts over prose.** API calls, parses and deterministic transforms live in `scripts/*.py`. Modules describe *what* and *when*, never *how*.

## Platform facts — don't rediscover

`references/architecture.md` is the single source of truth: the two hosts; cookie auth (no bearer tokens — every call is JavaScript run inside the user's logged-in Chrome tab via `mcp__Claude_in_Chrome__javascript_tool` with `credentials:'include'`); the ID glossary and the request-`id`-vs-`requestId` trap; fileProxy; the static `aud1tMgr!` gateway secret. Read it before any novel work; modules cite it and do not repeat it. Endpoint shapes are in `references/endpoints/*.json`.

Prerequisite for everything: a Chrome tab open and logged into `app.suralink.com`.
