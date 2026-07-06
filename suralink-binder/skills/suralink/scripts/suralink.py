"""Suralink operations.

Each *_js() returns a JavaScript string for mcp__Claude_in_Chrome__javascript_tool.
Prerequisite: a Chrome tab logged into app.suralink.com.
IDs and gotchas: see ../references/architecture.md.
"""
import json
from . import browser

CONTROLLER_AUDIT = "/Controllers/Auditors/Audit"


# --------------------------------------------------------------------------
# Enumeration
# --------------------------------------------------------------------------

def list_requests_js():
    """JS: scrape the live Audit.php DOM for every request in the open audit.

    The tab MUST already be on Audit.php?auditId={X}. Returns a JSON array of
    {id, newFiles, newComments, created, due, category}. `id` is the canonical
    8-digit request id (use it as rId in fileProxy and as requestId to gateway).
    `newFiles` > 0 means the request has files the firm has not seen yet.
    """
    return (
        "JSON.stringify("
        "[...document.querySelectorAll('li[id^=\"request_\"][id$=\"_min\"]')].map(li => ({"
        "  id: li.id.replace('request_','').replace('_min',''),"
        "  newFiles: +(li.getAttribute('data-newcontentfiles')||0),"
        "  newComments: +(li.getAttribute('data-newcontentcomments')||0),"
        "  created: li.getAttribute('data-creationdate')||'',"
        "  due: li.getAttribute('data-duedatestring')||'',"
        "  category: li.getAttribute('data-firstletter')||''"
        "})))"
    )


def list_clients_js():
    """DEPRECATED — do not use. `Clients.php` is a React app that renders only
    one client at a time, so this DOM scrape cannot enumerate the roster.

    Use list_clients_page_js() / search_clients_js() / get_client_engagements_js()
    instead (see modules/clients-and-engagements.md). Kept only so older callers
    do not break.
    """
    return (
        "JSON.stringify("
        "[...document.querySelectorAll('a[href*=\"auditId=\"]')].map(a => ({"
        "  auditId: (a.href.match(/auditId=(\\d+)/)||[])[1],"
        "  label: (a.textContent||'').trim().replace(/\\s+/g,' ')"
        "})).filter(x => x.auditId))"
    )


# --------------------------------------------------------------------------
# Request detail (+ its files)
# --------------------------------------------------------------------------

def get_request_js(audit_id, request_id):
    """JS: gateway `getRequest` — full detail for one request, including
    data.files.firm[] and data.files.client[].

    request_id = the canonical 8-digit id from list_requests_js().
    Run these sequentially (one fetch in flight at a time). `window.csrf`
    does NOT rotate on `getRequest` in practice — confirmed across 28
    sequential calls on a real engagement — but sequential is still required
    because Suralink's session serializes concurrent calls. Whole-engagement
    enumeration runs cleanly inside one `javascript_exec` with awaited
    fetches in a for-loop.
    Parse the result with browser.parse_result(); files are at body['data']['files'].
    """
    return browser.js_gateway(CONTROLLER_AUDIT, "getRequest", {
        "requestId": request_id,
        "auditId": audit_id,
        "fromAudit": "true",
        "limitedData": "true",
    })


def extract_files(get_request_body, side="client"):
    """Given the parsed body of get_request_js (browser.parse_result()['body']),
    return the list of file dicts. side = 'client' (client uploads) or 'firm'.

    Each file dict has: id, fmsId, origFileName, fileType, fileSize, ts, etc.
    """
    try:
        return (get_request_body or {}).get("data", {}).get("files", {}).get(side, []) or []
    except Exception:
        return []


# --------------------------------------------------------------------------
# Download
# --------------------------------------------------------------------------

def file_proxy_url(file_id, audit_id, request_id):
    """The fileProxy download URL.

    rId MUST be the canonical request id the file belongs to — a mismatch
    returns 403 'User has no access to this engagement'.
    """
    return (browser.API_BASE + "/v2/fileProxy"
            "?fId=" + str(file_id) +
            "&aId=" + str(audit_id) +
            "&rId=" + str(request_id))


