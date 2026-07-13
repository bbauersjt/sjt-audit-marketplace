# HOA — Homeowner / Common Interest Realty Associations

PPC-derived CCH inherent risk defaults. CR defaults to MAX. Tune per engagement.

## Cash

| Assertion | IR |
|---|---|
| EO | MOD |
| RO | LOW |
| CO | LOW |
| AV | LOW |
| CU | MOD |
| UC | LOW |

## Receivables

| Assertion | IR |
|---|---|
| EO | MOD |
| RO | MOD |
| CO | LOW |
| AV | MOD |
| CU | LOW |
| UC | MOD |

## Revenue

| Assertion | IR |
|---|---|
| EO | MOD |
| RO | MOD |
| CO | LOW |
| AV | MOD |
| CU | LOW |
| UC | MOD |

## Property and Equipment

| Assertion | IR |
|---|---|
| EO | LOW |
| RO | MOD |
| CO | LOW |
| AV | MOD |
| CU | LOW |
| UC | LOW |

## Investments and Derivatives

| Assertion | IR |
|---|---|
| EO | LOW |
| RO | LOW |
| CO | LOW |
| AV | LOW |
| CU | LOW |
| UC | LOW |

## Prepaid Expenses and Other Assets

| Assertion | IR |
|---|---|
| EO | LOW |
| RO | LOW |
| CO | LOW |
| AV | MOD |
| CU | LOW |
| UC | MOD |

## Accounts payable and other liabilities

| Assertion | IR |
|---|---|
| EO | LOW |
| RO | LOW |
| CO | LOW |
| AV | LOW |
| CU | LOW |
| UC | LOW |

## Payroll Liabilities and Related Expenses

| Assertion | IR |
|---|---|
| EO | LOW |
| RO | LOW |
| CO | LOW |
| AV | LOW |
| CU | LOW |
| UC | LOW |

## Debt/Related Liabilities

| Assertion | IR |
|---|---|
| EO | LOW |
| RO | MOD |
| CO | MOD |
| AV | LOW |
| CU | MOD |
| UC | LOW |

## IncomeTaxes

| Assertion | IR |
|---|---|
| EO | LOW |
| RO | LOW |
| CO | MOD |
| AV | MOD |
| CU | MOD |
| UC | MOD |

## Equity

| Assertion | IR |
|---|---|
| EO | LOW |
| RO | MOD |
| CO | LOW |
| AV | MOD |
| CU | LOW |
| UC | MOD |

## Operating Exp and Major Repair and Replacement Exp

| Assertion | IR |
|---|---|
| EO | MOD |
| RO | LOW |
| CO | LOW |
| AV | MOD |
| CU | LOW |
| UC | MOD |

---

## Universal risk-area defaults (apply to all entity types)

These five risk areas appear on KBA-502 but aren't part of PPC's per-area defaults. CCH-determined applicable assertions only — empty assertions are N/A for the area. CR defaults to MAX; RMM derives from IR×CR (will equal IR when CR=MAX). The parenthetical is the area **binding key**, not a form number — the AUD-8xx number is title-specific; resolve it for this title via `scoping/area-map-by-title.md`.

### Journal Entries (JE2)

| Assertion | IR |
|---|---|
| EO | MOD |
| CO | LOW |
| AV | LOW |
| UC | LOW |

### Related Party Transactions (RPTRNS2)

| Assertion | IR |
|---|---|
| CO | LOW |
| AV | LOW |
| UC | MOD |

### Fair Value Measurements and Disclosures (FAIRVALUE2)

| Assertion | IR |
|---|---|
| AV | MOD |
| UC | MOD |

### Commitments and Contingencies (COMMIT)

| Assertion | IR |
|---|---|
| CO | MOD |
| AV | MOD |
| UC | MOD |

### Concentrations (CONCENT)

| Assertion | IR |
|---|---|
| CO | LOW |
| UC | LOW |
