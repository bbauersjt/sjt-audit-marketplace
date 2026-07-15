---
name: audit-workspace-setup
description: One-pass first-time setup of an audit engagement workspace. Use when the user says "set up this engagement", "run the workspace setup", "onboard [client]", "new audit project setup", "run the setup procedure", or points at a fresh engagement folder holding a prior-year CaseWare copy and current-year PBCs. Orchestrates caseware-crosswalk (workpaper index + TB extract), suralink-sync (PBC pull), and trial-balance-prep (CaseWare→CCH conversion imports), then writes the reference memos (policies, planning rollforward, minutes, and — for benefit plans — plan provisions) and the project-memory search protocol. Supersedes the manual "Cowork Workspace Setup for an Audit" handout prompts.
---

# Audit Workspace Setup

Turns a raw pile — prior-year CaseWare copy, current-year Suralink PBCs, GLs,
prior FS, current grouped TB — into a working audit workspace: folders
verified, the CaseWare file crosswalked, reference memos written, the CCH
conversion imports built when they apply, and the project memory installed.

Orchestrates:
- **`caseware-crosswalk`** — document index + TB extract from the prior-year file
- **`suralink-sync`** — if PBCs still need pulling from the portal
- **`trial-balance-prep`** — the CaseWare→CCH import files (step 5)
- **`writing-styles`** — voice for every memo

Run the steps in order. Each is idempotent — re-running skips what exists.
**Ask before regenerating** anything that already exists (a memo, an import
file, a crosswalk); never silently overwrite work the user may have edited.

## Step 0 — Inventory & client type

1. List the engagement folder (names only — see Search protocol below).
2. Determine **client type** — Govt / NPO / Commercial / EBP. A 401(k)/403(b)/
   retirement plan is EBP; it changes step 4 (plan-provisions memo) and step 5
   (single trust entity, no fund import).
3. Check off what's present; report gaps and continue with what exists rather
   than stalling:
   - Prior-year CaseWare folder (has `*SH.dbf`)
   - Current-year PBCs (Suralink pull, or a client-sent folder)
   - GL (two years preferred), prior-year FS, current-year grouped TB
4. Determine **prior-year platform** — CaseWare folder present → this
   engagement is being **converted to CCH** and step 5 applies. Prior year
   already in CCH (no CaseWare DBF set) → skip step 5 entirely.

## Step 1 — Folder shape

1. Verify these folders (create only what's missing; never rename existing
   folders without asking):

| Folder | Holds |
|---|---|
| `{Client} {PY} Caseware Audit File` | the copied prior-year CaseWare folder, untouched |
| `{CY} Suralink Folder` | current-year PBCs (suralink-sync creates/owns this — `_raw/` is chain-of-custody, work out of `sorted/`) |
| `References` | GLs, prior FS, current grouped TB, and every memo this skill writes |

2. If PBCs haven't been pulled yet, run **`suralink-sync`** now (it names the
   folder itself).

## Step 2 — Crosswalk the CaseWare file

1. Run **`caseware-crosswalk`** on the prior-year folder, both modes:
   crosswalk (`_crosswalk.xlsx/json`) and TB extract (`_tb_extract.xlsx/json`).
2. If both outputs already sit at the top of the folder, skip step 2.1–2.2 —
   just read them.
3. Find planning docs and CaseWare forms by name in the crosswalk (CaseWare
   index and display name) — never by opening files one by one; disk
   filenames are unreliable.
4. Read groupings (L/S **code and name**, full code → name legend), fund
   structure, and five years of balances from the TB extract — never guess a
   grouping from an account description or ask the user for it. Neither
   question requires opening the pile again.

## Step 3 — Optional: {PY} Workpapers / {PY} Planning copies

Offer this; don't default to it. If the user wants it:
1. Workpapers = crosswalk rows whose `disk_file` is Excel and whose series
   is a testing section (leads, testwork, analytics — not CX/planning forms).
2. Planning forms = rows whose index matches PPC planning patterns
   (`CX-`, `*-CX-*`, planning/fraud/materiality memos).
3. Copy (never move) to `{PY} Workpapers/` and `{PY} Planning/`, renaming
   copies to `{index} - {caseware_name}.{ext}`.

## Step 4 — Reference memos

All memos go in `References/`, all in the firm voice (**`writing-styles`**,
memo module). Use the crosswalk to find the 3–6 documents each memo needs; do
not sweep the folder.

