// Shared: find playwright-core without a browser download and launch the system Chrome.
// Resolution order: $PLAYWRIGHT_CORE_PATH, require.resolve from cwd, global npm root, the
// playwright-cli install. Install if missing: npm i -g playwright-core
import { createRequire } from "node:module";
import { execSync } from "node:child_process";
import { existsSync, realpathSync } from "node:fs";
import { dirname, join } from "node:path";

export function loadPlaywright() {
  const req = createRequire(import.meta.url);
  const candidates = [];
  if (process.env.PLAYWRIGHT_CORE_PATH) candidates.push(process.env.PLAYWRIGHT_CORE_PATH);
  candidates.push("playwright-core", "playwright");
  const tryRun = (cmd) => { try { return execSync(cmd, { stdio: ["ignore", "pipe", "ignore"] }).toString().trim(); } catch { return ""; } };
  const globalRoot = tryRun("npm root -g");
  if (globalRoot) candidates.push(join(globalRoot, "playwright-core"), join(globalRoot, "playwright"));
  const cliBin = tryRun(process.platform === "win32" ? "where playwright-cli" : "command -v playwright-cli");
  if (cliBin) {
    try {
      let dir = dirname(realpathSync(cliBin.split("\n")[0]));
      for (let i = 0; i < 6; i++) {
        const hit = join(dir, "node_modules", "playwright-core");
        if (existsSync(hit)) { candidates.push(hit); break; }
        dir = dirname(dir);
      }
    } catch { /* ignore */ }
  }
  for (const c of candidates) {
    try { return req(c); } catch { /* next */ }
  }
  console.error("playwright-core not found. Run: npm i -g playwright-core  (uses the installed Chrome, no browser download)");
  process.exit(1);
}

export async function launchChrome(chromium, opts = {}) {
  try {
    return await chromium.launch({ channel: "chrome", ...opts });
  } catch (e) {
    try { return await chromium.launch(opts); }
    catch { console.error(`could not launch a browser: ${e.message}`); process.exit(1); }
  }
}
