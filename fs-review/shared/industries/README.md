# Industry overlays

1. Load one module per industry, on top of the framework modules, when intake detects the
   industry's signals (`shared/steps/intake.md`).
2. Each module covers: the industry's supplementary schedules (with any dedicated script),
   classification/presentation checks, revenue-recognition specifics, disclosures, and
   plausibility checks.

Built:
- `construction.md` — contractors: WIP / contracts-in-progress schedules (`scripts/tie_wip.py`),
  over/underbillings, ASC 606 for contractors, retainage, backlog, bonding.

Planned (add as clients demand — copy construction.md's section structure):
- real-estate.md — rental operations, investment property, depreciation lives, CAM.
- manufacturing.md — inventory costing/standard cost, capacity variances, warranty.
- restaurants-retail.md — sales tax, gift card breakage, franchise fees, leases.
- healthcare.md — patient receivables/contractual allowances, third-party settlements.
