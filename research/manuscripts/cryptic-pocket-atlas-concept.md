# Concept memo — a cheap cryptic-pocket *druggability* atlas for neglected targets (AlphaFlow + fpocket)

**Status:** concept / pre-proposal. **Priority:** HIGH — the designated next major program *after* the
NR4A3 degrader preprint posts (trimcrae, 2026-07-05). **Not now:** strictly post-degrader-paper; this is the
classic scope-expansion that quietly eats the months meant for the EMC lead. Scope it now, build it then.

**One-line pitch.** Generate conformational ensembles *cheaply* with an AlphaFold-class generative model
(AlphaFlow / BioEmu), run fpocket over the frames, and publish the first **structurally-explicit,
druggability-scored catalogue of cryptic pockets on neglected / "undruggable" human disease targets** —
the NR4A3 pipeline, generalized, with NR4A3 as the worked exemplar.

---

## 1. The gap (why this doesn't already exist)
Honest prior-art positioning — the novelty is narrow and specific, not "nobody found a cryptic pocket before":

- **Predictors** (PocketMiner [Meller, *Nat Commun* 2023]; CryptoSite [Cimermancic, *JMB* 2016]) tell you
  *where* a cryptic pocket may form, from one static structure. They give **no opened geometry, no
  druggability, no design-ready cavity.** (We ran PocketMiner on NR4A3 as a cross-check — it corroborates the
  *site*, nothing downstream.)
- **Static-pocket databases** (DoGSite, CavityPlus, proteome-wide fpocket scans) miss cryptic pockets **by
  construction** — they score the single frozen conformation, which is exactly where a cryptic pocket is closed.
- **The one deep-MD cryptic-pocket *campaign* at scale** (Bowman lab / Folding@home) covered the **SARS-CoV-2
  proteome**, with a distributed-compute army — **not** curated human disease targets, and **not** a
  druggability-scored resource.
- **Cryptic-pocket benchmarks** (CryptoSite ~90 sites; larger PDB-mined sets, e.g. CryptoBench, 2024) label
  pocket **existence** and are **heavily biased toward already-drugged, well-studied proteins** (a protein is in
  the set *because* someone co-crystallized it with a ligand) — the opposite of the neglected targets we care about.

**The unoccupied niche:** a *druggability-scored*, structurally-explicit cryptic-pocket resource for the
**neglected / undruggable / Tdark** targets that carry no ligand-bound structures. That does not appear to exist.

## 2. Why now (the economics just changed)
The reason it doesn't exist is the **compute wall**: opening cryptic pockets needs conformational sampling, and
MD/metadynamics costs **~GPU-days per protein** (NR4A3 alone was days of metadynamics). A proteome is GPU-years —
impossible solo. **Generative ensemble models collapse the sampling cost by 3–4 orders of magnitude:**
- **AlphaFlow** (Jing, Berger, Jaakkola; **ICML 2024**; arXiv 2402.04845; code `bjing2016/alphaflow`) —
  fine-tunes AlphaFold2/ESMFold with flow-matching to emit a *distribution* of structures. ~seconds–minutes/protein.
- **BioEmu** (Microsoft; **Science 2025**) — scalable emulation of equilibrium ensembles.

Credibility caveat (report honestly): these are **credible research methods, not settled tools** — AlphaFlow is
one of several ensemble generators and *reuses AlphaFold itself*; it is **not** validated to AlphaFold's tier,
and whether it captures **functionally-relevant rare motions (cryptic-pocket opening)** vs generic flexibility
is an **open question**. That question is the make-or-break (§4).

