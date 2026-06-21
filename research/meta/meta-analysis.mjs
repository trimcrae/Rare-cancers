#!/usr/bin/env node
// Random-effects meta-analysis of EMC outcome proportions (zero-dependency).
//
// Method: logit-transformed proportions, DerSimonian-Laird random-effects pooling
// with I^2 / tau^2 heterogeneity; 0.5 continuity correction only for 0%/100% cells.
// Studies are the POOLED cohorts (grouped by source so a registry's disjoint strata
// count once); individual case reports are described separately, not meta-analysed.
// Outputs: console summary + research/meta/results.json (study-level data). Forest plots and the
// PRISMA flow are rendered in the manuscript as a Markdown table + a Mermaid diagram - see
// AGENTS.md "Making figures"; hand-drawn SVG was removed. Regenerate results.json before
// circulating the manuscript.

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const data = JSON.parse(readFileSync(join(root, "data", "cancers", "emc.json"), "utf8"));
const cites = data.registry.citations || {};

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


// ---- run ----
const results = {};
const out = [];
for (const metric of ["recurrence", "metastasis", "diseaseDeath"]) {
  const r = meta(metric); if (!r) continue;
  results[metric] = { pooled: r.pooled, studies: r.rows.map((x) => ({ label: x.label, e: x.e, n: x.n, p: x.p, ci: [x.lo, x.hi], weight: x.weight, period: x.period })), loo: looRange(metric) };
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
results.prisma = prisma;
writeFileSync(join(dirname(fileURLToPath(import.meta.url)), "results.json"), JSON.stringify(results, null, 2));

console.log("EMC outcomes meta-analysis (random-effects, logit, DL)\n");
console.log(out.join("\n"));
console.log("Results: research/meta/results.json");
