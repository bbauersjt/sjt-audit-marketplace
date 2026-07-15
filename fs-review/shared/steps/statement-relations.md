# Statement Structural Relationships (Math Adjudication)

1. The footing and cross-footing arithmetic is performed by a deterministic script (`scripts/foot.py`) over the figures extracted into `statements.json`.
2. Adjudicate the script's output against the structural relationships below — confirm every relation holds, investigate every exception, and turn every unexplained exception into a finding.
3. Verify each relation using the extracted figures in `statements.json` / the `foot.py` report; never do mental arithmetic on the PDF text.
4. Rounding — zero tolerance: every column in the printed document must foot to the printed total exactly. A difference of any amount — including $1 — is a finding. Rounding is an explanation, not an excuse; flag it regardless.

**NOTE:** *The underlying schedules were prepared in Excel. Do not assume subtotals are correct. Hidden rows, rounding errors, or formula errors may cause presented totals to differ from the actual sum of visible line items. `foot.py` recalculates everything from the individual extracted line items — adjudicate its report; do not trust any printed total.*

## Every column foots
1. Every column of every financial statement, schedule, and table must sum to the subtotal or total presented. Confirm each column's result in the `foot.py` report and flag every column that does not foot to its printed total.

## Every row cross-foots
1. Confirm that each row total equals the sum of the columns that are intended to sum across.
2. In consolidating statements, combining statements, and segment reports, confirm all columns add correctly across each row and down each column. For consolidating statements, confirm: (entity 1 + entity 2 + ... + eliminations = consolidated).

## Subtotals and totals at every level
1. Where totals are built from subtotals, verify each subtotal independently, then verify the total as the sum of the subtotals.

## Balance Sheet / Statement of Financial Position
1. Confirm total assets equals total liabilities and equity.
2. Confirm current vs. non-current classification totals foot to the grand totals.

## Income Statement / Statement of Operations
1. Confirm gross profit = revenue − cost of sales (if presented with this structure).
2. Confirm operating income = gross profit − operating expenses.
3. Confirm income before taxes = operating income + other income/(expense).
4. Confirm net income = income before taxes − income tax expense.
5. Confirm any per-share data (if presented — rare in private companies but occurs in ESOPs and some closely-held structures): weighted average shares, basic EPS, diluted EPS all internally consistent.

## Statement of Stockholders'/Members'/Partners' Equity
1. Foot every column of equity rollforward (common stock, APIC, retained earnings, treasury stock, AOCI for corporations; member contributions, distributions, income allocations, ending capital for LLCs; partner capital accounts with separate columns per partner or class for partnerships).
2. Confirm beginning balance + changes = ending balance for each equity component.
3. Confirm the ending equity total equals the total equity on the balance sheet.
4. For partnerships and multi-member LLCs, confirm income/loss allocations across partners/members sum to total net income/loss on the income statement.
5. For S corporations, confirm AAA, PTI, OAA, and other S-corp-specific equity accounts (if disclosed) rollforward correctly.

## Statement of Cash Flows
1. Confirm operating, investing, and financing totals sum to net change in cash.
2. Confirm net change in cash + beginning cash = ending cash, and ending cash ties to the balance sheet.
3. Confirm the indirect method reconciliation starts with net income that matches the income statement.
4. Confirm any supplemental disclosures (interest paid, taxes paid, non-cash investing/financing) are internally consistent with the notes.

## Debt Schedules
1. Foot all maturity schedules. Confirm totals agree to the applicable note disclosure and to the face of the financial statements.
2. Confirm current portion of long-term debt + long-term debt = total debt per the note and the balance sheet.

## Capital Asset / Fixed Asset Schedules
1. Foot beginning balances, additions, disposals, and ending balances.
2. Confirm accumulated depreciation rollforward ties.
3. Confirm net PP&E ties to the balance sheet.

## Lease Schedules (ASC 842)
1. Foot right-of-use asset rollforward and lease liability rollforward.
2. Confirm the maturity schedule of lease payments ties to the lease liability note disclosure.

## Inventory Schedules
1. Foot any disclosed inventory components (raw materials, WIP, finished goods, reserves).

## Consolidating / Combining Schedules
1. Confirm each subsidiary column foots independently.
2. Confirm eliminations column is internally consistent (assets eliminated against liabilities; intercompany revenues eliminated against intercompany expenses).
3. Confirm the consolidated/combined column equals the sum of component entities plus eliminations.

**NOTE:** *Flag every instance where a figure does not recalculate correctly, with the location, the presented figure, and the recalculated figure.*
