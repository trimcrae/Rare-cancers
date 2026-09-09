---
id: DOC-PORTFOLIO-INVESTIGATION-ANDGATE-2-2026-09-09
title: "ANDGATE-2 — does the published record contain C_E, the AND-gate's decisive unmeasured parameter, and where does it land on the cost curve"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: ANDGATE-2
continues: PUB-ANDGATE
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# ANDGATE-2 — the literature search for `C_E`, and its placement on the cost curve

Bibliographic sources in this finding were retrieved from **PubMed / PubMed Central**; each
is cited with its DOI link. Retrieval was by the PubMed MCP route only — no direct HTTP
fetch was attempted, that route being proxy-refused in this environment.

## 1. The concrete question

The completed PUB-ANDGATE lane established that the AND-gate degrader's published 5.5×
selectivity window collapses as a function of exactly one unmeasured quantity — `C_E`, the
free concentration of engageable wild-type EWSR1 low-complexity arm-2 sites in the
compartment where the ligand acts — with the half-window point analytic at `C_E* = Kd2`.
It recorded that the repository holds no such measurement.
**Does that number, or a bound on it, exist in the published literature; and if so, which
regime does the design fall in — negligible, materially degraded, or fatal?**

## 2. Answer, in one paragraph

**`C_E` itself is not measured anywhere in the retrieved public record.** No source reports
the free engageable wild-type EWSR1-LC site concentration, in bulk nucleoplasm or inside a
condensate; no published small-molecule partition coefficient exists for a FET-family
condensate; and no measurement of free versus condensate-sequestered FET protein was found.
What *does* exist is a **direct in-cell concentration for the fusion protein in the
disease-relevant cell line** — EWS/FLI1 at **~200 nM** in A673 by FCS
([Chong et al. 2018, *Science*](https://doi.org/10.1126/science.aar2555)) — plus a
family-level ceiling that FUS-family proteins in HeLa are in most cases **below 5 µM**
([Wang et al. 2018, *Cell*](https://doi.org/10.1016/j.cell.2018.06.006)). Placing those on
the lane's own cost curve puts the **bulk-nucleoplasmic regime firmly in *negligible***
(window retained 0.998 at 200 nM, 0.957 at 5 µM), with roughly **20-fold of headroom**
before the curve turns. The **intra-condensate regime — which is where the design proposes
to act — remains unmeasured**, and the one plausible in-hub figure available (the upper end
of Chong's stated 100 nM–100 µM hub operating range) lands at **materially degraded**
(retained 0.545). The design is therefore **not** refuted by the record, and **not**
vindicated by it either: it is bounded, in the one compartment that has been measured, and
undetermined in the one that matters most.

## 3. What was found, and what each source actually measures

Per-source provenance, verbatim quotes, the full assumption ledger, and the negative
results are in **`CONCENTRATION-EVIDENCE.md`** in this directory. Summary:

| target | result |
|---|---|
| (a) absolute nuclear concentration of EWSR1 / FET LCDs | **Partially met, by proxy.** Chong 2018: intranuclear **~200 nM** for endogenously Halo-tagged **EWS/FLI1** in A673, by FCS and intensity calibration against purified-fluorophore standards, at CRISPR knock-in native expression. **This is the fusion, not wild-type EWSR1.** Wang 2018: 5 µM "in most cases … lies above the physiological concentration in HeLa cells" of the FUS family — a family ceiling, not an EWSR1 value. |
| (b) proteomic copy number convertible to a concentration | **Not met.** No EWSR1 copy number retrieved; no nuclear volume retrieved. [Wiśniewski et al. 2014](https://doi.org/10.1074/mcp.M113.037309) supplies only the conversion method (proteomic ruler) and its assumptions and ~2-fold accuracy. |
| (c) small-molecule partition coefficient into a FET condensate | **Not met, informatively.** [Klein et al. 2020, *Science*](https://doi.org/10.1126/science.aaz4427) measures cisplatin partitioning **up to 600** — into **MED1** condensates. Its scaffold panel is MED1, BRD4, SRSF2, HP1α, FIB1, NPM1: **no FET scaffold**. This lane does **not** adopt 600 as a FET `Kp`. |
| (d) free vs condensate-sequestered FET protein | **Not met.** Zero hits. |

**Two things are flagged rather than smoothed over.** First, the Chong PMC body text prints
the hub operating range as "100 nM to 100 **mM**" where the abstract and graphical abstract
say "100 nM to 100 **µM**" — an internal inconsistency in the source as retrieved; this lane
uses µM and reports the discrepancy. Second, Chong report **no detectable phase separation**
of EWS/FLI1 hubs at endogenous levels, which matters for §5.

## 4. The conversion assumptions, stated up front

A copy number becomes a concentration by `C = N / (N_A · V_nuc)`, and that carries six
assumptions, each able to move the answer by more than the factor separating the regimes:
**(1)** nuclear volume — not retrieved, and *deliberately not substituted from convention*,
since a 2× diameter is 8× in concentration; **(2)** nuclear-localised fraction, a separate
unretrieved measurement; **(3)** uniform intranuclear distribution — false by construction
for a condensate-forming protein, which is why **no bulk number can ever answer the
intra-condensate question**; **(4)** free versus bound — total abundance is an upper bound
on free engageable sites, so every placement below is conservative *against* the design;
**(5)** arm-2 **site multiplicity per chain** — `C_E` counts sites, not chains, and the
manuscript does not specify what arm 2 binds; **(6)** cell-type transfer.

The Chong anchor is used **because it escapes (1) and (2) entirely** — it is a concentration
measured directly in live cells, not a copy number. It still carries (3)–(6), and it carries
one more that the others do not: it is the **wrong species** (fusion, not wild-type).

## 5. Placement on the lane's cost curve

Artifact: `place_literature_bound_on_cost_curve.py` → `andgate2-literature-placement.json`.
It re-uses the parent lane's formalism unchanged (`Z_fus = 1 + L/Kd1 + L/Kd2 +
(L/Kd1)(EM/Kd2)`, `Z_wt = 1 + (L/Kd1)(1 + C_E/Kd2)`) with the paper's own illustrative
inputs, and **asserts** that its `C_E = 0` point reproduces the parent lane's 5.79× cis-only
baseline — it exits non-zero if not. Regime bands are declared once, in the script:
negligible ≥ 0.90 retained; materially degraded 0.20–0.90; fatal ≤ 0.20 (including
window → 1.0, selectivity gone).

| evidence point | `C_E` | window | retained | **regime** |
|---|---|---|---|---|
| E1 bulk — endogenous EWS/FLI1, A673 (Chong 2018) | 0.20 µM | 5.78× | 0.998 | **negligible** |
| E2b scale check — FUS full-length `c_sat` in vitro (Wang 2018) | 2 µM | 5.68× | 0.982 | **negligible** |
| E2 bulk ceiling — FUS family in HeLa (Wang 2018) | 5 µM | 5.54× | 0.957 | **negligible** |
| E3 intra-condensate — top of Chong's stated hub range | 100 µM | 3.16× | 0.545 | **materially degraded** |

**Verdict by compartment.**

* **Bulk nucleoplasm: negligible.** At the measured scale the in-trans failure mode costs
  ~0.2–4% of the window. The verdict is robust: the half-window point is `C_E* = Kd2` =
  100 µM, so the bulk anchor sits **20–500× below** the concentration at which the design
  starts to hurt, and the anchor is itself an upper bound (total, not free). Even a
  wild-type EWSR1 pool **10× more abundant than the fusion** would sit at 2 µM and retain
  0.98. This is a genuine margin, not a coincidence.
* **Inside FET condensates: undetermined, plausibly materially degraded, possibly fatal.**
  This is where the record stops. The only in-hub figure available is Chong's stated
  operating *range*, whose top end lands at retained 0.545. Nothing retrieved measures the
  in-hub EWSR1-LC site concentration, so the distance from there to `C_E ≈ EM = 1 mM`,
  where the window is exactly 1.00× and selectivity is entirely gone, **cannot be
  determined from the public record.**

**The sensitivity that could overturn the bulk verdict — and it is the site multiplicity,
not the abundance.** `C_E` counts engageable arm-2 *sites*. If arm 2 engages a repeated LC
motif rather than one site per chain, `C_E = n × C_protein`. From the JSON:

| protein concentration | n = 1 | n = 3 | n = 10 | n = 30 | n = 80 |
|---|---|---|---|---|---|
| EWS/FLI1 anchor, 200 nM | 0.998 | 0.995 | 0.982 | 0.949 | 0.875 |
| FUS-family HeLa ceiling, 5 µM | 0.957 | 0.881 | 0.697 | 0.455 | 0.273 |

Wang 2018 counts **80 tyrosine+arginine residues in EWSR1's disordered regions**. At the
200 nM anchor the bulk verdict survives multiplicity up to n ≈ 30; at the 5 µM ceiling it
fails by n ≈ 3. **So the bulk-regime "negligible" result is contingent on arm 2 engaging a
small number of sites per chain — and the manuscript does not say what arm 2 binds.** That
is a second named, answerable requirement on the design, and it is cheaper to settle than
the concentration measurement.

## 6. Artifact · validation · provenance · limitations · stop condition

**Artifact.** `place_literature_bound_on_cost_curve.py` → `andgate2-literature-placement.json`
(this directory), plus `CONCENTRATION-EVIDENCE.md`. Pure stdlib, CPU only, no network, no
external data, no GPU, no paid compute.

**Validation.** The script's identity check reproduces the parent lane's 5.79× cis-only
window from an independent re-implementation of the same partition functions (computed
5.787), and fails loudly rather than silently if the formalism drifts. There is no other
baseline, because no prior placement exists.

**Provenance.** Kd1/Kd2/EM/L are the manuscript's own illustrative inputs, unchanged, via
`../PUB-ANDGATE/andgate_trans_competition_model.py`. Every `C_E` entered is either a cited
published measurement whose exact measured quantity is named in the JSON record and in
`CONCENTRATION-EVIDENCE.md`, or an explicitly labelled swept sensitivity point. **No value
was guessed.** `checks/` holds all 13 execution attempts — including the six searches that
returned zero hits — with command, stdout, stderr and real exit codes.

**Limitations.**
1. **Conditional and bounding only.** No validated, selective, cell-active EWSR1-LC arm-2
   ligand exists in the public record. Nothing here asserts one exists, reports any
   molecule's properties, or constitutes an efficacy, selectivity, potency, safety or
   therapeutic-window claim — none of which computation can establish.
2. **The anchor is the wrong species.** ~200 nM is EWS/FLI1, not wild-type EWSR1. Wild-type
   EWSR1's nuclear concentration is unmeasured in the retrieved record and is plausibly
   higher. The bulk verdict is stated with that 10×-tolerance margin explicitly, not by
   pretending the anchor is the parameter.
3. **The decisive compartment is unmeasured.** The intra-condensate placement rests on the
   top of a stated *operating range* for hubs generally, not a measurement of EWSR1-LC
   sites inside a FET condensate.
4. **No FET-condensate `Kp` exists.** Klein 2020's 600 is MED1. It is reported and
   explicitly **not** adopted. What it licenses is only the mechanistic expectation that
   aromatic π-chemistry drives partitioning, and that the EWSR1 LC is aromatic-rich.
5. **Retrieval scope.** PubMed/PMC MCP only. Supplementary tables — where a proteomic EWSR1
   copy number would most likely live — are not reachable by this route, so "not found" here
   means "not found by title/abstract search plus retrieved PMC full texts", not "does not
   exist". PubMed's query parser ANDs every term, which forced short queries; the six
   zero-hit searches are preserved in `checks/` so the search surface is auditable.
6. Occupancy, not degradation; the paper's separate degradation model is untouched.

**Stop condition — reached.** The step was complete when each of the four retrieval targets
had been pursued to a definite found/not-found, the found values had been placed on the
existing curve with every conversion assumption stated, and the sensitivity that could
overturn the placement had been identified. It stops there: it does not estimate the
unmeasured intra-condensate value, does not adopt a number from a different protein or
compartment, does not touch the manuscript, and does not re-open the arm-2 ligand gate.

## 7. What this converts, and the next credible independent work

The manuscript's §8.7 caveat was "the in-trans failure mode is not modelled". PUB-ANDGATE
turned that into "bounded by one unmeasured quantity, `C_E`, with a half-window at `Kd2`".
**This lane turns it into a named, quantified, two-part experimental requirement:**

1. **Measure the free engageable wild-type EWSR1-LC site concentration, in-hub and
   nucleoplasmic, in a fusion-bearing cell.** The assay already exists: it is exactly what
   Chong et al. ran on the fusion (FCS + intensity calibration on a CRISPR knock-in tag),
   with in-hub versus nucleoplasmic segmentation added. Decision threshold: the design is
   safe from this failure mode while `C_E ≪ Kd2`, and is dead at `C_E ≈ EM`.
2. **Settle what arm 2 binds, and how many sites per chain.** The bulk-regime margin
   survives n ≲ 30 at the fusion anchor but only n ≲ 3 at the family ceiling. This is a
   chemistry/biophysics question, cheaper than (1), and it is currently unanswered because
   the manuscript carries two incompatible readings of arm 2 (the parent lane's item 5).

A third, separable measurement would close the partitioning reading: **a small-molecule
partition coefficient into a FET-family condensate**, which the Klein 2020 droplet assay
measures directly and which has been run on six non-FET scaffolds but not on this one.

**Unapplied recommendation for the manuscript owner (no edit made, per the contract).**
§8.7 can now cite a bulk-regime bound with named provenance rather than an open caveat, and
should state the intra-condensate value as an explicit experimental prerequisite with the
`C_E* = Kd2` threshold attached. Preparing that as an exact unified diff was out of scope
for this checkpoint and is not claimed as done.
