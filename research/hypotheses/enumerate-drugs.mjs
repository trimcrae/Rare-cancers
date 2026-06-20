#!/usr/bin/env node
// Systematic target -> drug enumeration (roadmap item #1; see METHODOLOGY.md §7).
//
// Turns "drugs the curator recalled" into "every approved drug a public database
// links to EMC's documented targets". Queries the DGIdb GraphQL API (dgidb.org)
// for the genes in targets.json, keeps APPROVED drugs, builds a target->drug
// matrix, and runs a gap analysis against the hand-built catalog (candidates.json)
// to surface drugs we have NOT yet considered.
//
// Network egress is blocked in the dev sandbox, so this is meant to run in CI
// (.github/workflows/enumerate-drugs.yml). Logic is testable offline:
//   node research/hypotheses/enumerate-drugs.mjs --selftest
//
// No dependencies. Node >= 20 (global fetch).

import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const TARGETS = join(HERE, "targets.json");
const CATALOG = join(HERE, "candidates.json");
const PATIENT = join(HERE, "..", "..", "data", "cancers", "emc.json");
const OUT = join(HERE, "target-drug-matrix.json");
const DGIDB = "https://dgidb.org/api/graphql";

const norm = (s) => String(s || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();

// Drugs already used/tried in EMC (from the patient page) — these are deliberately
// kept OUT of the repurposing catalog (METHODOLOGY §2), so a gap analysis against the
// catalog alone would wrongly flag them as "novel". Collect their names to exclude.
function knownEmcDrugNames(patient) {
  const names = [];
  for (const r of patient?.treatments?.systemicEvidence || []) names.push(r.agent || r.drug || r.name);
  for (const i of patient?.emergingTreatments?.items || []) names.push(i.name);
  // first alphabetic token of each, e.g. "Pazopanib (VEGFR TKI)" -> "pazopanib"
  return names.map((s) => norm(s).split(" ")[0]).filter((s) => s && s.length >= 4);
}

// --- gap analysis: catalogued vs known-in-EMC vs genuinely novel --------------
function analyseGaps(approvedDrugIndex, catalog, knownNames = []) {
  const hay = (catalog.candidates || [])
    .map((c) => norm(`${c.drug} ${c.drugClass}`))
    .join(" || ");
  const known = new Set(knownNames);
  const inCatalog = [];
  const knownActiveInEmc = [];
  const newlySurfaced = [];
  for (const [name, info] of Object.entries(approvedDrugIndex)) {
    // Match on the INN root (first token) so salt forms map correctly
    // ("Sunitinib Malate"->sunitinib) and substrings don't collide
    // ("Lapatinib" must NOT match the EMC agent "apatinib").
    const root = norm(name).split(" ")[0];
    const row = { drug: name, targets: info.targets };
    if (root.length >= 4 && hay.includes(root)) inCatalog.push(row);  // already a candidate
    else if (known.has(root)) knownActiveInEmc.push(row);             // already tried in EMC
    else newlySurfaced.push(row);                                     // genuinely not considered
  }
  const byReach = (a, b) => b.targets.length - a.targets.length || a.drug.localeCompare(b.drug);
  return {
    inCatalog: inCatalog.sort(byReach),
    knownActiveInEmc: knownActiveInEmc.sort(byReach),
    newlySurfaced: newlySurfaced.sort(byReach),
  };
}

// --- DGIdb query --------------------------------------------------------------
async function queryDgidb(geneNames) {
  const query = `query($names:[String!]!){
    genes(names:$names){
      nodes{
        name
        interactions{
          drug{ name conceptId approved }
          interactionTypes{ type directionality }
          sources{ sourceDbName }
        }
      }
    }
  }`;
  const res = await fetch(DGIDB, {
    method: "POST",
    headers: { "content-type": "application/json", accept: "application/json" },
    body: JSON.stringify({ query, variables: { names: geneNames } }),
  });
  if (!res.ok) throw new Error(`DGIdb HTTP ${res.status}: ${(await res.text()).slice(0, 300)}`);
  const json = await res.json();
  if (json.errors) throw new Error(`DGIdb GraphQL errors: ${JSON.stringify(json.errors).slice(0, 300)}`);
  return json.data?.genes?.nodes || [];
}

function buildMatrix(targetDefs, nodes) {
  const byGene = new Map(nodes.map((n) => [norm(n.name), n]));
  const approvedDrugIndex = {};
  const targets = targetDefs.map((t) => {
    const node = byGene.get(norm(t.gene));
    const approvedDrugs = [];
    for (const it of node?.interactions || []) {
      if (!it.drug?.approved) continue;
      const name = it.drug.name;
      approvedDrugs.push({
        name,
        conceptId: it.drug.conceptId || null,
        interactionTypes: (it.interactionTypes || []).map((x) => x.type).filter(Boolean),
        sources: (it.sources || []).map((x) => x.sourceDbName).filter(Boolean),
      });
      const slot = (approvedDrugIndex[name] ||= { conceptId: it.drug.conceptId || null, targets: [] });
      if (!slot.targets.includes(t.gene)) slot.targets.push(t.gene);
    }
    // dedupe drugs within a target
    const seen = new Set();
    const uniq = approvedDrugs.filter((d) => (seen.has(d.name) ? false : seen.add(d.name)));
    return { gene: t.gene, role: t.role, sourceId: t.sourceId, matched: !!node, approvedDrugCount: uniq.length, approvedDrugs: uniq };
  });
  return { targets, approvedDrugIndex };
}

// --- selftest (no network) ----------------------------------------------------
function selftest() {
  const catalog = { candidates: [{ drug: "Imatinib (and other KIT inhibitors)", drugClass: "KIT/ABL TKI" }] };
  const known = ["pazopanib", "sunitinib", "apatinib"];
  const index = {
    Imatinib: { conceptId: "chembl:CHEMBL941", targets: ["KIT", "PDGFRA"] },
    Regorafenib: { conceptId: "chembl:CHEMBL1946170", targets: ["KDR", "KIT", "RET"] },
    Pioglitazone: { conceptId: "chembl:CHEMBL595", targets: ["PPARG"] },
    "Sunitinib Malate": { conceptId: "chembl:CHEMBL535", targets: ["KIT", "KDR"] },
    Lapatinib: { conceptId: "chembl:CHEMBL554", targets: ["KDR"] }, // must NOT match "apatinib"
  };
  const gaps = analyseGaps(index, catalog, known);
  const ok =
    gaps.inCatalog.length === 1 && gaps.inCatalog[0].drug === "Imatinib" &&
    gaps.knownActiveInEmc.some((d) => d.drug === "Sunitinib Malate") &&     // salt form -> known
    gaps.newlySurfaced.some((d) => d.drug === "Lapatinib") &&               // substring guard
    gaps.newlySurfaced.some((d) => d.drug === "Regorafenib") &&
    gaps.newlySurfaced.some((d) => d.drug === "Pioglitazone") &&
    !gaps.newlySurfaced.some((d) => /sunitinib/i.test(d.drug)) &&
    gaps.newlySurfaced[0].drug === "Regorafenib"; // sorted by target reach (3 > 1)
  console.log(JSON.stringify(gaps, null, 2));
  console.log(ok ? "SELFTEST OK" : "SELFTEST FAILED");
  process.exit(ok ? 0 : 1);
}

async function main() {
  if (process.argv.includes("--selftest")) return selftest();

  const targetDefs = JSON.parse(readFileSync(TARGETS, "utf8")).targets;
  const catalog = JSON.parse(readFileSync(CATALOG, "utf8"));
  const patient = JSON.parse(readFileSync(PATIENT, "utf8"));
  const knownNames = knownEmcDrugNames(patient);
  const genes = targetDefs.map((t) => t.gene);
  console.log(`Querying DGIdb for ${genes.length} EMC targets: ${genes.join(", ")}`);

  const nodes = await queryDgidb(genes);
  const matched = nodes.map((n) => n.name).join(", ");
  console.log(`DGIdb matched genes: ${matched || "(none)"}`);

  const { targets, approvedDrugIndex } = buildMatrix(targetDefs, nodes);
  const gapAnalysis = analyseGaps(approvedDrugIndex, catalog, knownNames);

  const out = {
    generatedAt: new Date().toISOString(),
    source: "DGIdb GraphQL (dgidb.org)",
    note: "Approved drugs only. A target->drug link is a starting point for triage, NOT an efficacy claim or an EMC treatment. newlySurfaced drugs are candidates to review against METHODOLOGY.md before cataloguing.",
    targetCount: targets.length,
    approvedDrugCount: Object.keys(approvedDrugIndex).length,
    targets,
    approvedDrugIndex,
    gapAnalysis,
  };
  writeFileSync(OUT, JSON.stringify(out, null, 2) + "\n");

  console.log(`\nApproved drugs hitting EMC targets: ${out.approvedDrugCount}`);
  console.log(`  already in catalog   : ${gapAnalysis.inCatalog.length}`);
  console.log(`  known/tried in EMC   : ${gapAnalysis.knownActiveInEmc.length}`);
  console.log(`  newly surfaced       : ${gapAnalysis.newlySurfaced.length}`);
  console.log("\nTop newly-surfaced (by target reach):");
  for (const d of gapAnalysis.newlySurfaced.slice(0, 15))
    console.log(`  ${d.drug.padEnd(28)} ${d.targets.join(", ")}`);
  console.log(`\nWrote ${OUT}`);
}

main().catch((e) => { console.error(e.message || e); process.exit(1); });
