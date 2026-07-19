#!/usr/bin/env node
// Comprehensive browser probe for the official OpenExO "building-an-exo" Claude
// Skill. Discovery so far: downloads flow through
//   https://openexo.com/resource-hub/resources/{id}/access
// (the book-app is id 64). This script (1) renders the ExO 3.0 Claude Skill page
// and dumps ALL anchors + any resources/{id}/access links to find the skill's id,
// (2) navigates directly to each discovered /access endpoint with downloads
// enabled, capturing redirects, new tabs, download events, and any .skill/zip
// response, and (3) saves the file to out/building-an-exo.skill. Everything is
// printed to stdout so it's readable from the CI job log.

import { chromium } from 'playwright';
import { writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { execSync } from 'node:child_process';

const START = 'https://openexo.com/resource-hub/exo-30-claude-skill';
mkdirSync('out', { recursive: true });

const accessUrls = new Set();
const skillUrls = new Set();
const noteSkill = (u) => {
  if (u && /\.skill(\?|#|$)/i.test(u)) skillUrls.add(u.split('#')[0]);
};

const browser = await chromium.launch({ args: ['--no-sandbox'] });
const ctx = await browser.newContext({ acceptDownloads: true });

let saved = false;
const wireResponse = (pg) =>
  pg.on('response', async (res) => {
    const u = res.url();
    noteSkill(u);
    const cd = res.headers()['content-disposition'] || '';
    const ct = res.headers()['content-type'] || '';
    if (/\.skill|attachment/i.test(cd) || /application\/(zip|octet-stream)/i.test(ct)) {
      console.log(`  [resp] ${res.status()} ${ct} ${cd} ${u}`);
      try {
        const buf = await res.body();
        if (buf && (buf[0] === 0x50 || /\.skill/i.test(u + cd))) {
          writeFileSync('out/building-an-exo.skill', buf);
          console.log(`  SAVED ${buf.length} bytes from response ${u}`);
          saved = true;
        }
      } catch {}
    }
  });
const wireDownload = (pg) =>
  pg.on('download', async (dl) => {
    try {
      await dl.saveAs('out/building-an-exo.skill');
      console.log(`  DOWNLOAD EVENT ${dl.suggestedFilename()} <- ${dl.url()}`);
      noteSkill(dl.url());
      saved = true;
    } catch (e) {
      console.log(`  download err: ${e.message}`);
    }
  });

ctx.on('page', (pg) => {
  wireResponse(pg);
  wireDownload(pg);
});

const page = await ctx.newPage();
wireResponse(page);
wireDownload(page);

// 1) Render the skill page, dump ALL anchors, find /resources/{id}/access.
console.log(`======== ${START} ========`);
await page.goto(START, { waitUntil: 'networkidle', timeout: 60000 }).catch((e) => console.log(`goto: ${e.message}`));
await page.waitForTimeout(4500);
console.log(`final: ${page.url()} | title: ${await page.title().catch(() => '')}`);
const anchors = await page
  .$$eval('a', (els) => els.map((a) => ({ href: a.href, text: (a.innerText || '').trim().slice(0, 50) })))
  .catch(() => []);
console.log(`ALL ${anchors.length} anchors:`);
for (const a of anchors) {
  if (a.href) console.log(`  A "${a.text.replace(/\s+/g, ' ')}" -> ${a.href}`);
  const m = (a.href || '').match(/resource-hub\/resources\/\d+\/access/);
  if (m) accessUrls.add(a.href.split('#')[0]);
}
// Also scan rendered HTML for access links + any .skill.
const html = await page.content().catch(() => '');
(html.match(/https?:\/\/[^"'\s<>]*resources\/\d+\/access/gi) || []).forEach((u) => accessUrls.add(u));
(html.match(/https?:\/\/[^"'\s<>]+\.skill[^"'\s<>]*/gi) || []).forEach(noteSkill);
console.log(`access URLs discovered: ${JSON.stringify([...accessUrls])}`);

// If the skill page had no /access link, brute the resource-hub listing for it.
if (accessUrls.size === 0) {
  console.log('No /access link on skill page; scanning resource-hub listing...');
  await page.goto('https://openexo.com/resource-hub', { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
  await page.waitForTimeout(4000);
  const all = await page.$$eval('a', (els) => els.map((a) => a.href)).catch(() => []);
  all.filter((h) => /resources\/\d+\/access/.test(h || '')).forEach((h) => accessUrls.add(h.split('#')[0]));
  console.log(`from listing: ${JSON.stringify([...accessUrls])}`);
}

// 2) Visit each /access endpoint directly and watch for download/redirect.
for (const acc of accessUrls) {
  if (saved) break;
  console.log(`\n---- ACCESS ${acc} ----`);
  try {
    const resp = await page.goto(acc, { waitUntil: 'networkidle', timeout: 60000 });
    console.log(`  status: ${resp && resp.status()} final: ${page.url()} title: ${await page.title().catch(() => '')}`);
  } catch (e) {
    console.log(`  goto note: ${e.message?.slice(0, 80)}`); // a download navigation throws — that's fine
  }
  await page.waitForTimeout(5000);
  // On the access/detail page, click a real Download button if present.
  for (const sel of ['a:has-text("Download")', 'button:has-text("Download")', 'a[href*=".skill"]', 'a[download]']) {
    if (saved) break;
    const loc = page.locator(sel);
    const n = await loc.count().catch(() => 0);
    for (let i = 0; i < n && !saved; i++) {
      const href = await loc.nth(i).getAttribute('href').catch(() => null);
      const label = (await loc.nth(i).innerText().catch(() => '')).trim().slice(0, 40);
      console.log(`  click [${sel}] #${i} "${label}" href=${href}`);
      noteSkill(href);
      try {
        await Promise.race([loc.nth(i).click({ timeout: 6000 }), page.waitForTimeout(6000)]);
        await page.waitForTimeout(4000);
      } catch (e) {
        console.log(`    note: ${e.message?.slice(0, 60)}`);
      }
    }
  }
}

await browser.close();

// 3) Direct-fetch any discovered .skill URL as a fallback.
console.log(`\n==== .skill URLs: ${JSON.stringify([...skillUrls])} ====`);
if (!saved) {
  for (const u of skillUrls) {
    try {
      const r = await fetch(u, { redirect: 'follow' });
      console.log(`FETCH ${u} -> ${r.status}`);
      if (r.ok) {
        const buf = Buffer.from(await r.arrayBuffer());
        writeFileSync('out/building-an-exo.skill', buf);
        console.log(`SAVED ${buf.length} bytes`);
        saved = true;
        break;
      }
    } catch (e) {
      console.log(`fetch err: ${e.message}`);
    }
  }
}

if (existsSync('out/building-an-exo.skill')) {
  try {
    const head = execSync('head -c 4 out/building-an-exo.skill | xxd -p').toString().trim();
    console.log(`file head: ${head}`);
    if (head.startsWith('504b')) {
      mkdirSync('out/extracted', { recursive: true });
      execSync('unzip -o out/building-an-exo.skill -d out/extracted', { stdio: 'inherit' });
      execSync('find out/extracted -maxdepth 3 -type f | sort', { stdio: 'inherit' });
    }
  } catch (e) {
    console.log(`post: ${e.message}`);
  }
} else {
  console.log('\nStill no file. If /access requires an OpenExO login, the download is account-gated.');
}
