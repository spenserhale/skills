#!/usr/bin/env python3
"""Score the walk logs written by ux-reviewer walkers.

Reads every *.json file in a directory (one log per walker, in the shape given
in assets/walker-brief.md) and prints one comparable row per walker, followed
by the moments worth reading: first actions, dead ends, steps that needed the
small print or a guess, and where walkers gave up or stopped short.

Usage:
    python3 score_walks.py <walks-dir> [--shortest N] [--json]

Arguments:
    walks-dir     directory holding the walkers' *.json logs
    --shortest N  actions on the shortest correct path, counted the same way
                  the walkers count (a click, a choice, typing into one field,
                  a toggle, going back). Adds the "vs shortest" column.
    --json        print the scores as JSON instead of Markdown

Before scoring, read each log's done_evidence against the real success
condition and set "outcome" to "false_done" where the walker believed it had
finished and had not.

A log may carry "reads": "none", "stuck", or "first" (how much small print that
walker was allowed). A walker that reads none and still logs a step as "help"
is scored "stalled" at that step: someone who skips the small print would have
had nothing to go on there, whatever the walker did next.

Exit codes: 0 scored, 1 a log is malformed (each problem is listed), 2 usage.
"""

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

# What a walker may write, and the one spelling each is scored under. Small
# models paraphrase enum values; accepting the obvious variants costs nothing
# and saves a round trip to fix a log that is otherwise fine.
OUTCOMES = {
    "done": "done", "completed": "done", "complete": "done", "finished": "done", "success": "done",
    "gave_up": "gave_up", "gave up": "gave_up", "abandoned": "gave_up", "stuck": "gave_up",
    "false_done": "false_done", "false done": "false_done",
}
BASES = {"label": "label", "labels": "label", "help": "help", "guess": "guess", "guessed": "guess"}
READS = ("none", "stuck", "first")
TRUE = {True, "true", "yes", "y", 1}
FALSE = {False, "false", "no", "n", 0}
STEP_FIELDS = ("screen", "action", "basis", "result", "progress")
OUTCOME_TEXT = {"done": "done", "gave_up": "gave up", "false_done": "thought done, was not",
                "stalled": "stalled"}
CLIP = 110  # characters of free text shown per line, so a long answer cannot bury the list


def load_log(path):
    """Return (log, problems). Tolerates a code fence or stray prose around the JSON."""
    text = path.read_text(encoding="utf-8", errors="replace")
    start, end = text.find("{"), text.rfind("}")
    if start == -1:
        return None, [f"{path.name}: no JSON object found. The file must hold one log object."]
    if end <= start:
        return None, [f"{path.name}: the JSON object is never closed, so the log looks cut off. "
                      "Ask the walker to save it again."]
    try:
        return json.loads(text[start:end + 1]), []
    except json.JSONDecodeError as err:
        return None, [f"{path.name}: not valid JSON ({err.msg} at line {err.lineno}). "
                      "Ask the walker to rewrite the file, or fix the syntax by hand."]


def as_bool(value):
    if not isinstance(value, (bool, int, str)):
        return None
    key = value.strip().lower() if isinstance(value, str) else value
    if key in TRUE:
        return True
    if key in FALSE:
        return False
    return None


def clip(text):
    text = re.sub(r"\s+", " ", str(text)).strip()
    return text if len(text) <= CLIP else text[:CLIP - 1] + "…"


def score(path, log):
    problems = []
    name = str(log.get("walker") or path.stem)
    raw_outcome = str(log.get("outcome", "")).strip().lower()
    outcome = OUTCOMES.get(raw_outcome)
    if outcome is None:
        problems.append(f"{path.name}: outcome is {raw_outcome!r}. Use one of: done, gave_up, false_done.")
    reads = str(log.get("reads", "")).strip().lower()
    if reads and reads not in READS:
        problems.append(f"{path.name}: reads is {reads!r}. Use one of: {', '.join(READS)}, or leave it out.")
    steps = log.get("steps")
    if not isinstance(steps, list) or not steps:
        problems.append(f"{path.name}: \"steps\" must be a non-empty list, one entry per action.")
        return None, problems

    clean = []
    for i, step in enumerate(steps, 1):
        if not isinstance(step, dict):
            problems.append(f"{path.name}: step {i} is not an object.")
            continue
        missing = [f for f in STEP_FIELDS if f not in step]
        if missing:
            problems.append(f"{path.name}: step {i} is missing {', '.join(missing)}. "
                            f"Fields present: {', '.join(sorted(step)) or 'none'}.")
            continue
        basis = BASES.get(str(step["basis"]).strip().lower())
        if basis is None:
            problems.append(f"{path.name}: step {i} basis is {step['basis']!r}. Use one of: label, help, guess.")
        progress = as_bool(step["progress"])
        if progress is None:
            problems.append(f"{path.name}: step {i} progress is {step['progress']!r}. Use true or false.")
        clean.append({"n": i, "screen": str(step["screen"]).strip(), "action": str(step["action"]),
                      "result": str(step["result"]), "basis": basis, "progress": progress})
    if problems:
        return None, problems

    # A visit is a run of consecutive steps on one screen. Coming back to a
    # screen already visited is the backtracking a lost user does.
    visits = []
    for step in clean:
        key = step["screen"].lower()
        if not visits or visits[-1] != key:
            visits.append(key)
    # A walker told to read no small print cannot honestly proceed on it. Models do
    # anyway, and say so in the log, so the first such step marks where a person
    # who skips the small print runs out of cues.
    stop = len(clean)
    stalled = next((s for s in clean if s["basis"] == "help"), None) if reads == "none" else None
    if stalled:
        outcome, stop = "stalled", stalled["n"]
    return {
        "walker": name,
        "outcome": outcome,
        "stopped_at": stop,
        "stalled_step": stalled,
        "actions": len(clean),
        "dead_ends": [s for s in clean if not s["progress"]],
        "help": [s for s in clean if s["basis"] == "help"],
        "guess": [s for s in clean if s["basis"] == "guess"],
        "revisits": len(visits) - len(set(visits)),
        "first": clean[:2],
        "last": clean[-1],
        "done_evidence": str(log.get("done_evidence", "")),
        "stuck_at": str(log.get("stuck_at", "")),
    }, []


