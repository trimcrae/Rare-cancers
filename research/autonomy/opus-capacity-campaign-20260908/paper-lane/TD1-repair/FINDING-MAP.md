# TD1 — finding map for the single author correction batch

**Date:** 2026-09-08 · **Owner:** sole TD1 author-repair owner (no commit, no push; the parent integrates)
**Source of record:** the complete 44,985-byte `FINAL-SCIENTIFIC-REVIEW.md`
(SHA256 `edda66155c9c472329175eee5890c698679c8ecca5b77e961c90d436da4123b7`) and the root adjudication
memo `TD1-final-review-root-adjudication-20260908.md`, both read in full from the verified capsule,
together with **both** reviewer arithmetic attempts (attempt 1 exit 1 on a cp1252 decode of a UTF-8
artifact; attempt 2 exit 0) and the 29 original support files. No preliminary audit and no new
baseline review was performed.

## Objects

| | identity |
|---|---|
| frozen input manuscript | 20,924 B, SHA256 `fe316b44d44b7f16cbb62ea7451dd4c3acff1a8cc2edc0dd73932e98649c9398` — verified byte-identical in the working tree before editing; retained as `BEFORE-emc-transcriptional-proteostatic-dependency.md` |
| repaired candidate | 41,911 B, SHA256 `12c082b3d4dc8dabedb4e7f7716435f175da88ea6e684c66f7d40de29942e8aa`, Git blob `60fa27c312faefb106f627aaa085c86b8d37b645`, frozen under `frozen/` with `HASHES.sha256` |
| repository HEAD at repair time | `a6a21fc591d2451038cdf53449b91e3990d59cfb`. ⚠ The parent named input commit `498a6816a`; HEAD had advanced under other lanes, but the manuscript bytes were unchanged (`fe316b44…`), so the frozen object reviewed is the object repaired |
| E `emc-expression-panels.json` | `123bd05a9f9f5d08…` — identical to the hash recorded in the reviewer's attempt-2 input block |
| D `depmap-sarcoma-dependency.json` | `d88bed62a80dcb51…` — identical to the reviewer's recorded input |
| G `census-route-expression-grading.json` | `5bc3c80c034dde77…` — identical to the reviewer's recorded input |

Root accepts all 11 findings; the candidate frozen at `9f571e81` is **HOLD** and its central empirical
"opposite disagreement" claim is **PARKED**. This batch delivers the narrower descriptive synthesis of
two distinct evidence streams. ⛔ Nothing here reopens the parked claim, and no producer, raw
reanalysis, simulation, experiment, source acquisition, corpus preflight or publication was run.

## F1 — remove the unsupported empirical "opposite disagreement" result · **applied**

| what root required | where it now stands |
|---|---|
| reframe title, purpose, summary, results and outcome table as complementary unpaired observations | new title *"Two unpaired evidence streams for a fusion transcription factor…"*; `purpose:` and `scope:` rewritten in the front matter; §Summary restructured as **Stream A** and **Stream B**; §5 outcome table rewritten with a "what follows" column that names two unpaired descriptions |
| remove measured opposite disagreement | §Summary now states, in terms, that the paper "makes **no claim that abundance and dependency disagree**, in opposite directions or at all", and that testing such a claim needs a design observing both in comparable units, which was not run |
| remove abundance-only promotion/burial counterfactuals | the entire "reading only abundance would have given a confident answer / promoted / buried" narrative is deleted from the summary and from the old §4 |
| remove validated transfer and fusion-caused dependencies | Stream B is described as "an **uncalibrated assumption**, not a validated transfer"; no dependency anywhere is attributed to the fusion |
| sarcoma membership alone does not calibrate transfer | stated verbatim: shared "sarcoma" lineage membership does not establish that a dependency structure carries to this disease |
| ⛔ do not retain the discovery behind conditional wording | the old conditional construction (*"if the dependency structure … holds in EMC cells, then the transcriptional class offers nothing to select on"*) is removed outright, not softened |

