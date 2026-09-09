---
id: DOC-PORTFOLIO-ASSESS-DEGRADER-2-20260909
title: "ASSESS-DEGRADER-2 — independent methods and evidence assessment of the DEGRADER-2 per-frame RSA overlap result"
level: L4
kind: assessment-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: ASSESS-DEGRADER-2
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
subject: PORTFOLIO-INVESTIGATIONS-2026-09-08/DEGRADER-2
context: PORTFOLIO-INVESTIGATIONS-2026-09-08/PUB-DEGRADER
---

# ASSESS-DEGRADER-2 — assessment of one unadjudicated result

Independent assessor. I re-derived a stated subset of DEGRADER-2's numbers from the primary
conformers with code I wrote from scratch, then tested the four interpretive claims. I did not
modify, move or overwrite anything in `DEGRADER-2/` or `PUB-DEGRADER/`; conformer trees were read
in place and never copied. RSA is geometry: nothing below is an efficacy, safety, selectivity,
therapeutic-window or clinical-readiness statement.

## Verdict summary

| # | Item | Verdict |
|---|---|---|
| 1 | Reproduction of the 432 quantile statistics and the `0.2126` attribution | **SUPPORTED** (independently confirmed on 256/432 = 59.3 %, 0 mismatches; coverage stated below) — but see §1a: the values are reproducible to 4 dp and *accurate* to only ~2 dp |
| 2 | "72/75, not all" as the right frame | **SUPPORTED-WITH-QUALIFICATION** — the count is right; the presentation understates a statistically real `release_rep0` shift, and the per-replica table is not a like-for-like comparison |
| 3 | Supersession of the round-one "−0.0138 margin" as a p10-vs-max *artefact* | **OVERSTATED** — same fact, new statistic; round one had already drawn the correct conclusion and this result confirms rather than corrects it |
| 4 | The sampling caveat (a maximum grows with sampling) | **SUPPORTED** — and it bites `72/75` harder than the lane admits, while the lane simultaneously over-states the *precision* of the `0.9993` it recommends instead. A second, untested sensitivity (§1a, SASA quadrature) moves the same headline to 73/75 |
| 5 | Falsification | A concrete runnable test is given in §5 |

Nothing I checked was fabricated. Exit codes in `DEGRADER-2/checks/` are real, the script does not
weaken any guard or matcher, and its `main()` returns non-zero on mismatch rather than swallowing it.

---

## 1 · Is the reproduction real? — **SUPPORTED**

**What I actually ran.** `independent_rsa_check.py` in this lane is written from scratch and imports
**neither** `nr4a_differential_atlas` **nor** `nr4a_paralogue_dynamics`. It has its own PDB reader,
its own Shrake–Rupley (own Fibonacci lattice, own grid neighbour search, probe 1.4 Å, the standard
Bondi-type radii), its own Tien 2013 max-ASA table, its own quantile function, and — the part that
matters most — it derives each construct's local→UniProt offset **independently**, by exact
substring placement of the model sequence into the committed UniProt sequence cache, rather than
calling `species_offset` / `construct_frame`. If the labels were wrong, my offsets would disagree.

**Coverage — a stated partial check, not an implied full one.** I recomputed **125 of the 225
frames**: `NR4A1/release_rep2`, `NR4A2/release_rep0`, `NR4A3/release_rep{0,1,2}`. That covers
**256 of the 432** published statistics (59.3 %).

**Result: 256 statistics compared, 0 mismatches** at the committed 4-dp values
(`checks/01-…`, `checks/02-…`, both exit 0). Independently derived offsets came out
NR4A1 +347, NR4A2 +343, NR4A3 +372 — identical to the ones the subject script prints.

* **The `0.2126` attribution is correct on both counts.** In `NR4A1/release_rep2`, `C465`'s maximum
  is exactly `0.2126`, at frame `fp_74_release_rep2`, and it is also that ensemble's maximum over
  **all six** NR4A1 cysteines. The residue and the value both check out.
