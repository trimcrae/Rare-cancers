---
id: DOC-SPRINT-S28-PROSE-C
title: "S28-PROSE-C — the roadmap, surface-target, neoantigen and ATR papers, split to the ceiling"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S28-PROSE-C — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S28-PROSE-C — 11 over-ceiling sentences across four papers: 10 split, 1 deferred, 1 paper already clear

**Item(s):** S5-READABILITY follow-through for `PUB-EMC-PROGRAM`, `PUB-NEOANTIGEN`,
`PUB-SURFACE-TARGETS`, `PUB-ATR` (`publish_bar` clause 7, `readable_enough_to_review`)
**Owned paths:** `research/manuscripts/program/emc-treatment-roadmap.md`,
`research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md`,
`research/manuscripts/surface-targets/emc-surface-target-landscape.md`,
`research/manuscripts/dependency/emc-atr-vulnerability-assessment.md`, this file
**Started/Finished (UTC):** 2026-09-01T19:41Z — 2026-09-01T19:56Z

## Verdict

**PARTIAL — and the residue is not mine to fix.**

- **`PUB-SURFACE-TARGETS` — FIXED.** 2 over-ceiling → **0**. Clause 7 FAIL → PASS. Word count
  **unchanged at 10,184**; caution markers **byte-identical**.
- **`PUB-EMC-PROGRAM` — 8 of 9 FIXED, 1 DEFERRED.** Every sentence I was allowed to touch is split
  (9 → 1). The one that remains is the **72-word trabectedin reference sentence another seat is
  actively rewriting**, which my prompt forbids me to touch. Clause 7 therefore stays **FAIL**, on
  that sentence alone. ⭐ **And the trabectedin correction is what created it** — §1.3 below has the
  measurement.
- **`PUB-ATR` — REFUTED / NO-CHANGE-NEEDED.** Already **0 over-ceiling** and already **PASS** at
  `HEAD b6397c5`, exactly as S5 predicted after the splitter fix. Nothing was changed.
- **`PUB-NEOANTIGEN` — FIXED BY S22-PROSE-A WHILE I HELD IT.** 4 over-ceiling at 19:41Z, **0** at
  19:48:23Z, from an edit I did not make. It is a good pass (caution byte-identical, ±1 word) and I
  did **not** duplicate, revert or re-touch it — **no pre-S22 copy of that file was ever taken, so
  nothing in this seat could have reverted it.** §5 records the collision, §5.1 the evidence that I
  never wrote the file, and §5.2 one word-count figure in the driver's message I could not reproduce.

⛔ **No number, identifier, PMID, citation, hedge, null, UNKNOWN or limitation was altered anywhere.**
Every change is a punctuation split plus, at four sites, a supplied subject or a nominalisation turned
into a finite verb. Caution markers are **byte-identical, marker for marker**, in both files I edited.

⭐ **And all ten sentences I split were real prose, not instrument artefacts** — verified against both
of the extractor defects S22 reported, with the live linter untouched (§5A). **Nothing here was
reworded to satisfy a bug.**

---

## 1 · What I measured

### 1.1 · Refute-by-default: the defect, per paper, before any rewrite

```
$ python3 research/manuscripts/lint_readability.py --report <my four>
document                              sent  mean  p90  max  >60w  FKGL  caution/1kw
emc-treatment-roadmap.md               171  26.9   48  130     9  16.3         11.1
fusion-junction-neoantigen-paper.md    158  23.3   40   80     4  13.6         12.2
emc-surface-target-landscape.md        300  21.2   38   80     2  13.4          8.2
emc-atr-vulnerability-assessment.md    288  20.3   38   53     0  10.4         17.1
```

⭐ **`PUB-ATR` is clear and was clear before I arrived.** The prompt flagged it as "confirm before
working; it may already be clear" and the reading confirms it: **0 sentences over the ceiling,
longest 53 w.** The real clause agrees at HEAD (§1.2). **I did not edit that file at all**, and its
mtime is still `2026-08-28 21:58:03 UTC`.

`publish_bar.clause_7_readable_enough_to_review(pid, HEAD)`, the real call, at
`HEAD = b6397c5666efbf7d6755dfaedabc6a4bef24a8ee`:

### 1.2 · Clause 7 at HEAD

| endpoint | clause 7 at HEAD |
|---|---|
| PUB-EMC-PROGRAM | **FAIL** — 8 sentences over 60 w, longest 130 w at line 98 |
| PUB-NEOANTIGEN | **FAIL** — 4 over, longest 80 w at line 155 |
| PUB-SURFACE-TARGETS | **FAIL** — 2 over, longest 80 w at line 176 |
| PUB-ATR | **PASS** — longest 53 w, mean 20.3 w, FKGL 10.4, caution 17.1/1000 w, no baseline pinned |

⚠ **HEAD says 8 for the roadmap and the working tree said 9.** That is not a discrepancy in the
instrument — it is the finding in §1.3.

### 1.3 · ⭐ The trabectedin correction is itself a clause-7 blocker, and this is the seat's most
### actionable finding

The ninth roadmap flag exists **only in the working tree**, in the uncommitted trabectedin correction
another seat is making. Measured both sides:

```
at HEAD b6397c5, References paragraph, 32 w:
  "EMC-specific clinical signal: sunitinib response in EMC (PMC3534218); trabectedin +
   radiotherapy long-term response in metastatic EMC (case report — full bibliographic
   identifier (PMID/DOI) outstanding; OPEN reference item, must be completed before submission)."

in the working tree, same sentence, 72 w:
  "EMC-specific clinical signal: sunitinib response in EMC (PMC3534218); trabectedin in EMC —
   disease control, with no objective response located in an EMC patient: 0 of 2 in a randomised
   phase-2 sub-analysis with centrally reviewed imaging (PMID 27418251) and 0 of 3 in the Italian
   Sarcoma Group TrObs post-hoc (PMID 36568164), stated separately and not pooled ( , which also
   records the withdrawn ~12.5-month figure and the bounded PubMed search behind the negative)."
```

**32 w → 72 w.** The correction is right and the added denominators are exactly what the paper
needed; the side effect is that it is now the only thing keeping `PUB-EMC-PROGRAM` off clause 7.

