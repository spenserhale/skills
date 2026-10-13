#!/usr/bin/env python3
"""Summarize where a Claude Code session spent its context.

Reads a session transcript (JSONL) and prints per-tool call counts and result
sizes, the largest tool results, failed calls, and every user message in order.
Tool result bodies are never printed, only their sizes, so the output stays
small even for a transcript of many megabytes.

With no path, picks the newest transcript for the current directory (or the
nearest parent that has one). Check the printed first prompt to confirm it is
the session you mean.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Rough English/code average; good to about +/-25%, which is enough to rank
# findings. Report results as approximate.
CHARS_PER_TOKEN = 4
PREVIEW_CHARS = 110
MESSAGE_CHARS = 300
# Wide enough for a full MCP tool name (mcp__server__tool).
TOOL_WIDTH = 46
# Keys tried, in order, to describe a tool call in one line.
INPUT_KEYS = ("command", "file_path", "pattern", "url", "query", "prompt", "skill", "description")


def projects_dir():
    return Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude")) / "projects"


def find_transcript(start):
    """Newest transcript for `start` or its nearest parent that has any."""
    tried = []
    start = Path(start).resolve()
    for folder in (start, *start.parents):
        encoded = projects_dir() / re.sub(r"[^A-Za-z0-9]", "-", str(folder))
        tried.append(str(encoded))
        files = sorted(encoded.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
        if files:
            return files[0]
    sys.exit(
        "No transcript found. Looked for *.jsonl in:\n  "
        + "\n  ".join(tried[:4])
        + "\nPass the transcript path as the first argument, or use --cwd with the"
        " directory the session started in. Outside Claude Code there is no"
        " transcript to read; estimate from the conversation instead."
    )


def one_line(text, limit):
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def text_of(content):
    """Visible text of a message or tool result, plus a count of non-text parts."""
    if isinstance(content, str):
        return content, 0
    text, other = [], 0
    for part in content or []:
        if isinstance(part, dict) and part.get("type") == "text":
            text.append(part.get("text", ""))
        elif isinstance(part, dict) and part.get("type") != "tool_result":
            other += 1
    return "\n".join(text), other


def describe(tool_input):
    if not isinstance(tool_input, dict) or not tool_input:
        return ""
    for key in INPUT_KEYS:
        if tool_input.get(key):
            return one_line(tool_input[key], PREVIEW_CHARS)
    return one_line(json.dumps(tool_input), PREVIEW_CHARS)


def parse(path):
    calls, by_id, messages = [], {}, []
    usage, seen_requests, compactions, session = {}, set(), 0, ""
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("isSidechain"):
                continue
            session = session or row.get("sessionId", "")
            if row.get("isCompactSummary") or row.get("subtype") == "compact_boundary":
                compactions += 1
                continue
            message = row.get("message")
            if not isinstance(message, dict):
                continue
            content = message.get("content")
            if row.get("type") == "assistant":
                # One API response is split across several lines that repeat the
                # same usage block, so count each response id once.
                if message.get("id") not in seen_requests:
                    seen_requests.add(message.get("id"))
                    for key, value in (message.get("usage") or {}).items():
                        if isinstance(value, int):
                            usage[key] = usage.get(key, 0) + value
                for part in content if isinstance(content, list) else []:
                    if part.get("type") == "tool_use":
                        call = {
                            "n": len(calls) + 1,
                            "tool": part.get("name", "?"),
                            "input": describe(part.get("input")),
                            "tokens": 0,
                            "error": "",
                            "at_request": len(seen_requests),
                        }
                        calls.append(call)
                        by_id[part.get("id")] = call
            elif row.get("type") == "user":
                results = [p for p in content if isinstance(p, dict) and p.get("type") == "tool_result"] if isinstance(content, list) else []
                for part in results:
                    call = by_id.get(part.get("tool_use_id"))
                    if not call:
                        continue
                    body, other = text_of(part.get("content"))
                    call["tokens"] = len(body) // CHARS_PER_TOKEN
                    call["non_text_parts"] = other
                    if part.get("is_error"):
                        call["error"] = one_line(body, PREVIEW_CHARS)
                body, _ = text_of(content)
                if body.strip() and not results and not row.get("isMeta"):
                    messages.append({"after_call": len(calls), "text": one_line(body, MESSAGE_CHARS)})
    requests = len(seen_requests)
    for call in calls:
        # Each later request re-reads this result as (usually cached) input.
        call["carried"] = requests - call.pop("at_request")
    return {"session": session, "requests": requests, "compactions": compactions,
            "usage": usage, "calls": calls, "messages": messages}


def by_tool(calls):
    table = {}
    for call in calls:
        row = table.setdefault(call["tool"], {"calls": 0, "errors": 0, "tokens": 0, "max": 0})
        row["calls"] += 1
        row["errors"] += bool(call["error"])
        row["tokens"] += call["tokens"]
        row["max"] = max(row["max"], call["tokens"])
    return dict(sorted(table.items(), key=lambda item: -item[1]["tokens"]))


def render(path, data, top):
    calls, usage = data["calls"], data["usage"]
    errors = [c for c in calls if c["error"]]
    out = [
        f"transcript   {path} ({path.stat().st_size // 1024} KB)",
        f"session      {data['session']}",
        f"first prompt {data['messages'][0]['text'] if data['messages'] else '(none found)'}",
        f"requests {data['requests']}   user messages {len(data['messages'])}   "
        f"tool calls {len(calls)} ({len(errors)} errors)   compactions {data['compactions']}",
        f"usage        output {usage.get('output_tokens', 0):,}   cache read {usage.get('cache_read_input_tokens', 0):,}   "
        f"cache write {usage.get('cache_creation_input_tokens', 0):,}   uncached input {usage.get('input_tokens', 0):,}",
        "",
        f"{'TOOL':<{TOOL_WIDTH}}{'CALLS':>6}{'ERRORS':>8}{'RESULT_TOK':>12}{'AVG':>8}{'MAX':>8}",
    ]
    for tool, row in by_tool(calls).items():
        out.append(f"{tool[:TOOL_WIDTH - 1]:<{TOOL_WIDTH}}{row['calls']:>6}{row['errors']:>8}{row['tokens']:>12,}"
                   f"{row['tokens'] // row['calls']:>8,}{row['max']:>8,}")
    out += ["", f"LARGEST RESULTS (tokens = chars/{CHARS_PER_TOKEN}, approximate; carried = later requests that re-read the result)"]
    for call in sorted(calls, key=lambda c: -c["tokens"])[:top]:
        out.append(f"  #{call['n']:<4}~{call['tokens']:>7,} tok  carried {call['carried']:<4}{call['tool']}  {call['input']}")
    if errors:
        out += ["", "FAILED CALLS"]
        out += [f"  #{c['n']:<4}{c['tool']}  {c['input']}\n        -> {c['error']}" for c in errors]
    out += ["", "USER MESSAGES (after call # shows where each landed)"]
    out += [f"  [{i}] after call #{m['after_call']}: {m['text']}" for i, m in enumerate(data["messages"], 1)]
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("transcript", nargs="?", help="path to a session .jsonl; default: newest for the current directory")
    parser.add_argument("--cwd", default=os.environ.get("CLAUDE_PROJECT_DIR", "."),
                        help="directory the session started in, used to locate its transcript (default: $CLAUDE_PROJECT_DIR or .)")
    parser.add_argument("--top", type=int, default=10, help="how many of the largest tool results to list (default: 10)")
    parser.add_argument("--json", action="store_true", help="print the full parsed data as JSON, every call included")
    args = parser.parse_args()

    path = Path(args.transcript).expanduser() if args.transcript else find_transcript(args.cwd)
    if not path.is_file():
        sys.exit(f"Transcript not found: {path}")
    data = parse(path)
    if not data["requests"] and not data["messages"]:
        sys.exit(f"No conversation found in {path}. Is it a Claude Code session transcript (.jsonl)?")
    print(json.dumps({"transcript": str(path), **data, "by_tool": by_tool(data["calls"])}, indent=1) if args.json else render(path, data, args.top))


if __name__ == "__main__":
    main()
