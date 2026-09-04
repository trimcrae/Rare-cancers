---
id: DOC-FIELD-SCAN-LOG
title: NR4A3-selective degrader — weekly field-scan log
level: —
kind: index
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `index` from its location under research/.
audience: [maintainers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
# NR4A3-selective degrader — weekly field-scan log

Dated summaries of new/relevant literature + methods for the in-silico NR4A3 program (EMC / EWSR1::NR4A3).
Produced by the weekly field-scan Routine (**Fri 8 AM ET**, `trig_01X5xHy1cmkLjkATEijZSNJf`), or manually when
that run fails. **Scope is broader than the degrader path**: also ASO delivery, immunotherapy/neoantigen, and any
new solid-tumor modality that could apply to a fusion-driven sarcoma. It ALSO carries a **Tooling &
operating-environment watch** (added 2026-07-14/15, trimcrae): (a) new releases/changelogs of our in-silico
software stack (OpenFE, OpenMM, openmmtools, gufe, OpenFF/NAGL, LOMAP/Kartograf, RDKit, Boltz — esp. bumps that
change defaults/accuracy, e.g. the OpenFE v1.7 time_per_iteration 1.0→2.5 ps change); (b) whether the cancer/bio-research RESTRICTION on
Fable (claude-fable-5) — and on any future frontier model at least as capable — is relaxed, so we could use a
top-tier model for this NR4A3/EMC bio work; (c) whether OpenAI Codex has gained phone-without-Remote-Desktop
control (a Claude-Code-style mobile control surface); (d) **compute-cost / GPU-market watch** — GPU-provider
price drops, new providers or free/academic-allocation offers, and new GPUs with better FLOPS/$ for our
OpenMM/OpenFE MD (compute $ is the program's only real cost; material changes auto-capture to
`research/compute/cheap-gpu-plan.md`). Each entry should highlight
the **delta vs the previous entry**. Sources are real search hits; novelty/dating flagged where unverified. No
fabricated papers.

---

## 2026-07-13 (Mon) — MANUAL catch-up (baseline entry; no prior to diff against)

> ⚠ The automated Routine fired at 8:03 AM ET but delivered no email and no commit; a 9:20 AM ET re-fire also
> failed. This entry was produced **by hand** and reflects the **current landscape**, not strictly the past 7
> days (arXiv IDs date items to 2025–2026). Routine has since been recreated hardened + broadened (see repo).

**This week's takeaway:** Quiet on NR4A/EMC biology, but three things matter: (1) **Boltz 2.1** is closed-source
but **API-accessible** — usable via their hosted API, not ruled out; (2) a cluster of **ternary-cooperativity
FEP** papers is direct prior art for our Track B method; and (3) on the **non-degrader routes**, fusion-sarcoma
**immunotherapy** hit a real milestone (Tecelra full approval) and a **bivalent fusion-TF "rewiring"** modality
(TCIP; EWSR1::FLI1) is worth adding to the board.

### 1) METHOD-WATCH (plan-relevant — top priority)
- **Boltz 2.1 → closed-source but API-ACCESSIBLE (June 2026).** Correction to last read: closed weights do **not**
  rule it out — it runs via the Boltz-hosted API (inference-only, cheap). For our **co-fold generator** role, open
  Boltz-1/-2 already suffice (we don't use the generator for affinity/ranking), so 2.1 isn't urgent.
  **Recommendation: if we ever want a fast affinity pre-filter, use the Boltz 2.1 API rather than self-hosting** —
  physics stays the ranker regardless (generator scores never enter S_d). https://rowansci.com/tools/boltz-2 ·
  https://www.biorxiv.org/content/10.1101/2025.06.14.659707v1
- **Independent Boltz-2 reliability eval (arXiv 2603.05532).** Strong binary classifier, weak *quantitative*
  ranking — reinforces "generator never ranks selectivity." https://arxiv.org/html/2603.05532v1
- **Ternary/glue cooperativity FEP prior art** — JCTC `5c00736` (induced-PPI + cooperative-solvation decomposition,
  https://pubs.acs.org/doi/10.1021/acs.jctc.5c00736) and JCTC `5c00064` (glue cooperativity vs experiment,
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12159975/). Cite + benchmark our ΔG_coop method against these.
- **More architecture-proposal generators for the breadth-first list:** IntFold (arXiv 2507.02025) and PROflow
  (arXiv 2405.06654) — evaluate alongside Boltz + DeepTernary, never as rankers.

### 2) NR4A / EMC
- No new NR4A3/EMC primary papers this week. **NR-V04** (JEM 2024) remains the central positive control
  (NR4A1-selective; spares NR4A2/3): https://rupress.org/jem/article/221/3/e20231519/276559/ . NR4A LBDs show no
  canonical open pocket (bulky hydrophobic fill) — consistent with our cryptic-pocket premise.

### 3) Degrader methodology (context)
- **"Targeted Protein Degradation in the Digital Era" review (ScienceDirect, 2026)** —
  https://www.sciencedirect.com/science/article/pii/S3050787126002015 . Standing ternary refs: JCIM 4c01227,
  JCIM 4c00426.

### 4) NON-DEGRADER ROUTES (fusion-selective alternatives — per the multi-route strategy)
- **★ Fusion-neoantigen immunotherapy — real milestone.** **Tecelra (afami-cel)** got **full FDA approval for
  synovial sarcoma** (expanded to age ≥12; updated Phase-2 at ASCO 2026) — the first engineered TCR-T for a
  fusion-driven sarcoma. Plus fusion-derived public-neoantigen TCRs: **SYT-SSX** (synovial) and **EWSR1-WT1**
  (DSRCT). **Why it matters:** strong external validation for our fusion-junction/lineage-antigen route; the
  EWSR1::NR4A3 junction is directly analogous — an EWSR1-fusion public-neoantigen TCR is a credible parallel
  modality. https://www.mskcc.org/news/immunotherapy-clinical-trial-shows-promise-for-treating-rare-sarcomas ·
  https://aacrjournals.org/cancerres/article/84/6_Supplement/6/738983 ·
  https://pmc.ncbi.nlm.nih.gov/articles/PMC11821884/ · https://ascopubs.org/doi/10.1200/EDBK_432234
- **★ NEW modality to add to the board — bivalent fusion-TF "rewiring" (TCIP).** "Rewiring the fusion oncoprotein
  **EWSR1::FLI1** in Ewing sarcoma with bivalent small molecules" + TCIP (Transcriptional Chemical-Induced
  Proximity) compounds that hijack tumor-specific fusion TFs. **Why it matters:** a small-molecule route that
  *co-opts* the EWSR1 fusion TF rather than degrading it — directly conceptually transferable to EWSR1::NR4A3.
  **ACTION: check against research/IDEAS.md — if not already a tracked route, add it as a candidate
  fusion-selective modality.** https://pmc.ncbi.nlm.nih.gov/articles/PMC12851799/
- **ASO delivery (the fusion-junction ASO route's one remaining gate).** Advances: imaging-assisted tumor-targeted
  ASO delivery (https://pmc.ncbi.nlm.nih.gov/articles/PMC11503958/), MOF-nanoparticle ASO delivery for anti-tumor
  immunity (https://pubmed.ncbi.nlm.nih.gov/41712689/), and **AZD8701** (FOXP3 ASO) in a Phase-I solid-tumor trial
  — clinical precedent for systemic ASO in solid tumors (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11995004/).
- **Fusion-targeting overview refs:** "Targeting fusion proteins in solid tumors" (Acta Pharm Sinica 2026,
  https://www.nature.com/articles/s41401-026-01817-6); "Targeting pediatric solid tumors in the era of RNA
  therapeutics" (https://www.sciencedirect.com/science/article/pii/S1040842824001495).

### Action items for the program
1. Add JCTC 5c00736 + 5c00064 + the TPD review to `method-watch.md` prior-art (Track B benchmark set).
2. Keep Boltz pinned to open weights for co-fold; note Boltz 2.1 **API** as the path if a fast affinity
   pre-filter is ever wanted.
3. **Check the TCIP / bivalent-fusion-TF-rewiring route against `research/IDEAS.md`; add if new.**
4. Log Tecelra/SYT-SSX/EWSR1-WT1 as external validation for the neoantigen route; note ASO-delivery advances
   against the fusion-junction ASO route's delivery gate.

*Caveat: produced manually; reflects current landscape, not strictly the past 7 days. Links are real search
hits; dating/novelty flagged where uncertain.*

---

## 2026-08-24 (Mon) — AUTOMATED weekly field-scan (delta vs 2026-07-13 — a six-week gap)

> ⚠ **This run's own checkout succeeded** (`git fetch origin main && git checkout main && git reset --hard
> origin/main` completed cleanly, HEAD landed on `main` with a clean tree) — the STOP-and-say-so condition in
> this Routine's prompt did not fire. This does not resolve the separately-documented failure of the
> claude.ai-UI Routine `trig_01X5xHy1cmkLjkATEijZSNJf` (`method-watch.md` → the 2026-08-24 note on its missing
> `sources` grant) — that is a different triggering mechanism and still needs trimcrae to recreate from the UI.
> It does mean *this* run had full repo read/write access throughout.

**This week's takeaway:** quiet on NR4A3 itself — no new primary paper, ligand, or structure — but real
movement on three other axes: **OpenMM 8.6.0** shipped native replica-exchange/expanded-ensemble sampling (a
genuine new axis for our RBFE/ΔG_coop legs), a first-in-kind **glutathionylation-activated molecular glue**
targeting **DCAF11** landed in *Nature* with a new systematic degrader-discovery platform, and a **fusion-
junction peptide vaccine** trial (DNAJB1-PRKACA, fibrolamellar carcinoma, NCT06789198) is now the closest
external precedent yet for the parked vaccine route. The gap since the last entry is six weeks, not one; item
dates are given so recency within that window is checkable, and the mechanical trigger-scan layer
(`method-watch-trigger-scan.md`, via `IDEAS.md`'s auto-capture section) already logged dozens of narrower hits
across 2026-08-03 through 2026-08-21 — this entry does not re-list those, only genuinely new items the
mechanical scan's fixed queries would not catch, plus the tooling/operating-environment watch it doesn't cover.

### 1) METHOD-WATCH (plan-relevant)
- **OpenMM 8.6.0 (2026-08-19) — native `ReplicaExchangeSampler` + `ExpandedEnsembleSampler`.** New multistate-
  sampling primitives for the warhead RBFE and physics-ensemble ΔG_coop legs — a new evidence axis, default-
  worth-evaluating per the breadth-first rule. https://github.com/openmm/openmm/releases/tag/8.6.0
- **Riepenhausen et al., "AI-Based Prediction of PROTAC- and Molecular Glue-Mediated Ternary Complexes: A
  Comparative Evaluation of AlphaFold 3 and Boltz-2," Archiv der Pharmazie, e70225.** Head-to-head AF3-vs-
  Boltz-2 benchmark on 40 resolved ternary complexes (25 PROTAC + 15 glue) — read before the next ternary
  rebuild; issue date not independently re-verified. https://onlinelibrary.wiley.com/doi/10.1002/ardp.70225
- **DegradeQuery (arXiv 2608.10595, 2026-08-11).** Counterfactual-tuple pretraining on unlabeled PROTAC-DB
  molecule–target–E3 records for degradation-activity prediction (AUROC 0.907 on PROTAC-8K). Candidate weak
  prioritization signal only — physics stays the ranker. https://arxiv.org/abs/2608.10595
- **No DeepTernary or FKSFold update found this period.**

### 2) NR4A / EMC
- **No new NR4A3-specific primary paper, ligand, structure, or trial found this period.** Genuinely quiet —
  not padded with older NR4A1/NR4A2 background.

### 3) Degrader methodology
- **★ DCAF11-dependent molecular glue activated by glutathionylation (Nature, 2026-08-05, Dana-Farber).**
  First-in-kind *metabolically activated* molecular glue (prodrug M12, switched on by GST-mediated
  glutathionylation in oxidative-stress-high cancer cells), found via a new systematic degrader-discovery
  platform that broadens usable E3 ligases beyond CRBN/VHL. New axis: conditional/context-dependent activation
  + a non-CRBN/VHL E3 route. https://www.nature.com/articles/s41586-026-10873-1 ·
  https://www.dana-farber.org/newsroom/news-releases/2026/dana-farber-investigators-develop-protein-degrader-discovery-platform-and-find-first-in-kind-metabolically-activated-molecular-glue-degrader
- (TriGlue, arXiv 2607.22143, is NOT new here — already captured by the mechanical trigger scan on 2026-08-03.)

### 4) NON-DEGRADER ROUTES
- **★ NCT06789198 (corrected identifier — the first-pass hit "NCT07430202" did not resolve and was dropped
  per CLAUDE.md §7) — "Peptide Vaccine for Fibrolamellar Hepatocellular Carcinoma Patients and Other Tumor
  Entities Carrying the Driver Fusion DNAJB1-PRKACA."** Structurally the closest external precedent yet for a
  fusion-breakpoint-directed vaccine reaching clinic. Whether this is the same registration already tracked
  elsewhere in this program as "FusionVAC22_01" or a distinct trial is unconfirmed this scan (WebFetch to
  clinicaltrials.gov is egress-blocked; identity confirmed only via WebSearch snippet, not a direct fetch) —
  verify directly before citing further. https://clinicaltrials.gov/study/NCT06789198
- **NCT07648069 "SarVac" (Sun Yat-sen Univ.) — neoantigen vaccine + tumor-specific-lymphocyte reinfusion,
  advanced/unresectable sarcoma.** Not fusion-specific, but a live personalized-vaccine-plus-adoptive-cell
  precedent in sarcoma. https://clinicaltrials.gov/study/NCT07648069
- **TAC-001 (Tallac Therapeutics) — AOC in Phase I/II, solid tumors.** CD22-targeting antibody + TLR9-agonist
  oligo payload. Not knockdown, not sarcoma-specific, but a real clinical AOC reaching solid tumors — a
  delivery-platform precedent for the ASO route's dominant gate. Identity not independently re-verified.
- **AOC design-principles reviews** (J Hematol Oncol; Gene Therapy, both 2026) — synthesize AOC architecture,
  flag endosomal escape as rate-limiting for extrahepatic delivery; framing only, no new data. Exact issue
  dates UNKNOWN (springer.com egress-blocked). https://link.springer.com/article/10.1186/s13045-026-01824-4 ·
  https://www.nature.com/articles/s41434-026-00621-5
- **In vivo mRNA-LNP CAR generation (preclinical, e.g. FAP-CAR platforms).** Systemic LNP reprograms host
  T/myeloid cells in situ, avoiding ex vivo manufacturing. Speculative for EMC — no EMC surface/stromal target
  is defined yet to hang it on. https://www.pnas.org/doi/10.1073/pnas.2509698123

### 5) Tooling & operating-environment watch
**(a) Library releases (OpenFE/OpenMM/openmmtools/gufe/OpenFF-toolkit/openff-nagl/LOMAP2/Kartograf/RDKit/
Boltz).** OpenMM 8.6.0 (2026-08-19, see §1). **OpenFF toolkit 0.19.0** (2026-08-12) and **RDKit 2026.03.5**
(2026-08-01, patch) landed in-window but their changelog specifics are UNKNOWN — docs sites were egress-
blocked this scan; follow up via a CI fetch before relying on either for a numeric change.
https://github.com/openforcefield/openff-toolkit/releases/tag/0.19.0 ·
https://github.com/rdkit/rdkit/releases/tag/Release_2026.03.5. OpenFE, gufe, openmmtools, Kartograf and
LOMAP2 had **no new release** this window. No new open-weight Boltz release; Boltz 2.1 stays closed/API-only
(already tracked).

**(b) Frontier-model access.** No change to report as a restriction — that framing is retired per the
2026-08-24 CLAUDE.md correction. **Claude Opus 5** (released 2026-07-24) remains the current top generally-
available tier for this bio work (same ASL-3 protections as Opus 4.8, CB-1 not CB-2; blocked Fable-5 biology
requests fall back to Opus 5). No newer/more-capable model found since 2026-07-13 that out-measures Opus 5 for
scientific/biology reasoning — xAI Grok 4.6 and Alibaba Qwen3.5-Max shipped in-window with no head-to-head
benchmark showing them ahead (treat as UNKNOWN, not inferior). https://www.anthropic.com/news/claude-opus-5

**(c) Phone-drivable coding agents.** No change this period. Codex-side additions since 2026-07-13 (read-only
chat sharing, synced pinned chats, an Apple Messages plugin) are minor and don't shift the Codex-mobile-vs-
Claude-mobile comparison.

**(d) Compute-cost / GPU-market.** No major price move on Vast.ai/RunPod/GCP/AWS spot pricing this period —
Vast.ai remains the cheapest marketplace floor. **RTX 5090** (~1,792 GB/s, ~1.8× the RTX 4090's bandwidth —
the axis that predicts ns/day for our memory-bandwidth-bound OpenMM PME MD) continues falling in cloud price
(median on-demand ~$0.46–0.56/hr, down ~23% y/y), but **no OpenMM/OpenFE $/ns benchmark exists for it yet** —
UNPRICEABLE for our workload until measured, not "cheap." Auto-captured to `compute/cheap-gpu-plan.md` for
human review. No new provider or free/academic credit program found.

### Action items for the program
1. Evaluate OpenMM 8.6.0's replica-exchange/expanded-ensemble sampler against the current RBFE/ΔG_coop driver.
2. Read the Riepenhausen AF3-vs-Boltz-2 ternary benchmark before the next ternary rebuild.
3. Verify NCT06789198 and NCT07648069 details directly (this scan's clinicaltrials.gov WebFetch access was
   egress-blocked) before citing either further in the vaccine-route context.
4. If a cheap RTX 5090 smoke-test $/ns measurement is ever warranted, it would settle whether it beats the
   4090 for our workload — not scheduled, just noted as measurable.
5. Fix `trig_01X5xHy1cmkLjkATEijZSNJf`'s missing repo `sources` grant remains outstanding and needs trimcrae
   (unchanged from the 2026-08-24 method-watch.md note — this run used a different mechanism with working
   access, so it does not close that item).

*Sources are real search hits from four parallel research passes (method-watch/tooling, NR4A/EMC + degrader
methodology, non-degrader routes, model/mobile-agent/GPU-market); several were egress-blocked mid-scan
(clinicaltrials.gov, springer.com, docs.openforcefield.org, rdkit.org) and are flagged UNKNOWN rather than
guessed. No fabricated papers, trials, releases, or prices.*

---

## 2026-08-28 (Fri) — AUTOMATED weekly field-scan (delta vs 2026-08-24, ~4 days)

**This week's takeaway: genuinely quiet.** Three parallel research passes (method-watch/tooling/compute-cost;
NR4A/EMC + degrader methodology; non-degrader routes) turned up no NR4A3/EMC-specific news, no plan-changing
method, and only two real tooling/precedent deltas worth capturing — a routine RDKit patch release and one AOC
delivery-tech milestone. This is the honest finding for a short (~4-day) window, not padding.

### 1) METHOD-WATCH (plan-relevant)
- **No new co-folding/ternary/affinity/selectivity method found.** Boltz stays at v2.2.1 (open-weight); no
  DeepTernary, FKSFold, Chai, Protenix, or IntFold update since 2026-08-24.

### 2) NR4A / EMC
- **No new NR4A3-specific primary paper, ligand, structure, or trial found this period.** The one thing that
  looked promising on a first pass — press coverage of a "new multiplexed E3-ligase screening platform"
  (C&EN, phys.org, Drug Target Review, GEN, News-Medical, all ~2026-08-07) — traced back to the *same*
  Dana-Farber DCAF11/glutathionylation-activated glue (M12→DDX18) already logged as the Nature 2026-08-05
  paper in the prior entry. It is secondary amplification, not a new result.

### 3) Degrader methodology
- **Quiet.** DeepTernary/TernaryDB benchmarking, a paralog-selective p300 degrader (Nat Commun), and a
  molecular-glue-landscape review (Nat Chem Biol) all surfaced in search but predate the window (2025, and
  ~April/May 2026 respectively) — old prior art, not delta items.

### 4) NON-DEGRADER ROUTES
- **VERAXA Biotech + Secarna Pharmaceuticals — positive in-vitro proof-of-concept for their AOC alliance
  (2026-08-24).** A conjugated oligonucleotide candidate showed greater potency than the naked oligo; reported
  as validating VERAXA's click-chemistry conjugation platform (whose stated primary focus is solid tumors,
  though this specific readout is an immunology indication). A second AOC delivery-tech data point alongside
  TAC-001 for the ASO route's dominant gate — not EMC-specific, not yet a named candidate for our route.
  https://www.biospace.com/press-releases/veraxa-biotech-and-secarna-pharmaceuticals-achieve-research-milestone-in-antibody-oligonucleotide-conjugate-aoc-alliance
- **PerVision (NCT06094101) — a closer external precedent for the parked fusion-breakpoint vaccine idea.**
  Phase I/II personalized peptide vaccine in pediatric/young-adult fusion-positive sarcomas, combining a
  fusion-breakpoint peptide *plus* a neoantigen peptide — structurally closer to an EWSR1::NR4A3-breakpoint
  design than the DNAJB1-PRKACA precedent already tracked (breakpoint peptide only). Status RECRUITING per an
  April 2026 snapshot; not independently re-verified live this scan (clinicaltrials.gov direct fetch remains
  egress-blocked from this session). Does not reopen the parked vaccine row — that row was parked on economics
  and a cold, self-adjacent tumor, not on a shortage of precedent — but strengthens the "fusion-junction
  vaccines are a live, funded modality elsewhere" prior. https://clinicaltrials.gov/study/NCT06094101
- No new immunotherapy/TCR-T/cell-therapy trial or readout specific to fusion-driven sarcoma found otherwise.

### 5) Tooling & operating-environment watch
**(a) Library releases.** **RDKit 2026.03.6** (released 2026-08-28, today) — adds a "synthon space shape
search" feature, a BertzCT descriptor speed-up (no value change, safely re-runnable) and bug fixes (numpy
dtype handling, Boost 1.92 build compat); no default-affecting change to numbers we've already produced.
https://github.com/rdkit/rdkit/releases/tag/Release_2026_03_6. OpenMM (8.6.0), OpenFE (v1.12.0), gufe
(v1.12.0), openmmtools (v0.26.0), Kartograf (v2.0.0), openff-toolkit (0.19.0), openff-nagl (0.5.5) all confirmed
still latest via each project's own GitHub releases page — no change. LOMAP2's GitHub releases page 404'd on
direct fetch this scan; conda-forge metadata suggests it is still v3.3.0, unconfirmed via the primary route.

**(b) Frontier-model access.** No verified newer-than-Opus-5 model this week. Secondary aggregators
(llm-stats.com, pricepertoken.com, intuitionlabs.ai) surfaced claims that "Gemini 3.1 Pro" and "GPT-5.6 Sol"
beat Opus 5 on GPQA (~94%); OpenAI's own page confirms GPT-5.6 Sol/Terra/Luna is real
(openai.com/index/gpt-5-6/), but it previews from ~2026-07-09 — before the 2026-07-24 Opus 5 baseline — so it
is not a delta, and no primary head-to-head benchmark against Opus 5 was found. Treat the specific percentages
above as unverified/low-confidence, not established.

**(c) Phone-drivable coding agents.** Changelog aggregators describe Claude Code native remote-control
(launching sessions from the mobile app device card) and cross-session messaging as August 2026 features, but
this scan could not confirm an exact ship date fell inside the 2026-08-21→08-28 window from a primary Anthropic
changelog page — UNKNOWN precise timing, flagged rather than asserted. No Codex-mobile change found.

**(d) Compute-cost / GPU-market.** No verified price move since 2026-08-24 on Vast.ai, RunPod, Lambda, Modal,
Salad, Together, Crusoe, CoreWeave, AWS, or GCP spot/preemptible pricing. Nvidia's next-gen Vera Rubin (HBM4,
~22 TB/s per-GPU bandwidth — the axis that matters for our memory-bandwidth-bound OpenMM PME MD) remains an
"H2 2026" forward item with no cloud availability yet — not actionable now, not auto-captured. No new provider
or free/academic credit program found.

### Action items for the program
1. If the RDKit "synthon space shape search" feature looks useful for the de-novo/warhead pool work, evaluate
   it — otherwise no action needed on this release.
2. Fix `trig_01X5xHy1cmkLjkATEijZSNJf`'s missing repo `sources` grant remains outstanding and needs trimcrae
   (unchanged — carried from the 2026-08-24 entry).

*Sources are real search hits from three parallel research passes (method-watch/tooling/compute-cost; NR4A/EMC
+ degrader methodology; non-degrader routes). clinicaltrials.gov direct fetch and some publisher docs sites
remained egress-blocked mid-scan and are flagged UNKNOWN rather than guessed. No fabricated papers, trials,
releases, or prices.*

---

## 2026-09-04 (Fri) — AUTOMATED weekly field-scan (delta vs 2026-08-28, ~1 week)

**This week's takeaway: quiet for NR4A3/EMC itself, but a real tooling delta.** No new NR4A3/EMC-specific
paper, ligand, structure or trial, and no new co-folding/ternary/selectivity method beyond what is already
tracked. The one substantive finding is on the frontier-model watch: **Claude Fable 5.1 / Mythos 5.1 shipped
2026-09-01**, and Fable 5.1 is the first model found to out-measure Opus 5 on every published category,
including a science-reasoning benchmark that roughly doubled — worth checking whether these research sessions
are actually running on it.

### 1) METHOD-WATCH (plan-relevant)
- **No new co-folding/ternary/affinity/selectivity method found.** DeepTernary, FKSFold, Boltz-2 (still
  v2.2.1 open-weight) and Protenix (still v2, April 2026) are unchanged from the 2026-08-24/28 entries. A
  curated molecular-glue literature database surfaced this scan (a reference resource, not a new predictive
  method) — not capture-worthy on its own and not cited further here.

### 2) NR4A / EMC
- **No new NR4A3-specific primary paper, ligand, structure, or trial found this period.** General NR4A1/
  NR4A2/NR4A3 family literature (a dual-ligand commentary, an immunity review) turned up but adds nothing
  NR4A3- or EMC-specific.
- **⚠ Disambiguation, not a finding for us:** this week's chondrosarcoma clinical-trial news — the **CHONQUER**
  Phase III trial (first patient enrolled 2026-09-01, TIBSOVO vs placebo) and **ozekibart (INBRX-109)**'s BLA
  acceptance (PDUFA April 2027) — are both for **IDH1-mutated *conventional* (skeletal) chondrosarcoma**, a
  genetically and clinically distinct disease from extraskeletal myxoid chondrosarcoma (EMC/EWSR1::NR4A3).
  Flagged only so neither gets miscited as EMC-relevant; neither is. https://www.globenewswire.com/news-release/2026/09/01/3354489/0/en/chondrosarcoma-clinical-trial-pipeline-emerging-therapies-and-key-developments-shaping-the-treatment-landscape-delveinsight.html
  · https://www.clinicaltrialsarena.com/news/inhibrx-biosciences-ozekibart-chondrosarcoma-phase-ii/

### 3) Degrader methodology
- **Quiet.** No new PROTAC/molecular-glue cooperativity or ternary-prediction paper crosses the window beyond
  what 2026-08-24/28 already logged (the Riepenhausen AF3-vs-Boltz-2 benchmark, DegradeQuery).

### 4) NON-DEGRADER ROUTES
- **No new fusion-junction vaccine, TCR-T, or immunotherapy trial/readout specific to a FET-fusion sarcoma
  found this period.** PerVision, SarVac and FusionVAC22_01 (all already tracked) remain the live precedents;
  general TCR-T/neoantigen reviews surfaced but add no new EMC-relevant data point.
- **No new AOC/oligonucleotide-delivery technology candidate found this period.** The two AOC design-principles
  reviews already tracked (J Hematol Oncol, Gene Therapy) continue to be the freshest synthesis; no new
  delivery platform or EMC-enriched surface antigen found.

### 5) Tooling & operating-environment watch
**(a) Library releases.** **No change this period.** OpenFE stays v1.12.0 (2026-06-29), OpenMM 8.6.0
(2026-08-19), RDKit 2026.03.6 (2026-08-28, already captured), Boltz still v2.2.1 open-weight (2025-09-08).
No new gufe/openmmtools/Kartograf/LOMAP2/openff-toolkit/openff-nagl release found this window.

**(b) Frontier-model access — REAL DELTA, captured below.** **Claude Fable 5.1 and Claude Mythos 5.1 released
2026-09-01.** Fable 5.1 "finishes ahead of Opus 5 on every category Anthropic published," and specifically
roughly doubles the agentic-scientific-research benchmark Terminal-Bench-Science 0.1 (52.6% vs Fable 5's
24.7%); biology safeguards fire ~85% less often on benign medical/biology questions — fewer false-positive
refusals for legitimate research work like this program's. **Mythos 5.1** is the identical model with lighter
safeguards, gated to vetted organizations via a new Life Sciences Verification Program (US-only) — not a lane
this program has access to. Fable 5.1 itself is the generally-available tier. ⚠ **UNKNOWN this scan whether
these research sessions are actually running on Fable 5.1 or still falling back to Opus 5** — worth checking
`/status` rather than assuming, since the whole point of tracking this row is using the best available tier.
https://www.anthropic.com/claude/fable

**(c) Phone-drivable coding agents.** **Codex Remote is now GA on all ChatGPT plans** — from the ChatGPT
mobile app, users can start/continue work on a connected Mac or Windows host, review progress and approve
actions from the phone; pairing now uses authenticated one-to-one QR codes. A new DigitalOcean Droplet
Workspace plugin lets Codex provision and connect to a cloud host directly. Incremental relative to the
2026-08-28 entry (Codex mobile control already existed); the comparison to driving Claude Code from the
Claude mobile app is unchanged. https://openai.com/index/work-with-codex-from-anywhere/

**(d) Compute-cost / GPU-market.** No material price move found this period on Vast.ai/RunPod/Modal/GCP/AWS
spot pricing — Vast.ai remains the cheapest marketplace floor. RTX 5090 remains **UNPRICEABLE for our
OpenMM/OpenFE workload**: no $/ns benchmark found this scan either (general LLM-inference and rendering
benchmarks exist, but nothing for memory-bandwidth-bound PME MD). No new GPU provider or free/academic credit
program found.

### Action items for the program
1. **Check whether this session (or the research sessions generally) is running Fable 5.1 or still falling
   back to Opus 5** — if Fable 5.1 is available and out-measures Opus 5 on science reasoning as claimed, that
   is a free upgrade for every future research session, not just this newsletter.
2. Fix `trig_01X5xHy1cmkLjkATEijZSNJf`'s missing repo `sources` grant remains outstanding and needs trimcrae
   (unchanged — carried from prior entries; ⚠ this run itself landed on `main` successfully via the working
   session-based mechanism per method-watch.md, so the underlying Routine defect may be moot if that is now
   the mechanism in use — unverified this scan).

*Sources are real search hits from parallel WebSearch passes (method-watch/tooling/compute-cost; NR4A/EMC +
degrader methodology; non-degrader routes; frontier-model/mobile-agent watch). No fabricated papers, trials,
releases, or prices; items not independently verified beyond the search snippet are flagged as such above.*