## 3. The method — a funnel (cheap-wide → expensive-narrow), and where each tool sits
| Layer | What it does | Who does it | Cost |
|---|---|---|---|
| **0. Pre-screen** *(the funnel's mouth — trimcrae, 2026-07-05)* | rank the whole proteome by cryptic-pocket **propensity** so the expensive sampling only runs on proteins that plausibly *have* a cryptic pocket | **PocketMiner** (fast, single static structure, CPU) | ~free |
| **1. Sampling** | many conformations per (pre-screened) protein | **AlphaFlow / BioEmu** (replaces MD) | the only real GPU cost |
| **2. Pocket + druggability** | scan each frame → pockets, fpocket druggability, cryptic Δ | **fpocket over frames** | ~free (CPU) |
| **3. The atlas** | run 0–2 across curated neglected targets; label, validate, aggregate, publish w/ calibrated confidence | a **dataset + pipeline** | curation effort |
| **4. Predictor** *(optional 2nd paper)* | train a fast model on layer-3 labels → skip sampling for new targets | an **ML model** | cheap on top |

**The key funnel insight (Layer 0):** PocketMiner is a cheap, wide *predictor* and AlphaFlow is an expensive,
narrow *generator* — so **use PocketMiner as the triage filter that decides which proteins get AlphaFlow'd.**
Run PocketMiner across the whole proteome for ~free, rank by cryptic-pocket propensity, and spend the GPU budget
only on the top-flagged fraction. This is the "cheap-triage-before-the-expensive-step" pattern (same discipline
as the degrader-atlas FEP funnel), and it directly shrinks the one real cost (§5). It is **not circular** —
PocketMiner *selects*, AlphaFlow+fpocket *independently verify and score* (different methods, different signal).
**Honest coverage caveat (the "no silent caps" rule):** the pre-screen has false negatives — a protein
PocketMiner misses never gets sampled. Fine for a *focused* atlas; for a *complete* proteome atlas, **log the
filtered-out fraction** and periodically spot-check below the threshold, rather than reporting the filtered set
as "the proteome."

**AlphaFlow occupies layer 1 only.** It hands you a haystack of structures; it does *not* find or score pockets.
The signal we want — "a *druggable cryptic pocket* is here, with confidence X" — is layers 2–4, gated by 0.

**Auto-labeling recipe (no manual curation):** for each protein, `Δdruggability = max(fpocket over ensemble) −
fpocket(static)`. A large jump = a cryptic druggable pocket opened. This is the training label for layer 4, and
the ranking signal for the atlas.

## 4. The make-or-break premise → Phase 0 gate (do this first, it's cheap)
Everything rests on one unverified assumption: **does AlphaFlow actually sample the cryptic-*open*
conformations, or only generic wiggling?** If it under-samples the rare functional openings, cheap sampling of
the *wrong* states buys nothing.

**Phase 0 — the decisive, cheap experiment (~tens of $ of GPU):** run AlphaFlow on the **known cryptic-pocket
set** (CryptoSite ~90 proteins, and/or a CryptoBench subset) **+ NR4A3**, fpocket the ensembles, and measure
**recall of the *known* cryptic pockets**. Outcomes, both publishable:
- **Pass** → we have a validated cheap route; proceed to the focused atlas. Bonus: NR4A3 gets a *third*
  independent druggability cross-check (AlphaFlow reaching the same opened Pocket-5, alongside our metadynamics
  and PocketMiner).
- **Fail** → we've shown generative ensembles miss cryptic pockets and MD is still required — a result the field
  wants — and we fall back to targeted MD for the hard cases. No atlas at proteome scale, but the negative is real.

*(This Phase 0 gate is cheap enough to pull forward even before the degrader paper if desired, since it doubles
as an NR4A3 cross-check — but the full atlas stays post-degrader.)*

## 5. Feasibility / compute budget (order-of-magnitude)
- **Human proteome:** ~20,500 proteins (one AlphaFold structure each; already downloadable). Druggable genome
  ~3,000–4,500; Tdark ~5,000.
- **fpocket:** ~seconds–minute/structure, CPU. Static fpocket on *all* 20,500 ≈ tens of CPU-hours ≈ a few $
  (but static misses cryptic pockets — that's the point of layer 1).
- **AlphaFlow ensembles** (~50 samples/protein, ~15 s each):
  - full proteome ≈ **~4,000 GPU-hours ≈ low-thousands–~$10k** on spot;
  - **focused set (1,000–3,000 neglected targets) ≈ hundreds of GPU-hours ≈ a few hundred $.** ← the feasible entry point.
- **MD equivalent:** GPU-*years* (~$millions). So AlphaFlow is the enabling delta.
- **The PocketMiner pre-screen (§3, Layer 0) shrinks even the AlphaFlow bill:** run it proteome-wide for ~free,
  then sample only the top cryptic-prone fraction. If, say, ~10–20 % of proteins clear the threshold, the full
  "proteome" AlphaFlow run drops from ~4,000 GPU-hours to **~hundreds** — i.e. the *whole-proteome* atlas lands
  near the earlier *focused-set* budget. (Trade-off: false negatives below the threshold — log them, §3.)

## 6. Staged plan
- **Phase 0 — validate the sampler** (the gate, §4). Cheap. Gates everything below.
- **Phase 1 — focused atlas** on a curated **neglected target class** (fusion-TF / orphan-NR rare-cancer
  drivers; NR4A3 the worked exemplar). Use the **PocketMiner pre-screen (Layer 0)** to rank the candidate class
  by cryptic-pocket propensity and pick where to spend AlphaFlow. Dozens of targets, deep each, every entry a
  genuine lead. Deliverable: a *Scientific Data* / NAR-Database-issue resource paper.
- **Phase 2 — the predictor** (data-first, model-second): train a fast structure→druggability model on the
  atlas's auto-labels; differentiated from PocketMiner precisely by carrying the **druggability + opened-geometry**
  axis. Second paper.
- **Phase 3 — proteome-scale** (conditional on Phase 0 passing convincingly + budget): the full ~20k atlas.

## 7. Target-selection rubric (or it's garbage-in)
Each atlas entry must clear: (a) a **defined oncogenic/disease driver**; (b) **AF-modelable** structure; (c) a
**plausible ligandable/cryptic** pocket (borderline-static is the sweet spot — NR4A3-like); (d) a **real
selectivity or undruggability need**; (e) **no existing potent chemical matter** (else low value). Neglected /
Tdark / rare-disease bias is the point.

## 8. Honest risks & medical-integrity guardrails
- **Every entry is an unvalidated in-silico *hypothesis* with calibrated confidence + provenance**, credible
  only because the pipeline demonstrably re-finds held-out *known* cryptic sites (Phase 0). Ruthless labeling;
  publish **negative results** too (a computed pocket that *doesn't* open is signal, not omission).
- **Do not let it dilute the EMC #1 priority.** Post-degrader-preprint track only.
- The integrity discipline gets *more* important as this goes public — an unvalidated druggable-pocket claim on a
  disease target is easily misread as a validated lead.

## 9. Relationship to the rest of the portfolio
- Upstream of the **computational degrader atlas** (`IDEAS.md` Platform/vision #1–3): find the druggable pockets
  (this) → design selective degraders into them (that).
- **NR4A3 is the worked exemplar** that earns the pipeline its credibility — the degrader paper is the proof the
  method finds a real, actionable cryptic pocket.
- Watched enablers: `method-watch.md` cheap-ensemble-generator trigger (BioEmu / AlphaFlow / subsampled-MSA AF).

## 10. Pointers
- AlphaFlow — Jing, Berger, Jaakkola, *ICML 2024* (arXiv 2402.04845); code `github.com/bjing2016/alphaflow`.
- BioEmu — Microsoft Research, *Science 2025* (scalable equilibrium-ensemble emulation).
- PocketMiner — Meller et al., *Nat Commun* 14:1177 (2023); our NR4A3 run: `modalities/nr4a3-pocketminer-result.json`.
- CryptoSite — Cimermancic et al., *JMB* (2016); larger PDB-mined benchmarks (CryptoBench, 2024).
- fpocket — Le Guilloux et al., *BMC Bioinformatics* (2009). Our NR4A3 cryptic-pocket pipeline:
  `modalities/nr4a3_release_druggable.py`, `metad-methods-appendix.md`, `nr4a3-degrader-paper.md` §2.1–2.2.
