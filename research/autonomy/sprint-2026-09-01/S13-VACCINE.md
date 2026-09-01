---
id: DOC-SPRINT-S13-VACCINE
title: "S13-VACCINE — AUT-077's four Stage 0 items were already run; the near-self null turns entirely on position 1"
level: L3
kind: process
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
---

# S13-VACCINE — AUT-077's four Stage 0 items were already run; the near-self null turns entirely on position 1

**Item(s):** AUT-077 (route `RT-VACCINE-COMBINATION`, publication `PUB-VACCINE-PATH`, strategy `ST-IMMUNO`)

**Owned paths (all created this session, none pre-existing):**
`research/modalities/junction_anchor_convention_sensitivity.py`,
`research/modalities/junction-anchor-convention-sensitivity.json`,
`research/modalities/class2_novelty_inheritance.py`,
`research/modalities/class2-novelty-inheritance.json`,
`research/modalities/stage0_vaccine_item_provenance.py`,
`research/modalities/stage0-vaccine-item-provenance.json`,
`research/autonomy/sprint-2026-09-01/S13-VACCINE.md`

**Started (UTC):** 2026-09-01T19:05Z **Finished (UTC):** 2026-09-01T19:25Z

---

## Verdict

**REFUTED, then extended.** All four Stage 0 items AUT-077 asks for had already been run — between
2026-08-19 and 2026-08-24 — and all four are stated in the vaccine manuscript, which is checked here
rather than asserted. Running them again would have been a duplicate. Instead I took the two free
in-silico questions those four leave open and answered both, and the first one materially qualifies a
result the manuscript currently states without qualification: **§B3's "zero of the 11 binders has an
anchor-only near-self neighbour" is not a robust null. It survives the one allele-specific caveat the
producing artifact itself names, and it turns entirely on whether position 1 counts as an anchor —
under any convention that counts P1, 6 of the 11 binders acquire an anchor-only near-self neighbour,
all six in the same NR4A3 isoform.** Whether P1 is an anchor for the five restricting alleles is
UNKNOWN in this repository.

⚠ **And a third finding neither item was looking for: two live documents state OPPOSITE answers to
which anchor configuration deletes the T-cell repertoire** — the manuscript's §B3 says anchor-only is
the failing case, the shared-vs-individualized memo's falsifier 3 says contact positions are. Both
are quoted in §4(c). This is the falsifier my main result speaks to, so **nothing from
`junction-anchor-convention-sensitivity.json` should be written into a paper until it is reconciled**,
and reconciling it belongs to whoever owns the immunological claim, not to this seat.

---

## What I measured

### 1 · The refutation: the four items, their artifacts, and the manuscript lines that state them

`research/modalities/stage0-vaccine-item-provenance.json` (new). For each item it derives the
headline **from the artifact** and then searches
`research/manuscripts/neoantigen/emc-vaccine-development-path.md` for that derived string. An item is
`landed` only if both exist — an artifact whose figure nothing reads is a different state from a
finished item, and the two are separated rather than merged.

```
proteome-wide novelty      landed=True  '170 of 174'@[90, 509, 1169]
class II regeneration      landed=True  '23 class II alleles'@[60, 698], 'SYGQQNMPCVQAQYS'@[508, 701], '66.1'@[508, 701]
anchor-position analysis   landed=True  'Zero of the 11'@[652], '0 of 11 binders'@[507]
extended allele panel      landed=True  '34-allele'@[58, 262, 279, 534, 746, 748, 1243, 1279, 1494]
```

The artifacts, with both dates, because they are not the same thing and conflating them misdates the
work — two of these files were created weeks before the Stage 0 analysis and were **regenerated** by
it, so the creation date understates when the result landed (`git log --diff-filter=A` and
`git log -1`, both read-only):

