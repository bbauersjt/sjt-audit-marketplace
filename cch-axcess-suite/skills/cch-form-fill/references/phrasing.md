# Firm phrasing library

The firm's wording for recurring responses. Verbatim where given.

## Global phrasing rules
- **Every response is either a short narrative or a workpaper-index reference** (the WP/KC index where the support lives, e.g., `0302.1`).
- **WP references are INFERRED from the actual binder, not hardcoded.** Locate the workpaper by its content/type and use its real index — the standard 4-digit scheme (1000 cash, etc.) is a guide only; indexing varies by staff. (Ties into the cch-axcess binder parse — find where the testwork actually lives.)
- **Cross-area sourcing:** some answers are *corroborated* in one section but *sourced* from another (e.g., cash restrictions come from grants/debt/permanent-fund work). Reference the other-area work rather than re-deriving it.
- **N/A blocks — explain once at the top.** The header/gating step of an N/A block carries the reason; sub-steps get a plain "N/A." N/As are always explained, but only at the top level — never repeat per line.
  - *Example:* header "If instances of suspected fraud or noncompliance were noted, perform the following steps" → **"Steps are N/A, no instances of fraud or noncompliance were noted in our procedures."** then each sub-step → **"N/A."**
- **Match the question's tense** — a future-tense prompt gets a future-tense answer.
- **Style:** short, fits on a line. Longer only where a genuine explanation belongs.
- **Prompted fields in [brackets]** get filled per engagement (often a WP reference or a short description).

---

## Captured responses

### Control-cycle documentation approach (KBA-403/404/405/etc.)
> We will gain an understanding of the control system and identify and walk through key controls over significant transaction cycles. The results of these procedures will be considered when performing our risk assessment.

(Future-tense to match the prompt; always applicable under the substantive/understand-only approach.)

### Minutes review (AID-837)
**Workpaper reference**, not narrative — the minutes are summarized in a memo filed in the binder. Response = that memo's index, e.g., **`0302.1`**. (Index is an engagement constant.)

### Going concern conclusion
- **No substantial doubt:** "No circumstances were noted during our procedures that would indicate a going concern."
- **Doubt exists:** "We noted that due to [describe near-term doubt — liquidity, debt maturities the entity may be unable to pay, severe liquidity issues] that there may be doubts about [entity]'s ability to continue as a going concern. See our analysis and conclusion at [going-concern analysis index]." ([describe] is prompted; ends in a WP ref.)

### Management bias in estimates
> Per our testwork over [relevant areas], no indication of management bias was noted.

Usually cited as a **series of WP references**: "Per testwork performed at 1200, 1500 series, no indication of management bias was noted." (The area programs carry the specifics, so the series-cite is sufficient.)

**Default material-estimate areas** (where bias testwork is cited): capital/fixed assets · investments · receivables with allowances · goodwill (impairment) · ROU/lease assets & liabilities *(only if a discount-rate range would be material)* · revenue/expense items driven by estimates. If material elsewhere, list those too.

### Subsequent events (AUD-901) — model
Root: any subsequent events? **No** → procedures still documented (discuss with named management, review subsequent GL through report date, review subsequent minutes/agendas). **Yes** → describe the event, where it is documented in the file, and adjustment vs. disclosure-only.

---

## Cross-references for specific areas

### Substantive-only justification → `approach-decision.md`
The reasoning model, the two-question test, the justification pattern, and the cash model live in `approach-decision.md`. Key rule: the justification expresses the **coverage** — that the pool of procedures already addresses every way the area could be materially misstated, leaving no reasonable likelihood of a remaining material misstatement — **not the tool.** It is never framed as "why analytics do not add"; cash is justified because the substantive work covers every way cash could go wrong, not because analytics add little.

### Related party → `section-library.md` (Related Party Transactions)
Related parties usually exist; not a simple default. The branches — RPTs identified and where documented · arms-length assertion (and whether tested/substantiated) · previously-unidentified RPTs noted during the audit · disclosure adequacy — and the distilled answer are captured in `section-library.md` under Related Party Transactions.
