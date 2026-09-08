# X1 — ISOLATED PROPOSALS: cover-letter edits and directly dependent title references

**PROPOSED. NOTHING APPLIED.** No shared repository path was written, no view was regenerated, and
no title was changed anywhere outside this lane. These are proposals for the coordinator.

Source read read-only: `research/manuscripts/dependency/emc-atr-collaborator-package-cover-letter.md`
(HEAD 90d60d917b6f985a9c9f44cb3c6c545d91bb32d8).

## 1 · Cover-letter FACTUAL edits (independent of the title decision)

| # | current text (verbatim) | proposed | why |
|---|---|---|---|
| C1 | "Retained EWSR1 RG dipeptide counts place the two commonest EMC fusions at 0 of 30 and 8 of 30, bracketing the two fusions in which the mechanism has been measured" | "Retained EWSR1 RG dipeptide counts place EMC's type 1 fusion at 8 of 30 and its type 2 fusion at 0 of 30. Type 1 is the commonest EWSR1::NR4A3 type in both series that typed EWSR1 subtypes; type 2 is counted once in those series, so the pair is not 'the two commonest'. The three reported EWSR1::ATF1 breakpoints span 0.000 to 0.267 of retained RG; recruitment was measured on a construct whose breakpoint the source does not state, so that span describes reported breakpoints and not a measured range, and 'bracketing' overstates it." | three separate factual errors: the frequency claim, the word "bracketing" (§3.4 of the revision removes it), and the attribution of the span to measured fusions |
| C2 | "the type-2 junction carries 176 nucleotides of *NR4A3* 5' untranslated sequence in the EWSR1 reading frame, encoding 59 residues" | "the type-2 junction places 177 nucleotides in the EWSR1 reading frame between the two moieties — one donated by EWSR1 across the seam and 176 supplied by NR4A3 — encoding 59 residues" | 176 is not a multiple of three; 177 is, and 177/3 = 59. Both numbers are true and they are different quantities |
| C3 | "that the protein-level model in general use does not contain" | "that this programme's own earlier protein-level model did not contain" | no source retrieved states what protein-level model the field uses; the claim about "general use" is unsupported |
| C4 | "I am the sole author, an unaffiliated independent researcher with no institutional address; no ORCID accompanies this submission." | "I am the sole author, an unaffiliated independent researcher with no institutional address. My ORCID iD is 0000-0002-1823-1451." | the repository carries the author's ORCID (ASO author block; 2026-08-20 submission-plan record). Read from the repository; no external lookup |

## 2 · Cover-letter TITLE edits (apply only if the proposed title is adopted)

| # | location | current | proposed |
|---|---|---|---|
| T1 | frontmatter `title:` | "Cover letter — transcript-level NR4A3 fusion models and pre-specified DSB-recruitment predictions" | "Cover letter — reading-frame constraints and retained RG content in NR4A3 fusion models of EMC" |
| T2 | body, `**Re:**` line | *"Transcript-level models of the NR4A3 fusions of extraskeletal myxoid chondrosarcoma, and five pre-specified predictions for a DNA double-strand break recruitment assay"* | *"Reading-frame constraints and retained RG content in NR4A3 fusion models of extraskeletal myxoid chondrosarcoma"* |

## 3 · Directly dependent title references — LOCATED, NOT CHANGED

Found by a read-only grep for the current title string. Only files that quote the title itself are
listed; historical records are listed as do-not-edit.

| file:line | what it is | disposition |
|---|---|---|
| `systems/views/L3-publications.md:42, :121` | GENERATED view; `systems_check.py` reads the manuscript frontmatter `title` | regenerate with `python3 systems/systems_check.py --write-views` AFTER the title is adopted. **Coordinator's step. Not run here** |
| `systems/views/L2-rt-atr-panel.md:92` | GENERATED view, same mechanism | same |
| `research/manuscripts/dependency/emc-atr-collaborator-package-cover-letter.md:35` | live submission document | T2 above |
| `research/manuscripts/dependency/emc-atr-collaborator-package-changelog.md` | history | ⛔ do not edit; it records superseded titles by design |
| `research/manuscripts/dependency/emc-atr-collaborator-package-peer-review-2026-08-10.md` | dated review record | ⛔ do not edit |
| `research/autonomy/.../paper-lane/*` | this campaign's own lane records | ⛔ do not edit |

⚠ `systems/graph/instruments.json` (`INS-CONSTRUCT-DESIGNS`, `INS-FUSION-COFOLD`) carries
`owner.anchor` fields, not the title. The proposed revision does not rename
`#32-gene-models-and-open-reading-frames`, so those anchors are unaffected by the title change.
They were NOT re-verified here.

⛔ No shared title or view change was made. No `systems_check.py` run, no view regeneration.
