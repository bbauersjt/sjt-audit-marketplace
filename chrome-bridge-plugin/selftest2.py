"""
selftest2.py — prove the daemon/controller election WITHOUT Chrome or Claude.

Starts TWO BridgeHub instances in one process (mimicking the desktop app + the
Cowork runtime both spawning server.py). One should win the bind and become the
daemon; the other becomes a controller. A fake extension connects to the daemon.
Then BOTH hubs' call() must reach that one extension.

    pip install websockets
    python selftest2.py        # prints "SELFTEST2 OK" and exits 0 on success
"""

import asyncio
import json
import threading
import time

from bridge_core import BridgeHub, BRIDGE_HOST, BRIDGE_PORT, BRIDGE_TOKEN

CANNED = {"url": "https://engagement.cchaxcess.com/x",
          "title": "Engagement", "readyState": "complete"}


def start_fake_ext(stop, connected):
    async def run():
        import websockets
        url = f"ws://{BRIDGE_HOST}:{BRIDGE_PORT}/"
        async with websockets.connect(url) as ws:
            await ws.send(json.dumps({"type": "hello", "token": BRIDGE_TOKEN, "ext_version": "selftest2"}))
            w = json.loads(await ws.recv())
            assert w.get("type") == "welcome", w
            connected.set()
            while not stop.is_set():
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=0.2)
                except asyncio.TimeoutError:
                    continue
                msg = json.loads(raw)
                if msg.get("type") == "ping":
                    await ws.send(json.dumps({"type": "pong"}))
                    continue
                mid, method = msg.get("id"), msg.get("method")
                if method == "page_info":
                    await ws.send(json.dumps({"id": mid, "ok": True, "value": CANNED}))
                else:
                    await ws.send(json.dumps({"id": mid, "ok": True, "value": {"echo": method}}))
    asyncio.run(run())


def main():
    A = BridgeHub(); A.start()
    time.sleep(0.4)          # let A win the bind deterministically
    B = BridgeHub(); B.start()
    time.sleep(1.0)

    ra, rb = A.status()["role"], B.status()["role"]
    print("roles:", ra, "/", rb)
    assert {ra, rb} == {"daemon", "controller"}, (A.status(), B.status())

    stop, connected = threading.Event(), threading.Event()
    threading.Thread(target=start_fake_ext, args=(stop, connected), daemon=True).start()
    assert connected.wait(5), "fake extension never connected"
    time.sleep(0.3)

    call_a = A.call("page_info", {"target": "active"})
    call_b = B.call("page_info", {"target": "active"})
    print("daemon-side call :", json.dumps(call_a))
    print("controller call  :", json.dumps(call_b))

    assert call_a == CANNED, call_a
    assert call_b == CANNED, call_b   # proxied through the daemon to the extension

    daemon = A if ra == "daemon" else B
    assert daemon.status()["extension_connected"] is True, daemon.status()
    assert daemon.status()["controllers"] >= 1, daemon.status()

    stop.set()
    print("SELFTEST2 OK  (daemon + controller both reach the one extension)")


if __name__ == "__main__":
    main()
