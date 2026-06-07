# MCP Tools — Best Practices (opinionated)

> **This file is OPINIONATED.** It is how I think MCP tools should be designed, taking a stronger and more specific position than any single source. The wire-format facts live in `specification.md` — read that for what the protocol *allows*; read this for what is *wise*.
>
> It synthesizes three sources and then commits to defaults:
> - **The MCP specification** (modelcontextprotocol.io) — the protocol truth.
> - **Anthropic, *Writing effective tools for agents*** — the principles and the eval-driven iteration loop. *(A tool is a contract between a deterministic system and a non-deterministic agent.)*
> - **AWS Labs MCP `DESIGN_GUIDELINES.md`** — concrete, prescriptive implementation rules.
>
> Where they agree, I adopt it. Where they differ, I pick. Where they're silent, I fill in. Examples are TypeScript on `@modelcontextprotocol/sdk`.

## Contents

1. [The mental model](#1-the-mental-model)
2. [Choose the right tools](#2-choose-the-right-tools)
3. [Naming: `domain_verb_noun`](#3-naming-domain_verb_noun)
4. [name vs title vs description](#4-name-vs-title-vs-description)
5. [Input schemas](#5-input-schemas)
6. [Return values](#6-return-values)
7. [Errors that teach](#7-errors-that-teach)
8. [Behavior annotations](#8-behavior-annotations)
9. [The action / audit pattern](#9-the-action--audit-pattern)
10. [Evaluate and iterate](#10-evaluate-and-iterate)
11. [Anti-pattern cheat sheet](#11-anti-pattern-cheat-sheet)
12. [Sources](#12-sources)

---

## 1. The mental model

**A tool is a contract for a non-deterministic consumer.** A normal API is called by deterministic code that a programmer debugged once. A tool is called by a model that re-derives, on every turn, *which* tool to use and *what* to pass — from nothing but the tool's name, description, and schema. So the tool definition is **prompt engineering**, and it is read on every decision. Treat the name/description/schema/return-shape with the same care you'd give a system prompt, because functionally that's what they are.

Distilling Anthropic's guidance, a good tool is three things — keep them in mind as you read on:

- **Clear** — intentionally and clearly defined, so the agent can't easily misuse it (unambiguous name, params, description).
- **Context-efficient** — it uses the agent's limited context judiciously (high-signal returns, bounded size).
- **Composable** — it maps to a natural unit of work and combines with other tools into diverse workflows.

Anthropic's own summary: effective tools are *"intentionally and clearly defined, use agent context judiciously, can be combined together in diverse workflows, and enable agents to intuitively solve real-world tasks."* Everything below is in service of that.

---

## 2. Choose the right tools

This is the highest-leverage decision, and it happens before you write a line of schema. Both Anthropic and AWS converge here: **design tools around the agent's workflows, not your backend's API surface.**

**Don't wrap every endpoint 1:1.** A tool per REST route feels complete but makes the agent do the integration work — chaining `list` → `filter` → `get` → `patch` just to accomplish one human-meaningful task. More tools is not better: it inflates selection errors and burns context just describing them. Build **fewer, higher-leverage** tools.

**Consolidate multi-step jobs into one call** when they're always done together. Anthropic gives several examples: rather than `list_users` + `list_events` + `create_event`, expose a `schedule_event` tool that finds availability and books in one shot; rather than `read_logs`, expose `search_logs` that returns only the relevant lines plus surrounding context; rather than `get_customer_by_id` + `list_transactions` + `list_notes`, expose a `get_customer_context` tool that compiles the relevant customer info at once. (The address-book intuition: a `search_contacts` tool beats a `list_contacts` tool that makes the agent read every entry token-by-token.) Each consolidation removes a round-trip, saves context, and removes a place the agent can go wrong.

**Prefer business intent over raw CRUD.** This is the heart of my approach. The model performs better when a tool names a thing it actually wants to do than when it has to assemble that intent from primitives.

```
Less ideal (implementation-level)     Better (intent-level)
user_create                           user_invite_staff_member
user_update                           user_update_password
user_delete                           user_disable_account
loan_get / loan_patch                 loan_calculate_rewrite_quote
                                      loan_record_online_payment
dns_get / dns_update                  dns_prepare_site_launch
                                      dns_verify_launch_ready
```

CRUD tools leak your schema into the model's job and force it to know your invariants (which fields to patch, in what order, with what side effects). Intent tools encapsulate that. **Don't expose a generic `action_execute` "do anything" tool** unless its schema is tightly constrained — a god-tool hides intent from the model and defeats the point of having tools at all.

**The test:** list the jobs a user will ask the agent to accomplish. Each job that's a coherent unit of work is a candidate tool. Endpoints are not jobs.

---

## 3. Naming: `domain_verb_noun`

A name is the first thing the model sees and the thing it keys its decision off. Make it carry intent.

**My default convention is `domain_verb_noun`:**

```
email_search_messages      calendar_create_event       loan_calculate_rewrite_quote
email_read_message         calendar_update_event       loan_record_online_payment
email_send_reply           audit_create_entry          dns_prepare_site_launch
user_update_password       audit_search_entries        dns_verify_launch_ready
```

Why this shape:

- **`domain_` namespaces the tool.** This is **Anthropic's** recommendation: with an agent potentially holding hundreds of tools across many servers, namespacing by service (`asana_search`, `jira_search`) and by resource (`asana_projects_search`, `asana_users_search`) is one of the most effective ways to stop the model picking the wrong tool. MCP only requires names to be unique *within* a server, so namespacing is technically optional — but adopt it by default; it's nearly free and it scales. (Anthropic notes that **prefix- vs suffix-based** namespacing has non-trivial, model-dependent effects — if you have evals, test both; absent that, a prefix is the sensible default.)
- **`verb_noun` makes intent obvious** to both the model and a human reading logs. AWS independently recommends action-oriented **verb-noun** names (`get_status`, `create_user`).
- **Drop the `domain_` prefix only for a small, single-purpose server** where there's no ambiguity (`search_documents`, `read_document`, `create_document`). The moment a server spans two domains, prefix everything.

**Style:** `snake_case`. AWS recommends it (it matches the official MCP reference servers and Python conventions; it accepts kebab-case and PascalCase but says to pick one). It reads cleanly and is unambiguous about word boundaries. The spec also permits `.`-segmented names like `admin.tools.list` — fine if your ecosystem uses it, but **pick one style and hold it across the whole server.** Inconsistency is itself a source of model error.

**Hard rules** (from the spec): 1–128 chars, case-sensitive, only `A–Z a–z 0–9 _ - .`, unique within the server. AWS adds a stricter practical ceiling — **keep the fully-qualified name (server prefix included) under 64 chars**, since some clients tack on prefixes/suffixes — and points to **MCP SEP-986** (the tool-name format proposal) for official naming guidance.

**Avoid vague verbs and nouns** that tell the model nothing: `run`, `handle`, `process`, `submit`, `do_action`, `manager`, `helper`, or a bare `search`. If the name doesn't say what it does, the description has to do all the work — and the model often decides from the name alone.

---

## 4. name vs title vs description

These are three different jobs. Conflating them is a common mistake.

- **`name`** — the stable, machine-facing identifier. The model and your logs key off it. Never rename a shipped tool casually; it's an API contract.
- **`title`** — the human-facing display label for UIs (`"Search emails"`). Cosmetic; the model doesn't depend on it.
- **`description`** — the model's instruction manual, and the highest-ROI text you'll write. Anthropic's heuristic: describe the tool the way you'd brief a **new hire** — surface the implicit context (special query formats, niche terminology, how the underlying resources relate) you'd otherwise assume. Refining descriptions alone moved Claude to a state-of-the-art result on SWE-bench Verified; clarity here compounds on every single call.

**A good description answers six questions:**

1. **What** does this tool do?
2. **When** should the model use it?
3. **What** does it return?
4. **When should the model NOT use it** / which tool to prefer instead?
5. Are there **side effects**?
6. Does it need **confirmation / user approval**?

```ts
description:
  "Search Gmail messages using Gmail search syntax. Use when the user wants to find emails " +   // what + when
  "by sender, subject, date, label, or keywords. Returns message summaries only — use " +        // returns + which-tool-next
  "email_read_message to fetch a full body. Read-only; no confirmation needed.",                 // side effects + confirmation
```

Compare the anti-pattern: `description: "Searches emails."` — answers question 1 weakly and ignores the other five. AWS makes a useful point here too: the description field can carry **explicit instructions to the assistant** ("prefer this tool when…", "the assistant should choose the format based on the user's need"). Use it to steer, not just to label.

---

## 5. Input schemas

The schema is a typed contract *and* documentation. Make it strict and self-describing so the model can't easily form an invalid call.

**Every property gets a `description`.** No exceptions. An undescribed parameter is a guess the model has to make.

**Use the type system to constrain the space:** `enum` for fixed value sets, `default` for the common case, `minimum`/`maximum`/`minLength`/`maxLength` for ranges, `format` for things like dates and emails. The more the schema rules out, the fewer malformed calls you get. (AWS expresses this as Pydantic `Field(...)` validators and `Literal[...]` enums; the TypeScript/Zod equivalents below do the same job.)

```ts
inputSchema: {
  query: z.string().describe(
    "Gmail search query. Supports operators: from:, subject:, after:, before:, has:attachment, label:."
  ),
  max_results: z.number().int().min(1).max(50).default(10)
    .describe("Maximum number of messages to return."),
  response_format: z.enum(["concise", "detailed"]).default("concise")
    .describe("concise = summaries only; detailed = include full headers."),
}
```

**Name parameters unambiguously.** Prefer `user_id` over `user` so the model knows exactly what to pass — a name, an id, an object? Precision in param names prevents whole categories of bad calls.

**Never ship grab-bag parameters** like `data: string` or `options: object`. They give the model nothing to reason about and turn the tool into a guessing game. If you're tempted by `options: object`, enumerate the real options as typed fields.

**Don't leak internal parameters into the schema.** Framework plumbing — loggers, request context, the FastMCP `ctx: Context` object — should be injected by the framework, not surfaced as a parameter the model fills in. In AWS's examples `ctx: Context` is a framework-provided argument used for error reporting/logging, not a user-facing field. The schema should contain only what the model is actually meant to supply.

**No-parameter tools** still need a valid schema: `{ "type": "object", "additionalProperties": false }`.

---

## 6. Return values

The return value is what the model reads to decide its next step. Design it for *continuation*, not just correctness.

**Return high-signal context, not raw dumps.** Filter to what matters for the agent's reasoning; technical noise wastes context and degrades decisions. The context window is finite and shared — in Claude Code, tool responses are capped around **~25,000 tokens** by default; treat that as a ceiling to design under, not a target to fill.

**Prefer human-readable identifiers over opaque UUIDs.** Agents reason far better with `"from": "billing@example.com"` and `"subject": "Invoice for May"` than with `"thread_id": "AAMkAGI2..."`. When an opaque id is genuinely needed for the next call, return it *alongside* the human-readable context, never instead of it.

```jsonc
// Good — the model can summarize, choose, and act without another call
{
  "messages": [
    { "id": "msg_123", "subject": "Invoice for May", "from": "billing@example.com",
      "date": "2026-06-01", "snippet": "Your invoice is ready...", "has_attachments": true }
  ],
  "next_page_token": "..."
}

// Bad — opaque; forces a follow-up call just to learn what these are
{ "ids": ["msg_123", "msg_456"] }
```

**Use structured output when the result is data the model or client will parse.** Declare an `outputSchema` and return `structuredContent`; for backwards compatibility also mirror the serialized JSON in a text block (the spec asks for this, and the SDK helps):

```ts
return {
  content: [{ type: "text", text: JSON.stringify({ messages }, null, 2) }],
  structuredContent: { messages },
};
```

**Give the agent a verbosity lever.** A `response_format` (`concise` / `detailed`) or similar enum lets the model trade detail for tokens per call. Default to the economical format and let it opt into more — both Anthropic (`response_format`) and AWS (`output_format: markdown|html|text`) endorse this. Markdown is a fine default for text meant for the model to read.

**Bound large responses by default.** Anthropic's concrete advice: implement some combination of **pagination, range selection, filtering, and truncation** with sensible default parameter values for any response that could grow large. Use cursor pagination (`tools/list` itself uses `cursor`/`nextCursor`; apply the same to your own list-shaped results), filter server-side, allow range selection, and truncate with an explicit signal that truncation happened — and when you truncate, steer the agent toward a more targeted strategy (many small, targeted searches over one broad one). Choose defaults so the *common* call returns a manageable amount without the model having to think about it. An unbounded list tool is a context-window accident waiting to happen.

---

## 7. Errors that teach

There are two error mechanisms (see `specification.md`), and using the right one changes whether the model can recover.

- **Tool execution errors** → return `isError: true` *inside* the result, with an actionable message. Use this for API failures, **input validation errors**, and business-logic failures. The model sees these and can self-correct.
- **Protocol errors** → JSON-RPC `error`. Reserve for "unknown tool / malformed request." These are largely hidden from the model's reasoning, so it usually can't recover from them.

The 2025-11-25 spec is explicit: put recoverable failures (including validation errors) in the result with `isError: true`, *not* as protocol errors, precisely so the model can read them and try again. Anthropic reinforces the *content* of those errors — prompt-engineer them to communicate specific, actionable fixes rather than opaque codes or tracebacks. (AWS's servers report failures through the FastMCP `ctx.error` channel with meaningful messages — same goal, framework-specific mechanism.)

**Make the message actionable.** Say what went wrong and what to do next:

```ts
// Good — the model knows exactly how to recover
return { isError: true, content: [{ type: "text",
  text: "Rate limit exceeded (100 req/min). Retry after 30s, or narrow the query with a date range." }] };

// Bad — opaque; the model can only give up or retry blindly
return { isError: true, content: [{ type: "text", text: "Error 429" }] };
```

A good error is just another high-signal return value: it steers the non-deterministic consumer toward a better next step.

---

## 8. Behavior annotations

Annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`, plus a display `title`) let a host reason about a tool's behavior — e.g. to auto-allow read-only calls but gate destructive ones behind confirmation.

**Set them honestly to match real behavior.** A read-only search should declare `readOnlyHint: true`; a delete should declare `destructiveHint: true`. Honest annotations are what let a host build good consent UX.

```ts
annotations: { readOnlyHint: true,  openWorldHint: true  }   // a web/email search
annotations: { destructiveHint: true, idempotentHint: false } // a delete
```

**But annotations are hints, not enforcement.** The spec says clients MUST treat them as **untrusted** unless the server itself is trusted. So annotations improve UX; they do **not** replace server-side validation and access control. Never rely on `readOnlyHint` to keep a tool safe — enforce that in the implementation.

---

## 9. The action / audit pattern

For systems where actions must be audited (and most business systems should be), the instinct is to expose an `audit_create_entry` tool and have the model call it after each action. **Don't make that the model's job.** It's easy for the model to forget, it leaks your compliance plumbing into the prompt, and it adds a round-trip.

Instead, **make the business tool own its whole lifecycle, server-side:**

```
Tool the model sees:   user_update_password
What it does internally (the model never orchestrates this):
  1. validate permissions
  2. execute the action
  3. write the audit entry        ← side effect, not a separate tool call
  4. capture domain errors / exceptions
  5. return a structured result (success | domain_error | exception)
```

The model calls one intent-shaped tool; auditing, validation, and error capture happen inside the wrapper where they can't be skipped. Expose `audit_search_entries` (read) on its own if the agent genuinely needs to query the audit log — but the *writing* of audit records belongs to the action, not the agent.

This is the natural endpoint of "intent over CRUD" (§2): the tool is a business action, and everything that *must* accompany that action is bundled into it rather than left for the model to remember.

---

## 10. Evaluate and iterate

This is Anthropic's contribution and the part teams most often skip. A tool surface is not "done" when it compiles — it's done when the model uses it well, and you only know that by watching it. The loop is **Prototype → Evaluate → Collaborate.**

1. **Prototype fast.** Stand the tools up and load them into a real agent (Claude Code / Claude Desktop via MCP). Test in the loop before polishing.
2. **Write realistic, verifiable evals — lots of them.** Generate many tasks grounded in real-world use, each paired with a verifiable outcome (an exact-match check, or Claude-as-judge for fuzzier cases — but avoid verifiers so strict they reject valid phrasings). Strong tasks often require *multiple* tool calls; deliberately avoid superficial "sandbox" prompts that don't stress-test the tools. Keep a held-out set so you don't overfit descriptions to your "training" tasks.
3. **Run them and measure.** Run programmatically with simple agentic loops (one per task). Beyond top-line accuracy, track tool runtime, number of tool calls, token consumption, and tool errors — redundant calls hint at pagination/limit tuning; invalid-parameter errors hint at unclear descriptions. Without evals you can't tell whether a change helped or hurt, and even small, precise refinements compound (Anthropic credits exactly this loop for a SWE-bench Verified state-of-the-art result).
4. **Collaborate with the agent.** Concatenate the eval transcripts and hand them to Claude (e.g. in Claude Code): it's strong at spotting where the tools confused it — wrong tool picked, ambiguous param, contradictory descriptions, missing return field — and at refactoring many tools at once to stay self-consistent. But read between the lines: what the agent *omits* often matters more than what it says. The agent is your best tool-design reviewer, not the final word.

Treat each tool definition as a prompt you iterate, not code you write once.

> If you're building this as a *skill* and want a rigorous loop, the `skill-creator` workflow (eval prompts → with/without runs → review) is the same idea applied to skills.

---

## 11. Anti-pattern cheat sheet

| Don't | Do | Why |
|---|---|---|
| Mirror every API endpoint as a tool | Build fewer, intent-shaped tools | Endpoints aren't jobs; the model shouldn't integrate your API |
| Expose raw CRUD (`user_update`) | Expose intent (`user_update_password`) | CRUD leaks invariants into the model's job |
| One generic `action_execute` god-tool | Specific business tools | A god-tool hides intent and defeats tool selection |
| Bare names (`search`, `run`, `handle`) | `domain_verb_noun` (`email_search_messages`) | The model often decides from the name alone |
| Mixed naming styles in one server | One style, consistently | Inconsistency causes selection errors |
| `data: string` / `options: object` | Enumerated, typed, described params | Grab-bags give the model nothing to reason about |
| Undescribed parameters | `description` on every property | An undescribed param is a guess |
| Return `{ ids: [...] }` only | Return human-readable context + ids | Opaque ids force extra calls |
| Unbounded list responses | Paginate / filter / truncate by default | Protect the ~25k-token budget |
| Validation failure as protocol error | `isError: true` with actionable text | Only execution errors let the model self-correct |
| `Error 429` | "Rate limited; retry after 30s" | Errors are high-signal returns |
| Make the model call `audit_create_entry` | Audit inside the action wrapper | The model will forget; plumbing isn't its job |
| Trust `readOnlyHint` for safety | Enforce in the implementation | Annotations are untrusted hints |
| Ship descriptions/schemas blind | Iterate against realistic evals | Small refinements compound; measure them |

---

## 12. Sources

- **MCP Tools Specification** — modelcontextprotocol.io (`2025-11-25`; also `2025-06-18`). Wire format, annotations, error mechanisms. See `specification.md`.
- **Anthropic — *Writing effective tools for agents*** — https://www.anthropic.com/engineering/writing-tools-for-agents — the contract framing, five principles (right tools, namespacing, meaningful context, token efficiency, descriptions-as-prompt-engineering), and the Prototype→Evaluate→Collaborate loop.
- **AWS Labs — MCP `DESIGN_GUIDELINES.md`** — https://github.com/awslabs/mcp/blob/main/DESIGN_GUIDELINES.md — prescriptive (Python/FastMCP) rules: `snake_case` verb-noun names under 64 chars, strict Pydantic `Field` schemas with `Literal` enums and validators, instructing the assistant inside parameter descriptions, structured Pydantic responses, `ctx.error` reporting, and safe execution of untrusted code. Points to **MCP SEP-986** for the official tool-name format.

> **Sourcing note (verified 2026-06-07):** the Anthropic and AWS sources above were fetched and read in full via browser, and the attributions in this file were reconciled against the originals. In particular: namespacing/consolidation/pagination/token-budget guidance is **Anthropic's** (AWS does not prescribe service-prefixed names, a consolidation example, or pagination); AWS's security guidance is specifically about **safely executing untrusted code**. Quotes are paraphrased unless in quotation marks.

The opinionated defaults (`domain_verb_noun`, intent-over-CRUD, the action/audit wrapper) are mine; the labs guides are cited as backing where they actually support the point.
