#!/usr/bin/env node
// Render an HTML scene frame-exactly to MP4 under a virtual clock, or check it at timestamps.
//
// usage: node render_scene.mjs SCENE.html --duration SECONDS --out scene.mp4
//            [--fps 30] [--format landscape|vertical|square | --width W --height H] [--quality 92]
//        node render_scene.mjs SCENE.html --check 0,1.5,4 [--duration SECONDS] [--width W --height H]
//
// The page's clocks (requestAnimationFrame, setTimeout/setInterval, Date, performance.now, CSS and
// Web Animations) are replaced with a virtual clock that only advances when a frame is requested,
// so every frame is a deterministic seek and a render is reproducible. Write the scene so that what
// is on screen is a pure function of time: CSS @keyframes with animation-delay and
// animation-fill-mode: both, or one requestAnimationFrame loop driven by its t argument. No CSS
// transitions, no Math.random, no <video>/<audio>/<iframe>, no reads of wall-clock time.
// The render length is exposed as window.__SCENE_DURATION so a scene can hold its last beat and size
// its progress bar to the beat it is cut into. A starter with beat helpers and an editorial frame:
// assets/scene.template.html.
//
// --check seeks to the given seconds and prints JS errors, failed requests, and the visible text at
// each timestamp (leftover words from an earlier beat, or an empty beat, show up here). Cheap; run it
// before rendering.
//
// Needs playwright-core (see pw_resolve.mjs), a Chromium-based browser, and ffmpeg on PATH.

import { spawn } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { pathToFileURL } from "node:url";
import { loadPlaywright, launchChrome } from "./pw_resolve.mjs";

const FORMATS = { landscape: [1920, 1080], vertical: [1080, 1920], square: [1080, 1080] };
const args = process.argv.slice(2);
const flag = (name) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : undefined; };
if (args.includes("--help") || args.includes("-h") || !args.length) {
  const src = readFileSync(new URL(import.meta.url), "utf8");
  console.log(src.split("\n").filter((l) => l.startsWith("//")).map((l) => l.replace(/^\/\/ ?/, "")).join("\n"));
  process.exit(0);
}
const scenePath = args.find((a) => !a.startsWith("--") && /\.html?$/i.test(a));
if (!scenePath) { console.error("render_scene: SCENE.html is required"); process.exit(2); }
const check = flag("--check");
const out = flag("--out");
const duration = Number(flag("--duration") ?? (check ? 30 : NaN));
if (!check && (!out || !(duration > 0))) { console.error("render_scene: --duration and --out are required to render"); process.exit(2); }
const fps = Number(flag("--fps") ?? 30);
let [width, height] = FORMATS[flag("--format") ?? "landscape"] ?? FORMATS.landscape;
if (flag("--width") && flag("--height")) { width = Number(flag("--width")); height = Number(flag("--height")); }
const quality = Number(flag("--quality") ?? 92);

// Injected before any page script. Adapted from diggerhq/shipvideo (MIT).
const VIRTUAL_CLOCK = `(() => {
  const EPOCH = Date.now(); let now = 0; let rafs = new Map(); let rafId = 0; const timers = new Map(); let timerId = 0;
  const RealDate = Date;
  performance.now = () => now;
  const FakeDate = function (...a) { return a.length ? new RealDate(...a) : new RealDate(EPOCH + now); };
  FakeDate.now = () => EPOCH + now; FakeDate.UTC = RealDate.UTC; FakeDate.parse = RealDate.parse; FakeDate.prototype = RealDate.prototype;
  window.Date = FakeDate;
  window.requestAnimationFrame = (cb) => { rafs.set(++rafId, cb); return rafId; };
  window.cancelAnimationFrame = (id) => { rafs.delete(id); };
  window.setTimeout = (cb, ms = 0, ...a) => { const id = ++timerId; timers.set(id, { at: now + Math.max(0, +ms || 0), cb, a, every: null }); return id; };
  window.setInterval = (cb, ms = 0, ...a) => { const id = ++timerId; const every = Math.max(1, +ms || 1); timers.set(id, { at: now + every, cb, a, every }); return id; };
  window.clearTimeout = window.clearInterval = (id) => { timers.delete(id); };
  const seen = new WeakMap(); const step = 1000 / 60;
  window.__seek = (t) => {
    while (now < t - 1e-6) {
      now = Math.min(t, now + step);
      for (;;) {
        let next = null;
        for (const [id, tm] of timers) if (tm.at <= now + 1e-6 && (!next || tm.at < next[1].at)) next = [id, tm];
        if (!next) break;
        const [id, tm] = next;
        if (tm.every) tm.at += tm.every; else timers.delete(id);
        try { typeof tm.cb === "function" ? tm.cb(...tm.a) : (0, eval)(String(tm.cb)); } catch (e) { console.error("timer threw: " + (e && e.message)); }
      }
      const cbs = [...rafs.values()]; rafs = new Map();
      for (const cb of cbs) { try { cb(now); } catch (e) { console.error("rAF threw: " + (e && e.message)); } }
    }
    for (const a of document.getAnimations({ subtree: true })) {
      try { let s = seen.get(a); if (s === undefined) { s = now; seen.set(a, s); } a.pause(); a.currentTime = Math.max(0, now - s); } catch (e) {}
    }
    return now;
  };
})();`;

