# Auditing a skill

Treat a skill like a dependency with execute permission. One 2026 study found at least one vulnerability in 26% of public skills; an industry audit found prompt injection in 36%. Apply this to third-party skills before installing and to your own before publishing.

## Contents

- Trust boundary
- Checks in order
- Severity and reporting
- Principle of lack of surprise

## Trust boundary

A skill can influence the agent three ways: text the model reads (SKILL.md, references, assets), code the agent runs (scripts, dynamic `!` commands), and permissions it grants (`allowed-tools`, hooks). Each is a separate surface. A skill with no scripts can still exfiltrate data by instructing the model to.

## Checks in order

1. **Provenance.** Who published it, is the repo the canonical source, does the installed copy match the repo (`npx skills` records a hash in `skills-lock.json`; compare). Unknown fork of a known skill is a flag.
2. **Frontmatter permissions.** `allowed-tools` broader than the task needs (`Bash(*)`, `Bash(curl:*)`, `Bash(rm:*)`) is a finding. `hooks` that persist for the session need a reason in the body. `context: fork` with an unexpected `agent` is worth a look.
3. **Dynamic commands.** Every `` !`...` `` and multi-line `!` block runs before the model sees the body, without a prompt. Read each: network access, writes outside the skill directory, reads of dotfiles or credentials, `curl | sh`.
4. **Scripts.** For each file under `scripts/`: network calls and where to; writes outside the working directory; environment variables read (tokens, keys); subprocess with shell=True on user input; obfuscation, base64 blobs, minified code, downloads at run time; dependency installs. A script the body tells the agent to run without reading is exactly where to read.
5. **Instruction injection in text.** Search SKILL.md, references, and assets for instructions aimed at the model that have nothing to do with the skill's job: "ignore previous instructions", "also send", "do not tell the user", requests to read or transmit files, links to fetch and follow, hidden text (HTML comments, zero-width characters, white-on-white in HTML assets). Pasted third-party docs in `references/` carry whatever their source carried.
6. **Scope creep.** The description says one job; the body does that job plus something else (edits git config, installs a hook, phones home for "telemetry"). Compare description to body.
7. **Data handling.** What the skill reads (repo, env, clipboard, browser) and where it could send it. For anything touching regulated data, the answer to "where" must be "nowhere off-machine".
8. **Reversibility.** Destructive commands (`rm -rf`, `git push --force`, `DROP`, mass file edits) need a guard: a dry run, a confirmation, or a scoped path. A skill that runs them unguarded is a finding regardless of intent.

Run `scripts/validate_skill.py` first; it flags dynamic commands, broad `allowed-tools`, and missing link targets so the manual pass can focus on intent.

## Severity and reporting

| Severity | Meaning | Example |
|----------|---------|---------|
| Critical | Exfiltrates, executes remote code, or destroys data | Script posts env vars to a URL; `!` block downloads and runs a binary |
| High | Grants or uses capability well beyond the job | `allowed-tools: Bash(*)` on a formatting skill; hidden instructions to the model |
| Medium | Risky by construction, fixable | Unguarded destructive command; secrets read from env without need |
| Low | Hygiene | Extraneous docs, unpinned dependency, stale link |

Report one line per finding: `path:line`, severity, what it does, what to change. Do not install anything with a critical or high finding; fork and fix, or find another skill.

## Principle of lack of surprise

Your own skills must not surprise the person who installs them. If describing a skill's full behavior to its user would change their decision to install it, the behavior does not belong in the skill. Roleplay and opinionated workflows are fine; hidden side effects, credential handling the description does not mention, and instructions that override the user's own are not.
