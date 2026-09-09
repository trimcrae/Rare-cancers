---
id: DOC-NEOANTIGEN-4-FINDING
title: "NEOANTIGEN-4 — how many of the 174 junction peptides and 11 ranked binders are genuinely junction-novel, with exact denominators, and a defect in the novelty guard itself"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# NEOANTIGEN-4 — 170/174 and 10/11 against reviewed proteins **with** isoforms; 8/174 peptides and 2/11 binders carry **zero** EWSR1 residues; and the guard that caught the one failure can only ever catch one of the two parents

Paper-level defect audit of the EWSR1::NR4A3 junction screen's **own novelty filter**, on owned data.
Follows **NEOANTIGEN-3** (per-partner residue split for the 11 ranked binders; `DMPCVQAQY` takes zero
EWSR1 residues and is recorded verbatim in NR4A3 isoform Q92570-3) and **PUB-NEOANTIGEN**.

Writes confined to this directory. Nothing added, committed, pushed; no preflight; no manuscript,
graph or shared script edited; no subagents. **No network** — routes B1/B2/B4 stay closed and were
not retried or proxied around.

⛔ Prediction is not presentation. Nothing here is an immunogenicity, presentation, tolerance,
TCR-cross-reactivity, safety, selectivity or clinical claim, in either direction.

## 1 · The question

> Across all **174** junction peptides and all **11** ranked binders, how many are genuinely
> junction-novel — i.e. do **not** occur verbatim in wild-type human protein sequence, counting every
> recorded isoform of NR4A3 and EWSR1 and, where available, the wider proteome? Report the proportion
> with an exact denominator and name every non-novel peptide, its parent protein/isoform and the
> exact offset.

## 2 · Merit

