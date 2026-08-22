---
id: DOC-EMC-VACCINE-PATH-REDTEAM-ROUND1
title: "Round 1 red-team of the EMC fusion-junction vaccine preprint"
level: L3
kind: memo
status: live
canonical_for:
  - what round 1 of the vaccine-path hardening cycle found, verified and refuted
purpose: >
  The record of the first adversarial review PUB-VACCINE-PATH has ever had: five blind seats on one
  pinned commit, what each filed, what survived verification against the artifacts, what was refuted,
  and what the repairs cost in words. It exists so that a later round does not re-run this one from
  scratch and does not re-raise its refuted charges.
scope: >
  Process and findings only. Every scientific figure it names has its home in the manuscript or in the
  artifact cited beside it; none is defined here.
audience: [maintainers, external reviewers]
related: [DOC-EMC-VACCINE-DEVELOPMENT-PATH, DOC-EMC-VACCINE-PATH-STOPPING-RULE]
date: 2026-08-22
last_verified: 2026-08-22
---

# Round 1 — the first adversarial review of the vaccine paper

**Pin:** `987c50f205c980c6f0a8202ff9bd9c57f14c23da`. Every seat read that SHA and nothing else.
**Subject:** [`emc-vaccine-development-path.md`](./emc-vaccine-development-path.md).
**Budget, declared before the seats launched:** main text not to exceed its size at the pin, 7,154
words. Corrections to replace text, never append. No bound to be removed to hit the target without
being named. Outcome in §5.

## 1 · The prediction this round was registered against

The [stopping rule](./emc-vaccine-path-stopping-rule.md) was written before any seat returned and
carried one falsifiable prediction: *round 1 will file at least one blocker, and the highest-yield
seat will be the instrument-coverage lens rather than any prose lens.*

**Half right, and the wrong half is the interesting one.** Round 1 filed blocker-grade charges from
**all five** seats. The instrument seat did find the guard gap it predicted — no test in the
repository bound any number in this paper to any artifact — but the highest-yield seat was
**arithmetic**, which found that the paper's most-quoted number is a ten-allele result described as
though it came from the 34-allele panel the paper names. A prose lens reading the artifacts beat the
lens whose whole job was coverage. Recorded as a miss.

## 2 · Seats and yield

| seat | lens | blockers | P1 | what it was for |
|---|---|---|---|---|
| 1 | arithmetic re-derived from committed artifacts | 1 | 4 | every printed numeral recomputed from the file that produces it |
| 2 | statistics and experimental design | 4 | 4 | what each interval and each threshold actually bounds |
| 3 | citations, provenance and the build | 7 | 4 | every identifier traced to a fetch record, or not |
| 4 | hostile referee | 5 | 5 | one verdict, with reasons |
| 5 | instrument coverage and claim strength | 4 | 13 | which guards name this document, and which falsely report that they do |

Seat 4's verdict was **REJECT**.

★ **Independent convergence, which is this loop's strongest signal.** Four findings were reached by
seats that could not see each other: the unqualified coverage claim (seats 1, 2 and 4, from
arithmetic, from the code and from reading); the class II arm reported as a result (seats 1, 2 and 5,
plus the synthesis pass, from the artifact, from the script's own note and from a cross-document
sweep); the two self-declared unverified references (seats 3, 4 and 5); and the unfilled author block
(seats 3 and 4).

## 3 · What survived verification

