"""
selftest.py — prove the SERVER half of the loop WITHOUT Chrome or Claude.

Starts the BridgeHub (its localhost WebSocket server), connects a FAKE
extension that returns canned answers, then drives the hub the way the MCP
tools do and checks every round-trip (success, error, and timeout paths).

    pip install websockets
    python selftest.py        # prints "SELFTEST OK" and exits 0 on success
"""

import asyncio
import json
import threading
import time

from bridge_core import BridgeHub, BRIDGE_HOST, BRIDGE_PORT, BRIDGE_TOKEN

CANNED_PAGE = {"url": "https://engagement.cchaxcess.com/x",
               "title": "Engagement", "readyState": "complete"}


async def fake_extension(stop):
    import websockets
    url = f"ws://{BRIDGE_HOST}:{BRIDGE_PORT}/"
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({"type": "hello", "token": BRIDGE_TOKEN,
                                  "ext_version": "selftest"}))
        welcome = json.loads(await ws.recv())
        assert welcome.get("type") == "welcome", welcome
        while not stop.is_set():
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=0.2)
            except asyncio.TimeoutError:
                continue
            msg = json.loads(raw)
            mid, method, params = msg.get("id"), msg.get("method"), msg.get("params", {})
            if method == "page_info":
                await ws.send(json.dumps({"id": mid, "ok": True, "value": CANNED_PAGE}))
            elif method == "list_tabs":
                await ws.send(json.dumps({"id": mid, "ok": True, "value": [
                    {"id": 1, "url": CANNED_PAGE["url"], "title": "Engagement",
                     "active": True, "windowId": 1}]}))
            elif method == "fetch":
                await ws.send(json.dumps({"id": mid, "ok": True, "value": {
                    "status": 200, "ok": True, "url": params.get("url"),
                    "headers": {"content-type": "application/json"},
                    "body": '{"hello":"axcess"}'}}))
            elif method == "boom":
                await ws.send(json.dumps({"id": mid, "ok": False, "error": "simulated failure"}))
            elif method == "slow":
                pass  # never respond -> exercises the timeout path
            else:
                await ws.send(json.dumps({"id": mid, "ok": False, "error": "unknown"}))


def run_fake(stop):
    asyncio.run(fake_extension(stop))


def main():
    hub = BridgeHub()
    hub.start()
    assert hub.status()["server_ready"], hub.status()

    stop = threading.Event()
    threading.Thread(target=run_fake, args=(stop,), daemon=True).start()

    for _ in range(50):
        if hub.status()["extension_connected"]:
            break
        time.sleep(0.1)
    assert hub.status()["extension_connected"], "fake extension never connected"

    results = {
        "status": hub.status(),
        "list_tabs": hub.call("list_tabs"),
        "page_info": hub.call("page_info", {"target": "active"}),
        "fetch": hub.call("fetch", {"url": "https://engagement.cchaxcess.com/api/ping", "method": "GET"}),
        "error_path": hub.call("boom", {}),
        "timeout_path": hub.call("slow", {}, timeout=1.0),
    }

    assert results["page_info"] == CANNED_PAGE, results["page_info"]
    assert results["fetch"]["status"] == 200 and "axcess" in results["fetch"]["body"], results["fetch"]
    assert isinstance(results["list_tabs"], list) and results["list_tabs"][0]["id"] == 1, results["list_tabs"]
    assert results["error_path"].get("error") == "simulated failure", results["error_path"]
    assert "timeout" in results["timeout_path"].get("error", ""), results["timeout_path"]

    stop.set()
    print("SELFTEST OK")
    for k, v in results.items():
        print(f"  {k}: {json.dumps(v)[:160]}")


if __name__ == "__main__":
    main()
