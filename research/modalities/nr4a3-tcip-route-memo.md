---
id: DOC-NR4A3-TCIP-ROUTE-MEMO
title: "RT-TCIP after the run — what the paired anchor-plus-effector enumeration returned, and what it changes"
level: L4
kind: memo
status: live
canonical_for: []
purpose: "Grade RT-TCIP against the enumeration that has now been run, record which sentences the newly staged NAMED transcriptional effectors upgrade and which stay proxy-carried, and record the two documentation defects and one citation gate the run surfaced."
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

## 2 · What "one more anchor set" turned out to mean — and it has now been supplied

`PUB-TCIP` is recorded as unwritten because *"the machinery exists and takes one more anchor set."* Read
against the code, that phrase understates the input by a category.

The reach modules consume two points per cell: `a` (warhead exit-vector anchor, target-side, reused
unchanged) and `b` (the second terminus's ligand exit atom). **`b` is not typeable.** It is produced by
`nr4a3_basin_search.sample_placements`, which requires a staged **rigid body** — a registry record with
`receptor_pdb` coordinates on disk and a `ligand.exit_atom_xyz`. That is the anchor set. ⇒ *"one more anchor
set"* is **one more deposited structure**, staged through an RCSB fetch, and RCSB is 403'd by the dev
sandbox's egress proxy, so it is a CI-only path.

### ★★ 2026-08-06, later the same day: the CI fetch was run and the input now exists

⚠ **SUPERSEDED, RETAINED:** *"the repository stages **4** such bodies — `vhl` (5T35), `crbn` (6BOY), `birc2`
(4HY4), `mdm2` (6Q9L) — all four loadable, and **all four E3 ubiquitin-ligase recruiters. Staged
transcriptional-effector arms: 0.** … it is why no statement here names an effector protein."* That was a
correct count of the repository as it stood and it is the finding that converted this lead's status. **It is
no longer true**, and §7 records exactly which sentences that does and does not upgrade.

**Two NAMED transcriptional effectors are now staged** by
[`nr4a3_effector_stage.py`](./nr4a3_effector_stage.py) into
[`nr4a3-effector-arm-registry.json`](./nr4a3-effector-arm-registry.json) — a **second** registry, not extra
rows in the E3 one, because `nr4a3_e3_stage.py` rewrites its registry wholesale on every run and a merged
effector arm would be silently deleted by the next E3 staging job.

| arm | protein | what it is | entry | body | ligand | exit atom |
|---|---|---|---|---|---|---|
| `bcl6` | **BCL6** | BTB/POZ zinc-finger **transcriptional repressor** | 7LWG, 1.30 Å X-ray | BTB **homodimer**, chains A+B, residues 7–128, **243 residues** | YN7 (OICR-12694), 45 heavy atoms | C29, 5.44 Å exposed |
| `brd4_bd1` | **BRD4** | BET **transcriptional co-activator** / acetyl-lysine reader, bromodomain 1 | 4ZC9, 0.99 Å X-ray | chain A, residues 42–168, **127 residues** | 4MW, 55 heavy atoms | O2, 13.65 Å exposed |

### Why BCL6, on evidence rather than on plausibility

Read out of the route's own motivating paper, not recalled. `EV-EB-TCIP-2025`
(`10.1021/jacs.5c05634`, PMC12851799; CI-fetched full text committed on `literature-cache` at
`literature/emc-post-degrader-options/tcip_ewsfli1_jacs_pmc.txt`) states in its abstract that EB-TCIP
*"recruits FKBP12^F36V^-tagged EWSR1::FLI1 to DNA sites bound by the transcriptional regulator **BCL6**"*,
and in its results that EB-TCIP is *"BAK-04-212, a bivalent molecule comprised of OAP and **BI3812**"* —
BI3812 being a BCL6 BTB ligand. The recruited transcriptional machinery in the prior art is BCL6.

⛔ **The hard constraint is the LIGAND, not the protein.** A second terminus with no small-molecule handle
cannot supply `b` at all, and that is what rules out most transcriptional effectors. The paper names the same
constraint in its own words when explaining why it picked BCL6: *"known chemical matter, validated exit
vector, and assay availability."*

**What was rejected, and why:**

- **A bromodomain as the primary choice** — which is what `nr4a3_tcip_reach.effector_arm_census` itself
  guessed (*"the TCIP literature's effector handle is a bromodomain-class ligand"*). Checked against the
  source, that is **wrong for EB-TCIP**: the effector is BCL6 and the handle is a BTB lateral-groove ligand.
  The guess is corrected in the module, and BRD4 BD1 is kept as a **second** body rather than the first —
  see below.
- **EWSR1::FLI1 / any fusion TF itself** — the paper's own reason: *"highly disordered and difficult to
  drug"*, which is why it had to be FKBP-tagged. No ligandable handle ⇒ no `b`.
- **Every BCL6 entry that could not supply a two-protomer ligand-binding unit** — **20 of the 25** entries
  RCSB returned, each refused by name and reason in the registry's `rejected` list
  (*"not enough chains of this accession to build the declared ligand-binding unit"*), plus 3 more with no
  qualifying bound ligand. See the next paragraph: this is the defect the staging module exists to avoid,
  and it fired 20 times on the first real fetch.

### ⛔ Why this is not `nr4a3_e3_stage.py` with a different accession

That script's `select_assembly_copy` takes **one chain per protein**, which is right for VHL, CRBN, BIRC2
and MDM2 — every one of their ligand sites sits inside a single chain. **The BCL6 BTB lateral groove is
formed BETWEEN the two protomers of an obligate homodimer.** A one-chain body would be half a binding site:
the excluded volume understated, and the derived exit vector possibly pointing into the protomer that was
dropped — with every distance downstream still looking perfectly reasonable. So the body here is **derived
from the chosen ligand's own contacts**, and the evidence is recorded per chain rather than assumed:
YN7 contacts **38 atoms of chain A and 20 of chain B**, so the ligand demonstrably spans the dimer and the
body is `A+B` by measurement. An entry where the ligand touched one chain is completed only through an
interface of ≥30 residues, and is **refused as ambiguous** if two candidate partners are within 1.20×.

### Is the exit vector well determined, or is the argmax degenerate?

This is the failure
`nr4a3_e3_stage.pick_ligand`'s own docstring records paying for once — the first E3 run reported both arms'
exit exposure as *exactly* 8.00 Å, which was the distance field's **clamp**, not a measurement, so the
argmax was arbitrary. Checked here rather than assumed, on exact distances with no clamp in range:

| arm | chosen exit | runner-up | gap | relationship |
|---|---|---|---|---|
| `bcl6` | C29, 5.44 Å | C31, 5.33 Å | **0.11 Å — a near tie** | C29–N30 = 1.37 Å, C29–C31 = 2.23 Å ⇒ both atoms are in the **same terminal moiety**, so the exit *direction* is unchanged by the tie |
| `brd4_bd1` | O2, 13.65 Å | O4, 12.92 Å | 0.73 Å | O2–C10 = 1.22 Å (a carbonyl); one atom within 0.5 Å of the max |

⇒ `bcl6`'s argmax is a near tie and is reported as one. It is **not** the clamp failure: the distances are
exact, the maximum is 5.44 Å against an 8 Å clamp, and the two candidates are 2.23 Å apart on the same group.

### What was verified about the staged records, rather than read off `status: OK`

A filled `exit_atom_xyz` and a green `status` are exactly what a defaulted record would also carry, so the
staging job re-reads what it wrote and checks the things only a real staging can produce
(`nr4a3_effector_stage.self_check`): the coordinate file parses, `load_arm_from_registry` — **the same
consumer the enumeration uses** — turns it into a rigid body, and the exit atom **lands on a deposited
ligand heavy atom at 0.000 Å** rather than being a typed number. Both arms pass; both carry no RING, no
cullin and no transfer anchor.

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
| ★ **named effectors** (added 2026-08-06) | `bcl6` 243 res · `brd4_bd1` 127 res | the actual transcriptional machinery, enumerated on its own coordinates — §2 |

⛔ **`birc2` and `mdm2` are SIZE-AND-SHAPE PROXIES, not transcriptional effectors, and nothing here says
otherwise.** They are used for exactly one property: a ~90–95-residue single-domain ligandable body. **They
remain the ONLY bodies in the paired size comparison** — no effector arm enters those pools, and
`test_a_named_effector_may_not_be_pooled_into_the_size_class_comparison` fails the build if one ever does.
A statement about a *named* effector comes from the named arms' own cells (`★_named_effector`), never from
these two.

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
multi-subunit E3s at all 8 rungs — ratio **0.858–0.972**, intervals non-overlapping at 6 of 8 rungs, and
**0.877 at the 12-atom gate**. Taken alone that reads as "an effector-size terminus is geometrically
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
- **⛔ A staged named effector is its LIGAND-BINDING DOMAIN, not the protein.** A BCL6 BTB dimer (residues
  7–128 of a 706-residue protein) is not BCL6, and a bromodomain (42–168 of 1362) is not BRD4. Everything
  outside the deposited construct is absent from the excluded volume, so an admitting answer is an **upper
  bound** on what the full protein would allow — and the full protein is what a cell contains.
- **⛔ DNA and chromatin are absent entirely.** The whole point of a TCIP is that the effector is *bound to
  DNA*; a DNA-bound effector has less accessible volume than a free domain, and this enumeration cannot see
  that. It is a further reason the answer is an upper bound.
- **⚠ Exit-vector exposure is a real confounder and is now measured, not assumed** — the sampler places a
  body by putting its ligand exit atom in the reach shell, so how far that atom sits from its own body is a
  fixed offset that displaces the whole body relative to the target before any rotation. Committed E3 range:
  **5.00–5.79 Å**. `bcl6` sits at **5.44 Å — inside it**, so it is comparable to the four committed arms on
  the property that would otherwise do the work. `brd4_bd1` sits at **13.65 Å — outside it**, so its
  acceptance may not be pooled with or ranked against the others; it is kept as a second body, not as a
  comparator (`cross_checks.exit_vector_comparability`, status `FLAGS`).
  ⚠ **And the SIGN of that confounder is not claimed, because the first data that could speak to it went the
  other way.** The obvious story — a far-dangling exit atom clears the target, so it is admitted more easily
  — was written into this module and then contradicted: `brd4_bd1` at 13.65 Å accepted **less** than `bcl6`
  at 5.44 Å, because a large offset also pushes the body out of the shell it has to sit in. Two mechanisms
  with opposite signs, so the check outputs **"not comparable"** and never "comparable after allowing for
  it". *Superseded, retained: "is therefore admitted more easily for a reason that has nothing to do with
  BRD4."*
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
- `research/manuscripts/methods-record/fact-check-log.md` → **0** occurrences.
- Crossref and Europe PMC are **403'd at the egress proxy** from this sandbox (verified by direct `curl`
  and by `WebFetch`), so the check cannot be run locally either.