| AUT-077 phrase | artifact | script | entered repo | last change |
|---|---|---|---|---|
| proteome-wide novelty | `junction-proteome-novelty.json` | `junction_proteome_novelty.py` | 2026-08-19 | 2026-08-19 — *"seam provenance verified, and the isoform collision resolves to four specific junctions"* |
| class II regeneration | `patient-cd4-demo.json` | `patient_cd4_epitopes.py` | 2026-08-04 | 2026-08-23 — *"Close the class II provenance gap the paper had been disclosing…"* |
| anchor-position analysis | `junction-selfsimilarity.json` | `junction_selfsimilarity.py` | 2026-08-23 | 2026-08-23 |
| extended allele panel | `hla-coverage.json`, `coverage-threshold-curve.json` | `hla_coverage.py`, `coverage_threshold_curve.py` | 2026-08-04 | 2026-08-23 — *"Vaccine paper: four CI results written in, three of which change what the paper says"* |

Commit `e6b3da39e` (2026-08-19) is titled, verbatim, *"Stage 0 results: proteome novelty run,
class-II arm regenerated, two defects the run exposed"*. **AUT-077's `last_evidence_utc` is 2026-08-19 — the same
day the first two items landed — and the row has stood `queued` with `attempts: 0` since.** The row
was never wrong about what to do; it was never closed after it was done.

### 2 · New result — the anchor-convention sensitivity of §B3

`research/modalities/junction-anchor-convention-sensitivity.json` (new), from
`junction_anchor_convention_sensitivity.py`. Input: the committed `junction-selfsimilarity.json`. No
network, no predictor, no new search. **$0.**

The construction is exhaustive rather than a sample of conventions: a hit is anchor-only under an
anchor set `A` exactly when its mismatch positions are a **subset** of `A`, so **the mismatch
position set is the minimal anchor set that would flip that hit**, and every superset flips it too.
Named conventions are then labels over that lattice. Mismatch positions are **recomputed from the two
peptide strings**, not read from the artifact's field, and cross-checked against it.

```
P2_and_C_terminus          [sourced]    hits=0  queries=0
P2_P3_and_C_terminus       [sourced]    hits=0  queries=0
P1_P2_and_C_terminus       [UNSOURCED]  hits=6  queries=6
P1_P2_P3_and_C_terminus    [UNSOURCED]  hits=6  queries=6
reproduction agrees with the input artifact: True
disagreements in input bookkeeping: 0
the null turns on positions: ['1']
```

- **13 scored near-self hits** across the 11 binders (14 hit records; 1 is the exact-self
  `DMPCVQAQY`/`Q92570-3` match, excluded from convention scoring because an exact match is a
  *strictly worse* case than anchor-only, and it is the §B5 withdrawal, not a finding here).
- **The reproduction check passes**: under the input artifact's own declared convention this run
  returns the artifact's own per-hit verdicts and its headline `n_anchor_only_near_self_total = 0`.
- **The one caveat the artifact names does not bite.** Its `⚠_anchor_convention` field flags that
  `HLA-A*01:01` reads P3 as a primary anchor. Adding P3 — applied to *every* peptide, the
  conservative direction, since it can only add anchor-only hits — leaves the count at **0**. That is
  a genuine strengthening of B3 and the manuscript can say it.
- **The null turns entirely on P1.** Under a convention counting P1, six hits across six of the 11
  binders become anchor-only:

| binder | near-self neighbour | accession | mismatches at | allele it was called on |
|---|---|---|---|---|
| NMPCVQAQY | DMPCVQAQY | Q92570-3 | P1 | HLA-B\*15:01 |
| RGDMPCVQAQY | NVDMPCVQAQY | Q92570-3 | P1, P2 | HLA-A\*01:01 |
| DLDMPCVQAQY | NVDMPCVQAQY | Q92570-3 | P1, P2 | HLA-A\*01:01 |
| FDDMPCVQAQY | NVDMPCVQAQY | Q92570-3 | P1, P2 | HLA-A\*01:01 |
| GDMPCVQAQY | VDMPCVQAQY | Q92570-3 | P1 | HLA-B\*44:02 |
| LDMPCVQAQY | VDMPCVQAQY | Q92570-3 | P1 | HLA-A\*01:01 |

- **All six are the same accession, `Q92570-3` — an isoform of the acceptor gene itself** — and this
  is not a coincidence of position. Cross-checked against the independent committed artifact
  `novelty-seam-test.json`: for **6 of 6**, the residues shared with the self neighbour, read from
  just after the last mismatch, are exactly an acceptor-isoform **stem** (or a collision-alphabet
  residue followed by one; the alphabet is `["D"]`). The differences *are* the seam.
