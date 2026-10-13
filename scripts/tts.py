#!/usr/bin/env python3
"""用 Gemini TTS 產生旁白、並依實際音檔長度建立時間軸（只用 Python 標準函式庫）。

兩種金鑰擇一（設成環境變數，不要寫進程式或 script.json）：
  OPENROUTER_API_KEY  → 走 OpenRouter（預設模型 google/gemini-3.8-flash-tts）
  GEMINI_API_KEY      → 直接走 Google AI Studio（預設模型 gemini-2.5-flash-preview-tts）

用法：
  python scripts/tts.py videos/ep01                 # script.json 裡所有語言
  python scripts/tts.py videos/ep01 --lang zh       # 只做中文
  python scripts/tts.py videos/ep01 --only s03 s04  # 只重做某幾段（改台詞後用）
  python scripts/tts.py --probe                     # 用一句話測試金鑰與格式
輸出：audio_<lang>/sNN.wav、narration_<lang>.wav、timeline_<lang>.json
"""
import argparse, array, base64, json, os, re, sys, time, urllib.error, urllib.request, wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mvlib import CJK, GAP, LEAD_IN, TAIL, load_script, say, split_lines  # noqa: E402

RATE = 24000


def provider():
    if os.environ.get("OPENROUTER_API_KEY"):
        return "openrouter", os.environ["OPENROUTER_API_KEY"]
    if os.environ.get("GEMINI_API_KEY"):
        return "google", os.environ["GEMINI_API_KEY"]
    raise SystemExit("沒有金鑰。請先設定環境變數 OPENROUTER_API_KEY 或 GEMINI_API_KEY（設定方式見 README）")


def _post(url, headers, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
                                 headers=dict(headers, **{"Content-Type": "application/json"}))
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


# ---------- OpenRouter：依序嘗試幾種請求格式，第一個成功的會被記住 ----------
OR_MODEL = os.environ.get("TTS_MODEL", "google/gemini-3.8-flash-tts")
OR_VARIANTS = [
    ("字串 input + instructions", lambda t, v, i: {"model": OR_MODEL, "input": t, "voice": v, "instructions": i, "response_format": "pcm"}),
    ("陣列 input", lambda t, v, i: {"model": OR_MODEL, "response_format": "pcm", "voice": v, "input": [{"text": t, "voice": v, "instructions": i}]}),
    ("不帶 instructions", lambda t, v, i: {"model": OR_MODEL, "input": t, "voice": v, "response_format": "pcm"}),
]
_ok = None


def tts_openrouter(key, text, voice, instr):
    global _ok
    order = [_ok] if _ok is not None else range(len(OR_VARIANTS))
    for idx in order:
        name, build = OR_VARIANTS[idx]
        for attempt in range(3):
            try:
                data = _post("https://openrouter.ai/api/v1/audio/speech", {"Authorization": f"Bearer {key}"}, build(text, voice, instr))
                if len(data) < 2000:
                    raise RuntimeError(f"回傳太短，可能不是音訊：{data[:200]!r}")
                if _ok is None:
                    print(f"   ✓ 可用格式：{name}"); _ok = idx
                return data
            except urllib.error.HTTPError as e:
                print(f"   ✗ [{name}] HTTP {e.code}: {e.read().decode(errors='ignore')[:400]}")
                if e.code == 429 or e.code >= 500:
                    time.sleep(4 * (attempt + 1)); continue
                break
            except (urllib.error.URLError, RuntimeError, TimeoutError) as e:
                print(f"   ✗ [{name}] {e}"); time.sleep(3 * (attempt + 1))
    raise SystemExit("OpenRouter 所有格式都失敗。檢查金鑰、餘額，或改用 TTS_MODEL 指定其他模型。")


# ---------- Google AI Studio（Gemini API）----------
G_MODEL = os.environ.get("GEMINI_TTS_MODEL", "gemini-2.5-flash-preview-tts")


