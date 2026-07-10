# NR4A3-degrader paper — response to the simulated JCIM review (2026-07-10)

A rigorous simulated referee report was run against `nr4a3-degrader-paper.md`. This memo triages it,
records the changes already made in-repo, and lays out the major-rework plan + strategy decisions that
need trimcrae's sign-off. It is the working companion to
[`nr4a3-degrader-paper-redteam.md`](./nr4a3-degrader-paper-redteam.md) (which already logged many of the
same issues) — this memo covers what the review adds **beyond** the existing red-team.

## 0. The one genuinely new, load-bearing finding: PDB 8XTT exists

**Verified 2026-07-10.** The reviewer's central factual claim is correct and it was **new to this repo**
(0 prior mentions anywhere). RCSB's own indexed title is **"8XTT: Nuclear receptor Nor1 ligand binding
domain."** NOR-1 = NR4A3. So the manuscript's repeated **"NR4A3 has no experimental structure" is false**
and had to be corrected immediately (done — see §2).

- **What is confirmed:** the entry exists and is the human NR4A3/NOR-1 LBD. (Reviewer states: solution
  NMR, 20 conformers, 248 residues, released 2025-01-15 — plausible and consistent, but I could **not**
  verify the coordinate-level metadata: the egress policy blocks `data.rcsb.org`, `www.rcsb.org`, and
  `www.ebi.ac.uk` (403 CONNECT). Downloading the coordinates for reanalysis will require either an
  allow-listed host, fetching from within a SageMaker job, or trimcrae pulling the PDB manually.)
- **Why it is load-bearing, not cosmetic:** the entire structural foundation of the paper is an AF2 model,
  and every downstream step (static fpocket, PocketMiner, metadynamics CV, handle map, docking, MM-GBSA,
  ternary, ABFE) inherits it. An experimental apo LBD ensemble now exists to benchmark that foundation.
  - If 8XTT **agrees** with the AF2 pocket/handles → this becomes the paper's **single strongest
    validation** and materially de-risks the "load-bearing structural uncertainty."
  - If 8XTT **disagrees** → the downstream design must be rebased on 8XTT. Either way, an AF2-only
    foundation is no longer defensible for submission.

## 1. Triage: what the review gets right, what is already handled, what I dispute

### 1a. Correct and NOT previously handled — must act (the real blockers)
1. **8XTT** (MC1). New. Corrected in text; full reanalysis is P0 (see §3).
2. **ABFE "+7.1 kcal/mol universal offset" is indefensible** (MC14/15). The review is right that one T4L
   benchmark cannot define a target-independent additive constant, and "cancels exactly" is unproven.
   **Fixed in text** (§2): T4L is now reported as a *failed/biased absolute benchmark*, no offset-corrected
   absolutes are claimed, and ΔΔG cancellation is argued *empirically* (borne out for NR4A2, not NR4A1),
   not "exactly." The selectivity conclusion never depended on the offset (ΔΔG is offset-invariant), so
   this **removes an overclaim without weakening the headline result.**
3. **ABFE is conditional on pre-opened conformers** (MC16). This is the deepest thermodynamic point and was
   **not** previously stated: the per-receptor ABFE omits the receptor-specific free-energy cost of
   populating the cryptic-opened state, which can differ across paralogues and could narrow/reverse the
   conditional margin. **Added as an explicit caveat** (§2) and flagged as a revision task. The full fix
   (state-weighted ABFE with per-paralogue opening penalties) is expensive GPU work — see §3.
4. **Gate 1 should read "failed as preregistered," not "weak-form pass"** (MC4). The red-team already
   disclosed the monotonic F(Rg); the review is right that calling it a "pass" reads as post-hoc criterion
   substitution. **Reframed** to "failed as registered, and reformulated into the basin-breathing
   hypothesis the release run then tested" — which is *stronger* falsification narrative, not weaker.

### 1b. Correct in principle, already substantially hedged in the manuscript
The red-team had already caught and caveated most of these; the review's value is insisting the *headline
phrasing* match the caveats. I tightened the headlines (§2) rather than re-hedging:
- Release-run ~24% is persistence + single-trajectory frame fraction, **not** an equilibrium population
  (MC2/3): headline phrasings ("thermally-real," "spontaneously druggable ~a quarter of the time,"
  "conformational-selection target," "metastable") softened to persistence/frame-fraction language.
- fpocket D*/0.931 is a model **proxy**, not ground truth (MC6): removed "the score itself is not in
  question" (both instances); relabelled a druggability *prediction*.
- "escape-resistant" → **ortholog-conserved only** (MC10), with the "would cost the oncoprotein's own
  function" inference removed.
- "proteome-selective / every survivor is promiscuous / lipophilic stickers" (MC11) softened to a
  9-target counter-screen *panel* observation.
- Internal inconsistencies (MC23): ortholog count (five→six species) and LOEUF (NR4A3 0.37 is *above* the
  <0.35 intolerant line, not below — pLI-intolerant but LOEUF-borderline) **fixed.**

### 1c. Where I would push back / not act blindly
- **"Reject, resubmit" framing:** appropriate signal, but note the manuscript was already unusually
  self-critical (the red-team log shows retractions of denovo_15, the decoy-null failure, etc.). The core
  computational story is genuinely strong. The problem is **overclaim + breadth**, not fraud or a broken
  method — consistent with the review's own "very good paper inside this manuscript."
- **D* "build a 20–50 NR benchmark" (MC6):** worth doing eventually, but the cheaper honest fix (call 0.53
  an *empirical reference boundary from the selected NR panel*, not a calibrated threshold) is adequate for
  a first submission. Deferred, not dismissed.
