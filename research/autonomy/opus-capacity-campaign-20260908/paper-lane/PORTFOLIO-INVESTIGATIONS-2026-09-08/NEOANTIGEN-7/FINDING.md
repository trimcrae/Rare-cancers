---
id: DOC-NEOANTIGEN-7-FINDING
title: "NEOANTIGEN-7 — the 20 zero-NR4A3 junction peptides bounded: reproduced 20/20, absent from every EWSR1 sequence this checkout holds, and blocked on exactly 4 named EWSR1 isoforms the repository carries no sequence for"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# NEOANTIGEN-7 — a bounded UNKNOWN, sized exactly: **0 of 20 in the held set, 4 named isoforms missing, 1 residue is what the question turns on**

Lane `NEOANTIGEN-7`. Closes the open item NEOANTIGEN-6 left: the isoform status of the **20
zero-NR4A3** peptides. Builds on **NEOANTIGEN-3** (per-partner split for the 11 ranked binders),
**NEOANTIGEN-4** (8/174 zero-EWSR1; the four Q92570-3 proteome hits; the `PARENTS` guard defect),
**NEOANTIGEN-5** (the regression test for that repair) and **NEOANTIGEN-6** (the symmetric filter
that first counted the 20).

Writes confined to this directory. Nothing added, committed or pushed; no preflight; no manuscript,
graph, shared script or test edited; no subagents. **No network — $0.** Routes **B1/B2 were not
approached**: no isoform sequence was fetched, substituted, reconstructed, inferred from another
source, or guessed, and the question was not relabelled to get around them. B4/B8/B9 untouched;
R1/R2/R3/R4 not restarted. **No guard, floor, gate, matcher, pin or test is weakened, and none was
modified.**

⛔ Nothing here is an immunogenicity, presentation, tolerance, TCR-cross-reactivity, efficacy,
safety, selectivity, therapeutic-window or clinical-readiness claim, in either direction. **A
composition filter is not a novelty search, and neither is evidence about presentation.** Every
"absent" below means *absent from the sequences this checkout holds* — never *novel*.

## 1 · The question

> Without the closed route, what can be established about the 20 zero-NR4A3 junction peptides — and
> exactly what would it take to settle them?

A well-bounded **UNKNOWN** is the expected answer. It is the answer.

## 2 · Merit

NEOANTIGEN-6 removed 28 of 174 peptides symmetrically, but only the 8 zero-EWSR1 have a recorded
wild-type status (all four proteome hits fall inside them, NR4A3 isoform Q92570-3). The 20 are the
mirror class and carry the same structural risk: each is wild-type EWSR1 sequence plus a single
hybrid seam residue, so each one's junction-specificity rests on one residue. If any of them is
reproduced by an EWSR1 isoform, that peptide is not fusion-specific at the sequence level and no
future measurement on it could be attributed to the fusion. Before anyone spends a networked run on
it, the useful thing is to size the question precisely: how much of it is already answerable here,
how much is not, and what the missing input actually is.

## 3 · The exact evidence gap

NEOANTIGEN-6 §7 limitation 4: *"Whether the 20 zero-NR4A3 peptides occur in any recorded isoform is
UNKNOWN here — no isoform sequence is in this checkout and none was fetched."* That sentence names
no denominator. This lane converts it into a measured gap with a size, a name list and a stated
minimal input. Named inputs, all read in place: `fusion-breakpoint-neoantigens.json`
(sha256 `ae1ba4f7…`, `_utc` 2026-08-19T16:26:49Z), `fet-sequences-cache.json` (`0459ace2…`),
`nr4a-sequences-cache.json` (`66816f79…`), `junction-selfsimilarity.json` (`a59e22c9…`, generated
2026-08-23), `junction-proteome-novelty.json` (`ff1ccc2c…`), plus `../NEOANTIGEN-6/refiltered-panel.json`.

## 4 · Step 1 — the 20 reproduce, digit for digit, by two independent routes

