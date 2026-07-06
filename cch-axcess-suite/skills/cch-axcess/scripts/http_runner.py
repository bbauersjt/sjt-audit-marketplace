"""Shared JS helpers that execute one or more HTTP calls from inside the user's
authenticated browser tab via mcp__Claude_in_Chrome__javascript_tool.

The Python side calls build_*() to construct a JS string, passes it to the Chrome
tool, then parses the JSON result with parse_result().
"""
import json
from typing import Any


# WPM locale headers — REQUIRED on every workpapermanagementapi call.
# Without them the server returns status 200 with an EMPTY ARRAY (silent
# failure that looks like "nothing in the folder"). Confirmed live 2026-06-03.
# scripts.wpm merges these into every call automatically; callers that build
# WPM XHRs by hand must merge them too. Caller-supplied values win.
WPM_LOCALE_HEADERS = {
    "USERLocale": "en-US",
    "Accept-Language": "en-US,en;q=0.9",
    "CountryCode": "US",
}


def with_wpm_locale(headers):
    """Merge WPM_LOCALE_HEADERS under caller headers (caller wins on conflict)."""
    return {**WPM_LOCALE_HEADERS, **(headers or {})}


# --- localStorage self-sourcing auth (AX-26 / "with_ls_auth" fix) ---------------
#
# BT3 sessions improvised localStorage-self-sourcing wrappers in B1/B2/B3 (~20 bash
# calls) because every builder baked the headers dict as a JSON literal. This is the
# shipped version: pass the SENTINEL string "ls:wpm" / "ls:fp" / "ls:kc" as the
# `headers` argument of any build_* function and the emitted JS reads tokens from
# localStorage AT RUNTIME (tokens never cross the tool channel; kc.refreshToken
# keeps them fresh — re-read per call).
#
# Families and casing (architecture.md):
#   ls:wpm / ls:fp / ls:workbench -> all-caps IDToken + WPM locale headers
#   ls:kc                         -> mixed-case IdToken
# NOTE: workbench-api is NOT reachable with KC tokens (live 2026-06-04). The probe is
# CLOSED (2026-06-05): the monkeypatch-captured WPM bearer IS accepted by workbench-api
# and financialprep-api — production workbench calls pass the captured header DICT (the
# WPM leg). "ls:workbench" stays defined but has no validated use; don't reach for it.

_LS_FAMILIES = {
    "wpm":       {"id_token_key": "IDToken", "locale": True},
    "fp":        {"id_token_key": "IDToken", "locale": True},
    "workbench": {"id_token_key": "IDToken", "locale": True},
    "kc":        {"id_token_key": "IdToken", "locale": False},
}

# --- capture-leg auth (AX-32b: engagement-only-tab leg) -------------------------
#
# The ls:<family> sentinels read KC localStorage and are DEAD on an engagement-only
# tab (no kc.* keys there). The `cap:<family>` sentinel is the counterpart: it reads
# the freshest matching header set from window.__cch_capture (the monkeypatch buffer
# / the WPM leg) in-page, so a session that only has the engagement tab can still
# authenticate WPM/FP/workbench calls. je.py and wpm_replace.py read __cch_capture
# directly with the same filter; this sentinel reconciles that pattern into the
# builders. Requires the auth_capture monkeypatch installed AND an API call already
# fired so a matching capture exists (else the expr throws in-page).
_CAPTURE_HOSTS = {
    "wpm":       "workpapermanagementapi",
    "fp":        "financialprep-api",
    "workbench": "workbench-api",
}


