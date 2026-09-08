# F1 — paper-level contract, recorded BEFORE launch

`date -u` **Tue Sep  8 08:49:35 UTC 2026**. HEAD **572287f4c96717eef499a360314eff4e47919339**. Same session, sole parent, `claude-opus-5` medium, saved
subscription, no overage, deadline 2026-09-09T02:37:19Z. Disk 20 GiB free (floor 10 GiB).

## Selected paper

- **Path:** `research/manuscripts/mtap-prmt5/emc-mtap-prmt5-hypothesis.md` (8,041 words whole-file;
  `submission_metrics.py` grades it GCC-Research-Article, main 5,276 w, abs 249 w, 11 refs, within
  believed limits), endpoint `PUB-MTAP-PRMT5`, state `drafted`, unpublished.
- Selected because it is a drafted-but-unpublished manuscript carrying a **self-declared open caveat**
  that a committed repository record already answers. Per the standing correction, "already drafted"
  is not an exclusion.

## The exact unfinished substantive issue — parent-verified in the committed tree, not inherited

The manuscript states, in its limitations:

> "The original source of the fusion rationale is a preprint whose own pages state that it is not
> certified by peer review [2]. **Its status since 2022 was not established here**, and that caveat
> travels with every use of it."

and its reference note says reference 2 "carries its identifier and posting date alone and must be
completed from the source record before submission."

**Measured by me:** `research/literature/prmt5-ccs-preprint-publication-status-2026-08-10.json` is
committed and answers precisely that question — `"_answer": "YES — a peer-reviewed version exists."`
— giving Li BX, David LL, Davis LE, Xiao X., *Journal of Biological Chemistry* 2022;298(10):102434,
doi 10.1016/j.jbc.2022.102434, PMC9513783. That record's own `_what` field states it was created
*because* of this caveat: "a caveat about not having looked is not a caveat a referee accepts."
`grep -c -i 'jbc|102434|Journal of Biological Chemistry|PMC9513783|peer-reviewed version'` over the
manuscript returns **1**, and that single hit is reference 10 (a different JBC paper, 2001).

⭐ **So the manuscript still tells a referee that the peer-review status of its founding source was
never established, while the repository has held the answer since 2026-08-10.** This is claim
hardening on a caveat the paper itself flags — not a new result, and no new scientific claim.

## ⛔ The verification level is part of the correction, not a footnote to it

The record is explicitly **`[SE] SEARCH-INDEX ONLY`**: the publisher page, the PMC record, the
bioRxiv page and the institutional repository **all returned EGRESS_BLOCKED**. The title, authors,
volume, issue, article number, DOI and PMCID are **as returned by a search index, repeated
consistently across three queries, and NOT read off the publisher's own record.** What is established
at that level is **the fact that a peer-reviewed version exists** — the bibliographic detail is not.
The record further warns that **the findings the manuscript quotes were read from the preprint, not
from the published version.**

## Finite acceptance

1. Replace the "status since 2022 was not established here" caveat **in place, where it lives**, with
   what the repository actually establishes. Do not append an end-note.
2. **Carry the verification level with the claim.** The existence of a peer-reviewed version is
   established; the bibliographic detail is search-index-level and must be labelled as needing
   confirmation against the publisher record before submission. Do not silently promote it to a
   verified citation.
3. **Attributions do not move.** Every finding currently attributed to the preprint was read from the
   preprint; it stays attributed to the text actually read. Do not restate preprint-read results as
   though read from the JBC version.
4. **No overclaim in either direction.** A peer-reviewed version existing does not make the
   fusion-class transfer to EWSR1::NR4A3 any stronger — the manuscript's existing statements that
   EWSR1::ATF1 and EWSR1::NR4A3 share no DNA-binding domain, target repertoire or disease biology, and
   that no result presented is an observation in EMC, are **hedges that must survive intact**.
5. Update reference 2 and the reference-completion note consistently with 2 and 3.
6. Word count stays within the venue cap and **no hedge is deleted to make room**.
7. Applicable manuscript linters run and reported honestly with exit codes. ⛔ **If this trips a gate,
   that is a finding to report — never a reason to weaken, relax, reorder or edit the gate.**
   `lint_citations` is already failing repo-wide at exit 1 for unrelated reasons; establish a
   stashed baseline and compare, rather than attributing it to this edit.

## Named-hold non-overlap — checked, not assumed

**No network call of any kind.** The four routes in that record are EGRESS_BLOCKED and are **not to be
retried, reworded or rerouted**, and no paid access, credential or alternative network path may be
used — the record is already committed and is the only input needed. Not C1 (closed), not D1–D3 (not
reopened), not the mortality-mechanisms draft, not the repurposing paper (E1, collected). Not W25 /
GSE243553 / primary-article / Results / novelty — the blocked writer is **not** woken. Not the NR4A
Perspective, not the P6 successor. Not the frozen submitted comment, ASO or RNA assets. Not the parked
synthetic figure-validation family, S1/S3, or P1–P6 dispositions.

## Stop conditions

Stop if the caveat text does not read as quoted; if the record does not say what is quoted above; if
the correction cannot be made within the word cap without deleting a hedge; if any change would
require a network call, a new source, or a guard change; or at ~40 tool calls / ~40 minutes. Edits are
confined to `research/manuscripts/mtap-prmt5/emc-mtap-prmt5-hypothesis.md`. **No PR, no publication,
no graph edit, no other manuscript.**

## Git and retention

**No git write operation of any kind — no `stash`, no `checkout`, no `commit`. The parent
integrates and commits.** (This is stated explicitly because E1 ran `git stash`/`pop` and a
`git checkout` under the same instruction phrased less bluntly.) For the `lint_citations` baseline,
obtain it **without touching the index**: copy the manuscript aside, restore the pre-edit bytes from
your own saved copy, run the linter, then restore your post-edit copy — all by `cp`, never by git.
Retain, before any cleanup: pre-edit manuscript, post-edit manuscript, unified diff, and all linter
stdout/stderr with exit codes, under `/tmp/claude-0/f1-retained/`. The parent will preserve the
original child JSONL and tool bodies with hashes. **Nothing is re-run to recreate evidence.**