## F2 — GPL3290 withdrawn as clean independent corroboration · **applied (route: withdraw)**

- §1.1 carries an explicit **"Interpretation hold on GPL3290"** paragraph recording the actual deposited
  reference labels — **ten EMC `CRH-mRNA`, three DFSP `CRH`, three GIST `UHR`** — verified against the
  live annotations by check `03/04` (checks §1).
- It states that within-array standardization does not generally remove a gene-specific reference
  difference; that upstream harmonization is **not established**; and that incorrect original
  preprocessing is **not proven either**.
- The GPL3290 values remain displayed in a separate, explicitly held table so nothing is hidden, and
  every biological conclusion in the paper is carried by GPL6244 alone.
- ⛔ Reference equivalence is not assumed, six comparators were **not** silently reduced to three, no raw
  reanalysis was run, and no new processing record was acquired. The reopening condition is stated in
  §1.1.

## F3 — dependency construct defined; absence-of-selectivity claims withdrawn · **applied**

New §1.2 defines the **24Q4 Chronos gene effect** and its sign, the **< −0.5** threshold, the operational
**`OncotreeLineage` ∈ {Soft Tissue, Bone}** cohort rule, **91 screened versus 176 catalogued** models
with 91 named as the denominator, and `selectivity` as **non-sarcoma-cancer-line mean minus
sarcoma-lineage mean**, reported without variability, comparator n, or an equivalence margin.

- **Preserved:** the CDK7/CDK9 broad binary dependency (91/91), the small descriptive mean differences
  (+0.085, +0.017, −0.026, +0.073, −0.067) and the five dependency rows in full (§3 table).
- **Withdrawn:** "nothing to select on", "no selective handle", "no selectivity appears anywhere",
  "essentially no selectivity", the equivalence reading, and the normal-tissue-window inference —
  replaced by an explicit list of what a binary threshold cannot establish, including the note that a
  cancer-versus-cancer comparison cannot supply a tumour-versus-normal window.
- **SMARCB1 control:** recorded as **failing its own stated expected-positive criterion** (13 rhabdoid
  models, mean −0.025, 7.7 % dependent, against rest −0.832 and 83.9 %). ⛔ It is **not** relabelled a
  passed negative, and the failure is explicitly stated **not** to show that the CDK numbers are wrong —
  it means the release's sensitivity to selective dependencies is uncalibrated.
- **Class abstracts:** cited as model-specific differential CDK dependence in other diseases and assays
  (PMID 25043025 subset sensitivity; PMID 26406377 inhibitor + CRISPR/Cas9 contrast), explicitly not
  evidence of an EMC window and not a re-analysis of 24Q4.

## F4 — HSP70 non-significance correctly scoped · **applied**

§2 "The HSP70 reading" states that the two negative estimates are not distinguishable from zero and that
the approximate intervals **−0.274 to +0.103** and **−0.584 to +0.256** include positive differences;
that this is not absence of elevation, not an equivalence result and not contradictory biology; and that
a relative contrast against other tumours is not a test of whether EMC cells mount a stress response at
all. The reference-design qualification travels with it. ⛔ "absence of elevation", "the reading shows
none" and "internally contradictory" are gone; the phrase "absence of elevation" survives only inside its
own explicit negation, which check `04` asserts. ⛔ The reviewer's arithmetic is labelled conditional
arithmetic on rounded published summaries throughout and is never promoted into a raw biological result.

## F5 — compensation and clientship kept as separate untested hypotheses · **applied**

§3 records that single knockouts **were** measurable (5.5 % / 18.7 %), that a low dependent fraction does
not identify compensation, and that redundancy is plausible but not the only explanation with no dual
perturbation or rescue anywhere in evidence. **CDC37's 97.8 % is stated as the measured observation** and
explicitly not proof about every family member, not a double knockout, not evidence about a fusion and
not a therapeutic window. §4 separates binding, stability/folding dependence, fusion-specific dependence
and selective vulnerability as four different claims, uses *client* only for a binding observation, and
removes "one measurement settles". The inconsistent operational definition is corrected in the **C**
patch (`definitions.documented_chaperone_client`). ⛔ No experiment or protocol is commissioned.

