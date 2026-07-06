# General Sampling Rules

Two layers: **population cleanup** (applied before computing n) and **selection bias** (applied while pulling items).

## Layer 1 — Population cleanup

Run on the source data before sizing the sample.

- **Remove voided / reversed transactions.** Look for `Void`, `Voided`, `Cancelled`, `Reversal` markers in description, status, type. Match offsetting entries (positive + matching negative on same date / same reference).
- **De-duplicate** exact duplicate rows.
- **Drop scope-violators**: wrong period, wrong account, wrong entity.
- **Document removed items** by reason and dollar amount in the documentation file.

## Layer 2 — Population integrity

- Reconcile cleaned population to source balance (GL, TB, sub-ledger).
- Document the variance and explain it (timing differences, classification, immaterial cleanup).
- If variance is material to the assertion, escalate to user before sampling.

## Layer 3 — Selection bias rules

Apply during selection, after the method has been chosen and n computed.

- **Don't pull duplicates within a sample** — if the cleanup missed something, catch it here.
- **Don't pull negatives** (refunds, NSF reversals, credit memos) unless:
  - The sample MD explicitly says to include them
  - The population is dominated by negatives (and the test is about that population)
- **Avoid trivially small items** in general — they don't teach much. Pull them only when needed to fill out a static sample size or when the MD specifically calls for small-item coverage.
- **Skew toward larger items** but include some coverage on medium and small items — unless the method's selection logic says otherwise:
  - `60-percent-coverage` and `test-to-below-tm` are inherently top-down — already biased
  - `sampling-form` is typically random — don't override its randomness
  - `static-sample` follows the MD's selection guidance — defer to it
- **Random selection requires a documented seed.** Record it in the documentation file.

## Sampling unit

Sample at the unit defined in the sample MD (transaction, batch, vendor, customer, employee, period, distribution event, etc.). Don't sample at a different level than the method or sample MD specifies — e.g. don't pull individual invoices when the unit is the vendor, or individual journal-entry lines when the unit is the batch. Mixing units distorts both the sizing and the coverage conclusion.

<!-- [recovery 2026-06-01: trailing text reconstructed from context after a write-truncation; verify] -->
