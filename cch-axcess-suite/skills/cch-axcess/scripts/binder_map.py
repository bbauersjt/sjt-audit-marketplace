"""Binder map — fast, low-token inventory of an engagement binder.

INSTALL: drop into cch-axcess/scripts/binder_map.py

Meta tool for the rest of this skill. Produces a single greppable map of the
whole binder (every folder + every filed item: KCForms / LeadSheet / Report /
Workpaper) so other modules can resolve "where is workpaper X / form Y" by
grepping a file instead of poking the binder folder-by-folder and losing things.

Adapts to ANY binder structure — the folder skeleton is read live from
`folder_tree`, never assumed against a 4-digit template.

Two-endpoint gotcha (the whole reason this module exists — see architecture.md):
  * GET /v1/NewEngagementView/folder/{clientId}/{locationId}/   -> child FOLDERS only
        (this is what fires when you expand a node in the tree UI)
  * GET /v1/NewEngagementView/{clientId}/{locationId}/{engagementId}  -> folder CONTENTS
        (subfolders AND documents, typed). THIS is the one that returns workpapers.
  Confusing them returns 200 + an empty/folder-only list and silently loses every
  filed document. `scripts.wpm.folder_get` already builds the correct (contents) shape.

Pattern (mirrors scripts.kc.bulk_capture_forms_js):
  Python emits one JS blob -> runs in the engagement tab via the Chrome JS tool ->
  the blob walks the binder, renders the map, triggers a browser download, and
  returns ONLY compact counts to Claude. The full map text never enters context.

Tab requirements: any CCH tab on the target binder (KC tab preferred).
Headers (localStorage-primary, see architecture.md): build_map_js self-sources
kc.accessToken + kc.idToken from localStorage and sends them WPM-style
(Authorization + ALL-CAPS IDToken + locale headers) — no monkeypatch or folder
click needed when a KC tab is open. FALLBACK (engagement-tab-only): install
scripts.auth_capture.INSTALL_MONKEYPATCH_JS and trigger ONE WPM call (click any
folder); the JS then discovers the freshest captured workpapermanagementapi
header set from window.__cch_capture. Either way tokens never leave the browser.

Validated: Nansemond Indian Nation 2025 (client 94136 / engagement 368481),
2026-05-28 — 35 folders, 151 items (82 KCForms, 38 Workpaper, 17 Report, 14 LeadSheet).
"""
import json as _json

WPM = "https://workpapermanagementapi.cchaxcess.com"


