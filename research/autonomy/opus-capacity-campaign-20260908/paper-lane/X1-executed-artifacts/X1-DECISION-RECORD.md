# X1 — decision record for ONE proposed new working revision of the EMC ATR collaborator package

Worker **X1**, EMC capacity campaign, paper lane, 2026-09-08. Lane `/tmp/claude-0/x1-lane/`.

⭐ **This is a NEW working revision, PROPOSED now. It is not a recovery of any lost historical
revision, and nothing here is claimed to reproduce one.** Every sentence changed relative to R1's
candidate was written in this lane today. Shared integration, any view regeneration and the title
decision remain the scientific coordinator's.

**Start:** `date -u` 2026-09-08T12:09:06Z · `git rev-parse HEAD` `90d60d917b6f985a9c9f44cb3c6c545d91bb32d8`
· `git status --porcelain` = ` M research/manuscripts/submission-metrics.json` (pre-existing, not mine).

## 1 · What was built

| file | what |
|---|---|
| `PROPOSED-X1-emc-atr-collaborator-package.md` | the candidate, 762 lines |
| `PROPOSED-X1-vs-R1.diff` | 541-line unified diff against R1's candidate |
| `PROPOSED-X1-vs-COMMITTED-BASELINE.diff` | 616-line unified diff against the committed manuscript |
| `build_x1_candidate.py`, `build_x1_step2.py`, `build_x1_step3.py` | the edits, replayable; every replacement asserted |
| `RETAINED-APPENDIX-A-history.md` | Appendix A, byte-for-byte from the input, before removal |
| `MOVED-TABLES-SOURCE-BLOCKS.md` | the two moved tables, verbatim, before renumbering |
| `PREREG-ROWS-CANDIDATE-vs-BASELINE.txt` | the committed P1-P5 rows, for the equality check |
| `X1-COVER-LETTER-AND-TITLE-PROPOSALS.md` | isolated proposals, nothing applied |
| `INPUTS/` | R1, U1, W1, W2, W3 artifacts as received |

**Shape:** title, author block with ORCID, abstract, §1 Introduction, §2 Methods (2.1-2.6),
§3 Results (3.1-3.5), §4 Pre-specified predictions, §5 Constructs and controls, §6 Limitations,
§7 Data and code availability, §8 References (10), §9 Supplementary tables (S1, S2, S3).
**Main-text display items counted, not assumed: FIVE tables (1-5) and ONE figure.** The changelog's
"six tables" was not forced; five is what the document contains after the two moves.

## 2 · The three required corrections, as they now read

**1 — the abstract's comparator span.** Now:

> "…against a span of 0.000 to 0.267 spanned by the three reported EWSR1::ATF1 breakpoints. The
> EWSR1::ATF1 construct in which recruitment was measured has no stated breakpoint, so that span
> describes the reported breakpoints and not the measured construct; the measured positions on the
> axis itself are 0.000 and 1.000."

The phrase "measured comparator span" occurs nowhere in the candidate. Table 3's caption was
rewritten to the same effect, and Figure 1B's caption repeats it.

**2 — the retained-RG-axis limitation.** The sentence *"neither is placed between two positions
measured in reference 1, because only 0.000 and 1.000 were measured there"* is gone. Now:

> "Placing a fusion on the retained-RG axis does not establish that recruitment was measured at that
> position: reference 1 measured recruitment at 0.000 and at 1.000, and a position between them is a
> computed placement on the axis and not a measured recruitment result."

**3 — the evaluated grid.** No sweep was run. Every unrestricted claim was narrowed to the grid the
retained computation actually evaluated:

- abstract: "…falls outside the FET compositional range at **every prefix on the evaluated grid
  (50 aa upwards in 10-aa steps)**."
- Table 4 cell: "no TCF12 prefix **on the evaluated grid** reaches the lowest value any FET prefix
  takes **on that grid**".
- §3.5 prose: same restriction, plus "The grid is every prefix from 50 aa upwards in 10-aa steps,
  66 prefixes for TCF12 and 61, 55 and 48 for EWSR1, TAF15 and FUS; **lengths between grid points
  were not evaluated and no claim is made about them.**"
- §3.2's "computed over every prefix" gained "on the evaluated grid (section 3.5)".

The artifact's own `_reading` uses "of any length"; that phrase is not carried into the manuscript.

## 3 · Frequency wording, the 25-residue quotation, denominator provenance

