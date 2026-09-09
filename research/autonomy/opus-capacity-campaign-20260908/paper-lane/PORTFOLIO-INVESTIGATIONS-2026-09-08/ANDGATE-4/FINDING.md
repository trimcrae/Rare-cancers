---
id: DOC-PORTFOLIO-INVESTIGATION-ANDGATE-4-2026-09-09
title: "ANDGATE-4 — the selectivity-inversion error did not propagate: verified absent from every shared surface, live in two lane artifacts, and corrected by an unapplied diff"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: ANDGATE-4
continues: ANDGATE-3, ANDGATE-2, PUB-ANDGATE
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# ANDGATE-4 — testing ANDGATE-3's containment claim

## 1. The concrete question

ANDGATE-3 established that PUB-ANDGATE's reported selectivity **inversion** ("0.70×, 0.58× above EM
— the molecule prefers wild-type NR4A3 to the fusion") is a modelling artifact of an in-trans term
present in one partition function and absent from the other, and then asserted — **without
searching** — that the defect is contained in this campaign's lane artifacts because "the manuscript
makes no inversion claim", offering no diff. **Is that containment claim true?** Concretely: does the
symmetric result re-derive independently, and does the inversion claim or either of its numbers
appear anywhere on a shared surface — the AND-gate manuscript, `systems/graph/*.json`,
`systems/views/`, `pinned-figures.json`, the treatment-lanes roadmap, the program map, or any other
lane?

## 2. Paper-level merit

An unsearched containment claim is the difference between a contained lane finding and a propagated
error, and it is the cheapest possible thing to get wrong: ANDGATE-3 reasoned that the manuscript
"makes no inversion claim" from having read §8.7, not from having looked. The claim it protects is
the AND-gate design's entire patient-relevant argument — wild-type NR4A3 is tumour-suppressive
(AML on combined *Nr4a1/Nr4a3* loss; HCC/breast/lymphoma), so "spares wild-type NR4A3" is the whole
case for the AND-gate over the shared-LBD degrader. A statement that the molecule *prefers* wild-type
NR4A3 is the maximal-damage inversion of that argument. Verifying — rather than assuming — that it
never reached a manuscript, a canonical graph object or a pinned figure is a load-bearing check, it
is finite, and it is pure grep-and-arithmetic on committed inputs: no ligand, no sampling, no data,
no GPU.

## 3. The exact evidence gap

* ANDGATE-3 §6 asserts "The **manuscript makes no inversion claim**" and "The defect lives entirely
  in this campaign's own lane artifacts", then concludes "**No shared file needs changing, so no diff
  is offered and none was applied.**" No search is recorded in its `checks/`: its two checks are the
  symmetric model run and an inversion **recheck of PUB-ANDGATE's own JSON**. The negative was
  reasoned, not measured.
* The naive search does not find the site. PUB-ANDGATE's prose wraps mid-phrase —
  `…the molecule prefers\n   wild-type NR4A3…` — so a single-line `grep -i "prefers wild-type"`
  returns the ANDGATE-3 quotation and **misses the origin**. Any containment check that used it
  would have concluded, wrongly, that the phrase exists only inside a superseded marker.
* This is not a re-run of either parent model and not a new baseline review of the manuscript. It is
  the propagation search neither lane performed, plus the independent re-derivation ANDGATE-3's own
  numbers had not received from outside its own code.

## 4. The step taken

### 4a. Independent re-derivation (checks/01, checks/05)

`andgate4_independent_rederivation.py` → `andgate4-independent-rederivation.json`. Written from the
**algebra as stated in the two parent FINDING.md files**, deliberately not importing, exec'ing or
copying either parent script. Pure stdlib, CPU, no network, no external data.

**Reproduced digit for digit (10 of 12 identity checks, PASS):**

| Quantity | Committed | ANDGATE-4 |
|---|---|---|
| PUB-ANDGATE `fusion_fraction_bound` @ C_E=0 | 0.5261 | 0.526066 |
| PUB-ANDGATE `wildtype_fraction_bound` @ C_E=0 | 0.0909 | 0.090909 |
| cis-only window | 5.79 | 5.78673 |
| **symmetric** window @ C_E = 3 mM | 1.064 | **1.063759** |
| **symmetric** window @ C_E = 10 mM | 1.008 | **1.008258** |
| retained fraction, asymmetric, n = 10 @ 200 nM anchor | 0.9822 | 0.982175 |
| retained fraction, symmetric, n = 10 @ 200 nM anchor | 0.9822 | 0.982192 |

