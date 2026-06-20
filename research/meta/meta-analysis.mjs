#!/usr/bin/env node
// Random-effects meta-analysis of EMC outcome proportions (zero-dependency).
//
// Method: logit-transformed proportions, DerSimonian-Laird random-effects pooling
// with I^2 / tau^2 heterogeneity; 0.5 continuity correction only for 0%/100% cells.
// Studies are the POOLED cohorts (grouped by source so a registry's disjoint strata
// count once); individual case reports are described separately, not meta-analysed.
// Outputs: console summary, research/meta/results.json, and SVG forest + PRISMA
// figures in research/figures/. Regenerate before circulating the manuscript.

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const data = JSON.parse(readFileSync(join(root, "data", "cancers", "emc.json"), "utf8"));
const cites = data.registry.citations || {};
const figDir = join(root, "research", "figures");
mkdirSync(figDir, { recursive: true });

const sum = (a) => a.reduce((x, y) => x + y, 0);
const expit = (x) => 1 / (1 + Math.exp(-x));
const pc1 = (x) => Math.round(x * 1000) / 10; // proportion -> % with 1 dp

// ---- group pooled cohorts into studies (by source), summing strata per metric ----
const METRICS = ["recurrence", "metastasis", "diseaseDeath"];
const studies = {};
for (const c of data.registry.cohorts.filter((c) => c.pool !== false)) {
  const s = (studies[c.sourceId] ||= { sourceId: c.sourceId, label: (cites[c.sourceId] || {}).short || c.sourceId, period: null, m: { recurrence: null, metastasis: null, diseaseDeath: null } });
  if (!s.period && Array.isArray(c.studyPeriod)) s.period = c.studyPeriod.slice();
  for (const k of METRICS) {
    if (k === "metastasis" && (c.criteria || {}).stage === "distant") continue; // baseline, not outcome
    const mm = c[k];
    if (mm && mm.denom) { s.m[k] ||= { e: 0, d: 0 }; s.m[k].e += mm.events; s.m[k].d += mm.denom; }
  }
}
const studyList = Object.values(studies);

// ---- per-study logit stats + DL random effects ----
function studyStat(e, n) {
  let r = e, m = n - e;
  if (r === 0 || m === 0) { r += 0.5; m += 0.5; }
  const y = Math.log(r / m), v = 1 / r + 1 / m;
  return { e, n, p: e / n, y, v, lo: expit(y - 1.96 * Math.sqrt(v)), hi: expit(y + 1.96 * Math.sqrt(v)) };
}
function dl(items) { // items: [{y,v}]
  const k = items.length, wf = items.map((i) => 1 / i.v), sw = sum(wf);
  const ybarF = sum(items.map((i, j) => wf[j] * i.y)) / sw;
  const Q = sum(items.map((i, j) => wf[j] * (i.y - ybarF) ** 2));
  const C = sw - sum(wf.map((w) => w * w)) / sw;
  const tau2 = k > 1 ? Math.max(0, (Q - (k - 1)) / (C || 1)) : 0;
  const I2 = Q > 0 && k > 1 ? Math.max(0, ((Q - (k - 1)) / Q) * 100) : 0;
  const wr = items.map((i) => 1 / (i.v + tau2)), swr = sum(wr);
  const y = sum(items.map((i, j) => wr[j] * i.y)) / swr, varp = 1 / swr;
  return { k, tau2, I2, Q, p: expit(y), lo: expit(y - 1.96 * Math.sqrt(varp)), hi: expit(y + 1.96 * Math.sqrt(varp)), weights: wr.map((w) => w / swr) };
}
function meta(metric) {
  const rows = studyList.filter((s) => s.m[metric] && s.m[metric].d).map((s) => ({ label: s.label, period: s.period, ...studyStat(s.m[metric].e, s.m[metric].d) }));
  if (!rows.length) return null;
  const pooled = dl(rows);
  rows.forEach((r, j) => (r.weight = pooled.weights[j]));
  return { metric, rows, pooled };
}
function looRange(metric) {
  const base = studyList.filter((s) => s.m[metric] && s.m[metric].d);
  if (base.length < 3) return null;
  const ps = base.map((_, idx) => dl(base.filter((__, j) => j !== idx).map((s) => studyStat(s.m[metric].e, s.m[metric].d))).p);
  return [Math.min(...ps), Math.max(...ps)];
}
function subsetPool(metric, pred) {
  const rows = studyList.filter((s) => s.m[metric] && s.m[metric].d && pred(s)).map((s) => studyStat(s.m[metric].e, s.m[metric].d));
  return rows.length ? { ...dl(rows), n: rows.length } : null;
}

