#!/usr/bin/env python3
"""檢查環境是否準備好：python scripts/check_env.py"""
import os, shutil, subprocess, sys

ok = True
def line(good, msg, fix=""):
    global ok
    ok &= good
    print(("✓ " if good else "✗ ") + msg + ("" if good else f"\n    → {fix}"))

line(sys.version_info >= (3, 9), f"Python {sys.version.split()[0]}", "請安裝 Python 3.9 以上")
try:
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            p.chromium.launch().close()
        line(True, "Playwright + Chromium")
    except Exception as e:
        line(False, f"Chromium 無法啟動：{str(e)[:120]}", "python -m playwright install chromium")
except ImportError:
    line(False, "沒有安裝 Playwright", "pip install playwright && python -m playwright install chromium")
ff = shutil.which("ffmpeg")
if not ff:
    try:
        import imageio_ffmpeg; ff = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass
line(bool(ff), f"ffmpeg：{ff or '找不到'}", "pip install imageio-ffmpeg")
has_key = bool(os.environ.get("OPENROUTER_API_KEY") or os.environ.get("GEMINI_API_KEY"))
print(("✓ " if has_key else "△ ") + "TTS 金鑰：" + ("已設定" if has_key else "未設定（不配音也能做無聲預覽；設定方式見 README）"))
print("\n全部就緒！" if ok else "\n照上面 → 的指令修好再執行一次。")
