#!/usr/bin/env python3
"""Turn a pitch script into narration audio, beat timings, and captions.

usage: narrate.py SCRIPT.json --out WORKDIR [--provider auto|say|openai|elevenlabs|kokoro]
                  [--voice NAME] [--rate WPM] [--pad SECONDS] [--min-beat SECONDS] [--lead-in SECONDS]

SCRIPT.json shape:
  {"beats": [{"id": "hook", "text": "One or two spoken sentences."}, ...],
   "voice": "Samantha", "provider": "say"}          # optional defaults, CLI flags win

Writes into WORKDIR:
  narration/<id>.wav   one clip per beat, 48 kHz mono
  narration.wav        all beats in order with pads, loudness-normalised
  timing.json          {"beats": [{"id", "text", "start", "end", "duration", "audio_duration"}], "total"}
  captions.srt         caption cues split at ~42 chars per line, timed inside each beat

Provider selection with --provider auto (the default):
  elevenlabs when ELEVENLABS_API_KEY is set, else openai when OPENAI_API_KEY is set,
  else kokoro when the kokoro_onnx package and model files are present, else macOS `say`.
Only the standard library is used; ffmpeg and ffprobe must be on PATH.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

DEFAULT_VOICES = {
    "say": "Samantha",
    "openai": "alloy",
    "elevenlabs": "21m00Tcm4TlvDq8ikWAM",  # Rachel
    "kokoro": "af_heart",
}


def die(msg: str, code: int = 1) -> None:
    print(f"narrate: {msg}", file=sys.stderr)
    sys.exit(code)


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    res = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if res.returncode != 0:
        die(f"command failed: {' '.join(cmd)}\n{res.stderr.strip()[-2000:]}")
    return res


def need(tool: str) -> None:
    if not shutil.which(tool):
        die(f"{tool} not found on PATH")


def probe_duration(path: Path) -> float:
    res = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=nw=1:nk=1", str(path)])
    return float(res.stdout.strip())


def to_wav(src: Path, dst: Path) -> None:
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
         "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", str(dst)])


# ---------------------------------------------------------------- providers

def tts_say(text: str, voice: str, rate: int | None, dst: Path) -> None:
    if platform.system() != "Darwin":
        die("provider say only exists on macOS; set OPENAI_API_KEY or ELEVENLABS_API_KEY, or install kokoro")
    aiff = dst.with_suffix(".aiff")
    cmd = ["say", "-v", voice, "-o", str(aiff)]
    if rate:
        cmd += ["-r", str(rate)]
    cmd.append(text)
    run(cmd)
    to_wav(aiff, dst)
    aiff.unlink(missing_ok=True)


def http_post(url: str, headers: dict, body: dict) -> bytes:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **headers})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:  # type: ignore[attr-defined]
        die(f"{url} returned {e.code}: {e.read()[:500]!r}")


def tts_openai(text: str, voice: str, rate: int | None, dst: Path) -> None:
    key = os.environ.get("OPENAI_API_KEY") or die("OPENAI_API_KEY not set")
    body = {"model": os.environ.get("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
            "voice": voice, "input": text, "response_format": "wav"}
    if rate:
        body["speed"] = round(max(0.25, min(4.0, rate / 150)), 2)
    raw = http_post("https://api.openai.com/v1/audio/speech", {"Authorization": f"Bearer {key}"}, body)
    tmp = dst.with_suffix(".raw.wav")
    tmp.write_bytes(raw)
    to_wav(tmp, dst)
    tmp.unlink()


def tts_elevenlabs(text: str, voice: str, rate: int | None, dst: Path) -> None:
    key = os.environ.get("ELEVENLABS_API_KEY") or die("ELEVENLABS_API_KEY not set")
    body = {"text": text, "model_id": os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")}
    if rate:
        body["voice_settings"] = {"speed": round(max(0.7, min(1.2, rate / 150)), 2)}
    raw = http_post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128",
                    {"xi-api-key": key}, body)
    tmp = dst.with_suffix(".mp3")
    tmp.write_bytes(raw)
    to_wav(tmp, dst)
    tmp.unlink()


def kokoro_available() -> bool:
    try:
        import kokoro_onnx  # noqa: F401
    except Exception:
        return False
    return bool(os.environ.get("KOKORO_MODEL")) and bool(os.environ.get("KOKORO_VOICES"))


def tts_kokoro(text: str, voice: str, rate: int | None, dst: Path) -> None:
    if not kokoro_available():
        die("kokoro needs `pip install kokoro-onnx soundfile` plus KOKORO_MODEL and KOKORO_VOICES paths")
    from kokoro_onnx import Kokoro  # type: ignore
    import soundfile  # type: ignore
    k = Kokoro(os.environ["KOKORO_MODEL"], os.environ["KOKORO_VOICES"])
    samples, sr = k.create(text, voice=voice, speed=(rate / 150) if rate else 1.0, lang="en-us")
    tmp = dst.with_suffix(".raw.wav")
    soundfile.write(str(tmp), samples, sr)
    to_wav(tmp, dst)
    tmp.unlink()


PROVIDERS = {"say": tts_say, "openai": tts_openai, "elevenlabs": tts_elevenlabs, "kokoro": tts_kokoro}


def pick_provider(requested: str) -> str:
    if requested != "auto":
        return requested
    if os.environ.get("ELEVENLABS_API_KEY"):
        return "elevenlabs"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if kokoro_available():
        return "kokoro"
    if platform.system() == "Darwin":
        return "say"
    die("no TTS provider: set OPENAI_API_KEY or ELEVENLABS_API_KEY, install kokoro, or run on macOS")


# ---------------------------------------------------------------- captions

def split_caption_lines(text: str, max_chars: int = 42, max_lines: int = 2) -> list[str]:
    """Greedy split into cues of up to max_lines lines, each <= max_chars."""
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_chars:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    cues = ["\n".join(lines[i:i + max_lines]) for i in range(0, len(lines), max_lines)]
    return cues


def srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def write_srt(beats: list[dict], path: Path) -> None:
    n = 0
    out: list[str] = []
    for b in beats:
        cues = split_caption_lines(b["text"])
        words_total = sum(len(c.split()) for c in cues) or 1
        t = b["start"]
        for cue in cues:
            share = len(cue.split()) / words_total
            dur = b["audio_duration"] * share
            n += 1
            out.append(f"{n}\n{srt_time(t)} --> {srt_time(t + dur)}\n{cue}\n")
            t += dur
    path.write_text("\n".join(out), encoding="utf-8")


# ---------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script", type=Path)
    ap.add_argument("--out", type=Path, required=True, help="work directory for outputs")
    ap.add_argument("--provider", default=None, choices=["auto", *PROVIDERS], help="default: script.provider or auto")
    ap.add_argument("--voice", default=None, help="voice name or id for the provider")
    ap.add_argument("--rate", type=int, default=None, help="words per minute (say) or mapped speed (others)")
    ap.add_argument("--pad", type=float, default=0.45, help="silence after each beat, seconds (default %(default)s)")
    ap.add_argument("--min-beat", type=float, default=2.0, help="minimum visual duration per beat, seconds (default %(default)s)")
    ap.add_argument("--lead-in", type=float, default=0.3, help="silence before the first beat, seconds (default %(default)s)")
    args = ap.parse_args()

    need("ffmpeg")
    need("ffprobe")
    try:
        script = json.loads(args.script.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        die(f"cannot read {args.script}: {e}")
    beats_in = script.get("beats") or die("script has no beats")
    for b in beats_in:
        if not b.get("id") or not b.get("text"):
            die(f"beat needs id and text: {b}")

    provider = pick_provider(args.provider or script.get("provider") or "auto")
    voice = args.voice or script.get("voice") or DEFAULT_VOICES[provider]
    rate = args.rate or script.get("rate")
    synth = PROVIDERS[provider]

    out = args.out
    clips_dir = out / "narration"
    clips_dir.mkdir(parents=True, exist_ok=True)

    beats: list[dict] = []
    t = args.lead_in
    total_words = 0
    for b in beats_in:
        wav = clips_dir / f"{b['id']}.wav"
        synth(b["text"], voice, rate, wav)
        audio = probe_duration(wav)
        duration = max(audio + args.pad, float(b.get("min_duration", args.min_beat)))
        beats.append({"id": b["id"], "text": b["text"], "start": round(t, 3),
                      "end": round(t + duration, 3), "duration": round(duration, 3),
                      "audio_duration": round(audio, 3), "wav": str(wav)})
        total_words += len(b["text"].split())
        t += duration

    # Stitch: lead-in silence, then each clip padded to its beat duration.
    inputs: list[str] = []
    filters: list[str] = []
    for i, b in enumerate(beats):
        inputs += ["-i", b["wav"]]
        filters.append(f"[{i}:a]apad=whole_dur={b['duration']}[a{i}]")
    chain = "".join(f"[a{i}]" for i in range(len(beats)))
    filters.append(f"{chain}concat=n={len(beats)}:v=0:a=1,adelay={int(args.lead_in * 1000)}:all=1,"
                   f"loudnorm=I=-16:TP=-1.5:LRA=11[out]")
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filters),
         "-map", "[out]", "-ar", "48000", "-ac", "1", str(out / "narration.wav")])

    total = round(t, 3)
    (out / "timing.json").write_text(json.dumps({
        "provider": provider, "voice": voice, "total": total, "words": total_words,
        "beats": [{k: v for k, v in b.items() if k != "wav"} for b in beats],
    }, indent=2), encoding="utf-8")
    write_srt(beats, out / "captions.srt")

    wpm = total_words / (total / 60) if total else 0
    print(f"narration: {provider}/{voice}, {len(beats)} beats, {total_words} words, "
          f"{total:.1f}s total ({wpm:.0f} wpm incl. pads)")
    for b in beats:
        print(f"  {b['id']:<12} {b['start']:6.2f} -> {b['end']:6.2f}  speech {b['audio_duration']:.2f}s")
    print(f"wrote {out / 'narration.wav'}, {out / 'timing.json'}, {out / 'captions.srt'}")


if __name__ == "__main__":
    main()
