---
name: motion-video
description: 用 HTML + GSAP 做「有配音、有字幕、動態設計感」的教學短影音或專題介紹影片，以 Gemini TTS 配音、Playwright 逐格渲染成 MP4。當使用者要做動畫影片、教學短片、motion design 影片、專題介紹影片、YouTube Shorts / Reels、或說「做成影片」時使用。
---

# Motion Video Skill — 用程式做動態設計影片

這個 skill 把一支影片拆成三個檔案，全部用程式產生，可以反覆修改、一鍵重新輸出：

| 檔案 | 內容 | 誰來寫 |
|---|---|---|
| `script.json` | 旁白台詞、聲音、語氣、片頭片尾文字 | Agent 依主題撰寫，使用者確認 |
| `index.html` | 畫面元素 + GSAP 動畫時間軸 | Agent 撰寫 |
| `narration_<lang>.wav` + `timeline_<lang>.json` | 配音與每句台詞的精確秒數 | `scripts/tts.py` 自動產生 |

**核心原理**：動畫不是即時播放，而是由 `window.__seek(t)` 控制。渲染時每 1/30 秒呼叫一次 `__seek`、截一張圖，再用 ffmpeg 合成影片。所以畫面每一格都可重現、跟配音精準對齊。

```
主題 → script.json → (預覽：估計時間) → index.html 動畫 → 總覽圖檢查 → tts.py 配音 → 總覽圖複查 → render.py → MP4
```

`<SKILL>` 代表本 skill 資料夾（例如 `.agents/skills/motion-video`）。所有指令都在**工作區根目錄**執行，影片放在 `videos/<名稱>/`。

---

## 步驟 0：檢查環境（第一次使用時）

```bash
pip install -r <SKILL>/requirements.txt
python -m playwright install chromium
python <SKILL>/scripts/check_env.py
```
- 沒有 TTS 金鑰也可以先做「無聲預覽」，最後再配音。
- 金鑰一律用環境變數（`OPENROUTER_API_KEY` 或 `GEMINI_API_KEY`），**絕不寫進任何檔案或對話紀錄**。如果使用者把金鑰貼在對話裡，提醒他改用環境變數，並且不要把金鑰複製到任何檔案。

## 步驟 1：規劃（先跟使用者確認，再動手）

問清楚或自行判斷以下幾點，然後用 5～10 行列出「分鏡大綱」給使用者看：

1. **主題與觀眾**：教什麼？觀眾是誰（國中生、大學生、評審）？
2. **版型**：
   - `shorts`：直式 1080×1920，手繪墨線、紙張質感、貼紙字卡、小機器人主持。適合教學短影音、概念解釋。
   - `wide`：橫式 1920×1080，深色高級感、玻璃卡片、金色點綴、數字動畫。適合專題介紹、產品發表、成果報告。
3. **長度**：60 秒約 220～260 個中文字（或 150 個英文字）。建議 4～8 個場景，每場 1～3 句。
4. **語言**：`zh`（台灣華語）、`en` 或兩者。
5. **聲音與語氣**：見 `references/voices.md`。

分鏡大綱的標準結構：**鉤子（提問或反差）→ 解釋（比喻）→ 例子或數據 → 重點一句話 → 片尾**。

## 步驟 2：寫 `script.json`

規則與完整範例見 `references/script-guide.md`。重點：

- 每句台詞可以是字串，或 `["念的", "字幕顯示的"]`。數字、英文縮寫念法不同時用後者，例如 `["從十二分鐘縮短到三分鐘", "從 12 分鐘縮短到 3 分鐘"]`。
- `style` 是整支影片的聲音指示，`dir` 是每一場的語氣。
- `meta` 放片頭片尾文字與字幕要上色的關鍵字 `hl`。
- 中文一律使用**台灣用語**（例：影片、資料、軟體、品質；不要用視頻、數據、軟件、質量）。
- 寫完先給使用者看台詞，確認後再做動畫。

## 步驟 3：建立影片資料夾

```bash
python <SKILL>/scripts/new_episode.py videos/ep01 --template shorts   # 或 --template wide
```
會複製範本 `index.html`、`script.json` 和 `_runtime/`。**不要修改 `_runtime/` 裡的檔案**；要客製的東西寫在 `index.html` 的 `<style>` 和 `EPISODE` 裡。

## 步驟 4：做動畫（改 `index.html`）

先讀 `references/animation-cookbook.md`（API 一覽與常用招式），再參考 `references/design-guide.md`（設計原則）。

`index.html` 的結構固定如下，只改中間兩塊：

```html
<link rel="stylesheet" href="_runtime/runtime.css">
<style> /* ① 這一集的版面：每個元素的位置、大小 */ </style>
<div id="stage"> <!-- ② 畫面元素：卡片、貼紙、圖片、SVG；全部用 class="abs" + CSS 定位 --> </div>
<script src="_runtime/gsap.min.js"></script><script src="_tl.js"></script><script src="_runtime/core.js"></script>
<script>
window.EPISODE = {
  strings: { zh: {...}, en: {...} },   // 畫面上的文字，HTML 用 data-t="key" 取用
  build(c) { /* ③ 動畫時間軸 */ },
  tick(t, c) { /* 可省略：每格都要重算的程序動畫 */ }
};
</script>
<script src="_runtime/runtime.js"></script>
```

