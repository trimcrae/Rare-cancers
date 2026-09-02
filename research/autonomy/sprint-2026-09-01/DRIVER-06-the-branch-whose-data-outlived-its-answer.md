---
id: DOC-SPRINT-DRIVER-06-S24-PARTIAL-RECOVERY
title: "The threshold-calibration branch: its 549-epitope headline is refuted by the trunk's own later script, and its data is the half worth recovering"
level: L3
kind: memo
status: live
purpose: "Record why origin/claude/s24-threshold-calibration was recovered path-scoped rather than merged, how close a whole-branch merge came to restoring a refuted result, and the trunk defect the recovery fixes — a corrected generator whose declared input existed on no ref of main."
scope: "One branch, seven commits, five files. Says nothing about what the corrected adjudication will return when it is re-run; that run has not happened and its verdict is UNMEASURED here."
audience: [autonomous research agents, maintainers]
date: 2026-09-02
last_verified: 2026-09-02
---

# DRIVER-06 — a branch whose data outlived its answer

**2026-09-02.** `origin/claude/s24-threshold-calibration`, 7 commits, newest of the 28 refs the
merge-debt hook reports. Read because the hook's step 1 says read one. **Merged path-scoped: two data
files recovered, the conclusion refused.**

---

## 1 · ⛔⛔ What a whole-branch merge would have restored

The branch's artifact reports **549 distinct experimentally validated fusion-junction epitopes**,
clearing a preregistered minimum of 30 and a preregistered CI-width ceiling of 0.2 (measured 0.0622),
with `the_set_is_a_calibration_set: true`. It closes §6.1 step 1 of the vaccine paper — the item whose
own specification says *"until this is done every figure in B1 is a point on a curve."*

Everything about that record reads like this repository at its best: the harder of two defensible
readings taken, the refused comparator carried and labelled *"⛔ NOT THE CALIBRATION"*, the MHCflurry
circularity declared with its direction argued, and a scope line refusing any claim of presentation,
immunogenicity, efficacy or clinical readiness.

**And the number is not a calibration set.** The trunk's own later version of the generator says so,
in a comment written after seeing that very run:

> ⛔⛔ THE INCLUSION RULE IS NOT THE PROBE, AND CONFLATING THEM PRODUCED A FABRICATED CALIBRATION.
> Measured on run 33556831052, the first run whose IEDB fetch actually succeeded: probing
> `parent_source_antigen_name ILIKE *fusion*` returned 6,108 rows and 988 scoreable peptide-allele
> pairs across 39 distinct antigen names — and **NOT ONE of them was a fusion-oncoprotein
> breakpoint.**

Its classification of the 988:

| n | what they actually are |
|---|---|
| 316 | ubiquitin / ribosomal-protein fusion proteins (UBA52, RPS27A, FAU — normal housekeeping) |
| 205 | poxvirus **entry-fusion** complex proteins (OPG083/086/094/095) |
| 180 | vacuolar fusion proteins MON1 / CCZ1 (membrane trafficking) |
| 162 | read-through / natural chimeras (CNK3-IPCEF1, PALM2-AKAP2, POM121-ZP3, ERCC6-PGBD3) |
| 69 | paramyxovirus **fusion glycoprotein** F0 |
| 30 | "TCF3 fusion partner" (TFPT — a gene *named* fusion partner; the antigen is wild type) |
| 9 | sperm–egg fusion proteins (Juno, IZUMO4, TMEM95) |
| 9 | bacterial (RND efflux **membrane fusion**, ABC transporter) |
| 8 | PML-RARA-**regulated** adapter molecule 1 (PRAM1) — regulated *by* the fusion, not the fusion |

★ **The bare word "fusion" is a homonym in protein nomenclature and carries no oncogenic meaning.**
The trunk's fix is a separation the branch did not have — *probe broadly for RECALL, adjudicate
strictly for PRECISION* — implemented as a `FUSION_EXCLUSIONS` list applied **first**, so a name
cannot be admitted by an accident of wording, plus a directed `FUSION_ONCOPROTEIN_PATTERNS` list as
the only automatic admission. A generic two-partner match is admitted only as
`two_partner_unverified` and is **not** counted without adjudication, because PALM2-AKAP2 and
POM121-ZP3 are exactly why.

⛔ **So merging the branch wholesale would have overwritten a corrected generator with the one that
produced the artifact, and installed a refuted 549 as the trunk's answer** — DRIVER-03's named
failure, *a superseded claim restored to apparent currency*, and the same one S39 refused for the
atlas. A commit message celebrating the 549 had already been drafted when the conflict surfaced it.

