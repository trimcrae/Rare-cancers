---
id: DOC-OPUS-CAMPAIGN-TXN-DEPENDENCY-2
title: "TXN-DEPENDENCY-2 — three of ten fixed identities are stale, and only two of the three were forecast"
level: L4
kind: investigation
status: proposal-unapplied
date: 2026-09-09
last_verified: 2026-09-09
head_measured_at: b14a84259363f8b18c98d7754a305892cd37f92b
---

# TXN-DEPENDENCY-2 — provenance repair proposal for §8 "Fixed identities"

## Question

After commit `6466168d7` (TD1 R1–R4 integration), do the ten Git blob identities in §8 of
`research/manuscripts/dependency/emc-transcriptional-proteostatic-dependency.md` still resolve to the
current tree; which drifts does §8's own forecast cover; and is updating the table the honest
disposition at all?

## Merit

§8's identity table is the paper's only path-independent handle on the objects it was read against.
A reader who resolves those ten ids is doing the one check that survives a mutable path. If the table
silently tracks the tree, that check degrades from "this is what the paper read" to "this is whatever
is there now", and a reader can no longer tell a forecast annotation-only correction from an
unannounced change to a producer. This is provenance integrity for a manuscript already accepted by
its owner, not a scientific claim; ⛔ nothing here touches EMC efficacy, safety, selectivity,
therapeutic window or clinical readiness.

## Evidence gap addressed

Whether the drift is (a) exactly the two objects §8 forecast, or (b) wider — and specifically whether
the **producer script** drift is covered by any sentence in the manuscript.

## Step taken and result

### 1 · All ten identities re-derived (`checks/01-rederive-ten-identities/`)

Measured at HEAD `b14a84259363f8b18c98d7754a305892cd37f92b` (`b14a84259 Retain the parent
re-execution copies rather than deleting them`), by `git hash-object` against the working tree.
Re-checked unchanged at close of lane (`checks/06-head-recheck-at-close/`).

**Seven MATCH, three DRIFT. No other identity has drifted.**

| object | declared in §8 | current | status |
|---|---|---|---|
| `research/modalities/emc-expression-panels.json` | `330c04cb…` | `330c04cb…` | MATCH |
| `research/modalities/emc_expression_panels.py` | `d260a5d3…` | `d260a5d3…` | MATCH |
| `research/modalities/census-route-expression-grading.json` | `b45a35a4…` | `ee552394935792ed2e76bce926146b77907c5694` | **DRIFT** |
| `research/modalities/census_route_expression_grading.py` | `18625608…` | `fe00fe381957bf248d774d0ed68cbf93c6674487` | **DRIFT** |
| `research/modalities/depmap-sarcoma-dependency.json` | `1f00ad1c…` | `1f00ad1c…` | MATCH |
| `research/modalities/depmap_sarcoma_dependency.py` | `fc0a0cc0…` | `fc0a0cc0…` | MATCH |
| `research/modalities/emc_atr_vulnerability.py` | `177df6cf…` | `177df6cf…` | MATCH |
| `research/modalities/fet-ddr-axis-scan.json` | `41a575d2…` | `41a575d2…` | MATCH |
| `research/literature/txn-dependency-class-definitions-2026-08-09.json` | `a8fa744a…` | `a8fa744a…` | MATCH |
| `research/literature/fet-fusion-chaperone-clientship-2026-08-27.json` | `8728c34d…` | `9328cecebdffdb53921f82805b47fd0943d30c1f` | **DRIFT** |

The parent's three reported drifts are confirmed digit for digit and nothing else moved.
⚠ `checks/01` records **exit 1**: the trailing `read` of the here-doc returns non-zero at EOF. The
per-row output is complete and the code is preserved as it actually occurred, not fabricated or
suppressed.

Per-path blob history (`checks/04-blob-history-of-drifted-three/`): each of the three moved **once**,
at `6466168d7`, from exactly the §8-declared blob. Their previous value at `f22e5bb7e` is the declared
one, so §8 was accurate when written. The abbreviated ids in `6466168d7`'s message
(`7ba3ed7a → ae44e6e0`, `2dbd21cc → cbb9c9ac`, `42ffb5a9 → 43447cd4`) are **not** Git blob ids — they
are that commit's own content digests — and do not indicate a second move.

### 2 · What §8's forecast actually covers

The forecast sentence, quoted exactly:

> ⚠ Two of the objects above — `census-route-expression-grading.json` and
> `fet-fusion-chaperone-clientship-2026-08-27.json` — have a dated annotation-only correction prepared
> but not yet integrated at the time of writing; when it is applied their blob identities change and
> no reported number, membership or quotation does.

It **enumerates two objects by name**. `census_route_expression_grading.py` is not one of them. The
enumeration is closed ("Two of the objects above — X and Y"), so it cannot be read to include the
producer of X by implication.

**No other sentence in the manuscript covers it.** The only other producer-directed language in §8
is the opposite kind of statement — a claim about what was *not* done:

> ⛔ **no producer was re-run to write this version** — the numbers reported are a reading of the
> committed outputs identified above.