def capture_headers_js_expr(family):
    """JS EXPRESSION evaluating (at runtime, in-page) to the freshest captured
    engagement-tab headers for `family`, sourced from window.__cch_capture. Throws
    in-page if no matching capture exists (trigger an API call of that family first,
    with the auth_capture monkeypatch installed)."""
    host = _CAPTURE_HOSTS[family]
    return (
        "((() => {"
        "const _caps = window.__cch_capture || [];"
        "const _m = _caps.filter(c => /" + host + "/.test(c.url||'') && c.headers && c.headers.Authorization);"
        "if (!_m.length) throw new Error('no " + family + " bearer in __cch_capture - fire a " + family
        + " call first (auth_capture monkeypatch + a provoke)');"
        "const _h = _m[_m.length-1].headers;"
        "const _o = {'Authorization':_h.Authorization,'IDToken':_h.IDToken||_h.IdToken,"
        "'USERLocale':_h.USERLocale||'en-US','Accept-Language':_h['Accept-Language']||'en-US,en;q=0.9',"
        "'CountryCode':_h.CountryCode||'US','Accept':'application/json'};"
        "if (_h.traceparent) _o.traceparent = _h.traceparent;"
        "return _o;"
        "})())"
    )


def ls_headers_js_expr(family):
    """Return a JS EXPRESSION that evaluates (at runtime, in-page) to the headers
    object for `family`, self-sourced from KC localStorage. Throws in-page if the
    tokens are missing so the tool result surfaces a clear error."""
    fam = _LS_FAMILIES[family]
    locale = ("'USERLocale':'en-US','Accept-Language':'en-US,en;q=0.9','CountryCode':'US',"
              if fam["locale"] else "")
    return (
        "((() => {"
        "const _a = localStorage.getItem('kc.accessToken');"
        "const _i = localStorage.getItem('kc.idToken');"
        "if (!_a || !_i) throw new Error('KC tokens missing from localStorage - run this from a KC tab (or any tab on a kc-token origin)');"
        "return {'Authorization':'Bearer ' + _a,'" + fam["id_token_key"] + "':_i,"
        + locale + "'Accept':'application/json'};"
        "})())"
    )


def _headers_js(headers, content_type_if_body=False):
    """Resolve the `headers` argument of a build_* function into a JS expression.

    headers may be:
      - a dict (captured/manual headers)  -> baked as a JSON literal (status quo)
      - "ls:<family>" sentinel            -> runtime localStorage self-sourcing (KC tab)
      - "cap:<family>" sentinel           -> runtime __cch_capture self-sourcing (engagement tab)
    """
    if isinstance(headers, str):
        if headers.startswith("cap:"):
            fam = headers[4:]
            if fam not in _CAPTURE_HOSTS:
                raise ValueError(f"unknown cap family {fam!r} — one of {sorted(_CAPTURE_HOSTS)}")
            expr = capture_headers_js_expr(fam)
            if content_type_if_body:
                return "Object.assign(" + expr + ", {'Content-Type':'application/json'})"
            return expr
        if not headers.startswith("ls:"):
            raise ValueError(f"string headers must be an 'ls:<family>' or 'cap:<family>' sentinel, got {headers!r}")
        fam = headers[3:]
        if fam not in _LS_FAMILIES:
            raise ValueError(f"unknown ls family {fam!r} — one of {sorted(_LS_FAMILIES)}")
        expr = ls_headers_js_expr(fam)
        if content_type_if_body:
            return "Object.assign(" + expr + ", {'Content-Type':'application/json'})"
        return expr
    h = dict(headers or {})
    if content_type_if_body and not any(k.lower() == "content-type" for k in h):
        h["Content-Type"] = "application/json"
    return json.dumps(h)


