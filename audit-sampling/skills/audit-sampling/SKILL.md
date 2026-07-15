---
name: audit-sampling
description: Use this skill any time the user asks to pull, identify, or plan an audit sample. Triggers on phrases like "pull a sample of [balance]", "sample AR/AP/distributions/payroll/credit cards/AJEs/receipts/vendors/participant data", "what should I sample on this engagement", "build me a sampling plan", "identify samples for this trial balance", or when the user provides a trial balance in an audit context and asks what to test. Covers FS substantive samples (fs-*), walkthrough/static samples (wt-*), employee benefit plan audits (ebp-*), single audits (sa-*), and other compliance engagements like state OSA (other-*). Skip only when the user has fully specified a non-business random pull with no judgment required ("pull 25 random rows from this CSV"). Otherwise, lean into using this skill — most sampling requests in an audit context need it.
---

# Audit Sampling

Identify, plan, and pull audit samples. Two modes (direct sample request, full engagement intake). Default: pick the sampling method that produces the smallest defensible sample, run standard cleanup before pulling, and deliver Excel output per `references/output.md`.

## When to invoke

Trigger when the user:
- Names a sampleable thing — "sample AR", "pull a sample of distributions", "AJEs", "vendors", "credit cards", "receipts", "participant data", "fixed asset additions", "capital additions", "R&M testing", "search R&M for capitalizable items"
- Asks for engagement-level planning — "what samples does this engagement need?", "build me a sampling plan"
- Provides a trial balance and asks what to test
- Mentions an EBP, single audit, state OSA, or other compliance engagement and asks about testing

Skip when:
- The user has fully specified a non-business random pull and no judgment is required ("pull 25 random rows from this CSV with these columns")
- The task is data manipulation, not sampling

If unsure, trigger. Undertriggering is the bigger failure mode.

## Sample categories

- `fs-*` — FS substantive samples (AR, AP, revenue, fixed asset additions, capitalizable items search)
- `wt-*` — Walkthrough / static samples (vendors, payroll, receipts, credit cards, AJEs)
- `ebp-*` — Employee benefit plan samples
- `sa-*` — Single audit samples
- `other-*` — Reserved for state OSA / other compliance (none yet)

## Two modes

### Mode A — Direct sample request

The user names a specific balance or transaction stream.

1. Locate the matching sample MD in `samples/` (prefix + keyword match)
2. Read that MD
3. Read each acceptable method's MD in `methods/`
4. Check whether required source documents are in the conversation / uploads
5. Check whether tolerable misstatement (TM) is needed. If any acceptable method depends on TM (most do — `substantive` always needs it, `progressive-subsequent` always needs it), and TM has not already been provided, include it in the missing-docs ask
6. If anything is missing (docs or TM), ask for it in a single batch — don't drip-feed
7. Apply general rules (`references/general-rules.md`) — both population cleanup and selection bias rules
8. Compute n under each acceptable method against the cleaned population. Pick the smallest. If the sample MD declares a `mandatory_method`, use that instead. If `acceptable_methods` includes `substantive`, that token expands to the four-way comparison documented in `methods/substantive.md`
9. Pull the selections per the method's selection logic (and any sample-MD-specific selection rules)
10. Generate output per `references/output.md`

### Mode B — Full engagement intake

The user wants to identify what should be sampled across an engagement.

1. Determine engagement type:
   - If a trial balance is provided, infer from account names (401(k) plan accounts → EBP; federal grant accounts → likely SA candidate; grants receivable / contributions revenue → nonprofit FS; standard commercial chart → FS)
   - If uncertain, ask: FS only / FS + SA / EBP / Other
2. Filter sample MDs by category prefix:
   - FS only → `fs-*` + `wt-*`
   - FS + SA → `fs-*` + `wt-*` + `sa-*`, plus run the single-audit workflow (`references/single-audit-workflow.md`) to size program samples and apply cross-program control minimums + IDC rules
   - EBP → `ebp-*`
   - State OSA / other compliance → `other-*` (may layer on top of FS)
3. Apply mandatory samples first (each MD's `mandatory` field)
4. For optional samples, evaluate against TB balances and engagement context — surface only ones with a meaningful balance or stream
5. Recommend `progressive-subsequent` for AR completeness when nonprofit indicators are present (grants receivable / contributions revenue). For AR, this fires alongside the substantive sample, not instead of it
6. Apply the walkthrough omission rule before finalizing the proposed list:
   - If significant controls testing of vendor disbursements is planned → omit `wt-vendors`
   - If significant controls testing of payroll is planned → omit `wt-payroll`
   - If significant controls testing of revenue / deposits is planned, OR if `fs-revenue` will hit `controls-substantive-fallback` → omit `wt-receipts`
   - Walkthrough-style static samples and controls testing of the same area are redundant — pick one
7. Present the proposed sample list to the user; await confirmation
8. Ask for tolerable misstatement once, up front — get it before running Mode A on each sample so you don't have to ask repeatedly. If the engagement uses different TMs by area, capture that mapping
9. For each confirmed sample, run Mode A. For single-audit programs, follow `references/single-audit-workflow.md` instead of independent Mode A runs per program

## Sampling methods

Method details (size formula, applicability, selection logic) live in `methods/`. Read the relevant method MD before computing n.

**Substantive (composite):**
- `substantive` — Marker that triggers the four-way comparison: `60-percent-coverage`, `test-to-below-tm`, `sampling-form`, `controls-substantive-fallback`. Smallest n wins. See `methods/substantive.md` for the comparison logic. The four underlying method MDs hold the individual sizing formulas

**Controls:**
- `control-sample` — Tests of controls. n = 25 if population ≥ 250, else ceil(population × 10%)

**Compliance (non-financial):**
- `compliance-sample` — Standalone compliance attribute testing. n = 25 if population ≥ 250, else ceil(population × 10%). Used for non-FS compliance like state OSA. Ignore where the same population is also a combined test

**Dual-purpose:**
- `controls-substantive-dual` — Controls + substantive. n = 25 if population ≥ 250, else ceil(population × 10%). Sample must satisfy a valid substantive test. Mostly EBPs

**Single audit:**
- `single-audit` — Marker for the single-audit workflow at `references/single-audit-workflow.md`. Used by all SA samples

**Static / per-MD:**
- `static-sample` — n specified in the sample MD (default 5; some MDs override with variable n driven by their own selection rule, e.g., wt-vendors, wt-credit-cards)

**Planning:**
- `planning-walkthrough` — Identified-area walkthrough; n per MD, no statistical sample

**Subsequent:**
- `progressive-subsequent` — Tiered TM by month after year-end (TM/3 month 1, 2TM/3 month 2, TM month 3+). AP completeness in any engagement; AR completeness for nonprofits with grant income

## Default MO — smallest sample wins

For each sample:
1. Read the sample MD's `acceptable_methods`
2. If `mandatory_method` is set, use it and stop
3. Otherwise, compute n under each acceptable method (expanding `substantive` to its four-way comparison per `methods/substantive.md`) and pick the smallest

## Tolerable misstatement

Most sampling methods need TM (or a TM-derived threshold).

1. Ask once per engagement / Mode B run, t
