# J1 — collection and adjudication against `CONTRACT-J1-surface-targets-abstract-cspg4.md`

Collected 2026-09-08 10:09–10:14 UTC from retained originals. No re-run, no restart.

## Child identity — from the transcript

| item | measured |
|---|---|
| child | `a4733685da75134da` |
| original JSONL | `J1-executed-artifacts/ORIGINAL-CHILD-TRANSCRIPT-a4733685da75134da.jsonl`, **207,477 B**, `cmp`-identical |
| model strings | **39 × `claude-opus-5`, 0 others** |
| tool pairs | **22** (self-reported 14 — a **fifth** consecutive undercount) |
| span | 10:02:22 → 10:07:26 UTC |

## ⚠ J1 was NOT scratch-isolated: it temporarily swapped the shared manuscript

**I must not describe this child as having left the shared tree untouched.** Its baseline helper
mutated the shared checkout. The original command, quoted verbatim from the transcript at
**10:06:38.642Z**:

```
cp /tmp/claude-0/j1-lane/BEFORE.md research/manuscripts/surface-targets/emc-surface-target-landscape.md
for L in lint_consistency lint_citations submission_metrics lint_style lint_claims lint_submission_residue lint_asymmetry; do
  python3 research/manuscripts/$L.py > …$L.BASELINE.out 2> …$L.BASELINE.err
  echo "$L BASELINE(HEAD) exit=$?" | tee -a …EXITCODES.txt
done
cp /tmp/claude-0/j1-lane/AFTER.md research/manuscripts/surface-targets/emc-surface-target-landscape.md
```

So the **pre-edit bytes were written over the live manuscript**, seven linters were run against that
state, and the post-edit bytes were copied back — all inside one command. It used `cp`, not
`git stash`, so it satisfied the letter of the no-stash rule, but it is a **real temporary
shared-checkout swap** and the contract's isolation intent did not anticipate it.

**Consequences, measured rather than assumed:**

| check | result |
|---|---|
| restore complete? | working tree sha256 `35515cce…0168` **== retained `AFTER.md`** — no residue |
| baseline bytes correct? | `BEFORE.md` == `HEAD-baseline.md` == committed `d2ea5a7e` content, all `4aa5cdb2…9219` |
| swap window | ~seconds within the 10:06:38 command |
| my concurrent commit `4b59077c` (10:08:30) | **after** the window, and staged **neither** the manuscript nor `submission-metrics.json` — verified by `git show --name-only` |
| my concurrent commit `43958b91` | likewise staged neither |

**Nothing in flight was swept.** Explicit-path staging is what prevented it; had I used `git add -A`
during that window, a linter-baseline state of the manuscript could have been committed. Future
contracts must forbid writing to the shared path at all, not merely forbid `git stash`.

## Acceptance, adjudicated

1. **CSPG4 clause present in the Abstract's Results — MET.** From 0 mentions to 1:
   > "CSPG4, never evaluated at stage 1, rose on one array and in the sequencing cohort, was
   > uninformative, not negative, on the second, and is held open."
   Items **(a)–(d)** all fitted.
2. **Caps — MET.** Abstract **194 → 200 of 200**; main text **4,994, unchanged** — no main-text
   headroom spent. `submission_metrics` exit 0, within believed limits.
3. **No hedge deleted — MET, parent-spot-checked.** Twelve tightenings, all redundancy: e.g.
   "(n = 76 lines)" → "(76 lines)", "Those priorities were then tested" → "Priorities were tested",
   "None of eleven therapeutic addresses named by candidate routes" → "None of eleven route-named
   therapeutic addresses" (the body's own term). Every negative survives — `q = 1.0`, "no evaluated
   antigen both selective and restricted", "concordantly" on both array claims, "two were
   concordantly lower", ALCAM "yet sat below the normal-organ median", and the Conclusions sentence
   (only "and" → comma). Every count unchanged.
4. **No overclaim — MET.** The clause ends on "held open", states the array/sequencing asymmetry
   inside itself, and uses "never evaluated at stage 1" rather than "never scanned" — which matters,
   because the body says whether CSPG4 was ever scanned is **undecidable**. "Never scanned" would
   have overclaimed.
5. **⚠ (e) NOT fitted — a documented partial cap stop, which the contract counts as success.** The
   n = 4 / n = 6 transcript basis costs 8–10 more words against an abstract now at exactly 200/200.
   It remains where the response placed it, in Results and the Conclusion. **The abstract therefore
   still does not carry the basis "in the same breath", as review item 9 asked.** That residue is
   real and is recorded, not closed.
6. **No recomputation — MET.** No new number; the DFSP-only sensitivity analysis remains out of scope
   and undone.
7. **Linters — MET, and NOT all green.** `lint_consistency`, `submission_metrics`, `lint_style`,
   `lint_claims`, `lint_submission_residue`, `lint_asymmetry` all **exit 0** before and after.
   **`lint_citations` exits 1 both before and after**, stdout/stderr byte-identical across the two —
   the pre-existing repo-wide failure, neither caused nor fixed here, and **not** made green by I1.
   No gate weakened, relaxed, reordered or edited.

## A finding beyond the contract: the response's stated reason was never true

J1 checked the review response's "the abstract is at 199 words of 200" and found it **not reproducible
at any committed revision**: walking every commit touching the manuscript, the tool-equivalent
abstract count is **194 with 0 CSPG4 mentions throughout**. So the omission was never explained by a
one-word margin — there were six words of room the whole time, and the clause was never added.
Recorded as a provenance observation about the response document; **the response file itself is not
edited.**

## Standing

**Not publication acceptance.** Item 9's (e) is unfitted, the abstract is now at exactly 200/200 with
zero headroom, `lint_citations` is red, the DFSP-only sensitivity analysis is undone, and the F1
publisher/cross-version/Appendix A blockers are untouched.

## Retention

`/tmp/claude-0/j1-lane/` **intact, nothing deleted**, pending an exact-directory receipt. In-repo copy
`J1-executed-artifacts/` with a self-exclusive manifest.

---

# Scope narrowing, appended 2026-09-08 10:22 UTC — original finding preserved above

**"The response's stated reason was never true" overreaches the evidence and is narrowed here.**

What was actually inspected: the **committed Git history of this manuscript**. Across those
revisions the tool-equivalent abstract count is **194 words with zero CSPG4 mentions**, which
**mismatches** the response's "at 199 words of 200" and its "the clause is added".

What that does **not** establish: what existed in any **uncommitted working copy, external draft, or
separately reviewed version** at the time the response was written. Those were not inspected and
cannot be settled from here.

**Narrower reading, which is what stands:** *within the inspected committed history*, no revision
shows 199 words or a CSPG4 clause in the Abstract, so the response's statement does not correspond to
any committed state of the paper. Whether it corresponded to some uncommitted or external draft is
**unknown, not disproved.**

No search, rerun, or history-recovery exercise was performed for this narrowing, and none is planned.
The response file remains unedited. This is not a blocker to further work.

# Lifetime correction, same append

The adjudication's span "10:02:22 → 10:07:26 UTC" is the **tool window**, not the child's full
lifetime. The transcript's full span is **10:02:20.020Z → 10:08:14.816Z (~5 m 55 s)**. Tool pairs
**22** and model strings **`claude-opus-5` only** are unchanged.
