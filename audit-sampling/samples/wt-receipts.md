---
name: wt-receipts
category: wt
mandatory: false
description: Cash receipts walkthrough — substantive testing of recorded receipts for proper recognition, classification, and timing. Static n=5.
acceptable_methods: [static-sample]
mandatory_method: static-sample
n: 5
required_documents:
  - Cash receipts journal / register for the period
  - GL cash account detail
  - Bank statements for the period (for tracing)
---

# Cash Receipts Walkthrough

Static sample, **n = 5**.

## Selection logic
- Skew toward larger receipts; include 1–2 mid-sized items for coverage
- Avoid trivially small items
- Avoid negatives (NSF reversals, returned items) unless those are the population
- Include any unusual or one-time large receipts
- Spread across the period — don't pull 5 from one month if the population spans the year

## Omission rule

**Skip this sample when any of the following are true:**

- Significant controls testing of revenue / deposits is happening elsewhere, OR
- Revenue (`fs-revenue`) hits the `controls-substantive-fallback` method, OR
- Revenue (`fs-revenue`) is being tested substantively at meaningful coverage — i.e., `60-percent-coverage` or `test-to-below-tm` wins the substantive comparison.

The principle: if you're already going deep on revenue — whether through controls testing, controls fallback, or substantial substantive coverage — the audit team will apply walkthrough-style procedures in that work, and this separate n=5 receipts walkthrough becomes redundant. When in doubt, confirm with the engagement team before omitting.

<!-- [recovery 2026-06-01: trailing text reconstructed from context after a write-truncation; verify] -->
