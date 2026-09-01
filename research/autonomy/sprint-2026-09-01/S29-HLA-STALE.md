---
id: DOC-SPRINT-S29-HLA-STALE
title: "S29-HLA-STALE — the artifact was not waiting on CI; it was waiting on a snapshot nobody takes"
level: L3
kind: incident
status: live
purpose: "Record the 3-vs-23 class-II panel defect in hla-coverage.json and the systems graph, the evidence establishing which number is right, the regeneration, and the mechanism that let a fixed generator ship a stale artifact for four days under green gates."
scope: "research/modalities/hla_coverage.py, research/modalities/hla-coverage.json, systems/graph/artifacts.json (ART-HLA-COVERAGE). Downstream consumers are reported, not edited — other seats hold those paths."
audience: [autonomous research agents, maintainers]
date: 2026-09-01
last_verified: 2026-09-01
---

# S29-HLA-STALE — the artifact was not waiting on CI; it was waiting on a snapshot nobody takes

**Item(s):** S13-VACCINE §4(a) and §4(b); proposed ledger rows 5 and 6 of S13-VACCINE.

**Owned paths, named before editing (charter §2):**

| path | role | touched? |
|---|---|---|
| `research/modalities/hla_coverage.py` | **the generator** | yes — added an offline `--check` |
| `research/modalities/hla-coverage.json` | **its artifact** | yes — regenerated, 1 line changed |
| `systems/graph/artifacts.json` | the `ART-HLA-COVERAGE` record, where the graph's half of the 3-vs-23 contradiction lives | yes |
| `systems/views/**` | regenerated with `systems_check.py --write-views`, never hand-edited | yes (see the ⚠ under *What I changed*) |
| `.github/workflows/*.yml` (new file, if the AFND fetch needed one) | **not needed — no new workflow written**; the fetch is not blocked and the workflow already exists | no |
| `research/autonomy/sprint-2026-09-01/S29-HLA-STALE.md` | this file | yes |

**Started (UTC):** 2026-09-01T20:05Z **Finished (UTC):** 2026-09-01T20:52Z **Real-dollar cost: $0.**

---

## Verdict

**FIXED — and the framing S13 handed me was wrong in the part that mattered.** Both defects were real
and both are now corrected. But the finding underneath them is not "a generator fix was never
regenerated". It is this:

★ **The regeneration had already happened. `modalities-run.yml` produced the corrected artifact and
pushed it to `modalities-cache` on 2026-08-29 — the day after the generator fix — and `main` went on
carrying the pre-fix copy for three more days with every gate green.** The `modalities-cache` copy
and the copy I regenerated locally today are **byte-identical** (`md5 f5aa796488b36dda1a69ceb39a4b1461`).
Nothing was blocked, nothing was owed to CI, and no dispatch was required. What was missing is a
by-hand `git checkout modalities-cache -- research/modalities/` that exists only as a comment in a
workflow header, and that nothing on earth measures.

⛔ **And "it needs the AFND fetch, so it is a CI job" is REFUTED as a statement about this sandbox.**
Both source URLs answer 200 here. Measured, not assumed:

```
$ curl -sS -o /dev/null -w "afnd_http=%{http_code} size=%{size_download}\n" \
    https://raw.githubusercontent.com/slowkow/allelefrequencies/main/afnd.tsv
afnd_http=200 size=6282337
$ curl -sS -o /dev/null -w "iso_http=%{http_code} size=%{size_download}\n" \
    "https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.json"
iso_http=200 size=65317
```

Both are `raw.githubusercontent.com`, and this sandbox's egress allowlist is *git hosts*. The AFND
mirror is a GitHub raw file **by deliberate design** — `hla_coverage.py`'s own header says the mirror
was chosen because "AFND itself serves only its interactive search form to a non-browser client". So
the one property that makes this artifact regenerable here is written at the top of the file that
generates it, and the belief that it was blocked survived anyway. **A remembered "this is blocked"
is exactly the claim CLAUDE.md §0 says is usually wrong.**

---

## What I measured

### 1 · Defect (a) — the artifact contradicts itself inside one string

