# Cross-Type Core + Delta Taxonomy

**Engagement types:** Governmental, Nonprofit, EBP, Commercial, Construction (its own KC title; the question set overlaps heavily, so it is mapped as well). **Single Audit is a cross-cutting module** (federal awards), not a separate type.

**Anti-repeat principle:** the KC planning/concluding forms are largely **title-uniform** — KBA-200/201/302/303/401/402/501, KBA-102/103/105/902/903, AUD-901/909/813/814, AUD-101/201, COR-203, AID-201/837 share the same structure across all four titles. (Structure is uniform, but some AUD/AID form NUMBERS map to different programs per entity title — see `form-content-reference.md` §2b.) The **knowledge spine is answered once** (the governmental section maps document it). Only the **deltas** below change per type.

---

## Core spine — answer once, applies to all 4 types
Detailed in the section files (`section-01`…`section-06`); these forms and their knowledge requirements are type-agnostic:

- **Acceptance/setup:** AUD-100 tailoring [RA], KBA-200 entity info (skeleton), KBA-201 acceptance, AID-201 nonattest, COR-203 predecessor.
- **Strategy:** AUD-101 master program, KBA-101 strategy (skeleton), KBA-301 materiality [RA], AUD-201 opening balances.
- **Understanding:** KBA-302 (category skeleton + memo toggle), KBA-303 fraud inquiry, AID-837 minutes.
- **Controls:** KBA-401 COSO entity-level, KBA-402 IT — both universal.
- **Risk:** KBA-501 team discussion; KBA-502/503 [RA].
- **Concluding:** KBA-102/103/105 aggregators, KBA-902/903 checklists, AUD-901 subsequent events, AUD-813 JE, AUD-814 related party, AUD-909 FS review (skeleton). _(AUD-813/814 shown are the govt IDs; see `form-content-reference.md` §2b for per-title numbers.)_

Plus the universal machinery: the **engagement-profile cluster**, the **collapse levers**, and the **engagement constants** (the master constants list — the engagement-profile cluster + engagement constants summarized across the section files).

---

## The delta axes — where the 4 types diverge (what must be mapped per type)

### 1. Entity identity & reporting framework
- **Govt:** GASB; funds/opinion units; tribal/municipal/district entity-type list.
- **NPO:** FASB **ASC 958**; net assets with & without donor restrictions; 501(c) type.
- **EBP:** **ERISA** + **ASC 962/960/965**; plan type (DC/DB/H&W); plan sponsor; EIN/PN; **ERISA §103(a)(3)(C)** limited-scope election.
- **Commercial:** FASB ASC; C/S-corp, partnership, LLC.

### 2. Entity-understanding risk areas (KBA-302 embedded items)
- **Govt:** funds, intergovernmental revenue/grants, debt limits, GASB-specific (pension/OPEB, landfill).
- **NPO:** contributions & grants, donor restrictions, endowment/UPMIFA, functional expense, UBI.
- **EBP:** plan provisions & document, parties-in-interest, contributions/eligibility, investment arrangements, prohibited transactions.
- **Commercial:** revenue (ASC 606), inventory, debt covenants, equity, business combinations.

### 3. Activity-level control cycles (the KBA-40x set — from catalog)
- **Govt (403–408):** Cash Receipts · Inventory · Cash Disbursements · Payroll · Treasury · Reporting/Closing.
- **NPO & Commercial (403–411):** Cash Receipts · Inventory · PPE · Other Assets · Cash Disbursements · Payroll · Treasury · Income Tax · Reporting/Closing.
- **EBP:** Cash Receipts · **Benefit Payments** · **Investments** · **Participant Data** · **Loans/Hardship** · AP · Reporting/Closing. _(Map cycles by name; KBA-40x numbers vary by title — do not assume a fixed number.)_

### 4. Audit areas & programs (AUD-8xx — from catalog; selection is [RA], generic step responses are brain)
- **Govt:** fund balance/net position, interfund, budgets, nonexchange revenue, capital assets, landfill, self-insurance.
- **NPO:** net assets, contributions/split-interest, UBI, investments incl. programmatic.
- **EBP:** **participant data 814A-D**, benefit payments, contributions, notes rec. from participants, tax status of plan, **investments certified (802B) vs non-certified (802A)**, change in provider/merger/termination.
- **Commercial:** equity, VIE, share-based payments, income taxes, business combinations.

### 5. Type-unique forms (no govt analog — must read fresh)
- **EBP (largest delta):** participant data, benefit payments, contributions/EC receivable (AID-809/809A), participant loans (AID-812/813), participant confirmation (AID-818), income streams (AID-302), tax status, service-auditor/SOC-1 (AID-847), 103(a)(3)(C) certification.
- **NPO:** split-interest agreements, contributions/pledges, functional expense, endowment.
- **Govt:** SEFA, Single Audit (8000), budgetary, interfund.
- **Commercial:** covenant compliance, VIE, share-based payment.

### 6. Concluding pseudo-program toggles
AUD-909 FS-review and AUD-901/813/814 entity-fact toggles differ (govt: funds/opinion units; EBP: plan-level; NPO: net-asset classes). Same generic-response pattern, different toggle set.

---

## Profile-cluster toggle applicability by type
| Toggle | Govt | NPO | EBP | Comm |
|--------|------|-----|-----|------|
| GAGAS / Yellow Book | ✔ | grant-dependent | — | — |
| Single Audit | ✔ | ✔ | — | — |
| Multiple opinion units / funds | ✔ | — | — | — |
| ERISA / limited-scope (103(a)(3)(C)) | — | — | ✔ | — |
| KAM · integrated · EQ review · nonattest · SAS-146 | firm policy — all types |
| Test controls (default No / substantive) | all types |

---

## Delta reads — status
All four engagement types mapped (forms pulled cross-title into the test binder):
- **Govt** — full section maps (`section-01`…`06`).
- **EBP** — `type-ebp.md`
- **NPO** — `type-npo.md`
- **Commercial** — `type-commercial.md`
- **Construction** — not included in core.
- **Single Audit (8000) module** — `sa-module.md` (S-form series).

**Confirmed across all four:** the form machinery is identical; each type's delta is its entity/plan profile + a set of gating toggles (mostly default No) + a few unique forms (EBP tax status / 103(a)(3)(C); NPO net assets/contributions/split-interest; Commercial 606/VIE/equity). The core spine + collapse levers carry every type.
