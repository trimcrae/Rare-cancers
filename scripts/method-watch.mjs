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
// It ALSO watches CLINICAL / TREATMENT NEWS (added 2026-08-24 — see the section comment below
// for the miss that forced it): pivotal readouts, approvals and trial-registry movement in the
// modality classes this program pursues, plus a deliberately broad oncology catch-all.
// This script runs the search so a human/agent doesn't have to, and emits a digest tied
// to a capability->action trigger table (kept in research/method-watch.md and the
// strategy doc). It does NOT decide anything — it surfaces hits for triage.
//
// Zero dependencies (Node 22 global fetch). Sources:
//   - Europe PMC REST (literature)            https://www.ebi.ac.uk/europepmc
//   - GitHub Releases API (tool/model drops)  https://api.github.com
//   - grants.gov Search2 API (funding)        https://api.grants.gov
//   - ClinicalTrials.gov API v2 (trials)      https://clinicaltrials.gov
//   - RSS/Atom news feeds (treatment news)    https://news.google.com, https://www.fda.gov
//
// Usage:  node scripts/method-watch.mjs [out.md]
// Output: a Markdown digest (default research/method-watch-digest.md). The CI workflow
// publishes it to the `method-watch-cache` branch; read it with
//   git fetch origin method-watch-cache && git show origin/method-watch-cache:research/method-watch-digest.md
//
// NETWORK hosts (add to env egress to run locally): www.ebi.ac.uk, api.github.com,
// api.grants.gov, clinicaltrials.gov, news.google.com, www.fda.gov

import { writeFileSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
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
    // NEW (2026-07-05): cheap generative conformational-ensemble models (BioEmu / AlphaFlow /
    // subsampled-MSA AlphaFold / distributional structure prediction). If one validates against known
    // cryptic pockets, the per-target "open the pocket" cost collapses from GPU-days of MD to pennies —
    // which (a) cross-checks the NR4A3 metadynamics cheaply, and (b) flips the neglected-target
    // cryptic-pocket druggability atlas (IDEAS.md Platform/vision #4) from focused-class-only to
    // proteome-scale feasible.
    key: "cheap generative conformational-ensemble models (BioEmu / AlphaFlow / subsampled-MSA AF)",
    query: '(TITLE:BioEmu OR TITLE:AlphaFlow OR TITLE:"conformational ensemble" OR TITLE:"equilibrium ensemble" OR TITLE:"generative" OR TITLE:"Boltzmann generator" OR TITLE:"MSA subsampling" OR TITLE:"structural ensemble" OR TITLE:"protein dynamics") AND (TITLE:protein OR TITLE:structure OR TITLE:ensemble OR TITLE:conformation OR TITLE:"deep learning" OR TITLE:"machine learning")',
    trigger: "a cheap generative conformational-ensemble model validated against known cryptic pockets → (a) re-grade the NR4A3 LBD cryptic-pocket ensemble at near-zero cost as a cross-check on the metadynamics; (b) unlock proteome-scale feasibility for the cryptic-pocket druggability atlas (IDEAS.md Platform/vision #4)",
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
    // ⭑ ADDED 2026-08-24, by the backfill that swept the two months nothing was watching clinical
    // news. It surfaced "Durable clinical and immunologic response to an off-the-shelf EWSR1-FLI1
    // peptide vaccine in metastatic Ewing sarcoma" (2026-08-08) — a fusion-BREAKPOINT peptide
    // vaccine in a FET-fusion sarcoma, which is this repository's junction-vaccine route's exact
    // modality in a sibling fusion. NO ROW HERE COULD MATCH IT. The only FET row above requires a
    // MODEL word (cell line / organoid / PDX / xenograft / model) alongside the disease term, so it
    // catches new experimental systems and structurally cannot catch a THERAPEUTIC result in the
    // same disease. That is a gap in what we watch, not a ranking miss, and it is the second one
    // this episode has found: the first was having no clinical source at all.
    key: "fusion-BREAKPOINT-directed immunotherapy in FET / translocation sarcomas",
    query: '(TITLE:"EWSR1" OR TITLE:"EWS-FLI1" OR TITLE:"EWSR1-FLI1" OR TITLE:"EWSR1::FLI1" OR TITLE:"fusion breakpoint" OR TITLE:"fusion-derived" OR TITLE:"breakpoint peptide" OR TITLE:"Ewing sarcoma" OR TITLE:"synovial sarcoma" OR TITLE:"myxoid chondrosarcoma" OR TITLE:"fusion-positive sarcoma") AND (TITLE:vaccine OR TITLE:vaccination OR TITLE:neoantigen OR TITLE:immunotherapy OR TITLE:immunogenicity OR TITLE:epitope OR TITLE:"T cell" OR TITLE:"T-cell" OR TITLE:TCR)',
    trigger: "clinical or immunologic evidence for a fusion-BREAKPOINT-directed immunotherapy in ANY FET / translocation sarcoma → the closest available precedent for the EWSR1::NR4A3 junction-vaccine route (vaccine-construct.json); re-grade that route's central immunogenicity assumption and check whether the vaccine manuscript should cite it",
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
  ["microsoft/bioemu", "cheap generative equilibrium ensembles (cryptic-pocket atlas enabler)"],
  ["bjing2016/alphaflow", "AlphaFlow conformational ensembles (cryptic-pocket atlas enabler)"],
];

