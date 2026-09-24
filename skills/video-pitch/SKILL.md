---
name: video-pitch
description: "Produce a short video pitch (about 20 seconds) for a feature, tool, PR, running app, or the work just finished: spoken narration on why it matters over a real screen-recorded demo, rendered to mp4 with burned-in captions, a poster frame, and a share blurb. Use when the user asks for a video pitch, demo video, walkthrough clip, launch video, screen recording of a feature, or something to show customer success, sales, support, or stakeholders, even if they only say record this, make a clip, or show them how it works. Not for multi-minute training courses, and not for meme-style social launch videos (the brag skill covers those)."
license: MIT
metadata:
  author: spenserhale
  version: "1.0"
---

# video-pitch

A pitch is spoken first: the narration carries the argument and sets the clock, and the visuals prove it with the real product in use. Write the script, record the demo to fit it, assemble with the bundled scripts, then look at the frames before calling it done.

## Steps

Find where the user is and start there. Every step ends with something checkable.

1. **Preflight.** Run `bash scripts/doctor.sh`. It lists what exists for rendering, recording, and narration and exits non-zero when a required tool is missing. Fix or tell the user before doing any creative work, because the whole pipeline is local tools.
2. **Gather.** Decide the subject and audience, then pull material from the source: the repo or feature, a PR or diff, a running app, a CLI, or the conversation itself when the user says "pitch what we just built". Read the repo's pitch config if present (`docs/agents/video-pitch.md` or a section in `CLAUDE.md`/`AGENTS.md`; template in `assets/video-pitch.config.template.md`) for product name, brand, demo URL, and audience defaults; without one, run `python3 scripts/extract_brand.py <url or html>` for the site's colours, fonts, headings, and logo instead of guessing. Answer the six pitch questions in `references/gather.md`. Done when the answers are written to `<out>/pitch-brief.md` and the user has confirmed the audience and the one claim (ask once, briefly, only when the conversation does not already say).
3. **Script.** Write the story beats in the audience's language: problem, what it is, the demo as its own entry, action, and result beats, then so-what plus next step. One idea per beat, 2 to 5 seconds each, usually 5 to 7 beats. Budget about 45 to 50 spoken words for 20 seconds (pads add about 2 seconds) and put the demo narration over the demo footage, not before it. Save as `<out>/work/script.json`. Rules, word budgets, and examples: `references/script.md`.
4. **Narrate.** `python3 scripts/narrate.py <out>/work/script.json --out <out>/work`. It picks the best available voice (ElevenLabs, OpenAI, Kokoro, then macOS `say`), writes per-beat timing and captions, and prints total length. Done when the total is within the target and no beat runs long; shorten the text rather than speeding the voice.
5. **Record the demo.** Real product, real actions, one recording sized to the demo beats' total from `timing.json`, with a `mark` at the start of each demo beat so the cut lands on the screen the narration describes. Web app: write a steps file and run `node scripts/record_web_demo.mjs steps.json --out <out>/work`. CLI: build a self-playing terminal page with `scripts/build_terminal_page.py`, then record it the same way. Desktop or mobile: ask the user for a recording and use it as the clip. Recipes, selectors, login handling, and legibility rules: `references/record.md`. Done when `marks.json` shows the flow inside the recording and one extracted frame is legible at 1080p.
6. **Cards or scenes.** Render the hook and closing cards with `scripts/render_card.py`, using the product's colours and font (`--font-css` loads a webfont). When a beat needs motion the product cannot show on screen (a mechanism, a counter, a before-and-after, kinetic type), write an HTML scene from `assets/scene.template.html`, check it with `node scripts/render_scene.mjs scene.html --check 0,2,4`, and give the beat `"kind": "scene"`; it renders frame-exactly under a virtual clock at assembly. Cards and scenes carry the claim in at most eight words on screen; they never repeat the narration verbatim.
7. **Assemble.** Write `<out>/manifest.json` (copy `assets/manifest.example.json`) and run `python3 scripts/assemble.py <out>/manifest.json --out <out> --stills`. It cuts each beat to its narration, fits the demo clip, cross-fades, burns captions, mixes narration (and music when given), bakes the poster as frame 0, and writes a contact sheet. Options and the manifest schema: `references/render.md`.
8. **Review, then deliver.** Look at `<out>/work/stills.png` and at least one full-size frame from the demo beat. Check: text readable, demo UI legible, captions not covering UI that matters, no blank lead-in, ending lands on the closing card. Fix and re-run rather than shipping a known flaw. Then write `<out>/share.md` (a two-line internal post and a one-line subject) and tell the user where `pitch.mp4`, `pitch.jpg`, and `share.md` are, with one sentence on the angle.

