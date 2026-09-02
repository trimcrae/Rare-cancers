---
id: DOC-SPRINT-S50-FIVE-REFS-READ-TO-THE-LINE
title: "S50 — the five A-graded refs read to the line: 221 unabsorbed lines, 45 of them unique, and four of the five must not be deleted"
level: L3
kind: memo
status: live
date: 2026-09-02
audience: [autonomous research agents, maintainers]
purpose: >
  Extend S38-BRANCH-CENSUS from path-level absence to line-level content for the five refs it graded A
  on the strength of "13–82 % line absorption with the remainder being ledger/JSON reserialization",
  so that a deletion decision rests on the remainder having been READ rather than characterised.
scope: >
  The five refs named in S38 §4e's last row. Every added line of every file each ref changed relative
  to its own merge-base with origin/main, checked against origin/main's current copy of that file,
  and every line that is not there classified. No sampling: the per-file counts sum to the per-ref
  totals and the classification counts sum to the per-ref absent counts.
last_verified: 2026-09-02
---

# S50 — FIVE REFS READ TO THE LINE

Written 2026-09-02, 5:05 AM ET, against `origin/main` at **`471fdebf8`**. Read-only throughout:
no git write command of any kind was issued, and no branch was deleted. **The deletion is the
driver's act; this document is the reading it needs.**

⛔ **THE HEADLINE, BECAUSE IT INVERTS S38'S ROW.** S38 graded these five **A · SUPERSEDED BY
CONTENT** on a remainder it described as *"ledger/JSON reserialization"*. Read to the line, the
remainder is **16 lines of reserialization, 160 superseded, and 45 of unique content on four of the
five refs.** Only one of the five is safe to delete, and it is safe only because a DIFFERENT ref in
this same set carries the record that supersedes it.

---

## §1 · THE INSTRUMENT, AND THE TEST S38 SAID TO RUN

S38 §4a records that its first instrument was wrong because `git rev-parse` **echoes the unresolved
path and exits 128**, so an `|| echo MISSING` fallback never fired and every absent file graded
"differs". That failure was reproduced here before anything was trusted:

    $ git rev-parse origin/main:zz/definitely/not/here.txt ; echo $?
    origin/main:zz/definitely/not/here.txt          # <- the path, not an error string
    128

**This reading uses `git cat-file -e <ref>:<path>` and branches on the return code**, which is
immune to that. Both directions were tested before a single verdict was taken:

| probe | expected | measured |
|---|---|---|
| `origin/main:zz/definitely/not/here.txt` | ABSENT | `False` ✅ |
| `origin/main:CLAUDE.md` | PRESENT | `True` ✅ |
| `origin/main:autonomy/receipts/CYC-0073-d4ccfde4.json` | PRESENT (misfiled top level) | `True` ✅ |
| `origin/main:research/autonomy/receipts/CYC-0073-d4ccfde4.json` | ABSENT | `False` ✅ |
| a line known to be in `CLAUDE.md` | found | `True` ✅ |
| `"ZZZ this line is not in CLAUDE.md ZZZ"` | not found | `False` ✅ |

★ **The last two are the line-presence half, and they matter as much as the path half** — a
line-absorption instrument that silently matched everything would report 100 % absorption and grade
every branch safe. Presence is tested with a **multiset**, not a set, so a line the branch adds
three times and `main` holds once counts two absences rather than none.

### 1a · The command, exactly

For each ref, with `MB = git merge-base origin/main <ref>`:

    git diff --name-only $MB <ref>                     # files the branch itself changed
    git diff --no-color -U0 $MB <ref> -- <file>        # its own added lines (drop the +++ header)
    git cat-file -e origin/main:<file>                 # rc 0 = main has the path
    git show origin/main:<file>                        # main's CURRENT copy, matched as a multiset

A second, independent pass classified whether an "absent" line is absent only in its **indentation
or line-wrapping** by re-matching on `line.strip()`. And a third pass, because a merge-base diff
cannot see a file the branch inherited unchanged, took the whole-tree path check:

    comm -23 <(git ls-tree -r --name-only <ref> | sort) \
             <(git ls-tree -r --name-only origin/main | sort)

