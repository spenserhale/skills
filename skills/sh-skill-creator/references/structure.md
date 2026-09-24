# Skill structure (2026)

## Contents

- Folder layout
- Frontmatter: portable fields
- Frontmatter: Claude Code fields
- Invocation modes: model-invoked vs user-invoked
- Skill kinds and the body layout for each
- Naming
- Per-environment config outside the skill
- Loading model and budgets

## Folder layout

```
<name>/
├── SKILL.md                 required
├── references/              optional: docs the agent reads on demand
│   └── <topic>.md           one topic per file; TOC at top when > 100 lines
├── scripts/                 optional: code the agent executes (not reads)
│   └── <verb_noun>.py|.sh   --help, clear errors, no magic constants
├── assets/                  optional: files copied into output (templates, icons, fixtures)
├── evals/
│   ├── evals.json           test prompts + expectations
│   └── files/               input fixtures for evals
└── agents/
    └── openai.yaml          optional: Codex display metadata + invocation policy
```

Rules that follow from the layout:

- `name` in frontmatter equals the folder name. Loaders key on the folder; a mismatch means the skill is found under one name and referenced under another.
- Skills live at `<name>/SKILL.md`. A flat `<name>.md` is silently ignored by real loaders.
- Everything the body links to is one hop away. A reference that links to another reference gets skimmed with `head`, so the agent reads half of it.
- No `README.md`, `CHANGELOG.md`, or `INSTALL.md` inside the skill. Humans read the repo readme; the agent reads SKILL.md. Extra docs get loaded by accident and cost context.
- Flat companion files beside SKILL.md (the `aaa` skill's `arrange.md`, `act.md`, `assert.md`) are fine when there are two or three and each maps to one step. Once there are more, or they are reference rather than steps, use `references/`.
- Keep `evals/` in the skill so tests travel with it. Packagers exclude it from distribution.

## Frontmatter: portable fields

These come from the Agent Skills specification and work in every harness (Claude Code, Codex, Copilot, Cursor, Gemini CLI, Goose, OpenCode, Hermes, and others).

| Field | Required | Constraint |
|-------|----------|------------|
| `name` | yes | 1 to 64 chars, `a-z0-9-` only, no leading/trailing/double hyphen, equals folder name, no "anthropic" or "claude" |
| `description` | yes | 1 to 1024 chars, no angle brackets, third person, what + when |
| `license` | no | short: license name or bundled file name |
| `compatibility` | no | up to 500 chars, only when the skill needs specific tools, packages, or network |
| `metadata` | no | string-to-string map; put `author`, `version`, and any custom keys here |
| `allowed-tools` | no | space-separated pre-approved tools; experimental, support varies |

Quote a description that contains a colon. Keep `metadata` values as strings (`version: "1.0"`, not `1.0`).

## Frontmatter: Claude Code fields

Claude Code reads these at top level. Other harnesses ignore them, so using them does not break portability, but do not rely on them for correctness elsewhere.

| Field | Effect |
|-------|--------|
| `disable-model-invocation: true` | Only the user can run it via `/name`. Its description is not loaded into context at all. |
| `user-invocable: false` | Hidden from the `/` menu; only the model invokes it. |
| `argument-hint` | Autocomplete hint shown after `/name`, e.g. `[issue-number]`. |
| `arguments` | Named positional args for `$name` substitution in the body. |
| `allowed-tools` / `disallowed-tools` | Pre-approve or remove tools for the turn that invokes the skill. Pre-approval clears on the next user message. |
| `context: fork` + `agent` | Run the body in an isolated subagent of the given type. |
| `model`, `effort` | Override for this skill only. |
| `paths` | Globs; the skill auto-loads only when working with matching files. |
| `when_to_use` | Extra trigger text appended to the description (combined listing cap 1,536 chars). Prefer putting triggers in `description` itself so other harnesses see them. |
| `hooks` | Hook registrations that persist for the session. |
| `shell` | `bash` (default) or `powershell` for dynamic `!` commands. |

Body substitutions available in Claude Code: `$ARGUMENTS`, `$N`, `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_SESSION_ID}`. Dynamic context injection with `` !`command` `` runs before the body reaches the model. Neither runs in skills synced from claude.ai, so a skill that depends on them should say what happens when they are absent.

## Invocation modes: model-invoked vs user-invoked

Decide this before writing the description, because the description's shape depends on it.

**Model-invoked** (default). The agent may pick it up on its own; the user may also run it. The description is loaded into every session, so it must earn that cost with a trigger-rich description and a distinct leading concept. Test: could the agent usefully reach for this without being told?

**User-invoked** (`disable-model-invocation: true`). Reachable only by the human typing `/name`. Costs zero context until run. Use for entry points, routers, one-off setup, and anything that only ever fires by hand. The description is a human-facing one-liner with no trigger list, because no model reads it for routing.

Composition rules:

- A user-invoked skill may call model-invoked skills. It never calls another user-invoked skill; when it depends on one, it tells the user to run it.
- Model-invoked skills hold the reusable discipline. User-invoked wrappers are thin: a few lines that name which model-invoked skills to call, in what order.
- Invoke sibling skills by name through the Skill tool ("use the `grilling` skill"), not by linking to their files. Linking force-loads and couples folder layouts.
- Shared reference two skills both need lives in the skill that owns it; the other skill reaches it by invoking the owner. Reference two user-invoked skills both need lives outside the skill system entirely.

When `agents/openai.yaml` is present, mirror the mode: user-invoked means `policy.allow_implicit_invocation: false`. The validator checks this.

Naming by mode in this repo: model-invoked skills are noun or gerund phrases (`mcp-creator`, `doc-it`); user-invoked entry points may read as commands the human types (`/aaa`, `/human-driven-development`).

## Skill kinds and the body layout for each

Pick one. A skill that is two kinds is two skills.

| Kind | Job | Body layout |
|------|-----|-------------|
| **Reference** | Teach correct use of a library, CLI, API, or platform | Start-with-help pattern; the gotchas list (highest-signal content); routing table into `references/<topic>.md`; a few real command examples. No tutorial prose. |
| **Workflow** | Run a repeatable multi-step process | Numbered steps, each ending in a checkable completion criterion; a copyable checklist for long flows; decision points as short conditionals, not flowcharts; scripts for the mechanical steps. |
| **Verification** | Check work before it is called done | The evidence rule (no claim without a run in this turn); the checks in order; what "pass" looks like; the loop back on failure. These have the most measurable impact on output quality. |
| **Scaffold** | Generate boilerplate from a template | Where the template lives in `assets/`; the parameters; what to customize after generation; the validation command. |
| **Router** | Map a family of skills and hand off | User-invoked; a table of situation to skill; no logic of its own. Update it whenever a routed skill changes. |

Anthropic's internal catalog (Library and API reference, Product verification, Data fetching and analysis, Business process automation, Code scaffolding, Code quality and review, CI/CD, Runbooks, Infrastructure operations) is a finer cut of the same idea. Use it as a sanity check: if the skill fits none cleanly, it is probably two skills.

Whatever the kind, the body has at most four parts: a one- or two-sentence framing of the core idea, the rules or steps, the pointers to references and scripts with when to read each, and the hand-offs to sibling skills. A "When to use" section in the body is only for scope boundaries and hand-offs. Triggers belong in the description.

## Naming

- Lowercase kebab-case, verb-led or noun phrase, specific: `wp-components`, `agent-native-cli-creator`. Avoid `helper`, `utils`, `tools`, `docs`.
- Namespace by tool when it disambiguates: `gh-fix-ci`, `wp-vip-cli`.
- Prefix a family that ships together and must not collide: `add-*`, `hdd-*`.
- Scripts: `snake_case` with a verb, `validate_skill.py`, `fetch_comments.py`.
- References: lowercase `kebab-case.md` named by topic, `authorization.md`, `best-practices.md`. Never `doc2.md`.
- Forward slashes everywhere.

## Per-environment config outside the skill

Skills are installed on several machines and into many repos. Anything that differs per repo or per machine is not skill content:

- The skill speaks in abstract verbs: "publish to the issue tracker", "the project's triage labels", "the docs location".
- The repo's `AGENTS.md`/`CLAUDE.md` (or a `docs/agents/*.md` file it points to) translates those verbs into real commands, labels, and paths.
- Hard dependency: if the skill's output is wrong without the config, say so at the top and tell the user what to run or create. Soft dependency: read the config when present, proceed silently when absent.
- A setup skill (user-invoked, run once per repo) can write those config files after exploring the repo and confirming each answer.

The `doc-it` skill is the house example: it asks once how documentation works in this project, saves the answer in the repo, and never asks again.

## Loading model and budgets

| Layer | Loaded | Budget |
|-------|--------|--------|
| Metadata (`name` + `description`) | every session, every skill | about 100 words; keep the description near 300 to 600 chars |
| SKILL.md body | when the skill triggers | target under 150 lines; hard cap 500 lines |
| `references/`, `assets/` | when the body says to read them | unlimited, one file per topic |
| `scripts/` | executed, output only enters context | unlimited |

Claude Code re-attaches skill content after context compaction, first 5,000 tokens per skill within a 25,000 token total. Long bodies get truncated there; another reason to keep the body short and the depth in references.
