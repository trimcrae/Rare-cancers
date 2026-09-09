---
id: DOC-OPUS-CAMPAIGN-REPURPOSING-4-FINDING
title: "REPURPOSING-4 — the pending REPURPOSING diff chain fails on a malformed header, not on staleness"
level: L4
kind: record
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# REPURPOSING-4 — rebasing the REPURPOSING diff chain

## 1 · Question

The four unapplied REPURPOSING diffs all return `git apply --check` exit 1 at HEAD. **Why** does each
one fail, per hunk, and what is the one coherent, currently-applicable diff set that carries their
substance forward unchanged?

## 2 · Merit and the evidence gap

Merit is integration merit, not new science: REPURPOSING-2's cited-reference sweep and REPURPOSING-3's
five-abstract-level reading are already adjudicated evidence about
`research/manuscripts/repurposing/repurposing-hypotheses.md`. If the chain cannot be applied, that
evidence is lost at integration time. The gap the ledger recorded was "the tree has moved past the
rebased form." **That diagnosis was wrong**, and finding out why was the whole task.

### The real cause — measured, not assumed

All four diffs were produced with `diff -u <real file> <scratchpad AFTER file>`, so each carries:

```
--- research/manuscripts/repurposing/repurposing-hypotheses.md	2026-09-08 18:32:26 +0000
+++ /tmp/claude-0/.../scratchpad/rep2/AFTER.md	2026-09-09 00:14:04 +0000
```

`git apply` prefers the `+++` path, strips one component under the default `-p1`, and looks for
`tmp/claude-0/.../AFTER.md`. That file does not exist in the worktree. Every one of the four fails
identically, **before a single hunk is examined**:

```
error: tmp/claude-0/.../AFTER.md: No such file or directory
```

Measured: `checks/01`–`checks/04`, all exit **1**, all with that same stderr. **No hunk in any of the
four was ever tested against the tree.** The exit-1 reported in the pending-diff ledger is real, but
it is a patch-header defect, not an anchor drift, and it has nothing to do with the tree moving. This
is the same class of failure as HLA-COVERAGE-2's exit 128 — a hand-assembled patch envelope.

### Per-hunk diagnosis, after correcting only the two header lines

Rewriting line 1 to `--- a/<repo path>` and line 2 to `+++ b/<repo path>`, changing **no hunk and no
content byte**, and re-checking against the current tree (`checks/05`–`checks/08`):

| diff | hunks | `git apply --check` | per-hunk diagnosis |
|---|---|---|---|
| REPURPOSING-2 `cited-reference-sweep` | 7 | **0** (`checks/05`) | All 7 apply. No moved anchor, no conflict, nothing already applied. |
| REPURPOSING-3 `five-unread-references` | 6 | **0** (`checks/06`) | All 6 apply against the bare tree. |
| REPURPOSING-3 `zaltoprofen-…-ADDS-REFERENCE` | 4 | **0** (`checks/07`) | All 4 apply against the bare tree. |
| REPURPOSING-3 `rebased-onto-REPURPOSING-2` | 8 | **1** (`checks/08`) | **Genuine, and by design.** Enumerated with `git apply --reject` (`checks/18`): hunks **1, 7, 8 apply cleanly** (7 and 8 at offset −39); hunks **2, 3, 4, 5, 6 are rejected**. Their context contains REPURPOSING-2's *added* sentences — e.g. "Those trial figures are taken from the 2025 comprehensive review and from this project's registry record of that trial; the trial report itself was not retrieved for this manuscript." That text is **absent from the bare tree** because the sweep is not applied. This is a **base mismatch, not a conflict**: the diff's base is the post-sweep file, exactly as REPURPOSING-3 documented. |

So: **three of the four are content-clean against today's tree**, and the fourth fails only because
its declared base is a file the tree does not yet contain. Nothing here is stale.

## 3 · Step taken

Rebuilt the chain against the current tree and **generated every output patch programmatically** with
`difflib.unified_diff` (`gendiff.py`, `n=3`, explicit `a/`+`b/` file labels) from three real files —
BASE (the tree copy), MID (BASE + sweep), FINAL (MID + rebased). No patch text was hand-written or
hand-edited.

## 4 · Artifact

In `REPURPOSING-4/`:

* `REBASED-COMBINED-single-patch.diff` — 10 hunks, **+65 −20**. The whole set as one patch.
* `REBASED-01-cited-reference-sweep.diff` — 7 hunks, +29 −11.
* `REBASED-02-five-unread-references-and-zaltoprofen.diff` — 8 hunks, +38 −11.
* `APPLY-ORDER.md` — the explicit order, and which check result is expected to be non-zero and why.

`REBASED-02` is REPURPOSING-3's whole contribution: the five-reference reading **and** the
zaltoprofen parent-histology reference, merged. The two separately-authored REPURPOSING-3 diffs are
not both carried as separate patches because their table rows collide; §6 shows nothing was dropped.

## 5 · Validation — every exit code real, no pipes

