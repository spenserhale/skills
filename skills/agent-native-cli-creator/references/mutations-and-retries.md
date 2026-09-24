# Principle 4: Safe retries and explicit mutation boundaries

Agents retry. A human glances at a duplicate row and notices; an agent doesn't.

```bash
# Idempotent create — second call returns the existing record, not a duplicate
$ aicli record create --type=A --name=www --content=192.0.2.10
id: rec_a14b9c
existing: false

$ aicli record create --type=A --name=www --content=192.0.2.10
id: rec_a14b9c
existing: true

# --dry-run shows what would happen, with no side effect
$ aicli record delete rec_a14b9c --dry-run
status: dry_run
would_delete:
  id: rec_a14b9c
  type: A
  name: www
  content: 192.0.2.10
```

## What good looks like

- Idempotency tokens (`--idempotency-key=...`) or natural keys (zone+type+name+content for DNS) so a retried `create` returns the existing resource, not a duplicate
- `--dry-run` on anything consequential, returning the same shape as the real call plus `status: dry_run`
- Destructive ops require an explicit `--force` (or `--idempotency-key`); never default-yes
- Every mutation response returns the resource id and current state, so the agent has something to reference on the next call

## Async wrinkle

Retries on long-running ops aren't just about idempotency at submission; they're about idempotency across the whole submit-poll-collect arc. If the agent's first invocation submits a job and dies mid-poll, the second invocation must find the in-flight job, not start a new one. A persistent job ledger solves this (see the async reference for the ledger design).

## Grading

> **Blocker:** silent duplication on retry. **Friction:** scriptable destruction without preview. **Target:** idempotent mutations, durable job state, explicit destructive flags.
