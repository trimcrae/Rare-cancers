#!/usr/bin/env node
// Evidence-contract check for the EMC clinical registry. ($0, dependency-free)
//
//   node scripts/validate-registry.mjs
//
// ⛔ WHY THIS SURVIVED THE PATIENT-SITE RETIREMENT, when almost nothing else did.
// This was `scripts/validate.mjs`, and it looked like site tooling: it validated the JSON the static
// site rendered. But what it actually enforces is the repository's EVIDENCE CONTRACT — every cohort
// resolves to a citation, no cohort reports more events than its denominator, a secondary source
// names its primary, pooled strata of one study are disjoint, and a study period is real. Those are
// the invariants the manuscript's meta-analysis ASSUMES and does not re-check.
//
// It is also gate 2 of `scripts/preflight.sh`, the repository-wide pre-commit entry point, so
// deleting it with the site would have made preflight report FAILED on every invocation forever.
//
// WHAT WAS REMOVED with the site: the index cross-reference, per-centre coordinates for a distance
// tool, live trial-search links, and the presentation-only banner check. Those served the interface.
// Nothing here does.
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const REGISTRY = join(root, "research", "data", "emc-clinical-registry.json");
const where = "research/data/emc-clinical-registry.json";

const errors = [];
const warns = [];

let d;
try {
  d = JSON.parse(readFileSync(REGISTRY, "utf8"));
} catch (e) {
  console.error(`ERROR ${where}: cannot read or parse - ${e.message}`);
  console.error("\nThis file is read by research/meta/meta-analysis.mjs and");
  console.error("research/hypotheses/enumerate-drugs.mjs. Both build the path segment-by-segment,");
  console.error("so a text search for the directory name will NOT find them.");
  process.exit(1);
}

// ── the evidence contract ────────────────────────────────────────────────────
const reg = d.registry || {};
if (!["SAMPLE_SYNTHETIC", "partial-curated", "curated"].includes(reg.dataStatus))
  errors.push(`${where}: registry.dataStatus must be SAMPLE_SYNTHETIC | partial-curated | curated`);

// Non-real data must be flagged and bannered. This is a medical-integrity rule, not a UI one:
// synthetic rows that read as real are the single most damaging failure this file can permit.
if (reg.dataStatus === "SAMPLE_SYNTHETIC" && !reg.dataStatusBanner)
  errors.push(`${where}: SAMPLE_SYNTHETIC data MUST carry registry.dataStatusBanner - non-real data that reads as real is a medical-integrity failure`);

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

const CUR = new Date().getFullYear();
const checkPeriod = (sp, ctx) => {
  if (sp === undefined) return;
  if (!Array.isArray(sp) || sp.length !== 2 || !Number.isInteger(sp[0]) || !Number.isInteger(sp[1]) ||
      sp[0] > sp[1] || sp[1] > CUR + 1)
    errors.push(`${ctx} studyPeriod must be [startYear, endYear] with start<=end<=${CUR + 1}`);
};

(reg.patients || []).forEach((p, i) => {
  for (const k of ["age", "sex", "stage", "vitalStatus", "sourceId"])
    if (p[k] === undefined) errors.push(`${where}: registry.patients[${i}] missing "${k}"`);
  if (p.sourceId && !hasCite(p.sourceId))
    errors.push(`${where}: registry.patients[${i}] sourceId "${p.sourceId}" has no registry.citations entry`);
  if (p.stage && !["localized", "regional", "distant"].includes(p.stage))
    warns.push(`${where}: patient[${i}].stage "${p.stage}" not in localized|regional|distant`);
});

// Cohorts are what the meta-analysis pools. Every rule here is one it assumes and does not re-check.
const poolKeys = {};
(reg.cohorts || []).forEach((c, i) => {
  const cw = `${where}: registry.cohorts[${i}] "${c.label || "?"}"`;
  if (!c.label) errors.push(`${cw} missing "label"`);
  if (typeof c.n !== "number") errors.push(`${cw} needs numeric "n"`);
  if (!hasCite(c.sourceId)) errors.push(`${cw} sourceId "${c.sourceId || ""}" has no registry.citations entry`);
  if (c.provenance === "secondary" && !c.primaryRef)
    errors.push(`${cw} provenance:"secondary" requires "primaryRef" (the original study)`);
  if (c.pool === false && !c.contextReason) warns.push(`${cw} is context (pool:false) but gives no contextReason`);
  checkPeriod(c.studyPeriod, cw);
  if (c.pool !== false && c.studyPeriod === undefined && !c.studyPeriodUnknown)
    warns.push(`${cw} is pooled but has no studyPeriod (set it, or studyPeriodUnknown:true if the source does not state it)`);
  for (const k of ["recurrence", "metastasis", "diseaseDeath"]) {
    const m = c[k];
    if (m && (typeof m.events !== "number" || typeof m.denom !== "number" || m.events > m.denom))
      errors.push(`${cw} ${k} needs events<=denom`);
  }
  // Double-counting guard: pooled strata of the same study must be disjoint. The meta-analysis
  // weights by denominator, so one patient counted twice silently inflates the pooled estimate.
  if (c.pool !== false && c.populationKey) {
    const key = `${c.populationKey}::${c.stratum || ""}`;
    if (poolKeys[key]) warns.push(`${cw} shares populationKey+stratum with cohort[${poolKeys[key]}] - risk of double-counting in the pool`);
    else poolKeys[key] = i;
  }
});
for (const [id, c] of Object.entries(citations)) checkPeriod(c.studyPeriod, `${where}: registry.citations.${id}`);

// Contested-evidence questions: a question marked contested must actually show opposing stances.
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
  if (q.consensus === "contested") {
    const stances = new Set(positions.map((p) => p.stance));
    if (!(stances.has("supports") && stances.has("against")) && !stances.has("mixed"))
      errors.push(`${qw} is marked "contested" but lacks opposing positions (need both supports and against)`);
  }
});

// Systemic-therapy evidence. This is the EXCLUSION LIST for the repurposing gap analysis
// (research/hypotheses/enumerate-drugs.mjs) - an agent missing here gets reported as novel.
(d.treatments?.systemicEvidence || []).forEach((e, i) => {
  const tw = `${where}: treatments.systemicEvidence[${i}] "${e.agent || "?"}"`;
  if (!e.agent) errors.push(`${tw} missing "agent"`);
  if (!hasCite(e.sourceId)) errors.push(`${tw} sourceId "${e.sourceId || ""}" has no registry.citations entry`);
  if (e.provenance === "secondary" && !e.primaryRef) errors.push(`${tw} provenance:"secondary" requires "primaryRef"`);
});
(d.emergingTreatments?.items || []).forEach((it, i) => {
  if (!it.name) errors.push(`${where}: emergingTreatments.items[${i}] missing name`);
  if (!it.url) warns.push(`${where}: emergingTreatments.items[${i}] "${it.name || "?"}" has no source url`);
});

(d.studies?.items || []).forEach((s, i) => {
  if (!s.url) errors.push(`${where}: studies.items[${i}] missing url`);
  if (!s.title) errors.push(`${where}: studies.items[${i}] missing title`);
});

for (const w of warns) console.warn("WARN  " + w);
if (errors.length) {
  for (const e of errors) console.error("ERROR " + e);
  console.error(`\n${errors.length} error(s), ${warns.length} warning(s).`);
  process.exit(1);
}
const nCohorts = (reg.cohorts || []).length;
const nCites = Object.keys(citations).length;
console.log(`OK - EMC clinical registry valid: ${nCites} citation(s), ${nCohorts} cohort(s). ${warns.length} warning(s).`);
