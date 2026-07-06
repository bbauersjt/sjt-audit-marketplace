# chrome-bridge

A direct line from Claude Cowork into your **authenticated Chrome session** — no
linked tab, no file relay, no tab-group sprawl. Cowork calls MCP verbs; a local
relay forwards them over a localhost WebSocket to an MV3 extension, which acts
*inside the live page* (reads it, injects JS, calls the backend with the page's
own cookies/CSRF) and returns the result.

```
Cowork ──MCP stdio──► server.py (relay) ──localhost WS (token)──► extension ──► Axcess / Suralink page
```

This is the generic **transport**. Site-specific JS (Axcess, Suralink) lives in
the *skill*, not here.

## Pieces

| File | Role |
|------|------|
| `extension/` | MV3 extension. Holds the outbound WS, runs `fetch`/JS in the page. Load unpacked into Chrome. |
| `server.py` | Local stdio MCP server. Registers the `chrome_*` verbs; pure relay. |
| `bridge_core.py` | The WebSocket hub (background thread, request/response correlation). |
| `register_server.ps1` | Registers `server.py` with the Claude desktop app (auto-detects Python + config path, BOM-less). |
| `requirements.txt` | `mcp`, `websockets`. |
| `selftest.py` | Proves the server half with a mock extension — no Chrome/Claude needed. |

## Verbs

- `chrome_bridge_status()` — is the server up and the extension connected? Start here.
- `chrome_list_tabs()` — open tabs (id/url/title); use an id as `target`.
- `chrome_page_info(target="active")` — url/title/readyState.
- `chrome_fetch(url, method, headers, body, target="active")` — runs `fetch()` **inside the page**, so it carries that page's cookies/auth/CSRF. The backend-call primitive.
- `chrome_eval(code, target="active", world="MAIN")` — arbitrary JS, JSON result. MAIN world is subject to the page's CSP (may block eval); prefer `chrome_fetch` for backend calls.

## Setup (Windows)

1. **Install deps** — `pip install -r requirements.txt`
2. **Load the extension** — Chrome → `chrome://extensions` → enable *Developer mode* → *Load unpacked* → select the `extension/` folder. The toolbar badge reads **on** once it connects to the server (which must be running — see step 4/5).
3. **Register the server** — `powershell -ExecutionPolicy Bypass -File ".\register_server.ps1"`
4. **Fully quit and reopen the Claude desktop app** (not just close the window) so it loads the new MCP server and launches `server.py`.
5. **Test** — open an Axcess tab and log in, then in Cowork:
   - `chrome_bridge_status` → `extension_connected: true`
   - `chrome_list_tabs` → your tabs
   - `chrome_page_info` → the Axcess page's url/title
   - `chrome_fetch` an Axcess backend endpoint → JSON, authenticated.

Verify the server logic anytime without Chrome: `python selftest.py` → `SELFTEST OK`.

## Security model

- Server binds **127.0.0.1 only** and requires a **shared token** (`BRIDGE_TOKEN`, must match in `bridge_core.py` and `extension/background.js`).
- The relay is **capability-by-omission**: no filesystem/shell/code-exec verbs. Arbitrary JS (`chrome_eval`) runs in the *browser page*, contained by Chrome's sandbox — never on the host.
- You stay logged in as yourself; the extension reuses your live session (correct for an attest tool).

## Known limits / next

- **DEV token is hardcoded.** Before sharing with coworkers, move it to an extension options page (per-user secret), not source.
- **Multiple instances self-organize.** The desktop app and the Cowork runtime each spawn `server.py`. The first to bind 8765 is the **daemon** (owns the extension); any other becomes a **controller** that proxies its calls through the daemon. So whichever process a call lands on, it reaches the one extension. `chrome_bridge_status` shows `role` and (for the daemon) the controller count.
- **MV3 keepalive.** While connected, the worker pings every 20s so it isn't suspended (WebSocket activity resets Chrome's idle timer). A 30s alarm + on-demand connect cover cold starts, so a dropped socket self-heals within ~30s.
- **One extension at a time.** The daemon tracks a single extension socket. If the extension is installed in multiple Chrome profiles, disable all but one (the daemon would otherwise bind to whichever connected last). Multi-profile routing is a future enhancement.
- **`chrome_eval` vs page CSP.** If a page blocks eval, use `chrome_fetch` or `world="ISOLATED"`.
- **Distribution.** One-click handoff later = publish the extension (Web Store / enterprise CRX) + bundle `server.py` as a Cowork plugin (which registers the MCP server) + freeze Python to an exe so coworkers need no toolchain.
- **Port** is `8765` (change in both `bridge_core.py` and `background.js` if it collides).
