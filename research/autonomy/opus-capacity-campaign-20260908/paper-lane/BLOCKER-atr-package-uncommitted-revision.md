# Blocker — ATR collaborator package: the committed manuscript is the PRE-REVISION draft

Recorded 2026-09-08 ~11:24 UTC. Found by the read-only P2 lane and **verified independently by the
parent**. This is the largest version divergence the campaign has found.

## 1 · Paper and item

`research/manuscripts/dependency/emc-atr-collaborator-package.md`. Its 2026-08-10 review response
records **41 of 47 revision items applied in full**. **None of the 41 is present.**

## 2 · Evidence — parent-measured, not inherited

**Structural, and decisive on its own:**

| the response says | the committed file has |
|---|---|
| retitled to *"Untranslated NR4A3 sequence encodes a 59-residue insertion…"* | the old title, *"Transcript-level models of the NR4A3 fusions…"* (line 3) |
| one figure inserted | **0** references to Figure 1 — although `emc-fusion-frame-fig1.png` and `.pdf` **are committed** |
| Appendix A deleted, content moved to the changelog | `## Appendix A` **still present** |
| seven tables reduced to six plus a figure | seven tables, no figure |

**Sentence-level: every string the review targeted is still there**, each verified by me —
"the two commonest EMC fusions" (1), "interpolate between points already measured" (1),
"byte-identical" (2), "the protein-level model in general use" (2), "cut section 5 first" (1),
"ORCID TO BE SUPPLIED" (1). The arithmetic correction is absent: **"176 nucleotides" appears twice and
"177" zero times.**

**Side-products of the revision WERE committed** — the changelog, the `emc_fet_frame_and_composition`
module, its artifact, and the figure files. **Only the manuscript and cover-letter edits are missing.**

## 3 · Exact reopening condition

**An owner decision on which draft is canonical**, then one coherent action:

- **(a)** the revision exists elsewhere -> commit it as a whole; or
- **(b)** the revision is lost -> re-apply it deliberately as one revision, against the response and
  review as the specification, **not** as 41 separate patches.

⛔ **This is not patchable item-by-item, and no worker should be pointed at it as such.** Forty-one
items spanning title, structure, tables, figure, predictions and front matter are a **version
decision**, not a defect queue.

⛔ **No external draft identity is assumed.** P2 offered a lost-or-unstaged hypothesis and explicitly
labelled it a hypothesis, noting git history for these paths is squashed. **We do not claim to know
where the revision is, or that it exists.**

## 4 · A consequence that needs the owner's eye

The changelog registers the **176-nt sentence as superseded**, while the live manuscript carries it
**twice**. Under the repository's own rule that live text carries only the current value, **the
changelog and the manuscript now disagree about which number is current.** Recorded, not resolved —
resolving it means choosing (a) or (b) above.

## 5 · Two corrections, one to P2 and one to me

**⭐ P2's "broken pin" finding is FALSE, and I checked before repeating it.** P2 reported that
`test_emc_fet_frame_and_composition.py::test_the_extension_spans_a_whole_number_of_codons` "does not
exist anywhere in the tree". **It exists**:
`research/modalities/tests/test_emc_fet_frame_and_composition.py`, 5,157 B, with the named test at
**line 32** among 9 tests. P2's search was mis-scoped. **The arithmetic pin is intact**, and the
"nothing prevents the 176/177 error recurring" inference does not follow.

**⭐ My own spot-check was wrong, and P2 was right to flag it.** I earlier judged the response's
"frame rule" claim "present in substance under different wording" in this manuscript. It is **not
present in any wording** — `grep` for "phase 1", "frame rule", "174 nt" and "174 nucleotides" over the
manuscript returns **nothing**. The rule lives in `emc-fet-frame-and-composition.json` and the
changelog; I must have read one of those. **That spot-check is withdrawn**, and it is the reason I
concluded earlier that "ATR is well-closed" — a conclusion now overturned by evidence.

## 6 · Consequence for work selection

ATR is **set down at this blocker**, not queued for edits. Two of the campaign's four remaining
candidate papers are now blocked on the **same question in different degrees** — repurposing (four
divergences, one unapplyable) and ATR (a whole unapplied revision). **The canonical-draft question is
the campaign's dominant cross-paper dependency**, and it is an owner decision, not a worker task.