def build_xhr_call(method, url, headers, body=None):
    """Build a JS expression that runs ONE XHR and returns {status, body}.

    Use XHR (not fetch) for cross-origin from engagement.cchaxcess.com to WPM -
    fetch fails CORS preflight, XHR with the same headers succeeds.

    Auto-adds Content-Type: application/json when body is provided and the
    header isn't already in `headers`. Captured headers pulled from a recent
    GET lack Content-Type; without this defense, body-bearing requests fail
    415. Existing callers that already pass Content-Type are unaffected.

    `headers` may be a dict (captured/manual) OR an "ls:<family>" sentinel
    ("ls:wpm" / "ls:fp" / "ls:kc") for runtime localStorage self-sourcing —
    see ls_headers_js_expr. Prefer the sentinel for WPM/FP/KC; workbench-api
    requires captured dicts (architecture.md transport matrix).
    """
    body_js = "null" if body is None else json.dumps(json.dumps(body))
    headers_js = _headers_js(headers, content_type_if_body=(body is not None))
    return (
        "(() => new Promise((resolve) => {\n"
        "  const x = new XMLHttpRequest();\n"
        "  x.open(" + json.dumps(method) + ", " + json.dumps(url) + ", true);\n"
        "  const h = " + headers_js + ";\n"
        "  for (const k in h) x.setRequestHeader(k, h[k]);\n"
        "  x.onreadystatechange = () => {\n"
        "    if (x.readyState === 4) resolve(JSON.stringify({status: x.status, body: x.responseText}));\n"
        "  };\n"
        "  x.send(" + body_js + ");\n"
        "}))()"
    )


def build_fetch_call(method, url, headers, body=None):
    """Build a JS expression that runs ONE fetch() and returns {status, body}.

    Safe for same-origin (e.g. KC tab -> KC API). For cross-origin use build_xhr_call.
    `headers` may be a dict OR an "ls:<family>" sentinel (AX-26).
    """
    headers_js = _headers_js(headers, content_type_if_body=(body is not None))
    init_js = ('{"method": ' + json.dumps(method)
               + ', "headers": ' + headers_js
               + ', "credentials": "include"')
    if body is not None:
        init_js += ', "body": ' + json.dumps(json.dumps(body))
    init_js += "}"
    return (
        "(() => fetch(" + json.dumps(url) + ", " + init_js + ")\n"
        "  .then(r => r.text().then(t => JSON.stringify({status: r.status, body: t})))\n"
        "  .catch(e => JSON.stringify({status: 0, error: String(e)})))()"
    )


