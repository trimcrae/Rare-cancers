# The transfer-anchor conflict, resolved — and how much of the mechanism rests on C397

> **Lane doc (LANE 7).** Two unresolved risks that the Tier-2 GO currently rests on:
> **(1)** the **39 Å transfer-anchor conflict** RUNG 5a recorded as *"the discriminating observation has not
> been run"* — and it now has been; **(2)** whether the categorical chemistry axis is really a **single point
> of failure** at C397.
> Subordinate to [nr4a3-program-map.md](nr4a3-program-map.md); this lane does not edit it. Exact deltas are in §5.
> **$0 realized. No GPU. No GPU is requested.**
>
> Language discipline applies throughout: a surviving basin is a **nomination**, never a "selective hit", and
> nothing here implies efficacy, safety, a therapeutic window or clinical readiness.

---

## 1. The conflict, and the one observation that settles it

RUNG 5a staged VHL twice, from two *verified* receptor entries, and got two answers for where the observed
E2~Ub transfer anchor sits relative to the recruiter's ligand exit vector:

| staging | receptor entry | ligand | anchor → transfer anchor |
|---|---|---|---|
| **registry A** — [`nr4a3-e3-arm-registry.json`](../modalities/nr4a3-e3-arm-registry.json), **the one the authoritative 12-pose run consumed** | 5T35 | MZ1 (het 759, 69 heavy atoms) | **30.85 Å** |
| registry B — [`nr4a3-e3-arm-registry-lane1.json`](../modalities/nr4a3-e3-arm-registry-lane1.json) | 6GMN | F4E (12 heavy atoms) | **69.91 Å** |

Both bridged the *same* intact assembly (**8R5H**) at good RMSD (0.98 Å / 1.33 Å). The lane recorded two
hypotheses and did not separate them: **H1** a different copy selected inside a source structure; **H2**
genuinely different CRL-arm conformers — in which case the transfer zone carries ~40 Å of frame-to-frame
variation and **term (b) weakens further**. Two more are separable only by decomposition: **H3** the two
*exit vectors* are in different places; **H4** the two mapped *E2 positions* differ.

### 1.1 The discriminating observation: a distance that needs no model at all

**8R5H is a solved, intact CRL2^VHL ubiquitylation assembly that contains — in ONE frame, with no
superposition of any kind — VHL + Elongin B + Elongin C, the MZ1 degrader bound in the VHL site, and a
trapped UBE2R2~ubiquitin.** So the quantity in dispute is directly measurable inside that single structure.

The E2 catalytic cysteine is identified the same way the staging identifies it — the SG bearing ubiquitin's
C-terminal glycine — and the answer is again unambiguous: **Cys93 at 4.27 Å from ubiquitin's C-terminus
against 25.73 Å for the runner-up.**

> **GROUND TRUTH (8R5H, zero composition): ligand exit atom `759.CAE` → UBE2R2 catalytic Cys93 = 30.76 Å.**

| staging | reproduced | miss vs the observed 30.76 Å | its exit atom's distance from the exit atom **observed** in 8R5H |
|---|---|---|---|
| **registry A (5T35)** | 30.85 Å | **0.09 Å** | **0.99 Å** |
| registry B (6GMN) | 69.91 Å | **39.15 Å** | **51.41 Å** |

The 0.99 Å is a genuine agreement rather than a coincidence: 5T35 and 8R5H carry **the same ligand** (MZ1,
het 759), so the two derivations of "where does the linker leave VHL" are comparing like with like. They pick
*neighbouring* atoms of it — `CAG` in 5T35, `CAE` in 8R5H — which is exactly the resolution the
furthest-E3-side-atom rule can be expected to have on a 3.44 Å cryo-EM structure versus a 2.7 Å crystal, and
is the scale of disagreement the convention is worth.

**Registry A is right. Registry B's exit vector is not on the VHL ligand site.**

### 1.2 Where the 39 Å lives — the decomposition that kills H1, H2 and H4

Superposing the two receptor copies onto each other (**0.767 Å over 324 Cα**, all three subunits jointly) and
mapping both stagings' quantities into that one frame:

| quantity | value |
|---|---|
| Δ between the two **mapped E2 catalytic cysteines** | **0.02 Å** |
| Δ between the two **ligand exit vectors** | **50.67 Å** |

**The entire disagreement is in the exit vector.** The two bridges land the observed E2 in the same place to
two hundredths of an angstrom, so:

- **H1 (a different copy in the source assembly) — falsified twice over.** Both stagings map the same 8R5H
  conformer to the same point, *and* 8R5H deposits exactly **one** copy of VHL·EloB·EloC (copy selection
  reports `n_combinations: 1, coherent: true`), so there was no alternative copy to select.