**Monotonic decay to unity: confirmed and extended.** Over 17 sweep points from `C_E` = 0 to 10 M the
symmetric window is monotonically non-increasing, **> 1 at every point**, and → 1.000000 in the
limit; the asymmetric window → 0.526066, which is exactly what manufactured the "inversion".
The algebraic reason is recorded: the symmetric numerator exceeds its denominator by
`n·(EM + Kd1)/Kd2 > 0` for every `C_E`, so no inversion is possible for any parameter choice.

**★ Two identity checks FAILED, and the failure is the finding of §4a** (`checks/01/exit_code.txt`
= **1**, preserved; not softened, not retried into a pass):

* **`0.700` does not reproduce.** The exact asymmetric value at `C_E` = 3 mM is **0.695765**.
  PUB-ANDGATE committed `"window": 0.7` — a **2-dp** value. **ANDGATE-3's own artifact prints
  0.696.** The figure "0.700" appears only in ANDGATE-3's *prose*, which re-quoted a 2-dp number
  with a spurious third digit while calling it reproduced "digit for digit".
* **`0.580` does not reproduce, and is unevidenced in ANDGATE-3.** The exact value is **0.578152**
  (committed 2-dp as `0.58`). More importantly, **ANDGATE-3's sweep stops at `C_E` = 3 mM** — the
  10 mM row is absent from its committed JSON (checks/05). So neither `0.580` nor its symmetric
  partner `1.008` is backed by ANDGATE-3's own artifact. ANDGATE-4 computes 1.008258 independently,
  so **1.008 is arithmetically correct but was, in ANDGATE-3, a prose figure with no evidence
  behind it.**

**This does not overturn ANDGATE-3's conclusion.** The arithmetic agrees everywhere; the defect is
precision hygiene and one unevidenced prose figure. It is recorded because a "digit for digit"
claim that quietly adds a digit is exactly the kind of drift this campaign exists to catch.

### 4b. Exhaustive propagation search (checks/02, checks/03)

Terms: `invert`/`inversion`/`inverted`; `prefers wild-type` single-line **and** across a line break
(`perl -0777`, which is what finds the origin); `0.70×`/`0.58×`/`0.70x`/`0.58x`; `0.696`/`0.578`;
below-unity paraphrases (`below 1`, `below unity`, `less than one`, `under 1`, `sub-unity`, `<1x`);
`C_E`; `in-trans`/`in trans`/`trans-competition`. Whole repo, then each named target individually.

Full table with file and line in **`SITE-LIST.md`**. Summary:

* **(b) live claim — 2 sites, both PUB-ANDGATE's own:** `PUB-ANDGATE/FINDING.md:87–88` (the prose,
  no superseded marker) and `PUB-ANDGATE/fusion-andgate-trans-competition.json`
  `trans_competition_sweep[11]`,`[12]` (the data it is read off).
* **(c) inside an explicit superseded marker — 4 sites, all correct as they stand:**
  `ANDGATE-3/FINDING.md:86` and `:146`, `ANDGATE-3/andgate3_symmetric_trans_model.py:224–225`,
  `ANDGATE-3/andgate3-symmetric-trans-competition.json:133`.
* **(a) correctly absent — every shared surface.** The AND-gate manuscript carries **no** inversion
  claim and **no** window value below 1 (5.5× base, ~11× ceiling, 1.8× strong-arm-1 collapse,
  9.9–11.0× linker sweep); §8.7 says only that the mode "is not modelled". `systems/graph/*.json`:
  `MOD-ANDGATE` and `RT-ANDGATE` carry no selectivity figure at all. `systems/views/`: none.
  **`pinned-figures.json`: exit 1, no match — there is no AND-gate pin of any kind.** Program map and
  treatment-lanes roadmap: their `invert` occurrences are the covalent-mechanism, GPU-card-probe,
  Route-B, pmx and PARP-1 items, none of them this. All 89 other lane directories: none. ANDGATE-2
  inherits the defective `f_fusion` **structurally**, but every number it commits sits at
  `C_E` ≤ 5 µM where the two curves differ by < 1%, so it states no inversion and needs no correction.

**ANDGATE-3's containment claim is TRUE — now on evidence rather than on inference.** The error did
not propagate. That is the result, and it is not manufactured into something larger.

### 4c. The unapplied diff for the one live site

Because category (b) is non-empty, a diff is produced —
**`UNAPPLIED-pub-andgate-finding-inversion-correction.patch`**, against
`PUB-ANDGATE/FINDING.md`, **not applied**. It replaces the inversion sentence with "asymptotes to
unity from above and never falls below it", and **preserves the superseded wording verbatim inside a
dated correction block** ("Correction, 2026-09-09") that states the omitted term, the symmetric
window formula, the reason no inversion is possible, the replacement values 1.064 and 1.008, and the
two precision notes from §4a. It also marks the JSON's two superseded sweep rows as retained records
rather than current results, instead of silently rewriting another lane's data.

