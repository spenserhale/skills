#!/usr/bin/env python3
"""Scaffold a new skill folder that follows the sh-skill-creator structure.

Usage:
    python3 init_skill.py <name> [--path DIR] [--description TEXT]
                          [--user-invoked] [--resources scripts,references,assets]
                          [--codex] [--force]

Examples:
    python3 init_skill.py migrate-db --path ../../skills --resources scripts
    python3 init_skill.py grill-me --path ~/.claude/skills --user-invoked --codex

Creates:
    <DIR>/<name>/SKILL.md          from assets/SKILL.template.md, placeholders left visible
    <DIR>/<name>/evals/evals.json  from assets/evals.template.json
    <DIR>/<name>/<resource>/       empty folders for each requested resource
    <DIR>/<name>/agents/openai.yaml  with --codex, policy mirrored from --user-invoked

Refuses to overwrite an existing folder unless --force is given. Placeholders
are __UPPER_CASE__ so the validator and a grep both find what is left to fill.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
VALID_RESOURCES = ("scripts", "references", "assets")
NAME_MAX = 64  # Agent Skills spec


def slugify(raw: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", raw.strip().lower()).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    return s[:NAME_MAX].rstrip("-")


def title_case(name: str) -> str:
    acronyms = {"mcp": "MCP", "cli": "CLI", "api": "API", "wp": "WP", "gh": "GH", "pr": "PR", "db": "DB", "ci": "CI"}
    return " ".join(acronyms.get(w, w.capitalize()) for w in name.split("-"))


def render(template: str, values: dict[str, str]) -> str:
    out = template
    for k, v in values.items():
        out = out.replace(f"__{k}__", v)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Scaffold a skill folder.")
    ap.add_argument("name", help="skill name; lowercased and hyphenated if needed")
    ap.add_argument("--path", default=".", help="parent directory for the new skill folder (default: cwd)")
    ap.add_argument("--description", default=None, help="frontmatter description; leave unset to fill in later")
    ap.add_argument("--user-invoked", action="store_true", help="only the human runs it (/name); sets disable-model-invocation: true")
    ap.add_argument("--resources", default="", help="comma list of scripts,references,assets folders to create")
    ap.add_argument("--codex", action="store_true", help="also write agents/openai.yaml")
    ap.add_argument("--force", action="store_true", help="overwrite an existing folder")
    args = ap.parse_args(argv)

    name = slugify(args.name)
    if not name:
        print(f"error: '{args.name}' does not reduce to a valid skill name", file=sys.stderr)
        return 2
    if name != args.name:
        print(f"note: using name '{name}' (from '{args.name}')")
    if any(w in name for w in ("anthropic", "claude")):
        print("warning: names containing 'anthropic' or 'claude' are rejected by Claude platforms", file=sys.stderr)

    resources = [r for r in args.resources.split(",") if r]
    bad = [r for r in resources if r not in VALID_RESOURCES]
    if bad:
        print(f"error: unknown resource(s) {bad}; choose from {', '.join(VALID_RESOURCES)}", file=sys.stderr)
        return 2

    parent = Path(args.path).expanduser().resolve()
    target = parent / name
    if target.exists():
        if not args.force:
            print(f"error: {target} already exists; pass --force to overwrite", file=sys.stderr)
            return 1
        shutil.rmtree(target)
    parent.mkdir(parents=True, exist_ok=True)
    target.mkdir()

    if args.description:
        desc = args.description.strip()
        if ":" in desc and not desc.startswith('"'):
            desc = '"' + desc.replace('"', '\\"') + '"'
    elif args.user_invoked:
        desc = "__ONE_LINE_HUMAN_FACING_SUMMARY__"
    else:
        desc = "__WHAT_IT_DOES__. Use when __CONCRETE_TRIGGERS__, even if the user does not say __KEYWORD__. Not for __NEAR_MISS__; use __SIBLING_SKILL__ instead."

    extra = "disable-model-invocation: true\n" if args.user_invoked else ""

    resource_lines = []
    if "references" in resources:
        resource_lines.append("Read `references/__TOPIC__.md` when __CONDITION__.")
    if "scripts" in resources:
        resource_lines.append("Run `python3 scripts/__VERB_NOUN__.py --help` before reading its source; it __WHAT_IT_DOES__.")
    if "assets" in resources:
        resource_lines.append("Copy `assets/__TEMPLATE__` as the starting point for __OUTPUT__.")
    resources_block = ("## Resources\n\n" + "\n".join(f"- {l}" for l in resource_lines) + "\n") if resource_lines else ""

    skill_values = {
        "NAME": name,
        "DESCRIPTION": desc,
        "EXTRA_FRONTMATTER": extra,
        "TITLE": title_case(name),
        "FRAMING": "__ONE_OR_TWO_SENTENCES_ON_THE_CORE_IDEA__",
        "RULES_OR_STEPS_HEADING": "Steps" if not args.user_invoked else "What it runs",
        "STEP_ONE": "__STEP__ (done when __CRITERION__)",
        "STEP_TWO": "__STEP__ (done when __CRITERION__)",
        "STEP_THREE": "__STEP__ (done when __CRITERION__)",
        "GOTCHA": "__FAILURE_POINT_AND_WHY__",
        "RESOURCES": resources_block,
    }
    (target / "SKILL.md").write_text(render((ASSETS / "SKILL.template.md").read_text(), skill_values).rstrip() + "\n")

    (target / "evals").mkdir()
    (target / "evals" / "evals.json").write_text(render((ASSETS / "evals.template.json").read_text(), {"NAME": name}))

    for r in resources:
        (target / r).mkdir()
        (target / r / ".gitkeep").touch()

    if args.codex:
        (target / "agents").mkdir()
        policy = "policy:\n  allow_implicit_invocation: false\n" if args.user_invoked else ""
        oai = render((ASSETS / "openai.template.yaml").read_text(), {
            "DISPLAY_NAME": title_case(name),
            "SHORT_DESCRIPTION": "__25_TO_64_CHARS__",
            "NAME": name,
            "DEFAULT_PROMPT": "__WHAT_A_USER_WOULD_ASK__",
            "POLICY": policy,
        })
        (target / "agents" / "openai.yaml").write_text(oai.rstrip() + "\n")

    print(f"created {target}")
    for p in sorted(target.rglob("*")):
        if p.name != ".gitkeep":
            print(f"  {p.relative_to(target).as_posix()}{'/' if p.is_dir() else ''}")
    print("next: fill every __PLACEHOLDER__, then run scripts/validate_skill.py on it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