## F6 — expression construct, controls and comparator selection disclosed · **applied**

- **All seven memberships** in one reader-facing table with per-platform readable counts, plus the three
  unreadable members named (*HSP90AA1* on GPL3290; *HSPA8* on GPL6244; *HSF1* on GPL3290).
- **Weights:** stated as **unweighted** — the score is the plain mean over readable members; the live
  producer carries no weights (verified: `_score_gene_list` averages `readable`).
- **Formula:** within-array standardization written out, `(value − array mean over all probes) ÷ (array
  SD over all probes)`, then a per-specimen list mean, then Welch's *t*.
- ⛔ Explicitly **not** absolute abundance, transcription rate, protein, or a common cross-platform
  biological effect scale; the 0.61-vs-0.09 cross-platform reading is gone.
- **MYC** is shown to account for the positive four-gene context mean (+1.0625 / +1.863 against group
  +0.1983 / +0.4709), with the other-three algebra (≈ −0.090 / +0.007) labelled descriptive bookkeeping,
  **not** a new panel test.
- **Comparators as annotated:** 17 LGFMS, 6 desmoid fibromatosis, 6 myxofibrosarcoma (binned under
  `fibrosarcoma`) on GPL6244; 3 DFSP + 3 GIST on GPL3290; **5 solitary fibrous tumour and 2 pooled
  skeletal-muscle records excluded** as unclassified, with the operational reason given and no invented
  prospective rule.
- **Ascertainment:** counts are specimens/arrays under deposited labels; patient uniqueness and fusion
  confirmation are stated as **not established** by them.
- **Proliferation:** the independence claim is **removed**. The eleven-gene control (t = 0.441 / 2.905,
  df 6.7 / 14.0, Δ 0.0896 / 0.4459) and the unscored one-gene *MKI67* group are reported as **not**
  establishing independence, alongside cellularity, lineage, handling, batch and reference composition.

## F7 — uncertainty reported; census superlative removed · **applied**

Both §2 tables give **Δ, *t*, df, coverage, approximate two-sided *p* and an approximate 95 % interval**,
with the derivation and its rounding inheritance stated. All fourteen nominal significance descriptions
are preserved as conditional arithmetic and were **independently re-derived** in this repair (check
`04`), agreeing with the retained reviewer attempt-2 output to < 1e-9 on every *p* and < 1e-6 on every
interval bound, from a t-tail routine calibrated on the Cauchy identity. The illustrative fourteen-test
Bonferroni threshold is reported with the explicit statement that fourteen is **not** established as the
scientific family and that **no group clears it on both platforms** (three clear it on one platform:
`cdk7_initiation_module` and `transcriptional_output_context` on GPL3290, `hsp90_machine` on GPL6244 —
re-derived, check `04`). "Most concordant" and "largest t-statistics" are removed from the manuscript and
from the **G** annotation; ⛔ no census-wide rerank and no extra statistics were commissioned.

## F8 — literature bound to items actually inspected · **applied**

§4 states the finding as *"we did not identify a qualifying direct binding result … among the items
inspected in that dated search"*, and lists the limits explicitly: **Q15's 25 hits were not individually
screened**; **Q13's client-screen supplement membership is unknown**; several records are abstract-only or
inaccessible; **preprints and non-PubMed sources were not searched**; a title-only interactome query
cannot establish that no interactome exists. Human HSP90 clientship is separated from the engineered
**yeast** disaggregase FET work (PMID 31171724), and **depletion** is separated from **binding**
throughout. The four transported Europe PMC payloads are described in the reference note as retained
**abstracts, not full articles**. Detailed assertions requiring unavailable originals are narrowed to
what the curated records support. ⛔ No new source hunt was run; the four retained payloads already in
the lane were read for the bibliographic fields used in §9, and nothing was re-downloaded.

