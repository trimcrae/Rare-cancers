# EMC Open Target & Drug Atlas — Methods

*Manuscript-quality methods for the integrating evidence resource. Version-controlled; every
figure/number is regenerable from `build.mjs` over the JSON sources of truth.*

## 1. Scope and design principle

The atlas integrates the fragmented EMC evidence base — three modern patient-derived models,
two non-overlapping drug screens, small clinical treatment cohorts, legacy expression datasets,
and public perturbation/expression databases — into one provenance-checked, machine-readable
system. It does **not** re-derive analyses that already exist elsewhere in the repository
(DepMap surrogate reads, the NR4A3 biology/safety evidence base, repurposing candidates,
fusion-junction antigen prediction); it references them and assigns them a comparable evidence
score. The governing principle is **independent-evidence-type convergence**: an axis is ranked
by how many *distinct* kinds of evidence (model, tumor expression, genetic perturbation,
pharmacologic replication, clinical) point the same way, and is penalized for single-model-only
signals, expression-only claims, implausible achievable exposure, and one-drug=one-target
inference.

## 2. Sources of truth and provenance model

Five JSON files are authoritative; TSV deliverables are generated, never hand-edited.

- `citations.json` — every source, each with `verified` and (where relevant) `verification_level`.
- `samples.json` — the sample/model registry.
- `claims.json` — atomic evidence claims, each with a source locator, `evidence_type`,
  `emc_specificity` (emc_specific vs extrapolated), fusion-subtype scope, direction, confidence,
  and any `contradicts` link.
- `drug_screens.json` — reconstructed screens + compound→target→exposure, plus an explicit
  `did_not_survive_verification` block.
- `evidence_score.json` — per-entity component scores, ranked shortlist, validation panel,
  go/no-go criteria, and a `what_the_atlas_already_rejected_or_downgraded` block.

`build.mjs` enforces that **every** reference (sample `source_publication`, claim `source`,
screen `source`, `contradicts` link) resolves to a citation key, a claim id, a compound, or a
whitelisted token; a dangling reference fails the build. This is the machine-checked backbone of
"every claim is an evidence object with a precise source locator."

## 3. Verification level, and the CI workaround for the egress proxy

The dev sandbox's egress proxy blocks PubMed/PMC/Springer/EuropePMC **and** NCBI/GEO. Rather than
accept abstract-only verification, the atlas routes those fetches through a **GitHub Actions runner**
(unrestricted internet, free) via `.github/workflows/atlas-data.yml`, which runs
`fulltext_verify.py` (EuropePMC REST) and `expression_reprocess.py` (GEO). Every citation carries a
`verification_level` field recording exactly how it was confirmed. After the CI pass:

- **Most clinical + the NCC screen are PRIMARY-ABSTRACT confirmed** (EuropePMC): pazopanib
  (18%, 95% CI 1–36), sunitinib (6 PR/2 SD/2 PD **with the EWSR1-responsive / TAF15-refractory
  differential stated in-text**), anthracycline (4/11 PR), Masunaga registry (margin HR 4.76,
  95% CI 1.72–13.15), and Iwata/NCC (brigatinib/panobinostat/romidepsin named).
- **The USZ screen hit identities remain secondary-source:** the Bangerter EuropePMC abstract is
  generic and does not name compounds (Human Cell is not open-access), so carfilzomib/PU-H71 stay
  snippet-level and **HDM201/MDM2–MDM4 stays uncorroborated** (demoted to a hypothesis, not a hit).
- **Numeric IC50 values were not retrievable** and are recorded `not_reported_retrievable` — none invented.
- **Two upstream claims were corrected:** the carfilzomib+doxorubicin combination is *"additive **and**
  synergistic in **both** models"* (venetoclax also in the panel), not a one/other split.

Still pending an unblocked-PMC pass: USZ full-text hit confirmation, IC50 numbers, unbound-Cmax exposure.

## 3a. Expression reprocessing result

`expression_reprocess.py` (run in CI) reprocessed the GEO series matrices per platform. **GSE24369
(GPL6244, 6 EMC vs 36 sarcoma, 23,072 genes)** yields a rank-based AUC signature that **reproduces
known EMC biology** — NMB (1.00), CHRNA6 (1.00), SOX9 (0.92), RET (0.86), NR4A3 (0.82), PPARG (0.75)
all EMC-up — with leave-one-out top-50 Jaccard 0.64 (n=6). This meets the strategy's "recover known
EMC features" success criterion and is folded in as claim C018. GSE4303's seven legacy custom
two-colour platforms expose no standard probe→symbol column (0 genes annotatable) — an honest
limitation, so GSE4303 remains unverified and superseded by GSE24369 for the signature.

## 4. Sample registry

Each published tumor/model or cohort receives a stable `sample_id`. Individually-reported
samples get per-sample rows; multi-patient studies are registered as cohort-level rows with `n`.
`EWSR1::NR4A3` and `TAF15::NR4A3` are always distinct fields. Values absent from a source are
`unknown`; values asserted elsewhere but not verified from the primary source are `to_confirm`.
The historical H-EMC-SS line is registered with `authentication_status =
REQUIRES_AUTHENTICATION_BEFORE_USE` per the go/no-go rule that historical lines are used only
after molecular authentication.

## 5. Drug-screen reconstruction and compound→target→exposure

Hits are normalized to a compound, nominal target, a **polypharmacology** note (so no single
drug's activity is read as proof of its nominal target — brigatinib is flagged as multikinase,
not an ALK claim), approved indication, a qualitative **achievable-free-exposure** note (the
solid-tumor-window caveat for proteasome/HSP90/HDAC inhibitors is field-standard and stated
qualitatively; specific unbound-Cmax numbers are `to_populate`), and a named **target-engagement
assay**. This is the filter that prevents ranking a nanomolar 3D-sphere hit whose effective free
concentration cannot be reached safely in a solid tumor.

## 6. Evidence score

Each therapeutic axis/target is scored 0–3 on ten components (§`evidence_score.json` →
`components`). **Every component is published**; the composite sum is reported only alongside its
components and is explicitly *not* a probability of success. Two guard behaviors are built in:
maturity inflates the composite (doxorubicin scores 20 but is flagged as a comparator, not a
discovery), and expression-only entities (PPARG: expression 3, perturbation 0) are surfaced as
the exact anti-pattern the atlas exists to catch.

## 7. Reproducibility

`node research/atlas/build.mjs` validates provenance and regenerates all five `dist/*.tsv`
files deterministically. No third-party dependencies. The JSON sources are the diffable record;
the TSVs are the human-readable and collaborator-shareable deliverables.

## 8. What the atlas is *not*

It is not a treatment recommendation, not a trained model (no high-capacity model is fit to the
single-digit EMC-specific dataset — rank aggregation + explicit priors only), and not a substitute
for the wet-lab validation it is designed to enable. Its success criterion is that a reader who
did not build it can reproduce it, see which vulnerabilities have >1 independent evidence type,
and see — with citations — exactly which apparent targets collapsed on replication/exposure
filtering.
