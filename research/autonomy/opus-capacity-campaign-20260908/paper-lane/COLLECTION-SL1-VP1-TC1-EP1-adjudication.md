# COLLECTION SL1, VP1, TC1 and EP1 — four more distinct papers

Collected 2026-09-08 by the campaign parent. Four independent workers, four distinct manuscripts, all
`claude-opus-5` throughout, all transcripts retained and `cmp`-verified.

| worker | paper | tool pairs (observed) | self-reported |
|---|---|---|---|
| SL1 | `dependency/degrader-vs-synthetic-lethal.md` | 23 / 23 | 23 |
| VP1 | `neoantigen/emc-vaccine-development-path.md` | 43 / 43 | 33 |
| TC1 | `tcip/tcip-induced-interface-preprint.md` | 32 / 32 | 19 |
| EP1 | `endpoint/response-endpoint-indolent-tumours.md` | 34 / 34 | 21 |

Observed counts govern. SL1's self-report is the only one that matches.

---

## SL1 — the degrader-versus-synthetic-lethal comparison

SL1 was asked whether the comparison is symmetric, and found that it is not, on four criteria. The
parent re-derived each claim it acted on:

| claim | parent's read | outcome |
|---|---|---|
| the same DepMap run read Route D's own target and the memo prints it nowhere | `depmap-sarcoma-dependency.json → context_genes` NR4A3: `sarcoma_mean` **0.021**, `sarcoma_frac_dependent` **0.0**, `n_sarcoma` **91** | **CONFIRMED** |
| §2b's denominator is 91, not the 176 it prints | `n_sarcoma_models` = 176, but every `n_sarcoma` field is **91** | **CONFIRMED** |
| the only control that could validate selectivity detection came back weak | `self_validation.BRD9_in_synovial` = n 5, −0.13, `frac_dependent` **0.2** | **CONFIRMED** |
| the structure artifact holds no fusion model | `nr4a3-structure-assessment.json` top-level keys are exactly `_note`, `NR4A3`, `EWSR1` | **CONFIRMED** |
| Pocket 5 has 10 lining residues, not a 129-residue lining | `top_pocket_locale`: `resid_min` 406, `resid_max` 534, **`n_lining_residues` 10** | **CONFIRMED** |

**Applied, eight.** The `[established]` tag on a fusion the artifact does not model is now
`[prediction — repo, wild-type monomers]`. The 91-line denominator is stated. The run's null on
NR4A3 itself is printed, with the note that the same "no DepMap line is EMC" caveat qualifies both
nulls, so the two routes read at equal strength. The controls paragraph no longer says "distrust the
controls, not the headline" — the pan-essential recovery validates essentiality, while the headline
is about selectivity, and the one selectivity control was weak. The E3-availability line says the
cheap check has not been run and is an unrun check rather than a negative result. The verdict now
reads "comparatively better-placed … because the comparator lost support, not because the degrader
gained any".

**SL1's D7 applied in a weaker form than proposed.** Two committed homes disagree on the first-PROTAC
approval year: this memo says 2025, which is the VERITAC-2 publication year, while
`nr4a3-degrader-paper.md:152` records FDA approval as 2026-05-01. Neither can be checked without
opening the FDA page and there is no network. Rather than adopt either, the sentence now **states the
disagreement and says it is not adjudicated here**. SL1's D9 (adding a citation for CFT8634/FHD-609)
was not applied; it is a reference-list decision for the owner.

`lint_style` 46 → 48; the two additions are a `⚠` glyph and one em-dash. Eleven bold emphases my first
pass introduced were stripped.

---

## VP1 — the vaccine development path

VP1 found the hunted failure modes **absent**: no predicted epitope treated as a validated immunogen,
no planned step written as though it happened. Eleven of the twelve round-1 red-team findings are
FIXED IN TEXT rather than parked in a caveat, and the twelfth is at its honest terminal state. That is
recorded as a positive finding.

Three defects, all confirmed by the parent: reference 16 printed "fifteen of the seventeen authors"
where `emc-clinical-registry.json → citations.galitskiy2025emcpembrolizumab.independence` reads "13 of
the 16 authors … the remaining 3 are at the treating centre" and explicitly retains the old wording as
superseded and internally inconsistent; §7's "samples as small as 579" is not a sample size in any
coverage artifact, and the smallest behind a printed regional figure is 450; and `last_verified` was
2026-08-19 while the paper reports an artifact stamped 2026-09-01. All three applied. `lint_style` 0
ERROR before and after.

**Recorded, not acted on.** VP1 measured the paper's argument prose at ~16,585 words against round
1's flagged 7,154 → 8,415 growth, on a span that includes generated tables and so is not method-
identical. Stopping-rule gate 5 is failed by a wide margin. That is a process finding for the paper's
owner, not a scientific defect, and no trimming was attempted here.

---

## TC1 — the TCIP induced-interface floor

TC1 graded twelve transfers and 41 quantities. The parent re-derived the census claims directly:

