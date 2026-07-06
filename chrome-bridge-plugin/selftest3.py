"""
selftest3.py — validate the FILE verbs' server half without Chrome.

Starts server.hub, connects a fake extension that mocks download/upload/eval,
then drives the real server.py tool functions and checks the on-disk results:
  - chrome_download   : base64 from the "extension" is decoded and written (binary-exact)
  - chrome_eval+out_path : a big string result is written to disk, not returned inline
  - chrome_upload     : a local file is read, base64'd, and the bytes reach the extension

    pip install websockets
    python selftest3.py        # prints "SELFTEST3 OK" and exits 0 on success
"""

import asyncio
import base64
import json
import os
import tempfile
import threading
import time

import server  # uses server.hub + the real tool functions
from bridge_core import BRIDGE_HOST, BRIDGE_PORT, BRIDGE_TOKEN

KNOWN = bytes([0, 1, 2, 255, 254, 13, 10]) + b"AXCESS-binary"
UPLOAD_BYTES = bytes(range(0, 256))  # full byte range, exercises binary round-trip


async def fake_ext(stop, connected):
    import websockets
    async with websockets.connect(f"ws://{BRIDGE_HOST}:{BRIDGE_PORT}/", max_size=64 * 1024 * 1024) as ws:
        await ws.send(json.dumps({"type": "hello", "token": BRIDGE_TOKEN, "ext_version": "st3"}))
        await ws.recv()  # welcome
        connected.set()
        while not stop.is_set():
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=0.2)
            except asyncio.TimeoutError:
                continue
            m = json.loads(raw)
            mid, method, p = m.get("id"), m.get("method"), m.get("params", {})
            if method == "download":
                await ws.send(json.dumps({"id": mid, "ok": True, "value": {
                    "status": 200, "ok": True, "content_type": "application/octet-stream",
                    "b64": base64.b64encode(KNOWN).decode()}}))
            elif method == "eval":
                await ws.send(json.dumps({"id": mid, "ok": True, "value": {"result": "BIG-DATA-" * 100}}))
            elif method == "upload":
                dec = base64.b64decode(p.get("b64", ""))
                await ws.send(json.dumps({"id": mid, "ok": True, "value": {
                    "status": 200, "ok": True, "body": "ok",
                    "received_bytes": len(dec),
                    "received_ok": dec == UPLOAD_BYTES,
                    "field": p.get("field_name"), "filename": p.get("filename")}}))
            elif method == "network_recent":
                await ws.send(json.dumps({"id": mid, "ok": True, "value": {"requests": [
                    {"url": "https://financialprep-api.cchaxcess.com/v1.0/x", "method": "GET", "ts": 100,
                     "headers": {"Authorization": "Bearer eyJabc", "IDToken": "id123",
                                 "Cookie": "big=stuff", "User-Agent": "x"}},
                    {"url": "https://financialprep-api.cchaxcess.com/v1.0/y", "method": "GET", "ts": 50,
                     "headers": {"User-Agent": "x"}},
                    {"url": "https://firm-api.cchaxcess.com/z", "method": "GET", "ts": 80,
                     "headers": {"Authorization": "Bearer eyJfirm", "Cookie": "c"}}]}}))
            else:
                await ws.send(json.dumps({"id": mid, "ok": False, "error": "unknown"}))


def run_fake(stop, connected):
    asyncio.run(fake_ext(stop, connected))


def main():
    server.hub.start()
    stop, connected = threading.Event(), threading.Event()
    threading.Thread(target=run_fake, args=(stop, connected), daemon=True).start()
    assert connected.wait(5), "fake extension never connected"
    time.sleep(0.3)

    tmp = tempfile.mkdtemp(prefix="bridge_st3_")

    # 1) download -> file (binary-exact)
    dpath = os.path.join(tmp, "sub", "out.bin")  # nested -> exercises makedirs
    dl = server.chrome_download("https://x/y.bin", dpath)
    assert dl.get("path") and os.path.isfile(dl["path"]), dl
    assert open(dl["path"], "rb").read() == KNOWN, "download bytes mismatch"
    assert dl["bytes"] == len(KNOWN), dl

    # 2) eval + out_path -> file (not inline)
    epath = os.path.join(tmp, "big.json")
    ev = server.chrome_eval("(()=>'ignored, mock returns canned')()", out_path=epath)
    assert ev.get("path") == os.path.abspath(epath), ev
    assert open(epath).read() == "BIG-DATA-" * 100, "eval out_path content mismatch"

    # 3) upload: local file -> base64 -> extension receives exact bytes
    upath = os.path.join(tmp, "up.bin")
    with open(upath, "wb") as f:
        f.write(UPLOAD_BYTES)
    up = server.chrome_upload(upath, "https://x/upload", field_name="document", filename="up.bin")
    assert up.get("received_ok") is True, up
    assert up.get("received_bytes") == len(UPLOAD_BYTES), up
    assert up.get("field") == "document", up

    # 4) network_recent: compact (one per host, freshest carrying auth, auth-only headers)
    net = server.chrome_network_recent("cchaxcess", limit=10)
    reqs = net["requests"]
    hosts = sorted(r["host"] for r in reqs)
    assert hosts == ["financialprep-api.cchaxcess.com", "firm-api.cchaxcess.com"], hosts
    fp = [r for r in reqs if r["host"] == "financialprep-api.cchaxcess.com"][0]
    assert fp["ts"] == 100, fp                               # picked the auth-carrying one, not ts=50
    assert "Authorization" in fp["headers"], fp
    assert "Cookie" not in fp["headers"] and "User-Agent" not in fp["headers"], fp  # auth_only filtered

    stop.set()
    print("SELFTEST3 OK")
    print("  download:", json.dumps(dl))
    print("  eval+out_path:", json.dumps(ev))
    print("  upload:", json.dumps(up))


if __name__ == "__main__":
    main()
