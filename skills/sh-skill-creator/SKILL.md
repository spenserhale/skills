---
name: sh-skill-creator
description: Create, restructure, review, or test agent skills (SKILL.md folders) against Spenser's 2026 rule set. Use whenever the user wants to write a new skill, turn a workflow or the current conversation into a skill, fix a skill that is not triggering, slim a bloated SKILL.md, audit a third-party skill before installing it, or asks what a good skill looks like, even if they never say "skill" but mention SKILL.md, slash commands, or reusable agent instructions. Prefer this over the generic skill-creator for anything in Spenser's skills repo.
license: MIT
metadata:
  author: spenserhale
  version: "1.0"
---

# sh-skill-creator

Build skills that a fresh agent triggers correctly, reads cheaply, and measurably benefits from. The rule set below is the whole skill; the `references/` files carry the detail and load only when a step needs them.

## The rule set

Each rule carries its reason so it generalizes to cases this file never lists.

1. **The description does the triggering.** It is the only text loaded for every skill in every session, so it must name the concrete situations, phrases, file types, and near-miss handoffs. Everything else about "when to use" is wasted anywhere else, because the body loads only after the decision is made.
2. **The description never summarizes the workflow.** An agent that sees the steps in the description will follow that shortcut instead of reading the body.
3. **Assume a smart model.** Include only what changes a decision: gotchas, house conventions, the chosen default, the exact command. Cut background it already knows. Every body token competes with the conversation.
4. **State the rule and the reason, not the shout.** ALL-CAPS MUST/NEVER is a yellow flag; a rule with its "why" lets the model handle the case you did not write down. Reserve hard prohibitions for real guardrails (destructive ops, data loss), and when you do prohibit, close the loopholes explicitly.
5. **One skill, one job.** Skills that straddle categories confuse routing. Split by invocation or by sequence; hand off to sibling skills by name.
6. **Depth lives beside the body, one level deep.** `references/` for docs read on demand, `scripts/` for deterministic mechanics executed rather than read, `assets/` for output templates. Link each from SKILL.md with a sentence saying when to read it.
7. **Per-environment config lives outside the skill.** Skills stay identical across repos and machines; anything that varies (tracker, labels, paths, doc locations) is read from the repo's `AGENTS.md`/`CLAUDE.md` or `docs/agents/*.md` at run time.
8. **If a check is mechanical, script it.** Regex-checkable constraints go in a validator; prose is for judgment calls.
9. **Prose is not evidence.** A plausible SKILL.md is not a working skill. Test triggering with near-miss prompts and test function with-versus-without on a fresh agent before trusting it. Public benchmarks found most skills gave no lift and some hurt.
10. **Treat skills as executable dependencies.** Bundled scripts, `allowed-tools`, dynamic `!` commands, and pasted third-party references are all attack surface. Audit before install; keep your own skills free of surprises.

## The structure

```
<name>/
├── SKILL.md            frontmatter + lean body (target < 150 lines, hard cap 500)
├── references/         on-demand docs, one level deep, TOC when > 100 lines
├── scripts/            deterministic tools, executed not read, --help + clear errors
├── assets/             templates and files copied into output
├── evals/evals.json    test prompts + expectations (compatible with skill-creator tooling)
└── agents/openai.yaml  optional Codex UI metadata; mirrors invocation policy
```

Frontmatter: `name` (matches folder), `description`, then optional `license`, `compatibility`, `metadata`, `allowed-tools`. Claude Code extras (`disable-model-invocation`, `argument-hint`, `context`, `paths`, and so on) are allowed when the skill needs them; other harnesses ignore them. Full field semantics, invocation modes, body layout per skill kind, and naming rules: read `references/structure.md`.

## Workflow

Find where the user is and jump in there. Skip steps only with a stated reason.

1. **Capture intent.** If the conversation already contains the workflow ("turn this into a skill"), extract tools used, step order, user corrections, and input/output shapes from history first, then confirm. Otherwise ask, briefly: what should the agent be able to do, what would a user say that should trigger it, what should the output look like, and does the output have an objectively checkable form (then it gets evals).
2. **Classify.** Pick one kind (reference, workflow, verification, scaffold, router) and one invocation mode (model-invoked or user-invoked). The test for model-invoked: could the agent usefully reach for this on its own? If it only ever fires by hand, make it user-invoked so its description costs no context. See `references/structure.md`.
3. **Baseline first.** Run the target task on a fresh agent without the skill (a subagent works). Note the specific failures. If there are none, there is nothing to fix; a skill that cannot beat the baseline should not exist.
4. **Draft.** Scaffold with the script, then write the description before the body:

   ```bash
   python3 scripts/init_skill.py <name> --path <skills-dir> [--user-invoked] [--resources scripts,references,assets] [--codex]
   ```

   Description rules and worked examples: `references/description.md`. Writing rules for the body: `references/rules.md`. Write only what the baseline failures need. Bundle a script when the baseline agent kept rewriting the same helper.
5. **Validate.** Mechanical checks, run every time the skill changes:

   ```bash
   python3 scripts/validate_skill.py <path-to-skill> [--strict]
   ```

   It enforces the Agent Skills spec, then the house rules (folder name, description shape, body length, one-level references, missing link targets, shouting, Windows paths, extraneous docs, invocation mirror in the Codex metadata file). Fix errors; read warnings as prompts, not commands.
6. **Test.** Three kinds, in this order: triggering (should-fire and near-miss should-not-fire prompts), functional (same prompts with and without the skill on a fresh agent, graded against `evals/evals.json` expectations), and for discipline skills, pressure scenarios. Procedure, eval formats, and the hand-off to the heavier benchmark tooling: `references/testing.md`.
7. **Iterate, then trim.** Generalize from feedback rather than patching for the three test prompts. Read the transcripts, not just outputs; delete anything the agent ignored or that sent it on detours. Re-run validate and the tests after each pass.
8. **Register.** In this repo, add the readme table row and the install `--skill` flag, per `CLAUDE.md`. Elsewhere, follow the repo's own conventions.

## Other modes

- **Reviewing or auditing a skill** (yours or third-party): run the validator, then walk `references/audit.md`. Report findings by severity with file and line.
- **Fixing triggering**: rewrite the description per `references/description.md`, then run triggering tests. Under-triggering usually means the description is too polite or lacks the user's actual phrasing; over-triggering usually means a missing near-miss boundary.
- **Slimming a skill**: apply `references/rules.md` cut list, move depth to `references/`, keep the body under the target, re-validate.

## References

| Read when | File |
|-----------|------|
| Choosing invocation mode, frontmatter fields, folder layout, body layout for a skill kind, naming | `references/structure.md` |
| Writing or fixing a description | `references/description.md` |
| Writing or trimming a body; the cut list and checklist | `references/rules.md` |
| Designing evals, running trigger and functional tests, pressure tests, measuring | `references/testing.md` |
| Auditing a skill for prompt injection, script risk, over-broad permissions | `references/audit.md` |
| Wanting to know where a rule came from or what the research says | `references/sources.md` |
