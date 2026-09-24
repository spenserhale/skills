#!/usr/bin/env python3
"""Assemble cards, demo clips, narration, captions, and a poster into the final pitch video.

usage: assemble.py MANIFEST.json --out OUTDIR [--stills] [--draft] [--name pitch]

MANIFEST.json shape (paths are relative to the manifest's directory):
  {
    "format": "landscape" | "vertical" | "square" | {"width": 1920, "height": 1080},
    "fps": 30,
    "timing": "work/timing.json",         from narrate.py; beat durations come from here
    "marks": "work/marks.json",           from record_web_demo.mjs; lets "in"/"out" name a mark
    "narration": "work/narration.wav",
    "captions": "work/captions.srt",      omit or set "burn_captions": false to skip burn-in
    "caption_style": {"font": "...", "size": 44, "fg": "#fff", "box": "rgba(0,0,0,.62)", "margin": 70},
    "music": {"path": "bed.mp3", "gain_db": -20, "fade": 1.5},     optional
    "transition": {"type": "fade", "duration": 0.35},               or {"type": "cut"}; default fade
    "background": "#0b1020",             pad colour for demo clips
    "poster": {"beat": "what", "offset": 0.6},                      or {"time": 4.2}; default: 2nd beat + 0.5;
                                                                    taken before captions unless "with_captions": true
    "beats": [
      {"id": "hook", "kind": "card", "src": "work/cards/hook.png", "motion": "zoom"},        motion: zoom | none
      {"id": "how", "kind": "scene", "src": "work/how.html"},                                  HTML rendered frame-exactly by render_scene.mjs
      {"id": "demo", "kind": "video", "src": "work/demo.webm", "in": {"mark": "flow-start"}, "out": {"mark": "end"},
       "fit": "auto" | "speed" | "trim" | "hold", "crop": {"x":0,"y":0,"w":800,"h":450}, "inset": 0.05},
      {"id": "cta", "kind": "card", "src": "work/cards/cta.png", "duration": 3.0}           duration only when no timing entry
    ]
  }
Every beat id should exist in timing.json (its narration sets the visual duration). A beat without
narration needs an explicit "duration". "in"/"out" take seconds or {"mark": name} resolved from "marks",
so re-recording never leaves stale cut points; "out" defaults to the clip end. "fit" decides what happens when the demo clip is longer or
shorter than its beat: auto speeds it between 0.6x and 2.5x, otherwise trims and holds the last frame.

Writes OUTDIR/<name>.mp4 (H.264 + AAC, poster baked as frame 0), OUTDIR/<name>.jpg, and with
--stills OUTDIR/work/stills.png, a contact sheet to review before calling it done.
Captions are rendered as transparent PNGs with headless Chrome and overlaid, because ffmpeg builds
without libass or freetype are common; nothing here needs those.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_card import find_browser, screenshot  # noqa: E402

FORMATS = {"landscape": (1920, 1080), "vertical": (1080, 1920), "square": (1080, 1080)}
CAPTION_STYLE = {"font": "Inter, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif", "size": 44,
                 "fg": "#ffffff", "box": "rgba(0,0,0,.62)", "margin": 70}


def die(msg: str) -> None:
    print(f"assemble: {msg}", file=sys.stderr)
    sys.exit(1)


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        die(f"command failed: {' '.join(str(c) for c in cmd)}\n{res.stderr.strip()[-2500:]}")
    return res


def ffprobe_duration(path: Path) -> float:
    res = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)])
    return float(res.stdout.strip())


def parse_srt(path: Path) -> list[tuple[float, float, str]]:
    def t(s: str) -> float:
        h, m, rest = s.split(":")
        sec, ms = rest.split(",")
        return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000
    cues = []
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8").strip()):
        lines = block.strip().splitlines()
        if len(lines) < 3:
            continue
        m = re.match(r"(\S+)\s+-->\s+(\S+)", lines[1])
        if not m:
            continue
        cues.append((t(m.group(1)), t(m.group(2)), "\n".join(lines[2:])))
    return cues


class Assembler:
    def __init__(self, manifest: Path, out: Path, draft: bool, name: str):
        self.base = manifest.parent
        try:
            self.m = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            die(f"cannot read {manifest}: {e}")
        self.out = out
        self.work = out / "work" / "assemble"
        self.work.mkdir(parents=True, exist_ok=True)
        self.draft = draft
        self.name = name
        fmt = self.m.get("format", "landscape")
        self.w, self.h = FORMATS[fmt] if isinstance(fmt, str) else (int(fmt["width"]), int(fmt["height"]))
        self.fps = int(self.m.get("fps", 30))
        self.bg = self.m.get("background", "#0b1020")
        tr = self.m.get("transition") or {"type": "fade", "duration": 0.35}
        self.td = float(tr.get("duration", 0.35)) if tr.get("type", "fade") != "cut" else 0.0
        self.marks = {}
        if self.m.get("marks"):
            self.marks = json.loads(self.path(self.m["marks"]).read_text(encoding="utf-8"))
        self.timing = {}
        if self.m.get("timing"):
            tj = json.loads(self.path(self.m["timing"]).read_text(encoding="utf-8"))
            self.timing = {b["id"]: b for b in tj["beats"]}
        self.beats = self.m.get("beats") or die("manifest has no beats")
        self.durations: list[float] = []
        for b in self.beats:
            if b["id"] in self.timing:
                self.durations.append(float(self.timing[b["id"]]["duration"]))
            elif "duration" in b:
                self.durations.append(float(b["duration"]))
            else:
                die(f"beat {b['id']} has no timing entry and no duration")
        # narrate.py puts a short lead-in before the first beat; the first visual covers it so every
        # later beat starts exactly where its narration does and the video is as long as the audio.
        if self.beats[0]["id"] in self.timing:
            self.durations[0] += float(self.timing[self.beats[0]["id"]].get("start", 0))
        self.total = sum(self.durations)
        self.enc = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast" if draft else "medium",
                    "-crf", "23" if draft else "18"]

    def path(self, p: str) -> Path:
        q = Path(p)
        q = q if q.is_absolute() else (self.base / q)
        if not q.exists():
            die(f"file not found: {q}")
        return q

    def cut_point(self, beat: dict, key: str, default: float) -> float:
        v = beat.get(key)
        if v is None:
            return default
        if isinstance(v, dict):
            name = v.get("mark")
            if name not in self.marks:
                die(f"beat {beat['id']}: mark '{name}' not in marks file (have: {', '.join(self.marks) or 'none'})")
            return float(self.marks[name]) + float(v.get("offset", 0))
        return float(v)

    # ------------------------------------------------------------ segments
    def segment(self, i: int, beat: dict) -> Path:
        # Each segment is extended by the transition length so cross-fades do not shift beat starts.
        dur = self.durations[i] + (self.td if i < len(self.beats) - 1 else 0)
        dst = self.work / f"seg-{i:02d}-{beat['id']}.mp4"
        src = self.path(beat["src"])
        kind = beat.get("kind")
        if not kind:
            kind = {".webm": "video", ".mp4": "video", ".mov": "video", ".mkv": "video", ".html": "scene", ".htm": "scene"}.get(src.suffix.lower(), "card")
        frames = max(1, round(dur * self.fps))
        if kind == "scene":
            script = Path(__file__).resolve().parent / "render_scene.mjs"
            run(["node", str(script), str(src), "--duration", f"{dur:.3f}", "--fps", str(self.fps),
                 "--width", str(self.w), "--height", str(self.h), "--out", str(dst)])
            return dst
        if kind == "card":
            if beat.get("motion", "zoom") == "zoom":
                vf = (f"scale={self.w * 2}:{self.h * 2},zoompan=z='min(1+0.00035*on,1.06)':d={frames}"
                      f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={self.w}x{self.h}:fps={self.fps}")
                run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(src), "-vf", vf,
                     "-frames:v", str(frames), "-r", str(self.fps), *self.enc, "-an", str(dst)])
            else:
                run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(self.fps), "-i", str(src),
                     "-vf", f"scale={self.w}:{self.h}:force_original_aspect_ratio=decrease,pad={self.w}:{self.h}:(ow-iw)/2:(oh-ih)/2:color={self.bg}",
                     "-t", f"{dur:.3f}", *self.enc, "-an", str(dst)])
            return dst

        clip_in = self.cut_point(beat, "in", 0.0)
        clip_out = self.cut_point(beat, "out", ffprobe_duration(src))
        src_len = max(0.05, clip_out - clip_in)
        fit = beat.get("fit", "auto")
        ratio = src_len / dur  # >1 means the clip is longer than the beat
        filters = [f"fps={self.fps}"]
        if beat.get("crop"):
            c = beat["crop"]
            filters.append(f"crop={c['w']}:{c['h']}:{c['x']}:{c['y']}")
        if fit == "speed" or (fit == "auto" and 0.4 <= ratio <= 2.5):
            filters.append(f"setpts={1 / ratio:.5f}*PTS")
            if abs(ratio - 1) > 0.02:
                print(f"  {beat['id']}: clip {src_len:.1f}s fitted to {dur:.1f}s at {ratio:.2f}x")
        elif ratio < 1:
            filters.append(f"tpad=stop_mode=clone:stop_duration={dur - src_len + 0.5:.3f}")
            print(f"  {beat['id']}: clip {src_len:.1f}s shorter than beat {dur:.1f}s, holding last frame")
        else:
            print(f"  {beat['id']}: clip {src_len:.1f}s trimmed to beat {dur:.1f}s")
        inset = float(beat.get("inset", 0))
        tw, th = int(self.w * (1 - 2 * inset)) // 2 * 2, int(self.h * (1 - 2 * inset)) // 2 * 2
        filters.append(f"scale={tw}:{th}:force_original_aspect_ratio=decrease:flags=lanczos")
        filters.append(f"pad={self.w}:{self.h}:(ow-iw)/2:(oh-ih)/2:color={self.bg}")
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{clip_in:.3f}", "-t", f"{src_len:.3f}", "-i", str(src),
             "-vf", ",".join(filters), "-t", f"{dur:.3f}", "-r", str(self.fps), *self.enc, "-an", str(dst)])
        return dst

    def join(self, segs: list[Path]) -> Path:
        dst = self.work / "video.mp4"
        if len(segs) == 1 or self.td == 0:
            lst = self.work / "concat.txt"
            lst.write_text("".join(f"file '{s.resolve()}'\n" for s in segs))
            run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(dst)])
            return dst
        inputs: list[str] = []
        for s in segs:
            inputs += ["-i", str(s)]
        chain, prev, offset = [], "[0:v]", 0.0
        for i in range(1, len(segs)):
            offset += self.durations[i - 1]
            label = f"[x{i}]" if i < len(segs) - 1 else "[v]"
            chain.append(f"{prev}[{i}:v]xfade=transition=fade:duration={self.td}:offset={offset:.3f}{label}")
            prev = label
        run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(chain), "-map", "[v]",
             "-r", str(self.fps), *self.enc, "-an", str(dst)])
        return dst

    # ------------------------------------------------------------ captions
    def caption_pngs(self) -> list[tuple[float, float, Path]]:
        if not self.m.get("captions") or self.m.get("burn_captions") is False:
            return []
        cues = parse_srt(self.path(self.m["captions"]))
        style = {**CAPTION_STYLE, **(self.m.get("caption_style") or {})}
        if self.h > self.w:
            style = {**style, "size": int(style["size"] * 0.9), "margin": int(self.h * 0.16)}
        tpl_path = Path(__file__).resolve().parent.parent / "assets" / "caption.html"
        tpl = tpl_path.read_text(encoding="utf-8")
        browser = find_browser()
        cap_dir = self.work / "captions"
        cap_dir.mkdir(exist_ok=True)
        out = []
        for i, (start, end, text) in enumerate(cues):
            png = cap_dir / f"cap-{i:03d}.png"
            page = tpl
            for k, v in {"__WIDTH__": str(self.w), "__HEIGHT__": str(self.h), "__MARGIN__": str(style["margin"]),
                         "__FONT__": style["font"], "__FONT_SIZE__": str(style["size"]), "__FG__": style["fg"],
                         "__BOX__": style["box"], "__TEXT__": html.escape(text)}.items():
                page = page.replace(k, v)
            html_path = png.with_suffix(".html")
            html_path.write_text(page, encoding="utf-8")
            screenshot(browser, html_path, png, self.w, self.h, transparent=True)
            html_path.unlink(missing_ok=True)
            out.append((start, end, png))
        return out

    # ------------------------------------------------------------ mix + finish
    def finish(self, video: Path, captions: list[tuple[float, float, Path]]) -> Path:
        inputs = ["-i", str(video)]
        fc: list[str] = []
        vlabel = "[0:v]"
        for i, (start, end, png) in enumerate(captions):
            inputs += ["-i", str(png)]
            nxt = f"[c{i}]"
            fc.append(f"{vlabel}[{i + 1}:v]overlay=0:0:enable='between(t,{start:.3f},{end:.3f})'{nxt}")
            vlabel = nxt
        fc.append(f"{vlabel}fade=t=in:st=0:d=0.3,fade=t=out:st={self.total - 0.5:.3f}:d=0.5[vout]")

        audio_idx = len(inputs) // 2
        alabels = []
        if self.m.get("narration"):
            inputs += ["-i", str(self.path(self.m["narration"]))]
            fc.append(f"[{audio_idx}:a]apad=whole_dur={self.total:.3f},atrim=0:{self.total:.3f}[nar]")
            alabels.append("[nar]")
            audio_idx += 1
        if self.m.get("music"):
            mu = self.m["music"]
            inputs += ["-stream_loop", "-1", "-i", str(self.path(mu["path"]))]
            gain = float(mu.get("gain_db", -20))
            fade = float(mu.get("fade", 1.5))
            fc.append(f"[{audio_idx}:a]atrim=0:{self.total:.3f},volume={gain}dB,afade=t=in:st=0:d={fade},"
                      f"afade=t=out:st={self.total - fade:.3f}:d={fade}[mus]")
            alabels.append("[mus]")
        if len(alabels) == 2:
            fc.append("[mus][nar]sidechaincompress=threshold=0.05:ratio=6:attack=40:release=400[duck];"
                      "[duck][nar]amix=inputs=2:duration=first:normalize=0[aout]")
        elif alabels:
            fc.append(f"{alabels[0]}acopy[aout]")

        dst = self.out / f"{self.name}.mp4"
        cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(fc), "-map", "[vout]"]
        if alabels:
            cmd += ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
        cmd += [*self.enc, "-movflags", "+faststart", "-t", f"{self.total:.3f}", str(dst)]
        run(cmd)
        return dst

    def poster(self, video: Path, clean: Path) -> Path:
        spec = self.m.get("poster") or {}
        source = video if spec.get("with_captions") else clean
        if "time" in spec:
            t = float(spec["time"])
        else:
            beat_id = spec.get("beat") or (self.beats[1]["id"] if len(self.beats) > 1 else self.beats[0]["id"])
            idx = next((i for i, b in enumerate(self.beats) if b["id"] == beat_id), 0)
            t = sum(self.durations[:idx]) + float(spec.get("offset", 0.5))
        t = min(max(0.0, t), max(0.0, self.total - 0.1))
        jpg = self.out / f"{self.name}.jpg"
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(source), "-frames:v", "1", "-q:v", "2", str(jpg)])
        baked = self.work / "baked.mp4"
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(jpg), "-filter_complex",
             "[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]", "-map", "[v]", "-map", "0:a?", *self.enc,
             "-c:a", "copy", "-movflags", "+faststart", str(baked)])
        shutil.move(str(baked), str(video))
        print(f"poster from {t:.2f}s -> {jpg}, baked as frame 0")
        return jpg

    def stills(self, video: Path) -> Path:
        png = self.out / "work" / "stills.png"
        n = max(4, min(16, int(self.total / 1.5)))
        cols = 4
        rows = -(-n // cols)
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-vf",
             f"fps={n / self.total:.4f},scale=480:-1,tile={cols}x{rows}:padding=6:color=black", "-frames:v", "1", str(png)])
        print(f"stills -> {png} ({n} frames)")
        return png


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--name", default="pitch", help="output base name (pitch.mp4, pitch.jpg)")
    ap.add_argument("--stills", action="store_true", help="also write a contact sheet for review")
    ap.add_argument("--draft", action="store_true", help="fast, lower-quality encode for iteration")
    args = ap.parse_args()
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            die(f"{tool} not found on PATH")

    a = Assembler(args.manifest, args.out, args.draft, args.name)
    print(f"{len(a.beats)} beats, {a.total:.1f}s, {a.w}x{a.h}@{a.fps}")
    segs = [a.segment(i, b) for i, b in enumerate(a.beats)]
    video = a.join(segs)
    caps = a.caption_pngs()
    final = a.finish(video, caps)
    a.poster(final, clean=video)
    if args.stills:
        a.stills(final)
    print(f"wrote {final} ({ffprobe_duration(final):.1f}s)")


if __name__ == "__main__":
    main()