1. **Policies memo** — pull latest versions of policies bearing on the audit:
   controls (payroll, review/approval, procurement), compensated absences,
   capitalization threshold, anything driving disclosures or planning. Check
   current-year PBCs for versions newer than the CaseWare copies; flag
   changes year-over-year.
2. **Planning rollforward memo** — pull from prior-year planning forms
   (crosswalk: CX/planning series): risk assessments, materiality basis,
   control understanding, fraud considerations, prior-year issues.
3. **Minutes memo** — summarize all minutes in current-year PBCs, plus any
   minutes/minutes-memos in the CaseWare file; pull out anything with audit
   relevance (approvals, new debt, litigation, plan amendments, big
   transactions).
4. **Plan provisions memo — EBP only.** Same pattern as the policies memo but
   for the plan document set (adoption agreement, base plan document,
   amendments, SPD — usually in the PBCs and/or Permanent File section).
   Pull:
   - eligibility & entry dates; definition of compensation
   - deferral/match/safe-harbor formulas; profit-sharing allocation
   - vesting schedule; forfeiture usage
   - loan provisions; distribution & hardship rules; auto-enrollment/escalation
   - anything the audit tests against (participant data, contributions,
     distributions all test TO these provisions)

   4.1. Diff the current-year adoption agreement/amendments against the
   prior-year versions in the CaseWare file; lead the memo with what changed.

## Step 5 — CaseWare→CCH conversion imports (conditional)

Only run this step if step 0 found a prior-year CaseWare file. Prior year
already in CCH → skip; nothing to convert.

Requires `_tb_extract` (step 2) + the current-year TB. Hand both to
**`trial-balance-prep`**:

1. **Historical TB import** — build the CCH import carrying the prior-year
   final balances (and earlier years where the extract has them) on the
   firm's 4-digit grouping index, with **current-year values mapped onto the
   same account lines** — one file that seats history and current year
   together.
2. **Fund balance import** — only if the TB extract shows a fund structure
   (`funds` non-empty / fund-segmented balances). Build the standalone fund
   import too. EBP plans are single-trust — no fund import.
3. Verify before handing over: TB nets to zero in total and per fund; CY
   mapped total ties to the client TB; every unmapped account is surfaced,
   not silently dropped.
4. Park outputs in `References/` (or a `CCH Imports/` subfolder if there are
   several files).

## Step 6 — Project memory

Fill the brackets and save to project memory:

> This project is for the audit of [client]. Year end [date]. TM [amount].
> Client type: [Govt/NPO/Commercial/EBP].
>
> `{Client} {PY} Caseware Audit File` is the completed prior-year audit file.
> It is an unorganized flat pile — CaseWare does not carry names or indexes to
> disk. **Never browse it.** Its index is `_crosswalk.json` at the top of that
> folder: match on `index`/`caseware_name`, open only the `disk_file` named.
> `doc_type` "automatic (in CaseWare db)" means no disk file exists (TB,
> leads, AJEs live in the CaseWare database) — balances for those come from
> `_tb_extract.json` in the same folder, never from opening workpapers.
> `_tb_extract.json` also carries each account's L/S grouping code **and
> name** plus the full grouping legend — never guess groupings or ask for
> them; read them there.
> Current-year PBCs are in `{CY} Suralink Folder/sorted/` (`_raw/` is the
> untouched chain-of-custody copy — leave it alone).
>
> `References` holds the GLs, prior FS, current grouped TB, and the memos:
> policies, planning rollforward, minutes[, plan provisions].
>
> Search order: References memos first, then the current-year PBCs, then the
> CaseWare file **via the crosswalk only**. In any folder, list file names and
> pick candidates before opening anything; open at most 3–4 candidates before
> checking in. If nothing looks right, ask — do not read a folder file-by-file.

## Search protocol (applies to every step above)

1. Names first — list a folder before opening anything in it.
2. Treat the crosswalk as the index of the CaseWare pile and `_tb_extract` as
   its TB — answer any question answerable from those without touching the
   pile.
3. Open at most 3–4 candidate files per question before checking in.
4. Once a memo exists, read the memo, not the sources — memos are read-once
   artifacts.

## Done

Report what was built, what was skipped and why (already existed / input
missing / not applicable to client type), and any gaps the user needs to fill
(missing PBCs, unmapped accounts, provisions that changed year-over-year).
