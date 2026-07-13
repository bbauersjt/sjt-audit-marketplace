# Area & program map by title

The per-title list of audit areas and the AUD-8xx program each maps to. Used at KBA-400 (which areas/assertions to scope) and at program time (which AUD-8xx to recommend for each significant area).

## The stable key is the AREA (binding key), NOT the AUD number

**Critical:** AUD-8xx program *numbers are title-specific* — the same number maps to different areas across titles. AUD-804 is Inventory under Commercial/Construction, Other Assets under EBP, Nonexchange Revenue under Governmental, and Split-Interest Agreements under NPO. **Always resolve a program by its area binding key + title, never by AUD number alone.**

`cch-axcess` resolves the actual form for a (binding key, title) pair via `catalog.lookup_by_reference_tag` / the rich catalog. This table is the judgment map; the catalog is the source of truth for the exact form ID on a given engagement.

## Audit type → CCH title

ASB→Commercial, HOA→Commercial, CNS→Construction, EBP→Employee Benefit Plans, ALG→Governmental, NPO→Not-for-Profit. (See SKILL.md.)

## Master map — area (binding key) → AUD-8xx number by title

Source: `cch-axcess/references/data/kc-forms-catalog-rich.xlsx` (1,660-form catalog). `—` = the area does not exist as a program in that title.

| Area (binding key) | Plain name | ASB/HOA | CNS | EBP | ALG | NPO |
|---|---|---|---|---|---|---|
| CASH | Cash | 801 | 801 | 801 | 801 | 801 |
| INVEST | Investments | 802A | —† | 802A/802B | 802 | 802 |
| AR | Accounts Receivable / Revenue | 803 | 803 | 803 | — | 803 |
| ERR | Exchange Revenue & Receivables | — | — | — | 803 | — |
| SPLITINTX | Split-Interest Agreements | — | — | — | — | 804 |
| INVENTORY | Inventory & COGS | 804 | 804 | — | 805 | 806 |
| OTHASSET | Other Assets / Other Receivables | — | — | 804 | — | — |
| NER | Nonexchange Revenue | — | — | — | 804 | — |
| REVANDRECEIVABLESX | Contributions, Support, Program Rev | — | — | — | — | 805 |
| PP | Prepaids / Deferred / Other | 805 | 805 | — | 806 | 807 |
| PARTICIPANTNOTES | Participant Notes Receivable | — | — | 805 | — | — |
| INTANG | Intangibles | 806 | 806 | — | — | 808 |
| PPE | Property & Equipment | 807 | 807 | — | 807 | 809 |
| AP | Accounts Payable & Purchases | 808 | 808 | 806 | 808 | 810 |
| OL | Payroll & Other Liabilities | 809 | 809 | — | 809 | 811 |
| BENEFIT | Benefit Payments | — | — | 809 | — | — |
| INCTAX | Income Taxes / UBI | 810 | 810 | — | — | 812 |
| AUD810 | Tax Status of the Plan | — | — | 810 | — | — |
| DEBT | Debt & Debt Service | 811 | 811 | 807 | 810 | 813 |
| CHANGES | Change in Provider/Mgmt | — | — | 811 | — | — |
| EQUITY | Equity / Net Assets / Net Position | 812 | 812 | — | 811 | 814 |
| OTHREV | Other Income & Expense | 813 | 813 | 808 | 812 | 815 |
| JE2 | Journal Entries (risk area) | 814 | 814 | 812 | 813 | 816 |
| RPTRNS2 | Related Party Transactions (risk area) | 815 | 815 | 813 | 814 | 817 |
| AUD815 | Minutes & Other Records | — | — | 815 | — | — |
| (participant data) | Participant Data / Benefit Obligations | — | — | 814A–D | — | — |
| FAIRVALUE2 | Fair Value Measurements (risk area) | 816 | 816 | 816 | 815 | 818 |
| INTERFUND | Interfund Transactions | — | — | — | 816 | — |
| VIE2 | Variable Interest Entities | 817 | 818 | — | — | — |
| CONTRACT | Uncompleted / Completed Contracts | — | 817 | — | — | — |
| BUDGET2 | Budgets | — | — | — | 817 | — |
| STOCK | Share-Based Payments | 818 | 819 | — | — | — |
| DERIVATIVE | Derivative Instruments | 802B | — † | — | 818 | — |
| COMMIT | Commitments & Contingencies (risk area) | 819 | 820 | 817 | 821 | 819 |
| SELF | Self-Insurance | — | — | — | 819 | — |
| (bind=None) | Accounting Estimates | 820 | 821 | 818 | 822 | 820 |
| LANDFILL | Municipal Solid Waste Landfill | — | — | — | 820 | — |
| CONCENT | Concentrations (risk area) | 821 | 822 | 819 | 823 | 821 |
| BUSINESS | Business Combinations | 822 | 823 | — | — | 822 |

Numbers are the AUD-8xx suffix (801 = AUD-801). A/B suffixes are distinct forms (Commercial:
802A Investments, 802B Derivatives & Hedging; EBP: 802A Investments non-certified/ERISA, 802B
Investments certified; EBP 814A DC participant data, 814B DB participant data, 814C H&W DB,
814D Benefit Obligations DB/H&W). † CNS (Construction 2025) — resolve via
the catalog before relying on its Investments/Derivatives rows. Resolve the exact form on the
engagement through `cch-axcess`.

## Title-distinctive areas (scope these only for the matching title)

- **NPO:** SPLITINTX, REVANDRECEIVABLESX (Contributions/Support), INCTAX as UBI. Net Assets = EQUITY.
- **EBP:** OTHASSET, PARTICIPANTNOTES, BENEFIT (benefit payments), AUD810 (plan tax status), CHANGES, AUD815. Plus KBA-200 Plan Info and KBA-301E materiality. Always-significant EBP areas: investments, contributions, benefit payments, participant data, notes/loans.
- **Governmental (ALG):** ERR (exchange revenue), NER (nonexchange revenue), INTERFUND, BUDGET2, DERIVATIVE, SELF (self-insurance), LANDFILL. Equity = net position; scope by opinion unit.
- **Construction (CNS):** CONTRACT (uncompleted/completed contracts — the signature CNS area, revenue recognition over time).
- **Commercial (ASB/HOA):** VIE2, STOCK (share-based payments), INCTAX (income taxes).

## Risk-consideration areas (every title, not driven by a single balance)

JE2, RPTRNS2, FAIRVALUE2, COMMIT, CONCENT, and Accounting Estimates are scoped on most engagements regardless of a balance — they're risk/disclosure areas. Default IR for these is in `defaults/{CODE}.md` under "Universal risk-area defaults." They are part of the always-significant list (`scoping/significance.md`).

## How this drives recommendations

1. From intake, you have the set of **significant** areas (`scoping/significance.md`).
2. For each significant area, look up its program for the engagement's title in the table above → that's the AUD-8xx to recommend/add.
3. On KBA-400, the scoping selections should produce exactly this set; reconcile CCH's recommended forms against your list and resolve differences (CCH may recommend a program you scoped out, or miss one you scoped in — your significance call governs, document the deviation).
4. Hand the program set to `cch-axcess` (`add-audit-programs.md`), which plans against `binder-program-template-{type}.xlsx` and files them.

## Maintenance

When titles re-version, re-query the catalog rather than hand-editing — numbering shifts. The binding keys are stable across versions; the AUD numbers are not.
