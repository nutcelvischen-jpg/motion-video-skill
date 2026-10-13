# Motion Video Skill：讓 AI Agent 幫你做動態設計影片

[English](https://github.com/nutcelvischen-jpg/motion-video-skill/tree/en) | **繁體中文**

用一句話告訴 AI 你想做什麼影片，它會寫旁白、做動畫、配音，最後輸出 MP4。

- **兩種版型**：直式手繪短影音（教學、概念解釋）／橫式高級感（專題介紹、成果發表）
- **AI 配音**：Gemini TTS，可指定台灣口音、語氣
- **字幕自動對齊**：每句台詞的字幕、動畫都跟著配音時間走
- **可以一直改**：改台詞、改顏色、改動畫，重新跑一次就好

| 直式短影音 `shorts` | 橫式高級感 `wide` |
|---|---|
| ![shorts](docs/preview_shorts.jpg) | ![wide](docs/preview_wide.jpg) |

這是一個 **Agent Skill**（`SKILL.md` 格式），可以在 Google Antigravity、Claude Code 等支援 skills 的 AI 工具中使用。

---

## 一、準備（約 10 分鐘）

需要：**Python 3.9 以上**、**Git**、網路。

### 1. 開一個工作資料夾

在 Antigravity 開啟一個空資料夾（例如 `my-video`），打開終端機（Terminal）。

### 2. 安裝 skill

```bash
git clone https://github.com/nutcelvischen-jpg/motion-video-skill .agents/skills/motion-video
```

> 想讓所有專案都能用，可以改放在全域位置：`~/.gemini/config/skills/motion-video`
>
> 英文版：在 `git clone` 後面加上 `-b en`。

### 3. 安裝套件

Mac：
```bash
pip3 install -r .agents/skills/motion-video/requirements.txt
python3 -m playwright install chromium
python3 .agents/skills/motion-video/scripts/check_env.py
```
Windows：
```powershell
pip install -r .agents/skills/motion-video/requirements.txt
python -m playwright install chromium
python .agents/skills/motion-video/scripts/check_env.py
```
看到「全部就緒！」就完成了。

### 4. 設定配音金鑰（可以晚點再做）

二選一。**金鑰只放在環境變數，不要貼進程式碼、不要傳上 GitHub、不要貼給 AI。**

- **Google AI Studio**（有 Google 帳號就能申請）：到 https://aistudio.google.com 點 Get API key
- **OpenRouter**：到 https://openrouter.ai 申請 Key（需要儲值）

Mac（每次開新終端機都要重設）：
```bash
export GEMINI_API_KEY="貼上你的金鑰"
```
Windows PowerShell：
```powershell
$env:GEMINI_API_KEY="貼上你的金鑰"
```
OpenRouter 的話把 `GEMINI_API_KEY` 換成 `OPENROUTER_API_KEY`。

測試：
```bash
python .agents/skills/motion-video/scripts/tts.py --probe
```
會產生 `probe.wav`，點開聽聽看。

---

## 二、做第一支影片

在 Antigravity 的 Agent 對話框輸入（照抄後改主題）：

> 用 motion-video skill 幫我做一支 45 秒的直式教學短片，主題是「什麼是雲端？」，觀眾是大一新生，用生活比喻解釋，台灣口音、活潑的男生聲音。先給我分鏡大綱和台詞，我確認後再做動畫。

Agent 會依序：
1. 給你分鏡大綱與台詞 → **你確認或修改**
2. 建立 `videos/ep01/`，寫好 `script.json` 和 `index.html`
3. 輸出總覽圖 `stills/sheet_zh.png`，自己檢查畫面
4. 配音（`tts.py`）
5. 輸出影片 `videos/ep01/out/ep01_zh.mp4`

想先看動畫效果：在瀏覽器開 `videos/ep01/index.html?play`。

### 常用的修改說法

- 「第二場的箭頭太小，放大一點，改成橘色」
- 「主持人跟卡片重疊了，把主持人移到右下角」
- 「s03 的台詞改成『……』，只重新配那一段」
- 「整體節奏快一點，每個元素晚 0.2 秒離場」
- 「再做一個英文版」
- 「換成我們的吉祥物」（把圖片放到 `videos/ep01/assets/`）

### 專題介紹影片範例

> 用 motion-video skill 的 wide 版型，幫我做 60 秒的期末專題介紹影片。專題叫「○○○」，解決的問題是……，三個功能是……，成果數據是……。活潑有自信的女生聲音。

---

## 三、自己動手跑指令

不透過 Agent 也可以自己操作。Mac：

```bash
S=.agents/skills/motion-video/scripts
python3 $S/new_episode.py videos/ep01 --template shorts   # 建立（或 --template wide）
python3 $S/render.py videos/ep01 --preview                # 更新預覽，瀏覽器開 index.html?play
python3 $S/render.py videos/ep01 --sheet                  # 總覽圖
python3 $S/tts.py videos/ep01                             # 配音
python3 $S/render.py videos/ep01 --lang zh                # 輸出 MP4
```
Windows PowerShell：第一行改成 `$S=".agents/skills/motion-video/scripts"`，其餘把 `python3` 換成 `python`。

---

## 四、課堂練習

1. **暖身（15 分鐘）**：用 shorts 範本，不改動畫，只改 `script.json` 的台詞，做出自己的版本。
2. **改動畫（30 分鐘）**：請 Agent 把範例的「餐廳比喻」換成你自己想的比喻，並加一個新道具。
3. **完成作品（60 分鐘）**：選一個你懂的概念，做一支 45～60 秒的教學短片，含配音。
4. **互評**：用 `references/design-guide.md` 的檢查清單互相檢查。

---

## 五、運作原理

```
script.json（台詞）──► tts.py ──► narration.wav + timeline.json（每句幾秒）
                                         │
index.html（畫面 + GSAP 動畫）◄──────────┘ 動畫時間綁在台詞上
        │
        └──► render.py：Playwright 每 1/30 秒呼叫 __seek(t) 截圖 ──► ffmpeg ──► MP4
```

詳細流程寫在 [SKILL.md](SKILL.md)，Agent 會照著做。

---

## 授權

- 本專案的程式與文件：MIT License
- `templates/_common/gsap.min.js`：GSAP by GreenSock，依其 [Standard License](https://gsap.com/standard-license) 使用
- 字型由 Google Fonts 提供（Noto Sans TC、Noto Serif TC、Inter、JetBrains Mono，皆為 OFL 授權）
