# Method-watch — in-silico capabilities we are waiting on

**Purpose.** This program's bottleneck is *methods*, not ideas: several routes unlock the
moment a specific in-silico capability becomes usable. This file is the **watch config +
trigger table** (what to look for, and what to do when it appears). The periodic search
itself is automated — `scripts/method-watch.mjs`, run monthly by
`.github/workflows/method-watch.yml` — which emits a dated **digest**.

**Operating assumption (trimcrae, standing).** In-silico drug-discovery capability is on a
**steep, rising frontier** — the limits of today are not the limits in 6–12 months — and this is
a **long-lived, revisitable project that rides that frontier even if a wet-lab partner never
materialises** (regime: `emc-treatment-strategy.md → "Operating regime (2026-07-01)"`). So this
watch has **two jobs, not one**: (1) *unblock* stalled/parked routes when a capability lands
(the trigger table below), and (2) prompt a **re-grade of even *completed* work** as methods
improve — a cleared route or a shipped result is a *snapshot at a capability level*, worth
re-running when the frontier moves. Nothing here is "dead"; parked = "revisit when X lands."
**Integrity guardrail:** a coming capability justifies waiting and re-running — it never licenses
claiming the result before the method can support it.

**This file IS the "breadth" half of "state of the art."** Per the codified principle
(`CLAUDE.md → "WHAT 'STATE OF THE ART' MEANS = BREADTH-FIRST, STANDARD-DEPTH"`), a *new technique* that
opens a new evidence axis (rows below) is **default-worth-adding**; but *deepening a test we've already
run to field standard* (more FEP sampling, extra force fields, more replicates, HREX-when-independent-
windows-suffice) is **default-NO** unless the standard result is genuinely ambiguous and decision-relevant.
Adding a row here (breadth) beats over-optimizing an existing test (depth-past-standard).

> **Read the latest auto-digest:**
> `git fetch origin method-watch-cache`
> `git show origin/method-watch-cache:research/method-watch-digest.md`
> (or run `node scripts/method-watch.mjs` locally, hosts `www.ebi.ac.uk` + `api.github.com`).

**How to use it:** the digest surfaces newest papers / tool releases per capability. A hit is
a *prompt to check this table*, not a decision. If a "🆕" line genuinely crosses a trigger
below, do the paired action and open the follow-up; otherwise no action.

