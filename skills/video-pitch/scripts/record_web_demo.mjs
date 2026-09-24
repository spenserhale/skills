#!/usr/bin/env node
// Record a scripted browser walkthrough to WebM with a visible cursor and timing marks.
//
// usage: node record_web_demo.mjs STEPS.json --out WORKDIR [--headed]
//
// STEPS.json shape:
//   {"url": "http://localhost:3000/", "viewport": {"width": 1600, "height": 900}, "zoom": 1,
//    "storage_state": "work/auth.json", "wait_until": "networkidle", "slow_mo": 0,
//    "steps": [
//      {"wait": 800},                                    ms
//      {"mark": "flow-start"},                           named timestamp, written to marks.json
//      {"hover": "text=Launch domain"},                  any Playwright selector
//      {"click": "#submit"},
//      {"fill": ["input[name=domain]", "example.com"]},
//      {"type": ["input[name=domain]", "example.com", 60]},   per-char delay ms, looks human
//      {"press": "Enter"},
//      {"scroll": "#pricing"} | {"scroll": {"y": 600}},  smooth scroll: element to top of viewport, or by y pixels (relative)
//      {"wait_for": "text=Live"},                        wait for selector, default 15 s timeout
//      {"goto": "https://..."},
//      {"eval": "document.querySelector('.banner')?.remove()"},
//      {"screenshot": "work/step.png"}
//    ]}
// Writes WORKDIR/demo.webm and WORKDIR/marks.json ({"ready": s, "<mark>": s, "end": s}) with times
// relative to the recording start, so assemble.py can cut with "in"/"out". "ready" is when the first
// page had fonts and network settled; trim to it to drop the blank lead-in.
//
// Needs playwright-core (no browser download) and a Chromium-based browser. Resolution order:
// $PLAYWRIGHT_CORE_PATH, require.resolve from cwd, global npm root, the playwright-cli install.
// Install if missing: npm i -g playwright-core

import { createRequire } from "node:module";
import { execSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync, mkdirSync, renameSync, readdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { realpathSync } from "node:fs";

const args = process.argv.slice(2);
if (args.includes("--help") || args.includes("-h")) {
  const src = readFileSync(new URL(import.meta.url), "utf8");
  console.log(src.split("\n").filter((l) => l.startsWith("//")).map((l) => l.replace(/^\/\/ ?/, "")).join("\n"));
  process.exit(0);
}
const flag = (name) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : undefined; };
const stepsPath = args.find((a) => !a.startsWith("--") && a.endsWith(".json"));
const outDir = flag("--out");
const headed = args.includes("--headed");
if (!stepsPath || !outDir) {
  console.error("usage: record_web_demo.mjs STEPS.json --out WORKDIR [--headed]");
  process.exit(2);
}

function loadPlaywright() {
  const req = createRequire(import.meta.url);
  const candidates = [];
  if (process.env.PLAYWRIGHT_CORE_PATH) candidates.push(process.env.PLAYWRIGHT_CORE_PATH);
  candidates.push("playwright-core", "playwright");
  const tryRoot = (cmd) => { try { return execSync(cmd, { stdio: ["ignore", "pipe", "ignore"] }).toString().trim(); } catch { return ""; } };
  const globalRoot = tryRoot("npm root -g");
  if (globalRoot) candidates.push(join(globalRoot, "playwright-core"), join(globalRoot, "playwright"));
  const cliBin = tryRoot(process.platform === "win32" ? "where playwright-cli" : "command -v playwright-cli");
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
  console.error("record_web_demo: playwright-core not found. Run: npm i -g playwright-core  (uses the installed Chrome, no browser download)");
  process.exit(1);
}

const spec = JSON.parse(readFileSync(stepsPath, "utf8"));
const { chromium } = loadPlaywright();
const viewport = spec.viewport ?? { width: 1600, height: 900 };
mkdirSync(outDir, { recursive: true });
const videoDir = join(outDir, "video-tmp");
mkdirSync(videoDir, { recursive: true });

// Headless Chrome opens a 800x600 window by default and the screencast letterboxes the page in
// grey when the viewport is larger than the window, so size the window to the viewport.
const launchOpts = { headless: !headed, slowMo: spec.slow_mo ?? 0, args: [`--window-size=${viewport.width},${viewport.height}`] };
let browser;
try {
  browser = await chromium.launch({ ...launchOpts, channel: spec.channel ?? "chrome" });
} catch (e) {
  try { browser = await chromium.launch(launchOpts); }
  catch { console.error(`record_web_demo: could not launch a browser: ${e.message}`); process.exit(1); }
}
const ctx = await browser.newContext({
  viewport,
  deviceScaleFactor: spec.device_scale_factor ?? 1,
  colorScheme: spec.color_scheme ?? "light",
  recordVideo: { dir: videoDir, size: viewport },
  ...(spec.storage_state && existsSync(spec.storage_state) ? { storageState: spec.storage_state } : {}),
});
const page = await ctx.newPage();
const t0 = Date.now();
const now = () => (Date.now() - t0) / 1000;
const marks = {};
const waitUntil = spec.wait_until ?? "networkidle";