## F9 — falsifiers replaced by scoped update conditions · **applied**

§6 is now **"Update conditions"** with eight rows (U1–U8), each naming the statement at its actual scope
and what would update it. It states that one later null or reversed series does not erase a historical
estimate; that non-significance is not equivalence; that a future panel updates generalization, not the
validity of a fixed historical statistic (U2); that a finding in **any** FET fusion does not establish
EMC clientship (U5); that a third transcript series would not identify proteostatic load (U4); that
redundancy is not demonstrated so there is no redundancy result to falsify (U6); and that independence
from proliferation is not claimed, so nothing there awaits falsification (U7).

## F10 — live linked source conclusions repaired · **patched for the parent** (annotation-only)

See `CHANGED-FIELD-CODE-MAP.md` for the exact dated field/code map, `patches/` for the six unified
diffs, `patches/EDIT-LEDGER.json` for per-field hashes, and `INVARIANCE-EVIDENCE.json` for the numeric
and membership invariance evidence: **441,602 checks, 0 failures**, of which **393,752 non-string leaves
unchanged**, 34,675 key sets preserved, 13,114 list lengths preserved and exactly **22 string changes,
all declared**. Every patch was applied to a pristine copy **outside** the repository to prove it applies
cleanly; the working tree was not modified by the check. ⛔ No producer was regenerated, and each
generator-source edit was verified by AST comparison to change only the named string constants and to
produce a literal byte-identical to the corrected displayed annotation — without claiming any execution
occurred. All original historical output and check logs are preserved untouched.

## F11 — independently intelligible and accurately reproducible · **applied**

§1.1/§1.2 supply reader-facing methods; §2/§3 supply results tables; §8 names the **fixed producers and
input versions** (24Q4, `CRISPRGeneEffect.csv`, `Model.csv`, the two GEO series and platform records) and
carries a two-column table separating **retained derived summaries** from **unavailable original
matrices, mapping tables and per-line distributions**, with an explicit statement of exactly what is and
is not reproducible. ⛔ "No producer was run to write it" is corrected: it is stated that this fact
describes the drafting episode and is **not** the computational method, and that dynamic discovery of the
newest DepMap release is not a specification of the 24Q4 analysis. §9 is a conventional **15-entry
reference list** with DOIs, PMIDs and resolvable links, plus GEO and DepMap data sources. §7 scopes the
no-patient/no-agent language to **this study's** lack of new intervention and states that the analysis
uses archival patient-derived material and performed **no exhaustive clinical-exposure census**.

## Residual, and what this batch does not claim

1. **The parked claim stays parked.** The narrower revision stands free of it: no section depends on an
   observed expression–dependency relation, on GPL3290 as corroboration, on demonstrated compensation,
   on clientship, or on absent selectivity. **No blocker prevents this narrower version from standing.**
2. **GPL3290 remains under an interpretation hold**, which is a stated limit of the paper, not an
   unresolved defect in it. Reopening requires authentic deposited processing/reference evidence.
3. **Retraction sweep status for the new reference list is UNKNOWN, not clean.** `lint_citation_types`
   reports every one of the fifteen identifiers as `NOT SWEPT (advisory)` against the 2026-09-01 sweep.
   Sweeping them requires a network call, which this repair is fenced from. Flagged for the parent.
4. **House style is unchanged in kind.** `lint_style` exits 1 on the repaired candidate exactly as it
   did on the frozen input, for the repository's decorative-glyph convention. Em-dash density fell from
   10.4 to 4.0 per 1000 and heading-style errors from 4 to 2. This is not a scientific blocker.
5. **A cross-paper echo is flagged, not edited.** `research/manuscripts/modality-census/cancer-modality-census.md:186`
   still says "the most concordant elevation the whole census found". That file is another paper's and is
   outside the F10 scope (E/EP, G/GP, C); it is reported to the parent rather than touched here.