// ---- Funding watch (grants.gov open opportunities) -----------------------------------------
// WHY. The OSTP report "Science: A New Golden Age" (2026-07-21) directs federal agencies to
// redirect R&D funding toward AI and toward INDIVIDUAL scientists (away from universities). No
// applyable program shipped WITH the report — it's a directive; the money surfaces later as
// ordinary agency solicitations (NSF/DOE/NIH/DARPA/ARPA-H). This watch polls grants.gov's public
// Search2 API for currently-OPEN opportunities that fund AI/compute, and flags the actionable
// subset: those open to INDIVIDUALS (grants.gov eligibility code 25) or UNRESTRICTED (99) — the
// ones a solo, unaffiliated researcher on a personal/LLC status could actually apply to for GPU/
// compute funding. Triage only: a hit is a prompt to READ the solicitation, not a decision, and
// eligibility on the detail page is authoritative over the coarse filter here.
const GRANTS_API = "https://api.grants.gov/v1/api/search2";
// NOTE on precision: grants.gov OR-tokenizes bare keywords ("artificial" OR "intelligence"),
// which floods results with State-Dept/agriculture/NASA grants that merely contain "intelligence".
// Two levers fix it, applied together: (1) EXACT-PHRASE the keyword with embedded double quotes;
// (2) restrict to fundingCategories "ST" = Science & Technology / R&D (drops diplomacy/health-services
// noise). Eligibility 25 = Individuals, 99 = Unrestricted. Validated on a CI runner 2026-07-22.
const FUNDING = [
  {
    key: "AI research — open to INDIVIDUALS / unrestricted (the actionable set)",
    body: { keyword: '"artificial intelligence"', oppStatuses: "posted", fundingCategories: "ST", eligibilities: "25|99", rows: 12, sortBy: "openDate|desc" },
    note: "a solo unaffiliated researcher could apply directly — the OSTP 'individual scientists' path; the one to act on",
  },
  {
    key: "compute / GPU / HPC — open to INDIVIDUALS / unrestricted",
    body: { keyword: '"high performance computing"', oppStatuses: "posted", fundingCategories: "ST", eligibilities: "25|99", rows: 12, sortBy: "openDate|desc" },
    note: "directly funds the GPU/compute bottleneck AND is individual-eligible",
  },
  {
    key: "AI research (Science & Tech) — ALL eligibilities (firehose / early-warning)",
    body: { keyword: '"artificial intelligence"', oppStatuses: "posted", fundingCategories: "ST", rows: 12, sortBy: "openDate|desc" },
    note: "early warning of the OSTP-directed wave even where eligibility isn't (yet) individual — watch for individual-open successors",
  },
];

