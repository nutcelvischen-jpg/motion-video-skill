/* motion-video-skill — shared core (loaded by both templates)
 * Provides: language / timeline / META loading, seeded random, subtitles, font waiting, ?play preview, ?t= freeze frame.
 * Each template's runtime.js builds on window.MV.
 */
(function () {
  const qs = new URLSearchParams(location.search);
  const LANG = window.LANG || qs.get("lang") || (window.META && window.META.langs && window.META.langs[0]) || "zh";
  const TL = (window.TIMELINES && window.TIMELINES[LANG]);
  if (!TL) {
    document.body.innerHTML = `<pre style="font:28px monospace;padding:40px;color:#c00">No timeline for ${LANG}.\nRun first: python scripts/render.py &lt;video folder&gt; --preview</pre>`;
    throw new Error("no timeline for " + LANG);
  }
  const META = Object.assign({}, (window.META && window.META.common) || {}, (window.META && window.META[LANG]) || {});
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => Array.from(document.querySelectorAll(s));
  const CJK = /^(zh|ja|ko)/.test(LANG);
  document.body.classList.add("lang-" + LANG);
  document.documentElement.lang = LANG === "zh" ? "zh-Hant-TW" : LANG;

  /* Seeded random: every frame must be identical on every render */
  function rng(seed) {
    return function () {
      seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /* Subtitles: highlight keywords; allow CJK line breaks after punctuation */
  const HL = (META.hl || []).slice().sort((a, b) => b.length - a.length);
  function fmtSub(s) {
    const marks = [];
    HL.forEach((w) => { let i = s.indexOf(w); while (i >= 0) { marks.push([i, i + w.length]); i = s.indexOf(w, i + w.length); } });
    marks.sort((a, b) => a[0] - b[0]);
    let out = "", p = 0;
    for (const [a, b] of marks) { if (a < p) continue; out += s.slice(p, a) + "<b>" + s.slice(a, b) + "</b>"; p = b; }
    out += s.slice(p);
    return CJK ? out.replace(/([，、：；。！？])/g, "$1<wbr>") : out;
  }
  let lastSub = null;
  function subtitle(t, box) {
    let cur = null, talking = false;
    for (const sc of TL.scenes) for (const ln of sc.lines) {
      if (t >= ln.start - 0.05 && t < ln.end + 0.15) cur = ln;
      if (t >= ln.start && t < ln.end - 0.08) talking = true;
    }
    if (cur !== lastSub) { lastSub = cur; if (cur) box.innerHTML = fmtSub(cur.sub || cur.text); }
    box.style.opacity = cur ? 1 : 0;
    return talking;
  }

  /* Wait for fonts and images before rendering */
  function ready(seek, families) {
    const text = TL.scenes.map((s) => s.lines.map((l) => l.sub || l.text).join("")).join("") +
      JSON.stringify(META) + document.body.innerText + "0123456789%✓？！";
    const loads = [];
    families.forEach(([fam, weights]) => weights.forEach((w) => loads.push(document.fonts.load(`${w} 40px "${fam}"`, text).catch(() => []))));
    const imgs = () => Promise.all($$("img").map((i) => (i.complete ? 1 : new Promise((r) => { i.onload = i.onerror = r; }))));
    window.__ready = Promise.all(loads).then(() => document.fonts.ready).then(imgs).then(() => { seek(0); return true; });
    window.__total = TL.total;
    if (qs.has("play")) {
      window.__ready.then(() => { const t0 = performance.now(); (function loop() { seek(((performance.now() - t0) / 1000) % TL.total); requestAnimationFrame(loop); })(); });
    } else if (qs.has("t")) {
      window.__ready.then(() => seek(parseFloat(qs.get("t"))));
    }
  }

  /* Fill elements with data-t="key" from EPISODE.strings[LANG][key] */
  function fillStrings(EP) {
    const T = Object.assign({}, (EP.strings || {})[LANG]);
    $$("[data-t]").forEach((el) => { const k = el.dataset.t; if (T[k] !== undefined) el.innerHTML = T[k]; });
    return T;
  }

  /* Shared GSAP timeline + timing helpers */
  function timeline() {
    const m = gsap.timeline({ paused: true });
    const S = (i) => TL.scenes[i];
    const L = (i, j) => TL.scenes[i].lines[j].start;
    const LE = (i, j) => TL.scenes[i].lines[j].end;
    const SE = (i) => S(i).start + S(i).dur;
    const LM = (i, j, k = 0.5) => L(i, j) + (LE(i, j) - L(i, j)) * k; // a fraction k of the way through a line
    return { m, S, L, LE, SE, LM };
  }

  window.MV = { LANG, TL, META, $, $$, rng, subtitle, ready, fillStrings, timeline, CJK };
})();
