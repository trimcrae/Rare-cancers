---
id: DOC-PORTFOLIO-INVESTIGATION-PUB-ATR
title: "PUB-ATR lane — is the inherited class an FET class or an EWSR1 class?"
level: L4
kind: investigation
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# PUB-ATR — boundary of the class-inheritance premise

⛔ The posted/frozen ATR package is UNCHANGED by this lane. Nothing here edits, re-reviews or
reopens `emc-atr-vulnerability-assessment.md`, `emc-atr-collaborator-package.md`, the census or any
figure/panel work. PUB-ATR-PANEL-ASK and the draft-identity blocker are an owner decision and are
untouched. ⛔ No efficacy, potency, dose, safety or therapeutic-window claim is made or implied.

## 1 · The question

**PUB-ATR inherits an ATR dependency for EMC from "the FET class". Within the source's own cached
full text, which of the four measured fusions appear in the DSB-recruitment / RG-dependence arm —
the only arm the structural precondition census speaks to — and does the census's EWSR1-derived
zero-RG criterion transfer to EMC's non-EWSR1 partners, TAF15 and FUS?**

## 2 · Paper-level merit

The whole in-silico case that survives parts C and D is *structural*: EMC's fusion retains an
EWSR1 N-terminus that resembles a measured one, and loses RG dipeptides. That argument's strength is
exactly the breadth of the class it borrows from. If the recruitment arm is EWSR1-only, then
"inherited from the FET class" is really "inherited from EWSR1", and two consequences follow that
matter to a patient-facing programme: (i) EMC's **minority** fusions (TAF15::NR4A3, FUS::NR4A3)
inherit from **zero** measured members of their own FET protein, so the assessment's transfer is
weakest exactly where the disease is most heterogeneous; (ii) the census's comparator axis
(`fraction_of_wildtype_RG_retained`, calibrated on EWSR1's 30 RG dipeptides and its 299-residue
RGG-free ceiling) has no measured anchor in FUS or TAF15 units. Both are cheap to settle offline and
both sharpen a limit the assessment already gestures at without quantifying.

## 3 · The exact evidence gap, and why it is not prior work

Already done elsewhere, and **not** repeated here: the EMC-side TAF15/FUS *breakpoint sweeps*
(`emc-fet-idr-census.json` → `emc_TAF15_and_FUS_breakpoint_sweep`), the per-type EMC comparative
(`emc_vs_measured_fusions_comparative`), parts C and D of the assessment, and the drug-panel re-cut.

Not done anywhere in the repo before this lane:

* the census's `_control_rule` states *"AT LEAST ONE reported type of EACH measured fusion must read
  `PRECONDITION_MET`"*, but `positive_controls` implements it for **two** of the four measured
  fusions, both EWSR1. **Nobody had asked what assay the other two were measured in.**
* the census annotates each wild-type FET protein but never evaluates its **own criterion** on
  TAF15 or FUS at the retained lengths it uses for EWSR1 — so the criterion's family-dependence was
  unquantified.

Inputs used, all committed and read-only: `atr-hrd-sarcoma-series-inputs.json`
(`mechanism_fulltext_xml`, PMC10187251, cached verbatim), `fet-sequences-cache.json`,
`emc-fet-idr-census.json`.

## 4 · The bounded step taken, and its result

`fet_class_inheritance_audit.py` → `fet-class-inheritance-audit.json`. Offline, $0, no network, no
new sequence, breakpoint or citation introduced.

### Q1 — assay-level audit of the four measured fusions (cached main text)

| fusion | FET protein | mentions | in DSB-recruitment / laser arm |
|---|---|---|---|
| EWSR1::FLI1 | EWSR1 | 104 | **yes** (17 sentences) |
| EWSR1::ATF1 | EWSR1 | 14 | **yes** (4) |
| EWSR1::WT1 | EWSR1 | 3 | **yes** (1 — *"we also verified that the DSRCT fusion EWSR1-WT1 is recruited to laser-induced DSBs"*) |
| **FUS::CHOP** | **FUS** | **1** | **no** |

FUS::CHOP's single appearance in the cached text is as **one cell line in the ATR-inhibitor
sensitivity panel**: *"…and 1 myxoid liposarcoma cell line (FUS-CHOP), and multiple non-FET
rearranged cancer cell lines as controls."*

⭐ **Result: in the cached record, every fusion in the recruitment / RG-dependence arm is an EWSR1
fusion. The one non-EWSR1 member of the four enters only through the drug-sensitivity panel — the
class of evidence that PUB-ATR's own part D shows is not ATR-specific (paclitaxel and both PARP
inhibitors move further than either ATR inhibitor after the same correction).** The RG-based
structural mechanism is, on this record, an **EWSR1** result generalised to FET by family membership.

