---
id: DOC-OPUS-CAMPAIGN-TCIP-RESIDUAL-LIMITATIONS
title: "TCIP repair — what the revised paper still cannot support"
level: L4
kind: record
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# What the revised TCIP paper still cannot support

Stated plainly. Each item is a limit that survives the repair, not a caveat the prose softens.

1. **No predicate equivalence, and none is obtainable from the retained records.** The census scores
   exact nearest-atom distances on chain pairs; the sampler scores a grid lower bound
   (`cell_slack = 0.7794228634 Å`) on a whole body and then applies anchor clearance, a hard-clash
   break, a soft-clash budget and the contact floor. Nothing in the paper shows how the implemented
   sampler would score or admit any deposited complex. Closing this would need results produced under
   the same grid and query construction, body and target units, excluded constitutive contacts and
   full admission rules, or a proof of equivalence. Neither exists, and neither was commissioned.

2. **Nothing is calibrated or bounded.** Comparing a census score of 6 or 7 against the parameter
   value 12 is arithmetic between two differently defined quantities. It does not bound the filter
   from above or below, and it says nothing about a requirement that induced proximity imposes.

3. **The ratio has no usable uncertainty.** The ablation arms share proposals
   (`random.Random(777 + pose_index)` reused across arms and floors) and no cross-arm joint
   acceptance counts were retained, so the joint covariance is missing and no design-aware interval
   for the ratio can be computed from what exists. The stored Wilson intervals are marginal, pooled
   over fixed heterogeneous anchor strata, and quantify neither ratio precision nor biological
   sampling uncertainty. The reported sign change is a point-estimate ordering, not a significance
   result.

4. **The four-body design identifies no controlling variable.** Two bodies per class, differing in
   shape, multimeric extent, ligand pivot and exit geometry as well as residue count. The paper
   neither establishes nor refutes a body-size effect, and it identifies no cause.

5. **Monotonicity is unestablished beyond three sampled floors.** Each arm's acceptance is
   non-decreasing as the filter relaxes; the ratio of two such functions need not be, and behaviour
   at intermediate thresholds or other rungs is unknown.

6. **The census denominator is selected, and two pairs were removed on their measured score.** The
   zero-contact-band filter runs before induced-pair selection; in 9MZA it removed the ligand-spanned
   A/B and C/D pairs, whose profiles were **not retained** and are not reconstructable from anything
   held here. The reported denominator for that entry is two of four non-constitutive ligand-spanned
   candidates. The 6-of-15 degrader/glue result is a property of a selected list with dependent
   copies, not a population false-rejection rate.

7. **n = 1 for the transcriptional system.** One crystal form, and the two reported interfaces are
   two related instances inside one deposited A2B2 assembly sharing a BCL6 dimer — not two
   independent functional systems.

8. **Construct and crystal-context explanations are not excluded.** Resolved chain lengths, UniProt
   ranges, construct tags, three recorded sequence conflicts and 76 unmodeled of 546 deposited
   polymer monomers describe coverage. They do not show that the relevant full-length interface is
   complete or that unresolved segments do not matter.

9. **The score is not an interface measurement in any conventional sense.** Only probes in the
   3.6–6.0 Å shell are counted; closer probes fall in clash bands. It is not atomic contacts, buried
   surface area, or an interaction network, and its resolution at small interfaces is untested.

10. **The cross-run comparison remains `DISAGREES`.** 19 of 24 committed rates inside the recomputed
    interval and 5 outside, under a rule that treats a Monte Carlo estimate as an exact reference and
    was not calibrated as a family-level test. Cross-run reproducibility is unresolved, and the
    former offset-cancellation defence is gone rather than replaced.

11. **The literature evidence is bounded retrieval.** The two retained indexes have no query, date,
    total-hit, limit, pagination or response-envelope closure, so 100 and 300 cannot be shown to be
    result totals rather than caps. The term counts and the 31/6 classification are historical
    author-reported results whose text files and classifications are not in the retained source set.
    No absence in any field is established, and the two searches were not matched.

12. **One retained citation-query record is an invalid attribute, and stays uninformative.**
    `rcsb_cite_pubmed_42476129.txt` is HTTP 400 because search is not enabled on
    `rcsb_primary_citation.pdbx_database_id_PubMed`. It is not a negative search and not an access
    denial, and nothing is inferred from it. No retry was made or is proposed.

13. **The ten `allosteric_curated` pairs are name-level classifications** from the literature and do
    not themselves establish ligand dependence of those interfaces.

14. **Class totals overlap.** 9MZA is counted in both `tcip` and `induced_transcriptional`; the class
    rows cannot be summed as independent observations.

15. **No selectivity requirement is estimated**, for this modality or any other, and no ordering
    against degraders is claimed. The binary odds identity is not a sufficient ternary-window
    criterion.

16. **Original geometry reproduction does not close.** Published tables reproduce from the retained
    JSON by arithmetic. The coordinate, registry and helper input closure is not retained; branch
    names are not immutable input versions; runtime and date fields prevent general JSON byte
    identity. Nothing is publicly archived.

17. **The named-effector verdict field remains stale in the frozen artifact.** It is covered by a
    dated erratum in SI §S1 naming the `--refresh-derived` cause. No producer, named-arm or geometry
    run was performed, and the artifact was not edited.

18. **The 40,000-draw and two-process determinism checks are historical author reports.** Their
    original records were not available here; shared seeding means a longer run may contain a shorter
    run's prefix, so agreement would not be independent replication.

19. **No biology, and no wet lab.** Nothing here concerns binding, potency, selectivity,
    transcriptional output, efficacy, safety, therapeutic window or clinical readiness for any
    molecule. There is no wet-lab component of any kind, and none is proposed.

20. **One out-of-scope file still contradicts the narrowed paper.**
    `research/manuscripts/tcip/tcip-interface-floor-sizing.md` retains the predicate-equivalence,
    bound, field-absence and discovery-exclusivity framings. It was inspected and not edited; see
    `SIZING-MEMO-CARRYOVER.md`. Until its owner acts, a reader following the manuscript's link will
    find the withdrawn framing there.

21. **Generated views and derived metrics are stale until the parent regenerates them.**
    `systems/views/L3-publications.md`, `paper-strength.md`, `L2-rt-tcip.md`, `L1-st-proximity.md`
    are generated by `systems/systems_check.py` from the graph, and
    `research/manuscripts/claim-coverage.json` holds a sentence census of the old main text. This
    lane changed neither.
