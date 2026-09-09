---
id: DOC-PORTFOLIO-INVESTIGATION-PUB-HLA-COVERAGE
title: "PUB-HLA-COVERAGE lane — is the coverage build's upstream allele-frequency snapshot identifiable?"
level: L4
kind: report
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# PUB-HLA-COVERAGE — source-identification investigation

Run 2026-09-08T23:58Z – 2026-09-09T00:15Z. Writes confined to this directory. No shared file, no
manuscript, no graph entry and no artifact under `research/modalities/` was modified; the frozen
manuscript was read only.

## 1. The question

`hla-coverage.json` was built by fetching the AFND mirror at run time. The mirror table is **not
retained in this repository and no retrieval date was recorded**, so the frozen handoff states that
a reader "cannot identify which upstream snapshot they came from". **Is that gap real, or is the
snapshot recoverable post hoc from the mirror's public history — and does a retrieval today still
reproduce the frozen numbers, or a later, different analysis?**

This is a SOURCE question. It is not the manuscript's held evidence gap (`BLK-ANTIGEN-COLD`, the
absence of any measured presentation or immunogenicity result), and nothing here touches it.

## 2. Paper-level merit

Every figure in the manuscript, and every figure in `coverage-uncertainty.json` that the vaccine-path
paper reuses, is arithmetic over one 6.3 MB table fetched from a mirror at an unrecorded moment. If
that snapshot is unidentifiable, the coverage numbers cannot be re-derived from source, cannot be
diffed against a later AFND state, and cannot be re-used by anyone else with a stated provenance —
which is the reusability the endpoint's `what_it_would_claim` rests on. If it *is* identifiable, a
recorded reproducibility limit is cured at essentially no cost, and the manuscript's stated
staleness risk can be replaced by the correct one. Patient relevance is indirect and honest: this
changes whether a population-eligibility ceiling is checkable, not whether any patient benefits.

## 3. The exact gap, and how it differs from work already done

Already completed elsewhere, and deliberately **not** repeated here: the same-locus independence
error, the distribution-free (Fréchet) cross-locus LD bounds, and the between-population spread are
all computed in `research/modalities/coverage_uncertainty.py` → `coverage-uncertainty.json`. The
uncertainty axis is largely answered; the **source-identity** axis was not.

Unfinished inputs at the start of this lane, named exactly: the AFND mirror table
(`_source_urls.allele_frequencies`) with `_source_status` "AFND frequencies retrieved from
MIT-licensed mirror" and **no date field**; the region map (`_source_urls.region_mapping`), likewise
fetched live and not retained; and the manuscript's limitation 3, which asserts that "a refreshed
retrieval would give a different model estimate on a later date."

## 4. Step taken and result

**Result: the snapshot is identified, and the frozen build reproduces exactly from live sources
today.**

1. The mirror's history was read (blobless clone, no corpus re-fetch): **`afnd.tsv` has exactly one
   commit in the repository's entire history** — `af3f00bf8d05c25081634e5857ee536f520eefee`,
   2023-03-15T16:03:08Z, "concatenate into one file". The repository's most recent commit of any
   kind is 2024-04-22 and touches only `README`. The data file has therefore been immutable since
   2023-03-15, well before this project's build.
2. The live file fetched on 2026-09-09 is 6,282,337 bytes, sha256
   `2436932578b04ded18a06b11788557c7660ee893e5bd93f4bf8c79e898bbe80c`, git blob
   `036b93ee314c9f58b70272b0198216602c3f1ef2`, and that blob **is** the blob at the mirror's HEAD.
3. Re-pooling it through the paper's own producer functions (`hla_coverage.load_afnd`, live region
   map) reproduces the frozen artifact **exactly**: all four alleles' pooled frequency, Wilson
   interval, carrier frequency, population count, pooled individuals and per-population range are
   identical, `unassigned_populations` and `unassigned_individuals` are both 0 as recorded, and all
   16 sub-regions' per-allele frequencies match, including the three `null` (UNKNOWN) leaves, which
   are compared as null-equals-null and never as zero.
4. Second input, same treatment: the region map's `all/all.json` last changed **2024-06-19**
   (`99cdae15…`, blob `1e67efc0021eeccacb6f35c6f3dcdc85057f9d9e`, repo HEAD `145f1ad3…`,
   2024-06-30), so it too was static before the build.

**What this corrects.** Limitation 3's claim that a refreshed retrieval "would give a different
model estimate on a later date" is, measured, false: it gives this estimate. The real residual
source risk is the opposite one — the mirror is a frozen 2023-03-15 republication that will **not**
track later AFND revisions, and mirror-versus-AFND fidelity remains unverified. An unapplied diff
replacing limitation 3 with the measured wording is included; **it was not applied**, because the
manuscript is frozen for an independent review.

## 5. Artifact · validation · provenance · limitations · stop condition

* **Artifact.** `snapshot-identification.json` (the identification and the full comparison),
  `verify_snapshot.py` (re-runnable, ~30 s, network only), `PROPOSED-limitation3.unapplied.diff`
  (unapplied), `checks/01`–`09` with command, stdout, stderr and real exit code for every attempt.
* **Validation / baseline.** The baseline is the committed frozen artifact
  `research/modalities/hla-coverage.json`; the test is field-level equality against a fresh
  computation, not a narrative comparison. Two independent identifications agree: git history (one
  commit, ever) and content hash (live blob = HEAD blob). The comparison is falsifiable and did
  fail informatively on its first run — the null leaves — which is preserved in `checks/07` and
  fixed in `checks/08`.
* **Provenance.** `github.com/slowkow/allelefrequencies` (MIT) `afnd.tsv`; ISO 3166 / UN M49 map
  `github.com/lukes/ISO-3166-Countries-with-Regional-Codes` `all/all.json`; both reached by ordinary
  public access. No denied or closed source was approached. AFND itself was **not** queried.
* **Limitations.** (a) This identifies the *mirror* snapshot; it does not verify that the mirror
  faithfully reproduces AFND, and it says nothing about AFND's own survey quality. (b) No retrieval
  timestamp exists in the artifact, so identification is by immutability plus exact value match, not
  by a recorded fetch. (c) The 6.3 MB table was **not** committed (storage fence); the pin is the
  hash pair above, and it fails if the mirror repository is deleted or its history rewritten.
  (d) Nothing here affects binding, presentation, immunogenicity, `BLK-ANTIGEN-COLD`, or any
  clinical claim; the coverage figures remain modelled projections. (e) The same-locus and LD
  approximations are untouched by this work.
* **Stop condition.** Reached. The question is answered decisively in both directions it could have
  gone; the only remaining act is editorial (apply the diff after the review unfreezes) and is the
  paper owner's, not this lane's. No follow-on computation is proposed.

## 6. Scope fences observed

Backlog item **B8** (adding HLA-C) was not proposed, renamed or approached, and whether MHCflurry
2.1.4 scores HLA-C remains UNKNOWN and untouched here. No producer under `research/modalities/` was
re-run to write an artifact, nothing was committed, and `scripts/preflight.sh` was not run.
