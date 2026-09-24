# Assembling and rendering

`assemble.py` turns cards, clips, narration, and captions into `pitch.mp4`. It is deterministic: same manifest, same output. Read this when writing the manifest or when the result needs adjusting.

## Contents

- Manifest
- Timing and fitting
- Cards and motion
- Captions
- Music
- Poster and delivery files
- Vertical and square
- Review loop
- Polish with hyperframes

## Manifest

Copy `assets/manifest.example.json` to `<out>/manifest.json`. Paths are relative to the manifest. Fields:

| Field | Meaning |
|-------|---------|
| `format` | `landscape`, `vertical`, `square`, or `{"width","height"}` |
| `fps` | 30 default |
| `timing` | `work/timing.json` from `narrate.py`; each beat's visual length |
| `marks` | `work/marks.json` from the recorder; lets `in`/`out` name a mark |
| `narration`, `captions` | `work/narration.wav`, `work/captions.srt` |
| `burn_captions` | `false` to keep the SRT beside the video instead of burning |
| `caption_style` | `font`, `size`, `fg`, `box`, `margin` overrides |
| `music` | `{"path", "gain_db": -20, "fade": 1.5}` |
| `transition` | `{"type": "fade", "duration": 0.35}` or `{"type": "cut"}` |
| `background` | pad colour behind inset clips; match the card background |
| `poster` | `{"beat", "offset"}` or `{"time"}`; default is the second beat plus half a second; taken before captions unless `"with_captions": true` |
| `beats[]` | ordered; `id` must match the script beat ids |

Beat fields: `kind` (`card` or `video`), `src`, and for video `in` and `out` (seconds, or `{"mark": "flow-start", "offset": 0.2}` resolved from `marks`; prefer marks), `fit` (`auto`, `speed`, `trim`, `hold`), `crop` (`x,y,w,h` in source pixels), `inset` (0 to 0.15, frames the clip inside the background). A beat without narration needs `duration`.

## Timing and fitting

Beat durations come from `timing.json`, so the visuals always match the voice. For a video beat the clip length (`out` minus `in`) rarely equals the beat:

- ratio between 0.4x and 2.5x: `auto` changes playback speed to fit (a 12-second flow in a 10-second beat runs at 1.2x, which viewers do not notice).
- longer than 2.5x: trimmed to the beat. Cut the steps file instead; the end of the flow is usually the payoff.
- shorter than 0.4x: last frame held. Better to add a `wait` at the end of the recording.

Cross-fades do not shift beat starts; each segment is extended by the transition length under the hood.

## Cards and motion

`render_card.py` produces one PNG per card. Pass `--bg --bg2 --fg --muted --accent --font` from the brief's visual identity (any CSS colour syntax works, `oklch()` included, since Chrome renders it; only the manifest `background` pad colour must be hex for ffmpeg) and `--logo` when the config has one. Render one card and look at it before rendering the rest; a missing webfont silently falls back. The product name and date sit at the top so captions never collide with them. Cards get a slow 6 percent push-in by default; `"motion": "none"` for a static card.

Card copy is a headline, not the narration: `--title "Domain launches, without the ticket"`, `--subtitle` one short line, `--kicker` the audience or section label.

## Captions

Captions come from `captions.srt`, split at about 42 characters and timed inside each beat by word count. They are rendered as transparent PNGs with headless Chrome and overlaid, so ffmpeg builds without libass or freetype work. Keep them on for internal posting (Slack and Teams autoplay muted). Move them up with `caption_style.margin` when the demo has controls along the bottom edge.

## Music

Optional. Provide a licensed bed with `music.path`; it loops, sits at `gain_db` (default -20), fades in and out, and ducks under the narration with a side-chain compressor. No bed ships with the skill: licensing differs per company and a wrong bed is worse than none. Internal enablement pitches read fine without music.

## Poster and delivery files

`pitch.jpg` is the frame at `poster`, taken from the video before captions are burned so the thumbnail is clean, and is also baked over frame 0 of `pitch.mp4`, because Slack, Teams, and most players thumbnail frame 0. Choose a settled frame on the product-name card or the strongest demo moment, never a transition. `--name` changes the base file name.

`share.md` is written by hand, not by the script: two lines for the internal channel (what shipped, who it is for, where to learn more) and a one-line subject for email or a release note. No "excited to share".

## Vertical and square

Set `format` and re-render cards with the same `--format`. Web recordings stay landscape; give them `inset` or a `crop` to a phone-like region, or record at a narrow viewport (`{"width": 720, "height": 1280}`) when the product is responsive. Captions move up automatically in vertical output.

## Review loop

`--stills` writes `work/stills.png`, a contact sheet across the whole video. Look at it, then extract one full-size frame from the demo beat. Checks: text readable at a glance, demo UI legible, no grey letterbox, captions not covering key UI, no blank lead-in, last frame is the closing card. Use `--draft` for fast iterations, then a final run without it.

## Polish with hyperframes

When the user wants motion graphics beyond cards and cuts (animated callouts, zoom-to-cursor, kinetic type) and `npx hyperframes doctor` passes, build the composition there: use `demo.webm`, the narration, and `timing.json` as inputs, keep the same four beats, and render with `npx hyperframes render`. Its own skills (`hyperframes-core` and siblings) own the composition details; this skill still owns the script, the recording, and the delivery files.
