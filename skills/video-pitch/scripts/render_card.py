#!/usr/bin/env python3
"""Render a title/statement/CTA card to PNG with headless Chrome.

usage: render_card.py --out card.png --title "Text" [--subtitle S] [--kicker K] [--footer F] [--footer-right R]
                      [--logo path.png|svg] [--format landscape|vertical|square | --width W --height H]
                      [--bg #hex] [--bg2 #hex] [--fg #hex] [--muted #hex] [--accent #hex] [--font "CSS font stack"]
                      [--template assets/card.html] [--keep-html]

Fills the placeholders in assets/card.html, writes a temp HTML next to the PNG, and screenshots it
with the first browser found: $CHROME_PATH, then Chrome, Chromium, Edge, or Brave in the usual places.
Text is HTML-escaped; use --font to match the product's typeface (must be installed on this machine).
"""
from __future__ import annotations

import argparse
import base64
import html
import mimetypes
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

FORMATS = {"landscape": (1920, 1080), "vertical": (1080, 1920), "square": (1080, 1080)}
DEFAULT_STYLE = {"bg": "#0b1020", "bg2": "#1b2a4a", "fg": "#f5f7fb", "muted": "#aab4c8", "accent": "#5eb1ff",
                 "font": "Inter, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"}

BROWSER_CANDIDATES = {
    "Darwin": [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    ],
    "Linux": ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "brave-browser"],
    "Windows": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ],
}


def die(msg: str) -> None:
    print(f"render_card: {msg}", file=sys.stderr)
    sys.exit(1)


def find_browser() -> str:
    env = os.environ.get("CHROME_PATH")
    if env and (Path(env).exists() or shutil.which(env)):
        return env
    for cand in BROWSER_CANDIDATES.get(platform.system(), []):
        if Path(cand).exists():
            return cand
        found = shutil.which(cand)
        if found:
            return found
    die("no Chromium-based browser found; set CHROME_PATH to the executable")


def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def screenshot(browser: str, html_path: Path, png: Path, width: int, height: int, transparent: bool = False) -> None:
    cmd = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
           "--no-default-browser-check", "--disable-extensions", "--force-device-scale-factor=1",
           f"--window-size={width},{height}", f"--screenshot={png}", "--virtual-time-budget=1500"]
    if transparent:
        cmd.append("--default-background-color=00000000")
    cmd.append(html_path.resolve().as_uri())
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if res.returncode != 0 or not png.exists():
        die(f"browser screenshot failed ({res.returncode}): {res.stderr.strip()[-800:]}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--kicker", default="")
    ap.add_argument("--footer", default="")
    ap.add_argument("--footer-right", default="")
    ap.add_argument("--logo", type=Path)
    ap.add_argument("--format", choices=FORMATS, default="landscape")
    ap.add_argument("--width", type=int)
    ap.add_argument("--height", type=int)
    for k in DEFAULT_STYLE:
        ap.add_argument(f"--{k}", default=None)
    ap.add_argument("--template", type=Path, default=Path(__file__).resolve().parent.parent / "assets" / "card.html")
    ap.add_argument("--keep-html", action="store_true", help="leave the rendered HTML beside the PNG")
    args = ap.parse_args()

    width, height = FORMATS[args.format]
    if args.width and args.height:
        width, height = args.width, args.height
    style = {k: (getattr(args, k) or v) for k, v in DEFAULT_STYLE.items()}
    if not args.template.exists():
        die(f"template not found: {args.template}")
    if args.logo and not args.logo.exists():
        die(f"logo not found: {args.logo}")

    page = args.template.read_text(encoding="utf-8")
    fills = {
        "__WIDTH__": str(width), "__HEIGHT__": str(height),
        "__TITLE__": html.escape(args.title), "__SUBTITLE__": html.escape(args.subtitle),
        "__KICKER__": html.escape(args.kicker), "__FOOTER__": html.escape(args.footer),
        "__FOOTER_RIGHT__": html.escape(args.footer_right),
        "__LOGO__": data_uri(args.logo) if args.logo else "",
        "__LOGO_CLASS__": "" if args.logo else "hidden",
        "__BODY_CLASS__": "has-logo" if args.logo else "",
        "__KICKER_CLASS__": "" if args.kicker else "hidden",
        "__SUBTITLE_CLASS__": "" if args.subtitle else "hidden",
        "__FOOTER_CLASS__": "" if (args.footer or args.footer_right) else "hidden",
        **{f"__{k.upper()}__": v for k, v in style.items()},
    }
    for k, v in fills.items():
        page = page.replace(k, v)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    html_path = args.out.with_suffix(".html")
    html_path.write_text(page, encoding="utf-8")
    screenshot(find_browser(), html_path, args.out.resolve(), width, height)
    if not args.keep_html:
        html_path.unlink(missing_ok=True)
    print(f"wrote {args.out} ({width}x{height})")


if __name__ == "__main__":
    main()