## 2 · ★ How it surfaced, and why the cheap check was the wrong one

`git diff origin/main...<ref> --stat` reported **5 files, 43,535 insertions, 0 deletions** — the
shape of a purely additive branch, which is the shape you merge without worrying. That is a
**three-dot** diff, computed against the merge base, and it cannot see what the trunk did *after* the
fork. The merge itself disagreed immediately:

```
CONFLICT (add/add): research/modalities/vaccine-threshold-calibration.json
CONFLICT (add/add): research/modalities/vaccine_threshold_calibration.py
```

⚠ **An `add/add` conflict is the tell that the additive reading was wrong**, and it is worth naming
because the three-dot stat is the standard way this repository's censuses summarise a branch. A file
"added by both sides" means the trunk grew its own version, and the only way to know whose is current
is to read both.

★ **The deciding observation was sizes, then contents, and the sizes pointed the wrong way**: the
trunk's script is *larger* (62,084 B vs 57,234 B) while the trunk's artifact is *smaller* (72,086 B
vs 570,327 B) and older by timestamp (20:31:04Z vs 20:43:30Z). Reading only timestamps says take the
branch. Reading the code says the opposite, because the trunk's artifact is the **withheld** record of
a run whose IEDB fetch failed —

> `verdict.finding` = WITHHELD. The IEDB fetch did not complete, so the size of the validated
> fusion-junction set was not measured on this run.

— and the trunk's *script* is the one written afterwards, against the branch's successful run. **The
trunk is ahead in code and behind in output. Neither file alone tells you that.**

## 3 · ⭐⭐ The trunk defect this recovery fixes

`research/modalities/vaccine_threshold_calibration.py:106` on `main` declares

```python
IEDB_CACHE = os.path.join(HERE, "iedb-validated-epitope-cache.json")
```

and `:752` offers `--use-cache`, *"reuse iedb-validated-epitope-cache.json instead of re-fetching"*,
with the header calling it *"the normalised IEDB records the calibration ran on, so it is auditable
and re-runnable without re-fetching."*

⛔ **That file existed on no ref of `main`.** `git cat-file -e HEAD:<path>` → ABSENT. The corrected
generator had a documented, load-bearing input that lived only on a stranded branch — so the
corrected adjudication could not be re-run, audited, or reproduced by anybody reading the trunk. §7's
*"never let a branch a workflow runs from be the only home of an artifact"*, in its most literal form:
the workflow **was** on main; its input was not.

⚠ And the fetch cannot simply be repeated here: `curl https://query-api.iedb.org/` returns
*"CONNECT tunnel failed, response 403"* at the egress proxy, and `import mhcflurry` is a
`ModuleNotFoundError` in this sandbox — both measured 2026-09-01 and both recorded in the script's own
header, which is why it is a CI job. **A lost cache is a lost fetch, not an inconvenience.**

## 4 · What was recovered, and what was refused

| path | action | reason |
|---|---|---|
| `research/modalities/iedb-validated-epitope-cache.json` | **RECOVERED** | 988 arm-F and 965 arm-N normalised records, `fusion_errors: []`, `general_errors: []` — the successful fetch. Keys match what the trunk's `--use-cache` branch reads (`arm_F_records`, `arm_N_records`, `dropped_fusion`, `dropped_general`, checked against `:837-844`). Raw data, not a conclusion. |
| `research/modalities/vaccine-threshold-calibration-schema-probe.json` | **RECOVERED** | the live IEDB schema the column resolution was derived from; 39 tables. Absent from `main`. |
| `research/modalities/vaccine_threshold_calibration.py` | **REFUSED — trunk kept** | the trunk's is the corrected generator; the branch's is the one that produced the fabricated set |
| `research/modalities/vaccine-threshold-calibration.json` | **REFUSED — trunk kept** | the branch's headline is the refuted 549. The trunk's WITHHELD record is *less informative and more honest*, and replacing it would be the restoration this repository has already paid for once |
| `.github/workflows/vaccine-threshold-calibration.yml` | already on `main` | no action |

★ **The data survives its own conclusion, and that asymmetry is the general lesson.** A refuted
*claim* must not be recovered. The *measurement* it was computed from is still a measurement — 6,108
IEDB rows fetched through a proxy that refuses the fetch here — and throwing it away because its
interpretation was wrong would have cost a fetch this sandbox cannot repeat.

