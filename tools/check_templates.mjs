#!/usr/bin/env node
// Screenshots every template and checks the dash safe area.
//
//   node tools/check_templates.mjs            check + screenshots into media/raw/
//   node tools/check_templates.mjs --record   also records media/raw/*.webm from tools/demo/demo.html
//                                             (needs the author's assets in media/raw/demo/)
//   node tools/check_templates.mjs --dir ../my-dash-app/design   checks your own copy (dash/ and phone/ inside it)
//
// Dash pages (templates/dash/*.html) render at 480×234 and 480×240 (?h=). Every element marked
// data-keep (text, glyphs, signs, notices) must stay inside the frame and off the dash's own chrome.
// Phone pages (templates/phone/*.html) render at 390×844 and must not scroll sideways.
import { chromium } from "playwright";
import { existsSync, mkdirSync, readdirSync } from "node:fs";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const out = join(root, "media", "raw");
const args = process.argv.slice(2);
const dirAt = args.indexOf("--dir");
const templates = dirAt >= 0 ? resolve(args[dirAt + 1]) : join(root, "templates");
const only = args.filter((a, i) => !a.startsWith("--") && (dirAt < 0 || i !== dirAt + 1));

// Chrome the dash draws over the frame (docs/how-it-works/dash-canvas.md). [x, y, w, h]
const chrome = (h) => ({
  "zoom buttons": [0, 68, 56, 100],
  "road bar": [0, 186, 480, h - 186],
});
const sign = [411, 135, 62, 62];

const overlaps = (a, b) => a[0] < b[0] + b[2] && b[0] < a[0] + a[2] && a[1] < b[1] + b[3] && b[1] < a[1] + a[3];

function pages(folder) {
  const dir = join(templates, folder);
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((f) => f.endsWith(".html"))
    .filter((f) => !only.length || only.some((o) => join(dir, f).endsWith(o)))
    .map((f) => join(dir, f));
}

async function checkDash(browser, file, h, problems) {
  const page = await browser.newPage({ viewport: { width: 480, height: h } });
  await page.goto(`${pathToFileURL(file)}?h=${h}`);
  await page.evaluate(() => document.fonts.ready);
  const boxes = await page.$$eval("[data-keep]", (els) =>
    els.map((e) => {
      const r = e.getBoundingClientRect();
      return { name: e.dataset.keep || e.textContent.trim().slice(0, 24), box: [r.x, r.y, r.width, r.height] };
    }),
  );
  // A page that relies on the dash's own speed sign marks itself with data-native-sign.
  const usesSign = (await page.$("[data-native-sign]")) !== null;
  const name = basename(file, ".html");
  for (const { name: what, box } of boxes) {
    if (box[0] < 0 || box[1] < 0 || box[0] + box[2] > 480 || box[1] + box[3] > h) {
      problems.push(`${name} @480×${h}: "${what}" leaves the frame ${box.map(Math.round)}`);
    }
    for (const [zone, rect] of Object.entries(chrome(h))) {
      if (overlaps(box, rect)) problems.push(`${name} @480×${h}: "${what}" overlaps the ${zone} ${box.map(Math.round)}`);
    }
    if (usesSign && overlaps(box, sign)) {
      problems.push(`${name} @480×${h}: "${what}" overlaps the dash's speed sign`);
    }
  }
  await page.screenshot({ path: join(out, `dash-${name}-${h}.png`) });
  await page.close();
}

async function checkPhone(browser, file, problems) {
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  await page.goto(pathToFileURL(file).href);
  await page.evaluate(() => document.fonts.ready);
  const wide = await page.evaluate(() => document.documentElement.scrollWidth);
  const name = basename(file, ".html");
  if (wide > 390) problems.push(`${name}: page is ${wide}px wide at 390px (scrolls sideways)`);
  await page.screenshot({ path: join(out, `phone-${name}.png`) });
  await page.close();
}

async function record(browser) {
  if (!existsSync(join(root, "media", "raw", "demo"))) {
    console.log("--record needs media/raw/demo/: the demo's assets come from the author's own app and are not in this repo");
    process.exit(1);
  }
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 720 }, recordVideo: { dir: out, size: { width: 1280, height: 720 } } });
  const page = await ctx.newPage();
  await page.goto(pathToFileURL(join(root, "tools", "demo", "demo.html")).href);
  await page.waitForFunction(() => window.demoDone === true, null, { timeout: 120_000 });
  const video = page.video();
  await ctx.close();
  console.log(`video: ${await video.path()}`);
}

mkdirSync(out, { recursive: true });
// Playwright's own Chromium if installed (npx playwright install chromium), else system Chrome, else Edge.
const browser = await chromium
  .launch()
  .catch(() => chromium.launch({ channel: "chrome" }))
  .catch(() => chromium.launch({ channel: "msedge" }));
const problems = [];
for (const f of pages("dash")) for (const h of [234, 240]) await checkDash(browser, f, h, problems);
for (const f of pages("phone")) await checkPhone(browser, f, problems);
if (args.includes("--record")) await record(browser);
await browser.close();

for (const p of problems) console.log(p);
console.log(problems.length ? `${problems.length} problem(s)` : `ok, screenshots in ${out}`);
process.exit(problems.length ? 1 : 0);
