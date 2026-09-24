# Principle 8: Async-aware execution

Most CLIs treat async APIs the way the underlying HTTP endpoint does: submit returns a job ID, poll returns a status, that's the agent's problem. Two failure modes follow. Either the agent writes its own poll loop (wastes tokens, gets it subtly wrong), or it doesn't, and the workflow fails because the result wasn't ready when the next step ran.

The fix is `--wait`.

```bash
# Without --wait — agent has to write its own polling loop
$ aicli zone import --file=example.com.zone
job_id: job_5fa2e0
status: queued

$ aicli jobs get job_5fa2e0
job_id: job_5fa2e0
status: running
progress: 0.34

$ aicli jobs get job_5fa2e0
job_id: job_5fa2e0
status: complete
records_imported: 142

# With --wait — same workflow, one command, no polling logic
$ aicli zone import --file=example.com.zone --wait
job_id: job_5fa2e0
status: complete
records_imported: 142

# The job ledger survives across invocations
$ aicli jobs list
JOB_ID      STATUS    KIND          STARTED              DURATION
job_5fa2e0  complete  zone.import   2026-05-08T18:22:11  37s
job_7c1422  running   zone.scan     2026-05-08T18:24:02  12s
```

`--wait` blocks until completion. Behind it, the CLI runs a poll loop with exponential backoff and jitter, and writes job state to a local ledger. A `jobs` subcommand exposes the ledger: `jobs list`, `jobs get <id>`, `jobs prune`.

This collapses several agent turns into one: same workflow, fewer tokens, no polling logic the agent has to get right. The job ledger is what makes retries safe (Principle 4): if the agent's `--wait` invocation gets killed mid-poll, the next invocation finds the existing job rather than submitting a new one.

## What good looks like

- `--wait` on every submitting command that wraps an async API
- Polling implementation with exponential backoff and jitter (don't hammer the upstream)
- Persistent job ledger (`~/.aicli/jobs.jsonl` is fine; append-only, easy to inspect)
- A `jobs` parent command exposing `list` / `get` / `prune`
- Idempotency keys propagated into the ledger so resubmissions resolve to existing jobs

## Grading

> **Blocker:** async commands return a job ID and stop, forcing the agent to write its own poll loop. **Friction:** `--wait` exists but doesn't survive disconnect, or no way to inspect in-flight jobs. **Target:** `--wait` on every async submission with a durable, recoverable ledger.