Every charge was re-derived against the artifact before any prose moved. The findings that stood, and
the observation that settles each, are recorded in the manuscript's own
[Appendix B](./emc-vaccine-development-path.md#appendix-b-statements-withdrawn-by-the-first-adversarial-review-of-this-manuscript),
which is the reader-facing half of this ledger. In summary form, by class:

- **A headline number described against the wrong instrument.** `8.51%` and "presented on HLA-B\*15:01
  alone" are ten-allele-screen facts; the committed 34-allele screen finds the same lead peptide
  strong on a second allele, and the junction's coverage re-derives to 12.3%. §5 of the paper
  meanwhile told the reader the panel was 34.
- **Two figures presented as different quantities that are one quantity at two panel widths.** 27.4%
  and 30.4% differ by exactly one allele.
- **Intervals bounding a model their own input refutes**, and a **"ceiling" the paper's own §§5–6 say
  is not one**, and a **"does not attain 50% at any panel size"** for which no search over panel sizes
  exists and which the same artifact contradicts regionally.
- **A not-computed value reported as a null result**, against the explicit note of the script that
  produced it.
- **A contribution claim resting on quotations from this author's own route ledger**, unattributed,
  with the symmetry it asserted not supported on the vaccine side.
- **Seven citation defects**, including a title paraphrased so that a study of placenta and colorectal
  cancer reads as an EMC finding, a press release with no record anywhere in the repository as the
  sole support for the paper's opening claim, a phase 3 result cited to a phase 2b paper, two entries
  reading "[citation to verify]", and four references never cited in text.
- **A false reproducibility claim**: "regenerated in continuous integration" of artifacts whose
  workflow is dispatch-only, `continue-on-error` at every step, and writes to a cache branch.
- **An unfilled author block** in a document being prepared for posting.

## 4 · Refuted, and recorded so a later round does not re-raise them

- **REFUTED: that the paper quotes retracted-seam values.** The roadmap's account of
  `⛔_RETRACTED_SEAMS` describes the pre-correction state. The artifact was regenerated
  2026-08-19 on transcript coordinates, carries no retraction block, and its grade counts sum to the
  27 declared exon pairs. `fusion-neoantigen-retraction.json` records the breakpoint artifact as
  `CLEARED`.
- **REFUTED as filed, and re-filed sharper: seat 4's account of the B6 symmetry.** The seat was right
  that the quotations are the author's own notes, and wrong that the vaccine's ledger entry is simply
  mis-described: it is `on_board`, parked on immunogenicity, and its standing blocker names a weak
  peptide-HLA as well as a cold tumour. The repair follows the sharper reading.
- **A near-miss from CI, caught before it entered the manuscript.** A Crossref bibliographic query for
  the class II predictor returned a pan-specific class I binding paper — a plausible, wrong answer in
  quotable form. It was not used. Reference 12 states that no record exists rather than supplying one.

## 5 · The budget, and where it landed

**Main text at the pin: 7,154 words. After application: 8,415.** The budget was exceeded, and the
excess is named here rather than met by cutting evidence.

| component | at pin | after | why |
|---|---|---|---|
| argument prose (Abstract, §§1–7) | 6,608 | 6,898 | **+290**, and every word of it is a newly stated bound: the panel disclosure, the threshold-sensitivity ladder, what the class II negative does and does not bound, and the eligibility-adjusted accrual arithmetic |
| references (§10) | 356 | 773 | **+417.** Eleven stub entries, two of them literally "[citation to verify]", became fourteen complete ones with authors, journal, volume, pages, DOI and PMID |
| declarations (§9) | 47 | 388 | **+341.** One sentence became the AI-use, data-availability, competing-interests, funding, ethics and not-clinical-guidance statements a preprint server expects |
| reproducibility (§8) | 86 | 239 | **+153**, the correction of a false claim into a true and specific one |

⛔ **To reach 7,154 exactly, a bound would have had to come out** — the threshold-sensitivity ladder,
the class II bounding paragraph, the accrual arithmetic, or complete bibliographic entries. Per the
hardening rule, removing one to hit a length target is itself a finding, so none was removed and the
overage is reported instead. §§1, 5 and 6 were each cut below their size at the pin (−224, −252, −71),
and the cuts taken were duplication, derivation and meta-commentary only.

⚠ **The growth is nevertheless the failure mode this cycle exists to prevent**, and round 2 should
open with a budget stated as *argument prose only*, measured against 6,898, so that apparatus growth
and prose inflation cannot be confused again.

## 6 · Instruments built or widened this round

Every one closes a gap seat 5 measured rather than assumed.

- **[`tests/test_vaccine_path_numbers.py`](../tests/test_vaccine_path_numbers.py)** — the first guard
  of any kind for this document. Binds ~30 figures to the artifacts that produce them, at **every
  site that states each**, not "is the value in here anywhere".
  ⭐ **Mutation-tested: 41 of 41 corruptions caught, 0 missed, 0 skipped**, including every
  single-site case. Three blind spots were found by that run and closed — an accession checked by
  membership, one of two class II affinities, and a prose claim no assertion actually read.

  ⚠ **And it caught two errors in prose written this round, which is the point of building it during
  the round rather than after.** The first: the manuscript said the surviving calls lie within 0.13
  percentile units; the span is 0.125 exactly, and two-decimal rounding lands on a half-way case, so
  the guard reads three decimals. The second was mine and worse, found on a final read-through rather
  than by any seat — **two different quantities were being called by one number.** The span between
  the weakest and strongest surviving call is 0.125; the distance from the acceptance threshold down
  to the weakest call is 0.1264. A sentence saying "within 0.125 of the acceptance threshold" is
  therefore false, and the claim that a 0.125-unit move takes coverage to zero is false too: a cut
  moved by 0.125 lands at 0.375, and the weakest call at 0.3736 still passes there. Both quantities
  are now stated separately, and the guard binds each to the sentence that states it — the conflation
  would otherwise have been enforced as if it were consistency.
- **[`pinned-figures.json`](../pinned-figures.json)** — the paper registered as a target, and the four
  values this round retracted registered as superseded, in the same commit that retracted them, per
  CLAUDE.md rule 1.3. Probe-tested in both directions: each retired construction is caught if
  reintroduced, and the corrected sentence that contains the same allele name is not flagged.
- **[`lint_changed_prose.py`](../lint_changed_prose.py)** — the paper added. Its own comment records
  that the ASO journal article entered round 8 with this gap; this document entered round 1 with it.
- **[`build_submission_pdf.py`](../build_submission_pdf.py)** — an entry, so the PDF guard family can
  reach a manuscript being prepared for deposit.
- **[`verify-refs.yml`](../../../.github/workflows/verify-refs.yml)** — ten DOIs added to the
  CI-enforced list. All ten resolved at Crossref with titles matching expectation, including the one
  that confirms reference 8's title names placenta and colorectal cancer.
- **Two sibling manuscripts corrected.** `hla-coverage-emc.md` and `fusion-junction-neoantigen-paper.md`
  both stated in the present tense that the class II arm was withheld pending regeneration — false of
  the committed artifact, and invisible to every instrument. This is the eighth instance of the
  one-of-a-pair defect class, and the first found by asking which *documents*, rather than which
  guards, state a status.
- **⭐ Five generality defects in the PDF builder, found only because a second kind of paper entered
  it.** `build_submission_pdf.py` had been written against one shape of manuscript and encoded that
  shape as a requirement: it read `paper["tables"]` and `paper["references"]` unconditionally, so a
  paper with inline references crashed on `os.path.join(HERE, None)`; it dropped a "## Tables" and a
  "## Figure legends" section that a table-less, figure-less paper does not have; its
  first-section anchor was `^##\s+1\s`, which a manuscript numbering sections "## 1." cannot match;
  and its back-matter split looked for the exact string `<h2>Declarations</h2>`, which "## 9.
  Declarations" does not produce. None of these was a fault in the new paper. Each is now conditional
  on what the paper declares, with the strictness kept where it earns its keep — a paper that HAS
  tables still fails the build if its heading is renamed. ⚠ The registration also revealed that the
  builder requires a running title and a keyword list; both were added to the manuscript, and they
  are things a preprint should carry anyway.

## 7 · What round 1 did not close

- ~~**Reference 12 has no bibliographic record.**~~ ✅ **CLOSED the same day, and the way it closed is
  the finding.** I filed this as a blocker on the strength of ONE Crossref `query.bibliographic` that
  returned a near-miss. Refusing that near-miss was right — a wrong citation arriving in quotable form
  is the most dangerous kind, and §5 of this ledger is about exactly that. Concluding from it that the
  reference was unobtainable was not right: one failed query is a search abandoned, not evidence of
  absence, and this repository's own standing rule says a blocked row is usually waiting on a $0
  fetch. ⛔ **"Blocked" was a claim I made without the evidence to make it.**
  The repair was a by-NAME search across two corpora that prints every candidate WITH its title and
  accepts only a title containing "MHCnuggets" — the title decides, not the ranking, which is the
  specific trap the first attempt fell into. It resolved on the first run: Shao XM, Bhattacharya R,
  Huang J, et al., *High-throughput prediction of MHC class I and II neoantigens with MHCnuggets*,
  Cancer Immunology Research 2020, doi:10.1158/2326-6066.CIR-19-0464, PMID 31871119. Europe PMC
  returned the journal record; Crossref returned only the 2019 preprint and figshare "Data from"
  derivatives, which is why the two-corpus search mattered. The DOI is now in the CI-enforced
  `FIXED_DOIS` list, the record is in the literature metadata, and both identifiers are in the
  provenance ledger as `verified`.
- **The class II artifact records no tool version or models release**, where the class I artifact
  records both. A reproducibility gap stated in the paper rather than papered over.
- **Reference 9 is a company announcement with no identifier of any kind.** It is labelled as one and
  cited only for the fact of the announcement, which is the most that can honestly be done with it.
- **The seat-5 P1s on `blast_radius.py`, `submission_metrics.py` and `submission_packet.py`** — all
  ASO-only, all still ASO-only.
- **A process defect of my own, recorded rather than hidden.** I applied prose repairs while seat 5
  was still reading, and it reported the tree drifting under it. It reviewed the pin correctly and its
  findings stand, which is exactly what the pin discipline is for — but the rule is that the tree
  holds still until every seat is in, and I broke it. I also committed once before running preflight.

## 8 · Sandbox dependencies this round had to install, and what each was gating

Recorded because each looked like a repo failure for the length of one diagnostic, and the next
session should not re-derive them. None was a defect in this repository; every one of these tools
refused cleanly rather than emitting a fabricated artifact, which is why they were cheap to diagnose.

| package | what was red without it |
|---|---|
| `jsonschema` | `systems_check.py`, i.e. preflight gate 2 — the very first thing that ran, before any review work |
| `pytest` | every test in the repository |
| `pdfminer.six` | the PDF text-layer guard family, which fails rather than skipping when it cannot import |
| `cryptography` (reinstall) | a `pyo3` panic in the Debian-packaged build, reached through `pdfminer.six` |
| `pypdf` | the PDF build itself, which refuses rather than shipping a PDF whose metadata names headless Chrome |
| `biopython` | `junction_aso_thermo.py`, which refuses rather than hand-entering a nearest-neighbour table |
| `scipy`, `rdkit`, `boto3`, `matplotlib` | 42 modalities tests — see below |

⚠ **And one thing that was not a dependency at all.** `aso_priorart_evidence.py` failed in the
regeneration chain because `origin/literature-cache` was not fetched in this container. The script
names the exact fetch command in its refusal. A chain step that fails for a missing REF rather than a
missing package reads identically at the summary line, which is the reason to read the step's own
message rather than the chain's verdict.

### ⭐ The 42 that looked like this round's breakage and were not

`PREFLIGHT_FULL=1` returned **42 failures not in the sandbox baseline**, all in
`research/modalities/tests` — degrader, docking, FEP, Vast-supervision and slow-CV lanes, none of
them within a hundred files of this manuscript. The tempting reading is that something in this
round's diff broke them. It did not, and the way to know is the two-sided name-set comparison this
repository's own preflight header prescribes, **because two counts agreeing proves nothing**:

```
worktree at origin/main, same environment : 42 failing
this branch, same environment             : 42 failing
comm -23 / comm -13                       : BOTH EMPTY — the name sets are identical
```

The cause was **my own earlier installs**. Adding `pytest`, `pdfminer.six`, `pypdf` and `biopython`
to reach the gates this round actually needed made a set of previously-uncollectable modules
collectable, so tests that had been counted as import failures began executing and failing on their
real assertions instead. Tracing one to its module gave `ModuleNotFoundError: No module named
'scipy'` — a genuine dependency gap, not a regression.

⛔ **The wrong repair was available and was not taken.** `sandbox-failure-baseline.txt` is a shared
file and the preflight message invites adding entries to it; doing that here would have recorded 42
healthy tests as known-broken, to tidy away an environment artifact this round introduced. Installing
`scipy`, `rdkit`, `boto3` and `matplotlib` instead made **all 42 pass**, which is the direction the
gate's own comment calls always safe. The sandbox is now closer to CI than it was, and the baseline
was left alone.

**Measured after the install, on the same command:**

```
PREFLIGHT_FULL=1 ./scripts/preflight.sh   ->  PREFLIGHT OK, exit 0
modalities suite: 11 failed, 7,781 passed, 56 skipped in 886 s
                  every one of the 11 named in the sandbox baseline as dep-related
                  0 modules could not be imported
```

Before the install the same command reported 53 failed and 7,635 passed with 42 outside the baseline.
So the environment change moved **146 tests from failing-or-uncollected to passing** and took the
outside-baseline count to zero. ⚠ The remaining 11 are `pymbar` and `netCDF4` cases, which are
genuinely absent here and are already in the baseline with their reason; they are not this round's
business and were not touched.

★ **The outward-facing tier is therefore green**, which is what CLAUDE.md requires before a preprint,
a submission, a release or a DOI. That clears the GATE. It does not clear §7 of this ledger, which is
what actually blocks posting.
