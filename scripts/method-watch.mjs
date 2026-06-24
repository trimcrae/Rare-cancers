#!/usr/bin/env node
// method-watch — periodic digest of in-silico capabilities we are waiting on.
//
// WHY. The treatment program's bottleneck is not ideas but METHODS: several routes
// unlock the moment a specific in-silico capability becomes usable (virtual-cell
// perturbation prediction, open AF3-class ternary modelling, de-novo selective warhead
// design, and now an in-silico way to predict/test oligonucleotide tumour DELIVERY).
// This script runs the search so a human/agent doesn't have to, and emits a digest tied
// to a capability->action trigger table (kept in research/method-watch.md and the
// strategy doc). It does NOT decide anything — it surfaces hits for triage.
//
// Zero dependencies (Node 22 global fetch). Sources:
//   - Europe PMC REST (literature)            https://www.ebi.ac.uk/europepmc
//   - GitHub Releases API (tool/model drops)  https://api.github.com
//
// Usage:  node scripts/method-watch.mjs [out.md]
// Output: a Markdown digest (default research/method-watch-digest.md). The CI workflow
// publishes it to the `method-watch-cache` branch; read it with
//   git fetch origin method-watch-cache && git show origin/method-watch-cache:research/method-watch-digest.md
//
// NETWORK hosts (add to env egress to run locally): www.ebi.ac.uk, api.github.com

import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search";

// Capability gaps we are waiting on. Each is a literature query + the action a hit unlocks.
// Keep in sync with the trigger table in research/method-watch.md / emc-treatment-strategy.md.
const TOPICS = [
  {
    key: "virtual-cell / perturbation prediction",
    query: '("virtual cell" OR "perturbation prediction" OR scGPT OR Geneformer OR "State model" OR "Arc Virtual Cell") AND (knockdown OR knockout OR essentiality OR dependency)',
    trigger: "predicts held-out knockdown phenotype → test EMC EWSR1::NR4A3 fusion-dependence (the degrader make-or-break)",
  },
  {
    key: "AF3-class structure / ternary complex",
    query: '(AlphaFold3 OR Boltz OR "Chai-1" OR RoseTTAFold) AND (ligand OR "ternary complex" OR PROTAC OR "small molecule")',
    trigger: "open ternary-complex prediction → model NR4A3–PROTAC–E3 degradability geometry",
  },
  {
    key: "de-novo selective small-molecule / binder design",
    query: '("structure-based" OR "de novo" OR diffusion OR RFdiffusion OR ProteinMPNN) AND ("binder design" OR "molecule generation" OR "selectivity") AND ("nuclear receptor" OR kinase OR protein)',
    trigger: "reliable generative + selectivity scoring → design the NR4A3 warhead at the nr4a-selectivity.json handles",
  },
  {
    key: "cryptic-pocket / dynamics-based druggability",
    query: '("cryptic pocket" OR "transient pocket" OR PocketMiner OR "induced fit" OR metadynamics) AND (druggable OR "binding site" OR ligand)',
    trigger: "robust cryptic-pocket prediction → re-grade the NR4A3 LBD undruggability prior without GPU MD",
  },
  {
    // NEW: an in-silico way to test/predict tumour delivery — the ASO/siRNA route's gate.
    key: "in-silico oligonucleotide / nanoparticle tumour-delivery prediction",
    query: '("antibody oligonucleotide conjugate" OR "siRNA delivery" OR "lipid nanoparticle" OR "nanoparticle tumor" OR "endosomal escape" OR "tumor penetration") AND ("machine learning" OR "deep learning" OR predict* OR "in silico" OR computational OR PBPK OR model)',
    trigger: "usable in-silico delivery/biodistribution/endosomal-escape predictor → score the B7-H3-targeted junction-siRNA/AOC delivery and re-grade the ASO route feasibility",
  },
  {
    key: "NR4A3 / EWSR1::NR4A3 direct EMC advances",
    query: '(NR4A3 OR NOR-1 OR "EWSR1-NR4A3" OR "extraskeletal myxoid chondrosarcoma") AND (inhibitor OR degrader OR ligand OR "small molecule" OR therapy OR vulnerability)',
    trigger: "any direct chemical/biological matter against NR4A3 or the fusion → fold into the relevant route memo immediately",
  },
];

