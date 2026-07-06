# Single Audit Sampling Workflow

The full process for sizing and selecting samples for a single audit. Run this in Mode B when the engagement includes a single audit. The per-program method (`controls-compliance-dual`) is one piece of this larger workflow.

## Step 1 — Identify major programs and their populations

- The user identifies major programs (typically already determined in the planning workpapers)
- For each major program, obtain the cleaned population of expenditures
- Reconcile each program's population to the SEFA

If major programs haven't been determined yet, surface that to the user — sampling can't proceed without them.

## Step 2 — Compute program materiality

For each major program:

**Program materiality = 5% × total expenditures of that program**

Document this per program. Used downstream to identify whether transaction streams (payroll, disbursements, IDC, etc.) are material to that program.

## Step 3 — Identify if payroll or disbursements are material to any program

For each major program, determine whether **payroll** and **disbursements** independently exceed program materiality.

The user should confirm or the skill can compute from the population if expenditure-type tagging is available.

Two flags to set:
- `payroll_material_any_program` (true if material to ≥ 1 program)
- `disbursements_material_any_program` (true if material to ≥ 1 program)

## Step 4 — Apply cross-program control minimums

If payroll is material to any program:
- Treat payroll controls as **identical across programs**
- Across all program samples combined, hit a **minimum of 25 payroll occurrences**

If disbursements is material to any program:
- Treat disbursements controls as **identical across programs**
- Across all program samples combined, hit a **minimum of 25 disbursement occurrences**

If both are material, both minimums apply independently — minimum 25 payroll + 25 disbursements across the engagement.

**Important wrinkle**: if one program has all (or most) of the payroll, that program's sample may need to expand significantly to hit the 25 payroll minimum, even if the other program's substantive sample doesn't need the volume. This can produce heavy samples in some programs and lean ones in others. Document the rationale.

## Step 5 — Size each program's substantive sample

Per program, apply `controls-compliance-dual` per the questions:
- Is RMM for the program medium or lower?
- Are controls expected to be reliable?

If both yes → **n = 25** for the program
Otherwise → **n = 40** for the program

This is the **substantive minimum** for the program. The cross-program control minimums (Step 4) may push the actual selection count higher in some programs.

## Step 6 — Build the per-program selections

For each program:

1. Start with the program's substantive sample size (Step 5: 25 or 40)
2. If payroll is material to this program AND we need payroll occurrences toward the 25-cross-program minimum, weight selections toward payroll until the cumulative payroll count across all programs hits 25
3. Same for disbursements
4. **IDC**: If IDC is material to the program, include **at least 1 IDC selection**. Include up to **2** if IDC makes up an unusually high % of the program's expenditures. **Never more than 2 IDC** selections per program
5. Apply general population cleanup and selection bias rules (`references/general-rules.md`) — voids out, no negatives unless population dominated, skew larger with some medium coverage, etc.

## Step 7 — Document the sample plan

In the documentation file (`references/output.md` File 2), per program:
- Program name and federal award number
- Program materiality (Step 2)
- Material transaction types (Step 3)
- RMM and controls reliance answers (Step 5)
- Substantive n
- Actual selection count (after cross-program adjustments)
- IDC selections counted
- Cross-program totals: total payroll occurrences, total disbursement occurrences (confirm minimums met)

## Future TODOs

The user has flagged this workflow as evolving. Items pending:
- Mixed RMM / controls scenarios — confirm sizing when one is yes and the other is no (currently 40)
- Type A vs Type B program sizing nuances if any
- Compliance Supplement-specific selection rules per requirement
- How to handle programs with non-payroll, non-disbursement expenditure types that have their own material control populations