- **This generalises past this locus, and that is the part worth carrying.** For a fusion-junction
  peptide scored against the acceptor gene's own isoform, the tumour-specific residues sit at the
  seam by construction; for seam-proximal peptides the seam is near the N-terminus. So whether a
  near-self anchor null holds at all is decided by the N-terminal positions' anchor status for the
  restricting allele — a property of the antigen class, not of `EWSR1::NR4A3`.
- **The manuscript's own position on P1, represented fairly, because this is not a straw man.**
  §B3 does not merely adopt a convention; it gives a structural reason: *"Position 1 and position 5
  face outward or into the groove's middle rather than serving as the primary anchors at position 2
  and the C-terminus"*, and it defines the worst case it is excluding as *"an identical TCR-facing
  surface distinguished only by residues the T cell cannot see"*. **That argument is about PRIMARY
  anchors.** It neither asserts nor excludes a secondary-anchor role at P1, and a secondary anchor is
  still a residue the T cell does not read. So the finding here is not that the manuscript is wrong.
  It is that the headline null is worth **exactly** the strength of the P1 premise, that the premise
  is currently carried by one clause, and that if P1 acts as an anchor for these alleles then six of
  the eleven binders fall into the very configuration §B3 names as the worst case.
- **What is UNKNOWN, stated as such:** this repository holds no allele-specific binding-motif source,
  so the true anchor set for `HLA-A*01:01`, `HLA-B*07:02`, `HLA-B*15:01`, `HLA-B*35:01` and
  `HLA-B*44:02` is not known here. The P1 rows are labelled **UNSOURCED VARIANT** in the artifact and
  a count under them is **not** a claim that P1 is an anchor. Settling it needs an allele-specific
  motif dataset, which is a networked fetch nobody has run.

⛔ **What this cannot support.** Nothing here is a safety, presentation or immunogenicity result.
Sequence distance is not T-cell-receptor distance — the input artifact says so itself and it is
repeated in the new one. An anchor-only near-self neighbour is a hypothesis about why a repertoire
might have been deleted, not a measurement that it was.

### 3 · New result — the class II peptides are novel proteome-wide, decided without a new search

`research/modalities/class2-novelty-inheritance.json` (new), from `class2_novelty_inheritance.py`.
**$0**, no network, no predictor.

The gap: §B5's novelty result covers **174 peptides of length 8 to 11 — every one a class I
candidate**. The class II arm's **15-mers were never in that set**, so the paper's novelty statement
and its class II statement are about disjoint peptide sets, and a reader could take the first as
covering the second. It does not.

The class I search is an **exact-substring** search, and absence is inherited upward: if a peptide
occurs nowhere in the proteome, no string containing it occurs either. So a class II 15-mer
containing an already-certified-absent 8- to 11-mer is certified absent **by the search that has
already been run**.

```
class II peptides with a binder call: 13
certified absent from the reviewed proteome: 13
UNKNOWN: 0
strong call SYGQQNMPCVQAQYS on ['DRB1*14:01'] at 66.1 nM -> CERTIFIED_ABSENT_FROM_THE_REVIEWED_PROTEOME
```

Every one of the 13 carries multiple independent certifying substrings (4 to 26 each), and **none
contains any of the four peptides the search found in the proteome**. The inference runs one way
only: a 15-mer whose tested substrings were all found would be reported **UNKNOWN**, never "present"
— no row needed it.

⛔ **What this cannot support.** The 13 are **MHCnuggets binding predictions**, and the manuscript
already grades class II prediction as substantially less accurate than class I; one strong call on
one allele stays a weak positive and novelty does not change its weight. **No near-self search exists
for any class II peptide** — `junction-selfsimilarity.json` covers the 11 class I binders only — and
this does not supply one, so a 15-mer certified absent here may still have a near neighbour in a
normal protein. Two of the 15 candidate 15-mers carry no binder call and are not enumerated in the
committed artifact, so they are reported as outside what this can read rather than counted either
way.

### 4 · Three defects found while checking, in files I do not own

