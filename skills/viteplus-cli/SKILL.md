---
name: viteplus-cli
description: "Vite+ (vp) task runner and packager reference for monorepos that mix browser apps and Node CLI packages on pnpm workspaces: vp create, dev, build, check, run, pack, migrate, and vpx. Use when the user mentions Vite+, vite-plus, vp, or tsdown, is setting up or working in a monorepo that combines web apps and CLI tools, needs pnpm-workspace.yaml and the workspace: protocol wired up for Vite+, asks about workspace-level task orchestration, task caching, or packaging a CLI or library, or is migrating another tool to Vite+ with vp migrate. Not for plain Vite or pnpm questions where vp is not in play."
---

# Vite+ (vp) CLI Reference

Vite+ is a task runner and packager for monorepos that hold both browser apps and Node CLI packages on top of pnpm workspaces. One `vp run <script>` fans a task out across packages in dependency order with caching; `vp pack` (tsdown) builds the CLI and library packages that `vp build` (Vite) does not.

The official [Vite+ Guide](https://viteplus.dev/guide/) is the authoritative source; this skill carries the essentials. Run `vp --help` and `vp <command> --help` before guessing at flags.

## Scope

Vite+ in a monorepo, and the pnpm workspace wiring it depends on. Plain Vite app questions or pnpm questions with no `vp` in play belong to those tools' own docs or skills.

## Commands

| Command | Use it for |
|---------|-----------|
| `vp create [template]` | Scaffold apps, packages, or a monorepo (`vp create vite:monorepo`) |
| `vp migrate` | Move an existing repo from another tool to Vite+ |
| `vp install` | Install dependencies (pnpm wrapper) |
| `vp dev` / `vp build` | Vite dev server with HMR / production build of web apps to `dist/` |
| `vp check` | Format, lint, and type checks in one pass |
| `vp run <script>` | Run a script across packages with caching and dependency ordering |
| `vp pack` | Build libraries or CLIs with tsdown; `--exe` for a standalone executable |
| `vpx <command>` | Execute a binary from a package or npm |

Flags that decide `vp run` behavior: `-r` all packages in dependency order, `-t` one package plus its dependencies, `-w` root only, `--filter "@my/*"` (pnpm syntax), `--parallel` to ignore ordering, `-v` to see cache hits. Full tables, examples, and the option list: `references/commands.md`.

## Decision rules

- Web app (`apps/web-*`): scripts are `vite` / `vite build`; `vp dev` and `vp build` drive them.
- CLI or library (`apps/cli-*`, `packages/*`): `"type": "module"`, an `exports` map into `dist/`, and `"build": "vp pack"`; configure `pack` (`dts`, `sourcemap`, `minify`, `watch`) in `vite.config.ts`.
- Standard task names in every package are `dev`, `build`, `check`, `test`, so root scripts can be `vp run dev`, `vp run build`, `vp check`, `vp run test`. Libraries and CLIs skip `dev`.
- Local dependencies use `workspace:*` or `workspace:^`, never a version number, so they resolve from the workspace and never drift.
- Shared code lives in `packages/` (`config`, `core`, `ui`) as ESM.

## Gotchas

- Vite consumes linked workspace packages as source. A CommonJS package needs `optimizeDeps.include` and `build.commonjsOptions.include` in the consuming web app's `vite.config.ts`, or dev and build behave differently.
- The root `package.json` is `"private": true`; without it a stray publish ships the whole workspace.
- `linkWorkspacePackages` defaults to `false`; leave it and use explicit `workspace:` ranges rather than relying on auto-linking.
- All packages share one root `pnpm-lock.yaml` by default; a per-package lockfile means the workspace setting was changed.
- `vp pack --exe` is experimental; ship it as an extra, not the only distribution.
- `--concurrency-limit` defaults to 4; `--parallel` ignores dependency order entirely, so use it only for independent tasks.

## References

| Read when | File |
|-----------|------|
| Looking up a command, its docs link, `vp run` options, or a worked command example | `references/commands.md` |
| Laying out the repo, writing `pnpm-workspace.yaml`, root scripts, `workspace:` deps, or pnpm settings | `references/workspace-config.md` |
| Configuring a web app or a CLI/library package, `vp pack` options, or a CommonJS dependency | `references/packaging.md` |
