#!/usr/bin/env node
// Generate reproducible, data-driven manuscript figures from candidates.json.
// Zero dependencies; emits SVG (the repo is a static site). Re-run after the catalog
// changes:  node research/manuscripts/figures/make-figures.mjs
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const cands = JSON.parse(readFileSync(join(here, "../../hypotheses/candidates.json"), "utf8")).candidates;

const TIER_COLOR = { "T3": "#1b7837", "T2": "#5aae61", "T1": "#2c7fb8", "T0": "#9aa0a6" };
const tierKey = (t) => String(t).split("-")[0].toUpperCase(); // "T1-preclinical-or-analog" -> "T1"
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

// short label per candidate
function shortLabel(c) {
  const d = c.drug || "";
  const paren = d.indexOf("(");
  let s = (paren > 0 ? d.slice(0, paren) : d).trim();
  if (s.length > 30) s = s.split(/[\/,]/)[0].trim();
  if (s.length > 30) s = s.slice(0, 29) + "…";
  return s;
}

const rows = cands
  .map((c) => ({ label: shortLabel(c), tier: tierKey(c.evidenceTier), score: c.priorityScore, page: !!c.patientPageEligible, rank: c.rank }))
  .sort((a, b) => a.rank - b.rank);

// layout
const W = 760, padL = 250, padR = 70, padT = 64, rowH = 26, padB = 56;
const H = padT + rows.length * rowH + padB;
const maxScore = 18, plotW = W - padL - padR;
const x = (v) => padL + (v / maxScore) * plotW;

const parts = [];
parts.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif">`);
parts.push(`<rect width="${W}" height="${H}" fill="#ffffff"/>`);
parts.push(`<text x="${padL}" y="26" font-size="16" font-weight="700" fill="#202124">EMC existing-drug repurposing candidates</text>`);
parts.push(`<text x="${padL}" y="44" font-size="11.5" fill="#5f6368">Priority score (0–18) by evidence tier · ★ = eligible for the patient page (pending clinician review)</text>`);

// x gridlines + axis labels (0,6,12,18)
for (const v of [0, 6, 12, 18]) {
  parts.push(`<line x1="${x(v)}" y1="${padT - 8}" x2="${x(v)}" y2="${padT + rows.length * rowH}" stroke="#eceff1" stroke-width="1"/>`);
  parts.push(`<text x="${x(v)}" y="${padT + rows.length * rowH + 16}" font-size="10" fill="#80868b" text-anchor="middle">${v}</text>`);
}

rows.forEach((r, i) => {
  const y = padT + i * rowH;
  const cy = y + rowH / 2;
  const color = TIER_COLOR[r.tier] || "#9aa0a6";
  parts.push(`<text x="${padL - 10}" y="${cy + 3.5}" font-size="11.5" fill="#202124" text-anchor="end">${esc(r.label)}${r.page ? " ★" : ""}</text>`);
  parts.push(`<rect x="${padL}" y="${y + 4}" width="${Math.max(1, x(r.score) - padL)}" height="${rowH - 9}" rx="2" fill="${color}"/>`);
  parts.push(`<text x="${x(r.score) + 6}" y="${cy + 3.5}" font-size="10.5" fill="#5f6368">${r.score} · ${r.tier}</text>`);
});

// legend
const ly = padT + rows.length * rowH + 34;
let lx = padL;
parts.push(`<text x="${padL - 10}" y="${ly + 3}" font-size="10.5" fill="#5f6368" text-anchor="end">Tier</text>`);
for (const [t, c] of Object.entries(TIER_COLOR)) {
  parts.push(`<rect x="${lx}" y="${ly - 8}" width="11" height="11" rx="2" fill="${c}"/>`);
  parts.push(`<text x="${lx + 15}" y="${ly + 1.5}" font-size="10.5" fill="#5f6368">${t}</text>`);
  lx += 60;
}
parts.push(`</svg>`);

const out = join(here, "candidate-landscape.svg");
writeFileSync(out, parts.join("\n") + "\n");
console.log(`Wrote ${out} (${rows.length} candidates)`);
