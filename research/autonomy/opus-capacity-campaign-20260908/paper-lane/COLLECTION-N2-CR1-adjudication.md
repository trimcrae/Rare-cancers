# COLLECTION N2 and CR1 — HLA coverage, and the closed-routes negative record

Collected 2026-09-08 by the campaign parent. Two distinct papers, two independent workers, both
`claude-opus-5` throughout.

| worker | paper | transcript | model entries | tool pairs |
|---|---|---|---|---|
| N2 | `research/manuscripts/neoantigen/hla-coverage-emc.md` | `N2-executed-artifacts/ORIGINAL-CHILD-TRANSCRIPT-a60e2561a635cb269.jsonl`, `cmp`-verified | `claude-opus-5` only | 29 / 29 |
| CR1 | `research/manuscripts/methods-record/closed-routes-negative-record.md` | `CR1-executed-artifacts/ORIGINAL-CHILD-TRANSCRIPT-a0b91581cd82f529b.jsonl`, `cmp`-verified | `claude-opus-5` only | 24 / 24 |

Both self-reported 19 tool calls. The transcripts record **29** and **24**. The observed counts govern.

---

## N2 — HLA coverage

N2 graded every main-text quantity in groups A to G and dispositioned both submission-residue
placeholders. The parent re-derived every value it acted on, straight from the artifacts:

| N2 claim | parent's independent read | outcome |
|---|---|---|
| both-arms is computed at 1.78%, not "not computed" | `hla-coverage.json → global.coverage_cd8_and_cd4_combined` = **0.0178** | **CONFIRMED** |
| the class-II arm is 44 predicted binders, 1 strong, over 23 alleles | `patient-cd4-demo.json` → `n_predicted_binders` **44**, `n_strong` **1**, `n_alleles_screened` **23**, `shortlist[0]` = `SYGQQNMPCVQAQYS` / `DRB1*14:01` / 66.1 nM / strong | **CONFIRMED** — the banner said "2 predicted binders, none strong, on three DRB1 alleles" |
| four alleles, not seven | `global.allele_frequencies` keys are exactly `DRB1*14:01`, `HLA-A*01:01`, `HLA-B*07:02`, `HLA-B*15:01` | **CONFIRMED** |
| the coverage curve never reaches 50% globally | `coverage-curve.json` → `panel_size` 34, `presenting_alleles` 4, curve 0.1241 → 0.2062 → 0.2737 → 0.3040, `global_max_coverage` **0.304** | **CONFIRMED**; the text claimed "~50-60% cheaply" from `A*02:01/A*11:01/A*24:02`, none of which is a presenting allele |
| the §3.4 construct is built on the retracted seam | `vaccine-construct.json` → `assembled_window` `PSQYSQQSSSYGQQNMPCVQAQYSPSP`, `minimal_SLP` `SYGQQNMPCVQAQYS` (15 aa), CD8 epitopes both `B*15:01`, CD4 epitopes **one** entry on `DRB1*14:01` | **CONFIRMED** — the printed peptide, its two allele attributions and "4 strong CD4 helpers" were all on the retracted seam |

**Applied (D1 to D11 plus a banner-scope correction).** The author block now carries the identity the
repository actually holds — Tristan D. McRae, unaffiliated, ORCID and correspondence — and the
`[City, Country]` slot was **deleted rather than filled**, because the repository records no city, no
country and no institution, and inventing one was forbidden. That is the disposition N2 proposed and
the parent agrees with it. The two satisfied rows were removed from
`submission-residue-baseline.json`, which now reports `3 findings, 3 baselined, 0 NEW, 0 stale`.

Also corrected: the both-arms row, the class-II counts and panel size in three places, the two
sentences that stated a *predicted* binding as *presentation*, "seven alleles" to four, the §3.3
coverage scan (including a stale placeholder waiting on a scan that is already committed), the §3.4
construct, and two `novel-modalities.md` links that did not resolve from this directory.