**What does exist**, and is worth knowing before someone re-fetches: a CI-fetched full text is already
committed on the `literature-cache` branch at
`literature/emc-post-degrader-options/tcip_ewsfli1_jacs_pmc.txt` (HTTP 200 from PMC). That is a stronger
provenance record than "auto-captured lead" — but it is **not** `verify-refs`, and the repo's gate is
`verify-refs`.

**★ What changed on 2026-08-06, and what did not.** That citation is now the reason an effector was
**CHOSEN** — a staging decision, recorded verbatim in the effector registry's
`evidence_for_choosing_this_effector` with the two quotes it rests on. ⛔ **It still supplies no number to
any result, and the gate is still open.** A citation may tell you which protein to fetch; it may not enter
an artifact as a measurement until it clears `verify-refs`. The registry says so in its own
`⚠_citation_gate` field, and `.github/workflows/verify-refs.yml` is held by another lane, so adding the DOI
there is out of this one's remit and remains open.

⛔ **Consequently no number in `nr4a3-tcip-reach.json` comes from that citation.**
`required_distances()` refuses it explicitly and uses only repository-owned bounds
(`nr4a3_basin_search.PARAMS`, `nr4a3_linker_design.CHEM_MAX_ATOMS`), which are modality-agnostic — which is
also what makes the comparison against the E3 configuration paired. If a TCIP-specific linker length is
later verified it can only **tighten** the ceiling, never loosen it, so the "admits at the 12-atom gate"
reading is the one that survives any tightening.

