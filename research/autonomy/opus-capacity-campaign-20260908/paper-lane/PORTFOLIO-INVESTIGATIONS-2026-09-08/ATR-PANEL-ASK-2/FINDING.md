---
id: DOC-ATR-PANEL-ASK-2-FINDING
title: "What is the right repair for the PGR drift in emc_fet_construct_designs.py --check?"
level: L4
kind: investigation
status: live
lane: ATR-PANEL-ASK-2
date: 2026-09-09
last_verified: 2026-09-09
scope: >-
  Settles which of three candidate repairs is correct for one reporting defect and delivers the
  repair as an unapplied diff. It applies nothing, runs no producer with --write, weakens no check,
  and takes no position on release. It loosens nothing on the PUB-ATR release hold and is not an
  argument for release.
---

# ATR-PANEL-ASK-2 — settling the `PGR` drift, without making the repair

## Question

`research/modalities/emc_fet_construct_designs.py --check` exits 1 with
`DRIFT in: ['gene_models', 'ensembl_vs_uniprot_sequences']`, while §2.5 of
`research/manuscripts/dependency/emc-atr-collaborator-package.md` states that command prints
`REPRODUCES`. **Is `PGR` really the sole difference, where did `PGR` come from, and which of three
repairs — regenerate the artifact, scope the producer's cache read, or correct only the prose — is
the right one?**

## Merit

The defect is small and the wrong repair is not. Two of the three candidates change a shared
producer or a committed artifact that four other modules and a manuscript's cited hash depend on;
one of them would additionally blind a working drift detector. Choosing between them is exactly the
kind of decision that is cheap to get right once and expensive to get wrong quietly. Patient
relevance is indirect: this artifact holds the construct designs a collaborating laboratory would
build from, and a repository that repairs its detectors instead of its disagreements stops being
able to tell a stale design from a current one.

## Evidence gap addressed

ATR-PANEL-ASK-1 localised the drift to `PGR` and stopped, correctly, because repairing it touches a
shared producer or a committed artifact. It left two things undone and named them: **the provenance
of `PGR` in the cache was not established**, and **no decision was made between the candidate
repairs**. This lane closes both, and independently re-verifies the localisation rather than
inheriting it.

## Step taken

### 1 · Reproduced, and re-localised independently — `PGR` is the only difference

`checks/01-reproduce-drift/` reproduces the failure digit for digit:

```
$ python3 research/modalities/emc_fet_construct_designs.py --check
DRIFT in: ['gene_models', 'ensembl_vs_uniprot_sequences']
EXIT=1
```

