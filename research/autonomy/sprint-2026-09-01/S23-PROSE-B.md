---
id: DOC-SPRINT-S23-PROSE-B
title: "S23-PROSE-B — the four short-tail readability papers, split to zero"
level: L3
kind: process
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
---

# S23-PROSE-B — nine over-ceiling sentences in four papers, split

**Item(s):** S5-READABILITY follow-through (AUT-PD-142's blast radius)
**Owned paths:** `research/manuscripts/methods-record/degrader-methods-failure-record.md`,
`research/manuscripts/methods-record/closed-routes-negative-record.md`,
`research/manuscripts/modality-census/cancer-modality-census.md`,
`research/manuscripts/neoantigen/hla-coverage-emc.md`, this file
**Started/Finished (UTC):** 2026-09-01T19:25Z — 2026-09-01T19:40Z

## Verdict

**FIXED.** All four papers were confirmed still failing on the fixed linter (9 real flags, matching
S5 exactly — **nothing was already clear**), all nine sentences were split, and all four now measure
**0 over-ceiling**. `publish_bar.clause_7_readable_enough_to_review` moves **FAIL → PASS** for
**PUB-METHODS, PUB-CLOSED-ROUTES, PUB-MODALITY-CENSUS and PUB-HLA-COVERAGE**. No paper got longer.
Caution markers are **byte-identical** in three of the four; the one delta in the fourth is a
false-positive `CI` token removed with a duplicated sentence, itemised in §4 below.

⛔ **No number, identifier, citation, hedge, null or limitation was altered.** Every change is a
punctuation split plus, in four places, a one- or two-word subject supplied for the new sentence.

---

## 1 · What I measured — refute-by-default first

S5's table is an hour old and three of my four were in single digits, so the first job was to check
the defect still exists. It does, on every one of the four, and at exactly the counts S5 recorded.

```
$ python3 research/manuscripts/lint_readability.py --report <each file>
document                              sent  mean  p90  max  >60w  FKGL  caution/1kw
degrader-methods-failure-record.md     216  20.2   38   61     1  11.8         13.0
closed-routes-negative-record.md       192  23.0   44   79     3  12.2         17.0
cancer-modality-census.md              151  21.4   37   64     1  11.9         13.6
hla-coverage-emc.md                    110  23.4   44   80     4  14.0         11.7
```

`publish_bar.clause_7_readable_enough_to_review(pid, HEAD)`, run directly at
`HEAD = c9583ea41b33f85dd14541216acad55476a64d44`:

| endpoint | clause 7 at HEAD |
|---|---|
| PUB-METHODS | **FAIL** — 1 sentence over 60w, longest 61w at line 53 |
| PUB-CLOSED-ROUTES | **FAIL** — 3 over, longest 79w at line 268 |
| PUB-MODALITY-CENSUS | **FAIL** — 1 over, longest 64w at line 39 |
| PUB-HLA-COVERAGE | **FAIL** — 4 over, longest 80w at line 138 |

⭐ **Two of the four PUB-HLA-COVERAGE flags were not real prose**, which S5's classification does
not cover — see §5. I split their real constituent sentences anyway, on their own merits, and say
why there rather than claiming a rewrite the count did not need.

### After

| document | words B | words A | >60w B | >60w A | longest B | longest A | mean B | mean A | caution/1kw B | A |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `degrader-methods-failure-record.md` | 6256 | **6253** | 1 | **0** | 61 | 56 | 20.2 | 20.0 | 13.0 | 13.0 |
| `closed-routes-negative-record.md` | 5895 | **5895** | 3 | **0** | 79 | 55 | 23.0 | 22.5 | 17.0 | 17.0 |
| `cancer-modality-census.md` | 4033 | **4033** | 1 | **0** | 64 | 58 | 21.4 | 21.2 | 13.6 | 13.6 |
| `hla-coverage-emc.md` | 3594 | **3590** | 4 | **0** | 80 | 59 | 23.4 | 22.1 | 11.7 | 11.3 |

**No paper is longer.** Word counts are `wc -w` on the raw markdown, before = `git show HEAD:<path>`.

`clause_7` after, computed by replaying the clause's own logic (`LR.measure` + the baseline lookup)
against the working tree, because the real clause reads a committed sha and this seat may not commit:

| endpoint | clause 7 on the working tree |
|---|---|
| PUB-METHODS | **PASS** — longest 56w, mean 20.0, FKGL 11.7, caution 13.0/1000w, no baseline pinned |
| PUB-CLOSED-ROUTES | **PASS** — longest 55w, mean 22.5, FKGL 12.0, caution 17.0/1000w, no baseline pinned |
| PUB-MODALITY-CENSUS | **PASS** — longest 58w, mean 21.2, FKGL 11.9, caution 13.6/1000w, no baseline pinned |
| PUB-HLA-COVERAGE | **PASS** — longest 59w, mean 22.1, FKGL 13.6, caution 11.3/1000w, no baseline pinned |

⚠ **None of the four is in `readability-baseline.json`**, so clause 7's caution-ratchet branch is
inert for all of them (`was is None`). That is a fact about the baseline, not a licence: the caution
audit in §4 was done anyway, marker by marker.

### Gates run (scoped, per charter §6)

```
pytest research/manuscripts/tests/test_the_readability_splitter_breaks_where_a_sentence_does.py   53 passed
pytest research/manuscripts/tests/test_readability_screen_cannot_be_satisfied_by_saying_less.py   12 passed
python3 research/manuscripts/lint_claims.py <my four files>          lint_claims: OK - 4 file(s) clean
python3 research/manuscripts/lint_style.py  <my four, before/after>  414 ERROR before, 414 ERROR after — unchanged
```

⚠ `lint_style` reports 414 on these files **before my change and after it, identically**. None of the
four is in `lint_style.TARGETS`, so the gate is out of its own scope here and the number is noise;
the load-bearing reading is that **my edits moved it by zero**.

---

## 2 · ⭐ The deliverable — every sentence changed, original beside replacement

Read this column-by-column. **Nine splits, one deletion.** In every row the replacement contains the
same claims, the same numbers, the same hedges and the same citations as the original.

### PUB-METHODS · `methods-record/degrader-methods-failure-record.md`

| # | line | original (61w) | replacement (19 + 20 + 22w) | what moved |
|---|---|---|---|---|
| 1 | 53 | This paper reports one that did not, in the form the field is short of: an **instrument-by-instrument audit** in which every method used to support a paralogue-selectivity statement was first put to a test whose answer was already known, and the results — including the failures, the non-resolutions and the tests that were never run — are enumerated rather than discarded. | This paper reports one that did not, in the form the field is short of: an **instrument-by-instrument audit**. Every method used to support a paralogue-selectivity statement was first put to a test whose answer was already known. The results — including the failures, the non-resolutions and the tests that were never run — are enumerated rather than discarded. | Colon → full stop; `in which` deleted (2 words) so the audit's definition becomes its own sentence; `and the results` → `The results`. **Net −3 words.** The three-part enumeration `the failures, the non-resolutions and the tests that were never run` is carried verbatim — that clause is the paper's whole point and was not touched. |

### PUB-CLOSED-ROUTES · `methods-record/closed-routes-negative-record.md`

| # | line | original | replacement | what moved |
|---|---|---|---|---|
| 2 | 88 | The reason it is an enumerated field rather than prose is recorded there and is worth quoting, because it is the whole design brief: *"AI methods are advancing fast, …"* (65w) | The reason it is an enumerated field rather than prose is recorded there. It is worth quoting, because it is the whole design brief: *"AI methods are advancing fast, …"* (13 + 53w) | `and` → `. It`. **Net 0 words.** ⛔ The block quotation is untouched, character for character — it is the source's words and the whole reason the sentence was long. |
| 3 | 268 | A synthetic promoter driven by the fusion, wired to a suicide gene, is the most elegant idea in the search, and it has been built in the sibling disease: in Ewing sarcoma, EWSR1::FLI1 has **neomorphic** DNA binding — it activates GGAA microsatellites that wild-type FLI1 does not — so a GGAA-based cassette is active only where the fusion is, and both an enhancer-based expression cassette and a GGAA-driven HSV-TK/ganciclovir construct have been reported (route 14 holds both citations). (79w) | A synthetic promoter driven by the fusion, wired to a suicide gene, is the most elegant idea in the search, and it has been built in the sibling disease. In Ewing sarcoma, EWSR1::FLI1 has **neomorphic** DNA binding — it activates GGAA microsatellites that wild-type FLI1 does not — so a GGAA-based cassette is active only where the fusion is. Both an enhancer-based expression cassette and a GGAA-driven HSV-TK/ganciclovir construct have been reported (route 14 holds both citations). (29 + 33 + 20w) | Colon → full stop; `, and both` → `. Both` (−1 word). **Net −1 word.** ⚠ Guarded deliberately: the negative `that wild-type FLI1 does not` is intact, and `have been reported` was **not** upgraded to *are established* or *work* — this is a claim about the Ewing literature, not about EMC. |
| 4 | 340 | 6-mercaptopurine is the one **approved** drug reported to activate NR4A3, acting through the N-terminal AF-1 rather than the ligand-binding domain — *"the N-terminal AF-1 domain delimited to between amino acids 1 and 112 …"* (Wansa et al. …). (66w) | 6-mercaptopurine is the one **approved** drug reported to activate NR4A3, acting through the N-terminal AF-1 rather than the ligand-binding domain. Verbatim: *"the N-terminal AF-1 domain delimited to between amino acids 1 and 112 …"* (Wansa et al. …). (22 + 45w) | Em dash → full stop + the one-word lead-in `Verbatim:`. **Net 0 words** (one token out, one in). ⛔ The Wansa quotation, the PMID, the DOI-bearing link and the `EV-WANSA-2003` evidence id are all untouched and stay on the same lines. `reported to activate` was **not** shortened to `activates`. |

### PUB-MODALITY-CENSUS · `modality-census/cancer-modality-census.md`

| # | line | original (64w) | replacement (20 + 44w) | what moved |
|---|---|---|---|---|
| 5 | 39 | Four whole categories had been invisible to every previous search, and its diagnosis was not oversight but **instrument shape**: the portfolio's searches had all been molecular-modality-centric, so physical and locoregional treatment, … and treatment strategy as distinct from new agents were each outside the shape of every query anyone had written. | Four whole categories had been invisible to every previous search, and its diagnosis was not oversight but **instrument shape**. The portfolio's searches had all been molecular-modality-centric, so physical and locoregional treatment, … and treatment strategy as distinct from new agents were each outside the shape of every query anyone had written. | Colon → full stop; `the portfolio's` → `The portfolio's`. **Net 0 words.** The diagnosis sentence now ends on `instrument shape`, which is the term the rest of the section uses (stress position, `scientific-writing` §1.1). The four-item list is carried whole. |

### PUB-HLA-COVERAGE · `neoantigen/hla-coverage-emc.md`

| # | line | original | replacement | what moved |
|---|---|---|---|---|
| 6 | 101 (Conclusions) | A public, off-the-shelf fusion-neoantigen approach to EMC is **partial by construction** and **inequitable if framed by a single global number**: the most "public" junction misses ~70% of patients overall and ~90% of Sub-Saharan African and Latin American patients, and demanding both CD8 *and* CD4 coverage from public epitopes drops the addressable fraction to ~16% — with the CD8-best and CD4-best populations barely overlapping. (64w) | A public, off-the-shelf fusion-neoantigen approach to EMC is **partial by construction** and **inequitable if framed by a single global number**. The most "public" junction misses ~70% of patients overall and ~90% of Sub-Saharan African and Latin American patients. Demanding both CD8 *and* CD4 coverage from public epitopes drops the addressable fraction to ~16%, with the CD8-best and CD4-best populations barely overlapping. (23 + 23 + 25w) | Colon → full stop; `and demanding` → `Demanding` (−1); em dash → comma (−1). **Net −2 words.** ⛔ All four figures — `~70%`, `~90%`, `~16%`, and the naming of Sub-Saharan Africa and Latin America — are carried exactly. The `barely overlapping` caveat stays attached to the ~16%, which is the sentence it qualifies. |
| 7 | 138 | Not because the biology is unknown, but because the pieces past "know the variant" are hard: the breakpoint varies between patients (so there is no single off-the-shelf product), the junction is mostly self-sequence (EWSR1 and NR4A3 are both self proteins — only the seam is foreign, so central tolerance may have pruned reactive T cells), sarcomas are low-mutational-burden "cold" tumours, and a bespoke per-patient product for an ultra-rare cancer has no commercial pull and cannot easily be trialled at scale. (80w) | Not because the biology is unknown, but because the pieces past "know the variant" are hard. The breakpoint varies between patients, so there is no single off-the-shelf product. The junction is mostly self-sequence: EWSR1 and NR4A3 are both self proteins; only the seam is foreign, so central tolerance may have pruned reactive T cells. Sarcomas are low-mutational-burden "cold" tumours, and a bespoke per-patient product for an ultra-rare cancer has no commercial pull and cannot easily be trialled at scale. (17 + 13 + 27 + 27w) | A four-item colon list becomes four sentences. Two parentheticals are promoted to main clauses (parens → comma / colon + semicolon). **Net −1 word.** ⛔ Every hedge survives *in the same grammatical strength*: `may have pruned reactive T cells` (not *has pruned*), `cannot easily be trialled at scale` (not *cannot be trialled*), `no commercial pull`. The following sentence's counterweight — *"Personalised neoantigen vaccines are nonetheless in late-phase trials in other tumours"* — was not touched. |
| 8 | 262 | `coverage_scan.py` scans a broad common HLA-A/-B panel (≈34 alleles) through MHCflurry, takes every allele presenting a strong junction binder, and — because under 1 − ∏(1 − af)² the greedy-optimal order is simply descending allele frequency — plots **cumulative coverage vs. number of alleles**, globally and per region (Figure …; data …). (51w real; reported inside a 78w join, see §5) | `coverage_scan.py` scans a broad common HLA-A/-B panel (≈34 alleles) through MHCflurry and takes every allele presenting a strong junction binder. Because under 1 − ∏(1 − af)² the greedy-optimal order is simply descending allele frequency, it plots **cumulative coverage vs. number of alleles**, globally and per region (Figure …; data …). (19 + 32w) | The interrupting `— because … —` aside becomes the second sentence's opening clause, which is where the reader can use it. The formula `1 − ∏(1 − af)²`, the panel size `≈34 alleles`, and both artifact filenames are unchanged. **Net −1 word.** |
| 9 | 331 | `python research/modalities/hla_coverage.py` fetches the two public sources (AFND frequencies + ISO/UN M49 region map), reads the project's class-I and class-II epitope JSONs for the presenting alleles, recomputes every number above, and writes `hla-coverage.json` (global + per-region, class I + II + combined, with CIs, sample sizes and the unassigned-population audit). (48w real; reported inside a 74w join, see §5) | `python research/modalities/hla_coverage.py` fetches the two public sources (AFND frequencies + ISO/UN M49 region map) and reads the project's class-I and class-II epitope JSONs for the presenting alleles. It recomputes every number above and writes `hla-coverage.json` (global + per-region, class I + II + combined, with CIs, sample sizes and the unassigned-population audit). (23 + 25w) | Four chained actions become two sentences of two. **Net +2 words** — the only row anywhere in this seat's work that adds any, offset several times over by rows 6, 7, 8 and 10 in the same paper. `with CIs, sample sizes and the unassigned-population audit` is carried whole — that clause is what makes the artifact auditable. |
| 10 | 337 (**deletion**) | The MHCflurry/matplotlib steps run in CI (`.github/workflows/modalities-run.yml`). **The step runs in CI (`.github/workflows/modalities-run.yml`).** | The MHCflurry/matplotlib steps run in CI (`.github/workflows/modalities-run.yml`). | ⚠ **The only text removed anywhere in this seat's work.** The second sentence is a verbatim duplicate of the first's claim — same workflow path, no antecedent for its singular *"The step"*, and it names nothing the first does not. **Net −6 words.** Its caution accounting is in §4 and it is the *entire* caution delta in this paper. |

---

## 3 · ⛔ Sentences I did NOT change, and why (`scientific-writing` §5, seat rule 7)

The instruction was not to chase the count, so these are named rather than quietly left.

- **`closed-routes-negative-record.md`:88, the 53-word remainder.** After the split, the surviving
  long sentence is almost entirely the `integrity.json` design-brief **quotation**. It is one idea,
  it is somebody else's words, and shortening it would mean paraphrasing a source the paper quotes
  precisely because it wanted the source's own phrasing. It stays.
- **`closed-routes-negative-record.md`:340, the 45-word remainder.** Same shape: the Wansa et al.
  quotation plus its citation. A quotation is not a sentence a writer may split.
- **`closed-routes-negative-record.md`:520 (55w), :310 (54w), :393 (50w).** Each is a single
  qualification — *"Two grade-level questions are open and are not resolved here…"*,
  *"Non-selective activity of these classes in EMC is explicitly not closed…"*, *"The claim above is
  therefore conditional in a way that is stronger than it sounds…"*. `scientific-writing` §4:
  **those are allowed to be the longest sentences in the paper.** All three are under the ceiling
  and none was touched.
- **`hla-coverage-emc.md`:270 (59w) and :301 (56w).** The first is the coverage-curve shape result
  with its `~50–60%` and its named alleles; the second is the independence-assumption limitation
  (*"we ignore linkage disequilibrium between loci"*). Both are one idea, both under the ceiling.
- **`degrader-methods-failure-record.md`:483 (56w), :271 (50w).** Single-idea sentences under the
  ceiling. Left alone.

---

## 4 · ⛔⛔ The caution audit — did readability cost honesty?

`--caution` was run on `git show HEAD:<path>` and on the working tree for all four papers, and the
**full marker breakdown** was diffed, not just the total.

| document | markers B → A | per 1000w B → A | marker-by-marker diff |
|---|---|---|---|
| `degrader-methods-failure-record.md` | 57 → 57 | 13.0 → 13.0 | **identical** |
| `closed-routes-negative-record.md` | 75 → 75 | 17.0 → 17.0 | **identical** |
| `cancer-modality-census.md` | 44 → 44 | 13.6 → 13.6 | **identical** |
| `hla-coverage-emc.md` | 30 → **29** | 11.7 → **11.3** | one token: `ci` 6 → 5 |

⭐ **The single delta, named as §4 of the skill requires.** The marker that left is a bare `CI`
matched by `_INTERVAL`'s `\bCI\b`, and it came out of the **duplicated sentence removed in row 10**:
*"The step runs in CI (`.github/workflows/modalities-run.yml`)."* That `CI` is **continuous
integration**, not a confidence interval — a false positive of the interval pattern. The paper's
twelve `95% CI` markers and its five remaining `CI` tokens are all intact, as are `untested` (×3),
`unverified`, `unknown`, `limitation` (×2), `caveat`, `cannot` (×2), `may` (×2), `could` (×3) and
every `is not` / `are not` / `was not` / `do not`.

⛔ **No qualification, null, UNKNOWN, limitation or interval was removed from any of the four
papers.** The `--check` ratchet is not involved either way: none of the four is pinned in
`readability-baseline.json`, and **I did not touch that file** (not an owned path, and it needs no
change — a splitting change repartitions text without removing any).

Second, independent check, because the marker count is a pattern and not a reader: **every one of
the ten rows in §2 was re-read against its original**, and the "what moved" column is the record of
that read. The three constructions this seat refused, explicitly:

1. **`have been reported` → `works` / `is established`** (row 3). A negative-results paper reporting
   what the *Ewing* literature has built must not be compressed into a claim that it works in EMC.
2. **`reported to activate NR4A3` → `activates NR4A3`** (row 4). 6-MP's activation of NR4A3 is a
   literature report the paper then closes the route on; the attribution is the claim.
3. **`may have pruned reactive T cells` → `has pruned`**, and **`cannot easily be trialled at
   scale` → `cannot be trialled`** (row 7). Both would convert a stated difficulty into a fact
   about the world, which is the exact failure CLAUDE.md §6 records at scale.

---

## 5 · ⭐ A defect S5's classification does not cover: an inline code span that opens a sentence

**Two of PUB-HLA-COVERAGE's four flags were never real prose**, and this is a fourth artefact class —
distinct from S5's list-item join and multi-line-HTML-comment rows.

`lint_readability.body()` replaces an inline code span with a space
(`t = re.sub(r"`[^`]*`", " ", t)`, line 137). When a sentence **opens** with one, the splitter then
sees a terminal stop followed by whitespace and a lowercase word, which is not an opener, so it does
not split — and the two sentences are reported at their combined length.

Measured on the pre-edit file:

| reported | real parts | joined at |
|---|---|---|
| 78 w at line 262 | 27 w + 51 w | `… where does it plateau? ` `` `coverage_scan.py` `` ` scans a broad …` |
| 74 w at line 331 | 48 w + 26 w | `… unassigned-population audit). ` `` `coverage_scan.py` `` ` builds the §3.3 curve …` |

**Every real part was already under the 60-word ceiling.** Direction of harm is the same as
AUT-PD-142 — it **over**-states a length, so it is strict-only and lets nothing past the gate — but
it is the same instrument telling a writer to rewrite prose that does not need rewriting.

⛔ **I did not contort the prose to satisfy the instrument.** Rows 8 and 9 split the *first* real
sentence of each pair on its own merits — a three-action chain with an interrupting parenthetical
aside (row 8) and a four-action chain (row 9), both squarely `scientific-writing` §1.4 — and the
joins fall under the ceiling as a consequence, not as the reason. Had the only available fix been
"add a word so the linter sees a capital letter", the honest answer would have been to leave the
prose and file the row alone.

`research/manuscripts/lint_readability.py` is **not an owned path** (S5 holds it), so the fix is a
ledger row below, not an edit here.

---

## 6 · What I could not do, and what it is actually waiting on

- **Nothing is blocked.** All nine flagged sentences were mine to fix and all nine are fixed.
- **`clause_7` "after" is a replay, not the real call.** The real clause reads a document out of git
  at a pinned sha, and this seat may not commit (charter §1). I reproduced its exact logic
  (`LR.measure` on the working-tree file, then the `over_ceiling` branch and the baseline lookup) and
  report that. **The driver should re-run `publish_bar.clause_7_readable_enough_to_review` against
  the merge commit** — it is a $0 call and it is the reading that counts.
- **`readability-baseline.json` needs no change** — verified, not assumed: three of four papers'
  caution figures are byte-identical and none of the four is pinned in it.
- **The `lint_style` 414 on these four files is out of scope and pre-existing** (they are not in
  `TARGETS`), unchanged by my edits at 414 before and after. Whether these four documents *should*
  be `lint_style` targets is a real question and it is not mine — I did not touch that list.

---

## 7 · Ledger rows the driver should write

1. **`what`:** ⛔ `lint_readability.body()` REPLACES AN INLINE CODE SPAN WITH A SPACE, SO A SENTENCE
   THAT **OPENS** WITH ONE IS GLUED TO ITS PREDECESSOR. `re.sub(r"`[^`]*`", " ", t)` at
   `lint_readability.py:137` runs before the splitter, so `… plateau? ` `` `coverage_scan.py` ``
   ` scans …` presents the splitter with a stop followed by a lowercase word and no split happens.
   ⭐ Measured 2026-09-01 on `neoantigen/hla-coverage-emc.md` at
   `HEAD c9583ea41b33f85dd14541216acad55476a64d44`: **2 of that document's 4 over-ceiling flags**
   (78 w at line 262 = 27 + 51; 74 w at line 331 = 48 + 26) were this artefact, and **all four real
   constituent sentences were already under the ceiling.** Same strict-only direction as AUT-PD-142
   — it overstates a length and lets nothing through — and a fourth class beyond S5's two proposed
   rows. Candidate fix: allow the opener class to match after a run of whitespace left by a stripped
   code span, or substitute a placeholder token instead of a space. ⚠ A placeholder changes word
   counts, so the fix must be measured against the pinned baseline before it lands.
   **`kind`:** `process_defect` · **`state`:** `queued` · `cost_class`: free.

2. **`what`:** ⚠ FOUR PUBLICATION DOCUMENTS SIT OUTSIDE `lint_style.TARGETS` WHILE CARRYING
   PUBLICATION ENDPOINTS — `methods-record/degrader-methods-failure-record.md` (PUB-METHODS),
   `methods-record/closed-routes-negative-record.md` (PUB-CLOSED-ROUTES),
   `modality-census/cancer-modality-census.md` (PUB-MODALITY-CENSUS) and
   `neoantigen/hla-coverage-emc.md` (PUB-HLA-COVERAGE). Measured 2026-09-01: run manually, the four
   together report **414 style errors** (glyph density, bold density, em-dash density, emphasis
   fragments), unchanged before and after this seat's readability pass. ⛔ **This is a question, not
   a finding:** `lint_style` is scoped to submission texts deliberately, and whether these four are
   submission texts is an editorial call the seat did not make. Decide the scope; do not widen the
   list silently to make a number move.
   **`kind`:** `decision` · **`state`:** `queued` · `cost_class`: free.