---

## 7 · Grading the route, and what `PUB-TCIP` can honestly be

**`readiness.attainable_today` moves from `reproducible_workflow` to a computed result.** The route now
holds an artifact of its own. ⚠ *Superseded, retained: "`RT-TCIP.artifacts` is `[]` today."* Measured on
this branch it reads `["ART-TCIP-REACH"]` — the registration landed after this line was written, and a
stale "the graph does not know about this yet" reads as a live gap. The graph edits still owed after the
effector staging are described-not-applied at the end of §10.

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
4. ⚠ **SUPERSEDED, RETAINED:** *"A staged transcriptional-effector arm does not exist in this repository —
   so no claim about a named effector is available at any price until one CI fetch happens."* The CI fetch
   happened the same day. Replaced by 4′ and by the boundary in §7b, which is the part that matters.
4′. **The enumeration now runs on a NAMED transcriptional effector** — BCL6's BTB homodimer (7LWG, 243
   residues, 1.30 Å), chosen from the route's own motivating paper and staged with the ligand-spanning
   dimer measured rather than assumed. Its exit-vector exposure sits inside the committed E3 arms' range,
   so it is comparable to them; BRD4 BD1 is a second body and is flagged as NOT comparable on that axis.

⚠ **Recommendation: this is a section, not a paper.** On its own, (1)–(4) is thin for a standalone
preprint. It is a strong sub-section of a methods/negative-results paper about what the reach machinery can
and cannot decide, alongside the monovalent lane's result, which has the same shape (an intuition that is
true about reach and does not survive contact with the decision quantity).