**(a) `research/modalities/hla-coverage.json` is stale against its own generator.** Its
`_class_ii_note` reads *"That screen tested only a **3-allele DR panel** ("* followed by an
interpolated list of **23** alleles. `research/modalities/hla_coverage.py:459–461` was fixed on
2026-08-28 to derive the count (`"only a " + str(len(cd4_panel or [])) + "-allele class-II panel"`),
with a comment recording that the stale count *"was quoted onward into
fusion-junction-neoantigen-paper.md, which is how a wrong number in a note becomes a wrong number in
a manuscript"*. **The generator was fixed; the committed artifact was never regenerated.** Regenerating
it needs the AFND fetch, so it is a CI job, not a local one.

**(b) `research/manuscripts/emc-systems-map.json` contradicts itself about the same screen.** Line
2475, `artifacts` → `ART-HLA-COVERAGE.note`: *"Class-II coverage is a FLOOR over a tested 3-allele DR
panel"*. Line 3767, in the same file's route record: *"a 23-allele DR/DP/DQ panel in which every
declared allele was scored"*.

**(c) ⛔ Two live documents state OPPOSITE answers to which anchor configuration deletes the
repertoire, and this one is not cosmetic — it is the falsifier my §2 result speaks to.**

- `research/manuscripts/neoantigen/emc-vaccine-development-path.md:652–654` (§B3): the worst case is
  differences *"confined to anchor positions, which would have been the worst case: an identical
  TCR-facing surface distinguished only by residues the T cell cannot see"*. **Anchor-only = bad.**
- `research/manuscripts/neoantigen/shared-vs-individualized-neoantigen-evidence.md:332–334`
  (falsifier 3): the route is in trouble if *"The seam residues fall at T-cell-receptor contact
  positions rather than anchors, such that central tolerance to the near-self NR4A3-isoform
  neighbour has deleted the repertoire."* **Contact positions = bad.**

These cannot both be the failing configuration. §B3's version is the one whose stated mechanism is
internally consistent — a surface identical at the residues a receptor reads is the one tolerance
would have acted on — but **I am not adjudicating it here**, because neither file is mine and because
an immunological call of this kind should be made by whoever owns the claim, against a source rather
than against reasoning. What makes it urgent rather than pedantic: the memo introduces its six
falsifiers *"as falsifiers, so that a future session can check them rather than re-argue them"*, so a
falsifier pointing the wrong way will send the next session to the opposite conclusion from the same
data — and my §2 result is precisely the data it would be read against.

Lower priority, flagged not asserted: `hla-coverage-emc.md`, `fusion-junction-neoantigen-paper.md`
and `modality-census/novel-modalities.md` also carry "3-allele DR panel", but all three carry
superseded/subsumed banners, and one of the instances is inside a block quote of an earlier
statement. Someone who owns those paths should decide whether a superseded banner is enough.

### 5 · Mutation test of the two self-checks (charter §7), in a scratch copy

The sensitivity module carries two checks that would otherwise be decoration. Both were broken on
purpose **in a scratchpad copy — never the live tree** — and both fired:

| mutation (scratch copy of `junction-selfsimilarity.json`) | check | live run | mutated run |
|---|---|---|---|
| one recorded `mismatch_positions` `[1]` → `[2]`, peptide strings untouched | `disagreements in input bookkeeping` | 0 | **1** |
| one recorded `all_mismatches_at_anchors` `False` → `True`, positions untouched | `reproduction agrees with the input artifact` | True | **False** |

The counts did not move under the first mutation, which is the designed behaviour: positions are
**recomputed from the sequences** and the recorded field is only cross-checked, so a corrupted
bookkeeping field is reported rather than believed. `git status` on
`research/modalities/junction-selfsimilarity.json` and `novelty-seam-test.json` is empty — the live
tree was never touched.

### 6 · Gates

Charter §6 — scoped, not the whole thing:

```
python3 -m pytest research/modalities/tests/test_artifact_stub_guard.py \
  research/modalities/tests/test_junction_proteome_novelty.py \
  research/modalities/tests/test_coverage_threshold_curve.py \
  research/modalities/tests/test_hla_coverage_seam_provenance.py -q -p no:randomly
32 passed in 0.46s
```

```
python3 research/manuscripts/emc_systems_map_check.py
emc_systems_map_check: 155 registry items · 0 ERROR · 0 WARN
```

No pre-existing file was modified, so nothing else was in scope. `preflight.sh` is the driver's.