```
$ grep -n "class_ii_note" research/modalities/hla-coverage.json      # at HEAD, before my change
116:  "_class_ii_note": "... That screen tested only a 3-allele DR panel (DRB1*01:01, DRB1*03:01,
DRB1*04:01, DRB1*04:04, DRB1*07:01, DRB1*08:01, DRB1*09:01, DRB1*11:01, DRB1*12:01, DRB1*13:01,
DRB1*13:02, DRB1*14:01, DRB1*15:01, DRB1*15:02, DRB1*16:01, DRB3*01:01, DRB4*01:01, DRB5*01:01,
DPB1*02:01, DPB1*04:01, DQB1*02:01, DQB1*03:01, DQB1*06:02), so this coverage is a FLOOR ..."
```

A stated count of **3** beside a printed list of **23**. This is not "stale against an external
fact" — it is a self-contradiction internal to one string, which is why it is checkable offline (§5).

The generator's side, `research/modalities/hla_coverage.py:459` at HEAD:

```python
"only a " + str(len(cd4_panel or [])) + "-allele class-II panel ("
+ ", ".join(cd4_panel or []) + "), so this coverage "
```

⛔ **`hla_coverage.py` has no `--check` mode at HEAD** — `grep -n "sys.argv\|--check" research/modalities/hla_coverage.py`
returns nothing. The seat brief asked me to "run the generator's `--check`"; there was none to run.
I have now written one (§5).

### 2 · ⭐ Which number is right — established before anything was changed, and "the newer one" is not the reason

**The commit that changed it.** `13105be5d` (2026-08-28), *"AUT-PD-093: RT-JUNCTION-NEOANTIGEN was
not withheld on anything — re-grade on coverage"*, is the only commit touching the phrase
(`git log -S'-allele class-II panel' -- research/modalities/hla_coverage.py`). It replaced a typed
literal with `len(cd4_panel)` and left a comment naming the harm: the stale count *"was quoted onward
into fusion-junction-neoantigen-paper.md, which is how a wrong number in a note becomes a wrong
number in a manuscript."* Its commit body records `n_alleles_screened 23` from the class-II artifact.

**Both numbers were true, of different days — and neither is true of a different *purpose*.** The
brief asked me to check whether the panel is genuinely 3 for one purpose and 23 for another. It is
not. `cd4_panel` has exactly one definition — `patient_class2_hla` in `patient-cd4-demo.json` — and I
read its value at each commit that touched that file:

```
$ git show a2afd1bfa:research/modalities/patient-cd4-demo.json | python3 -c "..."
at a2afd1bfa (2026-08-04): len= 3 ['DRB1*15:01', 'DRB1*03:01', 'DRB1*07:01']
$ for c in e6b3da39e c6c7cd297 0e7a6d08a; do ...; done
e6b3da39e (2026-08-19): 3
c6c7cd297 (2026-08-23): 23
0e7a6d08a (2026-08-23): 23
```

So: the panel really was a 3-allele DR panel when the sentence was written on 2026-08-04; it widened
to a 23-allele DR/DP/DQ panel in `c6c7cd297` on 2026-08-23, and **the artifact regenerated in that
same commit — printing the new 23-allele list beside the old typed 3.** The file has been
self-contradictory since 2026-08-23, five days *before* the generator fix. The generator fix did not
create the defect; it prevented the next one.

**And 23 is what the code produces today**, read out of the file rather than recalled:

```
$ python3 -c "... json.load(open('research/modalities/patient-cd4-demo.json')) ..."
patient_class2_hla len = 23
strong alleles = 1 ['DRB1*14:01']
```

⚠ **The one alternative reading I checked and rejected:** the 23 alleles span **three** loci families
(DR / DP / DQ), so "3" is a true count of something adjacent. But the sentence says *"3-allele DR
panel"* and enumerates alleles, not families, and the generator's derived value is `len(cd4_panel)`.
There is no purpose under which this sentence's "3" is currently correct.

### 3 · Defect (b) — one file, both numbers, quoted with line numbers

