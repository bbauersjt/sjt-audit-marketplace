# CCH KC Field Registry — Consolidated Source of Truth (the spine)

**The ONE canonical map** of every KC form-field kind, valueKey convention, option-set/enum, per-prop
convention, collection-targeting rule, and the cross-cutting write protocol. Facts verified live
2026-06-22 AND untested-but-uncontradicted pre-existing conventions (carried forward, tagged
`[assume-true]`). This MD is the human-maintained registry; the same conventions are HARD-CODED in
`scripts/kc.py` (`classify_property` + `build_write_payload`) — there is no runtime JSON consumed by
the code, so **a convention change here must also land in kc.py** (and vice versa). valueKey
conventions are DATA — NOT discoverable from the form GET (floatieItemList is empty on
convention-driven props) — which is why the code must carry them.

Tags: `[V]` = VERIFIED 2026-06-22 (write→submit→reload→state 3). `[A:file]` = pre-existing, untested
this session, not contradicted — carry forward.

## 1. Field-kind → detection → value → valueKey → gotcha

| Kind | Detection | value | valueKey | Gotcha | Tag |
|---|---|---|---|---|---|
| text | pt 1; or pt 0 no opts/no sentinel | text | `""` | engagement-level TQ comment writes via propertyKey `Description`, not `Answer` | V |
| select | pt 0 + Radio / non-empty list / "Choose an item" | **display value** | option key | valueKey-only w/ value=None → `value:null` → `resetanswer`. Backfill value from option. | V |
| multiselect | pt 0 + CheckBox / "Choose all that apply." | values `;`-joined | keys `;`-joined | full-state replace, one POST; naive write → `resetcheckbox`; route via build_write_payload | V |
| signoff | pt 3 (`performedby`, dates) | token | **token** | token in valueKey; free-text-only ignored (state 0) | V |
| yes/no (matrix) | prop `yesno`/`text2` | Yes/No | **`YES`/`NO`** (UPPER) | not in floatie; lowercase `yes` → resetanswer (old "lowercase accepted" claim DISPROVEN) | V |
| yes/no/NA | prop `text3` | Yes/No/N/A | **`YESNONA-YES/-NO/-NA`** | compound; not in floatie | V (NA variant [A]) |
| X/dash toggle | KBA-400 Scoping flags | "X" | **`NOTDASH`** (X) / **`DASH`** | writing `YES` = state 3 but renders BLANK (the empty-checkbox bug) | V |
| recommended-answer | KBA-400 `FurtherUnderstanding` | "" | **`SCOPINGRECOMMENDEDANSWER`** | uniform across areas | V |
| custom multiselect | KBA-400 `CtrlConTestWp`/C09 | value(s) | server-derived **`KEY_<VALUE>`** (custom_value_key) | invented keys pass immediate GET, DROP on refresh — confirm after refresh | A:fill-kc-form/kc.py |
| addable template row | obj key `…-1`/`…_1` | per columns | per kind | seeded `-1` row IS writable; ADDITIONAL rows via build_spawn_payload → new GUID arrives empty → fill by GUID. Spawn IS REST (SignalR/NOT-REST claim FALSE). addable_grids misses seeded-template grids. | V |
| addable empty grid | `objectList:[]` | first cell | option key | looks done but isn't; fill via spawn. KBA-401 DISPLAY matrix spawn = 200 but NO row (it's display, not input). | A:fill-kc-form (KBA-401 noop V) |
| gated empty-opt choice | choice, opts empty + sentinel, driver unanswered | — | — | skip this pass; revisit after driver (fixed-point); free-text → resetanswer | A:architecture |
| linked/label | pt 5 / pt 2 | — | — | NEVER write (KBA-502 FinancialLevelRisks = 14/15 pt5 linked; only Comment writable) | V |
| silent-rejection signal | re-read: state 2 + valueKey starts `reset` | — | — | 200 ≠ accepted; **200 + no reset is STILL not proof — verify state 3 AFTER RELOAD** | V |
| KBA-302-class row dropdown | Radio on `global.yesno` row tables | — | UPPER `YES`/`NO` or `<OPTSET>-<VAL>` | once "known-unsolved"; SOLVED via UPPER valueKey + target the INPUT (`*Findings`/`*TQ`), not the display collection | V |

