---
id: DOC-OPUS-CAMPAIGN-TCIP-FINDING-MAP
title: "TCIP F01–F13 — finding-to-edit map"
level: L4
kind: record
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# TCIP F01–F13 — finding-to-edit map

One row per finding. **M** = `research/manuscripts/tcip/tcip-induced-interface-preprint.md`,
**S** = `research/manuscripts/tcip/tcip-induced-interface-preprint-si.md`. Anchors are section
numbers in the revised files. Every retained count, rate, interval and source byte is unchanged;
what changed is what is claimed from them.

---

## F01 — the census and the sampler do not use the same distance predicate

**Edit.** M §2 is a new section that tabulates the two predicates separately: the sampler's grid
lower bound (`field.min_dist(point) - field.cell_slack`, `cell_slack = sqrt(3)×0.9/2 = 0.7794228634 Å`),
its anchor clearance, hard-clash break, 6-soft-clash budget, 12-contact floor and whole-body unit,
against the census's exact nearest-atom distance, identical radii, chain-pair unit and absence of any
admission rule. The analytic non-identity example (a probe at a cell centre with exact distance 4.0 Å
is a census contact and a sampler soft clash at lower bound 3.2206 Å; probes beyond the exact 6.0 Å
boundary can enter the sampler band) is stated as an example about definitions, not a remeasurement.
S §S1 gives the full admission predicate and S §S2 the census predicate, with the same non-identity
paragraph. M §5c reports the retained scores against the value 12 as **hypothetical arithmetic
between two differently defined quantities**.

**WITHDRAWN.** "Measured under the sampler's own contact predicate"; "the same three distance bands
and the same query points the placement loop uses"; every "fails the floor" defined as *would be
rejected by this sampler's predicate*; "the real transcriptional CIP fails it in both directions".

**Qualified.** The retained 6/7 and 4-residue values are kept verbatim as exact-distance chain-pair
observations.

## F02 — acceptance is probability under a non-uniform proposal, not measured orientation volume

**Edit.** M §3 states the implemented radial draw `r = L_min + (L_max-L_min)·U^(1/3)`, the
uniform-shell-volume alternative, and the retained arithmetic at the 12-atom rung (`L_min = 3.75`,
`L_max = 15`; implemented P(r ≤ 9.375) = 0.125 against 0.232142857). It records this as a
comment-to-implementation discrepancy in the audit and states explicitly that the retained run is not
relabelled. S §S1 repeats it under "The proposal, as implemented". Both name what the numbers are:
observed proposal-acceptance fractions conditional on the proposal, twelve fixed anchors, one target
frame and distance field, and one rung.

**WITHDRAWN.** "0.896× the orientation space"; "25 % more admissible orientation space"; any reading
of the body-free grid-volume quotient as a common-measure or survival probability; any equilibrium,
binding or linker-realizability reading.

**Not done.** No rerun, no recomputation, no relabelling of the retained run.

## F03 — the census omits zero-contact ligand-bridged pairs and obscures 9MZA's chain topology

**Edit.** M §5a and S §S2a give the five-stage selection flow, with **stage 4** named as the
zero-contact-band filter applied to both directions **before** induced-pair selection, and marked as
selection on the measured outcome. M §5b and S §S6a map 9MZA completely: entity 1 BCL6 on chains A
and C, entity 2 p300 on B and D, `A1BUC` in two copies of 81 heavy atoms, author-defined hetero 4-mer
A2B2 with author-provided FRET evidence recorded in source metadata. All five ligand-spanned
candidate pairs are listed with disposition: A/B and C/D dropped at stage 4 (profiles not retained),
A/C excluded by name as the constitutive BCL6 BTB dimer and retained as the 71/66 control, A/D and
B/C retained and reported. The omission is stated as an inference from code and retained record, and
the text says explicitly that it must not be recoded as absent source, parse failure, absent ligand
bridge or biological inactivity. Reported denominator for this entry: **two of four** non-constitutive
ligand-spanned candidates.

**Ligand contacts corrected.** The per-copy `chains_touched` table is printed: `A1BUC` on chain A
touches A 33, B 42, C 18; `A1BUC` on chain C touches A 16, C 33, D 40. So 33/42 describes the **A/B**
attachment and 33/40 the **C/D** attachment — the two pairs dropped at stage 4. For the reported
pairs the directional counts are 16 and 40 (A/D) and 42 and 18 (B/C).

