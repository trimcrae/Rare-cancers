# Parent note — `NOT_CONTROL_SINGLE_ARM_TRIAL` is asserted from ZERO registered arms in 6 rows

**Date: 2026-09-08. Re-derived by the parent, not taken from a worker report.**

## The finding

Two Q-D leaves, working on disjoint NCT groups and unable to see each other, independently flagged
the same defect in Job 3's arm-attribution map: a group is labelled
`NOT_CONTROL_SINGLE_ARM_TRIAL` on the basis `trial registers 0 arm group(s)`, because Job 3's rule
tests `n_arms_registered <= 1`. **Zero registered arms is absence of information, not evidence of a
single arm**, and the two are not the same claim.

I re-derived the exact extent from `CURATION-endpoint-arm-attribution-map.tsv` myself:

- **6 rows**, across **3 distinct NCTs**, carry `control_status = NOT_CONTROL_SINGLE_ARM_TRIAL` with
  `control_basis = "trial registers 0 arm group(s)"`.
- Those are every row in the 552 whose `n_arms_registered` is 0. There are no others.

**Updated 2026-09-08, later the same day: all three have now been read.** The note first recorded
NCT02825420 as unreached; Q-D group 2 subsequently reached it and reports `armGroups` empty — zero
registered arms, so no `armGroupType` exists anywhere in that record. The three:

- **NCT00389805** — `protocolSection.armsInterventionsModule` is the empty object `{}`. The record
  nonetheless reports **two** results groups with different bortezomib schedules, so "single arm" is
  contradicted by the record it is drawn from.
- **NCT04539327** — `armsInterventionsModule` is `{}`; the study is OBSERVATIONAL / CASE_ONLY.
- **NCT02825420** — `armGroups` is empty. Read by Q-D group 2, which independently reached the same
  conclusion as the other two leaves without seeing this note.

## What this does and does not establish

⛔ It does **not** establish that any of these six groups IS a control. The correct value on this
evidence is `UNKNOWN`, and `UNKNOWN` must never be read as `NOT_CONTROL` — doing so would manufacture
a denominator, which is the specific error the whole endpoint review is about.

⛔ It does **not** invalidate Job 3's map. The other 546 rows are untouched by this note, and Job 3's
own limits section already says control status is unrecoverable for most of the corpus.

⛔ No producer was re-run, no map was edited, no rule was amended. Amending Job 3's rule is a
decision for the owner and for root, not something a note takes on its own.

## Why it is recorded here rather than fixed

The map is Job 3's artifact. This note exists so the defect is not lost between a worker report and
an integration, and so that whoever amends the rule knows the blast radius is exactly 6 rows and
3 trials rather than an unbounded correction.
