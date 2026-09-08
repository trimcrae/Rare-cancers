# COLLECTION Z1 — AND-gate degrader paper, quantity provenance

Collected 2026-09-08 by the campaign parent. Contract:
[`CONTRACT-Z1-andgate-quantity-provenance.md`](./CONTRACT-Z1-andgate-quantity-provenance.md).
Paper: `research/manuscripts/degrader/fusion-selective-andgate-degrader-paper.md` (PUB-ANDGATE).

## Execution, from the original transcript

Retained at `Z1-executed-artifacts/ORIGINAL-CHILD-TRANSCRIPT-a23107451c4c3b04f.jsonl`, copied and
`cmp`-verified identical to the original, 302,734 B, sha256
`5e3ecc4e5430cc6093b60ff312e676333ba921d7ea34b934de354387ca0b2f6a`.

| observed from the transcript | value |
|---|---|
| model, every entry | `claude-opus-5` (51 of 51) |
| tool_use / tool_result | 26 / 26, fully paired |
| span | 2026-09-08T12:40:45.433Z to 12:46:10.189Z |

Z1's report states 16 tool calls. The transcript records **26** tool_use blocks. The observed count
governs; the self-report is noted as inaccurate, not adopted. The stop condition was met on its first
branch either way.

Z1 was read-only and created no scratch directory, so the transcript and the parent's own
before/after copies are the whole of its evidence. It made no repository write and no git write.

## Verdict on the work

Z1 gave firm verdicts on **44 numeric quantities**: 38 MATCH, 2 MISMATCH, 2 NO SOURCE LOCATED, plus
two flagged non-numeric defects. The parent independently re-derived every claim it acted on, from
the artifacts directly:

| Z1 claim | parent's independent check | outcome |
|---|---|---|
| `nr4a-selectivity.json` holds no facing data | its top-level keys are exactly `_note`, `paralogues`, `nr4a3_lbd_pockets`; a grep for facing fields returns nothing | **CONFIRMED** |
| the program map calls "5 stay pocket-facing" neither confirmed nor committed | `nr4a3-program-map.md:2943` says exactly that | **CONFIRMED** |
| linker-EM windows run 9.9 to 11.0, so "~10-11×" excludes its own minimum | `fusion-andgate-linker-em.json`, `by_linker[*].fusion_vs_wildtype_window` = 11.0, 11.0, 11.0, 10.9, 10.9, 10.8, 10.6, 10.4, 9.9 | **CONFIRMED** |
| the 30 nm EM leaf is 9.43e-3, not ~9e-3 | `by_linker[8].effective_molarity_M` = 0.009430273502114964 | **CONFIRMED** |
| the ~0.76 kcal/mol "provisional pending the unbiased release run" label is stale | `nr4a3-degrader-paper.md:2659-2662` records the release run done and that reading **not supported** by the independent profiles (16.0 / 0.06 / 0.83 kcal/mol), Gate 3B unresolved | **CONFIRMED** |
| the YAML `title:` is truncated mid-word | line 3 ended `...EWSR1::NR4A3 extraskeleta`; the H1 at line 15 carries the full title | **CONFIRMED** |

## Applied, under ordinary manuscript-advancement scope

Six single-occurrence replacements, before/after/diff retained in `Z1-executed-artifacts/`:

1. **Frontmatter title** completed to match the H1 exactly.
2. **The 0.76 kcal/mol clause** no longer says "provisional pending the unbiased release run". It now
   records that the run was performed and that the reading is not supported by the independent
   replicas, with their three values and Gate 3B unresolved. The value itself is unchanged and still
   attributed to an incompletely-converged biased profile.
3. **The 30 nm EM** reads ~9.4e-3 M.
4. **The window range** reads 9.9 to 11.0× rather than ~10-11×, so it no longer excludes its own
   measured minimum. The 10.8× and 9.9× anchors are unchanged.
5. **The facing count** is no longer asserted as fact and no longer attributed to
   `nr4a-selectivity.json`. It is marked REPORTED BUT NOT CONFIRMED, with the real owner named as
   uncommitted and the superseded tracker noted. The 7 divergent Pocket-5 residues, which the artifact
   does hold, are unchanged.
6. **Both "engageable" parentheticals** now say they inherit that unconfirmed facing set, while the
   7-of-7 and 6-of-7 divergence counts, which the artifact supports, explicitly do not.

No artifact, producer, preregistration or figure was touched. No model was re-run. No number was
invented; every retained value already appeared in the manuscript or the artifact.

## Recorded, not applied

- **"~100% identity over the LBD" (line 96)** — NO SOURCE LOCATED. Z1 searched
  `research/modalities/*.json` and the degrader manuscripts and found only prose restatements. Absence
  of a located source is **not** evidence the claim is false, and it is a fusion-architecture
  statement rather than a computed result. Z1 declined to propose wording and the parent agrees. Left
  as it stands.
