# Maintainers Doc — audit-sampling

Read this file first before adding to or modifying this skill.

## What this skill does

Audit sampling assistant. Identifies what to sample on an engagement (Mode B intake from a TB) or pulls a specific sample on demand (Mode A). Picks the smallest defensible sample size from each sample's acceptable methods. Applies general population cleanup and selection bias rules. Outputs two Excel workbooks — a sterile pull file for staff, and a workpaper-styled documentation file for the binder.

Owner / firm: SJT Group (Brett Bauer).

## File structure

```
audit-sampling/
├── SKILL.md                     # Main skill instructions for the agent — read every invocation
├── MAINTAINERS.md               # This file
├── USER_GUIDE.md                # User-facing guide (Brett or staff can ask for it)
├── methods/                     # Sampling method MDs — sizing logic per method
├── samples/                     # Sampleable item MDs — one per balance / transaction stream
└── references/
    ├── general-rules.md         # Population cleanup + selection bias rules
    ├── output.md                # Excel output spec (revised frequently)
    └── single-audit-workflow.md # Full SA sampling workflow (multi-program)
```

## Naming conventions

Sample MDs are prefixed by category. **The prefix matters** — Mode B uses it for filtering by engagement type.

| Prefix | Category | Examples |
|--------|----------|----------|
| `fs-`  | FS substantive | fs-ar, fs-ap, fs-revenue |
| `wt-`  | Walkthrough / static | wt-vendors, wt-payroll, wt-receipts, wt-credit-cards, wt-journal-entries |
| `ebp-` | Employee benefit plan | ebp-distributions, ebp-loans, ebp-participant-data |
| `sa-`  | Single audit | sa-major-program-transactions, sa-reporting |
| `other-` | State OSA / other compliance | (none yet — reserved) |

When adding a sample, pick the prefix carefully. If you're unsure, ask the user.

## Frontmatter contracts

### Sample MD frontmatter (samples/*.md)

```yaml
---
name: <sample-id>             # Must match filename (e.g., wt-vendors)
category: fs|wt|ebp|sa|other  # Must match prefix
mandatory: true|false
description: <one-line description>
acceptable_methods: [list of method names from methods/]
mandatory_method: <method-name or null>
n: <integer>                  # Only for static-sample with fixed n; omit when variable
required_documents: [list of source docs]
---
```

**No `items_to_request` field.** That was cut. Don't reintroduce without confirming.

### Method MD frontmatter (methods/*.md)

```yaml
---
name: <method-id>
type: <free-form classifier>
needs_tm: true|false
---
```

## Method ↔ sample interdependencies

Sample MDs reference methods by exact name in `acceptable_methods` and `mandatory_method`. **If you rename or delete a method, every sample that references it breaks silently** — Grep first.

Quick reverse map (current state):

- `substantive` → fs-ar, fs-revenue
- `progressive-subsequent` → fs-ar, fs-ap (mandatory)
- `static-sample` → all wt-* samples, ebp-participant-data
- `controls-substantive-dual` → ebp-distributions, ebp-loans
- `compliance-sample` → ebp-distributions (alt), ebp-loans (alt), sa-reporting (mandatory)
- `single-audit` → sa-major-program-transactions (mandatory)
- `control-sample` → currently no sample lists it directly; referenced from SKILL.md and other method MDs

Run this when you change methods:

```
Grep "<method-name>" in samples/ and methods/
```

## Special methods — the two markers

Two methods don't have their own sizing formula — they expand to something else.

### `substantive` (composite)

**Expands to a four-way comparison**, smallest n wins:
1. `60-percent-coverage`
2. `test-to-below-tm`
3. `sampling-form` (TODO — firm form not yet supplied)
4. `controls-substantive-fallback` (always n=25)

The expansion logic lives in BOTH `methods/substantive.md` AND `SKILL.md` ("Sampling methods" section). **Keep them in sync.** If you add or remove a substantive method, update both.

### `single-audit` (workflow marker)

Points at `references/single-audit-workflow.md`. The whole multi-program sizing process lives in that workflow file. The method MD itself is a thin pointer.

If you change the SA workflow, update `references/single-audit-workflow.md` and confirm `methods/single-audit.md` still describes it correctly.

## Cross-cutting rules and where they live

### Walkthrough omission rule

When controls testing of an area is happening on the engagement, omit the corresponding walkthrough.

- `wt-vendors` ← omitted if controls testing of vendor disbursements
- `wt-payroll` ← omitted if controls testing of payroll
- `wt-receipts` ← omitted if controls testing of revenue / deposits, OR if `fs-revenue` lands on `controls-substantive-fallback`

Lives in TWO places:
- `SKILL.md` Mode B (engagement-level enforcement)
- The affected sample MDs (in their "Omission rule" sections)

Keep both in sync when changing the rule.

**Open gap**: Mode A doesn't currently apply this rule. If a user calls `wt-vendors` directly, the skill won't ask whether controls testing is happening. See TODO list below.

### Selection bias rules

Live in `references/general-rules.md`. Apply to all samples unless the sample's MD or the method's selection logic overrides. The bias rules:

- No duplicates within a sample
- No negatives unless MD says otherwise or population dominated
- Avoid trivially small items unless needed
- Skew larger but include some medium / small coverage
- Random selections require a documented seed

If a method (e.g., `sampling-form`, when supplied) uses pure random selection, document that override in the method MD.

### TM (tolerable misstatement)

Required by most methods. Asked once per Mode B run, carried forward. In Mode A, asked only if the sample's acceptable methods need it (most do).

Documented in `SKILL.md` "Tolerable misstatement" section.

