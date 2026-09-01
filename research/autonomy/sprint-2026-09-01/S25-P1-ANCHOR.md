---
id: DOC-SPRINT-S25-P1-ANCHOR
title: "S25-P1-ANCHOR — position 1 is a primary anchor for none of the six restricting alleles, a weak secondary for four, and the fetch never needed CI"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S25-P1-ANCHOR — the one question S20 left blocking the vaccine paper's near-self null, answered from two fetched allele-specific motif datasets under two declared conventions."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not edit the manuscript and does not decide what lands."
last_verified: 2026-09-01
---

# S25-P1-ANCHOR — position 1 is a primary anchor for none of the six restricting alleles, a weak secondary for four, and the fetch never needed CI

**Item(s):** S20's blocking question and its proposed ledger row 2 (*"Resolve the anchor convention
for the five restricting alleles from an allele-specific motif source"*); route
`RT-VACCINE-COMBINATION`, publication `PUB-VACCINE-PATH`, strategy `ST-IMMUNO`

**Owned paths, named before any was written (charter §2):**

1. `research/modalities/p1_anchor_convention.py` — new; the motif fetch and the analysis
2. `research/modalities/p1-anchor-convention.json` — new; its artifact, and the answer
3. `research/autonomy/sprint-2026-09-01/S25-P1-ANCHOR.md` — this file

**A path I was granted and did NOT take:** a new workflow under `.github/workflows/`. See §5 — it
turned out not to be needed, and adding one would have been the tail wagging the dog.

**⛔ No manuscript was touched.** S20 wrote the conditioned null; another seat may be in that
directory. §6 states what the answer implies for each of its four homes; the driver sequences it.

**Started (UTC):** 2026-09-01T19:52Z **Finished (UTC):** 2026-09-01T20:17Z **Real-dollar cost: $0.**

---

## Verdict

**FIXED — and the answer is not one word, so here it is at the grain it actually has.**

> **Position 1 is a PRIMARY anchor for NONE of the alleles.** That half is unconditional: it holds
> under both threshold rules, under both motif datasets, at every peptide length either dataset
> carries, for all six alleles. Across all 42 allele-by-length
> profiles the two sources carry, P1's motif information content runs **0.187–0.929 bits** against
> **2.307–3.785 bits** at the same allele's strongest position — the whole P1 range sits below the
> 1.0-bit primary floor, and P1 is never among the two most
> informative positions except in HLA-A\*30:02, where it is second.
>
> **Whether it is a SECONDARY (auxiliary) anchor is allele-dependent, and one allele is a real
> exception.** Weak secondary for HLA-B\*07:02, B\*35:01 and B\*44:02; neither primary nor secondary
> for HLA-A\*01:01 and B\*15:01; and a **clear secondary, ranked second of nine positions, for
> HLA-A\*30:02** — which is the lead peptide's second restriction and was not in the question I was
> handed.

**Consequence for the null, stated in both directions because it moves in both.** Under the anchor
sets this measurement produces, **the anchor-only count is 0 hits across 0 of the 11 binders** —
identical to the committed {P2, C-terminus} convention, so the manuscript's null stands as written
rather than collapsing to 6-of-11. But under the most permissive reading the same measurement
supports — counting secondary anchors too — it is **2 hits across 2 of the 11 binders**, and one of
the two is the lead peptide NMPCVQAQY, anchor-only *on HLA-A\*30:02*. It is neither the clean zero
the paper originally claimed nor the six the unsourced variant threatened.

**Three things this does NOT settle, and none may be rounded away:**

1. The manuscript's inference is *anchor ⇒ the T cell cannot see it*. **This measures groove
   selectivity, not receptor accessibility**, and those are different properties. A position the
   allele does not select on may still be buried. Nothing here validates that step.
2. **HLA-A\*30:02 rests on ONE motif source and a FAILED known-positive control** (§3a). It is the
   single allele where P1's signal is strong, and the single allele where I would not lean on it. The
   CI run in §5(2) weakened but did not remove that caveat: the Atlas lists A\*30:02 among the alleles
   with **experimental** ligands, so the motif is measured rather than predicted — but its **depth is
   still unknown**, SYFPEITHI has no matrix for it, and the control still failed.