## 5 · ⚠ What is now open, and what this memo does **not** claim

- **The corrected adjudication has not been run.** `--use-cache` makes it a $0 CI job with no
  re-fetch, and the workflow is on `main`. **UNMEASURED: what the corrected inclusion rule returns.**
  It is entirely possible the honest answer is that arm F is empty or far below the preregistered
  n = 30 — in which case §6.1 step 1 is settled by its *other* branch, which the specification
  explicitly permits: *"if no validated set restricted to fusion-junction peptides exists, that
  absence is itself the finding."* **That is a real outcome, not a failure**, and nothing here
  predicts which way it goes.
- ⛔ **Nothing in the vaccine manuscript is updated by this recovery**, and §2.3 / B1 still stand as
  written. Repointing them is a manuscript edit gated on a run that has not happened.
- The branch's other four commits (the schema probe, the column-name correction, and the commit
  refuting its own earlier diagnosis — *"the real cause of every 400 was `offset` without `order`"*)
  are process history. That refutation is the shape §4 asks for and is worth reading; it is not
  worth a merge, because the fix it describes is already in the trunk's script.
- **The branch is not deleted.** It remains the only home of its own commit history, and this memo
  is the written reading the merge-debt hook asks for in its option 3.

---

# Addendum — a cycle's own receipt was invisible to the gate that grades it

**Same session, found by working the merge-debt hook's list rather than the branch above.**

Five of the small stranded refs are graded **A** by `S38-BRANCH-CENSUS.md` — content measured as absorbed
into `main`. Verified independently here by set difference of tracked paths
(`comm -23 <(git ls-tree -r --name-only origin/<ref>) <(… origin/main)`):

| ref | paths on the branch and absent from `main` |
|---|---|
| `origin/seat/s1-aut-pd-130` | **0** |
| `origin/seat/s4-aut-045` | **0** |
| `origin/seat/s5-retest-blocks` | **0** |
| `origin/claude/aut-pd-130-s4-CYC-0074` | **1** — `research/autonomy/receipts/CYC-0073-d4ccfde4.json` |
| `origin/claude/aut-pd-147-s3-CYC-0074` | **1** — the same file |

## ⛔⛔ The one file was a receipt filed one directory too high, on `main`

`receipt_schema.RECEIPT_DIR` is `research/autonomy/receipts` — 110 files. `main` carried
`CYC-0073-d4ccfde4.json` at **`autonomy/receipts/`**, a top-level directory holding exactly one file,
which is not that path. So the receipt existed, was committed, and **no instrument could see it**: not
`receipt_schema.problems`, not the fan-out width census, not `health.py`'s `fanout_is_governed`.

★ **And it is precisely the receipt those instruments most needed.** Its `subagents` block reads
`max_concurrent: 2, total: 2` and carries a `_corrected` note whose finding is general:

> ⛔ THIS RECEIPT FIRST RECORDED max_concurrent 0 AND THAT WAS TRUE WHEN WRITTEN AND FALSE WITHIN THE
> HOUR. The receipt is written at step 10 and the seats were dispatched after it, so the field aged out
> silently. … `receipt_schema.py` verifies the field is PRESENT and correctly NAMED, never that it is
> still TRUE.

Its `what_i_got_wrong` also records a seat's `claim.py` pushing the driver's gated-but-unpushed `main`
commits to the trunk, creating two merge commits **no gate ever saw** — noticed only because the
driver's own later push was rejected as already-there. That is a governance incident whose only written
home was a file no census could read.

⚠ **The branch's copy is the EARLIER draft** (`max_concurrent: 0`, the shorter `what_i_got_wrong`);
`main`'s misfiled copy is the corrected one. So this is not a recovery from the branch — the content
was already on the trunk. **The defect was purely the path**, which is the more dangerous shape: a file
that is committed, current and correct, and invisible.

## What was done

Moved to `research/autonomy/receipts/CYC-0073-d4ccfde4.json`; the stray `autonomy/` tree is gone. The
census now reads **111** receipts and `receipt_schema.problems` returns none for it.

⚠ **Not done, and stated rather than quietly skipped:** the five refs above are now deletable on the
evidence — but deletion is irreversible and S38's grade A rests on "13–82 % line absorption with the
remainder being ledger/JSON reserialization". **13 % absorption is not full absorption**, and no reading
here has established that the unabsorbed 87 % on the low-absorption ref is truly reserialization noise.
Path-level absence is necessary and not sufficient. The deletion is left as its own act, needing that
line-level reading first.
