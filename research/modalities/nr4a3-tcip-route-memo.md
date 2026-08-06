---
id: DOC-NR4A3-TCIP-ROUTE-MEMO
title: "RT-TCIP after the run — what the paired anchor-plus-effector enumeration returned, and what it changes"
level: L4
kind: memo
status: live
canonical_for: []
purpose: "Grade RT-TCIP against the enumeration that has now been run, and record the two documentation defects and one citation gate the run surfaced."
scope: One route. Geometry only — no binding, activity, degradation, selectivity, efficacy or clinical statement.
audience: [maintainers, autonomous research agents]
date: 2026-08-06
last_verified: unverified
---

# RT-TCIP after the run

**Every number below has its one home in
[`nr4a3-tcip-reach.json`](./nr4a3-tcip-reach.json) (readout:
[`nr4a3-tcip-reach.md`](./nr4a3-tcip-reach.md)), produced by
[`nr4a3_tcip_reach.py`](./nr4a3_tcip_reach.py) at $0 on CPU.** This memo is the decision view over it and
adds no measurement of its own. Presentation view (private artifact, generated from the same JSON):
<https://claude.ai/code/artifact/5bef9b0b-9bdb-4180-884a-72d4164ca406>.

---

## 1 · The one-line answer

**The route is LIVE on geometry, and geometry is not where it is blocked.** The envelope admits a
second terminus of transcriptional-effector size at **every** rung of the committed linker ladder, down to
the shortest tested — **6 backbone atoms**, well inside the 12-atom gate and far inside the 24-atom
chemically routine ceiling. `answer: ADMITS`.

⚠ **That binary answer carries almost no information and must not be sold as the result.** Every one of the
four real staged bodies is admitted at every rung, including a **1183-residue** CRBN–DDB1 assembly. A test
that admits everything cannot refute anything — the same warning `nr4a3_basin_search.PARAMS` already
attaches to reading a reach gate at its sampling ceiling. What the run is actually worth is in §3 and §4.

---

## 2 · What "one more anchor set" turned out to mean — the status-converting finding

`PUB-TCIP` is recorded as unwritten because *"the machinery exists and takes one more anchor set."* Read
against the code, that phrase understates the input by a category.

