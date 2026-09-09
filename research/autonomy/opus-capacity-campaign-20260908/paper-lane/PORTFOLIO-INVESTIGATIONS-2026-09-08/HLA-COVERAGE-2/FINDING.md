---
id: DOC-PORTFOLIO-INVESTIGATION-HLA-COVERAGE-2
title: "HLA-COVERAGE-2 — what the ten-allele screen could cover, and the one locus it could not"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# HLA-COVERAGE-2 — the panel's population ceiling, the validated pairs it could not return, and a producer that has drifted ahead of every committed artifact

Follow-through lane on **PUB-HLA-COVERAGE** (which identified the coverage build's upstream AFND
snapshot), **EPITOPE-BENCHMARK** (n = 15 validated fusion-junction class I epitopes) and
**NEOANTIGEN-3** (which first observed that the screen's panel omits HLA-C entirely).

Writes confined to this directory. Nothing added, committed or pushed; `scripts/preflight.sh` not
run; no manuscript, graph entry, producer or committed artifact modified; no subagents; **no
network, no GPU, no paid API, cost $0**.

⛔ **Route B8 (HLA-C) is CLOSED and was not approached.** No HLA-C data was fetched, proxied or
substituted from any source. Every HLA-C population quantity below is reported **UNKNOWN**, never
zero, and the consequence of the exclusion is stated rather than worked around.

⛔ **No claim about immunogenicity, presentation, efficacy, safety, selectivity, therapeutic window
or clinical readiness is made anywhere in this lane.** "Coverage" here is allele **carriage** under
an arithmetic model the manuscript itself records as unjustified. A pair "the screen could not
return" is a statement about the screen's **configuration**, nothing else.

## 1 · The question

> Given the neoantigen screen's actual ten-allele panel: what fraction of a modelled population do
> those allotypes cover, and what fraction of the **experimentally validated** fusion-junction
> epitope–allotype pairs was the screen **structurally unable** to return — each quantified against
> a frequency source **already present in this checkout**, with its exact path and sha256?

## 2 · Merit

The vaccine-path manuscript's §2.3 already reports that its coverage figures "move with the panel",
and states that "extending the panel further can only raise them, so none of them is a ceiling".
That hedge is correct about **width** and silent about **locus**. The distinction matters at
paper level because it converts an open-ended caveat into a bounded, checkable statement: the panel
is A/B-only, an HLA-C-restricted fusion-junction epitope is a **known-to-occur** outcome in the
published record, and therefore one whole locus of the class I system is missing from the
instrument rather than merely under-sampled. That is a defect in a screen's configuration, and
configuration defects are fixable — unlike `BLK-ANTIGEN-COLD`, which this lane does not touch.
Patient relevance is indirect and honest: this changes what a screen could have found, not whether
any patient benefits.

## 3 · The exact evidence gap, and what distinguishes it from prior work

Done elsewhere and **not** repeated: PUB-HLA-COVERAGE identified the AFND mirror snapshot and showed
the frozen build reproduces from it; NEOANTIGEN-3 observed the panel/validated-allotype mismatch
qualitatively (4 of 7 allotypes, 5 of 15 pairs, no HLA-C). Neither attached a **population number**
to either side, and neither re-derived the counts independently.

The unfinished inputs, named exactly: `_predictor.alleles` in
`research/modalities/fusion-breakpoint-neoantigens.json` (never compared to a frequency table);
the `allele_frequencies` block of `research/modalities/coverage-threshold-curve.json` (28 alleles,
never used outside its own curve); and the restriction fields of the 15 validated records in
`EPITOPE-BENCHMARK/epitope-records.json` (counted but not re-parsed).

## 4 · Step taken

One offline generator, `panel_coverage.py`, over six read-only inputs. **Every number a prior lane
reported was re-derived here from the underlying artifact**, including EPITOPE-BENCHMARK's inclusion
rule (re-implemented, not imported) and the manuscript's two committed headline coverage figures.

## 5 · Results

### (a) The panel's own allele list, verbatim from the artifact

`research/modalities/fusion-breakpoint-neoantigens.json` · sha256
`ae1ba4f7216a11a956ed978035557c9226826dd93c09a5bcec3421a39d3eec0c` · field `_predictor.alleles`
(MHCflurry **2.1.4**, models release 2.2.0, lengths 8–11, strong ≤ 0.5 / weak ≤ 2.0 presentation
percentile):

```
HLA-A*01:01  HLA-A*02:01  HLA-A*03:01  HLA-A*11:01  HLA-A*24:02
HLA-B*07:02  HLA-B*08:01  HLA-B*15:01  HLA-B*35:01  HLA-B*44:02
```

**n = 10. Loci present: A and B. HLA-C allotypes in the panel: 0.** Reproduces NEOANTIGEN-3.

### (b) Coverage against the validated epitope–allotype pairs

Re-deriving EPITOPE-BENCHMARK's rule in this lane's own code returns **15** validated epitopes —
the same 15 — over **7** distinct two-field allotypes and **15** two-field epitope–allotype pairs.

| | count | allotypes |
|---|---|---|
| pairs on a panel allotype | **10 / 15** | A\*02:01 ×5, B\*07:02 ×3, A\*24:02 ×2 |
| pairs **outside** the panel | **5 / 15 = 33.33 %** | A\*68:02, B\*40:01, C\*04:01 ×2, C\*12:03 |
| of those, HLA-C pairs | **3 / 15**, across **2** epitopes | E18 `DKESEEEVS` (C\*04:01 **and** C\*12:03), E20 `IFDRYGEEV` (C\*04:01, MS-eluted) |

**A digit that reproduces but should not be quoted as a coincidence.** "15 pairs" equals "15
epitopes" only because **two offsetting effects cancel**: E18 contributes **two** restrictions
(C\*04:01 and C\*12:03), and E26 (`PYGYDQIMPK`) contributes **zero** two-field restrictions because
its record states only the one-field label `HLA-A24`. This lane refuses to silently promote a
one-field label to a two-field allotype, and reports it separately. Under the alternative accounting
that admits E26 at one-field resolution — where `A24` **does** match the panel's A\*24:02 — the
totals are **16** pairs, **11** in panel, **5** out, i.e. **5/16 = 31.25 %**. NEOANTIGEN-3's 5-of-15
is reproduced exactly; the arithmetic behind it was not previously stated.

Parenthesised "(also bound X in vitro)" clauses (E10, E13) are **in-vitro binding, not restriction**,
and are dropped — recorded in the artifact so the choice is auditable.

### (c) Coverage against a population frequency table — one is present, and it is A/B-only

**A frequency table IS present in this checkout.**
`research/modalities/coverage-threshold-curve.json` · **138 647 bytes** · sha256
`b2b80247bf377a05d8a38c3a5823e3d0e330424248d9369ca317f8ef9b78673b` · field `allele_frequencies`:
**28 alleles**, AFND-pooled `allele_frequency`, `n_populations`, `total_individuals` and
per-population range. Upstream: AFND 2020 [Gonzalez-Galarza *et al.*] via the MIT `slowkow/allelefrequencies`
mirror — the same snapshot PUB-HLA-COVERAGE identified. **Loci in the table: A and B only. HLA-C
allele frequencies present anywhere in this checkout: NONE.**

*Cross-check (passes):* on the three alleles it shares with
`research/modalities/hla-coverage.json` (sha256 `3b40a86392404800f6a0a5d5a701ecff49a168823ab067192ce2c5826d4acf9f`)
the two sources are **identical field for field** — frequency, CI, carrier, n, range.

*Model, and its stated defect:* carrier = 1−(1−af)², set coverage = 1−∏(1−af)². This is the
manuscript's own formula, and **§2.3 of the manuscript records it as an unjustified approximation**
(the product runs over same-locus alleles that are not independent draws; A/B linkage disequilibrium
is unmodelled). Wilson intervals exist upstream but §2.3 **withdraws** them; none is quoted here.
Distribution-free (Fréchet/Bonferroni) bounds are given alongside every model figure.

| set | freq known / requested | independence-model coverage | reading | distribution-free bounds |
|---|---|---|---|---|
| **the 10-allele panel** | 8 / 10 | **0.6413** | **LOWER BOUND** | [0.2806, 0.9416] |
| validated allotypes **in** panel | 2 / 3 | 0.3480 | lower bound | [0.2806, 0.3743] |
| validated allotypes **outside** panel | 2 / 4 | **0.1257** | **LOWER BOUND** | [0.0864, 0.1294] |
| all 7 validated allotypes | 4 / 7 | 0.4299 | lower bound | [0.2806, 0.5036] |
| manuscript all-strong base set | 3 / 3 | **0.2737** | exact | [0.1241, 0.3029] |
| manuscript e7::e3 public set | 1 / 1 | **0.0851** | exact | — |

**Re-derivation of the committed headline numbers: both reproduce digit for digit.**
`coverage_any_strong_binder_allele` committed **0.2737**, re-derived **0.2737**;
`coverage_e7e3_public` committed **0.0851**, re-derived **0.0851**. The manuscript's model and
frequencies are therefore confirmed independently in this lane.

**Two honest UNKNOWNs, not zeros.**
* **A\*11:01 and A\*24:02 have no frequency in this checkout**, so the panel's ceiling is a **lower
  bound**: ≥ 64.13 % under the model, exact value **UNKNOWN**. Note A\*24:02 is one of the panel
  allotypes that *does* carry validated junction epitopes.
* **C\*04:01 and C\*12:03 have no frequency in this checkout, and route B8 is closed**, so the
  population carrying an out-of-panel validated allotype is ≥ 12.57 % with the HLA-C contribution
  **UNQUANTIFIABLE from this checkout**. The consequence of the exclusion, stated plainly: the size
  of the population for whom an HLA-C-restricted junction epitope would be the relevant one cannot
  be computed here, now or later, without re-opening a closed route.

**The reading that matters.** The panel's own ≥ 64.13 % is the **ceiling on any coverage figure this
screen could ever have produced**; the manuscript's headline 27.37 % is 42.7 % of that ceiling. The
ceiling is itself locus-truncated: it is a ceiling over A and B, and the class I system has three
loci.

### (d) An unlooked-for finding: the producer has drifted ahead of every committed artifact

`research/modalities/coverage_scan.py` defines `PANEL = PANEL_AB + PANEL_C` = **34 A/B + 18 C = 52**
alleles, with an `AUT-079` comment describing the HLA-C broadening. **Every committed artifact
records 34, A/B only:** `epitope-allele-matrix.json` `panel` n = 34 (`_note`: "broad HLA-A/-B
panel"), `epitope-allele-loose-matrix.json` n = 34, `coverage-curve.json` `panel_size` 34; none
carries the `alleles_without_a_model` field the producer emits when a panel allele is unscorable.
The manuscript's "34-allele expanded scan" therefore matches the **artifacts**, and the arbitrated
digit **34** is independently confirmed here — while **re-running the committed producer today would
not reproduce any committed number**, because its panel is now 52. Git cannot date the divergence:
all six files land in one squashed `-s ours` merge (`14a3f172d`, 2026-09-04), so **relative ordering
is UNKNOWN** and is not asserted. **This lane did not run the producer** — doing so would be
route B8. It is recorded as a reproducibility divergence for the paper owner.

## 6 · Artifact · validation · provenance · limitations · stop condition

* **Artifact.** `panel-coverage.json` (machine-readable: panel, per-epitope restriction parse, all
  coverage blocks with per-allele carrier frequencies, the cross-check, the re-derivations, the
  producer/artifact divergence); generator `panel_coverage.py`; `PROPOSED-panel-locus-limit.unapplied.diff`
  (**UNAPPLIED**); `checks/01`–`04` with command, stdout, stderr and real exit code for every
  attempt, **including the failed one** (`checks/03`, exit **128**, hand-written diff rejected as a
  corrupt patch; regenerated in `checks/04`, exit **0**).
* **Validation / baseline.** (i) The two committed headline coverage numbers are the baseline and
  both reproduce to 4 dp from an independent implementation — so the model and frequencies used here
  are demonstrably the manuscript's. (ii) The two frequency sources are cross-checked field for
  field on every shared allele and an `assert` fails the run if they disagree. (iii) The validated
  set is rebuilt by re-implementing EPITOPE-BENCHMARK's rule, and independently returns 15.
  (iv) Every set with a missing frequency is labelled **LOWER BOUND** in the artifact, not reported
  as a point estimate. (v) Distribution-free bounds accompany every independence-model figure, so no
  number rests on the assumption the manuscript itself refuses to sign off.
* **Provenance.** All six inputs read-only from the existing checkout, each recorded with path,
  byte count and sha256 in the artifact's `_provenance`. Upstream of the frequency table: AFND 2020
  via the MIT `slowkow/allelefrequencies` mirror, the snapshot PUB-HLA-COVERAGE pinned. Offline;
  no network call was made or attempted; **$0**.
* **Limitations.** ⛔ Carriage, not presentation — nothing here says any peptide is presented,
  immunogenic, safe, selective or clinically usable, and nothing here speaks to EWSR1::NR4A3
  presentability in either direction. (i) The coverage model is the manuscript's own, and the
  manuscript records it as unjustified; the direction and size of its bias are not established.
  (ii) **Global pooling only** — the frequency table carries no sub-region breakdown for the panel
  alleles, so every figure in §5(c) is a pooled global figure and the per-region spread (60.4 % to
  1.4 % on the base set) is not reproduced for the panel. (iii) Frequencies are missing for 2 of 10
  panel and 3 of 7 validated allotypes; those are UNKNOWN. (iv) The 15 validated epitopes are
  published **positives** across nine oncoproteins, ascertainment-biased toward A\*02:01 and 9-mers,
  and a lower bound on the literature; **none is EWSR1::NR4A3**, and no inference about a tenth
  fusion follows from nine others. (v) "Structurally unable to return" means *this panel could not
  emit that allotype*; it does not mean a person carrying it presents nothing.
  (vi) Restriction parsing drops in-vitro co-binding clauses and refuses one-field promotion — both
  choices are recorded, and the alternative accounting (5/16) is reported alongside.
* **Stop condition. Reached.** All three requested quantities are delivered, two of them as honest
  bounds with the UNKNOWN named; the panel and both headline numbers reproduce; the only remaining
  acts are a paper owner's (the unapplied diff) and a re-run decision that is route B8 and therefore
  closed. **No follow-on computation is proposed by this lane.**

## 7 · Proposed, UNAPPLIED

`PROPOSED-panel-locus-limit.unapplied.diff` adds one paragraph to
`research/manuscripts/neoantigen/emc-vaccine-development-path.md` §2.3, immediately after the
existing "extending the panel further can only raise them" sentence, stating that both panels are
A/B-only, that 3 of 15 validated epitope–allotype pairs are HLA-C-restricted, that 5 of 15 sit
outside the ten-allele panel, and that the magnitude of an HLA-C arm's effect is **UNKNOWN** here
for want of any local HLA-C frequency. It **was not applied**; `git apply --check` returns **0**
(`checks/04`). Whether it belongs in the manuscript is the paper owner's call, and it must travel
with §6's limitations.