* **The three exception frames reproduce exactly**: `release_rep0` `fp_41_xmzapaw0` 0.1082,
  `fp_37_h9k263rg` 0.1617, `fp_99_az0_ci9r` 0.1870 — and my run finds **no other** NR4A3 C397 frame
  at or below 0.2126 in any of the three replicas.
* `NR4A2 C534 = 0.1737 @ fp_21_release_rep0` reproduces; `NR4A1 C551 = 0.1201` in `release_rep2`
  reproduces.

**What I did NOT verify independently**, and will not imply I did: `NR4A1/release_rep{0,1}` and
`NR4A2/release_rep{1,2}` — 176 statistics, 100 frames. Consequently the C551 control is
independently confirmed for **`release_rep2` only** (0/25 there, max 0.1201 against that replica's
own ceiling 0.2126); the `0.0907` and `0.1333` maxima in rep0/rep1 are reproduced by the subject's
own re-execution but not by mine.

**One qualification on how the subject frames its own validation.** DEGRADER-2 calls the 432/0 an
"independent integrity check on the artifact the manuscript quotes". It is not independent in that
sense: the script imports `parse_pdb`, `shrake_rupley`, `residue_rsa`, `construct_frame`,
`cysteines_of` and `quantiles` **unchanged** — the same functions that produced the committed
artifact. Its own check therefore establishes that the committed JSON was produced from those
conformers by that code (a real and useful re-execution check), not that the code is right. My
re-implementation is what supplies the missing half, and on 59.3 % of the block it agrees exactly.

### 1a · A quadrature result that the subject lane did not test, and that moves its headline

`checks/03-…` re-runs the same subset at **n_points = 512** instead of the committed 96
(`checks/06-…` re-does the four decisive frames alone). The comparison against the committed 4-dp
block is *expected* to mismatch there — **exit 3, recorded verbatim**, which is the intended outcome
of a sensitivity run, not a reproduction failure.

**The committed values are precise to 4 dp but not accurate to 4 dp.** Refining the SASA quadrature
alone moves individual RSA values by up to ~0.03:

| quantity | n = 96 (committed) | n = 512 | Δ |
|---|---|---|---|
| paralogue ceiling, NR4A1 C465 @ `fp_74_release_rep2` | **0.2126** | **0.2142** | +0.0016 |
| C397 @ `release_rep0/fp_41_xmzapaw0` | 0.1082 | 0.0982 | −0.0100 |
| C397 @ `release_rep0/fp_37_h9k263rg` | 0.1617 | 0.1606 | −0.0011 |
| C397 @ `release_rep0/fp_99_az0_ci9r` | **0.1870** | **0.2180** | **+0.0310** |

The third exception frame's gap below the ceiling at n = 96 is 0.0256 — **smaller than the shift the
quadrature refinement produces in that same frame**. At n = 512 `fp_99_az0_ci9r` sits **above** the
ceiling, and the headline count becomes **73/75, not 72/75**.

The **qualitative** conclusions survive: the ceiling residue and frame are unchanged (NR4A1 C465 @
`fp_74_release_rep2`), C397 still dominates overwhelmingly, and "not all frames" is still true — two
frames remain below. But the **exact integer the lane presents as its result is not stable to the
numerical resolution of the routine that produced it**, and neither the subject lane nor round one
tests this. An exact-count headline needs a convergence check on the quantity being counted; there
is none. (Caveat on my own check: I refined the quadrature for `NR4A1/release_rep2` and
`NR4A3/release_rep0` only, so the n = 512 ceiling is confirmed as the maximum of the replica that
carries it at n = 96; the other two replicas' paralogue maxima — 0.1737 and 0.1940 — are far enough
below 0.2142 that they are very unlikely to overtake it, but I did not recompute them.)

## 2 · Is "72/75, not all" the right frame? — **SUPPORTED-WITH-QUALIFICATION**

Reporting the three as exceptions is **honest** — the lane names each frame and its value, does not
round them away, and explicitly states all three fall in one replica. That is the opposite of
concealment. But the *presentation* around them understates what the concentration means.

**The concentration is not scatter.** On the per-frame values (`checks/04-…`):