**The 25-residue quotation is RETAINED**, because it verified: *"thus encoding 25 additional amino
acids prior to the NR4A3 ATG"* [3] stands at line 297 of the **committed** manuscript
(`BASELINE-emc-atr-collaborator-package.md:297`), i.e. in an already-committed section, and is
carried unchanged in §3.1 and in §3.3 where it is named as precedent for an N-terminal addition
ahead of NR4A3's initiator. Nothing about it was invented, extended or re-attributed.

**Frequency wording narrowed to the series that actually typed EWSR1 subtypes** — Panagopoulos 2002
[7] and Okamoto 2001 [9]. Sjögren 2003 [10] counts **partner genes** (EWS-TEC 5, TAF2N-TEC 4,
TCF12-TEC 1, of ten) and is now labelled as such in Table 1 and in reference 10. "commonest in every
series that types its cases" became "commonest EWSR1::NR4A3 type in **both series that typed EWSR1
subtypes**"; "counted once across three counted series" became "counted once **in the two series
that typed EWSR1 subtypes**".

**Denominator provenance, preserved and not credited to a quotation that lacks it.** The retained
Panagopoulos quotation is *"The most frequent EWS/CHN transcript (type 1; 10 tumors) … and the second
most common (type 5; two cases)…"* — it carries **counts without a denominator**. R1's "10 of 15" and
"2 of 15" were therefore removed: Table 1 now says "10 tumours, the most frequent transcript" and "in
two cases", and reference 7 states explicitly that the denominator of 15 EWS/NR4A3 cases comes from
this repository's editorial note on that reference and **not** from the quotation. Okamoto's
quotation does carry its denominators (15 of 18 cases fusion-positive; type 1 in 11, type 2 in 1,
TAF2N-CHN in 3), so "of the 15 fusion-positive cases" is used. Sjögren's ten is the sum of the
partner counts inside its own quotation.

**The "two commonest" lead-in is resolved**, and the source quotation is retained accurately and kept
distinct from the counts:

> "The type 1 and type 2 junctions are defined verbatim in a primary source: '…' That sentence names
> type 1 as the most common and defines type 2 without making any frequency claim about it, so it
> establishes the two junctions and not a ranking of the two; the counted series in the table above,
> and not this definition, carry the frequencies."

The corroboration sentence that followed it lost its invented denominators too.

## 4 · Preregistration — unchanged, with the explanations kept separate

**P1, P2, P3, P4 and P5 are byte-for-byte identical to the committed manuscript's rows.** Verified
programmatically against `BASELINE-emc-atr-collaborator-package.md`; all five report IDENTICAL.
R1's two proposed edits **inside** the registration were reverted: P1 keeps "byte-identical to the
reference construct's" and P3 keeps "14 residues of margin to TAF15's first RG at 175". P5 keeps "the
source's full-length FLI1 control" rather than R1's "reference 1's".

Added **after** the table, as explanation and not as amendment: the two margin conventions and why
§3.4 states 13 while P3 registers 14; the redundancy of P4's falsifier with P2's and the equivalence
form of P1, with the note that re-registering a narrowed set is not taken here; and the record
distinction — `registered_predictions` holds **four** entries (P1-P4) and the manuscript carries
**five** hypotheses, with P5 under `tcf12_negative_control.registered_prediction`. **Both records are
preserved as they stand; they are not asserted to be identical and neither was edited to agree with
the other.** No `registered_predictions` entry was read for edit; no shared JSON was written.

## 5 · Figure 1, and its W2 grounding

Inserted at the head of §3.4 with a three-panel caption. Panel A's key is taken from W2's
code-established semantics: ticks are RG dipeptides at the 1-based arginine position from
`composition.rg_content.<protein>.rg_positions`; dashed boxes are the operational RGG boxes
(`RGG_WINDOW = 60`, `RGG_MIN_RG_IN_WINDOW = 6`) whose drawn spans equal `rgg_boxes_operational`,
**"trimmed to start at the first RG the box contains and to end two residues past its last RG-start"**
— W2's exact definition, not paraphrased. The caption records that the finder returns two boxes on
EWSR1 where the source names three RGG-rich domains, and that the definition was not tuned to match.

Per the coordinator's five points: `C166` is described **neutrally** as a printed label with a marker
at residue 166, identifying a position and nothing more, with **no functional biology asserted**; the
box literals are **not** described as a present mismatch (they currently match, and that is stated);
the provenance limitation is stated only in its narrow, true form — the stamp does hash the listed
source files, but nothing binds the data field to the drawing literals, so a later redraw could
preserve a semantic mismatch under a fresh stamp; and the NR4A3 tick point is left **qualified** —
the generator draws ticks at 371 and 508, one reading of the image reported one of them, and
occlusion versus non-resolution is not decided.

