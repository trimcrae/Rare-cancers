#!/usr/bin/env node
// method-watch — periodic digest of in-silico capabilities we are waiting on.
//
// WHY. The treatment program's bottleneck is not ideas but METHODS: several routes
// unlock the moment a specific in-silico capability becomes usable (virtual-cell
// perturbation prediction, open AF3-class ternary modelling, de-novo selective warhead
// design, and an in-silico way to predict/test oligonucleotide tumour DELIVERY).
// It also watches the fusion-junction ASO paper's specific next-step gates: a calibrated
// ASO off-target / RNase-H cleavage predictor (to retire the gap-mismatch heuristic), an
// improved ASO/siRNA efficacy + target-accessibility predictor, and new patient-derived
// EMC / FET-fusion-sarcoma functional models (to unblock the decisive knockdown experiment).
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
    // TITLE-anchor the method term (kills the date-sorted noise), AND a relevance clause.
    query: '(TITLE:"virtual cell" OR TITLE:"perturbation prediction" OR TITLE:scGPT OR TITLE:Geneformer OR TITLE:"single-cell foundation model") AND (gene OR transcriptomic OR knockout OR knockdown OR essentiality)',
    trigger: "predicts held-out knockdown phenotype → test EMC EWSR1::NR4A3 fusion-dependence (the degrader make-or-break)",
  },
  {
    key: "AF3-class structure / ternary complex",
    query: '(TITLE:AlphaFold3 OR TITLE:"AlphaFold 3" OR TITLE:Boltz OR TITLE:"Chai-1" OR TITLE:"ternary complex" OR TITLE:PROTAC OR TITLE:degrader) AND (structure OR ligand OR complex OR degradation)',
    trigger: "open ternary-complex prediction → model NR4A3–PROTAC–E3 degradability geometry",
  },
  {
    key: "de-novo selective small-molecule / binder design",
    query: '(TITLE:RFdiffusion OR TITLE:ProteinMPNN OR TITLE:"de novo design" OR TITLE:"binder design" OR TITLE:"generative model" OR TITLE:"structure-based drug design") AND (protein OR molecule OR inhibitor OR selectivity OR binder)',
    trigger: "reliable generative + selectivity scoring → design the NR4A3 warhead at the nr4a-selectivity.json handles",
  },
  {
    key: "cryptic-pocket / dynamics-based druggability",
    query: '(TITLE:"cryptic pocket" OR TITLE:"cryptic site" OR TITLE:"transient pocket" OR TITLE:PocketMiner OR TITLE:druggability OR TITLE:"hidden pocket") AND (protein OR pocket OR binding OR ligand)',
    trigger: "robust cryptic-pocket prediction → re-grade the NR4A3 LBD undruggability prior without GPU MD",
  },
  {
    // NEW: an in-silico way to test/predict tumour delivery — the ASO/siRNA route's gate.
    key: "in-silico oligonucleotide / nanoparticle tumour-delivery prediction",
    query: '(TITLE:"oligonucleotide conjugate" OR TITLE:"antibody-oligonucleotide" OR TITLE:"siRNA delivery" OR TITLE:"tumor delivery" OR TITLE:"tumour delivery" OR TITLE:"endosomal escape" OR TITLE:"tumor penetration" OR TITLE:"tumour penetration") AND (predict OR prediction OR "machine learning" OR "deep learning" OR "in silico" OR computational OR model)',
    trigger: "usable in-silico delivery/biodistribution/endosomal-escape predictor → score the B7-H3-targeted junction-siRNA/AOC delivery and re-grade the ASO route feasibility",
  },
  {
    // NEW (2026-07-03): the ASO route's dominant gate is delivery, and the unblock may be an
    // actual delivery TECHNOLOGY/CANDIDATE — not just an in-silico predictor. This topic watches
    // for a real delivery handle we could name for an EMC/soft-tissue-sarcoma oligo: an AOC/
    // conjugate or tumour-penetrating-peptide/nanoparticle platform that reaches non-hepatic solid
    // tumours, OR an EMC-enriched surface antigen characterised (which would give the AOC its
    // targeting arm). A hit here is what makes a concrete delivery CANDIDATE proposable, moving the
    // route off "delivery-limited" even without an in-silico predictor.
    key: "oligonucleotide tumour-delivery TECHNOLOGY / candidate (AOC, TPP, sarcoma-targeted, EMC surface antigen)",
    query: '(TITLE:"antibody-oligonucleotide conjugate" OR TITLE:"antibody oligonucleotide conjugate" OR TITLE:AOC OR TITLE:"tumor-penetrating peptide" OR TITLE:"tumour-penetrating peptide" OR TITLE:"cell-penetrating peptide" OR TITLE:"targeted lipid nanoparticle" OR TITLE:"receptor-targeted" OR TITLE:"ligand-targeted") AND (TITLE:oligonucleotide OR TITLE:siRNA OR TITLE:antisense OR TITLE:gapmer OR TITLE:sarcoma OR TITLE:"solid tumor" OR TITLE:"solid tumour" OR TITLE:delivery)',
    trigger: "a delivery technology/candidate for non-hepatic solid tumours (AOC, tumour-penetrating peptide, ligand-targeted LNP), or an EMC-enriched surface antigen → propose a concrete junction-oligo delivery CANDIDATE and re-grade the ASO route's dominant gate",
  },
  {
    // ASO next-step gate #1: a calibrated ASO off-target / RNase-H cleavage-activity predictor
    // would let us replace the conservative "gap mismatch => non-cleaving" heuristic the junction-ASO
    // specificity screen currently relies on (fusion-junction-aso-paper §3a-quater red-team finding).
    key: "ASO/gapmer off-target & RNase-H cleavage prediction",
    query: '(TITLE:antisense OR TITLE:gapmer OR TITLE:"antisense oligonucleotide" OR TITLE:ASO OR TITLE:"RNase H" OR TITLE:"RNase-H") AND (TITLE:"off-target" OR TITLE:specificity OR TITLE:toxicity OR TITLE:hepatotoxicity OR TITLE:cleavage OR TITLE:prediction OR TITLE:"machine learning" OR TITLE:"deep learning")',
    trigger: "usable ASO off-target / RNase-H cleavage-activity predictor → replace the conservative gap-mismatch heuristic in the junction-ASO specificity screen (aso-paper §3a-quater) with a calibrated predictor and re-grade predicted specificity",
  },
  {
    // ASO next-step gate #2: better ASO/siRNA efficacy + target-site accessibility prediction would
    // improve design ranking and replace the local-fold accessibility proxy (aso-paper §3a-bis iii).
    key: "ASO/siRNA design, efficacy & target-accessibility prediction",
    query: '(TITLE:siRNA OR TITLE:gapmer OR TITLE:antisense OR TITLE:"antisense oligonucleotide" OR TITLE:RNAi) AND (TITLE:design OR TITLE:efficacy OR TITLE:potency OR TITLE:accessibility OR TITLE:"machine learning" OR TITLE:"deep learning" OR TITLE:"target site")',
    trigger: "improved ASO/siRNA efficacy/accessibility predictor → re-rank the junction designs for potency and replace the local-fold accessibility proxy (aso-paper §3a-bis iii)",
  },
  {
    // ASO next-step gate #3: a new patient-derived EMC / FET-fusion-sarcoma functional model unblocks
    // the decisive wet-lab knockdown + parental-sparing experiment (aso-paper §4) and a fusion-dependence readout.
    key: "patient-derived EMC / FET-fusion-sarcoma functional models",
    query: '(TITLE:"myxoid chondrosarcoma" OR TITLE:"EWSR1-NR4A3" OR TITLE:"EWSR1::NR4A3" OR TITLE:"fusion-positive sarcoma" OR TITLE:"Ewing sarcoma") AND (TITLE:"cell line" OR TITLE:organoid OR TITLE:"patient-derived" OR TITLE:xenograft OR TITLE:PDX OR TITLE:model)',
    trigger: "new patient-derived EMC model (line/organoid/PDX) → enables the decisive junction-ASO knockdown + parental-sparing experiment (aso-paper §4) and a fusion-dependence readout",
  },
  {
    // The ONE row that is not in-silico: a remote-controlled / cloud robotic wet lab a solo
    // researcher can rent by the experiment (Emerald Cloud Lab, Strateos/Transcriptic-class, or an
    // autonomous "self-driving lab" / lab-in-the-loop service). This is the only watched capability
    // that could FLIP the project's founding "no wet lab" constraint — letting US run the wet-lab-
    // gated experiments (junction-ASO knockdown + parental-sparing; degrader/delivery validation)
    // rather than routing them through a hypothetical funded collaborator. Trigger requires solo-
    // affordable pricing AND cell-based-assay scope; the EMC cell line/reagents remain a separate gate.
    key: "remote-controlled / cloud robotic wet lab (solo-affordable, cell-assay scope)",
    query: '(TITLE:"cloud lab" OR TITLE:"cloud laboratory" OR TITLE:"self-driving laboratory" OR TITLE:"self-driving lab" OR TITLE:"autonomous laboratory" OR TITLE:"autonomous lab" OR TITLE:"robotic laboratory" OR TITLE:"remote experiment" OR TITLE:"lab-in-the-loop" OR TITLE:"Emerald Cloud Lab" OR TITLE:Strateos OR TITLE:Transcriptic OR TITLE:"laboratory automation") AND (biology OR cell OR assay OR experiment OR "drug discovery" OR wet-lab OR wetlab)',
    trigger: "a solo-affordable, cell-assay-capable remote/cloud robotic wet lab → re-grade the whole 'no wet lab' operating regime; scope+price the cheapest decisive experiment (junction-ASO knockdown + parental-sparing, aso-paper §4) and ask trimcrae before committing spend. Flips the EXECUTION gate, not the EMC-cell-line/reagent (material) gate",
  },
  {
    key: "NR4A3 / EWSR1::NR4A3 direct EMC advances",
    query: '(TITLE:NR4A3 OR TITLE:NOR-1 OR TITLE:"EWSR1-NR4A3" OR TITLE:"EWSR1::NR4A3" OR TITLE:"myxoid chondrosarcoma" OR ABSTRACT:"EWSR1-NR4A3" OR ABSTRACT:NR4A3)',
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
