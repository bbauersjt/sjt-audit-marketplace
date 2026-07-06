"""
chrome-bridge — local stdio MCP server.

Gives Claude Cowork a DIRECT line into your authenticated Chrome session via a
companion MV3 extension over a localhost WebSocket — no linked tab, no file
relay for commands. The agent calls these verbs; the server forwards them to the
extension, which acts inside the live page and returns the result.

Relay verbs (status/list_tabs/page_info/fetch/eval/navigate/tabs/network) carry
no host capability of their own — arbitrary JS runs only inside the browser page,
contained by Chrome's sandbox; the no-code-exec line on this host is intact.

FILE verbs (chrome_download, chrome_upload, chrome_eval out_path) read & write
real files so Axcess downloads/uploads and oversized payloads don't have to cross
the model context. They touch only the absolute path you hand them (parent dir
created for writes; file must exist for reads) — no delete, no listing, no
traversal helper. Optionally confine them with BRIDGE_FILE_ROOTS below.
"""

import base64
import json
import os
import sys
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP

from bridge_core import BridgeHub

mcp = FastMCP("chrome-bridge")
hub = BridgeHub()

# Optional file-IO confinement. Empty list = any absolute path is allowed (writes
# create the parent dir; reads require the file to exist). To restrict, list
# absolute roots, e.g. [r"C:\Users\bbauer\Documents", r"S:\Engagements"].
BRIDGE_FILE_ROOTS: list[str] = []

# Headers worth keeping when summarizing captured requests for auth reuse.
_AUTH_KEYS = {"authorization", "idtoken", "userlocale", "accept-language",
              "countrycode", "traceparent", "ocp-apim-subscription-key"}


def _check_root(ap: str) -> None:
    if not BRIDGE_FILE_ROOTS:
        return
    for root in BRIDGE_FILE_ROOTS:
        r = os.path.abspath(root)
        if ap == r or ap.startswith(r + os.sep):
            return
    raise ValueError(f"path is outside BRIDGE_FILE_ROOTS: {ap}")


def _dest_path(p: str) -> str:
    if not os.path.isabs(p):
        raise ValueError(f"out_path must be absolute: {p!r}")
    ap = os.path.abspath(p)
    _check_root(ap)
    return ap


def _src_path(p: str) -> str:
    if not os.path.isabs(p):
        raise ValueError(f"local_path must be absolute: {p!r}")
    ap = os.path.abspath(p)
    _check_root(ap)
    if not os.path.isfile(ap):
        raise FileNotFoundError(ap)
    return ap


# ---------------------------------------------------------------- status / read

@mcp.tool()
def chrome_bridge_status() -> dict:
    """Is the bridge server up and the Chrome extension connected? Start here.
    Reports role (daemon/controller) and, for the daemon, the live extension."""
    return hub.status()


@mcp.tool()
def chrome_list_tabs() -> dict:
    """List open browser tabs (id, url, title, active, windowId). Use a tab's id
    as `target` on the other verbs to act on a specific tab."""
    return {"tabs": hub.call("list_tabs")}


@mcp.tool()
def chrome_page_info(target: int | str = "active") -> dict:
    """url / title / readyState of a tab (default: the active tab)."""
    return hub.call("page_info", {"target": target})


# ---------------------------------------------------------------- in-page calls

@mcp.tool()
def chrome_fetch(url: str, method: str = "GET", headers: dict | None = None,
                 body: str | None = None, target: int | str = "active",
                 timeout: float = 30.0) -> dict:
    """Run fetch() INSIDE the page (text response), so it carries that page's
    cookies / auth / CSRF — the same-origin backend primitive. For cross-origin
    Axcess calls use chrome_eval with an XHR (fetch fails CORS preflight there);
    for binary or large responses use chrome_download. Returns {status, ok, url,
    headers, body}."""
    return hub.call("fetch",
                    {"url": url, "method": method, "headers": headers or {},
                     "body": body, "target": target}, timeout=timeout)


@mcp.tool()
def chrome_api_call(url: str, method: str = "GET", headers: dict | None = None,
                    body: str | dict | None = None, timeout: float = 30.0) -> dict:
    """Call a backend API from the EXTENSION's service worker (NOT in-page). Use
    this for strict-CSP origins like knowledgecoach.cchaxcess.com where chrome_eval
    / chrome_fetch are CSP-blocked (KC form reads + writes: UpdateProperty, submit,
    refresh, GetWorkpaperDiagnostics, GetBinder). SW fetch is CSP-exempt and, for
    hosts in host_permissions (*.cchaxcess.com), CORS-bypassed (no preflight).
    Supply the captured KC bearer + IdToken in `headers` (from chrome_network_recent);
    cookies ride along via credentials:include. Returns {status, ok, url, headers, body}.

    `body` may be a JSON string OR a dict — a dict is json.dumps'd here so a clean
    JSON string crosses the wire (the skill no longer has to pre-serialize)."""
    if isinstance(body, dict):
        body = json.dumps(body)
    return hub.call("api_call",
                    {"url": url, "method": method, "headers": headers or {},
                     "body": body}, timeout=timeout)