**Actual panel support only.** A "What the figure does not show" paragraph names the four results
with no panel support — the frame rule as a rule, the phase-1 donor set, the symmetric sweep and its
0.039 margin, and the TAF15 margin — and forbids citing the figure for them. Panel C's caption
carries the scope clause U1 required, because the panel never prints "type 2".
⚠ **U1's four cross-reference traps were hypothetical and were NOT "fixed"**: no such defect existed
in either document and none was invented to repair.

## 6 · Supplementary, and Appendix A

Table 2 (gene models) → **Supplementary Table S1**; Table 7 (wild-type controls) → **Supplementary
Table S2**. Both moved **verbatim** (the pre-move blocks are retained in
`MOVED-TABLES-SOURCE-BLOCKS.md`); only the label changed, and the main text now points at them.
**Supplementary Table S3** is W1's source-derived table, included as a proposal, with its UNRESOLVED
cells and its no-transcript-level-junction rows intact. ⛔ **No new construct is proposed anywhere.**

**Appendix A was removed from the submission copy only after being retained**, byte-for-byte, in
`RETAINED-APPENDIX-A-history.md` (checked programmatically: the 8,566-character section is contained
in the retention file exactly). Its content also stands in the committed changelog, which the
appendix's own header states it is the former version of. **No original history was erased.**

## 7 · §2.6, drafted without independent annotation-source verification

A new Methods subsection states the transcript-exon-rank convention, the two-exon offset for NR4A3,
and that exon labels never enter a computation directly. It says in terms: **"This correspondence has
not been verified against a second, independent annotation source in this work."** Limitation 3 was
widened to carry the same statement. ⛔ **No wet-lab procedure and no six-step construct/assay
protocol was written**; §5 is unchanged apart from the table move.

## 8 · Also applied

D5: the "Scope of the claims" blockquote moved from the front matter into §6 Limitations,
**wording unchanged** (moved as an extracted string, not retyped). References 9 and 10 completed from
the retained identity-matched records — Okamoto 2001 *Hum Pathol* 2001;32(10):1116-1124,
doi 10.1053/hupa.2001.28226 (W3), Sjögren 2003 *Am J Pathol* 2003;162(3):781-792, PMC1868116
(`PUB-FUSION-PARTNER.json:88`, via U1). **No retrieval was performed.** ORCID 0000-0002-1823-1451
inserted from the repository's existing author record; no external identity lookup.

## 9 · UNRESOLVED

- **"Roughly 3 to 4 per cent of EMC carries TCF12::NR4A3"** (§3.5) is inherited from the committed
  text and its provenance was **not** located in the inputs read here. Sjögren counts 1 of 10.
  ⚠ Flagged for the coordinator; **not changed and not deleted**, because correcting it would need a
  source this task did not open.
- **Whether the four vertical-line weights in Panel A are distinguishable at print size.** A code
  reading cannot settle it and no image was opened here.
- **The NR4A3 tick at residue 371** — occluded or not resolved; undecidable from code, left qualified.
- **The title decision itself**, the view regeneration, and D6 (renumbering into a Discussion) and D7:
  D6 and D7 were not taken. The changelog's §4.1-§4.4 structure is not adopted here.
- **The first missing revision pass.** R1's U8 finding stands: the later changelog block corrects
  sentences committed nowhere, so its "before" column cannot be applied. Nothing here closes that.
- **Word and display counts** in the editorial block were replaced with this revision's actual
  counts as a statement to re-measure; a fresh word count was not run against a journal limit.

## 10 · What I did NOT do

No shared repository path was written, copied, moved or deleted. **No git write of any kind** —
read-only `git rev-parse`, `git status` and `git show` only. No network, no retrieval, no PubMed or
WebFetch call, no new science run, no sweep, no figure regeneration, no image opened, no
`systems_check.py`, no view regeneration, no gate or preflight cycle, no historical response audit,
no publication, no deposit. No frozen or held scope was touched. No EMC efficacy, safety,
selectivity or clinical-readiness claim is made anywhere in the candidate; there is no wet lab. No
fact, source, measurement or citation field was invented. **No content-policy refusal occurred**, so
there is nothing to record verbatim under that heading. **I deleted nothing:** every input, the
candidate, both diffs, the three build scripts, the retained appendix, the moved-table blocks and
the hashes are in this lane.