**時間一律綁台詞**，不要寫死秒數：
- `c.S(i).start`：第 i 場開始；`c.L(i, j)` / `c.LE(i, j)`：第 i 場第 j 句的開始 / 結束；`c.LM(i, j, 0.5)`：那句講到一半。
- 換成真實配音後，動畫會自動對齊。

**必守規則**（違反就會渲染錯誤或畫面閃爍）：
1. 所有動畫都放進 `build` 的 GSAP 時間軸（`c.m`），或寫在 `tick(t)` 裡由 `t` 計算。**不要用** CSS `animation` / `transition`、`setTimeout`、`setInterval`、`requestAnimationFrame`、`<video>`、GIF。
2. 不要用 `Math.random()` 或 `Date.now()`；需要亂數用 `c.rng(seed)`（每格結果都一樣）。
3. 圖片放在影片資料夾的 `assets/`，用相對路徑；不要引用網路上的圖片。
4. 版面：
   - `shorts` 的 `#stage` 是 1080×1330（畫面 y=170 起），字幕區在下方，不能放東西。
   - `wide` 是全畫面 1920×1080，上方 140px 是品牌列、下方 160px 是字幕區，內容放中間。
5. 同一時間畫面上最多 3 個重點元素；新場景開始前（`S(i).start - 0.3`）把上一場的元素淡出。
6. 文字不能超出框、不能被字幕蓋住、不能跟主持角色重疊；英文通常比中文長，需要另外調整（`.lang-en #xxx{...}`）。

## 步驟 5：預覽與檢查（每次改完都要做）

```bash
python <SKILL>/scripts/render.py videos/ep01 --sheet            # 每句台詞結尾截一張，拼成總覽圖
python <SKILL>/scripts/render.py videos/ep01 --stills 3.2,7.5   # 指定秒數截圖
python <SKILL>/scripts/render.py videos/ep01 --preview          # 更新 _tl.js；再用瀏覽器開 index.html?play 即時預覽
```
- **一定要打開 `videos/ep01/stills/sheet_<lang>.png` 親自看過**，逐張檢查：文字溢出、元素重疊、元素該出現卻沒出現、該消失卻還在、字幕被擋住。
- 瀏覽器預覽網址加參數：`?play`（循環播放）、`?t=12.5`（停在 12.5 秒）、`&lang=en`（切換語言）。
- 發現問題 → 改 `index.html` → 重跑 `--sheet`，直到沒有問題。
- 還沒配音時用的是估計時間，配音後要再檢查一次。

## 步驟 6：配音

```bash
python <SKILL>/scripts/tts.py --probe                    # 先測金鑰（會產生 probe.wav）
python <SKILL>/scripts/tts.py videos/ep01                # 全部語言
python <SKILL>/scripts/tts.py videos/ep01 --lang zh --only s03   # 改了 s03 的台詞，只重做這段
```
- 已經做過的段落會自動略過；改了台詞一定要用 `--only` 重做該段。
- 產生 `timeline_<lang>.json` 後，`render.py` 會自動改用真實秒數。
- 聽起來不對（口音、語速、念錯字）：調整 `style` / `dir`，或用 `["念法", "顯示"]` 修正念法，再 `--only` 重做。

## 步驟 7：輸出影片

```bash
python <SKILL>/scripts/render.py videos/ep01 --lang zh
```
- 輸出：`videos/ep01/out/ep01_zh.mp4`（沒有配音時是 `_silent.mp4` 無聲預覽）。
- 60 秒的影片約需 2～5 分鐘。電腦較慢就加 `--workers 1`。
- 想加背景音樂：把 `bgm.mp3` 放進影片資料夾，會自動以 -22dB 混入。
- 完成後回報：檔案位置、長度、大小。

## 常見問題

見 `references/troubleshooting.md`。最常見的三個：
- **總覽圖是空白或缺元素**：JavaScript 出錯。`render.py` 會印出錯誤訊息；或用瀏覽器開 `index.html` 看 Console。
- **字型跑掉**：範本從 Google Fonts 載入字型，渲染時需要網路。
- **動畫跟聲音對不上**：動畫時間寫死了秒數，改用 `c.L(i, j)`。

## 檔案地圖

```
<SKILL>/
├── SKILL.md                    ← 本檔：完整流程
├── scripts/
│   ├── check_env.py            ← 檢查環境
│   ├── new_episode.py          ← 建立影片資料夾
│   ├── tts.py                  ← Gemini TTS 配音 + 時間軸
│   ├── render.py               ← 預覽 / 截圖 / 總覽圖 / 輸出 MP4
│   └── mvlib.py                ← 共用函式
├── templates/
│   ├── _common/                ← core.js（字幕、時間軸、字型）、gsap.min.js
│   ├── shorts/                 ← 直式手繪版型 + 範例「API 是什麼？」
│   └── wide/                   ← 橫式高級感版型 + 範例「SnackMap 專題介紹」
└── references/
    ├── script-guide.md         ← 怎麼寫旁白與 script.json
    ├── animation-cookbook.md   ← 動畫 API 與常用招式
    ├── design-guide.md         ← 動態設計原則
    ├── voices.md               ← 聲音選擇與語氣指示
    └── troubleshooting.md      ← 錯誤排除
```
