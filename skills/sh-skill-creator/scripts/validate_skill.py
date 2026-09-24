#!/usr/bin/env python3
"""Validate a skill folder against the Agent Skills spec and Spenser's house rules.

Usage:
    python3 validate_skill.py <path-to-skill> [--strict] [--json] [--quiet]

Exit codes:
    0  no errors (warnings may be present unless --strict)
    1  errors found (or warnings found with --strict)
    2  usage error

Checks are split into two tiers:
    ERROR   violates the Agent Skills specification or breaks loading
    WARN    violates a house rule; usually worth fixing, sometimes deliberate

Stdlib only. The frontmatter parser handles the YAML subset skills use
(scalars, quoted strings, one level of nested maps, simple lists).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# --- Limits -----------------------------------------------------------------
# Spec constraints (agentskills.io/specification).
NAME_MAX = 64
DESCRIPTION_MAX = 1024
COMPATIBILITY_MAX = 500
# House targets. Spec says "keep SKILL.md under 500 lines"; 150 is the target
# because the body is re-attached after compaction only up to 5,000 tokens.
BODY_TARGET_LINES = 150
BODY_HARD_LINES = 500
# Description sweet spot: long enough to carry triggers, short enough not to
# crowd the listing that holds every skill's description.
DESCRIPTION_WARN_CHARS = 700
# Reference files longer than this need a table of contents so partial reads
# still show the file's scope.
REFERENCE_TOC_LINES = 100
# More than this many shouted directives suggests rules without reasons.
SHOUT_LIMIT = 3

SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
CLAUDE_CODE_FIELDS = {
    "disable-model-invocation", "user-invocable", "argument-hint", "arguments",
    "disallowed-tools", "model", "effort", "context", "agent", "background",
    "when_to_use", "paths", "shell", "hooks",
}
KNOWN_DIRS = {"references", "reference", "scripts", "assets", "evals", "agents", "examples", "templates"}
EXTRANEOUS_FILES = {"README.md", "CHANGELOG.md", "INSTALL.md", "INSTALLATION_GUIDE.md", "QUICK_REFERENCE.md", "CONTRIBUTING.md"}
RESERVED_NAME_WORDS = ("anthropic", "claude")

TRIGGER_MARKERS = re.compile(r"\b(use (this )?(skill )?(when|for|whenever|if)|trigger|whenever|when the user|use it when|invoke)\b", re.I)
FIRST_PERSON = re.compile(r"\b(I can|I will|I'll|I help|you can use this|helps you)\b", re.I)
SHOUT = re.compile(r"\b(MUST|NEVER|ALWAYS|DO NOT|CRITICAL|IMPORTANT)\b")
WINDOWS_PATH = re.compile(r"[A-Za-z0-9_]\\[A-Za-z0-9_]+\\")
TIME_SENSITIVE = re.compile(r"\b(before|after|as of|until|since)\s+(19|20)\d\d\b", re.I)
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s#]+)(#[^)]*)?\)")
BACKTICK_PATH = re.compile(r"`((?:(?:references?|scripts|assets|evals|agents|examples)/[^`\s]+)|(?:[a-z0-9_-]+\.md))`")
DYNAMIC_CMD = re.compile(r"(^|\s)!`[^`]+`|^```!\s*$", re.M)
# Flags a blanket grant or a grant to a command that is itself a shell,
# downloader, deleter, or privilege escalator. `Bash(git clone *)` is fine.
BROAD_TOOLS = re.compile(r"Bash\(\s*\*?\s*\)|(?:^|\s)Bash(?:\s|$)|Bash\((?:sh|bash|zsh|eval|sudo|curl|wget|rm|python3?|node)\s+\*\)")


class Report:
    def __init__(self) -> None:
        self.items: list[dict] = []

    def error(self, msg: str, where: str = "SKILL.md") -> None:
        self.items.append({"level": "ERROR", "where": where, "message": msg})

    def warn(self, msg: str, where: str = "SKILL.md") -> None:
        self.items.append({"level": "WARN", "where": where, "message": msg})

    def info(self, msg: str, where: str = "SKILL.md") -> None:
        self.items.append({"level": "INFO", "where": where, "message": msg})

    def count(self, level: str) -> int:
        return sum(1 for i in self.items if i["level"] == level)


# --- Frontmatter ------------------------------------------------------------

def split_frontmatter(text: str) -> tuple[str | None, str]:
    """Return (frontmatter_text, body). frontmatter_text is None when absent."""
    if not text.startswith("---"):
        return None, text
    m = re.match(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(\r?\n|$)", text, re.S)
    if not m:
        return None, text
    return m.group(1), text[m.end():]


def _unquote(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        inner = v[1:-1]
        if v[0] == '"':
            inner = inner.replace('\\"', '"').replace("\\n", "\n")
        return inner
    return v


def parse_frontmatter(fm: str) -> dict:
    """Minimal YAML subset parser sufficient for SKILL.md frontmatter."""
    result: dict = {}
    lines = fm.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line.startswith((" ", "\t")):
            raise ValueError(f"unexpected indentation at line {i + 1}: {line!r}")
        if ":" not in line:
            raise ValueError(f"expected 'key: value' at line {i + 1}: {line!r}")
        key, _, raw = line.partition(":")
        key = key.strip()
        raw = raw.strip()
        if raw in (">", "|", ">-", "|-"):
            # Block scalar: gather indented lines.
            block: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            joiner = "\n" if raw.startswith("|") else " "
            result[key] = joiner.join(b for b in block if b).strip()
            continue
        if raw == "":
            # Nested map or list follows.
            i += 1
            nested_map: dict = {}
            nested_list: list = []
            while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                item = lines[i].strip()
                if not item:
                    i += 1
                    continue
                if item.startswith("- "):
                    nested_list.append(_unquote(item[2:]))
                elif ":" in item:
                    k, _, v = item.partition(":")
                    nested_map[k.strip()] = _unquote(v)
                else:
                    raise ValueError(f"cannot parse nested line {i + 1}: {lines[i]!r}")
                i += 1
            result[key] = nested_list if nested_list else nested_map
            continue
        if raw.startswith("[") and raw.endswith("]"):
            result[key] = [_unquote(x) for x in raw[1:-1].split(",") if x.strip()]
        elif raw in ("true", "false"):
            result[key] = raw == "true"
        else:
            result[key] = _unquote(raw)
        i += 1
    return result


# --- Checks -----------------------------------------------------------------

def check_frontmatter(fm: dict, skill_dir: Path, rep: Report) -> None:
    unknown = set(fm) - SPEC_FIELDS - CLAUDE_CODE_FIELDS
    for k in sorted(unknown):
        rep.warn(f"frontmatter key '{k}' is neither Agent Skills spec nor Claude Code; move custom keys under metadata:")
    for k in sorted(set(fm) & CLAUDE_CODE_FIELDS):
        rep.info(f"frontmatter key '{k}' is Claude Code only; other harnesses ignore it")

    name = fm.get("name")
    if not isinstance(name, str) or not name.strip():
        rep.error("missing or empty 'name'")
    else:
        name = name.strip()
        if len(name) > NAME_MAX:
            rep.error(f"name is {len(name)} chars; max {NAME_MAX}")
        if not re.fullmatch(r"[a-z0-9-]+", name):
            rep.error(f"name '{name}' must be lowercase letters, digits, hyphens only")
        if name.startswith("-") or name.endswith("-") or "--" in name:
            rep.error(f"name '{name}' cannot start/end with a hyphen or contain '--'")
        if name != skill_dir.name:
            rep.error(f"name '{name}' does not match folder name '{skill_dir.name}'; loaders key on the folder")
        for w in RESERVED_NAME_WORDS:
            if w in name:
                rep.warn(f"name contains reserved word '{w}'; Claude platforms reject it")

    desc = fm.get("description")
    if isinstance(desc, str) and re.search(r"__[A-Z][A-Z0-9_]+__", desc):
        rep.error("description still contains scaffold placeholders")
    user_invoked = fm.get("disable-model-invocation") is True
    if not isinstance(desc, str) or not desc.strip():
        rep.error("missing or empty 'description'")
    else:
        d = desc.strip()
        if len(d) > DESCRIPTION_MAX:
            rep.error(f"description is {len(d)} chars; max {DESCRIPTION_MAX}")
        elif len(d) > DESCRIPTION_WARN_CHARS:
            rep.warn(f"description is {len(d)} chars; aim for 300-600. Generalize the trigger list instead of enumerating queries")
        if "<" in d or ">" in d:
            rep.error("description contains angle brackets")
        if FIRST_PERSON.search(d):
            rep.warn("description is not in third person ('I can', 'you can use this'); write about the skill and the user")
        if re.match(r"^(this skill|a skill|skill (that|for|to))\b", d, re.I):
            rep.warn("description starts with 'This skill' / 'A skill'; front-load the leading concept instead")
        if not user_invoked and not TRIGGER_MARKERS.search(d):
            rep.warn("description has no trigger clause ('Use when ...', 'whenever the user ...'); the description is the only text that decides triggering")
        if user_invoked and TRIGGER_MARKERS.search(d) and len(d) > 200:
            rep.info("user-invoked skill has a long trigger-style description; a human-facing one-liner is enough since no model routes on it")
        if re.search(r"\bstep \d\b.*\bstep \d\b|\bfirst\b.*\bthen\b.*\b(finally|lastly|last)\b", d, re.I):
            rep.warn("description reads like a workflow summary (first/then/finally); say when to use it, not how it works, or the agent will shortcut the body")

    comp = fm.get("compatibility")
    if comp is not None:
        if not isinstance(comp, str):
            rep.error("compatibility must be a string")
        elif len(comp) > COMPATIBILITY_MAX:
            rep.error(f"compatibility is {len(comp)} chars; max {COMPATIBILITY_MAX}")

    meta = fm.get("metadata")
    if meta is not None:
        if not isinstance(meta, dict):
            rep.error("metadata must be a map of string keys to string values")
        else:
            for k, v in meta.items():
                if not isinstance(v, str):
                    rep.error(f"metadata.{k} must be a string (quote numbers like version: \"1.0\")")

    tools = fm.get("allowed-tools")
    if tools is not None:
        joined = " ".join(tools) if isinstance(tools, list) else str(tools)
        if BROAD_TOOLS.search(joined):
            rep.warn(f"allowed-tools pre-approves a broad pattern ({joined!r}); scope it to the commands the skill actually runs")

    if fm.get("when_to_use") and isinstance(desc, str):
        combined = len(desc) + len(str(fm["when_to_use"]))
        if combined > 1536:
            rep.warn(f"description + when_to_use is {combined} chars; Claude Code truncates the listing at 1536")
        rep.info("when_to_use is Claude Code only; consider folding its triggers into description so every harness sees them")


def check_body(body: str, skill_dir: Path, fm: dict, rep: Report) -> list[Path]:
    """Check the markdown body. Returns the list of referenced local files that exist."""
    lines = body.splitlines()
    n = len(lines)
    if n > BODY_HARD_LINES:
        rep.error(f"body is {n} lines; hard cap {BODY_HARD_LINES}. Move depth to references/")
    elif n > BODY_TARGET_LINES:
        rep.warn(f"body is {n} lines; target under {BODY_TARGET_LINES}. Move depth to references/ and keep rules in the body")
    if n < 3:
        rep.warn("body is nearly empty; a description alone rarely changes behavior")

    LANG_CONSTANTS = {"__FILE__", "__DIR__", "__LINE__", "__CLASS__", "__FUNCTION__", "__METHOD__", "__NAMESPACE__", "__TRAIT__", "__NAME__", "__MAIN__", "__DEBUG__", "__DEV__"}
    if (ph := [x for x in re.findall(r"__[A-Z][A-Z0-9_]+__", body) if x not in LANG_CONSTANTS]):
        rep.warn(f"{len(ph)} unfilled scaffold placeholder(s), e.g. {ph[0]}")

    shouts = SHOUT.findall(body)
    if len(shouts) > SHOUT_LIMIT:
        rep.warn(f"{len(shouts)} shouted directives ({', '.join(sorted(set(shouts)))}); state the rule and the reason instead, keep caps for hard guardrails")

    if WINDOWS_PATH.search(body):
        rep.warn("backslash path found; use forward slashes everywhere")

    for m in TIME_SENSITIVE.finditer(body):
        rep.warn(f"time-sensitive phrase '{m.group(0)}'; put the current method in the body and old ones under an 'Old patterns' heading")

    if re.search(r"^##+\s*when to use\b", body, re.I | re.M):
        section = re.split(r"^##+\s*when to use\b[^\n]*\n", body, flags=re.I | re.M)[1]
        section = re.split(r"^##+ ", section, flags=re.M)[0]
        bullets = len(re.findall(r"^\s*[-*]\s", section, re.M))
        if bullets >= 4:
            rep.warn(f"'When to use' section has {bullets} bullets; triggers belong in the description (only it is loaded before the decision). Keep the body section for scope boundaries and hand-offs")

    if DYNAMIC_CMD.search(body):
        rep.info("dynamic !`command` injection present; it runs before the model sees the body, never in synced skills. Audit each command")

    # Links and backtick paths to local files. Fenced code blocks are skipped:
    # tree diagrams and example commands mention paths that need not exist.
    prose = re.sub(r"^```.*?^```[ \t]*$", "", body, flags=re.S | re.M)
    referenced: list[Path] = []
    seen: set[str] = set()
    targets = [(m.group(1), "link") for m in MD_LINK.finditer(prose)] + [(m.group(1), "mention") for m in BACKTICK_PATH.finditer(prose)]
    for t, kind in targets:
        if re.match(r"^[a-z]+://", t) or t.startswith(("mailto:", "#", "$", "{")):
            continue
        t_clean = t.split("#")[0].rstrip("/")
        if t_clean in seen or not t_clean:
            continue
        seen.add(t_clean)
        p = (skill_dir / t_clean)
        if not p.exists() and "/" not in t_clean:
            # Bare `topic.md` mentions usually mean a file under references/.
            for alt in ("references", "reference"):
                if (skill_dir / alt / t_clean).exists():
                    p = skill_dir / alt / t_clean
                    break
        if not p.exists():
            local = t_clean.startswith(("references/", "reference/", "scripts/", "assets/", "evals/", "agents/", "examples/")) or t_clean.endswith(".md")
            if local and kind == "link":
                rep.error(f"body links to '{t_clean}' but it does not exist")
            elif local and "/" in t_clean:
                rep.warn(f"body mentions '{t_clean}' but it does not exist")
            elif local:
                # Bare `name.md` may describe a file the skill creates elsewhere.
                rep.info(f"body mentions '{t_clean}', not found in the skill; fine if it names a file the skill writes")
            continue
        if ".." in Path(t_clean).parts:
            rep.warn(f"'{t_clean}' points outside the skill; cross-skill file links couple folder layouts. Invoke the sibling skill by name instead")
        if p.is_file():
            referenced.append(p)
            if p.suffix == ".md" and len(Path(t_clean).parts) > 2:
                rep.warn(f"'{t_clean}' is nested more than one folder deep; keep references one hop from SKILL.md")
    return referenced


def check_references(skill_dir: Path, referenced: list[Path], rep: Report) -> None:
    ref_dirs = [d for d in (skill_dir / "references", skill_dir / "reference") if d.is_dir()]
    md_files: list[Path] = []
    for d in ref_dirs:
        md_files.extend(sorted(d.rglob("*.md")))
    # Companion .md files beside SKILL.md count as references too.
    md_files.extend(p for p in sorted(skill_dir.glob("*.md")) if p.name != "SKILL.md")

    unlinked: list[str] = []
    no_toc: list[str] = []
    for f in md_files:
        rel = f.relative_to(skill_dir).as_posix()
        text = f.read_text(encoding="utf-8", errors="replace")
        n = len(text.splitlines())
        if f not in referenced:
            unlinked.append(rel)
        if n > REFERENCE_TOC_LINES and not re.search(r"^##+\s*(contents|table of contents)\b", text, re.I | re.M):
            no_toc.append(rel)
    AGG = 5  # above this many, one summary line reads better than a wall
    if len(unlinked) > AGG:
        rep.warn(f"{len(unlinked)} reference files are not individually linked from SKILL.md ({', '.join(unlinked[:3])}, ...). Fine when the body gives a lookup rule such as references/<topic>.md; otherwise link each with a when-to-read sentence", "references/")
    else:
        for rel in unlinked:
            rep.warn("not linked from SKILL.md; the agent will never know when to read it", rel)
    if len(no_toc) > AGG:
        rep.warn(f"{len(no_toc)} reference files exceed {REFERENCE_TOC_LINES} lines without a '## Contents' heading ({', '.join(no_toc[:3])}, ...); partial reads then miss their scope", "references/")
    else:
        for rel in no_toc:
            rep.warn(f"over {REFERENCE_TOC_LINES} lines and no '## Contents' heading; partial reads then miss its scope", rel)
    for f in md_files:
        rel = f.relative_to(skill_dir).as_posix()
        text = f.read_text(encoding="utf-8", errors="replace")
        for m in MD_LINK.finditer(text):
            t = m.group(1)
            if re.match(r"^[a-z]+://", t) or t.startswith("#"):
                continue
            target = (f.parent / t.split("#")[0])
            if target.suffix == ".md" and target.exists() and target.resolve() != (skill_dir / "SKILL.md").resolve():
                rep.warn(f"links to '{t}'; a reference that links to another reference gets skimmed, not read. Link both from SKILL.md", rel)
        if WINDOWS_PATH.search(text):
            rep.warn("backslash path found; use forward slashes", rel)
        if len(shouts := SHOUT.findall(text)) > SHOUT_LIMIT * 2:
            rep.info(f"{len(shouts)} shouted directives; consider reasons over caps", rel)


def check_scripts(skill_dir: Path, rep: Report) -> None:
    sdir = skill_dir / "scripts"
    if not sdir.is_dir():
        return
    for f in sorted(sdir.rglob("*")):
        if not f.is_file() or f.name.startswith(".") or f.suffix in {".pyc", ".json", ".txt", ".md", ".xml", ".yaml", ".yml", ".toml"}:
            continue
        rel = f.relative_to(skill_dir).as_posix()
        head = f.read_text(encoding="utf-8", errors="replace")[:400]
        if f.suffix in {".py", ".sh", ".js", ".mjs", ".ts", ".rb"} and not head.startswith("#!") and f.suffix == ".sh":
            rep.warn("shell script without a shebang", rel)
        if f.suffix in {".py", ".sh", ".js", ".mjs"} and not re.search(r"(usage|Usage|USAGE|--help|argparse|docstring|\"\"\")", head):
            rep.info("no usage text in the first lines; the body tells the agent to run --help before reading source", rel)
        if re.search(r"curl[^\n|]*\|\s*(ba)?sh", f.read_text(encoding="utf-8", errors="replace")):
            rep.warn("pipes a download into a shell; audit or replace", rel)


def check_layout(skill_dir: Path, fm: dict, rep: Report) -> None:
    for f in sorted(skill_dir.iterdir()):
        if f.name in EXTRANEOUS_FILES:
            rep.warn(f"{f.name} inside the skill; humans read the repo readme, the agent reads SKILL.md. Extra docs get loaded by accident", f.name)
        if f.is_dir() and f.name not in KNOWN_DIRS and not f.name.startswith("."):
            rep.info(f"non-standard directory '{f.name}/'; conventional names are references/, scripts/, assets/, evals/, agents/", f.name)
    names = {f.name for f in skill_dir.iterdir()}
    if "SKILL.md" not in names and any(n.lower() == "skill.md" for n in names):
        rep.error("SKILL.md must be exactly that case")

    evals = skill_dir / "evals" / "evals.json"
    if evals.exists():
        try:
            data = json.loads(evals.read_text(encoding="utf-8"))
            count = len(data.get("evals", [])) if isinstance(data, dict) else 0
            if count < 3:
                rep.warn(f"only {count} eval(s); start with three that cover the baseline failures", "evals/evals.json")
            if isinstance(data, dict) and data.get("skill_name") not in (None, fm.get("name")):
                rep.warn(f"skill_name '{data.get('skill_name')}' does not match frontmatter name", "evals/evals.json")
        except json.JSONDecodeError as e:
            rep.error(f"invalid JSON: {e}", "evals/evals.json")
    else:
        rep.info("no evals/evals.json; the skill has not been tested against a baseline", "evals/")

    oai = skill_dir / "agents" / "openai.yaml"
    if oai.exists():
        text = oai.read_text(encoding="utf-8", errors="replace")
        user_invoked = fm.get("disable-model-invocation") is True
        m = re.search(r"allow_implicit_invocation:\s*(true|false)", text)
        if user_invoked and (not m or m.group(1) != "false"):
            rep.warn("skill is user-invoked (disable-model-invocation: true) but policy.allow_implicit_invocation is not false; keep both harnesses in sync", "agents/openai.yaml")
        if not user_invoked and m and m.group(1) == "false":
            rep.warn("policy.allow_implicit_invocation: false but frontmatter allows model invocation; keep both harnesses in sync", "agents/openai.yaml")
        sd = re.search(r"short_description:\s*\"?([^\"\n]+)\"?", text)
        if sd and not (25 <= len(sd.group(1).strip()) <= 64):
            rep.warn(f"short_description is {len(sd.group(1).strip())} chars; Codex expects 25-64", "agents/openai.yaml")


def validate(skill_dir: Path) -> Report:
    rep = Report()
    skill_md = skill_dir / "SKILL.md"
    if not skill_dir.is_dir():
        rep.error(f"{skill_dir} is not a directory", str(skill_dir))
        return rep
    if not skill_md.exists():
        rep.error("SKILL.md not found; skills must live at <name>/SKILL.md, a flat <name>.md is ignored by loaders")
        return rep
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    fm_text, body = split_frontmatter(text)
    if fm_text is None:
        rep.error("no YAML frontmatter (file must start with --- and close with ---)")
        return rep
    try:
        fm = parse_frontmatter(fm_text)
    except ValueError as e:
        rep.error(f"frontmatter parse error: {e}")
        return rep
    check_frontmatter(fm, skill_dir, rep)
    referenced = check_body(body, skill_dir, fm, rep)
    check_references(skill_dir, referenced, rep)
    check_scripts(skill_dir, rep)
    check_layout(skill_dir, fm, rep)
    return rep


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate a skill folder against the Agent Skills spec and house rules.")
    ap.add_argument("skill", help="path to the skill directory (contains SKILL.md)")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--json", action="store_true", help="emit findings as JSON")
    ap.add_argument("--quiet", action="store_true", help="suppress INFO lines")
    args = ap.parse_args(argv)

    skill_dir = Path(args.skill).expanduser().resolve()
    rep = validate(skill_dir)
    errors, warns, infos = rep.count("ERROR"), rep.count("WARN"), rep.count("INFO")
    failed = errors > 0 or (args.strict and warns > 0)

    if args.json:
        print(json.dumps({"skill": str(skill_dir), "ok": not failed, "errors": errors, "warnings": warns, "findings": rep.items}, indent=2))
        return 1 if failed else 0

    for it in rep.items:
        if args.quiet and it["level"] == "INFO":
            continue
        print(f"{it['level']:5} {it['where']}: {it['message']}")
    summary = f"{skill_dir.name}: {errors} error(s), {warns} warning(s), {infos} info"
    print(("FAIL " if failed else "OK   ") + summary)
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
