# NR4A3-selective degrader — weekly field-scan log

Dated summaries of new/relevant literature + methods for the in-silico NR4A3 program (EMC / EWSR1::NR4A3).
Produced by the weekly field-scan Routine (**Fri 8 AM ET**, `trig_0195bCWjobUPB6S6nM25bCL1`), or manually when
that run fails. **Scope is broader than the degrader path**: also ASO delivery, immunotherapy/neoantigen, and any
new solid-tumor modality that could apply to a fusion-driven sarcoma. It ALSO carries a **Tooling &
operating-environment watch** (added 2026-07-14, trimcrae): (a) new releases/changelogs of our in-silico
software stack (OpenFE, OpenMM, openmmtools, gufe, OpenFF/NAGL, LOMAP/Kartograf, RDKit, Boltz — esp. bumps that
change defaults/accuracy, e.g. the OpenFE v1.7 time_per_iteration 1.0→2.5 ps change); (b) changes to Anthropic's
bio/biosecurity guardrail policy (Usage Policy / RSP / ASL bio-CBRN); (c) whether OpenAI Codex has gained
phone-without-Remote-Desktop control (a Claude-Code-style mobile control surface). Each entry should highlight
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
