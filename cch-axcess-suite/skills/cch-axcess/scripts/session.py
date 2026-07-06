"""Cold-start session discovery for CCH Axcess.

Collapses the old multi-step "figure out the session" fumble (find the GUID,
find a token, find the right tab) into ONE browser call that returns a small,
DLP-filter-safe object. No token blobs leave the browser — only structural
facts (ids, a single GUID, booleans).

The SESSION TRIPLE every KC/engagement write needs:
  1. engagementGuid  — canonical GUID (KC API + workbench TB create)
  2. live KC tokens  — localStorage kc.accessToken + kc.idToken (writes)
  3. a KC-origin tab  — knowledgecoach.cchaxcess.com, to fire writes from

discover_session_js() runs in whatever CCH tab is active and reports which of
the three you already have and how to get the rest. See
references/runbooks/session-bootstrap.md for the procedure that uses it.

These functions return JavaScript strings for
mcp__Claude_in_Chrome__javascript_tool. Python never touches a token.
"""

# Run in the active CCH tab (engagement OR knowledgecoach). Returns a small JSON
# object that passes the Cowork DLP filter (no tokens, just facts + one GUID).
DISCOVER_SESSION_JS = r"""
(() => {
  const href = location.href;
  const host = /knowledgecoach\.cchaxcess\.com/.test(href) ? 'knowledgecoach'
             : /engagement\.cchaxcess\.com/.test(href)     ? 'engagement'
             : 'other';
  const GUID = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i;

  // ints from the engagement URL: /engagement/{clientId}/.../engagementview/{engagementId}
  const ints = (href.match(/\/(\d{3,})(?=\/|$)/g) || []).map(s => s.replace('/', ''));
  const clientId = ints[0] || null;
  const engagementId = ints[1] || null;

  // KC tokens (booleans only — never return the token strings)
  const hasKcTokens = !!(localStorage.getItem('kc.accessToken') && localStorage.getItem('kc.idToken'));

  // engagementGuid, cheapest source first
  let engagementGuid = null, guidSource = null;
  if (host === 'knowledgecoach') {
    const m = href.match(/\/binder\/(.+?)(?:\/|$)/i);
    if (m && GUID.test(m[1])) { engagementGuid = m[1]; guidSource = 'kc-url'; }
  }
  if (!engagementGuid && Array.isArray(window.__cch_capture)) {
    for (const c of window.__cch_capture) {
      const m = (c.url || '').match(/knowledgecoach\.cchaxcess\.com\/api\/engagement\/(.+?)(?:[\/?]|$)/i);
      if (m && GUID.test(m[1])) { engagementGuid = m[1]; guidSource = 'capture'; break; }
    }
  }

  const needs = [];
  if (!engagementGuid) needs.push('engagementGuid: click into a KC-form folder (e.g. 0500 Risk Assessment) once to fire GET /api/engagement/{guid}, or reuse an open KC tab');
  if (!hasKcTokens)    needs.push('kcTokens: open/reuse a knowledgecoach.cchaxcess.com tab so kc.accessToken/kc.idToken land in localStorage');
  if (host !== 'knowledgecoach') needs.push('kcTab: writes must fire from a knowledgecoach.cchaxcess.com tab');

  return JSON.stringify({
    host, clientId, engagementId, engagementGuid, guidSource,
    hasKcTokens, kcTabUrl: host === 'knowledgecoach' ? href : null,
    ready_to_write: !!(engagementGuid && hasKcTokens && host === 'knowledgecoach'),
    needs
  });
})()
"""


def discover_session_js() -> str:
    """JS for mcp__Claude_in_Chrome__javascript_tool. Run in the active CCH tab.

    Returns a filter-safe JSON object: {host, clientId, engagementId,
    engagementGuid, guidSource, hasKcTokens, kcTabUrl, ready_to_write, needs[]}.
    Parse it and follow `needs` until `ready_to_write` is true.
    """
    return DISCOVER_SESSION_JS



# --- Browser + tab auto-reuse (kills the per-chat tab whack-a-mole) ---------
#
# Reality of the Chrome tools: there is ONE MCP tab group per connected browser;
# it is not nameable, and tabs_context_mcp returns only tab IDs (no URLs). So
# "find the right tab" = list the group's tab IDs, probe each for a cchaxcess.com
# host, and reuse it instead of spawning a new tab/group. To stop two chats from
# fighting over the same tab during UI actions, each chat claims a tab by stamping
# window.__cch_owner; a probe reports another chat's claim so we can skip it.
# See references/runbooks/session-bootstrap.md for the procedure that uses these.

# A claim older than this many seconds is treated as abandoned (the owning chat
# refreshes ts on each in-tab call, so a live chat's claim stays well under it).
CLAIM_STALE_SEC = 600

# Probe ONE tab (run via javascript_tool with that tab's tabId). Filter-safe:
# only structural facts leave the tab — no URLs, no tokens.
TAB_PROBE_JS = r"""
(() => {
  const h = location.host || '';
  const isCch = /\.cchaxcess\.com$/i.test(h);
  const o = (window.__cch_owner && typeof window.__cch_owner === 'object') ? window.__cch_owner : null;
  return JSON.stringify({
    isCch,
    kind: /knowledgecoach/.test(h) ? 'kc'
        : /^engagement\./.test(h)  ? 'engagement'
        : (isCch ? 'cch-other' : 'non-cch'),
    ownerToken: o ? (o.token || null) : null,
    ownerAgeSec: (o && o.ts) ? Math.round((Date.now() - o.ts) / 1000) : null
  });
})()
"""


def tab_probe_js() -> str:
    """JS for javascript_tool(tabId). Returns JSON
    {isCch, kind, ownerToken, ownerAgeSec}. A tab is reusable when isCch is true
    and (ownerToken is null, or ownerToken == yours, or ownerAgeSec > CLAIM_STALE_SEC)."""
    return TAB_PROBE_JS


def claim_tab_js(token: str) -> str:
    """JS for javascript_tool(tabId). Stamp/refresh THIS chat's ownership of the
    tab. Mint `token` once per chat (any short string) and reuse it all session;
    call this on claim and cheaply on each in-tab action to keep the claim live."""
    t = (token or "").replace("\\", "").replace('"', "")
    return '(() => { window.__cch_owner = {token:"%s", ts: Date.now()}; return "claimed:%s"; })()' % (t, t)
# <!-- END -->