| check | command | exit |
|---|---|---|
| `01`–`04` | `git apply --check -v` on the four original diffs | **1, 1, 1, 1** |
| `05`–`07` | `git apply --check -v`, header-corrected, sweep / five-unread / zaltoprofen | **0, 0, 0** |
| `08` | `git apply --check -v`, header-corrected `rebased-onto-REPURPOSING-2` | **1** (expected — base mismatch) |
| `09`,`10` | cumulative apply on a scratch copy: sweep, then rebased | **0, 0** |
| `11` | every added non-blank line of the two superseded REPURPOSING-3 diffs, searched in the result | **0** (26/26 and 10/12; see §6) |
| `12` | `git apply --check` in tree, `REBASED-01` | **0** |
| `13` | `git apply --check` in tree, `REBASED-02` | **1** — *expected*, its base is post-`01` |
| `14` | `git apply --check` in tree, `REBASED-COMBINED` | **0** |
| `15`,`16` | real cumulative `git apply` on a scratch copy **outside the repo**: `01` then `02` | **0, 0** |
| `17` | real `git apply` of `REBASED-COMBINED` on a second fresh scratch copy | **0** |
| — | `cmp` two-step result vs combined result vs FINAL | **0** — byte-identical |

The `git apply --check`-is-not-cumulative caveat is why `13` is 1 and why `15`/`16`/`17` exist:
`--check` tests each patch against the tree, so the two-step route can only be proven by really
applying it, which was done on a copy outside the repository.

## 6 · Substance preserved — verified line by line

`checks/11` searched the cumulative result for every added non-blank line of the two superseded
REPURPOSING-3 diffs.

* `five-unread-references`: **26 of 26 added lines present verbatim.**
* `zaltoprofen-…-ADDS-REFERENCE`: 10 of 12 present verbatim. The **2 absent lines are two table rows
  that REPURPOSING-2's sweep also rewrote**; REPURPOSING-3's own rebased form merged them. Both merged
  rows still carry the reference: §3.1 reads "zaltoprofen itself is not clinically untried in the
  parent histology **[23]**", §3.2 reads "zaltoprofen itself has been given to one chondrosarcoma
  patient **[23]**". Reference 23 (Higuchi 2018, *Cancer Med*, PMID 29573200, PMC5943440) is present
  in §9. **Nothing was dropped; two rows were merged rather than duplicated.**

Each of the four items the task required to survive, located in the applied result:

1. **Abstract-level-only reading of [2], [8], [9], [12], [14]** — present: "References 2, 8, 9, 12 and
   14 are also abstract-level only, as checked against PubMed on 2026-09-09", with the reason stated
   (no PMC record via the PubMed-to-PMC link database; reference 12's PMC10054153 "returns an abstract
   and an empty full text"). Every absence in that passage is written **"not in the abstract"**;
   `grep -c "not in the abstract"` = 1 in the new passage and `grep "not in the paper"` returns
   **nothing** in the whole file.
2. **Huang 2023 chemotherapy finding** — present: "chemotherapy was one of the factors that portended
   shorter univariate disease-specific survival", immediately qualified "the association of this shape
   is **confounded by indication**, because chemotherapy is given to the …". Not written as evidence
   of harm.
3. **The CD117 threshold distinction** — present and intact: "approximately 53% in one series and
   approximately 84% of 31 cases in another [2,8]. Those two figures are not measured to the same
   threshold and should not be read as a single range: the first counts **moderate-to-strong
   immunoreactivity among 48 assessed cases** [2], the second counts positivity that its authors
   define as **focal or diffuse** [8]."
4. **The zaltoprofen parent-histology caveat** — present: the [23] patient is a **grade 2 cervical
   chondrosarcoma**, "no … therapeutic-window conclusion is drawn from it in either histology", and
   the manuscript still reads the candidate as untried **in EMC** while not clinically untried in the
   parent histology.

## 7 · Provenance

* Baseline: worktree at `673d33044`; the target manuscript is unmodified in `git status`.
* Inputs: the four existing diffs, unchanged on disk. Only their two header lines were rewritten, into
  scratch copies outside the repo (`h1`–`h4`), to make the envelope resolvable.
* Generation: `difflib.unified_diff` over BASE/MID/FINAL. No hand-written patch text.
* No source retrieval, no PubMed/PMC call, no network. This was a rebase, not a re-adjudication: no
  claim, reference or number was added, removed or reworded by this lane.

## 8 · Limitations

* The set is **not applied**. `git add`/`commit`/`push` and `scripts/preflight.sh` were not run.
* Whether the substance *should* go into the manuscript is REPURPOSING-2's and REPURPOSING-3's
  adjudication, untouched here. This lane certifies applicability and substance-preservation only.
* Not re-verified here: the citation gate, link and reference-numbering checks that the manuscript's
  own gates run at commit time. The set adds reference 23 and edits §9; a gate run belongs to whoever
  applies it.
* The set is valid **against `673d33044`**. Any later commit touching this manuscript invalidates it,
  and the same rebase must be redone — this time it will fail for a real reason.
* No clinical efficacy, safety, selectivity or therapeutic-window claim is made or implied by this
  lane. The candidates remain preclinical and untried in EMC.

## 9 · Stop condition

Reached. The set checks 0 in the tree as one patch, applies cumulatively to exit 0 on a scratch copy
outside the repo by either route, and both routes produce a byte-identical file whose substance was
verified line by line. The remaining decision — apply or not — is the parent's.
