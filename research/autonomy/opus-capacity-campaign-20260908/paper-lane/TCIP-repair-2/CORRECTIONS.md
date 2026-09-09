---
id: DOC-OPUS-CAMPAIGN-TCIP-REPAIR-2-CORRECTIONS
title: "TCIP residual repair — the four accepted P2 corrections"
level: L4
kind: record
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# The four corrections, exactly as made

Scope is the root adjudication memo
`TCIP-focused-residual-root-adjudication-20260908.md` (6,201 B, SHA256
`e79e2ce888866a24f6c831332ded0cc2485f78354f7e1eb7f6e5bb818fce4f43`), read in full, plus the returned
first batch under `../TCIP-repair/` and the two current manuscripts, which were at the exact focused
freeze when this lane began (main 51,625 B / `d211e11a…`, SI 35,997 B / `72d21e7f…`).

**Nothing measured changed.** No number, table, count, status, interval, exit code or artifact was
altered. The nine closed findings, the 19 inside / 5 outside counts, the `DISAGREES` label, the
illustrative five-to-three diagnostic, the draw counts and the 968 sizing-memo carryover from the
first batch are untouched. No sampler, census, geometry, uncertainty calculation, figure, source
retrieval or second review was run.

## 1 · Probe/residue inference (memo item 1, F08)

Three propositions, now stated distinctly wherever the paper abbreviates the relation.

* **Necessary:** a residue supplies at most two probes, so acceptance at **at least** 12 probes
  requires **at least six** contributing residues.
* **Not sufficient, not equivalent:** six or more contributing residues do not imply 12 scoring
  probes — a residue scores only for those of its two query points that fall in the contact band — so
  no residue-count threshold reproduces the probe rule.
* **No upper bound:** six to twelve is the range of residues that could supply **exactly** twelve
  probes; acceptance requires twelve **or more**, so arbitrarily many residues may contribute.

Sites: main §1 (was "A threshold of 12 probes can therefore be satisfied by between six and twelve
distinct residues"); main §6, where the false sentence "**a threshold on probes does not impose any
threshold on residues**" is removed and replaced by the numbered three-part statement; SI §S2 (was
"Six is the minimum, not a maximum"); and the unapplied `PUB-TCIP` field. Measured scores and the
four-of-six / two-thirds arithmetic are preserved verbatim.

## 2 · Uncertainty scope (memo item 2, F05)

The missing joint acceptance counts, and the shared-stream covariance they would be needed for, are
now scoped to the **shared-proposal floor ablation** (`random.Random(777 + pose_index)` reused across
arms and floors). The **eight-rung main enumeration** is named as a different object: distinct random
streams for the four pooled arms, marginal cell counts retained, and — as its own statement — **no
ratio interval and no significance test are reported for it**. The former universal phrasing ("no
design-aware interval can be computed", "it is not a test of the ratio, for which the joint counts
are not retained") is withdrawn at each site.

Sites: main §4 *Uncertainty*; main §9 limit 4; SI §S1 "Random streams, and what they permit" and the
following main-enumeration seed paragraph; SI §S5 under Table S3. No new interval, calculation or
significance claim is introduced.

## 3 · Expected count versus verdict rule (memo item 3, F06)

SI §S1 now separates two objects that the previous text ran together.

* **Nominal expected count.** 1.20 = 24 × 0.05, which follows from **linearity of expectation** and
  requires neither independent comparisons nor a calibrated family test. What it does assume is 5 %
  noncoverage per comparison against an **exact** reference; that fails here, because the committed
  rates are themselves Monte Carlo estimates (1,000,000 draws per compared cell against 300,000).
* **Verdict rule.** Separately, the label is `AGREES` when at most `max(1, ceil(1.20)) = 2` of the 24
  comparisons fall outside and `DISAGREES` otherwise; five fell outside. That at-most-two-exclusions
  threshold was never calibrated as a family-level replication test. Its being uncalibrated is a
  statement about the rule, not about the expected count.

The rule text is read from the retained producer
`research/modalities/nr4a3_tcip_reach.py` → `crosscheck_replicates_committed_acceptance`, and the
counts from the retained artifact block in `research/modalities/nr4a3-tcip-reach.json`. Nothing was
re-run. `DISAGREES`, 19 inside / 5 outside, the draw counts and the illustrative five-to-three
diagnostic are preserved exactly.

## 4 · PUB-TCIP current-claim field (memo item 4, F04) — UNAPPLIED

The `what_it_would_claim` opening assertion "THE CLAIM IS MODALITY-GENERAL AND THE EMC ANCHOR IS THE
SETTING IT WAS COMPUTED IN" is explicitly retired in the new field text, and replaced with the
demonstrated **named-toolchain audit** and a **potentially transferable** methodological caution that
is offered as a possibility rather than a result. The NOT-AN-EMC-SPECIFIC-RESULT designation is
retained unchanged. Corrections 1 and 2 are carried into the same field's abbreviated statements.

**This lane did not edit `systems/graph/publications.json`.** The change is delivered as an exact
unified diff against the **current** file (68,790 B, SHA256
`8dc9b0b9894679277e94d3e283459e9fae63d13b845460bf177a1997db0e1418`, i.e. after the parent's
91609d30f application), at
`patches/0001-PUB-TCIP-retire-modality-general-opening.patch`, with the full new field text at
`patches/PUB-TCIP-what_it_would_claim-NEW.txt`. `git apply --check` on that patch exited **0** and
the patched copy parses as JSON. Applying it yields 70,224 B, SHA256
`800e844ff1e6b8127c5d4d6811438e820f8c66c4efe11269e1c083d751d1902d`; only the one string value in the
`PUB-TCIP` entry changes.

## Change-log entry added

Main Appendix A gains item 5, dated **2026-09-09** (the working clock had rolled past 2026-09-08 UTC
when these edits were made), recording (a)–(d) above. The focused-review freeze is **not** redated,
and the separately accepted 968 sizing-memo banner and `canonical_for` retirement are neither
repeated nor touched.
