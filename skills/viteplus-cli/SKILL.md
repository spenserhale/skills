---
name: viteplus-cli
description: Vite+ monorepo task runner and packager for mixed browser and Node CLI projects
---

# Vite+ (vp) CLI Reference

Vite+ is a modern task runner and packager designed for monorepos containing both browser apps and Node CLI packages. It unifies the development and build experience across mixed project types while integrating with pnpm workspaces.

> **Note:** This skill teaches the essentials of Vite+. For the latest features, configuration options, and updates, consult the official [Vite+ Guide](https://viteplus.dev/guide/) — it's the authoritative source.

## When to use

Activate this skill when:
- User is setting up or working with a **monorepo combining web apps and CLI tools**
- User wants to use **`vp create`, `vp dev`, `vp build`, `vp check`, `vp run`, or `vp pack`** commands
- User needs help **integrating Vite+ with pnpm workspaces** (`pnpm-workspace.yaml`)
- User is asking about **workspace-level task orchestration**, **task caching**, or **CLI packaging**
- User mentions **vite-plus**, **vp**, or **tsdown** in the context of monorepo tooling
- User is migrating from another tool to Vite+ (`vp migrate`)

## Monorepo Structure with Vite+ + pnpm

### Workspace layout

Separate browser apps, CLI packages, and shared libraries:

```text
repo/
  pnpm-workspace.yaml
  package.json (root, with "private": true)
  apps/
    web-admin/         # Vite web app
    web-marketing/     # Vite web app
    cli-sync/          # Node CLI packaged with vp pack
    cli-import/        # Node CLI packaged with vp pack
  packages/
    ui/                # Shared ESM components
    core/              # Shared business logic
    config/            # Shared config
```

### Root pnpm-workspace.yaml

```yaml
packages:
  - apps/*
  - packages/*
```

### Root package.json

```json
{
  "name": "my-monorepo",
  "private": true,
  "scripts": {
    "dev": "vp run dev",
    "build": "vp run build",
    "check": "vp check",
    "pack": "vp pack"
  }
}
```

## Core Vite+ Commands

**Reference:** [Vite+ Guide](https://viteplus.dev/guide/)

### Project Setup

| Command | Purpose | Docs |
|---------|---------|------|
| `vp create [template]` | Scaffold new apps, packages, or monorepos interactively | [vp create](https://viteplus.dev/guide/create) |
| `vp migrate` | Migrate from another tool to Vite+ | [vp migrate](https://viteplus.dev/guide/migrate) |
| `vp install` | Install dependencies (pnpm wrapper) | [vp install](https://viteplus.dev/guide/install) |

### Development and Building

| Command | Purpose | Docs |
|---------|---------|------|
| `vp dev` | Start Vite dev server with HMR | [vp dev](https://viteplus.dev/guide/dev) |
| `vp build` | Production build for web apps (outputs to dist/) | [vp build](https://viteplus.dev/guide/build) |
| `vp check` | Run format, lint, and type checks together | [vp check](https://viteplus.dev/guide/check) |

### Workspace-level Tasks

| Command | Purpose | Docs |
|---------|---------|------|
| `vp run <script>` | Run scripts/tasks across workspaces with built-in caching and dependency ordering | [vp run](https://viteplus.dev/guide/run) |
| `vp pack` | Build libraries (with `tsdown`) or standalone executables | [vp pack](https://viteplus.dev/guide/pack) |
| `vpx <command>` | Execute binaries from packages or npm | [vpx](https://viteplus.dev/guide/run) |

### Examples

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

**Key `vp run` options:**
- `-r` (recursive): Run across all workspace packages in dependency order
- `-t` (transitive): Run in one package plus all its dependencies
- `-w`: Target root package only
- `--filter <pattern>`: Select packages by name/glob (pnpm-compatible syntax like `@my/*`)
- `-v`: Verbose mode; shows task summaries and cache hits
- `--concurrency-limit N`: Control simultaneous task execution (default: 4)
- `--parallel`: Ignore dependencies, run all tasks with unlimited concurrency

## Workspace Dependencies with pnpm

### Using workspace: protocol

In any package's `package.json`, depend on local packages without version numbers:

```json
{
  "name": "@acme/cli-sync",
  "dependencies": {
    "@acme/core": "workspace:*",
    "@acme/config": "workspace:^"
  }
}
```

This ensures:
- Local packages are resolved from the workspace, not npm registry
- Changes to shared packages are immediately available during development
- No accidental version mismatches

### Key pnpm workspace settings

- **Root lockfile (default enabled)**: All packages share one `pnpm-lock.yaml` for faster installs and singleton dependencies
- **linkWorkspacePackages**: Set to `true` in `.npmrc` if you want automatic linking without `workspace:` prefix (less explicit, not recommended)

## Web Apps vs CLI Packages

### Web apps (in `apps/web-*`)

Use native Vite workflow with `vp dev` and `vp build`:

```json
{
  "name": "@acme/web-admin",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "check": "tsc --noEmit && eslint src"
  }
}
```

Vite automatically handles:
- HMR (hot module replacement)
- CSS/asset bundling
- Dependency pre-bundling for workspace packages

### CLI packages (in `apps/cli-*` or distributed libraries)

Package as ESM-first TypeScript libraries using `vp pack` (powered by [tsdown](https://viteplus.dev/guide/pack)):

```json
{
  "name": "@acme/cli-sync",
  "type": "module",
  "exports": {
    ".": "./dist/index.js",
    "./cli": "./dist/cli.js"
  },
  "scripts": {
    "build": "vp pack",
    "check": "tsc --noEmit && eslint src"
  }
}
```

Configure in `vite.config.ts`:

```javascript
export default {
  build: {
    // ... Vite build config for apps
  },
  pack: {
    // Outputs declaration files (.d.ts)
    dts: true,
    // Watch mode for development
    watch: false,
    // Generate source maps
    sourcemap: true,
    // Minify output (optional)
    minify: true
  }
}
```

Then package with `vp pack`:

```bash
# Build library/CLI package
vp pack

# Build with declaration files
vp pack src/index.ts --dts

# Watch mode for development
vp pack --watch

# Create standalone executable (experimental)
vp pack --exe
```

**`vp pack` includes out-of-the-box:**
- Declaration file generation (`.d.ts`)
- Multiple output formats (ESM and CommonJS)
- Source maps
- Minification
- Standalone executable support (via tsdown's `exe` option) — great for distributing CLIs without requiring Node.js

## Important Constraints

### Vite and monorepo dependencies

Vite processes linked workspace packages as source code rather than pre-bundled modules. This works best when those packages are **ESM** (ES modules). If a linked dependency is CommonJS or needs special handling, configure it in your web app's `vite.config.ts`:

```javascript
export default {
  optimizeDeps: {
    include: ['@acme/legacy-cjs-package']
  },
  build: {
    commonjsOptions: {
      include: ['@acme/legacy-cjs-package']
    }
  }
}
```

See [Vite Dependency Pre-bundling](https://vite.dev/guide/dep-pre-bundling.html) for details.

### Shared workspace packages best practices

Keep shared internal packages in `packages/` and prefer ESM format:
- `packages/config` — Shared config schemas or objects
- `packages/core` — Business logic, API clients, data transformations  
- `packages/ui` — React/Vue components (if applicable)

Use the [`workspace:` protocol](https://pnpm.io/workspaces#workspace-protocol-workspace) in `package.json` to ensure local resolution:

```json
{
  "dependencies": {
    "@acme/config": "workspace:^",
    "@acme/core": "workspace:*"
  }
}
```

### pnpm workspace configuration

- **Root lockfile** (enabled by default): All packages share one `pnpm-lock.yaml` for faster installs and singleton dependencies
- **linkWorkspacePackages**: Defaults to `false`; use explicit `workspace:` ranges for clarity instead of auto-linking

## Standard Task Names

Standardize script names across packages so `vp run` works consistently:

```json
{
  "scripts": {
    "dev": "...",           // Start dev (web) or skip (lib/CLI)
    "build": "...",         // Build output (web → dist, lib → dist)
    "check": "...",         // Type-check and lint
    "test": "..."           // Run unit tests (optional)
  }
}
```

Then at root:

```json
{
  "scripts": {
    "dev": "vp run dev",
    "build": "vp run build",
    "check": "vp check",
    "test": "vp run test"
  }
}
```

## References

### Vite+ Official
- **Main Guide**: https://viteplus.dev/guide/
- **vp create**: https://viteplus.dev/guide/create
- **vp dev**: https://viteplus.dev/guide/dev
- **vp build**: https://viteplus.dev/guide/build
- **vp run**: https://viteplus.dev/guide/run
- **vp pack** (tsdown): https://viteplus.dev/guide/pack
- **vp check**: https://viteplus.dev/guide/check
- **vp migrate**: https://viteplus.dev/guide/migrate
- **GitHub**: https://github.com/voidzero-dev/vite-plus

### pnpm Workspaces
- **pnpm Workspaces Guide**: https://pnpm.io/workspaces
- **workspace: protocol**: https://pnpm.io/workspaces#workspace-protocol-workspace

### Related Tools
- **Vite Official**: https://vite.dev
- **Vite Dependency Pre-bundling**: https://vite.dev/guide/dep-pre-bundling.html
