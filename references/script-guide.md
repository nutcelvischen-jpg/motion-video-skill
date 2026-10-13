# Writing narration and script.json

## 1. File format

```json
{
  "format": "shorts",                 // "shorts" (vertical 1080×1920) or "wide" (horizontal 1920×1080)
  "size": [1080, 1920],               // optional; derived from format
  "langs": ["en", "zh"],              // languages to produce; the first is the default
  "voice": { "en": "Charon", "zh": "Puck" },     // Gemini TTS voice names, see voices.md
  "style": {                          // voice direction for the whole video (director's notes for TTS)
    "en": "Warm, clear British English, like a friendly young teacher. Brisk pace.",
    "zh": "請用台灣口音的華語，像親切活潑的年輕老師，語速稍快，不要播音腔。"
  },
  "meta": {
    "common": { "num": 1 },           // shared across languages: episode number (shorts), brand (wide)
    "en": {
      "series": "AI Basics",          // shorts: series name, top left
      "topic": "What is an API?",     // shorts: topic, top right
      "tagline": "AI BASICS",         // shorts: small text in the outro
      "outro": { "a": "An API is", "b": "the Waiter", "c": "Next → What is a key?" },  // shorts: three outro lines
      "event": "FINAL PROJECT · DEMO",// wide: event name, top right
      "hl": ["API", "waiter"]         // words to highlight in subtitles
    },
    "zh": { "...": "..." }
  },
  "scenes": [
    {
      "id": "s01",                    // scene id, used in audio file names; must be unique
      "dir": { "en": "Curious opening.", "zh": "開場，好奇地提問。" },  // tone for this scene
      "en": ["First line.", "Second line."],   // each item is one subtitle
      "zh": ["第一句", "第二句"]
    }
  ]
}
```

(Comments are for explanation only; real JSON cannot contain comments.)

## 2. Narration principles

1. **One idea per line**: each line becomes one subtitle. Keep English lines to about 6–14 words; split anything longer.
2. **Conversational**: write it as you would say it to a friend, not as a report. Use "you"; avoid "In this video we will introduce…".
3. **Hook first**: open with a question, a contrast or a number to grab attention in the first 3 seconds.
4. **One metaphor carries the video**: explain abstract ideas with everyday images (API = waiter, database = warehouse, API key = house key) and build the visuals around that one metaphor.
5. **End with one line**: the last scene sums up in one memorable sentence that matches the `outro`.
6. **Length**: about 2.5 English words per second, so 60 s ≈ 150 words. Chinese runs about 4.5 characters per second.
7. **Chinese versions**: use Taiwanese Mandarin vocabulary (影片, 資料, 軟體, 品質, 網路, 程式), not Mainland terms (視頻, 數據, 軟件, 質量, 網絡, 程序).

## 3. When pronunciation and subtitles differ

TTS reads exactly what it is given, so numbers, symbols and acronyms can come out wrong. Use `["spoken", "shown"]`:

```json
["mentions jumped from twenty-eight percent to eighty-one percent!", "mentions jumped from 28% to 81%!"]
["we tested it with G P T", "we tested it with GPT"]
["it costs nine hundred sixty-five New Taiwan dollars", "it costs NT$965"]
```

## 4. Writing `style` and `dir`

- `style` describes who is speaking, to whom, with what accent and at what pace.
- `dir` only says what is different in this scene: "surprised", "slower, with emphasis", "light, upbeat close".
- Name the accent explicitly ("British English", "Taiwanese Mandarin"), otherwise the voice may drift to a default accent.

## 5. Example: a 60-second explainer outline

| Scene | Purpose | Narration | Visuals |
|---|---|---|---|
| s01 | Hook | Ever wondered how a phone app gets its data? / The answer: an API! | Phone card with "?" → API sticker slams in |
| s02 | Metaphor | An API is like a waiter in a restaurant. / You order, the waiter takes it to the kitchen, then brings your food back. | You → Waiter → Kitchen, arrows drawn in |
| s03 | Example | A weather app works the same way: it "orders" today's weather from a weather service's API. | Weather card, data flying in |
| s04 | Takeaway | You don't need to know how the kitchen cooks. You just need to know how to order! | Green sticker "Just know how to order" |
| Outro | Memory hook | (no narration) | An API is the Waiter |
