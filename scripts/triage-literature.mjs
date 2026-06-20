#!/usr/bin/env node
// Triage a fetched literature index to surface the papers most likely to hold
// EXTRACTABLE cohort/outcome data, so curation reads the right papers first
// instead of skimming thousands of abstracts blind. Dependency-free.
//
// The index is produced by `scripts/fetch-paper.mjs sync` and published to the
// literature-cache branch. To triage that branch without checking it out:
//   git show origin/literature-cache:literature/<slug>/_index.json > /tmp/idx.json
//   node scripts/triage-literature.mjs /tmp/idx.json --term "extraskeletal myxoid chondrosarcoma"
//
// Flags: --term "<disease phrase>"  --top N  --json  --kind cohort/series
//
// Heuristic only — it points you at papers; every clinical value still has to be
// read, verified, and cited per METHODOLOGY.md. It never writes data.

import { readFileSync } from "node:fs";

const args = process.argv.slice(2);
const path = args.find((a) => !a.startsWith("--"));
const opt = (name, def) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : def; };
const flag = (name) => args.includes(name);
if (!path) {
  console.error('Usage: node scripts/triage-literature.mjs <_index.json> [--term "phrase"] [--top N] [--kind cohort/series] [--json]');
  process.exit(1);
}

const term = opt("--term", "extraskeletal myxoid chondrosarcoma").toLowerCase();
const top = Number(opt("--top", "60"));
const onlyKind = opt("--kind", null);
const records = JSON.parse(readFileSync(path, "utf8"));

const COHORT = /\b(cohort|retrospective|series|registry|database|seer|nationwide|population-based|multicenter|multicentre|consecutive|institution)\b/i;
const CASE = /\bcase report\b|\ba case of\b|\bwe report a\b|\bcase presentation\b/i;
const REVIEW = /\breview\b|\bmeta-analysis\b|\bsystematic review\b/i;
const OUTCOME = /\b(survival|disease-specific|recurrence|metastas|follow-?up|prognos|outcome|local control)\b/i;
const TOPICAL = /\bnr4a3\b|\bextraskeletal myxoid\b|\bextra-skeletal myxoid\b/i;

function nHints(t) {
  const out = new Set();
  for (const m of t.matchAll(/\bn\s*=\s*(\d{1,5})/gi)) out.add(+m[1]);
  for (const m of t.matchAll(/\b(\d{1,5})\s+(?:patients|cases|individuals|tumou?rs)\b/gi)) out.add(+m[1]);
  return [...out].filter((x) => x >= 2).sort((a, b) => b - a);
}
function periodHint(t) {
  const m = t.match(/between\s+(\d{4})\s+and\s+(\d{4})/i)
    || t.match(/\b(19\d{2}|20\d{2})\s*(?:[-–]|to)\s*(19\d{2}|20\d{2})\b/);
  return m ? [Math.min(+m[1], +m[2]), Math.max(+m[1], +m[2])] : null;
}

const scored = records.map((r) => {
  const t = ((r.title || "") + " " + (r.abstract || "")).replace(/\s+/g, " ");
  const onTopic = t.toLowerCase().includes(term) || TOPICAL.test(t);
  const ns = nHints(t);
  const maxN = ns[0] || r.n || 0;
  let kind = "other";
  if (REVIEW.test(t)) kind = "review";
  if (CASE.test(t)) kind = "case-report";
  if (COHORT.test(t) || maxN >= 10) kind = "cohort/series";
  let score = 0;
  if (onTopic) score += 5; else score -= 4;
  if (kind === "cohort/series") score += 6;
  else if (kind === "review") score += 2;
  if (OUTCOME.test(t)) score += 3;
  score += Math.min(6, Math.log10(Math.max(1, maxN)) * 3);
  if (r.abstract) score += 1;
  return { r, kind, maxN, ns, period: periodHint(t), onTopic, outcome: OUTCOME.test(t), score: Math.round(score * 10) / 10 };
}).filter((s) => (onlyKind ? s.kind === onlyKind : true))
  .sort((a, b) => b.score - a.score);

if (flag("--json")) {
  console.log(JSON.stringify(scored.slice(0, top).map((s) => ({
    pmcid: s.r.pmcid, pmid: s.r.pmid, year: s.r.year, kind: s.kind, n: s.maxN || null,
    period: s.period, onTopic: s.onTopic, hasFullText: !!s.r.fullTextFile, score: s.score, title: s.r.title,
  })), null, 2));
  process.exit(0);
}

const counts = scored.reduce((m, s) => ((m[s.kind] = (m[s.kind] || 0) + 1), m), {});
console.log(`${records.length} records | on-topic ${scored.filter((s) => s.onTopic).length} | `
  + Object.entries(counts).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k}:${v}`).join(" "));
console.log(`\nTop ${Math.min(top, scored.length)} candidates to read for cohort/outcome extraction`
  + (onlyKind ? ` (kind=${onlyKind})` : "") + ":\n");
for (const s of scored.slice(0, top)) {
  const id = s.r.pmcid || (s.r.pmid ? "MED/" + s.r.pmid : s.r.source + "/" + s.r.id) || "?";
  const tags = [s.kind, s.maxN ? "N~" + s.maxN : null, s.period ? "dx " + s.period[0] + "-" + s.period[1] : null,
    s.r.fullTextFile ? "fulltext" : "abstract", s.outcome ? "outcomes" : null].filter(Boolean).join(" · ");
  console.log(`${String(s.score).padStart(5)}  ${String(id).padEnd(14)} ${s.r.year || "????"}  ${tags}`);
  console.log(`        ${(s.r.title || "").slice(0, 110)}`);
}