def build_map_js(client_id: int | str, eng_id: int | str,
                 download_filename: str | None = None,
                 concurrency: int = 8) -> str:
    """JS that builds the full binder map and (optionally) downloads it.

    client_id : first int in the engagement URL (/engagement/{clientId}/...).
    eng_id    : second int (/engagementview/{engagementId}).
    download_filename : if set, triggers a browser download of "{stem}.txt" +
                        "{stem}.tsv" (download needs the user's OK). If None,
                        the map is stashed on window.__binder_map only.
    concurrency : parallel folder_get fan-out; 8 observed safe.

    Returns a compact JSON summary to Claude:
      {clientId, engagementId, folderCount, itemCount, byType,
       mapChars, tsvRows, stashed:true, downloaded:bool}

    Full artifacts live on window.__binder_map = {meta, txt, tsv, folders, itemsByLoc}.
    """
    stem = (download_filename or "binder-map").rsplit(".", 1)[0]
    return (
        "(async () => {\n"
        f"  const CID = {_json.dumps(str(client_id))}, ENG = {_json.dumps(str(eng_id))};\n"
        f"  const N = {int(concurrency)};\n"
        f"  const STEM = {_json.dumps(stem)};\n"
        f"  const DOWNLOAD = {_json.dumps(bool(download_filename))};\n"
        f"  const BASE = {_json.dumps(WPM)} + '/v1/NewEngagementView';\n"
        # --- HEADERS: localStorage-primary (KC tokens authenticate WPM, sent WPM-style:
        #     Authorization + ALL-CAPS IDToken + locale headers; see architecture.md).
        #     __cch_capture is fallback ONLY when no KC tokens are in localStorage.
        #     Tokens are read at runtime and never leave the page.
        "  let H = null;\n"
        "  const _kcAccess = localStorage.getItem('kc.accessToken');\n"
        "  const _kcId = localStorage.getItem('kc.idToken');\n"
        "  if (_kcAccess && _kcId) {\n"
        "    H = {'Authorization': 'Bearer ' + _kcAccess, 'IDToken': _kcId,\n"
        "         'USERLocale': 'en-US', 'Accept-Language': 'en-US,en;q=0.9',\n"
        "         'CountryCode': 'US', 'Accept': 'application/json'};\n"
        "  } else {\n"
        "    const caps = (window.__cch_capture||[]).filter(c => /workpapermanagementapi/.test(c.url||''));\n"
        "    if (!caps.length) return JSON.stringify({error:'No KC tokens in localStorage and no WPM capture. Open a KC tab, or install the monkeypatch and click a folder once.'});\n"
        "    H = caps[caps.length-1].headers;\n"
        "  }\n"
        "  const xhr = (url) => new Promise((res) => {\n"
        "    const x = new XMLHttpRequest(); x.open('GET', url);\n"
        "    Object.entries(H).forEach(([k,v]) => { try{ x.setRequestHeader(k,v); }catch(e){} });\n"
        "    x.onload = () => res({status:x.status, text:x.responseText});\n"
        "    x.onerror = () => res({status:0, text:''});\n"
        "    x.send();\n"
        "  });\n"
        # --- 1. folder skeleton (complete, incl. empty folders)
        "  const tr = await xhr(`${BASE}/folders/${CID}`);\n"
        "  let tree; try{ tree = JSON.parse(tr.text); }catch(e){ return JSON.stringify({error:'folder_tree parse failed', status:tr.status}); }\n"
        "  const folders = [];\n"
        "  const walk = (n, depth) => { folders.push({locationId:n.locationId, index:n.index||'', name:n.name, depth}); (n.children||[]).forEach(c => walk(c, depth+1)); };\n"
        "  (tree.root||[]).forEach(n => walk(n, 0));\n"
        # --- 2. contents per folder via the CONTENTS endpoint (subfolders + documents)
        "  const itemsByLoc = {};\n"
        "  for (let i=0; i<folders.length; i+=N) {\n"
        "    const chunk = folders.slice(i, i+N);\n"
        "    const res = await Promise.all(chunk.map(f => xhr(`${BASE}/${CID}/${f.locationId}/${ENG}`).then(r => ({f, r}))));\n"
        "    res.forEach(({f, r}) => {\n"
        "      let rows=null; try{ rows = JSON.parse(r.text); }catch(e){}\n"
        "      if (!Array.isArray(rows)) return;\n"
        "      itemsByLoc[f.locationId] = rows.filter(x => x.type !== 'Folder').map(x => ({\n"
        "        index: x.index || x.documentIndex || '', type: x.type, name: x.name,\n"
        "        id: x.documentId || x.reportId || x.fileId || '', ext: x.fileExtension || '',\n"
        "        status: x.documentStatus || x.formStatus || ''\n"
        "      }));\n"
        "    });\n"
        "  }\n"
        # --- 3. render: indented tree (human) + flat TSV (grep)
        "  const clean = (name, ext) => { let nm = String(name).replace(/\\.+$/,''); if (ext) { const e = String(ext).replace(/^\\.+/,''); if (e && !nm.toLowerCase().endsWith('.'+e.toLowerCase())) nm = nm+'.'+e; } return nm; };\n"
        "  const lines = [`# Binder map  client ${CID}  engagement ${ENG}  generated ${new Date().toISOString()}`];\n"
        "  const flat = ['folderIndex\\titemIndex\\ttype\\tname\\tstatus\\tid'];\n"
        "  const byType = {}; let itemCount = 0;\n"
        "  folders.forEach(f => {\n"
        "    const pad = '  '.repeat(f.depth);\n"
        "    lines.push(`${pad}[${f.index||'--'}] ${f.name}`);\n"
        "    (itemsByLoc[f.locationId]||[]).slice().sort((a,b) => String(a.index).localeCompare(String(b.index))).forEach(it => {\n"
        "      itemCount++; byType[it.type] = (byType[it.type]||0)+1;\n"
        "      const disp = clean(it.name, it.ext);\n"
        "      lines.push(`${pad}  - <${it.type}> [${it.index||''}] ${disp}${it.status?'  ('+it.status+')':''}`);\n"
        "      flat.push(`${f.index||''}\\t${it.index||''}\\t${it.type}\\t${disp}\\t${it.status||''}\\t${it.id}`);\n"
        "    });\n"
        "  });\n"
        "  const txt = lines.join('\\n'); const tsv = flat.join('\\n');\n"
        "  window.__binder_map = {meta:{clientId:CID, engagementId:ENG, folderCount:folders.length, itemCount, byType}, txt, tsv, folders, itemsByLoc};\n"
        # --- 4. optional download (two files)
        "  let downloaded = false;\n"
        "  if (DOWNLOAD) {\n"
        "    const dl = (text, fname, mime) => { const b = new Blob([text], {type:mime}); const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = fname; document.body.appendChild(a); a.click(); document.body.removeChild(a); };\n"
        "    dl(txt, STEM+'.txt', 'text/plain'); dl(tsv, STEM+'.tsv', 'text/tab-separated-values'); downloaded = true;\n"
        "  }\n"
        "  return JSON.stringify({clientId:CID, engagementId:ENG, folderCount:folders.length, itemCount, byType, mapChars:txt.length, tsvRows:flat.length-1, stashed:true, downloaded}, null, 2);\n"
        "})()"
    )


def fetch_chunk_js(which: str = "txt", start: int = 0, length: int = 1200) -> str:
    """JS to read a slice of the stashed map for transfer into a file when a
    browser download isn't wanted. `which` in {'txt','tsv'}. Returns the slice
    plus total length so the caller can loop until start+length >= total.
    """
    key = "txt" if which == "txt" else "tsv"
    return (
        "(() => { const m = window.__binder_map; if(!m) return JSON.stringify({error:'no map; run build_map_js first'});"
        f" const s = m.{key}; return JSON.stringify({{total:s.length, chunk:s.slice({int(start)}, {int(start)+int(length)})}}); }})()"
    )
# <!-- END -->