async function grantsSearch(body) {
  const r = await fetch(GRANTS_API, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      "User-Agent": "rare-cancers-method-watch",
    },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`grants.gov ${r.status}`);
  const j = await r.json();
  const hits = j?.data?.oppHits || [];
  return hits.map((h) => ({
    number: h.number || h.id || "",
    title: (h.title || "").replace(/\s+/g, " ").trim(),
    agency: h.agencyCode || h.agency || "",
    open: h.openDate || "",
    close: h.closeDate || "",
    url: h.id ? `https://www.grants.gov/search-results-detail/${h.id}` : "",
  }));
}

// ---- Clinical / treatment-news watch ------------------------------------------------------
// WHY THIS EXISTS (2026-08-24, trimcrae). The Merck/Moderna Phase 3 INTerpath-001 readout —
// intismeran autogene (mRNA-4157/V940) + pembrolizumab meeting RFS and DMFS in resected
// stage IIB-IV melanoma, the FIRST positive Phase 3 for an individualized neoantigen therapy —
// was announced 2026-08-19 and did NOT appear in the 2026-08-21 newsletter. It could not have:
// this script's only sources were Europe PMC (TITLE-anchored METHOD queries), eight GitHub
// release feeds and grants.gov. A topline readout announced by press release is not a paper,
// not a tool release and not a grant, so no query here could return it. That is an ABSENT
// SOURCE, not a bad filter — and it is exactly the class of item this program must see, because
// the repo carries a live EWSR1::NR4A3 junction-neoantigen vaccine route whose central premise
// is the modality that just read out.
//
// So two layers are added, and they are deliberately different in kind:
//   (1) TRIALS — ClinicalTrials.gov API v2, the authoritative registry. Slower than news but
//       structured, dated and citable; catches status flips, phase advances and posted results.
//   (2) NEWS — dated RSS/Atom. This is the layer that carries a same-day topline announcement.
// Both are TRIAGE, on the same terms as everything else in this digest: a hit is a prompt to
// check the trigger table, never a status change and never a result. NEWS ITEMS ARE PRESS
// SOURCES — a press release is not evidence at the standard this repo cites papers to
// (CLAUDE.md section 7), so a news hit may prompt reading the primary source, and may never
// itself be cited as a medical fact.
const NEWS_DAYS = Number(process.env.METHOD_WATCH_NEWS_DAYS || 14);
const CTG_DAYS = Number(process.env.METHOD_WATCH_CTG_DAYS || 60);

const CTGOV = "https://clinicaltrials.gov/api/v2/studies";

function isoDaysAgo(n) {
  return new Date(Date.now() - n * 86400000).toISOString().slice(0, 10);
}

// Registry watch. Scoped to the modality classes THIS program actually pursues, so a hit maps
// onto a route we hold rather than onto oncology at large.
const TRIALS = [
  {
    key: "individualized neoantigen therapy / therapeutic cancer vaccine (phase 2-3)",
    // ⚠ This row keeps query.term while its neighbours moved to query.intr, and the reason is
    // measured, not stylistic. Under query.intr (run 32719107868) the row lost INTerpath-009 —
    // the sibling Phase 3 of the very agent that prompted this whole watch — because the
    // intervention is registered as "Intismeran Autogene (V940)" and matches no modality word.
    // Under query.term (run 32718034880) it found it, and that row's other hits were all
    // genuinely vaccine/immunotherapy trials, so query.term costs little here. The ASO and
    // degrader rows went the other way on the same kind of evidence. Per-row, on what each
    // actually returned.
    term: '"neoantigen" OR "cancer vaccine" OR "individualized neoantigen therapy"',
    cond: 'cancer OR sarcoma OR melanoma OR "solid tumor"',
    trigger: "a pivotal readout, approval or halt for an individualized neoantigen therapy → re-grade the EWSR1::NR4A3 junction-vaccine route's precedent and feasibility (vaccine-construct.json); it is the modality that route assumes",
  },
  {
    key: "antisense / siRNA / oligonucleotide in SOLID tumours (phase 1-3)",
    intr: '"antisense oligonucleotide" OR antisense OR siRNA OR gapmer OR "RNA interference"',
    cond: 'cancer OR sarcoma OR "solid tumor"',
    trigger: "an oligonucleotide reaching a solid-tumour endpoint in humans → re-grade the fusion-junction ASO route's dominant gate (delivery), which is the whole reason that route is parked",
  },
  {
    key: "targeted protein degrader / molecular glue (clinical)",
    intr: '"protein degrader" OR PROTAC OR "molecular glue" OR "targeted protein degradation"',
    cond: "cancer",
    trigger: "clinical validation or failure of a degrader against a transcription-factor-class target → re-grade the NR4A3 degrader route's clinical precedent",
  },
  {
    key: "sarcoma / fusion-driven sarcoma — any interventional trial",
    term: '"myxoid chondrosarcoma" OR "extraskeletal myxoid chondrosarcoma" OR "fusion-positive sarcoma" OR "translocation-associated sarcoma"',
    cond: "sarcoma",
    trigger: "ANY trial recruiting in EMC or a fusion-driven sarcoma → a real-world route for a patient, and a possible collaborator/model source; fold into the registry (emc-clinical-registry.json) after reading the record",
  },
];

