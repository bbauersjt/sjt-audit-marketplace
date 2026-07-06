#!/usr/bin/env python3
"""Generate the per-area planning cascade seed into data/seed/ for one or more audit types.

The cascade (AUD-100 area -> KBA-400 Scoping[6 toggles] -> spawned rows -> KBA-502
RelevantAssertion/AssertionLevelRisk) is 1:1 by area key. Live-verified on NPO
(CASH/INVEST/AR); templated onto every area of each TYPES title from areas.csv.

Idempotent: rewrites rows for the audit types in TYPES, preserves all others.
Run, then build_db.py. Edit TYPES to add titles (CNS/HOA flagged for future).

Confidence tags in `notes`:
  - NPO balance areas: 502 assertion-grid edges live-verified.
  - NPO risk areas: 502 grid templated, not live-verified.
  - other titles: whole cascade TEMPLATED from NPO, not re-verified live for that title.
  - co_feeds_row + AssertionLevelRisk edges: unisolated/inferred throughout.
"""
import csv, os
HERE=os.path.dirname(os.path.abspath(__file__)); SEED=os.path.join(HERE,"..","data","seed")
TYPES=["NPO","ASB","EBP","ALG"]   # CNS/HOA: future
ASSERTIONS=[("EO","EO - Existence/Occurrence"),("RO","RO - Rights/Obligations"),
            ("CO","CO - Completeness"),("AV","AV - Accuracy/Valuation"),
            ("CU","CU - Cutoff"),("UC","UC - Classification/Understandability")]

def _vtag(at, cat):
    if at=="NPO":
        return ("category=risk; 502 assertion-grid TEMPLATED from balance areas, NOT live-verified"
                if cat=="risk" else "balance area; matches live-verified CASH/INVEST/AR pattern")
    return f"audit_type={at}; cascade structure TEMPLATED from NPO live-capture, NOT re-verified live for this title"

def edges_for(at, area, plain, aud_form, cat):
    A=f"AuditAreas.{area}"; S=f"Scoping.{area}"
    rar=f"AuditareaRelevantAssertions.{area}"; rrsr=f"RiskRelatedSpecificrisks.{area}"
    ra502=f"RelevantAssertion.{area}"; alr502=f"AssertionLevelRisk.{area}"
    rtag=_vtag(at,cat)
    e=[(at,"AUD-100",A,"KBA-400",S,"spawns_scoping_row","area_selected","row objectKey==area key; immediate, no submit")]
    for tog in ["SigClassTans","MaterialAccount","SigDisclosure","SigAcctEst","SigFraudRisk","substantivetesting"]:
        e.append((at,"KBA-400",S,"KBA-400",f"{S}.{tog}","contains_toggle","",""))
    e+=[
     (at,"KBA-400",f"{S}.SigClassTans","KBA-400",rar,"spawns_row","NOTDASH","isolated-confirmed OR trigger (NPO)"),
     (at,"KBA-400",f"{S}.MaterialAccount","KBA-400",rar,"co_feeds_row","NOTDASH","OR-trigger; unisolated"),
     (at,"KBA-400",f"{S}.SigDisclosure","KBA-400",f"SigDisclosures.{area}","spawns_row","NOTDASH",""),
     (at,"KBA-400",f"{S}.SigAcctEst","KBA-400",rrsr,"spawns_row","NOTDASH",""),
     (at,"KBA-400",f"{S}.SigFraudRisk","KBA-400",rrsr,"co_feeds_row","NOTDASH","OR-trigger; unisolated"),
     (at,"KBA-400",f"{S}.substantivetesting","AUD-8xx",f"program.{area}","recommends_program","NOTDASH",f"program-side; {aud_form}"),
     (at,"KBA-400",rar,"KBA-502",ra502,"renders_section_client_side","assertion_picked",
        f"CLIENT RENDER ONLY - 502 UI shows only KBA-400-picked assertions; nothing stored on 502. {rtag}"),
    ]
    for code,_ in ASSERTIONS:
        e.append((at,"KBA-502",ra502,"KBA-502",f"{ra502}.{code}","assertion_row","shown_if_picked","write surface: selected/ir/cr/rmm on 502"))
    e.append((at,"KBA-400",rrsr,"KBA-502",alr502,"renders_section_client_side","","parallel to RelevantAssertion; INFERRED, not isolated live"))
    return e

