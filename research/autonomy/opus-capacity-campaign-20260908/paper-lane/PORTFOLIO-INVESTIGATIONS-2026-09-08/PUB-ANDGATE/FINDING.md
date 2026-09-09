---
id: DOC-PORTFOLIO-INVESTIGATION-PUB-ANDGATE-2026-09-08
title: "PUB-ANDGATE portfolio investigation — which AND-gate design assumptions are testable, and what the unmodelled in-trans mode costs"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: PUB-ANDGATE
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# PUB-ANDGATE — testable design assumptions and the in-trans competition bound

## 1. The concrete question

The AND-gate design rests on three assumptions — *coincidence* (only the fusion presents both
features on one chain), *margin* (the avidity window is 5.5–11×), and *what each arm binds*.
**Which of these can be decided with evidence that does not require the missing arm-2 ligand, and
what does the failure mode the paper names but never models — one ligand bridging wild-type NR4A3
and wild-type EWSR1 *in trans* — actually cost the published window?**

## 2. Paper-level merit

The published window is the manuscript's only quantitative result and its entire selectivity
argument: wild-type NR4A3 is tumour-suppressive (AML on combined Nr4a1/Nr4a3 loss [Mullican 2007];
HCC/breast/lymphoma [Safe & Karki 2021]), so "spares wild-type NR4A3" is the design's whole
patient-relevant claim over the shared-LBD degrader. The paper itself records (Limitation 8.7) that
the number backing that claim is an **upper bound with respect to an unmodelled failure mode**, and
the Erratum states the acceptance requirement — `K_eff(cis) ≫ K_eff(trans)` — **without ever
evaluating it**. Closing that is non-trivial (it changes how the headline number must be read), is
attainable with CPU/stdlib arithmetic on inputs the paper already publishes, and requires no ligand
that does not exist. It also separates the two mutually exclusive readings of arm 2 that the paper
carries side by side, which decides whether the §3 model describes the mechanism at all.

## 3. The exact evidence gap, and how it differs from completed or held work

* `research/manuscripts/degrader/fusion-selective-andgate-degrader-paper.md` §8.7, verbatim:
  "**The in-trans failure mode is not modelled.** The §3 models represent wild-type NR4A3 as an
  arm-1-only species. They contain no species in which one bivalent ligand bridges wild-type NR4A3
  and wild-type EWSR1 as two separate proteins … so the computed windows are upper bounds with
  respect to it." §2 repeats it: "nothing in §3 excludes it."
* The three committed models — `research/modalities/andgate_selectivity_model.py`,
  `andgate_linker_em.py`, `andgate_degradation_model.py` and their JSON outputs — were read. **None
  contains a trans species.** `andgate_selectivity_model.py` scores wild-type as
  `frac_bound_monovalent(L, Kd1)` and nothing else.
* A repository-wide grep for any prior in-trans treatment returned **no hit** anywhere outside the
  manuscript's own Erratum text and its campaign copies (`checks/` records the search).
* This is therefore not a re-run of a completed model, not a re-review of repaired prose, and not
  the held GPU program of §5 (ternary/linker/condensate sampling). It is the one arithmetic the
  paper defers and then relies on.
* **What it is not:** it does not touch the blocking gate. No validated, selective, cell-active
  EWSR1-LC arm-2 ligand exists in the public record; that stands unchanged and is the reason the
  work below is explicitly conditional.

## 4. The bounded step taken

Extended the paper's own equilibrium formalism to include the trans-bridged species, in a new
CPU/stdlib model, and derived the partitioning regime analytically.

**Artifact.**
`andgate_trans_competition_model.py` → `fusion-andgate-trans-competition.json` (this directory).
Pure stdlib, CPU only, no network, no external data, no GPU, no paid compute.

**Method.** Site-occupancy partition functions at fixed free ligand, the same dilute-ligand
convention the published model uses, with the paper's own illustrative inputs unchanged
(Kd1 = 10 µM, Kd2 = 100 µM, EM = 1 mM, free ligand 1 µM):

* fusion (cis): `Z = 1 + L/Kd1 + L/Kd2 + (L/Kd1)(EM/Kd2)` — four states, strictly more complete
  than the published `min(Kd1·Kd2/EM, Kd1, Kd2)` cap;
* wild-type NR4A3 with free WT EWSR1-LC sites at concentration `C_E`:
  `Z = 1 + (L/Kd1)(1 + C_E/Kd2)` — adds the trans bridge, charged **no** steric or configurational
  penalty, so the requirement it produces is a *lower* bound on what a real linker must beat.

**Results.**

1. **Validation against the published base case.** At `C_E = 0` the extension gives a window of
   **5.79×** against the paper's published **5.5×**; the small difference is the added arm-2-only
   state, and the agreement is the evidence that this is the same model with one species added.
2. **The Erratum's requirement, quantified.** In the low-occupancy limit
   `window → (1 + EM/Kd2 + Kd1/Kd2) / (1 + C_E/Kd2)`. So `K_eff(cis) ≫ K_eff(trans)` means, exactly,
   **EM ≫ C_E**: a linker-geometry quantity must beat the ambient free concentration of wild-type
   EWSR1-LC sites. That converts an unevaluated qualitative caveat into a comparison against a
   measurable cell-biological number.