// News watch. Google News RSS is keyless and same-day, which is what a topline press release
// needs; the FDA feed is the official channel for the approval half. A dead feed prints its own
// failure and the digest still builds — never let one feed take the newsletter down.
const NEWS_FEEDS = [
  {
    key: "PIVOTAL ONCOLOGY READOUTS — the broad catch-all",
    // Deliberately NOT scoped to our modalities: this row exists so that treatment news large
    // enough to matter surfaces even when it is outside the route portfolio. It is the row whose
    // absence lost INTerpath-001.
    q: '("phase+3"+OR+"phase+III")+cancer+(topline+OR+"primary+endpoint"+OR+"met+its+endpoint"+OR+approval)',
    trigger: "any practice-changing or first-in-class oncology result → ask whether the MODALITY maps onto EWSR1::NR4A3 / EMC; if it does, re-grade that route and read the primary source before citing anything",
  },
  {
    key: "cancer vaccines / individualized neoantigen therapy",
    q: '("cancer+vaccine"+OR+"neoantigen"+OR+"mRNA+cancer")+(trial+OR+results+OR+approval)',
    trigger: "neoantigen-therapy news → direct precedent for the junction-vaccine route (the route's premise is that an individualized neoantigen approach can work); read the primary source, then re-grade",
  },
  {
    key: "oligonucleotide therapeutics in solid tumours (the ASO route's gate)",
    q: '("antisense"+OR+"siRNA"+OR+"oligonucleotide"+OR+"RNA+therapeutic")+(tumor+OR+tumour+OR+cancer+OR+sarcoma)',
    trigger: "an oligo delivered to a non-hepatic solid tumour in humans → the fusion-junction ASO route's dominant gate; re-grade delivery feasibility",
  },
  {
    key: "targeted protein degradation (clinical)",
    q: '("protein+degrader"+OR+PROTAC+OR+"molecular+glue")+(clinical+OR+trial+OR+patients)',
    trigger: "degrader clinical progress or failure → clinical precedent for the NR4A3 degrader route",
  },
  {
    key: "sarcoma treatment news",
    q: '(sarcoma+OR+"soft+tissue+cancer")+(treatment+OR+trial+OR+approval+OR+therapy+OR+drug)+-awareness+-fundraiser+-fundraising+-wedding+-obituary+-"in+memory"',
    trigger: "sarcoma treatment news → the disease area itself; anything touching EMC or a fusion-driven sarcoma goes into the registry after reading the primary source",
  },
  {
    // ⚠ NOT an FDA-hosted feed, and deliberately so. The first version of this row pointed at
    // https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-releases/rss.xml
    // and returned HTTP 404 on the validating CI run (2026-08-24, run 32717738350). FDA publishes
    // an oncology approval-notifications PAGE but no RSS endpoint that could be confirmed for it,
    // so the honest state of "the official feed URL" is UNKNOWN — and CLAUDE.md §4 says write
    // UNKNOWN rather than guess. Guessing a second FDA path would have bought another 404.
    // An approval reported by the trade press is the same signal, on a mechanism already proven
    // working in the rows above; if an official endpoint is ever confirmed, swap this URL for it.
    key: "regulatory approvals in oncology (via news; FDA's own RSS endpoint is UNKNOWN)",
    q: '(FDA+OR+EMA)+(approves+OR+approval)+(cancer+OR+oncology+OR+tumor+OR+sarcoma+OR+melanoma)',
    trigger: "an oncology approval → a modality cleared a regulator, which is the strongest available precedent signal for any route using it; confirm against the regulator's own notice before citing",
  },
];

