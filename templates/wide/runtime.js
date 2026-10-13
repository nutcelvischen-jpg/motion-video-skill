/* Wide premium template (1920×1080) — dark background, gold accents, glass cards, bokeh, blur-rise
 * The page must define window.EPISODE = { strings:{...}, build(ctx), tick(t,ctx)? }
 * Host: <div id="host"><img src="assets/host.svg"></div> (swap in your own mascot PNG)
 */
(function () {
  const { LANG, TL, META, $, $$, rng, subtitle, ready, fillStrings, timeline } = window.MV;
  const EP = window.EPISODE;

  const stage = $("#stage");
  const frame = document.createElement("div"); frame.id = "frame";
  frame.innerHTML = `
 <canvas id="bokeh" width="960" height="540"></canvas>
 <div id="chrome"><div class="brandmark"><span class="dot"></span>${META.brand || ""}</div><div class="eventmark">${META.event || ""}</div></div>
 <div id="sub"><div id="subbox" style="opacity:0"></div></div>
 <div id="vig"></div>`;
  document.body.prepend(frame);
  frame.insertBefore(stage, $("#sub"));
  if ($("#host")) gsap.set("#host", { transformOrigin: "50% 95%", opacity: 0 });

  const T = fillStrings(EP);
  const { m, S, L, LE, SE, LM } = timeline();
  const E = "expo.out";
  const state = { bob: 1 };
  const ctx = {
    m, S, L, LE, SE, LM, T, LANG, $, $$, TL, rng, state,
    rise(sel, t, d = 1.0, dy = 50) { m.fromTo(sel, { opacity: 0, y: dy, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: d, ease: E, stagger: 0.08 }, t); },
    out(sel, t, d = 0.6) { m.to(sel, { opacity: 0, y: -30, filter: "blur(10px)", duration: d, ease: "power2.in" }, t); },
    wipe(sel, t, d = 1.1) { m.fromTo(sel, { clipPath: "inset(0 100% 0 0)" }, { clipPath: "inset(0 0% 0 0)", duration: d, ease: "expo.inOut" }, t); },
    count(el, from, to, t, d, fmt) { const o = { v: from }; const node = typeof el === "string" ? $(el) : el; m.fromTo(o, { v: from }, { v: to, duration: d, ease: "power2.out", onUpdate: () => { node.textContent = fmt ? fmt(o.v) : Math.round(o.v); } }, t); },
    type(el, text, t, d) { const o = { n: 0 }; const node = typeof el === "string" ? $(el) : el; m.fromTo(o, { n: 0 }, { n: text.length, duration: d, ease: "none", onUpdate: () => { node.textContent = text.slice(0, Math.round(o.n)); } }, t); },
    bar(sel, pct, t, d = 1.4) { m.fromTo(sel, { width: "0%" }, { width: pct + "%", duration: d, ease: "expo.out" }, t); },
    sheen(sel, t) { m.fromTo(sel + " .sheen", { xPercent: -120 }, { xPercent: 420, duration: 1.4, ease: "power2.inOut" }, t); },
    tilt(sel, t, d = 1.6) { m.fromTo(sel, { opacity: 0, rotateX: 18, rotateY: -14, y: 80, scale: 0.92 }, { opacity: 1, rotateX: 6, rotateY: -6, y: 0, scale: 1, duration: d, ease: E }, t); },
    hostTo(vars, t, d = 1.0) { m.to("#host", Object.assign({ duration: d, ease: "expo.inOut" }, vars), t); },
  };
  EP.build(ctx);
  m.set({}, {}, TL.total);

  /* bokeh: gold particles drifting slowly upward */
  const bc = $("#bokeh").getContext("2d"); const R = rng(77); const P = [];
  const glow = getComputedStyle(document.documentElement).getPropertyValue("--glow-rgb").trim() || "244,185,45";
  for (let i = 0; i < 46; i++) P.push({ x: R() * 960, y: R() * 540, r: 2 + R() * 10, s: 0.2 + R() * 0.6, a: 0.05 + R() * 0.18, ph: R() * 6.28 });
  function bokeh(t) {
    bc.clearRect(0, 0, 960, 540);
    for (const p of P) {
      const y = ((p.y - t * p.s * 14 + 540 * 4) % 560) - 10, x = p.x + Math.sin(t * 0.4 + p.ph) * 18;
      const g = bc.createRadialGradient(x, y, 0, x, y, p.r * 2.2);
      g.addColorStop(0, `rgba(${glow},${p.a})`); g.addColorStop(1, `rgba(${glow},0)`);
      bc.fillStyle = g; bc.beginPath(); bc.arc(x, y, p.r * 2.2, 0, 6.283); bc.fill();
    }
  }
  const hostImg = $("#host img");
  function seek(t) {
    m.seek(t, false);
    bokeh(t);
    const talking = subtitle(t, $("#subbox"));
    if (hostImg) {   // image host: idle bob; slight squash while speaking so it looks like talking
      const bob = Math.sin(t * 2.2) * 8 * state.bob;
      const talk = talking ? Math.max(0, Math.sin(t * 17) + Math.sin(t * 9.3)) * 0.018 : 0;
      hostImg.style.transform = `translateY(${bob.toFixed(1)}px) scale(${(1 - talk / 2).toFixed(4)}, ${(1 + talk).toFixed(4)}) rotate(${(Math.sin(t * 1.3) * 1.5).toFixed(2)}deg)`;
    }
    $$(".caret").forEach((c) => (c.style.opacity = Math.floor(t * 2.5) % 2 ? 0 : 1));
    if (EP.tick) EP.tick(t, ctx);
  }
  window.__seek = seek;
  ready(seek, [["Noto Serif TC", [700, 900]], ["Noto Sans TC", [500, 700]], ["Inter", [500, 700, 800]], ["JetBrains Mono", [500]]]);
})();