### Q2 — does the EWSR1-calibrated criterion transfer? `fraction_of_wildtype_RG_retained` at the census's own landmark cuts

| retained N-terminal length | EWSR1 | TAF15 | FUS |
|---|---|---|---|
| 161 (pinned TAF15 e6 junction) | 0.000 | **0.000** | 0.000 |
| 264 (Ewing type-1 measured half; EMC type 2 is byte-identical) | 0.000 | 0.161 | **0.333** |
| 324 (EWSR1::ATF1 e8, a measured fusion) | 0.233 | 0.161 | 0.333 |
| 431 (EMC type 1, commonest) | 0.267 | 0.581 | 0.583 |
| 472 (EMC type 5) | 0.367 | 0.645 | 0.583 |

Longest zero-RG N-terminus: EWSR1 **299**, FUS **212**, TAF15 **174** (all three reproduce the
census's own `first_RG_dipeptide_at`, so this is a recomputation and not a re-annotation).

⭐ **Result: the zero-RG criterion is EWSR1-shaped.** At the *measured* retained length (264) a FUS
fusion would retain **0.333** of its wild-type RG — above the entire calibration range spanned by
the measured EWSR1 fusions (max **0.267**, EWSR1::ATF1 e10) — and a TAF15 fusion **0.161**. The
census's calibration therefore cannot be read across proteins: the same architectural cut is
"clean" in EWSR1 and "RG-retaining" in FUS purely because FUS's RGG region begins 87 residues
earlier. ✅ The one *pinned* non-EWSR1 EMC junction (TAF15 exon 6, residue 161) is the exception —
it is genuinely zero-RG, with 13 residues of margin.

## 5 · Artifact · validation · provenance · limitations · stop condition

* **Artifact:** `fet_class_inheritance_audit.py`, `fet-class-inheritance-audit.json`, `checks/`
  (two execution attempts, both exit 0; attempt 01 is retained even though its arm regex
  under-classified FUS::CHOP's sentence — attempt 02 adds the `cell_line_panel_membership` arm).
* **Validation / baseline:** Q2 is self-checking against the frozen census — `first_RG_at` is
  recomputed from sequence and compared to the census's `wild_type_annotation`
  (`agrees_with_census_annotation: true` for all three proteins), and the EWSR1 row reproduces the
  census's published 0.000 / 0.233 / 0.267 / 0.367. Q1 prints a verbatim quote for every arm it
  scores, so each classification is checkable by eye.
* **Provenance:** three committed artifacts, listed in the JSON's `_inputs`. No network call, no
  denied source touched, no B1/B2/B4 route approached, no R1–R4 restart.
* **Limitations:** Q1 audits the **cached main text only** — Supplementary Notes, figures and tables
  are not in this repo's cache, so "does not appear in the recruitment arm" bounds the cached record
  and not the source's whole body of work; this is a claim about what this repository can currently
  support, and a supplementary figure could overturn it. Q2 is a sequence geometry: it locates RG
  dipeptides, it does not show that any fusion is recruited to a break or suppresses ATM. Nothing
  here measures ATR dependency, and nothing here is an EMC finding.
* **Stop condition:** stop if the source's supplementary material (not currently cached) shows
  FUS::CHOP in the recruitment or RGG-mutant arm — Q1's conclusion would then be wrong and must be
  withdrawn. Q2 stops as computed; it needs no further work.

## 6 · Honest outcome and what follows

This is a **negative/boundary result, not a new positive claim**: it narrows the assessment's
inherited class rather than extending it, and it is preserved as such. Two things it does **not**
do — it does not settle PUB-ATR-PANEL-ASK, and it does not license any edit to the frozen package.

**One observation is recorded for the owner and is deliberately left unapplied.** The assessment's
banner reads *"The source reports four fusions across four diseases"* and describes the mechanism as
measured on them. On the cached full text, the **recruitment / RG arm** carries three, all EWSR1;
the fourth is a drug-panel cell line. Whether that warrants a wording change is an owner decision on
a frozen document. **No diff is proposed or applied here, and the package is untouched.**

**Next credible independent work** (not started): the census could carry EWSR1::WT1 as a third
positive control — it is now shown to be in the right assay arm — provided its exon-level junction
is sourced with a quote in the junction registry the way TAF15's was; and any future non-EWSR1 EMC
claim needs a comparator axis expressed in that protein's own RG units, since this lane shows the
EWSR1 axis does not carry across.