`research/manuscripts/emc-systems-map.json`, at HEAD:

```
2475:      "note": "Class-II coverage is a FLOOR over a tested 3-allele DR panel, and the junction
                   it is computed on is OBJ-MODEL-E7E3."
3767:      "value": "PARKED ... The class-II result is itself weak: ONE strong binder on ONE allele
                   across a 23-allele DR/DP/DQ panel in which every declared allele was scored ..."
```

Both lines are **projections of `systems/graph/`**, which is the source of truth (CLAUDE.md §7):

- line 2475 ← `systems/graph/artifacts.json:132`, `ART-HLA-COVERAGE.note` — **the wrong one**
- line 3767 ← `systems/graph/routes.json:2606`, `RT-VACCINE.grade` — **the right one, 23, left untouched**

I fixed the source (`artifacts.json`). ⛔ **I did not edit `research/manuscripts/emc-systems-map.json`
or `emc-systems-map.md`** — neither is in my owned paths, and another seat is editing that JSON right
now (its working-tree diff is an `RT-TRABECTEDIN` `closure_note`). The reprojection is a driver action;
the exact edit is under *What the driver must still do*.

### 4 · ★★ The mechanism — why four days passed with nothing red

Four independent gaps, each verified, in the order they let the defect through.

**(i) The producing workflow publishes to a branch nobody reads, and the snapshot is a comment.**
`.github/workflows/modalities-run.yml:127` runs `python research/modalities/hla_coverage.py`. Its
publish step pushes to `modalities-cache` (`git push origin modalities-cache`, line 267), and the
route back to `main` is documented **only** in the workflow's own header:

```
#   git fetch origin modalities-cache && git checkout modalities-cache -- research/modalities/
```

The discriminating observation, and it is decisive:

```
$ git log --format='%h %ad' --date=short -S'23-allele class-II panel' \
      origin/modalities-cache -- research/modalities/hla-coverage.json
d7bfcaf28 2026-08-29
$ git show origin/modalities-cache:research/modalities/hla-coverage.json > cache.json
$ diff cache.json research/modalities/hla-coverage.json && echo BYTE-IDENTICAL
BYTE-IDENTICAL to origin/modalities-cache
```

⭐ **The corrected artifact has existed since 2026-08-29. It was on the wrong ref.** This is CLAUDE.md
§7's branch-drift rule — *"never let a branch a workflow runs from be the only home of an artifact"* —
firing on an artifact whose graph record said it lived on `main`.

**(ii) The graph said this artifact had no workflow at all.** `ART-HLA-COVERAGE` carried
`"workflow": null` and `"published_to": ["main"]`. Both are false, and false in precisely the
direction that hides (i): a reader consulting the architecture to ask *"where does this file come
from, and could a fresher copy exist elsewhere?"* was told there is no workflow and only one branch.
Fixed.

**(iii) `check_artifacts` measures EXISTENCE, never CURRENCY.** `systems/systems_check.py:2028`
is explicitly built for this failure class — its docstring records that *"41 artifacts were found
living only on the `modalities-cache` branch"* — but the question it asks is *"does the cited file
exist on this branch?"* `hla-coverage.json` exists on `main`, so it passed, every day, while its
content was three days behind the copy its own workflow had published. **Existing is not the same as
being the current one, and no check in this repository asks the second question.**

**(iv) `preflight.sh`'s generated-artifact gate is an opt-in allowlist, and this producer is not on it.**
The loop at `scripts/preflight.sh:777` enumerates **17** producers by hand. `research/modalities` holds
**591** `.py` files and **4** of them appear in that list. `hla_coverage.py` is not one — and it could
not have been, because it had no `--check` and a full re-run of it costs two network fetches that a
commit-loop gate cannot depend on. **The gate is a list of the producers somebody remembered, not a
property of being a producer.** That is the finding worth more than the regeneration, and it
generalises: 574 producers under `research/modalities` alone are outside it.