The screen's own filter (`fusion_breakpoints.py`, `emit_junction`: `k not in ews_prot and k not in
nr4_prot`) is a **two-protein, canonical-only** test. Every downstream claim that a ranked peptide is
a *fusion* neoantigen rests on it. A peptide that is verbatim wild-type sequence is not
fusion-specific, so it cannot support a public (off-the-shelf) product argument and it changes what a
future measurement on that peptide could be attributed to. The failure is already **recorded** in this
repository with verdict `BROKEN`, but it has never been quantified as a proportion with a stated
denominator, the offsets have never been assembled in one place, and the *guard that produced the
verdict* has never itself been audited. All three are answerable offline, today, on committed data.

## 3 · Written BEFORE computing — what a high non-novel proportion would and would not license

Recorded in the generator's module docstring before the first execution
(`neoantigen4_novelty_audit.py`, run in `checks/01`), so the reading is not fitted to the outcome.

**It WOULD license exactly one statement:** those peptides are **not fusion-specific at the sequence
level** — a screen that ranked them as fusion neoantigens ranked wild-type self sequence — and any
measurement later made on such a peptide could not be attributed to the fusion.

**It would NOT license any claim about immunogenicity, presentation, tolerance or clinical
usability.** Specifically: a non-novel peptide is **not** thereby shown to be tolerated, ignored, or
unsafe to target; a novel peptide is **not** thereby shown to be presented or immunogenic; central and
peripheral tolerance are not sequence-identity lookups; and no proportion, however high or low,
speaks to a therapeutic window. Equally, a **zero** in the arm this checkout can recompute would be
the **expected** result and would be no reassurance at all (§5.1).

## 4 · The step taken

One offline generator, `neoantigen4_novelty_audit.py`, over four already-committed read-only inputs:
`fusion-breakpoint-neoantigens.json` (`_utc` 2026-08-19T16:26:49Z — the 174 distinct `novel_peptides`
across the 5 in-frame junctions and the 11 ranked binders), `junction-proteome-novelty.json`,
`junction-selfsimilarity.json` (generated 2026-08-23), and the committed sequence caches
`nr4a-sequences-cache.json` / `fet-sequences-cache.json`.

**The wild-type sequence set available in this checkout is smaller than the set
`junction-proteome-novelty.json` used, and this is stated exactly rather than papered over.** That
artifact searched **42,547 reviewed UniProt sequences *with* isoforms**, fetched over the network in
CI. This checkout contains **no proteome FASTA and no isoform sequence of any protein** — the only
wild-type sequences present are **6 canonical proteins**: NR4A3 (Q92570), EWSR1 (Q01844), NR4A1
(P22736), NR4A2 (P43354), TAF15 (Q92804), FUS (P35637), each with its length and sequence hash in the
artifact. So the two strata are reported **separately and never merged**: **A** is recomputed here and
scoped to those 6; **B** is **read, not re-derived**, from the committed artifact.

## 5 · Results — `neoantigen4-novelty-audit.json`

### 5.1 Stratum A — recomputed here, 6 canonical proteins, no isoforms

| arm | denominator | non-novel | novel |
|---|---|---|---|
| junction peptides | **174** | **0** | 174 |
| ranked binders | **11** | **0** | 11 |

**The zero is expected and is not reassurance.** The upstream filter already screens every candidate
against canonical EWSR1 and canonical NR4A3, so a hit here would have meant the filter had failed
outright. What stratum A does establish, and all it establishes: (i) the canonical two-protein filter
was in fact applied; (ii) no peptide is a verbatim NR4A1, NR4A2, TAF15 or FUS wild-type peptide
either — a stratum nobody had checked, and a real if small extension; (iii) **the only recorded
non-novelty comes from an isoform, which is precisely the sequence class this checkout cannot
search.** Point (iii) is carried by a deliberate third control (§5.4).

### 5.2 Stratum B — read from the committed reviewed proteome **with** isoforms (42,547 sequences)

| arm | denominator | non-novel | novel |
|---|---|---|---|
| junction peptides | **174** | **4 (2.3 %)** | **170 (97.7 %)** |
| ranked binders | **11** | **1 (9.1 %)** | **10 (90.9 %)** |

**Every non-novel peptide, its parent protein/isoform, and its offset:**

| peptide | ranked binder | parent protein / isoform | offset (1-based) | offset provenance |
|---|---|---|---|---|
| `DMPCVQAQY` | **yes — the top-ranked binder** (HLA-B\*35:01, weak, 369.1 nM) | NR4A3 isoform 3, **Q92570-3** | **11** | **stated** by `junction-selfsimilarity.json` (exact, 0 mismatches) |
| `DMPCVQAQ` | no | NR4A3 isoform 3, Q92570-3 | 11 | **derived**, not stated (see below) |
| `DMPCVQAQYS` | no | NR4A3 isoform 3, Q92570-3 | 11 | **derived**, not stated |
| `DMPCVQAQYSP` | no | NR4A3 isoform 3, Q92570-3 | 11 | **derived**, not stated |

All four arise at the same junction family (`EWSR1_e9/e10/e12/e13__NR4A3_e3`) and share the prefix
`DMPCVQAQ`; the offset of `DMPCVQAQY` in Q92570-3 is **stated** in a committed artifact, so the other
three necessarily begin at the same residue. That inference is **flagged as derived in the artifact**
and is **not independently verified here**, because the Q92570-3 sequence is not in this checkout.
The four are consistent with the isoform carrying an 11-residue N-terminal extension whose last
residue is D, placing canonical `MPCVQAQY…` at residue 12 — the seam residue the screen counted as
novel is reproduced by the isoform.

**The non-novel one is the top of the list, not the tail of it.** 1 in 11 is a small proportion; that
it is the **rank-1** binder is the part that matters to the paper.

Stratum B's own residual scope, quoted with it: **reviewed (Swiss-Prot) entries only** — TrEMBL was
deliberately not searched — so "novel" there means *absent from reviewed human protein sequence*, not
*absent from every human protein*; and it is a 2026-08-22 snapshot.

### 5.3 The number that is not reassuring — per-partner split, extended to all 174

NEOANTIGEN-3 computed the partner split for the 11 ranked binders. Extending it to the full set:

* **8 of 174** junction peptides contribute **zero residues from EWSR1** — they are one hybrid seam
  residue plus 7–10 residues of wild-type NR4A3.
* **2 of 11** ranked binders are in that class: `DMPCVQAQY` (seam D) and `NMPCVQAQY` (seam N).
* The eight are exactly `{D,N}MPCVQAQ`, `{D,N}MPCVQAQY`, `{D,N}MPCVQAQYS`, `{D,N}MPCVQAQYSP` — the
  `DMPCVQAQ…` half at junction `EWSR1_e9__NR4A3_e3`, the `NMPCVQAQ…` half at `EWSR1_e7__NR4A3_e3`.

**All four stratum-B hits are drawn from this eight.** That is the mechanism, stated as a mechanism
and not as a coincidence: a peptide whose novelty rests on a single hybrid residue is reproduced
verbatim the moment any isoform happens to place that residue before the acceptor's start codon —
which is what NR4A3 isoform 3 does. The remaining four (`NMPCVQAQ…`) survive only because no recorded
reviewed isoform places an N there; that is a fact about the isoform catalogue, not a property of the
peptides, and it would change with the catalogue.

**A discriminator that follows directly, and is not a new claim:** a candidate contributing zero
residues from one partner is not junction-specific and should not be ranked as a fusion neoantigen.
This is a screen-configuration statement. It is **not** offered as a safety criterion.

### 5.4 Controls — the matcher is demonstrated in both directions

| control | peptide | expectation | result |
|---|---|---|---|
| **positive, planted** | `MPCVQAQYS` — the first NR4A3 9-mer window that occurs **exactly once** in the whole corpus | exactly 1 hit, NR4A3 (Q92570), offset 1 | **PASS** — 1 hit, Q92570, offset 1 |
| **negative, scrambled** | `PAQCDVQYM` (seeded shuffle of `DMPCVQAQY`, seed 20260909) | no hit anywhere | **PASS** — 0 hits |
| **positive, blind-spot** | `DMPCVQAQY` | must **miss** locally, because the isoform it hits is absent from this checkout | **PASS** — 0 local hits |

The first attempt's positive control planted `HHHHHHHHH` from NR4A3's 14-residue poly-histidine tract
— degenerate, satisfiable at many offsets, and therefore a weak demonstration. **That run is preserved
in `checks/01`**; `checks/02` runs the tightened, uniqueness-enforced control. Neither run was
overwritten.

Further internal checks, as asserts that fail the run rather than warn: the query sets are exactly 174
and 11; the 11 are a subset of the 174; the committed novelty artifact tests **the same 174 peptides**
(`true` in the artifact, so stratum B is reconciled against the same input); the two sequence caches
**agree** on every gene they share; every peptide is locatable in its own junction context.

### 5.5 A defect in the novelty **guard** itself — new here

`research/modalities/junction_proteome_novelty.py`, line 85:

```python
PARENTS = {"P56945": "EWSR1", "Q92570": "NR4A3"}
```

**Every other module in this repository records human EWSR1 as `Q01844`** —
`nr4a_paralogue_unique_residues.py:54`, `emc_fet_construct_designs.py:113`, `fusion_neoantigen.py:78`,
`emc-construct-inputs.json`, `nr4a-paralogue-unique-residues.json` — and
`junction-selfsimilarity.json`'s own proteome hits name the EWSR1 entries `Q01844`, `Q01844-2`, `-3`,
`-5`, `-6`. (What `P56945` actually designates is not asserted here: this lane is offline and does not
guess an accession's identity.)

**Consequence.** The `⛔_upstream_filter_check` arm can only ever flag **NR4A3**. A junction peptide
occurring verbatim in wild-type EWSR1 **or any EWSR1 isoform** would still be counted in
`n_found_in_proteome`, but would **not** appear in `parent_protein_hits` and would **not** trip the
`BROKEN` verdict — the guard silently covers one parent instead of two.

**Impact on the committed result: none on the headline counts.** All four recorded hits are Q92570-3,
so the verdict is `BROKEN` either way, and `4/174` and `170/174` stand. The defect is in the guard's
**coverage**, not in the numbers.

**Why the test suite does not catch it:** `tests/test_junction_proteome_novelty.py` builds its
synthetic FASTA with `>sp|P56945-2|EWS_HUMAN …` — the fixture bakes in the same accession, so
`test_an_isoform_hit_counts_and_is_flagged_as_a_parent` passes on the wrong identifier. The 9 tests
pass on the unmodified tree (`checks/03`), which is the baseline the proposed change must not break.

## 6 · Artifact · validation · provenance · limitations · stop condition

* **Artifact.** `neoantigen4-novelty-audit.json`; generator `neoantigen4_novelty_audit.py`;
  `UNAPPLIED-junction_proteome_novelty-parent-accession.diff`; `checks/` (3 attempts, real exit codes,
  including the superseded weak-control run, which is preserved and not overwritten).
* **Validation / baseline.** Three controls, two positive and one negative, all reported in the
  artifact and all required to pass (§5.4); the positive control is enforced **unique** in the corpus,
  so "found at the right offset" is not satisfiable by a degenerate tract. Asserts on both
  denominators, on the binder⊂peptide relation, on cache agreement, and on the identity of the 174
  peptides between this lane and the committed artifact. The existing repository tests for the audited
  script are run unmodified as the baseline (`checks/03`, 9 passed).
* **Provenance.** All four inputs read in place from the existing checkout; nothing copied, nothing
  fetched, no repo copy or worktree. Cost **$0** — no network, no GPU, no paid API.
* **Limitations.**
  1. ⛔ No immunogenicity, presentation, tolerance, safety, selectivity or clinical claim (§3).
  2. **Stratum A's denominator of wild-type sequence is 6 canonical proteins**, because that is what
     this checkout holds. It cannot reproduce, confirm or contradict stratum B, and its zero must never
     be quoted as "no junction peptide is wild-type".
  3. **Stratum B is read, not re-derived.** Its correctness is the committed artifact's, not this
     lane's; this lane checks only that it was computed over the same 174 peptides.
  4. Three of the four offsets are **derived** from a fourth that is stated. Marked as such.
  5. Exact substring only. No mismatch tolerance, no I/L isobaric arm, no post-translational or
     splice-variant reasoning. A near-self peptide is not covered here — that is
     `junction-selfsimilarity.json`'s question, and 8 of the 11 binders have near-self hits there.
  6. TrEMBL is outside both strata, so "novel" never means "absent from every human protein".
  7. The transcript-model junction sequences are this repository's own.
* **Stop condition.** Reached. The proportion is answered with exact denominators in both strata, every
  non-novel peptide is named with its isoform and offset, the mechanism (§5.3) is quantified over the
  full 174, and the one new defect is a one-line change for the owner. The next move is not another
  offline computation.

## 7 · Proposed, UNAPPLIED — no shared file was edited

`UNAPPLIED-junction_proteome_novelty-parent-accession.diff` adds `Q01844` to `PARENTS` and **keeps**
`P56945`, so the guard can only catch **more**, never less, and the existing fixture-bound test stays
green. **No guard, floor, gate, matcher, pin or test is weakened anywhere in this lane.** Whether to
apply it is the paper owner's call.

Two statements the paper owner may wish to consider, each to travel with §6's limitations:

1. *"Of the 174 junction peptides, 170 (97.7 %) and, of the 11 ranked binders, 10 (90.9 %) are absent
   from all 42,547 reviewed human protein sequences including isoforms; the exceptions are four
   peptides of the `DMPCVQAQ…` family, among them the top-ranked binder `DMPCVQAQY`, which occurs
   verbatim at residue 11 of NR4A3 isoform 3 (Q92570-3) and is therefore not fusion-specific."*
2. *"Eight of the 174 candidate peptides, including two of the eleven ranked binders, contribute no
   residue from EWSR1: their novelty rests on the single hybrid seam residue, and all four peptides
   found in the wild-type proteome are drawn from that class."*

## 8 · Next credible independent work (not done here, not authorised here)

1. **Apply the zero-partner discriminator inside `fusion_breakpoints.py`** and re-emit the panel — the
   change is to a *screen*, not to a presentation claim, and it removes 8 peptides and 2 ranked binders
   including rank 1. It should be made as an explicit, separately-reported filter, never a silent one.
2. **Apply the `PARENTS` diff and re-run the CI novelty job**, so the guard covers both parents; add a
   fixture using `Q01844` so the test can actually fail if the map regresses.
3. **Re-run stratum A against isoform sequences** on the CI runner (networked), which would let the four
   offsets be verified rather than derived, and would test the `NMPCVQAQ…` half against the same
   catalogue.
4. The manuscript's novelty sentence and `pinned-figures.json` should be checked against `170/174`
   before either is quoted again — not done here, as both are outside this lane.
