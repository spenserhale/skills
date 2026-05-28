---
name: doc-it
description: Document the current work by following this project's established documentation process. Use whenever the user says "doc it", "document this", "document the change", "write it up", "add docs", "log this", or just wants whatever was just done recorded somewhere. Also triggers on "doc-it". If no documentation process has been defined yet for this project, asks the user how docs should work and saves the answer so it never needs to ask again.
---

# doc-it

Documents whatever just happened — following whatever process this project uses. Could be updating a markdown file, posting to Confluence, writing a Notion page, appending to a changelog, updating inline code docs, or anything else. The first time you run it in a project with no doc process defined, it asks once and saves the answer.

## Workflow

### Step 1: Find the Documentation Process

Check the project's agent context for how documentation should work. Look in order:

1. `AGENTS.md` — look for a documentation or doc-it section
2. `CLAUDE.md` — same
3. `docs/documentation.md` — a dedicated doc policy
4. `.agents/skills/doc-it/SKILL.md` — a project-local override

If you find clear instructions describing the documentation process and destination, skip to Step 3.

### Step 2: No Process Defined — Ask Once, Then Save

Ask the user one focused question:

> "How should documentation work in this project? Describe the process and destination — for example: update a specific markdown file, post to Confluence, create a Notion page, append to a changelog, add inline code comments, or something else."

Once they answer, save the documentation process so this never needs to be asked again:

- If `AGENTS.md` exists: add a `## Documentation` section with the process description
- If `docs/` exists but no `AGENTS.md`: create `docs/documentation.md` with the process, and add a pointer in `CLAUDE.md` if it exists
- Otherwise: create `docs/documentation.md` at the repo root

Tell the user: "Saved. Future `/doc-it` calls will follow this automatically."

Then continue to Step 3 using what they just described.

### Step 3: Infer What to Document

From the current conversation context, determine what needs to be documented:
- A new feature or capability was added
- A bug was fixed and how
- An architectural or process decision was made
- A CLI command, API endpoint, config option, or schema changed
- A workflow was established

Write from the perspective of someone who needs to understand or use this going forward — not a commit summary, but useful reference content. Be specific: include relevant names, paths, commands, or examples.

### Step 4: Execute the Documentation

Follow the project's documented process. Common patterns:

**Markdown file** — append or update the relevant section; match the file's existing heading style and tone

**Changelog** (`CHANGELOG.md`, `RELEASES.md`, etc.) — add an entry under `Unreleased` or the current version using whatever format is already in the file (Keep a Changelog, plain prose, etc.)

**README** — update the relevant section (usage, features, API, configuration); don't rewrite the whole thing, just the part that changed

**Confluence** — use the Confluence MCP if available; create or update the appropriate page in the space the project uses

**Notion** — use the Notion MCP if available; create or update the relevant page or database entry

**Inline code docs** — add or update docstrings, JSDoc, PHPDoc, etc. on the changed functions, classes, or modules

**Slack / other** — if the process involves posting a summary somewhere, draft the message and either post it (if the MCP is available) or present it for the user to send

If the process requires an external tool and the relevant MCP is not available, write the documentation content in full and tell the user exactly where to paste or post it.