3. Every input to the re-scored hits is a binding prediction plus a sequence-distance search.
   Sequence distance is not receptor distance.

---

## 1 · What would count as an answer — declared before anything was fetched

⛔ *"Primary anchor" is a definition, not an observation, and this entire problem exists because a
convention went unstated.* So the conventions were fixed first, and both are read out of a fetched
dataset rather than asserted from memory.

**The general class I statement being tested against**, quoted from a source rather than recalled —
according to PubMed, the MHC Motif Atlas paper states: *"Primary anchor residues are mainly found at
the second and last positions of these peptides"*, and describes its Figure 1A as showing *"the two
main anchor residues at the second and last position (P2 and P9 for 9-mers)"*
([10.1093/nar/gkac965](https://doi.org/10.1093/nar/gkac965), Nucleic Acids Research 2023;
PMC9825574). That is a **general class I** statement — it is exactly the convention
`junction-selfsimilarity.json` encodes, and it is silent on the allele-specific question.

**Convention A — motif information content (quantitative, mass-spectrometry derived).** For each
position, the Kullback–Leibler divergence in bits of that position's amino-acid distribution from the
human proteome background:

```
IC(p) = Σ_aa  f(aa,p) · log2( f(aa,p) / bg(aa) )
```

The matrices this runs on are built the way the Atlas paper describes its own: *"The Position Weight
Matrices (PWMs) representing the final motifs were computed by normalizing the PPMs with the amino
acid background frequencies of the human proteome."*

⚠ **AND I FIRST CALLED THIS "exactly the stack height of the Atlas's logo", WHICH IS FALSE.** The CI
run in §5(2) came back with the Atlas F.A.Q., which defines that height as a **different function** —
verbatim: *"These frequencies are then renormalized by the background amino acid frequencies (from the
human proteome), and normalized again to 1 … The total height of the letters at a given position
represents the information content: log(20) + Σₐ pₐ log(pₐ) … the maximum at log₂(20) = 4.3219."* That
is log₂(20) minus the entropy of the background-**corrected** distribution against a **uniform**
reference; mine is the KL divergence of the **raw** distribution from the background. Both are
background-corrected information measures; they are not the same measure. **The artifact now computes
and reports both on every position**, and whether they grade a position the same way is computed
rather than asserted — see §3b.

⛔ **A cut-off on IC is itself a convention, so TWO were applied and both are reported on every row:**

| rule | PRIMARY | SECONDARY |
|---|---|---|
| relative | ≥ 0.50 × the allele's strongest position | ≥ 0.15 × strongest |
| absolute | ≥ 1.0 bits | ≥ 0.5 bits |

★ **The absolute rule is the one the known-positive control validates**, and it is the one the anchor
sets used for re-scoring are taken from. The relative rule mis-grades HLA-A\*01:01's P2 — an anchor
under every published convention — because that allele's C-terminal Y is so dominant that P2 falls to
29 % of it. **Neither rule was tuned to produce the P1 answer: P1's verdict is identical under both.**

**Convention B — the curated SYFPEITHI matrices (ordinal, pooled-sequencing derived).** SYFPEITHI is
the resource that encodes the anchor / auxiliary-anchor distinction as a score rather than leaving it
to a reader's eye, so it is the closest thing to a direct answer to the question as posed. ⛔ **I make
no claim about what SYFPEITHI's score tiers are named.** The claim is purely ordinal: where P1's best
score sits relative to the strongest position's, and relative to the **middle positions P4…PΩ−1**,
which every convention agrees are not anchors.

**The known-positive control, fixed in advance.** Two facts this repository already holds must fall
out of the measurement before its verdict on P1 is worth anything. Neither was fed in:

1. **P2 and the C-terminus are primary anchors** — the general class I rule
   `junction-selfsimilarity.json` states it used.
2. **HLA-A\*01:01 reads P3 as a primary anchor** — the caveat that same artifact raises against
   itself.

---

## 2 · The egress reading, taken before anything was routed

The seat prompt's premise was that this costs *"one CI dispatch"* because *"a seat cannot dispatch
it."* Half of that was right and half was wrong, and the wrong half is worth recording.

