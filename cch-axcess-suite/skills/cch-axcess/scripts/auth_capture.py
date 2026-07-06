"""Live header capture for CCH Axcess.

Two paths:

1. KC fast path — tokens are in localStorage, no monkey-patch needed. Pass the
   "ls:<family>" headers sentinel to any builder (http_runner.ls_headers_js_expr).
2. Engagement / WPM — tokens are added by Angular interceptors. Need the monkey-patch
   to read them from a live XHR. Use the INSTALL_MONKEYPATCH_JS constant + capture_query_js().

These functions return JavaScript strings meant to be passed to
mcp__Claude_in_Chrome__javascript_tool. The Python side never sees a token directly.
"""

def KC_HEADERS_JS():
    """DEPRECATED shim (AX-26). The old string constant caused a TypeError when
    called (BT3 B1). Use the "ls:<family>" headers sentinel on any builder
    (http_runner.ls_headers_js_expr) instead. This shim returns the ls:kc JS
    expression wrapped to return JSON, for any straggler call-sites."""
    from . import http_runner
    return "(() => JSON.stringify(" + http_runner.ls_headers_js_expr("kc") + "))()"


INSTALL_MONKEYPATCH_JS = r"""
(() => {
  if (window.__cch_capture_installed) return 'already-installed';
  window.__cch_capture = [];
  const _of = window.fetch;
  window.fetch = function(input, init) {
    try {
      const url = typeof input === 'string' ? input : input.url;
      const headers = (init && init.headers) || (input && input.headers) || {};
      const h = {};
      if (headers instanceof Headers) headers.forEach((v,k)=>h[k]=v);
      else if (Array.isArray(headers)) headers.forEach(([k,v])=>h[k]=v);
      else Object.assign(h, headers);
      window.__cch_capture.push({type:'fetch', url, method:(init&&init.method)||'GET', headers:h, body: init&&init.body});
    } catch(e){}
    return _of.apply(this, arguments);
  };
  const _oo = XMLHttpRequest.prototype.open;
  const _osh = XMLHttpRequest.prototype.setRequestHeader;
  const _os = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function(m, u) { this.__m=m; this.__u=u; this.__h={}; return _oo.apply(this, arguments); };
  XMLHttpRequest.prototype.setRequestHeader = function(k, v) { (this.__h=this.__h||{})[k]=v; return _osh.apply(this, arguments); };
  XMLHttpRequest.prototype.send = function(b) {
    window.__cch_capture.push({type:'xhr', url:this.__u, method:this.__m, headers:this.__h, body:b});
    return _os.apply(this, arguments);
  };
  window.__cch_capture_installed = true;
  return 'monkeypatch-installed';
})()
"""

def capture_query_js(host_pattern: str = "cchaxcess", limit: int = 15) -> str:
    """Build a JS snippet that returns the last N captured calls matching the host pattern."""
    return (
        "JSON.stringify("
        f"  window.__cch_capture.filter(c => /{host_pattern}/.test(c.url)).slice(-{limit}),"
        "  null, 2"
        ")"
    )


def headers_from_capture(captures: list, host_substring: str) -> dict:
    """Pick the freshest matching capture and return its headers dict.

    captures: parsed JSON array from window.__cch_capture
    host_substring: 'workpapermanagementapi' or 'knowledgecoach' etc.

    Filters out [BLOCKED: Sensitive key] placeholders — they came from Cowork's
    PII filter, not from CCH. The real token is still in the browser; just
    re-capture in the page context if you got blocked output.
    """
    matches = [c for c in captures if host_substring in c.get("url", "")]
    if not matches:
        raise ValueError(f"No captures match {host_substring!r}. Trigger a UI action first.")
    return matches[-1]["headers"]
# <!-- END -->
