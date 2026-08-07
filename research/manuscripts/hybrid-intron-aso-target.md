---
id: DOC-HYBRID-INTRON-ASO
title: "The EWSR1::NR4A3 hybrid intron as a fusion-exclusive ASO target — the premise, graded"
level: L3
kind: memo
status: live
canonical_for: ["the hybrid-intron lane's fusion-unique budget and its head-to-head against the exon-junction gapmer panel"]
purpose: >
  Grade the single premise that put the hybrid intron at rank 5 of the unexplored-lane sweep —
  "kilobases of sequence existing in no other transcript" — against the repository's own committed
  record, and say plainly whether it rescues the exon-junction ASO route that was refuted on
  2026-08-06.
scope: >
  L3. Sequence arithmetic and composition only. No potency, no knockdown, no delivery, no
  tolerability, and no efficacy, safety, therapeutic-window or clinical claim is made or implied.
  An ASO design is a sequence proposal, never a therapeutic claim.
audience: [maintainers, autonomous research agents, external reviewers]
date: 2026-08-07
last_verified: 2026-08-07
---

# The hybrid intron as a fusion-exclusive ASO target — the premise, graded

> ⛔ **NOTHING HERE ASSERTS EFFICACY, SAFETY, A THERAPEUTIC WINDOW OR CLINICAL READINESS FOR EMC.**
> Every sequence discussed is a design hypothesis. Predicted specificity is not validated
> specificity, and delivery — the route's dominant gate — is untouched by anything below.

Machine-readable record: [`hybrid-intron-model.json`](../modalities/hybrid-intron-model.json),
produced by [`hybrid_intron.py`](../modalities/hybrid_intron.py). **$0** — CPU only, committed
inputs, no network call, no GPU, no rental.

## 1 · Why this was worth checking, and against what

The exon-junction gapmer route was regenerated at the corrected mRNA junction on 2026-08-06 and the
corrected screen **refuted its headline**: `n_oligos_no_true_cleavage_risk = 0` and
`n_candidates_zero_offtarget = 0` at **both** graded junctions
([`junction-aso-offtarget-e7n3.json`](../modalities/junction-aso-offtarget-e7n3.json),
[`-e12n3.json`](../modalities/junction-aso-offtarget-e12n3.json),
[`aso-insilico-evaluation-e7n3.json`](../modalities/aso-insilico-evaluation-e7n3.json),
[`-e12n3.json`](../modalities/aso-insilico-evaluation-e12n3.json); the retraction and its lifting
are in [`fusion-junction-aso-paper.md`](./fusion-junction-aso-paper.md)).

