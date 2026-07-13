# Universal Cross-Program Conventions

Rules and patterns that apply to **every** CCH AUD-8xx audit program. Apply these consistently across new program MDs as they're built.

## Step → Assertion → RMM linkage rule

Each visible program step has three linked sets:

1. **`Assertion`** valueKey (semicolon-joined, e.g., `"EO;CO;CU;"`) — which assertions this step addresses.
2. **`Risks`** valueKey (semicolon-joined, e.g., `"FINANCIALLEVELRISKS-1;RMM-EO;RMM-CO;RMM-CU;"`) — which risks this step is linked to.

**Convention:** For each visible step, the `Risks` valueKey must include `RMM-{assertion}` for every assertion in the step's `Assertion` valueKey, **skipping** any assertion that is N/A for the area (CCH server-side rule — e.g., AV is N/A for Cash, no `RMM-AV` checkbox exists).

Preserve any FS-level risk references already on the step (e.g., `FINANCIALLEVELRISKS-1` for Management Override) when adding RMM-X links. Full-state replacement on write — see `cch-axcess/references/modules/fill-kc-form.md` "Multi-value / multiselect" (the Risks bullet) for the API format.

## Cross-cutting steps — Fraud Awareness & Information as Audit Evidence

Two steps appear in **every** AUD-8xx program with **no specific assertion linkage** by default:

- **Fraud Awareness** (AU-C 240) — alertness for fraud indicators. Cross-cutting professional skepticism.
- **Information To Be Used As Audit Evidence** (AU-C 500) — evaluation of evidence relevance/reliability. Cross-cutting evaluation step.

CCH's diagnostic flags both as "Program Step Not Linked to Risk or Relevant Assertion" when left empty. **Firm convention:**

For each of these two steps, write:
- `Assertion` = all applicable (non-N/A) assertions for the area, semicolon-joined.
- `Risks` = `FINANCIALLEVELRISKS-1;` (Management Override) + every `RMM-{assertion}` for the applicable set.

Example for Cash (AV is N/A):
- Assertion = `"EO;RO;CO;CU;UC;"`
- Risks valueKey = `"FINANCIALLEVELRISKS-1;RMM-EO;RMM-RO;RMM-CO;RMM-CU;RMM-UC;"`
- Risks value = `"Management Override;RMM-EO;RMM-RO;RMM-CO;RMM-CU;RMM-UC;"`

This clears the CCH diagnostic and reflects the audit-standards reality that these steps cover all evidence/fraud risk across the area.

## Management Override (FINANCIALLEVELRISKS-1)

`FINANCIALLEVELRISKS-1` is the engagement-wide Management Override of Controls fraud risk per AU-C 240. It's an **FS-level risk**, not an area-level one. CCH auto-creates it on every engagement.

**Convention:** Management Override should be linked to:
- Cross-cutting steps (Fraud Awareness, Info as Audit Evidence) — always.
- Specific procedure steps where management override is a plausible concern (e.g., Account Summary, Subsequent Bank Statements where journal entry posting/cash manipulation could occur).
- NOT linked to disclosure-testing or routine FS tie-out steps where management override isn't the relevant risk.

CCH defaults will pre-link Management Override on the steps where it's a typical concern. Preserve those defaults; only add it where CCH didn't auto-link if the engagement specifically identifies management override risk in that procedure.

## PlannedAuditApproach (Combined / Analytical / In-depth)

For each assertion row in `.{AREA}.RelevantAssertion`, check 1+ of:

| Option | valueKey | When to check |
|---|---|---|
| Combined | `COMBINED` | Controls tested → CR < MAX |
| Substantive: Analytical | `ANALYTICAL` | Active program includes analytical procedure steps |
| Substantive: In-depth | `INDEPTH` | Active program is tests-of-details based |

**Decision algorithm** (walk this for each assertion):
1. If CR < MAX → `COMBINED` is available; check it if the firm wants to take credit for controls reliance.
2. If active step set includes analytical steps (e.g., "Cash Analytical Procedures", "Analytical Procedures" on Cash) → check `ANALYTICAL`.
3. If active step set includes tests-of-details (most steps) → check `INDEPTH`.

For the standard 8-step Cash default (no analytical, CR=Max), the result is `INDEPTH` on all 5 applicable assertions.

## IR / CR / RMM write order

IR/CR/RMM on `.{AREA}.RelevantAssertion` is written against **KBA-502's wpId** — the program's grid is the
derived/read-through view (a program-targeted write lands in a working copy the KBA-502-owned recompute
discards on refresh). Per assertion:

1. **Write `ir`** with one of `SBM`/`MOD`/`LOW` (never `MAX` — defaults applied as-is).
2. **Write `cr` = MAX explicitly** on a substantive audit — the pre-committed state-2 default still raises
   a Question-Unanswered diagnostic. Lower only with controls support.
3. **RMM = IR when CR=MAX** — deterministic; write it explicitly in the same pass. Only when CR < MAX, read
   the row's `rmm.recommendedAnswer` back and write that (CCH computes IR×CR → RMM server-side).
4. **`selected` is NOT required** — assertion presence on the grid already reflects KBA-400's selection.
5. **Per-area durable unit:** writes → submit (KBA-502's wpId) → refresh before the next area; verify via
   the diagnostics oracle (cch-axcess `field-conventions.md` §5).
6. **N/A assertions** render `visible:false` / reject with `resetanswer` — server-side rule. Don't waste calls on them. Per area:
   - Cash: AV is N/A
   - Investments: CU is N/A
   - PP&E: CU is N/A
   - AP, Other Liabilities, Equity: RO is N/A
   - (capture more as each program is built)

## Risk-area programs (no PPC defaults)

Five "areas" exist on KBA-502 but aren't FS captions — they're risk consideration areas:

| Area code | AUD form | Note |
|---|---|---|
| JE2 | AUD-816 | Journal Entries |
| RPTRNS2 | AUD-817 | Related Party Transactions |
| FAIRVALUE2 | AUD-818 | Fair Value Measurements |
| COMMIT | AUD-819 | Commitments and Contingencies |
| CONCENT | AUD-821 | Concentrations |

PPC didn't track these. Universal defaults are in `defaults/{CODE}.md` under "Universal risk-area defaults" — apply to every audit type.

## Submit semantics

Submit AFTER your writes; never between writes within a logical group, or partial state may surface. The endpoint and payload shape are `cch-axcess`'s to state (`references/modules/fill-kc-form.md`) — this file only carries the timing rule.