- **H2 (different CRL-arm conformers) — falsified.** There is no conformational disagreement to explain.
  **The 39 Å is NOT a second instance of the 48.6 Å composed-RING spread**, and the suggestive numerical
  similarity was a coincidence. Term (b) does **not** carry ~40 Å of frame-to-frame transfer-zone variation
  from this source.
- **H4 (a bridge/copy fault on the 8R5H side) — falsified**, same evidence.
- **H3 — confirmed, and localised to registry B.**

### 1.3 Root cause: the staging never required the recruiter ligand to touch the *recruiter*

Read out of the structure rather than argued:

| | registry A (5T35) | registry B (6GMN) |
|---|---|---|
| chosen ligand | MZ1 (het 759), chain D | F4E, chain B |
| ligand → nearest **recruiter (VHL)** atom | **2.57 Å** | **6.87 Å** (and > 8 Å from *every* VHL chain in the file) |
| 4.5 Å lining of the chosen site | **VHL Trp88, Tyr98, Arg107, His110, Ser111, Tyr112, His115, Trp117** (the HIF-1α hydroxyproline pocket) + the BRD4-BD2 acetyl-lysine site | **Elongin C Glu64, Ile65, Pro66, Val69, Glu102, Met105, Ala106, Phe109 — and no VHL residue at all** |
| chain identity | derived from the file's own sequences, not from the API's labels | same |

`pick_ligand` tested ligand contact against the **BODY** — the recruiter *plus its obligate partners*
(Elongin B/C for VHL, DDB1 for CRBN) — and never against the recruiter. A fragment bound to a partner subunit
therefore passed every check and produced an "E3 exit vector" that is not on the E3 ligand site, silently,
because the exit atom is still ~4 Å from *some* body atom and every downstream distance still looks
reasonable. (6GMN deposits four copies of the complex and two modelled F4E copies; the statement above is
measured for the one the staging **chose**. The other copy was not evaluated against its own copy's VHL and
no claim is made about it — it is simply not the ligand that produced the 69.9 Å.)

**Fixed** in [`nr4a3_e3_stage.py`](../modalities/nr4a3_e3_stage.py): `pick_ligand` now takes
`recruiter_chains` and refuses a ligand more than 4.5 Å from the recruiter, recording
`ligand_min_dist_to_recruiter_A`, with a unit test that encodes the 6GMN case. **Verified to move no
committed number** — re-staging on CI reproduces registry A's VHL and CRBN arms with **bit-identical** exit
vectors and anchor-to-transfer distances
([`nr4a3-e3-arm-registry-recruiter-contact-recheck.json`](../modalities/nr4a3-e3-arm-registry-recruiter-contact-recheck.json)).

### 1.4 ⚠ CRBN has no defect, but it has a real ±15 Å exit-vector spread — and the run used the low end

The same zero-composition measurement on **9UUM** (mezigdomide-organized CRL4–CRBN–IKZF3–UbcH5a~Ub):

> **GROUND TRUTH (9UUM, zero composition): exit atom `QFC.C10` → UBE2D1 catalytic Cys85 = 27.69 Å.**

| CRBN staging | ligand | anchor → transfer anchor | ligand → CRBN |
|---|---|---|---|
| registry A (6BOY) — **used by the authoritative run** | dBET6 | **12.87 Å** | 2.69 Å |
| registry B (9FJX) | lenalidomide | 21.50 Å | 2.96 Å |
| observed in 9UUM itself | mezigdomide | **27.69 Å** | — |

**All three are legitimately at the CRBN ligand site** — the 4.5 Å lining of all three shares the
tri-tryptophan thalidomide pocket (His353, Glu377, His378, Ser379, Trp380, Trp386, Trp400, Phe402), and all
three are in contact with CRBN. So this is **not** a defect; it is genuine, ligand-dependent variation in
where "the exit vector" is, because a PROTAC's E3-side moiety terminates in a different place and points a
different way from an IMiD's. The common-frame decomposition puts 11.21 Å of the 6BOY-vs-9FJX difference in
the exit vector and only 2.56 Å in the mapped E2.

**Why this is decision-relevant.** RUNG 5a's own explanation for CRBN's very high lysine null is exactly this
distance: *"CRBN's null is much higher … because its observed transfer anchor sits only 12.9 Å from the
ligand exit vector while VHL's sits 30.9 Å away."* That 12.9 Å is the **smallest of three legitimate values**
spanning 12.87–27.69 Å. So CRBN's 0.81–0.96 background — the number nr4a3-program-map.md cites when it says *"most of
CRBN's apparent term-(b) signal is background"* — is partly a consequence of an arbitrary co-structure choice,
and `crbn|M0`, the **strongest basin in the whole 12-pose run**, was scored against it.