// ---- SVG forest plot ----
function forestSVG(title, res) {
  const rows = res.rows, P = res.pooled;
  const W = 720, rowH = 26, top = 64, H = top + (rows.length + 3) * rowH + 30;
  const x0 = 300, x1 = 690; const maxX = Math.max(P.hi, ...rows.map((r) => r.hi)) * 1.1 || 1;
  const sx = (p) => x0 + (p / maxX) * (x1 - x0);
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" font-family="system-ui,Arial" font-size="13">`;
  s += `<rect width="${W}" height="${H}" fill="white"/>`;
  s += `<text x="14" y="26" font-size="15" font-weight="700">${esc(title)}</text>`;
  s += `<text x="14" y="48" fill="#555">Random-effects (DerSimonian-Laird, logit); I²=${P.I2.toFixed(0)}%, τ²=${P.tau2.toFixed(3)}, k=${P.k}</text>`;
  s += `<line x1="${x0}" y1="${top - 8}" x2="${x1}" y2="${top - 8}" stroke="#ccc"/>`;
  [0, 0.25, 0.5, 0.75].forEach((t) => { if (t <= maxX) { const x = sx(t); s += `<line x1="${x}" y1="${top - 8}" x2="${x}" y2="${H - 30}" stroke="#eee"/><text x="${x}" y="${H - 14}" text-anchor="middle" fill="#888">${t * 100}%</text>`; } });
  rows.forEach((r, i) => {
    const y = top + i * rowH + 14;
    s += `<text x="14" y="${y + 4}">${esc(r.label)}${r.period ? " (" + r.period[0] + "-" + r.period[1] + ")" : ""}</text>`;
    s += `<text x="250" y="${y + 4}" text-anchor="end" fill="#555">${r.e}/${r.n}</text>`;
    s += `<line x1="${sx(r.lo)}" y1="${y}" x2="${sx(r.hi)}" y2="${y}" stroke="#444"/>`;
    const sz = 3 + 7 * r.weight;
    s += `<rect x="${sx(r.p) - sz}" y="${y - sz}" width="${2 * sz}" height="${2 * sz}" fill="#2a6"/>`;
  });
  const yp = top + rows.length * rowH + 20;
  s += `<text x="14" y="${yp + 4}" font-weight="700">Pooled</text>`;
  s += `<text x="250" y="${yp + 4}" text-anchor="end" font-weight="700">${pc1(P.p)}%</text>`;
  const d = sx(P.p), l = sx(P.lo), h = sx(P.hi);
  s += `<polygon points="${l},${yp} ${d},${yp - 7} ${h},${yp} ${d},${yp + 7}" fill="#06c"/>`;
  s += `<text x="${h + 8}" y="${yp + 4}" fill="#06c">${pc1(P.p)}% (${pc1(P.lo)}-${pc1(P.hi)}%)</text>`;
  return s + "</svg>";
}

