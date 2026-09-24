# Gathering material and answering the pitch questions

## Contents

- Identify the subject
- Sources by input type
- The six pitch questions
- Per-repo config
- The brief file

## Identify the subject

The subject is one thing the audience can act on: a feature, a tool, a workflow, a fix. If the user points at a whole product, ask which capability the video should sell; a 20-second pitch cannot carry more than one claim. If the conversation just built something, that thing is the subject and the transcript is the first source.

## Sources by input type

| Input | How to recognise it | Where the material comes from |
|-------|---------------------|-------------------------------|
| Feature in the current repo | User names a feature, folder, or command | README and docs for the feature, the UI strings and route files, tests (they state the intended behaviour plainly), recent commits touching it |
| PR or diff | A PR number, branch, or `git diff` | PR title and description, changed UI strings, screenshots in the PR, the linked issue for the "before" pain |
| Running app | An `http(s)://` URL or a dev server the repo starts | The live screens: navigate with `playwright-cli` snapshots, read visible copy, note the entry point, the key action, and the result screen |
| CLI tool | A command name or a `bin/` entry | `--help` output, the README usage block, one real invocation and its output (this becomes the terminal demo script) |
| Conversation | "Pitch what we just did" | The transcript: what the user asked for, what changed, what was verified; confirm the user-facing framing before writing |
| Doc or spec | A Confluence, Notion, or markdown page | The problem statement and the acceptance criteria; ask what actually shipped |

For a web app, run the flow once with `playwright-cli` before scripting it. Save the snapshot refs or CSS selectors you will click; guessing selectors is the most common reason a recording fails.

## The six pitch questions

Write the answers down before scripting. Each answer is one or two sentences.

1. **Who is watching, and what do they do next?** Name the audience (customer success, sales, support, leadership, a customer) and the action the video should cause (mention it on calls, enable it for an account, approve rollout, try it).
2. **What was painful before?** The concrete situation the audience recognises: the ticket, the wait, the workaround, the manual step. Use their words, not the engineering description.
3. **What is it, in one sentence?** Product name, what it does, for whom. No architecture.
4. **What does the demo show?** Three beats of real use: entry, key action, result. Name the screens or commands.
5. **What changes for the audience?** The so-what: time saved, fewer escalations, a new thing to offer, a risk removed. One claim, with a number when the source has one and no invented number otherwise.
6. **Where do they get it or learn more?** Plan or rollout status, the doc link, the owner. This is the last line.

If question 2 or 5 has no honest answer, say so; a pitch without a pain or a payoff is a feature tour, and the user may prefer a walkthrough instead.

## Per-repo config

Anything that differs per product lives in the repo, not in this skill. Read, in order, `docs/agents/video-pitch.md`, then a `## Video pitch` section in `CLAUDE.md` or `AGENTS.md`. Expected keys (all optional): product name, default audience, brand colours and font, logo path, demo base URL and how to obtain a logged-in `storage_state`, preferred narration provider and voice, where finished pitches get posted. When none exists, infer colours and fonts from the product's stylesheet, use the defaults in the SKILL.md options table, and offer to save a config file from `assets/video-pitch.config.template.md` at the end so the next run does not ask.

## The brief file

`<out>/pitch-brief.md` holds: subject, audience, the six answers, format and duration, visual identity (background, accent, text colour, font), and the demo plan (screens or commands, expected length). The script step reads from it; the review step checks the video against it.
