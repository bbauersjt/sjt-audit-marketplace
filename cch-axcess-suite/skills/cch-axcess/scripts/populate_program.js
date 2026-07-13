// populate_program.js — reusable AUD-8xx program populator (Knowledge Coach).
//
// Drives the full "build out a program" pipeline for ONE AUD-8xx workpaper:
//   first-N tailoring questions = Yes  ->  bring in non-N/A steps  ->  link risks
//   (RMM matching each parent's assertions + Management Override)  ->  gibberish
//   Comment on every non-heading step  ->  preparer SignOff on every non-heading step.
//
// USAGE (paste this whole file via javascript_tool to define window.kcPop, then):
//   const cfg = {binder:'<engGuid>', wp:'<workpaperId>', area:'CASH'|'AR'|'PPE'|'AP'|'EQUITY'|...,
//                tqYesCount:4, gibberish:'zzz gibberish ', initials:'XX'};
//   1) await window.kcPop.tqAndVisible(cfg)   // answers TQs + sets the visible step-set (server-side)
//   2) RELOAD the tab, then RE-PASTE this file   // <-- REQUIRED: see gotcha below
//   3) await window.kcPop.build(cfg)          // reads form + rendered DOM -> ordered payload list
//   4) loop:  v = await kcPop.verify();  await kcPop.repair(v.badIdx.slice(0,35));  until v.bad===0
//   (verify+repair is preferred over fire() because the 45s CDP renderer cap kills
//    long single calls; repairing ~35 not-done payloads per call stays under it and
//    is idempotent, so re-runs and dropped writes self-heal.)
//
// Behavior notes:
//  - SignOff needs BOTH value AND valueKey = initials. valueKey-only is silently
//    ignored (state stays 0).
//  - Tight back-to-back UpdateProperty writes to one form silently drop (HTTP 200,
//    no persist). The old ~300ms floor is WRONG — ~60% still
//    dropped at ~350ms, and ~30-50% drop even at 1-2s gaps. Pace ~1200ms and rely on
//    the verify+repair loop (NOT pacing) for persistence; verify-by-read is mandatory
//    (field-conventions.md section 5 item 3a).
//  - GOTCHA: an API UpdateProgramStep does NOT make the Angular UI re-render the
//    newly-visible steps, so the Risks-checkbox / Comment-box DOM nodes aren't there
//    yet. You MUST reload the tab between tqAndVisible() and build() so the rendered
//    DOM reflects the visible step-set. (build reads risk codes + heading flags from
//    that DOM — they are NOT in the /api/Workpaper GET.)
//  - Risks options + heading flags come from the DOM: checkbox names
//    `ProgramSteps|{key}|Risks||{code}`, response boxes `ProgramSteps|{key}|Comment`.
//    A visible step with no Comment box = heading -> skipped for Comment + SignOff.
//  - Risks property = full-state replacement, value/valueKey semicolon-joined WITH a
//    trailing semi. Unknown code 500s ("Index was outside the bounds"), so build only
//    uses codes actually present in the DOM (per-area: some areas have no assertion
//    RMMs at all, only the entity-level Management Override = FINANCIALLEVELRISKS-N).
(() => {
  const KC = 'https://knowledgecoach.cchaxcess.com';
  const H = () => ({ Authorization: 'Bearer ' + localStorage.getItem('kc.accessToken'), IdToken: localStorage.getItem('kc.idToken'), Accept: 'application/json', 'Content-Type': 'application/json' });
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const gp = (o, k) => (o.renderProperties || []).find(x => x.key === k) || {};
  const applicable = o => gp(o, 'IsApplicable').value !== 'False';
  async function readForm(b, wp) { const r = await fetch(`${KC}/api/Workpaper/${b}/${wp}`, { headers: H() }); if (r.status !== 200) throw new Error('read ' + r.status); return (await r.json()).result; }
  const ps = (f, a) => JSON.parse(f.collections).find(c => c.path === `.${a}.ProgramSteps`);

  // present risk codes + per-code display label, read from the rendered DOM
  function domRisk() {
    const label = {}, codes = new Set();
    [...document.querySelectorAll('input')].forEach(inp => {
      const n = inp.getAttribute('name') || ''; const m = n.match(/\|Risks\|\|(.+)$/); if (!m) return;
      const code = m[1]; codes.add(code);
      if (!label[code]) { let t = ''; if (inp.id) { const l = document.querySelector('label[for="' + CSS.escape(inp.id) + '"]'); if (l) t = l.textContent.trim(); } if (!t) { const p = inp.closest('label') || inp.parentElement; if (p) t = (p.textContent || '').trim(); } label[code] = t.slice(0, 80); }
    });
    return { codes: [...codes], label };
  }
  // step keys with a rendered response box (non-heading)
  function domCommentKeys() { const s = new Set(); [...document.querySelectorAll('[name]')].forEach(e => { const p = (e.getAttribute('name') || '').split('|'); if (p[0] === 'ProgramSteps' && p[2] === 'Comment') s.add(p[1]); }); return s; }

  window.kcPop = {
    cfg: null, payloads: null, meta: null,

    // Phase 1 — answer first-N visible TQs = Yes, then set the applicable visible-set. (Server-side.)
    async tqAndVisible(cfg) {
      cfg = Object.assign({ tqYesCount: 4, gibberish: 'zzz gibberish ', initials: 'XX' }, cfg); this.cfg = cfg;
      let form = await readForm(cfg.binder, cfg.wp);
      const tqCol = JSON.parse(form.collections).find(c => c.path === `.${cfg.area}.TailoringQuestions`);
      const tqFirst = (tqCol ? tqCol.objectList.filter(x => x.visible) : []).slice(0, cfg.tqYesCount);
      for (const row of tqFirst) { await fetch(`${KC}/api/Workpaper/UpdateProperty/${cfg.binder}/${cfg.wp}`, { method: 'POST', headers: H(), body: JSON.stringify({ collectionKey: `.${cfg.area}.TailoringQuestions`, objectKey: row.key, propertyKey: 'Answer', value: 'Yes', valueKey: 'YES', dataEntryExpression: '', dataEntryExpressionContextObjectKey: '' }) }); await sleep(320); }
      await sleep(1000); form = await readForm(cfg.binder, cfg.wp); const coll = ps(form, cfg.area);
      const vis = []; for (const p of coll.objectList) { if (!applicable(p)) continue; vis.push(p.key); for (const ch of (p.childObjectList || [])) if (applicable(ch)) vis.push(ch.key); }
      await fetch(`${KC}/api/Workpaper/UpdateProgramStep`, { method: 'POST', headers: H(), body: JSON.stringify({ binderId: cfg.binder, workpaperId: cfg.wp, value: vis.join(';') }) });
      return { tqAnswered: tqFirst.length, visibleSent: vis.length, note: 'RELOAD the tab + re-paste this file, then call build().' };
    },

    // Phase 2 — build the ordered payload list from form + rendered DOM. (Run AFTER reload.)
    async build(cfg) {
      cfg = cfg || this.cfg; cfg = Object.assign({ tqYesCount: 4, gibberish: 'zzz gibberish ', initials: 'XX' }, cfg); this.cfg = cfg;
      const form = await readForm(cfg.binder, cfg.wp); const coll = ps(form, cfg.area);
      const risk = domRisk(); const presentRMM = new Set(risk.codes.filter(c => /^RMM-/.test(c)));
      const mgmt = risk.codes.find(c => /^FINANCIALLEVELRISKS-/.test(c) && /override/i.test(risk.label[c] || '')) || risk.codes.find(c => /^FINANCIALLEVELRISKS-/.test(c));
      const commentKeys = domCommentKeys(); const flat = [], parents = [];
      for (const p of coll.objectList) { if (!applicable(p)) continue; parents.push(p); flat.push(p); for (const ch of (p.childObjectList || [])) if (applicable(ch)) flat.push(ch); }
      const payloads = [];
      for (const p of parents) { const a = (gp(p, 'Assertion').valueKey || ''); const codes = a.split(';').filter(s => presentRMM.has('RMM-' + s)).map(s => 'RMM-' + s); if (mgmt) codes.push(mgmt); if (!codes.length) continue; payloads.push({ k: 'Risks', objectKey: p.key, propertyKey: 'Risks', value: codes.map(c => risk.label[c] || c).join(';') + ';', valueKey: codes.join(';') + ';' }); }
      for (const row of flat) { if (!commentKeys.has(row.key)) continue; payloads.push({ k: 'Comment', objectKey: row.key, propertyKey: 'Comment', value: cfg.gibberish + row.key.slice(0, 5), valueKey: '' }); payloads.push({ k: 'SignOff', objectKey: row.key, propertyKey: 'SignOff', value: cfg.initials, valueKey: cfg.initials }); }
      this.payloads = payloads; this.meta = { area: cfg.area, parents: parents.length, steps: flat.length, headings: flat.length - commentKeys.size, presentRMM: [...presentRMM], mgmt, payloadCount: payloads.length };
      return this.meta;
    },

    // Optional forward-fire (offset/limit). Prefer verify+repair under the 45s CDP cap.
    async fire(offset = 0, limit = 60, gap = 320) {
      const c = this.cfg, list = this.payloads.slice(offset, offset + limit);
      for (const p of list) { await fetch(`${KC}/api/Workpaper/UpdateProperty/${c.binder}/${c.wp}`, { method: 'POST', headers: H(), body: JSON.stringify({ collectionKey: `.${c.area}.ProgramSteps`, objectKey: p.objectKey, propertyKey: p.propertyKey, value: p.value, valueKey: p.valueKey, dataEntryExpression: '', dataEntryExpressionContextObjectKey: '' }) }); await sleep(gap); }
      return { fired: list.length, nextOffset: offset + list.length, total: this.payloads.length, done: offset + list.length >= this.payloads.length };
    },

    // re-read and return payload indices that didn't stick (drops / not-yet-fired)
    async verify() {
      const c = this.cfg; const form = await readForm(c.binder, c.wp); const coll = ps(form, c.area);
      const byKey = {}; for (const p of coll.objectList) { byKey[p.key] = p; for (const ch of (p.childObjectList || [])) byKey[ch.key] = ch; }
      const bad = [];
      this.payloads.forEach((p, i) => { const row = byKey[p.objectKey]; if (!row) { bad.push(i); return; } const prop = gp(row, p.propertyKey); let ok;
        if (p.k === 'Risks') ok = prop.state === 3 && (prop.valueKey || '').indexOf((p.valueKey || '').split(';')[0]) === 0;
        else if (p.k === 'Comment') ok = prop.state === 3 && (prop.value || '') !== '';
        else ok = prop.state === 3 && prop.valueKey === p.value; // SignOff
        if (!ok) bad.push(i); });
      return { total: this.payloads.length, bad: bad.length, badIdx: bad.slice(0, 200) };
    },

    // fire a chunk of not-done payloads (idempotent). ~35 per call stays under the 45s cap.
    async repair(badIdx, gap = 320) {
      const c = this.cfg;
      for (const i of badIdx) { const p = this.payloads[i]; await fetch(`${KC}/api/Workpaper/UpdateProperty/${c.binder}/${c.wp}`, { method: 'POST', headers: H(), body: JSON.stringify({ collectionKey: `.${c.area}.ProgramSteps`, objectKey: p.objectKey, propertyKey: p.propertyKey, value: p.value, valueKey: p.valueKey, dataEntryExpression: '', dataEntryExpressionContextObjectKey: '' }) }); await sleep(gap); }
      return { repaired: badIdx.length };
    }
  };
  return 'kcPop ready';
})()
// <!-- END -->