The reach modules consume two points per cell: `a` (warhead exit-vector anchor, target-side, reused
unchanged) and `b` (the second terminus's ligand exit atom). **`b` is not typeable.** It is produced by
`nr4a3_basin_search.sample_placements`, which requires a staged **rigid body** — a registry record with
`receptor_pdb` coordinates on disk and a `ligand.exit_atom_xyz`. That is the anchor set.

**Counted, not recalled** (`effector_arm_census`): the repository stages **4** such bodies — `vhl` (5T35),
`crbn` (6BOY), `birc2` (4HY4), `mdm2` (6Q9L) — all four loadable, and **all four E3 ubiquitin-ligase
recruiters. Staged transcriptional-effector arms: 0.**

⇒ *"one more anchor set"* is **one more deposited structure**, staged through an RCSB fetch. RCSB is 403'd
by the dev sandbox's egress proxy, so it is a CI-only path and cannot be done from here. **This does not
block the run** — see §3 — but it does bound what the run may be said to be about, and it is why no
statement here names an effector protein.

---

## 3 · What was run instead, and why it is the stronger form

The second-terminus body enters `sample_placements` only as (i) an excluded volume and (ii) a contact
count. Nothing in the acceptance test knows what the recruited protein does. So the question does not need
*that* effector; it needs the envelope **resolved by body size**. Three things were computed in one pass
from identical anchors, an identical target frame, an identical distance field and the sampler unchanged:

| | what | why it is there |
|---|---|---|
| body-free | the pure anchor envelope, on a deterministic 1.0 Å lattice with no RNG | this **is** the E3-free machinery; second-terminus-independent by construction |
| E3 bodies | `vhl` 340 res · `crbn` 1183 res | the replication target — if these do not reproduce the committed run, nothing else means anything |
| effector-size bodies | `birc2` 92 res · `mdm2` 94 res | single-domain ligand-binding bodies with solved ligand exit vectors |

⛔ **`birc2` and `mdm2` are SIZE-AND-SHAPE PROXIES, not transcriptional effectors, and nothing here says
otherwise.** They are used for exactly one property: a ~90–95-residue single-domain ligandable body. A
statement about a *named* effector still needs that effector staged.

### ★ The half of `PUB-TCIP`'s claim that is now MEASURED rather than read

`PUB-TCIP` would claim *"the reach enumeration built for E3 recruitment applies unchanged when the second
terminus is a transcriptional effector rather than a ligase."* Reading the source suggests that is true.
**Reading source is a hypothesis.** The controlled reproduction that discriminates it: run each arm twice
from the same seed, once as staged and once with every E3-specific field (`ring`, `cullin`,
`transfer_anchor`, `crl`) stripped. **4 of 4 arms returned byte-identical accepted counts, spans and
contact counts.** The acceptance test is E3-free — measured, not asserted.

### Cross-checks (rule 1)

| check | result |
|---|---|
| reproduces the committed 12-anchor pose ensemble | **AGREES** — 12/12, max Δ 0 Å |
| every committed accepted `anchor_e3_xyz` is admissible here | **HOLDS** — 232 tested, 0 failing |
| replicates the committed E3 acceptance rates | **AGREES** — 24 cells compared, **2 outside** the recomputed 95 % interval against **1.20 expected by chance** (P(≥2) = 0.34 under a 95 % interval). Graded against that expectation, never against zero — a 95 % interval that excluded nothing would be the surprising result |
| size labels match the coordinates | **AGREES** |
| acceptance test is E3-free | **HOLDS** |

---

## 4 · ★★ The finding: the size penalty is a degrader's interface floor, not steric bulk

Pooled by size class, the single-domain (effector-size) bodies accept **less** orientation space than the
multi-subunit E3s at all 8 rungs — ratio **0.865–0.997**, intervals non-overlapping at 5 of 8 rungs, and
**0.867 at the 12-atom gate**. Taken alone that reads as "an effector-size terminus is geometrically
harder", which is the opposite of the intuition recorded in two route memos.

**Two controls stop that reading, and both were run.**

**(a) The contrast is smaller than the spread within a size class — at all 8 rungs.** `birc2` (92 res) and
`mdm2` (94 res) are the same size and differ from each other by up to **1.43×**, while the classes differ
by at most **1.16×**. `birc2` beats `crbn` at every rung despite being 13× smaller, and `mdm2` — the same
size as `birc2` — sits at the bottom of the board. ⇒ **body size is not the controlling variable; the
individual body's shape and exit-vector geometry is.** The pooled ratio may not be reported as a size law.

⚠ **The direction of the pooled contrast is not robust either, and that is a measurement not a hedge.** An
earlier run of the identical code put one rung *above* parity (1.007). The cause was a real defect — the
per-cell seeds were built from `hash(arm_id)`, which Python salts per process, so the artifact did not
reproduce between runs. Fixed to `zlib.crc32`, and **verified**: two full runs under `PYTHONHASHSEED=0` and
`PYTHONHASHSEED=99` now produce byte-identical JSON. The committed numbers are from the deterministic run;
the ~0.13-wide swing that defect produced is a fair estimate of how little the pooled ratio is worth.

**(b) Ablating the interface floor INVERTS the sign.** `min_contact_residues = 12` is a
**degrader-derived** parameter — the search's own comment is *"below this it is a tethered pair, not an
interface"*, and a PROTAC needs a cooperative target·E3 interface. Re-running the identical cells at the
12-atom rung with only that floor changed:

| `min_contact_residues` | single-domain | multi-subunit | ratio |
|---|---|---|---|
| **12 (committed)** | 0.000810 | 0.000904 | **0.896** |
| 6 | 0.008771 | 0.007822 | **1.121** |
| **0 (pure steric)** | 0.080079 | 0.063875 | **1.254** |

⇒ **On clash alone the smaller body gets 25 % MORE orientation space** — exactly what the "smaller second
terminus is a smaller problem" intuition predicts. The entire measured penalty is the induced-interface
requirement, and it is monotone in the floor. Reproduced independently at two sample counts and across
the seed fix (0.894 at 40 000/arm/pose, 0.896 at 30 000) — this is the most stable number on the board.

⛔ **This does not settle which floor is right for a transcriptional CIP, and the module refuses to pick.**
Whether a TCIP needs a 12-residue induced interface or only needs the two proteins co-localised is a
question this repository has never asked — which is precisely what `BLK-UNSIZED-REQUIREMENT` records about
this route. **So the TCIP number must be reported at both floors, never at the inherited one alone.**

---

## 5 · What this inherits, stated rather than footnoted

- **`R5` — the SITE half, in full.** Every warhead anchor is conditional on the cryptic pocket being the
  site, and `V3` returned INCONCLUSIVE on site selection.
- **⭐ `R5` — the POSE half, NOT inherited, and this is worth stating because it is easy to get wrong.**
  The anchors are **marginalised** over 12 pocket-mouth positions in a 5–11 Å shell around the pocket
  centroid (`nr4a3_basin_search.build_pose_ensemble`, whose own docstring says the repo holds no cmpd19
  pose in this frame and that asserting one *"would manufacture precision the evidence does not support"*).
  They are **not taken from a docked pose.** `pose-convergence-401.json`'s **7.006 Å** median
  pocket-superposed ligand RMSD over 6 poses / 15 pairs, with `cross_method_evidence: NONE`, is a statement
  about a docked pose this enumeration does not use. It is not inherited as a coordinate error here; what
  *is* shared is the site premise both rest on.
- One opened NR4A3 frame; no ensemble, no dynamics, no induced fit.
- Single deposited conformers for the bodies, two of them explicit proxies.
- **`BLK-INDUCED-COMPLEX` is untouched.** Nothing here assembles or scores an induced complex.
- **`R7` (paralogue discrimination on the binder) is not a geometry question and is not addressed at all.**

---

## 6 · The citation gate — still open, and it cannot be closed from here

The route's only cited TCIP source is `EV-EB-TCIP-2025` (`10.1021/jacs.5c05634`, PMC12851799), recorded as
an auto-captured lead that *"must clear `verify-refs` before any manuscript quotes it."*

**Measured, this session:**

- `grep -c "jacs.5c05634" .github/workflows/verify-refs.yml` → **0**. The DOI is **absent from the
  workflow**, so dispatching `verify-refs` as committed cannot clear it. Adding it is a workflow edit,
  i.e. a commit — outside this lane's remit. (The 2026-08-06 route audit already recorded this under *"Left
  open deliberately"*; re-read here and unchanged.)
- `research/manuscripts/fact-check-log.md` → **0** occurrences.
- Crossref and Europe PMC are **403'd at the egress proxy** from this sandbox (verified by direct `curl`
  and by `WebFetch`), so the check cannot be run locally either.

