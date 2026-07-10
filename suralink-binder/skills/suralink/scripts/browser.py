"""Low-level JS builders for Suralink HTTP calls.

Each function returns a JavaScript string. Run it in a Chrome tab logged into
app.suralink.com via the session transport — chrome_eval(code, target=tabId)
on the bridge (preferred), or mcp__Claude_in_Chrome__javascript_tool(code,
tabId) linked-tab (fallback); see the skill's architecture.md "Transport".
The JS runs in the page either way, so cross-origin calls to api.suralink.com
work and the session cookie authorizes everything.

Parse every result with parse_result().
"""
import json

# The 20 gateways (aGateway.php .. tGateway.php) are interchangeable. Pick one.
GATEWAY_URL = "https://app.suralink.com/gateways/aGateway.php"
GATEWAY_SECRET = "aud1tMgr!"          # static, required on every gateway call
API_BASE = "https://api.suralink.com"


def js_get_json(url):
    """JS expression: GET a (v2 API) URL with credentials, return
    JSON string {status, body, error}. `body` is the raw response text."""
    return (
        "(() => fetch(" + json.dumps(url) + ", {credentials:'include'})\n"
        "  .then(r => r.text().then(t => JSON.stringify({status:r.status, body:t})))\n"
        "  .catch(e => JSON.stringify({status:0, error:String(e)})))()"
    )


def js_gateway(controller, command, params):
    """JS expression: POST a legacy gateway command.

    Reads `window.csrf` LIVE per call, assembles the x-www-form-urlencoded
    body, returns JSON string {status, body, error}.

    CSRF behavior — what is actually observed, not assumed:

    - Read-only commands like `/Controllers/Auditors/Audit.getRequest` do NOT
      rotate `window.csrf` between calls. A whole engagement's 28-40 requests
      can be enumerated in one sequential JS sweep using the same token.
      Confirmed 2026-05-25 on Kymera 401k Audit 2025 (28 requests, single
      `window.csrf` snapshot, zero rotations, zero errors).
    - Some mutating commands (state changes, sign-offs) may rotate. The safe
      rule: always read `window.csrf` live per call so a rotation never
      stales the token mid-sweep.

    SEQUENCING — independent of rotation. Run sequentially anyway:
    one fetch in flight at a time. Two concurrent gateway calls collide on
    the session, not the token. Inside a single `javascript_exec`, that
    means awaiting each fetch before starting the next; do NOT
    `Promise.all` a batch of them.
    """
    fixed = {"secret": GATEWAY_SECRET, "controller": controller, "command": command}
    fixed.update({k: str(v) for k, v in params.items()})
    return (
        "(() => {\n"
        "  const c = window.csrf || {};\n"
        "  if (!c.csrf_token) return Promise.resolve(JSON.stringify("
        "{status:0, error:'window.csrf missing - is the tab on a Suralink page?'}));\n"
        "  const f = " + json.dumps(fixed) + ";\n"
        "  f.csrf_token = c.csrf_token;\n"
        "  f.csrf_hash_offset = c.csrf_hash_offset;\n"
        "  const body = Object.keys(f).map(k => "
        "encodeURIComponent(k)+'='+encodeURIComponent(f[k])).join('&');\n"
        "  return fetch(" + json.dumps(GATEWAY_URL) + ", {method:'POST', credentials:'include',\n"
        "    headers:{'Content-Type':'application/x-www-form-urlencoded'}, body})\n"
        "    .then(r => r.text().then(t => JSON.stringify({status:r.status, body:t})))\n"
        "    .catch(e => JSON.stringify({status:0, error:String(e)}));\n"
        "})()"
    )


def parse_result(js_result_str):
    """Parse the JSON string returned by js_get_json / js_gateway.

    Returns {status, body, body_text, error} where `body` is the parsed JSON
    (or None if the response was not JSON).
    """
    outer = json.loads(js_result_str)
    txt = outer.get("body", "")
    parsed = None
    if txt:
        try:
            parsed = json.loads(txt)
        except Exception:
            parsed = None
    return {
        "status": outer.get("status"),
        "body": parsed,
        "body_text": txt,
        "error": outer.get("error"),
    }
