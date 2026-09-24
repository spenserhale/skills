# Writing the narration

The narration is the pitch. The video exists to make the narration believable.

## Beats

A beat is one idea on screen for 2 to 5 seconds, then a clean cut. The four-part shape below is the skeleton, not the count: a 20-second pitch usually has 5 to 7 beats because the demo splits into its own entry, action, and result beats, each with a recorder `mark`, so the caption and the voice land on the screen they describe. A 30-second pitch adds a proof beat (a real number, a quote) or a second flow, never longer cards.

Rhythm: fast beats for the problem, a breath for the name, a confident hold for the payoff. The final beat holds its last frame for about 2 seconds so the ending reads as an ending.

## Shape and budget

Four parts. Speech runs about 150 words per minute and `narrate.py` adds a 0.3 s lead-in and 0.45 s after each beat, so 20 seconds holds 45 to 50 words. Aim at the low end of each range below with macOS `say` (it is slower than cloud voices); `narrate.py` prints the real total.

| Beat | Job | Seconds | Words | On screen |
|------|-----|---------|-------|-----------|
| `hook` | The pain the audience recognises | 3 to 4 | 8 to 11 | Card: the claim in five words or fewer |
| `what` | Name it and say what it does | 3 to 4 | 8 to 11 | Card: product name and one line, or the product's entry screen |
| `demo-entry`, `demo-action`, `demo-result` | Narrate each step of use while it happens | 8 to 11 total | 18 to 26 total | The recording, cut at each beat's mark |
| `cta` | So-what and where to get it | 3 to 4 | 8 to 11 | Card: availability and next step |

## Rules

- **Audience language.** Customer success hears "on the next call", "without a ticket", "for every plan". Engineering words (endpoint, migration, refactor) only when the audience is engineering.
- **One claim.** Every beat serves the claim from question 5 in the brief. Cut anything that serves a second claim.
- **Specific over generic.** Use the product's own labels and the real screen names. "Streamline", "seamless", "robust", "empower", "excited to share" are banned; they signal nothing.
- **Demo narration describes what the viewer sees, a half-step ahead.** "Pick the site, enter the domain, and it verifies DNS" while the cursor does exactly that. Do not narrate things the recording does not show.
- **No invented numbers or quotes.** A number from the source is welcome; a made-up "saves 80%" is not.
- **Cards say less than the voice.** The card is a headline, at most eight words on screen at once; the narration is the sentence. Captions already show the narration; a card that repeats it reads as three copies of one line.
- **Show the mechanism, not stock imagery.** When a beat needs a visual the product cannot show (a request racing through boxes, a counter climbing, a diff resolving), build it as an HTML scene from divs and SVG, never a stock image or an abstract gradient.
- **Cut words, not speed.** If `narrate.py` reports the total over target, remove a clause. Faster speech reads as nervous.
- **Say the voice's limits.** With macOS `say`, keep sentences short and avoid brand names it mangles; test with `say -v Samantha "text"` when unsure. Prefer a cloud or Kokoro voice for anything a customer will hear.

## Script file

```json
{
  "voice": "Samantha",
  "beats": [
    {"id": "hook", "text": "Launching a new domain used to mean a support ticket and a two-day wait."},
    {"id": "what", "text": "Domain Launch does it from the dashboard in one guided flow."},
    {"id": "demo-entry",  "text": "Pick the site and enter the domain."},
    {"id": "demo-action", "text": "It verifies DNS and issues the certificate, with live status for each step."},
    {"id": "demo-result", "text": "Then it swaps traffic over. The domain is live."},
    {"id": "cta",  "text": "It is live on every plan today. Show it on the next customer call."}
  ]
}
```

Beat ids are the join key for `timing.json` and the manifest; keep them stable across re-runs. Add `"min_duration": 4` on a beat whose visual needs more time than its sentence (a closing card that should hold, a scene that needs its full animation, a demo step the viewer must watch). Reaching a target length is done with words first and `min_duration` second, never by slowing the voice.

## Words per target length

Measured with macOS `say` at its default rate plus the default pads; cloud voices run about 10 percent faster, so add a few words.

| Target | Beats | Spoken words |
|--------|-------|--------------|
| 15 s | 4 to 5 | 32 to 38 |
| 20 s | 5 to 7 | 45 to 50 |
| 25 s | 6 to 8 | 56 to 62 |
| 30 s | 7 to 9 | 68 to 75 |

## Audience presets

| Audience | Hook angle | Closing line |
|----------|------------|--------------|
| Customer success / support | The ticket or question they keep getting | What to tell customers, and where the doc is |
| Sales | The objection or the competitor gap | Which plans include it |
| Leadership / stakeholders | The cost or risk it removes | Rollout status and the owner |
| Customers | Their task, in their words | Where the button is |
| Engineering (internal tools) | The manual step it replaces | Command or link, and who maintains it |
