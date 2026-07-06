"""
Cowork Bridge — core transport hub (no MCP, no Office; a pure relay).

Single-instance-aware. Several chrome-bridge processes can run at once (the
Claude desktop app and the Cowork runtime each spawn one from the same config).
They self-organize over the bridge port:

  - The first process to bind 127.0.0.1:8765 becomes the DAEMON. It owns the
    WebSocket to the browser extension and also accepts CONTROLLER connections
    from peer chrome-bridge processes.
  - Any process that cannot bind becomes a CONTROLLER: it connects to the daemon
    and proxies its tool calls through it.

Either way every process's call() reaches the one extension. If the daemon dies,
controllers re-elect — whoever binds next becomes the new daemon, and the
extension reconnects to it.

Capability-by-omission: this module has NO filesystem / shell / code-exec verbs.
It forwards an opaque {method, params} to the extension and returns the reply.
"""

import asyncio
import json
import threading

BRIDGE_HOST = "127.0.0.1"
BRIDGE_PORT = 8765
# DEV token — MUST match extension/background.js. Replace with a per-user secret
# (entered on an options page) before distributing to coworkers.
BRIDGE_TOKEN = "cowork-bridge-dev-7f3a9c21"

DEFAULT_TIMEOUT = 30.0

# Files (downloads/uploads) and big payloads ride the WebSocket; lift the
# library's 1 MB default so binary file transfers fit.
WS_MAX_SIZE = 64 * 1024 * 1024