⚠ **That third pass is the one that finds what the first two cannot**, and it is how the single
`main`-absent path on the two CYC-0074 refs was confirmed: it is inherited from before their
merge-base, so it appears in **no** branch diff.

---

## §2 · THE TABLE — real absorption, and where it disagrees with S38

| ref | files changed | added lines | absent from `main` | **absorption** | inside S38's 13–82 %? |
|---|---:|---:|---:|---:|---|
| `origin/seat/s1-aut-pd-130` | 7 | 543 | 70 | **87.1 %** | ⛔ no — above |
| `origin/seat/s4-aut-045` | 4 | 21 | 13 | **38.1 %** | ✅ yes |
| `origin/seat/s5-retest-blocks` | 2 | 20 | 20 | **0.0 %** | ⛔ no — below |
| `origin/claude/aut-pd-130-s4-CYC-0074` | 7 | 585 | 85 | **85.5 %** | ⛔ no — above |
| `origin/claude/aut-pd-147-s3-CYC-0074` | 3 | 660 | 33 | **95.0 %** | ⛔ no — above |
| **total** | **23** | **1 829** | **221** | **87.9 %** | — |

**⛔ FOUR OF THE FIVE FALL OUTSIDE S38'S STATED RANGE, AND THIS IS A DISAGREEMENT RECORDED RATHER
THAN RECONCILED.** S38 published the range as a summary and no per-ref numbers for this row, so
there is nothing to diff against line by line; what can be said is that **no ref in this set
produces 13 % or 82 % under the method above**, and the true range is **0.0 – 95.0 %**.

★ **The floor is the one that matters.** `origin/seat/s5-retest-blocks` absorbs **zero** of its
twenty added lines. A row summarised as "13–82 %" carries no signal that one of its members is at
the bottom of the scale, and 0 % is precisely the shape a branch has when its work never landed.

### 2a · Path-level absence, confirmed and extended

Zero `main`-absent paths in the branch diffs of all five — every file each branch touched exists on
`main` today. The whole-tree pass finds **exactly one** inherited `main`-absent path, on the two
CYC-0074 refs only:

    research/autonomy/receipts/CYC-0073-d4ccfde4.json

⚠ **AND THE RESOLUTION OF IT IS NOT ON `origin/main`.** The prompt for this reading states the
corrected copy "has since been moved into `research/autonomy/receipts/`". That move is in the
**working tree only** — `git status` shows `D autonomy/receipts/…` staged nowhere and `??
research/autonomy/receipts/…` untracked. `origin/main` at `471fdebf8` still holds the receipt at the
misfiled top-level path and does not hold the correct one. This changes nothing about the verdicts
below, because the branch copy is superseded either way, but a later reader must not take the move
as landed.

**The branch copies are the OLDER receipt.** Blob comparison, not inference:

| copy | blob |
|---|---|
| both CYC-0074 refs, `research/autonomy/receipts/…` | `4cb8ad7e2` |
| `origin/main`, misfiled `autonomy/receipts/…` | `cfc6a268e` |
| working-tree untracked copy | `cfc6a268e` (identical to `main`'s) |

`cfc6a268e` is strictly richer: `max_concurrent` 0 → 2 with a `_corrected` field explaining that the
receipt aged out silently, a fourth `what_i_got_wrong` entry, a populated `blocked_by`, and a full
`handoff` block. **The branch copies are SUPERSEDED, and the surviving question is only where
`main`'s copy should sit — which is a trunk defect, not a branch one.**

---

## §3 · THE CLASSIFICATION — all 221 lines, and UNMEASURED = 0

| ref | RESERIALIZATION | SUPERSEDED | **UNIQUE CONTENT** | UNMEASURED | total |
|---|---:|---:|---:|---:|---:|
| `seat/s1-aut-pd-130` | 0 | 70 | **0** | 0 | 70 |
| `seat/s4-aut-045` | 0 | 0 | **13** | 0 | 13 |
| `seat/s5-retest-blocks` | 10 | 0 | **10** | 0 | 20 |
| `claude/aut-pd-130-s4-CYC-0074` | 2 | 78 | **5** | 0 | 85 |
| `claude/aut-pd-147-s3-CYC-0074` | 4 | 12 | **17** | 0 | 33 |
| **total** | **16** | **160** | **45** | **0** | **221** |

**UNMEASURED IS ZERO AND IT IS A COUNT, NOT A CLAIM.** Every one of the 221 lines was printed and
read; the per-file counts sum to the per-ref totals and the classification row sums to the absent
column. Two of the 221 differ from `main` in indentation alone; they are counted under SUPERSEDED
rather than given a category of their own.

---

## §4 · `origin/seat/s1-aut-pd-130` — 87.1 %, and its remainder is a REWRITE, not a loss

**✅ SAFE TO DELETE — conditional on §7's ordering.**

The branch built AUT-PD-130: a real `--check` for `claim_coverage.py`, wired into the commit loop.
**That feature is on `main`.** Not inferred — read:

| wiring | `main` at `471fdebf8` |
|---|---|
| `scripts/preflight.sh` | line 821, `"research/manuscripts/claim_coverage.py\|claim coverage census\|--check"` |
| `.github/workflows/tests.yml` | line 237–238, step *"The claim-coverage census reproduces from the live corpus"* |
| `scripts/regenerate_aso_chain.sh` | line 311, `run_step "claim coverage census" … "--check"` |
| the paired test module | present, 385 lines, first added `062a48ae1` (2026-09-01) |

The 70 unabsorbed lines break down as **23 + 5 comment lines in `preflight.sh` and
`regenerate_aso_chain.sh` that `main` rewrote later and longer**, 2 guard-list lines present on
`main` in a different order within the same `for g in`, 2 `run_step` continuation lines `main` holds
on one line, 7 `tests.yml` comment lines plus a step name `main` restates, 6 archive-manifest
digests, 20 lines of the test module, and 1 ledger line.

⭐ **THE SUPERSESSION IS SIGNED, WHICH IS WHY THIS IS A READING AND NOT A GUESS.** `main`'s copy of
the test module says so in its own source, naming this branch:

> *"⛔⛔ A REAL COPY, NOT A SYMLINK, FOR THE ONE FILE A TEST HERE MUTATES — AND THIS IS A CORRECTION
> TO THE PORTED VERSION RATHER THAN A PREFERENCE (measured 2026-09-01). `tracked_tree_guard`
> (AUT-PD-186, added 2026-08-29, **after this module was first written on its stranded branch**)
> audits every write event and resolves the path with `os.path.realpath` … So replacing the clone's
> SYMLINK … the manoeuvre the original `_materialise` performed, raised `RuntimeError` …"*

Every one of the module's 20 unabsorbed lines is inside that supersession: `_materialise` was
deliberately removed, `~1.7 s` became `~1.8 s`, `reads 32 manuscripts` became `reads every censused
manuscript`, `if not os.path.lexists(dst) and os.path.exists(src)` became
`if os.path.lexists(dst) or not os.path.exists(src)`, and each bare `assert` gained a failure
message. `main` also carries **18** test functions to the branch's **17**.

The 6 manifest lines are a regeneration `main` has redone since — branch `git_revision`
`c02dcd6c6` (2026-08-28 23:07), `main`'s `fd11a624e` (2026-09-02 07:59), `total_bytes`
43 248 550 → 53 196 078.

**The one ledger line** is the branch's own AUT-PD-130 `evidence`. It is superseded by the fuller
closure record on `claude/aut-pd-130-s4-CYC-0074`, whose `_recovered_from` block names this branch
and settles its fate in its own words:

> `"branch": "seat/s1-aut-pd-130"`, `"merged_into_main": false`,
> *"Re-derived onto origin/main by seat s4-aut-pd-130-CYC-0074-5a21085f rather than merged: the
> branch's manifest regeneration is base-specific and was redone here. **The branch itself remains
> unmerged and can be deleted once this lands.**"*

⚠ **"Once this lands" has not fully happened** — the code landed, the ledger record did not (§6).
That is why this verdict carries §7's ordering condition.

---

## §5 · `origin/seat/s4-aut-045` — 38.1 %, and every unabsorbed line is live work

**⛔ DO NOT DELETE. 13 of 13 unabsorbed lines are UNIQUE CONTENT.**

S38 called this remainder reserialization. It is a completed **$0 re-test of a blocked route**, and
`origin/main` is still carrying the pre-test state it corrects.

**The proof is what `main` says today, not what the branch says.** `origin/main`'s `RT-MONOVALENT`
row in `systems/graph/routes.json`:

    "next": { "best_next_action": "Write down the selectivity requirement this route would have to
              meet, with its basis. It is $0 and it is what makes every later grade of this route
              meaningful.", "cost": "$0", "blocked_on": ["BLK-UNSIZED-REQUIREMENT"] },
    "state": { …, "last_verified": "2026-08-06" }

and its ledger row `AUT-045`:

    "state": "queued",  "blocked_evidence": null,  "last_evidence_utc": "2026-08-06",  "score": 64.0

**The branch proves that action was already done, three weeks ago.** Its `blocked_evidence`, absent
from `main` in full:

> *"RE-TESTED 2026-08-28 (SEAT-s4-ba841eee) — THE BLOCK ON THIS ROW'S ACTION IS DISSOLVED … the
> named action (write the selectivity requirement with its basis) was DONE on 2026-08-07 in
> `research/manuscripts/degrader/selectivity-requirement-sizing.md` §2 as REQ-MONO-1/2/3, and commit
> `ba0f4a7f2` (2026-08-07) restated BLK-UNSIZED-REQUIREMENT … but that commit never touched
> RT-MONOVALENT's `next.best_next_action`, which `git log -S` shows unchanged since the graph was
> created on 2026-08-05. `priority.py:286` reads this row's `what` straight from
> `next.best_next_action` … **so the row re-derived a discharged action for three weeks.**"*

It also carries a **NEW $0 LEAD nowhere on `main`** — CLAUDE.md §0's exact currency:

> *"`research/modalities/nr4a3-monovalent-reach.json` contains zero occurrences of
> rsa/exposed/exposure/C7, so the exposure criterion the route's closure_note names is not applied
> inside the artifact carrying the covalent negative; whether it is inherited upstream is untraced
> and is the route's next action."*

⛔ **This bears directly on whether a computed NEGATIVE stands.** `main`'s `closure_note` still
says the covalent sub-form's negative "rests on a geometry computed with an exposure cutoff that
fails its own control". The branch measured that the artifact carrying that negative **contains no
exposure term at all**, and named the $0 trace that would settle it. Losing this ref loses a lead
about the soundness of a result the program has published a grade against.

The remaining lines are the three generated `systems/views/` rows and the routes-graph
`six_month_delta` / `rationale` / `required_validation` edits that carry the same finding — all
absent from `main`, all regenerable **from the graph edit and not from nothing**.

**Where it should go instead of deletion:** apply the `routes.json` edit for `RT-MONOVALENT`
(`required_validation[1]`, `next`, `six_month_delta`, `state.last_verified`), regenerate
`systems/views/`, and set `AUT-045.blocked_evidence` on the trunk. The views are generated, so only
the graph edit and the ledger line are real work.

---

## §6 · `origin/seat/s5-retest-blocks` — 0.0 %, and it reverses a null

**⛔ DO NOT DELETE. 10 of 20 unabsorbed lines are UNIQUE CONTENT; the other 10 are re-run
telemetry.**

Two artifacts, both regenerated 2026-08-28. `main`'s copies are the **2026-08-07** originals.

`research/modalities/cys-chemoproteomics-precheck.json` — **9 lines, all RESERIALIZATION.** One
`_generated_utc` and eight per-request `seconds`. Every status, count and verdict is byte-identical
to `main`. Nothing here.

`research/modalities/nr4a3-thiol-environment.json` — **1 line RESERIALIZATION, 10 UNIQUE.** The
branch's re-run changes what the file says:

| field | `main` (2026-08-07) | branch (2026-08-28) |
|---|---|---|
| `pkad_article_oa` `http_status` | `null` | **`200`** |
| `pkad_article_oa` `bytes` | `0` | **`154073`** |
| `pkad_article_oa` `error` | `"URLError: … Tunnel connection failed: 403 Forbidden"` | **`null`** |
| `pkad_article_oa` `status` | `"UNREACHABLE"` | **`"OK"`** |
| `pkad_webserver` / `_https` | `403` / tunnel-403 | **`404` / `404`** |
| `n_reachable_in_this_run` | `0` | **`1`** |
| `verdict` | `"REFERENCE_DATABASE_EXISTS_BUT_UNREAD"` | **`"REFERENCE_READ"`** |

★ **THE ONE LINE, NAMED EXACTLY, THAT IS THE REASON THIS READING EXISTS:**

    "verdict": "REFERENCE_READ",

`main`'s artifact asserts a null — the experimentally-measured-pKa reference database exists and
could not be read. The branch's artifact says it **was** read: PMC6389863, HTTP 200, 154 073 bytes.
CLAUDE.md §4 is explicit that *an absent reading is not a reading of absence*, and `main` is
currently the one holding the absent reading.

⚠ **AND THE 403 → 404 IS A SEPARATE FINDING IN THE OTHER DIRECTION.** From an unblocked network the
`pkad` webserver returns **404**, not a proxy 403 — an endpoint statement rather than a network one.
A merge must not let the `REFERENCE_READ` verdict beside it round that up.

**The finding is preserved in prose; the artifacts are not.** `origin/main`'s
`research/autonomy/sprint-2026-09-01/S31-ORPHANS.md` lines 191–205 transcribes every number above
and files it at line 436 as a `queued` `fetch` row, noting *"main has not re-run these files since
2026-08-07"*. **So deleting this ref does not lose the numbers — it loses the two regenerated
artifacts that carry them, while `main`'s copies keep asserting the opposite.** That is a
one-commit patch, not a re-fetch, and it should be taken before the ref goes.

---

## §7 · `origin/claude/aut-pd-130-s4-CYC-0074` — 85.5 %, and the code landed while the record did not

**⛔ DO NOT DELETE. 5 of 85 unabsorbed lines are UNIQUE CONTENT** (78 SUPERSEDED, 2 RESERIALIZATION).

The 78 are §4's story again — the same `preflight.sh` / `tests.yml` / `regenerate_aso_chain.sh`
comment blocks `main` rewrote on 2026-09-01, the same manifest regeneration, and the same test
module `main` ported and corrected. Two of them deserve naming because they look like losses and
are not:

- `test_a_missing_artifact_is_refused` — the branch's one surviving mutation — **is on `main`**, and
  `S34-STRANDED.md` records it recovered as patch `P4`.
- the branch turned a bare `pytest.skip` into a `pytest.fail`; `main` went the other way, back to a
  skip carrying a `⛔ SKIP IS DELIBERATE` marker and a five-line rationale, in commit `f9aa5df36`
  *"two skips that recorded no decision"* (2026-09-01). `S34-STRANDED.md` line 333 names this
  explicitly: *"the `aut-pd-130` skip half would … undo a deliberate later decision."* **SUPERSEDED
  by a later decision, and re-applying the branch's version would be a regression.**

The 2 RESERIALIZATION lines are the ledger's derived `"done": 116` / `"queued": 141` counters.

**The 5 UNIQUE lines are the AUT-PD-130 closure record**, and `main` does not have it in any form:

    "state": "done"
    "evidence": "CLOSED. RECOVERED, RE-DERIVED, MUTATION-TESTED, WIRED. …"
    "_recovered_from": { "branch": "seat/s1-aut-pd-130", "sha": "c02dcd6c68 …",
                         "merged_into_main": false, "checked_utc": "2026-08-29T02:22Z", "note": … }

`origin/main`'s AUT-PD-130 row is **`state: in_progress`** carrying an `evidence` field that
describes `lease_arbitration()` in `continuity.py` — another item's work (§8). Searched on `main`
repo-wide, the strings `"RECOVERED, RE-DERIVED, MUTATION-TESTED, WIRED"`, `"ONE SURVIVOR ON THE
FIRST PASS"` and `"13/13, SINGLE SITES"` return **zero files**. The record of *which mutation
survived and why the artifact-missing branch was unbound* exists on this ref alone.

★ **AND THIS REF IS WHAT MAKES §4'S VERDICT SAFE.** `seat/s1-aut-pd-130` is deletable because its
work was re-derived here and its own note says so. **Delete this ref and that chain of custody is
gone, and `s1` stops being safe retroactively.** The ordering is: land this record on the trunk,
then `s1` and this ref may both go.

---

## §8 · `origin/claude/aut-pd-147-s3-CYC-0074` — 95.0 %, the highest absorption and the most unique content

**⛔ DO NOT DELETE. 17 of 33 unabsorbed lines are UNIQUE CONTENT** (12 SUPERSEDED, 4
RESERIALIZATION).

⚠ **THE HIGHEST ABSORPTION PERCENTAGE IN THE SET IS THE MOST DANGEROUS NUMBER IN IT.** 95 % reads as
"nearly all landed", and what landed is the easy part: both code files are **byte-identical** on
`main` —
`research/manuscripts/tests/test_the_fusion_partner_gene_identifiers_are_ones_an_artifact_names.py`
(385 lines, added `ca9c6da22`) and `mutate_fusion_partner_guard.py` (848 lines). **All 33 residual
lines are in `research-ledger.json`, which is exactly where a percentage cannot see them.**

The 4 RESERIALIZATION lines are derived counters (`process_defect: 135`, `done: 114`,
`in_progress: 4`, `queued: 141`). The 12 SUPERSEDED are lease bookkeeping — `owner`, `score`,
`claimed_utc`, `age_factor` — plus two `what` strings present verbatim on `main`.

### 8a · The 17 unique lines

**(i) The AUT-PD-147 closure evidence** — `main`'s row is `in_progress` with the wrong evidence
string. Two measurements inside it were searched for on `main` and return **zero files**:

    "⛔ WHAT IS NOT CLOSED, MEASURED RATHER THAN ESTIMATED: a drift between two ATTESTED symbols
     outside a `::` construction remains unguarded — 31 of the manuscript's 71 NR4A3 sites, 34 of 46
     EWSR1, 74 of 100 TAF15 and 5 of 6 TCF12 are bare."

and the reason registers are out of the pair check's scope — *"the pair predicate WOULD have red on
true input at `partner-event-counts-2026-08-08.md`, which quotes PMID 41755350's novel `FUS::NR4A2`
and `ACTB::NR4A3` verbatim"*. **That second one is a design justification for a guard that is live
on `main` today**, and a later session narrowing that scope without it would be re-deriving it from
scratch or getting it wrong.

**(ii) The `_evidence_was_misfiled` note**, which diagnoses a defect this reading independently
reproduced at `471fdebf8`:

    "The evidence field on this row when the seat opened it described `lease_arbitration()` … It is
     byte-identical (sha256 b6d6cda689a7…) on EIGHT unrelated rows."

⛔ **REPRODUCED HERE, AT HEAD, BY GROUPING `evidence` BY SHA256.** Eight rows on `origin/main` carry
the identical 1 743-character string: `AUT-PD-049`, `132`, `140` (done), `AUT-PD-130`, `147`, `148`
(in_progress), `AUT-PD-133`, `149` (queued). **Five are still open, and a reader opening any of them
reads another item's proof of work.** This is the mechanism that made §7's and §8's closure records
vanish from the trunk in the first place — the same ledger writes this reading is recommending are
the ones the bug ate.

**(iii) Three defect rows filed under COLLIDED IDS.** The branch filed `AUT-PD-154`, `155`, `156`.
On `origin/main` those three ids exist and mean **entirely different defects** — 154 is the step-11
auto-permission reaper, 155 the commit-loop cost row, 156 a `changed_paths()` fix (done). The
branch's three are therefore invisible on the trunk under any id, and searching `main`'s ledger for
their content returns **0 hits** for `b6d6cda689a7`, `EIGHT UNRELATED LEDGER ROWS`, `HARNESS ERROR`
and `ANOTHER REAL SYMBOL`.

✅ **All three ARE transcribed in prose on `main`** — `S34-STRANDED.md` lines 412, 416, 417 — and
S34 caught the collision itself: *"Found on `claude/aut-pd-147-s3-CYC-0074` as its 'AUT-PD-155', an
id that on the trunk means the commit-loop cost row — so it has been invisible for four days."*
⛔ **But a proposed row in a memo is not a ledger row.** `priority.py` does not read `S34`, so these
three defects — one of them the eight-row broadcast that is still live — are scored by nothing.

---

## §9 · VERDICTS

| ref | absorption | unique lines | **verdict** |
|---|---:|---:|---|
| `origin/seat/s1-aut-pd-130` | 87.1 % | 0 | ✅ **SAFE TO DELETE** — conditional: only after `claude/aut-pd-130-s4-CYC-0074`'s closure record lands, since that ref is the chain of custody for this one |
| `origin/seat/s4-aut-045` | 38.1 % | 13 | ⛔ **DO NOT DELETE** — a completed $0 block re-test and a new $0 lead about whether a computed negative stands; `main`'s route row and `AUT-045` are both still pre-test |
| `origin/seat/s5-retest-blocks` | 0.0 % | 10 | ⛔ **DO NOT DELETE** — the only copy of two artifacts whose verdict flips `REFERENCE_DATABASE_EXISTS_BUT_UNREAD` → `REFERENCE_READ`; `main` still asserts the null |
| `origin/claude/aut-pd-130-s4-CYC-0074` | 85.5 % | 5 | ⛔ **DO NOT DELETE** — the AUT-PD-130 closure record, absent from `main` in every form, and the provenance that makes `s1` deletable |
| `origin/claude/aut-pd-147-s3-CYC-0074` | 95.0 % | 17 | ⛔ **DO NOT DELETE** — the AUT-PD-147 closure evidence with two measurements found nowhere on `main`, and three defect rows filed under ids the trunk gave to other work |

### 9a · What to do instead of deleting, smallest first

1. **`s5`** — commit the two regenerated `research/modalities/` JSONs onto the trunk. No re-fetch;
   `S31-ORPHANS` already holds a `queued` row for it. Keep the `403 → 404` distinction intact.
2. **`s4`** — apply the `RT-MONOVALENT` edit to `systems/graph/routes.json`, regenerate
   `systems/views/`, set `AUT-045.blocked_evidence`. The views are generated; the real work is two
   fields and a ledger line.
3. **`aut-pd-130-s4` and `aut-pd-147-s3`** — write the two closure records onto the trunk
   (`AUT-PD-130` → `done`, `AUT-PD-147` → `done`, each with its real evidence and the
   `_recovered_from` / `_evidence_was_misfiled` notes). Then `s1` and `aut-pd-130-s4` are both free.
4. **The eight-row broadcast** — file it as a ledger row with a fresh id from `ids.py`, not as
   `AUT-PD-155`. Until it is a row, `S34`'s prose is the only thing that knows, and nothing scores
   prose.

⛔ **Nothing in §9a was done here.** This ref set was read read-only; the tree was not touched
outside this file.

---

## §10 · WHAT THIS READING DOES NOT CLAIM

- **It does not re-grade the other 180 refs.** S38's verdicts elsewhere stand or fall on their own
  evidence; what is shown here is that *one* of its rows characterised a remainder it had not read,
  and the characterisation was wrong on four of five members.
- **It does not claim the 160 SUPERSEDED lines were read for scientific correctness** — only that
  `origin/main` says something later about the same thing, with the commit or the source comment
  that says so cited in each case.
- **It does not settle whether `mutate_fusion_partner_guard.py` still exits 1 on the trunk with 8
  un-run mutations.** That claim lives on `aut-pd-147-s3` and `S34` marks it `UNKNOWN, NOT ABSENT`.
  Running it needs a settled tree; it was not run here, and it is not counted as measured.
- **It does not treat `S31`'s and `S34`'s prose as a substitute for the artifacts and rows.** A memo
  preserves a finding for a human reader; it does not restore an artifact `main` contradicts, and it
  is not read by `priority.py`.
