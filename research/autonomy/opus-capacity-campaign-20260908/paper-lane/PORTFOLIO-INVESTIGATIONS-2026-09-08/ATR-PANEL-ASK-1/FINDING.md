---
id: DOC-ATR-PANEL-ASK-1-FINDING
title: "Does the ATR collaborator package ask for exactly what its evidence supports?"
level: L4
kind: investigation
status: live
lane: ATR-PANEL-ASK-1
date: 2026-09-09
last_verified: 2026-09-09
scope: >-
  An audit of one manuscript against its committed evidence. It prepares no outreach, proposes no
  contact, and takes no position on whether the package is ever sent. It loosens nothing on the
  PUB-ATR release hold and is not an argument for release.
---

# ATR-PANEL-ASK-1 — auditing an ASK against its own evidence

## Question

`PUB-ATR-PANEL-ASK` (`research/manuscripts/dependency/emc-atr-collaborator-package.md`) is an ASK:
it proposes that a laboratory outside this programme run an experiment. **Does it ask for exactly
what its own evidence supports, no more?** Concretely: does any sentence assert an EMC efficacy,
safety, selectivity, therapeutic-window or clinical-readiness finding that computation cannot
establish; are the quantities it hands a collaborator re-derivable from committed artifacts today;
and does it state its own limits where a reader needs them?

## Merit

An ASK is the one document class whose integrity question is fully checkable without a laboratory.
Every quantity in it is either re-derivable from a committed artifact or it is not, and every
sentence either overstates the ask or it does not. Getting this wrong has a real cost that falls on
someone else: an overstated ask spends another group's bench time on a specification that is not as
complete as the document implies. Patient relevance is indirect but real — EMC's driver is
undrugged, and a mis-scoped ask is how a cheap, testable prediction becomes an expensive failure.

## Evidence gap addressed

`PUB-ATR-PANEL-ASK` had never had a lane. Its graph row was corrected on 2026-09-08 — the phrase
"the marginal cost of testing the assessment's prediction is the bench time and nothing else" was
retracted there as describing an experimental programme nobody has performed. **That correction was
made in `systems/graph/publications.json` and was never carried into the manuscript body.** No
audit had checked whether the same claim survived in the prose, and no ledger had re-derived the
manuscript's numbers against the artifacts as they stand today.

## Step taken, and what it found

### 1 · Two surviving unsupported-ask sites, and one reproduction claim that is now false

**Defect A — `emc-atr-collaborator-package.md:661` (section 5).**
> "Adding EMC to that panel requires plasmids and nothing else."

