# NPO — Not-For-Profit

PPC-derived CCH inherent risk defaults. CR defaults to MAX. Tune per engagement.

## Cash and Cash Equivalents

| Assertion | IR |
|---|---|
| EO | MOD |
| RO | LOW |
| CO | LOW |
| AV | LOW |
| CU | MOD |
| UC | LOW |

## Investments and Derivatives

| Assertion | IR |
|---|---|
| EO | MOD |
| RO | MOD |
| CO | LOW |
| AV | MOD |
| CU | LOW |
| UC | MOD |

## Promises to Give

| Assertion | IR |
|---|---|
| EO | MOD |
| RO | MOD |
| CO | LOW |
| AV | MOD |
| CU | LOW |
| UC | MOD |

## Support

| Assertion | IR |
|---|---|
| EO | LOW |
| RO | MOD |
| CO | LOW |
| AV | MOD |
| CU | LOW |
| UC | LOW |

## Accounts Receivable

| Assertion | IR |
|---|---|
| EO | LOW |
| RO | LOW |
| CO | LOW |
| AV | LOW |
| CU | LOW |
| UC | LOW |

## Program Svc Fees and Other Revenue

| Assertion | IR |
|---|---|
| EO | LOW |
| RO | LOW |
| CO | LOW |
| AV | MOD |
| CU | LOW |
| UC | MOD |

## Donated Materials, Facilities, and Svcs

| Assertion | IR |
|---|---|
| EO | LOW |
| RO | LOW |
| CO | LOW |
| AV | LOW |
| CU | LOW |
| UC | LOW |

## Inventory and Cost of Sales

| Assertion | IR |
|---|---|
| EO | LOW |
| RO | LOW |
| CO | LOW |
| AV | LOW |
| CU | LOW |
| UC | LOW |

## Property and Equipment

| Assertion | IR |
|---|---|
| EO | LOW |
| RO | MOD |
| CO | MOD |
| AV | LOW |
| CU | MOD |
| UC | LOW |

## Prepaid Expenses and Other Assets

| Assertion | IR |
|---|---|
| EO | LOW |
| RO | LOW |
| CO | MOD |
| AV | MOD |
| CU | MOD |
| UC | MOD |

## Goodwill and Intangible Assets

| Assertion | IR |
|---|---|
| EO | LOW |
| RO | MOD |
| CO | LOW |
| AV | MOD |
| CU | LOW |
| UC | MOD |

## Expenses for Programs/Support and AP

| Assertion | IR |
|---|---|
| EO | LOW |
| RO | MOD |
| CO | LOW |
| AV | MOD |
| CU | LOW |
| UC | LOW |

## Payroll Liabilities and Related Expenses

| Assertion | IR |
|---|---|
| EO | LOW |
| RO | MOD |
| CO | LOW |
| AV | MOD |
| CU | LOW |
| UC | MOD |

## Net Assets

| Assertion | IR |
|---|---|
| EO | MOD |
| RO | LOW |
| CO | LOW |
| AV | MOD |
| CU | LOW |
| UC | MOD |

## Grant and Similar Programs

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

These five risk areas appear on KBA-502 but aren't part of PPC's per-area defaults. CCH-determined applicable assertions only — empty assertions are N/A for the area. CR defaults to MAX; RMM derives from IR×CR (will equal IR when CR=MAX). The AUD-8xx numbers in the headers below are the **NPO title's** numbering; the stable key is the binding key (JE2, RPTRNS2, …) — for any other title resolve each area's program number via `scoping/area-map-by-title.md`.

### Journal Entries (JE2 / AUD-816)

| Assertion | IR |
|---|---|
| EO | MOD |
| CO | LOW |
| AV | LOW |
| UC | LOW |

### Related Party Transactions (RPTRNS2 / AUD-817)

| Assertion | IR |
|---|---|
| CO | LOW |
| AV | LOW |
| UC | MOD |

### Fair Value Measurements and Disclosures (FAIRVALUE2 / AUD-818)

| Assertion | IR |
|---|---|
| AV | MOD |
| UC | MOD |

### Commitments and Contingencies (COMMIT / AUD-819)

| Assertion | IR |
|---|---|
| CO | MOD |
| AV | MOD |
| UC | MOD |

### Concentrations (CONCENT / AUD-821)

| Assertion | IR |
|---|---|
| CO | LOW |
| UC | LOW |
