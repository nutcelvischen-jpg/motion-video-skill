# Animation API and recipes

All animation goes in `EPISODE.build(c)`. `c` is the toolbox; `c.m` is the GSAP master timeline.

## 1. Timing helpers (both templates)

| Helper | Meaning |
|---|---|
| `c.S(i).start` / `c.S(i).dur` | Start / length of scene i (0-based) |
| `c.SE(i)` | End of scene i |
| `c.L(i, j)` | Start of line j in scene i |
| `c.LE(i, j)` | End of line j in scene i |
| `c.LM(i, j, k)` | Time when line j of scene i is fraction k through (0.5 = halfway) |
| `c.TL.total` | Total video length |
| `c.LANG` | Current language ("en" / "zh") |
| `c.T` | `strings` for this language |
| `c.rng(seed)` | Seeded random generator |

**Rhythm**: an element appears when the line that mentions it starts (`L(i,j)`), or 0.1–0.2 s earlier. It leaves 0.2–0.4 s before the next scene (`S(i+1).start - 0.3`).

## 2. shorts template helpers

| Helper | Effect | Use for |
|---|---|---|
| `c.pop(sel, t, d=.45)` | Pops in from scale 0 (back.out) | Cards, icons, nodes |
| `c.slam(sel, t)` | Slams down from 2.8× | Key stickers, exclamations |
| `c.show(sel, t, d=.35, {y:30})` | Fades in, sliding up | Text, panels |
| `c.fade(sel, t, d=.3)` | Fades out | Clearing between scenes |
| `c.draw(sel, t, d=.6, len=1200)` | Draws an SVG stroke | Arrows, underlines, circles |
| `c.type(sel, text, t, d)` | Typewriter | Input boxes, code |
| `c.hostTo({x,y,scale,opacity}, t, d)` | Moves the robot host | Entrance, stepping aside |
| `c.wave(t0, t1)` | Host waves | Greeting |
| `c.shock(t0, t1)` | Host sweats and frowns | Errors, danger |
| `c.outroAt(t)` | Black-out + three outro lines | 0.2 s after the last line ends |

The host's mouth moves **automatically** while it speaks.

CSS classes: `.card` (cream card, black border, hard shadow), `.sticker` (sticker card; add `.hot` orange, `.dark` black, `.good` green), `.panel` (dark panel), `.term` (terminal text), `.browser` (browser window), `.boil` (hand-drawn wobble), `.caret` (blinking cursor), `.mono`.

## 3. wide template helpers

| Helper | Effect | Use for |
|---|---|---|
| `c.rise(sel, t, d=1, dy=50)` | Blur → sharp while rising (staggers multiple elements) | Titles, card groups |
| `c.out(sel, t, d=.6)` | Blurs out and lifts | Scene exits |
| `c.wipe(sel, t, d=1.1)` | Left-to-right reveal | Bars, images, titles |
| `c.count(sel, from, to, t, d, fmt)` | Counting number | KPIs, percentages |
| `c.bar(sel, pct, t, d=1.4)` | Grows a bar to pct% | Before/after comparisons |
| `c.tilt(sel, t, d=1.6)` | 3D tilted float-in | Screenshots, websites |
| `c.sheen(sel, t)` | A light sweep (element needs `<div class="sheen">`) | Cards, highlights |
| `c.type(sel, text, t, d)` | Typewriter | Search boxes, questions |
| `c.hostTo({x,y,scale,opacity}, t, d)` | Moves the host | Entrance, stepping aside |

The host is `<div id="host"><img src="assets/host.svg"></div>`. Swap in your own mascot (a transparent PNG works best). It squashes slightly while speaking.

CSS classes: `.glass` (glass card), `.chip` (pill label), `.shot` (browser screenshot frame with `.bar` and `<img>`), `.track` (bar track containing `<i>`), `.h1` `.h2` `.eyebrow` `.gold` `.serif` `.num` `.foot`. Change brand colours with the `:root` variables such as `--gold` and `--glow-rgb`.

## 4. Using GSAP directly

When the helpers are not enough, call `c.m.to / fromTo / set`; the third argument is the time:

```js
c.m.to("#card", { x: 200, rotation: -6, duration: .5, ease: "power3.out" }, c.L(1, 0));
c.m.fromTo(".dot", { scale: 0 }, { scale: 1, duration: .3, stagger: .1, ease: "back.out(3)" }, c.L(2, 1));
c.m.set("#warn", { opacity: 1 }, c.LM(2, 0, .5));          // instant switch
```
Useful eases: `power3.out` (natural slow-down), `back.out(2)` (bounce), `expo.out` (premium), `expo.inOut` (big moves), `none` (linear).

## 5. Recipes

**Clear the stage between scenes**
```js
c.fade(["#a", "#b", "#c"], c.S(2).start - .25);   // shorts
c.out("#scene1", c.S(2).start - .4);              // wide
```

**Host steps aside to present**
```js
c.hostTo({ scale: 1, opacity: 1 }, c.S(0).start, .5);              // enter
c.hostTo({ x: -230, y: 60, scale: .55 }, c.L(0, 1) - .2, .5);      // move to lower left
```

**Bullet points in sync with narration**
```js
["#p1", "#p2", "#p3"].forEach((id, k) => c.pop(id, c.LM(1, 0, .2 + k * .3)));
```

**Typing a question**
```html
<div id="ask" class="abs panel"><span id="q"></span><span class="caret"></span></div>
```
```js
c.show("#ask", c.S(0).start);
c.type("#q", c.T.question, c.S(0).start + .3, 1.6);
```

**Counting number with a unit**
```js
c.count("#v", 0, 81.4, c.L(3, 1), 1.5, v => v.toFixed(1) + "%");
```

**Per-frame procedural animation (tick)**: clocks, spinning, particles, blinking — compute from t, never accumulate.
```js
tick(t, c) { c.$("#gear").style.transform = `rotate(${(t * 90) % 360}deg)`; }
```

**State value + tick**: tween a number on the timeline and read it in tick.
```js
// build
c.state.pour = 0;                                    // give it a starting value first
c.m.to(c.state, { pour: 1, duration: 1 }, c.L(1, 1));
// tick
tick(t, c) { const k = c.state.pour || 0; c.$("#water").setAttribute("height", 200 * k); }
```

## 6. Visual assets

- **Hand-drawn SVG**: write `<svg>` directly with strokes like `stroke="#1B1A17" stroke-width="8" stroke-linecap="round"`, and add `class="boil"` for the hand-drawn wobble.
- **Website screenshots**: capture them first (e.g. with Playwright), save to `assets/`, and place them in a `.shot` or `.browser` frame.
- **Icons**: simple SVG or text symbols (✓ ✗ → ①). Avoid emoji, which render differently on different machines.
- **Never draw well-known characters or logos**; use original characters.
