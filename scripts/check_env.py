#!/usr/bin/env python3
"""Check that your environment is ready: python scripts/check_env.py"""
import os, shutil, subprocess, sys

ok = True
def line(good, msg, fix=""):
    global ok
    ok &= good
    print(("✓ " if good else "✗ ") + msg + ("" if good else f"\n    → {fix}"))

line(sys.version_info >= (3, 9), f"Python {sys.version.split()[0]}", "Install Python 3.9 or newer")
try:
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            p.chromium.launch().close()
        line(True, "Playwright + Chromium")
    except Exception as e:
        line(False, f"Chromium failed to launch: {str(e)[:120]}", "python -m playwright install chromium")
except ImportError:
    line(False, "Playwright is not installed", "pip install playwright && python -m playwright install chromium")
ff = shutil.which("ffmpeg")
if not ff:
    try:
        import imageio_ffmpeg; ff = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass
line(bool(ff), f"ffmpeg: {ff or 'not found'}", "pip install imageio-ffmpeg")
has_key = bool(os.environ.get("OPENROUTER_API_KEY") or os.environ.get("GEMINI_API_KEY"))
print(("✓ " if has_key else "△ ") + "TTS key: " + ("set" if has_key else "not set (you can still make silent previews; see README)"))
print("\nAll set!" if ok else "\nFix the items marked → above, then run this again.")
