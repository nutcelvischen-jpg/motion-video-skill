#!/usr/bin/env python3
"""把 HTML 動畫逐格截圖，合成 MP4。

用法：
  python scripts/render.py videos/ep01 --preview          # 只更新 _tl.js，之後用瀏覽器開 index.html?play 預覽
  python scripts/render.py videos/ep01 --sheet            # 每句台詞截一張圖，拼成一張檢查用的總覽圖
  python scripts/render.py videos/ep01 --stills 1.5,8,12  # 指定秒數截圖
  python scripts/render.py videos/ep01 --lang zh          # 渲染影片（有配音就合成，沒有就輸出無聲預覽）

輸出：<影片資料夾>/out/<資料夾名>_<語言>.mp4；截圖在 <影片資料夾>/stills/
需求：pip install playwright imageio-ffmpeg && python -m playwright install chromium
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
        raise SystemExit("頁面沒有正常啟動。JavaScript 錯誤：\n  " + "\n  ".join(errors or ["（無訊息，請用瀏覽器開 index.html 看 Console）"]))
    if errors:
        print("⚠ 頁面有 JavaScript 錯誤：\n  " + "\n  ".join(errors))
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
                print(f"  {lang} 第 {f}/{f1} 格", flush=True)
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
        print("→ 總覽圖：", out)
    else:
        print("→ 截圖在：", sd)


def main():
    ap = argparse.ArgumentParser(description="渲染 motion video")
    ap.add_argument("folder", help="影片資料夾（裡面有 index.html、script.json）")
    ap.add_argument("--lang", help="語言代碼，預設是 script.json 的第一個語言")
    ap.add_argument("--preview", action="store_true", help="只更新 _tl.js")
    ap.add_argument("--sheet", action="store_true", help="每句台詞結尾截一張，拼成總覽圖")
    ap.add_argument("--stills", help="指定秒數截圖，例如 1,5.5,10")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--workers", type=int, default=2, help="同時開幾個瀏覽器渲染（電腦慢就設 1）")
    ap.add_argument("--crf", type=int, default=26, help="畫質，數字越小越清楚、檔案越大（18~30）")
    a = ap.parse_args()

    folder = Path(a.folder)
    data = load_script(folder)
    lang = a.lang or data["langs"][0]
    if lang not in data["langs"]:
        raise SystemExit(f"script.json 的 langs 沒有 {lang}")
    tls, meta = write_tl_js(folder, data)
    tl = tls[lang]; size = data["size"]
    note = "（估計值，尚未配音）" if tl.get("estimated") else ""
    print(f"▶ {folder.name} {lang}：{tl['total']:.1f} 秒{note}，{size[0]}×{size[1]}")
    if a.preview:
        print(f"→ 已更新 _tl.js。用瀏覽器開：{(folder / 'index.html').resolve().as_uri()}?play&lang={lang}")
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
        raise SystemExit("渲染失敗，請看上面的錯誤訊息。")
    (tmp / "list.txt").write_text("".join(f"file '{(tmp / f'part{i}.mp4').as_posix()}'\n" for i in range(k)), encoding="utf-8")
    silent = tmp / "video.mp4"
    subprocess.run([ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"), "-c", "copy", str(silent)], check=True)
    out_dir = folder / "out"; out_dir.mkdir(exist_ok=True)
    nar = folder / f"narration_{lang}.wav"; bgm = folder / "bgm.mp3"
    if nar.exists() and not tl.get("estimated"):
        out = out_dir / f"{folder.name}_{lang}.mp4"
        cmd = [ffmpeg_exe(), "-y", "-loglevel", "error", "-i", str(silent), "-i", str(nar)]
        if bgm.exists():   # 有背景音樂就壓低音量混進去
            cmd += ["-stream_loop", "-1", "-i", str(bgm), "-filter_complex",
                    "[2:a]volume=-22dB[b];[1:a][b]amix=inputs=2:duration=first:normalize=0[a]", "-map", "0:v", "-map", "[a]"]
        else:
            cmd += ["-map", "0:v", "-map", "1:a"]
        subprocess.run(cmd + ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", str(out)], check=True)
    else:
        out = out_dir / f"{folder.name}_{lang}_silent.mp4"
        shutil.move(str(silent), str(out))
        print("（還沒有配音，輸出的是無聲預覽）")
    print("✓ 完成：", out)


if __name__ == "__main__":
    main()
