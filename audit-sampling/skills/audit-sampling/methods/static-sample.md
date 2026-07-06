---
name: static-sample
type: static / judgmental
needs_tm: false
---

# Static Sample

## Concept
Fixed or near-fixed sample size driven by the sample MD itself, not by a population formula. Used for small recurring substantive procedures where the firm has standardized n and selection logic per balance / transaction stream.

## Size determination
n is **specified in the sample MD body**. Default for static FS samples is **5** unless the MD says otherwise.

This method does not compute n from population, TM, or risk — it relies on the MD's static rule.

## When to use
- FS substantive samples where the firm uses a standardized small sample (AJEs, payroll testing, cash disbursements, credit cards, receipts)
- Any sample MD that declares `mandatory_method: static-sample`

## When NOT to use
- Substantive testing of large balances where coverage methods are appropriate (AR, AP, revenue) — use 60% / test-to-TM / sampling-form
- Anything where a defensible n requires a population-driven formula

## Selection logic
The selection rules are also MD-driven. Each static-sample MD includes its own selection guidance — e.g., "focus on year-end period," "spread across time periods," "include any unusual large items." Apply the MD's rules, not generic random selection, unless the MD says otherwise.

## Population assumptions
- Cleaned population still required (voids out, dedup applied)
- General selection bias rules still apply (avoid negatives, avoid trivially small items, prefer larger items unless MD says otherwise)
