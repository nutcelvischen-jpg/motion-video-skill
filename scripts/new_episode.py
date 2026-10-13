#!/usr/bin/env python3
"""Create a new video folder from a template.

Usage:
  python scripts/new_episode.py videos/ep01 --template shorts   # vertical 1080×1920 hand-drawn short
  python scripts/new_episode.py videos/demo --template wide     # horizontal 1920×1080 premium explainer
  python scripts/new_episode.py videos/ep01 --update            # refresh _runtime only (keeps your index.html / script.json)
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
        copy_runtime(dst, t); print("✓ Updated", dst / "_runtime"); return
    if not a.template:
        ap.error("Use --template shorts or --template wide")
    if (dst / "index.html").exists() and not a.force:
        raise SystemExit(f"{dst} already has a video (add --force to overwrite)")
    dst.mkdir(parents=True, exist_ok=True)
    src = TPL / a.template
    for f in ("index.html", "script.json"):
        shutil.copy2(src / f, dst / f)
    if (src / "assets").exists():
        shutil.copytree(src / "assets", dst / "assets", dirs_exist_ok=True)
    copy_runtime(dst, a.template)
    write_tl_js(dst, load_script(dst))
    print(f"✓ Created {dst} (template: {a.template})")
    print("  1. Edit the lines in script.json")
    print("  2. Edit the visuals and animation in index.html")
    print(f"  3. Preview: python scripts/render.py {dst.as_posix()} --preview, then open index.html?play in a browser")


if __name__ == "__main__":
    main()
