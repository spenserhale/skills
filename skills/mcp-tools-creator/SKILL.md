---
name: mcp-tools-creator
description: Design and implement MCP (Model Context Protocol) tools that AI agents use reliably — choosing what to expose, naming (domain_verb_noun over raw CRUD), JSON Schema inputs, structured outputs, error handling, behavior annotations, and the audit/action wrapper pattern — backed by the official tools specification and an opinionated best-practices guide. Use this skill whenever the user is adding, designing, naming, reviewing, or refactoring MCP tools, deciding which tools a server should expose, writing tool descriptions or inputSchema, shaping tool return values, or asks how to make MCP tools work well for an agent like Claude. For the broader server (transports, resources, prompts, auth, lifecycle), use the mcp-creator skill.
---

# MCP Tools Creator

Design the tools an MCP server exposes so a model invokes the **right** tool with the **right** arguments and gets back enough to take the **next** step — without burning tokens or guessing. Tools are the part of MCP the model actually drives, so this is where design effort pays off most.

This skill is the tool-design half of the MCP picture. For the rest of the server — transports, resources, prompts, authorization, lifecycle — use the **`mcp-creator`** skill.

## When to use

Activate this skill when the user is:

- Adding or designing tools on an MCP server (any language; examples here are TypeScript)
- Deciding **what** tools to expose — which operations become tools, how coarse or fine-grained
- Naming tools, or debating naming conventions / namespacing
- Writing tool `description`s or `inputSchema` / `outputSchema`
- Shaping what a tool **returns** (content vs structured content, how much context)
- Handling tool errors, or designing behavior **annotations** (read-only, destructive, idempotent, open-world)
- Reviewing or refactoring an existing tool surface that "the model keeps misusing"
- Building an action/audit pattern where tools map to business intent

**Hand off:** for transports, resources, prompts, auth, or general server setup, use **`mcp-creator`**. For designing a *CLI* (not an MCP tool), use `agent-native-cli-creator`. For *installing* an existing MCP server into a client, use `add-mcp`.

## The two reference layers

- **`references/specification.md`** — the faithful **SPECIFICATION** of tools: exact methods (`tools/list`, `tools/call`), the tool definition object, `inputSchema`/`outputSchema`, annotations, `CallToolResult`, content types, the two error mechanisms, and 2025-11-25 changes. Read it to get the wire format and field names exactly right.
- **`references/best-practices.md`** — the **opinionated** guide: how to choose, name, scope, schema, and return tools well, synthesizing the official MCP guidance, Anthropic's *Writing effective tools for agents*, and the AWS Labs design guidelines, then taking a stronger position than any of them. Read it whenever you're making a design decision.

Read the spec for *what's allowed*; read best-practices for *what's wise*.

## Core philosophy

**Design tools around the agent's intent and workflow, not your backend's API surface.** A model performs better when a tool maps to a meaningful unit of work it actually wants to do (`loan_record_online_payment`) than when it has to orchestrate three generic CRUD calls (`loan_get` → `loan_patch` → `audit_create`) to achieve the same thing. The tool is a *contract for the model*, and its name, description, schema, and return value are all prompt-engineering. Get those right and the model uses the tool correctly the first time; get them vague and you pay in retries and wrong calls on every invocation.

The full reasoning, with examples and trade-offs, is in `best-practices.md`. The condensed rules below are the everyday checklist.

## Quick reference — the everyday rules

**Naming** — default to `domain_verb_noun` (e.g. `email_search_messages`, `calendar_create_event`, `loan_calculate_rewrite_quote`). Drop the `domain_` prefix only for a small single-purpose server. Names must be stable, unique, 1–128 chars, `A–Z a–z 0–9 _ - .`. Avoid vague verbs: `run`, `handle`, `process`, `submit`, `do_action`, `manager`, `helper`.

