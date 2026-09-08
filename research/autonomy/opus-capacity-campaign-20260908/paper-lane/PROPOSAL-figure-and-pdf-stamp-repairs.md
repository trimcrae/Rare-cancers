---
id: DOC-OPUS-CAMPAIGN-PROPOSAL-STAMP-REPAIRS
title: "Proposal — the figure-stamp and stale-PDF repairs from the 6186189a CI failures"
level: L4
kind: memo
status: live
purpose: >
  Record the diagnosed cause of the figure-stamp and stamped-PDF CI failures and the smallest
  file-specific repair for each, with the re-stamp versus rebuild distinction made explicit.
scope: >
  L4. A diagnosis and a proposal. Nothing is applied: no figure regenerated, no PDF rebuilt, no
  stamp edited.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Stamp failures at `6186189a` — cause and smallest repair

## 1 · The figure stamp — a RE-STAMP, and the evidence that makes it honest

**Failure, reproduced:** `test_nr4a3_fusion_targets_figures.py` 2 failed / 7 passed / 1 skipped, and
`nr4a3_fusion_targets_figures.py --check` exits 1 with
`DRIFT nr4a3-fusion-targets-occupancy.json: stamped cc8e8b419ac013a5, now b2a56d0cb648276f`. Six of
seven sources match; all ten stamped figure files exist.

**Mechanism, read not inferred:** `_fingerprint()` streams the source file's raw bytes into sha256
and stores the first 16 hex characters. It is a **whole-file digest**, so any byte change — prose,
whitespace, timestamp — drifts it.

**Cause, with commit evidence:** commit `143d7f3f` changed
`research/modalities/nr4a3-fusion-targets-occupancy.json`. A full leaf diff of the two blobs:
**1,379 leaves both sides, no key added or removed, exactly TWO changed leaves** — `generated_utc`
and one prose caveat under `verdict`. No numeric or boolean leaf moved. The change corrects a false
sentence and is scientifically right.

⭐ **The figures cannot have changed.** The generator reads only
`per_gene_summary[gene].best_empirical_p_vs_panel` and `.n_informative_experiments`; all six of those
values are byte-identical across the two blobs (ENO3 0.0348/12, PPARG 0.8291/12, SEMA3C 0.2935/12),
and neither changed field appears anywhere in the generator.

**Proposal:** edit one string in `research/manuscripts/figures/figure-provenance.json`,
`"nr4a3-fusion-targets-occupancy.json"` from `cc8e8b419ac013a5` to `b2a56d0cb648276f`. No figure byte
changes; both tests and `--check` go green; reversal is one string.
⚠ **The honesty condition travels with it:** a re-stamp asserts something the tool did not recompute,
and is only truthful because the leaf diff above shows the read fields unchanged. That evidence must
be in the commit message. ⛔ Running the generator instead would rewrite all ten PNG/PDF files as a
side effect, and matplotlib is absent from this checkout in any case.

## 2 · The four stale PDFs — a REBUILD, and only a rebuild

⚠ **A correction to how this was briefed.** The sources did **not** move. Both `.md` files exist at
exactly the paths their stamps name; the assertion is "was built from a different version of", not
"names a file that is missing". Their **content** changed.

Nine stamped PDFs exist; five are clean — including `dependency/emc-atr-collaborator-package.pdf`,
so ⭐ **the held ATR package is NOT affected**. Four are stale:

| stale PDF | stamped sha256 of source | current sha256 |
|---|---|---|
| `fusion-output/nr4a3-fusion-transcriptional-output{,-manuscript}.pdf` | `c23812ffddc17960…fa3a` | `010261ab8247b0b0…6e51` |
| `neoantigen/emc-vaccine-development-path{,-manuscript}.pdf` | `59a72c41cd4f5ed1…e396e` | `cc6f41d721761e82…9fe12` |

Both stamps were last written at `14a3f172`, and `git show 14a3f172:<path>` reproduces the stamped
digest exactly. Since then the sources changed **factually**, not cosmetically: `0b402921` corrected
the fusion-output percentile denominators 14,120 → 13,708 and 13,247, `p 0.050` → `0.0503` with build
labels, added an asymmetric-SGK1 disclosure and rescoped the SEMA3C claim; `d775c80f` and `56c9f985`
changed the vaccine path's smallest sample 579 → 450 and a reference's affiliation split. The
neoantigen stamp's two SVG figures hash clean, so only the prose drifted.

⛔ **These four must NOT be re-stamped.** The rendered bytes genuinely no longer contain the current
text — the PDFs still print 14,120, `p 0.050`, 579 individuals and "fifteen of the seventeen".
Editing their stamps would make each PDF assert it renders text it does not, converting a caught
staleness into a silent falsehood in exactly the artifact a depositor uploads. **A re-stamp is
available only where the producer's output is provably unchanged: true of the figure, false of all
four PDFs.**

**Proposal:** rebuild each of the four with `build_submission_pdf.py --paper {fusion-output,
vaccine-path} --style {journal,manuscript}`; each command rewrites the PDF and its stamp together,
and they must be reverted as a pair. ⛔ **Not executed here.**

## 3 · Named limits on this proposal

- Whether the four rebuilds are permitted right now was **not** established: no release hold naming
  `fusion-output` or `vaccine-path` was found, but the publication-authority and hold registers were
  not audited. That check belongs before anyone runs those commands.
- Builder byte-determinism is **asserted in test docstrings, not verified here** — verifying requires
  building.
- Whether the figure PNGs would be byte-identical under a regenerate is **unverifiable in this
  checkout** (matplotlib absent), which is a further reason the re-stamp is the right act.
- Whether `143d7f3f`'s author considered the figure stamp is **unknown**; `figures --check` is not
  among the gates its commit message lists, but absence from a list is not proof of intent.