All three modules are deterministic: each was re-run after its final edit and reproduced its output
byte-for-byte from committed inputs, with no network, no predictor and no GPU. **Total real-dollar
cost of this seat: $0.**

---

## What I changed

Six new files, all under owned paths. **No pre-existing file was edited.** No git command other than
read-only `git log`.

| path | what |
|---|---|
| `research/modalities/junction_anchor_convention_sensitivity.py` | new — exhaustive anchor-convention sensitivity over the committed near-self search, with the seam-mechanism cross-check |
| `research/modalities/junction-anchor-convention-sensitivity.json` | its output |
| `research/modalities/class2_novelty_inheritance.py` | new — inherits proteome-wide absence upward from the class I search to the class II 15-mers |
| `research/modalities/class2-novelty-inheritance.json` | its output |
| `research/modalities/stage0_vaccine_item_provenance.py` | new — derives each Stage 0 headline from its artifact and checks the manuscript states it |
| `research/modalities/stage0-vaccine-item-provenance.json` | its output — the evidence that closes AUT-077 |
| `research/autonomy/sprint-2026-09-01/S13-VACCINE.md` | this file |

One derivation bug was caught and is recorded in the code rather than smoothed over: the first draft
of the provenance module derived the panel size as **28** from `coverage-threshold-curve.json`'s
frequency table, because that table records a frequency only for an allele presenting something at or
below the curve's 5.0 ceiling. The panel is **34**, defined in `epitope-allele-matrix.json`. Both
numbers are true about different things; the module now reads the panel from the file that defines
the panel and records the 34-vs-28 difference as **a negative reading, not a missing frequency** —
verified by checking that the curve's allele set and its frequency table agree exactly.

---

## What PUB-VACCINE-PATH can now say that it could not before, and at what weight

**Three sentences, all of them qualifications or weak positives. None of them is a new capability
claim, and one of them makes the paper's position weaker.**

1. **"The near-self anchor null survives the allele-specific caveat this paper states against it."**
   Adding P3 — the position the producing artifact flags for `HLA-A*01:01` — to every peptide leaves
   the count at zero. *Weight: real but narrow.* It closes a caveat the paper raised against itself;
   it is still a sequence-distance result under a convention, not a measurement.

2. **⛔ "And the null rests entirely on treating position 1 as a non-anchor: under any convention
   counting P1, six of the eleven binders have an anchor-only near-self neighbour, all six in the
   same NR4A3 isoform, and whether P1 is an anchor for these five alleles is not established here."**
   *Weight: this is the load-bearing one, and it points against the route.* It converts a stated null
   into a null with a named dependency. §B3 rests the point on P1 and P5 not being *primary*
   anchors; this quantifies that **everything** B3 concludes rests on that, and a secondary-anchor
   role at P1 — neither asserted nor excluded there — would be enough to flip it. It answers the question falsifier 3 of
   `shared-vs-individualized-neoantigen-evidence.md` raises — where the seam residues fall — with
   "under one convention at contact positions, under another at an anchor, and this repository
   cannot say which convention applies." ⚠ **That falsifier is stated in the direction opposite to
   §B3; see §4(c) below, and do not build on either wording until it is reconciled.**

3. **"The class II peptides, including the one strong call, are absent from the reviewed human
   proteome."** *Weight: a clean but small positive.* It closes a novelty gap the paper does not
   currently disclose, at zero cost, by inheritance from a search already paid for. It removes one
   failure mode from a result that remains one strong prediction on one allele from a predictor the
   paper itself grades as the weaker of the two, and **no near-self search exists for these peptides
   at all**.

**What is still missing, and what each is actually waiting on** — see the next section. In one line:
the paper's own §6.1 **step 1** (calibrate the acceptance threshold against experimentally validated
epitopes) has **not** been run, and until it is, every coverage figure in B1 remains a point on
`coverage-threshold-curve.json`, exactly as §6.1 says.

---

## What I could not do, and what it is actually waiting on

None of these is "blocked" in the sense CLAUDE.md §0 warns about — each names a specific missing
input, and two of the three are a CI dispatch away rather than a rental or a human.

