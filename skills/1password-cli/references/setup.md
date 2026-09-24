# Installation and authentication

How `op` gets installed and how it authenticates in each environment. Read this when `op` is missing or a command fails to authenticate.

## Authentication Methods

`op inject` (and all `op` commands) authenticate via one of these methods:

| Method | When to use | Setup |
|--------|-------------|-------|
| **Biometric unlock** | Local development | Enable 1Password desktop app integration |
| **Service Account** | CI/CD pipelines | Set `OP_SERVICE_ACCOUNT_TOKEN` env var |
| **Connect server** | Self-hosted infrastructure | Set `OP_CONNECT_HOST` + `OP_CONNECT_TOKEN` |

For local dev, biometric unlock through the desktop app is the smoothest experience — no tokens to manage, just authenticate with Touch ID / fingerprint when prompted.

---

## Installation

```bash
# macOS
brew install 1password-cli

# Verify
op --version
```

Enable the desktop app integration for biometric unlock: open the 1Password desktop app → Settings → Developer → enable "Integrate with 1Password CLI".
