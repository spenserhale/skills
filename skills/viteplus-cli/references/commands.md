# Vite+ command reference

Authoritative source for every command: the official [Vite+ Guide](https://viteplus.dev/guide/). Run `vp <command> --help` for the current flags before guessing.

## Project setup

| Command | Purpose | Docs |
|---------|---------|------|
| `vp create [template]` | Scaffold new apps, packages, or monorepos interactively | [vp create](https://viteplus.dev/guide/create) |
| `vp migrate` | Migrate from another tool to Vite+ | [vp migrate](https://viteplus.dev/guide/migrate) |
| `vp install` | Install dependencies (pnpm wrapper) | [vp install](https://viteplus.dev/guide/install) |

## Development and building

| Command | Purpose | Docs |
|---------|---------|------|
| `vp dev` | Start Vite dev server with HMR | [vp dev](https://viteplus.dev/guide/dev) |
| `vp build` | Production build for web apps (outputs to dist/) | [vp build](https://viteplus.dev/guide/build) |
| `vp check` | Run format, lint, and type checks together | [vp check](https://viteplus.dev/guide/check) |

## Workspace-level tasks

| Command | Purpose | Docs |
|---------|---------|------|
| `vp run <script>` | Run scripts/tasks across workspaces with built-in caching and dependency ordering | [vp run](https://viteplus.dev/guide/run) |
| `vp pack` | Build libraries (with `tsdown`) or standalone executables | [vp pack](https://viteplus.dev/guide/pack) |
| `vpx <command>` | Execute binaries from packages or npm | [vpx](https://viteplus.dev/guide/run) |

## Examples

```bash
# Create a new monorepo
vp create vite:monorepo

# Start dev server
vp dev

# Build production (web apps)
vp build

# Type-check and lint entire workspace
vp check

# Run 'test' script in all packages that define it, in dependency order
vp run test

# Run a task in specific packages
vp run build --filter "@my/*"
vp run build --filter "apps/cli-*"

# Run a task and all its dependencies
vp run build -t

# Package CLI apps or libraries for distribution
vp pack

# Run with verbose output and see caching info
vp run build -v

# Install dependencies (wrapper around pnpm)
vp install
```

## Key `vp run` options

- `-r` (recursive): Run across all workspace packages in dependency order
- `-t` (transitive): Run in one package plus all its dependencies
- `-w`: Target root package only
- `--filter <pattern>`: Select packages by name/glob (pnpm-compatible syntax like `@my/*`)
- `-v`: Verbose mode; shows task summaries and cache hits
- `--concurrency-limit N`: Control simultaneous task execution (default: 4)
- `--parallel`: Ignore dependencies, run all tasks with unlimited concurrency

## Official links

- Main guide: https://viteplus.dev/guide/
- GitHub: https://github.com/voidzero-dev/vite-plus
- Vite: https://vite.dev
