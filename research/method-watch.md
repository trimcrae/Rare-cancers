# Method-watch — in-silico capabilities we are waiting on

**Purpose.** This program's bottleneck is *methods*, not ideas: several routes unlock the
moment a specific in-silico capability becomes usable. This file is the **watch config +
trigger table** (what to look for, and what to do when it appears). The periodic search
itself is automated — `scripts/method-watch.mjs`, run monthly by
`.github/workflows/method-watch.yml` — which emits a dated **digest**.

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
| **in-silico oligonucleotide/nanoparticle tumour-delivery** predictor (biodistribution / endosomal escape / PBPK / ML tumour-penetration) | score the **B7-H3-targeted junction-siRNA / AOC** delivery in-silico and **re-grade the ASO route feasibility** (delivery is the route's gate) |
| calibrated **ASO off-target / RNase-H cleavage-activity** predictor | **retire the conservative "gap-mismatch ⇒ non-cleaving" heuristic** in the junction-ASO specificity screen (`fusion-junction-aso-paper.md` §3a-quater) and re-grade predicted specificity with a calibrated model |
| improved **ASO/siRNA efficacy + target-site-accessibility** predictor | **re-rank the junction designs for potency** and replace the local-fold accessibility proxy (`fusion-junction-aso-paper.md` §3a-bis iii) |
| new **patient-derived EMC / FET-fusion-sarcoma model** (cell line / organoid / PDX) | **enables the decisive wet-lab experiment** — junction-ASO knockdown + parental-sparing in EMC cells (`fusion-junction-aso-paper.md` §4) — and a fusion-dependence readout |
| improved **perturbation / DepMap-transfer** models | re-test synthetic-lethal / nominate new EMC dependencies |
| any direct **chemical/biological matter against NR4A3** or the fusion | fold into the relevant route memo immediately |

The **delivery** row is the newest watch: the ASO/siRNA route is gated by tumour delivery,
which we cannot solve in-silico today — but the moment a usable delivery/biodistribution
*predictor* exists, the proposed B7-H3-AOC/junction-siRNA design (see
`manuscripts/emc-treatment-roadmap.md` → ASO "Delivery strategy") becomes computationally
testable, which would move the route off "delivery-limited."

## Watched topics (kept in sync with `scripts/method-watch.mjs`)
- virtual-cell / perturbation prediction (scGPT / Geneformer / State / Arc Virtual Cell)
- AF3-class structure & ternary complex (AlphaFold3 / Boltz / Chai / RoseTTAFold)
- de-novo selective small-molecule / binder design (RFdiffusion / ProteinMPNN / diffusion SBDD)
- cryptic-pocket / dynamics-based druggability (PocketMiner, metadynamics)
- **in-silico oligo/nanoparticle tumour-delivery prediction** (AOC, siRNA delivery, LNP,
  endosomal escape, tumour penetration — ML / PBPK / computational)
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
