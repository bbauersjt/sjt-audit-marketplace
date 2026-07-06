# Audit Sampling — User Guide

A skill that picks audit samples for you. Two ways to use it: ask for a specific sample directly, or hand it a trial balance and let it propose what to test.

## What it does

- **Identifies** what samples an engagement needs (FS, EBP, single audit, walkthroughs)
- **Picks the smallest defensible sample** by comparing acceptable methods (60% coverage, test-to-below-TM, sampling form, controls fallback) and picking the one that produces the lowest n
- **Cleans the population** before sampling — removes voids, duplicates, scope-violators
- **Pulls the selections** with selection bias rules baked in — skews larger, avoids negatives, avoids trivially small items
- **Outputs two Excel files**:
  - **Pull file** — sterile, one tab per sample, hand to staff
  - **Documentation file** — workpaper-styled with methodology, strata, coverage, thresholds, for the binder

## How to use it — direct sample requests

Just ask for the sample. The skill picks up phrases like:

- "Pull a sample of distributions"
- "Sample AR for me"
- "Pull AJEs"
- "Run vendors for [client]"
- "Sample participant data for the EBP"

The skill will:
1. Find the matching sample type
2. Ask for any source documents it needs (GL, register, aging, census file, etc.)
3. Ask for tolerable misstatement (TM) if the method needs it
4. Apply cleanup, pick the method, pull the selections
5. Produce the Excel files

If you've already given it the docs and TM in the conversation, it skips the asking and goes straight to pulling.

## How to use it — engagement intake

Hand it a trial balance and ask:

- "What samples does this engagement need?"
- "Build me a sampling plan from this TB"
- "Identify samples for this engagement"

The skill will:
1. Infer engagement type from the chart (FS / EBP / single audit / nonprofit FS) — or ask if it's not obvious
2. Propose the mandatory samples plus optional ones based on what the TB shows
3. Apply the walkthrough omission rule (if you're testing controls over vendors, it skips the vendor walkthrough — you don't need both)
4. Ask for TM once, up front
5. Wait for your confirmation, then pull the confirmed samples

## What you'll be asked for

Depending on the sample, the skill may ask for any of:

- **Trial balance** (for engagement intake)
- **Source data** — GL detail, AR aging, AP aging, check register, payroll register, distribution register, census file, contribution detail, SEFA, statement copies, etc.
- **Tolerable misstatement** — as a dollar figure, ask once and it'll be carried for the engagement
- **Engagement type** — if it can't be inferred from the TB
- **Risk answers** — for single audits, RMM and controls reliance per program
- **Compliance supplement** — for SA reporting, either a supplement file or confirmation it can find applicable reports online

The skill batches these asks — when something's missing, it asks for everything missing in one message. Don't expect drip-feed questions.

## What you'll get back

**Pull file** (`<client>_<period>_sample_pull.xlsx`)
- One tab per sample
- Heading + selections table only
- Trimmed columns — only what staff needs
- No methodology, no scoping — sterile

**Documentation file** (`<client>_<period>_sample_documentation.xlsx`)
- Summary tab — one row per sample with methodology, n, population, coverage, TM, strata
- Per-sample tabs with Purpose / Procedure / Notes / population reconciliation / methodology block / coverage table / selections / Conclusion placeholder
- Workpaper-styled (Aptos Narrow 11, header block, red bold PPC labels)

If you only ask for "the sample," you get the Pull file. If you ask for "the workpaper" or "for the file," you get the Documentation file. Or both if you ask for both.

## What the skill won't do

- It won't trigger if you give a fully specified random pull with no judgment ("pull 25 random rows from this CSV"). That's a data manipulation request, not a sampling one
- It won't compute n until TM is in hand for samples that need it
- It won't proceed without source data — if a doc is missing, it'll ask
- It won't double-up walkthroughs and controls testing of the same area (omission rule)

## Sampling methods used

You generally don't need to pick — the skill picks the smallest acceptable n. But for reference:

- **substantive** (composite) — picks the smallest of: 60% coverage, test-to-below-TM, sampling form, controls-substantive-fallback (n=25)
- **controls-substantive-dual** — n=25 (or 10% rounded up if population <250) for EBP-style dual-purpose
- **single-audit** — runs the full SA workflow (program materiality, cross-program control minimums, IDC handling, per-program 25 or 40)
- **compliance-sample** — n=25 (or 10% rounded up if <250) for non-financial compliance like state OSA
- **control-sample** — n=25 (or 10% rounded up if <250) for tests of controls
- **static-sample** — n driven by the sample MD (typically 5; some have variable n driven by their selection rule)
- **progressive-subsequent** — TM/3 month 1, 2TM/3 month 2, TM month 3+ for AP / AR completeness
- **planning-walkthrough** — judgmental, identified-area

## Samples currently supported

- **FS substantive**: AR, AP (completeness), revenue
- **Walkthroughs / static**: vendors, payroll, receipts, credit cards, AJEs
- **EBP**: distributions, loans, participant data (combined demographic + eligibility + individual contributions)
- **Single audit**: major program transactions, reporting

## Tips

- Provide TM upfront in the conversation if you know it — saves a question
- If you have multiple clients in flight, mention which one — naming gets clearer
- For a workpaper-styled output, include a workpaper trigger word: "workpaper," "WP," "memo," "for the file"
- For a plain data dump on an existing tab, say "dump this on a new tab" or "put this on a tab" — no PPC fluff
- If the skill misses something or proposes something off, push back — it's faster to course-correct than to redo

## Asking for this guide

If you're in a Cowork chat and want to read this guide, ask:

- "Show me the audit sampling user guide"
- "How do I use the audit-sampling skill"
- "Read the user guide for audit-sampling"

Claude will pull it up.