**Choose intent over CRUD** — don't mechanically expose `create`/`read`/`update`/`delete` for every entity. Prefer business-intent tools (`user_update_password`, `dns_prepare_site_launch`) over implementation-level ones (`user_patch`). Consolidate multi-step workflows the agent always does together into one tool.

**`name` / `title` / `description`** are three different jobs:
- `name` — stable machine identifier (the model and logs key off this).
- `title` — human display label for UIs.
- `description` — the model's instruction manual. It SHOULD answer: what it does, when to use it (and when **not** to), what it returns, side effects, and whether it needs confirmation.

**Schemas are strongly typed and described** — every property gets a `description`; use `enum`, `default`, `minimum`/`maximum`, `format`. Never ship `data: string` or `options: object` grab-bags.

**Return enough context to continue** — prefer human-meaningful fields (names, dates, snippets) over bare opaque IDs. Use `structuredContent` (with `outputSchema`) when the result is data the model or client will parse; still mirror it in a text block for compatibility.

**Errors that teach** — return execution failures as `isError: true` inside the result with a message the model can act on ("rate limit exceeded, retry after 30s"), not a bare protocol error. Reserve JSON-RPC protocol errors for "unknown tool / malformed request."

**Annotate behavior honestly** — set `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint` to match reality so hosts can gate consequential calls. Remember clients treat these as untrusted unless the server is trusted — annotations inform UX, they don't replace server-side validation.

**Keep audit/side-effects inside the action** — for an action+audit architecture, the business tool (`user_update_password`) should validate, execute, write the audit entry, and return a structured result *server-side*. Don't make the model call a separate `audit_create_entry` after every action; that leaks implementation detail into the model's job and is easy to skip.

## A worked tool definition

The shape to aim for (see `best-practices.md` for why each part is the way it is):

```ts
server.registerTool(
  "email_search_messages",
  {
    title: "Search emails",
    description:
      "Search Gmail messages using Gmail search syntax. Use when the user wants to find " +
      "emails by sender, subject, date, label, or keywords. Returns message summaries only — " +
      "use email_read_message to fetch a full body. Read-only; no confirmation needed.",
    inputSchema: {
      query: z.string().describe(
        "Gmail search query. Supports operators: from:, subject:, after:, before:, has:attachment, label:."
      ),
      max_results: z.number().int().min(1).max(50).default(10)
        .describe("Maximum number of messages to return."),
    },
    annotations: { readOnlyHint: true, openWorldHint: true },
  },
  async ({ query, max_results }) => {
    const messages = await gmail.search(query, max_results); // [{id, subject, from, date, snippet, has_attachments}]
    return {
      content: [{ type: "text", text: JSON.stringify({ messages }, null, 2) }],
      structuredContent: { messages },
    };
  }
);
```

Contrast with the anti-pattern — `name: "search"`, `description: "Searches emails."`, `inputSchema: { data: { type: "string" } }`, returning `{ ids: [...] }`. Same capability; the model can't tell when to use it, what to pass, or what it got back.

## Workflow for designing a tool surface

1. **List the agent's jobs**, not your endpoints. What will a user actually ask the agent to accomplish?
2. **Map each job to one intent-shaped tool.** Consolidate always-together steps; split genuinely independent ones. Check against the "choose intent over CRUD" guidance in `best-practices.md`.
3. **Name** them `domain_verb_noun`; keep names consistent across the surface.
4. **Write the description** to answer the six questions (what / when / returns / not-for / side effects / confirmation).
5. **Define strict, described schemas** for inputs and (when parseable) outputs.
6. **Design the return value** to carry the next-step context, not just IDs.
7. **Set annotations** to match real behavior; put validation, auth, and audit *inside* the implementation.
8. **Exercise it like an agent would** — run realistic tasks, watch where the model misfires, and tighten the name/description/schema/return. Anthropic's evaluation loop in `best-practices.md` describes this; treat the tool spec as a prompt you iterate.
