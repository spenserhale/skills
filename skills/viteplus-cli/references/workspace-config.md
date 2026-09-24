# Monorepo layout and pnpm workspace configuration

## Workspace layout

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

## Root pnpm-workspace.yaml

```yaml
packages:
  - apps/*
  - packages/*
```

## Root package.json

Root scripts delegate to `vp run` so one command fans out across the workspace:

```json
{
  "name": "my-monorepo",
  "private": true,
  "scripts": {
    "dev": "vp run dev",
    "build": "vp run build",
    "check": "vp check",
    "test": "vp run test"
  }
}
```

## Standard task names

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

## Workspace dependencies with the `workspace:` protocol

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
- Local packages are resolved from the workspace, not the npm registry
- Changes to shared packages are immediately available during development
- No accidental version mismatches

Docs: [workspace: protocol](https://pnpm.io/workspaces#workspace-protocol-workspace), [pnpm Workspaces Guide](https://pnpm.io/workspaces).

## Key pnpm workspace settings

- **Root lockfile** (enabled by default): All packages share one `pnpm-lock.yaml` for faster installs and singleton dependencies
- **linkWorkspacePackages**: Defaults to `false`. Setting it to `true` in `.npmrc` auto-links local packages without the `workspace:` prefix, which is less explicit and not recommended; use explicit `workspace:` ranges instead

## Shared workspace packages

Keep shared internal packages in `packages/` and prefer ESM format:
- `packages/config`: Shared config schemas or objects
- `packages/core`: Business logic, API clients, data transformations
- `packages/ui`: React/Vue components (if applicable)