⚠ **And the guard the manuscripts suite does have looks like it should have caught this and could
not.** `research/manuscripts/tests/test_vaccine_path_numbers.py:408` was rewritten on 2026-08-23
*"WHEN THE PANEL WIDENED FROM 3 ALLELES TO 23"*; it binds the **manuscript's** prose to
`patient-cd4-demo.json` directly. It never reads `hla-coverage.json`'s note. The one file that
mediates between them was the one nobody checked.

### 5 · The fix to the mechanism, and its mutation test (charter §7)

I added an **offline** `--check` to `hla_coverage.py`. It deliberately does **not** re-run the
producer: every field the defect lived in is derived from a committed local input, so the cheap half
is checkable with no network, and a gate that claimed to check the frequency figures without fetching
them would be a worse gate than none. It says so in its own success line.

It asserts three things: (1) the count the note **states** equals the number of alleles the note
**prints**; (2) that list is the panel in `patient-cd4-demo.json`; (3) `class_ii_cd4_helper_alleles`
is still the set of strong calls on disk.

**Mutation-tested in a scratch copy — the live tree's `OUT` path was redirected, never its contents:**

| mutation | check output | rc |
|---|---|---|
| **M1 — the real pre-fix artifact at `HEAD`** | `_class_ii_note says a 3-allele panel and prints 23 alleles beside it` | **1** |
| **M2 — note lists an allele the panel file lacks** | `... says a 23-allele panel and prints 24 ...` + `... is not the panel in patient-cd4-demo.json (23 alleles)` | **1** |
| **M3 — `class_ii_cd4_helper_alleles` set to `['DRB1*15:01']`** | `... is ['DRB1*15:01']; the strong calls ... are ['DRB1*14:01']` | **1** |
| **CONTROL — the live tree** | agrees | **0** |

M1 is the point: **the guard fires on the exact artifact that shipped**, not on a synthetic case.

### 6 · The regeneration, and the reason it changed exactly one line

Run with only the OUTPUT path redirected — every input resolved against the real tree — then diffed
against the committed copy:

```
$ diff <(python3 -m json.tool research/modalities/hla-coverage.json) \
       <(python3 -m json.tool <regenerated>)
116c116
<   "... only a 3-allele DR panel (...23 alleles...) ... not a complete DR scan: untested DR alleles ..."
---
>   "... only a 23-allele class-II panel (...23 alleles...) ... not a complete class-II scan: untested alleles ..."
```

**One line. Nothing else moved.** Every coverage figure, every Wilson CI, all 16 regional rows and
the allele-frequency table are unchanged, so the live AFND mirror has not drifted since 2026-08-23 in
any way that touches these four alleles. ⭐ **No pinned figure changes and `pinned-figures.json` needs
no entry.** The current values, read out of the regenerated artifact rather than recalled:

| figure | value | 95% CI | alleles used |
|---|---|---|---|
| e7::e3 public junction, class I | 0.0851 | [0.0826, 0.0876] | `HLA-B*15:01` |
| any strong binder, class I | 0.2737 | [0.2663, 0.2814] | `HLA-A*01:01`, `HLA-B*07:02`, `HLA-B*15:01` |
| CD4 class II | 0.0649 | [0.063, 0.067] | `DRB1*14:01` |
| both arms (CD8 ∧ CD4) | 0.0178 | — | — |

Two independent productions of this file — CI's on `modalities-cache` (2026-08-29) and mine today —
are byte-identical. That is as strong a reproducibility reading as this artifact can carry.

### 7 · Gates I ran (charter §6 — scoped, not the whole thing)

```
$ python3 research/modalities/hla_coverage.py --check
hla-coverage.json: class-II panel note and helper set agree with patient-cd4-demo.json
(⚠ the AFND frequency figures are NOT checked here -- that needs the fetch)          rc=0

$ python3 systems/systems_check.py --write-views
systems_check: wrote 104 view(s) to systems/views/                                   rc=0

$ python3 systems/systems_check.py
systems_check: 602 objects across 15 collections · 147 ERROR · 76 WARN · 7 INFO
```

