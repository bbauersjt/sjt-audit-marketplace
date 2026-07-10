# Statement Structural Relationships (Math Adjudication)

**How this step works:** The footing and cross-footing arithmetic is performed by a deterministic script (`scripts/foot.py`) over the figures extracted into `statements.json`. The reviewer's job is to adjudicate the script's output against the structural relationships below — confirm every relation holds, investigate every exception, and turn every unexplained exception into a finding. Verify each relation using the extracted figures in `statements.json` / the `foot.py` report; never do mental arithmetic on the PDF text.

**Rounding — zero tolerance:** Every column in the printed document must foot to the printed total exactly as a reader would verify on a 10-key. A difference of any amount — including $1 — is a finding. Rounding is an explanation, not an excuse. Flag it regardless.

**NOTE:** *The underlying schedules were prepared in Excel. Do not assume subtotals are correct. Hidden rows, rounding errors, or formula errors may cause presented totals to differ from the actual sum of visible line items. `foot.py` recalculates everything from the individual extracted line items — adjudicate its report; do not trust any printed total.*

### Every column foots:

- Every column of every financial statement, schedule, and table must sum to the subtotal or total presented. Confirm each column's result in the `foot.py` report and flag every column that does not foot to its printed total.

### Every row cross-foots:

- Confirm that each row total equals the sum of the columns that are intended to sum across.

- In consolidating statements, combining statements, and segment reports, confirm all columns add correctly across each row and down each column. For consolidating statements, confirm: (entity 1 + entity 2 + ... + eliminations = consolidated).

### Subtotals and totals at every level:

- Where totals are built from subtotals, verify each subtotal independently, then verify the total as the sum of the subtotals.

### Balance Sheet / Statement of Financial Position:

- Confirm total assets equals total liabilities and equity.

- Confirm current vs. non-current classification totals foot to the grand totals.

### Income Statement / Statement of Operations:

- Confirm gross profit = revenue − cost of sales (if presented with this structure).

- Confirm operating income = gross profit − operating expenses.

- Confirm income before taxes = operating income + other income/(expense).

- Confirm net income = income before taxes − income tax expense.

- Confirm any per-share data (if presented — rare in private companies but occurs in ESOPs and some closely-held structures): weighted average shares, basic EPS, diluted EPS all internally consistent.

### Statement of Stockholders'/Members'/Partners' Equity:

- Foot every column of equity rollforward (common stock, APIC, retained earnings, treasury stock, AOCI for corporations; member contributions, distributions, income allocations, ending capital for LLCs; partner capital accounts with separate columns per partner or class for partnerships).

- Confirm beginning balance + changes = ending balance for each equity component.

- Confirm the ending equity total equals the total equity on the balance sheet.

- For partnerships and multi-member LLCs, confirm income/loss allocations across partners/members sum to total net income/loss on the income statement.

- For S corporations, confirm AAA, PTI, OAA, and other S-corp-specific equity accounts (if disclosed) rollforward correctly.

### Statement of Cash Flows:

- Confirm operating, investing, and financing totals sum to net change in cash.

- Confirm net change in cash + beginning cash = ending cash, and ending cash ties to the balance sheet.

- Confirm the indirect method reconciliation starts with net income that matches the income statement.

- Confirm any supplemental disclosures (interest paid, taxes paid, non-cash investing/financing) are internally consistent with the notes.

### Debt Schedules:

- Foot all maturity schedules. Confirm totals agree to the applicable note disclosure and to the face of the financial statements.

- Confirm current portion of long-term debt + long-term debt = total debt per the note and the balance sheet.

### Capital Asset / Fixed Asset Schedules:

- Foot beginning balances, additions, disposals, and ending balances.

- Confirm accumulated depreciation rollforward ties.

- Confirm net PP&E ties to the balance sheet.

### Lease Schedules (ASC 842):

- Foot right-of-use asset rollforward and lease liability rollforward.

- Confirm the maturity schedule of lease payments ties to the lease liability note disclosure.

### Inventory Schedules:

- Foot any disclosed inventory components (raw materials, WIP, finished goods, reserves).

### Consolidating / Combining Schedules:

- Confirm each subsidiary column foots independently.

- Confirm eliminations column is internally consistent (assets eliminated against liabilities; intercompany revenues eliminated against intercompany expenses).

- Confirm the consolidated/combined column equals the sum of component entities plus eliminations.

**NOTE:** *Flag every instance where a figure does not recalculate correctly, with the location, the presented figure, and the recalculated figure.*
