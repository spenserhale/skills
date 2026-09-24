# Testing a skill

A skill is a hypothesis: "with this folder loaded, a fresh agent does the task better than without." Test the hypothesis. Public benchmarks found that most published software-engineering skills gave no pass-rate lift, some made results worse, and skills an agent wrote for itself without review gave no benefit. Prose quality predicts nothing.

## Contents

- Three kinds of test
- Baseline first
- Evals: format and how many
- Functional test procedure
- Triggering test procedure
- Pressure tests for discipline skills
- Grading
- Measuring and reading results
- Heavier tooling

## Three kinds of test

| Test | Question | When |
|------|----------|------|
| Triggering | Does it fire on the right prompts and stay quiet on near-misses? | After writing or changing the description |
| Functional | With the skill, does a fresh agent produce better output than without? | After every body change that matters |
| Pressure | Under time, sunk cost, and authority pressure, does the agent still follow the rule? | Discipline and verification skills only |

Always run tests on a fresh agent (a subagent or a separate `claude -p` session) with the skill loaded, never in the session that authored it. The authoring session already knows what you meant.

## Baseline first

Before writing anything beyond the description, run the target task without the skill and record the specific failures: wrong library, skipped validation, missing field, wrong file layout, ten minutes rediscovering a flag. Those failures are the skill's content. If the baseline succeeds, stop; there is nothing to fix and a skill would only add context cost.

When improving an existing skill, the baseline is the old version. Snapshot it first (`cp -r <skill> <workspace>/skill-snapshot/`) so the comparison is against what shipped, not what you remember.

## Evals: format and how many

Keep evals in the skill at `evals/evals.json`. This shape is compatible with the Anthropic skill-creator tooling, so the heavier benchmark scripts can consume it directly.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "the user's task, as a real user would phrase it",
      "expected_output": "human-readable description of success",
      "files": ["evals/files/input.pdf"],
      "expectations": [
        "The output file exists at the requested path",
        "The agent ran scripts/validate.py before reporting done",
        "No field in the output is empty"
      ]
    }
  ]
}
```

Start with three evals that cover the baseline failures. Grow toward 20 to 50 real tasks or observed failures as the skill matures; that range is where signal becomes stable. Write prompts as users type them, with file names, context, and casual phrasing. Only objectively checkable outputs get expectations; subjective output (writing voice, design taste) gets human review instead of forced assertions.

Good expectations are verifiable by reading the output or transcript, phrased so a pass is unambiguous, and discriminating: an expectation that passes with and without the skill measures nothing.

## Functional test procedure

For each eval, spawn two runs in the same turn so they finish together:

- **with_skill**: skill path, prompt, input files; save outputs to `<skill>-workspace/iteration-N/<eval-name>/with_skill/outputs/`.
- **baseline**: same prompt with no skill (new skill) or the snapshot (existing skill); save to `without_skill/` or `old_skill/`.

The workspace sits beside the skill directory, not inside it. While runs execute, draft or refine the expectations. When each run's completion notification arrives, save its `total_tokens` and `duration_ms` to `timing.json` in the run directory; that data is not persisted anywhere else.

Read the transcripts, not just the outputs. Where the with-skill agent wandered, the body sent it there. Where all runs wrote the same helper script, bundle that script.

## Triggering test procedure

1. Write 20 prompts: 8 to 10 that should trigger, 8 to 10 that should not. Save as:

   ```json
   [
     {"query": "ok so my boss sent me 'Q4 sales final FINAL v2.xlsx' and wants a profit margin column, revenue is col C costs col D i think", "should_trigger": true},
     {"query": "write a python script that reads a csv and prints the column names", "should_trigger": false}
   ]
   ```

2. Should-trigger prompts vary phrasing (formal, casual, typos), include cases that never name the file type or tool, and include cases where a sibling skill competes but this one should win.
3. Should-not-trigger prompts are near-misses: same vocabulary, different need. "Write a fibonacci function" as a negative for a PDF skill tests nothing.
4. Prompts must be substantive. The model only consults a skill when the task is more than one obvious step.
5. Run each prompt three times on a fresh agent with the skill installed. Count a trigger when the agent invokes the skill or reads its SKILL.md. Pass if the rate is at least 0.5 in the expected direction.
6. Fix the description per `description.md`, then re-run on a held-out set of prompts you did not tune against. Tuning on the same 20 prompts overfits.

Under-triggering is the common failure. The usual fix is adding the user's real phrasing and a pushy "even if they don't say X" clause.

## Pressure tests for discipline skills

Academic questions ("should you write tests first?") always pass. Test the rule the way it fails in practice:

- Give a concrete scenario with real constraints: three hours of work already done, dinner at 6:30, review at 9 a.m., the rule was skipped, options A/B/C. Ask "What do you do?", not "What should you do?"
- Combine at least three pressures: time, sunk cost, authority ("the lead said skip it"), economic, exhaustion, social.
- Run without the skill first and record the rationalizations verbatim. Those exact phrases go into the skill's rationalization table.
- Run with the skill. It is bulletproof when the agent picks the correct option under maximum pressure, cites the rule, and acknowledges the temptation. It is not when it invents a hybrid or asks permission while arguing for the violation.
- When it fails with the skill loaded, ask the agent: "How could the skill have been written so the right option was the only acceptable answer?" Three diagnoses: it was clear and ignored (add a foundational reason), it should have said X (add X verbatim), the section was missed (make it prominent).

## Grading

Grade each run against the eval's expectations. Rules for an honest grade:

- The burden of proof is on the expectation; when uncertain, fail.
- No partial credit.
- Superficial evidence fails: a file with the right name and wrong contents is a fail.
- Where a check can be scripted (file exists, field present, command ran), script it and reuse the script across iterations.

Save as `grading.json` in the run directory with exactly these field names, so the viewer tooling can read it:

```json
{
  "expectations": [
    {"text": "The output includes a SUM formula in B10", "passed": false, "evidence": "No spreadsheet created; output was a text file."}
  ],
  "summary": {"passed": 2, "failed": 1, "total": 3, "pass_rate": 0.67}
}
```

## Measuring and reading results

Report per configuration: pass rate, time, tokens, each as mean plus spread across runs. Then look past the averages:

- Expectations that pass in both configurations do not discriminate; replace them.
- Expectations that fail only with the skill mean the skill is hurting; find the sentence responsible.
- High variance across identical runs means a flaky eval or an ambiguous instruction.
- A token increase with no pass-rate gain is a cost with no benefit; cut the body.

Stop iterating when the user is satisfied, the feedback is empty, or two iterations in a row move nothing. Then trim once more.

## Heavier tooling

The Anthropic skill-creator ships scripts that automate the above and are compatible with the eval format here. When it is installed (`~/.agents/skills/skill-creator/` or the `anthropic-skills` plugin), run from its directory:

- `python -m scripts.run_loop --eval-set <trigger-evals.json> --skill-path <skill> --model <session model> --max-iterations 5` runs the trigger test with a 60/40 train/test split and proposes description rewrites, selecting the best by held-out score.
- `python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>` turns `grading.json` files into `benchmark.json` and `benchmark.md`.
- `python eval-viewer/generate_review.py <workspace>/iteration-N --skill-name <name> --benchmark <benchmark.json>` opens a browser review of outputs and numbers; add `--static out.html` in headless environments.

Use them for the numbers. Keep the judgment (what to cut, what to generalize) here.