async function settle() {
  await page.evaluate(() => document.fonts?.ready).catch(() => {});
  if (spec.zoom && spec.zoom !== 1) await page.evaluate((z) => { document.documentElement.style.zoom = String(z); }, spec.zoom);
  if (spec.cursor !== false) await installCursor();
}

async function installCursor() {
  await page.evaluate(() => {
    if (document.getElementById("__vp_cursor")) return;
    const c = document.createElement("div");
    c.id = "__vp_cursor";
    c.style.cssText = "position:fixed;z-index:2147483647;width:22px;height:22px;border-radius:50%;background:rgba(30,60,120,.85);border:2.5px solid #fff;box-shadow:0 2px 10px rgba(0,0,0,.4);pointer-events:none;left:-60px;top:-60px;transition:left .3s ease,top .3s ease,transform .12s ease";
    document.documentElement.appendChild(c);
    window.addEventListener("mousemove", (e) => { c.style.left = e.clientX - 11 + "px"; c.style.top = e.clientY - 11 + "px"; }, true);
    window.addEventListener("mousedown", () => { c.style.transform = "scale(.7)"; }, true);
    window.addEventListener("mouseup", () => { c.style.transform = "scale(1)"; }, true);
  });
}

async function glideTo(selector) {
  const loc = page.locator(selector).first();
  await loc.scrollIntoViewIfNeeded();
  const box = await loc.boundingBox();
  if (!box) throw new Error(`no bounding box for ${selector}`);
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 18 });
  await page.waitForTimeout(250);
}

if (spec.url) {
  await page.goto(spec.url, { waitUntil });
  await settle();
}
marks.ready = +now().toFixed(3);

try {
  for (const step of spec.steps ?? []) {
    const [key] = Object.keys(step);
    const v = step[key];
    switch (key) {
      case "wait": await page.waitForTimeout(v); break;
      case "mark": marks[v] = +now().toFixed(3); break;
      case "goto": await page.goto(v, { waitUntil }); await settle(); break;
      case "hover": await glideTo(v); break;
      case "click": await glideTo(v); await page.locator(v).first().click(); await page.waitForTimeout(150); await installCursor(); break;
      case "fill": await glideTo(v[0]); await page.locator(v[0]).first().fill(v[1]); break;
      case "type": await glideTo(v[0]); await page.locator(v[0]).first().click(); await page.keyboard.type(v[1], { delay: v[2] ?? 60 }); break;
      case "press": await page.keyboard.press(v); break;
      case "scroll":
        if (typeof v === "string") await page.locator(v).first().evaluate((el) => el.scrollIntoView({ behavior: "smooth", block: "start" }));
        else await page.evaluate(({ y }) => window.scrollBy({ top: y, behavior: "smooth" }), v);
        await page.waitForTimeout(700);
        break;
      case "wait_for": await page.locator(v).first().waitFor({ timeout: step.timeout ?? 15000 }); break;
      case "eval": await page.evaluate(v); break;
      case "screenshot": await page.screenshot({ path: v }); break;
      default: throw new Error(`unknown step: ${JSON.stringify(step)}`);
    }
  }
} catch (e) {
  console.error(`record_web_demo: step failed at ${now().toFixed(1)}s: ${e.message}`);
  marks.error = +now().toFixed(3);
}
marks.end = +now().toFixed(3);

await ctx.close();
await browser.close();
const files = readdirSync(videoDir).filter((f) => f.endsWith(".webm"));
if (!files.length) { console.error("record_web_demo: no video written"); process.exit(1); }
const dest = join(outDir, "demo.webm");
renameSync(join(videoDir, files[0]), dest);
writeFileSync(join(outDir, "marks.json"), JSON.stringify(marks, null, 2));
console.log(`wrote ${dest} (${viewport.width}x${viewport.height}, ${marks.end.toFixed(1)}s) and marks.json`);
for (const [k, t] of Object.entries(marks)) console.log(`  ${k.padEnd(14)} ${t.toFixed(2)}s`);
if (marks.error !== undefined) process.exit(1);
