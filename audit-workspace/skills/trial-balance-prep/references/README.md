# Reference data — trial-balance-prep

Everything the skill reads at run time. Hand-maintained by the firm except
where noted. The skill reads these; it never writes to them.

## Grouping indexes — what conversion targets

### standard-group-codes.xlsx
Commercial, nonprofit, and governmental engagements. Two sheets: `Natural`
(FASB; nonprofit & commercial) and `Governmental`. Columns: `Index`,
`Group Name`, `Class`. The `4xxx` / `5xxx` ranges are deliberately sparse —
when a meaning has no listed Group Name, generate the next free code in the
range rather than forcing a wrong match. Header sits a few rows down under a
title; the loader finds it by the `Index` / `Group` keywords.

### ebp-group-codes.xlsx
401(k) / 403(b) / defined-contribution plan audits. One sheet,
`EBP Grouping Index`. Columns: `Index`, `Group Name`, `Financial Statement`,
`Class`, `Carries TB Balances`, `Binder Include Rule`. Rows `6000 Participant
Data` and `9000 Perm File` are audit areas that carry no GL balances — never a
conversion target; drop them when matching.

The `Class` on both indexes is **coarse** (Asset / Liability / … ). See
`cch-import-formats.md` for how it resolves to the 10-way import classification.

## Classification vocabulary

### default-classes.xlsx
The firm's 10-way import classification: `ABBREV | DESCRIPTION`
(CA, NA, CL, NL, EQ, REV, COR, OI, OPX, OE). This is the ONLY set the CCH
`Classification` column may draw from — validate every value written against
it. `tb_io.load_classes()` reads it.

## CCH import format

### cch-import-examples.xlsx
Ground-truth column specs for the three CCH import tiers — `Basic`, `Grouped`,
`Fund` sheets. This is a real, importable layout captured from an engagement;
mirror it exactly. `cch-import-formats.md` documents the columns, the hard
constraints (no freeze panes, debits-positive, etc.), and how classification
and fund index are derived.

## Maintenance

Edit the xlsx files directly in Excel when the firm revises an index, the class
list, or the import layout. Keep column headers intact — the loaders key off
them. `default-classes.xlsx` and `cch-import-examples.xlsx` originate from the
firm's default class list and a sample CCH import; re-capture from a real CCH
export if CCH changes the accepted format.