This is the retracted graph sentence, still standing in the manuscript. It asserts the sufficiency
of a computational specification for bench work, which computation cannot establish, and it
contradicts the same document twice: section 6 item 1 ("Every junction requires verification
against a sequenced breakpoint before any order is placed") and section 5's own next paragraph
("No TCF12::NR4A3 construct is emitted ... Without one, P5 cannot be run").

**Defect B — `emc-atr-collaborator-package.md:217` (section 1).**
> "what is missing is the sequence, the placement and the criteria."

The same completeness claim in the Introduction. "What is missing is X, Y and Z" asserts that X, Y
and Z are all that is missing. They are not, by the document's own limitations.

**Defect C — `emc-atr-collaborator-package.md:17` (frontmatter `purpose`).**
> "and falsifiers a group already running the assay would need to test them."

"Would need" carries the same completeness implication into the document's machine-readable purpose.

**Defect D — `emc-atr-collaborator-package.md:~155` (section 2.5), a reproduction claim that no
longer holds.** Section 2.5 states that the first of its three reproduction commands "prints
`REPRODUCES`". Run today it does not:

```
$ python3 research/modalities/emc_fet_construct_designs.py --check
DRIFT in: ['gene_models', 'ensembl_vs_uniprot_sequences']
EXIT=1
```

A reader following section 2.5 gets a non-zero exit and a DRIFT report. **The drift is localised
and is not a scientific mismatch** (`checks/04-drift-localisation/`): the sole difference is the
gene `PGR`, present in the shared input cache `emc-construct-inputs.json` and absent from the
committed artifact. `constructs`, `wild_type_controls`,
`rgg_dose_calibration_and_predictions`, `tcf12_negative_control` and every other key are `SAME`.
The other two commands pass: `emc_fet_frame_and_composition.py --check` prints `REPRODUCES`
(exit 0) and `emc_fusion_frame_figure.py --check` prints `PROVENANCE MATCHES` (exit 0).

⚠ **This is a reporting defect in section 2.5, not a defect in any scientific value**, and it is
recorded that way. Repairing it means either narrowing the producer's check to the genes this paper
declares, or refreshing the artifact — both touch a shared producer or a committed artifact outside
this lane, so neither is proposed here.

### 2 · The claim ledger — 95 rows, zero substantive mismatches

[`claim-ledger.md`](./claim-ledger.md). Every quantity the package hands a collaborator was
re-derived from committed artifacts: the four constructs' ORF lengths, extra junction residues,
retained-residue counts and in-frame self-checks; the whole type-2 seam arithmetic
(793 / 264 / 1 / 176 / 174 / 2 / 177 / 59 / 58 / AAG / K265 / no internal stop / 949 aa); the
frame rule and its phase-1 donor set; every row of Table 3 including the 0.000–0.267 EWSR1::ATF1
span and the 0.000 / 1.000 measured anchors; every cell of Table 4; the TAF15 margin including the
174/13 versus 175/14 discrepancy the manuscript itself documents; Supplementary Table S1's five
gene models; the prior-art screen's 322 / 238 / 0; and S3's cited sha256
`726aae02…c2048b`, which matches the artifact byte for byte.

**Result: 95 rows — 85 substantive REPRODUCES, 0 substantive MISMATCH, 6
NOT-RE-DERIVABLE-LOCALLY, and 4 known-answer controls (1 REPRODUCES, 3 MISMATCH as required).**
The only MISMATCH rows in the ledger are those three deliberate controls, which is the harness
reporting itself healthy.

The six NOT-RE-DERIVABLE-LOCALLY rows name their exact missing input. Four of the six are
limits the manuscript already states in its own prose (genomic breakpoints UNRESOLVED, the single
annotation source, the unsourced FUS and TCF12 junctions). Two are literature quantities with no
committed extraction artifact: the pazopanib 18 per cent ORR / 19-month PFS figures from ref [2],
and reference [1]'s measured recruitment anchors. Both are correctly attributed in the text; the
gap is that this repository holds no extraction record for them, not that they are misreported.

### 3 · Does it state its limits where a reader needs them?

**No wet lab: yes.** Section 6 item 8, the frontmatter `scope`, the Declarations block and the
subtitle all say so.
**Computational prediction only: yes, and unusually well.** The "Scope of the claims" block after
section 6 disclaims efficacy, potency, dose, safety, therapeutic window and clinical readiness by
name; section 6 item 4 and the closing paragraph of section 4 repeat it; section 3.4 states in
terms that placement on the axis is not a measured recruitment result. **No sentence in the
document asserts an EMC efficacy, safety, selectivity, therapeutic-window or clinical-readiness
finding.** The defects found are all of one narrower kind — completeness-of-the-ask claims — and
that is the honest result.
**The release hold: absent from the manuscript, and correctly so.** The hold is repository
release-path state, not a scientific claim, and it is recorded where it belongs
(`paper-lane/HOLD-atr-release-path.md` and the graph row's `blocked_by`). ⛔ **This lane proposes no
change to that, prepares no outreach, and takes no position on release.** The one place where the
manuscript's prose could be read as readiness is Defect A, and the diff below removes exactly that
reading.

## Artifact

- [`claim-ledger.md`](./claim-ledger.md) — 95 rows with verdicts, plus the artifact hashes read.
- [`unsupported-ask-claims.patch`](./unsupported-ask-claims.patch) — **UNAPPLIED** unified diff
  correcting Defects A, B and C. Each preserves its superseded wording verbatim behind a
  `⛔ CORRECTED 2026-09-09` marker. It does **not** touch Defect D, which needs a decision outside
  this lane.
- `checks/01` … `checks/13` — every execution attempt, failures included
  (`05`, `06` and `10` failed and are retained with their real exit codes).

## Validation

`git apply --check` on the diff: **exit 0** (`checks/12-git-apply-check/`). The manuscript is
unmodified — `git status --porcelain research/manuscripts/` returns empty
(`checks/13-tree-clean-verify/`). The ledger harness carries four known-answer controls, all four
behaving as required, so a silently-passing comparator is excluded.

## Provenance

All values re-derived 2026-09-09 from the committed artifacts hashed at the top of
`claim-ledger.md`, in this checkout, offline. No network call was made or attempted. The three
reproduction commands are the manuscript's own, quoted from its section 2.5.

## Limitations

1. **This audits a document against its evidence. It establishes nothing about EMC biology.** No
   experiment was performed; no efficacy, safety, selectivity or therapeutic-window question is
   touched, and none could be.
2. **The ledger tests internal consistency, not correctness against nature.** A row REPRODUCES when
   the manuscript matches the committed artifact. Both could be wrong together, and the manuscript's
   own section 6 item 2 records a prior instance of exactly that.
3. **The six NOT-RE-DERIVABLE-LOCALLY rows are not verified.** Naming a missing input is not
   supplying it, and no retrieval was attempted.
4. **Defect D is diagnosed, not repaired.** The DRIFT's cause is localised to `PGR`; whether the
   producer or the artifact should change is a decision for the shared-artifact owner.
5. **The diff is unapplied and is a proposal.** Whether to apply it is the paper owner's call.
6. ⛔ **Nothing here bears on the release hold, and nothing here is an argument for release.**

## Stop condition

Reached. The three unsupported-ask sites are identified with file and line, the ledger is complete
with a passing control, the reproduction-claim defect is localised digit for digit, and the diff is
proved by `git apply --check` at exit 0. The remaining work — applying the diff, and deciding the
`PGR` drift — belongs to the paper owner and the shared-artifact owner respectively, not to this lane.
