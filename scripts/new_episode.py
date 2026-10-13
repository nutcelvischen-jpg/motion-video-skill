#!/usr/bin/env python3
"""從範本建立一支新影片的資料夾。

用法：
  python scripts/new_episode.py videos/ep01 --template shorts   # 直式 1080×1920 手繪短影音
  python scripts/new_episode.py videos/demo --template wide     # 橫式 1920×1080 高級感簡報片
  python scripts/new_episode.py videos/ep01 --update            # 只更新 _runtime（不動你的 index.html / script.json）
"""
import argparse, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mvlib import load_script, write_tl_js  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
TPL = SKILL / "templates"


def copy_runtime(dst, template):
    rt = dst / "_runtime"; rt.mkdir(parents=True, exist_ok=True)
    for f in (TPL / "_common").iterdir():
        shutil.copy2(f, rt / f.name)
    for name in ("runtime.js", "runtime.css"):
        shutil.copy2(TPL / template / name, rt / name)
    (rt / "TEMPLATE").write_text(template, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"); ap.add_argument("--template", choices=["shorts", "wide"])
    ap.add_argument("--update", action="store_true"); ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    dst = Path(a.folder)
    if a.update:
        t = (dst / "_runtime" / "TEMPLATE").read_text(encoding="utf-8").strip()
        copy_runtime(dst, t); print("✓ 已更新", dst / "_runtime"); return
    if not a.template:
        ap.error("請用 --template shorts 或 --template wide")
    if (dst / "index.html").exists() and not a.force:
        raise SystemExit(f"{dst} 已經有影片了（要覆蓋請加 --force）")
    dst.mkdir(parents=True, exist_ok=True)
    src = TPL / a.template
    for f in ("index.html", "script.json"):
        shutil.copy2(src / f, dst / f)
    if (src / "assets").exists():
        shutil.copytree(src / "assets", dst / "assets", dirs_exist_ok=True)
    copy_runtime(dst, a.template)
    write_tl_js(dst, load_script(dst))
    print(f"✓ 已建立 {dst}（範本：{a.template}）")
    print("  1. 改 script.json 的台詞")
    print("  2. 改 index.html 的畫面與動畫")
    print(f"  3. 預覽：python scripts/render.py {dst.as_posix()} --preview，再用瀏覽器開 index.html?play")


if __name__ == "__main__":
    main()
