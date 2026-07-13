# cch-risk-assessment — README

The risk-assessment **judgment engine** for CCH Axcess (Knowledge Coach) audits. It reads the client (prior FS, prior risk assessment or an example, current-year TB), determines what's significant against tolerable, and decides the **content** of the planning cascade — AUD-100 → KBA-400 → KBA-502 → recommended audit programs. The sibling skill **`cch-axcess`** parses the live forms and executes every write. This skill never touches the platform.

Load both together. **Enter through `SKILL.md` and run its Step 0 first** (load cch-axcess · intake · materiality · significance) — it is a gated dispatcher; sub-references are not valid entry points.

## The cascade (what this skill drives)

```
client docs + materiality
   → intake & significance        (references/intake.md, scoping/significance.md)
   → AUD-100  tailoring/areas      (references/cascade/aud-100.md)
   → KBA-400  scoping + assertions (references/cascade/kba-400.md, scoping/area-map-by-title.md)
   → KBA-502  IR/CR/RMM + approach (references/cascade/kba-502.md, references/risk-framework.md)
   → AUD-8xx  programs + steps     (programs/{area}.md)
```

**Design rule:** parse the cascade **live** via `cch-axcess`; store only judgment + compact lookups here. No field-level form dumps (the forms re-version yearly and are uniform by `dataBindingKey` across titles).

## Layout

```
cch-risk-assessment/
├── SKILL.md                       # Gated dispatcher (Step-0 bootstrap) + cascade spine (read first)
├── README.md                      # This file
├── references/
│   ├── intake.md                  # ingest client docs; derive class balances; get materiality; significance entry
│   ├── risk-framework.md          # 4-level model, RMM matrix, 6 assertions, PPC→CCH map, significant risk, KBA-301/503
│   ├── cch-handoff.md             # HANDOFF protocol → cch-axcess (cascade-ordered; names the AUD-8xx program)
│   └── cascade/                   # the driving forms, one judgment doc each
│       ├── aud-100.md             #   engagement tailoring → areas + controls-testing decision
│       ├── kba-400.md             #   scoping & mapping; relevant-assertion selection
│       └── kba-502.md             #   IR/CR/RMM + planned-approach; the risk summary (writes to the program)
├── scoping/
│   ├── significance.md            #   significance methodology (quant vs tolerable + always-significant list)
│   └── area-map-by-title.md       #   per-title area → AUD-8xx program map (from the rich catalog)
├── defaults/                      # PPC-derived IR starting points by audit type (consumed at KBA-502)
│   ├── INDEX.md  ALG  ASB  CNS  EBP  HOA  NPO
└── programs/                      # Per-area audit-program step libraries
    ├── INDEX.md  _conventions.md  cash.md (template, complete)  + area stubs
```

## Audit type → CCH title

ASB→Commercial, HOA→Commercial, CNS→Construction, EBP→Employee Benefit Plans, ALG→Governmental, NPO→Not-for-Profit. Five underlying titles. The cascade forms (AUD100/KBA400/KBA502) are uniform across them by binding key; **AUD-8xx program numbers are title-specific** — resolve by area, not number (`scoping/area-map-by-title.md`).

## Status

| Component | Status |
|---|---|
| SKILL.md | Gated dispatcher (Step 0: load cch-axcess · intake · materiality · significance) + cascade spine |
| references/intake.md | Document ingestion + significance entry |
| scoping/significance.md | Methodology; **firm-tunable params flagged** |
| scoping/area-map-by-title.md | Per-title program map (catalog-derived) |
| references/cascade/aud-100.md | Methodology solid; live option lists per engagement |
| references/cascade/kba-400.md | The six scoping options confirmed live |
| references/cascade/kba-502.md | **KBA-502 IS the IR/CR/RMM/approach write target; program grids derived** |
| references/risk-framework.md | Shared-collection reframe; KBA-301/503 added |
| references/cch-handoff.md | Cascade-ordered handoff examples; names KBA-502 for IR/CR/RMM writes (programs derived) |
| defaults/{6}.md | IR starting points; title mapping noted |
| programs/cash.md + _conventions.md | Template + universal conventions (mechanics deferred to cch-axcess) |
| programs/{other areas} | Stubs — incremental, captured one at a time |

## Open items

1. ✓ **KBA-502 writable surface.** KBA-502 OWNS the per-assertion IR/CR/RMM/approach
   grid and is the WRITE target (collectionKey `.{AREA}.RelevantAssertion` against **KBA-502's wpId**); the
   AUD-8xx program grid is DERIVED/read-through — program-targeted writes land in a working copy the
   KBA-502-owned recompute discards on refresh. The bulk GET doesn't embed the RelevantAssertion child rows
   (`childObjectList: []`) and `inventory_form` over-filters the form.
2. ✓ **KBA-400's six scoping options** — per-area scoping row + relevant assertions selection (mechanics in cch-axcess).
4. ✓ **Durable write pattern** — per-area writes → per-workpaper submit (KBA-502's wpId) → refresh before
   the next area, from a parked non-target tab; verify via refresh → GetWorkpaperDiagnostics (never the
   in-session echo). propertyType-5
   (`…/ProgramSteps`, `…/plannedauditapproach`) stays linked/never-write; its "Unaddressed" diagnostics
   resolve via program step-linkage/sign-off at section fan-out.

**Still open:**
3. **Firm-tunable significance parameters** — performance-materiality %, clearly-trivial %, the house always-significant list.

## Sibling skills

- `cch-axcess/SKILL.md` — platform mechanics (parse, write, add forms, file leadsheets). Loaded first, every run.
- `cch-form-fill` — the non-cascade planning forms + program-step RESPONSE text. Selection here; responses there.
