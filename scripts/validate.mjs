#!/usr/bin/env node
// Dependency-free sanity check for the data files.
// Run: node scripts/validate.mjs
import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const errors = [];
const warns = [];

const REQUIRED_TOP = ["schemaVersion", "meta", "overview", "studies", "outcomes", "registry", "treatments", "emergingTreatments", "clinicalTrials", "monitoring", "supportGroups", "centers", "questionsForOncologist"];
const REQUIRED_META = ["slug", "name", "abbreviation", "summary", "lastReviewed", "dataConfidence"];

function loadJson(path) {
  try { return JSON.parse(readFileSync(path, "utf8")); }
  catch (e) { errors.push(`${path}: invalid JSON - ${e.message}`); return null; }
}

// index.json
const index = loadJson(join(root, "data", "index.json"));
const indexSlugs = index ? new Set((index.cancers || []).map((c) => c.slug)) : new Set();

// each cancer file
const dir = join(root, "data", "cancers");
const files = readdirSync(dir).filter((f) => f.endsWith(".json"));
if (!files.length) errors.push("No data/cancers/*.json files found.");

for (const file of files) {
  const slug = file.replace(/\.json$/, "");
  const d = loadJson(join(dir, file));
  if (!d) continue;
  const where = `data/cancers/${file}`;

  for (const k of REQUIRED_TOP) if (!(k in d)) errors.push(`${where}: missing top-level "${k}"`);
  if (d.meta) {
    for (const k of REQUIRED_META) if (!(k in d.meta)) errors.push(`${where}: meta missing "${k}"`);
    if (d.meta.slug && d.meta.slug !== slug) errors.push(`${where}: meta.slug "${d.meta.slug}" != filename "${slug}"`);
    if (d.meta.dataConfidence && !["draft", "literature-reviewed", "clinician-reviewed"].includes(d.meta.dataConfidence))
      errors.push(`${where}: invalid dataConfidence "${d.meta.dataConfidence}"`);
    if (!indexSlugs.has(slug)) errors.push(`data/index.json: missing entry for "${slug}" (a data file exists but it's not listed)`);
  }

  // studies
  const items = d.studies?.items || [];
  items.forEach((s, i) => { if (!s.url) errors.push(`${where}: studies.items[${i}] missing url`); if (!s.title) errors.push(`${where}: studies.items[${i}] missing title`); });

  // registry / patients
  const reg = d.registry || {};
  if (!["SAMPLE_SYNTHETIC", "partial-curated", "curated"].includes(reg.dataStatus))
    errors.push(`${where}: registry.dataStatus must be SAMPLE_SYNTHETIC | partial-curated | curated`);
  (reg.patients || []).forEach((p, i) => {
    for (const k of ["age", "sex", "stage", "vitalStatus", "source"]) if (p[k] === undefined) errors.push(`${where}: registry.patients[${i}] missing "${k}"`);
    if (p.stage && !["localized", "regional", "distant"].includes(p.stage)) warns.push(`${where}: patient[${i}].stage "${p.stage}" not in localized|regional|distant`);
  });
  (reg.cohorts || []).forEach((c, i) => {
    if (!c.label) errors.push(`${where}: registry.cohorts[${i}] missing "label"`);
    if (typeof c.n !== "number") errors.push(`${where}: registry.cohorts[${i}] "${c.label || "?"}" needs numeric "n"`);
    if (!c.source) errors.push(`${where}: registry.cohorts[${i}] "${c.label || "?"}" missing "source"`);
    for (const k of ["recurrence", "metastasis", "diseaseDeath"]) {
      const m = c[k];
      if (m && (typeof m.events !== "number" || typeof m.denom !== "number" || m.events > m.denom))
        errors.push(`${where}: registry.cohorts[${i}] "${c.label || "?"}" ${k} needs events<=denom`);
    }
  });
  if (reg.dataStatus === "SAMPLE_SYNTHETIC" && !reg.dataStatusBanner)
    warns.push(`${where}: SAMPLE data should set registry.dataStatusBanner so the UI warns users.`);

  // emerging treatments
  (d.emergingTreatments?.items || []).forEach((it, i) => {
    if (!it.name) errors.push(`${where}: emergingTreatments.items[${i}] missing name`);
    if (!it.url) warns.push(`${where}: emergingTreatments.items[${i}] "${it.name || "?"}" has no source url`);
  });

  // clinical trials
  const ct = d.clinicalTrials || {};
  if (!(ct.liveSearches || []).length && !(ct.trials || []).length)
    warns.push(`${where}: clinicalTrials has no liveSearches and no trials - users won't find any trials.`);
  (ct.liveSearches || []).forEach((s, i) => { if (!s.url || !s.label) errors.push(`${where}: clinicalTrials.liveSearches[${i}] needs label + url`); });
  (ct.trials || []).forEach((t, i) => { if (!t.url || !t.title) errors.push(`${where}: clinicalTrials.trials[${i}] needs title + url`); });

  // centers need coords for the "near me" tool
  (d.centers?.list || []).forEach((c, i) => {
    if (!c.name || !c.country) errors.push(`${where}: centers.list[${i}] missing name/country`);
    if (c.lat == null || c.lng == null) warns.push(`${where}: centers.list[${i}] "${c.name}" has no lat/lng (won't appear in distance sort)`);
  });

  // shell page exists?
  // (informational only)
}

// index entries pointing at non-existent files
if (index) {
  for (const c of index.cancers || []) {
    if (!files.includes(`${c.slug}.json`)) errors.push(`data/index.json: "${c.slug}" listed but data/cancers/${c.slug}.json is missing`);
  }
}

for (const w of warns) console.warn("WARN  " + w);
if (errors.length) {
  for (const e of errors) console.error("ERROR " + e);
  console.error(`\n${errors.length} error(s), ${warns.length} warning(s).`);
  process.exit(1);
}
console.log(`OK - ${files.length} cancer file(s) valid. ${warns.length} warning(s).`);