def build_batch_xhr(calls, headers, concurrency=1, retry_on_body_drop=False):
    """Build a JS expression that runs N XHR calls and returns an array of {status, body, url, attempts}.

    Each call: {method, url, body (object|None)}.
    Sequential (concurrency=1) is required for kc_update_property - server drops
    parallel writes on the same form.
    `headers` may be a dict OR an "ls:<family>"/"cap:<family>" sentinel.

    Content-Type: application/json is now injected per call in `send1` whenever the
    call has a body — this is THE 415 fix (the single-call builders already inject it;
    this batch builder used to omit it, so every body-bearing KC write 415'd).

    retry_on_body_drop (AX-33, the "stick" fix): when True, each call retries up to
    5x (~200ms apart) while the response body matches /non-empty request body|Bad
    Request/i — the intermittent 400-in-a-200 where the POST body sporadically isn't
    received and the write silently no-ops (UpdateProperty). Default False keeps
    every existing caller byte-for-byte unchanged. `attempts` records how many tries
    landed the call. NOTE: the body-drop retry does NOT catch a 415 (the 415 response
    body doesn't match the regex) — and a non-2xx is NOT treated as success; 415/401
    break immediately (no retry) so the failure surfaces distinctly instead of being
    swallowed.
    """
    retry_js = "true" if retry_on_body_drop else "false"
    return (
        "(() => {\n"
        "  const calls = " + json.dumps(calls) + ";\n"
        "  const hdrs = " + _headers_js(headers) + ";\n"
        "  const N = " + str(int(concurrency)) + ";\n"
        "  const RETRY = " + retry_js + ";\n"
        "  const out = new Array(calls.length);\n"
        "  const send1 = (c) => new Promise((res) => {\n"
        "    const x = new XMLHttpRequest();\n"
        "    x.open(c.method, c.url, true);\n"
        "    for (const k in hdrs) x.setRequestHeader(k, hdrs[k]);\n"
        "    if (c.body) x.setRequestHeader('Content-Type', 'application/json');\n"
        "    x.onreadystatechange = () => {\n"
        "      if (x.readyState === 4) res({status: x.status, body: x.responseText});\n"
        "    };\n"
        "    x.send(c.body ? JSON.stringify(c.body) : null);\n"
        "  });\n"
        "  const run = (i) => (async () => {\n"
        "    const c = calls[i];\n"
        "    const MAXR = RETRY ? 5 : 1;\n"
        "    let r;\n"
        "    for (let attempt = 1; attempt <= MAXR; attempt++) {\n"
        "      r = await send1(c);\n"
        "      out[i] = {url: c.url, status: r.status, body: r.body, attempts: attempt};\n"
        "      // A non-2xx is NOT success. 415 (missing/ wrong Content-Type) and 401\n"
        "      // (auth) are not transient body-drops — the body-drop retry regex never\n"
        "      // matches an empty 415 body — so break immediately and let the caller see\n"
        "      // the distinct status instead of swallowing it as a retry exhaustion.\n"
        "      if (r.status === 415 || r.status === 401) break;\n"
        "      if (!RETRY) break;\n"
        "      if (!/non-empty request body|Bad Request/i.test(r.body || '')) break;\n"
        "      if (attempt < MAXR) await new Promise((s) => setTimeout(s, 200));\n"
        "    }\n"
        "  })();\n"
        "  return (async () => {\n"
        "    if (N === 1) {\n"
        "      for (let i = 0; i < calls.length; i++) await run(i);\n"
        "    } else {\n"
        "      let idx = 0;\n"
        "      const workers = Array.from({length: N}, async () => {\n"
        "        while (idx < calls.length) { const i = idx++; await run(i); }\n"
        "      });\n"
        "      await Promise.all(workers);\n"
        "    }\n"
        "    return JSON.stringify(out);\n"
        "  })();\n"
        "})()"
    )


def build_compact_batch_xhr(calls, headers, retry_on_body_drop=True):
    """Compact batch XHR for KC UpdateProperty writes (AX-36).

    Same writes + same AX-33 body-drop retry as build_batch_xhr, but returns ONLY
    [{i, status, attempts, ok, bodyDrop}] per call -- NEVER the response body. KC
    UpdateProperty echoes the full ~88KB working-copy form on every write; that echo's
    only consumer is the body-drop check (200-wrapping-400 silent no-op), which runs
    IN-PAGE here -- so the body never crosses the bridge. (A 55-field form went from
    ~2.7h of echo transfer to seconds.) Verification is unchanged: submit -> reload ->
    GetWorkpaperDiagnostics ("200 != applied"). Sequential (writes on one form drop if
    parallel). Keep build_batch_xhr for callers that genuinely need response bodies.
    """
    retry_js = "true" if retry_on_body_drop else "false"
    return (
        "(() => {\n"
        "  const calls = " + json.dumps(calls) + ";\n"
        "  const hdrs = " + _headers_js(headers) + ";\n"
        "  const RETRY = " + retry_js + ";\n"
        "  const out = [];\n"
        "  const send1 = (c) => new Promise((res) => {\n"
        "    const x = new XMLHttpRequest();\n"
        "    x.open(c.method, c.url, true);\n"
        "    for (const k in hdrs) x.setRequestHeader(k, hdrs[k]);\n"
        "    if (c.body) x.setRequestHeader('Content-Type', 'application/json');\n"
        "    x.onreadystatechange = () => { if (x.readyState === 4) res({status: x.status, bodyText: x.responseText}); };\n"
        "    x.send(c.body ? JSON.stringify(c.body) : null);\n"
        "  });\n"
        "  return (async () => {\n"
        "    for (let i = 0; i < calls.length; i++) {\n"
        "      const c = calls[i]; const MAXR = RETRY ? 5 : 1;\n"
        "      let r, attempts = 0, bodyDrop = false;\n"
        "      for (let attempt = 1; attempt <= MAXR; attempt++) {\n"
        "        attempts = attempt; r = await send1(c);\n"
        "        if (r.status === 415 || r.status === 401) break;\n"
        "        if (!RETRY) break;\n"
        "        bodyDrop = /non-empty request body|Bad Request/i.test(r.bodyText || '');\n"
        "        if (!bodyDrop) break;\n"
        "        if (attempt < MAXR) await new Promise(s => setTimeout(s, 200));\n"
        "      }\n"
        "      out.push({i: i, status: r.status, attempts: attempts, ok: r.status >= 200 && r.status < 300, bodyDrop: bodyDrop});\n"
        "    }\n"
        "    return JSON.stringify(out);\n"
        "  })();\n"
        "})()"
    )


