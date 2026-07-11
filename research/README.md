# EMC research program

The mission of this project is not a web page — it is to **improve outcomes for
people with extraskeletal myxoid chondrosarcoma (EMC)**. That runs on three rails:

1. **Patient education** — the public hub (`/cancers/emc/`), already live.
2. **Hypothesis generation** — find *existing* drugs whose mechanisms plausibly fit
   EMC's biology but have **not been tried** in EMC, as testable, cited hypotheses.
3. **Dissemination** — manuscripts toward a preprint / journal submission:
   - a **systematic review & meta-analysis** of EMC outcomes (built on the pooled,
     cited registry),
   - a **drug-repurposing hypothesis** paper, and
   - a **computational target-assessment & novel-modality program** for the
     EWSR1::NR4A3 fusion (structure-based druggability + fusion-junction neoantigen +
     a prioritised degradation/ASO/immune/dependency-screen program).

```
research/
  README.md                         this file
  PROTOCOL.md                       systematic-review / meta-analysis protocol (PRISMA-style)
  IDEAS.md                          parked ideas / future-work backlog (e.g. upstreaming to TxGNN)
  hypotheses/
    METHODOLOGY.md                  how candidates are generated, graded, and cited
    candidates.json                 structured repurposing-candidate catalog (data)
    targets.json                    EMC drug-target list (drives the systematic enumeration)
    enumerate-drugs.mjs             DGIdb target->drug enumeration + gap analysis (runs in CI)
    target-drug-matrix.json         enumeration output: approved drugs per EMC target
                                    (snapshot on main; auto-refreshed on the `enumeration-cache` branch)
    txgnn_predict.py                runs the real pretrained TxGNN model for EMC (CI)
    txgnn-emc-predictions.json      TxGNN's genuine zero-shot ranking of 7,957 drugs for EMC
    txgnn-emc-findings.md           interpretation: TxGNN diverges from mechanism/enumeration (a limitation finding)
    txgnn-relatives-comparison.json interpretation: sparsity stress-test (EMC vs chondrosarcoma vs STS)
  modalities/
    nr4a3_structure.py              AlphaFold pLDDT (disorder) + fpocket druggability of NR4A3/EWSR1 (CI)
    fusion_neoantigen.py            UniProt seqs + MHCflurry EWSR1::NR4A3 junction-neoantigen prediction (CI)
    fusion_breakpoints.py           breakpoint-resolved neoantigens across real in-frame junctions (Ensembl exons)
    patient_neoepitopes.py          per-patient tool: fusion breakpoint + HLA -> ranked candidate epitopes
    hla_coverage.py                 HLA population coverage of the neoepitopes (AFND mirror; Wilson CIs; class I+II)
    coverage_scan.py                coverage vs #-alleles-targeted curve + chart (broad MHCflurry panel; CI)
    vaccine_construct.py            minimal junction SLP + string-of-beads candidate construct (no network)
    nr4a3-structure-assessment.json structure/druggability result (snapshot; refreshed on modalities-cache branch)
    fusion-neoantigen-predictions.json junction-neoantigen result (snapshot; refreshed on modalities-cache branch)
  atlas/                            ★ EMC Open Target & Drug Atlas — the integrating, machine-readable evidence system
    README.md                       what it is + integration map to existing repo assets
    METHODS.md                      manuscript-quality methods; STATUS.md is the live build log
    citations.json                  provenance backbone (verified flag + verification_level per source)
    {samples,claims,drug_screens,evidence_score}.json   sources of truth (EWSR1/TAF15 always distinct)
    build.mjs                       one-command validate + regenerate dist/*.tsv (no deps)
    dist/*.tsv                      generated deliverables (sample manifest, claims, screens, compound-exposure, score)
  manuscripts/
    README.md                       index: the ONE active manuscript + role of every other file (read this first)
    emc-treatment-roadmap.md        ★ ACTIVE MANUSCRIPT — the prioritized, falsifiable treatment roadmap (#1 deliverable)
    emc-treatment-strategy.md       strategy/source-of-truth capstone behind the roadmap (not a manuscript)
    {immunotherapy-options,emerging-modalities-scan,car-t-strategies,degrader-vs-synthetic-lethal}-emc.md
                                    source memos feeding the roadmap (per-route deep-dives)
    repurposing-hypotheses.md       earlier treatment-track draft, subsumed by the roadmap
    novel-modalities.md             earlier treatment-track draft, subsumed by the roadmap
    clinical-brief-emc-neoantigen.md one-page clinician brief drawn from novel-modalities
    hla-coverage-emc.md             PARKED: HLA coverage of the public fusion-neoantigen (reusable as eligibility input)
    meta-analysis.md                SEPARATE track: outcomes systematic review/meta-analysis (prognosis, not treatment)
    {fact-check-log,repurposing-hypotheses-review,novel-modalities-factcheck}.md
                                    QA: fact-check & internal-review logs (not manuscripts)
```

## Non-negotiable rules

- **Firewall.** Nothing in `research/` is served on the patient site, and no
  hypothesis (Tier T0–T2, see hypotheses/METHODOLOGY.md) may appear on the
  patient-facing page. Only a candidate that reaches **real EMC clinical evidence
  (T3)** can migrate to `emergingTreatments`, and only after clinician review.
- **Hypotheses are hypotheses.** Every mechanistic claim is cited or explicitly
  flagged `needs-verification`. Nothing here is medical advice, a recommendation,
  or a statement that any drug works in EMC. It does not.
- **Human-in-the-loop publishing.** Claude drafts, structures, and cites. A named
  human author (ideally with a sarcoma clinician/researcher) reviews and is the one
  who submits. No automated posting to a preprint server or journal.
- **No fabrication** (inherits the repo's medical-integrity rule and
  `METHODOLOGY.md`): no invented citations, mechanisms, or results.

## Status

- Meta-analysis: pooled dataset built; protocol drafted; **random-effects engine
  implemented** (`research/meta/meta-analysis.mjs` → DL pooling + I²/τ², forest
  plots, PRISMA flow, leave-one-out / era / registry-vs-all sensitivity); manuscript
  results populated. **Still needs** formal risk-of-bias scoring, a GLMM/Freeman–Tukey
  cross-check, and clinician review before submission.
- Repurposing: methodology + grading rubric drafted; catalog seeded with 3 graded
  candidates. **Needs** targeted literature verification of `needs-verification`
  claims and clinician review.
- Novel modalities: manuscript drafted (`manuscripts/novel-modalities.md`) with **real,
  reproducible CI compute** (`research/modalities/`, `modalities-run.yml`): AlphaFold/
  fpocket druggability of NR4A3 (folded LBD, no druggable pocket — max 0.495), the
  fusion-junction neoantigen (lead **GQQPCVQAQY** strong on HLA-B*15:01), and
  fusion-specific ASO designs. Verification trail in `novel-modalities-factcheck.md`
  (incl. a corrected MHCflurry column bug). **Needs** a wet-lab/sarcoma collaborator —
  the program is explicitly designed to be handed to one — and confirmation of 2 ⚠ DOIs.