**And the route's actual blockers are untouched by any of this:** `BLK-R4-BINDS` (nothing is known to bind
the pocket), `BLK-INDUCED-COMPLEX`, `BLK-PARALOGUE-DDG`, `BLK-UNSIZED-REQUIREMENT`, `BLK-NO-WET-LAB`. The
$0 item is discharged; it was never the thing holding the route down.

---

## 7b · ⛔ THE LINE: what a named effector upgraded, and what it did NOT

**This is the section to read before quoting anything from this route.** Staging BCL6 moved exactly one
sentence, and the temptation to let it move the others is precisely the failure this memo was written to
prevent.

| statement | before | after | why |
|---|---|---|---|
| "the envelope admits a second terminus of effector SIZE" | size class, carried by two proxies | **unchanged** | the proxies still carry it; it is the same gate |
| "the envelope admits **BCL6's BTB domain**" | ⛔ not available at any price | ✅ **measured**, on BCL6's own coordinates | `★_named_effector`, computed from that arm's own cells |
| the paired single/multi **size** ratio, its intervals, and the within-class spread control | four E3 bodies, `birc2`/`mdm2` as proxies | **unchanged, and still proxy-carried** | no effector arm enters those pools; a test enforces it |
| the **interface-floor ablation** and its sign inversion | a statement about the SAMPLER's inherited degrader parameter | **unchanged** | it is about the instrument, not about any effector |
| anything about binding, recruitment, chromatin retention or transcription | ⛔ not claimed | ⛔ **still not claimed** | a staged body is an excluded volume and one atom's coordinates |
| paralogue discrimination on the binder (`R7`) | not addressed | **still not addressed** | not a geometry question |

⭐ **And the honest reading of the upgrade is small.** The gate the named effector passed is the gate every
body has passed at every rung — the module says so itself
(`★_the_named_effector.⚠_the_gate_still_cannot_fail`). What genuinely changed is **whose** excluded volume
was tested, not how discriminating the test is. The value of staging BCL6 is that the route can now be
written about without a proxy disclaimer attached to its central noun — not that a new result appeared.

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

