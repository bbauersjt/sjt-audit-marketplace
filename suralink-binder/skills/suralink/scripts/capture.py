"""Capture helpers for TRAINING MODE — observing Suralink operations the skill
does not yet know. See ../references/training-mode.md.

These return JS strings to run in the Suralink tab via the session transport
(bridge chrome_eval preferred; linked-tab javascript_tool fallback).
"""

# Install a network monkey-patch that records gateway + API calls (with bodies)
# into window.__sl. Survives client-side navigation; a FULL PAGE RELOAD wipes it
# — reinstall after any reload.
INSTALL_CAPTURE_JS = r"""
(() => {
  if (window.__sl_installed) { window.__sl = []; return 'reset'; }
  window.__sl = [];
  const want = /gateway|api\.suralink\.com/i;
  const of = window.fetch;
  window.fetch = function(input, init){
    const url = typeof input==='string'?input:(input&&input.url);
    const p = of.apply(this, arguments);
    if (want.test(url||'')) {
      p.then(r => { const c=r.clone(); c.text().then(t => {
        window.__sl.push({k:'fetch', url, method:(init&&init.method)||'GET',
          body:String((init&&init.body)||''), status:r.status, resp:(t||'').slice(0,3500)});
      }).catch(()=>{}); }).catch(()=>{});
    }
    return p;
  };
  const oo=XMLHttpRequest.prototype.open, os=XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open=function(m,u){this.__m=m;this.__u=u;return oo.apply(this,arguments);};
  XMLHttpRequest.prototype.send=function(b){
    if (want.test(this.__u||'')) {
      this.addEventListener('load', () => { try {
        window.__sl.push({k:'xhr', url:this.__u, method:this.__m, body:String(b||''),
          status:this.status, resp:(this.responseText||'').slice(0,3500)});
      } catch(e){} });
    }
    return os.apply(this, arguments);
  };
  window.__sl_installed = true;
  return 'capture armed';
})()
"""


def summarize_capture_js():
    """JS: return a SANITIZED summary of window.__sl — one line per call,
    no raw URLs or tokens (the Cowork content filter blocks those). Shows
    host+path with ids masked, gateway controller::command, body param NAMES,
    and response top-level keys.
    """
    return r"""
(() => {
  const sl = window.__sl || [];
  const sanPath = p => p.split('/').map(s =>
    /^[0-9a-f]{8}-[0-9a-f]{4}/i.test(s) ? '{GUID}' :
    /^\d{4,}$/.test(s) ? '{NUM}' : s).join('/');
  const out = sl.map((c,i) => {
    let host='', path='', qkeys=[];
    try { const u=new URL(c.url, location.origin); host=u.host; path=sanPath(u.pathname);
          qkeys=[...u.searchParams.keys()]; } catch(e){}
    const form = {};
    (c.body||'').split('&').forEach(p => { const j=p.indexOf('=');
      if (j>0) form[decodeURIComponent(p.slice(0,j))]=1; });
    let respKeys=null;
    try { const j=JSON.parse(c.resp); respKeys=Object.keys(j);
      if (j.data && typeof j.data==='object')
        respKeys=respKeys.concat(Object.keys(j.data).slice(0,12).map(k=>'data.'+k)); }
    catch(e){ respKeys='nonjson'; }
    return { i, host, path, method:c.method, status:c.status,
             query:qkeys, controller:form.controller?'(see body)':null,
             command: Object.keys(form).indexOf('command')>=0 ? 'present':null,
             bodyParams: Object.keys(form), respKeys };
  });
  return JSON.stringify(out, null, 1);
})()
"""


def read_command_js(index):
    """JS: for ONE captured gateway call (by index in window.__sl), return its
    controller, command, and non-secret param NAMES, plus response data shape.
    Never emits secret/csrf values.
    """
    return (
        "(() => { const c=(window.__sl||[])[" + str(int(index)) + "]; if(!c) return 'no such index';\n"
        "  const o={}; (c.body||'').split('&').forEach(p=>{const j=p.indexOf('=');"
        "    o[decodeURIComponent(p.slice(0,j))]=decodeURIComponent(p.slice(j+1));});\n"
        "  const drop=['secret','csrf_token','csrf_hash_offset'];\n"
        "  const params={}; for(const k in o) if(drop.indexOf(k)<0) params[k]=o[k];\n"
        "  let dataShape=null; try{const j=JSON.parse(c.resp);"
        "    dataShape=j.data&&typeof j.data==='object'?Object.keys(j.data):typeof j.data;}catch(e){}\n"
        "  return JSON.stringify({controller:o.controller, command:o.command, params, dataShape}, null, 1);\n"
        "})()"
    )
