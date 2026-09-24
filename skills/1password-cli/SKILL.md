---
name: 1password-cli
description: "1Password CLI (op) reference focused on op inject for securely populating config files, env files, and scripts from vault secrets. Use when the user wants to set up or populate a .env file from 1Password, hydrate a config template with real credentials, references secrets with op:// URIs, runs or asks about op inject, op run, or op read, or needs 1Password Service Accounts or Connect servers in CI/CD, even if they only say 'pull the secrets from 1Password' or 'stop hardcoding this password'. Not for other secret managers such as HashiCorp Vault, AWS Secrets Manager, or Doppler."
---

# 1Password CLI

A skill for working with the 1Password CLI (`op`) to manage secrets securely — with a focus on `op inject` for populating configuration and environment files from vault references.

## When to use

Any task that reads secrets out of a 1Password vault from the terminal, a script, or CI. Other secret managers (HashiCorp Vault, AWS Secrets Manager, Doppler) have their own CLIs and are out of scope.

## Security principles

**Never hardcode secrets.** The entire point of this workflow is to keep plaintext credentials out of source control.

- `.env.example` (contains `op://` references) → **safe to commit**
- `.env` (contains resolved plaintext secrets) → **must be in `.gitignore`**
- Secret values are fetched live from 1Password at injection time, never stored in intermediate files that get checked in

---

## The `op://` Secret Reference URI

All secret references follow this structure:

```
op://<vault>/<item>/<section>/<field>
```

| Segment | Example | Description |
|---------|---------|-------------|
| `vault` | `Private` | The 1Password vault containing the item |
| `item` | `Herd Local Env` | The item name or ID |
| `section` | `Variables` | The section within the item (optional for top-level fields) |
| `field` | `seeder_user_password` | The specific field to retrieve |

**Example in a `.env.example` template:**

```bash
DB_PASSWORD="op://Private/Herd Local Env/Variables/db_password"
SEEDER_USER_PASSWORD="op://Private/Herd Local Env/Variables/seeder_user_password"
API_KEY="op://Development/API Keys/production/api_key"
```

---

## The Key Command: `op inject`

`op inject` reads a template file containing `op://` references and outputs a new file with those references replaced by the actual secret values fetched live from your 1Password vault.

```bash
op inject -i <input-template> -o <output-file>
```

| Flag | Meaning |
|------|---------|
| `-i` | Input template file (contains `op://` references) |
| `-o` | Output file (contains resolved plaintext secrets) |

**Standard usage — populate a `.env` from a template:**

```bash
op inject -i .env.example -o .env
```

**Pipe from stdin:**

```bash
cat .env.example | op inject -o .env
```

**Write to stdout (useful for debugging or piping):**

```bash
op inject -i .env.example
```

### The setup pattern

A typical project includes a setup script that wraps `op inject`:

```json
{
  "scripts": {
    "setup:env": "op inject -i .env.example -o .env"
  }
}
```

Every developer runs `npm run setup:env` (or equivalent) once per machine or whenever secrets rotate. Each person resolves secrets from their own 1Password account, keeping the team in sync without sharing plaintext credentials.

---

## Other Useful `op` Commands

### `op run` — inject secrets as environment variables at runtime

Pass secrets directly to a subprocess without writing them to disk:

```bash
op run -- npm start
op run --env-file=.env.example -- docker compose up
```

### `op read` — read a single secret to stdout

Fetch one value for use in scripts or one-off lookups:

```bash
op read "op://Private/Herd Local Env/Variables/db_password"
```

### Quick comparison

| Command | Use Case |
|---------|----------|
| `op inject -i template -o output` | Populate config/`.env` files from templates |
| `op run -- <command>` | Pass secrets as env vars to a subprocess at runtime |
| `op read op://vault/item/field` | Read a single secret value to stdout |

---

## Installation and authentication

Read `references/setup.md` when `op` is not installed, or a command fails with an authentication or session error; it covers the Homebrew install, desktop-app biometric unlock, Service Account tokens for CI/CD, and Connect servers.

---

## Start with `op --help`

When unsure about any command's flags or syntax:

```bash
op --help
op inject --help
op run --help
op read --help
```
