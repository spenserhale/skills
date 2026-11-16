#!/usr/bin/env python3
"""Check filled walker briefs for leaks before they are sent.

A walker that is told the route cannot show whether the route is findable, and
a leaked brief produces a walk that looks perfectly normal. This script checks
the mechanical part. Whether a flagged word is one a user would say without
having seen the interface is your call: reword the line, or pass --allow.

Usage:
    python3 check_brief.py <brief.md> [<brief.md> ...] --labels "<label>, <label>, ..." [--allow "<word>, ..."]

Arguments:
    brief.md   one or more filled briefs
    --labels   every label, menu name, section name, and field name on the
               shortest path, comma separated, spelled as the interface spells them
    --allow    words from those labels that a user would say unprompted

Checks, on the lines you filled in (lines identical to the template are skipped):
    - a {{slot}} left unfilled, or the template's header comment still present
    - a label from --labels, or a distinctive word from one, used in the brief
    - a path to a source file, or wording that points at the code

Exit codes: 0 clean, 1 something to fix (each is listed with its line), 2 usage.
"""

import argparse
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "walker-brief.md"

# Words too common in interfaces to give a route away on their own. A label that is
# one of these alone ("Settings", "Save") is skipped; a label made of several
# ("Add new") is checked as a whole phrase.
GENERIC = {
    "settings", "setting", "open", "save", "saved", "add", "new", "edit", "next", "back", "done",
    "cancel", "close", "name", "type", "your", "with", "from", "into", "this", "that", "more",
    "connect", "continue", "create", "enable", "turn", "choose", "select", "change", "show",
    "view", "list", "page", "screen", "button", "menu", "home", "app", "apps", "main", "general",
}
MIN_WORD = 4  # shorter words ("on", "off", "set") match too much ordinary prose to be useful
SOURCE_FILE = re.compile(r"(?<![\w/:.])[\w./~-]*\.(?:tsx?|jsx?|html?|py|vue|svelte|css|php|rb|go|rs|swift|kt)\b")
CODE_WORDS = re.compile(r"\b(?:repo|repository|source code|codebase|pull request|the diff)\b", re.I)
CLIP = 150  # characters of the offending line shown


def template_lines():
    if not TEMPLATE.is_file():
        return set()
    text = re.sub(r"<!--.*?-->", "", TEMPLATE.read_text(encoding="utf-8"), flags=re.S)
    return {line.strip() for line in text.splitlines() if line.strip()}


def split_list(value):
    return [item.strip() for item in (value or "").split(",") if item.strip()]


def needles(labels, allowed):
    """Map each thing to look for onto (regex, the label it came from)."""
    found = {}
    for label in labels:
        words = re.findall(r"[A-Za-z][A-Za-z'-]*", label)
        distinctive = [w.lower() for w in words if len(w) >= MIN_WORD and w.lower() not in GENERIC]
        if not distinctive and len(words) < 2:
            continue
        # A label with no distinctive word is only meaningful as the whole phrase.
        for term in distinctive or [label.lower()]:
            if term in allowed:
                continue
            # Accept a plural or singular form of the same word.
            stem = term[:-1] if term.endswith("s") and len(term) > MIN_WORD else term
            found.setdefault(term, (re.compile(rf"(?<![\w-]){re.escape(stem)}s?(?![\w-])", re.I), label))
    return found


def check(path, look_for, skip):
    """Return [(line text, what is wrong with it, "brief:line")] for one brief."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as err:
        return [("", f"cannot read ({err.strerror})", str(path))]
    name = path.name.replace(".brief.md", "").replace(".md", "")
    found = []
    if "<!--" in text:
        found.append(("", "the template's header comment is still in the brief; delete it before sending", name))
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line in skip:
            continue
        where = f"{name}:{number}"
        for slot in sorted(set(re.findall(r"\{\{\s*\w+\s*\}\}", line))):
            found.append((line, f"slot {slot} is not filled in", where))
        for term, (pattern, label) in look_for.items():
            if pattern.search(line):
                found.append((line, f'"{term}"' + ("" if term == label.lower() else f' (label "{label}")'), where))
        without_urls = re.sub(r"\b\w+://\S+", "", line)
        for match in SOURCE_FILE.finditer(without_urls):
            found.append((line, f"path to a source file ({match.group(0)})", where))
        for match in CODE_WORDS.finditer(line):
            found.append((line, f'points at the code ("{match.group(0)}")', where))
    return found


def report(found):
    """One entry per distinct line, however many briefs repeat it."""
    groups = {}
    for line, what, where in found:
        entry = groups.setdefault(line, {"what": [], "where": []})
        if what not in entry["what"]:
            entry["what"].append(what)
        if where not in entry["where"]:
            entry["where"].append(where)
    out = []
    for line, entry in groups.items():
        out.append(f"{', '.join(entry['where'])}: {'; '.join(entry['what'])}")
        if line:
            out.append("    " + (line if len(line) <= CLIP else line[:CLIP - 1] + "…"))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("briefs", nargs="+", help="filled walker briefs")
    parser.add_argument("--labels", default="", help="labels on the shortest path, comma separated")
    parser.add_argument("--allow", default="", help="label words a user would say unprompted, comma separated")
    args = parser.parse_args()

    labels = split_list(args.labels)
    if not labels:
        print('error: pass --labels with every label, menu name, and field name on the shortest path, '
              'for example --labels "Secrets, Add provider, Save provider".', file=sys.stderr)
        return 2
    paths = [Path(p) for p in args.briefs]
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        print(f"error: not a file: {', '.join(missing)}", file=sys.stderr)
        return 2

    allowed = {w.lower() for w in split_list(args.allow)}
    look_for = needles(labels, allowed)
    skip = template_lines()
    found = [item for path in paths for item in check(path, look_for, skip)]
    if found:
        print("\n".join(report(found)))
        print("\nFor each line: reword it so the walker has to find that for itself, or pass --allow for a word "
              "a user would say without having seen the interface.")
        return 1
    print(f"{len(paths)} brief(s) checked against {len(labels)} label(s): no leaks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
