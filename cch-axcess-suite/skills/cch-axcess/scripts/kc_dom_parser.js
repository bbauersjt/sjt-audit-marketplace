/* kc_dom_parser.js — DOM-driven fillable-field parser for CCH Knowledge Coach forms.
 *
 * Replaces the snapshot/OCR/diff field-detector. Reads the rendered KC form DOM and
 * returns every fillable field as a structured record whose identity maps 1:1 to the
 * UpdateProperty write target. No images, no OCR.
 *
 * CASCADE NOTE (important): a single parse only sees the CURRENT render. Filling a
 * tailoring question / choice makes KC cascade in new steps & questions that did not
 * exist in the DOM yet. So this parser does NOT remove the iterate-until-stable loop —
 * it makes each iteration structured and the diff a cheap Set comparison instead of an
 * image compare. Drive it with runToStable() (bottom of file).
 *
 * Field `name` convention (the killer feature):
 *     "Collection|objectKey|property||optionCode"
 *   e.g. "ProgramSteps|675EFD7E-...|Assertion||EO"
 *        "ProgramSteps|675EFD7E-...|Risks||RMM-EO"
 *        "ProgramSteps|675EFD7E-...|Comment"
 *        "TailoringQuestions|CASH_TQ_..|Answer"
 *   collection + objectKey + property come straight out of it; the "||optionCode" is the
 *   valid valueKey (no case-guessing → avoids the resetanswer reject).
 *
 * The API collectionKey is ".{AREA}.{collection}" (AREA = CASH/AP/OL/EQUITY/...). AREA is
 * NOT in the DOM name; pass it to parse(area) to get full collectionKeys, or read it once
 * from the GET (result.dataBindingKey) / the ProgramSteps collection path.
 */