## Capability → action trigger table
| When this capability becomes usable | …do this |
|---|---|
| virtual-cell / perturbation model predicts held-out **knockdown phenotype** | test EMC **EWSR1::NR4A3 fusion-dependence** — the degrader/ASO make-or-break |
| open **AF3-class ternary-complex** prediction | model **NR4A3–PROTAC–E3** degradability geometry |
| reliable **structure-based generative + selectivity** scoring | design the **NR4A3 warhead** at the `nr4a-selectivity.json` divergent handles |
| robust **cryptic-pocket** prediction | re-grade the NR4A3 LBD **undruggability** prior without GPU MD |
| cheaper / more reliable **free-energy (FEP or ML free-energy)** on **cryptic / induced-fit** pockets | run the **denovo_401 selectivity FEP** currently SKIP-ped as ceiling-bound + least-reliable-here, and re-grade the binder-selectivity claim against it |
| turnkey / maintained **alchemical protein-mutation (relative selectivity) FEP** **AND** a favourable NR4A3-vs-NR4A1/2 **pocket-homology** assessment (few divergent pocket-lining residues; similar *opened* backbones) | run **alchemical-mutation FEP as a confirmatory cross-check** on the ABFE selectivity ΔΔG — a *direct* ΔΔG with built-in error cancellation would harden (or refute) the binder-selectivity claim now carried by the ABFE-difference. Precursor = the pocket-homology check itself (align NR4A3/1/2 opened Pocket-5, count differing lining residues + backbone RMSD): if pockets are highly similar, mutation-FEP becomes attractive; if they diverge conformationally, that *itself justifies* the per-receptor ABFE choice (`nr4a3-degrader-paper.md` §4 "Why absolute (ABFE), not relative/mutation, FEP") |
| better **induced-fit / conformational-ensemble docking or ML affinity** | re-score denovo_401 (and the de-novo pool) against the *dynamic* NR4A3 pocket instead of single/few frames — tightens the frame-dependent margin (+12.83 release vs +7.44 metad) |
| **in-silico oligonucleotide/nanoparticle tumour-delivery** predictor (biodistribution / endosomal escape / PBPK / ML tumour-penetration) | score the **B7-H3-targeted junction-siRNA / AOC** delivery in-silico and **re-grade the ASO route feasibility** (delivery is the route's gate) |
| **oligonucleotide tumour-delivery TECHNOLOGY / candidate** — an AOC/conjugate, tumour-penetrating-peptide, or ligand-targeted-LNP platform that reaches **non-hepatic solid tumours**, OR a **characterised EMC-enriched surface antigen** (the AOC's targeting arm) | **propose a concrete junction-oligo delivery *candidate*** (not just an in-silico test) and re-grade the ASO route's dominant gate — this is the watch for a real *way to do delivery*, distinct from the predictor row above |
| calibrated **ASO off-target / RNase-H cleavage-activity** predictor | **retire the conservative "gap-mismatch ⇒ non-cleaving" heuristic** in the junction-ASO specificity screen (`fusion-junction-aso-paper.md` §3a-quater) and re-grade predicted specificity with a calibrated model |
| improved **ASO/siRNA efficacy + target-site-accessibility** predictor | **re-rank the junction designs for potency** and replace the local-fold accessibility proxy (`fusion-junction-aso-paper.md` §3a-bis iii) |
| new **patient-derived EMC / FET-fusion-sarcoma model** (cell line / organoid / PDX) | **enables the decisive wet-lab experiment** — junction-ASO knockdown + parental-sparing in EMC cells (`fusion-junction-aso-paper.md` §4) — and a fusion-dependence readout |
| improved **perturbation / DepMap-transfer** models | re-test synthetic-lethal / nominate new EMC dependencies |
| any direct **chemical/biological matter against NR4A3** or the fusion | fold into the relevant route memo immediately |

The **delivery** rows are load-bearing: the ASO/siRNA route is gated by tumour delivery, which
we cannot solve in-silico today. There are **two distinct ways this unblocks**, so there are two
delivery rows:
1. **An in-silico delivery *predictor*** (biodistribution / endosomal escape / PBPK / ML
   tumour-penetration) → the proposed B7-H3-AOC/junction-siRNA design (see
   `manuscripts/emc-treatment-roadmap.md` → ASO "Delivery strategy") becomes computationally
   *testable*, moving the route off "delivery-limited" **in-silico**.
2. **A delivery *technology/candidate*** — an AOC/conjugate, tumour-penetrating peptide, or
   ligand-targeted LNP that actually reaches non-hepatic solid tumours, or a characterised
   EMC-enriched surface antigen to serve as the targeting arm → lets us **name a concrete delivery
   candidate**, moving the route off "delivery-limited" **in reality**. This is the more important
   of the two: the honest bottleneck is not "we can't simulate delivery," it is "no validated way
   to deliver an oligo to an EMC tumour exists yet." A single characterised EMC surface antigen or a
   working soft-tissue-sarcoma AOC would change the route's standing more than any predictor.

## Watched topics (kept in sync with `scripts/method-watch.mjs`)
- virtual-cell / perturbation prediction (scGPT / Geneformer / State / Arc Virtual Cell)
- AF3-class structure & ternary complex (AlphaFold3 / Boltz / Chai / RoseTTAFold)
- de-novo selective small-molecule / binder design (RFdiffusion / ProteinMPNN / diffusion SBDD)
- cryptic-pocket / dynamics-based druggability (PocketMiner, metadynamics)
- **in-silico oligo/nanoparticle tumour-delivery prediction** (AOC, siRNA delivery, LNP,
  endosomal escape, tumour penetration — ML / PBPK / computational)
- **oligo tumour-delivery TECHNOLOGY / candidate** (AOC / antibody-oligonucleotide conjugate,
  tumour-penetrating peptide, ligand-targeted LNP for non-hepatic solid tumours; EMC-enriched
  surface antigen for a targeting arm) — the watch for a real *way to do delivery*, not a predictor
- **ASO/gapmer off-target & RNase-H cleavage prediction** (ASO-paper next step: retire the
  gap-mismatch heuristic — §3a-quater)
- **ASO/siRNA design, efficacy & target-accessibility prediction** (ASO-paper next step:
  potency ranking + better accessibility than the local-fold proxy — §3a-bis iii)
- **patient-derived EMC / FET-fusion-sarcoma functional models** (ASO-paper next step: unblocks
  the decisive knockdown + parental-sparing experiment — §4)
- NR4A3 / EWSR1::NR4A3 direct EMC advances

> **ASO-paper coverage.** The last three rows above (plus the delivery row) are the
> fusion-junction ASO paper's specific next-step gates, mirroring how the degrader paper's
> gates (ternary modelling, warhead design, cryptic-pocket) are watched. Each maps to a
> concrete in-paper action so a digest "🆕" can be triaged straight to a section to update.

*Design principle (from `emc-treatment-strategy.md` Q3): keep this a periodic digest + this
table. Do not over-engineer a "capability detector"; pipelines are kept modular so a new
model swaps in cheaply.*

## Open follow-ups from digests (triage log)
Hits that crossed (or are warming) a trigger. A new session should action or clear these.

- **[2026-07-03] EMC-line real-data probe — new lines NOT public; GSE4303 tumour microarray IS.** A probe
  (`modalities/emc_line_data_probe.py` → `emc-line-data-probe.json`) for real-EMC surface/expression data found:
  (1) the two new patient-derived lines **have not deposited transcriptomes** — USZ-EMC [Bangerter 2022/2023] is
  "available on request", NCC-EMC1-C1 [Iwata 2025] is paywalled (abstract has no accession); the USZ OA text
  mentions **EGFR/KIT** (unverified as surface IHC). (2) A public **real-EMC *tumour* microarray, `GSE4303`**
  ("Gene expression profile of EMC"; Subramanian-type), plus scattered EMC tumour samples, DOES exist. **Action
  options (open):** (a) re-point/ cross-check the surfaceome scan against `GSE4303` — real EMC *tumour*, but old
  microarray, bulk-tumour stromal dilution, small n, possibly two-colour ratio data (may not give absolute
  surface-antigen levels — verify platform first); (b) **obtain the USZ/NCC line data by contacting the authors**
  (better data, but a human/wet-lab-adjacent action, not in-silico); (c) leave the DepMap surrogate as the
  published basis and cite `GSE4303`/line-existence as the upgrade path. **Decision (trimcrae, 2026-07-03): DO
  BOTH (a)+(b).** (a) built + run: `modalities/emc_gse4303_crosscheck.py` → `emc-gse4303-crosscheck.json` —
  **outcome: GSE4303 is UNUSABLE** (two-colour cDNA-clone array; log-ratios not absolute expression; probes
  lack gene symbols → 0 shortlist genes resolved; the platform gate correctly flagged it). Public-data route
  exhausted → author-held line data is the only real unlock. **A surface-antigen scaffold paper was spun out**
  ([`manuscripts/emc-surface-target-landscape.md`](manuscripts/emc-surface-target-landscape.md), gated on that
  data). (b) queued: the
  ASO paper §4 now names the **USZ (Zurich)** and **NCC (Japan)** groups as recipients, with the
  delivery-directed ask for their EMC lines' surface immunophenotype/RNA-seq (preprint-stage outreach).
  Status: **actioned.**

- **[2026-07-03] Delivery watch split into predictor + technology/candidate (trimcrae ask).** The
  ASO route's dominant gate is tumour delivery. The watch now has **two** delivery rows/topics: (1)
  an in-silico delivery *predictor* (makes the AOC/siRNA design computationally testable), and (2) a
  delivery *technology/candidate* — an AOC, tumour-penetrating peptide, or ligand-targeted LNP for
  non-hepatic solid tumours, or a **characterised EMC-enriched surface antigen** (the AOC's targeting
  arm). Row (2) is the one most likely to actually move the route, because the real bottleneck is the
  absence of a delivery *route*, not the absence of a *simulator*. Status: **watching** (no hits yet).
  Companion GPU-experiment to-do (RNase-H1 cleavage-discrimination MD) is tracked in the ASO paper §9
  and IDEAS.md — that firms up *specificity*; it does **not** touch delivery.

- **[2026-06-26] ASO-paper next-step gates added to the watch.** The fusion-junction ASO paper
  now has its own watched capabilities (three new literature topics in `scripts/method-watch.mjs`
  + trigger-table rows above): (1) ASO off-target / RNase-H cleavage prediction → retire the
  §3a-quater gap-mismatch heuristic; (2) ASO/siRNA efficacy & accessibility prediction → re-rank
  designs and replace the §3a-bis(iii) local-fold proxy; (3) patient-derived EMC / FET-fusion-sarcoma
  models → unblock the §4 decisive experiment. Status: **watching** (no hits triaged yet — re-check on
  the next monthly digest). Delivery (the route's dominant gate) was already watched.

- **[2026-06-24] AF3-class ternary modelling is now usable** (tool watch: AlphaFold3 v3.0.3,
  Boltz v2.2.1, Protenix v2.0.0; + a wave of fresh PROTAC-degrader papers). This crosses the
  *"open AF3-class ternary-complex prediction"* trigger → **model the NR4A3–PROTAC–E3 ternary
  complex** (degradability geometry / accessible-lysine check) with Boltz/Protenix. Status:
  **pipeline BUILT, awaiting GPU** — `nr4a3_ternary.py` (CPU prep + CRBN+lenalidomide positive
  control, validated in modalities-run CI) + `nr4a3_ternary_sagemaker.py` + `boltz_src/entry.py` +
  `gpu-ternary-aws.yml` (dispatch-only). Runs the moment AWS GPU access lands; the real ternary
  completes when a warhead SMILES exists (degrader experiment #2). See degrader spec point 3.
- **[2026-06-24] Degrader precedent in a sibling FET-fusion sarcoma — VERIFY BEFORE CITING.**
  Digest title only: *"Discovery and characterization of YSA64, a RBM39 degrader with in vivo
  efficacy and potent cellular activity in pediatric Ewing sarcoma A673"* (Europe PMC MED/42085934,
  2026-05). Relevance: shows degrader-modality efficacy in an EWS-fusion sarcoma — **but it targets
  the RBM39 dependency, not the fusion itself**, so it supports *"degraders deliver in FET-fusion
  sarcoma"*, NOT *"the fusion was degraded."* Action: fetch + read (CI `fetch-literature.yml`),
  confirm claims, then cite in the degrader spec/roadmap with that precise framing. Status: **open,
  unverified** (do not assert in a manuscript until read).
- **[2026-06-24] Virtual-cell target discovery warming up** — *"Discovery of candidate therapeutic
  targets with Geneformer"* (MED/42026145, 2026-04). Not yet a held-out-knockdown predictor, but the
  capability behind the EMC fusion-dependence trigger is maturing; keep watching. Status: **watch**.
