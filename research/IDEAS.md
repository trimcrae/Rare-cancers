# Parked ideas / future-work backlog

Ideas worth doing later but deliberately *not* started yet. Each entry: the idea, why
it matters, rough effort/risk, open questions, and what to check before committing.
Add to this rather than losing ideas in chat. Newest at top.

---

## EMC treatment-discovery — route status board (updated 2026-06-21)

**Read `research/manuscripts/degrader-vs-synthetic-lethal.md` first** — it is the live
head-to-head. This board is the one-screen summary of what's shelved vs. active and the next
step for each. The goal pivoted away from the vaccine/coverage work (rigorous but unlikely to
*yield a treatment*; economics favour a tumour-agnostic platform we don't control) toward routes
that could actually drug or immuno-target EWSR1::NR4A3 EMC.

| Route | Status | Next step (★ = computational, no wet lab) |
|---|---|---|
| **TCR-T / engineered T cells vs a cancer-testis antigen (port the synovial-sarcoma win)** | **TOP NEAR-TERM LEAD — but gated by an unconfirmed fact.** afami-cel (MAGE-A4, HLA-A\*02) is FDA-approved (2024) for synovial sarcoma; letetresgene (NY-ESO-1) trials in synovial/myxoid-RC liposarcoma. The *product already exists*. Sidesteps the weak fusion-junction immunogenicity. | ★ **Gating check:** does EMC express MAGE-A4 / PRAME / NY-ESO-1 at a targetable frequency? (Lit hint: NY-ESO-1 is used to tell myxoid liposarcoma *apart from* EMC → EMC likely NY-ESO-1–low; MAGE-A4/PRAME in EMC under-characterised.) ★ Cross with HLA-A\*02 prevalence (our `hla_coverage.py` work feeds straight into eligibility). If antigen+, an approved/clinical TCR-T may apply to a subset. |
| **Degrader — NR4A3-LBD PROTAC** | **LEADING small-molecule route** (after synth-lethal transfer prior went negative). Fusion retains the ordered NR4A3 LBD with the protein's only real pocket (fpocket 0.495); first approved PROTAC (vepdegestrant, 2025) degrades a nuclear receptor. | ★ Map NR4A-ligand contacts onto fpocket Pocket-5 (406–534); ★ CRBN/VHL expression in EMC. **AI accelerator:** de-novo binder design (RFdiffusion/AF-based) for the NR4A3-LBD warhead the route currently lacks. Then wet-lab dTAG fusion-addiction test. |
| **ImmTAC / soluble-TCR bispecific (off-the-shelf)** | Speculative-but-real. Tebentafusp (gp100/HLA-A\*02) is approved (uveal melanoma); same platform could target a MAGE-A4/NY-ESO-1 peptide-HLA without cell manufacturing. | ★ Same antigen + HLA gating as TCR-T; then a platform/partner question. |
| **Synthetic-lethal (BRD9/ncBAF via EWSR1-prion→BAF)** | **DOWNGRADED.** DepMap 24Q4 transfer prior **negative**: BRD9 not a sarcoma dependency, not even in Ewing; BET/CDK pan-essential, no selectivity window (`depmap-sarcoma-dependency.json`). | No cheap shortcut; needs a **de-novo CRISPR screen in patient-derived EMC lines**. Don't spend a wet-lab slot on a transfer-justified BRD9 test. |
| **AF3 on a druggable interface** | Deferred; method not strategy. | ★ Only once the degrader route picks a ternary/PPI interface (fusion↔CBP/p300 or fusion↔E3). |
| **Fusion-junction ASO** (`novel-modalities.md` §3.2) | Designed; 5 gapmers exist. | GC-rich (75–81%) + tumour delivery unsolved. |
| **Vaccine / HLA-coverage paper** | **PARKED** (done, not a treatment path; self-adjacent junction in a cold tumour = weak immunogen). `hla-coverage-emc.md`. | Never built: (a) reality filters (distance-to-self/tolerance + anchor-vs-TCR position); (b) breakpoint-recurrence quant. `coverage_scan.py` §3.3 numbers + `coverage-curve.png` await a `modalities-cache` snapshot. **Reusable:** its HLA-A\*02 coverage feeds TCR-T eligibility above. |

**Shared rate-limiter for every route:** EMC is nearly absent from public functional-genomics data
(only new patient-derived lines: NCC-EMC1-C1 2025; USZ-EMC). The decisive experiment of *every*
route needs those lines — that bottleneck, not idea-generation, is the real constraint.

**Speculative / forward-looking (AI-era), kept honest:** de-novo binder/TCR design (diffusion
models) to manufacture the warhead or TCR a route lacks; AI structure (AF3) for ternary/PPI
interfaces; combination therapy (anti-angiogenic TKI — EMC's one real clinical signal — + IO).
Lower-credibility for *near* term: CAR-T (no good EMC surface antigen), ADCs (ditto), "nanobots"
(not a near-term clinical reality). Don't over-invest in these until a concrete target is in hand.

---

## Modernize & help maintain the TxGNN repo (upstream contribution)

**Status:** parked / idea only (filed 2026-06-20).
**Origin:** while running the real TxGNN model for EMC predictions (roadmap #3, see
`hypotheses/METHODOLOGY.md §7` and `txgnn_predict.py` / `.github/workflows/txgnn-run.yml`)
we hit the exact dependency-rot wall that limits TxGNN's reach.

### The idea
Contribute to [`mims-harvard/TxGNN`](https://github.com/mims-harvard/TxGNN): port the
2023-era stack to a modern one and/or refresh the knowledge graph, so the model is
runnable out-of-the-box in 2026+.

### Why it could be high-value
- **The dependency rot is a real, shared barrier.** TxGNN pins **DGL 0.5.2** + an old
  PyTorch; its `model.py` uses DGL 0.5.2 heterograph/message-passing APIs that broke in
  DGL 0.6→0.7→1.0→2.x. Anyone trying to run it today hits this (we did). A clean
  torch-2.x / DGL-2.x port would unblock many rare-disease researchers — high leverage
  for a small, well-scoped repo.
- **Public good aligned with this project's mission** (lower the information cost of
  repurposing for neglected diseases; see METHODOLOGY §7.4 economics).
- Candidate contributions, roughly in increasing effort:
  1. A **CPU-friendly, pinned, reproducible "run inference for one disease" recipe**
     (basically what we built in `txgnn_predict.py` + the workflow) — could be a docs PR
     or an `examples/` script. Lowest effort, immediately useful.
  2. **Dependency modernization** (torch 2.x + DGL 2.x) — non-trivial: rewrite the
     heterograph layers; the released weights are tied to the old DGL, so behavior must
     be re-validated (likely a retrain or careful weight port).
  3. **Refreshed knowledge graph** (newer PrimeKG / MONDO / DrugBank) — bigger, would
     change predictions, needs re-training and re-benchmarking.

### Effort / risk
- (1) is small and self-contained. (2) and (3) are real research-engineering projects
  (weeks), and a faithful port must preserve or transparently re-validate model behavior,
  or it's no longer "the published TxGNN."

### Open questions — check these BEFORE investing
- **Does the maintainer accept/merge PRs?** Check recent commit date, open/merged PR
  activity, issue responsiveness, and whether a `CONTRIBUTING` exists. As of this note the
  repo looks publication-frozen (README still pins DGL 0.5.2; PyPI `TxGNN` at 0.0.3), so
  confirm it isn't effectively archived before sinking effort. (Our GitHub tooling is
  scoped to `trimcrae/rare-cancers`, so this needs a manual look or a widened scope.)
- Is there an **official successor / maintained fork** already (e.g., a newer Zitnik-lab
  release, or PrimeKG v2 tooling) that's the better contribution target?
- Would a **lightweight standalone "txgnn-runner"** (our pinned wrapper, published
  separately) deliver most of the value (1) without needing upstream buy-in?

### Pointers
- Repo: https://github.com/mims-harvard/TxGNN · Explorer: http://txgnn.org
- Paper: Huang et al., *A foundation model for clinician-centered drug repurposing*,
  Nat Med 2024 (doi:10.1038/s41591-024-03233-x).
- KG on Harvard Dataverse: doi:10.7910/DVN/IXA7BM.
- Our working runner: `research/hypotheses/txgnn_predict.py` + `txgnn-run.yml`.