def tts_google(key, text, voice, instr):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{G_MODEL}:generateContent"
    payload = {"contents": [{"parts": [{"text": f"{instr}\n\n{text}"}]}],
               "generationConfig": {"responseModalities": ["AUDIO"],
                                    "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    for attempt in range(4):
        try:
            res = json.loads(_post(url, {"x-goog-api-key": key}, payload))
            part = res["candidates"][0]["content"]["parts"][0]["inlineData"]
            m = re.search(r"rate=(\d+)", part.get("mimeType", ""))
            if m and int(m.group(1)) != RATE:
                raise SystemExit(f"取樣率是 {m.group(1)}，程式預期 {RATE}，請回報。")
            return base64.b64decode(part["data"])
        except urllib.error.HTTPError as e:
            print(f"   ✗ HTTP {e.code}: {e.read().decode(errors='ignore')[:400]}")
            if e.code == 429 or e.code >= 500:
                time.sleep(8 * (attempt + 1)); continue     # 免費額度有每分鐘上限，等一下再試
            break
        except (urllib.error.URLError, KeyError, IndexError, TimeoutError) as e:
            print(f"   ✗ {e}"); time.sleep(3 * (attempt + 1))
    raise SystemExit("Gemini API 失敗。檢查金鑰，或用 GEMINI_TTS_MODEL 指定可用的 TTS 模型。")


def tts(text, voice, instr):
    prov, key = provider()
    return (tts_openrouter if prov == "openrouter" else tts_google)(key, text, voice, instr)


# ---------- 音訊處理 ----------
def trim(pcm, thresh=350):
    """切掉頭尾的靜音，讓段落銜接更緊。"""
    a = array.array("h", pcm); win = RATE // 100
    if len(a) < win * 4:
        return pcm
    loud = lambda i: max(abs(x) for x in a[i:i + win]) > thresh
    s = 0
    while s < len(a) - win and not loud(s): s += win
    e = len(a) - win
    while e > s and not loud(e): e -= win
    return a[max(0, s - win * 3):min(len(a), e + win * 6)].tobytes()


def write_wav(path, pcm):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(pcm)


def build_timeline(folder, data, lang):
    t = LEAD_IN; tl = {"lang": lang, "lead_in": LEAD_IN, "gap": GAP, "scenes": []}
    merged = bytearray(b"\x00\x00" * int(RATE * LEAD_IN))
    for sc in data["scenes"]:
        with wave.open(str(folder / f"audio_{lang}" / f"{sc['id']}.wav")) as w:
            pcm = w.readframes(w.getnframes())
        dur = len(pcm) / 2 / RATE
        tl["scenes"].append({"id": sc["id"], "start": round(t, 3), "dur": round(dur, 3), "lines": split_lines(sc[lang], lang, t, dur)})
        merged += pcm + b"\x00\x00" * int(RATE * GAP); t += dur + GAP
    tl["total"] = round(t + TAIL, 3)
    merged += b"\x00\x00" * int(RATE * TAIL)
    write_wav(folder / f"narration_{lang}.wav", bytes(merged))
    (folder / f"timeline_{lang}.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    return tl["total"]


def run(folder, data, lang, only):
    out = folder / f"audio_{lang}"; out.mkdir(exist_ok=True)
    for sc in data["scenes"]:
        if only and sc["id"] not in only:
            continue
        f = out / f"{sc['id']}.wav"
        if f.exists() and not only:
            continue                      # 已經做過的段落略過；要重做請用 --only
        joiner = "" if lang in CJK else " "
        text = joiner.join(say(l) for l in sc[lang])
        instr = (data.get("style", {}).get(lang, "") + " " + sc.get("dir", {}).get(lang, "")).strip()
        print(f"→ {lang} {sc['id']}：{text[:36]}…")
        write_wav(f, trim(tts(text, data["voice"][lang], instr)))
    missing = [sc["id"] for sc in data["scenes"] if not (out / f"{sc['id']}.wav").exists()]
    if missing:
        raise SystemExit(f"還缺這些段落的音檔：{missing}")
    print(f"✓ {folder.name} {lang} 總長 {build_timeline(folder, data, lang):.1f} 秒")


def main():
    ap = argparse.ArgumentParser(description="Gemini TTS 配音")
    ap.add_argument("folder", nargs="?")
    ap.add_argument("--lang"); ap.add_argument("--only", nargs="*", default=[])
    ap.add_argument("--probe", action="store_true", help="用一句短句測試")
    a = ap.parse_args()
    if a.probe:
        pcm = tts("大家好，這是配音測試。", "Puck", "請用台灣口音的華語，活潑的年輕人。")
        write_wav("probe.wav", pcm); print(f"✓ 已輸出 probe.wav（{len(pcm) / 2 / RATE:.1f} 秒），用 {provider()[0]}"); return
    if not a.folder:
        ap.error("請指定影片資料夾，例如 python scripts/tts.py videos/ep01")
    folder = Path(a.folder); data = load_script(folder)
    for lang in ([a.lang] if a.lang else data["langs"]):
        run(folder, data, lang, set(a.only))
    print("下一步：python scripts/render.py", folder.as_posix(), "--sheet")


if __name__ == "__main__":
    main()
