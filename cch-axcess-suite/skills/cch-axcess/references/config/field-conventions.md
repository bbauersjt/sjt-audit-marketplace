# CCH KC Field Registry — Consolidated Source of Truth (the spine)

**The ONE canonical map** of every KC form-field kind, valueKey convention, option-set/enum, per-prop
convention, collection-targeting rule, and the cross-cutting write protocol. Facts verified live
AND untested-but-uncontradicted pre-existing conventions (carried forward, tagged
`[assume-true]`). This MD is the human-maintained registry; the same conventions are HARD-CODED in
`scripts/kc.py` (`classify_property` + `build_write_payload`) — there is no runtime JSON consumed by
the code, so **a convention change here must also land in kc.py** (and vice versa). valueKey
conventions are DATA — NOT discoverable from the form GET (floatieItemList is empty on
convention-driven props) — which is why the code must carry them.

Tags: `[V]` = VERIFIED (write→submit→reload→state 3). `[A:file]` = pre-existing, untested
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
| addable empty grid | `objectList:[]` | first cell | option key | looks done but isn't; fill via spawn. KBA-401 DISPLAY matrix spawn = 200 but NO row (it's display, not input). **`.{AREA}.AssertionLevelRisk` is a special case: do NOT spawn via raw API — it risks a wholesale purge of existing rows. Use the UI's binder-wide `{binderGuid}/risks` page "Specific Risk" form instead — see `spawn-assertion-level-risk.md`. That form spawns one row per assertion picked. Two follow-ups then complete the row, BOTH resolved via rendered-UI DOM interaction, never raw API: (1) `ir`/`rmm`/`PlannedAuditApproach` — fill via the KBA-502 risk-drilldown radios, NOT the Risks-page's own (deprecated) combined-risk-assessment section; (2) `.{AREA}.ProgramSteps` `Risks` linkage — fill via the AUD-8xx program's own step-row checkboxes, NOT a raw `UpdateProperty` POST (raw POST is rejected "Program Step Linked Incorrectly" for pairs the UI checkbox clears cleanly). See §3 `ir`/`rmm`/`PlannedAuditApproach` and `Risks` rows below for the full recipe + caveats.** | A:fill-kc-form (KBA-401 noop V) |
| gated empty-opt choice | choice, opts empty + sentinel, driver unanswered | — | — | skip this pass; revisit after driver (fixed-point); free-text → resetanswer | A:architecture |
| linked/label | pt 5 / pt 2 | — | — | NEVER write — `propertyType:5` is LINKED/derived; a direct UpdateProperty 200s but leaves state-2/empty (silent no-op). Cases: KBA-502 FinancialLevelRisks 14/15 pt5 (only Comment writable); AUD-8xx `AuditFinancialLevelRisks/<risk>/plannedauditapproach` and `RelevantAssertion/<assertion>/ProgramSteps`. Their diagnostics `Risk Unaddressed` / `Relevant Assertion Unaddressed` clear via program-step assertion-affirmation / risk→step link (`.{AREA}.ProgramSteps` `Risks`, e.g. Mgmt-Override `FINANCIALLEVELRISKS-1`) / sign-off in the UI — enumerate + hand off, don't force the pt5 write | V |
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
| `selected` | select | `YES` | `.{AREA}.RelevantAssertion` — NOT required (grid presence reflects KBA-400) | V |
| `selected` | (not writable) | — | `.{AREA}.AssertionLevelRisk` — **DIFFERENT collection from the row above.** Reads `defaultanswer`/"Choose an item" (state 2) forever — this is NOT a field the API can set. It is the row's own baked-in assertion code (EO/RO/CO/AV/CU/UC), fixed at row-SPAWN time by which assertion was picked in the binder-wide `{binderGuid}/risks` "Specific Risk" form's assertions picker (one row spawns per assertion chosen). Never attempt to write it. | V |
| `ir`/`rmm`/`PlannedAuditApproach` | select/select/multiselect | `MAX/SBM/MOD/LOW`, `MAX/SBM/MOD/LOW`, `COMBINED/ANALYTICAL/INDEPTH` | `.{AREA}.AssertionLevelRisk` (distinct from the KBA-502-targeted `RelevantAssertion` rows above) — **PREFERRED PATH: the KBA-502 risk-drilldown render.** Navigate to `/binder/{binderGuid}/risk-drilldown/{titleGuid}/1/{riskGuid}/[EMPTY]/[EMPTY]/[EMPTY]` — this renders KBA-502's OWN form (not a mirror), scrolled to that risk, with real `kcc-radio`/checkbox DOM inputs per assertion row whose `name` attribute is `AssertionLevelRisk|{objectKey}|{propertyKey}||{valueKey}`. A real `.click()` on these fires the SPA's own `UpdateProperty` against KBA-502's wpId — submit(KBA502 wpId)→refresh→diagnostics is the verify path. The Risks-page's own "Combined risk assessment"/"Planned audit approach" section is deprecated by the platform's own UI copy for SAS-145 titles ("...will not flow to KBA-502...Please add this information to KBA-502") — do not use it; use the KBA-502 drilldown radios instead. Fallback path (if the drilldown route is unavailable): normal `UpdateProperty` against the AUD-8xx program's OWN wpId once the row exists — this fallback path is prone to a partial revert on some rows; re-verify+re-fill as the last action before handoff if used. | V |
| `ir`/`cr` | select | `MAX/SBM/MOD/LOW` | `.{AREA}.RelevantAssertion` on **KBA-502's wpId** — NOT the AUD-8xx program (its grid is DERIVED; program-targeted writes land in a working copy the KBA-502-owned recompute discards on refresh). Set `cr` explicitly (state-2 default still fires a QU). | V |
| `rmm` | select | `MAX/SBM/MOD/LOW` | `.{AREA}.RelevantAssertion` on KBA-502's wpId — **=IR when CR=MAX, write explicitly**; read-back `recommendedAnswer` only when CR<MAX | V |
| `PlannedAuditApproach` | multiselect | `COMBINED/ANALYTICAL/INDEPTH` | `.{AREA}.RelevantAssertion` on KBA-502's wpId (one POST per approach) | V |
| `Assertion` | multiselect | `EO;RO;CO;AV;CU;UC` | `.{AREA}.ProgramSteps`, `.KBA400.AuditareaRelevantAssertions` | A:_conventions |
| `Risks` | multiselect | `FINANCIALLEVELRISKS-N;RMM-…;` (also `{AREA}{riskGuid}{ASSERTION}` for AssertionLevelRisk-code links) | `.{AREA}.ProgramSteps` — **only registers as a real risk→step link if the step is in the program's visible step-set FIRST** (`POST /api/Workpaper/UpdateProgramStep`, body `{binderId, workpaperId, value:"<;-joined step objectKeys>"}`, full-state replacement — the same call kcPop's tqAndVisible fires). Push the visibility set even when `TailoringQuestions`/`FlowTailoringQuestions` are BOTH empty (a program with zero TQs can still have every ProgramSteps row `visible:false`). Phantom-echo trap: on an invisible step the plain `/api/Workpaper/{eng}/{wp}` GET can echo `Risks` at state 3 / `isValueDefault:false` while a fresh SPA render says "No steps have been linked" and "Risk Unaddressed" still fires — never trust the plain form GET for this collection; verify via the SPA render / diagnostics oracle. Fix: push visible-set → reload tab → rewrite `Risks` → verify diagnostic cleared. **Linking an `AssertionLevelRisk`-code onto a step: PREFER the rendered UI checkbox over a raw `UpdateProperty` POST.** Once the target step is visible, the AUD-8xx program's OWN rendered page shows one real `<input type=checkbox name="ProgramSteps|{stepGuid}|Risks||{riskObjectKey}">` per currently-spawned risk-assertion — a `.click()` + submit→refresh→diagnostics clears the `pslink`/"Risk Unaddressed" diagnostic reliably where a raw-API POST for the identical step+risk pair can be rejected `Program Step Linked Incorrectly` (likely cause: full-state-replace multiselect semantics — a single-value POST may not replicate the SPA's full checked-set). **A real, non-bypassable content-library gate does exist**, distinct from that rejection: linking an assertion to a step that doesn't substantively address it produces `Program Step Linked Incorrectly` / `Risk Incorrectly Addressed` THROUGH THE UI TOO — uncheck and retry on a better-fitting step. **Warn before pushing a large invisible step-set visible just to reach a few target checkboxes:** it can surface new diagnostics (`Program Step Not Linked to Risk or Relevant Assertion` / `Program Step is Not Applicable`) on the OTHER, non-target steps in that program, and narrowing the visible-set back down afterward does not reliably retract them — treat this as a standing side effect, not a one-off bug. | V |
| `SigClassTans`/`MaterialAccount`/`SigDisclosure`/`SigAcctEst`/`SigFraudRisk`/`substantivetesting` | X/dash | `NOTDASH`/`DASH` | `.KBA400.Scoping` | V |
| `FurtherUnderstanding` | recommended | `SCOPINGRECOMMENDEDANSWER` | `.KBA400.Scoping` | V |
| `CtrlConTestWp` | custom multi | option keys + `KEY_<VALUE>` | `.KBA400.Scoping` C09 | A:kba-400 |
| `Applicable` | yes/no | `YES`/`NO` (UPPER) | AID-201: header rows of `.AID201.TypeofNonauditService` — a header's `NO` gates its nested `childObjectList` rows off; EXCEPTION: Header1 "General Considerations" children are UNGATED and must each be answered individually | V |
| `Consideration` / `IndependenceRequirementMet` | per kind (child rows) | per kind | AID-201 child/grandchild rows under `TypeofNonauditService` headers (rows live in `childObjectList`, NOT the flat objectList — see §4 note) | V |
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
`inventory_form.stats` / the diagnostics endpoint, not a flat count. [V]
| Form | INPUT (write) | DISPLAY (never write) |
|---|---|---|
| AUD-100 | `.AUD100.OverAllTailoringQuestions` (note caps: OverAll), `.AUD100.TQComments`, `.AUD100.Overallauditareastemp` (`Description`, seeded -1 + spawn) | — |
| KBA-200 | `.KBA200.EntityandContInfoKBA200` (entity/contact free-text — prop key `answer`, lowercase), `.KBA200.*Selection` (`chooseitem`), `.KBA200.Describe*Change` (`Description` and lowercase `description`) | — |
| KBA-400 | `.KBA400.Scoping` (toggles/FU/CtrlConTestWp/Comments), `.KBA400.AuditareaRelevantAssertions` | — |
| KBA-401 | `.KBA401.<Comp>TQ` (yesno), `.KBA401.<Comp>Findings` (text1/2/3), `.KBA401.EntityEnvOverall{Assessment,Effective}` (yesno), `.KBA401.Noncomplex*` | `.KBA401.EntityEnv*` matrix (present/controlsimplemented/functioning/risk) — reject + spawn-noop |
| KBA-502 | **`.{AREA}.RelevantAssertion` grid (ir/cr/rmm/PlannedAuditApproach) — THE IR/CR/RMM WRITE TARGET** + `Comment`. The grid is NOT visible in the bulk GET (`OverallAuditAreas[].childObjectList: []` — cross-form bindings the SPA renders per area) — write blind by AREA collectionKey per this registry against KBA-502's wpId. | FinancialLevelRisks non-Comment props (pt5 linked); RelevantAssertion `ProgramSteps` (pt5) |
| AUD-8xx | `.{AREA}.ProgramSteps`, `.{AREA}.AssertionLevelRisk` (spawn), tailoring/results/findings text | **`.{AREA}.RelevantAssertion` (ir/cr/rmm/approach) — DERIVED from KBA-502; writes here discard on refresh**; OverallAuditAreas / RelevantAssertion.ProgramSteps rollups |