| | rep0 | rep1 | rep2 |
|---|---|---|---|
| C397 mean RSA | **0.3510** | 0.4448 | 0.4188 |
| C397 median | **0.3312** | 0.4542 | 0.4128 |
| C397 min | **0.1082** | 0.2722 | 0.2993 |

Two-sided permutation test on the mean, rep0 vs rep1+rep2 (200 000 shuffles): shift **0.0808,
p = 0.00039**. Fisher exact on frames above the *pooled* ceiling, 22/25 vs 50/50: **p = 0.034**.
The NR4A3 `release_rep0` ensemble is distributionally shifted downward at C397; the three exceptions
are its left tail, not three unlucky frames.

**The per-replica table is not a like-for-like comparison.** Each replica is scored against **its
own** paralogue ceiling, and rep0's ceiling is the *lowest* of the three (0.1737 vs 0.1940 vs
0.2126). So rep0 earns its 23/25 against the loosest bar in the set. Put all three against a common
bar (the pooled 0.2126) and the pattern is **22/25 · 25/25 · 25/25** — 0.88, not 0.92. The table as
printed flatters the weakest replica.

**What 23/25 vs 25/25 vs 25/25 licenses:** that the frame-level separation is not carried by a
single replica — two replicas are clean and the third is 0.88–0.92. Wilson 95 % intervals are
23/25 [0.750, 0.978], 25/25 [0.867, 1.000], 22/25 [0.700, 0.958]: **the count table alone cannot
distinguish the replicas.** The distributional test above can, and does.

**What it does not license:** quoting **0.96 (72/75)** as one proportion over 75 exchangeable
frames. It is a mixture of one ensemble near 0.88 and two at 1.00, and the effective number of
independent units is 3 replicas, not 75 frames. It also licenses nothing physical: replica indices
are arbitrary, unpaired across species, and n = 3.

**Recommended reframing** (unapplied): quote the per-replica fractions against a **common** ceiling
with the replica spread, not the pooled 0.96 alone.

## 3 · Is the supersession of "−0.0138" argued correctly? — **OVERSTATED**

The subject says the round-one margin "was an interpolation artefact of comparing p10 to a max" and
that the new count "supersedes" it. Both halves fail on the arithmetic.

**The −0.0138 was reporting real frames.** It is rep0's C397 p10 (0.1988) minus rep2's ceiling
(0.2126). With n = 25, p10 interpolates at index 0.1 × 24 = 2.4, i.e. between the **3rd** lowest
frame (0.1870) and the **4th** (0.2165). Those are exactly the boundary of the three exceptions:
the 3rd is genuinely below 0.2126, the 4th genuinely above. The p10 landed below the ceiling
**because 12 % of rep0 frames are below the ceiling**, which is precisely what the exact count then
measured (22/25). There is no interpolation artefact to correct.

**Round one had already reached the right conclusion.** `PUB-DEGRADER/FINDING.md` §2 states, before
any per-frame data existed: *"in `release_rep0` the separation is **negative at the frame floor**
(C397's least-exposed frames fall below that replica's paralogue ceiling). **'No overlap at any
frame' is not supported**"*, and §3 predicts that a "90 % of frames" statement *"fails in the worst
replica pairing"*. DEGRADER-2's worst cross-replica pairing is **0.88 < 0.90**. That is round one's
prediction **confirmed**, in the direction and roughly the magnitude it named.

So DEGRADER-2's §4b¶1 headline — "**'No overlap' is falsified**, with an exact count" — takes credit
for a falsification round one had already made from the quantiles, and its ¶2 recasts a corroborated
prior reading as a corrected one. The honest description is: *a bounded statement replaced by an
exact count of the same phenomenon.* The comparison of a lower-tail quantile against an opposing
maximum is not an error — it is a conservative screen, and it gave the right answer.

Two things in the subject are fine and should not be lost: the −0.0138 arithmetic **is**
reproducible (I confirmed 0.1988 − 0.2126 from the frames), and the lane's own hedge — "this is a
correction of a reading, not of a number" — is correct. The overstatement lives in the surrounding
sentences ("artefact", "supersedes", "not a sign flip"), not in the numbers. "Not a sign flip" is
also a scale confusion: 0.88 and −0.0138 are the same overlap in two units.