**WITHDRAWN.** "The bridging ligand ... contacts 33–42 atoms' worth of each partner" as a statement
about the reported interfaces. The dominant A–B/C–D counts are **not** transferred to A–D/B–C.

**Qualified.** "Two crystallographically independent copies" is kept only in that crystallographic
sense and is replaced elsewhere by "two related interface instances inside one deposited A2B2
assembly".

## F04 — the controls and one-system structure do not establish a calibrated or biological floor

**Edit.** Title, front matter, abstract and role blocks are rewritten to scope inheritance to **one
toolchain** throughout (M title, `purpose`, `scope`, §1). M §5d and S §S6 describe the BCL6 dimer
readings as dynamic-range and consistency observations, and the residue counts as construct coverage,
now sharpened with source metadata (UniProt 5–129 and 1040–1161, construct tags, BCL6 sequence
conflicts at 8/67/84, 470 modeled and 76 unmodeled of 546 deposited monomers). The 3.6–6.0 Å shell
restriction is stated: closer probes are clashes, so this is not atomic contacts, buried surface area
or an interaction network. M §5e frames the 15 selected degrader/glue pairs as a selected list with
dependent copies.

**WITHDRAWN.** "The small number is a property of the interface, not of the instrument"; "a property
of the interface rather than of a short chain"; "bounds the floor from above"; the ubiquitin-transfer
necessity reconstruction (M §1); "a threshold that would reject a substantial share of its own
modality's solved ternaries is ... uncalibrated"; the recruiter-clustering inference.

**Preserved.** The n = 1, one-crystal-form and no-activity limitations, now consistent with the
affirmative claims.

## F05 — paired design and uncertainty claims exceed the retained summary statistics

**Edit.** M §4 prints the retained accepted/drawn counts (583, 651, 6,315, 5,632, 57,657, 45,990, all
of 720,000) beside the ratios 0.895545 / 1.121271 / 1.253686. S §S5 adds a pooled-counts table with
the stored marginal Wilson intervals. Both state the sampling unit, the fixed anchor strata, the
pooling, the common-random-number design (`random.Random(777 + pose_index)` reused across arms and
floors), and that **no cross-arm joint acceptance counts are retained**, so the joint covariance is
missing and no paired interval can be computed. The floor-12 interval overlap is reported as a
marginal fact that does not test the ratio. The 40,000-draw result and the two-process
byte-identity check are labelled historical author-reported checks whose original records were not
available here, with the note that shared seeding means a longer run may contain a shorter run's
prefix.

**WITHDRAWN.** Treatment of the rounded sign change as a significance claim; independence inferred
from identical anchors or byte determinism; convergence inferred from stable seeds; the reruns as
independent support.

## F06 — the cross-run disagreement cannot be dismissed by offset cancellation

**Edit.** S §S1 keeps `DISAGREES`, 19 inside and 5 outside of 24, and the artifact's 1.20 expected
figure, and then states why that expectation does not hold: the old values are themselves Monte Carlo
estimates (1,000,000 draws per compared cell against 300,000), and the 24 pointwise comparisons were
not calibrated as one family-level test. The status stays identifiable under its original rule.

**WITHDRAWN.** "A level offset between this module and the earlier committed run cancels in every
ratio reported here." Replaced with the algebra: `(a+c)/(b+c) = a/b` only when `c = 0` or `a = b`
(0.90 → 0.91 at the retained illustrative values), and no run-bias model is established.

**Not promoted.** The reviewer's illustrative two-estimate diagnostic (five interval violations → three
standardized differences above 1.96) is recorded as an illustration and explicitly not a replacement
acceptance test and not an author replication result.

## F07 — the four-body comparison does not identify the controlling variable or a universal size effect

**Edit.** M §4a and S §S5 keep the rung table, the 0.858–0.972 span, the 0.877 and 0.896 values, and
the within-class 1.421× against between-class 1.165×, and then state that **this design identifies no
controlling variable**: two bodies per class differing in shape, multimeric extent, ligand pivot and
exit geometry as well as residue count, and within-class spread exceeding a between-class contrast
does not refute a size contribution. Monotonicity is restricted to what the filter guarantees — each
arm's accepted count is non-decreasing as the filter relaxes, and the retained marginal counts are
nested — with the note that a ratio of two such functions need not be monotone and three floors are
three points. Anchor selection is described as a geometric-eligibility and spacing construction around
a modelled pocket, conditioning the comparison.

