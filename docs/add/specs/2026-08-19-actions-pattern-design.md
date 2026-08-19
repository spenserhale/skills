# Actions Pattern Skill Design

## Purpose

Create a project-level `actions-pattern` skill that helps an agent design, implement,
refactor, and review Laravel application actions. The skill must distinguish the general
Action pattern from the optional `lorisleiva/laravel-actions` package, preserve the
project's existing architecture, and keep transport concerns out of reusable business
logic.

Success means another agent can consistently choose an action boundary, write a typed
and container-resolvable `handle()` method, adapt it to HTTP/queue/event/console entry
points when appropriate, and test the result without turning every small operation into
an action.

## Architecture

Use progressive disclosure:

- `skills/actions-pattern/SKILL.md` contains activation boundaries, architectural
  decisions, the implementation workflow, a compact plain-action example, and the
  quality checklist.
- `skills/actions-pattern/references/laravel-actions.md` contains package-specific
  conventions for `AsAction`, context adapters, validation, queue behavior, and test
  helpers. The entrypoint tells the agent to read it only when the package is installed
  or explicitly requested.
- `readme.md` indexes the new framework-specific project skill.

No scripts or assets are justified: this skill teaches context-sensitive design and
implementation choices rather than a deterministic transformation.

## Behavioral Design

The skill first inspects `composer.json`, existing action classes, project instructions,
and tests. It follows established naming and location conventions when they are coherent;
otherwise it defaults to verb-first classes grouped by domain under `app/Actions` and a
single public `handle()` method.

The `handle()` method forms the reusable application boundary. It accepts typed business
inputs (models, scalars, value objects, or DTOs), returns an explicit business result,
and does not depend on HTTP requests, responses, console I/O, or queue wrappers. Entry
points translate their input into `handle()` arguments and translate its output back to
their transport. Constructor injection supplies collaborators.

An action represents one meaningful application task, not necessarily one database
statement. It may orchestrate smaller actions or domain services when that composition
remains cohesive. Multi-write invariants belong in a transaction at the orchestration
boundary. Retryable actions must be designed for idempotency, and externally visible
side effects must not escape before a transaction commits.

The package path uses `AsAction` and container resolution, with `asController`, `asJob`,
`asListener`, and `asCommand` as adapters only when needed. It explains package-specific
dispatch and fake/assertion helpers without making the dependency mandatory. Plain
Laravel projects continue to use ordinary action classes and thin framework adapters.

## Error Handling

Actions should fail explicitly with domain-meaningful exceptions or framework exceptions
appropriate to the application layer. They must not swallow errors or convert them into
HTTP/CLI responses inside `handle()`. Boundary adapters may translate failures when the
project requires a transport-specific response. Transactions should roll back naturally;
external effects should be deferred until commit when atomicity matters.

## Testing

Test the action's observable result and state changes directly. Add focused tests for
authorization, validation, routing, queue dispatch, listener mapping, or command mapping
only for entry points the action actually exposes. Package mocks and spies verify
collaboration at a caller boundary; they do not replace testing the action's real
behavior. Queue-specific assertions use the package helpers when available.

Validation of the skill itself consists of the bundled skill validator plus manual checks
that the activation description excludes GitHub Actions, the package reference is routed
correctly, examples keep transports out of `handle()`, and the README entry/install
guidance matches repository conventions.

## Approaches Considered

1. **One comprehensive `SKILL.md`.** Easiest to browse as a file, but every invocation
   would load package-specific controllers, jobs, listeners, commands, and testing details
   even for a plain action. Rejected because it weakens discovery and wastes context.
2. **Concise entrypoint plus one package reference.** Keeps universal Action-pattern
   guidance immediately available while loading Laravel Actions details only when needed.
   Selected as the best balance of usability and progressive disclosure.
3. **Many narrow references by execution context.** Offers the smallest conditional
   reads, but fragments a modest body of guidance and increases routing overhead. Rejected
   as premature complexity.

## Assumptions & Decisions

- **Location:** Create the skill in `public/skills/actions-pattern` because `public` is the
  active skills repository and Laravel is a project framework, not a global user tool.
- **Invocation:** Keep implicit discovery enabled. The description will explicitly cover
  Laravel actions and exclude GitHub Actions to avoid the largest naming collision.
- **Package policy:** Do not add `lorisleiva/laravel-actions` merely to use the pattern.
  Use it when already installed or explicitly requested; otherwise generate a plain,
  container-resolvable class.
- **Method convention:** Default to `handle()` because it aligns with both source articles,
  Laravel conventions, and Laravel Actions. Preserve a coherent project-wide alternative
  such as `execute()` rather than mixing styles.
- **Naming:** Prefer verb-first task sentences such as `CreateOrder` or
  `SendResetPasswordEmail`. Do not require an `Action` suffix; follow an existing coherent
  suffix convention if present.
- **Inputs:** Prefer explicit typed parameters or a DTO when the input has a stable shape.
  Arrays remain acceptable when they match an established local convention or validated
  payload and a DTO would add no clarity.
- **Final classes:** Do not require `final`; this is a local style choice and package
  mocking/container replacement should remain compatible with project conventions.
- **Source currency:** Link to the official 2.x documentation and tell the agent to inspect
  the installed Composer version. Avoid hard-coding the currently published package
  version into durable instructions.
- **Documentation footprint:** Add one focused package reference, not copied upstream
  manuals. The skill should distill decisions and link to authoritative docs for uncommon
  APIs.
