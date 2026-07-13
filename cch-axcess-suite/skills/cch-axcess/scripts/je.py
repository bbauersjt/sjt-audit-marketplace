"""je.py — post actual journal entries into the TB via FinancialPrep.

Distinct from reports.create_je_report,
which only builds a JE *report* workpaper. This posts a real AJE/RJE/PAJE/TJE.

House style: this module BUILDS JS; the browser executes it (chrome_eval on the
bridge). The built JS sources the FP bearer in-page via the `cap:fp` sentinel
(`http_runner.capture_headers_js_expr('fp')` — reads window.__cch_capture, the
engagement-only-tab leg) so the token never crosses the tool channel. The
`ls:wpm` localStorage sentinel is dead on an engagement-only tab; `cap:fp` is
its capture-leg counterpart — see architecture.md.

Endpoint spec: references/endpoints/fp_journalentry.json.

NO-HARD-DELETE: create only (journalEntryId:0). No edit/delete is built here.
"""
import json

from . import http_runner

FP = "https://financialprep-api.cchaxcess.com"


def build_post_je_js(client_id, eng_id, je_type, lines, comment, document_id=None):
    """Return a self-contained async-IIFE JS string that, in-page:
      1. resolves each line's accountNumber -> accountId via the FP account search,
      2. asserts the entry balances (sum debits == sum credits),
      3. POSTs /v1.0/journalentry,
      4. verifies via the JE list,
    sourcing FP auth via the cap:fp sentinel (window.__cch_capture) and guarding the engagement URL.

    Args:
      client_id, eng_id: ints (engagementId field = client_id; periodId = str(eng_id)).
      je_type: "AJE" | "RJE" | "PAJE" | "TJE".  ("PJE" accepted as a synonym for PAJE.)
      lines: [{"number": "20000-100", "side": "D"|"C", "amount": 100.00}, ...].
      comment: free-text comment string.
      document_id: optional WPM documentId (int) of a referenced workpaper.

    Run with chrome_eval(target=<cch tab>). Returns JSON: {postStatus, id, landed} or {abort/error}.
    """
    je_type = {"PJE": "PAJE"}.get(str(je_type).upper(), str(je_type).upper())  # CCH term is PAJE; accept PJE synonym
    if je_type not in ("AJE", "RJE", "PAJE", "TJE"):
        raise ValueError(f"je_type must be AJE/RJE/PAJE(/PJE)/TJE, got {je_type!r}")
    # NOTE: AJE/RJE/PAJE are the confirmed types. TJE (tax JE) rides the SAME path/body
    # shape; supported for completeness only — confirm the "TJE" type string on first real use.
    if not lines:
        raise ValueError("lines is empty")
    cfg = {
        "clientId": int(client_id),
        "engId": str(eng_id),
        "jeType": je_type,
        "comment": comment,
        "documentId": (int(document_id) if document_id is not None else None),
        "lines": [
            {"number": str(l["number"]), "side": l["side"].upper(), "amount": round(float(l["amount"]), 2)}
            for l in lines
        ],
    }
    # round-trip guard
    for l in cfg["lines"]:
        if l["side"] not in ("D", "C"):
            raise ValueError(f"line side must be D or C: {l!r}")
    C = json.dumps(cfg)
    cap_fp = http_runner.capture_headers_js_expr("fp")  # cap:fp sentinel — reads __cch_capture in-page
    return (
        "(async () => {\n"
        "  const cfg = " + C + ";\n"
        "  const eng = `engagement/${cfg.clientId}/`;\n"
        "  if (!location.href.includes(eng) || !location.href.includes(cfg.engId))\n"
        "    return JSON.stringify({abort:'wrong engagement', url:location.href, want:eng+cfg.engId});\n"
        "  let H;\n"
        "  try { H = " + cap_fp + "; } catch(e){ return JSON.stringify({error:'no FP bearer in __cch_capture — trigger an FP call first'}); }\n"
        "  const call=(m,u,b)=>new Promise(res=>{const x=new XMLHttpRequest();x.open(m,u);\n"
        "    ['Authorization','IDToken','USERLocale','Accept-Language','CountryCode'].forEach(k=>{if(H[k])x.setRequestHeader(k,H[k]);});\n"
        "    if(b)x.setRequestHeader('Content-Type','application/json');\n"
        "    x.onreadystatechange=()=>{if(x.readyState===4)res({status:x.status,text:x.responseText});};\n"
        "    x.onerror=()=>res({status:'err'});x.send(b?JSON.stringify(b):null);});\n"
        "  const FP='" + FP + "';\n"
        "  // 1. resolve accounts\n"
        "  const li=[]; let dr=0, crd=0;\n"
        "  for (const l of cfg.lines){\n"
        "    const r=await call('GET',`${FP}/v1.0/account/${cfg.clientId}/accounts?page=0&query=${encodeURIComponent(l.number)}&take=16`);\n"
        "    let acc=null; try{ acc=(JSON.parse(r.text).accounts||[]).find(a=>a.number===l.number); }catch(e){}\n"
        "    if(!acc) return JSON.stringify({error:'account not found', number:l.number});\n"
        "    const money={value:'USD'+l.amount.toFixed(2),currency:'USD'}, empty={currency:'USD'};\n"
        "    if(l.side==='D') dr+=l.amount; else crd+=l.amount;\n"
        "    li.push({id:0, accountId:acc.id, accountName:acc.name, accountNumber:acc.number,\n"
        "      debit: l.side==='D'?money:empty, credit: l.side==='C'?money:empty, m3Type:null, defaultM3:null});\n"
        "  }\n"
        "  // 2. balance check\n"
        "  if (Math.round((dr-crd)*100)!==0) return JSON.stringify({error:'unbalanced', debit:dr, credit:crd});\n"
        "  // 3. post\n"
        "  const body={engagementId:cfg.clientId, periodId:cfg.engId, comment:cfg.comment, journalEntryId:0,\n"
        "    journalEntryType:cfg.jeType, lineItems:li, rollforwardOption:0, consolidatedEngagementId:null};\n"
        "  if (cfg.documentId!=null) body.documentId=cfg.documentId;\n"
        "  const post=await call('POST',`${FP}/v1.0/journalentry`, body);\n"
        "  let newId=null; try{ newId=JSON.parse(post.text).id; }catch(e){}\n"
        "  // 4. verify\n"
        "  const list=await call('GET',`${FP}/v1.0/journalentry?engagementId=${cfg.clientId}&periodId=${cfg.engId}`);\n"
        "  let landed=null; try{ const a=JSON.parse(list.text); const rows=Array.isArray(a)?a:(a.journalEntries||a.data||[]);\n"
        "    landed=rows.find(j=>String(j.id)===String(newId))||{notfound:true,total:rows.length}; }catch(e){ landed='listparsefail'; }\n"
        "  return JSON.stringify({postStatus:post.status, id:newId, balanced:true, landed});\n"
        "})()"
    )
# <!-- END -->
