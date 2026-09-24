#!/usr/bin/env bash
# Check the machine for everything video-pitch needs and report what is missing.
# usage: doctor.sh            exit 0 when the required tools exist, 1 otherwise
set -u
ok=0; missing=0
have() { command -v "$1" >/dev/null 2>&1; }
line() { printf '  %-16s %s\n' "$1" "$2"; }
req() { if have "$1"; then line "$1" "ok ($($1 --version 2>/dev/null | head -1 | cut -c1-40))"; else line "$1" "MISSING: $2"; missing=1; fi; }
opt() { if have "$1"; then line "$1" "ok"; else line "$1" "optional: $2"; fi; }

echo "required"
req ffmpeg "brew install ffmpeg (or apt/choco); needs no libass or freetype"
req ffprobe "ships with ffmpeg"
req node "Node 18+ (https://nodejs.org)"
req python3 "Python 3.9+"

echo "browser (cards, captions, demo recording)"
browser=""
for c in "${CHROME_PATH:-}" \
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  "/Applications/Chromium.app/Contents/MacOS/Chromium" \
  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
  "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" \
  google-chrome google-chrome-stable chromium chromium-browser microsoft-edge brave-browser; do
  [ -z "$c" ] && continue
  if [ -x "$c" ] || have "$c"; then browser="$c"; break; fi
done
if [ -n "$browser" ]; then line "chrome" "ok ($browser)"; else line "chrome" "MISSING: install Chrome/Chromium/Edge or set CHROME_PATH"; missing=1; fi

pw=""
if [ -n "${PLAYWRIGHT_CORE_PATH:-}" ] && [ -e "$PLAYWRIGHT_CORE_PATH" ]; then pw="$PLAYWRIGHT_CORE_PATH"; fi
[ -z "$pw" ] && pw=$(node -e 'try{console.log(require.resolve("playwright-core/package.json"))}catch{}' 2>/dev/null)
[ -z "$pw" ] && root=$(npm root -g 2>/dev/null) && [ -d "$root/playwright-core" ] && pw="$root/playwright-core"
if [ -z "$pw" ] && have playwright-cli; then
  d=$(dirname "$(readlink -f "$(command -v playwright-cli)")")
  for _ in 1 2 3 4 5 6; do [ -d "$d/node_modules/playwright-core" ] && pw="$d/node_modules/playwright-core" && break; d=$(dirname "$d"); done
fi
if [ -n "$pw" ]; then line "playwright-core" "ok ($pw)"; else line "playwright-core" "for web demos: npm i -g playwright-core"; fi

echo "narration (one is enough; auto picks the first present)"
[ -n "${ELEVENLABS_API_KEY:-}" ] && line "elevenlabs" "ok (ELEVENLABS_API_KEY set)" || line "elevenlabs" "set ELEVENLABS_API_KEY for the best voices"
[ -n "${OPENAI_API_KEY:-}" ] && line "openai" "ok (OPENAI_API_KEY set)" || line "openai" "set OPENAI_API_KEY for gpt-4o-mini-tts"
python3 -c 'import kokoro_onnx' 2>/dev/null && line "kokoro" "ok (needs KOKORO_MODEL and KOKORO_VOICES)" || line "kokoro" "pip install kokoro-onnx soundfile, local and free"
have say && line "say" "ok (macOS built-in, fallback)" || line "say" "not macOS"
if [ -z "${ELEVENLABS_API_KEY:-}${OPENAI_API_KEY:-}" ] && ! have say && ! python3 -c 'import kokoro_onnx' 2>/dev/null; then line "tts" "MISSING: no narration provider"; missing=1; fi

echo "optional"
opt hyperframes "npx hyperframes, for motion-graphics polish"
opt screencapture "macOS screen recorder for desktop apps (screencapture -v)"
exit $missing
