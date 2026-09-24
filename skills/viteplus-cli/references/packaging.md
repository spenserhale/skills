# Web apps vs CLI packages, and vp pack

## Contents

- Web apps (in `apps/web-*`)
- CLI packages (in `apps/cli-*` or distributed libraries)
- Linked CommonJS dependencies in web apps

## Web apps (in `apps/web-*`)

Use the native Vite workflow with `vp dev` and `vp build`:

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

## CLI packages (in `apps/cli-*` or distributed libraries)

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

`vp pack` includes out of the box:
- Declaration file generation (`.d.ts`)
- Multiple output formats (ESM and CommonJS)
- Source maps
- Minification
- Standalone executable support (via tsdown's `exe` option), useful for distributing CLIs without requiring Node.js

## Linked CommonJS dependencies in web apps

Vite processes linked workspace packages as source code rather than pre-bundled modules. This works best when those packages are ESM. If a linked dependency is CommonJS or needs special handling, configure it in the web app's `vite.config.ts`:

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
