# Complete Knowledge Inventory (distilled) + Defaults worksheet

Every distinct thing the engine must know to answer the planning + concluding forms accurately, deduplicated across all sections, types, and the SA module. This is the distilled "what you need to know," and the worksheet for the defaults pass.

**Handling tags:**
- **[D]** — near-invariant boilerplate → **auto-filled silently; the user reviews the completed binder, not each answer.**
- **[C]** — defaults to no/none but a "yes" is rare and material → default applied, but **confirmed once in the gather-phase batch** before write.
- **[L]** — looked up from client docs / TB / prior file (entity fact).
- **[A]** — genuinely asked (no good default; varies every engagement): named people, interviewees, dates.
- **[M]** — memo narrative, carried forward and updated (memo-format toggle).
- **[X]** — cross-reference to the owning form (`form-content-reference.md` §2; resolve the per-title ID via §2b).

**Gather-phase order:** (1) glean all [L] facts + [M] narratives from the mounted file; (2) ask the [A] knowns (people, interviewees, dates, predecessor, designated individual, new-vs-continuing); (3) present the [C] confirm-defaults as one batch, each pre-set to no/none, user flags exceptions. Then fill: [D] auto, [C]/[K] from steps 2–3, [X] by recognition index. Nothing tagged [D] is ever asked.

---

## CORE — every engagement, every type

### 1. Engagement profile cluster — [D] (firm / engagement-type)
new vs recurring · GAGAS (government: Yes) · Single Audit (if federal awards) · integrated audit (No) · **test controls operating effectiveness — [X]→AUD-100** (read RA's live answer; No/substantive only if RA is silent — do not silently auto-fill) · rely on prior-year control evidence (No) · KAM (No) · EQ/concurring review (per policy) · nonattest = FS prep (Yes) · SAS-146/SQMS early-adopt (No) · interim substantive · CAATs · access granted to outside parties (federal: often Yes) · multiple opinion units/components.

### 2. Entity & client facts — [L]
legal name · location · contact block · entity type/legal form · reporting framework · FYE/FS date · # employees · reporting-entity composition (component units in/out) · funds / opinion units · accounting & IT system · funding sources / federal awards present.

### 3. People — [A]
key management names & titles · those charged with governance / governing body name · reviewers (partner/manager/EQ) · predecessor auditor + contact (if new) · nonattest designated individual + SKE · fraud-inquiry interviewees.

### 4. Acceptance & independence — [D]/[C]
**[C] confirm:** integrity concerns (none) · fraud/noncompliance awareness (none) · disagreements/limitations (none) · independence threats (none). **[D] auto:** competence/resources/time (yes) · accept/continue (yes) · nonattest independence not impaired (yes) · GAGAS independence documented (yes).

### 5. Understanding the entity — [M] + [L]
entity/environment narrative by category (memo) · regulatory & economic factors · investments · **related-party listing [L]** · **going-concern indicators [L]** · litigation/contingencies [L] · significant unusual transactions · IT/cybersecurity.

### 6. Fraud & noncompliance inquiry (KBA-303) — [A] — NO DEFAULT
Fill manually — actual inquiries of named people. The engine surfaces interviewees + prompts; never pre-fills answers. (Auditor's own fraud-awareness at acceptance → KBA-201 [D]; fraud presumptions → KBA-501 [D].)

### 7. Controls — [D] + [M]
control approach (substantive, control risk = max) [D] · COSO 5 components present & functioning, no deficiency [D] · IT environment [L] + ITGC present [D] · per-cycle walkthrough narrative [M/L] · SoD adequate / operating as documented / no deviations [D] · **control deficiencies → none [C]** · controls-reliance overrides (e.g., current-year procurement testing) [A].

### 8. Team discussion — [D] + constants
fraud presumptions (improper revenue recognition + management override) [D] · professional-skepticism narrative [D] · attendees + date (constants).

### 9. Audit team & timing — [A]
team members/roles · RMM & fraud discussion dates · fieldwork start/end · manager/partner/EQ review dates · wrap-up.

### 10. FS-area gating toggles — [L] (entity-fact-driven, default No unless a balance exists)
per balance area (cash, AR/revenue, inventory, PPE, AP, payroll, debt, equity, etc.): does the balance exist / is it material · related-party balances · pledged/assigned · long-term · improper-revenue-recognition fraud risk. (Selection is the risk-assessment's; the engine answers the toggles from the TB.)

### 11. Concluding findings — [C] (default none/no; confirmed once in the gather batch)
subsequent events (none) · going concern (no) · litigation/contingencies (none) · related-party transactions (none beyond normal) · management bias in estimates (no) · significant unusual transactions (none) · business combinations/mergers (none) · significant matters (none) · control deficiencies (none).

### 12. Reviewer & documentation checklists — [D] (all yes/satisfied/documented)
KBA-902 review attestations · KBA-903 documentation completeness. Exceptions that can go No/N-A: legal-counsel confirmations (if no litigation), component auditor, KAM.

### 13. Standard references / constants — [D]/[L]
testing-WP indexes (JE, related party, subsequent events, FS review, analytics, minutes) · standard records source ("the general ledger") · minutes name (e.g., General Assembly) · report date.

---

## TYPE ADD-ONS

### EBP
plan profile [L/A]: plan type (DC/DB/H&W + sub-flavors), plan name/number, sponsor EIN, plan year, trustee/custodian/recordkeeper · **§103(a)(3)(C) limited-scope election [A]** (certified vs non-certified investments) · SOC-1 used? [L] · plan-characteristic toggles [L] (contributions, forfeitures, rollovers, loans/hardship, benefit-payment types) · tax-status facts [L] (plan document type, IRS determination letter, Form 5500 draft, amendments).

### NPO
net assets with donor restrictions? [L] · contributions/support toggles [L] (cash, in-kind, contributed services, conditional promises, agency transactions, fundraising) · split-interest agreements [L] (default No) · functional expense allocation [L/M] · endowment/UPMIFA [L].

### Commercial
revenue/AR (606) toggles [L] · inventory toggles [L] (observation, perpetual, FIFO/LIFO, manufacturing, warehouses, pledged) · income tax (deferred/UTP) [L] · equity structure [L] (share-based comp, treasury/preferred, OCI) · VIE [L] (primary beneficiary, PCC alternative).

### Single Audit module (government/NPO + federal awards)
SEFA facts [L] (programs/ALN/expenditures/clusters/pass-through/de-minimis) · major-program determination [A/det] (Type A/B, low-risk auditee, coverage %) · compliance-requirement matrix per major program [det] (the 12 D&M requirements) · controls over compliance [D] (substantive default, or reliance override) · SEFA presentation checklist [D] · questioned costs / noncompliance findings [D: none].

---

## The defaults set
**[D] generic** (sections 1, 7-COSO, 8, 12, 13 + control/SA affirmations) → auto-filled silently. **[C] confirm-default** (the rare-yes-material items in sections 4, 7-deficiencies, 11) → surfaced once in the gather-phase confirm batch, default applied, before write. **[A]/[L]** → gathered from the file or asked. The user reviews the completed binder; only [C] items and genuine [A] knowns interrupt the fill.

## Distillation check
Whole-engagement knowledge reduces to: ~15 profile toggles + ~12 entity facts + ~6 people + ~7 understanding/narrative items + the per-area TB toggles + ~8 default-none findings + the type/SA add-ons. The forms' thousands of boxes collapse onto this list via the seven levers. No form mechanics remain in the inventory — it is purely what must be known.
