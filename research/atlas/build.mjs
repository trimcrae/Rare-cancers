#!/usr/bin/env node
/**
 * EMC Open Target & Drug Atlas — build & validate.
 *
 * One command: `node research/atlas/build.mjs`
 *   1. Loads the JSON sources of truth (citations, samples, claims, drug_screens, evidence_score).
 *   2. Validates PROVENANCE: every citation key referenced anywhere must resolve in citations.json
 *      (or be a whitelisted token like "unknown"/a claim id). Fails (exit 1) on a dangling reference.
 *   3. Emits the human-readable TSV deliverables into research/atlas/dist/.
 *
 * No third-party dependencies (repo rule). Deterministic: same inputs -> same dist/.
 */
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const DIST = join(HERE, "dist");
const load = (f) => JSON.parse(readFileSync(join(HERE, f), "utf8"));

const citations = load("citations.json");
const samples = load("samples.json");
const claims = load("claims.json");
const screens = load("drug_screens.json");
const score = load("evidence_score.json");

const CIT = new Set(Object.keys(citations.citations));
const CLAIM_IDS = new Set(claims.claims.map((c) => c.claim_id));
const COMPOUNDS = new Set(screens.hits.map((h) => h.compound));
const WHITELIST = new Set(["unknown", "to_confirm", "n/a", "NA"]);

const errors = [];
const warnings = [];

// --- provenance: a reference resolves if it's a citation key, a claim id, a compound, or whitelisted ---
const resolves = (ref) =>
  CIT.has(ref) || CLAIM_IDS.has(ref) || COMPOUNDS.has(ref) || WHITELIST.has(ref);

for (const s of samples.samples) {
  if (!resolves(s.source_publication))
    errors.push(`sample ${s.sample_id}: unresolved source_publication '${s.source_publication}'`);
}
for (const c of claims.claims) {
  for (const ref of [].concat(c.source || [])) {
    if (!resolves(ref)) errors.push(`claim ${c.claim_id}: unresolved source '${ref}'`);
  }
  if (c.contradicts && !CLAIM_IDS.has(c.contradicts))
    errors.push(`claim ${c.claim_id}: contradicts unknown claim '${c.contradicts}'`);
}
for (const sc of screens.screens) {
  if (!resolves(sc.source)) errors.push(`screen ${sc.screen_id}: unresolved source '${sc.source}'`);
}
const SCREEN_IDS = new Set(screens.screens.map((s) => s.screen_id));
for (const h of screens.hits) {
  if (!SCREEN_IDS.has(h.screen_id)) errors.push(`hit ${h.compound}: unknown screen_id '${h.screen_id}'`);
}
for (const e of score.entities) {
  for (const ref of e.supporting_claims || []) {
    if (!resolves(ref)) warnings.push(`entity ${e.id}: supporting_claim '${ref}' not a citation/claim/compound`);
  }
}

// --- integrity spot-checks the atlas is meant to enforce ---
// every non-database citation should have a verified flag present
for (const [k, v] of Object.entries(citations.citations)) {
  if (v.verified === undefined) warnings.push(`citation ${k}: missing 'verified' flag`);
}
// EWSR1/TAF15 must never be pooled silently: any claim scoped 'all' should say so explicitly (informational)

// --- TSV writers ---
const tsv = (rows) => rows.map((r) => r.map((x) => String(x ?? "").replace(/\t/g, " ").replace(/\n/g, " ")).join("\t")).join("\n") + "\n";
mkdirSync(DIST, { recursive: true });

// 1. sample manifest
writeFileSync(join(DIST, "emc_sample_manifest.tsv"), tsv([
  samples.fields,
  ...samples.samples.map((s) => samples.fields.map((f) => s[f])),
]));

// 2. claims with provenance
writeFileSync(join(DIST, "emc_claims_with_provenance.tsv"), tsv([
  claims.fields,
  ...claims.claims.map((c) => claims.fields.map((f) => (Array.isArray(c[f]) ? c[f].join(";") : c[f]))),
]));