## 4 · Is the sampling caveat load-bearing? — **SUPPORTED** (and cuts both ways)

The lane's structural caveat is correct and I confirmed it empirically. Mean maximum over random
subsets of the 825 paralogue cysteine·frame observations (200 draws each):

| n sampled | 75 | 150 | 275 | 550 | 825 |
|---|---|---|---|---|---|
| mean ceiling | 0.1590 | 0.1768 | 0.1950 | 0.2071 | **0.2126** |

No saturation. The ceiling is still climbing at the full sample.

**It undercuts `72/75` more than the lane admits.** The 4th-lowest C397 frame is **0.2165** — only
**0.0039** above the current ceiling. The 5th is 0.2736. So a paralogue ceiling that rises past
0.2165 (well inside the trend above) turns 72/75 into **71/75**, and past 0.2736 into 70/75. The
"72/75" headline is a count against a threshold that is visibly still moving, and the lane's §4b¶5
says the ceiling grows without carrying that consequence back into its own headline number.

**But the lane's replacement statistic is over-precise.** The pooled dominance is genuinely
sampling-stable in expectation — it estimates P(C397 frame > paralogue observation), which does not
drift with n the way a maximum does, so the lane's recommendation to quote it is right. The problem
is the decimal places. **0.9993** is 44 discordant pairs out of 61 875, but those pairs are not
independent: the **entire** discordance is carried by **exactly 3 distinct C397 frames** against 33
paralogue observations. Change the unit to frames — 75 C397 frames against the 150 paralogue frames'
maxima — and the same quantity is **0.9962**, i.e. ~1 in 260 rather than 1 in 1 400. The honest
small-sample statement is "3 of 75 C397 frames are not more exposed than every paralogue
observation", which is 72/75 again. A four-decimal dominance figure invites exactly the
over-reading the lane's own caveat warns against everywhere else.

**And there is a second sensitivity the caveat does not cover.** §1a shows the count also moves with
the *numerical resolution* of the SASA routine: at n_points 512 the third exception rises above the
ceiling and the headline becomes 73/75. So `72/75` is a count against a threshold that moves with
sampling **and** a set of values that move with quadrature, with the decisive frame's margin
(0.0256) smaller than the quadrature shift it experiences (0.0310).

**Net:** the caveat is load-bearing, the lane states it, and the lane then does not apply it to
either of the two numbers it asks the paper owner to quote — and it misses the quadrature axis
entirely. The one statement that survives all three sensitivities is the qualitative one: *C397 is
more exposed than every NR4A1/NR4A2 cysteine in the large majority of frames, with a small number of
`release_rep0` exceptions.* That is what should go in prose; the integer should not.

## 5 · What would falsify it? — concrete, runnable, $0 CPU

Two tests, in order of decisiveness. Neither needs GPU, network, docking or new sampling.

**(a) Ceiling-growth falsification — extend the paralogue reference set to the excluded ensembles.**
The `metad` subset and the 8XTT experimental ensemble sit in the same trees and were excluded by the
subject. Add their NR4A1/NR4A2 cysteine frames to the reference pool and recompute:

```
python3 .../ASSESS-DEGRADER-2/independent_rsa_check.py 96 NR4A1:metad NR4A2:metad NR4A1:8xtt NR4A2:8xtt
# then: new_ceiling = max over the union of all paralogue observations
#       C397 frames strictly above new_ceiling, out of 75
```

*Falsifies* the headline if the union ceiling exceeds **0.2165** — the count drops to ≤71/75 and
"72/75" as published is wrong; it falsifies the *claim's spirit* if the ceiling exceeds **0.2993**
(rep1/rep2 C397 minima), because then the separation stops being replica-clean. It falsifies the
lane's recommended statistic if pooled dominance against the enlarged reference falls below 0.99.
(The subject itself names this run as "next work"; it is also the test that can break the result,
which is why it should be run before the qualifier is applied to prose, not after.)

