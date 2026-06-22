# Outline — the EMC treatment-strategy paper (the #1 deliverable)

> **DRAFT WRITTEN:** a full first draft now exists at
> [`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md). This outline is retained as the
> planning scaffold / figure + claims checklist; edit the draft directly going forward.

**Status:** skeleton for review (reshape freely). This is the publish-to-convince artifact the repo
exists to produce: a rigorous, honest map of *what could drive an EMC treatment forward*, built
entirely from the tracker (`emc-treatment-strategy.md`) and the in-silico evidence we generated. No
wet lab; every claim is sourced or computed, with explicit kill-criteria.

## Working title (options)
1. *Computational triage of treatment routes for EWSR1::NR4A3 extraskeletal myxoid chondrosarcoma:
   a prioritized, falsifiable roadmap.*
2. *No wet lab, no excuses: an in-silico decision framework for advancing treatment of an
   ultra-rare fusion sarcoma (EMC).*

## Thesis (one sentence)
For an ultra-rare fusion-driven sarcoma with no models and no commercial pull, the rate-limiter is
not ideas but **prioritization and evidence** — and a disciplined in-silico program can rank the
routes, generate new supporting evidence, and hand testable, de-risked hypotheses to groups who can
run them.

## Audience / venue
Sarcoma & rare-cancer translational researchers; computational-oncology methods readers. Venue
candidates: a rare-cancer or sarcoma journal, or a computational-oncology/methods venue. Also a
preprint for reach (the point is to mobilise testers).

## Sections
1. **Background.** EMC = near-universal EWSR1::NR4A3 fusion; an undruggable transcription-factor
   driver in a cold, ultra-rare tumour. Why the obvious routes stall (no models, no market,
   untrialable). Framing: the goal is to *push treatment forward*, and an untested-but-grounded
   mechanism is itself a contribution.
2. **Methods (reproducible, no wet lab).** AF2/AFDB + fpocket structure; MHCflurry/MHCnuggets;
   AFND coverage; **DepMap surrogate mining** (dependency, fusion-addiction proxy, target
   expression); literature triage. All scripts in `research/modalities/`; all results as JSON.
3. **Results — the prioritized portfolio** (the core; from `emc-treatment-strategy.md`):
   - Tier-1 repurposing with EMC evidence: TKI+ICI (ImmunoSarc responder), trabectedin (fusion-TF
     MoA), carfilzomib+anthracycline (ex-vivo EMC hit).
   - The driver-directed bet: **NR4A3 degrader** — mechanism, the warhead starting points, and the
     **in-silico fusion-addiction support (FLI1-in-Ewing −0.93/74%)**.
   - Surface modalities: **B7-H3** (surrogate 99% of sarcoma lines) → ADC/CAR-T; the surfaceome idea.
   - Antigen-directed: **PRAME** the best CTA (myxoid/synovial-high); MAGE-A4/NY-ESO-1 out.
   - Down-weighted with data/logic: synthetic-lethal/BRD9 (DepMap-negative), fusion-junction vaccine
     (economics + immunogenicity), TCR-T port (CTA-low).
4. **What would prove or kill each** (the falsifiable core — the reason a reader can act): per-route
   decisive experiment + kill-criteria (from the capstone). This is what makes it publish-to-convince.
5. **An in-silico program others can extend.** The NR4A3-degrader warhead design spec; public-data
   expression mining; preparing for virtual-cell/perturbation models. Invite collaboration.
6. **Limitations.** Surrogate (no EMC line); cell-line CTA silencing / stromal-FAP under-rep; AF2
   single static model; predictions not validation.

## Figures (all already generated or one step away)
- F1: EMC fusion architecture + AF2 disorder/pocket map — **GENERATED**:
  `figures/fusion-architecture.svg` (via `figures/fusion_architecture_figure.py`).
- F2: the prioritized-portfolio tier chart — **GENERATED**: `figures/portfolio.svg`
  (regenerate via `figures/portfolio_figure.py`).
- F3: DepMap fusion-addiction proxy — FLI1-in-Ewing vs context (`depmap-sarcoma-dependency.*`).
- F4: candidate-target expression in sarcoma (`depmap-target-expression.png`).
- F5: HLA coverage curve, if the vaccine angle is kept as a contrast (`coverage-curve.png`, CI).

## Key claims → support (audit)
| Claim | Support | Kill-criterion |
|---|---|---|
| EMC driver is undruggable by occupancy | AF2+fpocket (0.495, sub-threshold) | a cryptic-pocket / holo structure |
| EMC likely fusion-addicted | FLI1-in-Ewing −0.93/74% (analogy) | dTAG in EMC cells shows no death |
| Degradation is the right modality | NOR-1 activity ∝ expression; NR4A1 PROTAC precedent | no selective NR4A3 warhead achievable |
| B7-H3 is a viable surface target | 99% sarcoma-line expression + 97% pan-STS IHC | EMC-specific B7-H3-negative |
| PRAME > MAGE-A4/NY-ESO-1 for EMC | DepMap CTA expression (myxoid/synovial-high) | primary-EMC PRAME-negative |
| Synthetic-lethal/BRD9 not selective | DepMap (BRD9 not sarcoma-selective, not in Ewing) | a real EMC CRISPR screen disagrees |

## Immediate drafting next steps
- Convert the tier chart (F2) + claims table into final form.
- Pull the exact ImmunoSarc / trabectedin / Bangerter citations into a reference list (verify-refs).
- Decide scope: single comprehensive roadmap paper, or split (a degrader-focused paper + a
  portfolio paper). Recommendation: **one roadmap paper first** (mobilises the most), degrader
  design as a focused follow-on once the warhead docking is run.
