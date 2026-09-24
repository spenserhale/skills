# Principle 2: Structured, parseable output (TOON, JSON, CSV)

Aligned tables with ANSI color are for humans. Agents extracting an ID need a parser-friendly format on stdout.

```bash
# TOON is the default machine format — compact, indentation-based,
# cheaper in tokens than JSON for typical record shapes
$ aicli record list
records[3]:
  - id: rec_a14b9c
    type: A
    name: www
    content: 192.0.2.10
  - id: rec_b22e71
    type: A
    name: api
    content: 192.0.2.11
  - id: rec_c8d04f
    type: CNAME
    name: docs
    content: www.example.com

# --json and --csv when the consumer prefers them
$ aicli record list --json | jq '.records[0].id'
"rec_a14b9c"

$ aicli record list --csv
id,type,name,content
rec_a14b9c,A,www,192.0.2.10
rec_b22e71,A,api,192.0.2.11
rec_c8d04f,CNAME,docs,www.example.com

# Errors go to stderr; exit codes signal failure class
$ aicli record get rec_does_not_exist
$ echo $?
4
# stderr: error: record not found: rec_does_not_exist (zone: example.com)
```

## Why TOON as default

TOON (Token-Oriented Object Notation) was designed for LLM consumption: indentation-based, no quote noise, materially cheaper in tokens than JSON for typical record/list shapes. Agents are the primary consumer of structured CLI output, so the default should be optimized for them. JSON and CSV stay first-class for tooling that already speaks them (jq, Excel, dataframes). Spec: https://github.com/johannschopplich/toon

## Choosing the default per consumer

The convention this skill recommends is `--toon` (default), `--json`, `--csv`: three first-class flags, one canonical name each, applied uniformly across every data-returning command.

| Format | When to default to it | Why |
|---|---|---|
| **TOON** | Agent / LLM consumers | Indentation-based, no quote noise, materially fewer tokens than JSON for typical record/list shapes. The format is designed for LLM context efficiency. |
| **JSON** | Tooling consumers (jq, scripts, other CLIs) | Universally parsed; the path of least surprise for non-LLM automation. |
| **CSV** | Tabular data, spreadsheets, dataframes | Frictionless handoff to Excel / pandas / dbt. Only makes sense for flat tabular outputs. |

Pick one canonical flag per format and apply it uniformly. Don't ship `--toon` on some commands and `--format=toon` on others. Don't add `-j` as an alias "for convenience." Inconsistency at this layer is its own category of brokenness.

For nested objects, TOON and JSON both work; CSV doesn't and shouldn't be supported on commands whose output isn't naturally tabular. When CSV isn't supported, return a clean enumerated error: `error: --csv is only supported for list-style commands; this command returns a nested object. Use --toon (default) or --json.`

## What good looks like

- A single canonical machine format flag set: `--toon` (default), `--json`, `--csv`; never `--format=toon` mixed with `--output json`
- Coverage: every data-returning command supports all three; no "this one only does JSON" gaps
- Stable exit-code taxonomy (e.g., `0` ok, `1` generic error, `2` usage, `3` config, `4` not-found, `5` auth, `6` rate-limited)
- Results to stdout, diagnostics to stderr, ANSI suppressed when stdout isn't a TTY

## Grading

> **Blocker:** no structured output. **Friction:** coverage gaps; some commands JSON-capable, others not. **Target:** uniform `--toon` / `--json` / `--csv` across the CLI with documented exit codes.