def build_keepalive_js(enable=True):
    """Silent-audio keep-alive — the Chrome throttle killer (AX-33).

    A backgrounded ('hidden') tab gets frozen/throttled (eval timeouts, token-refresh
    stall). A 0-gain Web-Audio oscillator makes Chrome treat the tab as AUDIBLE, which
    exempts it from freeze even when backgrounded. This builds the JS to turn it ON or OFF.

    enable=True  → start it (IDEMPOTENT: reuses window.__cchKeepAlive if already running;
                   calls ctx.resume() since a programmatically-created AudioContext can
                   start 'suspended' until a user gesture — if it reports 'suspended', the
                   tab has had no gesture and the keep-alive won't take; surface that).
    enable=False → MANDATORY TEARDOWN: stop the oscillator, close the AudioContext, null
                   the handle. ALWAYS call this when done with the tab — a leaked oscillator
                   keeps the tab permanently throttle-exempt (the "100 un-throttleable tabs"
                   resource leak). Returns 'keepalive:off' / 'keepalive:already-off'.
    """
    if enable:
        return (
            "(() => { const k = window.__cchKeepAlive;"
            " if (k && k.ctx && k.ctx.state === 'running') return 'keepalive:already-on';"
            " const Ctx = window.AudioContext || window.webkitAudioContext;"
            " if (!Ctx) return 'keepalive:no-webaudio';"
            " const ctx = new Ctx(); const wasSuspended = ctx.state === 'suspended';"
            " const osc = ctx.createOscillator(); const g = ctx.createGain(); g.gain.value = 0;"
            " osc.connect(g); g.connect(ctx.destination); osc.start();"
            " if (wasSuspended) { try { ctx.resume(); } catch (e) {} }"
            " window.__cchKeepAlive = { ctx, osc, g };"
            " return wasSuspended"
            "   ? 'keepalive:suspended (NO gesture yet — click the tab once to activate; not exempt until then)'"
            "   : 'keepalive:on state=' + ctx.state; })()"
        )
    return (
        "(() => { const k = window.__cchKeepAlive; if (!k) return 'keepalive:already-off';"
        " try { k.osc.stop(); } catch (e) {} try { k.ctx.close(); } catch (e) {}"
        " window.__cchKeepAlive = null; return 'keepalive:off'; })()"
    )


def parse_result(js_result_str):
    """Parse the JSON string returned by build_xhr_call / build_fetch_call.

    Returns {status, body, body_text, error}.
    """
    outer = json.loads(js_result_str)
    body_text = outer.get("body", "")
    parsed = None
    if body_text:
        try:
            parsed = json.loads(body_text)
        except Exception:
            parsed = None
    return {
        "status": outer.get("status"),
        "body": parsed,
        "body_text": body_text,
        "error": outer.get("error"),
    }


# --- Named helpers for the two patterns that were previously improvised inline ---
#
# Both keep the honest execution model (architecture.md): the Python BUILDS a JS
# string, the browser EXECUTES it, auth is read from localStorage at runtime, and
# big payloads stay IN the page (`window.__x`) instead of crossing the tool channel.
# Naming them kills the B7-style ad-hoc inline JS that bred errors in testing.


