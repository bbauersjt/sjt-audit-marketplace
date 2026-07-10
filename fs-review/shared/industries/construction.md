# Industry Overlay — Construction Contractors

Load whenever the package shows contractor signals: contract receivables, costs and
estimated earnings in excess of billings (underbillings) or billings in excess of costs
and estimated earnings (overbillings), retainage, a schedule of contracts in progress /
completed contracts, percentage-of-completion or cost-to-cost language, backlog, surety
or bonding references. Applies on top of the framework modules (usually commercial).

## Job schedules (supplementary information)

Contractor packages typically present two supplemental schedules. Both are in scope and
both run through the deterministic pipeline — run `tie_wip.py` against the contracts-in-
progress schedule and VERIFY its printed column mapping before trusting results.

### Schedule of contracts in progress (WIP)

`tie_wip.py` recomputes, per job, every relation the schedule's columns allow:

- total estimated cost = costs incurred to date + estimated cost to complete
- estimated gross profit = contract price − total estimated cost
- percent complete = costs incurred to date ÷ total estimated cost (cost-to-cost)
- revenues earned = percent complete × contract price
- gross profit to date = revenues earned − costs incurred to date
- over/(under)billings = billings to date − revenues earned

Adjudication: recompute diffs ≤ $2 are percent-rounding artifacts — note, don't flag
unless pervasive. Anything larger is a finding (wrong percent, stale estimate, or a
hand-keyed cell). Column footings are zero tolerance like everything else.

Then tie the schedule to the statements:

- Sum of underbillings (negative over/under rows) = **costs and estimated earnings in
  excess of billings on uncompleted contracts** (asset) on the balance sheet.
- Sum of overbillings (positive rows) = **billings in excess of costs and estimated
  earnings on uncompleted contracts** (liability). The two must NOT be netted unless a
  right of setoff exists and the presentation says so — netting is a finding.
- Contracts-in-progress revenues earned + completed-contracts revenues (below) +
  any non-contract revenue = contract revenues earned on the income statement.
- Corresponding costs tie to cost of revenues earned; gross profit ties by arithmetic.

### Schedule of completed contracts

- Foot every column (pipeline does this; adjudicate FAILs).
- Per job: gross profit = contract revenues − contract costs.
- Combined with the WIP schedule, current-year revenue/cost/gross-profit totals must
  reconcile to the income statement. A common error: the completed schedule shows
  since-inception amounts while the IS needs current-year amounts — confirm which the
  schedule presents and that the reconciliation is disclosed or derivable.

## Balance sheet / classification checks

- **Contract receivables** — confirm retainage receivable is disclosed (amount and,
  if long-cycle, expected collection); billed vs. unbilled receivables distinguished
  where material.
- **Over/underbillings both absent** with active contracts is implausible — every open
  job is either over- or underbilled by some amount at any date. Flag.
- **Classified balance sheet**: contractors commonly use an operating-cycle basis where
  the cycle exceeds one year — confirm the policy note says so if retainage or contract
  balances extend beyond 12 months.
- **Contract assets/liabilities terminology (ASC 606)** — "costs and estimated earnings
  in excess of billings" and "contract assets" are both acceptable, but usage must be
  consistent between the face, the notes, and the schedules.

## Income statement / revenue recognition (ASC 606 for contractors)

- Revenue recognition note must describe: performance obligations (typically a single
  PO satisfied over time), measure of progress (cost-to-cost input method), contract
  modifications/change orders (approved vs. unpriced), variable consideration
  (claims, incentives, liquidated damages) and its constraint, and uninstalled
  materials treatment where relevant.
- **Provision for anticipated losses** — any job in the WIP schedule with negative
  estimated gross profit requires the full expected loss recognized immediately (not
  ratably). If the schedule shows a loss job, confirm the loss provision is recorded
  and disclosed. A loss job with percent-complete-recognized loss only is a finding.
- Disaggregation of revenue (e.g., by contract type or market) should sum to total
  revenue.
- Contract balance rollforward disclosures (opening/closing contract assets and
  liabilities, revenue recognized from opening contract liability) — confirm amounts
  tie to the face and to the WIP schedule aggregates.

## Notes and other disclosures specific to contractors

- **Backlog** — if presented (often as unaudited SI or in MD&A-style narrative),
  confirm arithmetic: beginning backlog + new awards − revenues earned = ending
  backlog, and that it is labeled unaudited if unaudited.
- **Retainage payable** to subcontractors disclosed symmetrically with retainage
  receivable where material.
- **Concentrations** — few customers/jobs dominating revenue (common: one job > 10% of
  revenue), geographic concentration, union labor exposure, key supplier/sub reliance.
- **Surety/bonding** — bonding agreements, indemnifications (typically joint and
  several by owners), letters of credit; covenant metrics the surety imposes (working
  capital, tangible net worth) checked against the reported figures — an apparent
  breach without disclosure is a finding.
- **Related parties** — contractor + related-party equipment LLC / real estate LLC is
  the classic structure; confirm VIE analysis or PCC common-control scope-out election
  and related-party lease/rent disclosure.
- **Warranty accruals** where contracts carry warranty obligations.
- **Uninstalled materials / inventory** — materials purchased for jobs but not yet
  installed: confirm consistent policy (inventory vs. contract cost vs. zero-margin
  revenue under ASC 606).

## Plausibility (adjudicate with the paired-accounts module)

- Gross margin by the WIP schedule vs. the income statement overall — a schedule
  showing healthy per-job margins with a thin IS gross profit (or vice versa) needs an
  explanation (unallocated indirect costs, completed-job fade).
- **Profit fade** — jobs whose estimated gross profit shrank materially versus the
  prior year schedule (if available) suggest estimate quality issues; not a document
  error by itself, but flag pervasive fade as a contextual finding for the reviewer.
- Percent complete near 100% with large estimated cost to complete remaining, or 0%
  jobs with billings, are internal inconsistencies — flag.
