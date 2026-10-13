"""motion-video-skill 共用函式（tts.py / render.py / new_episode.py 都會用到）。"""
import json, shutil
from pathlib import Path

LEAD_IN, GAP, TAIL = 0.4, 0.35, 2.6          # 開頭留白、段落間隔、結尾留白（秒）
CJK = ("zh", "ja", "ko")


def say(line):   # 一行台詞可以是字串，或 [念的, 字幕顯示的]
    return line[0] if isinstance(line, list) else line


def show(line):
    return line[1] if isinstance(line, list) else line


def load_script(folder):
    f = Path(folder) / "script.json"
    if not f.exists():
        raise SystemExit(f"找不到 {f}。影片資料夾裡要有 script.json")
    data = json.loads(f.read_text(encoding="utf-8"))
    data.setdefault("langs", ["zh"])
    data.setdefault("size", [1080, 1920] if data.get("format") == "shorts" else [1920, 1080])
    for sc in data["scenes"]:
        for lang in data["langs"]:
            if lang not in sc:
                raise SystemExit(f"script.json 的 {sc.get('id')} 少了 {lang} 台詞")
    return data


def weight(line, lang):
    s = say(line)
    return max(1, len(s.replace(" ", "")) if lang in CJK else len(s))


def split_lines(sc_lines, lang, start, dur):
    """依字數比例，把一段音檔的長度分給每一句台詞。"""
    ws = [weight(l, lang) for l in sc_lines]; out, t = [], start
    for l, w in zip(sc_lines, ws):
        d = dur * w / sum(ws)
        out.append({"text": say(l), "sub": show(l), "start": round(t, 3), "end": round(t + d, 3)}); t += d
    return out


def estimate(data, lang):
    """還沒配音時，用語速估計時間軸（中文每秒 4.6 字、英文每秒 14.5 字元）。"""
    rate = 4.6 if lang in CJK else 14.5
    t = LEAD_IN; tl = {"lang": lang, "estimated": True, "scenes": []}
    for sc in data["scenes"]:
        n = sum(weight(l, lang) for l in sc[lang])
        dur = n / rate + 0.3 * (len(sc[lang]) - 1)
        tl["scenes"].append({"id": sc["id"], "start": round(t, 3), "dur": round(dur, 3), "lines": split_lines(sc[lang], lang, t, dur)})
        t += dur + GAP
    tl["total"] = round(t + TAIL, 3)
    return tl


def load_tl(folder, data, lang):
    f = Path(folder) / f"timeline_{lang}.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else estimate(data, lang)


def write_tl_js(folder, data):
    """產生 _tl.js：瀏覽器直接開 index.html 預覽時用。"""
    tls = {l: load_tl(folder, data, l) for l in data["langs"]}
    meta = dict(data.get("meta", {})); meta["langs"] = data["langs"]
    js = "window.TIMELINES=" + json.dumps(tls, ensure_ascii=False) + ";\nwindow.META=" + json.dumps(meta, ensure_ascii=False) + ";\n"
    (Path(folder) / "_tl.js").write_text(js, encoding="utf-8")
    return tls, meta


def ffmpeg_exe():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        raise SystemExit("找不到 ffmpeg。請執行：pip install imageio-ffmpeg（或自行安裝 ffmpeg）")