(() => {
  const norm = s => (s || '').replace(/\s+/g, ' ').trim();

  // nearest custom-element ancestor tag (kcc-*) — used to classify field kind
  function kccAncestor(el) {
    let p = el;
    for (let i = 0; i < 8 && p; i++) {
      const t = (p.tagName || '').toLowerCase();
      if (t.startsWith('kcc-')) return t;
      p = p.parentElement;
    }
    return null;
  }

  // is this element inside the OVERALL / form-level sign-off (never auto-sign this)
  function isOverallSignoff(el) {
    return !!el.closest('kcc-workpaper-signoff, kcc-workpaper-signoff-group');
  }

  // parse one "Collection|objectKey|property||optionCode" name
  function parseName(name) {
    if (!name || name.indexOf('|') === -1) return null;
    const parts = name.split('|');
    return {
      collection: parts[0] || '',
      objectKey:  parts[1] || '',
      property:   parts[2] || '',
      // names use a double-pipe before the option: "...|Risks||RMM-EO" -> parts[3]===''
      optionCode: parts.length > 4 ? parts.slice(4).join('|') : (parts[3] || '')
    };
  }

  /* parse(area) -> {
   *   fields:   [ fillable field records ],
   *   signoffs: [ per-step sign-off cells with signed/unsigned + objectKey if derivable ],
   *   overallSignoff: { present, signed } | null,
   *   keySet:   Set<string> of stable field identities (for cascade diffing),
   *   diagnostics: [ text shown in kcc-diagnostics-pane ]
   * } */
  function parse(area) {
    const prefix = area ? '.' + area + '.' : '';
    const fields = [];

    // --- 1. named inputs: choices (checkbox/radio) + text/comment cells ---------------
    for (const el of document.querySelectorAll('[name]')) {
      const nm = el.getAttribute('name');
      const pn = parseName(nm);
      if (!pn || !pn.property) continue;

      const tag = el.tagName.toLowerCase();
      const type = (el.type || '').toLowerCase();
      const kcc = kccAncestor(el);
      const rendered = el.offsetParent !== null || (el.getClientRects && el.getClientRects().length > 0);

      let kind, current;
      if (type === 'checkbox' || type === 'radio') {
        kind = (type === 'checkbox') ? 'choice-multi' : 'choice';
        current = el.checked;
      } else if (el.isContentEditable || kcc === 'kcc-richtext') {
        kind = 'text';
        current = norm(el.textContent);
      } else {
        kind = 'other';
        current = el.value != null ? el.value : norm(el.textContent);
      }

      fields.push({
        collection: pn.collection,
        collectionKey: prefix ? prefix + pn.collection : null, // full API key if area given
        objectKey: pn.objectKey,
        property: pn.property,        // e.g. Assertion / Risks / Comment / Answer
        optionCode: pn.optionCode || null, // valid valueKey for choices (no case-guess)
        kind,                          // choice | choice-multi | text | other
        rendered,                      // false => gated/phantom; don't write (would reset)
        filled: kind.startsWith('choice') ? !!current : !!(current && String(current).length),
        currentValue: current,
        domEl: el
      });
    }

    // --- 2. per-step sign-off cells (kcc-signoff) — state only; write target via API ----
    const signoffs = [];
    for (const so of document.querySelectorAll('kcc-signoff')) {
      if (!so.closest('kcc-table-cell')) continue; // step/section signoffs live in table cells
      const txt = norm(so.textContent);
      const signed = !/Sign Off/i.test(txt) || /\b[A-Z]{1,3}\b\s*\d/.test(txt); // initials+date present
      signoffs.push({ signed, overall: isOverallSignoff(so), text: txt.slice(0, 40), domEl: so });
    }

    // --- 3. overall / form-level sign-off (the one to NEVER auto-sign) ------------------
    const og = document.querySelector('kcc-workpaper-signoff-group, kcc-workpaper-signoff');
    const overallSignoff = og ? { present: true, signed: /\b[A-Z]{1,3}\b\s*\d/.test(norm(og.textContent)) } : null;

    // --- 4. diagnostics KC actually shows the user (truer than GET diagnosticCount) -----
    const diagnostics = [...document.querySelectorAll('kcc-diagnostics-pane [class*="diagnostic"], kcc-diagnostics-pane li')]
      .map(e => norm(e.textContent)).filter(Boolean).slice(0, 50);

    // --- 5. stable identity set for cascade diffing -------------------------------------
    const keySet = new Set(fields.map(fieldId));

    return { fields, signoffs, overallSignoff, keySet, diagnostics };
  }

  // stable identity of a field (independent of value) — for detecting cascaded-in fields
  function fieldId(f) {
    return f.collection + '|' + f.objectKey + '|' + f.property + (f.optionCode ? '||' + f.optionCode : '');
  }

  // new field identities present in `after` but not in `before` (cascade detector)
  function diffNew(beforeKeySet, afterParse) {
    return afterParse.fields.filter(f => !beforeKeySet.has(fieldId(f)));
  }

  /* runToStable(fillFn, {area, maxRounds}) — the cascade loop, DOM-driven.
   *   fillFn(newFields, fullParse) : async — your code that fills the given fields
   *      (write via UpdateProperty using f.collectionKey/objectKey/property/optionCode),
   *      then awaits the KC re-render (e.g. small delay or a reload-less refresh).
   *   Returns when a parse adds no new fillable fields (snapshots match) or maxRounds hit.
   * The DOM does NOT bypass the loop: cascaded fields only appear after their trigger is
   * filled, so we re-parse each round and act only on the newly-appeared fields. */
  async function runToStable(fillFn, opts = {}) {
    const { area, maxRounds = 12, settle = () => new Promise(r => setTimeout(r, 1200)) } = opts;
    let prev = new Set();
    const log = [];
    for (let round = 1; round <= maxRounds; round++) {
      const p = parse(area);
      const fresh = [...p.fields].filter(f => !prev.has(fieldId(f)));
      log.push({ round, totalFields: p.fields.length, newThisRound: fresh.length });
      if (round > 1 && fresh.length === 0) return { stable: true, rounds: round, log, final: p };
      await fillFn(fresh.length ? fresh : p.fields, p); // round 1: fill all; later: only new
      await settle(); // let KC cascade the next wave into the DOM
      prev = new Set(p.fields.map(fieldId));
    }
    return { stable: false, rounds: maxRounds, log, final: parse(area) };
  }

  window.kcDom = { parse, fieldId, diffNew, runToStable, parseName, isOverallSignoff };
  return 'kcDom ready';
})();
// <!-- END -->