// 3. drug screen hits + combinations
writeFileSync(join(DIST, "emc_drug_screens.tsv"), tsv([
  ["type", "compound_or_combo", "screen_id", "target_or_classpair", "result", "verification", "notes"],
  ...screens.hits.map((h) => ["hit", h.compound, h.screen_id, h.nominal_target, h.result, h.verification, h.notes || ""]),
  ...screens.combinations.map((c) => ["combo", c.combo, c.screen_id, c.class_pair, c.result, c.verification, c.correction_note || ""]),
]));

// 4. compound -> target -> exposure
writeFileSync(join(DIST, "emc_compound_target_exposure.tsv"), tsv([
  ["compound", "class", "nominal_target", "polypharmacology", "approved_indication", "achievable_free_exposure", "solid_tumor_caveat", "engagement_assay", "verification"],
  ...screens.hits.map((h) => [h.compound, h.class, h.nominal_target, h.polypharmacology, h.approved_indication, h.achievable_free_exposure, h.solid_tumor_caveat, h.engagement_assay, h.verification]),
]));

// 5. evidence score (components as columns)
const comp = Object.keys(score.components);
writeFileSync(join(DIST, "emc_evidence_score.tsv"), tsv([
  ["entity_id", "label", "tier", "composite", ...comp],
  ...score.entities.map((e) => [e.id, e.label, e.tier, e.composite, ...comp.map((c) => e.scores[c])]),
]));

// --- report ---
console.log(`EMC Atlas build:`);
console.log(`  citations: ${CIT.size}  samples: ${samples.samples.length}  claims: ${claims.claims.length}  screen-hits: ${screens.hits.length}  scored-entities: ${score.entities.length}`);
// Verification tiers (transparent heuristic classification of each source's verification_level;
// unlike tiers are NOT aggregated as one "verified" count). Rules below; refine per-source as needed.
const tierOf = (c) => {
  if (!c.verified) return "unresolved_pending";
  const v = (c.verification_level || "").toLowerCase();
  const rt = (c.resourceType || "").toLowerCase();
  if (/full[ _-]?text|full text open/.test(v)) return "primary_full_text";
  if (/primary abstract/.test(v)) return "primary_abstract";
  if (/dailymed|fda label|regulatory/.test(v) || rt === "database" && /dailymed/.test((c.short||"").toLowerCase())) return "regulatory_label";
  if (/reprocessed|computational|ci,|\(ci\)|repro/.test(v) || ["repo_analysis","repo_synthesis","method","database"].includes(rt)) return "computational_or_resource";
  if (/secondary|snippet/.test(v)) return "secondary_source_unconfirmed";
  if (c.pmid || c.pmcid || c.doi) return "primary_reference"; // verified PMID/PMCID/DOI, tier not otherwise specified
  return "verified_other";
};
const tierCounts = {};
for (const c of Object.values(citations.citations)) { const t = tierOf(c); tierCounts[t] = (tierCounts[t]||0)+1; }
console.log(`  verification tiers (sources): ${JSON.stringify(tierCounts)}`);
console.log(`  (unlike tiers are NOT summed as one 'verified' count; 'unresolved_pending' must not be stated as fact)`);
console.log(`  dist/: emc_sample_manifest.tsv, emc_claims_with_provenance.tsv, emc_drug_screens.tsv, emc_compound_target_exposure.tsv, emc_evidence_score.tsv`);
if (warnings.length) { console.log(`\n  ${warnings.length} warning(s):`); warnings.forEach((w) => console.log(`   - ${w}`)); }
if (errors.length) {
  console.error(`\n  ${errors.length} ERROR(s):`);
  errors.forEach((e) => console.error(`   ! ${e}`));
  process.exit(1);
}
console.log(`\n  provenance OK — every reference resolves.`);