**Proof:** `git apply --check --verbose` → **exit 0** (`checks/04/exit_code.txt`), with
`git status --porcelain` on the target file empty and the original string still present afterwards —
i.e. verified applicable and verifiably **not applied**.

## 5. Artifact · validation · provenance · limitations · stop condition

**Artifact.** `andgate4_independent_rederivation.py` → `andgate4-independent-rederivation.json`;
`SITE-LIST.md`; `UNAPPLIED-pub-andgate-finding-inversion-correction.patch`; `checks/01`–`05`.

**Validation / baseline.** The 12 identity checks against the committed values of two prior lanes are
the baseline; the script exits **1** on any drift and did so, and that run is preserved unmodified.
The diff is validated by a real `git apply --check` exit code. The absence result is validated by
per-target exit codes, including the `pinned-figures.json` **exit 1** that proves no match rather
than asserting it.

**Provenance.** Kd1 = 10 µM, Kd2 = 100 µM, EM = 1 mM, L = 1 µM — the manuscript's own illustrative
values, unchanged. `C_E` and `n` are swept, never asserted. The 200 nM anchor is carried from
ANDGATE-2 **with its caveat intact** (it is EWS/FLI1, not wild-type EWSR1) and is an anchor, not a
`C_E`. Every execution attempt, failures included, is in `checks/` with command, stdout, stderr and
real exit code.

**Limitations.**
1. **Conditional and bounding only.** No validated, selective, cell-active EWSR1-LC arm-2 ligand
   exists in the public record. Every number here is a property of a **model**, and none of it is an
   EMC efficacy, safety, selectivity-as-therapeutic-property, therapeutic-window or
   clinical-readiness claim. No wet lab, no GPU, no docking, no structure prediction, no new
   sampling, no paid API, no publication, no outreach, no direct HTTP egress.
2. **An exhaustive search is exhaustive over the terms it uses.** It is bounded by the term list in
   §4b, which was deliberately widened after the line-break miss. A paraphrase using none of those
   words could still exist; the search is strong evidence of absence, not a proof.
3. The search covers the working tree at this checkpoint, not repository history.
4. The trans bridge is still charged **no** steric or configurational penalty on either side, and
   multiplicity is `n` independent equivalent sites with no cooperativity. `n_cis ≤ n_trans` remains
   the more likely truth and is **not** assumed.
5. Occupancy, not degradation. The degradation model is untouched.

**Stop condition — reached.** Complete when the symmetric result was independently re-derived (with
the two non-reproducing digits reported rather than smoothed), every named surface was searched and
classified with a real exit code, and the one live site had an unapplied diff proved by
`git apply --check`. It stops there: it does not estimate `C_E`, adopt any `n`, reopen the arm-2
ligand gate, edit any shared file, or edit another lane's artifacts.

## 6. Carried forward unsoftened

* **Symmetric `n` does NOT rescue the multiplicity fragility.** Against an **n-matched** cis-only
  baseline the retained fraction at the 200 nM anchor with n = 10 is **0.9822 asymmetric vs 0.9822
  symmetric** (independently reproduced: 0.982175 / 0.982192). The correction changes the *absolute*
  window, not the shape of the decay. ANDGATE-2's fragility conclusion survives intact.
* **The bulk verdict is unchanged.** At the bulk-nucleoplasmic anchors the correction moves the
  retained window by well under 1%. The verdict rests, as it did, entirely on **in-hub `C_E` — the
  free concentration of engageable wild-type EWSR1-LC arm-2 sites — which remains UNKNOWN in this
  repository, not zero.** Nothing computational substitutes for measuring it.

## 7. Next credible independent work

1. **Unchanged and still decisive:** measure in-hub and nucleoplasmic free engageable wild-type
   EWSR1-LC site concentration in a fusion-bearing cell (ANDGATE-2 item 1). Wet lab; unavailable here.
2. **Owner action, ready:** the parent of PUB-ANDGATE applies the diff in this directory, and
   re-emits `fusion-andgate-trans-competition.json` from a `f_fusion` that takes `C_E`. Until it
   does, sites b1/b2 in `SITE-LIST.md` remain live, and **no later lane may carry the "inverted /
   prefers wild-type" statement forward** — ANDGATE-3's prohibition, now with the search behind it.
3. **Gating item, still open:** the manuscript carries two incompatible readings of arm 2 (discrete
   IDR contact vs condensate partitioning) and only the first is modelled. No further modelling in
   this lane is well-posed until that is resolved. **Not opened here.**