**What does exist**, and is worth knowing before someone re-fetches: a CI-fetched full text is already
committed on the `literature-cache` branch at
`literature/emc-post-degrader-options/tcip_ewsfli1_jacs_pmc.txt` (HTTP 200 from PMC). That is a stronger
provenance record than "auto-captured lead" — but it is **not** `verify-refs`, and the repo's gate is
`verify-refs`.

⛔ **Consequently no number in `nr4a3-tcip-reach.json` comes from that citation.**
`required_distances()` refuses it explicitly and uses only repository-owned bounds
(`nr4a3_basin_search.PARAMS`, `nr4a3_linker_design.CHEM_MAX_ATOMS`), which are modality-agnostic — which is
also what makes the comparison against the E3 configuration paired. If a TCIP-specific linker length is
later verified it can only **tighten** the ceiling, never loosen it, so the "admits at the 12-atom gate"
reading is the one that survives any tightening.

---

## 7 · Grading the route, and what `PUB-TCIP` can honestly be

**`readiness.attainable_today` moves from `reproducible_workflow` to a computed result.** The route now
holds an artifact of its own; `RT-TCIP.artifacts` is `[]` today.

**What `PUB-TCIP` can now claim, in order of strength:**

1. **The enumeration is measurably second-terminus-agnostic** — a controlled reproduction, not a code
   reading. This is the methodological half of the stated claim, and it lands.
