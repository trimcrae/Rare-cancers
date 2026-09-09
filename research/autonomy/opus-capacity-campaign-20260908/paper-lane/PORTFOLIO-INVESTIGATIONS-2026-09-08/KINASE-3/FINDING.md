---
id: DOC-PORTFOLIO-INVESTIGATION-KINASE-3-2026-09-09
title: "KINASE-3 — EXPR-COMPOSITION's attenuation reproduces exactly, and the correction it owes touches eight prose sites in two lane findings, no manuscript sentence, and no pin"
level: L4
kind: investigation
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: KINASE-3
continues: EXPR-COMPOSITION
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# KINASE-3 — propagating the composition attenuation

Repo HEAD at lane start `673d330446ee07a8db3e83b817d9e619834d4d1f` (2026-09-09T01:24:10Z). Writes confined to this directory.
No `git add`/`commit`/`push`, no `preflight.sh`, no subagent, no worktree, no repo copy, no
network, no GPU, no paid API, no shared-file edit, no applied diff. **No pin, guard, gate, floor,
matcher or test was touched.**

## 1 · Question

EXPR-COMPOSITION named a downstream prose correction it owed and deliberately did not write.
**Does its result reproduce, and exactly which sentences — everywhere, not one — does it change?**

## 2 · Merit

A correction that repairs one sentence and leaves the same claim standing two sections later is not
a correction; it is a second version of the error. The kinase expression arm's load-bearing sentence
("moves the same way in EMC on both platforms") now has three successive qualifications attached to
it — a strength term (PUB-KINASE-LEADS), a crowding term (KINASE-2), and now a composition term —
and the three live in different documents. Reconciling them once, with the unadjusted figures kept
beside the adjusted ones, is what keeps the arm honest for whoever writes the endpoint.

## 3 · Evidence gap

EXPR-COMPOSITION's §7 states the debt and declines to pay it: "**No shared file is edited by this
lane and no diff is proposed.**" KINASE-2's §8 item 2 routes the same debt onward. Nobody had
(a) independently re-derived the attenuation, (b) enumerated the affected sentences, or (c) written
the diff. The inputs were all committed and local.

## 4 · Step taken

**(a) Re-derivation — every headline figure reproduces, digit for digit.**
The committed `composition-adjusted-contrast.json` was re-read (`checks/01`) and the generator was
re-run end-to-end (`checks/02`, exit 0, runtime 33.7 s) from a copy differing from
`EXPR-COMPOSITION/composition_adjusted_contrast.py` **only** in `HERE` (pinned to the
EXPR-COMPOSITION directory, read-only) and `OUT` (redirected into this lane, so no EXPR-COMPOSITION
file is written). The re-derived artifact was then compared leaf by leaf against the committed one
(`checks/03`): **433 leaf comparisons, 0 mismatches**, ignoring only `runtime_seconds`.

| Quantity | Reported | Re-derived | |
|---|---|---|---|
| Spearman(C, EMC label) GPL6244 / GPL3290 | −0.578 / −0.504 | −0.5780 / −0.5041 | ✅ |
| primary concordance unadj → adj | 0.6521 → 0.5668 | 0.6521 → 0.5668 | ✅ |
| primary attenuation of excess over 0.5 | 0.561 | 0.5606 | ✅ |
| secondary concordance unadj → adj | 0.6368 → 0.5981 | 0.6368 → 0.5981 | ✅ |
| secondary attenuation | 0.283 | 0.2832 | ✅ |
| cross-platform Pearson r, primary / secondary | 0.405 → 0.251 / 0.447 → 0.281 | 0.4046 → 0.2511 / 0.4467 → 0.2812 | ✅ |
| adjusted-null p, primary / secondary | 0.022 / 0.0085 | 0.02249 / 0.0085 | ✅ |
| negative control: permuted-score mean (sd), draws ≤ 0.5668 | 0.6469 (0.0135), 0 of 500 | 0.6469 (0.0135), 0 of 500 | ✅ |
| NR4A3 strengthens on both platforms | +0.540→+0.610; +0.373→+0.474 | identical | ✅ |
| NDRG1 attenuates most and consistently | +0.398→+0.150; +0.504→+0.324 | identical | ✅ |
| known-answer gate vs KINASE-2 | 103 comparisons, 0 mismatches | 103, 0 | ✅ |

**No discrepancy was found**, so the reproduction branch — not the discrepancy branch — applies.

