#!/usr/bin/env python3
"""Build a self-playing fake terminal page from a JSON script, for recording a CLI demo.

usage: build_terminal_page.py STEPS.json --out terminal.html [--format landscape|vertical|square | --width W --height H]
                              [--title "zsh"] [--bg #hex] [--prompt-color #hex] [--font-size 26]

STEPS.json shape:
  {"prompt": "$ ", "lead_in": 0.8, "tail": 1.5,
   "steps": [
     {"cmd": "vip domain launch example.com", "type_ms": 45, "delay": 0.4,
      "output": ["Verifying DNS ... ok", {"text": "Issued certificate", "class": "ok"}], "line_ms": 70, "pause": 0.8}
   ]}
Each step types the command, waits `delay`, prints output lines `line_ms` apart, then waits `pause`.
Classes: o (default), ok, warn, err, dim. Omit `cmd` to print output only.

Prints the estimated play time so the recording can be sized. Record the page with the browser
recorder (playwright-cli `video-start`, see references/record.md); `document.title` becomes "done" when finished.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FORMATS = {"landscape": (1920, 1080), "vertical": (1080, 1920), "square": (1080, 1080)}


def die(msg: str) -> None:
    print(f"build_terminal_page: {msg}", file=sys.stderr)
    sys.exit(1)


def estimate(script: dict) -> float:
    t = float(script.get("lead_in", 0.8))
    for s in script.get("steps", []):
        if "cmd" in s:
            t += len(s["cmd"]) * float(s.get("type_ms", 45)) / 1000
        t += float(s.get("delay", 0.35))
        out = s.get("output") or []
        lines = out if isinstance(out, list) else str(out).split("\n")
        t += len(lines) * float(s.get("line_ms", 70)) / 1000
        t += float(s.get("pause", 0.6))
    return t + float(script.get("tail", 1.5))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("steps", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--format", choices=FORMATS, default="landscape")
    ap.add_argument("--width", type=int)
    ap.add_argument("--height", type=int)
    ap.add_argument("--title", default="zsh")
    ap.add_argument("--bg", default="#0b1020")
    ap.add_argument("--prompt-color", default="#5eb1ff")
    ap.add_argument("--font-size", type=int, default=None, help="default: 26 landscape, 22 vertical")
    ap.add_argument("--template", type=Path, default=Path(__file__).resolve().parent.parent / "assets" / "terminal.html")
    args = ap.parse_args()

    try:
        script = json.loads(args.steps.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        die(f"cannot read {args.steps}: {e}")
    if not script.get("steps"):
        die("script has no steps")
    width, height = FORMATS[args.format]
    if args.width and args.height:
        width, height = args.width, args.height
    font_size = args.font_size or (22 if height > width else 26)

    page = args.template.read_text(encoding="utf-8")
    for k, v in {"__WIDTH__": str(width), "__HEIGHT__": str(height), "__BG__": args.bg,
                 "__PROMPT_COLOR__": args.prompt_color, "__FONT_SIZE__": str(font_size),
                 "__TITLE__": args.title.replace("<", "&lt;"),
                 "__SCRIPT_JSON__": json.dumps(script).replace("</", "<\\/")}.items():
        page = page.replace(k, v)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(page, encoding="utf-8")
    print(f"wrote {args.out} ({width}x{height}); plays for about {estimate(script):.1f}s")


if __name__ == "__main__":
    main()
