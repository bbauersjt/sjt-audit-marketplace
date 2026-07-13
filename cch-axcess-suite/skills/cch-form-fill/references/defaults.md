# Defaults — the auto-fill answer set

**Principle:** these are the firm's high-frequency answers, in two tiers:
- **[D] generic default** — **auto-filled silently**; the user reviews the completed binder, not each answer. The ~75% (COSO/controls affirmations, "the entity commits to monitoring activities," substantive approach, reviewer attestations).
- **[C] confirm-default** — defaults to *no/none* but a "yes" is rare and material; the default is applied, but the item is surfaced once in the **gathering-phase confirm batch** so a real exception is caught before write (see the confirm-default list below). Never silently write a [C] item that wasn't confirmed.

Cross-references and known (gathered) answers outrank both — full cascade [X] → [K] → [C] → [D] → blank in `form-content-reference.md` §1.

---

## Confirm-default list — the [C] items (surface once in the gather batch, then apply the default)
These default to *no/none* but get one explicit confirm because a "yes" is material:
- **Acceptance / independence "are you aware of any…":** integrity concerns · fraud / noncompliance / illegal acts · disagreements / unresolved issues / scope limitations · independence threats (KBA-201, AID-201).
- **Concluding findings:** subsequent events · going concern / substantial doubt · litigation / contingencies / claims · related-party transactions beyond normal · management bias in estimates · significant or unusual transactions · business combinations / mergers · significant matters · control deficiencies.
- **Engagement-quality / concurring review (EQR):** default **No** unless firm QM policy requires an EQR for this engagement (a second-partner review captured as the KBA-902 partner sign-off is **not** an EQR). Confirm against firm QM policy per engagement — answering "Yes" activates the KBA-902A/EQR documentation.

Everything else below is **[D] generic** — auto-filled, no confirm.

## Engagement profile cluster
| Toggle | Default |
|--------|---------|
| New vs recurring | recurring (continuing client) — confirm |
| GAGAS / Yellow Book | Yes if government or grant-required, else No |
| Single Audit | Yes if federal expenditures ≥ $750K, else No |
| Integrated audit | **No** |
| Test operating effectiveness of controls | **[X] → AUD-100** — read RA's live answer (via `cch-axcess`, or a `form-fill-context.md` artifact if one exists); default No/substantive only if RA is silent. Do NOT silently auto-fill — a controls-reliance election lives on AUD-100 (mirrors the `ConTestingEffControlQuestion` treatment). |
| Rely on prior-year control evidence | **No** |
| Key Audit Matters | **No** |
| EQ / concurring review (EQR) | **[C] confirm-default — No** unless firm QM policy requires it (second-partner review = the KBA-902 partner sign-off, not an EQR) |
| Nonattest services | **Yes — FS preparation only** ✓ locked (expand-gate — see Locked defaults) |
| SAS-146 / SQMS-1 & 2 early implemented | **No** ✓ locked (standard KBA-902, not 902A) |
| Substantive procedures at interim | No (per engagement) |
| CAATs | No (per engagement) |
| Access to audit docs granted to outside parties | **Yes on Single Audit or EBP; No otherwise** ✓ locked |
| Multiple opinion units | entity fact (government: often Yes) |
| Multiple components/sites | entity fact (default No) |

## Acceptance & independence (KBA-201, AID-201)
**[C] confirm-default:** integrity concerns → **none** · fraud / noncompliance / illegal-acts awareness → **none** · disagreements / unresolved issues / scope limitations → **none** · independence threats → **none**.
**[D] generic:** competence/resources/time → **yes** · accept/continue → **yes** · nonattest independence not impaired → **yes** · GAGAS independence documented → **yes** (when GAGAS).

## Fraud & noncompliance inquiry (KBA-303) — NO DEFAULT
**Fill manually.** These are actual inquiries of named individuals — pick the people, interview them, document their real responses. The engine gathers interviewees and surfaces the prompts, but **does not pre-fill any answer.** (Separate items that still default: the auditor's own fraud-awareness at acceptance on KBA-201, and the KBA-501 fraud presumptions.)

## Controls (KBA-401/402/40x)
**[D] generic (auto-fill):** control approach → **substantive, control risk = max** · COSO components present & functioning → **yes, no deficiency** · ITGC → **present** · SoD adequate / operating as documented / no deviations → **yes**. **[C] confirm-default:** control deficiencies → **none**. (Controls-reliance overrides — e.g., current-year procurement testing — prompt the user.)

## Team discussion (KBA-501)
Fraud presumptions → **improper revenue recognition + management override** · professional-skepticism narrative → standard.
- **Improper-revenue-recognition presumption — default rebutted / low-risk** for NPO / government / EBP (no incentive; EBP custodians do not fabricate returns); addressed via substantive procedures + analytics. **Commercial exception:** elevate where the client has income incentive (covenant pressure, loan, going-concern uncertainty).

## Concluding findings — [C] confirm-default (default none/no; confirmed once in the gather batch)
Subsequent events → **none** · going concern → **no** · litigation/contingencies → **none** · related-party transactions → **none beyond normal** · management bias in estimates → **no** · significant unusual transactions → **none** · business combinations / mergers → **none** · significant matters → **none** · control deficiencies → **none**.

## Reviewer & documentation checklists (KBA-902/903)
All review attestations → **satisfied / yes** · documentation completeness → **all documented / yes**. Legitimate No/N-A: legal-counsel confirmations (if no litigation) · component auditor (No) · KAM (No).

## SA module
Controls over compliance → **substantive default** (reliance override per engagement) · SEFA presentation checklist → **all yes** · questioned costs / noncompliance → **none**.

---

## Locked defaults
- **SAS-146 / SQMS** → not early implemented (No).
- **Nonattest** → FS preparation only. *(Expand-gate: answering the nonattest gate "Yes" expands the full prohibited-services checklist — fill only the FS-prep row; never let the default trip the whole list. If the firm actually performed additional nonattest services (bookkeeping, tax provision, valuation, etc.), that is a [K] known fact — list those services and complete the expanded checklist; do not rely on the locked default to hide them.)*
- **Access to audit docs** → Yes on Single Audit / EBP; No otherwise.
- **EQ review (EQR)** → **[C] confirm-default**, not a silent default: No unless the firm's QM/monitoring policy requires an EQR for this engagement (second-partner review ≠ EQR). Surface it in the gather batch.

## Firm-phrasing note
Text-response defaults that still need the firm's exact wording (capture as you confirm them with the firm): fraud-inquiry narrative, controls narratives, FS-review and SEFA wording. The subsequent-events model wording is captured in `phrasing.md`; use it as the pattern.