@mcp.tool()
def chrome_eval(code: str, target: int | str = "active", world: str = "MAIN",
                timeout: float = 30.0, out_path: str | None = None) -> dict:
    """Run arbitrary JS in a tab; returns the JSON-serializable result. MAIN world
    sees the page's own JS/globals (Axcess allows eval there). This is the
    workhorse for Axcess backend calls — run the skill's XHR builders here.

    If out_path is set, the (string) result is written to that file and the tool
    returns {path, bytes} instead of the payload — for results too big to return
    inline. Returns {result} or {error} otherwise."""
    res = hub.call("eval", {"code": code, "target": target, "world": world}, timeout=timeout)
    if out_path and isinstance(res, dict) and res.get("result") is not None:
        try:
            dest = _dest_path(out_path)
            r = res["result"]
            text = r if isinstance(r, str) else json.dumps(r)
            parent = os.path.dirname(dest)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(text)
            return {"path": dest, "bytes": len(text.encode("utf-8"))}
        except Exception as e:
            return {"error": f"write failed: {e}", "type": type(e).__name__}
    return res


# ---------------------------------------------------------------- navigation / tabs

@mcp.tool()
def chrome_navigate(url: str, target: int | str = "active", timeout: float = 60.0) -> dict:
    """Navigate a tab to `url` and wait for load to complete (e.g. land KC deep-link
    tokens). Returns {id, url, title, status}."""
    return hub.call("navigate", {"url": url, "target": target}, timeout=timeout)


@mcp.tool()
def chrome_open_tab(url: str, active: bool = False, timeout: float = 60.0) -> dict:
    """Open a new tab at `url` (active=False opens it in the background) and wait
    for load — e.g. warm a KC tab without disturbing your active one. Returns
    {id, url, title}."""
    return hub.call("open_tab", {"url": url, "active": active}, timeout=timeout)


@mcp.tool()
def chrome_close_tab(tab_id: int) -> dict:
    """Close a tab by id (e.g. a background tab you opened to warm tokens)."""
    return hub.call("close_tab", {"tab_id": tab_id})


# ---------------------------------------------------------------- files

@mcp.tool()
def chrome_download(url: str, out_path: str, method: str = "GET",
                    headers: dict | None = None, body: str | None = None,
                    target: int | str = "active", timeout: float = 180.0) -> dict:
    """Authenticated, binary-safe fetch of `url` from INSIDE the page, saved to
    `out_path` on disk. Cookies/auth ride along — the Axcess file-download
    primitive, and the clean way to land a big payload without crossing the model
    context. Returns {path, bytes, status, content_type}."""
    try:
        dest = _dest_path(out_path)
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}
    res = hub.call("download", {"url": url, "method": method, "headers": headers or {},
                                "body": body, "target": target}, timeout=timeout)
    if not isinstance(res, dict) or res.get("b64") is None:
        return res  # error / unexpected — pass through
    try:
        data = base64.b64decode(res["b64"])
        parent = os.path.dirname(dest)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
        return {"path": dest, "bytes": len(data), "status": res.get("status"),
                "content_type": res.get("content_type")}
    except Exception as e:
        return {"error": f"write failed: {e}", "type": type(e).__name__}


@mcp.tool()
def chrome_upload(local_path: str, url: str, field_name: str = "file",
                  filename: str | None = None, fields: dict | None = None,
                  headers: dict | None = None, target: int | str = "active",
                  timeout: float = 180.0) -> dict:
    """Upload a local file to `url` as multipart/form-data, POSTed INSIDE the page
    so auth rides along (the Axcess file-upload primitive). `fields` adds extra
    form fields; `field_name`/`filename` name the file part. Returns {status, ok,
    body}."""
    try:
        src = _src_path(local_path)
        with open(src, "rb") as f:
            data = f.read()
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}
    b64 = base64.b64encode(data).decode("ascii")
    return hub.call("upload",
                    {"url": url, "field_name": field_name,
                     "filename": filename or os.path.basename(src), "b64": b64,
                     "fields": fields or {}, "headers": headers or {}, "target": target},
                    timeout=timeout)


# ---------------------------------------------------------------- network capture

@mcp.tool()
def chrome_network_recent(host_filter: str = "cchaxcess", limit: int = 10,
                          auth_only: bool = True) -> dict:
    """Recent request headers captured via webRequest — the auth-capture path
    (the engagement bearer rides Axcess API calls; no monkeypatch needed). To
    stay compact this collapses to ONE entry per host (the freshest request that
    carries an Authorization header), and by default returns only auth-relevant
    headers. Set auth_only=False for all headers (can be large). Returns
    {requests: [{host, method, url, ts, headers}]}."""
    res = hub.call("network_recent", {"host_filter": host_filter, "limit": 200})
    reqs = res.get("requests", []) if isinstance(res, dict) else []
    if not isinstance(reqs, list):
        return res
    best: dict = {}
    for r in reqs:
        host = urlparse(r.get("url", "")).netloc
        hdrs = r.get("headers", {}) or {}
        has_auth = any(k.lower() == "authorization" for k in hdrs)
        score = (1 if has_auth else 0, r.get("ts", 0))
        cur = best.get(host)
        if cur is None or score > cur[0]:
            best[host] = (score, r)
    out = []
    for host, (score, r) in best.items():
        hdrs = r.get("headers", {}) or {}
        if auth_only:
            hdrs = {k: v for k, v in hdrs.items() if k.lower() in _AUTH_KEYS}
        out.append({"host": host, "method": r.get("method"), "url": r.get("url"),
                    "ts": r.get("ts"), "headers": hdrs})
    out.sort(key=lambda e: e.get("ts", 0), reverse=True)
    return {"requests": out[:limit]}


def main():
    hub.start()
    mcp.run()


if __name__ == "__main__":
    main()