[`emc-unexplored-treatment-lanes.md` §3.5](./emc-unexplored-treatment-lanes.md#35--the-hybrid-intron)
proposes the hybrid intron as the rescue, on one premise, quoted in full:

> "the fusion **pre-mRNA** has a second unique feature that is far larger: the **hybrid intron**,
> EWSR1 intron 7's 5′ portion joined to NR4A3 intron 2's 3′ portion. That sequence exists in no
> other transcript in the body. … there are **kilobases** of it."

If true, that premise attacks exactly the weakness the refutation exposed. **It is not true**, and
the reason is an identity rather than a measurement — which is why this memo could be written
without the network and why no screen result should be quoted as if it had tested it.

## 2 · The coordinate convention, verified before anything was built on it

This lane has been burned twice by coordinate defects
([`junction_aso.py`](../modalities/junction_aso.py) → the two-defect block): a table keyed by
**coding** exon indexed with a **transcript** exon number, and a CDS-to-CDS concatenation that
discarded the 2 nt of NR4A3 5′UTR the fusion transcript retains. Both live in the same two-rank gap,
so this module re-derives the convention from committed artifacts and **raises** on disagreement
rather than restating it.

| | value | consequence |
|---|---|---|
| EWSR1 `ENST00000397938`, donor exon | transcript rank **7** = coding rank **7** | the two schemes coincide, which is why the 2026-08-06 off-by-two reproduced *correctly* on this side and stayed invisible |
| NR4A3 `ENST00000395097`, acceptor exon | transcript rank **3** = coding rank **1** | transcript exons 1–2 carry no CDS |
| "NR4A3 intron 2" here | the intron **5′ of transcript exon 3** | naming the same intron by coding rank gives **"NR4A3 intron 4" — a different piece of DNA** |
| NR4A3 exon-3 5′UTR the fusion retains | **2 nt** | reproduced from `emc-construct-inputs.json` (cDNA 697 → CDS at 699) and cross-checked by 953 − 951 in `nr4a3-exon-audit.json` |

Both transcript models passed `junction_aso.transcript_model`'s four sequence self-checks **and**
the `nr4a3-exon-audit.json` provenance gate before the table above was emitted.

⭐ **And the instrument in hand is the one that produced the record being compared against —
checked, not assumed.** `regeneration_check` rebuilds **both** committed exon-junction design panels
from the committed transcript cache and compares them design-for-design: `designs_identical: true`
and the same seams (`ACGGGCAGCAGA|ATATGCCCTGCG`, `AATGGTTTGATG|ATATGCCCTGCG`) at both. A
head-to-head against a record this code could no longer reproduce would be worthless, and that is
the precise state the 2026-08-06 retraction was found in.

## 3 · What the hybrid intron actually is, and how much of it is fusion-unique

**What it is.** The intron 3′ of EWSR1 transcript exon 7, truncated at the genomic breakpoint, joined
to the intron 5′ of NR4A3 transcript exon 3, truncated at the same breakpoint. Its **length in
nucleotides is UNMEASURED here** — that needs an Ensembl genomic read the dev sandbox's egress proxy
refuses (re-measured 2026-08-07: CONNECT to `rest.ensembl.org` and `api.genome.ucsc.edu` both fail).
`hybrid_intron.py mode=ci` measures it; §7 says exactly what is owed.

**How much of it is absent from every wild-type transcript — the load-bearing answer.** It does not
depend on that read.

- The hybrid intron is composed **entirely** of wild-type EWSR1 intron-7 and wild-type NR4A3
  intron-2 nucleotides. Every one of those bases is present, base for base, in the unspliced
  pre-mRNA of the wild-type alleles — including the wild-type allele **in the tumour cell itself**.
- So an oligo window that does not span the intronic breakpoint is a **perfect, full-length match to
  a wild-type pre-mRNA**. Not a near-match with two mismatches — an identity.
- The only novel sequence is the windows that **straddle** the breakpoint. For an oligo of length
  *L* that is exactly **L − 1** windows, and for an RNase-H gapmer, which additionally needs the seam
  inside its central DNA gap, exactly **GAP − 1**.

⛔ **And the compartment argument eats itself.** An intron is a target *only* because it exists in
nuclear pre-mRNA. The wild-type introns exist in the same compartment, in the same nucleus. *"It
exists as pre-mRNA"* and *"its sequence does not exist in the wild type"* cannot both be true of the
same bases.

## 4 · The head-to-head, on the axis that decides it

| | exon junction (mRNA) | hybrid intron (pre-mRNA) |
|---|---|---|
| fusion-unique windows, 16-mer | **15** (= L − 1) | **15** (= L − 1) |
| RNase-H-usable windows, 5-6-5 | **5** (= GAP − 1) | **5** (= GAP − 1) |
| designs in the committed panels | **5** at E7::N3, **5** at E12::N3 | not applicable — no panel exists |
| lane memo's claim | ~20 nt | *"kilobases"* |
| shared across patients with the same exon pair | **yes** — splicing normalises every intronic DNA breakpoint in a given intron pair to one mRNA seam | **no** — the intronic breakpoint is the position of a DNA double-strand break and is not so normalised |
| screen result | `n_oligos_no_true_cleavage_risk = 0` at both junctions | **UNMEASURED** (§7) |

The predicted budget is checked against the committed panels rather than asserted: both panels carry
exactly `GAP − 1 = 5` candidates, and `hybrid_intron.unique_budget()` **raises** if they ever stop
agreeing, because a head-to-head against a panel it cannot model would be meaningless.

**Verdict. The hybrid intron does not clear the bar the exon junction failed, and it does not change
the bar.** The fusion-unique budget is identical — 5 usable windows, not kilobases; the surplus it
appeared to offer is wild-type pre-mRNA of a ubiquitously expressed gene; and the seam it does offer
is **per-patient**, where the mRNA seam is shared. On the axis that motivated the lane, moving from
exon to intron **loses** ground.

## 5 · The honest mechanistic complication, stated rather than papered over

A pre-mRNA intron is a **nuclear, transient** target: splicing is largely co-transcriptional, so the
intron is present at a small fraction of the steady-state transcript pool, while the exon junction is
present in every copy of the mature fusion mRNA for as long as it survives. Two mechanisms are
available and they are **not** interchangeable.

| mechanism | available? | what it costs in confidence | do the panel's metrics transfer? |
|---|---|---|---|
| **RNase-H1 gapmer** against the intron | yes — RNase-H1 is nuclear-active and gapmers do act on pre-mRNA | effect size becomes a **kinetic** quantity: the oligo must direct cleavage before the intron is excised. Nothing in this repository measures that rate. An identical-looking screen result therefore supports a **weaker** conclusion here than at the exon junction | **yes, unchanged** — `classify()`'s gap logic and the `n_true_cleavage_risk` family apply as written |
| **steric-block SSO** at a splice element (branch point, PPT, poison/cryptic exon) — what §3.5 actually proposes | yes, and it is the mechanism with clinical precedent in other diseases | its liability is **occupancy, not cleavage**; its endpoint is mis-splicing, not transcript loss; it needs a splice-effect predictor (SpliceAI/Pangolin/MaxEntScan) and an accessibility screen this lane has not built | **no** — reporting `n_true_cleavage_risk` for an SSO is a category error. Not substituted with a different metric here |

⭐ **The one piece of real support the lane has, reported at full strength and no further.** This
repository already holds a cited record that a real TAF15::NR4A3 fusion *"retains a short cryptic
exon located in NR4A3 intron 2 (ENST00000395097.6 isoform), thus encoding 25 additional amino acids
prior to the NR4A3 ATG"* (PMC6766969, quoted in
[`emc_fet_construct_designs.py`](../modalities/emc_fet_construct_designs.py) →
`TAF15_NR4A3._reported_variant_not_modelled`). That supports the **biology** of §3.5's pseudoexon
idea — a cryptic exon inside NR4A3 intron 2 is used in at least one reported EMC fusion. It does
**nothing** for fusion-exclusivity: that cryptic exon's sequence is wild-type NR4A3 intron 2, so an
SSO promoting its inclusion acts on wild-type NR4A3 pre-mRNA on the same terms. Its sequence is not
held here — an absent reading, not a reading of absence.