**That prediction was then tested — see §4.** Restaging both arms **assembly-native** and re-running at
matched settings **halves CRBN's any-lysine null (0.858 → 0.399)** while leaving VHL's unmoved. The 0.81–0.96
figure is an exit-vector artifact — though §4.2 shows it is also **not the null the gate divides by**, so the
GO itself is unaffected and it is the surrounding narrative that falls.

### 1.5 A free by-product: the composed-RING caveat is quantified on **both** arms now, not one

The staging's own known-answer check compares each arm's composed RING against **one** reference assembly —
9UUM — and VHL shares no bridge protein with it, so it returned `possible: false` for VHL and the number was
never measured. But every VHL record already carries both quantities in the same frame. Subtracting them is
arithmetic on a committed artifact:

| arm | composed RING from | vs the RING of its **own** intact assembly | displacement |
|---|---|---|---|
| VHL | 5N4W | 8R5H | **30.18 Å** ← not previously reported |
| CRBN | 2HYE | 9UUM | **50.14 Å** (consistent with the 48.58 Å measured through the other bridge) |

So the program-wide caveat is **~30–50 Å across both arms**, not "48.6 Å on CRBN". It is **not load-bearing
in the authoritative run** — both arms carry `transfer_anchor.source = observed_in_intact_assembly`, and
`transfer_zone()` uses that observed point with an 8 Å isotropic mobility rather than swinging an arc about
the composed RING — but it binds immediately for any future arm that has no intact assembly and falls back to
the composed-RING arc.