def download_file_js(file_id, audit_id, request_id, filename):
    """JS: fetch a file through fileProxy and save it to the BROWSER's Downloads
    folder via the blob + <a download> trick.

    The file bytes never enter Claude's context — this is the method to use for
    bulk sync. After it runs, the file is in the browser's default download
    location; the suralink-sync skill relocates it into the mirror folder.

    Returns JSON string {ok, bytes, filename} on success, {ok:false, ...} else.
    """
    url = file_proxy_url(file_id, audit_id, request_id)
    fn = json.dumps(filename)
    return (
        "(() => fetch(" + json.dumps(url) + ", {credentials:'include'})\n"
        "  .then(r => r.status===200\n"
        "    ? r.blob().then(b => {\n"
        "        const u = URL.createObjectURL(b);\n"
        "        const a = document.createElement('a');\n"
        "        a.href = u; a.download = " + fn + ";\n"
        "        document.body.appendChild(a); a.click(); a.remove();\n"
        "        setTimeout(() => URL.revokeObjectURL(u), 30000);\n"
        "        return JSON.stringify({ok:true, bytes:b.size, filename:" + fn + "});\n"
        "      })\n"
        "    : r.text().then(t => JSON.stringify({ok:false, status:r.status, body:t.slice(0,200)})))\n"
        "  .catch(e => JSON.stringify({ok:false, error:String(e)})))()"
    )


def fetch_file_b64_js(file_id, audit_id, request_id):
    """JS: fetch a file through fileProxy and return it base64-encoded.

    Use ONLY for a single small file whose bytes must come back to Claude (e.g.
    to write with the Write tool). For bulk sync use download_file_js() — base64
    through the tool channel bloats context and can trip the content filter.

    Returns JSON string {ok, b64, bytes}.
    """
    url = file_proxy_url(file_id, audit_id, request_id)
    return (
        "(() => fetch(" + json.dumps(url) + ", {credentials:'include'})\n"
        "  .then(r => r.blob()).then(b => new Promise(res => {\n"
        "     const fr = new FileReader();\n"
        "     fr.onload = () => res(JSON.stringify("
        "{ok:true, b64:String(fr.result).split(',')[1], bytes:b.size}));\n"
        "     fr.onerror = () => res(JSON.stringify({ok:false, error:'read failed'}));\n"
        "     fr.readAsDataURL(b);\n"
        "  })).catch(e => JSON.stringify({ok:false, error:String(e)})))()"
    )


def list_categories_js():
    """JS: scrape the live Audit.php DOM for the engagement's categories in
    WEBSITE (document) order. Returns a JSON array of category names.

    The tab MUST be on Audit.php?auditId={X}. Suralink's own category ids do
    not sort in display order, so document order is the source of truth. The
    suralink-sync skill uses this list to number category folders 01, 02, ...
    """
    return (
        "JSON.stringify("
        "[...document.querySelectorAll('div[id^=\"pm_category_\"]')]"
        ".filter(e => /^pm_category_\\d+$/.test(e.id))"
        ".map(e => (e.textContent||'').trim().replace(/\\s+/g,' ')))"
    )