- **Some "move everything to SI" cuts** are a venue-dependent judgment (§4), not an unconditional must.

## 2. Changes already made (committed to `nr4a3-degrader-paper.md`)
All text-level, no new compute, durable across any restructuring:
1. Removed **all** "no experimental structure / uncrystallized" claims; acknowledged **8XTT** in Abstract,
   §1, §5 (×2), with 8XTT-benchmarking named as the primary revision task.
2. **ABFE:** removed the universal +7.1 offset-correction and all offset-corrected absolutes; T4L reframed
   as a failed/biased benchmark; ΔΔG cancellation argued empirically not "exactly"; **added the
   conditional-on-opened-conformer caveat** (omitted opening-penalty term).
3. **Gate 1** reframed as failed-as-preregistered + reformulated (§2.2, §5 caveat 2, §6).
4. Release-run population language narrowed (Abstract, §2.2, §5 caveat 3).
5. fpocket "score not in question" removed (×2) → geometric proxy/prediction.
6. "escape-resistant" → ortholog-conserved (§2.3).
7. "proteome-selective" absolute → 9-target panel observation (§2.4b).
8. Fixed ortholog count (six species) and LOEUF inconsistency (§2.3, §5, Fig S4 caption).
9. Dropped the nonstandard "thermally-real" throughout.

## 3. Major rework plan (needs decisions + GPU $)
Priority order, with honest cost. "Cheap" = default-proceed under the autonomy threshold; "$$$" = needs a nod.

**P0 — before any preprint/submission:**
- **P0.1 Integrate 8XTT.** (Cheap compute, but gated on getting the coordinates past the egress block.)
  Align AF2 model to all 20 conformers (global + pocket-local RMSD); run fpocket on each conformer
  (static druggability distribution); re-run PocketMiner on 8XTT; remap the 10 lining / 7 divergent
  residues; ideally seed a short unbiased MD from a representative 8XTT conformer. This is the single
  highest-value experiment available and is mostly CPU/one-GPU-inference.
- **P0.2 ABFE protocol audit** (engineering, ~free): sign/convention/restraint/SSC/Jacobian audit of
  `nr4a3_abfe.py` given the +7.1 T4L miss; publish per-replicate ΔG, λ-overlap matrices, ESS, convergence
  traces as SI. Decide whether T4L needs a longer re-run (2 ns/window matched to production) — **$$ small.**
- **P0.3 Title + scope decision** (no compute) — see §4.

**P1 — strongest acceptance-probability gains ($$$, sequence on the single g5):**
- Multiple **independent metadynamics** realizations (≥3 walkers/replicas) + an **orthogonal pocket CV**
  (pocket volume or a gate distance) + time-block convergence — answers MC5. **$$$.**
- **State-weighted ABFE**: per-paralogue opening free energy folded into ΔG_bind, converting the
  conditional selectivity into an ensemble one — directly answers MC16, the deepest critique. **$$$$**
  (the most expensive item; may be deferrable to a v2 if we caveat honestly instead).
- **Generation-matched decoy null** (re-run DiffSBDD → filter → dock → MM-GBSA on matched control pockets)
  — answers the winner's-curse confound the paper already flags. **$$–$$$.**
- Statistical nulls that are **cheap/free**: PocketMiner residue-set permutation null; 7/10 divergence
  enrichment test; fpocket per-frame **pocket-tracking** (residue-overlap identity across frames). Do these.

**P2 — polish / packaging (mostly free engineering):**
- Zenodo DOI + full reproducibility bundle; conventional reference list; specific ACS AI disclosure;
  regularize section numbering; simplify the abstract.

## 4. Strategy recommendation (the decisions I need from you)
1. **Title.** The review is right that "**degrader**" overclaims — we have a computationally designed
   *paralogue-selective binder/warhead candidate*, a representative arbitrary-linker PROTAC, and a ternary
   that is explicitly **not** paralogue-selective. Recommend retitling to a **binder/warhead** claim (see
   the question I'll pose). Degradation stays as the framing/future application, honestly scoped.
2. **Scope / breadth.** The manuscript is carrying ~3 papers. Recommend cutting the main text to the
   coherent spine — **8XTT-anchored pocket → dynamics → divergent handles → falsification-controlled
   de-novo design → conditional ABFE selectivity** — and demoting the 6k repurposing screen, superfamily
   screen, CAR-T/pan pole, safety genetics, degradation-window model, and lo_m0_NCCO to SI or a second
   paper. This is the review's biggest structural ask and I think it's right, but it's your call on how
   aggressively to cut vs. keep the "program dossier" character.
3. **Sequencing vs. the ★ North Star.** The standing directive is "make the paper as strong as in-silico
   allows before preprinting." 8XTT integration (P0.1) is squarely on-mission and cheap — I'd do it next
   regardless. The expensive P1 items (multi-walker metad, state-weighted ABFE, generation-matched null)
   are each a **new axis of evidence** (breadth-first = default-yes) but collectively add up to real GPU $
   and time — so they need explicit go/no-go.
4. **Venue.** JCIM remains plausible *after* rework, but its no-wet-lab risk is real. Worth reconfirming
   JCIM vs. leading with the ChemRxiv preprint and treating journal choice as parallel.

## 5. Immediate next action (pending your answers)
Get 8XTT coordinates past the egress block and run P0.1 — it is cheap, on-mission, and gates how much of
the rest even needs to change. Everything expensive (P1) waits on your go/no-go and on what 8XTT shows.