## 9 · ✅ CLOSED — the one CI job was run, and what is open after it

⚠ **SUPERSEDED, RETAINED:** *"Stage **one** transcriptional-effector arm through the existing
`e3_recruiter_staging` path (RCSB fetch in CI, then `receptor_pdb` + `ligand.exit_atom_xyz` into the
registry schema) and re-run this module with it in the arm list … it is the only remaining input."*

**Done, 2026-08-06, $0.** Two arms rather than one, because a single body cannot tell an effector result
from that body's own shape — which is the finding §4 already established for the size axis and which
applies with equal force here. The staging ran on a GitHub Actions runner (RCSB is 403'd at the dev
sandbox's egress proxy), through `fusion-cpu-extras.yml` → `tcip_effector_stage`
(`task=nr4a_e3_stage`, `fanout_mode=precheck`), which commits the coordinates and the registry back to the
triggering branch. One correction the prediction got wrong: it could **not** go through the
`e3_recruiter_staging` path, for the homodimer reason in §2.

**What is open after it, in the order it is worth doing:**

1. **The citation gate** — `EV-EB-TCIP-2025` still has not cleared `verify-refs` (§6). It now motivates a
   staging choice, which raises rather than lowers the cost of leaving it unverified. `verify-refs.yml` is
   held by another lane.
2. **A DNA-bound effector body.** Every named-effector number here is an upper bound because the enumeration
   sees a free ligand-binding domain, and a TCIP's whole premise is that the effector is on chromatin. A
   BCL6 BTB–corepressor-peptide or a nucleosome-context body would tighten it. This is a staging question,
   not a sampling one, and is $0.
3. **A wider named panel, if it is ever worth it — and it may not be.** `nr4a3_effector_stage.EFFECTORS`
   takes a UniProt accession and a declared ligand-binding stoichiometry, so adding a repressor arm (EED,
   Q9C0K0, the EED226/A-395 series) or a co-activator adaptor (WDR5, P61964, the WIN-site series) is one
   dispatch and $0. ⛔ **But the honest expectation is that it changes nothing**: the gate admits every body
   tested at every rung, so more bodies buy breadth in a test that cannot fail. Do it if the paper needs a
   panel, not because it is available.
4. **Which interface floor a transcriptional CIP actually needs** (`BLK-UNSIZED-REQUIREMENT`). Unchanged by
   any of this, and still the question that decides whether the ablation's committed row or its floor-0 row
   is the one to report.
5. **Nothing here touches `BLK-R4-BINDS`**, and it remains the blocker that matters: no molecule is known
   to bind the pocket every anchor in this enumeration hangs off.

---

## 10 · Graph edits — DESCRIBED, NOT APPLIED

`systems/graph/` is held by another lane in this session, so nothing below was written. Each entry names
the file, the exact current text and the replacement, so it can be applied and anchor-checked without
re-deriving anything.

### (a) `systems/graph/artifacts.json` — register the effector arm registry

`ART-TCIP-REACH`'s note currently ends:

> *"Its two size-class bodies (birc2, mdm2) are SIZE-AND-SHAPE PROXIES, not transcriptional effectors — no
> effector arm is staged in this repository."*

That clause is now false. Proposed replacement for the clause only:

> *"Its two size-class bodies (birc2, mdm2) are SIZE-AND-SHAPE PROXIES, not transcriptional effectors, and
> they alone carry the paired size comparison. ⭐ From 2026-08-06 the enumeration ALSO runs two NAMED
> transcriptional effectors staged in ART-TCIP-EFFECTOR-ARMS; the admissibility statement is upgraded for
> those arms and the size comparison is NOT. ⚠ Superseded, retained: 'no effector arm is staged in this
> repository.'"*

And a new record:

```json
{
  "id": "ART-TCIP-EFFECTOR-ARMS",
  "name": "Transcriptional-effector second-terminus arm registry",
  "path": "research/modalities/nr4a3-effector-arm-registry.json",
  "produced_by": "research/modalities/nr4a3_effector_stage.py",
  "workflow": ".github/workflows/fusion-cpu-extras.yml",
  "published_to": ["claude/tcip-effector-stage-ci"],
  "note": "The input RT-TCIP was blocked on: staged rigid bodies for NAMED transcriptional effectors, so the route can speak about an effector rather than a size class. BCL6 BTB homodimer (7LWG, chains A+B, 243 res, ligand YN7) and BRD4 BD1 (4ZC9, 127 res, ligand 4MW). Discovery is by UniProt accession — this module supplies NO PDB id — and the rigid body is DERIVED from the chains the chosen ligand actually contacts, because the BCL6 groove spans the dimer and a one-chain body would be half a binding site. ⚠ The body is the LIGAND-BINDING DOMAIN, not the protein, and no DNA or chromatin is present, so any admitting answer computed on it is an UPPER bound. ⚠ brd4_bd1's exit-atom exposure (13.65 A) is OUTSIDE the committed E3 arms' range (5.00-5.79 A) and its acceptance may not be pooled with or ranked against theirs; bcl6 (5.44 A) is inside it. The citation that motivates the CHOICE of effector (10.1021/jacs.5c05634) has NOT cleared verify-refs and supplies no number."
}
```

### (b) `systems/graph/routes.json` — `RT-TCIP`

Add `"ART-TCIP-EFFECTOR-ARMS"` to `artifacts`.

`closure_note` currently contains:

> *"What it does NOT yet hold is a named effector: 0 transcriptional-effector bodies are staged."*

Proposed replacement for that sentence:

> *"⭐ AND ON 2026-08-06 IT ALSO GAINED THE INPUT IT WAS MISSING: two NAMED transcriptional-effector bodies
> are staged (BCL6 BTB, BRD4 BD1 — ART-TCIP-EFFECTOR-ARMS), so the admissibility statement is no longer
> proxy-carried. ⛔ The size comparison still is, and none of the route's blockers moved. ⚠ Superseded,
> retained: 'What it does NOT yet hold is a named effector: 0 transcriptional-effector bodies are
> staged.'"*

⛔ **No blocker, grade, `closure_kind` or `required_validation` field changes.** Staging a body is an input,
not a result: `BLK-R4-BINDS`, `BLK-INDUCED-COMPLEX`, `BLK-PARALOGUE-DDG`, `BLK-UNSIZED-REQUIREMENT` and
`BLK-NO-WET-LAB` are all exactly where they were.

### (c) `systems/graph/instruments.json` / `evidence.json` — nothing owed

`nr4a3_effector_stage.py` is a STAGING step, not an instrument: it emits no verdict and answers no
scientific question, so it gets no `INS-` id. `EV-EB-TCIP-2025` already exists and its status is unchanged
(§6).


---

## Appendix · Superseded numbers

Per CLAUDE.md rule 1.2, a corrected number is registered here rather than silently dropped; the live
text above carries only the current value.

- **2026-08-07 — §4 pooled size-axis figures.** This memo recorded the pooled single/multi ratio as
  spanning **0.865–0.997**, with intervals non-overlapping at **5 of 8** rungs and **0.867** at the
  12-atom gate. Recomputed from the primary per-rung data in
  [`nr4a3-tcip-reach.json`](./nr4a3-tcip-reach.json) → `★_paired_body_size_comparison`, the values are
  **0.858–0.972**, non-overlapping at **6 of 8**, and **0.877** at the gate — which is also what that
  artifact's own `verdict.★_the_size_axis` block reports. The artifact is the one home; these three
  figures had been restated here and drifted from it. Neither set is registered in
  [`pinned-figures.json`](../manuscripts/pinned-figures.json), which is why `lint_consistency.py` could
  not catch the drift. Found while writing
  [`PUB-TCIP`](../manuscripts/tcip/tcip-induced-interface-preprint.md). The §4(b) ablation table
  (0.896 / 1.121 / 1.254) was checked in the same pass and is **unchanged**.
