---
id: DOC-PORTFOLIO-ASSESS-MONOVALENT-3
title: "ASSESS-MONOVALENT-3 — independent methods and evidence assessment of MONOVALENT-3's clash-cutoff sweep"
level: L4
kind: assessment
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: ASSESS-MONOVALENT-3
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
subject: PORTFOLIO-INVESTIGATIONS-2026-09-08/MONOVALENT-3
---

# ASSESS-MONOVALENT-3 — independent assessment of one unadjudicated result

Assessor lane under `SHARED-CONTRACT.md`. **Read-only outside this directory.** MONOVALENT-3's files were
read but never modified or re-written; the two mutation runs below were executed on **copies** in the
session scratchpad, whose output went to the scratchpad. MONOVALENT-3's four `checks/` directories and its
591 KB artifact are byte-identical to what it left (mtimes 01:08–01:13Z; this lane's first write 01:2xZ).
No `git add`/commit/push, no `scripts/preflight.sh`, no subagent, no network, no GPU, no paid API.
No cutoff was added, no analysis extended, no NR4A1 coordinates sought.
Model: **SELF-REPORT, NOT INDEPENDENTLY VERIFIED — `claude-opus-5`.**

**Nothing here is an EMC efficacy, potency, selectivity, safety, therapeutic-window or clinical-readiness
statement, and nothing in MONOVALENT-3 is read as one. This is geometry about geometry.**

---

## Headline

MONOVALENT-3's **arithmetic is clean** — every load-bearing number in its prose reproduces from its own
artifact, its gates are real and demonstrably fire, and its two negatives (the cutoff-dependence of
MONOVALENT-2's identity claim, and the collapse of the C534 attribution) are honestly and accurately
framed. **One claim is overstated: "all 24 go the same way … never the reverse."** Under an NR4A2-only
substitution the reverse direction is **structurally impossible in 2 390 of the 2 400 decisions**. Only
**10** cell-frame decisions in the whole grid had any opportunity to go the other way. Observing zero
reversals out of ten opportunities is not evidence of direction robustness; the sentence reads as though
it were 2 400.

| # | item | verdict |
|---|---|---|
| 1 | Do the gates gate? | **SUPPORTED** |
| 2 | Is "all 24 go the same way" as strong as it sounds? | **OVERSTATED** |
| 3 | Is the negative against MONOVALENT-2 honestly framed? | **SUPPORTED** (one minor understatement elsewhere in §5.4) |
| 4 | Is the NR4A1 caveat carried everywhere? | **SUPPORTED-WITH-QUALIFICATION** |
| 5 | What would falsify the direction result? | **SUPPORTED** — a concrete runnable test is named below |

---

## 1 · Do the gates gate? — **SUPPORTED**

**Ordering, from the code and not the prose** (`checks/01-gate-ordering-static/`, exit 0). In
`cutoff_sweep_closure.py`: Gate A's recomputation is line 180, its mismatch loop line 184, its hard
`return 2` line 208; Gate B's comparison line 244, its hard `return 3` line 257. The **first read of an
experimental structure is line 283** (`text = read_text(path)`), parse at 286, experimental
`reach_one_frame` at 290. Both hard exits strictly precede any experimental read, and the only reference
to `CRYSTALS` between the Gate A banner and that read is the loop header itself. Gate A's baseline is
built from `LCR.OPENED["NR4A2"]` — the committed modelled frame — so no experimental coordinate can
influence the gate that licenses reading them.

**Both gates demonstrably fail when they should.** I ran two mutants of the script on copies:

* `checks/05-gate-a-fires/` — Gate A's recomputed side keyed to `"2.0"` instead of the primary:
  **`GATE A: 23/300`, exit 2**, no experimental frame line printed. The comparison is live, not decorative.
* `checks/04-gate-b-fires/` — `GATE_B_EXPECTED` corrupted 34→33: **`GATE B FAILED`, exit 3**, again with
  no experimental chain read. Gate A passed 300/300 in that same run, which is also my **independent
  reproduction of Gate A's headline** on this machine.

Neither mutant produced the sensitivity block; both wrote a `_status: GATE … FAILED` artifact. The claimed
hard exits are the observed hard exits.

**What neither gate covers — name it in the record:**

1. **The experimental path is ungated.** `parse_chain` / `model_from_chain` / `protein_chains` run only on
   the crystal chains and are validated by nothing here (Gate A exercises `atlas.parse_pdb` +
   `BS.load_paralogue`, a *different* reader). The lane's provenance says the parser is "reused verbatim
   from MONOVALENT-2" — reuse of an unvalidated component is inheritance, not validation. The alt-loc and
   insertion-code handling in `parse_chain` is a real behavioural choice (`ln[16] not in (" ","A")`, hard
   raise on insertion codes) that no gate tests.
2. **Only the primary cutoff is gated.** The other three cutoffs are checked only in the block the script
   itself labels *supplementary … never used to license anything* (300/300 at each, which I confirmed).
   The result that actually depends on 2.0 and 2.6 Å therefore rests on an ungated reproduction.
3. **The NR4A3 target rows and all NR4A1 rows are taken from the committed artifact unchanged and are
   never recomputed at any cutoff.** Half of every window's arithmetic is asserted, not reproduced.
4. **Gate B is a self-consistency check, not an independent control.** It re-derives the committed tally
   from the committed rows through the committed engine; the adjacent 0/360-field control shows it is
   nearly the same measurement twice. It can fail (proven above), but it can only catch drift in the
   engine or artifact, never an error in the experimental substitution.

None of these is a defect in what the lane claims — the gates do exactly what §4 of its FINDING says. They
are the load-bearing surfaces left uncovered, and item 1 is the one I would want covered before this is
quoted anywhere.

## 2 · "All 24 go the same way" — **OVERSTATED**

The **fact** is exactly as reported. I reproduced it: 24 cell-frame open/closed differences
(22 at 2.0 Å, 2 at 2.6 Å, 0 at 3.0 and 3.4 Å), **every one** committed-open → experimental-closed, **every
one** in a committed window of **width 1**, in **four** distinct cells (`checks/03-…`, exit 0, assertion
on direction passes).

The **inference** does not carry the weight the prose gives it. The decision quantity is
`width = min(chem_max, min(all competitors) − 1) − target + 1`
(`chemoselectivity_margin`, `nr4a3_linker_covalent_reach.py:316`). Substituting experimental chains
changes **only the NR4A2 competitor values**. So a closed cell can be opened **only if its committed
blocker is an NR4A2 cysteine**. If the blocker is NR4A1/NR4A3, or if the target itself is unreachable
(`closed_by = null`), the substitution cannot open that cell at any geometry — it is arithmetically
excluded, not empirically refuted.

Counted per cutoff (`checks/02-reversal-opportunity/`, exit 0):

| cutoff | committed open | closed | closed by **NR4A2** (openable) | closed by NR4A1/NR4A3 | target unreachable | chances to close | observed | chances to **open** | observed |
|---|---|---|---|---|---|---|---|---|---|
| 2.0 Å | 40 | 20 | **0** | 7 | 13 | 400 | 22 | **0** | 0 |
| 2.6 Å | 42 | 18 | **1** | 0 | 17 | 420 | 2 | **10** | 0 |
| 3.0 Å | 37 | 23 | **0** | 5 | 18 | 370 | 0 | **0** | 0 |
| 3.4 Å | 42 | 18 | **0** | 0 | 18 | 420 | 0 | **0** | 0 |
| **grid** | | | | | | **1 610** | **24** | **10** | **0** |

**Of 2 400 decisions, 1 610 could go the "closing" way and 10 could go the "opening" way.** The single
openable situation is `vhl|M3@representative|dab_branch` at 2.6 Å (blocker NR4A2 C465 at 18 atoms), where
all ten chains give width 0. "Not once, at any cutoff, does an experimental chain open a window the
committed model closes" is therefore **true, and almost entirely a property of the closed cells' blocker
identity rather than of competitor geometry.** Zero reversals out of ten opportunities is consistent with
the geometry being directionless.

Could the 24 arise from a structural artifact of how width-1 windows are scored? **Partly, and the lane
half-says so.** Two mechanisms, both real:

* **Width 1 is the discretisation floor.** A window of width 1 means `min(competitor) − 1 == target`
  exactly; the *smallest possible integer perturbation* of one competitor closes it, and no perturbation
  in the other direction is visible as an open/closed change (it only widens an already-open cell). Width-1
  cells are therefore a one-sided detector by construction: **all 24 differences are width-1 cells, and no
  width-2-or-more cell ever disagrees.** The direction of a one-sided detector is not news.
* **The competitor-distance bias is cutoff-dependent and, at loose cutoffs, points the other way.**
  Comparing experimental vs committed NR4A2 C534 corridor atoms over all 600 cell-frames per cutoff:
  2.0 Å mean **−0.41** (257 nearer / 33 farther), 2.6 Å **−0.03** (151/139), 3.0 Å **+0.20** (120/195),
  3.4 Å **+1.65** (24/471). At 3.4 Å the experimental chains reach **farther**, i.e. are *less* competitive
  — the direction that would open cells — and produced no openings only because there were **no openable
  cells** there. The "closes, never opens" summary is thus an artifact of *where the openable cells sit in
  the cutoff axis*, not a uniform geometric fact.

**What the direction result does establish:** at every cutoff, real NR4A2 geometry does not *rescue* the
route — no cell that the committed model calls closed becomes open, and the 24 movements are all against
the route. That is the operationally relevant half, and it stands. **What it does not establish:** that the
closure is direction-robust *because* experimental competitor geometry is systematically more competitive.
It is not, above 3.0 Å.

**Suggested repair (owner decision, not mine):** replace "over 2 400 decisions … all 24 go the same way"
with "of 1 610 cell-frame opportunities to close an open cell, 24 closed; of the **10** opportunities to
open a closed one, none did — every closed cell elsewhere in the grid is closed by a competitor this
substitution does not vary."

## 3 · The negative against MONOVALENT-2 — **SUPPORTED**, fair, not an overcorrection

Reproduced exactly (`checks/06-prose-number-audit/`, exit 0): committed open cells **40 / 42 / 37 / 42**;
experimental open ranges **37–38 / 41–42 / 37 / 42**; set-identical-in-every-frame **False / False / True /
True**; differences **22 / 2 / 0 / 0**. MONOVALENT-2's headline is quoted correctly (its FINDING line 23
and 112) and the correction is stated as narrowing, not as refutation — which is right: MONOVALENT-2 said
explicitly in its own §5 limitation 4 that it ran one cutoff, and MONOVALENT-3 quotes that verbatim rather
than pretending to catch it out. The framing is fair to MONOVALENT-2.

The four width-1 cells are described **accurately**, cell by cell, against the artifact:
`vhl|M3@term_a_exemplar|dab_branch` 2.0 Å all 10 chains; `vhl|M4@term_a_exemplar|dab_branch` 2.0 Å all 10
plus 2.6 Å in 1OVL_E and 7WNH_C (2 chains); `vhl|M3@term_a_exemplar|dap_branch` 2.0 Å 1 chain;
`vhl|M14@term_a_exemplar|aryl_direct` 2.0 Å 1 chain with the closer moving NR4A1 C505 → NR4A2 C505. All
four have committed width 1. The non-monotone open-cell count (7 of 60 flipping cells: 5 in the committed
model, all `vhl|M14@term_a_exemplar`, plus `vhl|M3`/`vhl|M4@term_a_exemplar|dab_branch` under experimental
geometry only) reproduces exactly, as does the C534 closer-count grid range **15–36** (per-cutoff 25–34 /
26–31 / 20–36 / 15–36) against the published 34.

**One factual error, in the understating direction.** §5.4 says *"`NR4A1 C551` additionally appears as a
closer in one experimental cell at 3.4 Å."* It appears in **three** cells at 3.4 Å —
`vhl|M4@term_a_exemplar|amide_direct` (2 frames), `|dap_branch` (3), `|dab_branch` (3): 8 cell-frames.
Worth correcting; it strengthens, not weakens, the lane's own point about the attribution.

## 4 · The NR4A1 caveat — **SUPPORTED-WITH-QUALIFICATION**

The caveat **is** in the JSON, not only the prose: a dedicated top-level `_nr4a1_caveat` key, a repeat in
`_scope`, and `_limits[2]`. That is more than most lanes carry, and the prose repeats it in §5.4 and
limitation 3. It is honest and it is machine-findable.

The qualification is about **placement, not presence**: **0 of 523** cell-level readings whose closer is an
NR4A1 cysteine carry any local flag, and `tally_per_cutoff` carries none — the NR4A1 C505 counts
(**20 / 13 / 8 / 3**) and the 8 `NR4A1 C551` cell-frames sit in the artifact as bare numbers alongside
experimentally-ranged NR4A2 numbers. A consumer slicing `tally_per_cutoff` or `per_cell[].by_cutoff[]`
programmatically — which is the normal way to use a 591 KB artifact — gets un-error-barred single-conformer
numbers formatted identically to error-barred ones. That is the concrete risk, and it is cheap to close: a
`"nr4a1_un_error_barred": true` field beside every NR4A1 reading, or an explicit
`"error_bar": "single modelled conformer — none"` in the per-frame records. **No misstatement is made
anywhere; the caveat is simply not attached at the point of use.**

## 5 · What would falsify the direction result — **SUPPORTED** (concrete and runnable today)

The direction claim is currently untestable because only 10 of 2 400 decisions could have refuted it. The
falsifying test is to **manufacture opening opportunities from the committed inputs**, without new data,
new cutoffs or NR4A1 coordinates:

> **Re-run `cutoff_sweep_closure.py` with the NR4A1 competitor rows excluded from
> `cells_at_cutoff` (pass `par = {"opened": {"NR4A2": rows}}`), and the NR4A3 conserved competitors kept.**
> Every remaining closed cell is then blocked by an NR4A2 cysteine or by target-unreachability; the count
> of *openable* cell-frames rises from 10 to (closed-by-NR4A2 cells) × 10 across four cutoffs.
> **Prediction of the lane's claim: still zero openings. Falsified if any experimental chain opens a cell
> the modelled competitor closes** in that competitor-restricted world.

Two properties make this the right test: it is a **pure re-parameterisation of the existing script** (one
dict, no engine change, no cutoff change, ~60 s, $0), and it isolates exactly the confound — it removes
the untouched-competitor shield that currently makes reversal arithmetically impossible, while leaving the
geometry, cutoffs, chains and gates untouched. It is not a whole-paper claim: a competitor-restricted world
is a *sensitivity probe*, and its result must be reported as one.

A second, weaker but even cheaper falsifier already partly run here: the sign test of
`experimental − committed` NR4A2 competitor reach per cutoff. A genuinely one-sided geometry predicts a
negative mean at **every** cutoff. It is negative at 2.0 Å and **positive at 3.0 and 3.4 Å**, which already
falsifies the *uniform-bias* reading of the direction result (§2). Extending that sign test from C534 to
the **minimum over all NR4A2 competitors** — the quantity that actually sets the window — is the exact,
runnable completion of it, and it needs only `all_competitors_atoms`, which the script already computes.

⛔ **Explicitly not proposed:** fetching NR4A1 coordinates, adding cutoffs, or varying the NR4A3 target
ensemble. Those are MONOVALENT-3's own next-work items and are outside this assessment.

---

## What I checked, and what I did not

**Checked.** Gate ordering by line number in the source; both gates' failure behaviour by mutation on
copies (exits 2 and 3, no experimental read in either); independent reproduction of Gate A (300/300) and of
the primary tally (34/8/18 over 60 cells, 0/360 field mismatches); the 24 disagreements, their direction,
their committed widths and their four cells; the reversal-opportunity arithmetic per cutoff; the
experimental-minus-committed competitor sign distribution per cutoff; every numeric claim in §5.1–§5.4 and
the gate table of §4 against the artifact; the NR4A1 caveat's presence at top level and its absence at the
point of use; all ten frames' alignment identity (1.000), core RMSD (1.525–1.969 Å) and invariant
violations (0 in every frame); the preserved failed check 02 (a genuine `FileNotFoundError`, one `dirname`
too many, correctly retained and correctly labelled).

**Not checked.** I did not re-derive the corridor geometry itself, the superposition, or `reach_one_frame`
from first principles; I did not re-parse the crystals independently of the lane's parser (that is the
ungated surface named in §1, and testing it is a distinct task); I did not audit MONOVALENT-2 or
PUB-MONOVALENT beyond the sentences MONOVALENT-3 quotes; I did not verify the committed artifact
`nr4a3-linker-covalent-reach.json` against its own producer. I ran the lane's script only as mutated
copies, so the 57 s unmutated end-to-end run is reproduced here only through its gate-A/gate-B prefix.