Recomputed from the committed panel alone (`neoantigen7_zero_nr4a3_bounding.py`, `checks/01`), by
placing every `novel_peptide` in its junction's 21-residue `junction_context` (seam at index 10;
placement asserted **unique** and asserted to **cover the seam**, or the run fails):

| class | observed here | NEOANTIGEN-6 | agrees |
|---|---|---|---|
| distinct peptides | **174** | 174 | ✔ |
| zero from EWSR1 | **8** | 8 | ✔ |
| **zero from NR4A3** | **20** | 20 | ✔ |
| zero from both | **0** | 0 | ✔ |

**No discrepancy. `agrees: true`, `disagreements: {}`.** All 20 also appear verbatim in
NEOANTIGEN-6's own artifact (20/20).

A **second, method-independent derivation** (`neoantigen7_independent_derivation.py`, `checks/02`)
rebuilds the class without using context placement at all: a peptide is zero-NR4A3 iff its body
(everything but the last residue) is exactly the canonical EWSR1 window **ending at the panel's own
`donor_last_whole_residue`**, and its last residue is the junction's `seam_codon_residue`. Method 2
returns the **same 20**, `only_in_method1: []`, `only_in_method2: []`.

The 20, **4 per junction family**, all five in-frame junctions:

| junction | seam | peptides |
|---|---|---|
| `EWSR1_e7__NR4A3_e3` | N | `SSSYGQQN`, `QSSSYGQQN`, `QQSSSYGQQN`, `SQQSSSYGQQN` |
| `EWSR1_e9__NR4A3_e3` | D | `GGFNKPGD`, `RGGFNKPGD`, `ERGGFNKPGD`, `GERGGFNKPGD` |
| `EWSR1_e10__NR4A3_e3` | D | `EGPDLDLD`, `DEGPDLDLD`, `MDEGPDLDLD`, `PMDEGPDLDLD` |
| `EWSR1_e12__NR4A3_e3` | D | `AAVEWFDD`, `KAAVEWFDD`, `AKAAVEWFDD`, `TAKAAVEWFDD` |
| `EWSR1_e13__NR4A3_e3` | D | `MPPPLRGD`, `RGMPPPLRGD`, `GRGMPPPLRGD`, `GMPPPLRGD` |

None of the 20 is a ranked binder — the ranked arm's two removals were both zero-**EWSR1**
(NEOANTIGEN-6 §5.2). This is a peptide-arm question.

## 5 · Step 2 — what IS held, and what the held set decides

**The checkout holds exactly one wild-type EWSR1 sequence.** A repository-wide scan of every tracked
file under `research/` and `systems/`, excluding this campaign's investigation lanes
(`neoantigen7_isoform_gap_scan.py`, `checks/03`, `checks/04`):

| held wild-type EWSR1 | length | sha256 | where |
|---|---|---|---|
| canonical **Q01844** | **656 aa** | `50aceb523187df7b1de28f4831385e42ea889e02268107d81adcd59941fce8f9` | `fet-sequences-cache.json` → `EWSR1`, `nr4a-sequences-cache.json` → `EWSR1` (byte-identical), and the same string in `emc-construct-inputs.json` ×2 and one `emc-fet-construct-designs.json` wild-type control |

Seven other sequences begin with the canonical EWSR1 N-terminus (264, 360, 431, 472, 949, 1058,
1099 aa). Every one is a **designed construct** — truncated EWSR1 fragments, condensate constructs
and EWSR1::NR4A3 fusion designs. They are searched **separately** and are **never** counted as
wild-type evidence.

### Result — 0 of 20

| | n |
|---|---|
| verbatim in the held wild-type EWSR1 (canonical Q01844) | **0** |
| not present in the held set | **20** |

**A hit would have been decisive; a miss is only "not in the held set."** It is not novelty, not
absence from the human proteome, and not absence from any EWSR1 isoform.