- **Line 130's "wild-type NR4A3 has no EWS LC domain"** — literally true as written, but sits under a
  bullet the paper's own 2026-07-13 erratum exists to correct. Outside a quantity contract, and a
  judgement about the erratum's scope. Left as it stands.
- **Link display text** says `../modalities/...` while the targets say `../../modalities/...`. The
  targets resolve; the display text does not match them. Cosmetic, no quantity involved. Left as it
  stands.

## Gate state

`lint_claims` clean on the paper. `lint_consistency` 0 ERROR across 29 files.

`lint_style` on this paper: **72 ERROR before, 71 after**. It was never taken through a style pass and
the errors are overwhelmingly `bold-midsentence` and density limits across the whole document. The
parent's first pass added two `bold-midsentence` errors of its own; those were removed, and the net
change is one fewer error than before. **A whole-paper style pass was not attempted and this paper
does not pass `lint_style`.**

## Scope

This outcome is specific to this paper. It is not a statement that the backlog is exhausted, and Z1's
own coverage is manuscript-versus-artifact provenance only: it did not verify that the committed JSON
matches what the producers would emit today, and it did not audit the external references. Its
suggested successor task — re-running the three AND-gate CPU models into a scratch path and diffing
against the committed artifacts — is recorded here as a candidate, not opened.

---

## Dated append — 2026-09-08, two corrections to this record

Nothing above is rewritten, and Z1's original report is preserved verbatim inside its retained
transcript (23,502 B, sha256
`24c4ce503fc6d65144216d1f6233bf3f2461a00d59f067d36bcd6481265e7da8`).

### 1 · My verdict tally was wrong

I wrote "38 MATCH, 2 MISMATCH, 2 NO SOURCE LOCATED". That is **42**, not 44, and it is not what Z1's
table says. Read off the original table's own labels, the correct summary is:

| verdict | rows |
|---|---|
| MATCH | **40** |
| MISMATCH | **1** — row 23, the linker-EM window range |
| MIXED | **1** — row 39: the 0.76 kcal/mol **value** MATCHes; its **status label** was stale, and that half is the MISMATCH |
| NO SOURCE LOCATED | **2** — rows 41 and 44 |
| **total numeric rows** | **44** |

Plus **two non-numeric defects** Z1 flagged separately: the truncated frontmatter title, and the
sentence adjacent to the paper's own erratum. Those sit outside the 44 and are not part of the tally.

My error was collapsing row 39's two halves into one MISMATCH and then losing two rows in the
arithmetic. The corrected summary above governs; the earlier one does not.

### 2 · Two of the six fixes are precision refinements, not newly discovered false numbers

The record above described the window range as one that "excludes its own measured minimum". Both
halves of that are wrong and are withdrawn:

- **The approximation marker matters.** "~10-11×" and "~9×10⁻³ M" carry a tilde. An approximation is
  not made false by a nearby value it rounds; "~10-11×" does not exclude 9.9, and "~9×10⁻³" does not
  misstate 9.43×10⁻³. Neither was a false numeric claim. The precise wording is better and is kept,
  but the rationale is **precision refinement**, not the discovery of a numeric error.
- **"Measured" is the wrong word.** 9.9 and 9.43×10⁻³ are **computed outputs of a committed CPU
  artifact** over illustrative assumed inputs. They are not measured biological minima, and nothing
  here establishes the artifact's source validity or that its producer would emit the same values
  today.

The other four fixes are not in this category and stand as recorded: the truncated title, the stale
"provisional pending the unbiased release run" status label, the facing count asserted as fact and
attributed to a file holding no facing data, and the inherited "engageable" parentheticals. Those are
attribution and status defects, not rounding.

### 3 · Two housekeeping notes

Z1's proposed re-run of the three AND-gate CPU models against their committed artifacts remains a
**proposed next step only**. It is not opened, and no producer replay, audit or science run was
performed for this correction.

The views that carry the AND-gate title were synchronised at commit `4992bca5` after Z1's completed
frontmatter title, through the ordinary view workflow. `L3-publications.md` and `L2-rt-andgate.md`
changed in that string alone and the diff was inspected.

### 4 · Parent-side execution evidence, retained

`Z1-executed-artifacts/` originally held the child JSONL, before/after copies, the applied diff and
the style outputs — the child's evidence, not the parent's. The parent's own re-derivations, mutation
commands, gate invocations and their stdout for both the Z1 and the AB1 collections existed only in
the parent session transcript, because they were shell heredocs and unredirected output.

`EXTRACTED-FROM-PARENT-TRANSCRIPT-z1-and-ab1-parent-execution.txt` retains **29 Bash calls**
verbatim, bounded to timestamps at or after 2026-09-08T12:46:00. It is an extraction from a parent
transcript, labelled as such in its own header, and **not** a complete parent execution transcript.
Exit codes are partial, exactly as for the X1 integration set. Nothing was re-run and no absent
original was recreated.