**(b) Sites.** `SITES.md` lists every affected sentence with file and line: **8 correction sites**
(3 in `PUB-KINASE-LEADS/FINDING.md`, 5 in `KINASE-2/FINDING.md`), plus **7 sites checked and
deliberately left unchanged** with the reason each survives, plus the finding that
**`PUB-KINASE-LEADS` has no manuscript file at all** (`systems/graph/publications.json:281`,
`"state": "outlined"`, no `document.file`) and that the nearest kinase manuscript,
`research/manuscripts/dependency/emc-kinase-leads-source-verification.md`, contains **no sentence
resting on the concordance statistic** — its one "both platforms" sentence (line 351, EGFR) is a
per-gene direction read that *survives* adjustment concordantly.

**(c) Diff.** `composition-attenuation-correction.diff`, **unapplied**, 2 files, 7 hunks. It states
the adjusted figures **alongside** the unadjusted ones (no silent replacement), carries
EXPR-COMPOSITION's bounding limitation verbatim in substance — composition and biology are not
separable here even in principle, so **0.561 is an upper bound on the composition share, not an
estimate, and the surviving p values are conservative** — and says in three places that the residual
**survives**, so this is an attenuation and **not a refutation**. Proved with
`git apply --check --verbose`: **exit code 0** (`checks/04`), both patches checked clean.

**(d) Pins.** `checks/05`. **0 hits in `research/manuscripts/pinned-figures.json`** for any affected
figure; **0 in `systems/graph/` or `systems/views/`**. Every hit elsewhere is coincidental — see
SITES.md §D. **No pin was changed.**

## 5 · Artifact · validation · provenance · limitations · stop condition

**Artifact.** `composition-attenuation-correction.diff` (unapplied), `SITES.md`,
`rederive/composition-adjusted-contrast.REDERIVED.json` + `rederive/*.OUTPATCHED.py`,
`work/{K2.md,P1.md}` (the edited copies the diff was generated from, retained as evidence).

**Validation.** (1) Independent re-run of the generator, exit 0, 0/433 leaf mismatches against the
committed artifact. (2) The generator's own known-answer gate re-passed inside that run (103
comparisons vs KINASE-2, 0 mismatches, hard exit 2 on any mismatch). (3) The negative control
re-passed (0 of 500 permuted-score draws reached 0.5668). (4) `git apply --check`, exit 0.
(5) Site enumeration cross-checked against the files' actual line numbers by `sed -n`.

**Provenance.** `EXPR-COMPOSITION/composition-adjusted-contrast.json` and
`composition_adjusted_contrast.py`; `KINASE-2/label-permutation-vs-gene-resampling-null.json`
(sha256 `f799e5ed…`, the gate target); sole data input
`research/modalities/emc-expression-panels.json` sha256 `59bccb55…`, `generated_utc`
2026-08-29T12:51:32+00:00. All read read-only.

**Limitations.**
- This lane **re-derived** the attenuation; it did not independently re-implement it. A shared bug in
  `composition_adjusted_contrast.py` would reproduce identically. The independent checks it inherits
  are the known-answer gate and the negative control, not a second implementation.
- The diff is **prose only**. It changes no computed value, no artifact, no pin, no gate.
- `KINASE-2/FINDING.md`'s title (line 3) is **not** edited: as literally written it survives. It is
  flagged in SITES.md §C for the owner, because a reader who takes "real shared EMC contrast" to mean
  "EMC biology" would be reading past the qualification.
- The two-covariate and MKI67/EPCAM sensitivity adjustments are **out of scope** and were not run;
  EXPR-COMPOSITION stopped at its declared stop condition and so did this lane. No further
  adjustment was invented.
- ⛔ Nothing here establishes efficacy, safety, selectivity, a therapeutic window, target attribution
  or clinical readiness for any agent in any disease, and nothing here is advice about a patient. An
  expression association is not a target.

**Stop condition.** Stop once the headline figures are re-derived, every affected sentence is
enumerated with file and line, the unapplied diff passes `git apply --check`, and the pin scan is
recorded — or stop immediately and report digit for digit on a reproduction failure. **Met, on the
reproducing branch.**

## 6 · What this owes onward (not done here)

1. **Someone must apply the diff.** It is unapplied by fence. Its two target files belong to lanes
   `KINASE-2` and `PUB-KINASE-LEADS`; the parent coordinator integrates.
2. KINASE-2 §8 item 2 (propagate both nulls into the endpoint's prose) stays open — there is no
   endpoint prose yet to propagate into, which is exactly why the correction is cheap today.
3. A **deconvolution** with a real reference signature, and a **third series**, remain the two things
   that would do more for this arm than any further reanalysis of these two.
