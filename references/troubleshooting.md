# 錯誤排除

| 症狀 | 原因 | 解法 |
|---|---|---|
| `頁面沒有正常啟動` + JavaScript 錯誤 | `index.html` 程式寫錯（常見：選擇器打錯、`c.L(i,j)` 的 j 超過台詞句數） | 看錯誤訊息的行號；用瀏覽器開 `index.html?t=0` 看 Console |
| 開 `index.html` 出現「找不到時間軸」 | 還沒產生 `_tl.js` | `python <SKILL>/scripts/render.py <資料夾> --preview` |
| 總覽圖某張空白 | 元素在那個時間點已經淡出，或還沒進場 | 調整進場／離場時間 |
| 元素一開始就出現在畫面上 | 用了 `m.to` 做進場（沒有起始值） | 改用 `fromTo`，或在 CSS 先設 `opacity:0` |
| 動畫跟聲音對不上 | 時間寫死秒數 | 改用 `c.L(i,j)`、`c.S(i).start` |
| 畫面閃爍、每次渲染不一樣 | 用了 `Math.random`、CSS animation、`setTimeout` | 改用 `c.rng(seed)`、GSAP、`tick(t)` |
| 字型變成預設字型 | 渲染時沒有網路，Google Fonts 載不到 | 確認網路；或把字型檔放在 `_runtime/` 並改用本機 `@font-face` |
| 中文變成方框 | 系統缺中文字型且 Google Fonts 載不到 | 同上 |
| TTS `HTTP 401` | 金鑰錯誤或沒設定 | 重新設定環境變數；新開的終端機要重新設定 |
| TTS `HTTP 402` / 額度不足 | OpenRouter 餘額不足 | 儲值，或改用 `GEMINI_API_KEY` |
| TTS `HTTP 429` | 呼叫太頻繁（免費額度每分鐘有上限） | 程式會自動等待重試；仍失敗就隔幾分鐘再跑，已完成的段落會略過 |
| TTS `HTTP 400` / `404` | 模型名稱已更新或格式不符 | 改 `TTS_MODEL` 或 `GEMINI_TTS_MODEL` 為目前可用的 TTS 模型 |
| 改了台詞但聲音沒變 | 已存在的段落會略過 | `tts.py <資料夾> --only s03` |
| 配音口音不對 | 指示不夠明確 | `style` 寫「台灣口音的華語」；換聲音試試 |
| 數字、英文念錯 | TTS 照字念 | 用 `["念法", "字幕"]` |
| `找不到 ffmpeg` | 沒安裝 | `pip install imageio-ffmpeg` |
| Chromium 無法啟動 | 沒下載瀏覽器 | `python -m playwright install chromium` |
| 渲染很慢、電腦很燙 | 同時開兩個瀏覽器 | `--workers 1` |
| 影片檔太大 | 畫質設定高 | `--crf 28`（數字越大檔案越小） |
| Windows 終端機中文亂碼 | 編碼 | 先執行 `chcp 65001`，或用 PowerShell 7 |
