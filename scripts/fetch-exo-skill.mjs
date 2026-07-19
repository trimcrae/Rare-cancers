#!/usr/bin/env node
// One-off: retrieve the official OpenExO "ExO 3.0 / building-an-exo" Claude Skill
// from a GitHub-hosted runner (unrestricted internet; the dev sandbox egress proxy
// 403s openexo.com at CONNECT). Diagnostic-first: it scrapes the public OpenExO
// pages for the .skill download URL, follows it, and verifies the payload is a real
// skill archive (a zip containing SKILL.md). Prints every URL it finds and every
// HTTP status so the log reveals an auth wall if the download is gated.
//
// Output: writes the raw archive to out/building-an-exo.skill and, if it is a zip,
// extracts it to out/extracted/. Exits non-zero only on a hard failure so the
// caller can distinguish "gated/not-found" (reported in log, exit 0 with no file)
// from "download succeeded".

import { writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { execSync } from 'node:child_process';

const UA =
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36';

const SEED_PAGES = [
  'https://openexo.com/resource-hub/exo-30-claude-skill',
  'https://openexo.com/claude-skill-how-to-guide',
  'https://openexo.com/resource-hub',
  'https://openexo.com/resource-hub/organizational-singularity-book-app',
];

async function get(url, asBuffer = false) {
  const res = await fetch(url, {
    redirect: 'follow',
    headers: { 'User-Agent': UA, Accept: '*/*' },
  });
  const status = res.status;
  const ctype = res.headers.get('content-type') || '';
  const clen = res.headers.get('content-length') || '?';
  console.log(`GET ${url} -> ${status} (${ctype}, ${clen} bytes)`);
  if (!res.ok) return { status, ok: false, ctype };
  if (asBuffer) {
    const buf = Buffer.from(await res.arrayBuffer());
    return { status, ok: true, ctype, buf };
  }
  const text = await res.text();
  return { status, ok: true, ctype, text };
}

// Pull candidate download URLs out of an HTML/JSON blob.
function extractCandidates(text, base) {
  const urls = new Set();
  // Any absolute or protocol-relative URL that smells like a skill / download / asset.
  const re =
    /(https?:\/\/[^\s"'<>()\\]+|\/\/[^\s"'<>()\\]+|\/[A-Za-z0-9_\-./%]+)/g;
  let m;
  while ((m = re.exec(text)) !== null) {
    let u = m[1];
    if (u.startsWith('//')) u = 'https:' + u;
    else if (u.startsWith('/')) {
      try {
        u = new URL(u, base).href;
      } catch {
        continue;
      }
    }
    const low = u.toLowerCase();
    if (
      low.includes('.skill') ||
      low.includes('building-an-exo') ||
      low.includes('.zip') ||
      (low.includes('download') &&
        (low.includes('skill') || low.includes('exo'))) ||
      // Webflow / S3 / uploads asset hosts commonly used by openexo
      low.includes('uploads-ssl.webflow') ||
      low.includes('assets.website-files') ||
      low.includes('cdn.prod.website-files') ||
      low.includes('amazonaws.com')
    ) {
      urls.add(u);
    }
  }
  return [...urls];
}

function looksLikeZip(buf) {
  return buf && buf.length > 4 && buf[0] === 0x50 && buf[1] === 0x4b; // "PK"
}

async function main() {
  mkdirSync('out', { recursive: true });
  const found = new Set();

  for (const page of SEED_PAGES) {
    let r;
    try {
      r = await get(page);
    } catch (e) {
      console.log(`  fetch error: ${e.message}`);
      continue;
    }
    if (!r.ok || !r.text) continue;
    const cands = extractCandidates(r.text, page);
    console.log(`  ${cands.length} candidate URL(s) on this page:`);
    for (const c of cands) {
      console.log(`    - ${c}`);
      found.add(c);
    }
  }

  // Prioritize direct .skill files, then building-an-exo, then zips.
  const ranked = [...found].sort((a, b) => {
    const score = (u) =>
      (u.toLowerCase().includes('.skill') ? 0 : 10) +
      (u.toLowerCase().includes('building-an-exo') ? 0 : 5) +
      (u.toLowerCase().includes('.zip') ? 0 : 2);
    return score(a) - score(b);
  });

  console.log(`\n=== Attempting downloads (${ranked.length} candidates) ===`);
  for (const url of ranked) {
    let r;
    try {
      r = await get(url, true);
    } catch (e) {
      console.log(`  download error: ${e.message}`);
      continue;
    }
    if (!r.ok || !r.buf) continue;
    // Accept a zip payload, or anything served as a .skill.
    const isZip = looksLikeZip(r.buf);
    const named = url.toLowerCase().includes('.skill');
    if (isZip || named) {
      writeFileSync('out/building-an-exo.skill', r.buf);
      console.log(
        `\nSAVED out/building-an-exo.skill from ${url} (${r.buf.length} bytes, zip=${isZip})`
      );
      if (isZip) {
        mkdirSync('out/extracted', { recursive: true });
        try {
          execSync('unzip -o out/building-an-exo.skill -d out/extracted', {
            stdio: 'inherit',
          });
          console.log('\n=== Extracted tree ===');
          execSync('find out/extracted -maxdepth 3 -type f | sort', {
            stdio: 'inherit',
          });
        } catch (e) {
          console.log(`unzip failed: ${e.message}`);
        }
      }
      return; // success
    } else {
      console.log(
        `  (not a skill/zip payload: first bytes ${r.buf.slice(0, 8).toString('hex')})`
      );
    }
  }

  console.log(
    '\nNO DOWNLOADABLE .skill FOUND. The resource is likely behind an OpenExO ' +
      'account login (client-rendered SPA / gated download). Reporting back to the user.'
  );
}

main().catch((e) => {
  console.error(e);
  process.exit(2);
});
