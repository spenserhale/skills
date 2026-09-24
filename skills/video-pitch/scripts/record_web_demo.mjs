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
//      {"scroll": {"to": "#pricing", "block": "center"}},  element to center (use under sticky headers)
//      {"wait_for": "text=Live"},                        wait for selector, default 15 s timeout
//      {"goto": "https://..."},
//      {"eval": "document.querySelector('.banner')?.remove()"},
//      {"screenshot": "work/step.png"}
//    ]}
// Writes WORKDIR/demo.webm and WORKDIR/marks.json, a flat object of seconds from the recording start:
//   {"ready": 0.9, "demo-entry": 1.4, "demo-action": 4.2, "end": 11.4}
// "ready" (first page settled) and "end" are added automatically; the rest come from your "mark"
// steps. assemble.py cuts with {"mark": name}. URLs may be http(s) or file:// for a static site.
//
// Needs playwright-core (no browser download) and a Chromium-based browser; see pw_resolve.mjs.
// Install if missing: npm i -g playwright-core

import { existsSync, readFileSync, writeFileSync, mkdirSync, renameSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { loadPlaywright, launchChrome } from "./pw_resolve.mjs";

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

const spec = JSON.parse(readFileSync(stepsPath, "utf8"));
const { chromium } = loadPlaywright();
const viewport = spec.viewport ?? { width: 1600, height: 900 };
mkdirSync(outDir, { recursive: true });
const videoDir = join(outDir, "video-tmp");
mkdirSync(videoDir, { recursive: true });

// Headless Chrome opens a 800x600 window by default and the screencast letterboxes the page in
// grey when the viewport is larger than the window, so size the window to the viewport.
const launchOpts = { headless: !headed, slowMo: spec.slow_mo ?? 0, args: [`--window-size=${viewport.width},${viewport.height}`] };
const browser = await launchChrome(chromium, launchOpts);
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
        else if (v.to) await page.locator(v.to).first().evaluate((el, block) => el.scrollIntoView({ behavior: "smooth", block }), v.block ?? "center");
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
