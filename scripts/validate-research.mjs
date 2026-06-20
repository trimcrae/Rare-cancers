#!/usr/bin/env node
// Validate the drug-repurposing candidate catalog (research/hypotheses/candidates.json).
// Enforces the integrity rules in research/hypotheses/METHODOLOGY.md:
// every candidate is graded, and every mechanistic claim is either cited to a
// resolvable source or explicitly flagged needs-verification.
// Run: node scripts/validate-research.mjs

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const file = join(root, "research", "hypotheses", "candidates.json");
const errors = [];
const warns = [];

let d;
try { d = JSON.parse(readFileSync(file, "utf8")); }
catch (e) { console.error(`candidates.json: invalid JSON - ${e.message}`); process.exit(1); }

const citations = d.citations || {};
const tiers = d.tiers || {};
const hasCite = (id) => id && Object.prototype.hasOwnProperty.call(citations, id);
const SPEC = ["low", "moderate", "high"];

if (!d.disclaimer) errors.push("missing top-level disclaimer");
if (!Object.keys(tiers).length) errors.push("missing tiers");

for (const [id, c] of Object.entries(citations)) {
  const cw = `citations.${id}`;
  if (!c.title) errors.push(`${cw} missing title`);
  if (!c.pmid && !c.pmcid && !c.doi) errors.push(`${cw} needs a resolvable id (pmid|pmcid|doi)`);
  if (!c.url) errors.push(`${cw} missing url`);
}

const checkClaim = (o, ctx) => {
  if (!o.claim) errors.push(`${ctx} missing claim`);
  if (o.sourceId) { if (!hasCite(o.sourceId)) errors.push(`${ctx} sourceId "${o.sourceId}" has no citation`); }
  else if (o.sourceStatus === "needs-verification") warns.push(`${ctx} claim is unverified (needs-verification) — resolve before publication`);
  else errors.push(`${ctx} needs a sourceId or sourceStatus:"needs-verification"`);
};

const cands = d.candidates || [];
if (!cands.length) errors.push("no candidates");
const ids = new Set();
cands.forEach((c, i) => {
  const cw = `candidates[${i}] "${c.id || c.drug || "?"}"`;
  for (const k of ["id", "drug", "drugClass", "mechanism", "rationale"]) if (!c[k]) errors.push(`${cw} missing "${k}"`);
  if (c.id) { if (ids.has(c.id)) errors.push(`${cw} duplicate id`); ids.add(c.id); }
  if (!tiers[c.evidenceTier]) errors.push(`${cw} evidenceTier "${c.evidenceTier}" not in tiers`);
  if (!SPEC.includes(c.speculationLevel)) errors.push(`${cw} speculationLevel must be ${SPEC.join("|")}`);
  if (typeof c.notTriedInEmc !== "boolean") errors.push(`${cw} needs boolean "notTriedInEmc"`);
  if (!c.keyRisks) warns.push(`${cw} has no keyRisks stated`);
  if (!c.emcVulnerability) errors.push(`${cw} missing emcVulnerability`);
  else checkClaim(c.emcVulnerability, `${cw}.emcVulnerability`);
  (c.supportingEvidence || []).forEach((e, k) => checkClaim(e, `${cw}.supportingEvidence[${k}]`));
  // a graduated (T3) candidate would belong on the patient page; flag for review
  if (c.evidenceTier === "T3-emc-clinical-evidence")
    warns.push(`${cw} is T3 — eligible to graduate to the patient page (needs clinician review)`);
});

for (const w of warns) console.warn("WARN  " + w);
if (errors.length) {
  for (const e of errors) console.error("ERROR " + e);
  console.error(`\n${errors.length} error(s), ${warns.length} warning(s).`);
  process.exit(1);
}
console.log(`OK - ${cands.length} candidate(s) valid. ${warns.length} warning(s) (unverified claims to resolve before publication).`);
