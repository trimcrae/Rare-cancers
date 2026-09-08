# INTEGRATION RECORD — ATR collaborator package, new working revision

Date: 2026-09-08 (times from `date -u` in the executing command).
Integrated by: the campaign parent, in this same session. No new child was dispatched.
Base commit at start: `7d42e1f07c5f24ce97f52e16ba31575519431c6e`, branch `claude/confident-bardeen-ji76cd`.

The scientific coordinator ACCEPTED X1's reconstruction and its already-supplied title as the NEW
working manuscript, and authorised shared integration after six bounded corrections, plus one
sentence replacement in section 3.5 arising from Y1's disposition. **Integration is not publication
acceptance.**

## Source and target

| | |
|---|---|
| Candidate | `paper-lane/X1-executed-artifacts/PROPOSED-X1-emc-atr-collaborator-package.md`, sha256 `60742f92e4133acc618aca02665100a49d9ff6474e28d79bebb59bb61db09926`, 58,254 B |
| Committed baseline replaced | `research/manuscripts/dependency/emc-atr-collaborator-package.md`, sha256 `8180932a59ecad8f94c753579931c945d582d2a1465c3727e223a5ad0bee4da1` |
| Cover letter baseline | `...-cover-letter.md`, sha256 `5a79fc20079d96c59cbf70dde751e57e5e31a038ed4bf81ac0c55bcf21ceed93` |

The retained X1 lane directory, including the original child JSONL, the decision record, the verbatim
earlier Appendix A and both diffs, is UNCHANGED. Nothing in it was edited to agree with this
integration.

## The seven authorized changes, as applied

Each was applied by an exact single-occurrence string replacement; the script aborted on any count
other than one. All twelve replacements reported success.

1. **Frontmatter.** The leading HTML proposal comment was removed from the head of the file, so valid
   YAML frontmatter is now the first block. A revised editorial provenance comment was placed
   immediately AFTER the frontmatter. Its present tense was corrected: it no longer says nothing has
   been applied. `date: 2026-08-09` and `last_verified: 2026-08-09` are unchanged, and the comment
   states explicitly that no scientific result was recomputed or re-verified and that no fresh
   verification is claimed. It also carries the qualification that the introducing edit's wording was
   not recovered from the history examined at its squash and shallow-clone boundary, which is a limit
   of that examination and not global historical absence.
2. **Figure 1.** A Markdown image was added for the existing committed
   `../figures/emc-fusion-frame-fig1.png`. No figure was generated, redrawn or recomputed. The Panel C
   caption's nucleotide accounting was corrected: 1 nt donated by EWSR1 plus 176 nt of NR4A3
   untranslated sequence, being 174 nt of exon 2 and the first 2 nt of exon 3, giving 177 nt and 59
   codons. Independently re-derived by the parent from
   `emc-fet-frame-and-composition.json`: `type2_seam.nr4a3_5utr_nt_from_exon_2 = 174`,
   `nr4a3_5utr_nt_from_exon_3 = 2`, `nr4a3_5utr_nt_retained_total = 176`. The generator does draw the
   exon-3 contribution as a separate annotated block (`emc_fusion_frame_figure.py:231-242`), so the
   caption describes what is drawn.
3. **Methods 2.3, 2.5 and section 7.** 2.3 now describes the retained symmetric sweep run on the same
   evaluated grid, every N-terminal prefix from 50 residues to full length in 10-residue steps, for
   TCF12 and each of the three FET proteins, read from the retained artifact rather than re-run; the
   asymmetric published version is named as what it replaces. 2.5 now lists three commands and scopes
   each: `emc_fet_construct_designs.py --check` to the assembly coordinates, frames and axis rows it
   actually produces; `emc_fet_frame_and_composition.py --check` to the frame rule, seam arithmetic
   and composition results, with its unit tests named; and `emc_fusion_frame_figure.py --check` to the
   figure provenance stamp. Section 7 gained rows for that producer, its artifact, its tests and the
   figure generator with its provenance file, and the GitHub Actions sentence was scoped to the one
   artifact it describes. All command signatures were read from the modules' `main()`; **none of the
   three was executed**, and the manuscript says so.
4. **Preregistration commentary.** The P2/P4 falsifiers are now stated as OVERLAPPING and not
   identical, with the two-sided and directional difference spelled out. The equivalence sentence was
   replaced by the exact authorized wording: "Failure to detect a difference does not establish
   equivalence. The registered wording supplies no equivalence margin or precision criterion, so a
   nonsignificant comparison alone cannot confirm P1." No margin was invented, no registered
   hypothesis or falsifier was altered, no assay plan was created, and the P1-P5 rows and both source
   records are intact.
