# Writing the description

The description is the trigger. It is the only part of the skill loaded for every skill in every session, and the model picks a skill from possibly a hundred descriptions using nothing else. Write it before the body, and rewrite it after testing.

## Shape

For a model-invoked skill:

```
<What it does, one clause>. Use when <situations, phrases, file types, contexts>, even if <the user does not say the obvious keyword>. <Not for X; use <sibling> instead.>
```

For a user-invoked skill (`disable-model-invocation: true`), a human-facing one-liner. No trigger list; no model reads it for routing:

```
A relentless interview to sharpen a plan or design.
```

## Rules

1. **Third person, about the skill and the user.** "Processes Excel files", "Use when the user asks". Never "I can help" or "you can use this to". The description is injected into a system prompt; point-of-view drift causes mis-selection.
2. **Front-load the leading word.** The first few words carry the concept the model scans for: `Build MCP servers`, `Convert JSON to TOON`, `Arrange · Act · Assert`.
3. **Name concrete triggers.** Actual phrases users type, file extensions, tool names, symptoms, situations. "Use when handling PDFs, forms, or document extraction" beats "helps with documents".
4. **Be a little pushy.** Models under-trigger. Add "even if they don't say X" and "whenever the user mentions Y" clauses. The docx skill's description ends with what not to use it for, which is the same idea from the other side.
5. **Draw the near-miss boundary.** Say what adjacent task belongs to a sibling skill: "For designing the server's tools specifically, hand off to mcp-tools-creator." That sentence prevents both over-triggering and orphaned tasks.
6. **Never summarize the workflow.** A description that says "runs two review passes" makes the agent run two passes from the description and skip the body, where it would have found the third. Say when, not how.
7. **One trigger per branch.** Synonyms that rename the same branch are the same trigger written twice. Cut them.
8. **Cut identity the body carries.** No "This skill", no "A skill that". Start with the verb or the noun.
9. **Length.** Hard cap 1,024 characters. Aim for 300 to 600. Long descriptions with an ever-growing list of specific queries overfit; generalize to categories of intent instead.
10. **No angle brackets, quote if it contains a colon.**

## Worked examples

Under-triggers (too polite, no phrases):

```
description: Guidance for building dashboards.
```

Fixed:

```
description: Build a simple, fast internal dashboard for company data. Use whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of company data, even if they don't explicitly ask for a "dashboard."
```

Over-triggers (keyword soup, no boundary):

```
description: Anything about MCP, tools, servers, resources, prompts, transports, auth, sampling, roots, elicitation, SDKs, protocols.
```

Fixed with a leading concept and a hand-off:

```
description: Build Model Context Protocol (MCP) servers: architecture, lifecycle, transports, resources, prompts, authorization, and client features. Use whenever the user wants to create, scaffold, design, or debug an MCP server, mentions @modelcontextprotocol/sdk or FastMCP, or describes exposing tools or data to an LLM host even without saying "MCP". For designing the server's tools specifically, hand off to the mcp-tools-creator skill.
```

Summarizes the workflow (the agent will shortcut):

```
description: Code review skill: runs a correctness pass, then a style pass, then posts comments.
```

Fixed:

```
description: Review a diff, PR, or branch for defects before merge. Use when the user asks for a review, says "check my changes", or is about to open or merge a PR.
```

## Testing the description

Write 20 realistic prompts, 8 to 10 that should fire and 8 to 10 near-misses that should not. Realistic means file names, typos, backstory, casual phrasing, and enough substance that the agent would actually benefit from a skill (one-step asks like "read this file" never trigger anything). The near-misses must share vocabulary with the skill and need something else. Run each three times on a fresh agent; a query passes at a trigger rate of at least 0.5 in the expected direction. Details and tooling: `testing.md`.

Under-triggering: add the user's actual phrasing and a pushy clause. Over-triggering: add the near-miss boundary and the sibling hand-off. Then re-test on prompts you did not tune against.