3. **The cost curve.** Window retained vs the cis-only value: 0.999 at C_E = 0.1 µM, 0.991 at 1 µM,
   0.917 at 10 µM, 0.545 at 100 µM, 0.318 at 300 µM, **1.00× (selectivity entirely gone) at
   C_E = 1 mM = EM**, and **inverted (0.70×, 0.58×) above EM** — where the molecule prefers
   wild-type NR4A3 to the fusion. The half-window point is analytic, `C_E* = Kd2·(1/f − 1)`, i.e.
   **C_E* = Kd2 = 100 µM**, set by arm-2 affinity **alone** and not by the linker.
4. **A non-obvious consequence that supports the design.** The published design rule ("make both
   arms weak") is *also* what suppresses the trans pathway, because a weak Kd2 raises C_E*. The two
   requirements point the same way. The arm-2 sensitivity table makes the tradeoff explicit: at
   Kd2 = 1 µM the *cis-only* window is larger (10.9×) but C_E* falls to 1 µM, and the window collapses
   to 1.89× by C_E = 10 µM and 1.09× by 100 µM — whereas at the paper's Kd2 = 100 µM it still holds
   3.16× at C_E = 100 µM. **A stronger arm 2 buys a wider paper window and a far more fragile real
   one**; that tradeoff is a testable design rule the paper does not state.
5. **The partitioning reading is a no-go for the AND-gate argument, analytically.** The paper offers
   two mutually exclusive readings of arm 2 and calls the second "more realistic": a discrete IDR
   contact (modelled above), or partitioning into the EWS-LC condensate. Partitioning is a
   compartment property, not a per-chain binding event; it has no Kd2 to enter the cis partition
   function and imposes no coincidence requirement. If the ligand partitions with coefficient Kp,
   local free ligand is `Kp·L` for everything in the condensate, and fusion and wild-type NR4A3 both
   present only an arm-1 site to it at the same Kd1 — so the **inside-condensate window is exactly
   1.0 for any Kp**, and partitioning *worsens* wild-type sparing for whatever fraction of WT NR4A3
   sits in FET condensates (e.g. 91% WT occupancy at Kp = 100). Under that reading the residual
   selectivity is a *localisation* ratio, not an avidity gate, and **§3 cannot be cited in support of
   it.**

**Verdict on the question asked.** Of the three assumptions: *margin* is now bounded rather than
assumed (item 3 gives the exact function of the one unmeasured input); *coincidence* is testable
against an independent benchmark quantity that is not in hand (below); and *what each arm binds* is
**not currently a single assumption at all** — the paper carries two incompatible ones, only one of
which its model describes.

**Validation / baseline.** The cis-only limit reproduces the published base case (5.79 vs 5.5,
difference attributed and explained). No other baseline exists, because no prior in-trans model exists.

**Provenance.** Inputs are the manuscript's own illustrative Kd1/Kd2/EM/L, copied unchanged from
`research/modalities/andgate_selectivity_model.py`. `C_E` and `Kp` are **swept**, not asserted. Every
execution attempt is in `checks/` with command, stdout, stderr and real exit code.

**Limitations.**
1. **Conditional and bounding only.** The model asks what the design would do *even if* the missing
   arm-2 ligand existed with the paper's illustrative Kd2. **No such ligand exists in the public
   record.** Nothing here reports any molecule's properties, and nothing here is an efficacy,
   selectivity, potency, safety or therapeutic-window claim — none of which computation can establish.
2. The inputs are the paper's assumptions, not measured affinities; the outputs are properties of a
   model.
3. `C_E` — the free concentration of engageable wild-type EWSR1-LC arm-2 sites, in bulk nucleoplasm
   and inside condensates — is **unmeasured in this repository**. A repo-wide search for EWSR1
   abundance, intra-condensate concentration or any small-molecule condensate partition coefficient
   returned nothing (`checks/02-…`). No external source was fetched for this lane. The critical value
   is therefore reported as a threshold, not compared to a number.
4. The trans bridge is charged no steric/configurational penalty, so the trans pathway as modelled is
   optimistic for the failure mode and pessimistic for the design.
5. Occupancy, not degradation. The published degradation model is separately narrower and
   dose-fragile; this extension does not address it.

**Stop condition — reached.** The step was complete when the in-trans species was added to the
paper's formalism, the cis-only limit reproduced the published base case, and the critical
concentration became analytic. It stops there: it does **not** attempt to measure or estimate `C_E`,
does not touch the manuscript, and does not re-open the arm-2 ligand gate.

## 5. Next credible independent work, and the actual missing dependency

* **Missing dependency (decisive, external, measurable):** free engageable wild-type EWSR1-LC site
  concentration, bulk-nucleoplasmic and intra-condensate. This single number decides whether the
  in-trans mode is negligible (bulk regime) or fatal (intra-condensate regime, which is where the
  design proposes to act). It is measurable by others and requires no new chemistry.
* **Next independent step available here:** none that changes the verdict without that measurement.
  A legitimate follow-up would be a sourced, verified abundance/partition-coefficient extraction under
  ordinary permitted access, feeding the same script's `C_E` sweep — a data-retrieval task, not a
  modelling one.
* **Unapplied recommendation for the manuscript owner (no edit made, per the contract).** §8.7 can be
  upgraded from "not modelled" to a bounded statement with a named threshold, and §2/§4 should
  resolve — not carry both — the discrete-site vs condensate-partitioning readings of arm 2, because
  the §3 model describes only the first. Preparing that as an exact unified diff was out of scope for
  this checkpoint and is not claimed as done.