`validate_composition_against_solved_assembly` now performs this **own-assembly** comparison for every arm
before its single-reference check, so the number is recorded in the registry for any future arm rather than
being silently skipped whenever the arm and the reference entry share no bridge protein. (Added, not re-run:
Lane 2's committed registry is left exactly as it was.)

### 1.6 Verdict

> **The VHL staging that the authoritative Tier-2 result rests on is CORRECT, validated to 0.09 Å against a
> composition-free measurement in a solved intact assembly. The 69.9 Å figure was a staging defect in a
> registry the authoritative run never consumed, now root-caused and fixed. The VHL basin ranking is
> unchanged, and Tier-2 SURVIVES — slightly strengthened on its VHL limb, because the "term (b) may carry
> ~40 Å of transfer-zone variation" risk is removed rather than merely unquantified.**
>
> The offsetting finding is on the other arm: **CRBN's exit vector, and therefore its any-lysine null, is not
> a fixed property of CRBN** — §4 shows that when the arm is staged composition-free, that null **halves**
> (0.858 → 0.399) while VHL's does not move, and while the *gate's own* denominator (the unique-lysine null)
> barely changes on either arm. So the Tier-2 GO and its enrichments stand on both constructions; what does
> not survive is the conclusion built around the old figure — *"the discrimination lives on VHL"*.

---

## 2. Is the categorical chemistry axis a single point of failure?

All **7** term-(a) meta-basins reach **C397 and only C397**. The two quantities that decided that were
single-frame numbers: C397's exposure (RSA 0.395) and the exit-anchor→SG distances driving the E3-independent
envelope. **Both are answerable for $0 from evidence this repo already owns and had never used for this
question:** `results/nr4a3-pocket-reharmonize/` holds **100 real NR4A3 conformers** — 25 metadynamics frames
and **75 unbiased release frames** (3 replicas × 25) — same 254-residue construct, same atom composition,
same numbering as `nr4a3-opened.pdb`, so the identical Shrake–Rupley routine and the identical envelope run
on each of them unchanged ([`nr4a3_handle_ensemble.py`](../modalities/nr4a3_handle_ensemble.py) →
[`nr4a3-handle-ensemble.json`](../modalities/nr4a3-handle-ensemble.json)).

### 2.1 C397's exposure is a robust property of the fold, not a lucky frame

Pooled over the **75 unbiased** conformers (the metadynamics set is reported separately and never pooled,
because it is biased along the pocket-opening CV and its histogram is not a population estimate):

| handle | single-frame RSA (committed) | ensemble median | mean ± SD | p10–p90 | min–max |
|---|---|---|---|---|---|
| **C397** | 0.395 | **0.416** | 0.405 ± 0.096 | 0.298–0.510 | 0.108–0.673 |
| C420 | 0.311 | 0.186 | 0.205 ± 0.085 | 0.102–0.328 | 0.064–0.451 |
| C559 | 0.095 | 0.132 | 0.141 ± 0.052 | 0.077–0.207 | 0.040–0.290 |
| K572 | 0.879 | 0.760 | 0.766 ± 0.150 | 0.513–0.969 | 0.443–1.024 |
| K592 | 0.506 | 0.554 | 0.528 ± 0.088 | 0.396–0.623 | 0.284–0.681 |
| K518 | 0.413 | 0.304 | 0.299 ± 0.068 | 0.208–0.383 | 0.122–0.459 |

**The committed 0.395 sits essentially at the ensemble median** — C397 is exposed in every conformer sampled
and never approaches buried. Two secondary readings matter:

- **C420's single frame was optimistic**: 0.311 sits near the top decile of its 0.186-median distribution.
- **C559 is slightly *more* exposed in the ensemble** (0.132) than in the reference frame (0.095) — so the
  "buried in this conformer" language is a fair description of the frame but understates the ensemble. It is
  still the least exposed of the three, and, as §2.2 shows, **exposure is not what closes C559 anyway.**
- All three unique **lysines** stay exposed across the ensemble, so term (b)'s handles are robust too.

### 2.2 Reach: C397 holds up; C420 and C559 are closed at the gate in **every unbiased** conformer

The E3-independent envelope, recomputed independently on each conformer with its own pocket centroid and its
own 12-anchor warhead exit-vector ensemble — the fraction of frames in which each cysteine is reachable at or
below a given linker length:

| | ≤8 | ≤10 | **≤12 (the gate)** | ≤14 | ≤16 | ≤20 | never within 20 |
|---|---|---|---|---|---|---|---|
| **C397** (75 unbiased) | 0.19 | 0.65 | **0.96** | 0.97 | 1.00 | 1.00 | 0 |
| **C420** | 0 | 0 | **0.00** | 0.09 | **0.51** | 0.99 | 1 |
| **C559** | 0 | 0 | **0.00** | 0.00 | 0.00 | **0.81** | 14 |
| *C397 (25 metad, biased)* | 0.08 | 0.48 | *0.72* | 1.00 | 1.00 | 1.00 | 0 |

- **C397 opens at or below the 12-atom gate in 72/75 = 96 % of unbiased conformers** (median shortest linker
  10 atoms). The "opens at a 10-atom linker" claim is an ensemble property, not a single-frame artifact.
- **Neither C420 nor C559 is reachable at ≤12 atoms in ANY of the 75 unbiased conformers × 12 exit-vector
  poses.** A different receptor frame does not rescue them, and neither does a different exit vector. Across
  all 100 conformers the exceptions are **2 biased metadynamics frames for C420 and none at all for C559** —
  and those two are frames driven along the pocket-opening CV, not a population the design can count on.
- **They are recoverable only by paying linker length**: C420 at **16** atoms (51 % of frames), C559 at
  **20** (81 %, and 14/75 frames never open at all within 20).
- The **biased** metadynamics ensemble is *less* favourable for C397 (median RSA 0.290; 72 % at the gate), so
  the term-(a) claim is not riding on the biased frames — it is stronger on the unbiased ones.

*Honest limit on this table:* `shortest_linker` is reported on the discrete grid {6, 8, 10, 12, 14, 16, 20}
and the per-frame pose ensemble is stochastic, so an individual frame's bin carries roughly ±1 step of
pose-sampling noise (the reference model reads 10/14/20 here against 10/16/20 in the committed 12-pose run).
Every frame is processed by the identical protocol, so the **cross-frame** comparison — which is what the
table is for — is unaffected.

### 2.3 ★ The question the marginals cannot answer: is it the SAME conformer?

Term (a) needs one conformer to do two things at once — present the cryptic pocket the warhead occupies
**and** put C397 within a linker's reach of a dockable E3 anchor. "The pocket opens in 59 % of frames" and
"C397 is reachable in 96 % of frames" say nothing about whether those are the *same* frames, and if they were
anti-correlated the entire term-(a) axis would be conditional on a conformational state that excludes the
warhead binding — with no marginal statistic showing it.

The join is free: the reharmonized pocket analysis carries a per-frame `orthosteric_druggability` for exactly
these conformers, keyed by the same frame index, against the pinned **d\* = 0.53**.

| 75 unbiased conformers | value |
|---|---|
| P(pocket druggable at d\*) | 0.587 |
| P(C397 reachable at the 12-atom gate) | 0.960 |
| **P(BOTH)** | **0.560** |
| P(both) if independent | 0.563 |
| **P(C397 reachable \| pocket druggable)** | **0.955** |

**They are independent to within the noise of 75 frames — no anti-correlation.** In **56 %** of unbiased
conformers the cryptic pocket is druggable *and* C397 sits at the gate, and conditioning on a druggable
pocket does not cost the handle anything (0.955 vs 0.960 unconditional). The biased metadynamics set agrees
(0.48 observed vs 0.49 independent). This was a live way the mechanism could have failed, and it does not.

*Limit:* 25 frames per replica is small for a joint statistic — read the direction and the magnitude of the
(absent) anti-correlation, not a precise probability.

### 2.4 Verdict: concentration risk, not fragility

**C397 is genuinely the only handle at any credible linker length — and it is a *robust* only handle.** The
axis is not fragile in the sense the question feared (the handle failing to be there in a different
conformer): across 75 unbiased conformers C397 is exposed at median RSA 0.42, reachable at the gate in 96 %
of them, and reachable in **95.5 %** of the conformers that also present a druggable cryptic pocket — the two
requirements are independent, not competing. What the axis *does* carry is **concentration risk**:
everything rests on one residue, and the
untested failure modes are chemical, not geometric — thiol pKa, intrinsic nucleophilicity, adduct stability,
and electrophile promiscuity, none of which this or any other in-silico step in the program has tested, and
the last of which needs chemoproteomics.

The fallbacks are real but expensive: reaching C420 costs a **16-atom** linker and C559 a **20-atom** one,
and that extra contour length is **not free reach** — the prolate-spheroid criterion pays for reaching the
cysteine and for spanning to the E3 out of the *same* budget, so lengthening the linker to capture C420
directly degrades the E3-span term the basin nomination depends on. A 16–20-atom linker is also a materially
worse degrader by every physicochemical measure.

**What this means for the mechanism-first thesis.** The categorical *chemistry* axis is one residue deep, and
should be stated that way in the manuscript rather than as "NR4A3 carries paralogue-unique cysteines"
(plural, true by sequence, but only one of them is a usable handle). The thesis is not weakened — the
paralogue side is a **sequence** fact that no NR4A3 dynamics can touch — but its *redundancy* is one, and the
program's insurance against a C397-specific chemical failure is the categorical **lysine** axis (term (b)),
not a second cysteine.

*Not answered here, and it is a GPU question:* matched **NR4A1/NR4A2** MD ensembles do not exist in this repo.
They are not needed for the claim above — the paralogue side is categorical by sequence — but they are the
only way to test whether a paralogue's *dynamics* open a compensating site. Estimated ~$10–40 on Vast; **not
launched, not pre-staged, and not requested by this lane.**

---

## 3. What was built

| file | what it is |
|---|---|
| [`transfer_anchor_diag.py`](../modalities/transfer_anchor_diag.py) | the discriminating observation: composition-free ground truth inside a solved intact assembly + common-frame decomposition + per-copy ligand audit + registry cross-check |
| [`transfer-anchor-diagnostic.json`](../modalities/transfer-anchor-diagnostic.json) | its output (CI) |
| [`nr4a3_handle_ensemble.py`](../modalities/nr4a3_handle_ensemble.py) | C397/C420/C559 exposure + E3-independent reach across 100 real NR4A3 conformers |
| [`nr4a3-handle-ensemble.json`](../modalities/nr4a3-handle-ensemble.json) | its output |
| `nr4a3_e3_stage.py` | `pick_ligand` now requires **recruiter** contact; `--prefer-entry` stages assembly-native arms |
| `tests/test_basin_search.py` | a unit test encoding the 6GMN partner-bound-ligand case |
| [`nr4a3-e3-arm-registry-recruiter-contact-recheck.json`](../modalities/nr4a3-e3-arm-registry-recruiter-contact-recheck.json) | proof the fix moves no committed number |
| [`nr4a3-e3-arm-registry-native.json`](../modalities/nr4a3-e3-arm-registry-native.json) | both arms staged **assembly-native** — every bridge 0.0 Å |
| `nr4a3-orientation-basins-matched-{composed,native}.json` | the matched, identical-settings comparison of §4 |

---

## 4. ★ Matched composed-vs-assembly-native comparison — CRBN's promiscuity null halves, and it was the exit vector

Both arms were restaged **assembly-native** — receptor, ligand, RING and E2 all from ONE intact assembly, so
**every bridge RMSD is 0.0 Å and nothing is composed**:

| arm | receptor = scaffold = intact assembly | ligand | ligand → recruiter | anchor → transfer anchor |
|---|---|---|---|---|
| VHL | **8R5H** (354 Cα bridge @ **0.0 Å**) | MZ1 (het 759) | 2.80 Å | **30.76 Å** |
| CRBN | **9UUM** (1489 Cα bridge @ **0.0 Å**) | mezigdomide (QFC) | 2.18 Å | **27.69 Å** |

The basin search then ran **twice at identical settings** (250 000 samples × 8 poses × 2 arms, same seed;
700 s and 816 s), once per registry — so this is a controlled comparison, not a re-quote of the 12-pose run at
different parameters.

### 4.1 The result

| | VHL (composed, 5T35) | VHL (**native**, 8R5H) | CRBN (composed, 6BOY) | CRBN (**native**, 9UUM) |
|---|---|---|---|---|
| anchor → transfer anchor | 30.85 Å | 30.76 Å | **12.87 Å** | **27.69 Å** |
| exit vector moved | — | **0.99 Å** | — | **16.5 Å** |
| **null: any NR4A3 lysine covered** (mean over poses) | 0.419 | 0.437 | **0.858** | **0.399** |
| null range | 0.385–0.445 | 0.380–0.520 | **0.760–0.980** | **0.320–0.445** |
| null: unique lysine covered | 0.027 | 0.026 | 0.040 | 0.035 |
| accepted placements / pose | 249–364 | 265–375 | 202–277 | 367–481 |

**This is a causal demonstration, not a correlation.** The arm whose exit vector barely moved (VHL, 0.99 Å)
shows **no** change in its null; the arm whose exit vector moved 16.5 Å shows its null **halve, 0.858 → 0.399**.
The change tracks the manipulated variable and nothing else.

### 4.2 What it does to the record — and a conflation of TWO different nulls

> **CRBN's 0.81–0.96 lysine null is an artifact of the dBET6 exit-vector choice, not a property of CRBN.**
> At the composition-free geometry — the one measured inside the very assembly the transfer anchor is taken
> from — CRBN's null is **0.32–0.45**, indistinguishable from VHL's **0.38–0.52**.

**But it matters exactly which null that is,** and checking the source (`run_arm_pose`, the
`term_b_background_null` block) shows the record has been mixing two:

| null | what it counts | used for |
|---|---|---|
| `fraction_any_nr4a3_lysine` | the zone covers **any** NR4A3 lysine (rank ≥ 1) | reported only — **this is the 0.81–0.96** |
| `fraction_unique_covering` | the zone covers a **paralogue-unique** lysine (rank ≥ 3) | **the denominator the gate actually divides by** — `enrichment_over_background`, and the `exceeds_background` test |

Under the arm swap the two behave completely differently:

| | VHL composed → native | CRBN composed → native |
|---|---|---|
| `fraction_any_nr4a3_lysine` (mean) | 0.419 → 0.437 | **0.858 → 0.399** |
| `fraction_unique_covering` (mean) | 0.027 → 0.026 | **0.040 → 0.035** |

**So the gate's denominator barely moves, and the promiscuity statistic halves.** Two consequences, and they
point in opposite directions:

1. **The Tier-2 GO is untouched.** The enrichments and the `exceeds_background` test are computed against
   `fraction_unique_covering`, which changes by ~10 % — well inside sampling noise at these counts. Nothing
   about the authoritative run's enrichment figures needs restating.
2. **The interpretive claim built on the other null does not survive.** nr4a3-program-map.md's Tier-2 block states:
   *"CRBN's null is 0.81–0.96, so most of CRBN's apparent term-(b) signal is background. **The discrimination
   lives on VHL — the arm carried as a control, not as the winner.** This is decision-relevant and must not be
   smoothed over when the E3 is chosen."* That inference has **two** independent problems. First, the
   0.81–0.96 is the **any-lysine** null, while "CRBN's apparent term-(b) signal" is an enrichment over the
   **unique-lysine** null — the sentence draws a conclusion about one quantity from a different one. Second,
   the 0.81–0.96 itself is an **exit-vector artifact**: staged composition-free it is 0.32–0.45. **"The
   discrimination lives on VHL" is not established on either reading.**

### 4.3 And the gate itself is robust to the arm construction

| | composed | native |
|---|---|---|
| meta-basins / basins | 53 / 127 | 55 / 128 |
| exploiting term (a) at the 12-atom gate | 2 | 3 |
| exploiting term (b) above the null | 26 | 26 |
| nominally discriminating | 22 | 26 |
| **Tier-2** | **GO, CATEGORICAL** | **GO, CATEGORICAL** |

**Tier-2 passes on both**, on the same basis, with the native construction marginally *stronger* on both the
term-(a) and discrimination counts. So the GO does not depend on how the arm was built.

### 4.4 Two things this comparison does NOT say

- **It is not a restatement of the authoritative 12-pose result.** At 250 k × 8 poses the absolute counts are
  necessarily lower than the 10⁶ × 12-pose run's (7 term-(a), 40 term-(b), 28 discriminating). Only the
  composed-vs-native contrast at matched settings is meaningful here.
- **Meta-basin IDs are not stable across runs**, so `crbn|M0` here is not the `crbn|M0` of the authoritative
  run and nothing above re-ranks that specific basin. And as §4.2 shows, its **7.5× enrichment is not the
  quantity that moves** — that figure divides by the unique-lysine null, which the arm swap leaves alone. What
  falls is the surrounding claim that CRBN's signal is mostly background. **Re-running the authoritative
  12-pose configuration on the assembly-native registry is the clean way to settle the ranking; it is ~60 min
  of free CPU and is running now — its result belongs here, not in this section's inferences.**

---

## 5. Exact nr4a3-program-map.md deltas proposed by this lane

*This lane does not edit nr4a3-program-map.md.*

**L1 — the open item in the "★ Tier-2 result in full" block is RESOLVED and should be replaced, not deleted.**
Current text: *"⚠ OPEN AND DECISION-RELEVANT: two verified VHL stagings place the observed transfer anchor
30.9 Å vs 69.9 Å from the exit vector. Two hypotheses, and the discriminating observation has not been run.
This is the top follow-up, and no VHL basin ranking should be treated as settled until it is resolved."*
Replace with:

> **RESOLVED 2026-07-25 (LANE 7, $0).** Measured with **no composition at all** inside 8R5H — a solved intact
> CRL2^VHL assembly carrying VHL·EloB·EloC, MZ1 and a trapped UBE2R2~Ub in one frame — the exit vector sits
> **30.76 Å** from the E2 catalytic Cys93. The staging the authoritative run consumed (5T35) reproduces it to
> **0.09 Å**, with its exit atom **0.99 Å** from the one 8R5H observes for the same ligand. The 69.9 Å figure
> came from a registry the run never used, whose "recruiter ligand" is a fragment bound to **Elongin C**
> (8 EloC lining residues, 0 VHL residues, 6.87 Å from the nearest VHL atom). In a common frame the two
> mapped E2 cysteines agree to **0.02 Å** while the exit vectors differ by **50.67 Å**, so the disagreement is
> entirely an exit-vector defect and is **not** a second instance of the composed-RING spread. Root cause:
> `pick_ligand` tested contact against the receptor **body** (recruiter + obligate partners) and never against
> the **recruiter**; fixed, with a unit test, and verified to leave both consumed arms bit-identical.
> **The VHL basin ranking stands and Tier-2 survives.**

**L2 — ★ RETRACT "the discrimination lives on VHL". CRBN's 0.81–0.96 null is an exit-vector artifact.**
CRBN's anchor→transfer distance is **not a property of CRBN**: it reads **12.87 / 21.50 / 27.69 Å** for
dBET6 (6BOY) / lenalidomide (9FJX) / mezigdomide (9UUM, measured composition-free inside the assembly
itself), all three ligands bound to CRBN in the same tri-tryptophan pocket. The 12-pose run used the
**smallest**, and STRATEGY names that distance as the cause of the high null. **Tested, at $0:** restaging
both arms **assembly-native** (8R5H / 9UUM, every bridge 0.0 Å) and re-running the search at identical
settings (250 k × 8 poses, same seed) halves CRBN's null — **0.858 → 0.399 mean** (0.760–0.980 → 0.320–0.445)
— while VHL's, whose exit vector moved only 0.99 Å, does not move (0.419 → 0.437). The change tracks the
manipulated variable and nothing else. So:

> Delete *"CRBN's null is 0.81–0.96, so most of CRBN's apparent term-(b) signal is background. **The
> discrimination lives on VHL — the arm carried as a control, not as the winner.**"* and replace with:
> *"CRBN's 0.81–0.96 figure is the **any-lysine** null, and two things are wrong with the inference drawn
> from it. (i) It is not the denominator the gate uses: `enrichment_over_background` and `exceeds_background`
> divide by the **unique-lysine** null, which is 0.010–0.060 — so a statement about term-(b) signal cannot be
> read off the any-lysine figure. (ii) The 0.81–0.96 is itself an **exit-vector artifact**: staged
> composition-free from 9UUM (the assembly the transfer anchor comes from), CRBN's any-lysine null is
> **0.32–0.45**, comparable to VHL's **0.38–0.52**, while the unique-lysine null — the one that matters —
> barely moves on either arm (CRBN 0.040 → 0.035; VHL 0.027 → 0.026). **So the Tier-2 GO and its enrichment
> figures are unaffected, and "the discrimination lives on VHL" is not established.** The gate is robust to
> the arm construction: CATEGORICAL GO either way, native marginally stronger (3 vs 2 term-(a), 26 vs 22
> discriminating, at matched settings)."*

Add as the block's new open item: the **authoritative 12-pose configuration on the assembly-native registry**
(~60 min of free CPU) is the clean way to see whether the basin *ranking* moves once no bridge is composed
and both arms sit at their measured anchor distances.

**L3 — §MECHANISM-FIRST: state the chemistry axis as ONE residue deep, and give C397's distribution.**
Replace the single-frame "RSA 0.395" with the ensemble result: over **75 unbiased NR4A3 MD conformers**,
C397's RSA is **median 0.416 (mean 0.405 ± 0.096, p10–p90 0.298–0.510)** — the committed 0.395 is at the
median — and it is reachable at or below the **12-atom gate in 96 %** of them. Add plainly: **C420 and C559
are reachable at ≤12 atoms in ZERO of the 75 unbiased conformers × 12 exit-vector poses** (across all 100,
2 biased metadynamics frames for C420 and none for C559); C420 needs **16** atoms (51 % of frames) and C559
**20** (81 %), paid out of the same contour length that must also span to the E3. Add the joint result, which
closes a live failure mode: the cryptic pocket being druggable and C397 being reachable are **independent**
over the same 75 conformers — P(both) = **0.560** against an independence product of 0.563, and
P(reachable | druggable) = **0.955** — so the handle is not conditional on a conformational state that
excludes the warhead. So the
categorical *chemistry* axis is **one residue deep** — robustly present, but with no geometric fallback — and
the program's insurance against a C397-specific *chemical* failure (pKa, nucleophilicity, adduct stability,
promiscuity — all untested here) is the categorical **lysine** axis, not a second cysteine. C559's
"RSA 0.095, buried" should read "RSA 0.095 in the reference frame, ensemble median 0.132 — but it is **reach**,
not exposure, that closes it."

