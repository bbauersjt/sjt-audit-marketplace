---
name: substantive
type: substantive (composite)
needs_tm: true
---

# Substantive

Composite method that triggers the four-way substantive comparison. When a sample MD lists `substantive` as an acceptable method, all four underlying substantive methods are considered and the **smallest n wins**.

## The four-way comparison
1. **60-percent-coverage** → n_60 (with the +3 rule when untested 40% > TM)
2. **test-to-below-tm** → n_TM
3. **sampling-form** → n_form (skip if firm form not yet supplied — currently TODO)
4. **controls-substantive-fallback** → always 25

Use the smallest. The fallback "wins" when the other three all exceed 25.

## Underlying method MDs
- `methods/60-percent-coverage.md`
- `methods/test-to-below-tm.md`
- `methods/sampling-form.md` (TODO until firm sampling form supplied)
- `methods/controls-substantive-fallback.md`

Read each before computing — the underlying MDs hold the actual sizing logic.

## When to use
- Any sample MD calling for substantive testing of a balance or transaction stream

## TM
Required. Most underlying methods need it. Ask once per engagement and carry forward.

## Selection logic
Per the underlying method that wins the comparison. General selection bias rules (`references/general-rules.md`) still apply.