`<Comp>` ∈ {ControlEnvironment, RiskAssess, ControlActivities, Information, Monitoring}. Path uses AREA short name, never the form number (`.CASH.ProgramSteps`).

## 5. Cross-cutting write protocol (EVERY write)
1. **Content-Type: application/json** on every body-bearing write (`build_batch_xhr` omitted it → 415 on all KC writes; single-call builders already inject it). [V]
2. **Submit to commit — PER-WORKPAPER ONLY.** Writes are PENDING until `POST /api/Workpaper/submit` `{binderId, workpaperId:"<wpId>"}`. A refresh discards unsubmitted writes. **Never submit with an EMPTY workpaperId** — the "submit all pending in binder" form silently DISCARDS pending writes on other forms instead of committing them. [V]
   - **IR/CR/RMM/approach cascade: the durable recipe is CORRECT wpId (KBA-502) + parked non-target tab + per-area writes → submit → refresh.** A "program grid reverts / unwritable" symptom is almost always a **wrong-wpId write to the DERIVED AUD-8xx surface** — the KBA-502-owned recompute discards it on refresh regardless of submit discipline. Always write the grid against KBA-502's wpId, never the AUD-8xx program's own wpId. [V]
   - **NEVER write to a workpaper OPEN in a KC tab.** The open SPA tab holds its own editor session; your `submit` commits the SPA's EMPTY working copy over your API writes → the grid reverts to `defaultanswer` on true reload (write 200s, submit 200s, still lost). Park the bridge tab on a NON-target form and write every target from there; confirm no other user tab holds the target open. [V]
   - **`submit` alone is NOT durable — submit THEN `refresh(sameWp)` to finalize BEFORE touching another workpaper.** write→submit (no refresh) then writing the next area silently discards the prior area's submitted-but-unfinalized state. Durable per-area unit: paced writes → ~1s → submit → ~0.9s → refresh THAT wp → verify via GetWorkpaperDiagnostics. [V]
