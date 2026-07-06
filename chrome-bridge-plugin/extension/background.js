/*
 * Cowork Bridge — MV3 service worker.
 *
 * Dumb, generic transport. Holds ONE outbound WebSocket to the local
 * chrome-bridge MCP server (127.0.0.1) and answers the server's requests by
 * acting on the live browser:
 *   list_tabs / page_info               — read tab state
 *   eval                                 — run JS in the page (the workhorse)
 *   fetch                                — text fetch() in-page (same-origin)
 *   download                             — binary-safe fetch() -> base64 (server writes the file)
 *   upload                               — rebuild a File from base64 -> multipart POST in-page
 *   navigate / open_tab / close_tab      — drive tabs (e.g. KC deep-link token landing)
 *   network_recent                       — recent request headers seen via webRequest (auth capture)
 *
 * Site-specific knowledge lives in the SKILL, not here. This file just relays.
 */

const BRIDGE_PORT = 8765;
// DEV token — must match server.py / bridge_core.py.
const BRIDGE_TOKEN = "cowork-bridge-dev-7f3a9c21";
const WS_URL = `ws://127.0.0.1:${BRIDGE_PORT}/`;

let socket = null;
let connecting = false;
let keepaliveTimer = null;

function log(...a) { console.log("[cowork-bridge]", ...a); }

// Ping every 20s while connected. WebSocket activity resets the MV3
// service-worker idle timer, so the connection stays alive instead of being
// suspended after ~30s.
function startKeepalive() {
  stopKeepalive();
  keepaliveTimer = setInterval(() => send({ type: "ping" }), 20000);
}
function stopKeepalive() {
  if (keepaliveTimer) { clearInterval(keepaliveTimer); keepaliveTimer = null; }
}

function setBadge(ok) {
  try {
    chrome.action.setBadgeText({ text: ok ? "on" : "" });
    chrome.action.setBadgeBackgroundColor({ color: ok ? "#1a7f37" : "#999999" });
  } catch (e) { /* action may be unavailable during early SW boot */ }
}

function send(obj) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(obj));
  }
}

function connect() {
  if (connecting) return;
  if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) return;
  connecting = true;
  try {
    socket = new WebSocket(WS_URL);
  } catch (e) {
    connecting = false;
    return; // alarm keepalive will retry
  }
  socket.onopen = () => {
    connecting = false;
    log("ws open; sending hello");
    send({ type: "hello", token: BRIDGE_TOKEN, ext_version: chrome.runtime.getManifest().version });
    setBadge(true);
    startKeepalive();
  };
  socket.onmessage = (ev) => handleMessage(ev.data);
  socket.onclose = () => {
    connecting = false;
    socket = null;
    stopKeepalive();
    setBadge(false);
    setTimeout(connect, 1500); // quick retry; alarm is the backstop
  };
  socket.onerror = () => { /* onclose follows */ };
}

async function handleMessage(raw) {
  let msg;
  try { msg = JSON.parse(raw); } catch (e) { return; }
  if (msg.type === "welcome") { log("authenticated by server"); return; }
  if (msg.type === "ping") { send({ type: "pong" }); return; }
  if (!msg.method) return;

  const { id, method, params } = msg;
  try {
    const value = await dispatch(method, params || {});
    send({ id, ok: true, value });
  } catch (e) {
    send({ id, ok: false, error: String((e && e.message) || e) });
  }
}

async function dispatch(method, params) {
  switch (method) {
    case "list_tabs":      return await listTabs();
    case "page_info":      return await pageInfo(params);
    case "fetch":          return await pageFetch(params);
    case "eval":           return await pageEval(params);
    case "download":       return await pageDownload(params);
    case "upload":         return await pageUpload(params);
    case "navigate":       return await navigate(params);
    case "open_tab":       return await openTab(params);
    case "close_tab":      return await closeTab(params);
    case "network_recent": return await networkRecent(params);
    case "api_call":       return await apiCall(params);
    default: throw new Error("unknown method: " + method);
  }
}