def trigger_bulk_zip_js(layout="categories_requests"):
    """JS: trigger the bulk-zip export workflow end-to-end (select-all,
    open the Download popup, click the layout option).

    `layout` is one of:
      'categories_requests'  → Category/Request/File (default, recommended)
      'categories'           → Category/File
      'just_files'           → flat

    Wrapper-vs-anchor gotcha (fixed here): the click handlers are bound to
    the wrapper divs (`#multiDownloadCategory_wrapper`, etc.), NOT the inner
    `<a>` anchors. Clicking the anchor silently closes the popup with no
    effect. This function always clicks the wrapper.

    Returns JSON string {ok, layout}. The zip itself lands in the browser's
    download folder a minute or more later (server-side build). Poll for it
    with `suralink-sync`'s `sync.wait_for_download` or equivalent.

    The tab MUST be on Audit.php?auditId={X} with all-requests selectable.
    """
    target_map = {
        "categories_requests": "#multiDownloadCategory_wrapper",
        "categories":          "#multiDownloadCategoryOnly_wrapper",
        "just_files":          "#multiDownloadFolder_wrapper",
    }
    target = target_map.get(layout, target_map["categories_requests"])
    target_js = json.dumps(target)
    return (
        "(async () => {\n"
        "  try {\n"
        "    if (typeof closeCurrentPopup === 'function') closeCurrentPopup();\n"
        "    await new Promise(r => setTimeout(r, 400));\n"
        "    const cb = document.querySelector('#multiSelectCheckBox');\n"
        "    if (!cb) return JSON.stringify({ok:false, error:'no select-all checkbox'});\n"
        "    if (!cb.checked) cb.click();\n"
        "    await new Promise(r => setTimeout(r, 300));\n"
        "    if (typeof multiSelectDownload === 'function') multiSelectDownload(1);\n"
        "    else { const b = document.querySelector('#multiDownloadButton'); if (b) b.click(); }\n"
        "    await new Promise(r => setTimeout(r, 1200));\n"
        "    const wrapper = document.querySelector(" + target_js + ");\n"
        "    if (!wrapper) return JSON.stringify({ok:false, error:'layout wrapper not found: ' + " + target_js + "});\n"
        "    if (window.jQuery) window.jQuery(wrapper).trigger('click');\n"
        "    else wrapper.click();\n"
        "    return JSON.stringify({ok:true, layout:" + json.dumps(layout) + "});\n"
        "  } catch (e) {\n"
        "    return JSON.stringify({ok:false, error:String(e)});\n"
        "  }\n"
        "})()"
    )


def map_binder_js():
    """JS: scrape the ENTIRE binder structure from the live Audit.php DOM in one
    pass - categories in website order, each with the requests under it.

    The tab MUST be on Audit.php?auditId={X}. Returns a JSON object:
      {auditId, categories:[
        {catId, name, order, requests:[
          {id, displayNum, name, state, newFiles, newComments, created, due}
        ]}
      ]}

    This is the binder INDEX. It replaces looping get_request_js over every
    request just to enumerate - one scrape, no gateway round-trips, and it works
    uniformly across clients. File-level detail (fmsId / fId) is NOT in the map;
    run get_request_js for a specific request only when file ids are needed.
    """
    return r"""
(() => {
  const cats = [...document.querySelectorAll('div[id^="pm_category_"]')]
    .filter(e => /^pm_category_\d+$/.test(e.id));
  const out = {auditId: String(window.auditId||''), categories: []};
  cats.forEach((cd, idx) => {
    const catId = cd.id.replace('pm_category_','');
    const name = (cd.textContent||'').trim().replace(/\s+/g,' ');
    const ul = document.getElementById('category_'+catId+'_requestsList');
    const reqs = ul ? [...ul.querySelectorAll('li[id^="request_"][id$="_min"]')].map(li => {
      const id = li.id.replace('request_','').replace('_min','');
      const nm = document.getElementById('request_'+id+'_min_name');
      const dn = document.getElementById('request_'+id+'_min_id');
      return {
        id: id,
        displayNum: dn ? (dn.textContent||'').trim() : '',
        name: nm ? (nm.textContent||'').trim() : '',
        state: li.getAttribute('data-statesort')||'',
        newFiles: +(li.getAttribute('data-newcontentfiles')||0),
        newComments: +(li.getAttribute('data-newcontentcomments')||0),
        created: li.getAttribute('data-creationdate')||'',
        due: li.getAttribute('data-duedatestring')||''
      };
    }) : [];
    out.categories.push({catId: catId, name: name, order: idx+1, requests: reqs});
  });
  return JSON.stringify(out);
})()
"""


CONTROLLER_IAN = "/Controllers/Shares/IAN"