3. **Verify AFTER reload — never the immediate GET** (it reads the uncommitted working copy; false state-3). [V]
3a. **Mandatory write→verify→retry loop — the standard KC write pattern.** KC silently drops a share of UpdateProperty→submit pairs even when payloads match this registry exactly: up to ~60% loss at ~350ms pacing, still ~30–50% loss with a 1–2s inter-write sleep — sleeps reduce but do NOT eliminate drops, so pacing alone is never sufficient. Binding pattern for every KC write: **write → settle ~1.2s → per-workpaper submit → re-read COMMITTED state after reload → rewrite ONLY the dropped cells → iterate until the committed read matches intent** (the CONVERGE loop; budget 2–4 rounds); batch the verify (one re-read covers the whole write set). The drop set ROTATES between rounds — each write echoes state 3 but the commit loses a different subset — so a counted "retry ≤3 misses" pass under-delivers on large sets; converge to match-intent instead of counting retries. A write not re-read as state-3-after-reload was NOT made — never count it, never blind-repeat it (re-read first). Exception: writes correctly targeted at KBA-502's wpId for the IR/CR/RMM/approach cascade need zero converge rounds when the wrong-wpId mistake above is avoided — the loop remains binding for all other KC forms, where rotating drops are real. [V]
4. **Completion oracle = diagnostics endpoint.** `POST /api/Workpaper/refresh/{eng}/{wp}` → `GET /api/diagnostics/GetWorkpaperDiagnostics/{eng}/{wp}` → `result.diagnostics[]`. Drive the loop from it. Form `diagnosticCount` is STALE. `type:"Missing KnowledgeCoach Form"` = a Yes-answer needs a dependent form → flip to No or add it. `type:"Unnecessary KnowledgeCoach Form"` = the inverse: an answer gates a form OFF and KC wants it REMOVED — the entry names it via `unnecessaryWorkpaperReferenceTag`/`unnecessaryWorkpaperDataBindingKey` (fixture: `data/fixtures/aud100-unnecessary-form-diag.json`); check these on the driving form BEFORE adding conditional forms (add-audit-programs.md), and treat existing ones as a removal worklist — the diagnostic is PERMANENT while the form stays. [V]
5. **Transport by origin, then verb.** KC origin: for **writes** (UpdateProperty/submit/refresh) the PRIMARY path is **in-page `fetch` via `chrome_eval` on a dedicated bridge tab** with an explicit `Authorization: Bearer`+`IdToken` — this is NOT CSP-blocked (a bare in-page fetch reaches the KC API; a 401 JSON, not a CSP error, proves it), and `chrome_api_call` is UNUSABLE for KC writes (SW double-encodes the body → 400). For **reads** (GetBinder/diagnostics/form GET) `chrome_api_call` (SW fetch, CSP-exempt) is clean and preferred. CAVEAT: in-page eval on a THROTTLED background *user* tab hangs the bridge channel — that caveat is for the user's own throttled tabs, NOT a dedicated foreground bridge tab. engagement/WPM/FP/workbench -> bridge primary, linked tab fallback. [V]
6. Sequential writes; settle ~1.2–1.5s between write and submit/verify — pacing at ~350ms alone still silently drops up to ~60% of writes, and no sleep duration alone fully prevents drops (see 3a). [V]
7. Fixed-point fill: choices-with-options → re-read → repeat (cap ~8) before text/signoffs; reset* = not-answered. [A:fill-kc-form]
8. TQ-cascade: answer `*TQ` first; skip descriptions where TQ=No. [A:architecture]
9. `build_reset_payload` FORBIDDEN (leaves state 3 blank; diagnostic never re-fires). [A:fill-kc-form]
10. Builders mandatory for writes; source fields from `inventory_form(decode_form(read_form()))` (integrity seal blocks hand-assembled keys). [A:kc.py]
11. DOM-first detection (`kcDom`) + GET substrate (GET over-reports fillable ~2:1). [A:fill-kc-form]
12. Single re-auth on 401: one deep-link reload (re-mint) + retry. [V]
13. Batch multi-write into ONE in-page JS call (KC tab times out on many sequential per-call XHRs). [A:architecture]

### Endpoint quick-ref
Write: `POST kc/api/Workpaper/UpdateProperty/{engGuid}/{wpId}` body `{collectionKey,objectKey,propertyKey,value,valueKey,dataEntryExpression:"",dataEntryExpressionContextObjectKey:""}` + Content-Type. Spawn: same, identity keys `""`, collection path in dataEntryExpression. Submit: `POST /api/Workpaper/submit` `{binderId, workpaperId:"<wpId>"}` (per-workpaper ONLY — empty wpId discards other forms' pending writes). Diagnostics: refresh then GET GetWorkpaperDiagnostics. wpId lookup: `GET /api/binder/GetBinder/{engGuid}` → result.workpapers[].

<!-- END -->