const VISIBLE_TEXT = () => {
  const vw = window.innerWidth, vh = window.innerHeight, texts = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = walker.nextNode())) {
    const s = (n.textContent ?? "").replace(/\s+/g, " ").trim();
    if (!s) continue;
    const el = n.parentElement; if (!el) continue;
    let e = el, hidden = false;
    while (e && e !== document.body) {
      const cs = getComputedStyle(e);
      if (cs.display === "none" || cs.visibility === "hidden" || Number(cs.opacity) < 0.05) { hidden = true; break; }
      e = e.parentElement;
    }
    if (hidden) continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0 || r.right < 0 || r.bottom < 0 || r.left > vw || r.top > vh) continue;
    texts.push(s.slice(0, 80));
  }
  return [...new Set(texts)].join(" | ").slice(0, 600);
};

const { chromium } = loadPlaywright();
const browser = await launchChrome(chromium, { headless: true, args: [`--window-size=${width},${height}`, "--font-render-hinting=none", "--force-color-profile=srgb", "--hide-scrollbars"] });
const ctx = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: 1, colorScheme: "light" });
await ctx.addInitScript(VIRTUAL_CLOCK);
await ctx.addInitScript(`window.__SCENE_DURATION = ${Number.isFinite(duration) ? duration : "undefined"};`);
const page = await ctx.newPage();
const errors = [];
page.on("pageerror", (e) => errors.push(`pageerror: ${e.message}`));
page.on("console", (m) => { if (m.type() === "error" || m.type() === "warning") errors.push(`console.${m.type()}: ${m.text()}`); });
page.on("requestfailed", (r) => errors.push(`request failed: ${r.url()} ${r.failure()?.errorText ?? ""}`));
await page.goto(pathToFileURL(resolve(scenePath)).href, { waitUntil: "load", timeout: 30000 });
await page.evaluate(() => document.fonts.ready);
await page.waitForLoadState("networkidle", { timeout: 10000 }).catch(() => {});
await page.evaluate(() => window.__seek(0));

if (check) {
  const stamps = check.split(",").map(Number).filter((t) => t >= 0);
  for (const t of stamps) {
    await page.evaluate((ms) => window.__seek(ms), t * 1000);
    const text = await page.evaluate(VISIBLE_TEXT);
    const bg = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
    console.log(`t=${t.toFixed(2).padStart(6)}s  bg ${bg}  | ${text || "(no visible text)"}`);
  }
  if (errors.length) { console.log("errors:"); for (const e of errors.slice(0, 20)) console.log("  " + e); }
  await browser.close();
  process.exit(errors.length ? 1 : 0);
}

const total = Math.round(duration * fps);
const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(fps), "-i", "-",
  "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]);
let ffErr = "";
ff.stderr.on("data", (d) => { ffErr += String(d); });
const closed = new Promise((r) => ff.on("close", (code) => r(code ?? 1)));
const started = Date.now();
try {
  for (let i = 0; i < total; i++) {
    await page.evaluate((ms) => window.__seek(ms), (i * 1000) / fps);
    const frame = await page.screenshot({ type: "jpeg", quality });
    if (!ff.stdin.write(frame)) await new Promise((r) => ff.stdin.once("drain", r));
    if (i && i % (fps * 5) === 0) process.stderr.write(`  ${i}/${total} frames\n`);
  }
} finally {
  ff.stdin.end();
}
const code = await closed;
await browser.close();
if (code !== 0) { console.error(`render_scene: ffmpeg exited ${code}: ${ffErr.slice(-1200)}`); process.exit(1); }
console.log(`wrote ${out} (${width}x${height}, ${duration}s, ${total} frames in ${((Date.now() - started) / 1000).toFixed(1)}s)`);
if (errors.length) { console.log(`page reported ${errors.length} error(s); first: ${errors[0]}`); }