class BridgeHub:
    def __init__(self, host=BRIDGE_HOST, port=BRIDGE_PORT, token=BRIDGE_TOKEN):
        self.host = host
        self.port = port
        self.token = token
        self.loop = None
        self._ready = threading.Event()
        self._started = False

        self.role = None            # "daemon" | "controller" | None
        self._server = None         # daemon: the websockets server
        self._ext_ws = None         # daemon: the extension socket
        self._controllers = set()   # daemon: peer controller sockets
        self._daemon_ws = None      # controller: socket to the daemon
        self._pending = {}          # id -> Future, for THIS process's own calls
        self._routes = {}           # daemon: eid -> (controller_ws, cid) proxied
        self._idctr = 0
        self.ext_info = None
        self._last_error = None

    # ---------- public, synchronous API (called from MCP tool threads) ----------
    def start(self, wait=6.0):
        if self._started:
            return
        self._started = True
        threading.Thread(target=self._run, name="bridge-net", daemon=True).start()
        self._ready.wait(wait)

    def status(self):
        return {
            "listening": f"ws://{self.host}:{self.port}/",
            "role": self.role,
            "server_ready": self.role is not None,
            "extension_connected": (self._ext_ws is not None) if self.role == "daemon" else None,
            "linked_to_daemon": (self._daemon_ws is not None) if self.role == "controller" else None,
            "controllers": len(self._controllers) if self.role == "daemon" else None,
            "extension": self.ext_info if self.role == "daemon" else None,
            "last_error": self._last_error,
        }

    def call(self, method, params=None, timeout=DEFAULT_TIMEOUT):
        if self.loop is None or not self._ready.is_set():
            return {"error": "bridge not running", "last_error": self._last_error}
        fut = asyncio.run_coroutine_threadsafe(
            self._call(method, params or {}, timeout), self.loop)
        try:
            return fut.result(timeout + 5)
        except Exception as e:
            return {"error": str(e), "type": type(e).__name__}

    # ---------- event-loop thread ----------
    def _run(self):
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._main())
        except Exception as e:
            self._last_error = f"{type(e).__name__}: {e}"
            self._ready.set()

    async def _main(self):
        await self._elect()
        self._ready.set()
        # supervisor: re-elect if we have no role, or lost our daemon link
        while True:
            await asyncio.sleep(2.0)
            if self.role is None or (self.role == "controller" and self._daemon_ws is None):
                await self._elect()

    async def _elect(self):
        import websockets
        # 1) try to become the daemon by binding the port
        try:
            self._server = await websockets.serve(self._on_conn, self.host, self.port,
                                                   max_size=WS_MAX_SIZE)
            self.role = "daemon"
            self._last_error = None
            return
        except OSError:
            pass  # port taken -> someone else is the daemon
        # 2) otherwise become a controller of the existing daemon
        try:
            await self._connect_controller()
            self.role = "controller"
            self._last_error = None
        except Exception as e:
            self.role = None
            self._last_error = f"controller connect failed: {type(e).__name__}: {e}"

    # ---------- daemon side ----------
    async def _on_conn(self, ws, path=None):
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=10)
            hello = json.loads(raw)
        except Exception:
            await self._safe_close(ws)
            return
        if hello.get("token") != self.token:
            await self._safe_close(ws, 4001, "bad token")
            return
        if hello.get("role") == "controller":
            await self._serve_controller(ws)
        else:
            await self._serve_extension(ws, hello)

    async def _serve_extension(self, ws, hello):
        self._ext_ws = ws
        self.ext_info = {"ext_version": hello.get("ext_version")}
        try:
            await ws.send(json.dumps({"type": "welcome"}))
            async for raw in ws:
                try:
                    msg = json.loads(raw)
                except Exception:
                    continue
                t = msg.get("type")
                if t == "ping":
                    await self._safe_send(ws, {"type": "pong"})
                    continue
                if t == "pong":
                    continue
                eid = msg.get("id")
                route = self._routes.pop(eid, None)
                if route is not None:                       # reply to a proxied call
                    cws, cid = route
                    await self._safe_send(cws, {"id": cid, "ok": msg.get("ok"),
                                                "value": msg.get("value"),
                                                "error": msg.get("error")})
                else:                                       # reply to our own call
                    fut = self._pending.pop(eid, None)
                    if fut is not None and not fut.done():
                        fut.set_result(msg)
        except Exception:
            pass
        finally:
            if self._ext_ws is ws:
                self._ext_ws = None
                self.ext_info = None

    async def _serve_controller(self, ws):
        self._controllers.add(ws)
        try:
            await ws.send(json.dumps({"type": "welcome"}))
            async for raw in ws:
                try:
                    msg = json.loads(raw)
                except Exception:
                    continue
                if msg.get("type") == "ping":
                    await self._safe_send(ws, {"type": "pong"})
                    continue
                cid, method, params = msg.get("id"), msg.get("method"), msg.get("params", {})
                if self._ext_ws is None:
                    await self._safe_send(ws, {"id": cid, "ok": False, "error": "no extension connected"})
                    continue
                self._idctr += 1
                eid = self._idctr
                self._routes[eid] = (ws, cid)
                try:
                    await self._ext_ws.send(json.dumps({"id": eid, "method": method, "params": params}))
                except Exception as e:
                    self._routes.pop(eid, None)
                    await self._safe_send(ws, {"id": cid, "ok": False, "error": f"forward failed: {e}"})
        except Exception:
            pass
        finally:
            self._controllers.discard(ws)
            for eid in [k for k, (cws, _) in list(self._routes.items()) if cws is ws]:
                self._routes.pop(eid, None)

    # ---------- controller side ----------
    async def _connect_controller(self):
        import websockets
        url = f"ws://{self.host}:{self.port}/"
        ws = await asyncio.wait_for(websockets.connect(url, max_size=WS_MAX_SIZE), timeout=5)
        await ws.send(json.dumps({"type": "hello", "token": self.token, "role": "controller"}))
        await asyncio.wait_for(ws.recv(), timeout=5)  # welcome
        self._daemon_ws = ws
        asyncio.ensure_future(self._controller_reader(ws))

    async def _controller_reader(self, ws):
        try:
            async for raw in ws:
                try:
                    msg = json.loads(raw)
                except Exception:
                    continue
                if msg.get("type") in ("ping", "pong"):
                    continue
                fut = self._pending.pop(msg.get("id"), None)
                if fut is not None and not fut.done():
                    fut.set_result(msg)
        except Exception:
            pass
        finally:
            if self._daemon_ws is ws:
                self._daemon_ws = None  # supervisor will re-elect

    # ---------- unified call (works as daemon or controller) ----------
    async def _call(self, method, params, timeout):
        if self.role == "daemon":
            ext = self._ext_ws
            if ext is None:
                return {"error": "no extension connected",
                        "hint": "open Chrome with the Cowork Bridge extension loaded; "
                                "its toolbar badge should read 'on'."}
            sock = ext
        elif self.role == "controller":
            sock = self._daemon_ws
            if sock is None:
                return {"error": "bridge daemon unavailable (re-electing)"}
        else:
            return {"error": "bridge has no role yet", "last_error": self._last_error}

        self._idctr += 1
        mid = self._idctr
        fut = self.loop.create_future()
        self._pending[mid] = fut
        try:
            await sock.send(json.dumps({"id": mid, "method": method, "params": params}))
        except Exception as e:
            self._pending.pop(mid, None)
            return {"error": f"send failed: {e}"}
        try:
            msg = await asyncio.wait_for(fut, timeout)
        except asyncio.TimeoutError:
            self._pending.pop(mid, None)
            return {"error": "timeout waiting for extension", "method": method, "timeout": timeout}
        if msg.get("ok"):
            return msg.get("value")
        return {"error": msg.get("error", "unknown error from extension"), "method": method}

    # ---------- helpers ----------
    @staticmethod
    async def _safe_send(ws, obj):
        try:
            await ws.send(json.dumps(obj))
        except Exception:
            pass

    @staticmethod
    async def _safe_close(ws, code=1000, reason=""):
        try:
            await ws.close(code=code, reason=reason)
        except Exception:
            pass