| claim | parent's read | outcome |
|---|---|---|
| the abstract's "15 ternaries" is 15 induced **pairs** over 8 ternaries | `summary_over_induced_pairs.by_class.degrader_or_glue`: `n_induced_pairs` **15**, `pairs_below_floor_in_at_least_one_direction` **6**, `entries` list length **8** | **CONFIRMED** |
| 6SIS does not read 10–11 on the weaker side across its copies | its two ligand-bridged pairs are (11, 10) `clears=False` and (13, 16) `clears=True` — weaker sides **10 and 13**, and one copy clears | **CONFIRMED** |
| 6HAX is the entry that reads 11 on the weaker side in both copies | ligand-bridged pairs (18, 11) and (18, 11) | **CONFIRMED** |
| 5T35's "10–11" is right | (11, 14) and (10, 14) | **CONFIRMED** |

**Applied, seven.** The abstract's unit is corrected and its uniqueness claim scoped to what the
search located, matching §3's already-correct hedge. §4's 6SIS clause is replaced by 6HAX with 6SIS's
actual split reported. The two-sample-count reproduction is cited to the record that owns it. Appendix
A(1) no longer says in the present tense that the memo records values the memo has already corrected.
§5.4 now states that `bcl6` is excluded from the pooled figures too, so the pooled numbers are named
as `birc2`, `mdm2`, `crbn`, `vhl` only.

**The most important one is TC1's D6**, and it goes to the paper's load-bearing transfer. §1 said the
floor's "justification is a degrader's: ubiquitin transfer requires a cooperative, buried interface".
The source records no such derivation — `nr4a3_basin_search.py:119` carries only the comment "below
this it is a tethered pair, not an interface". The paragraph now presents that reading as the
authors' reconstruction of intent and states the narrower fact the source does establish: the value
has no recorded derivation of any kind.

TC1's D8 and D9 were not applied: D8 adds a citation and a qualifier the owner should place, D9 is a
class-bookkeeping nuance whose numbers are already exact. `lint_style` 54 → 55, the addition being one
glyph.

---

## EP1 — objective response and disease control

EP1 resolved every main-text quantity with **zero** NO SOURCE LOCATED, and found one error by
recomputing rather than by comparing. The parent reproduced that recomputation:

`endpoint-regime-map.json → G6_the_phase_composition_sensitivity.per_condition` has 44 rows. Sixteen
sit at or below the 5 % null. Two have no phase-2/3 arm. Of the remaining fourteen, **thirteen** still
read 0.0 % on phase-2/3 arms only and one (`Solid Tumors`) rises to 21.4 %. The manuscript said
twelve. 13 + 1 = 14, which is the arithmetic the sentence itself needs. **CONFIRMED**, and the
direction favours the paper — one more condition survives the sensitivity than was claimed.

**Applied, six.** The abstract's 31.8–73.9 % bound no longer implies a single 28-condition
denominator for two endpoints computed on different condition sets. The twelve became thirteen. §3.4's
table header now says what its column actually holds — a median over conditions of per-condition
median enrolments, not a median enrolment over the 875/962 records. The 2,027 and 16,035 totals are
labelled with which query each belongs to. §6.1 states the ≤15 % rule that defines its 25 conditions,
instead of borrowing §3's two-axis phrase. And the two desmoid records are no longer presented as
though independence were established: the pooled analysis draws on three studies of which one is
French, and whether its 282 patients overlap the other's 100 is stated in neither report.

**EP1's D2 has a second half the parent did not act on.** The "twelve" is a hard-coded prose string in
`endpoint_regime_map.py:489-490`, three lines from the `per_condition` block that contradicts it. The
manuscript is now right and the artifact's own string is still wrong. Fixing it means editing a
producer and regenerating `endpoint-regime-map.json`, which is a separate act; it is **routed to the
paper's owner, not repaired here**.

**EP1's D6 and D7 were not applied**, and this is a judgement worth stating. D6 would add to §8 that
the EMC pool does not satisfy the four-cell identity §2.3 asserts for every corpus row — one cohort
reports 23 response-evaluable patients whose categories sum to 22, so one patient sits in both
denominators and neither numerator — and would print the artifact's own 46-patient sensitivity
(13.0 % / 91.3 %). D7 would scope "the cleanest point on the map" and disclose that the later cohort
is a conference abstract. Both look right and both change what a headline result means, so they are
**recorded as a blocker rather than applied by the parent**.

**BLOCKER — EMC worked-extreme denominator disclosure.** Paper:
`research/manuscripts/endpoint/response-endpoint-indolent-tumours.md` §8. Measured evidence:
`emc-endpoint-discordance.json → D1_same_patients_two_endpoints` gives 47 patients with 6 objective
responses, 42 disease control and 36 stable disease; 36 + 6 + 4 = 46, and
`D1.sensitivity_immunosarc2_denominator_22.why` records the unreconciled 23-versus-22 cohort.
`D1.per_cohort.sunitinib_nivolumab_immunosarc2.design_tier` reads "CONFERENCE ABSTRACT ONLY". **Exact
reopening condition:** a decision by the paper's owner on whether §8 states the four-cell exception
and prints the 46-patient sensitivity alongside the 47-patient headline, since the paper's title claim
is that the two endpoints are read on identical patients. Nothing else in the paper is blocked.

`lint_style` 0 ERROR before and after.

---

Across all four: `lint_consistency` 0 ERROR across 29 files. No producer, figure generator or
preflight was run, no artifact was edited, and no verdict generalises beyond its own paper.
