---
id: DOC-OPUS-CAMPAIGN-PARENT-VERIFICATION-20260909
title: "Parent re-derivation of three portfolio lanes, 2026-09-09"
level: L4
kind: verification-record
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# Parent re-derivation — MORTALITY-2, NEOANTIGEN-3, CARE-DELIVERY-3

The parent does not commit a child's claim on the child's word. Each lane's generators were
re-executed by the parent, from a copy placed at the SAME directory depth (the scripts resolve the
repo root by counting parents, so a scratchpad copy resolves to the wrong root — the first attempt
did exactly that and died on `/tmp/research/literature/emc-mortality-probe.json`). No child capture
under any lane's `checks/` was overwritten; the parent's own stdout is in `reruns/`.

## MORTALITY-2 — reproduces byte-for-byte

`genre_stratified_rates.py` rerun exit 0. All three JSON outputs are byte-identical to the lane's,
INCLUDING the 2000-draw misclassification simulation, so its RNG is seeded and the result is not a
lucky draw:

| output | sha256 | identical |
|---|---|---|
| `genre-stratified-rates.json` | `85aaf825…` | yes |
| `reclassification-sensitivity.json` | `c0c072c4…` | yes |
| `genre-classification.json` | `0044b9cd…` | yes |

The frozen classifier hashes to `9f00b724…`, matching what the lane reported before it read any cue
field. Every load-bearing number re-derived: composition 53 % / 20 % of papers and 56 / 60
death-cue sentences; crude 4/116 = 3.45 % vs 3/461 = 0.65 %, Fisher **p = 0.03304**; within case
reports 4/56 vs 2/60, **p = 0.4272**; all other genres 0/60 vs 1/401, p = 1.0; exact stratified
T = 4, E[T] = 3.1209, **two-sided p = 0.6953**, MH OR 1.7844; collapsed case-vs-non-case
**p = 0.4554**, MH OR 1.948; standardisation 3.45 % → **0.929 %** and 0.65 % → **1.856 %**; shipped
cue 0.005748 crude → **0.1021** stratified; simulation median p **0.2074** at e = 0.10 and
**0.0442** at e = 0.30.

⚠ ONE LABEL THE PARENT SHARPENS. The lane calls the strict-endpoint test a "five-stratum exact
conditional". The program's own output records `strata_used: 2` for that endpoint — three strata
carry zero flagged sentences on both sides and are dropped as degenerate. Five strata are the
DESIGN; two carry the information. The shipped-cue endpoint does use all five. This does not change
any number; it changes what the phrase should be taken to mean.

## NEOANTIGEN-3 — reproduces byte-for-byte

`neoantigen3_correspondence.py` rerun exit 0; `neoantigen3-correspondence.json` byte-identical
(`140a437c…`). Re-derived: exact / substring / isobaric-exact / isobaric-substring all **0** for
both the 174 junction peptides and the 11 ranked binders against the validated 15 and against the 5
sequenced negative controls; exactly **one** substring hit anywhere, `SQQSSSYGQQN ~ SQQSSSYGQQ` in
prediction-only record E38; matcher demonstrably live (exact arm 15/15 on the reference against
itself, isobaric arm 13 hits on 13 I/L-swapped queries); 4 of the 7 validated allotypes
(A\*68:02, B\*40:01, C\*04:01, C\*12:03) outside the 10-allele panel = **5 of 15** epitope-allele
pairs off-panel; **no HLA-C in the panel at all** while 2 of 15 validated epitopes are C-restricted;
A\*02:01 and A\*24:02 among the panel allotypes returning **zero** ranked binders; breakpoint
position stated or locally derivable for **4 of 15**, the other 11 recorded UNKNOWN, not zero.

The lane's `checks/03` exit **1** (a leaked loop variable in the self-test comprehension) is
retained beside the fixed `checks/04`, which is the correct handling.

## CARE-DELIVERY-3 — validator and diff both re-run by the parent

`validate_v3.py` rerun by the parent: **131 passed, 0 failed, exit 0**.
`git apply --check` on `PROPOSED-UNAPPLIED-emc-surgical-quality-scope.diff`: **exit 0**;
`git apply --stat`: `research/modalities/emc-surgical-quality.json`, 38 insertions, 5 deletions,
one file. The diff stays UNAPPLIED — `research/modalities/` is shared state and the parent applies
it only as a separate, separately-verified act.

⚠ Carried forward from the lane, not softened: this does NOT make PUB-CARE-DELIVERY writable. Its
publish decision is recorded "no" and BLK-NO-FIELD-ATTENTION-MEASUREMENT is unresolved. Neither was
touched.

## Scope of this record

`reruns/` holds the parent's own stdout for the three re-executions and the hash list. The full
rerun trees (`_PARENT-VERIFY-*`) were byte-identical duplicates of the committed lanes and are left
untracked; nothing unique lives in them, and the originals they reproduce are committed. This is
annotation and arithmetic verification only — it establishes that the lanes' numbers come out of
their stated inputs, and it establishes nothing biological, clinical or therapeutic.
