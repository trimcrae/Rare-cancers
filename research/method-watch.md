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
- NR4A3 / EWSR1::NR4A3 direct EMC advances

*Design principle (from `emc-treatment-strategy.md` Q3): keep this a periodic digest + this
table. Do not over-engineer a "capability detector"; pipelines are kept modular so a new
model swaps in cheaply.*