def step_list(steps):
    if not steps:
        return "0"
    return f"{len(steps)} (step{'s' if len(steps) > 1 else ''} {', '.join(str(s['n']) for s in steps)})"


def render_markdown(rows, shortest):
    out = []
    finished = [r for r in rows if r["outcome"] == "done"]
    summary = f"{len(finished)} of {len(rows)} walkers finished"
    if finished:
        summary += f"; median {statistics.median(r['actions'] for r in finished):g} actions"
        if shortest:
            summary += f" against a shortest path of {shortest}"
    out.append(summary + ".\n")

    head = ["Walker", "Outcome", "Actions"] + ([f"vs shortest ({shortest})"] if shortest else []) + [
        "Dead ends", "Needed small print", "Guessed", "Revisits"]
    out.append("| " + " | ".join(head) + " |")
    out.append("|" + "---|" * len(head))
    for r in rows:
        outcome = OUTCOME_TEXT[r["outcome"]] + (f" at step {r['stopped_at']}" if r["outcome"] != "done" else "")
        # For a stalled walker only the steps up to the stall are evidence.
        cells = [r["walker"], outcome, str(r["stopped_at"] if r["outcome"] == "stalled" else r["actions"])]
        if shortest:
            # A ratio only means something for a walker that reached the end.
            cells.append(f"{r['actions'] / shortest:.1f}x" if r["outcome"] == "done" else "-")
        cells += [str(len(r["dead_ends"])), step_list(r["help"]), step_list(r["guess"]), str(r["revisits"])]
        out.append("| " + " | ".join(cells) + " |")

    out.append("\nFirst actions")
    for r in rows:
        out.append(f"- {r['walker']}: " + " -> ".join(clip(s["action"]) for s in r["first"]))

    def section(title, key, show):
        lines = [f"- {r['walker']} step {s['n']} ({s['screen']}): {show(s)}" for r in rows for s in r[key]]
        if lines:
            out.append(f"\n{title}")
            out.extend(lines)

    section("Dead ends (an action that did not move the walker forward)", "dead_ends",
            lambda s: f"{clip(s['action'])} -> {clip(s['result'])}")
    section("Needed the small print", "help", lambda s: clip(s["action"]))
    section("Guessed", "guess", lambda s: clip(s["action"]))

    stopped = [r for r in rows if r["outcome"] != "done"]
    if stopped:
        out.append("\nDid not finish")
        for r in stopped:
            if r["outcome"] == "stalled":
                why = ("reads no small print, and only the small print pointed onward at step "
                       f"{r['stopped_at']}: {r['stalled_step']['action']}")
            else:
                why = r["stuck_at"] or r["done_evidence"] or f"last action: {r['last']['action']}"
            out.append(f"- {r['walker']} ({OUTCOME_TEXT[r['outcome']]}): {clip(why)}")
    if not shortest:
        out.append("\nPass --shortest N to compare each walk with the shortest correct path.")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("walks_dir", help="directory holding the walkers' *.json logs")
    parser.add_argument("--shortest", type=int, default=0, metavar="N",
                        help="actions on the shortest correct path")
    parser.add_argument("--json", action="store_true", help="print scores as JSON")
    args = parser.parse_args()

    folder = Path(args.walks_dir)
    if not folder.is_dir():
        print(f"error: {folder} is not a directory. Pass the folder the walkers saved their logs in.", file=sys.stderr)
        return 2
    if args.shortest < 0:
        print("error: --shortest must be a positive number of actions.", file=sys.stderr)
        return 2
    paths = sorted(folder.glob("*.json"))
    if not paths:
        others = ", ".join(sorted(p.name for p in folder.iterdir())[:8]) or "nothing"
        print(f"error: no *.json logs in {folder} (found: {others}). "
              "Each walker saves its log to the path named in its brief.", file=sys.stderr)
        return 2

    rows, problems = [], []
    for path in paths:
        log, errs = load_log(path)
        if log is not None:
            row, errs = score(path, log)
            if row:
                rows.append(row)
        problems.extend(errs)
    if problems:
        print("error: fix these logs, then run again:", file=sys.stderr)
        for line in problems:
            print(f"  {line}", file=sys.stderr)
        return 1

    if args.json:
        for r in rows:
            r["vs_shortest"] = round(r["actions"] / args.shortest, 2) if args.shortest and r["outcome"] == "done" else None
            del r["first"], r["last"], r["stalled_step"]
        print(json.dumps({"shortest": args.shortest or None, "walks": rows}, indent=2))
    else:
        print(render_markdown(rows, args.shortest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
