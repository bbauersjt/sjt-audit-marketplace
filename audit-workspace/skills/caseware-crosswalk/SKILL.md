---
name: caseware-crosswalk
description: Reads a copied CaseWare Working Papers engagement folder's DBF tables directly — no CaseWare needed. Two modes. (1) Crosswalk - drops _crosswalk.xlsx + _crosswalk.json at the top of the folder, mapping each workpaper index and CaseWare display name to the real (often cryptic) filename on disk. (2) TB extract - drops _tb_extract.xlsx + _tb_extract.json with the full trial balance (accounts, descriptions, L/S grouping codes AND names, the full grouping legend, fund structure, unadjusted/AJE/final balances for CY + 4 prior years, JE detail). Use whenever the user points at a CaseWare engagement folder copy (cowork reference folders, sync folders, prior-year dumps) and asks to "crosswalk", "index", or "organize" it, asks "which file is [workpaper]" in a jumbled CaseWare dump, asks to pull the TB / groupings / leadsheet codes / fund list / chart of accounts / balances "out of the caseware file", or wants to roll a prior CaseWare TB into a CCH import (pair with trial-balance-prep). Also triggers on "caseware crosswalk" or /caseware-crosswalk.
---

# CaseWare Crosswalk

CaseWare Working Papers folders are a flat, unorganized pile of files on disk — a
workpaper called "Fixed asset testing and rollforward" in the app may be `U-1.xlsx` on
disk. The pretty Document Manager tree (index, names, folders, sign-offs) lives in the
engagement's `<ClientFile>SH.dbf` FoxPro table, which travels with any **full copy** of
the folder. This skill reads it directly — no CaseWare needed — and writes the crosswalk
to the top of the folder.

Run this before opening anything in a CaseWare dump. Disk filenames are a crapshoot; the
CaseWare display names and indexes (crosswalk) and the L/S groupings (TB extract) are what
the documents and accounts actually *are* — use them to find planning docs, CaseWare
forms, and leadsheets, and to get groupings without asking the user or inferring them from
account descriptions.

## 1. When to run

1. The user points at a cowork/reference folder holding a copy of a prior-year CaseWare
   file and wants it indexed, or asks where a workpaper is in it.
2. Any folder containing `*SH.dbf` where workpaper questions are being asked.
3. If `_crosswalk.json` already sits at the top of the folder, this skill already ran —
   **read it**; only regenerate if the DBFs are newer than the crosswalk or the user asks.

## 2. Mode 1 — Crosswalk

1. Run:
```
python scripts/cw_crosswalk.py "<engagement folder>"
python scripts/cw_crosswalk.py --all "<parent folder>"      # every CaseWare folder inside
```
Options: `--include-deleted` (recycle-bin docs), `--out DIR` (write elsewhere —
default is the top of the engagement folder itself).

2. Outputs land at the top of the folder:
   - **`_crosswalk.xlsx`** — for humans: filterable table (Index | CaseWare Name | Folder |
     File on Disk | On Disk? | Doc Type | Sign-offs | Modified), MISSING rows highlighted.
   - **`_crosswalk.json`** — for the agent: same rows under `documents`, plus engagement
     name, generation timestamp, and source table.

## 3. Answer a workpaper question from the crosswalk

1. Read `_crosswalk.json` (not the xlsx) and match on `index` and `caseware_name`.
2. Open the file named in `disk_file` in the same folder. That is the real workpaper.
3. If `doc_type` = "automatic (in CaseWare db)" — the doc (TB, leadsheets, document
   index) lives inside the CaseWare database — there is no disk file to open.
4. If `on_disk` = "MISSING" — the DM references a file the copy doesn't contain
   (partial copy or never-synced perm file) — tell the user rather than guessing.

## 4. Mode 2 — TB extract (accounts, groupings, funds, balances)

1. Run:
```
python scripts/cw_tb_extract.py "<engagement folder>" [--out DIR]
```
2. Reads `am.dbf` (chart of accounts + L/S groupings; GROUP2 is the firm 4-digit index
   where used), `CE.dbf` (fund/entity structure — fund number, name, master/child),
   `bl.dbf` (balances), `gl.dbf` (JE detail), and `MP.dbf` (grouping legend — the ID `1`
   rows map each L/S code to its name).
3. Outputs land at the top of the folder:
   - **`_tb_extract.xlsx`** — sheets TB / Funds / AJEs / Groupings.
   - **`_tb_extract.json`** — same data for the agent, plus the `groupings` legend.
4. Every TB row carries `leadsheet_name` next to the `leadsheet` code, and the Groupings
   sheet/`groupings` key is the full code → name legend (with a used-by-an-account flag).
   **Use the names, not just the codes, when mapping to the firm 4-digit index** — "B. 1 →
   Participant loans" converts itself; a bare "B. 1" is a guess. The script warns on any
   L/S code it can't name.
5. The `funds` list carries the full consolidation **hierarchy**, recovered from the
   CE.dbf ENTITY-key prefixes: each entity is `root` / `master` / `child` with `parent`,
   `fund_type` (nearest master ancestor's ABBR), and `fund_type_name`. This maps straight
   onto CCH's two fund layers — masters → fund types, children → funds — feed it to
   `trial-balance-prep`'s `funds_from_cw_extract()` + `write_fund_list()` to build the
   4-column CCH fund import (Fund Type Index / Fund Type Name / Fund Index / Fund Name)
   with no screenshots or asks.
6. Balance semantics:
   - `cy_unadjusted` = year-end unadjusted balance (bl ID `O`, bucket `O`, YEAR `0`).
   - `cy_aje` = booked normal JEs (bl ID `X`, bucket `Y`, type `N`); `cy_final` =
     unadjusted + AJEs. Reclass (`L`) and passed/unrecorded (`U`) are separate columns
     and NOT in `cy_final`.
   - `py1_final`..`py4_final` = final balances 1-4 years back.
   - Credits are negative (CaseWare natural sign). The TB nets to zero in total and per
     fund — verify this after extraction and flag if not.
   - CaseWare's computed `NETINC` rows and all-`Z` JE header lines are excluded.
7. **Rolling into CCH:** hand the extract to the `trial-balance-prep` skill to map
   groupings to the firm 4-digit index and build the CCH import file (Basic / Grouped /
   Fund tier, sign convention, classifications).

## 5. Caveats / guards

1. No `*SH.dbf` in the copy → script exits with SKIP; tell the user the copy is
   files-only and the index can't be rebuilt from filenames alone.
2. Deleted (recycle-bin) documents are excluded by default.
3. Do not write crosswalks into a **live** sync folder without the user asking —
   reference copies are the intended target.
4. Multiple `*SH.dbf` matches only happen if two client files share a folder; the script
   takes the first — flag it if the folder looks like a merged dump.