⛔ **And no split outside the protected material clears it.** I measured the one boundary I could
legitimately cut at — the `;` between the sunitinib citation and the trabectedin material:

| candidate split | words |
|---|---:|
| `EMC-specific clinical signal: sunitinib response in EMC (PMC3534218).` | **8** |
| `Trabectedin in EMC — disease control, with no objective response located …` | **64** ⛔ still over |

Getting under 60 requires a split **inside** the trabectedin claim — between the negative
(*"no objective response located in an EMC patient"*) and its two denominators (0 of 2, PMID
27418251; 0 of 3, PMID 36568164). That is the claim, its hedge and its evidence, which my prompt
names as the one thing I may not touch. **So it is deferred, not skipped, and it needs the owning
seat to make one more split before `PUB-EMC-PROGRAM` can clear clause 7.**

### 1.4 · After

| document | words B | words A | >60w B | >60w A | longest B | longest A | mean B | mean A | FKGL B | A | caution/1kw B | A |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `emc-treatment-roadmap.md` | 6180 | **6193** | 9 | **1** ⚠ | 130 | 72 ⚠ | 26.9 | **23.9** | 16.3 | **15.1** | 11.1 | 11.1 |
| `emc-surface-target-landscape.md` | 10184 | **10184** | 2 | **0** | 80 | 59 | 21.2 | **20.9** | 13.4 | **13.3** | 8.2 | 8.2 |
| `fusion-junction-neoantigen-paper.md` ‡ | 4956 | 4957 | 4 | **0** | 80 | 54 | 23.3 | 22.7 | 13.6 | 13.4 | 12.2 | 12.2 |
| `emc-atr-vulnerability-assessment.md` † | 10490 | 10490 | 0 | 0 | 53 | 53 | 20.3 | 20.3 | 10.4 | 10.4 | 17.1 | 17.1 |

⚠ = the deferred trabectedin sentence (§1.3). ‡ = **not my edit** (§5). † = **untouched** (§1.1).
Word counts are `wc -w` on the raw markdown; "before" for the roadmap is the working tree as I
received it, which already carried the other seat's trabectedin edit, so the delta below is mine
alone.

⭐ **The roadmap grew by 13 words (+0.21 %) and here is exactly where they went**, S17's
justification and no other: splitting a semicolon- or colon-joined clause into a sentence needs the
subject and finite verb the clause was borrowing from its neighbour.

| site | words added | what was added |
|---|---:|---|
| §4.2 ASO evaluation arm | **+2** | `— four modules` in the lead-in, `cover` and `and` supplied to (iii), less `and`/`is scanned` recovered by (i) and (iv) |
| §4.2 first-pass result | **+3** | `four results` as the lead-in's object, replacing a bare `returns:` |
| §10 Conclusion | **+9** | `Its first arm is`, `Its second arm is`, and two supplied `is` for participles that had been sharing a verb |
| §4.1 WIP block | **+1** | `is` supplied twice, `to test`→`tests` recovered one |
| §7 Running bullet | **+1** | `is` supplied to (ii), `and` before (iii); `to test for`→`tests for` recovered one |
| Abstract | **−2** | `an analogy that`→`That analogy`; `and`→`.` at two joins |
| §9 broader indications | **0** | punctuation only |
| §1.3 deferred | 0 | not touched |

**No content word, number, identifier or citation was added or removed anywhere.**

### 1.5 · Gates run (scoped, per charter §6 — I did not run preflight)

```
python3 research/manuscripts/lint_claims.py <my 3 non-ATR files>   0 ERROR, 8 WARN
   ... same 3 files at HEAD (git show into scratch)                 0 ERROR, 8 WARN  ← identical
python3 research/manuscripts/lint_style.py  emc-surface-target-landscape.md
   working tree: clean, 0 ERROR        HEAD copy: clean, 0 ERROR    ← identical
pytest test_the_readability_splitter_breaks_where_a_sentence_does.py
       test_readability_screen_cannot_be_satisfied_by_saying_less.py   65 passed in 0.12s
python3 research/manuscripts/lint_readability.py --check <my four>  FAILS on 1 sentence: the
   deferred trabectedin sentence, line 487. Everything else is green.
```

⚠ **The 8 `lint_claims` WARNs are pre-existing and none is in text I touched** — established by
running the linter against `git show HEAD:` copies in a scratch directory and getting the same 8.
They are `R4-confirms` on `validate`/`confirmed`, `R4-proves` on `prove`, and `R1-nr4a3-selective`
on `NR4A3-selective`. ⛔ Only `emc-surface-target-landscape.md` is in `lint_style.TARGETS`; it is
clean before and after.

### 1.6 · ⭐ Clause 7 AFTER — the real call, on the commit that carries this work

⭐ **Not a replay.** The driver committed the wave as **`6f1be6d6df5b4957f3b3802cb44ae1a7d094447c`**
while this seat was finishing, so `publish_bar.clause_7_readable_enough_to_review(pid, sha)` could be
run for real against a sha that contains both my eight splits and S19-TRABECTEDIN's correction. All
five of my edit sites were verified present at that sha before the call.

| endpoint | clause 7 at `6f1be6d` — the real call |
|---|---|
| PUB-EMC-PROGRAM | **FAIL** — 1 sentence over 60 words, longest **72 w at line 485** (the deferred trabectedin sentence, and nothing else) |
| PUB-NEOANTIGEN | **PASS** — longest 54 w, mean 22.7 w, FKGL 13.4, caution 12.2/1000 w (no baseline pinned) |
| PUB-SURFACE-TARGETS | **PASS** — longest 59 w, mean 20.9 w, FKGL 13.3, caution 8.2/1000 w **against a 7.9 baseline** |
| PUB-ATR | **PASS** — longest 53 w, mean 20.3 w, FKGL 10.4, caution 17.1/1000 w (no baseline pinned) |

⭐ **Three of four PASS on the committed record. `PUB-EMC-PROGRAM` fails on exactly one sentence, and
it is the one I was told not to touch** — which is the prediction §5B made before the commit landed
(*"expect 8-over → 1-over, not green"*), now confirmed by the bar itself rather than by my replay.