// Calls a backend API from the SERVICE WORKER's own context (NOT in-page). SW
// fetch is exempt from the page's CSP, so this works on strict-CSP origins like
// knowledgecoach.cchaxcess.com where pageEval/pageFetch are blocked. The host
// must be in host_permissions (*.cchaxcess.com already is) -> also CORS-bypassed,
// so no preflight. Pass the captured bearer/IdToken in params.headers
// (chrome_network_recent), or rely on cookies via credentials:"include".
async function apiCall(params) {
  const url = params.url;
  const method = params.method || "GET";
  const headers = Object.assign({}, params.headers || {});
  const body = (params.body ?? null);
  const init = { method, headers, credentials: "include" };
  if (body !== null && method !== "GET" && method !== "HEAD") {
    init.body = (typeof body === "string") ? body : JSON.stringify(body);
  }
  try {
    const r = await fetch(url, init);
    const text = await r.text();
    const h = {}; r.headers.forEach((v, k) => { h[k] = v; });
    return { status: r.status, ok: r.ok, url: r.url, headers: h, body: text };
  } catch (e) {
    return { error: String((e && e.message) || e) };
  }
}

async function resolveTabId(target) {
  if (typeof target === "number") return target;
  // tab ids may arrive as numeric strings over the MCP int|str union
  if (typeof target === "string" && /^\d+$/.test(target.trim())) return parseInt(target, 10);
  // "active" (or anything else) -> active tab of the last focused window
  let tabs = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
  if (tabs && tabs[0]) return tabs[0].id;
  tabs = await chrome.tabs.query({ active: true });
  if (tabs && tabs[0]) return tabs[0].id;
  throw new Error("no active tab found");
}

async function listTabs() {
  const tabs = await chrome.tabs.query({});
  return tabs.map((t) => ({
    id: t.id, url: t.url, title: t.title, active: t.active, windowId: t.windowId
  }));
}

async function pageInfo(params) {
  const tabId = await resolveTabId(params.target);
  const [res] = await chrome.scripting.executeScript({
    target: { tabId },
    world: "MAIN",
    func: () => ({ url: location.href, title: document.title, readyState: document.readyState })
  });
  return res.result;
}

// Runs INSIDE the page so cookies / same-origin / the app's auth context apply.
async function pageFetch(params) {
  const tabId = await resolveTabId(params.target);
  const [res] = await chrome.scripting.executeScript({
    target: { tabId },
    world: "MAIN",
    args: [params.url, params.method || "GET", params.headers || {}, (params.body ?? null)],
    func: async (url, method, headers, body) => {
      try {
        const init = { method, headers, credentials: "include" };
        if (body !== null && method !== "GET" && method !== "HEAD") {
          init.body = (typeof body === "string") ? body : JSON.stringify(body);
        }
        const r = await fetch(url, init);
        const text = await r.text();
        const h = {}; r.headers.forEach((v, k) => { h[k] = v; });
        return { status: r.status, ok: r.ok, url: r.url, headers: h, body: text };
      } catch (e) {
        return { error: String((e && e.message) || e) };
      }
    }
  });
  return res.result;
}

// Best-effort arbitrary JS. MAIN world is subject to the PAGE's CSP; Axcess
// allows eval, so the skill's XHR builders run fine here.
async function pageEval(params) {
  const tabId = await resolveTabId(params.target);
  const world = (params.world === "ISOLATED") ? "ISOLATED" : "MAIN";
  const [res] = await chrome.scripting.executeScript({
    target: { tabId },
    world,
    args: [String(params.code || "")],
    func: async (code) => {
      try {
        const out = await (async () => eval(code))();
        return { result: (out && typeof out === "object") ? JSON.parse(JSON.stringify(out)) : out };
      } catch (e) {
        return { error: String((e && e.message) || e) };
      }
    }
  });
  return res.result;
}

// Binary-safe download: fetch in-page, return base64; the SERVER writes the file.
async function pageDownload(params) {
  const tabId = await resolveTabId(params.target);
  const [res] = await chrome.scripting.executeScript({
    target: { tabId },
    world: "MAIN",
    args: [params.url, params.method || "GET", params.headers || {}, (params.body ?? null)],
    func: async (url, method, headers, body) => {
      try {
        const init = { method, headers, credentials: "include" };
        if (body !== null && method !== "GET" && method !== "HEAD") {
          init.body = (typeof body === "string") ? body : JSON.stringify(body);
        }
        const r = await fetch(url, init);
        const buf = await r.arrayBuffer();
        const bytes = new Uint8Array(buf);
        let bin = "";
        const CH = 0x8000;
        for (let i = 0; i < bytes.length; i += CH) {
          bin += String.fromCharCode.apply(null, bytes.subarray(i, i + CH));
        }
        return { status: r.status, ok: r.ok, content_type: r.headers.get("content-type"), b64: btoa(bin) };
      } catch (e) {
        return { error: String((e && e.message) || e) };
      }
    }
  });
  return res.result;
}

