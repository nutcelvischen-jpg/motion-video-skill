# 聲音選擇（Gemini TTS）

在 `script.json` 的 `voice` 填聲音名稱，`style` 寫語氣指示。Gemini TTS 的聲音名稱與官方描述的特質：

| 聲音 | 特質 | 聲音 | 特質 |
|---|---|---|---|
| Zephyr | 明亮 | Puck | 輕快、有活力 |
| Charon | 知性、說明感 | Kore | 堅定 |
| Fenrir | 興奮 | Leda | 年輕 |
| Orus | 堅定 | Aoede | 輕鬆 |
| Callirrhoe | 隨和 | Autonoe | 明亮 |
| Enceladus | 氣音 | Iapetus | 清晰 |
| Umbriel | 隨和 | Algieba | 圓潤 |
| Despina | 圓潤 | Erinome | 清晰 |
| Algenib | 沙啞 | Rasalgethi | 知性 |
| Laomedeia | 輕快 | Achernar | 柔和 |
| Alnilam | 堅定 | Schedar | 平穩 |
| Gacrux | 成熟 | Pulcherrima | 直接 |
| Achird | 友善 | Zubenelgenubi | 隨性 |
| Vindemiatrix | 溫柔 | Sadachbia | 活潑 |
| Sadaltager | 博學 | Sulafat | 溫暖 |

**實測好用的組合**
- 台灣口音、活潑年輕男生：`Puck`
- 台灣口音、活潑年輕女生：`Leda`
- 英式英文、穩重說明：`Charon`；輕快女聲：`Aoede`

**語氣指示範例**
- 「請用台灣口音的華語，像親切、活潑的年輕老師在跟學生解釋，語速稍快、句尾自然，不要播音腔。」
- 「請用台灣口音的華語，活潑、有自信的年輕女生，像在發表會上介紹自己的作品。」
- 「Speak in a warm, clear British English accent, like a friendly young teacher. Brisk and upbeat.」

先用 `python <SKILL>/scripts/tts.py --probe` 或只做一段（`--only s01`）試聽，滿意再全部產生。

## 金鑰設定

擇一即可，**設成環境變數，不要寫進檔案**：

| 服務 | 環境變數 | 申請 | 預設模型（可用環境變數覆寫） |
|---|---|---|---|
| OpenRouter | `OPENROUTER_API_KEY` | openrouter.ai → Keys | `TTS_MODEL`，預設 `google/gemini-3.8-flash-tts` |
| Google AI Studio | `GEMINI_API_KEY` | aistudio.google.com → Get API key | `GEMINI_TTS_MODEL`，預設 `gemini-2.5-flash-preview-tts` |

兩個都設定時優先用 OpenRouter。模型名稱會更新，失敗時先確認該服務目前提供的 TTS 模型名稱。
