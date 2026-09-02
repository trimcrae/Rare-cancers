---
id: DOC-SPRINT-S39-ATLAS-ADJUDICATION
title: "S39-ATLAS-ADJUDICATION — the 'backup route' STRATEGY.md still names is superseded, and recovering it would have restored a retracted junction model"
level: L3
kind: memo
status: live
date: 2026-09-02
audience: [autonomous research agents, maintainers]
purpose: >
  Decide whether the EMC Open Target and Drug Atlas — 39 files present on one git ref of 302, and cited
  by STRATEGY.md as the degrader programme's backup route — is live work that was lost or a snapshot the
  programme has since overtaken, and act on the answer rather than leaving the pointer dangling.
scope: >
  All 39 files of research/atlas/ as they stand on origin/claude/emc-research-strategy-kdz9kn, read
  against what origin/main carries today. Records one genuinely unique reading (CHRNA6) that survives the
  supersession verdict, and corrects the dispatching brief's claim about which branch holds the missing
  ST-MORTALITY-MECHANISM family.
last_verified: 2026-09-02
---

# Atlas adjudication — notes as I go
Started 2026-09-02. Agent: atlas-adjudication subagent.

## Established facts (verified)
- `git ls-tree -r --name-only origin/claude/emc-research-strategy-kdz9kn | grep '^research/atlas/'` -> 39 files. CONFIRMED.
- STRATEGY.md line ~156 (Appendix B, "Atlas-anchor reframe" row) says atlas work stays valuable as support +
  "backup route if degrader design fails", and points at `research/atlas/README.md` + `STATUS.md`.
  CONFIRMED verbatim by `sed -n '140,175p' STRATEGY.md`.
- STRATEGY.md is history-only per CLAUDE.md. The row is in **Appendix B — superseded strategy framings**.

## What the atlas IS (from its own README/STATUS, dated 2026-07-11)
"EMC Open Target & Drug Atlas" — versioned, machine-readable curated synthesis of *identified public*
EMC evidence. Question: which genes/pathways/drugs/combos have independent support in EMC, in which
fusion subtype, at what evidence level, with what feasible validation experiment.
- 32 sources, 23 atomic claims, 10 scored therapeutic axes. Triage heuristic, NOT calibrated probabilities.
- CI analyses folded in: GEO GSE24369 reprocess, EuropePMC full-text verify, DepMap panel dependency,
  junction antigen MHC-I/II, FDA-label pharmacology.