⛔ **Those 147 errors are not mine and the driver needs to know it before preflight.** Every one is a
document-frontmatter class, and **every one is a file in `research/autonomy/sprint-2026-09-01/`** —
`grep -c` on the error stream: `D1` 60/60 in the sprint directory, `D11` 80/80, `D4` 7/7 (the seven
are `WAVE-1/2/3.md`, `DRIVER-01/02`, `S14-DETECTOR.md`, `S15-CAREDELIVERY.md`, all with no frontmatter
at all). Filtering the same stream for `hla|ART-HLA|artifacts.json|modalities-cache` returns **nothing**.
★ **The sprint's own findings-file convention violates `systems/schema/document.schema.json`:**
`kind: process` is not in its enum, and `purpose`, `scope` and `last_verified` are required. This file
is written to pass; the rest of the wave is not, and the driver's `preflight.sh` will be red on it.

`emc_systems_map_check.py` reports `1 ERROR [V1]` — `emc-systems-map.md` differs from what the
registry generates. **That is not mine either:** it is the `RT-TRABECTEDIN` `closure_note` another seat
changed in `emc-systems-map.json` without regenerating the view. It resolves with `--write-view`
after that seat lands.

---

## What I changed

| path | change |
|---|---|
| `research/modalities/hla-coverage.json` | **regenerated.** 1 line: `_class_ii_note` now reads `23-allele class-II panel` and `not a complete class-II scan: untested alleles`. Byte-identical to `origin/modalities-cache`. |
| `research/modalities/hla_coverage.py` | **added `check()` and a `--check` dispatch in `main()`** (+73 lines, 0 removed). Offline, pure-stdlib, sub-second; no existing behaviour touched — with no `--check` argument `main()` runs exactly as before. |
| `systems/graph/artifacts.json` | `ART-HLA-COVERAGE`: `note` no longer types a panel size (it points at the artifact, which owns it); `workflow` `null` → `.github/workflows/modalities-run.yml`; `published_to` `["main"]` → `["main", "modalities-cache"]`; the note records the measured snapshot gap. |
| `systems/views/**` | regenerated with `systems_check.py --write-views`, never hand-edited. |
| `research/autonomy/sprint-2026-09-01/S29-HLA-STALE.md` | this file. |

⚠⚠ **DRIVER, READ THIS BEFORE STAGING (CLAUDE.md §6, the `git add -A` incident).** My `--write-views`
run happened while other seats were mutating `systems/graph/`, so it wrote **their** in-flight graph
edits into the views too. Four view files moved and **none of them is mine**:
`systems/views/L1-st-repurposing.md`, `L2-rt-trabectedin.md`, `L3-publications.md`, `readiness.md`.
Evidence that they are not mine: `grep -rn "FLOOR over" systems/views/` returns **nothing** — no view
renders an artifact `note` at all, so my `artifacts.json` edit cannot have produced a view diff.
**Stage those four with the routes.json seat's work, not with mine, and re-run `--write-views` on the
settled tree before committing.**

⛔ **No new workflow was written**, and that is a deliberate refusal rather than an omission: the fetch
is not blocked here, `modalities-run.yml` already runs this generator, and a second workflow would
have been a third home for the same job. ⛔ **No CI was dispatched**, so there is no run id to report —
the answer was already committed on `modalities-cache` and independently reproduced locally.
⛔ **`systems/graph/routes.json` was not touched** — neither its `RT-TRABECTEDIN` entry nor its
`RT-VACCINE` entry, whose 23-allele statement is correct as it stands.

---

## What I could not do, and what it is actually waiting on

Nothing here is blocked in the CLAUDE.md §0 sense. Each is a named path I do not own.

1. **`scripts/preflight.sh` — the one-line enrolment that makes the new guard binding.** *"RECORDED IS
   NOT ENFORCED"*: `--check` exists and nothing calls it. Add to the `for g in ...` list at line 777:
   ```
            "research/modalities/hla_coverage.py|HLA class-II panel note|--check" \
   ```
   ⚠ Another seat has `scripts/preflight.sh` modified in the working tree right now; this must be
   sequenced after that seat, not merged over it. **Until this lands, the fix is a value fix and not a
   mechanism fix.**