⭐ **`PUB-SURFACE-TARGETS` is the one paper of the four that is pinned in
`readability-baseline.json`** (at 7.9), so its caution ratchet is live rather than inert. It measures
**8.2 before and 8.2 after**, above the pin in both readings, with an identical marker breakdown. **I
did not touch `readability-baseline.json`** — it is not an owned path and it needs no change, because
a splitting pass repartitions text without removing any.

---

## 2 · ⭐ The deliverable — every sentence changed, original beside replacement

Ten sentence sites. In every row the replacement carries the same claims, numbers, hedges and
citations as the original.

### PUB-EMC-PROGRAM · `program/emc-treatment-roadmap.md`

| # | § | original | replacement | what moved |
|---|---|---|---|---|
| 1 | Abstract | **(130 w)** New computed evidence reported here is honest about its weight: the degrader's make-or-break premise — that EMC is *addicted* to its fusion — is supported only at the level of a **class prior** (FET-fusion sarcomas are fusion-addicted; FLI1 in Ewing has gene effect −0.93 with 74% of lines dependent), an analogy that does **not** establish NR4A3-fusion-specific dependence (the partners differ) and that the dTAG experiment we hand to others would settle; the ASO's first transcriptome-wide screen returns a deliberately uncomfortable result (0 of 5 designed gapmers are transcriptome-clean), converting a "fusion-specific in principle" claim into a measured specificity bar; and DepMap surrogate mining (sarcoma lines stand in for the absent EMC line) nominates **B7-H3** and **PRAME** as the strongest surface/antigen targets while down-weighting NY-ESO-1/MAGE-A4 cell therapy and a fusion-junction vaccine. | **(10 + 37 + 22 + 30 + 33 w)** New computed evidence reported here is honest about its weight. The degrader's make-or-break premise — that EMC is *addicted* to its fusion — is supported only at the level of a **class prior** (FET-fusion sarcomas are fusion-addicted; FLI1 in Ewing has gene effect −0.93 with 74% of lines dependent). That analogy does **not** establish NR4A3-fusion-specific dependence (the partners differ), and the dTAG experiment we hand to others would settle it. The ASO's first transcriptome-wide screen returns a deliberately uncomfortable result (0 of 5 designed gapmers are transcriptome-clean), converting a "fusion-specific in principle" claim into a measured specificity bar. DepMap surrogate mining (sarcoma lines stand in for the absent EMC line) nominates **B7-H3** and **PRAME** as the strongest surface/antigen targets while down-weighting NY-ESO-1/MAGE-A4 cell therapy and a fusion-junction vaccine. | A colon and two semicolons become full stops; `an analogy that`→`That analogy` (−1); `and that the … would settle`→`and the … would settle **it**` (0); `bar; and DepMap`→`bar. DepMap` (−1). **Net −2 words.** ⛔ Every qualification is carried verbatim: `only at the level of a class prior`, `does **not** establish`, `(the partners differ)`, `would settle it`, `0 of 5`, `−0.93`, `74%`. The stress position of each new sentence is now the thing it is about (`class prior`, `settle it`, `specificity bar`). |
| 2 | Abstract | **(72 w)** (2) We make the first systematic computational case against the EWSR1::NR4A3 driver: AlphaFold2 + fpocket find the transactivation domain disordered and the best NR4A3 ligand-binding-domain cavity only borderline druggable (fpocket druggability 0.495, sub-threshold) — which is *why* we reframe the driver as a degradation/knockdown problem and define two driver-directed modalities: a **NR4A3 degrader** (…) and a uniquely tumour-specific **fusion-junction ASO/siRNA** (…). | **(33 + 42 w)** (2) We make the first systematic computational case against the EWSR1::NR4A3 driver: AlphaFold2 + fpocket find the transactivation domain disordered and the best NR4A3 ligand-binding-domain cavity only borderline druggable (fpocket druggability 0.495, sub-threshold). That is *why* we reframe the driver as a degradation/knockdown problem and define two driver-directed modalities: a **NR4A3 degrader** (…) and a uniquely tumour-specific **fusion-junction ASO/siRNA** (…). | Em dash → full stop; `which`→`That`. **Net 0 words.** `only borderline druggable` and the number `0.495, sub-threshold` are untouched, and the first sentence now ends on the sub-threshold reading rather than burying it mid-clause. |
| 3 | §4.1 | **(68 w)** *What we are running (WIP, pipelines built, results pending — not claimed here):* (i) molecular dynamics of the NR4A3 LBD to test whether a transient/cryptic druggable pocket opens that the static AlphaFold model misses — a positive result would directly challenge the "undruggable" prior of §1; (ii) de-novo selective-warhead/binder design scored against NR4A1/2; (iii) an AF3-class ternary-complex model of NR4A3–PROTAC–E3 geometry (re-primed now that open AF3-class tools shipped). | **(12 + 33 + 9 + 17 w)** *What we are running (WIP, pipelines built, results pending — not claimed here).* (i) Molecular dynamics of the NR4A3 LBD tests whether a transient/cryptic druggable pocket opens that the static AlphaFold model misses; a positive result would directly challenge the "undruggable" prior of §1. (ii) De-novo selective-warhead/binder design is scored against NR4A1/2. (iii) An AF3-class ternary-complex model of NR4A3–PROTAC–E3 geometry is re-primed now that open AF3-class tools shipped. | A three-item colon list becomes a status line plus three sentences; `to test whether`→`tests whether`; a parenthetical promoted to a main clause. **Net +1 word.** ⛔ `results pending — not claimed here` — the whole point of the block — is carried into the lead-in unaltered, and `would directly challenge` was **not** upgraded to `challenges`. |
| 4 | §4.2 | **(124 w)** **In-silico evaluation arm (…; `aso_insilico.py`):** (i) a **transcriptome-wide off-target screen** — every candidate's target window is scanned against the whole human RefSeq transcriptome (GRCh38) …; (ii) **target-site accessibility**, folding the fusion mRNA …; (iii) **sequence-liability filters** (CpG/TLR9 immunostimulation, G-quadruplex, homopolymer runs); and (iv) an **siRNA seed-region off-target** module, reporting each candidate's seed 7-mer, … | **(17 + 47 + 24 + 12 + 30 w)** **In-silico evaluation arm (…; `aso_insilico.py`) — four modules.** (i) A **transcriptome-wide off-target screen** scans every candidate's target window against the whole human RefSeq transcriptome (GRCh38) …. (ii) **Target-site accessibility** folds the fusion mRNA …. (iii) **Sequence-liability filters** cover CpG/TLR9 immunostimulation, G-quadruplex and homopolymer runs. (iv) An **siRNA seed-region off-target** module reports each candidate's seed 7-mer, … | The longest sentence in the paper after the abstract: a four-item colon list with the items joined by semicolons. Each module becomes its own sentence with **the module as its grammatical subject and its action as the verb** (`is scanned against`→`scans`, `folding`→`folds`, `reporting`→`reports`) — `scientific-writing` §1.2 and §1.3. **Net +2 words**, all function words plus the lead-in's `four modules`, which is a count of the (i)–(iv) already there. ⛔ The reason clause `because hybridization-dependent off-target RNase-H cleavage is the dominant gapmer-toxicity mode and "not a perfect complement of the two parents" is too weak a specificity bar` is carried whole — it is the justification for the strict bar and it is why the sentence was long. |
| 5 | §4.2 | **(63 w)** Screening the 5 fusion-specific gapmers against the full human RefSeq transcriptome (186,185 transcripts) returns: **none is transcriptome-clean** — every candidate has at least one near-complementary off-target at ≤1 mismatch (best candidate: 0 exact but 8 one-mismatch hits); the junction sites are **poorly accessible** (best ≈0.35 unpaired probability); they are **GC-rich (~75%)**; and only **2 of 5** place the RISC seed across the junction. | **(15 + 27 + 12 + 4 + 12 w)** Screening the 5 fusion-specific gapmers against the full human RefSeq transcriptome (186,185 transcripts) returns four results. **None is transcriptome-clean**: every candidate has at least one near-complementary off-target at ≤1 mismatch (best candidate: 0 exact but 8 one-mismatch hits). The junction sites are **poorly accessible** (best ≈0.35 unpaired probability). They are **GC-rich (~75%)**. And only **2 of 5** place the RISC seed across the junction. | Four semicolon-joined findings become four sentences, each ending on its own result. **Net +3 words** (`four results` as the lead-in's object, replacing a bare `returns:`). ⛔ Every figure survives exactly — `186,185`, `0 exact`, `8 one-mismatch`, `≈0.35`, `~75%`, `2 of 5` — and the negative `none is transcriptome-clean` is now the **first** thing after the lead-in rather than buried behind a colon. |
| 6 | §7 | **(61 w, one bullet)** - **Running (pipelines built; …):** (i) **molecular dynamics of the NR4A3 LBD** to test for a transient/cryptic druggable pocket the static model misses — a positive result would overturn the "undruggable" prior; (ii) **de-novo selective warhead/binder design** (…), scored for selectivity against NR4A1/NR4A2; (iii) the **AF3-class ternary-complex** model. | **(10 + 25 + 27 w)** - **Running (pipelines built; …).** (i) **Molecular dynamics of the NR4A3 LBD** tests for a transient/cryptic druggable pocket the static model misses; a positive result would overturn the "undruggable" prior. (ii) **De-novo selective warhead/binder design** (…) is scored for selectivity against NR4A1/NR4A2; and (iii) the **AF3-class ternary-complex** model. | `to test for`→`tests for`; `scored`→`is scored`; `and` supplied before (iii) so it does not become a verbless four-word fragment. **Net +1 word.** ⚠ (ii) and (iii) are deliberately left joined: splitting them would manufacture a stub sentence, which drags the mean down without helping a reader — `scientific-writing` §5, the metric is a screen. |
| 7 | §9 | **(76 w)** Second, **each lead here has a plausible path to common cancers** that should be assessed alongside the EMC case to widen the addressable population and the incentive to develop it — the NR4A receptor family (NR4A1/2/3) is implicated across leukaemia, melanoma, prostate, breast and colorectal cancer (and the "degrade an undruggable nuclear-receptor TF via its retained LBD" *platform* is itself transferable); B7-H3, PRAME and FAP are already pan-cancer targets; and the repurposed agents carry other-cancer evidence. | **(30 + 33 + 15 w)** Second, **each lead here has a plausible path to common cancers** that should be assessed alongside the EMC case to widen the addressable population and the incentive to develop it. The NR4A receptor family (NR4A1/2/3) is implicated across leukaemia, melanoma, prostate, breast and colorectal cancer, and the "degrade an undruggable nuclear-receptor TF via its retained LBD" *platform* is itself transferable. B7-H3, PRAME and FAP are already pan-cancer targets, and the repurposed agents carry other-cancer evidence. | Em dash → full stop, a parenthetical promoted to a coordinate clause, one semicolon → full stop. **Net 0 words.** ⛔ Guarded: the sentence that follows in the paper — *"**These broader-indication claims are stated as hypotheses to be substantiated …; they are not computed in this draft.**"* — is what stops a reader over-reading this passage, and it was **not touched, shortened or moved**. |
| 8 | §10 | **(84 w)** We give a reproducible framework whose central result is that no *ready* route attacks the EWSR1::NR4A3 driver, and we define the driver-directed program that aims to fill that gap — a NR4A3 degrader (rationalised by the very structural finding that rules out occupancy, its make-or-break fusion-addiction premise supported only as a class prior and explicitly gated on a dTAG test) and a uniquely tumour-specific fusion-junction ASO/siRNA (whose first transcriptome-wide screen sets a concrete specificity bar and whose delivery we propose but do not solve). | **(29 + 35 + 29 w)** We give a reproducible framework whose central result is that no *ready* route attacks the EWSR1::NR4A3 driver, and we define the driver-directed program that aims to fill that gap. Its first arm is a NR4A3 degrader, rationalised by the very structural finding that rules out occupancy; its make-or-break fusion-addiction premise is supported only as a class prior and is explicitly gated on a dTAG test. Its second arm is a uniquely tumour-specific fusion-junction ASO/siRNA, whose first transcriptome-wide screen sets a concrete specificity bar and whose delivery we propose but do not solve. | Two parenthesised arms become two sentences, each with the arm as its subject. **Net +9 words**, all of them `Its first/second arm is` plus two supplied `is` — the S17 case exactly. ⛔ **The three sentences that make this paragraph honest are carried verbatim**: `supported only as a class prior`, `explicitly gated on a dTAG test`, and `whose delivery we propose but **do not solve**` — the last of which is a caution marker (`do not`) and would have been the cheapest word to lose. |

### PUB-SURFACE-TARGETS · `surface-targets/emc-surface-target-landscape.md`

| # | § | original | replacement | what moved |
|---|---|---|---|---|
| 9 | prior-art screen | **(72 w)** A Europe PMC retrieval of 322 EMC-linked records, 238 of them with full text, was hand-screened for surfaceome, surface antigen, cell-surface protein, chimeric antigen receptor, radioligand, antibody-drug conjugate and immunotherapy terms, and returned three EMC-specific records, none of which is a systematic surface-antigen map: a radiotherapy case report [3], a single case describing an immunosuppressive tumour microenvironment in EMC with pleural metastases [4], and a multidisciplinary review of uncommon soft-tissue sarcomas [5]. | **(31 + 41 w)** A Europe PMC retrieval of 322 EMC-linked records, 238 of them with full text, was hand-screened for surfaceome, surface antigen, cell-surface protein, chimeric antigen receptor, radioligand, antibody-drug conjugate and immunotherapy terms. It returned three EMC-specific records, none of which is a systematic surface-antigen map: a radiotherapy case report [3], a single case describing an immunosuppressive tumour microenvironment in EMC with pleural metastases [4], and a multidisciplinary review of uncommon soft-tissue sarcomas [5]. | `terms, and returned`→`terms. It returned`. **Net 0 words.** Method and result now sit in separate sentences, which is the shape a reader can check. ⛔ `322`, `238`, `three`, and all three reference markers `[3] [4] [5]` are untouched; so is the next sentence's limitation — *"That screen matched titles and abstracts, not full text, so it establishes that nothing is indexed on those pairings rather than that no such work exists"* — which was left exactly as it stands. |
| 10 | instrument limits | **(80 w)** The scanned population is tumour-cell monoculture, so it contains no stromal or fibroblast compartment; an antigen carried only by stroma reads at the floor, demonstrated by LRRC15, an established sarcoma cancer-associated-fibroblast antigen with a clinical antibody-drug conjugate programme behind it, at `frac_expressed` 0.0; a glycan such as oncofetal chondroitin sulfate is the product of a biosynthetic pathway rather than of one gene [14] and so cannot be ranked; and CSPG4 has no per-gene row in any committed artifact of this instrument. | **(15 + 32 + 25 + 15 w)** The scanned population is tumour-cell monoculture, so it contains no stromal or fibroblast compartment. An antigen carried only by stroma reads at the floor, demonstrated by LRRC15, an established sarcoma cancer-associated-fibroblast antigen with a clinical antibody-drug conjugate programme behind it, at `frac_expressed` 0.0. A glycan such as oncofetal chondroitin sulfate is the product of a biosynthetic pathway rather than of one gene [14], and so cannot be ranked. And CSPG4 has no per-gene row in any committed artifact of this instrument. | The paper's longest sentence, and it is **four limitations of the instrument** joined by semicolons — the preceding sentence already says *"Four limits of this instrument were computed"*, so one limit per sentence is the paper's own structure. Three semicolons → full stops. **Net 0 words.** ⛔⛔ **This is the sentence I guarded hardest.** It is a pure limitations sentence and `scientific-writing` §4 says such sentences are allowed to be the longest in the paper; it was split only because it is four ideas, never to shorten it. `cannot be ranked` (a caution marker), `0.0`, `[14]`, `no per-gene row in any committed artifact` and the LRRC15 demonstration all survive in the same grammatical strength. |

**Three cosmetic re-wraps** accompany rows 4, 3 and 8 — the hard wrap left a ragged short line after
each split. No words changed; verified by the identical `wc -w` on the surface-target file and by the
byte-identical caution census on both.

---

## 3 · ⛔ Sentences I did NOT change, and why

Named rather than quietly left, because the instruction was not to chase the count.

- **`emc-treatment-roadmap.md`:487, 72 w — the trabectedin reference sentence.** DEFERRED under my
  prompt's explicit hazard, with the measurement in §1.3 showing why no split I am allowed to make
  clears it.
- **`emc-treatment-roadmap.md`:410 (58 w)** — *"Because we attack the actual driver only
  computationally, we define a runnable program and state its status honestly (done / running /
  planned), so the contribution is the program plus the completed pieces, not unfinished results"*.
  One idea, and that idea is the paper's honesty framing. Under the ceiling. Left.
- **`emc-treatment-roadmap.md`:430 (53 w)** — the fusion-addiction limitation
  (*"a class-level analogy (FLI1/Ewing), **not EMC data**, and an imperfect one"*). One
  qualification, under the ceiling, `scientific-writing` §4. Left.
- **`emc-treatment-roadmap.md`:203 (53 w), :187 (51 w), :175 (49 w), :252 (49 w).** Each is one idea
  under the ceiling. Left.
- **`emc-surface-target-landscape.md`:375 (59 w)** — *"Two candidate explanations are live and
  **neither is settled here**…"*. The strongest live-uncertainty sentence in the paper and one word
  under the ceiling. ⛔ **Deliberately not touched**: it is exactly the sentence §4 says to guard, and
  its two caution markers (`neither`, `is not`) are worth more than three words of length.
- **`emc-surface-target-landscape.md`:500 (58 w), :491 (57 w).** The open-questions list and the
  concordance negative. Under the ceiling, one idea each. Left.
- **`emc-atr-vulnerability-assessment.md` — the whole file.** 0 over ceiling; clause 7 already PASS.
  **Editing prose that the screen does not flag, in a paper that already passes, would be a rewrite
  with no falsifiable reason** — and it would put a second seat's hand into a file another cycle may
  be reading. Untouched.

### Constructions I refused, by name

1. **`would settle it` → `settles it`** (row 1). The dTAG experiment has not been run; the
   conditional *is* the claim.
2. **`would directly challenge` → `challenges`** and **`would overturn` → `overturns`** (rows 3, 6).
   Both describe a result that does not exist yet. Compressing the modal would convert a planned test
   into a reported finding.
3. **`do not solve` → dropping the clause** (row 8). It is the delivery gate — the single sentence
   that stops a reader taking the ASO arm as deliverable — and it is a caution marker. Kept verbatim.
4. **`cannot be ranked` → `is not ranked`** (row 10). `cannot` states an instrument limit;
   `is not` would read as a choice.
5. **`none of which is a systematic surface-antigen map` → `no systematic map exists`** (row 9). The
   screen searched titles and abstracts; the paper's next sentence says so. Weakening the scoping to
   a claim about the world is precisely the §4 failure.

---

## 4 · ⛔⛔ The caution audit — did readability cost honesty?

`--caution` was run on the pre-edit file and on the post-edit file for both papers I changed, and
the **full marker breakdown was diffed**, not just the total.

| document | markers B → A | per 1000 w B → A | marker-by-marker diff |
|---|---|---|---|
| `emc-treatment-roadmap.md` | 51 → 51 | 11.1 → 11.1 | **byte-identical** (`diff` returns empty) |
| `emc-surface-target-landscape.md` | 52 → 52 | 8.2 → 8.2 | **byte-identical** (`diff` returns empty) |
| `fusion-junction-neoantigen-paper.md` ‡ | 45 → 45 | 12.2 → 12.2 | **byte-identical** — not my edit, checked anyway (§5) |
| `emc-atr-vulnerability-assessment.md` | 100 → 100 | 17.1 → 17.1 | file untouched |

⛔ **Zero deltas anywhere. Nothing to name, because nothing left.** Every marker class is unmoved:
roadmap `is not` ×8, `untested` ×8, `does not` ×6, `are not` ×5 and the rest; surface-target
`is not` ×25, `does not` ×12, `cannot` ×11, `neither` ×7 and the rest.

Second, independent check, because a marker count is a pattern and not a reader: **each of the ten
rows in §2 was re-read against its original**, and the "what moved" column is the record of that
read. The five constructions above are the ones the rewrite was tempted by and refused.

⛔ **`readability-baseline.json` was not touched**, and it needs no change: the one pinned file among
my four measures 8.2 against its 7.9 pin, before and after.

---

## 5 · ⚠ A seat-ownership collision — measured before the driver named it, and now reconciled

`research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md` was assigned to this seat as
**exclusive**. It was edited by **S22-PROSE-A** while I held it. The driver has since confirmed the
cause: S22 was given "the vaccine-path document" in the same directory and read that as covering this
file too. **The error is the driver's and the outcome is clean** — but I found it by `stat` before
being told, which is the part worth keeping.

```
19:41Z  my first --report:   4 sentences over ceiling, longest 80w at line 155
19:48:23Z  file mtime changes; I made no edit to this path at any point
19:49Z  my re-read:          0 sentences over ceiling, longest 54w
        git diff:            58 insertions, 49 deletions — a full re-wrap plus 4 splits
```

The other seat's pass is a **good** one and I am recording it rather than repeating it: caution
markers byte-identical against HEAD (45 → 45, 12.2 → 12.2), `wc -w` 4956 → 4957, and the four splits
are the same four sentences I had queued (abstract §3-item list, the §1 fusion-exclusive layer, the
"why this is not already a therapy" list, and the `junctions_graded` refusals sentence).

⛔ **I did not revert, re-touch or duplicate any of it**, and I did not run a competing edit into that
file — a second writer in a file another seat is mid-pass on is the 2026-08-27 incident from the
other end.

★ **The finding for the driver is not about this file, it is about the wave**: two seats were pointed
at the same manuscript in one tree, and the only reason nothing was lost is that neither ran a git
write and I re-measured before editing. **The collision was invisible until a `stat` was run.** The
charter's rule 2 was followed by both of us and still collided, because the collision is in the
*prompts*, not in the seats' behaviour.

### 5.1 · ⛔ I never wrote this file, and here is the evidence rather than the assurance

The driver's message asks which of three cases applies. **Case 1: I never started it.** Falsifiable
record, not memory:

- The file's mtime is **`2026-09-01 19:48:23.996 UTC`** and has not moved since — it is S22's write.
  Every file this seat wrote has a later mtime (`emc-treatment-roadmap.md` at 19:53:58,
  `emc-surface-target-landscape.md` after it).
- ⛔ **No pre-S22 buffer of this file was ever taken.** My only snapshot of it is
  `git show HEAD:` output in scratch, taken for the caution census and never written back. There is
  no copy anywhere in this seat's working set that could revert S22's pass.
- I re-read the file from disk after the collision and again after the driver's message. Both reads
  agree: **0 over ceiling, longest 54 w.**

### 5.2 · ⚠ The driver's word figures for S22's pass match nothing on disk — an honest UNKNOWN

The message reports S22 taking this file **5,068 → 5,067** words. I cannot reproduce either number by
any method, at any commit:

| metric | HEAD `b6397c5` | working tree | delta |
|---|---:|---:|---:|
| `wc -w` on the raw markdown | **4,956** | **4,957** | +1 |
| `LR.measure()["words"]` (extracted prose) | **3,677** | **3,676** | **−1** |
| the file at its previous two commits (`a4fcdca9a`, `0dce79be0`) | 4,785 / 4,672 | — | — |
| every other `.md` in `research/manuscripts/neoantigen/` | none is 5,067 or 5,068 | — | — |

⭐ **The magnitude and direction of S22's reported change reproduce exactly on one of these** — the
extracted-prose count falls by 1 — so the *claim* ("essentially no length change") is sound and I
have no reason to doubt S22's pass. **The absolute figures are what I cannot place**, and I am
recording that rather than adopting a number I could not measure (CLAUDE.md §4: never write a figure
from a report when a $0 reading is available). Most likely a different baseline or a different
counter; **UNKNOWN which**, and it costs nothing to say so.

⛔ **The substantive claim is confirmed independently and does hold:** 4 over-ceiling → **0**, caution
markers **45 → 45 byte-identical**, `max_len` 80 → 54, FKGL 13.6 → 13.4. Clause 7 for `PUB-NEOANTIGEN`
is **PASS** on the working tree. Nothing about my report changes.

---

## 5A · ⭐ The artefact probe — none of my ten flags was an instrument defect

The driver relayed two further extractor defects found by S22 that **inflate** counts, with the
correct instruction attached: *where the prose is right and the instrument is wrong, say so and leave
it.* So before letting my ten rewrites stand, I tested whether any of them was a rewrite of prose that
never needed one.

**Method.** `lint_readability.py` is not an owned path and I did not touch it — `git status` on it is
empty. I copied it to scratch and patched **both** defects out of the copy:

1. **the numbered-item strip** (`re.sub(r"^\s*\d+\.\s+", "", t)`, `body()` line 135) disabled, so a
   sentence-terminating numeral a hard wrap put at column 0 is no longer deleted;
2. **the opener class widened** from `[A-Z(“"§ + callouts]` to `[A-Za-z0-9(“"§ + callouts]`, so a
   sentence opening with a digit or a lowercase word splits.

Then I re-measured the **pre-edit (HEAD) text** of both files I changed under the strict and the
patched splitters and compared, sentence by sentence.

| flag (at HEAD) | strict | both defects patched | verdict |
|---|---:|---:|---|
| roadmap:98 | 130 w | **130 w** | REAL |
| roadmap:98 | 72 w | **72 w** | REAL |
| roadmap:286 | 68 w | **68 w** | REAL |
| roadmap:305 | 124 w | **124 w** | REAL |
| roadmap:318 | 63 w | **63 w** | REAL |
| roadmap:409 | 61 w | **61 w** | REAL |
| roadmap:451 | 76 w | **76 w** | REAL |
| roadmap:469 | 84 w | **84 w** | REAL |
| surface-targets:124 | 72 w | **72 w** | REAL |
| surface-targets:176 | 80 w | **80 w** | REAL |

⭐ **Ten for ten, unchanged to the word.** Every sentence I split was genuinely that long: each is a
colon-or-semicolon list of three to five ideas, which is `scientific-writing` §1.4 and not an
extraction artefact. **No edit in §2 was made to satisfy a bug**, and none needs reverting if the
instrument is fixed.

⛔ **And the deferred sentence is real too**, which matters because it is the only thing still holding
`PUB-EMC-PROGRAM` off clause 7:

```
strict splitter          : line 485/487, 72 w
both defects patched out : line 485,     72 w   ← unchanged
```

So it cannot be dismissed as a measurement error, and the split named in §1.3 and ledger row 1 is
genuinely required.

⚠ For completeness, the patched splitter changes **nothing** across all four of my papers in their
current state: roadmap 1 → 1, neoantigen 0 → 0, surface-targets 0 → 0, ATR 0 → 0. **S22's two defects
are real and worth fixing, and neither of them touched this seat's worklist.**

---

## 5B · ⭐ S19-TRABECTEDIN's correction has now COMMITTED, and the prediction it drove was right

When the driver's message arrived, the trabectedin correction had landed **in the working tree only**
— `git show b6397c5:… | grep -c 'no objective response located'` returned **0**, against **1** on the
tree. That mattered rather than being a quibble, because **clause 7 reads a committed sha**: at
`b6397c5` the bar still measured the 32-word pre-correction sentence and reported
`PUB-EMC-PROGRAM` failing on the **eight sentences I had already fixed**. So this section predicted:

> *"Expect clause 7 to go 8-over → 1-over on the merge commit, not to go green."*

**It committed as `6f1be6d` and it did exactly that** (§1.6): `PUB-EMC-PROGRAM` now fails on **one**
sentence, 72 w at line 485, which is the corrected trabectedin material and nothing else.

⛔ **I did not restore, re-hedge or reword any of that material**, and §3 lists it as deferred. The
single edit that clears the endpoint is named in §1.3 and ledger row 1, and it belongs to the seat
that owns the claim.

---

## 6 · What I could not do, and what it is actually waiting on

- **`PUB-EMC-PROGRAM` clause 7 stays FAIL at `6f1be6d`, and it is waiting on ONE more split inside
  the trabectedin material** — not on me, not on the linter, and not on any fetch. §1.3 has the exact sentence, the
  measurement showing that a split at the sunitinib boundary leaves 64 w, and the boundary that would
  work (between the negative and its two denominators). **The seat that owns that claim can clear it
  in one edit.**
- **Nothing else is blocked.** Every other flagged sentence in every file I own is fixed or is
  another seat's already-landed work.
- ✅ **The clause-7 "after" readings are no longer a replay — RESOLVED.** The driver committed the
  wave as `6f1be6d` while I was finishing, so the real call was made against a sha carrying this
  work: **PUB-NEOANTIGEN, PUB-SURFACE-TARGETS and PUB-ATR all PASS; PUB-EMC-PROGRAM FAILs on the one
  deferred sentence** (§1.6). Nothing here is waiting on a re-run.
- **`./scripts/preflight.sh` was not run** — charter §6, it is the driver's job on a settled tree, and
  eleven other seats were mutating this one while I worked.
- **I ran no git write command of any kind.**

---

## 7 · Ledger rows the driver should write

1. **`what`:** ⛔ THE TRABECTEDIN DENOMINATOR CORRECTION TURNED `emc-treatment-roadmap.md`'s
   REFERENCES SENTENCE INTO A `publish_bar` CLAUSE-7 BLOCKER FOR `PUB-EMC-PROGRAM`. Measured
   2026-09-01T19:52Z against `HEAD b6397c5666efbf7d6755dfaedabc6a4bef24a8ee`: the sentence is
   **32 w committed and 72 w in the working tree** — the correction added 40 words (the two
   denominators, 0 of 2 / PMID 27418251 and 0 of 3 / PMID 36568164, plus the artifact pointer). It is
   now the **only** over-ceiling sentence in the paper; S28-PROSE-C split the other eight. ⛔ A split
   at the `;` between the sunitinib citation and the trabectedin material leaves **64 w** — still
   over — so clearing it requires a split **inside** the corrected claim, between the negative
   (*"no objective response located in an EMC patient"*) and its denominators. That is the claim
   itself, which S28-PROSE-C was instructed not to touch. ⭐ **The correction is right; only its
   sentence length is the problem, and nothing about the claim, its hedges or its PMIDs needs to
   change to fix it.**
   ⚠ **AND IT IS NOT YET VISIBLE TO THE BAR.** At `HEAD b6397c5` the correction is uncommitted
   (`git show HEAD:… | grep -c 'no objective response located'` → **0**; the same grep on the working
   tree → **1**), and clause 7 reads a committed sha. So the bar currently reports
   `PUB-EMC-PROGRAM` failing on the **8 sentences S28 already fixed**, and will switch to failing on
   **this one** at the merge commit. **Expect 8-over → 1-over, not green.**
   ⭐ Verified real, not an instrument artefact: the sentence measures **72 w** under the strict
   splitter and **72 w** with both of S22's reported extractor defects patched out (§5A).
   **`kind`:** `manuscript` · **`state`:** `queued` · `cost_class`: free.

2. **`what`:** ⚠ TWO SEATS OF THE 2026-09-01 WAVE WERE POINTED AT
   `research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md` AS AN EXCLUSIVE OWNED PATH —
   **S22-PROSE-A BY A DIRECTORY-SHAPED PROMPT ("the vaccine-path document"), S28-PROSE-C BY AN
   EXPLICIT FILE PATH.** Measured: S28 read 4 over-ceiling sentences at 19:41Z; the file's mtime
   moved to 19:48:23Z with 58 insertions / 49 deletions S28 did not make; at 19:49Z it read 0.
   **Nothing was lost** — S22's pass is sound (caution 45 → 45 byte-identical, ±1 word, the same four
   splits S28 had queued) and S28 stood down rather than writing over it. ⛔ **But the safety came
   from a `stat` nobody required.** The charter's rule 2 was obeyed by both seats, so **the collision
   is in the seat PROMPTS, not the seats' behaviour** — and a prompt that names a path by description
   ("the vaccine-path document") cannot be checked against one that names a path literally.
   ★ Candidate fix, and it is the cheap half: the wave file carries the owned-path map as **one table
   of literal paths the driver derives**, and every seat prompt quotes its row from that table, so an
   overlap is a build error rather than something a seat notices by accident. ⚠ A second, smaller
   defect rides along: the driver's hand-off reported S22's word counts as **5,068 → 5,067**, which
   reproduces no measurement of that file by `wc -w` (4,956 → 4,957) or by extracted prose
   (3,677 → 3,676) at HEAD or in the tree — the −1 direction matches the extracted-prose count
   exactly, the absolute figures match nothing. **A hand-off that carries a number a receiving seat
   cannot reproduce is a number that will be copied forward.**
   **`kind`:** `process_defect` · **`state`:** `queued` · `cost_class`: free.