def build_relay_store_js(payload, slot="__x"):
    """Build JS that STORES a large payload on `window.<slot>` and returns only a
    tiny ack — step 1 of the big-body relay.

    Use when a payload (an assembled form-write batch, a big move body, etc.) is
    too large to thread back-and-forth through the tool channel, or must NOT be
    surfaced (it may carry data the channel filters). Stash it in the page here,
    then fire the next call against it with build_relay_call_js — the payload
    never leaves the browser.

    Returns a JS expression that sets window[slot] = <payload> and returns
    {"stored": slot, "bytes": <approx length>}.
    """
    pj = json.dumps(payload)
    return (
        "(() => {\n"
        "  window[" + json.dumps(slot) + "] = " + pj + ";\n"
        "  return JSON.stringify({stored: " + json.dumps(slot) + ", "
        "bytes: (JSON.stringify(window[" + json.dumps(slot) + "])||'').length});\n"
        "})()"
    )


def build_relay_call_js(method, url, headers, slot="__x", body_key=None):
    """Build JS that fires ONE XHR using a payload previously stashed on
    `window.<slot>` by build_relay_store_js — step 2 of the big-body relay.

    The body sent is window[slot] (or window[slot][body_key] if body_key is set,
    to pick one field out of a stashed object). `headers` may be a dict OR an
    "ls:<family>" sentinel for runtime localStorage self-sourcing (preferred for
    WPM/FP/KC — see ls_headers_js_expr). Returns {status, body} like build_xhr_call.
    Content-Type: application/json is auto-added when not already present.
    """
    headers_js = _headers_js(headers, content_type_if_body=True)
    src = "window[" + json.dumps(slot) + "]"
    if body_key is not None:
        src = src + "[" + json.dumps(body_key) + "]"
    return (
        "(() => new Promise((resolve) => {\n"
        "  const payload = " + src + ";\n"
        "  const x = new XMLHttpRequest();\n"
        "  x.open(" + json.dumps(method) + ", " + json.dumps(url) + ", true);\n"
        "  const h = " + headers_js + ";\n"
        "  for (const k in h) x.setRequestHeader(k, h[k]);\n"
        "  x.onreadystatechange = () => {\n"
        "    if (x.readyState === 4) resolve(JSON.stringify({status: x.status, body: x.responseText}));\n"
        "  };\n"
        "  x.send(payload == null ? null : JSON.stringify(payload));\n"
        "}))()"
    )


def build_chunked_read_js(expr, start=0, length=50000, slot="__read"):
    """Build JS for CHUNKED enumeration of a large in-page read.

    `expr` is a JS expression that evaluates to the big string/object you want to
    page through (e.g. "JSON.stringify(window.__bundle)" or
    "window.__binder_map.tsv"). On the FIRST call it is evaluated once and the
    result cached as a string on window[slot]; subsequent calls slice the cache so
    a multi-megabyte read returns in bounded pieces without re-fetching and without
    blowing the tool-result size limit.

    Returns {total, start, end, chunk}. Loop with start += length until
    start >= total. Caller reassembles the chunks.
    """
    return (
        "(() => {\n"
        "  const SLOT = " + json.dumps(slot) + ";\n"
        "  if (typeof window[SLOT] !== 'string') {\n"
        "    const v = (" + expr + ");\n"
        "    window[SLOT] = (typeof v === 'string') ? v : JSON.stringify(v);\n"
        "  }\n"
        "  const s = window[SLOT];\n"
        "  const a = " + str(int(start)) + ", b = a + " + str(int(length)) + ";\n"
        "  return JSON.stringify({total: s.length, start: a, end: Math.min(b, s.length), "
        "chunk: s.slice(a, b)});\n"
        "})()"
    )
# <!-- END -->
