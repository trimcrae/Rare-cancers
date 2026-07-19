#!/usr/bin/env node
// Headless-browser DISCOVERY + retrieval of the official OpenExO "building-an-exo"
// Claude Skill. The Resource Hub is a client-rendered SPA. This renders each
// candidate page, prints every anchor (href+text), every button label, and any
// string matching *.skill found in the rendered DOM or in captured network
// traffic — all to stdout so it's readable straight from the CI job log (no
// artifact download needed). When a .skill URL is discovered it is fetched
// directly and saved to out/building-an-exo.skill (+ extracted).

import { chromium } from 'playwright';
import { writeFileSync, mkdirSync, appendFileSync } from 'node:fs';
import { execSync } from 'node:child_process';

const PAGES = [
  'https://openexo.com/resource-hub/exo-30-claude-skill',
  'https://openexo.com/claude-skill-how-to-guide',
  'https://openexo.com/resource-hub/organizational-singularity-book-app',
];

mkdirSync('out', { recursive: true });
const netUrls = new Set();
const skillUrls = new Set();

const addIfSkill = (u) => {
  if (!u) return;
  if (/\.skill(\?|#|$)/i.test(u) || /building-an-exo[^"'\s]*\.skill/i.test(u)) {
    skillUrls.add(u.split('#')[0]);
  }
};

const browser = await chromium.launch({ args: ['--no-sandbox'] });
const ctx = await browser.newContext({ acceptDownloads: true });
const page = await ctx.newPage();

page.on('response', (res) => {
  const u = res.url();
  netUrls.add(u);
  addIfSkill(u);
  const cd = res.headers()['content-disposition'] || '';
  if (/\.skill/i.test(cd)) skillUrls.add(u);
});
page.on('download', async (dl) => {
  try {
    await dl.saveAs('out/building-an-exo.skill');
    console.log(`DOWNLOAD EVENT saved: ${dl.suggestedFilename()} <- ${dl.url()}`);
    addIfSkill(dl.url());
  } catch (e) {
    console.log(`download event error: ${e.message}`);
  }
});

for (const url of PAGES) {
  console.log(`\n======== ${url} ========`);
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
  } catch (e) {
    console.log(`goto error: ${e.message}`);
    continue;
  }
  await page.waitForTimeout(4000);
  console.log(`final: ${page.url()} | title: ${await page.title().catch(() => '')}`);

  // Every anchor href+text.
  const anchors = await page
    .$$eval('a', (els) =>
      els.map((a) => ({ href: a.href, text: (a.innerText || '').trim().slice(0, 60) }))
    )
    .catch(() => []);
  console.log(`  ${anchors.length} anchors:`);
  for (const a of anchors) {
    if (!a.href) continue;
    addIfSkill(a.href);
    if (
      /\.skill|download|resource|s3|exosquare|amazonaws|drive|dropbox/i.test(
        a.href + ' ' + a.text
      )
    ) {
      console.log(`    A "${a.text}" -> ${a.href}`);
    }
  }
  // Every button label.
  const buttons = await page
    .$$eval('button', (els) => els.map((b) => (b.innerText || '').trim().slice(0, 60)))
    .catch(() => []);
  console.log(`  buttons: ${JSON.stringify(buttons.filter(Boolean))}`);

  // Any *.skill in the raw rendered HTML.
  const html = await page.content().catch(() => '');
  const m = html.match(/https?:\/\/[^"'\s<>]+\.skill[^"'\s<>]*/gi) || [];
  m.forEach(addIfSkill);
  if (m.length) console.log(`  .skill in HTML: ${JSON.stringify([...new Set(m)])}`);

  // Try the REAL download affordance: "Download Resource" / "Access Content".
  for (const sel of [
    'a:has-text("Download Resource")',
    'button:has-text("Download Resource")',
    'a:has-text("Access Content")',
    'button:has-text("Access Content")',
    'a[href*=".skill"]',
  ]) {
    const loc = page.locator(sel);
    const n = await loc.count().catch(() => 0);
    for (let i = 0; i < n; i++) {
      const label = (await loc.nth(i).innerText().catch(() => '')).trim().slice(0, 40);
      const href = await loc.nth(i).getAttribute('href').catch(() => null);
      console.log(`  affordance [${sel}] #${i} "${label}" href=${href}`);
      addIfSkill(href);
      try {
        await Promise.race([
          loc.nth(i).click({ timeout: 6000 }),
          page.waitForTimeout(6000),
        ]);
        await page.waitForTimeout(3000);
        const h2 = await page.content().catch(() => '');
        (h2.match(/https?:\/\/[^"'\s<>]+\.skill[^"'\s<>]*/gi) || []).forEach(addIfSkill);
      } catch (e) {
        console.log(`    click note: ${e.message?.slice(0, 60)}`);
      }
    }
  }
}

await browser.close();

console.log(`\n==== DISCOVERY SUMMARY ====`);
console.log(`.skill URLs found: ${JSON.stringify([...skillUrls])}`);
const s3ish = [...netUrls].filter((u) => /exosquare|amazonaws|\.zip/i.test(u) && !/\.(png|jpe?g|webp|svg|css|js|woff2?)/i.test(u));
console.log(`non-image S3/zip network URLs: ${JSON.stringify(s3ish.slice(0, 40))}`);

// Direct-fetch the first discovered .skill URL.
let saved = false;
for (const u of skillUrls) {
  try {
    const r = await fetch(u, { redirect: 'follow' });
    console.log(`FETCH ${u} -> ${r.status} ${r.headers.get('content-type')}`);
    if (r.ok) {
      const buf = Buffer.from(await r.arrayBuffer());
      writeFileSync('out/building-an-exo.skill', buf);
      console.log(`SAVED ${buf.length} bytes from ${u}`);
      saved = true;
      break;
    }
  } catch (e) {
    console.log(`fetch error ${u}: ${e.message}`);
  }
}

if (saved || skillUrls.size) {
  try {
    const buf = execSync('head -c 4 out/building-an-exo.skill | xxd -p').toString().trim();
    if (buf.startsWith('504b')) {
      mkdirSync('out/extracted', { recursive: true });
      execSync('unzip -o out/building-an-exo.skill -d out/extracted', { stdio: 'inherit' });
      execSync('find out/extracted -maxdepth 3 -type f | sort', { stdio: 'inherit' });
    }
  } catch {}
}
if (!saved) {
  console.log('\nNo .skill saved yet — inspect the discovery summary above for the real URL.');
}