**And the miss is a one-residue miss, which is the whole point.** For each of the 20, its
EWSR1-only prefix occurs in the held canonical sequence **exactly once** (20/20, single offset
each), ending precisely at that junction's `donor_last_whole_residue`. The residue that follows in
wild-type canonical EWSR1 is **G** for 16 of them and **S** for 4 — **never** the seam residue
(**D** ×16, **N** ×4). So every one of the 20 differs from held wild-type EWSR1 at exactly one
position, the last. The canonical search **could not** have hit, and its zero carries no
information about the isoforms: an isoform that terminated, or spliced onward with a D or N, at that
donor position would reproduce the peptide exactly. That is precisely the sequence class this
checkout cannot search — the same class that produced the only recorded non-novelty on the other
side (Q92570-3, NEOANTIGEN-4 §5.2).

**8 of the 20** do occur verbatim inside the designed EWSR1::NR4A3 constructs (`AAVEWFDD`,
`KAAVEWFDD`, `AKAAVEWFDD`, `TAKAAVEWFDD`, `MPPPLRGD`, `GMPPPLRGD`, `RGMPPPLRGD`, `GRGMPPPLRGD`).
That is **expected by construction** — those constructs contain the fusion seam this repository
designed — and is **not** evidence of wild-type occurrence. It is reported so nobody later
mistakes a construct file for a proteome.

### Controls (`checks/01`, `checks/06`)

* **Positive — passed.** `TSYDQSSYS`, planted verbatim from the held canonical EWSR1 at 1-based
  offset 201, **was found**, at offset 201. Had the searcher missed it, the 0/20 above would have
  been a bug report, not a result.
* **Negative — passed.** `WVFEDDAAW` (a deterministic scramble of `AAVEWFDD` plus a W) **was not
  found**.

Both are assertions, not remarks: the generator exits non-zero if either fails, or if the
reproduction disagrees.

## 6 · Step 3 — the blind spot, counted and named

**4.** The repository's own artifacts NAME four EWSR1 isoform accessions and carry **sequence for
none of them**:

| accession | protein name, as recorded in `junction-selfsimilarity.json` | sequence in checkout |
|---|---|---|
| **Q01844-2** | `EWS_HUMAN Isoform EWS-B of RNA-binding protein EWS` | **absent** |
| **Q01844-3** | `EWS_HUMAN Isoform 3 of RNA-binding protein EWS` | **absent** |
| **Q01844-5** | `EWS_HUMAN Isoform 5 of RNA-binding protein EWS` | **absent** |
| **Q01844-6** | `EWS_HUMAN Isoform 6 of RNA-binding protein EWS` | **absent** |

They are named in `junction-selfsimilarity.json` (as near-self hit accessions),
`junction-anchor-convention-sensitivity.json`, `p1-anchor-convention.json` and
`emc-condensate-window-eligibility.json`. Canonical `Q01844` is the only EWSR1 accession the
checkout can back with a sequence.

⚠ **4 is a lower bound, and must be quoted as one.** It counts the isoforms this repository's
artifacts happened to name — an isoform that produced no recorded near-self or exact hit would not
appear at all, and this checkout cannot enumerate UniProt. `Q01844-4` is conspicuously absent from
the list; whether it exists is **UNKNOWN here** and was not looked up.

## 7 · Step 4 — the exact minimal input that would settle all 20, and the stop