**(a′) Quadrature convergence — the cheapest and, on §1a, the most likely to bite.** Recompute the
whole 225-frame block at n_points 96 / 256 / 512 / 1024 and report the frame count above the
*matched-resolution* ceiling at each. *Falsifies the exact count* if the count is not identical at
the top two resolutions. On the subset I ran it already is not (72 vs 73), so the published integer
should be treated as unconverged until this is done at full scope.

**(b) Leave-one-replica-out on the NR4A3 side** — a two-line variant of the same script: recompute
the frame fraction and the dominance with each NR4A3 replica held out in turn. Given §2, the
predicted values are ≈1.00 / ≈0.94 / ≈0.94; if the LORO spread exceeds ~0.10 the pooled 0.96 is a
replica artefact and only the per-replica table may be quoted. This is the cheap pre-check for (a).

---

## What I checked, precisely

* `DEGRADER-2/FINDING.md`, `per_frame_rsa_overlap.py`, `artifacts/per-frame-rsa-overlap.json`, and
  both `checks/` directories (commands, stdout, stderr, exit codes) — read only.
* `PUB-DEGRADER/FINDING.md` §2–§5, its `checks/02-…/stdout.txt` VERDICT line and
  `artifacts/exposure-separation-per-replica.json` — for the round-one comparison in §3.
* The committed routine (`nr4a_differential_atlas.parse_pdb / shrake_rupley / residue_rsa`,
  `nr4a_paralogue_dynamics.construct_frame / cysteines_of / quantiles`) — read, to confirm the
  subject imports them unchanged and to know what convention my re-implementation had to match.
* 125 conformers under `results/nr4a{1,2,3}-*/release_rep*/*/frame.pdb`, read in place.
* `research/modalities/nr4a-paralogue-dynamics.json` (committed quantile block) and
  `nr4a-sequences-cache.json` — read only.

## Limitations of this assessment

1. **Partial recomputation, stated:** 125/225 frames, 256/432 statistics. `NR4A1/release_rep{0,1}`
   and `NR4A2/release_rep{1,2}` are *not* independently verified; the C551 control is independently
   verified in `release_rep2` only.
2. The statistical probes in `checks/04-…` read per-frame values from the **subject's** artifact for
   the paralogue replicas I did not recompute (NR4A1 rep0/rep1, NR4A2 rep1/rep2). For every frame I
   did recompute, the subject's values were identical to mine, which is the basis for using the rest.
3. My Shrake–Rupley deliberately matches the committed **convention** (probe 1.4 Å, hydrogens kept,
   Fibonacci lattice, Tien normalisation) — it is an independent *implementation*, not an
   independent *method*. `checks/03-…` and `checks/06-…` probe one axis of that convention
   (quadrature density) at one alternative level, n = 512. I did **not** test probe radius, radius
   set, hydrogen inclusion or an established external SASA implementation; each could move the
   values further than quadrature does.
7. `artifacts/independent-rsa-n512.json` is 0 bytes — the background wrapper terminated the process
   before that write flushed. The n = 512 numbers I quote come from `checks/03-…/stdout.txt` and
   from the four-frame re-run in `checks/06-…`, which exited 0. The failed write is left in place
   rather than tidied away.
4. Permutation and Fisher p-values treat MD frames as exchangeable draws. They are not — frames
   within a replica are autocorrelated — so the true p-values are **larger** than reported. The
   direction of the rep0 shift is robust to this; its exact significance is not.
5. I did not re-derive the reach envelope, any free-energy construct, the `C7` cutoff, the `metad` or
   8XTT subsets, or anything on the chemoproteomics route. Test (a) in §5 is proposed, not run.
6. Every number here is geometric exposure on MD conformers. It bears on no chemical, biological or
   clinical property.

## Stop condition

Met. Five verdicts are recorded with evidence; the reproduction is independently confirmed on a
stated 59.3 % of the published block with 0 mismatches; the two interpretive defects (§2 the
non-like-for-like per-replica table and the untested rep0 shift, §3 the supersession framing) and
the one under-applied caveat (§4) are named with the arithmetic that shows them. This lane stops
here. It does not edit the subject lane, does not apply any prose change, and does not run test (a).