// Rebuild a File from base64 and POST it as multipart/form-data, in-page.
async function pageUpload(params) {
  const tabId = await resolveTabId(params.target);
  const [res] = await chrome.scripting.executeScript({
    target: { tabId },
    world: "MAIN",
    args: [params.url, params.field_name || "file", params.filename || "upload.bin",
           params.b64 || "", params.fields || {}, params.headers || {}],
    func: async (url, field, filename, b64, fields, headers) => {
      try {
        const bin = atob(b64);
        const bytes = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
        const file = new File([bytes], filename);
        const fd = new FormData();
        fd.append(field, file, filename);
        for (const k in fields) fd.append(k, fields[k]);
        // never set Content-Type by hand — the browser adds the multipart boundary
        const h = {};
        for (const k in headers) { if (k.toLowerCase() !== "content-type") h[k] = headers[k]; }
        const r = await fetch(url, { method: "POST", body: fd, headers: h, credentials: "include" });
        const t = await r.text();
        return { status: r.status, ok: r.ok, body: t };
      } catch (e) {
        return { error: String((e && e.message) || e) };
      }
    }
  });
  return res.result;
}

async function navigate(params) {
  const tabId = await resolveTabId(params.target);
  await chrome.tabs.update(tabId, { url: params.url });
  await waitForComplete(tabId, 60000);
  const t = await chrome.tabs.get(tabId);
  return { id: tabId, url: t.url, title: t.title, status: t.status };
}

async function openTab(params) {
  const tab = await chrome.tabs.create({ url: params.url, active: !!params.active });
  await waitForComplete(tab.id, 60000);
  const t = await chrome.tabs.get(tab.id);
  return { id: tab.id, url: t.url, title: t.title };
}

async function closeTab(params) {
  await chrome.tabs.remove(params.tab_id);
  return { closed: params.tab_id };
}

// Resolve when the tab finishes loading the REAL landing page — skipping SSO
// redirect hops (an /authenticate?code=... bounce reports 'complete' before the
// app lands). Falls back to resolving at the timeout.
function isRedirectHop(url) {
  return /\/authenticate\b/.test(url || "") || /[?&]code=/.test(url || "");
}
function waitForComplete(tabId, timeoutMs) {
  return new Promise((resolve) => {
    let done = false;
    const finish = () => {
      if (done) return;
      done = true;
      chrome.tabs.onUpdated.removeListener(listener);
      resolve();
    };
    const check = () => {
      chrome.tabs.get(tabId).then((t) => {
        if (t && t.status === "complete" && !isRedirectHop(t.url)) finish();
      }).catch(() => {});
    };
    const listener = (id, info) => { if (id === tabId && info.status === "complete") check(); };
    chrome.tabs.onUpdated.addListener(listener);
    setTimeout(check, 400);
    setTimeout(finish, timeoutMs); // hard cap
  });
}

async function networkRecent(params) {
  const f = params.host_filter || "cchaxcess";
  const lim = params.limit || 20;
  const out = netBuffer.filter((e) => (e.url || "").indexOf(f) >= 0).slice(-lim);
  return { requests: out };
}

// ---- webRequest header capture (ring buffer) -------------------------------
const netBuffer = [];
const NET_MAX = 200;
try {
  chrome.webRequest.onSendHeaders.addListener(
    (details) => {
      const h = {};
      (details.requestHeaders || []).forEach((x) => { h[x.name] = x.value; });
      netBuffer.push({ url: details.url, method: details.method, ts: Date.now(), headers: h });
      if (netBuffer.length > NET_MAX) netBuffer.shift();
    },
    { urls: ["https://*.cchaxcess.com/*", "https://*.suralink.com/*"] },
    ["requestHeaders", "extraHeaders"]
  );
} catch (e) { /* webRequest unavailable / permission missing */ }

// ---- lifecycle / keepalive -------------------------------------------------
chrome.runtime.onInstalled.addListener(() => connect());
chrome.runtime.onStartup.addListener(() => connect());
chrome.alarms.create("bridge-keepalive", { periodInMinutes: 0.5 });
chrome.alarms.onAlarm.addListener((a) => {
  if (a.name !== "bridge-keepalive") return;
  if (!socket || socket.readyState !== WebSocket.OPEN) connect();
  else send({ type: "ping" });
});

connect(); // also connect when the SW first spins up
