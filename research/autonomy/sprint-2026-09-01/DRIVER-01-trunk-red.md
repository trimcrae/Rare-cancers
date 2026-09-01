# DRIVER-01 — the trunk is red, and the guard that is red was checking a git with one commit in it

**Found:** 2026-09-01, ~18:50Z (2:50 PM ET), by the driver, taking the free reading that
`health.py` said it could not take itself (`gates_green` → `NO-GATE-VERDICT`, "this checker has no
network by design").

## Verdict

**CONFIRMED, and the failing test is not reporting what it appears to report.** `main` is red, one
test, three commits running. The deposit record it names is correct; the guard checking it cannot
see the history it needs.

## What I measured

`tests (modalities)` on `main`, most recent runs:

| run | created | head | conclusion |
|---|---|---|---|
| 33537002198 | 17:18Z | bd8aac753 (**HEAD**) | failure |
| 33534733266 | 16:55Z | 7e9409a4b | failure |
| 33532168479 | 16:30Z | c48875a00 | failure |
| 33523366953 | 15:03Z | **850edb335** | **success** |
| 33518... | 14:28Z | f37ef3c02 | success |

One failure in run 33537002198, out of 11,012 passing:

```
FAILED research/manuscripts/tests/test_the_deposit_the_papers_cite_is_current.py::
       test_the_recorded_upload_digest_is_corroborated_by_git_rather_than_declared
AssertionError: deposit-state.json records the draft as built at 850edb3358ba, which is not a
commit in this repository. A revision nobody can resolve cannot corroborate anything.
assert 128 == 0
 + where 128 = CompletedProcess(args=['git','cat-file','-e','850edb3358ba…^{commit}'],
                                returncode=128, stderr=b'fatal: Not a valid object name …')
```

I tested that assertion here rather than believing it:

```
$ git cat-file -e 850edb3358ba56ca127f3b5c79e23804b08c540c^{commit} && echo PRESENT LOCALLY
PRESENT LOCALLY
$ git merge-base --is-ancestor 850edb3358ba56ca127f3b5c79e23804b08c540c HEAD && echo YES
YES
```

**The sha is real and it is an ancestor of `main`'s current head.** So the message is false as
written — the revision is resolvable, just not by the process that asked.

## The discriminating observation

Competing hypotheses were (a) `main` was rebased and the commit orphaned — the AUT-PD-195 shape,
and the one this repository has been trained by five open rows to expect; (b) the CI checkout cannot
see it.

(a) is refuted by the `merge-base` reading above. (b) is confirmed by the workflow: the `pytest` job
in `.github/workflows/tests.yml` (~line 414) is

```yaml
  pytest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4          # no fetch-depth → depth 1
```

**In a depth-1 checkout the object store holds exactly one commit: the tip.** So
`git cat-file -e <recorded revision>` can succeed only when the recorded revision IS the tip.

★ **And that is precisely the shape of the run history.** The last green run's `head_sha` is
`850edb335` — the same commit `deposit-state.json` records as `uploaded_at_git_revision`. The guard
passed because the tip happened to be the one commit it wanted, and it has been red on every commit
since because the tip moved.

## Why this is worth a finding rather than a fix note

The test's own docstring says:

> ★ THE FIELD IS MADE OBSERVABLE BY THE ONE WITNESS THAT CANNOT BE BACK-DATED: git.

In CI, that witness has been a repository containing one commit. The guard was not wrong about
what it wanted; it was **structurally unable to look**, and the one time it reported success it was
a coincidence rather than a measurement. That is this repository's most-repeated defect — a check
that appears to measure and does not — and it is the same family as AUT-PD-141, AUT-PD-175 and
AUT-PD-195, one level up: not *an artifact recording a sha that does not survive*, but *a check that
cannot see the history it claims to check*.

⚠ It also means the green run at 15:03Z is not evidence that the deposit record was ever
corroborated. Nothing has corroborated it in CI. The corroboration this sandbox just performed by
hand is the first one on record.

## Handed to

**S7-CHAIN**, whose cluster (AUT-PD-028/141/168/175/195/001/189) is this exact machine. Its owned
paths were widened for this fix to `.github/workflows/tests.yml` and
`research/manuscripts/tests/test_the_deposit_the_papers_cite_is_current.py`, with two constraints
sent verbatim:

1. `tests.yml` ~line 512 documents the depth-1 default as **deliberate** — two stuck-clock tests
   carry a shallow-horizon degrade-gracefully path that CI is the only place to exercise. A blanket
   `fetch-depth: 0` may still be right, but it must be shown not to retire that property.
2. ⛔ The fix must make the guard **able to run**, never easier to pass. Skipping it, making the
   assertion conditional on the object being present, or downgrading it to a warning are all the
   failure this finding is about.

## Ledger rows the driver should write

- **kind `process_defect`, state `queued`** — "⛔⛔ THE DEPOSIT-CORROBORATION GUARD RUNS IN A DEPTH-1
  CHECKOUT, SO IT CAN ONLY PASS WHEN THE RECORDED REVISION IS THE TIP — AND ITS ONE GREEN RUN WAS
  THAT COINCIDENCE. Measured 2026-09-01 (runs 33523366953 green at head 850edb335, 33532168479 /
  33534733266 / 33537002198 red after the tip moved); the sha resolves locally and is an ancestor of
  HEAD, so the assertion's own message is false as written." Serves RT-AUTONOMY. Closes nothing;
  blocks the trunk.
- **kind `process_defect`, state `queued`** — "⚠ `health.py`'s `gates_green` row is UNMEASURED by
  design (no network), and the trunk was red for three commits before anyone looked. The verdict it
  asks for is a `{ok, red_since_utc, detail}` blob the tick workflow could write on every run; until
  it does, `main` being red is discoverable only by a human remembering to check Actions."