## 6 · Running the committed screen on an intron target — what applies and what does not

Task discipline: if the screen cannot be applied without modification, say exactly why rather than
substituting a different metric. Three of its four assumptions fail; the fourth is why the seam arm
*can* be reported with identical metric names.

| assumption | exon junction | intron | why |
|---|---|---|---|
| the database contains the compartment the drug acts in | ✅ | ⛔ | `refseq_rna` (BLAST) and `GCF_000001405.40_*_rna.fna.gz` (`aso_insilico`) are **mature transcript** sets. Neither contains introns, so the largest liability class — wild-type pre-mRNA — is invisible to both. **Running them unchanged yields a low off-target count by construction.** An absent reading is not a reading of absence |
| a hit to a parent gene is benign | ✅ | ⛔ | measured, not asserted: `junction_aso_offtarget.is_parent()` returns **True** on a perfect 16/16 gap-spanning hit to wild-type EWSR1, and `screen_one` counts off-targets over `not is_parent(h)`. `classify()` grades that same alignment **`true_cleavage_risk`**. So the intron arm's fatal liability is filtered into `n_parent_or_intended_hits` and the oligo scores clean |
| the seam is shared across patients | ✅ | ⛔ | see §4. No EMC breakpoint-position distribution is held here, so the spread is **UNMEASURED**, not assumed wide |
| the gap-resolved RNase-H classification is meaningful | ✅ | ✅ | RNase-H1 is nuclear-active, so the gap logic transfers unchanged |