**WITHDRAWN.** "Body size is not the controlling variable; the individual body's shape and
exit-vector geometry is"; "the entire measured penalty is the induced-interface requirement"; "it is
monotone in the floor"; "a gate no tested body has ever failed"; "a gate that cannot fail carries no
information"; "any admitting answer is therefore an upper bound on what a nucleus would allow".

## F08 — the residue interpretation reverses the inequality

**Edit.** M §6 and S §S2 state that up to two probes exist per residue (CA and side-chain centroid,
CA reused for glycine), that the loop increments per probe, and that 12 probes can be supplied by
**between six and twelve** distinct residues — six being the minimum, not a maximum. The retained
values are reported separately as 6 and 7 contact-band probes and 4 distinct residues per side. For
completeness the text records 4/6 = 2/3 and 4/12 = 1/3 and states there is no single conversion, and
that a probe count is not a count of interatomic contacts.

**WITHDRAWN.** "12 points, as few as 6 residues" used as "a floor of at most 6 residues' worth of
probes"; "roughly half either way"; any title or headline depending on a residue conversion.

## F09 — the literature searches do not establish field-wide absence, prevalence or exclusivity

**Edit.** M §7 and S §S7 restate the searches as bounded retrieval observations. The two retained
indexes are reported as inventories: 100 records with 20 full-text pointers, and 300 records with 51
pointers, verified at metadata level, with the explicit statement that neither carries a query
string, request date, total-hit count, requested limit, pagination history or response envelope, so
whether 100 and 300 are totals or retrieval caps is unresolved and no field absence can be
established. The term counts (0 occurrences of five terms across 20 full texts; `cooperativit*` once
in one file, twice) and the 31/6 split are carried as **historical author-reported results** whose
text files and classifications are not in the retained source set. The queries are described as
unmatched and open-access-selected. The successful entry/abstract joins are cited for what they
support: 9MZA identity, title, X-ray, 2.1 Å, dates, chain assignments, A2B2 assembly and the
citation join to the bioRxiv preprint with the Cell article recorded as an update of that record; and
the abstracts' functional context, with the note that the primary work already discusses the induced
interface's functional relevance.

**WITHDRAWN.** "Two Europe PMC sweeps ... establish that the absence ... is a property of the field
rather than of this search"; the matched-prevalence asymmetry conclusion and the inference that it
explains why the floor was inheritable; "9MZA is findable only by its two proteins"; the EuropePMC
`"9MZA"` hitCount-0 argument as support for anything.

**Source status recorded exactly.** M Appendix B and S §S7 state that
`rcsb_cite_pubmed_42476129.txt` reports **HTTP 400** because search is not enabled on the requested
`rcsb_primary_citation.pdbx_database_id_PubMed` attribute — an **invalid-request outcome about an
unsupported search attribute**, explicitly **not** a negative search and **not** an access denial,
with nothing inferable from it. No retry was made.

## F10 — the selectivity odds identity is transferred beyond its model

**Edit.** M §8 is a dedicated withdrawal section. It states where the identity is derived (binary
Langmuir occupancy `theta_i(D) = D/(D+K_i)` at a shared dose), that its transfer to ternary
induced-complex fraction is not derived there, and gives the algebraic counterexample:
`f_i = D/(K_i + 2D)` when `E/K_E = 1` never reaches 0.5, and `K_on = 1`, `K_anti = 100`, `A = 0.8`,
`B = 0.2` clears the binary threshold of 16 yet cannot reach `A`. It is labelled algebra over a
specified model, not a biological calculation.

**WITHDRAWN.** "The selectivity requirement for this modality is not smaller than a degrader's"; "it
needs the same odds-product difference in induced-complex-fraction space"; the general
ternary-window sufficiency of the binary identity; the anti-target-ceiling ordering. The paper now
states that no selectivity requirement was estimated and that unknown requirements are not evidence
of equal or greater ones.

## F11 — the named-effector contradiction has a derived-reporting cause