// A feed's QUERY has one home (the `q` above); the WINDOW is supplied per run. Live runs pass
// `when:<N>d`; the backfill sweep passes `after:<date> before:<date>` for each slice. Keeping the
// two apart is what lets a backfill reuse the live query set instead of duplicating it — a second
// copy of these queries would drift from the first the day either is edited.
function feedUrl(f, windowToken) {
  return `https://news.google.com/rss/search?q=${f.q}+${windowToken}&hl=en-US&gl=US&ceid=US:en`;
}

function decodeEntities(s) {
  return String(s || "")
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1")
    .replace(/<[^>]+>/g, " ")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&apos;|&#0?39;/g, "'")
    .replace(/&nbsp;/g, " ")
    .replace(/&#(\d+);/g, (_, d) => String.fromCharCode(Number(d)))
    .replace(/&amp;/g, "&")
    .replace(/\s+/g, " ")
    .trim();
}

// Minimal RSS/Atom reader. Zero dependencies is a hard constraint of this script (see header),
// so this is a regex reader, not a parser — it reads well-formed feeds and is not asked to do
// more. Anything it cannot read shows up as a missing/failed row, never as a silent empty one.
function parseFeed(xml, limit) {
  const blocks = String(xml).match(/<(item|entry)\b[\s\S]*?<\/\1>/g) || [];
  return blocks.slice(0, limit).map((b) => {
    const title = decodeEntities((b.match(/<title[^>]*>([\s\S]*?)<\/title>/) || [, ""])[1]);
    let link = ((b.match(/<link[^>]*>([\s\S]*?)<\/link>/) || [, ""])[1] || "").trim();
    if (!link) link = (b.match(/<link[^>]*href="([^"]+)"/) || [, ""])[1] || "";
    const date = decodeEntities(
      (b.match(/<(pubDate|published|updated|dc:date)[^>]*>([\s\S]*?)<\/\1>/) || [, , ""])[2] || "",
    );
    return { title, link: decodeEntities(link), date };
  });
}

async function fetchText(url, ms = 25000) {
  const r = await fetch(url, {
    headers: { "User-Agent": "rare-cancers-method-watch", Accept: "*/*" },
    signal: AbortSignal.timeout(ms),
  });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.text();
}

// ClinicalTrials.gov API v2. The advanced filter + sort are the parts most likely to be
// rejected if the API's Essie syntax moves under us, so a 4xx retries WITHOUT them rather than
// returning nothing: a coarser row is a real reading, an empty row is an absent one, and
// CLAUDE.md section 4 forbids letting the second masquerade as the first.
async function ctgov(spec) {
  const since = isoDaysAgo(CTG_DAYS);
  const base = { format: "json", pageSize: "6", countTotal: "false" };
  // query.intr searches the INTERVENTION field; query.term searches everything and both stems and
  // expands, which is how the first validating run put a tamoxifen dose-optimisation trial in the
  // antisense row. A modality row means "this intervention", so it says so.
  if (spec.intr) base["query.intr"] = spec.intr;
  if (spec.term) base["query.term"] = spec.term;
  if (spec.cond) base["query.cond"] = spec.cond;
  const full = {
    ...base,
    "filter.advanced": `AREA[LastUpdatePostDate]RANGE[${since},MAX]`,
    sort: "LastUpdatePostDate:desc",
  };
  let json;
  let degraded = false;
  try {
    json = JSON.parse(await fetchText(`${CTGOV}?${new URLSearchParams(full)}`));
  } catch (e) {
    if (!/HTTP 4\d\d/.test(String(e.message))) throw e;
    degraded = true;
    json = JSON.parse(await fetchText(`${CTGOV}?${new URLSearchParams(base)}`));
  }
  const studies = json?.studies || [];
  return {
    degraded,
    hits: studies.map((st) => {
      const p = st.protocolSection || {};
      return {
        nct: p.identificationModule?.nctId || "",
        title: (p.identificationModule?.briefTitle || "").replace(/\s+/g, " ").trim(),
        phase: (p.designModule?.phases || []).join("/"),
        status: p.statusModule?.overallStatus || "",
        updated: p.statusModule?.lastUpdatePostDateStruct?.date || "",
        sponsor: p.sponsorCollaboratorsModule?.leadSponsor?.name || "",
        hasResults: Boolean(st.hasResults),
      };
    }),
  };
}

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

function withinDays(dateStr, days) {
  const d = Date.parse(dateStr);
  if (Number.isNaN(d)) return false;
  return (Date.now() - d) / 86400000 <= days;
}

function recent(dateStr) {
  return withinDays(dateStr, SINCE_DAYS);
}

async function main() {
  const out = process.argv[2] ||
    join(dirname(fileURLToPath(import.meta.url)), "..", "research", "method-watch-digest.md");
  const today = new Date().toISOString().slice(0, 10);
  const L = [];
  L.push(`# Method-watch digest — ${today}`);
  L.push("");
  L.push(`Auto-generated by \`scripts/method-watch.mjs\`. Four watches: **clinical / treatment news**`);
  L.push(`(trial registry + dated feeds), the **in-silico capabilities** that unlock blocked routes,`);
  L.push(`**tool/model releases**, and **open AI/compute funding** a solo researcher could apply to`);
  L.push(`(grants.gov). **Triage, don't trust:** a hit is a prompt to check the trigger table in`);
  L.push(`[research/method-watch.md](./method-watch.md), not a decision. Newest results first;`);
  L.push(`"🆕" = within ${SINCE_DAYS} days for literature/tools, ${NEWS_DAYS} days for news and trials.`);
  L.push("");

  // Clinical / treatment news comes FIRST: a pivotal readout outranks every keyword hit below it,
  // and burying it was half of why INTerpath-001 went unread even once a source existed for it.
  L.push(`## Clinical / treatment-news watch`);
  L.push(`*Added 2026-08-24* because a Phase 3 readout announced by press release is not a paper, a`);
  L.push(`tool release or a grant — so **no query in the three sections below could ever have returned`);
  L.push(`one.** ⚠ **Press sources are LEADS, NOT EVIDENCE:** a hit here is a prompt to read the`);
  L.push(`primary source (the registry record, the abstract, the regulator's notice). Nothing from a`);
  L.push(`news feed may be cited as a medical fact — repo rule, CLAUDE.md §7.`);
  L.push("");
  L.push(`### Trial registry — ClinicalTrials.gov (records updated within ${CTG_DAYS} days)`);
  for (const t of TRIALS) {
    L.push("");
    L.push(`#### ${t.key}`);
    L.push(`*Unlocks:* ${t.trigger}`);
    try {
      const { hits, degraded } = await ctgov(t);
      if (degraded) L.push(`- ⚠ _date filter/sort rejected by the API; showing an UNFILTERED, UNSORTED page instead — the recency flags below are not a recency filter._`);
      if (!hits.length) {
        L.push(`- _(no matching records)_`);
      } else {
        for (const h of hits) {
          const flag = withinDays(h.updated, NEWS_DAYS) ? "🆕 " : "";
          const bits = [h.phase, h.status, h.sponsor].filter(Boolean).join(" · ");
          const res = h.hasResults ? " · **results posted**" : "";
          L.push(`- ${flag}**${h.updated || "?"}** — ${h.title} (${bits}${res}) — https://clinicaltrials.gov/study/${h.nct}`);
        }
      }
    } catch (e) {
      L.push(`- _query failed: ${e.message}_`);
    }
  }

  L.push("");
  L.push(`### News feeds (items from the last ${NEWS_DAYS} days)`);
  for (const f of NEWS_FEEDS) {
    L.push("");
    L.push(`#### ${f.key}`);
    L.push(`*Unlocks:* ${f.trigger}`);
    try {
      const items = parseFeed(await fetchText(feedUrl(f, `when:${NEWS_DAYS}d`)), 25);
      if (!items.length) {
        // Distinguish "the feed said nothing happened" from "we could not read the feed" —
        // an absent reading is not a reading of absence (CLAUDE.md §4).
        L.push(`- ⚠ _feed returned no items at all — treat as UNREAD, not as quiet; check the feed URL._`);
      } else {
        const fresh = items.filter((i) => withinDays(i.date, NEWS_DAYS));
        if (!fresh.length) {
          L.push(`- _(feed live, ${items.length} items read; none dated in the last ${NEWS_DAYS} days)_`);
        } else {
          for (const i of fresh.slice(0, 8)) {
            const d = Date.parse(i.date);
            const day = Number.isNaN(d) ? i.date : new Date(d).toISOString().slice(0, 10);
            L.push(`- 🆕 **${day}** — ${i.title}${i.link ? ` — ${i.link}` : ""}`);
          }
          if (fresh.length > 8) L.push(`- _…and ${fresh.length - 8} more in window (not listed)._`);
        }
      }
    } catch (e) {
      L.push(`- _feed failed: ${e.message}_`);
    }
  }

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
  L.push(`## Funding watch (grants.gov — open AI / compute solicitations)`);
  L.push(`*Context:* the OSTP **"Science: A New Golden Age"** directive (2026-07-21) redirects federal`);
  L.push(`R&D toward AI and toward **individual scientists**. This polls grants.gov for currently-open`);
  L.push(`opportunities; the **individuals / unrestricted** blocks are the ones a solo unaffiliated`);
  L.push(`researcher could apply to for **GPU/compute** funding. Triage: a hit is a prompt to read the`);
  L.push(`solicitation — the detail page's eligibility is authoritative over this coarse filter.`);
  for (const f of FUNDING) {
    L.push("");
    L.push(`### ${f.key}`);
    L.push(`*Why it matters:* ${f.note}`);
    try {
      const hits = await grantsSearch(f.body);
      if (!hits.length) {
        L.push(`- _(no open opportunities match)_`);
      } else {
        for (const h of hits) {
          const flag = recent(h.open) ? "🆕 " : "";
          const close = h.close ? `, closes ${h.close}` : "";
          const link = h.url ? ` — ${h.url}` : "";
          L.push(`- ${flag}**${h.open || "?"}** — ${h.title} (${h.agency}, ${h.number}${close})${link}`);
        }
      }
    } catch (e) {
      L.push(`- _query failed: ${e.message}_`);
    }
  }

  L.push("");
  L.push(`---`);
  L.push(`_Next: if any 🆕 line crosses its trigger, act per research/method-watch.md and open the`);
  L.push(`corresponding follow-up; otherwise no action. Re-run monthly (CI) or \`node scripts/method-watch.mjs\`._`);

  writeFileSync(out, L.join("\n") + "\n");
  console.error(`wrote ${out}`);
}

export { CTGOV, NEWS_FEEDS, TRIALS, ctgov, decodeEntities, feedUrl, fetchText, isoDaysAgo, parseFeed, withinDays };

// Only sweep when run as a command. scripts/method-watch-backfill.mjs imports the config above,
// and an import that fired a live digest run would be a surprise with a network bill attached.
if (import.meta.url === pathToFileURL(process.argv[1] || "").href) {
  main().catch((e) => {
    console.error("method-watch failed:", e);
    process.exit(1);
  });
}
