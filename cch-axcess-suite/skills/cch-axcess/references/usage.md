---
summary: User-facing "what is this / how do I use it" doc. Load ONLY when the user asks what the skill does or how to use it. Not part of any routine load path.
triggers:
  - "how do I use cch-axcess / what does it do / what can it do / what can't it do"
status: validated
---

# CCH Axcess — How to use this skill

**What it is:** an assistant that works *inside your* CCH Axcess engagement — building
binders, filling forms, running reports — by driving a browser tab as you, using your own
logged-in session.

## How to use it

It works through your Chrome browser, not a separate login:

- Have **Chrome open** with the **Claude extension** connected, and be **signed in to CCH
  Axcess** in that browser. Your access is its access — it never asks for or enters your password.
- **Open the engagement** you want to work (the engagement-view page). It won't switch
  clients for you — that's on purpose, so it can't land in the wrong engagement.
- It then uses **one browser tab** to read and write through your authenticated session.
  First use in a session needs a single click into a planning folder so it can pick up your
  credentials; after that it runs on its own.
- Just tell it what you want in plain language ("set up the binder," "fill out KBA-400,"
  "run the TB report").

## What it's trained to do

- Set up and build out **binders** and section folders
- Add **audit programs** (NFP / Govt / EBP) and file leadsheets
- Fill out **Knowledge Coach forms** (KBA / AID / AUD), fast-fill, scan cross-references
- Record a **risk assessment / audit plan** into the binder — planning built with the
  `cch-risk-assessment` skill, written through to the forms by this one
- Build out and tailor **AUD-8xx audit programs** — bring in steps, link risks, sign off
- Manage **TB groupings** and **fund** setup
- Run **TB and Journal Entry reports**; build leadsheets
- Annotate **leadsheets and TB reports** (REF columns, tickmarks, comments)
- **Rename / re-index** workpapers; **map** the binder to find anything
- Upload, download, and replace **files** in the binder

## What it can't do (by design)

- **No hard deletes.** It only soft-deletes — anything "removed" lands in a *User to delete*
  folder for you to clear.
- **Won't switch clients/engagements** for you — you open the target engagement.
- **Won't enter credentials** or log in for you — it relies on your existing session.
- **Not CCH how-to/support** (that's the `cch-help` skill) and **not accounting/standards
  research** (that's `cch-answerconnect`).

<!-- END -->
