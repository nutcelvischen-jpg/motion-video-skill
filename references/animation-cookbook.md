# 動畫 API 與常用招式

所有動畫寫在 `EPISODE.build(c)` 裡。`c` 是工具箱，`c.m` 是 GSAP 主時間軸。

## 1. 時間函式（兩種版型都有）

| 函式 | 意思 |
|---|---|
| `c.S(i).start` / `c.S(i).dur` | 第 i 場（從 0 開始）的開始時間 / 長度 |
| `c.SE(i)` | 第 i 場結束時間 |
| `c.L(i, j)` | 第 i 場第 j 句台詞開始 |
| `c.LE(i, j)` | 第 i 場第 j 句台詞結束 |
| `c.LM(i, j, k)` | 第 i 場第 j 句講到 k 比例的時間（0.5 = 一半） |
| `c.TL.total` | 影片總長 |
| `c.LANG` | 目前語言（"zh" / "en"） |
| `c.T` | 這個語言的 `strings` |
| `c.rng(seed)` | 可重現的亂數產生器 |

**節奏原則**：元素在「講到它的那句」開始時出現（`L(i,j)`），或稍早 0.1～0.2 秒；離場在下一場開始前 0.2～0.4 秒（`S(i+1).start - 0.3`）。

## 2. shorts 版型工具

| 工具 | 效果 | 適合 |
|---|---|---|
| `c.pop(sel, t, d=.45)` | 從 0 彈出放大（back.out） | 卡片、圖示、節點 |
| `c.slam(sel, t)` | 從 2.8 倍大砸下來 | 重點字卡、驚嘆 |
| `c.show(sel, t, d=.35, {y:30})` | 淡入並從下方滑入 | 文字、面板 |
| `c.fade(sel, t, d=.3)` | 淡出 | 換場清除 |
| `c.draw(sel, t, d=.6, len=1200)` | SVG 線條畫出來 | 箭頭、底線、圈選 |
| `c.type(sel, text, t, d)` | 打字機效果 | 輸入框、程式碼 |
| `c.hostTo({x,y,scale,opacity}, t, d)` | 移動主持機器人 | 登場、退到角落 |
| `c.wave(t0, t1)` | 主持人揮手 | 開場打招呼 |
| `c.shock(t0, t1)` | 主持人流汗皺眉 | 出錯、危險 |
| `c.outroAt(t)` | 黑幕 + 片尾三行字 | 最後一句結束後 0.2 秒 |

主持人講話時嘴巴會**自動**開合，不用另外寫。

CSS class：`.card`（米白卡片＋黑框＋硬陰影）、`.sticker`（貼紙字卡，加 `.hot` 橘、`.dark` 黑、`.good` 綠）、`.panel`（深色面板）、`.term`（終端機文字）、`.browser`（瀏覽器視窗）、`.boil`（線條抖動手繪感）、`.caret`（閃爍游標）、`.mono`。

## 3. wide 版型工具

| 工具 | 效果 | 適合 |
|---|---|---|
| `c.rise(sel, t, d=1, dy=50)` | 模糊 → 清晰並上浮（多個元素自動錯開） | 標題、卡片群 |
| `c.out(sel, t, d=.6)` | 模糊淡出並上移 | 換場 |
| `c.wipe(sel, t, d=1.1)` | 由左到右揭開 | 長條、圖片、標題 |
| `c.count(sel, from, to, t, d, fmt)` | 數字跳動 | KPI、百分比 |
| `c.bar(sel, pct, t, d=1.4)` | 長條長到 pct% | 前後比較 |
| `c.tilt(sel, t, d=1.6)` | 3D 傾斜浮入 | 截圖、網站畫面 |
| `c.sheen(sel, t)` | 一道光澤掃過（元素內要有 `<div class="sheen">`） | 卡片、重點 |
| `c.type(sel, text, t, d)` | 打字機效果 | 搜尋框、提問 |
| `c.hostTo({x,y,scale,opacity}, t, d)` | 移動主持角色 | 登場、退到角落 |

主持角色是 `<div id="host"><img src="assets/host.svg"></div>`，換成自己的吉祥物圖片即可（建議 PNG 去背）；講話時會自動輕微伸縮。

CSS class：`.glass`（玻璃卡片）、`.chip`（膠囊標籤）、`.shot`（瀏覽器截圖框，內含 `.bar` 與 `<img>`）、`.track`（長條底，內含 `<i>`）、`.h1` `.h2` `.eyebrow` `.gold` `.serif` `.num` `.foot`。品牌色改 `:root` 的 `--gold` `--glow-rgb` 等變數。

## 4. 直接用 GSAP

工具不夠用時，直接寫 `c.m.to / fromTo / set`，第三個參數是時間：

```js
c.m.to("#card", { x: 200, rotation: -6, duration: .5, ease: "power3.out" }, c.L(1, 0));
c.m.fromTo(".dot", { scale: 0 }, { scale: 1, duration: .3, stagger: .1, ease: "back.out(3)" }, c.L(2, 1));
c.m.set("#warn", { opacity: 1 }, c.LM(2, 0, .5));          // 瞬間切換
```
常用 ease：`power3.out`（自然減速）、`back.out(2)`（回彈）、`expo.out`（高級感）、`expo.inOut`（大位移）、`none`（等速）。

## 5. 常用招式

**換場清空**
```js
c.fade(["#a", "#b", "#c"], c.S(2).start - .25);   // shorts
c.out("#scene1", c.S(2).start - .4);              // wide
```

**主持人退到角落再講解**
```js
c.hostTo({ scale: 1, opacity: 1 }, c.S(0).start, .5);              // 登場
c.hostTo({ x: -230, y: 60, scale: .55 }, c.L(0, 1) - .2, .5);      // 退到左下
```

**逐項列點（跟著台詞出現）**
```js
["#p1", "#p2", "#p3"].forEach((id, k) => c.pop(id, c.LM(1, 0, .2 + k * .3)));
```

**打字 + 送出**
```html
<div id="ask" class="abs panel"><span id="q"></span><span class="caret"></span></div>
```
```js
c.show("#ask", c.S(0).start);
c.type("#q", c.T.question, c.S(0).start + .3, 1.6);
```

**數字跳動加單位**
```js
c.count("#v", 0, 81.4, c.L(3, 1), 1.5, v => v.toFixed(1) + "%");
```

**每格程序動畫（tick）**：時鐘、旋轉、粒子、閃爍——由 t 算出來，不要用累加。
```js
tick(t, c) { c.$("#gear").style.transform = `rotate(${(t * 90) % 360}deg)`; }
```

**狀態值 + tick**：用時間軸改一個數字，在 tick 裡讀它。
```js
// build
c.state.pour = 0;                                    // 先給初始值
c.m.to(c.state, { pour: 1, duration: 1 }, c.L(1, 1));
// tick
tick(t, c) { const k = c.state.pour || 0; c.$("#water").setAttribute("height", 200 * k); }
```

## 6. 畫面素材

- **SVG 手繪風**：直接寫 `<svg>`，線條 `stroke="#1B1A17" stroke-width="8" stroke-linecap="round"`，加 `class="boil"` 產生手繪抖動。
- **網站截圖**：先用 Playwright 截好圖存到 `assets/`，放進 `.shot` 或 `.browser` 框裡。
- **圖示**：用簡單 SVG 或文字符號（✓ ✗ → ①），避免 emoji（不同電腦顯示不一致）。
- **不要畫知名角色或商標**；用原創角色。