2. **`research/manuscripts/emc-systems-map.json:2475` — reproject from the graph.** Replace the
   `ART-HLA-COVERAGE` `note` with the new `systems/graph/artifacts.json` text verbatim, then
   `python3 research/manuscripts/emc_systems_map_check.py --write-view` to regenerate
   `emc-systems-map.md:427`. Another seat holds that JSON at this moment.
3. **The manuscript prose in §"Downstream consumers" below** — `research/manuscripts/neoantigen/`
   and `research/manuscripts/modality-census/` are other seats' paths.

---

## Downstream consumers still carrying the wrong number — every one, with file and line

⛔ **Read out of the files today, not recalled.** `grep -rn "3-allele DR panel\|3-allele class-II"`
over `*.md`/`*.json`/`*.py`/`*.yml`, excluding `.git`, the ledger and this sprint directory.

| # | file:line | what it says | state | mine? |
|---|---|---|---|---|
| 1 | `research/modalities/hla-coverage.json:116` | `3-allele DR panel` beside 23 alleles | ✅ **FIXED** | yes |
| 2 | `systems/graph/artifacts.json:132` | `FLOOR over a tested 3-allele DR panel` | ✅ **FIXED** — size removed, not re-typed | yes |
| 3 | `research/manuscripts/emc-systems-map.json:2475` | projection of #2 | ⛔ **open** — driver, item 2 above | no |
| 4 | `research/manuscripts/emc-systems-map.md:427` | generated view of #3 | ⛔ **open** — clears when #3 is reprojected | no |
| 5 | `research/manuscripts/neoantigen/hla-coverage-emc.md:181` | §2.4, **unbannered method prose** | ⛔ **the worst one — see below** | no |
| 6 | `research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md:289` | inside a block quote whose own preceding paragraph says *"The panel is no longer three alleles"* | ⚠ correctly banner-ed; a reader could still lift the sentence | no |
| 7 | `research/manuscripts/modality-census/novel-modalities.md:318` | *"The structural point survives: ... the class-II screen tested only a 3-allele DR panel"* — presented as **current**, inside a superseded block | ⚠ open | no |
| 8 | `research/manuscripts/modality-census/novel-modalities-factcheck.md:144` | *"It remains a FLOOR in any case, because the class-II screen tested only a 3-allele DR panel (not fabricated up)"* | ⚠ open | no |

`systems/graph/routes.json:2606` and its three projections (`emc-systems-map.json:3767`,
`emc-systems-map.md:65`, `systems/views/L2-rt-vaccine.md:23`) already say **23-allele DR/DP/DQ** and
are correct. No view renders the artifact `note`, so #2 has no view consumers.

### ⛔ Row 5 is a live manuscript defect that is bigger than the panel size

`research/manuscripts/neoantigen/hla-coverage-emc.md` §2.4 is **Methods prose under no banner**, and
three separate statements in it are false against the committed artifact:

| §2.4 says | the artifact says |
|---|---|
| *"The DRB1 alleles presenting a **strong** helper (DRB1\*03:01, DRB1\*07:01)"* | `class_ii_cd4_helper_alleles: ["DRB1*14:01"]` — a different allele, and one, not two |
| *"that screen tested only a **3-allele DR panel** (DRB1\*15:01/03:01/07:01)"* | a 23-allele DR/DP/DQ panel |
| §2.5: *"all populations for the **seven** class-I and class-II alleles resolved"* | the run loads **4** alleles (`DRB1*14:01`, `HLA-A*01:01`, `HLA-B*07:02`, `HLA-B*15:01`) |

⚠ **And the file's own correction banner (lines 40–48) is itself stale in the direction that matters** —
it states *"The arm is reported, and it is negative: 2 predicted binders, none strong, on three DRB1
alleles"* and *"The both-arms figure is **not computed** rather than withheld"*. Both are now false:
there **is** one strong call, and `coverage_cd8_and_cd4_combined = 0.0178` is computed and committed.
The banner's own table row *"CD8∧CD4 both-arms | 16.5% | **not computed**"* is stale for the same
reason. **A correction banner that has itself gone stale is the most dangerous state here**, because a
reader who does the right thing — reads the banner before the body — is sent to the wrong answer with
extra confidence. That file is modified in the working tree by another seat right now; whoever holds
it should take this whole block.