`checks/02-independent-localisation/` re-derives from the cache with a freshly written comparator
(not ASK-1's) and walks **all 17 top-level keys**, including `_limits`, which `--check` itself
excludes. Result:

* 15 keys `SAME` — `_title`, `⛔_STATUS_OF_EVERYTHING_BELOW`, `_assay_this_serves`, `_method`,
  `gene_model_self_checks_all_pass`, `_self_check_keys_aggregated`,
  `nr4a3_landmarks_read_from_the_audit`, `constructs`, `n_constructs_in_frame`,
  `n_constructs_total`, `partners_with_no_sourced_transcript_junction`, `wild_type_controls`,
  `rgg_dose_calibration_and_predictions`, `tcf12_negative_control`, and `_limits`.
* 2 keys `DRIFT` — `gene_models` and `ensembl_vs_uniprot_sequences`.
* Within both, a recursive structural diff reports exactly one path each:
  `ONLY-IN-RECOMPUTED /PGR`. **No `VALUE` difference, no `LEN` difference, and no
  `ONLY-IN-COMMITTED` path anywhere in the artifact.**

A control settles it positively rather than by absence. Deleting `PGR` from the loaded cache and
re-deriving gives:

```
DRIFT AFTER REMOVING PGR FROM INPUTS: []
EXACT EQUALITY (all keys except _limits): True
_limits equal: True
```

**So `PGR` is not merely the only difference found; it is the whole difference.** The cache holds
seven genes (`EWSR1, TAF15, FUS, TCF12, TFG, NR4A3, PGR`); `emc_fet_construct_designs.GENES` names
six, `PGR` not among them.

The other two §2.5 commands pass, as ASK-1 reported: `emc_fet_frame_and_composition.py --check`
prints `REPRODUCES` at exit 0 (`checks/04`), `emc_fusion_frame_figure.py --check` prints
`PROVENANCE MATCHES` at exit 0 (`checks/05`).

### 2 · Provenance of `PGR` — established from the repository's own records, and it is correct

Not UNKNOWN. The entry carries its own provenance fields, written by the code that created it:

| field | value |
|---|---|
| `_added_by` | `research/modalities/pgr_transcript_fetch.py` |
| `_fetched_utc` | `2026-08-15T13:39:56Z` |
| `_ensembl_gene_id` | `ENSG00000082175` |
| `transcript` / `translation` | `ENST00000325455` / `ENSP00000325120` |
| `_ensembl_description` | `progesterone receptor [Source:HGNC Symbol;Acc:HGNC:8910]` |
| `_why` | "5' partner of the PGR::NR4A3 fusion reported in PMID 36103645 — the only reported EMC case with this partner. Fetched because no transcript model for PGR existed in this repository, so the junction could not be built at all." |

Four corroborating records agree:

1. **`research/modalities/pgr_transcript_fetch.py`** exists for exactly this, and its header states
   why it is a separate script rather than a seventh entry in `GENES`: that module's `--refresh`
   "re-fetches EVERY gene and rewrites the whole file with a new `_fetched_utc`", which would
   overwrite the six models `junction_aso._diff_live_against_cache` compares live reads against —
   "which converts a detectable re-annotation into an invisible one". The script is additive by
   construction, refuses to overwrite a gene already present, and leaves the file-level
   `_fetched_utc` alone. The cache's file-level `_fetched_utc` is still `2026-08-12T13:41:57Z`,
   which is consistent with that design and is itself evidence the merge behaved as documented.
2. **`.github/workflows/fusion-cpu-extras.yml`** (job `pgr_transcript`) is the CI route that ran it,
   with the same rationale in its comments and a post-merge confirmation step that loads the record
   through `junction_aso` and prints the provenance gate used.
3. **The four required self-checks are recorded True** on the entry —
   `exon_lengths_sum_equals_cdna`, `coding_nt_sum_equals_cds`, `cdna_slice_at_utr5_equals_cds`,
   `cds_translation_equals_protein` — and `python3 research/modalities/pgr_transcript_fetch.py
   --check` passes at exit 0 (`checks/03-pgr-fetch-check/`), reporting
   `ENST00000325455 — 13037 nt cDNA, 2802 nt CDS, 933 aa, utr5=743 nt, 8 transcript exons`.
4. The scientific reason is real and is not this paper's: PMID 36103645 / PMC9489176 reports a
   PGR::NR4A3 EMC, and `hormone-partner-lane.json` owns that single-case count.

**Verdict: `PGR`'s presence in the shared cache is correct.** It is a deliberate, documented,
self-checked, additive later addition for a different fusion lane — not contamination, and not
something to remove. Its absence from the artifact is equally correct: the artifact was built before
2026-08-15 from a six-gene cache, and this paper's Supplementary Table S1 declares five gene models.
**Nothing is wrong with either file. The disagreement between them is real, and `--check` is
reporting it accurately.**

### 3 · The decision, with argument

**(a) Regenerate the artifact so it includes `PGR` — WRONG, and it would break true statements.**

The artifact `research/modalities/emc-fet-construct-designs.json` is sha256
`726aae02ae38b41c34d4398363e3581cfc9e4602d0fe9d65906a4fba79c2048b`. That hash is **cited in the
manuscript at line 787** and recorded in `research/modalities/fus-ddit3-prefix-comparison.json` and
in seven autonomy cycle-outcome records. Manuscript line 731 additionally states the artifact "was
produced by GitHub Actions run 30857647907". Regenerating it here would falsify the cited hash and
replace a CI-produced artifact with a sandbox-produced one, so a repair aimed at one false sentence
would manufacture two more. It also widens the artifact past what the paper describes: it would add
a `PGR` gene model, and an `ensembl_vs_uniprot_sequences` row whose `uniprot_len` is `null` and
`identical` is `false` (no UniProt accession for PGR exists in `UNIPROT`), into an artifact whose
paper declares five gene models and four constructs. **And the change would not stick.** The CI step
that maintains this artifact (`.github/workflows/depmap-dependency.yml:143`) runs `--refresh` first,
which rebuilds the cache from `GENES` — six genes, no `PGR` — so the next scheduled run deletes
`PGR` from the cache and the drift reappears with its sign reversed.

**(b) Scope the cache read so the producer ignores `PGR` — WRONG, and it is the forbidden shape of
repair.** Filtering `derive`'s `gene_models` to `GENES` would make `--check` print `REPRODUCES`
while the underlying disagreement is untouched. That is special-casing the detector to make it pass.
It is also the exact failure `pgr_transcript_fetch.py`'s own header names: it converts a detectable
input change into an invisible one. The artifact's `gene_models` block is the record of which inputs
the artifact was built from; blinding it removes the only signal that would show a future additive
cache change — including, concretely, the `--refresh` step above silently destroying the `PGR`
record that a different lane's CI job spent five outer retries fetching. **A producer whose
`--check` fails here is telling the truth.**

**(c) Leave both files and correct §2.5 — RIGHT.** Nothing in the cache is wrong, nothing in the
artifact is wrong, and the detector is working. The single false object in the repository is the
manuscript sentence. Correcting it has **zero blast radius**: the artifact's cited sha256 stays
true, its Actions-run provenance stays true, the four modules that read it
(`emc_fet_frame_and_composition.py`, `emc_condensate_calvados.py`,
`emc_prmt5_substrate_motif_map.py`, `fusion_cofold_recut.py`) and their committed artifacts are
untouched, and `--check` keeps its meaning: *the artifact and its current inputs disagree, and here
is where*. The cost is that a reader running the command gets exit 1 — which is why the correction
must state the expected output and its cause, not merely delete the word `REPRODUCES`. This is not a
blocking failure: the CI step at `depmap-dependency.yml:148` is explicitly non-blocking
(`|| echo "construct-designs --check reported drift; non-blocking, but READ IT"`), and no preflight
gate or test runs this command.

**What `--check` means under each option.** Under (c) it means what it says. Under (b) it means "the
subset of inputs I still look at agrees", which reads identically and is weaker. Under (a) it means
the same as (c) but only until the next `--refresh`, after which it means the opposite.

⭐ **A latent defect found while deciding, reported and not repaired.**
`.github/workflows/depmap-dependency.yml:143` runs `emc_fet_construct_designs.py --refresh`, whose
`fetch_inputs` iterates `GENES` and rewrites `emc-construct-inputs.json` wholesale. `PGR` is not in
`GENES`. **The next run of that workflow will delete the `PGR` model from the shared cache**, and
the `--check` on line 148 will then print `REPRODUCES` — so the loss would be masked by the very
step that would otherwise report it. This is a separate defect in a shared workflow, outside this
lane's write scope and outside its brief; it is recorded here for its owner. It is also an
independent argument against (b), which would mask the same loss permanently.

## Artifact

* [`reproduction-claim-2.5.patch`](./reproduction-claim-2.5.patch) — **UNAPPLIED** unified diff,
  the recommended repair. It replaces §2.5's false clause with the true current output, names
  `PGR` and `pgr_transcript_fetch.py` as the cause, states that every other key re-derives
  identically so no scientific value is affected, and retains the superseded wording verbatim
  behind a `⛔ CORRECTED 2026-09-09` marker.
* **No regenerated artifact is delivered**, because option (a) is not recommended. No producer was
  run with `--write` or `--refresh`.
* Under the recommended option the repair **is** the §2.5 prose correction, so the deliverable
  required by instruction 5 and the deliverable required by instruction 4 are the same file.
* `checks/01` … `checks/09` — every execution attempt, including the harness failure at `09`.

## Validation

* `git apply --check --verbose` on the diff: **exit 0** (`checks/06-git-apply-check-2.5/`).
* `git apply --check` on **ASK-1's `unsupported-ask-claims.patch` and this diff together**: **exit
  0** (`checks/07-both-patches-coexist/`). The two lanes' hunks do not overlap and both may be
  applied; ASK-1's is the earlier-numbered set of hunks in the same file.
* Tree unmodified: `git status --porcelain research/manuscripts/ research/modalities/` returns
  empty, exit 0 (`checks/08-tree-clean-verify/`).
* The localisation carries its own positive control — removing `PGR` from the inputs yields exact
  equality on all 17 keys — so a comparator that silently reported "no difference" is excluded.

## Provenance

All values read 2026-09-09 from this checkout, offline; no network call was made or attempted.
`PGR`'s provenance is read from the cache entry's own `_added_by`, `_fetched_utc`, `_why` and
Ensembl identifier fields, from `research/modalities/pgr_transcript_fetch.py`, and from
`.github/workflows/fusion-cpu-extras.yml`. ⚠ The commit-level history is **not** a usable source
here: `git log` on `emc-construct-inputs.json`, `emc-fet-construct-designs.json` and
`pgr_transcript_fetch.py` all return the single squashed merge `14a3f172d` (2026-09-04, `-s ours`),
so **the date and agent of the merge are established from the in-file records and the CI workflow,
not from commit history.** The PMID 36103645 attribution is quoted from the repository's own files;
no literature retrieval was performed in this lane.

## Limitations

1. **This decides a repair; it does not make one.** Nothing was applied, no producer was run with
   `--write` or `--refresh`, and no shared file was edited.
2. **It establishes nothing about EMC biology.** No efficacy, safety, selectivity,
   therapeutic-window or clinical-readiness question is touched, and none could be by this work.
3. **`PGR`'s biological correctness is not re-verified here.** What is verified is that its record
   is internally sound (four self-checks True), that its origin is documented, and that its presence
   in the cache is deliberate. Whether Ensembl's current annotation still matches
   `ENST00000325455` was not checked; no network read was attempted.
4. **The `--refresh` defect at `depmap-dependency.yml:143` is reported from reading the workflow,
   not from observing a run.** No workflow was dispatched. Its owner should confirm before acting.
5. **Commit-level provenance is unavailable** for the reason given above, and this is a real gap:
   if the in-file `_added_by`/`_fetched_utc` fields were ever wrong, nothing in this checkout would
   contradict them.
6. ⛔ **Nothing here bears on the PUB-ATR release hold, and nothing here is an argument for
   release.** The recommended change is a prose correction to a reproduction instruction; it clears
   no gate, satisfies no publication-bar clause, and asks for no release decision.
7. **A shell failure interrupted this lane.** Four consecutive Bash calls returned no output because
   the harness's own temp filesystem reached 0 MB free (`checks/09-enospc-incident/`). Per
   CLAUDE.md §8 nothing was deleted to free space; the affected read was completed with a
   non-shell tool and the condition later cleared. It is reported here as a resource problem for
   its owner, not as a resolved one.

## Stop condition

Reached. The drift is reproduced and independently re-localised to `PGR` with a positive control;
`PGR`'s provenance is established as a correct, documented, additive 2026-08-15 fetch; the three
candidate repairs are decided with their downstream consequences named; and the recommended repair
is delivered unapplied and proved at `git apply --check` exit 0. What remains — applying the diff,
and fixing the `--refresh`/`GENES` interaction that will delete `PGR` from the shared cache —
belongs to the paper owner and the workflow's owner respectively, not to this lane.