**Consequence, and it is the reason this memo exists in this shape:** an unmodified run of the
committed screen against intron-body windows would have returned a *clean* number and it would have
been an artifact of the database and the parent filter, not a result. That is the precise shape of
failure this repository keeps re-learning.

## 7 · What is unmeasured, and what would close it

Nothing above rests on the unmeasured items — they would refine the record, not change the verdict.

1. **EWSR1 intron 7 and NR4A3 intron 2 lengths, GC, and GT…AG boundaries.**
2. **The hybrid intron's measured fusion-unique extent** against both parent loci (prediction: L − 1;
   a *smaller* number would mean repeat content makes even the seam windows non-unique, which would
   make the lane worse, not better).
3. **The intronic seam's composition and its five gapmer windows**, and the same gap-resolved BLAST
   screen the exon-junction panel ran, reported under the identical metric names.

All three are one `workflow_dispatch` away: `aso-offtarget.yml`, input `hybrid_intron: true`
(`HYBRID_INTRON_MODE=ci`). ⚠ **They were not run in this session** because dispatching a workflow
requires the branch to exist on `origin`, and this session was instructed not to push. That is a
routing constraint, not a capability gap, and it is stated here rather than left as a silent gap.

⚠ **The prior on item 3 is poor, and it is measured rather than assumed.** §3.5's stated attraction
is that the intron *"directly attacks the known GC-rich-junction weakness"*. The GC-rich seam is real
but belongs to the **codon-space modelled** breakpoint, not to the junctions that were actually
graded. Read out of the committed panels against this repository's own favourable GC band
(40–60 %, imported from `junction_breakpoint_scan.GC_FAV_LO/HI`, never typed):

| junction | design GC range | designs inside the favourable band | `n_oligos_no_true_cleavage_risk` |
|---|---|---|---|
| E7::N3 | 50.0 – 56.2 % | **5 of 5** | **0** |
| E12::N3 | 37.5 – 43.8 % | 3 of 5 | **0** |

So the exon-junction route is **not** failing on composition. It is failing because a seam yields
only `GAP − 1` windows and a 16-mer allowing two mismatches has near-matches across the
transcriptome. **Moving the seam into an intron does not lengthen the window.**

## 8 · What this route is now, and the paper it belongs to

Per the rule that every route names its paper: this is **not** a new publication endpoint. It is a
**negative that belongs inside `PUB-ASO`** — the fusion-junction ASO manuscript — as the section that
closes the "target more of the fusion" escape hatch, because a reader who accepts that manuscript's
refutation will ask exactly this question next. One sentence for the field's record:

> *In EWSR1::NR4A3, the fusion-unique sequence available to a hybridisation-based oligonucleotide is
> set by the seam, not by how much of the fusion is transcribed: the hybrid intron adds kilobases of
> target but no additional fusion-unique window, because its bulk is wild-type pre-mRNA present in
> the same nuclear compartment — and unlike the spliced exon junction, its seam is per-patient.*

What is missing and should be said with it: no measured intron length or seam composition (§7), no
splice-effect prediction, no accessibility or occupancy screen for the SSO arm, and no EMC breakpoint
distribution. And `BLK-DELIVERY` is untouched — none of this speaks to getting an oligonucleotide
into an EMC tumour.

---

*Map edits routed as [`hybrid-intron-map-edits.json`](./hybrid-intron-map-edits.json).*