**Limitations of this assessment.** It is a methods-and-evidence review of one lane's internal
consistency and inferential strength on committed bytes, at $0, with no network. It cannot and does not
speak to whether the corridor convention, the clash-cutoff sweep, or the reach model are the right physics
— only to whether MONOVALENT-3's conclusions follow from its own inputs. **Nothing assessed here bears on
EMC efficacy, safety, selectivity, therapeutic window or clinical readiness, in either direction.**

**Stop condition (met).** Stop when all five assessment items have a verdict backed by an executed check or
a code-level reading, or on discovering a defect that invalidates the subject's result. All five have
verdicts; no invalidating defect was found. Stopped there: no extra cutoffs, no extension of the analysis,
no NR4A1 fetch, no edit to MONOVALENT-3, no shared-state write.

## Checks

| dir | what | exit |
|---|---|---|
| `checks/01-gate-ordering-static/` | line-number proof that both hard exits precede any experimental read | 0 |
| `checks/02-reversal-opportunity/` | closing vs opening opportunities per cutoff; competitor sign distribution | 0 |
| `checks/03-diff-cells-and-nr4a1-caveat/` | the 24 differences, their widths/cells/direction; NR4A1 caveat placement | 0 |
| `checks/04-gate-b-fires/` | **mutation on a copy** — `GATE_B_EXPECTED` 34→33: gate fires, **exit 3**, no chain read | 3 |
| `checks/05-gate-a-fires/` | **mutation on a copy** — Gate A keyed to 2.0 Å: `23/300`, **exit 2**, no chain read | 2 |
| `checks/06-prose-number-audit/` | every load-bearing number in §4–§5.4 against the artifact | 0 |

Exits 3 and 2 are the **intended** results of checks 04 and 05 — a passing exit there would have been the
finding. No exit code was fabricated (no pipes; `$?` captured directly). No guard, floor, gate, matcher,
pin, cutoff or test was weakened anywhere; the two mutations weakened nothing, because they ran on
scratchpad copies and their only purpose was to confirm the real gates bite.