⛔ **What none of this changes.** Every figure above is a **prediction-derived population-coverage
number** — MHCnuggets/MHCflurry calls pooled over AFND frequencies. The class-II arm is **one strong
call on one allele** from the predictor the vaccine manuscript itself grades as the weaker of the two,
and a coverage figure is a ceiling on eligibility, not evidence of immunogenicity, presentation,
efficacy or safety. Correcting `3` to `23` makes the **caveat** larger, not the result stronger: a
floor over 23 alleles that yielded one strong call is a **weaker** signal than a floor over 3 would
have been, because far more was tested for the same single hit.

---

## Ledger rows the driver should write

I may not write these. S13-VACCINE proposed rows 5 and 6; both should now be written as **done**,
with a new row for the mechanism, which is the part that is not fixed yet.

1. **Close S13's proposed row 5 (`hla-coverage.json` regeneration).** `kind: hardening`,
   `state: done`, `cost_class: free`, `last_evidence_utc: 2026-09-01`. Evidence: the artifact's
   `_class_ii_note`, byte-identical to `origin/modalities-cache@d7bfcaf28`. ⚠ The row's premise —
   *"the regeneration needs the AFND fetch, which is 403 at this sandbox's egress"* — is **false**
   and should be recorded as refuted, not merely closed: both source URLs answer 200 here.
2. **Close S13's proposed row 6 (`emc-systems-map.json` 3-vs-23).** `kind: hardening`,
   `state: done` for the graph source, **`state: queued` for the legacy reprojection** — the
   projection at `emc-systems-map.json:2475` is still open and belongs to whoever holds that file.
3. **NEW — "Enrol `hla_coverage.py --check` in `preflight.sh`'s generated-artifact gate."**
   `kind: hardening`, `state: queued`, `cost_class: free`, local, one line. **This is the only part
   of the mechanism fix that is not landed**, and without it the guard is recorded and unenforced.
4. **NEW — "An artifact on `main` is never compared against the copy its producing workflow
   published."** `kind: hardening`, `state: queued`, `cost_class: free`. `check_artifacts` asks
   whether a cited artifact **exists** on this branch; this defect proves existence is not currency.
   A cheap first version: for every `systems/graph/artifacts.json` row whose `published_to` names a
   branch other than `main`, `git diff` the two copies and report. Evidence: this file §4(i)/(iii),
   and the three-day gap it measures. ⭐ **Higher value than any single artifact fix**, because the
   docstring of `check_artifacts` records that 41 artifacts once lived only on `modalities-cache`.
5. **NEW — "The generated-artifact gate is a 17-row hand-kept allowlist over 591 producers in
   `research/modalities` alone."** `kind: hardening`, `state: queued`, `cost_class: free`. Not a
   proposal to enrol all of them — most have no `--check`. The proposal is to make *absence from the
   list* visible: a census of producers-with-a-`--check` that are not wired to the gate. Measured
   today: 74 producers under `research/modalities` define a `--check`; **4** are in the gate.
6. **NEW — "`research/manuscripts/neoantigen/hla-coverage-emc.md` §2.4/§2.5 and its correction
   banner state a superseded class-II panel, allele set, allele count and both-arms status."**
   `kind: hardening`, `state: queued`, `cost_class: free`, local, **needs the seat that owns
   `research/manuscripts/neoantigen/`**. Evidence: the table above.
7. **NEW — "The sprint's findings-file frontmatter convention fails
   `systems/schema/document.schema.json`; 147 `systems_check` errors, all in
   `research/autonomy/sprint-2026-09-01/`."** `kind: hardening`, `state: queued`, `cost_class: free`.
   `kind: process` is not in the enum; `purpose`, `scope`, `last_verified` are required; seven files
   have no frontmatter at all. **This will make the driver's `preflight.sh` red for reasons unrelated
   to any seat's work.**