1. **§6.1 step 1 — calibrate the acceptance threshold against experimentally validated epitopes.**
   Genuinely not run; the threshold-agnostic curve is the *stand-in* the manuscript names, not the
   calibration. Waiting on two things, both free: (a) **MHCflurry, which is not importable in this
   sandbox** — `python3 -c "import mhcflurry"` → `ModuleNotFoundError`; it runs only in
   `.github/workflows/modalities-run.yml`; and (b) a validated-epitope set, which is a networked
   fetch. **A seat may not push a branch or dispatch a workflow, so this needs the driver.** ⚠ It is
   also the item most likely to move the paper, because it is the one that decides whether B1's
   figures survive at all.
2. **The allele-specific anchor motifs that would settle result 2 above.** Waiting on an
   allele-specific binding-motif dataset — a networked fetch, therefore CI. Until then the artifact
   says UNKNOWN, and UNKNOWN is the correct entry.
3. **A near-self search for the class II peptides.** Waiting on the UniProt proteome fetch the class
   I search used (CI, $0). Mechanically identical to `junction_selfsimilarity.py` with a different
   query list.
4. **Regenerating `hla-coverage.json`** to clear the stale note in §4(a). Needs the AFND fetch, so
   CI; and it is not my path.

---

## Ledger rows the driver should write

I may not write these. Proposed:

1. **Close `AUT-077`.** `state: done`, `attempts: 1`, `last_evidence_utc: 2026-09-01`, evidence
   `research/modalities/stage0-vaccine-item-provenance.json` — all four items landed between
   2026-08-19 and 2026-08-24 and each figure is bound to a manuscript line. `kind` should stay as it
   is; the row's `kind: negative` was never what it did.
2. **New row — "Calibrate the vaccine acceptance threshold against experimentally validated
   epitopes, or record that no validated fusion-junction set exists."** `kind: experiment`,
   `state: queued`, `cost_class: free`, serves `RT-VACCINE-COMBINATION` → `PUB-VACCINE-PATH`. This is
   §6.1 step 1 of the manuscript's own ordering, it is the cheapest step that can close the route,
   and it needs a CI dispatch (MHCflurry is not importable locally). **It should outrank anything
   else on this route.**
3. **New row — "Resolve the anchor convention for the five restricting alleles from an
   allele-specific motif source."** `kind: experiment`, `state: queued`, `cost_class: free`,
   `blocked_by`: needs a networked motif dataset (CI). Evidence for why it matters:
   `research/modalities/junction-anchor-convention-sensitivity.json`.
4. **New row — "Run the near-self search for the class II junction peptides."** `kind: experiment`,
   `state: queued`, `cost_class: free`, CI. Evidence:
   `research/modalities/class2-novelty-inheritance.json` → `⛔_the_gap_this_does_not_close`.
5. **New row — "Regenerate `hla-coverage.json`; its committed `_class_ii_note` says *3-allele DR
   panel* where `hla_coverage.py` has emitted the derived count since 2026-08-28."**
   `kind: hardening`, `state: queued`, `cost_class: free`, CI (AFND fetch).
6. **New row — "`emc-systems-map.json` states the class II panel as 3-allele at
   `ART-HLA-COVERAGE.note` and as 23-allele in the same file's route record."** `kind: hardening`,
   `state: queued`, `cost_class: free`, local.

7. **New row — "Reconcile the anchor/contact falsifier: `emc-vaccine-development-path.md` §B3 and
   `shared-vs-individualized-neoantigen-evidence.md` falsifier 3 name opposite configurations as the
   one that deletes the repertoire."** `kind: hardening`, `state: queued`, `cost_class: free`, local,
   **but it needs whoever owns the immunological claim, not a mechanical fix.** Evidence: §4(c)
   above. ⚠ This should be sequenced **before** anything is written into the manuscript from
   `junction-anchor-convention-sensitivity.json`, because the direction of that result depends on
   which framing is correct.

⛔ **Not proposed, deliberately: extending the allele panel further (HLA-C, more class II alleles).**
The manuscript's §6 already answers it — *"A larger allele panel raises a figure without grounding
it"* — and CLAUDE.md §5 defaults such deepening to NO. The panel's HLA-C gap is already disclosed in
the manuscript's Table 2 caption. Running it would raise a number and ground nothing.