**The motif hosts are blocked from this sandbox.** Measured, verbatim:

```
http://mhcmotifatlas.org/home        HTTP/1.1 403 Forbidden      (gateway answered the GET)
https://www.iedb.org/                CONNECT tunnel failed, response 403   curl: (56)
http://www.syfpeithi.de/             403
https://services.healthtech.dtu.dk/  000  (CONNECT refused)
https://rest.uniprot.org/            000
https://files.rcsb.org/…             000
http://tools.iedb.org/mhci/download/ 403
WebFetch mhcmotifatlas.org           {"error_type":"EGRESS_BLOCKED"}
```

`$HTTPS_PROXY/__agentproxy/status` confirms the mechanism: `"kind":"connect_rejected"`,
`"detail":"gateway answered 403 to CONNECT (policy denial or upstream failure)"`.

**But `raw.githubusercontent.com` answers 200 from here**, and both motif datasets I needed live in
public GitHub repositories:

```
curl -o /dev/null -w '%{http_code}' \
  https://raw.githubusercontent.com/GfellerLab/MixMHCpred/c29e4db.../lib/pwm/class1_9/PWM_A0101_1.csv
→ 200
```

★ **So the blocking fetch was never a CI-only fetch, and the seat that could not dispatch could
answer the question anyway.** `ci-escape-hatches` §0 is right that the rung you need is usually lower
than the one you reach for; here the reading that changed the plan cost one `curl -w %{http_code}`.

---

## 3 · What I measured

`research/modalities/p1_anchor_convention.py` fetches both datasets at **pinned commits**, records
every URL with its sha256 and byte count, and computes the profiles. **99 fetches, 27 of them HTTP
404** — every 404 a real absence (a source that carries no matrix for that allele and length),
recorded in `missing_source_rows` and never filled in by a guess.

| dataset | pinned at | what it is |
|---|---|---|
| `GfellerLab/MixMHCpred` v3 PWM library | `c29e4db17abe6266bfee72750efb713459540d18` | position probability matrices of naturally presented mass-spectrometry eluted ligands, divided by the human proteome background |
| `KohlbacherLab/epytope` SYFPEITHI matrices | `de6c5bdcb360d59eb13ff5b49b6349502ae81765` | the curated SYFPEITHI per-allele scores, as redistributed |