## 2. Named enums / option-sets (exact keys)
- **IR/CR** (`ir`/`cr`): Max=`MAX`, SBM=`SBM`, Mod=`MOD`, Low=`LOW`. CR defaults MAX until controls tested. [A:enums/risk-framework]
- **RMM**: derived — read CCH `rmm.recommendedAnswer` after IR+CR, write it back (don't compute). [A:risk-framework]
- **Assertions (6)**: `EO RO CO AV CU UC`. N/A by area (server rejects, no checkbox): Cash→AV; Invest→CU; PPE→CU; AP/OL/Equity→RO. [A:enums/risk-framework]
- **Planned approach** (`PlannedAuditApproach`): Combined=`COMBINED`, Substantive-Analytical=`ANALYTICAL`, Substantive-In-depth=`INDEPTH`. API returns state 3 for ANY key — UI honors only these 3; verify after reload. [A:enums/kba-502]
- **Risk-link** (`Risks` on `.{AREA}.ProgramSteps`): `FINANCIALLEVELRISKS-N` (N=FS-level risk; -1=Mgmt Override auto), `RMM-EO/RO/CO/AV/CU/UC`. `;`-joined w/ trailing semi, full-state. Unknown→500. [A:enums/_conventions]
- **global.yesno** → `YES`/`NO` (UPPER) [V]. **Yes/No/NA** → `YESNONA-YES/-NO/-NA` [V; NA A].
- **Scoping** (KBA-400): X/dash → `NOTDASH`/`DASH` [V]; `FurtherUnderstanding` → `SCOPINGRECOMMENDEDANSWER` [V].
- **Sentinels (never write)**: `defaultanswer` (unanswered select), `resetanswer` (rejected select, state 2), `resetcheckbox` (rejected multi, state 3). [V]
- **JE type IDs**: AJE=1, TJE=2, PAJE=3, RJE=4 (positional). [A:je_types]
- **Tickmark IDs**: 1–71; base marks 1,4,7,…49 in red/blue/green (+0/+1/+2); 52–71 explanatory circles (A–J, 1–10), red. [A:tickmark_ids]
- **Group account types**: 1 Asset,2 Liability,3 Equity,4 Revenue,5 Expense; classifications 1–10. [A:group_account_types]
- **WPM objectTypes**: Folder/LeadSheet/KCForms/Report. Pseudo-folderIds: -1 Unfiled WP, -2 Reports, -3 Leadsheets, -4 KC Forms (read-only). [A:architecture]

## 3. Per-prop-key conventions
| prop | kind | valueKey | where | tag |
|---|---|---|---|---|
| `yesno` | yes/no | `YES`/`NO` | KBA-401 `<Comp>TQ` (obj `OVERALLQS_<Comp>TQ_1`), EntityEnvOverall{Assessment,Effective} | V |
| `text2` | yes/no | `YES`/`NO` | KBA-401 `<Comp>Findings` (obj `OVERALL_PR_UNDERSTANDENTITYLEVELCONTROLS_FLOW<COMP>_1`) | V |
| `text3` | yes/no/NA | `YESNONA-*` | KBA-401 `<Comp>Findings` | V |
| `text1` | text | `""` | KBA-401 Findings; spawned cells | V |
| `present`/`controlsimplemented`/`functioning`/`risk` | DISPLAY | — | KBA-401 `EntityEnv*` rollup — **never write (resetanswer)** | V |
| `selected` | select | `YES` | `.{AREA}.RelevantAssertion` — write FIRST | A:_conventions |
| `ir`/`cr` | select | `MAX/SBM/MOD/LOW` | `.{AREA}.RelevantAssertion` (AUD-8xx, NOT KBA-502) | A:enums |
| `rmm` | select | read-back recommendedAnswer | derived | A:kba-502 |
| `PlannedAuditApproach` | multiselect | `COMBINED/ANALYTICAL/INDEPTH` | `.{AREA}.RelevantAssertion` | A:enums |
| `Assertion` | multiselect | `EO;RO;CO;AV;CU;UC` | `.{AREA}.ProgramSteps`, `.KBA400.AuditareaRelevantAssertions` | A:_conventions |
| `Risks` | multiselect | `FINANCIALLEVELRISKS-N;RMM-…;` | `.{AREA}.ProgramSteps` | A:enums |
| `SigClassTans`/`MaterialAccount`/`SigDisclosure`/`SigAcctEst`/`SigFraudRisk`/`substantivetesting` | X/dash | `NOTDASH`/`DASH` | `.KBA400.Scoping` | V |
| `FurtherUnderstanding` | recommended | `SCOPINGRECOMMENDEDANSWER` | `.KBA400.Scoping` | V |
| `CtrlConTestWp` | custom multi | option keys + `KEY_<VALUE>` | `.KBA400.Scoping` C09 | A:kba-400 |
| `Applicable` | yes/no | `YES`/`NO` (UPPER) | AID-201: header rows of `.AID201.TypeofNonauditService` — a header's `NO` gates its nested `childObjectList` rows off; EXCEPTION: Header1 "General Considerations" children are UNGATED and must each be answered individually | V 2026-07-08 |
| `Consideration` / `IndependenceRequirementMet` | per kind (child rows) | per kind | AID-201 child/grandchild rows under `TypeofNonauditService` headers (rows live in `childObjectList`, NOT the flat objectList — see §4 note) | V 2026-07-08 |
| `performedby` | signoff | token | AUD-8xx steps | V |
| `Description` | text | `""` | eng-level TQ comment; KBA-401 `Noncomplex*.description` | V |
| `Comment`/`Comments`/`comment` | text | `""` | KBA-502 FinancialLevelRisks (ONLY writable), KBA-400 Scoping/AuditareaRelevantAssertions | V |

## 4. Collection-targeting — INPUT vs DISPLAY
`inventory_form` over-filters grid forms → for KBA-4xx/5xx read raw `result.collections` and target INPUT.

**Nested rows: never hand-count the flat `objectList`.** Answerable rows nest in `childObjectList`
(children/grandchildren/great-grandchildren) — AID-201's `TypeofNonauditService` is 17 flat objects
but 112 rows / 195 fillable fields across depths 0–3 (fixture:
`data/fixtures/aid201-form-get.json`). `inventory_form` DOES walk the nesting (rows carry
`children[]`; `fillable` includes nested fields) — the under-count trap is sizing work from
`len(objectList)` on a raw GET or from top-level `sections[].rows` only. Same class of surprise as
the KBA-4xx grid over-filtering above: when a UI count disagrees with your estimate, trust
`inventory_form.stats` / the diagnostics endpoint, not a flat count. [V 2026-07-08]
| Form | INPUT (write) | DISPLAY (never write) |
|---|---|---|
| AUD-100 | `.AUD100.OverAllTailoringQuestions` (note caps: OverAll), `.AUD100.TQComments`, `.AUD100.Overallauditareastemp` (`Description`, seeded -1 + spawn) | — |
| KBA-200 | `.KBA200.EntityandContInfoKBA200` (entity/contact free-text — prop key `answer`, lowercase), `.KBA200.*Selection` (`chooseitem`), `.KBA200.Describe*Change` (`Description` and lowercase `description`) | — |
| KBA-400 | `.KBA400.Scoping` (toggles/FU/CtrlConTestWp/Comments), `.KBA400.AuditareaRelevantAssertions` | — |
| KBA-401 | `.KBA401.<Comp>TQ` (yesno), `.KBA401.<Comp>Findings` (text1/2/3), `.KBA401.EntityEnvOverall{Assessment,Effective}` (yesno), `.KBA401.Noncomplex*` | `.KBA401.EntityEnv*` matrix (present/controlsimplemented/functioning/risk) — reject + spawn-noop |
| KBA-502 | `Comment` only (rollup) | all else (pt5 linked, OverallAuditAreas visible:false). IR/CR/RMM is on AUD-8xx. |
| AUD-8xx | `.{AREA}.RelevantAssertion` (selected/ir/cr/rmm/PlannedAuditApproach), `.{AREA}.ProgramSteps`, `.{AREA}.AssertionLevelRisk` (spawn), tailoring/results/findings text | OverallAuditAreas / RelevantAssertion.ProgramSteps rollups |

`<Comp>` ∈ {ControlEnvironment, RiskAssess, ControlActivities, Information, Monitoring}. Path uses AREA short name, never the form number (`.CASH.ProgramSteps`).

## 5. Cross-cutting write protocol (EVERY write)
1. **Content-Type: application/json** on every body-bearing write (`build_batch_xhr` omitted it → 415 on all KC writes; single-call builders already inject it). [V]
2. **Submit to commit — PER-WORKPAPER ONLY.** Writes are PENDING until `POST /api/Workpaper/submit` `{binderId, workpaperId:"<wpId>"}`. A refresh discards unsubmitted writes. (The "persists without submit" note is WRONG.) **Never submit with an EMPTY workpaperId** — the "submit all pending in binder" form silently DISCARDS pending writes on other forms instead of committing them (isolated-test confirmed, batch-2 2026-07-08). [V 2026-07-08]
3. **Verify AFTER reload — never the immediate GET** (it reads the uncommitted working copy; false state-3). [V]
3a. **Mandatory write→verify→retry loop — the standard KC write pattern.** KC silently drops a large share of UpdateProperty→submit pairs even when payloads match this registry exactly: ~60% loss at ~350ms pacing (batch-2), still ~30–50% loss with a 1–2s inter-write sleep (SFRC 401k 0100, 2026-07-08) — sleeps reduce but do NOT eliminate drops, so pacing alone is never sufficient. Binding pattern for every KC write: **write → settle ~1.2s → per-workpaper submit → re-read COMMITTED state after reload → rewrite ONLY the dropped cells → iterate until the committed read matches intent** (the CONVERGE loop; 2–4 rounds converges); batch the verify (one re-read covers the whole write set). The drop set ROTATES between rounds — each write echoes state 3 but the commit loses a different subset — so a counted "retry ≤3 misses" pass under-delivers on large sets; converge to match-intent (81-write form converged, Coop Consulting 2026-07-09). A write not re-read as state-3-after-reload was NOT made — never count it, never blind-repeat it (re-read first; see RECOVERY.md). [V 2026-07-09]
4. **Completion oracle = diagnostics endpoint.** `POST /api/Workpaper/refresh/{eng}/{wp}` → `GET /api/diagnostics/GetWorkpaperDiagnostics/{eng}/{wp}` → `result.diagnostics[]`. Drive the loop from it. Form `diagnosticCount` is STALE. `type:"Missing KnowledgeCoach Form"` = a Yes-answer needs a dependent form → flip to No or add it. `type:"Unnecessary KnowledgeCoach Form"` = the inverse: an answer gates a form OFF and KC wants it REMOVED — the entry names it via `unnecessaryWorkpaperReferenceTag`/`unnecessaryWorkpaperDataBindingKey` (fixture: `data/fixtures/aud100-unnecessary-form-diag.json`); check these on the driving form BEFORE adding conditional forms (add-audit-programs.md), and treat existing ones as a removal worklist — the diagnostic is PERMANENT while the form stays. [V 2026-07-08]
5. **Transport by origin, then verb.** KC origin -> **bridge via `chrome_api_call`** (SW fetch, CSP-exempt) PRIMARY, linked tab fallback; the bridge's IN-PAGE verbs (eval/fetch) stay CSP-blocked on KC. engagement/WPM/FP/workbench -> bridge primary, linked tab fallback. [V 2026-06-23]
6. Sequential writes; settle ~1.2–1.5s between write and submit/verify. (The old ~300ms pacing floor is WRONG — ~60% silent drop at ~350ms; and no sleep alone fully prevents drops, see 3a.) [V 2026-07-08]
7. Fixed-point fill: choices-with-options → re-read → repeat (cap ~8) before text/signoffs; reset* = not-answered. [A:fill-kc-form]
8. TQ-cascade: answer `*TQ` first; skip descriptions where TQ=No. [A:architecture]
9. `build_reset_payload` FORBIDDEN (leaves state 3 blank; diagnostic never re-fires). [A:fill-kc-form]
10. Builders mandatory for writes; source fields from `inventory_form(decode_form(read_form()))` (integrity seal blocks hand-assembled keys). [A:kc.py]
11. DOM-first detection (`kcDom`) + GET substrate (GET over-reports fillable ~2:1). [A:fill-kc-form]
12. Single re-auth on 401: one deep-link reload (re-mint) + retry. [V]
13. Batch multi-write into ONE in-page JS call (KC tab times out on many sequential per-call XHRs). [A:architecture]

### Endpoint quick-ref
Write: `POST kc/api/Workpaper/UpdateProperty/{engGuid}/{wpId}` body `{collectionKey,objectKey,propertyKey,value,valueKey,dataEntryExpression:"",dataEntryExpressionContextObjectKey:""}` + Content-Type. Spawn: same, identity keys `""`, collection path in dataEntryExpression. Submit: `POST /api/Workpaper/submit` `{binderId, workpaperId:"<wpId>"}` (per-workpaper ONLY — empty wpId discards other forms' pending writes). Diagnostics: refresh then GET GetWorkpaperDiagnostics. wpId lookup: `GET /api/binder/GetBinder/{engGuid}` → result.workpapers[].

**Provenance (2026-06-22, Coop "Bridge test", commercial, eng 102417/399548):** AUD-100 0-diag, KBA-400 176/176, KBA-401 0-diag, KBA-403, KBA-105, KBA-502 rollup, AUD-801/807. (Session capture notes live in the source repo, not this install.)
<!-- END -->
