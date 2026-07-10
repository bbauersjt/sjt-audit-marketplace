# EBP — Deltas vs. Core

Mapped from live forms (pulled cross-title into the test binder). The machinery is identical to the governmental type: control cycles and programs use the same gate + walkthrough + (controls-N/A under substantive) + analytics + disclosure + WP-ref pattern. EBP's divergence is in the facts and toggles, not the form mechanics. The core spine + collapse levers all carry over; only the items below are new.

---

## EBP-specific additions to the knowledge map

### 1. Plan profile (EBP engagement constants — add to master list)
- Plan type: **DC / DB / H&W**, and sub-flavors (money purchase, cash balance / pension equity, VEBA, multiemployer).
- Plan name, plan number (PN), sponsor EIN, plan year, plan sponsor/administrator.
- **ERISA §103(a)(3)(C) limited-scope election** — the master EBP gate (certified vs. non-certified investments). Determines AUD-802A vs **802B** and whether investment detail is audited at all.
- Service organization / SOC-1 used? (recordkeeper/custodian) → AID-847.
- Trustee/custodian; recordkeeper.

### 2. Plan-characteristic toggles (gate program steps — default per plan type)
Employer contributions? · receivables? · forfeitures? · rollovers? · noncash contributions? · participant loans / hardship withdrawals? · benefit payment types (lump sum vs annuity; previously-audited annuities) · multiemployer? · money purchase? These gate steps on AUD-803/809/814A — answer from the plan profile.

### 3. Tax status / qualification (AUD-810 — 99 boxes, EBP-unique)
The one form with no govt analog. Knowledge to gather (from plan documents):
- Plan document type — individually designed vs. prototype/pre-approved; substantial departures?
- **IRS determination/opinion letter** reviewed.
- **Form 5500** — substantially completed draft obtained before report.
- Plan amendments made for law changes; plan operations revised for compliance.
- Reportable events (DB); correspondence from legal counsel / TPA.

### 4. Control cycles (KBA-40x — same walkthrough structure; map by cycle name, not number)
Cycle list: Cash Receipts · **Benefit Payments & Distributions** · **Investments** · **Participant Data** · **Loans & Hardship Withdrawals** · AP · Reporting/Closing. Same fields as govt (gate → subprocesses → SoD/walkthrough confirmations); only cycle names + subprocess lists change. The KBA-40x numbers vary by title — match each cycle by name, not by number.

### 5. EBP-unique procedures & their testing WPs (generic-response + WP ref, like govt pseudo-programs)
Participant data testing (AUD-814A-D by plan type) · benefit payments (AUD-809) · contributions received/receivable + **timeliness of participant contributions** (AID-809A — the late-deferral/prohibited-transaction check) · participant confirmations (AID-818) · **SOC-1 / service-auditor report review** (AID-847) · investments (802A non-certified / 802B certified).

### 6. The 103(a)(3)(C) structural fork (biggest single EBP difference)
Under a §103(a)(3)(C) (ERISA limited-scope) election, certified investment information is **not audited** (certified by a qualified bank/insurer) → AUD-802B, certified-investments path, and the ERISA-§103(a)(3)(C) opinion (RPT-097x series) + COR-803C certification + COR-901A rep letter + COR-201A engagement letter. Full-scope → AUD-802A and standard opinion. This election reshapes the investment approach and the report — capture it in the plan profile.

### 7. AID-201 — don't add it unless AUD-100 demands it; and there's NO clean N/A shortcut inside
Two lessons from the first EBP run (SFRC 401k 0100, 2026-07-08; refined by the read-only diagnosis pass):

**(a) The right N/A answer is to NOT ADD the form.** AID-201 is add-gated by AUD-100's
`OtherServices` tailoring question. On a no-nonattest engagement, KC's design is that the form is
simply absent — the PPC habit of an always-present independence checklist with a "None performed"
line does NOT map to KC. Adding it anyway costs ~110 permanent diagnostics on the form plus a
permanent `type:"Unnecessary KnowledgeCoach Form"` "remove this workpaper" diagnostic on AUD-100
(it names the form via `unnecessaryWorkpaperReferenceTag: AID_200_NONAUD_SERVI_INDEP_CKLST`).
Check AUD-100's diagnostics for Unnecessary-form entries BEFORE adding pre-engagement forms
(cch-axcess `add-audit-programs.md` gotcha), and remove an already-added AID-201 via
`remove-kc-form.md` rather than trying to answer it quiet.

**(b) When the form IS genuinely needed (nonattest services exist), know its shape.** Unlike
KBA-201's engagement-level TQ shortcut (which cleanly gates its ~89 items off), AID-201 gates
per-category: each header row in `TypeofNonauditService` carries an `Applicable` prop (`YES`/`NO`,
uppercase) that gates its nested `childObjectList` rows; children carry
`Applicable`/`Consideration`/`IndependenceRequirementMet`. EXCEPTION: Header1 "General
Considerations" children are UNGATED — they must always be answered individually. And the rows are
NESTED: the flat objectList shows ~17 objects but there are ~110+ answerable rows down the
`childObjectList` tree (fixture: cch-axcess `references/data/fixtures/aid201-form-get.json`), so
don't trust flat inventory counts. The volume, not the mechanics, is the surprise — the writes are
convention-standard.

---

## What carries over unchanged (no EBP work needed)
Acceptance (KBA-201), entity info (KBA-200 skeleton), independence (AID-201 — content unchanged, but see §7 above for its diagnostic-cascade trap), strategy (KBA-101), fraud inquiry (KBA-303), COSO controls (KBA-401/402), team discussion (KBA-501), concluding aggregators/checklists (KBA-102/103/105/902/903), subsequent events (AUD-901), JE/related-party programs, the engagement-profile cluster (minus GAGAS/opinion-units; plus ERISA/limited-scope), and every collapse lever.

## Net
EBP = core spine + **plan profile** + **plan-characteristic toggles** + **AUD-810 tax status** + **103(a)(3)(C) fork**. Everything else is the govt machinery with relabeled cycles.