- Build: `node research/atlas/build.mjs` -> dist/*.tsv (5 TSVs).
- Release blockers listed (DOI never minted; PR #3 unreviewed).
- Self-declared limits: no EMC line in DepMap (all surrogates), USZ compound IDs secondary-source-unconfirmed,
  panel not exposure-matched, antigen = predicted binding only, weights are author judgments.

## File inventory (39)
docs: CHANGELOG, DEPOSIT, METHODS, README, REPRODUCIBILITY, STATUS,
      antiangiogenic-mechanism.md, collaborator-brief.md, lineage-antigen-program.md,
      outreach.md, overview-plain-language.md
data: citations.json, claims.json, drug_screens.json, evidence_score.json, samples.json
code: build.mjs, antigen_expand.py, antigen_mhcii.py, expression_reprocess.py, fulltext_verify.py,
      panel_dependency.py, panel_exposure.py
generated: _generated/{antigen-expanded,antigen-mhcii,emc-expression-reprocess,panel-dependency,panel-exposure}.{json,md},
           _generated/fulltext-verify.json
dist: emc_claims_with_provenance.tsv, emc_compound_target_exposure.tsv, emc_drug_screens.tsv,
      emc_evidence_score.tsv, emc_sample_manifest.tsv

## Supersession findings (as I go)

### drug_screens.json + dist/emc_drug_screens.tsv + dist/emc_compound_target_exposure.tsv -> SUPERSEDED, AND BEATEN
Atlas state (2026-07-11): USZ/Bangerter hit identities `SECONDARY_SOURCE_UNCONFIRMED`; STATUS.md release
blocker #1 was "Source-author accuracy corrections folded in (esp. Pauli / USZ compound identities)"; the
atlas planned to EMAIL Dr Pauli to resolve it (outreach.md Email 1).
Main today: `research/manuscripts/repurposing/repurposing-hypotheses-review.md:111-112` —
"~~Confirm the Bangerter 2023 venetoclax/carfilzomib/doxorubicin identities~~ — **done via CI
(NCBI efetch full text):** all three drugs' sensitivities + the carfilzomib synergies are..." 
=> the atlas's #1 release blocker was cleared on main, by CI, without the email.
AND main CORRECTS the atlas: `repurposing-hypotheses.md:440,636` — the 40-drug discovery screen ran on
**USZ20-EMC1 ALONE** (atlas TSV says "high sensitivity in BOTH USZ models"), and venetoclax showed
**no monotherapy response**. So the atlas row is not merely superseded, it is WRONG by main's full-text read.
Also on main: `emc-systems-map.json` carries the carfilzomib clinical bound (paediatric phase 1; the
bortezomib STS trial, 1/21 PR) — evidence the atlas never had.
VERDICT: superseded + partly refuted. Do NOT recover.

### Junction-antigen claims C016/C021/C022 + antigen_expand.py/antigen_mhcii.py/_generated -> SUPERSEDED ON A RETRACTED MODEL
Atlas C016: "34 junction-spanning peptides ... Breakpoint-resolved: 7 in-frame junctions"; C021 "Both share
the NR4A3 exon-2 right seam"; C022 EWSR1 junction DRB1*07:01 IC50 16.4 nM.
Main: `research/modalities/fusion-neoantigen-retraction.json` (2026-08-07) — the corrected TRANSCRIPT model
gives junction `EWSR1(1-264)::NR4A3(1-626)`, NR4A3 resuming at RESIDUE 1 via exon 3, and **5 of 27 declared
exon pairs EMITTABLE, not 7**; "The retracted 7-junction set is not recovered and was not padded back to:
the corrected denominator is 5." 38 junction peptides per pair, 11 distinct predicted binders, 4 strong.
So the atlas's junction GEOMETRY (exon-2 seam, 7 junctions, 34 peptides) is the retracted one.
Main also carries far more: epitope-allele-matrix-mhcnuggets.json, coverage-uncertainty.json (Wilson CIs +
a dependence-free bound the manuscript's independence product lacks), coverage-threshold-curve.json,
vaccine-threshold-calibration.json, vaccine-construct.json, and the whole
`research/manuscripts/neoantigen/emc-vaccine-development-path.md` manuscript + PDF.
VERDICT: superseded, and recovering it would restore a retracted junction set. Do NOT recover.

### C013/C014 (B7-H3, PRAME) -> SUPERSEDED, and C014's myxoid half is INVALIDATED on main
The atlas never owned these — its README says it REFERENCES `research/modalities/depmap-insilico-findings.md`.
That file is on main and carries a 2026-08-05 AMENDMENT: the `myxoid` column is n=1 and that line is
ACH-001519 / H-EMC-SS, whose identity is disputed (Cellosaurus CVCL_1238: "Does not harbor a gene fusion
involving EWSR1 ... (PubMed=34413129)"). Finding 3's "PRAME HIGH in myxoid (7.6) ... most promising
antigen-directed signal" is marked "⛔ INVALIDATED as an EMC-proximal read".
Atlas C014 states exactly that invalidated number, and lineage-antigen-program.md ranks PRAME #2 on it.
VERDICT: superseded; the atlas copy is the pre-amendment text. Do NOT recover.

### C019 + antiangiogenic-mechanism.md (EWSR1-vs-TAF15 antiangiogenic biomarker) -> SUPERSEDED BY A MANUSCRIPT
This is THE claim STRATEGY.md's "backup route" sentence rests on.
Main: `research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md` (DOC-EMC-FUSION-PARTNER-
STRATIFICATION, 2026-08-08, status live, L3 manuscript, `canonical_for: [NR4A3 fusion-partner
stratification, ...]`) — a partner-stratified pooled synthesis with per-arm denominators, an explicit
population-overlap exclusion of the sunitinib series against the pazopanib trial, a headline denominator
given as a RANGE (3 to 5), and — line 525 — the counter-quotation from the source literature
**"Even in EMCS the fusion-protein is unlikely to be related to sunitinib sensitivity"**.
The atlas's C019 asserts the differential as primary-confirmed with no overlap caveat and no counter-source.
The CRF/growth-modulation-index half of antiangiogenic-mechanism.md §2 is superseded by the whole
`research/manuscripts/endpoint/` programme (emc-endpoint-alternatives-2026-08-08.md,
response-endpoint-indolent-tumours.md, meta-analysis.md, orr-dcr-reread.json, placebo-arm-calibration.json).
The RET half is superseded by `research/modalities/emc-ret-lane.md` + emc-ret-activation-bar.json.
VERDICT: superseded, and main states it MORE WEAKLY, which is the honest direction. Do NOT recover.

### C020 panel dependency + panel_dependency.py -> SUPERSEDED
Main: `research/manuscripts/dependency/emc-biomarker-selected-classes.md` (DOC-EMC-BIOMARKER-SELECTED,
2026-08-09, live L3 manuscript) covers the BH3/apoptosis axis on **16 EMC tumours across two series**
plus the sarcoma CRISPR panel — EMC tumour data the atlas never had. Also
`research/modalities/emc-proteostasis-read.json`, and `emc-mtap-prmt5-hypothesis-SI.md:107-109` carries
the proteasome dependency read (PSMB5 97.8% of sarcoma lines).
VERDICT: superseded. Do NOT recover.

### C018 GSE24369 rank-AUC signature -> SUPERSEDED METHODOLOGICALLY; one gene (CHRNA6) is unique
Atlas: "6 EMC vs 36 other sarcoma ... NMB AUC 1.00 (rank 11), CHRNA6 1.00 (rank 26), SOX9 0.92, RET 0.86,
NR4A3 0.82, PPARG 0.75", leave-one-out top-50 Jaccard 0.64.
Main reads the SAME series with a different and better-specified comparator arm: `emc-expression-panels.json`
platforms block — GSE24369 = 42 samples, **6 EMC vs 29 comparator sarcomas** (17 LGFMS + 6 desmoid +
6 fibrosarcoma per emc-surface-target-landscape.md:541), noting "the comparator arm is itself FET-rearranged
(LGFMS is FUS::CREB3L2)". The atlas's 36 is a different denominator; nothing on the atlas branch justifies it.
Main also applies a size-matched empirical null and states the governing rule the atlas's raw AUC violates:
`nr4a3-fusion-targets.json._the_second_rule` — "⛔ A RAW 'HIGHER IN EMC' IS NOT A RESULT."
Per-gene on main (nr4a3-fusion-targets.json gene_reads, null-calibrated): NMB EMC mean_z 1.3968 vs
comparator 0.146, 89th array percentile; DKK1 2.3181 vs -0.5197. PPARG/SOX9/RET/NR4A3/CD276/PRAME all read
in emc-expression-panels.json.
⭑ **CHRNA6 is ABSENT from every EMC expression artifact on main** (`grep -rn CHRNA6` returns only
accession-symbol-cache.json and nr4a3-nuccore-sweep.json — incidental symbol/RefSeq rows, not reads).
VERDICT: the signature as a whole is superseded by better-instrumented reads; CHRNA6 is the one
unique gene, and it survives only as an UNCALIBRATED 2026-07 AUC on a denominator main does not use.

### lineage-antigen-program.md -> SUPERSEDED, and its top two rankings are contradicted on main
Its #1 is B7-H3 "near-universal surrogate signal". Main's `emc-surface-target-landscape.md:527` reads
B7-H3/CD276 at **+0.14 enrichment, BH q = 1.0, "Selective: no"**, and :559 has CD276 −0.249 (t −2.55) on
GPL6244 and not readable on GPL3290. Its #2 is PRAME on the invalidated myxoid 7.6.
Main's landscape roster (CDH11, KIT, CD248, FGFR1, NCAM1, GPC2, PTK7, MCAM, EPHB4, ...) with BH q values,
normal-tissue verdicts and a 3-cohort table is a strictly larger and better-controlled version of the same
document, plus an SI, a cover letter, a redteam and an outreach file.
VERDICT: superseded. Only the CHRNA6 and NMB/NMBR rows have no counterpart — and NMB IS read on main.

### C001/C002/C003/C005/C007/C010/C011/C012 (fusion biology, prevalence, gnomAD, redundancy, ligandability)
-> SUPERSEDED. Main: `research/manuscripts/degrader/nr4a3-emc-biology-evidence.md` (DOC-NR4A3-EMC-BIOLOGY-
EVIDENCE, live L3) is the file the atlas README says it REFERENCES rather than duplicates. It carries the
same four-pillar prior WITH PMIDs the atlas claim rows lack (PMID 36948401 cohort; gnomAD pLI 0.9999 /
LOEUF 0.37 / 13 observed vs 55.6 expected; PMID 17515897 Mullican Nr4a1-/-;Nr4a3-/- AML), plus an MGI
single-KO cross-check added 2026-08-03 that the atlas never had. Do NOT recover.

### C009 (no LOF experiment in any EMC cell line) -> SUPERSEDED
On main in `nr4a3-emc-biology-evidence.md` and tracked as a literature-absence claim in
`research/manuscripts/emc-systems-map.md:327` ("'no LOF experiment in any EMC cell line (e.g. H-EMC-SS)'
— a literature-absence claim | ⚠ survives, re-labelled"), and it is load-bearing in the RT-6MP closure
(emc-systems-map.md:492). Main tracks it as a re-openable claim; the atlas states it flat.

### citations.json (32 sources) -> SUPERSEDED
Main: `research/manuscripts/citation-provenance-ledger.json` — **237 entries**, with statuses,
`_defects_found`, and an arXiv article-class check added 2026-08-28. Plus `citation-article-types.json`,
`citation-retraction-notices.json`, `citation-retraction-sweep.json`, and gate 12 (`lint_citations.py` (does not exist in this checkout — atlas files were read from the branch, not recovered))
in the commit loop. The atlas's `verification_level` idea is the ancestor of all of this.

### evidence_score.json `what_the_atlas_already_rejected_or_downgraded` (8 entries) -> ALL EIGHT ARE ON MAIN
| atlas rejection | where it lives on main today |
|---|---|
| MDM2/MDM4 — HDM201 not a USZ hit | `repurposing-hypotheses-review.md` (identities resolved via CI full text) |
| ALK not a driver; brigatinib polypharmacologic | `research/literature/alk-ihc-fet-tumours-2026-08-29.json`, `emc-systems-map.json` |
| PPARG expression-only, not a target | `nr4a3-fusion-targets.json.pparg_arms` (6 resolved Enrichr-pinned slots + a knockout-UP control arm) |
| RET marker not addiction | `research/modalities/emc-ret-lane.md` + `emc-ret-activation-bar.json` — and main goes further: the ONLY RET-activation report in existence is one paywalled 2014 sentence (PMID 24703573), and PMID 28423517 is the 2017 paper CITING it, "not a second observation" |
| carfilzomib+dox synergy split unsupported | `repurposing-hypotheses.md:636` — and main's full-text read corrects the atlas's own correction |
| BCL2 vs BCL-xL/MCL1 | `emc-biomarker-selected-classes.md §2.5` |
| proteasome/XPO1/HDAC pan-essential, window is pharmacology | same manuscript + `emc-proteostasis-read.json` + `emc-mtap-prmt5-hypothesis-SI.md` |
| no tumour-cell-autonomous TKI addiction | `emc-surface-target-landscape.md` + the dependency lane |

### samples.json / dist/emc_sample_manifest.tsv -> SUPERSEDED IN SUBSTANCE
Main: `research/modalities/emc-line-data-probe.json` (the same three models, with verbatim abstracts and a
GEO/SRA accession probe), `research/literature/rt-lung-mets-probe.json`, and for the disputed historical
line `emc-atr-vulnerability.json -> part_a_hemcss_identity` + the depmap-insilico-findings amendment.
The atlas's exon-level USZ breakpoints are superseded by `research/modalities/fusion-breakpoint-neoantigens.json`
(27 declared exon pairs graded, with a `_superseded_cds_model_comparison` block) and `junction-breakpoint-scan.json`.

### C023 / panel_exposure.py / _generated/panel-exposure.* -> UNIQUE BUT LOW-VALUE, and the atlas says so itself
Nothing on main compiles DailyMed FDA-label PK for these 11 compounds (`grep -rln DailyMed` on main hits
only three ASO-delivery files). BUT: it is a KEYWORD SCRAPE, not a PK table. Its own CHANGELOG says
"Keyword extraction caught some non-PK sentences", and the doxorubicin block is mostly trial demographics
("The median age of the patients is 60 years..."). STATUS.md's own open list still wants
"A completed compound-by-compound pharmacology table (active conc vs total/unbound exposure, units, QC)".
It is a $0 CI refetch of public labels, regenerable at will. Not a backup route.

### collaborator-brief.md / outreach.md -> SUPERSEDED BY A DECISION, not only by content
Main has `research/manuscripts/surface-targets/emc-surface-target-outreach.md` (live L3) targeting the SAME
two model groups (USZ Bangerter; NCC Kondo/Iwata) with a stronger, preprint-backed ask.
And the atlas outreach's Email 1 — its lead ask, "confirm the USZ compound identities" — is DEAD: main
resolved it by CI full text.
⛔ More importantly the whole premise is retired. STRATEGY.md Appendix B's own "post-degrader route ranking
graded on Axis W" row (2026-08-03): "The axis assumed a collaborator with a bench who would run the winning
experiment, and there is none ... an experiment nobody will run has no size." The atlas's Phase B
(collaborator recruitment) is the activity that axis correction demoted.
⚠ Emails 3-6 (Stacchiotti; Rare Cancer Research Foundation; Sarcoma Foundation of America; SGC) name
recipients main does not. That is an OUTWARD-FACING act gated on trimcrae (CLAUDE.md §3) and is not
recoverable content in the sense this task means.

### overview-plain-language.md -> UNIQUE; NOT RECOVERED, ON PURPOSE
Patient/family/foundation-facing explainer. Nothing like it on main. ⛔ Recovering it recreates the audience
CLAUDE.md §7 retired ("THE PATIENT-FACING SITE IS RETIRED AND DELETED, NOT SHELVED. DO NOT RECREATE IT").
Its three headline leads are also the three superseded above.

### METHODS/REPRODUCIBILITY/DEPOSIT/build.mjs/atlas-data.yml -> SUPERSEDED BY THE REPO'S OWN MACHINERY
DEPOSIT.md's whole argument (Zenodo archives the WHOLE repo; mint from a curated bundle; exclude the site,
scratchpads and outreach) is now the repository's standing practice and is being worked this sprint
(`research/autonomy/sprint-2026-09-01/S33-DEPOSIT.md`). build.mjs's provenance-validation-plus-generated-TSV
pattern is what `systems_check.py` (does not exist in this checkout — atlas files were read from the branch, not recovered), `lint_citations.py` and the generated `systems/views/` do at repo scale.
REPRODUCIBILITY.md's two-layer model (deterministic local rebuild + pinned CI fetch) is the repo's
`fetch-literature.yml` (does not exist in this checkout — atlas files were read from the branch, not recovered) / `--check` regeneration contract.

## VERDICT — the "backup route" sentence is STALE and the work is SUPERSEDED

§5's test: can it name its paper? **No.** The atlas's own endpoint was a curated Zenodo/DOI deposit
(DEPOSIT.md), gated on four release blockers: #1 cleared elsewhere by CI; #2 (real ORCID in CITATION.cff
+ .zenodo.json) never filled; #3 (curated bundle) never assembled; #4 (independent review + green build on
a tagged commit, "PR #3 not merged/released while unreviewed") — and PR #3 was merged, against that
blocker's own condition (STRATEGY.md line 161).
`systems/views/L3-publications.md` on main carries **32 publication endpoints and NONE of them is the
atlas**; its four content pillars each map to a named, drafted paper:
- proteostasis-chromatin -> PUB-REPURPOSING / PUB-TXN-DEPENDENCY / PUB-BIOMARKER-DEP
- fusion-subtype antiangiogenic biomarker -> PUB-FUSION-PARTNER
- fusion-junction + lineage antigens -> PUB-NEOANTIGEN / PUB-VACCINE-PATH / PUB-HLA-COVERAGE / PUB-SURFACE-TARGETS
- direct fusion targeting -> PUB-DEGRADER / PUB-ASO / PUB-ANDGATE / PUB-MONOVALENT / PUB-TCIP
An aggregation layer over papers that now exist separately is an activity, not an option.

## COUNTS, verified independently of the census
- refs on origin: 302 (`git for-each-ref refs/remotes/origin | wc -l`, and `git ls-remote --heads origin`)
- refs carrying `research/atlas/`: **1** (loop over all 302) — `origin/claude/emc-research-strategy-kdz9kn`, 39 files
- `origin/main` `research/atlas/` paths: **0**
- `git log --diff-filter=D --oneline origin/main -- 'research/atlas/*'`: **0 commits** (invisible in main's history)
- publication endpoint rows in L3-publications.md: **32**

## ACTION TAKEN
Corrected `STRATEGY.md` — NOT a recovery. Two rows in Appendix B (which is history-only per CLAUDE.md):
- line 156 (Atlas-anchor reframe): appended a `⚠ Superseded, retained (rule 1.2)` block — original text
  untouched — recording that the two paths do not exist, that nothing was recovered and why (the four
  rows that would restore corrected readings), that the biology/dependency/expression/exposure/citation
  layers are superseded the ordinary way, that "backup route" is retired as a FRAMING with the four
  pillars mapped to their named papers, that Phase B is retired by the Axis W correction, and that the
  one free survivor is a CHRNA6 filing rather than a route.
- line 161 (PR #3 coordination note): appended a retention — "merged" is true of the framing and false
  of the files.
No file was recovered into the working tree. Nothing outside STRATEGY.md was written.

## WHAT THE OTHER OPTION WOULD HAVE COST
Recovering `research/atlas/**` (39 files) would have put back into the working tree, as live artifacts:
- the RETRACTED 7-junction / exon-2-seam antigen set that `fusion-neoantigen-retraction.json` explicitly
  says "was not padded back to" — the exact "superseded claim restored to apparent currency" failure the
  current HEAD commit (f1d3621fe) is named after;
- the PRAME myxoid 7.6 read that depmap-insilico-findings.md marks INVALIDATED;
- a drug-screen table asserting BOTH USZ models where the primary text says one;
- a B7-H3 #1 ranking that main's surface landscape reads at BH q = 1.0, not selective;
- a 32-source citation map competing with a 237-entry provenance ledger, and a second sample registry,
  a second methods doc and a second deposit policy — direct hits on §1's ONE FACT, ONE PLACE;
- `build.mjs` (does not exist in this checkout — atlas files were read from the branch, not recovered) + `atlas-data.yml`, a second generated-artifact pipeline the commit-loop gates do not know
  about (systems_check's generated-views check, gate 13 and the selector would all need teaching);
- and it would have required frontmatter to be invented for 11 documents whose `last_verified` is
  honestly 2026-07-11, i.e. eight weeks stale, on a repo whose §4 rule is that a remembered reading is a
  dated observation.
Cost of the path NOT taken in the other direction (correcting instead of recovering): the atlas's unique
bytes stay on one branch. That is real but bounded — the branch is not deleted, the census names it, and
this row now tells any reader where it is and why it was not brought back.

### atlas-data.yml (the CI workflow, NOT counted in the 39) -> SUPERSEDED LEG BY LEG
Branch has `.github/workflows/atlas-data.yml` (GEO reprocess + EuropePMC full text + DepMap panel +
MHC-I/II + DailyMed PK). Main's workflow list carries the successors of every leg:
`emc-expression-datasets.yml` (does not exist in this checkout — atlas files were read from the branch, not recovered) (GEO), `fetch-literature.yml` (EuropePMC/PubMed), `depmap-dependency.yml`,
`aso-breakpoint-scan.yml` (does not exist in this checkout — atlas files were read from the branch, not recovered) + `modalities-run.yml` (junction/antigen), `deposit-zenodo.yml` (the deposit leg
DEPOSIT.md only described). Not recovered; nothing is lost that main cannot dispatch today.

### CHRNA6 feasibility, VERIFIED rather than assumed
The atlas's own CI output `_generated/emc-expression-reprocess.json`
-> `datasets[1].platforms[0].known_marker_reproduction.CHRNA6` = {auc 1.0, rank 26, of 23072}, on
GPL6244 with n=42 (EMC 6, other 36), single-channel, 23,072 mapped genes. So a CHRNA6 probe DOES map on
that platform and the read is takeable in main's existing lane at $0.
⛔ But the atlas figure itself is not carryable: it is uncalibrated (main's `nr4a3-fusion-targets.json`
rules "A RAW 'HIGHER IN EMC' IS NOT A RESULT" and requires a size-matched null), and its comparator arm is
all 36 non-EMC samples of the 42-sample matrix where main reads 29. Different contrast, not a smaller one.
Same file also shows GSE4303's seven legacy platforms all at "0 genes" — which main independently
re-established and then SOLVED via an archived UniGene bridge (method-watch-triggers.json), so even the
atlas's honest negative there is superseded by a positive.

## ITEM 5 — THE ST-MORTALITY FINDING IS ON A DIFFERENT BRANCH (task brief was wrong on this)
The brief said `claude/emc-research-strategy-kdz9kn` also carries `ST-MORTALITY-MECHANISM` + six RT-* rows
"in its routes.json". It does not: that branch has **0 paths under `systems/`** at all
(`git ls-tree -r --name-only origin/claude/emc-research-strategy-kdz9kn | grep -c '^systems/'` = 0).
The family is on **`origin/claude/emc-symptom-treatment-742257`** (census §C-10). Verified directly:
  git show origin/main:systems/graph/routes.json | grep -c 'MORTALITY|PALLIATIVE|VTE-PROPHYLAXIS'  -> 0
  git show origin/claude/emc-symptom-treatment-742257:systems/graph/routes.json | grep -oE ... ->
    RT-COMPETING-MORTALITY, RT-EARLY-PALLIATIVE, RT-HOST-FACTOR, RT-RESPIRATORY-FAILURE,
    RT-TREATMENT-HARM, RT-VTE-PROPHYLAXIS  (+ ST-MORTALITY-MECHANISM per the census)
NOT ACTED ON — it is a graph edit, and `systems/graph/` is another agent's lane this session.
⭑ Unlike the atlas this one IS live under §5 (supportive/mortality care for EMC is a route family with no
counterpart on main, not an aggregation of routes that already have papers), and it is the higher-value
recovery of the two.

### ⭑ THE STRONGEST SINGLE PIECE OF EVIDENCE — the junction seam, byte for byte
atlas `_generated/antigen-expanded.md`, EWSR1::NR4A3 modelled seam:  `...SQQSSSYGQQ|PCVQAQYSPS...`
main  `fusion-neoantigen-retraction.json` -> single_breakpoint_artifact.what_was_checked[0]:
        junction_context_right10  got 'NMPCVQAQYS'  want 'NMPCVQAQYS'  ok True
The atlas seam starts the NR4A3 side at `PCV`; the corrected model starts it at `NM` — NR4A3's Met1
survives as an internal residue and one residue precedes it. So the atlas's 34 junction peptides (and its
14 class-II 15mers, seam `...QYSQQSSSYGQQ|PCVQAQYSPSPP...`) are built TWO RESIDUES OFF the junction this
repository now holds. The same artifact's fifth check records "no peptide from the superseded seam
survives in the artifact" -> got [], want [], ok True.
This is not "the programme moved on". It is a byte comparison, and it settles C016/C021/C022 alone.

## PREFLIGHT — the manuscripts-suite failure is CONCURRENCY, not my edit, and not a repo defect
Gate output: "FAILED: pytest reported no test count -- the run collected nothing. AssertionError: the test
run CHANGED tracked files that it did not find changed:  M research/manuscripts/mtap-prmt5/
emc-mtap-prmt5-hypothesis.md  M research/manuscripts/submission-metrics.json" (AUT-PD-186 guard).
⭐ THE DISCRIMINATING OBSERVATION — read the diff, per the guard's own instruction:
  mtap-prmt5/emc-mtap-prmt5-hypothesis.md:171 is an AUTHORED PROSE REWRITE —
    -  "Two public archival series contain this histology and are the only readable EMC expression data."
    +  "Two public archival series carry this histology in a form this array-based reader can score as a
       group of tumours. ⚠ That is a statement about the instrument, not about what exists: ... GSE28866
       (4 EMC), GSE43632 (1), GSE80126 (1) — are unread here because no platform of theirs mapped probes
       to gene symbols, which is an absent reading and never a reading of absence."
  submission-metrics.json: main_words 5213 -> 5277 for that same file — the regenerated count for it.
  mtimes: 01:24:02.276 and 01:24:02.370 — 93 ms apart, i.e. edit-then-regenerate.
No test writes hedged prose citing three GEO accessions. This is another agent editing the tree mid-run.
Corroborating: `ps` showed THREE concurrent preflights (two other `lint_citations.py` (does not exist in this checkout — atlas files were read from the branch, not recovered), two other
`research/manuscripts/tests` pytest runs) at load average 10.5-11.0, and `git diff --stat` shows 75
modified paths of which exactly ONE (STRATEGY.md, 2 insertions / 2 deletions) is mine.
⛔ NOT ABSORBED, NOT FIXED, NOT REVERTED. `git stash` / `git checkout --` are forbidden by this task and
would destroy that agent's uncommitted prose correction. Reported instead.

## FINAL GATE READING
Full `PREFLIGHT_TESTS=1 ./scripts/preflight.sh` completed: **EXIT=1**. Three failures, NONE mine:
  L62  archive-manifest REFUSED: "the manifest on disk records `git_tree_is_clean_apart_from_this_manifest:
       false`" — a provenance refusal; the driver owns the commit-then-regenerate ordering that clears it.
  L89  manuscripts suite: AUT-PD-186 tree-mutation guard — diagnosed above as another agent's authored
       prose edit to emc-mtap-prmt5-hypothesis.md at 01:24:02 mid-run. 1 failed, 1414 passed, 1 skipped.
  L98  scripts/tests/test_affected_tests.py::test_the_committed_record_matches_the_committed_gatekeepers —
       the selector-validation tripwire; clearable only by PREFLIGHT_FULL=1, which §6 reserves for
       publication. Documented in CLAUDE.md §6 as a standing red ("a tripwire clearable only by a rare act
       is a permanent tripwire").
Guards that actually cover STRATEGY.md, re-run directly on the current tree — ALL GREEN:
  lint_consistency   0 ERROR across 27 target files   rc=0   (STRATEGY.md is one of the 27)
  lint_claims        0 ERROR, 172 WARN, 129 files     rc=0
  lint_changed_prose 0 changed passages               rc=0
  systems_check      604 objects, 0 ERROR             rc=0   (no new K3 dead pointer from my links)

## WHAT I WROTE TO THE TREE — ONE PATH, TWO LINES
  /home/user/Rare-cancers/STRATEGY.md   (git diff --numstat: 2 insertions, 2 deletions)
    line 156 — Atlas-anchor reframe row: appended `⚠ Superseded, retained (rule 1.2)` block
    line 161 — PR #3 coordination note row: appended `⚠ Superseded, retained (rule 1.2)` clause
Nothing else. No file recovered from the branch. No git write command run. No commit, no push.

## FILES READ — ALL 39 (extracted to scratchpad/atlas/ via `git show <ref>:<path>`, one path at a time)
Read in full: README.md, STATUS.md, CHANGELOG.md, METHODS.md, REPRODUCIBILITY.md, DEPOSIT.md,
  antiangiogenic-mechanism.md, lineage-antigen-program.md, overview-plain-language.md, outreach.md (part),
  collaborator-brief.md (header/role), dist/*.tsv (all 5, claims + evidence-score + drug-screens in full),
  evidence_score.json (keys + rejected block), citations.json (structure/count), claims.json (via its TSV,
  all 23 claims), samples.json (via its TSV), drug_screens.json (via its TSV),
  _generated/antigen-expanded.{json,md}, _generated/antigen-mhcii.{json,md},
  _generated/emc-expression-reprocess.{json,md}, _generated/panel-exposure.md, _generated/panel-dependency.md
Read at the level of "what it produces" rather than line by line (each is a fetch/scoring script whose
OUTPUT I read in full, which is what the adjudication turns on): build.mjs, antigen_expand.py,
antigen_mhcii.py, expression_reprocess.py, fulltext_verify.py, panel_dependency.py, panel_exposure.py,
_generated/fulltext-verify.json, _generated/panel-dependency.json, _generated/panel-exposure.json,
dist/emc_compound_target_exposure.tsv.
No file was skipped.