Citation the first repository's own README asks for: Tadros et al., *Predicting MHC-I ligands across
alleles and species: How far can we go?*, Genome Medicine (2025),
[10.1186/s13073-025-01450-8](https://doi.org/10.1186/s13073-025-01450-8). Licence, from the same
README: free for academic use; for-profit use requires a separate licence from the Ludwig Institute
for Cancer Research. Recorded in the artifact.

### 3a · The known-positive control — passed for five of six, and the sixth is the story

```
HLA-A*01:01  L9  primary = [2, 3, 9]   P2+Cterm primary = True    A*01:01 P3 primary = True
HLA-B*07:02  L9  primary = [2, 9]      P2+Cterm primary = True
HLA-B*15:01  L9  primary = [2, 9]      P2+Cterm primary = True
HLA-B*35:01  L9  primary = [2, 9]      P2+Cterm primary = True
HLA-B*44:02  L9  primary = [2, 9]      P2+Cterm primary = True
HLA-A*30:02  L9  primary = [9]         P2+Cterm primary = FALSE   ← control FAILED
```

Both predictions land for five alleles, **including the A\*01:01 P3 clause the producing artifact
raises against itself and which nothing fed in.** That is what licenses reading the P1 grades.

⛔ **The control fails for HLA-A\*30:02, and the threshold was not moved to fix it.** For that allele
P2 measures 0.567 bits — below the 1.0-bit primary floor — while P1 measures 0.756 bits and ranks
**second of nine**. Either A\*30:02 genuinely carries a non-canonical anchor layout, or its motif is
less well determined than the others'. The artifact carries the failure on that allele's own verdict
row, and A\*30:02 is also the one allele **SYFPEITHI has no matrix for**, so it is the only row
resting on a single source. *Moving a bar because it failed is the one edit this repository refuses.*

### 3b · The answer, per allele

Convention A is bits (P1 / strongest position / P1's rank among all positions). Convention B is
SYFPEITHI's per-position maximum score (P1 / strongest / highest **middle** position).

| allele | L | A: P1 bits | A: strongest | A: P1 rank | A: grade (rel / abs) | B: P1 / strongest / best middle |
|---|---|---|---|---|---|---|
| HLA-A\*01:01 | 9 | 0.187 | 3.755 | 4 | NEITHER / NEITHER | 1 / 15 / 3 |
| HLA-A\*01:01 | 10 | 0.188 | 3.545 | 4 | NEITHER / NEITHER | 1 / 15 / 3 |
| HLA-A\*01:01 | 11 | 0.217 | 3.236 | 4 | NEITHER / NEITHER | 1 / 15 / 3 |
| **HLA-A\*30:02** | 9 | **0.756** | 3.785 | **2** | SECONDARY / SECONDARY | — no matrix — |
| **HLA-A\*30:02** | 10 | **0.838** | 3.692 | **2** | SECONDARY / SECONDARY | — no matrix — |
| **HLA-A\*30:02** | 11 | **0.841** | 3.533 | **2** | SECONDARY / SECONDARY | — no matrix — |
| HLA-B\*07:02 | 9 | 0.346 | 2.421 | 3 | NEITHER / NEITHER | 2 / 10 / 3 |
| HLA-B\*07:02 | 10 | 0.371 | 2.414 | 4 | SECONDARY / NEITHER | 2 / 10 / 2 |
| HLA-B\*07:02 | 11 | 0.361 | 2.409 | 4 | NEITHER / NEITHER | 2 / 10 / 2 |
| HLA-B\*15:01 | 9 | 0.331 | 2.888 | 4 | NEITHER / NEITHER | 1 / 10 / 1 |
| HLA-B\*15:01 | 10 | 0.408 | 2.984 | 4 | NEITHER / NEITHER | 2 / 10 / 2 |
| HLA-B\*15:01 | 11 | 0.376 | 2.970 | 4 | NEITHER / NEITHER | — no matrix — |
| HLA-B\*35:01 | 9 | 0.377 | 2.407 | 3 | SECONDARY / NEITHER | 1 / 10 / 2 |
| HLA-B\*35:01 | 10 | 0.496 | 2.515 | 3 | SECONDARY / NEITHER | 1 / 10 / 1 |
| HLA-B\*35:01 | 11 | 0.586 | 2.559 | 3 | SECONDARY / SECONDARY | — no matrix — |
| HLA-B\*44:02 | 9 | 0.492 | 2.724 | 3 | SECONDARY / NEITHER | 3 / 10 / 3 |
| HLA-B\*44:02 | 10 | 0.652 | 2.926 | 3 | SECONDARY / SECONDARY | 3 / 10 / 3 |
| HLA-B\*44:02 | 11 | 0.522 | 2.744 | 3 | SECONDARY / SECONDARY | 3 / 10 / 3 |

**Three readings that need saying plainly:**

- **No cell in the "grade" column reads PRIMARY.** Not for any allele, length or rule. The primary
  half of the question has one answer and it is *no*.
- **Nor under the Atlas's own formula, which is the third grading and was added after the CI run
  corrected me.** Across **462 graded positions** the two information measures assign a different
  grade to **17**. ⛔ **None of the 17 turns a NEITHER or SECONDARY into a PRIMARY at position 1**, and
  the only four that cross the PRIMARY line at all go the *other* way — they promote **P2** for
  HLA-A\*01:01 (lengths 8, 10, 12) and HLA-B\*15:01 (13) from SECONDARY to PRIMARY, which strengthens
  the known-positive control rather than the P1 verdict. The two P1 rows that do move — B\*35:01 at
  L10, B\*44:02 at L11 — move only across the SECONDARY/NEITHER line, exactly the boundary already
  flagged as threshold-sensitive. Per-allele P1 grades under the Atlas formula are unchanged in
  substance: A\*01:01 NEITHER; A\*30:02 SECONDARY; B\*15:01 NEITHER; B\*07:02, B\*35:01, B\*44:02
  NEITHER-to-SECONDARY by length.
- **Convention B agrees, by a test that needs no tier names.** In every allele and length SYFPEITHI
  covers, **P1's best score never exceeds the best of the middle positions** — the positions every
  convention agrees are not anchors — while the strongest position scores 10 or 15. Under SYFPEITHI,
  P1 is not distinguishable from the middle of the peptide.

### 3c · The find the seat's own premise hid: there are SIX alleles, not five

⚠ **The question I was handed named five alleles. The committed artifact restricts on six.**

The first version of the script carried the five as a hand-written list plus a check that the list
matched `junction-selfsimilarity.json`. **The check failed on its first run:**

```
declared:  A*01:01  B*07:02  B*15:01  B*35:01  B*44:02
in the artifact:  A*01:01  A*30:02  B*07:02  B*15:01  B*35:01  B*44:02
agree: False
```

**HLA-A\*30:02 calls NMPCVQAQY — the lead peptide — on the 34-allele panel, alongside HLA-B\*15:01**
(`strong_on_34_allele_panel: ["HLA-A*30:02", "HLA-B*15:01"]`). NMPCVQAQY is exactly the peptide whose
near-self neighbour `DMPCVQAQY` differs at **position 1 alone**. So a five-allele answer would have
left the lead peptide's second restriction unexamined **while reading as complete** — and A\*30:02
turns out to be the one allele where P1 carries a real signal. The allele list in the module is now
*derived* from the artifact, never typed.

⚠ **AND THE FIVE DID NOT COME FROM MY PROMPT — THEY COME FROM THE MANUSCRIPT, WHICH KNOWS BETTER
ELSEWHERE IN ITSELF.** I first wrote here that the paper "may not carry" A\*30:02, then checked
instead of leaving it as a guess, and the guess was wrong. `grep -rn "30:02"
research/manuscripts/neoantigen/` returns nine hits: the **abstract** (*"on 34, where the same lead
peptide is also strong on HLA-A\*30:02"*), §2.3 at lines 268/327/337, the predictor-comparison at line
366, the 34-allele panel table at 1305, the coverage table at 1492, and an Appendix C correction at
1516. The paper carries the allele prominently.

⛔ **The defect is narrower and worse than "a missing allele": it is §B3’s own sentence**, at line 675,
verbatim —

> *"**Whether position 1 is an anchor for HLA-A\*01:01, B\*07:02, B\*15:01, B\*35:01 or B\*44:02 is not
> established here**, no allele-specific binding motif being held in this work…"*

Five alleles, in the one paragraph where the question is asked, in a paper that names the sixth in its
own abstract as the lead peptide's second presenting allele. **This is the one-of-a-pair defect
Appendix C of that manuscript already records once**, and it lands on the allele that turns out to
matter most.

### 3d · The near-self hits, re-scored under five named anchor-set definitions

⛔ No single threshold is allowed to drive this count silently. Mismatch positions were **recomputed
from the peptide strings**, not read from the artifact: **0 disagreements** across all 14 records.

| anchor-set definition | anchor-only hits | binders | contact-only | mixed |
|---|---|---|---|---|
| **measured PRIMARY positions (absolute rule)** — the answer row | **0** | **0 of 11** | 5 | 8 |
| measured PRIMARY ∪ SECONDARY — the permissive upper bound | 2 | 2 of 11 | 2 | 9 |
| `{P2, C-terminus}` — the committed convention | 0 | 0 of 11 | 5 | 8 |
| `{P2, P3, C-terminus}` — the artifact's own A\*01:01 caveat | 0 | 0 of 11 | 5 | 8 |
| `{P1, P2, C-terminus}` — ⛔ the unsourced variant | 6 | 6 of 11 | 0 | 7 |

The last row **reproduces S20's 6-of-11 exactly**, which is the cross-check that the re-scoring is
the same computation over the same hits.

**The two hits in the permissive row, named:**

```
NMPCVQAQY   vs DMPCVQAQY    mm=[1]   HLA-B*15:01 + HLA-A*30:02   anchor sets [2,9] and [1,2,9]
GDMPCVQAQY  vs VDMPCVQAQY   mm=[1]   HLA-B*44:02                 anchor set  [1,2,10]
```

Both are anchor-only *only because a SECONDARY position was counted as an anchor*, and NMPCVQAQY's
route runs through **A\*30:02** — the allele whose control failed. That is the weakest link in the
adverse direction, and it is named rather than buried.

### 3e · Mutation-testing the two checks I wrote (charter §7), and one gap they have

⛔ **In scratch copies under the scratchpad, never in the live tree** — that is the 2026-08-27
incident from the other end. Three single-site mutations; a `--selfsim` override was added to the
module for no other reason than to let it run outside its own directory.

| mutation | what it breaks | what the checks did |
|---|---|---|
| `PRIMARY_BITS` 1.0 → 3.0 | the threshold that defines a primary anchor | control **red for all six alleles** ✅ |
| human-proteome background → uniform 1/20 | the normalisation the whole IC definition rests on | control **unchanged — still red only for A\*30:02** ⛔ |
| `mismatch_positions` shifted by one | the recompute-vs-recorded cross-check | **13 disagreements reported** ✅ |

⛔ **The middle row is a real gap and it is not smoothed over: the known-positive control cannot
detect a wrong background.** Reported rather than patched, because the reason it cannot is itself the
finding — P2 and the C-terminus dominate under either normalisation, so the control has nothing to
catch. That gap turns out to be the sensitivity check I would otherwise have had to construct:

| allele | P1 bits / rank / grade, human background | P1 bits / rank / grade, uniform background |
|---|---|---|
| HLA-A\*01:01 | 0.187 / 4 / NEITHER | 0.216 / 4 / NEITHER |
| HLA-A\*30:02 | 0.756 / 2 / SECONDARY | 0.762 / 2 / SECONDARY |
| HLA-B\*07:02 | 0.346 / 3 / NEITHER | 0.337 / 3 / NEITHER |
| HLA-B\*15:01 | 0.331 / 4 / NEITHER | 0.353 / 4 / NEITHER |
| HLA-B\*35:01 | 0.377 / 3 / NEITHER | 0.394 / 3 / NEITHER |
| HLA-B\*44:02 | 0.492 / 3 / NEITHER | 0.494 / 3 / NEITHER |

**Every grade, every rank and every re-scoring count is identical** (`measured_primary`: 0 anchor-only;
`measured_primary_or_secondary`: 2). **The answer does not depend on the one modelling choice
convention A makes.**

### 3f · Gates (charter §6 — scoped, not the whole thing)

```
python3 research/manuscripts/lint_consistency.py   → 0 ERROR across 26 target file(s)
python3 research/manuscripts/lint_claims.py        → 0 ERROR, 171 WARN across 129 file(s)
```

No WARN cites either of my paths (`grep -iE "p1[-_]anchor"` over the lint output returns nothing).
`preflight.sh` is the driver's, on a settled tree.

---

## 4 · What I changed

### `research/modalities/p1_anchor_convention.py` — new

Fetches both motif datasets at pinned commits, computes per-position information content (mixing
multi-specificity motifs with the library's own `alphas.txt` weights rather than taking motif 1),
parses the SYFPEITHI matrices **without importing or `eval`ing them** — they are Python source files
fetched over the network — runs the known-positive control, grades P1 under both threshold rules and
both conventions, and re-scores the committed near-self hits under five named anchor-set definitions.
Pure stdlib. Every fetched blob's URL, sha256 and byte count is in the artifact.

### `research/modalities/p1-anchor-convention.json` — new

The artifact. Carries the per-allele verdicts, the full per-position profiles for every allele and
length either source covers, the SYFPEITHI score profiles, the control rows with the failing allele
named, the five re-scorings with their buckets, the 27 missing source rows, and the provenance block.

### Nothing else

⛔ **No manuscript, no memo, no ledger, no `systems/`, no workflow.** §6 says what the answer implies
for the four places the manuscript carries the conditional; applying it is the driver's sequencing
call, and another seat may be in that directory.

---

## 5 · What I could not do, and what it is actually waiting on

1. **A workflow was in my owned paths and I did not write one — deliberately, and this is the "blocked
   is usually wrong" case in reverse.** The route this seat existed to open turned out not to need
   opening: `raw.githubusercontent.com` answers 200 from the sandbox, the script is $0 and pure
   stdlib, and it regenerates its artifact in place. `ci-escape-hatches` rung 2 says build a workflow
   *only when rung 1 will be re-run*; a workflow here would exist to run a script the dev sandbox
   already runs. **If a future session needs this in CI it is one `run: python3
   research/modalities/p1_anchor_convention.py` step in any existing CPU workflow.**

2. **An independent THIRD motif source, and a ligand count per allele — dispatched, not yet read.**
   Both my sources are matrix-derived, and A\*30:02 rests on one of them with a failed control. The
   MHC Motif Atlas publishes the underlying ligand lists and per-allele ligand counts, which would
   say whether A\*30:02's motif is thinly supported. Its host 403s from here, so it went to CI:

   > **`fetch-literature.yml`, `slug=browser-fetch`, run id `33553076455`, ref `main`,
   > `https://github.com/trimcrae/Rare-cancers/actions/runs/33553076455`** — a headless-Chromium
   > fetch of the Atlas class I pages plus IEDB's MHC-I download page, with link harvesting on, so a
   > second dispatch can name the data files instead of guessing their URLs. It publishes
   > `research/literature/browser-fetch.json` to `main`.
   >
   > Dispatched at `ref=main` rather than at the sprint branch on purpose: the workflow's code is
   > identical on both refs, and its publish step pushes to the triggering ref, which would have put
   > `origin` ahead of the driver mid-sprint.

   ⚠ **A CI run does not wake a session. This one completed inside my turn and I read it** —
   `status: completed`, `conclusion: success`, 20:03:29Z → 20:07:14Z, result published to
   `main:research/literature/browser-fetch.json` (fetched back at HTTP 200). **What it returned, at
   its true weight:**

   | target | status | what it gave |
   |---|---|---|
   | `mhcmotifatlas.org/home` | 200 | reachable from a runner; 403 from the sandbox |
   | `mhcmotifatlas.org/class1` | 200 | ★ the Atlas's curated allele list — **HLA-A\*30:02 is in it**, i.e. its motif is built from experimental eluted ligands, not predicted |
   | `mhcmotifatlas.org/faq` | 200 | ★★ the Atlas's own **definition of logo information content**, which corrected §1 |
   | `mhcmotifatlas.org/class1_download` | *no status* | the path does not exist; the downloads are buttons on `/class1`, not a page |
   | `tools.iedb.org/mhci/download/` | 200 | reachable; not yet mined |

   **It changed two things and neither was the thing I dispatched it for.** It corrected my
   description of the information measure (§1, §3b) — which is the more valuable of the two — and it
   removed part of the A\*30:02 caveat: that allele is one of the Atlas's alleles *with naturally
   presented ligands*, so its motif is experimental. ⛔ **What it did NOT give is the per-allele ligand
   COUNT**, which is what would say whether A\*30:02's motif is thinly supported, and no link was
   harvested (the download controls are script-driven, so the file URLs are still unknown rather than
   guessed). The A\*30:02 caveat in §3a therefore stands in weakened form: experimentally grounded,
   depth unknown, control still failed, still one source.

3. **Whether "not an anchor" implies "the T cell can read it".** ⛔ **This is the real remaining gap,
   and it is not the one the ledger row names.** Motif information content measures how selective the
   groove is for a side chain. The manuscript's ranking rests on whether a receptor can *see* that
   side chain, which is structural. A position can be unselective and still buried. Settling it needs
   per-position solvent accessibility over class I pMHC crystal structures — `files.rcsb.org` returns
   `000` from here, so it is a CI fetch, still $0, still no human. **Until it is done, "P1 is not an
   anchor, therefore a P1 difference is one the T cell can read" is an inference the paper is making,
   not a result this seat delivered.**

4. **S20's second premise is untouched and stays untouched** — whether the near-self neighbours are
   themselves presented on the same allele. No motif dataset answers it; it is the presentation
   question B2 is bounded by.

---

## 6 · What the answer implies for the manuscript — for the driver to sequence

⛔ **I did not make these edits.** Each names a place S20 left conditional and what the measurement
now licenses. **Every one of them must keep the conditional's *form* while naming the source**: the
claim moves from *"if position 1 counts as an anchor, which no allele-specific motif held here can
settle"* to *"position 1 is not a primary anchor for any restricting allele, from two motif datasets
under two declared conventions"* — which is a different sentence, not a deletion.

| where | what it says now (S20) | what the measurement supports |
|---|---|---|
| abstract, ~line 94 | *"…though six of the 11 would if position 1 counted as an anchor, which no allele-specific motif held here can settle."* | Position 1 is a primary anchor for none of the six restricting alleles; the anchor-only count under the measured primary sets is 0 of 11. The six-of-11 figure belongs to an unsourced variant and can be retired from the abstract. |
| §B3, caveat 1 | the P1-inclusive count carried as a live alternative | Replace with the measured grades; keep the **2 of 11** permissive-reading figure, because dropping it would be the overclaim in the other direction. |
| §3 limits table, row B3 | *"…6 of 11 if position 1 counts, which is not established here"* | It is now established, and the answer is that it does not count as a primary anchor. Row becomes 0 of 11 with the source named. |
| §B3 second caveat / falsifier 3 in the memo | conditional on P1 | Same substitution. |
| §B3, line 675 — *"Whether position 1 is an anchor for HLA-A\*01:01, B\*07:02, B\*15:01, B\*35:01 or B\*44:02…"* | five alleles named | **SIX.** The same paper names HLA-A\*30:02 in its own abstract as the lead peptide's second presenting allele on the 34-allele panel. The sentence must list six — and A\*30:02 is the allele where P1 *is* a secondary anchor, so the correction and the answer land in the same sentence. |
| **new** | — | The **anchor ⇒ TCR-invisible** inference is now the load-bearing unvalidated step, and it should be stated as an inference in §B3 rather than carried as a definition. |

**⛔ And one boundary that does not move.** None of this is a presentation, immunogenicity or safety
result. An anchor-only near-self neighbour is a hypothesis about why a repertoire might have been
deleted, never a measurement that it was, and a binding prediction is a binding prediction.

---

## 7 · Ledger rows the driver should write

I may not write these (charter §2). Proposed:

1. **Close S20's proposed row 2** — *"Resolve the anchor convention for the five restricting alleles
   from an allele-specific motif source."* `kind: experiment`, `state: done`, `cost_class: free`,
   `last_evidence_utc: 2026-09-01`, evidence `research/modalities/p1-anchor-convention.json` and this
   file. ⚠ **Amend its title from "five" to "six"** — see §3c.

2. **New row — "Apply the P1 answer to the four homes of the conditioned null in the vaccine paper."**
   `kind: hardening`, `state: queued`, `cost_class: free`, local. §6 is the map. A path this seat did
   not own.

3. **New row — "§B3 line 675 names five restricting alleles; there are six."** `kind: hardening`,
   `state: queued`, `cost_class: free`. The paper names HLA-A\*30:02 in its own abstract and in five
   other places, and omits it from the one sentence that asks the anchor question — the one-of-a-pair
   defect its Appendix C already records once. Found by a guard, not by reading — §3c.

4. **New row — "Is a low-information motif position a position a TCR can read? Per-position solvent
   accessibility over class I pMHC crystal structures."** `kind: experiment`, `state: queued`,
   `cost_class: free`, CI (`files.rcsb.org` 403s from the sandbox). ★ **This is now the load-bearing
   unvalidated step under §B3's ranking** — it inherits the priority S20's row 2 had, because the
   question the ranking actually turns on has moved one link down the chain.

5. **New row — "Get HLA-A\*30:02's ligand COUNT from the MHC Motif Atlas and confirm its P1 signal
   from a third source."** `kind: hardening`, `state: queued`, `cost_class: free`, CI. Run
   `33553076455` is **read and closed** — it confirmed A\*30:02 is one of the Atlas's alleles with
   experimental ligands and corrected this seat's description of the information measure, but the
   Atlas's download controls are script-driven, so the ligand-list file URLs remain **unknown rather
   than guessed**. A follow-up needs a browser that clicks, not one that reads. §5(2).

6. ⚠ **Note for whoever writes row 2:** the substitution is not a deletion. Removing the conditional
   without naming what settled it would leave the manuscript asserting the null more strongly than
   its own evidence chain supports, because the *anchor ⇒ TCR-invisible* link is still open (row 4).
