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
  // structured citation registry (see METHODOLOGY.md)
  const citations = reg.citations || {};
  const hasCite = (id) => id && Object.prototype.hasOwnProperty.call(citations, id);
  for (const [id, c] of Object.entries(citations)) {
    const cw = `${where}: registry.citations.${id}`;
    if (!c.title) errors.push(`${cw} missing "title"`);
    if (!c.year) errors.push(`${cw} missing "year"`);
    if (!c.pmid && !c.pmcid && !c.doi) errors.push(`${cw} needs a resolvable id (pmid|pmcid|doi)`);
    if (!c.url) errors.push(`${cw} missing "url"`);
    if (!c.license) warns.push(`${cw} has no license recorded`);
  }
  (reg.patients || []).forEach((p, i) => {
    for (const k of ["age", "sex", "stage", "vitalStatus", "sourceId"]) if (p[k] === undefined) errors.push(`${where}: registry.patients[${i}] missing "${k}"`);
    if (p.sourceId && !hasCite(p.sourceId)) errors.push(`${where}: registry.patients[${i}] sourceId "${p.sourceId}" has no registry.citations entry`);
    if (p.stage && !["localized", "regional", "distant"].includes(p.stage)) warns.push(`${where}: patient[${i}].stage "${p.stage}" not in localized|regional|distant`);
  });
  // study period (diagnosis years) sanity — see METHODOLOGY.md §4
  const CUR = new Date().getFullYear();
  const checkPeriod = (sp, ctx) => {
    if (sp === undefined) return;
    if (!Array.isArray(sp) || sp.length !== 2 || !Number.isInteger(sp[0]) || !Number.isInteger(sp[1]) || sp[0] > sp[1] || sp[1] > CUR + 1)
      errors.push(`${ctx} studyPeriod must be [startYear, endYear] with start<=end<=${CUR + 1}`);
  };
  const poolKeys = {};
  (reg.cohorts || []).forEach((c, i) => {
    const cw = `${where}: registry.cohorts[${i}] "${c.label || "?"}"`;
    if (!c.label) errors.push(`${cw} missing "label"`);
    if (typeof c.n !== "number") errors.push(`${cw} needs numeric "n"`);
    if (!hasCite(c.sourceId)) errors.push(`${cw} sourceId "${c.sourceId || ""}" has no registry.citations entry`);
    if (c.provenance === "secondary" && !c.primaryRef) errors.push(`${cw} provenance:"secondary" requires "primaryRef" (the original study)`);
    if (c.pool === false && !c.contextReason) warns.push(`${cw} is context (pool:false) but gives no contextReason`);
    checkPeriod(c.studyPeriod, cw);
    if (c.pool !== false && c.studyPeriod === undefined) warns.push(`${cw} is pooled but has no studyPeriod (diagnosis years) — record it if the source states it`);
    for (const k of ["recurrence", "metastasis", "diseaseDeath"]) {
      const m = c[k];
      if (m && (typeof m.events !== "number" || typeof m.denom !== "number" || m.events > m.denom))
        errors.push(`${cw} ${k} needs events<=denom`);
    }
    // double-counting guard: pooled strata of the same study must be disjoint
    if (c.pool !== false && c.populationKey) {
      const key = `${c.populationKey}::${c.stratum || ""}`;
      if (poolKeys[key]) warns.push(`${cw} shares populationKey+stratum with cohort[${poolKeys[key]}] - risk of double-counting in the pool`);
      else poolKeys[key] = i;
    }
  });
  for (const [id, c] of Object.entries(citations)) checkPeriod(c.studyPeriod, `${where}: registry.citations.${id}`);

  // contested-evidence questions — see METHODOLOGY.md §3
  const CONSENSUS = ["consensus-for", "consensus-against", "contested", "limited-evidence", "emerging"];
  const STANCES = ["supports", "against", "mixed", "null"];
  (d.evidenceQuestions || []).forEach((q, i) => {
    const qw = `${where}: evidenceQuestions[${i}] "${q.id || q.question || "?"}"`;
    if (!q.question) errors.push(`${qw} missing "question"`);
    if (!CONSENSUS.includes(q.consensus)) errors.push(`${qw} consensus must be one of ${CONSENSUS.join("|")}`);
    const positions = q.positions || [];
    if (!positions.length) errors.push(`${qw} needs at least one position`);
    positions.forEach((p, k) => {
      if (!STANCES.includes(p.stance)) errors.push(`${qw} position[${k}] stance must be ${STANCES.join("|")}`);
      if (!p.claim) errors.push(`${qw} position[${k}] missing "claim"`);
      if (!hasCite(p.sourceId)) errors.push(`${qw} position[${k}] sourceId "${p.sourceId || ""}" has no registry.citations entry`);
      if (p.provenance === "secondary" && !p.primaryRef) errors.push(`${qw} position[${k}] provenance:"secondary" requires "primaryRef"`);
      checkPeriod(p.studyPeriod, `${qw} position[${k}]`);
    });
    // "contested" must actually show opposing stances, not one-sided framing
    if (q.consensus === "contested") {
      const stances = new Set(positions.map((p) => p.stance));
      if (!(stances.has("supports") && stances.has("against")) && !stances.has("mixed"))
        errors.push(`${qw} is marked "contested" but lacks opposing positions (need both supports and against)`);
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
