# Recording the demo

The demo is the proof. It shows the real product doing the thing the narration claims, in the order the narration says it, and it fits the demo beat's duration from `timing.json`.

## Contents

- Sizing the recording
- Web app: record_web_demo.mjs
- Logged-in demos
- CLI: a self-playing terminal page
- Desktop, mobile, or an existing recording
- Legibility rules
- When the recording fails

## Sizing the recording

Read the demo beats' durations from `<out>/work/timing.json` before recording; one recording covers all of them, with a `mark` named after each beat (`demo-entry`, `demo-action`, `demo-result`) at the moment that beat's screen appears. Plan waits so the flow takes about that long; `assemble.py` can speed or slow a clip within 0.6x to 2.5x, but real-time footage always looks best. Reference the marks from the manifest (`"in": {"mark": "demo-action"}, "out": {"mark": "demo-result"}`) so the blank lead-in never ships and a re-recording cannot leave stale seconds behind.

## Web app: record_web_demo.mjs

1. Explore first. Open the page with `playwright-cli`, take a snapshot, and note the selectors for the elements you will hover, click, or fill. Text selectors (`text=Launch domain`) survive markup changes better than nth-child chains.
2. Write `<out>/work/steps.json`:

```json
{
  "url": "http://localhost:3000/sites/42/domains",
  "viewport": {"width": 1600, "height": 900},
  "zoom": 1,
  "storage_state": "work/auth.json",
  "steps": [
    {"wait": 700},
    {"mark": "demo-entry"},
    {"click": "text=Add domain"},
    {"type": ["input[name=domain]", "example.com", 55]},
    {"press": "Enter"},
    {"mark": "demo-action"},
    {"wait_for": "text=DNS verified"},
    {"wait": 1200},
    {"hover": "text=Launch"},
    {"click": "text=Launch"},
    {"mark": "demo-result"},
    {"wait_for": "text=Live"},
    {"wait": 1500}
  ]
}
```

3. Run `node scripts/record_web_demo.mjs <out>/work/steps.json --out <out>/work`. It writes `demo.webm` and `marks.json`, a flat object of seconds from the recording start (`{"ready": 0.9, "demo-entry": 1.4, "demo-action": 4.2, "end": 11.4}`); `ready` and `end` are added for you, the rest come from your `mark` steps. The `url` may be `file:///path/index.html` for a static site.
4. Extract one frame (`ffmpeg -ss <t> -i demo.webm -frames:v 1 frame.png`) and look at it. Check the cursor is visible, the UI is legible, and no cookie banner or dev overlay is in shot. Remove overlays with an `eval` step.

Step vocabulary: `wait` (ms), `mark`, `goto`, `hover`, `click`, `fill`, `type` (with per-key delay), `press`, `scroll` (a selector scrolls that element to the top of the viewport; `{"y": px}` scrolls by that many pixels relative to the current position; both smooth, then pause 0.7 s), `wait_for`, `eval`, `screenshot`. Hover, click, and scroll each add roughly 0.3 to 1 s of glide and settle on top of your `wait`s; budget about 2 s of overhead per six actions. Under a sticky header, a top-aligned scroll hides the element's own heading behind the nav; use `{"scroll": {"to": "#sel", "block": "center"}}` instead, and skip scrolling entirely when the flow fits above the fold. Use `type` over `fill` when the viewer should see the text arrive. Add `--headed` to watch a run while debugging selectors.

The script needs `playwright-core` and a Chromium-based browser; no browser download. It looks in `$PLAYWRIGHT_CORE_PATH`, the cwd, the global npm root, and the `playwright-cli` install. Otherwise `npm i -g playwright-core`.

## Logged-in demos

Never put credentials in `steps.json`. Produce a storage state once and point `storage_state` at it:

```bash
playwright-cli open http://localhost:3000/login     # log in by hand or with fill/click
playwright-cli state-save work/auth.json            # storage state, reusable across runs
```

Without `playwright-cli`, a five-line Node script with `playwright-core` (`context.storageState({ path })` after logging in) does it. Keep `auth.json` out of git and out of the delivered folder. Demo against a staging site or a seeded local account, never production customer data.

## CLI: a self-playing terminal page

Write the command and its real output (run it once and paste) into a steps file:

```json
{"prompt": "~/site $ ", "steps": [
  {"cmd": "vip domain launch example.com", "type_ms": 45, "delay": 0.5,
   "output": ["Verifying DNS records ... ok", {"text": "Issued TLS certificate", "class": "ok"},
              "Switching traffic ... done", {"text": "example.com is live", "class": "ok"}],
   "pause": 1.2}
]}
```

Then `python3 scripts/build_terminal_page.py steps.json --out <out>/work/terminal.html` (prints the play length; adjust `delay`, `line_ms`, `pause` to match the beat) and record it like a web page: `{"url": "file:///.../terminal.html", "steps": [{"wait": <play length ms>}]}` with `"cursor": false`. The page sets `document.title` to `done` when finished.

Use real output. Trim long output to the lines that carry the story; do not invent success lines the tool does not print.

## Desktop, mobile, or an existing recording

Ask the user for a screen recording (macOS: `screencapture -v -V 15 demo.mov` records the screen for 15 seconds; QuickTime and phone screen recorders also work). Use it as the `video` beat's `src` and set `in`/`out` after watching a contact sheet. Vertical phone recordings go in a vertical pitch or get an `inset` inside a landscape one.

## Legibility rules

- Record at 1600x900 (or 1440x900) for landscape; UI text stays readable after the upscale. A 1920x1080 viewport makes dense product screens too small.
- Use `zoom` (1.15 to 1.3) for dashboards with small type, or a `crop` in the manifest to frame the part of the screen that matters.
- Cursor on, movement gliding, one action at a time with a beat between actions. Viewers need about a second to register each change.
- Nothing in shot the audience should not see: dev toolbars, other tabs, personal data, unfinished features.
- Captions occupy the bottom eighth of the frame. Frame the recording so the UI the narration names sits above that band (scroll target, `zoom`, or a manifest `crop`); moving captions up hides more, not less.
- Light colour scheme unless the product is dark by default; captions sit on a dark box and read on either.

## When the recording fails

`marks.json` gains an `error` key and the script exits 1 with the failing step. Usual causes: selector not found (explore with `playwright-cli snapshot` and fix), page needed login (add `storage_state`), an element animated in after the click (add `wait_for`). Fix the step and re-run; recordings are cheap.