and

> ⚠ **The producers were not re-run to write this paper, and that fact is not the method.**

Those license nothing; they assert non-execution. The general annotation-only paragraph
("A dated annotation-only correction to one of these artifacts changes its blob identity while
changing **no** number…") is a *definition* of a category, and its instantiation is the two named
objects. So: **the producer-script drift is genuinely uncovered by §8's forecast.**

### 3 · What the producer-script change actually is (`checks/02-what-changed-in-the-three/`)

`git diff 18625608… fe00fe38…` — 18 insertions, 6 deletions, all inside `build()`, all edits to
literal annotation strings assigned to `route_action`, `observed` and `verdict` for `RT-CHAPERONE`
and the CDK route: "non-selective" withdrawn in favour of "broad binary dependency … selectivity
UNRESOLVED", and the GPL3290 corroboration hold. **No computation, threshold, membership, cohort
rule or numeric literal is touched**, and the JSON diff is the projection of the same strings.

⚠ That makes it annotation-only *in substance* while remaining a **code** change, which is exactly why
the forecast's guarantee — written for data artifacts — does not simply extend to it. The distinction
is not pedantic: for a JSON artifact, "no number changed" is checkable by leaf invariance on the file
itself; for a producer, the same assurance requires either reading the code or re-running it, and
⛔ no producer was re-run here.

### 4 · Disposition — should the table be updated at all?

**Recommendation: NO for the plain overwrite (variant A). Prefer marking the rows superseded
(variant B), and in either case this is the owner's act, not this lane's.**

Argued from what §8 says the table is for:

> Each is the Git blob SHA-1 of **the exact object this paper was read against**, and each is
> verifiable with `git cat-file -p <id>` in this repository without trusting a path.

The table's stated referent is the *read-against* object, not the *current* object. Overwriting a row
with the current tree identity therefore falsifies the sentence that introduces the table: after the
overwrite, `b45a35a4…` — the object actually read — no longer appears anywhere, and the paper asserts
it read something it did not read. It also destroys the property that makes the table useful: an
identity that tracks the tree cannot detect drift, so §8 would stop being a check and become a
restatement. And because Git retains the old blobs, `git cat-file -p b45a35a4…` still succeeds today,
so keeping the read-against ids costs the reader nothing.

The honest disposition is to **record supersession**: keep each read-against identity, name the
commit that superseded it, give the current identity, and separate the two forecast annotation-only
supersessions from the one uncovered producer-script supersession. That is variant B.

## Artifact

* `PROPOSED-A-update-rows.diff` — the literally requested repair: the three rows rewritten to the
  current identities, plus a dated note distinguishing the two forecast changes from the uncovered
  producer-script change. **Prepared, proved, and NOT recommended** (see §4).
* `PROPOSED-B-mark-superseded.diff` — **recommended**: the table gains a `status` column, the three
  rows keep their read-against ids and are marked `superseded 2026-09-09 by <current id>`, the other
  seven are marked `current`, and the same dated note is added.

## Validation

`git apply --check --verbose` against the working tree at HEAD `b14a84259…`:

| diff | exit code | evidence |
|---|---|---|
| `PROPOSED-A-update-rows.diff` | **0** | `checks/05-git-apply-check-A-update-rows/` |
| `PROPOSED-B-mark-superseded.diff` | **0** | `checks/05-git-apply-check-B-mark-superseded/` |

⛔ **Neither diff was applied.** The manuscript is byte-identical at close: `git status --porcelain`
reports nothing for it and `git hash-object` gives `0c6c57f63b89f41e8ef7722d87035fbfa440cb50`, the
identity `6466168d7` declares for the owner-edited main. No producer was run, no file among the three
was reverted or altered, nothing was staged, committed or pushed, and `scripts/preflight.sh` was not
run. Only the two diffs are mutually exclusive — applying one invalidates the other's context.

## Provenance

HEAD `b14a84259363f8b18c98d7754a305892cd37f92b`, measured at lane start and re-measured unchanged at
lane close. All ten identities re-derived by `git hash-object` against the working tree in this lane;
none taken from the task statement or from any earlier record. Blob history read with
`git rev-parse <commit>:<path>`.

## Limitations

* Blob identity is content identity, not data provenance — as §8 itself says. Confirming a hash says
  nothing about whether the underlying GEO or DepMap inputs are what they claim to be.
* The producer-script change was judged annotation-only **by reading its diff**, not by executing it.
  ⛔ No producer was re-run, so leaf-invariance of its output was not independently reproduced in this
  lane; the claim is "the diff touches no computation or literal", which is weaker.
* Whether the *other seven* objects' §8 identities correspond to the data the paper reports was not
  re-verified; only that they still match the tree.
* HEAD can move again. Both diffs should be re-checked with `git apply --check` before any owner
  applies one.

## Stop condition

Reached. Ten identities re-derived, coverage question answered by quotation, both repair variants
prepared and proved with real exit code 0, neither applied. ⛔ Further action — choosing a variant and
applying it — belongs to the manuscript's owner, whose batch is already accepted; this lane does not
edit the manuscript.