### Output spec

Lives in `references/output.md`. **Revise this file frequently** — that's expected. The skill should treat output formatting as soft logic and read this file every time it generates output.

Two-workbook default (Pull file, Documentation file). One-workbook fallback for "plain data dump" requests.

## How to add things

### Add a new sampleable item

1. Pick the category prefix (`fs-`, `wt-`, `ebp-`, `sa-`, or `other-`)
2. Create `samples/<prefix>-<name>.md` with the frontmatter contract
3. Decide acceptable methods. Reuse existing methods if possible. If you need a new method, follow "Add a new method" below
4. Document selection logic in the body. Be specific — staff use this
5. If it's a walkthrough that should be omitted under controls testing, add it to the omission rule (SKILL.md Mode B + the affected MDs)
6. **Update SKILL.md description** to include any new triggering keywords
7. Run validation: `python -m scripts.quick_validate <skill-path>` from the skill-creator dir

### Add a new method

1. Create `methods/<name>.md` with the frontmatter contract
2. Document the size formula concretely. If TODO, mark it clearly
3. Document when-to-use / when-not-to-use / population assumptions
4. If the method is substantive-flavored, decide:
   - Add it to the `substantive` four-way comparison? Update `methods/substantive.md` AND `SKILL.md`
   - Or stand alone (separate `acceptable_methods` entry)? Document the choice
5. Update sample MDs that should accept this method
6. Run validation

### Add a new output format

1. Edit `references/output.md`
2. Don't change the SKILL.md "Output" section unless the high-level structure changes (one workbook vs. two)
3. Confirm the `xlsx` skill produces what you describe — the rendering is done by that skill, not this one

### Update the skill description (triggering)

The `description:` field in `SKILL.md` frontmatter is the **primary triggering mechanism**. Changes here change when the skill fires.

- After significant description edits, consider running the description optimizer (`scripts/run_loop.py` from skill-creator) with a fresh eval set
- Bias toward triggering: undertriggering is the bigger failure mode

## Warnings / common ways things break

- **Renaming a method without grepping** — sample MDs reference methods by exact name. Renames silently break references
- **Deleting a method that's still referenced** — same problem
- **Adding a method to `substantive` without updating SKILL.md** — the description of substantive in SKILL.md is also where the agent learns the comparison list
- **Reintroducing `items_to_request`** — was cut intentionally. If user asks to bring it back, revisit `references/output.md` File 1 and the sample MD shape in SKILL.md too
- **Letting category prefix and `category:` field drift apart** — Mode B filters on prefix, frontmatter validation may rely on field. Keep them aligned
- **Not updating SKILL.md description when adding new sampleable items** — staff might not be able to invoke them by name
- **Static-sample with variable n MDs** (wt-vendors, wt-credit-cards) — these don't have a fixed `n` in frontmatter; the n comes from the MD's selection rule. Don't add `n:` to these or the parser may misread
- **Single-audit logic spread across files** — `methods/single-audit.md`, `references/single-audit-workflow.md`, `samples/sa-major-program-transactions.md`. When changing SA logic, audit all three
- **Output.md is unstable on purpose** — the user wants it revisable. Don't bake output assumptions into other files; read `references/output.md` every time

## Open TODOs

1. **Sampling form formula** — firm-specific, needs Brett's actual sampling form to be dropped in. Currently a placeholder in `methods/sampling-form.md`. Until then, the substantive comparison runs on three methods, not four
2. **Mode A omission rule check** — currently the omission rule only fires in Mode B. If a user calls `wt-payroll` directly via Mode A while controls testing is happening, the skill won't catch the conflict. Decision pending: ask in Mode A or trust the user
3. **Single audit — full logic completeness**:
   - Mixed RMM / controls reliance answers (one yes, one no): currently sized at 40 (conservative) — confirm with firm guidance
   - Type A vs Type B program sizing nuances
   - Compliance Supplement-specific selection rules per requirement
   - Programs with non-payroll, non-disbursement material expenditure types (program income, equipment, subrecipient pass-throughs)
4. **No `other-*` MDs yet** — state OSA, vehicle usage compliance, etc. To be added as encountered
5. **ebp-loans method choice** — currently lists both `controls-substantive-dual` and `compliance-sample`. Confirm preference (keep both? drop compliance-sample?)
6. **fs-ap substantive option** — currently mandatory_method = `progressive-subsequent` only. If recorded-balance testing should be opt-in (not just exceptional override), add `substantive` back to acceptable_methods with a body note

## Available extension points (for future expansion)

- New sampleable items in any category — follow the "Add a new sampleable item" steps
- New output formats / additional workbook types in `references/output.md`
- New sampling methods (firm-specific, regulatory)
- New cross-cutting rules — add to `references/general-rules.md` or create a new references file
- New engagement-type categories beyond fs/wt/ebp/sa/other (haven't needed any)
- Description optimization run via skill-creator's `run_loop.py` after meaningful changes

## Validation and packaging

After every change set:

```bash
# Validate
cd <skill-creator-path>
python -m scripts.quick_validate <path-to-audit-sampling>

# Package
python -m scripts.package_skill <path-to-audit-sampling> <output-dir>
```

Produces `audit-sampling.skill` — the installable bundle.

## Style rules

The user (Brett) has explicit workpaper style preferences captured in his Cowork preferences. Output File 2 (the documentation workbook) must follow them. File 1 is sterile and ignores most of those rules. See `references/output.md` for the application.

The user prefers concise responses, narrator voice (noir), pushback over sycophancy, and explicit confidence ratings. Don't bury concerns under polite hedging.