// ---- PRISMA flow (current snapshot; counts from the corpus + extraction) ----
function prismaSVG(n) {
  const box = (x, y, w, h, lines) => { let t = `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="#f7f9fb" stroke="#456"/>`; lines.forEach((ln, i) => (t += `<text x="${x + 10}" y="${y + 20 + i * 16}" font-size="12">${ln}</text>`)); return t; };
  const arrow = (x, y1, y2) => `<line x1="${x}" y1="${y1}" x2="${x}" y2="${y2}" stroke="#456" marker-end="url(#a)"/>`;
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="640" height="430" font-family="system-ui,Arial"><defs><marker id="a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#456"/></marker></defs><rect width="640" height="430" fill="white"/>`;
  s += `<text x="14" y="24" font-size="15" font-weight="700">PRISMA flow (snapshot) - EMC outcomes meta-analysis</text>`;
  s += box(160, 40, 320, 46, [`Records identified via Europe PMC: ${n.identified}`, `(EMC OR chordoid sarcoma OR NR4A3 AND chondrosarcoma)`]);
  s += arrow(320, 86, 110);
  s += box(160, 110, 320, 44, [`Title/abstract screened: ${n.identified}`, `Excluded - not EMC-specific: ${n.identified - n.onTopic}`]);
  s += arrow(320, 154, 178);
  s += box(160, 178, 320, 44, [`EMC-specific records: ${n.onTopic}`, `Assessed for extractable outcomes`]);
  s += arrow(320, 222, 246);
  s += box(120, 246, 400, 60, [`Included studies: ${n.pooled} pooled cohorts + ${n.context} context`, `+ ${n.cases} individual case reports`, `Excluded from pooling: overlap / %-only / different endpoint`]);
  s += arrow(320, 306, 330);
  s += box(120, 330, 400, 56, [`Quantitative synthesis (random-effects):`, `local recurrence (k=${n.kRec}), distant metastasis (k=${n.kMet})`, `disease-specific survival described per study`]);
  return s + "</svg>";
}

// ---- run ----
const results = {};
const out = [];
for (const metric of ["recurrence", "metastasis", "diseaseDeath"]) {
  const r = meta(metric); if (!r) continue;
  results[metric] = { pooled: r.pooled, studies: r.rows.map((x) => ({ label: x.label, e: x.e, n: x.n, p: x.p, ci: [x.lo, x.hi], weight: x.weight, period: x.period })), loo: looRange(metric) };
  writeFileSync(join(figDir, `forest-${metric}.svg`), forestSVG({ recurrence: "Local recurrence", metastasis: "Distant metastasis", diseaseDeath: "Disease-specific mortality" }[metric], r));
  out.push(`${metric}: pooled ${pc1(r.pooled.p)}% (95% CI ${pc1(r.pooled.lo)}-${pc1(r.pooled.hi)}%), I²=${r.pooled.I2.toFixed(0)}%, τ²=${r.pooled.tau2.toFixed(3)}, k=${r.pooled.k}`);
  const loo = looRange(metric); if (loo) out.push(`   leave-one-out pooled range: ${pc1(loo[0])}-${pc1(loo[1])}%`);
}
// sensitivity: era-stratified (study-period midpoint >= 2005) and registry-only, for recurrence
const mid = (s) => (s.period ? (s.period[0] + s.period[1]) / 2 : null);
const modern = subsetPool("recurrence", (s) => mid(s) !== null && mid(s) >= 2005);
const older = subsetPool("recurrence", (s) => mid(s) === null || mid(s) < 2005);
const registry = subsetPool("recurrence", (s) => s.sourceId === "masunaga2025");
if (modern) out.push(`recurrence (modern, dx mid>=2005, k=${modern.n}): ${pc1(modern.p)}% (${pc1(modern.lo)}-${pc1(modern.hi)}%)`);
if (older) out.push(`recurrence (older/undated, k=${older.n}): ${pc1(older.p)}% (${pc1(older.lo)}-${pc1(older.hi)}%)`);
if (registry) out.push(`recurrence (registry-only): ${pc1(registry.p)}% (${pc1(registry.lo)}-${pc1(registry.hi)}%)`);
results.sensitivity = { recurrence: { modern, older, registryOnly: registry } };

const prisma = { identified: 1369, onTopic: 133, pooled: 5, context: 9, cases: 4, kRec: results.recurrence?.pooled.k || 0, kMet: results.metastasis?.pooled.k || 0 };
writeFileSync(join(figDir, "prisma.svg"), prismaSVG(prisma));
results.prisma = prisma;
writeFileSync(join(dirname(fileURLToPath(import.meta.url)), "results.json"), JSON.stringify(results, null, 2));

console.log("EMC outcomes meta-analysis (random-effects, logit, DL)\n");
console.log(out.join("\n"));
console.log(`\nFigures: research/figures/{forest-recurrence,forest-metastasis,forest-diseaseDeath,prisma}.svg`);
console.log("Results: research/meta/results.json");
