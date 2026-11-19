"""Attach to a signed-in Chrome or Edge profile with a unique Playwright CLI session.

Usage: python -B attach.py --browser chrome --task codex-calendar
Connection approval is interactive unless the caller opts in to a matching profile token.
Prints the session name. Playwright CLI manages session data under its normal paths.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--browser", required=True, choices=("chrome", "edge"))
    parser.add_argument("--task", required=True, help="Short task or agent label")
    parser.add_argument("--profile", help="Profile directory name, such as Default or Profile 1")
    parser.add_argument("--use-profile-token", action="store_true", help="Use the configured token for the selected profile")
    args = parser.parse_args()

    cli = shutil.which("playwright-cli")
    if cli is None:
        parser.error("playwright-cli is required on PATH")

    channel = "msedge" if args.browser == "edge" else "chrome"
    profile = args.profile
    if profile and not re.fullmatch(r"Default|Profile [0-9]+", profile):
        parser.error("--profile must be Default or a numbered Profile directory name")

    label = re.sub(r"[^a-z0-9]+", "-", args.task.lower()).strip("-")
    label = label[:40].rstrip("-") or "task"
    session = f"{args.browser}-{label}-{uuid.uuid4().hex[:12]}"

    env = os.environ.copy()
    if profile:
        env["PLAYWRIGHT_MCP_PROFILE_DIR_NAME"] = profile
    else:
        env.pop("PLAYWRIGHT_MCP_PROFILE_DIR_NAME", None)
    token_key = "PLAYWRIGHT_MCP_EXTENSION_TOKEN"
    if args.use_profile_token:
        if not profile or not env.get(token_key):
            parser.error("--use-profile-token requires --profile and a configured extension token")
    else:
        env.pop(token_key, None)
    token = env.get(token_key)
    if not token:
        print(f"Approve the Playwright connection in {args.browser} ({profile or 'extension-selected profile'}) with no existing tabs selected.", flush=True)

    # The browser daemon outlives attach. Regular files let captured shell commands finish
    # even when Windows descendants retain output handles.
    with tempfile.TemporaryFile() as output:
        result = subprocess.run(
            [cli, f"--session={session}", "attach", f"--extension={channel}"],
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=output,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode:
            output.seek(0)
            detail = output.read().decode("utf-8", errors="replace").strip()
            if token:
                detail = detail.replace(token, "[redacted]")
            print(detail or f"Playwright attach exited with code {result.returncode}.", file=sys.stderr)
            return result.returncode

    print(f"Playwright session: {session}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