// Tool/model GitHub repos whose releases mark a capability becoming usable.
const REPOS = [
  ["google-deepmind/alphafold3", "AF3 weights/code availability"],
  ["jwohlwend/boltz", "open AF3-class structure+affinity"],
  ["chaidiscovery/chai-lab", "open AF3-class folding"],
  ["RosettaCommons/RFdiffusion", "de-novo binder design"],
  ["bowman-lab/PocketMiner", "cryptic-pocket prediction"],
  ["bytedance/protenix", "open AF3-class folding"],
];

const SINCE_DAYS = Number(process.env.METHOD_WATCH_DAYS || 120);

async function epmc(query) {
  const url =
    `${EPMC}?query=${encodeURIComponent(query)}` +
    `&format=json&resultType=lite&pageSize=6&sort=${encodeURIComponent("P_PDATE_D desc")}`;
  const r = await fetch(url, { headers: { "User-Agent": "rare-cancers-method-watch" } });
  if (!r.ok) throw new Error(`EPMC ${r.status}`);
  const j = await r.json();
  return (j.resultList?.result || []).map((p) => ({
    id: p.pmcid || (p.pmid ? `MED/${p.pmid}` : p.id),
    title: (p.title || "").replace(/\s+/g, " ").trim(),
    date: p.firstPublicationDate || String(p.pubYear || ""),
    source: p.source,
  }));
}

async function ghLatest(repo) {
  const headers = { "User-Agent": "rare-cancers-method-watch", Accept: "application/vnd.github+json" };
  if (process.env.GITHUB_TOKEN) headers.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`;
  const r = await fetch(`https://api.github.com/repos/${repo}/releases/latest`, { headers });
  if (r.status === 404) return { repo, note: "no published release yet" };
  if (!r.ok) throw new Error(`GH ${r.status}`);
  const j = await r.json();
  return { repo, tag: j.tag_name, name: (j.name || "").trim(), date: j.published_at };
}

function recent(dateStr) {
  const d = Date.parse(dateStr);
  if (Number.isNaN(d)) return false;
  return (Date.now() - d) / 86400000 <= SINCE_DAYS;
}

async function main() {
  const out = process.argv[2] ||
    join(dirname(fileURLToPath(import.meta.url)), "..", "research", "method-watch-digest.md");
  const today = new Date().toISOString().slice(0, 10);
  const L = [];
  L.push(`# Method-watch digest — ${today}`);
  L.push("");
  L.push(`Auto-generated by \`scripts/method-watch.mjs\`. Watches the in-silico capabilities that`);
  L.push(`unlock blocked routes. **Triage, don't trust:** a hit is a prompt to check the trigger`);
  L.push(`table in [research/method-watch.md](./method-watch.md), not a decision. Newest results`);
  L.push(`first; "🆕" = within ${SINCE_DAYS} days.`);
  L.push("");

  L.push(`## Literature watch`);
  for (const t of TOPICS) {
    L.push("");
    L.push(`### ${t.key}`);
    L.push(`*Unlocks:* ${t.trigger}`);
    try {
      const hits = await epmc(t.query);
      if (!hits.length) {
        L.push(`- _(no hits)_`);
      } else {
        for (const h of hits) {
          const flag = recent(h.date) ? "🆕 " : "";
          L.push(`- ${flag}**${h.date}** — ${h.title} (${h.source}:${h.id})`);
        }
      }
    } catch (e) {
      L.push(`- _query failed: ${e.message}_`);
    }
  }

  L.push("");
  L.push(`## Tool / model release watch`);
  for (const [repo, why] of REPOS) {
    try {
      const g = await ghLatest(repo);
      if (g.note) {
        L.push(`- \`${repo}\` — ${g.note} _(${why})_`);
      } else {
        const flag = recent(g.date) ? "🆕 " : "";
        L.push(`- ${flag}\`${repo}\` — ${g.tag} (${(g.date || "").slice(0, 10)}) _(${why})_`);
      }
    } catch (e) {
      L.push(`- \`${repo}\` — _check failed: ${e.message}_`);
    }
  }

  L.push("");
  L.push(`---`);
  L.push(`_Next: if any 🆕 line crosses its trigger, act per research/method-watch.md and open the`);
  L.push(`corresponding follow-up; otherwise no action. Re-run monthly (CI) or \`node scripts/method-watch.mjs\`._`);

  writeFileSync(out, L.join("\n") + "\n");
  console.error(`wrote ${out}`);
}

main().catch((e) => {
  console.error("method-watch failed:", e);
  process.exit(1);
});