2. **The envelope admits an effector-size body at every chemically routine linker length** — true, and
   nearly contentless, because it admits everything tested. Publishing it as a positive would be
   over-selling a gate that cannot fail.
3. **A publishable negative that was not on the board:** the paired size comparison that the route was
   demoted for is **confounded** — within-class spread exceeds the between-class contrast at every rung —
   and the apparent effector-size penalty is entirely an **interface floor inherited from a degrader**,
   which inverts when ablated. That is a real result about the *instrument*, and it generalises beyond this
   route.
4. **A staged transcriptional-effector arm does not exist in this repository** — so no claim about a named
   effector is available at any price until one CI fetch happens.

⚠ **Recommendation: this is a section, not a paper.** On its own, (1)–(4) is thin for a standalone
preprint. It is a strong sub-section of a methods/negative-results paper about what the reach machinery can
and cannot decide, alongside the monovalent lane's result, which has the same shape (an intuition that is
true about reach and does not survive contact with the decision quantity).

**And the route's actual blockers are untouched by any of this:** `BLK-R4-BINDS` (nothing is known to bind
the pocket), `BLK-INDUCED-COMPLEX`, `BLK-PARALOGUE-DDG`, `BLK-UNSIZED-REQUIREMENT`, `BLK-NO-WET-LAB`. The
$0 item is discharged; it was never the thing holding the route down.

---

## 8 · The `retires R9/R10/R12` discrepancy — established, not repeated

`map_edits_required` in the artifact carries these as **described, not applied**, each anchor-checked
against the live file. The finding:

**Truth: TCIP retires `R12` only. `R9` and `R10` survive.**

| register | what it says |
|---|---|
| `R9` | *"OUR ternary is correctly assembled"* — not "our ternary **with an E3**"; its instrument `V2` is a general ternary generator |
| `R10` | *"A ternary forms"* — a TCIP is bivalent and induces a target·molecule·effector complex, so a ternary is exactly what it needs |
| `R12` | *"The ternary is compatible with **DEGRADATION** — productive unique-lysine geometry"* — the only one a non-degrading modality removes |

**`systems/graph/routes.json` already encodes the correct version**: `RT-TCIP.blockers_retired` is
`["BLK-TERNARY-GEOMETRY"]` alone, `blockers_inherited` includes `BLK-INDUCED-COMPLEX`, and
`required_validation` still carries *"A ternary geometry for the induced complex"* as
`feasible_today: false`. The generated L2 view says the same in prose: *"it retires the ubiquitin-transfer
geometry while keeping the induced-complex problem."*

**Four prose files disagree with the graph** and need one deliberate commit:
`nr4a3-program-map.md` (Q12 row, and the modality-fork row), `path-family-synthesis.md` (Tier 3 row 12),
and `target-route-options.md` (register row 6, and the Route 6 prose). ⭐ The Route 6 prose **contradicts
itself two paragraphs apart** — *"it retires `R9` … `R10` and `R12` outright"* and then *"It inherits the
same induced-complex modelling problem as `R9` (an assembled ternary-like complex nobody has built)."*
Both cannot stand; the second is the one the graph agrees with.

**`closure_kind`: already fixed, do not fix again.** The 2026-08-06 audit found `RT-TCIP` filed
`closure_kind: instrument_limit` with no instruments and nothing failed, and corrected it in the same pass.
Measured on this branch it reads **`open`**. Pinned by
`tests/test_nr4a3_tcip_reach.py::test_the_closure_kind_row_records_a_verified_state_and_asks_for_no_edit`,
which also fails if `blockers_retired` ever regresses.

---

## 9 · What would make the next run decisive — one CI job, $0

Stage **one** transcriptional-effector arm through the existing `e3_recruiter_staging` path (RCSB fetch in
CI, then `receptor_pdb` + `ligand.exit_atom_xyz` into the registry schema) and re-run this module with it
in the arm list. Nothing else changes: the sampler, the anchors, the ladder and the cross-checks all
already accept an arbitrary arm, which §3's control measures. That converts every "effector-size proxy"
sentence here into a statement about a named protein, and it is the only remaining input.
