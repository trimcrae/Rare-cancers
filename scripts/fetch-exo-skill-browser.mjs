#!/usr/bin/env node
// Headless-browser retrieval of the official OpenExO "building-an-exo" Claude Skill.
// The Resource Hub is a client-rendered SPA, so the .skill download URL only exists
// after JS runs. This renders the page with Playwright/Chromium on a CI runner
// (open internet), captures ALL network traffic, follows the "Download" affordance,
// and saves any .skill / zip / attachment response. It also detects a login wall so
// we can definitively distinguish "public-but-JS-injected" from "account-gated".
//
// Output: out/building-an-exo.skill on success; out/page-dump.html + out/network.log
// always, for diagnosis.

import { chromium } from 'playwright';
import { writeFileSync, mkdirSync, appendFileSync, readFileSync } from 'node:fs';
import { execSync } from 'node:child_process';

const PAGES = [
  'https://openexo.com/resource-hub/exo-30-claude-skill',
  'https://openexo.com/resource-hub/organizational-singularity-book-app',
  'https://openexo.com/claude-skill-how-to-guide',
];

mkdirSync('out', { recursive: true });
const netlog = 'out/network.log';
writeFileSync(netlog, '');

const isBinaryTarget = (url, ct, cd) => {
  const u = url.toLowerCase();
  return (
    u.includes('.skill') ||
    u.endsWith('.zip') ||
    /application\/(zip|octet-stream)/i.test(ct || '') ||
    /attachment/i.test(cd || '')
  );
};

const looksLikeZip = (buf) =>
  buf && buf.length > 4 && buf[0] === 0x50 && buf[1] === 0x4b;

let saved = false;
let sawLoginWall = false;

const browser = await chromium.launch({ args: ['--no-sandbox'] });
const ctx = await browser.newContext({ acceptDownloads: true });
const page = await ctx.newPage();

// Capture every response; save the first that smells like the skill archive.
page.on('response', async (res) => {
  try {
    const url = res.url();
    const h = res.headers();
    const ct = h['content-type'] || '';
    const cd = h['content-disposition'] || '';
    appendFileSync(netlog, `${res.status()} ${ct} ${cd} ${url}\n`);
    if (!saved && isBinaryTarget(url, ct, cd)) {
      const buf = await res.body();
      if (looksLikeZip(buf) || url.toLowerCase().includes('.skill')) {
        writeFileSync('out/building-an-exo.skill', buf);
        console.log(`SAVED from response: ${url} (${buf.length} bytes)`);
        saved = true;
      }
    }
  } catch {
    /* body may be unavailable for some responses */
  }
});

// Also catch actual browser downloads (Download Resource button → file).
ctx.on('page', () => {});
page.on('download', async (dl) => {
  try {
    const p = 'out/building-an-exo.skill';
    await dl.saveAs(p);
    console.log(`SAVED from download event: ${dl.suggestedFilename()}`);
    saved = true;
  } catch (e) {
    console.log(`download event error: ${e.message}`);
  }
});

for (const url of PAGES) {
  if (saved) break;
  console.log(`\n=== Rendering ${url} ===`);
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
  } catch (e) {
    console.log(`goto error: ${e.message}`);
    continue;
  }
  await page.waitForTimeout(3500);

  const finalUrl = page.url();
  const title = await page.title().catch(() => '');
  console.log(`  final URL: ${finalUrl}`);
  console.log(`  title: ${title}`);
  if (/log ?in|sign ?in|auth|account\/login/i.test(finalUrl + ' ' + title)) {
    sawLoginWall = true;
    console.log('  -> looks like a login wall');
  }

  // Dump rendered HTML for diagnosis.
  try {
    const html = await page.content();
    writeFileSync('out/page-dump.html', html);
  } catch {}

  // Find and click any download affordance.
  const clickSelectors = [
    'a:has-text("Download")',
    'button:has-text("Download")',
    'a:has-text("Access Content")',
    'button:has-text("Access Content")',
    'a[href$=".skill"]',
    'a[download]',
  ];
  for (const sel of clickSelectors) {
    if (saved) break;
    const loc = page.locator(sel);
    const n = await loc.count().catch(() => 0);
    for (let i = 0; i < n && !saved; i++) {
      const label = (await loc.nth(i).innerText().catch(() => '')).trim();
      console.log(`  clicking [${sel}] #${i} "${label.slice(0, 40)}"`);
      try {
        await loc.nth(i).click({ timeout: 8000 });
        await page.waitForTimeout(4000);
      } catch (e) {
        console.log(`    click error: ${e.message}`);
      }
      // A click may open a detail page with its own Download button; try those too.
      const dl2 = page.locator('a:has-text("Download"), button:has-text("Download"), a[href$=".skill"]');
      const n2 = await dl2.count().catch(() => 0);
      for (let j = 0; j < n2 && !saved; j++) {
        try {
          await dl2.nth(j).click({ timeout: 8000 });
          await page.waitForTimeout(4000);
        } catch {}
      }
    }
  }
}

await browser.close();

if (saved) {
  console.log('\nDownload succeeded.');
  try {
    if (looksLikeZip(readFileSync('out/building-an-exo.skill'))) {
      mkdirSync('out/extracted', { recursive: true });
      execSync('unzip -o out/building-an-exo.skill -d out/extracted', { stdio: 'inherit' });
      execSync('find out/extracted -maxdepth 3 -type f | sort', { stdio: 'inherit' });
    }
  } catch (e) {
    console.log(`post-process note: ${e.message}`);
  }
} else {
  console.log(
    `\nNO .skill CAPTURED. loginWallSeen=${sawLoginWall}. ` +
      'See out/network.log + out/page-dump.html (uploaded as artifact) for the ' +
      'exact endpoints. If gated, the official download needs an OpenExO account.'
  );
}
