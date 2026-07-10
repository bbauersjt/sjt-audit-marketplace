# Cross-Reference and Consistency (GAAP-common)

These are the cross-reference ties common to all frameworks; the framework specifics module adds framework-specific ties. Use the `xref.py` amounts index to locate every occurrence of a figure instead of re-scanning pages.

Identify every number that appears in more than one location in the document and confirm all instances agree. At minimum, check:

Three sweeps over the `amounts_index` itself, beyond the named ties below — these are
cheap lookups and historically where findings slip:

- **Same amount, different labels** — for every amount appearing in 2+ locations,
  compare the row labels: the same figure labeled differently in different places
  (e.g., "Bad debt" on one statement, "Credit loss expense" on another) is a
  terminology-consistency finding even though the numbers agree.
- **Every near-miss adjudicated** — work the `near_misses` list to zero; each is
  either an extraction artifact (verify the page), a legitimate different figure, or
  a broken tie/typo. Do not sample it.
- **Material unexplained catch-alls** — any "miscellaneous" / "other" income or
  expense line exceeding ~5% of its statement total with no disaggregation in the
  notes is a presentation finding; look its amount up in the index to confirm no
  note breaks it out.

## Equity / Net Assets

- Confirm ending balances on the balance sheet agree to the statement of stockholders'/members'/partners' equity ending balances, to any equity-related note disclosures, and to any narrative references.

- For partnerships and LLCs, confirm partner/member capital ending balances in any detailed capital account note agree to the statement of equity.

## Revenue and Expense Totals

- Confirm totals on the face of statements agree to any segment disclosure, product-line disclosure, or geographic disclosure in the notes.

- Confirm revenue recognition note disclosures (ASC 606) reconcile to the income statement revenue total — disaggregation of revenue should sum to total revenue.

## Depreciation and Amortization

- Confirm depreciation expense per the income statement (or per the notes if disclosed separately) agrees to depreciation as a reconciling item on the statement of cash flows and to the accumulated depreciation change in the PP&E rollforward.

- Confirm amortization of intangibles, deferred financing costs, and right-of-use assets (if applicable) are internally consistent across the income statement, cash flow statement, and relevant notes.

## Long-Term Debt

- Confirm the total outstanding balance per the debt footnote agrees to the face of the financial statements (long-term debt + current portion).

- Confirm the current portion of long-term debt on the balance sheet agrees to the amount maturing in the next year per the maturity schedule in the footnotes.

- Confirm interest expense per the income statement is plausible given the disclosed interest rates and balances — this is a reasonableness check rather than a tie-out, flag material inconsistencies.

## Capital / Fixed Assets

- Confirm beginning balances, additions, disposals, and ending balances in the capital assets note roll-forward are internally consistent.

- Confirm ending net PP&E balance agrees to the face of the statements.

- Confirm depreciation expense in the PP&E rollforward ties to depreciation in the cash flow statement and to any disclosure in the income statement.

## Leases (ASC 842)

- Confirm right-of-use asset and lease liability balances per the lease note agree to the face of the balance sheet.

- Confirm the total undiscounted lease payments per the maturity schedule reconcile to the present-value lease liability via the disclosed discount factor.

- Confirm operating lease expense and finance lease components per the note agree to any income statement line items or disclosures.

## Intangibles and Goodwill

- Confirm goodwill rollforward (if applicable) ties to the balance sheet.

- Confirm intangible asset rollforward (gross, accumulated amortization, net) ties to the balance sheet.

- If the PCC goodwill amortization alternative has been elected, confirm amortization is being recorded and the useful life disclosed.

- Confirm impairment charges (if any) are disclosed consistently across the note, income statement, and cash flow statement.

## Income Taxes

- For C corporations: confirm current and deferred tax provision on the income statement agrees to the tax note; confirm deferred tax assets/liabilities per the balance sheet tie to the components disclosed in the tax note; confirm any valuation allowance is disclosed with reconciling detail.

- For S corporations, partnerships, and LLCs taxed as partnerships: confirm pass-through tax disclosures are appropriate — typically no federal income tax provision (other than state-level pass-through entity taxes, built-in gains tax for S-corps, or other entity-level taxes that may apply). Flag any federal income tax provision on an entity that appears to be taxed as a pass-through unless entity-level taxes are specifically explained.

- For state and local income taxes: confirm the state tax provision is disclosed and plausible.

- Confirm uncertain tax positions (ASC 740-10) are addressed — either with disclosed unrecognized tax benefits or with a statement that none exist.

## Cash and Investments

- Confirm total cash and cash equivalents per the balance sheet agrees to the cash flow statement ending cash.

- Confirm restricted cash (if any) is reconciled between the balance sheet and cash flow statement per ASU 2016-18.

- Confirm investments (if any) tie to any fair value disclosures (ASC 820) with consistent Level 1/2/3 classifications.

## Receivables

- Confirm accounts receivable, allowance for credit losses (CECL under ASC 326 if adopted, or legacy allowance), and net receivables per the balance sheet tie to any detail schedule in the notes.

- Confirm related-party receivables (if any) disclosed in the related-party note tie to any separate balance sheet line item or parenthetical disclosure.

## Payables

- Confirm accounts payable and accrued expenses tie to any detail disclosure in the notes.

- Confirm related-party payables (if any) are disclosed consistently.

## Revenue Recognition (ASC 606)

- Confirm disaggregated revenue disclosures sum to total revenue on the income statement.

- Confirm contract assets, contract liabilities, and deferred revenue balances per the note agree to the balance sheet.

- Confirm beginning and ending contract liability balances roll forward with revenue recognized from the beginning balance, as disclosed.

## Commitments and Contingencies

- Confirm any accrued loss contingencies tie to any related balance sheet line item.

- Confirm commitments (purchase commitments, employment agreements, guarantees) are internally consistent with any related note or schedule.

## Related Party Transactions (ASC 850)

- Confirm every related-party balance disclosed is reflected on the balance sheet in the expected line item.

- Confirm every related-party transaction disclosed (revenues, expenses, management fees, rent, loans) is reflected on the income statement and cash flow statement as appropriate.

- Confirm intercompany balances for consolidated statements are fully eliminated.

## Prior Year Figures

- Confirm prior year comparative figures (if presented) are internally consistent with each other throughout the document.

- Where prior year audited statements are available for reference, confirm comparative figures agree.

- Confirm beginning balances (retained earnings, capital accounts, AOCI) agree to prior year ending audited balances. Flag any that cannot be confirmed without the prior year report.

## Footnote Figures

- Confirm every figure cited in the footnotes agrees to the corresponding line item on the face of the financial statements.

- Confirm all cross-references between footnotes are accurate.

**NOTE:** *Identify any other figure appearing in multiple locations and confirm consistency. Flag every discrepancy with location, expected figure, and actual figure found.*
