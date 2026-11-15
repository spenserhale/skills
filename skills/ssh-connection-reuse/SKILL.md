---
name: ssh-connection-reuse
description: "Reuse one authenticated SSH connection per host (OpenSSH ControlMaster), so a 1Password or other hardware-backed SSH agent approves once per host instead of once per command. Use before running several ssh, scp, rsync or git-over-ssh commands against the same machine, before fanning parallel agents or builds out to remote hosts, and whenever ssh keeps triggering 1Password or Touch ID prompts or fails with 'communication with agent failed', even if the user only says 'stop making me approve every ssh'. Not for keeping an interactive remote shell alive across disconnects; use tmux or a similar multiplexer for that."
---

# SSH Connection Reuse

With the private key in an agent (1Password, Secretive, a YubiKey), every new SSH connection asks
the agent to sign, and the agent may ask the human. OpenSSH can keep the first authenticated
connection open and run every later command to that host through it: one approval, then nothing
until it expires. Make sure that is in place before you run a batch of remote commands.

## Steps

1. **See whether the host already shares.** `ssh -G <host> | grep -E '^control(master|path|persist) '`.
   `controlmaster auto` with a `controlpath` means it is configured. `ssh -O check <host>` says
   whether a shared connection is open right now ("Master running").
2. **Configured: open it once, then work normally.** Before a batch, and always before parallel
   work, run `ssh -fN <host>`: it authenticates (the one approval), goes to the background and
   stays for the configured time. Every later `ssh`, `scp`, `rsync -e ssh` or git command to that
   host reuses it with no prompt.
3. **Not configured: add the options to your own commands.** No config change needed:
   `ssh -o ControlMaster=auto -o ControlPath=~/.ssh/cm/%C -o ControlPersist=1h <host> ...`, after
   `mkdir -p -m 700 ~/.ssh/cm`. Put them in a shell array or script variable so every call
   carries the same three. In scripts, use the same `ControlPath` as the user's config, or you
   make a second connection and a second approval.
4. **Making it permanent is the user's call.** `~/.ssh/config` is theirs and the trade-off is
   theirs (below), so ask first, then add a block for the named hosts only, after the `Host *`
   block if there is one:

   ```
   Host build.example.lan 10.0.0.21 nas
       ControlMaster auto
       ControlPath ~/.ssh/cm/%C
       ControlPersist 1h
       ServerAliveInterval 30
       ServerAliveCountMax 4
   ```

   Check it with `ssh -G <host>` before relying on it.
5. **End one early** with `ssh -O exit <host>`, for example after the work is done on a host you
   will not touch again, or to force a fresh login.

## Gotchas

- Parallel first connections race. Several `ssh` calls started at once to a host with no open
  connection each authenticate, and the user gets one prompt per call. Open it first (step 2),
  then fan out.
- The trade-off: while a shared connection is open, any process running as the user can open new
  sessions to that host through its socket without asking the agent. Keep the lifetime modest
  (an hour) and the block limited to named hosts. Never put `ControlMaster` under `Host *`.
- The match is on the host as typed. `Host linkmini.home.arpa` does not cover the alias `mini`
  or a bare IP; list every spelling the user and the scripts use, and confirm each with `ssh -G`.
- `%C` hashes local host, remote host, port and user, so the same machine on two ports (a WSL
  sshd on 2222 beside Windows OpenSSH on 22) gets two connections. That is correct.
- Sockets must live on a short path: macOS caps a socket path near 104 characters. `~/.ssh/cm/%C`
  fits; `$TMPDIR` often does not.
- A remote that sleeps, reboots or changes network drops the connection; the next command signs
  again (one prompt). A dead socket shows as `Control socket connect(...): Connection refused`:
  `ssh -O exit <host>` or delete that socket file, then retry.
- Commit signing through the agent (for example 1Password's `op-ssh-sign`) is not an SSH
  connection and is not covered: every signed commit still asks the agent.
- `communication with agent failed`, `failed to fill whole buffer`, or an ssh that hangs right
  after "Server accepts key" usually means the agent is locked or waiting for an approval click.
  Tell the user and wait; do not retry in a loop or switch to password authentication.
- A command-line `-o` beats the config file. To test a fresh login while a connection is open,
  use `-o ControlMaster=no -o ControlPath=none`.

## Hand-offs

- For the 1Password CLI itself (`op inject`, vault references), use the `1password-cli` skill.