The banner's scope was widened. It said "EVERY CLASS-I COVERAGE NUMBER BELOW IS SUPERSEDED"; the CD4
column, the DRB1 rows, the both-arms figure and the per-region sample-size column are none of them
class-I coverage numbers and are superseded too. A reader honouring the old banner literally would
still have quoted wrong numbers.

**NOT applied, and why.** Groups B, C and D are roughly 140 superseded numbers across the Abstract,
the §3.1 allele table and the 16-row §3.2 regional table. The document's own line 47 already
instructs regeneration from `hla-coverage.json` before circulation, and patching them individually
would reintroduce exactly the drift the banner exists to record.

**BLOCKER — HLA coverage prose regeneration.** Paper:
`research/manuscripts/neoantigen/hla-coverage-emc.md`. Measured evidence: every class-I and class-II
coverage figure in the Abstract, §3.1 and §3.2 mismatches the committed `hla-coverage.json` at this
HEAD, and the qualitative direction has reversed in at least two places — Melanesia is now the lowest
computed region for e7::e3 rather than the highest, and the stated CD4-versus-CD8 anti-correlation
does not hold on the current artifact. **Exact reopening condition:** a regeneration of the Abstract,
§3.1 and §3.2 prose from `hla-coverage.json` and `coverage-curve.json` as a single act, replacing the
superseded block rather than patching values one at a time. Nothing else in the paper is blocked by
this.

---

## CR1 — the closed-routes negative record

CR1 gave all seven routes a verdict against a located and read closure record: five SUPPORTED, two
OVERSTATED. The parent re-derived the load-bearing ones:

| CR1 claim | parent's independent read | outcome |
|---|---|---|
| the audit grades RT-FET-LC-LIGAND DEFECTIVE and its ruling was never applied | `AUDIT-2026-08-06-routes.md`: the verdict table row reads `RT-FET-LC-LIGAND \| DEFECTIVE`, and X11 states "**Not applied:** the ruling itself", with S2 "empirical, and it is what actually closes the route" and `BLK-NOT-FUSION-SELECTIVE` "held by 9 routes, three of which are live" | **CONFIRMED** |
| RT-SYNPROMOTER's registered trigger names a capability, not the observation | `routes.json` → `RT-SYNPROMOTER.revival_trigger` = `["TR-VECTOR-TUMOUR-DELIVERY"]`, `closure_kind: premise_false`, `status: parked` | **CONFIRMED** |
| the Iwata hits were checked as named in an abstract, with no IC50 | `fact-check-log.md:51` = "Iwata model screen hits: brigatinib, panobinostat, romidepsin \| Iwata 2025 \| ✓ (221-drug HTS, named in abstract)" | **CONFIRMED** |

**Applied, all five.** §4.1 no longer reports as settled a permanence its own cited audit graded
DEFECTIVE and declined to rule on. §4.3 no longer treats one inspected 2025 paper's silence about
NR4A3 as re-establishing a 1996 negative — the closure still rests on a single measurement no
retrieved source replicates, and the silence of one inspected source is not evidence that no
contradicting evidence exists. §4.4's "the reason it fails is itself a result" is now stated as what
it is, an inference from two committed facts with no EMC binding-specificity measurement in
existence, on a route that inherits `BLK-NO-EMC-DATA` and whose own `remaining_unknowns` says the
absence may be merely unmeasured. §9 discloses the trigger-field mismatch. §4.5's "low-IC50 hits"
became "reported hits", the predicate that was actually checked.

Four bold emphases the parent's first pass added were removed. The file ends at **99** `lint_style`
errors against 98 before: the one addition is a `⚠` glyph, matching the file's own register of 35.
This paper has never had a style pass and does not pass `lint_style`.

---

## Both papers

`lint_consistency` 0 ERROR across 29 files. `lint_claims` clean on both. `lint_submission_residue`
exits 0 with no stale rows. Neither verdict generalises: each is specific to its own paper, and
neither says anything about the readiness of any other manuscript.