def load_ian_js(audit_id, last_id=0):
    """JS: gateway `loadIAN` - the engagement's activity timeline (the 'clock'
    feed at the top of the Suralink page; IAN = item-activity notifications).

    `last_id` is REQUIRED by the gateway (omitting it -> {success:false},
    error 'missingParameter'). Pass `0` for the whole feed; pass a prior
    `newestId` to fetch only messages since then.

    Returns {success, data:{ianData}} where ianData =
      {newestId, messages[], fromUsers, numRead, numUnread, filters}.
    Each message is an activity event:
      {id, requestId, auditId, stateChange, ts, isRead, userType, userId,
       notes, commentId, files[], requestData, ...}
    Messages whose files[] is non-empty are uploads - each file object carries
    id (fId), fmsId, origFileName, fileSize, requestId, ts, isDeleted.

    NOTE: the timeline is a convenience feed, NOT a dependable whole-engagement
    source - it can return empty even when the binder holds files, and it
    throttles under rapid calls. For "what's new" prefer map_binder_js (a DOM
    scrape: free, no throttle, carries per-request newFiles counts).
    Run sequentially (Suralink session serializes gateway calls; concurrent
    calls collide on the session, not the CSRF token — see browser.js_gateway).
    """
    return browser.js_gateway(CONTROLLER_IAN, "loadIAN", {
        "ianType": "1",
        "showMine": "-1",
        "auditId": audit_id,
        "lastId": str(last_id),
    })


# --------------------------------------------------------------------------
# Organization id
# --------------------------------------------------------------------------

def get_org_id_js():
    """JS: extract the firm's organizationId GUID from the page.

    organizationId is needed for every /v2/organization/... call. It is not a
    window global, but it is assigned in an inline <script>. Returns the GUID
    string, or '' if not found (wrong page / not logged in). Read it once per
    session and reuse it. Works on any logged-in Suralink page.
    """
    return (
        "(() => {"
        " for (const s of document.querySelectorAll('script:not([src])')) {"
        "   const m = (s.textContent||'').match("
        "/organizationId[\"']?\\s*[:=]\\s*[\"']([0-9a-f-]{30,})[\"']/i);"
        "   if (m) return m[1];"
        " }"
        " return '';"
        "})()"
    )


# --------------------------------------------------------------------------
# Clients & engagements
# --------------------------------------------------------------------------

CONTROLLER_CLIENTS = "/Controllers/Auditors/Clients"


def list_clients_page_js(org_id, limit=100, offset=0):
    """JS: GET one page of the firm's client roster.

    GET /v2/organization/{org}/clients?limit&offset  -- `limit` is capped at
    100 server-side. Returns the raw response JSON string {status, body};
    parse with browser.parse_result(). The parsed body is
    {totalCount, offset, limit, data:[...], nextPage}; each client dict has
    {id, customId, name, state, contactEmail, departmentId, isSensitive, ...}.

    To enumerate ALL clients, call repeatedly with offset 0, 100, 200, ...
    until offset + len(data) >= totalCount  (see clients-and-engagements.md).
    """
    url = (browser.API_BASE + "/v2/organization/" + str(org_id) +
           "/clients?limit=" + str(min(int(limit), 100)) +
           "&offset=" + str(int(offset)))
    return browser.js_get_json(url)


def search_clients_js(org_id, term):
    """JS: GET /v2/organization/{org}/clients/search?searchTerm={term}

    Name-indexed search. Returns {status, body}; parsed body is
    {totalHits, hitsCount, clients:[{score, highlight, source}]} where `source`
    is the client object (incl. engagementCounts {total,active,inactive,archived}).
    An empty term returns HTTP 400 - use list_clients_page_js to enumerate all.
    Use this to resolve a client the user named.
    """
    import urllib.parse
    url = (browser.API_BASE + "/v2/organization/" + str(org_id) +
           "/clients/search?searchTerm=" + urllib.parse.quote(str(term)))
    return browser.js_get_json(url)