**Minimal sufficient input:** the amino-acid sequences of the named EWSR1 isoforms — **Q01844-2,
Q01844-3, Q01844-5, Q01844-6** (and any further EWSR1 isoform, given §6's lower bound) — followed by
an exact-substring search of the 20 against them, run exactly as
`junction-proteome-novelty.json` was run. Nothing less settles them: each of the 20 is EWSR1
sequence up to and including one hybrid residue, so its status depends entirely on what an isoform's
residues are **at and after** that donor position. No amount of canonical sequence, no near-self
table, and no composition rule can substitute — §5 shows the canonical answer is fixed by
construction and therefore uninformative.

**That input is behind routes B1/B2 (Ensembl / UniProt isoform FASTA), which are CLOSED for this
lane. STOP.** Not fetched, not proxied, not substituted with another source, not reconstructed from
exon models, not approached. The status of the 20 against EWSR1 isoforms is **UNKNOWN**, and this
lane leaves it that way deliberately.

## 8 · Artifact · validation · provenance · limitations · stop condition

* **Artifacts.** `neoantigen7-zero-nr4a3-bounding.json` (machine-readable: reproduction verdict, the
  20 with per-peptide junction, split, held-set search result, prefix offset and following wild-type
  residue; held-sequence inventory; construct inventory; both controls; the blind-spot list; the
  minimal input), `neoantigen7-independent-derivation.json`, `neoantigen7-isoform-gap-scan.json`;
  generators `neoantigen7_zero_nr4a3_bounding.py`, `neoantigen7_independent_derivation.py`,
  `neoantigen7_isoform_gap_scan.py`; `run_check.sh`; `checks/01–06`.
* **Validation / baseline.** Reproduction asserted against NEOANTIGEN-6's four counts and against
  its emitted peptide list (20/20); a second derivation by a different route returning the same 20
  with empty symmetric difference; unique-placement and seam-coverage assertions that fail the run;
  the required **positive** and **negative** controls, both passed and both fatal on failure; the
  existing 9 novelty tests re-run **unmodified** on the committed tree — **9 passed, exit 0**
  (`checks/05`); the generator re-run for determinism (`checks/06`, exit 0). Every exit code is the
  real one (`run_check.sh` records `$?` of an unpiped command). **No check failed in this lane; had
  one failed it would be here, unedited.** ⚠ `research/modalities/tests/conftest.py`'s
  `tracked_tree_guard` is a known non-concurrency-safe artifact that can fail at `sessionfinish`
  with an empty changed-file list while other lanes write (NEOANTIGEN-5 §7); it did not fire in
  `checks/05`, and it was **not** modified or worked around.
* **Provenance.** Every input read in place from this checkout; no copy, no worktree, no network,
  no GPU, no paid API, **$0**. `git status` shows no tracked file modified by this lane; no shared
  file needed changing, so no diff is proposed here (NEOANTIGEN-4/5/6's diffs stand as they are).
* **Limitations.**
  1. ⛔ No immunogenicity, presentation, tolerance, efficacy, safety, selectivity,
     therapeutic-window or clinical claim. The 20 are screen output; where they occur in wild-type
     sequence is a sequence question and nothing more.
  2. **0 of 20 is a statement about the held set only.** It is not novelty and must never be quoted
     as such. The 20 were never tested against any isoform, against TrEMBL, or against the
     42,547-sequence reviewed proteome used by `junction-proteome-novelty.json` — that artifact's
     own peptide-level records were not re-derived here either.
  3. §6's **4** is a lower bound on the isoform set (§6).
  4. Exact substring only; near-self and 1–2 mismatch neighbours are out of scope
     (`junction-selfsimilarity.json` covers only the 11 ranked binders, none of which is in the 20).
  5. The junction model, its five junctions and the 174 peptides are this repository's own; this
     lane inherits them and does not re-derive the transcript model.
* **Stop condition.** Reached, as set: the class is reproduced, the held set is exhausted, the gap
  is counted and named, and the minimal settling input is stated and confirmed closed. Nothing
  further was started.

## 9 · What a networked runner would do (not done, not authorised here)

1. Fetch the four named EWSR1 isoform sequences by the ordinary permitted route **when one is
   open**, and run the same exact-substring search over the 20. One run settles the class.
2. While doing so, re-run the full proteome-wide arm over all 174 peptides with the
   NEOANTIGEN-4/-5 `PARENTS` repair applied, so an EWSR1-side hit would actually trip the guard —
   which is the exact failure mode these 20 represent and the reason that repair matters.
3. Report the outcome beside NEOANTIGEN-6's re-filtered panel; do not merge composition and novelty
   into a single number.
