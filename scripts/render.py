#!/usr/bin/env python3
"""Screenshot the HTML animation frame by frame and encode it to MP4.

Usage:
  python scripts/render.py videos/ep01 --preview          # only refresh _tl.js, then open index.html?play in a browser
  python scripts/render.py videos/ep01 --sheet            # one still per subtitle line, tiled into a contact sheet
  python scripts/render.py videos/ep01 --stills 1.5,8,12  # stills at specific seconds
  python scripts/render.py videos/ep01 --lang zh          # render (muxes narration if present, else a silent preview)

Output: <video folder>/out/<folder>_<lang>.mp4; stills in <video folder>/stills/
Requires: pip install playwright imageio-ffmpeg && python -m playwright install chromium
"""
import argparse, json, shutil, subprocess, sys, tempfile
from multiprocessing import Process
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mvlib import load_script, write_tl_js, ffmpeg_exe  # noqa: E402


def open_page(p, folder, lang, tls, meta, size):
    b = p.chromium.launch(args=["--allow-file-access-from-files", "--disable-web-security"])
    pg = b.new_page(viewport={"width": size[0], "height": size[1]})
    pg.add_init_script("window.LANG=%s;window.TIMELINES=%s;window.META=%s;" % (
        json.dumps(lang), json.dumps(tls, ensure_ascii=False), json.dumps(meta, ensure_ascii=False)))
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto((Path(folder) / "index.html").resolve().as_uri())
    try:
        pg.wait_for_function("window.__ready !== undefined", timeout=20000)
        pg.evaluate("window.__ready")
    except Exception:
        raise SystemExit("The page failed to start. JavaScript errors:\n  " + "\n  ".join(errors or ["(no message; open index.html in a browser and check the Console)"]))
    if errors:
        print("⚠ JavaScript errors on the page:\n  " + "\n  ".join(errors))
    return b, pg


def worker(folder, lang, tls, meta, size, f0, f1, fps, crf, out):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b, pg = open_page(p, folder, lang, tls, meta, size)
        ff = subprocess.Popen([ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-i", "-",
                               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(crf), "-preset", "medium", out], stdin=subprocess.PIPE)
        for f in range(f0, f1):
            pg.evaluate(f"__seek({f / fps})")
            ff.stdin.write(pg.screenshot(type="jpeg", quality=90))
            if (f - f0) % 150 == 0:
                print(f"  {lang} frame {f}/{f1}", flush=True)
        ff.stdin.close(); ff.wait(); b.close()


def stills(folder, lang, tls, meta, size, times, sheet=False):
    from playwright.sync_api import sync_playwright
    sd = Path(folder) / "stills"; sd.mkdir(exist_ok=True)
    for old in sd.glob(f"{lang}_*.png"):
        old.unlink()
    with sync_playwright() as p:
        b, pg = open_page(p, folder, lang, tls, meta, size)
        for i, t in enumerate(times):
            pg.evaluate(f"__seek({t})")
            pg.screenshot(path=str(sd / f"{lang}_{i:03d}.png"))
        b.close()
    if sheet:
        cols = 4 if size[0] > size[1] else 6
        w = 480 if size[0] > size[1] else 270
        h = round(w * size[1] / size[0])
        rows = (len(times) + cols - 1) // cols
        out = sd / f"sheet_{lang}.png"
        subprocess.run([ffmpeg_exe(), "-y", "-loglevel", "error", "-i", str(sd / f"{lang}_%03d.png"),
                        "-vf", f"scale={w}:{h},tile={cols}x{rows}:padding=6:color=white", "-frames:v", "1", str(out)], check=True)
        print("→ Contact sheet:", out)
    else:
        print("→ Stills in:", sd)


def main():
    ap = argparse.ArgumentParser(description="Render a motion video")
    ap.add_argument("folder", help="video folder (contains index.html and script.json)")
    ap.add_argument("--lang", help="language code; defaults to the first language in script.json")
    ap.add_argument("--preview", action="store_true", help="only refresh _tl.js")
    ap.add_argument("--sheet", action="store_true", help="one still at the end of each line, tiled into a contact sheet")
    ap.add_argument("--stills", help="stills at given seconds, e.g. 1,5.5,10")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--workers", type=int, default=2, help="parallel browsers (use 1 on slow machines)")
    ap.add_argument("--crf", type=int, default=26, help="quality: lower = sharper and bigger (18-30)")
    a = ap.parse_args()

    folder = Path(a.folder)
    data = load_script(folder)
    lang = a.lang or data["langs"][0]
    if lang not in data["langs"]:
        raise SystemExit(f"'{lang}' is not in script.json langs")
    tls, meta = write_tl_js(folder, data)
    tl = tls[lang]; size = data["size"]
    note = " (estimated, no narration yet)" if tl.get("estimated") else ""
    print(f"▶ {folder.name} {lang}: {tl['total']:.1f}s{note}, {size[0]}×{size[1]}")
    if a.preview:
        print(f"→ _tl.js updated. Open in a browser: {(folder / 'index.html').resolve().as_uri()}?play&lang={lang}")
        return
    if a.sheet or a.stills:
        times = [float(x) for x in a.stills.split(",")] if a.stills else \
            [round(ln["end"] - 0.15, 2) for sc in tl["scenes"] for ln in sc["lines"]] + [round(tl["total"] - 0.3, 2)]
        stills(folder, lang, tls, meta, size, times, sheet=a.sheet)
        return

    n = int(tl["total"] * a.fps); k = max(1, a.workers)
    tmp = Path(tempfile.mkdtemp())
    bounds = [(i * n // k, (i + 1) * n // k) for i in range(k)]
    procs = [Process(target=worker, args=(str(folder), lang, tls, meta, size, f0, f1, a.fps, a.crf, str(tmp / f"part{i}.mp4")))
             for i, (f0, f1) in enumerate(bounds)]
    [p.start() for p in procs]; [p.join() for p in procs]
    if any(p.exitcode for p in procs):
        raise SystemExit("Render failed; see the errors above.")
    (tmp / "list.txt").write_text("".join(f"file '{(tmp / f'part{i}.mp4').as_posix()}'\n" for i in range(k)), encoding="utf-8")
    silent = tmp / "video.mp4"
    subprocess.run([ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"), "-c", "copy", str(silent)], check=True)
    out_dir = folder / "out"; out_dir.mkdir(exist_ok=True)
    nar = folder / f"narration_{lang}.wav"; bgm = folder / "bgm.mp3"
    if nar.exists() and not tl.get("estimated"):
        out = out_dir / f"{folder.name}_{lang}.mp4"
        cmd = [ffmpeg_exe(), "-y", "-loglevel", "error", "-i", str(silent), "-i", str(nar)]
        if bgm.exists():   # mix in background music at low volume
            cmd += ["-stream_loop", "-1", "-i", str(bgm), "-filter_complex",
                    "[2:a]volume=-22dB[b];[1:a][b]amix=inputs=2:duration=first:normalize=0[a]", "-map", "0:v", "-map", "[a]"]
        else:
            cmd += ["-map", "0:v", "-map", "1:a"]
        subprocess.run(cmd + ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", str(out)], check=True)
    else:
        out = out_dir / f"{folder.name}_{lang}_silent.mp4"
        shutil.move(str(silent), str(out))
        print("(no narration yet, so this is a silent preview)")
    print("✓ Done:", out)


if __name__ == "__main__":
    main()
