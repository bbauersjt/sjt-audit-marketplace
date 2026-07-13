"""wpm_replace.py — replace a workpaper's content in place ("Upload new version").

Native in-place version overwrite via
PUT /v1/Documents/file/{clientId}/{documentId}. Endpoint spec:
references/endpoints/wpm_replace_version.json.

HARD RULE: the uploaded File's BASE name must equal the workpaper's
CURRENT DISPLAY NAME, or WPM returns 400 "File name does not match existing workpaper
name." The name can NOT come from the stored blob (crypto). So the caller MUST read the
current display name from WPM metadata first (wpm.folder_get -> row.name for the documentId)
and build the File with that exact base name + the file's real extension.

⛔ MANDATORY CONSENT GATE (every call, no exceptions): this UNRECOVERABLY overwrites a
workpaper in place (prior content survives only in CCH version history). Before calling this
builder you MUST (1) tell the user plainly it cannot be undone, (2) show the exact plan — for
each replacement, the TARGET (index + display name + folder/address) and the REPLACEMENT (file
name + source) — and (3) get an explicit "yes". No silent/batched/implied replace; the gate
fires every time, and a user "just do it" does NOT waive showing the plan + getting the yes.
It fires NO delete but is destructive-in-spirit. file-io.md's DEFAULT
replace stays soft-delete->evict->claim; use THIS only when the user explicitly wants a true
in-place new version. Full gate: references/modules/replace-workpaper.md.

House style: builds JS; the browser executes it (chrome_eval). File bytes ride as base64
inside the JS (DLP-unfiltered bridge channel) so they never cross the tool boundary, and the
WPM bearer is read from __cch_capture in-page (token stays in-page).
"""
import json

WPM = "https://workpapermanagementapi.cchaxcess.com"


def build_replace_version_js(client_id, document_id, file_b64, match_filename):
    """Return a self-contained async-IIFE JS string that, in-page:
      1. reads the freshest WPM bearer from window.__cch_capture,
      2. decodes file_b64 -> Blob -> File named `match_filename`,
      3. PUTs multipart `file` to /v1/Documents/file/{clientId}/{documentId} via XHR,
    returning {status, body}. 200 = replaced; 400 = name mismatch.

    Args:
      client_id, document_id: ints/strs identifying the workpaper.
      file_b64: base64 of the replacement file's bytes.
      match_filename: MUST equal the workpaper's current display name + the real extension
        (e.g. display 'C-1 Cash' + '.xlsx' -> 'C-1 Cash.xlsx'). Read the display name from
        wpm.folder_get(...).name first; do NOT guess.

    Run via chrome_eval(target=<engagement tab>). The tab must be VISIBLE (background tabs
    drop writes / throttle).
    """
    cfg = json.dumps({
        "clientId": str(client_id),
        "documentId": str(document_id),
        "fileName": match_filename,
        "b64": file_b64,
    })
    return (
        "(async () => {\n"
        "  const cfg = " + cfg + ";\n"
        "  const caps = window.__cch_capture||[];\n"
        "  const wpm = caps.filter(c=>/workpapermanagementapi/.test(c.url||'') && c.headers && c.headers.Authorization).slice(-1)[0];\n"
        "  if(!wpm) return JSON.stringify({error:'no WPM bearer in __cch_capture — trigger a WPM call first'});\n"
        "  const H = wpm.headers;\n"
        "  const bin = atob(cfg.b64); const arr = new Uint8Array(bin.length);\n"
        "  for (let i=0;i<bin.length;i++) arr[i]=bin.charCodeAt(i);\n"
        "  const fd = new FormData();\n"
        "  fd.append('file', new File([arr], cfg.fileName));\n"
        "  const res = await new Promise(resolve=>{\n"
        "    const x = new XMLHttpRequest();\n"
        "    x.open('PUT', `" + WPM + "/v1/Documents/file/${cfg.clientId}/${cfg.documentId}`);\n"
        "    ['Authorization','IDToken','USERLocale','Accept-Language','CountryCode'].forEach(k=>{ if(H[k]) x.setRequestHeader(k, H[k]); });\n"
        "    x.onreadystatechange=()=>{ if(x.readyState===4) resolve({status:x.status, body:(x.responseText||'').slice(0,400)}); };\n"
        "    x.onerror=()=>resolve({status:'neterr'});\n"
        "    x.send(fd);\n"
        "  });\n"
        "  return JSON.stringify(res);\n"
        "})()"
    )
# <!-- END -->
