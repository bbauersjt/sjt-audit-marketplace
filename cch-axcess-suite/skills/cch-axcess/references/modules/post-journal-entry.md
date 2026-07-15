---
summary: Post an actual journal entry (AJE/RJE/PAJE/TJE) into the engagement trial balance (FinancialPrep)
leg: wpm
triggers:
  - "post a journal entry"
  - "book an AJE / RJE / PAJE / TJE"
  - "enter this adjusting entry into the TB"
  - "import these journal entries when too large for the TB import path"
  - "add a journal entry referencing [workpaper]"
inputs:
  - "engagement (clientId + engagementId)"
  - "JE type (AJE/RJE/PAJE/TJE)"
  - "line items: account number, debit/credit side, amount"
  - "optional: comment; referenced workpaper documentId"
calls:
  - scripts.je.build_post_je_js
status: validated
---
# Module — Post Journal Entry (FinancialPrep)

## What this does
- Posts a real journal entry into the trial balance via FinancialPrep (`POST financialprep-api /v1.0/journalentry`).
- Use for large JEs that cannot be imported — they get posted here line by line.
- **Not** the same as `run-reports` JE *reports* (`workbench-api /v1/JournalEntryReport`), which only build a report workpaper.

## Prerequisites
- Leg: `wpm` warm (engagement/FP bearer). Rules 0–3 (SKILL.md).
- An FP call must have fired in the tab so the bearer is in `__cch_capture` (opening the
  TB / JE panel does this). Bridge transport; tab must be **visible** (writes drop on hidden tabs).
- **Binder guard**: the builder asserts the active URL is the intended `engagement/{clientId}/...{engagementId}`
  and aborts otherwise — do not post into whatever binder happens to be open.

## Procedure
### 1. Build + run
```python
from scripts import je
js = je.build_post_je_js(
    client_id=<clientId>, eng_id=<engagementId>, je_type="AJE",
    lines=[{"number":"20000-100","side":"D","amount":100.00},
           {"number":"40500-200","side":"C","amount":100.00}],
    comment="To reclass ...", document_id=None)   # document_id = referenced workpaper's WPM documentId
# run via chrome_eval(target=<cch tab>)
```
The built JS resolves each account number → accountId (FP account search), asserts the
entry balances, POSTs, and verifies via the JE list. Returns `{postStatus:201, id, landed}`.

### 2. Verify (201 = created)
Success is **201** with `{id, sequenceNumber}`; the builder also reads the JE list back and
matches the new `id`. (Note: request uses `rollforwardOption`; read-back echoes `rollForwardOption`.)

## Known failure modes
- **Unbalanced** → builder refuses to POST (`{error:'unbalanced'}`). JEs must net to zero.
- **Account not found** → the number didn't exact-match `accounts[].number`; check the chart.
- **Wrong engagement** → builder aborts via the URL guard; navigate the correct binder first.
- **PAJE/TJE** type strings are inferred (only AJE/RJE verified) — confirm on first real use.

## No-hard-delete
CREATE only (`journalEntryId:0`). Editing (non-zero id) or deleting a JE is **not** scripted —
done manually (infrequent + destructive).

<!-- END -->
