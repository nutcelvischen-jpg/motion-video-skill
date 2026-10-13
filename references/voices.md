# Choosing a voice (Gemini TTS)

Put the voice name in `voice` in `script.json` and the tone direction in `style`. Gemini TTS voices and their official character descriptions:

| Voice | Character | Voice | Character |
|---|---|---|---|
| Zephyr | Bright | Puck | Upbeat |
| Charon | Informative | Kore | Firm |
| Fenrir | Excitable | Leda | Youthful |
| Orus | Firm | Aoede | Breezy |
| Callirrhoe | Easy-going | Autonoe | Bright |
| Enceladus | Breathy | Iapetus | Clear |
| Umbriel | Easy-going | Algieba | Smooth |
| Despina | Smooth | Erinome | Clear |
| Algenib | Gravelly | Rasalgethi | Informative |
| Laomedeia | Upbeat | Achernar | Soft |
| Alnilam | Firm | Schedar | Even |
| Gacrux | Mature | Pulcherrima | Forward |
| Achird | Friendly | Zubenelgenubi | Casual |
| Vindemiatrix | Gentle | Sadachbia | Lively |
| Sadaltager | Knowledgeable | Sulafat | Warm |

**Combinations we have tested**
- British English, steady explainer: `Charon`; light and breezy: `Aoede`
- Taiwanese Mandarin, lively young male voice: `Puck`; lively young female voice: `Leda`

**Example directions**
- "Speak in a warm, clear British English accent, like a friendly young teacher. Brisk and upbeat."
- "Bright, confident young woman presenting her own project at a showcase. Clear and upbeat."
- 「請用台灣口音的華語，像親切、活潑的年輕老師在跟學生解釋，語速稍快，不要播音腔。」

Test with `python <SKILL>/scripts/tts.py --probe`, or generate one scene (`--only s01`) and listen before producing everything.

## API keys

Use either one, **as an environment variable, never in a file**:

| Service | Variable | Get a key | Default model (override with) |
|---|---|---|---|
| OpenRouter | `OPENROUTER_API_KEY` | openrouter.ai → Keys | `TTS_MODEL`, default `google/gemini-3.8-flash-tts` |
| Google AI Studio | `GEMINI_API_KEY` | aistudio.google.com → Get API key | `GEMINI_TTS_MODEL`, default `gemini-2.5-flash-preview-tts` |

If both are set, OpenRouter is used. Model names change over time; if a call fails, check which TTS models the service currently offers.