## Options

Accept flags or plain language. Defaults come from the repo config, then these:

| Option | Default |
|--------|---------|
| `--audience` | customer success (internal enablement) |
| `--duration` | 20 s; 15 to 30 is the sane range |
| `--format` | landscape 1920x1080; also vertical, square |
| `--voice` / `--provider` | best available, see `narrate.py --help` |
| `--music path` | none; a bed at -20 dB with ducking when given |
| `--no-captions` | captions burned in |
| `--out` | `pitch-output/` in the project, timestamped if it exists |

## Gotchas

- Homebrew and many distro ffmpeg builds lack `drawtext` and `subtitles`; the scripts render text with headless Chrome for that reason. Do not hand-write ffmpeg text filters.
- Foreground `sleep` is often blocked in agent shells, so step-by-step browser CLIs cannot pace a recording. The recorder runs the waits inside Node.
- Playwright video starts before the page paints. Use the `ready` mark (or a later mark) as the clip's `in` point.
- Headless Chrome letterboxes the page in grey when the viewport exceeds the window. The recorder sets the window size; if you launch a browser another way, pass `--window-size`.
- Fonts: cards use the font stack you pass and colours can be any CSS colour (oklch and var-free rgb included); only the manifest `background` must be hex for ffmpeg. If the product's webfont is not installed locally, pass a close system font, and look at one rendered card before rendering the rest.
- Narration timing is the source of truth. Never `atempo` the voice to fit a clip; fit the clip (speed within 0.6x to 2.5x, trim, or hold) or cut words.
- Voices: macOS `say` is fine for internal enablement and wrong for anything customer-facing. Say so in the hand-off when it was the provider.
- Demo UI at 1600x900 upscaled to 1080p is legible; 1920x1080 viewports make product text tiny. Use `zoom` in the steps file for dense screens.
- Captions cover the bottom eighth of the frame. When they hide UI the narration refers to, reframe the recording (scroll target, `zoom`, `crop`) rather than moving the captions; moving them up covers more.
- Cut points: use `{"mark": "flow-start"}` in the manifest instead of copying seconds from `marks.json`, so a re-recording cannot leave stale cuts.
- Secrets never go in `steps.json`. Use a saved `storage_state` file for logged-in demos and keep it out of git.
- Scenes must be a pure function of time: `requestAnimationFrame` driven by its `t` argument or CSS keyframes with fill-mode. CSS transitions, `Math.random`, wall-clock reads, and `<video>` break the virtual clock and render wrong or frozen.

## References

| Read when | File |
|-----------|------|
| Identifying the subject, audience, and the six pitch questions; per-repo config | `references/gather.md` |
| Writing or cutting the narration; word budgets; audience voice; banned phrases | `references/script.md` |
| Recording a web, CLI, or desktop demo; login state; selectors; legibility | `references/record.md` |
| Manifest schema, fitting clips, HTML scenes and the virtual clock, captions, music, poster, vertical output, craft rules | `references/render.md` |

Sibling skills: `playwright-cli` for exploring a page to find selectors before writing the steps file; `brag` for playful public launch videos.
