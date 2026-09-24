# Writing the body

## Contents

- What goes in the body
- Degrees of freedom
- Rules with reasons
- The cut list
- Discipline skills: resisting rationalization
- Scripts
- Checklist before sharing

## What goes in the body

The body loads only after the model has already decided to use the skill. Its job is to change what the model does next, not to justify the skill or re-explain the domain. Four parts, in this order, each as short as it can be:

1. One or two sentences framing the core idea (the thing the model should hold in mind throughout).
2. The rules or steps.
3. Pointers to `references/`, `scripts/`, `assets/`, each with a sentence saying when to read or run it.
4. Hand-offs to sibling skills, by name.

Write in imperative form. Address the model directly and briefly.

## Degrees of freedom

Match specificity to fragility.

| Freedom | Form | Use when |
|---------|------|----------|
| High | Prose principles and heuristics | Several approaches are valid and context decides (code review, design) |
| Medium | Parameterized pseudocode or a template with slots | There is a preferred pattern and some variation is fine (report formats, scaffolds) |
| Low | An exact command or script, no options | The operation is fragile or must be identical every time (migrations, packaging, validation) |

An open field gets a direction; a narrow bridge gets a railing. Most skills mix levels: high-freedom guidance around low-freedom scripts.

## Rules with reasons

**Include only what changes a decision.** The model already knows what a PDF is and how libraries work. Gotchas, house conventions, the chosen default, the exact flag: those change decisions. Background does not. Every body token competes with the conversation.

**State the goal and the constraints, not every step.** Over-specified procedures break on the first case you did not anticipate. Goals plus constraints generalize.

**Give reasons instead of volume.** "Run the validator after every edit, because errors compound and the message points at the line" beats "ALWAYS VALIDATE". Caps and rigid MUSTs are a yellow flag: they signal a rule the author could not explain, and the model cannot extend a rule it does not understand.

**Prefer the positive form.** "Write the test first" outperforms "Don't write code before tests". Prohibition lists have measured worse than no guidance for shaping output; recipes and contracts shape it. Reserve prohibitions for hard guardrails, and when you use one, close its loopholes (see below).

**One default, one escape hatch.** "Use pdfplumber. For scanned PDFs needing OCR, use pdf2image with pytesseract." Not a menu of five libraries. Menus push the decision back to the model with less context than you had.

**Consistent terms.** Pick "endpoint" or "route", "field" or "control", and keep it. Synonym drift reads as different concepts.

**No time-sensitive text.** "Before August use the old API" rots. Put the current method in the body and the old one under a collapsed "Old patterns" heading if it must exist.

**Gotchas are the highest-signal section.** The failure points you found by iterating are exactly what the model cannot know. Keep them as a flat list under one heading.

**Examples over descriptions of examples.** One complete, runnable input/output pair beats three paragraphs describing the style. One excellent example beats five mediocre ones; do not implement it in five languages.

**Templates match the strictness needed.** "Use exactly this structure" for machine-read output; "sensible default, adjust as needed" for human-read output.

**Checklists for long workflows.** A copyable checklist the model ticks off keeps it from skipping the validation step in step 5 because step 4 went well. Create a todo per item.

**Completion criteria per step.** Every step ends on something checkable: a command that exits 0, a file that exists, a question answered. Steps without criteria end early.

**Feedback loops for quality-critical output.** Validate, fix, repeat. The validator can be a script or a reference checklist the model compares against.

**Reference pointers say when.** "Read `references/authorization.md` when the transport is HTTP" beats a bare link. The model should know before opening the file whether it needs it.

**Execute or read, say which.** "Run `scripts/x.py`" versus "See `scripts/x.py` for the algorithm". Executing is cheaper and more reliable; reading is for when the logic itself is the lesson.

**Fully qualify MCP tools.** `Server:tool_name`. A bare tool name fails when several servers are connected.

**Do not assume tools are installed.** Name the package and the install command, or check for it with a script.

## The cut list

When slimming a body, delete in this order and re-read after each pass:

1. Anything a capable model already knows (definitions, library overviews, "why testing matters").
2. Restatements of what the environment already tells the model (file trees it can `ls`, versions it can query).
3. Sentences the transcripts show the model ignored or that sent it on a detour.
4. Duplicate coverage: information living in both the body and a reference. Keep one copy, in the reference if it is depth, in the body if it is a rule.
5. Motivational text, apologies, hedges, "note that", "it is important to".
6. Multi-language examples: keep the one language the skill targets.
7. Menus of options: keep the default and the escape hatch.
8. Whole sentences that fail, not words within them. Trimming words from a bad sentence leaves a shorter bad sentence.

Stop when every remaining sentence would change a decision if removed.

## Discipline skills: resisting rationalization

A discipline skill (TDD, verification-before-completion, no destructive commands) fails differently from a reference skill: the model understands the rule and talks itself out of it under pressure (time, sunk cost, authority, "this case is different"). For these, the positive-recipe rule still holds for the main body, and you add three things:

- **Explicit loophole closure** for the one hard prohibition: "Delete it. Don't keep it as reference. Don't adapt it. Delete means delete."
- **A rationalization table**: the excuse in the model's words and the reality, one row each. "Too simple to test" / "Simple code breaks; the test takes 30 seconds."
- **Red flags**: phrases in its own reasoning that mean stop ("I already manually tested", "this is different because").

Do not add nuance clauses ("unless it matters"); they reopen the negotiation. Test these skills with pressure scenarios (see `testing.md`), not academic questions.

## Scripts

- Solve, do not defer: handle the missing file, the permission error, the empty input, rather than failing and letting the model improvise.
- `--help` that explains inputs and outputs; the body tells the model to run it before reading source.
- Verbose, specific error messages: "Field 'signature_date' not found. Available: customer_name, order_total."
- No magic numbers. Every constant has a comment saying why that value.
- Prefer stdlib or declare dependencies in `compatibility` and in the body.
- Deterministic output, and `--json` when a machine will read it.
- Test every script by running it before shipping the skill.

## Checklist before sharing

Core:

- [ ] Description names what and when, in third person, with concrete phrases and a near-miss boundary
- [ ] Description does not summarize the workflow
- [ ] Body under target length; depth moved to `references/`
- [ ] Every reference is one hop from SKILL.md and has a when-to-read sentence
- [ ] Reference files over 100 lines start with a Contents list
- [ ] Reasons given where a rule could be misapplied; no unexplained shouting
- [ ] One default per decision, escape hatch where needed
- [ ] Consistent terminology; no dates or "current version" claims
- [ ] Per-repo config read from the repo, not baked in
- [ ] Forward slashes; fully qualified MCP tool names

Scripts (if any):

- [ ] Handle errors themselves with specific messages
- [ ] Constants justified; dependencies declared
- [ ] Run once by hand; `--help` works

Testing:

- [ ] Baseline run without the skill documented the failures this skill fixes
- [ ] At least three functional evals in `evals/evals.json`
- [ ] Triggering tested with near-miss prompts
- [ ] Tested on a fresh agent, not the session that wrote it
- [ ] `validate_skill.py` passes