def nodes_for(at, area, plain, aud_form, cat):
    S=f"Scoping.{area}"
    n=[(at,"AUD-100","OverAllTailoringQuestions",f"AuditAreas.{area}",f"{plain} - audit area selected","area_select",area,f"category={cat}"),
       (at,"KBA-400","Scoping",S,f"{plain} scoping row","row","",""),
       (at,"KBA-400","Scoping",f"{S}.SigClassTans","Sig class of transactions?","toggle","NOTDASH;DASH",""),
       (at,"KBA-400","Scoping",f"{S}.MaterialAccount","Material/sig account?","toggle","NOTDASH;DASH",""),
       (at,"KBA-400","Scoping",f"{S}.SigDisclosure","Sig disclosure?","toggle","NOTDASH;DASH",""),
       (at,"KBA-400","Scoping",f"{S}.SigAcctEst","Sig accounting estimate?","toggle","NOTDASH;DASH",""),
       (at,"KBA-400","Scoping",f"{S}.SigFraudRisk","Sig fraud risk?","toggle","NOTDASH;DASH",""),
       (at,"KBA-400","Scoping",f"{S}.substantivetesting","Substantive testing planned?","toggle","NOTDASH;DASH",""),
       (at,"KBA-400","AuditareaRelevantAssertions",f"AuditareaRelevantAssertions.{area}",f"{plain} relevant assertions","row","EO;RO;CO;AV;CU;UC",""),
       (at,"KBA-400","SigDisclosures",f"SigDisclosures.{area}",f"{plain} significant disclosures","row","",""),
       (at,"KBA-400","RiskRelatedSpecificrisks",f"RiskRelatedSpecificrisks.{area}",f"{plain} risk-related specific risks","row","",""),
       (at,"AUD-8xx","program",f"program.{area}",f"{plain} audit program ({aud_form})","program","",""),
       (at,"KBA-502","RelevantAssertion",f"RelevantAssertion.{area}",f"{plain} - 502 relevant-assertion risk section","section","",f"category={cat}"),]
    for code,lbl in ASSERTIONS:
        n.append((at,"KBA-502","RelevantAssertion",f"RelevantAssertion.{area}.{code}",lbl,"assertion","",""))
    n.append((at,"KBA-502","AssertionLevelRisk",f"AssertionLevelRisk.{area}",f"{plain} - 502 specific-risk (assertion-level) section","section","",""))
    return n

def _keep(path, hdr_default):
    if not os.path.exists(path): return hdr_default,[]
    with open(path,newline="") as f:
        r=csv.reader(f); hdr=next(r); rows=[row for row in r if row and row[0] not in TYPES]
    return hdr,rows

areas=list(csv.DictReader(open(os.path.join(SEED,"areas.csv"))))
E=[]; N=[]; per={}
for at in TYPES:
    rows=[a for a in areas if a["audit_type"]==at]; per[at]=len(rows)
    for a in rows:
        E+=edges_for(at,a["binding_key"],a["plain_name"],a["aud_form"],a["category"])
        N+=nodes_for(at,a["binding_key"],a["plain_name"],a["aud_form"],a["category"])

eh,ek=_keep(os.path.join(SEED,"cascade_edge.csv"),["audit_type","from_form","from_key","to_form","to_key","relation","trigger_value","notes"])
nh,nk=_keep(os.path.join(SEED,"form_node.csv"),["audit_type","form","collection","node_key","label","kind","value_keys","notes"])
with open(os.path.join(SEED,"cascade_edge.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(eh); w.writerows(ek); w.writerows(E)
with open(os.path.join(SEED,"form_node.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(nh); w.writerows(nk); w.writerows(N)
print("areas per type:",per,"| edges:",len(E),"| nodes:",len(N),"| preserved non-TYPES edges:",len(ek))
