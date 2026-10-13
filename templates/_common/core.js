/* motion-video-skill — 共用核心（兩種版型都會載入）
 * 提供：語言/時間軸/META 讀取、亂數、字幕、字型等待、?play 預覽、?t= 定格。
 * 版型 runtime 會呼叫 MV.boot({...})。
 */
(function () {
  const qs = new URLSearchParams(location.search);
  const LANG = window.LANG || qs.get("lang") || (window.META && window.META.langs && window.META.langs[0]) || "zh";
  const TL = (window.TIMELINES && window.TIMELINES[LANG]);
  if (!TL) {
    document.body.innerHTML = `<pre style="font:28px monospace;padding:40px;color:#c00">找不到 ${LANG} 的時間軸。\n請先執行：python scripts/render.py &lt;影片資料夾&gt; --preview</pre>`;
    throw new Error("no timeline for " + LANG);
  }
  const META = Object.assign({}, (window.META && window.META.common) || {}, (window.META && window.META[LANG]) || {});
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => Array.from(document.querySelectorAll(s));
  const CJK = /^(zh|ja|ko)/.test(LANG);
  document.body.classList.add("lang-" + LANG);
  document.documentElement.lang = LANG === "zh" ? "zh-Hant-TW" : LANG;

  /* 可重現的亂數（每一格畫面都要一樣，渲染才會穩定） */
  function rng(seed) {
    return function () {
      seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /* 字幕：highlight 關鍵字、中文在標點後允許換行 */
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

  /* 等字型與圖片都載入完，再允許渲染 */
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

  /* 把 data-t="key" 的元素填上 EPISODE.strings[LANG][key] */
  function fillStrings(EP) {
    const T = Object.assign({}, (EP.strings || {})[LANG]);
    $$("[data-t]").forEach((el) => { const k = el.dataset.t; if (T[k] !== undefined) el.innerHTML = T[k]; });
    return T;
  }

  /* 共用 GSAP 時間軸 + 常用時間函式 */
  function timeline() {
    const m = gsap.timeline({ paused: true });
    const S = (i) => TL.scenes[i];
    const L = (i, j) => TL.scenes[i].lines[j].start;
    const LE = (i, j) => TL.scenes[i].lines[j].end;
    const SE = (i) => S(i).start + S(i).dur;
    const LM = (i, j, k = 0.5) => L(i, j) + (LE(i, j) - L(i, j)) * k; // 某句講到一半
    return { m, S, L, LE, SE, LM };
  }

  window.MV = { LANG, TL, META, $, $$, rng, subtitle, ready, fillStrings, timeline, CJK };
})();
