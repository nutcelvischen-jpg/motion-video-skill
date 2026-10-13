# Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `The page failed to start` + JavaScript errors | A bug in `index.html` (often a mistyped selector, or `c.L(i,j)` with j past the last line) | Read the error line; open `index.html?t=0` in a browser and check the Console |
| Opening `index.html` says "No timeline" | `_tl.js` not generated yet | `python <SKILL>/scripts/render.py <folder> --preview` |
| A contact-sheet frame is empty | The element already faded out, or hasn't entered yet | Adjust entrance / exit times |
| An element is visible from the very first frame | It enters with `m.to` (no start value) | Use `fromTo`, or set `opacity:0` in CSS |
| Animation out of sync with the voice | Hard-coded seconds | Use `c.L(i,j)`, `c.S(i).start` |
| Flicker, renders differ each time | `Math.random`, CSS animation or `setTimeout` | Use `c.rng(seed)`, GSAP and `tick(t)` |
| Fonts fall back to defaults | No internet during render, so Google Fonts can't load | Check the connection, or bundle font files in `_runtime/` with a local `@font-face` |
| Chinese shows as boxes | No CJK font on the system and Google Fonts unreachable | As above |
| TTS `HTTP 401` | Wrong or missing key | Set the environment variable again; a new terminal needs it set again |
| TTS `HTTP 402` / out of credit | OpenRouter balance too low | Top up, or use `GEMINI_API_KEY` |
| TTS `HTTP 429` | Too many requests (free tiers have per-minute limits) | The script waits and retries; if it still fails, rerun later. Finished scenes are skipped |
| TTS `HTTP 400` / `404` | Model name changed or request format differs | Set `TTS_MODEL` or `GEMINI_TTS_MODEL` to a currently available TTS model |
| Edited a line but the voice didn't change | Existing scenes are skipped | `tts.py <folder> --only s03` |
| Wrong accent | Direction too vague | Name the accent in `style`; try another voice |
| Numbers or acronyms read wrongly | TTS reads literally | Use `["spoken", "shown"]` |
| `ffmpeg not found` | Not installed | `pip install imageio-ffmpeg` |
| Chromium fails to launch | Browser not downloaded | `python -m playwright install chromium` |
| Render is slow / machine is hot | Two browsers in parallel | `--workers 1` |
| Video file too large | High quality setting | `--crf 28` (higher = smaller) |
| Garbled Chinese in the Windows terminal | Console encoding | Run `chcp 65001` first, or use PowerShell 7 |