**L4 — the composed-RING caveat is ~30–50 Å across BOTH arms.** STRATEGY currently carries "a composed CRL
RING carries ~48.6 Å of positional uncertainty", measured on CRBN only. The VHL arm's composed RING (5N4W)
sits **30.18 Å** from the RING of its own intact assembly (8R5H) in the same frame — arithmetic on data
already in the committed registry, which the staging's own known-answer check could not see because it
compares every arm against 9UUM alone. Restate as **~30–50 Å, measured on both arms**, and add that it is
**not in force** in the authoritative run (both arms use the observed-E2 anchor, and `transfer_zone()`
models an 8 Å isotropic mobility about that point rather than a RING arc) — it binds only for a future arm
with no intact assembly.

**L5 — the E3 downselect's third axis gains a sharper test.** RUNG 5a proposed "does a solved assembly place
this recruiter's RING or E2 relative to its ligand-binding site?" Two additions from this lane: **(a)** the
strongest form of a YES is an **assembly-native** arm — receptor, ligand, RING and E2 all from one intact
assembly, so nothing is composed (available for both VHL via 8R5H and CRBN via 9UUM, and now stageable with
`--prefer-entry`); **(b)** the axis must also ask **"is the recruiter's ligand actually bound to the
recruiter?"** — the 6GMN failure passed every existing check.

---

## 6. Honest scope

- Everything about the target side stays conditional on the hypothesised cmpd19 binary pose × the chosen
  receptor frame. §2 **narrows the second conditionality** (100 conformers instead of one) and does not touch
  the first.
- The ensemble is **NR4A3 only**. No matched NR4A1/NR4A2 dynamics exist in this repo. The paralogue side of
  the categorical claim is a **sequence** fact, so the risk quantified in §2 is one-sided by construction.
- Exposure and reach are **necessary, not sufficient**. Nothing here tests thiol pKa, nucleophilicity, local
  electrostatics or electrophile promiscuity; a covalent handle remains an unresolved liability, and
  reversible-covalent chemistry is still preferred so catalytic turnover survives.
- The E3-independent envelope is an **upper bound**: a cysteine that opens at a length here has not been
  shown reachable by any real recruiter at that length.
- 8R5H (3.44 Å) and 9UUM (3.41 Å) are cryo-EM assemblies poised for transfer, not transition states. The
  distances read from them are empirically anchored **permissive** values, not proofs of the productive
  geometry — the same caveat RUNG 5a attached to the 17.1 Å transfer distance.
- No efficacy, safety, therapeutic-window or clinical claim is made or implied.