3. **`what`:** ✅ REFUTED — `PUB-ATR` (`dependency/emc-atr-vulnerability-assessment.md`) NEEDED NO
   READABILITY WORK. `publish_bar.clause_7_readable_enough_to_review("PUB-ATR", HEAD)` returns
   **PASS** at `b6397c5` (longest 53 w, mean 20.3 w, FKGL 10.4, caution 17.1/1000 w, no baseline
   pinned), confirming S5-READABILITY's post-splitter-fix measurement of 7 → 0. **The file was not
   edited**; its mtime is still 2026-08-28. Any remaining row asserting an ATR readability defect
   describes a state that no longer holds.
   **`kind`:** `verification` · **`state`:** `done` · `cost_class`: free.

4. **`what`:** ⚠ THREE OF THE FOUR PAPERS IN THIS SEAT'S SCOPE ARE ABSENT FROM
   `research/manuscripts/readability-baseline.json` WHILE CARRYING PUBLICATION ENDPOINTS —
   `program/emc-treatment-roadmap.md` (PUB-EMC-PROGRAM),
   `neoantigen/fusion-junction-neoantigen-paper.md` (PUB-NEOANTIGEN) and
   `dependency/emc-atr-vulnerability-assessment.md` (PUB-ATR). Only
   `surface-targets/emc-surface-target-landscape.md` is pinned (7.9). ⛔ **Consequence, stated
   plainly:** clause 7's caution-ratchet branch is **inert** for those three (`was is None`), so the
   only half of the clause that binds them is the sentence ceiling — the half that *cannot* catch a
   dropped hedge. Measured values available to pin today: roadmap **11.1**, neoantigen **12.2**, ATR
   **17.1**. ⚠ This is a decision, not a finding: pinning a baseline mid-sprint pins whatever the
   tree happens to hold, so it belongs to a settled tree and to the driver, not to a seat.
   **`kind`:** `decision` · **`state`:** `queued` · `cost_class`: free.

5. **`what`:** ⭐ THE TWO EXTRACTOR DEFECTS REPORTED BY S22-PROSE-A ACCOUNT FOR **NONE** OF
   S28-PROSE-C's TEN REWRITES — probed rather than assumed. Method, 2026-09-01: `lint_readability.py`
   copied to scratch (**the live module untouched**, `git status` on it empty) with (a) the
   numbered-item strip `re.sub(r"^\s*\d+\.\s+", "", t)` at `body()` line 135 disabled and (b) the
   opener class widened from `[A-Z(“"§ + callouts]` to `[A-Za-z0-9(“"§ + callouts]`; both edited
   files then re-measured at `HEAD b6397c5` under the strict and the patched splitters. **All ten
   flags are identical to the word** (130, 124, 84, 76, 72, 72, 68, 63, 61 and 80 w), and the
   deferred trabectedin sentence measures **72 w under both**. Across all four papers in their
   current state the patched splitter changes nothing (1 / 0 / 0 / 0 either way). ⛔ **This confirms
   S28 reworded no prose to satisfy a bug, and it is NOT evidence against S22's defects** — both are
   real and worth fixing; they simply did not intersect this seat's worklist.
   **`kind`:** `verification` · **`state`:** `done` · `cost_class`: free.