**Edit.** S §S1 carries an explicit **Erratum, 2026-09-08**: the populated `★_named_effector`,
`body_geometry` and per-arm blocks are the current-field authority for this paper; the derived
`verdict.★_the_named_effector` field (`NO_NAMED_EFFECTOR_STAGED`, 0 enumerated, "NOT ASKED — none
staged") and the generated reach Markdown are stale. The mechanism is named from source: the
`--refresh-derived` branch calls `verdict(...)` without the named-effector argument, which then
defaults to an empty result, while the full-build path supplies it. Agreement among the three
populated fields is described as internal consistency within one artifact rather than three
independent validations.

**Not done.** No producer run, no named-arm run, no geometry re-run, no edit to the frozen artifact.

## F12 — the reproduction instructions do not identify an executable, immutable input closure

**Edit.** M §10 and S §S8 give the corrected commands. The census requires a corpus directory of
files named `cif_<PDBID>.txt`:
`python3 research/modalities/nr4a3_induced_interface_census.py <corpus-dir> [out.json]`; with no
argument it prints usage and returns **exit code 2**, so the frozen SI's command did not run it. The
enumeration entry point is given with its actual options and with the statement that it additionally
requires staged coordinates, both registries, helper modules and model-derived anchor inputs not
enumerated by the settlement's eight dependency hashes, and that `literature-cache` and
`ci-input/tcip-interface-floor-2026-08-07` are branch names rather than immutable input versions.
S §S8 separates three levels: published tables from retained JSON (reproduces), census re-execution
(needs a corpus not retained as an immutable manifest), original geometry and sampling (does not
close). Stale manifest self-metadata is recorded without rewriting source evidence: the delivered
`SHA256SUMS.txt` declares the empty-file digest for itself while its actual 1,602-byte SHA256 is
`de6eb0e6…ea5610`, and the settlement's `MANIFEST.md` self-entry is stale against an actual 15,854
bytes / `cff7b931…535e88`. The authoritative mmCIF SHA256
`b81668a1eaeb1eb40e74c99b65f093f647fd78eec30cecf201aa83006bc75780` is recorded.

**WITHDRAWN.** Any implication of public archiving, of complete computational closure, or of
independent re-execution of the original geometry. "Deterministic and offline" is narrowed to
pure-stdlib and offline at analysis time, with the note that runtime/date fields prevent general
byte-identity.

## F13 — standalone communication must expose the definitions and results

**Edit.** The six unrendered figure specifications are **removed** from the manuscript and the
removal is registered in M Appendix A item 4, with the frozen revision named as where they remain.
No figures were added. In their place the material definitions are made readable as prose and tables:
the two predicates (M §2), the implemented proposal (M §3), the retained counts and their design
limits (M §4, S §S5), the census selection flow (M §5a, S §S2a), the 9MZA chain map, assembly and
candidate-pair disposition (M §5b, S §S6a), and the class-overlap warning — 9MZA is counted in both
`tcip` and `induced_transcriptional`, so the class rows cannot be summed as independent observations
(S §S3). S §S2 states that the ten `allosteric_curated` pairs from the five nuclear-receptor/
coactivator entries are name-level literature classifications and **do not themselves establish
ligand dependence**. Title, abstract, front matter and limitations were rewritten in one pass around
the final narrowed claim; the primary record for 9MZA is cited for what it actually establishes, with
the abstract-only reach stated.

---

## Cross-cutting: nothing was re-run and nothing was overwritten

No source query, network fetch, denied-route retry or new source acquisition. No geometry, sampling,
statistical-experiment, producer, figure-producer or named-arm run. No test weakened, no guard,
floor, gate, matcher or pin changed. Every numeric input, historical result and source byte is
preserved; the frozen manuscript remains at `f43f1495f40d8aff7b4f34bd385d55aac521a500` in repository
history and byte copies of both inputs are retained beside this map as `BEFORE-*.md`.

## Out-of-scope file inspected, NOT edited

`research/manuscripts/tcip/tcip-interface-floor-sizing.md` (21,346 bytes, SHA256
`f865a51c85a01ad6392d7951492acd48fd8e2a151122063fa6987bf6057ba707`) **still carries several of the
claims withdrawn here.** It was inspected and deliberately left unchanged; see
`SIZING-MEMO-CARRYOVER.md` in this directory for the itemised evidence.
