# Principle 3: Errors that teach, and enumerate

Errors are the highest-signal moment an agent gets. They fire exactly when the agent doesn't know what to do next. Don't waste them.

```bash
# Useless — agent now has to read --help, parse, guess, retry
$ aicli record create --type=AAAAA --name=www --content=2001:db8::1
error: invalid type

# Better — names the valid set, agent self-corrects in one retry
$ aicli record create --type=AAAAA --name=www --content=2001:db8::1
error: --type must be one of: A, AAAA, CNAME, MX, TXT, NS, SRV, CAA (got: "AAAAA")
hint: did you mean AAAA?
```

The pattern generalizes. Any time the CLI rejects input against an enum, an enum-shaped resource list (zone names, profile names, region codes), or a schema, surface the enumeration in the error itself. Don't make the agent run `--help` to discover it.

## What good looks like

- Validate input early, before any side effects
- Echo the offending value in quotes (`got: "AAAAA"`) so the agent can grep its own state
- Enumerate valid values when the cause is enum-shaped
- Include a working example in the error text where the fix isn't obvious
- No raw stack traces; those are a sign your error layer is unfinished

## Grading

> **Blocker:** silent or vague failure. **Friction:** error names the problem but not the solution. **Target:** error includes the valid set and a working invocation.