def get_client_engagements_js(client_id):
    """JS: gateway `getClientInfo` for one client, parsed to its engagements.

    The gateway returns {data:{groupId, html}} where `html` is the engagement
    table fragment. This runs the gateway call AND parses the html in the tab,
    returning a JSON string:
      {clientId, engagements:[{auditId, name, state, customId}]}
    `state` is 'Active' / 'Inactive' / 'Archived' (from the row class).

    Sibling engagements under one client (e.g. Audit 2024 + Audit 2025) come
    back as separate rows - this is how prior-year vs current-year audits are
    told apart. Run sequentially (Suralink session serializes gateway calls —
    see browser.js_gateway for the full story; "CSRF rotates" is outdated lore).
    """
    inner = browser.js_gateway(CONTROLLER_CLIENTS, "getClientInfo",
                               {"clientId": client_id})
    cid = json.dumps(str(client_id))
    return (
        "(() => " + inner + ".then(s => {\n"
        "  let html=''; try { const o=JSON.parse(s);\n"
        "    const j=JSON.parse(o.body); html=(j.data&&j.data.html)||''; } catch(e){}\n"
        "  const doc=new DOMParser().parseFromString(html,'text/html');\n"
        "  const rows=[...doc.querySelectorAll('tr[id*=\"_engagements_row_\"]')]\n"
        "    .filter(r => !/_row_empty$/.test(r.id));\n"
        "  const eng=rows.map(r => {\n"
        "    const cls=(typeof r.className==='string'?r.className:'');\n"
        "    const st=(cls.match(/\\b(Active|Inactive|Archived)\\b/)||[])[1]||'';\n"
        "    return {\n"
        "      auditId:(r.id.match(/_row_(\\d+)$/)||[])[1]||'',\n"
        "      name:((r.querySelector('.engagementName')||{}).textContent||'').trim(),\n"
        "      customId:((r.querySelector('.customId')||{}).textContent||'').trim(),\n"
        "      state:st };\n"
        "  });\n"
        "  return JSON.stringify({clientId:" + cid + ", engagements:eng});\n"
        "}))()"
    )


# --------------------------------------------------------------------------
# Ferry — getting large data OUT of the tab and onto disk
# --------------------------------------------------------------------------
# The Cowork tool channel truncates JS return values around ~1 KB of display.
# A whole-engagement enumeration (28-90 requests, files included) is many KB.
# Don't paginate through chunked JS reads — it's slow and brittle.
#
# Pattern: serialize on the JS side, save as a Blob to a download trigger,
# and read from the user's download folder on the Python side. The browser's
# default Downloads folder is where Chrome puts it; mount `~/Downloads` via
# `request_cowork_directory` (the suralink-sync skill's import-zip module
# already does this) and read the file with normal Python.

def dump_to_download_js(payload_expr, filename):
    """JS: serialize `payload_expr` as JSON, save it as `filename` to the
    user's browser-default download folder.

    `payload_expr` is a JS expression evaluated inside the tab (e.g.
    `'window.__reqs'`, or any JS that produces a JSON-serializable value).
    `filename` is the suggested download name (e.g. `'kymera_reqs.json'`).

    Returns JSON string {ok, bytes, filename} on success.

    Use this whenever a tool-channel return would be more than a few hundred
    bytes — whole-engagement enumerations, binder maps, big diff results.
    Then on the Python side: wait for the file to appear under your mounted
    Downloads folder, json.load it, proceed. Faster, simpler, no truncation.

    Example:
        # JS side — store the data first, then dump it
        run("window.__data = { categories: [...], files: [...] }")
        run(suralink.dump_to_download_js("window.__data", "kymera_dump.json"))
        # Python side — read it back
        data = json.load(open("/path/to/Downloads/kymera_dump.json"))
    """
    fn = json.dumps(filename)
    return (
        "(() => {\n"
        "  try {\n"
        "    const payload = (" + payload_expr + ");\n"
        "    const txt = JSON.stringify(payload);\n"
        "    const b = new Blob([txt], {type:'application/json'});\n"
        "    const u = URL.createObjectURL(b);\n"
        "    const a = document.createElement('a');\n"
        "    a.href = u; a.download = " + fn + ";\n"
        "    document.body.appendChild(a); a.click(); a.remove();\n"
        "    setTimeout(() => URL.revokeObjectURL(u), 30000);\n"
        "    return JSON.stringify({ok:true, bytes:b.size, filename:" + fn + "});\n"
        "  } catch (e) {\n"
        "    return JSON.stringify({ok:false, error:String(e)});\n"
        "  }\n"
        "})()"
    )
