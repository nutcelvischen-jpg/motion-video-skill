"""Shared helpers for motion-video-skill (used by tts.py, render.py and new_episode.py)."""
import json, shutil
from pathlib import Path

LEAD_IN, GAP, TAIL = 0.4, 0.35, 2.6          # silence at start, gap between scenes, tail (seconds)
CJK = ("zh", "ja", "ko")


def say(line):   # a line is either a string, or [spoken text, subtitle text]
    return line[0] if isinstance(line, list) else line


def show(line):
    return line[1] if isinstance(line, list) else line


def load_script(folder):
    f = Path(folder) / "script.json"
    if not f.exists():
        raise SystemExit(f"Cannot find {f}. The video folder needs a script.json")
    data = json.loads(f.read_text(encoding="utf-8"))
    data.setdefault("langs", ["en"])
    data.setdefault("size", [1080, 1920] if data.get("format") == "shorts" else [1920, 1080])
    for sc in data["scenes"]:
        for lang in data["langs"]:
            if lang not in sc:
                raise SystemExit(f"Scene {sc.get('id')} in script.json has no '{lang}' lines")
    return data


def weight(line, lang):
    s = say(line)
    return max(1, len(s.replace(" ", "")) if lang in CJK else len(s))


def split_lines(sc_lines, lang, start, dur):
    """Split one scene's audio duration across its lines, proportional to text length."""
    ws = [weight(l, lang) for l in sc_lines]; out, t = [], start
    for l, w in zip(sc_lines, ws):
        d = dur * w / sum(ws)
        out.append({"text": say(l), "sub": show(l), "start": round(t, 3), "end": round(t + d, 3)}); t += d
    return out


def estimate(data, lang):
    """Before narration exists, estimate timing from speaking rate (zh 4.6 chars/s, en 14.5 chars/s)."""
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
    """Write _tl.js so index.html can be previewed directly in a browser."""
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
        raise SystemExit("ffmpeg not found. Run: pip install imageio-ffmpeg (or install ffmpeg yourself)")