5. **Supplementary Table S3.** The "Reported rank" row is relabelled "Reported rank — LEGACY SOURCE
   DESCRIPTION, not a counted frequency (see note)" and a note after the table states that its cells
   are retained verbatim with their provenance, that they are a legacy source description rather than
   a frequency counted in this work, and that Table 1 carries the corrected frequency evidence and
   governs where the two differ. No artifact value or cell content was modified.
6. **Figure QA placement.** The NR4A3 fine-tick legibility uncertainty and the literal-versus-data
   binding hazard were moved out of the caption into a new QA note,
   `emc-atr-collaborator-package-integration-qa-2026-09-08.md`. The caption now carries a concise
   reader-facing scope statement grounded in panel content; the instruction "none of them may be
   cited to this figure" is gone. No legibility claim is made anywhere.
7. **Section 3.5 opening (Y1 disposition).** Replaced with the exact authorized sentences. Details and
   the partner-assigned versus total-series denominator distinction are in the Y1 collection record's
   dated append and in the QA note.

Two style-gate errors inherited from the candidate (`deliberately` in the Panel A caption, `stated
here` in section 3.4) were removed by minimal rewording that changes no quantity or claim. The
committed baseline passed `lint_style` and the candidate did not; this restores that.

## Companions and generated views

- Cover letter: C1, C2 and C3 applied as one contiguous rewrite of the passage that carried all
  three; C4 adds the ORCID; T1 and T2 carry the adopted title.
- `python3 systems/systems_check.py --write-views` regenerated 111 views. Exactly two changed,
  `L3-publications.md` and `L2-rt-atr-panel.md`, and in each the only change is the title string. The
  diff was inspected. No unrelated mutation was committed.
- `#32-gene-models-and-open-reading-frames` is not renamed, so the `owner.anchor` fields in
  `systems/graph/instruments.json` are unaffected; `systems_check` reports no link or anchor error on
  any changed file.

## Checks actually run, once, with exit codes

| check | exit | result |
|---|---|---|
| `lint_style.py` on the three changed/added manuscript files | 0 for manuscript and QA note | The cover letter's two `second-person` errors (`you`, `Yours`) are PRE-EXISTING and reproduce identically on the retained baseline copy. |
| `lint_consistency.py` (repo) | 0 | `0 ERROR across 29 target file(s)` |
| `lint_claims.py` on the three files | 0 | 1 pre-existing WARN on an author-block line, unrelated to this integration |
| `lint_submission_residue.py --report` | 0 | `5 finding(s) ... 5 baselined, 0 NEW` |
| `lint_asymmetry.py --report` | 0 | `0 new symmetric restatements` |
| `lint_citations.py` | **1** | PRE-EXISTING repo-wide failure: type claims disagreeing with PubMed and NOT-SWEPT identifiers in campaign report files. Not introduced here and not repaired here. **Not all gates are green.** |
| `systems_check.py` | **1** | `907 ERROR` before and after the tracked changes — an identical count. Two D11 frontmatter-enum errors on the new QA note were introduced and fixed (`kind: memo`, `audience: external reviewers`). The pre-existing D6 duplicate-id errors on `DOC-EMC-ATR-COLLABORATOR-PACKAGE` come from retained lane copies and were not touched. |

`scripts/preflight.sh` was NOT run and no full preflight replay was performed. No science was
recomputed: no producer, figure generator or sweep was executed.

**A disclosure about one command.** `python3 research/manuscripts/submission_metrics.py --help` was
invoked expecting usage text. The script does not implement `--help`; it ran and rewrote
`research/manuscripts/submission-metrics.json`. That file is an authorized derived metric for this
integration and its update is legitimate, but the invocation was not deliberate and is recorded as it
happened.

## Measured consequence, and one thing now blocked

`submission_metrics.py` measures the new revision at main 6,298 w, abstract **341 w**, 1 figure, 5
tables, 6 display items, 10 references, against the committed baseline's 3,153 w / 238 w / 0 / 7 / 7 /
8. The recorded venue is *Genes, Chromosomes and Cancer*, whose abstract limit as recorded is 250
words, so `over_limit` now carries `abstract_words 341 > 250`.

**BLOCKER — ATR abstract length.** Paper: `research/manuscripts/dependency/emc-atr-collaborator-package.md`.
Measured evidence: `submission-metrics.json`, `abstract_words 341`, limit 250, provenance
"search-derived; onlinelibrary.wiley.com serves a bot challenge to CI and to a real headless browser
alike". Cutting 91 words from an abstract is a substantive scientific-writing change and is NOT among
the seven authorized corrections, so it was not attempted. **Exact reopening condition:** an
authorization to rewrite the abstract of this manuscript to at most 250 words, or a coordinator
decision that the recorded 250-word limit does not bind this submission. Nothing else about the
manuscript is blocked by this, and integration stands.
