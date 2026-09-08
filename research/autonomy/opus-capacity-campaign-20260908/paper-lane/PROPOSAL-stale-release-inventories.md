---
id: DOC-OPUS-CAMPAIGN-PROPOSAL-RELEASE-INVENTORIES
title: "Proposal — the stale release inventories, their exact diff and their required order"
level: L4
kind: memo
status: live
purpose: >
  Record the measured staleness of the release inventories at 6186189a and since, the exact proposed
  updates, the order they must be regenerated in, and the one row that should not be committed as it
  stands.
scope: >
  L4. A measurement and a proposal. Nothing is applied: no inventory regenerated in the tree, no
  resubmission, no deposit.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Stale release inventories — measured diff, required order, one blocked row

All three failures reproduce with `--check`, exit 1 each: `submission_metrics.py`,
`submission_packet.py`, `aso_archive_manifest.py`. ⚠ **The earlier diagnosis was right at
`fddede9a` and is already out of date**: metrics is now stale in **five fields across three
papers**, not two fields in one. Everything below is measured at **`b7292160`** and is exact for
that revision and no other. The full four-file diff is retained beside this memo as
`PROPOSED-release-inventory-updates-b7292160.diff`.

## ⭐ A verdict flips, and the stale artifact was hiding it

`submission-metrics.json` for MTAP-PRMT5: `main_words` 5588 → **6386**, `abstract_words` 249 →
**282**, and `over_limit` goes from `[]` to **`["abstract_words 282 > 250"]`**. The bookkeeping does
not cause that — the manuscript edits already committed at `b7292160` do. ⚠ It is an editorial-format
item for the MTAP lane, not a scientific one, and the limit itself is search-derived and unverified;
"over limit" means over a **believed** limit. The ATR package moves 6200 → 6577 / 243 → 245, and
repurposing 6037 → 6460.

`SUBMISSION-PACKET.md` changes four venue blocks; ⭐ **the ASO/NAT block does not change at all**.
The ATR block gains a real figure row and an upload slot flagged `figure — SUBMISSION FORMAT NOT
BUILT`.

`fusion-junction-aso-archive-manifest.json`: **1 file added, 4 hashes changed**, plus derived totals
(516 → 517 files, digest `c3d9882e…` → `403d93e0…`). ⚠ `git_revision` and the clean-tree flag also
move but are excluded from the inventory diff by design, so they are not part of the staleness.

## ⛔ The required order, with three measured dependencies

**`submission_metrics.py` → `submission_packet.py` → commit → `aso_archive_manifest.py` →
`aso_deposit_drift.py` → commit.**

1. **The packet reads the COMMITTED metrics file.** Regenerating the packet alone reproduces the ATR
   row as the stale `6200 / 243`; the correct order gives `6577 / 245`. Both outputs were generated
   and diffed — the delta is exactly those two cells. A packet-first commit would ship a freshly
   generated file carrying known-wrong numbers.
2. **The manifest hashes `submission-metrics.json`.** Manifest-first records the pre-regeneration
   digest and is immediately stale again.
3. **The manifest must run LAST on a CLEAN tree, as its own commit.** Its dirty-tree refusal is a
   hard precondition and it fired during measurement: with metrics and packet uncommitted, `--check`
   returns REFUSED, not STALE. The module's own note says the fix is an ordering, not a regeneration.

⚠ **A fourth artifact falls out.** `aso_deposit_drift.py --check` passes today **only because the
manifest is stale** — it reads the manifest's digests. Once the manifest is regenerated it returns
exit 1 and the generated block in the ASO preprint checklist must be re-emitted, moving the recorded
divergence from the published deposit **up**: 28 → 32 differing paths. ⭐ That is the honest
direction; those paths already differ and the stale manifest was concealing four of them.

## ⛔ One row that should NOT be committed as it stands

The added manifest row is
`…/opus-capacity-campaign-20260908/paper-lane/I1-executed-artifacts/shim/pytest.py`, whose own
docstring says it is **evidence-support, not a deliverable**. It entered the ASO release inventory
because fifteen deposited ASO test files `import pytest` and this campaign shim is now the only
tracked file of that name, so the import-closure resolver binds to it; before the shim existed the
name matched nothing tracked and was skipped.

Committing that row ships a sandbox test stub inside the ASO archive inventory and inflates the
deposit-drift count by one. Fixing it means an exclusion in the generator or relocating the shim —
⛔ **neither is this lane's**, and the campaign evidence directory is immutable under the retention
rule. **This is an ASO-owner decision and it belongs BEFORE the manifest is committed, not after.**

## What this is, and is not

**Is:** re-deriving generated inventories so each states what its own inputs currently are, entirely
by committed generators from committed inputs. No manuscript byte, no sequence, no measurement and
no claim changes.

**Is not:** ⛔ not a resubmission, not a new ASO release, not a Zenodo deposit, not a version bump.
The deposited record and the manifest it is compared against are immutable and untouched; the drift
block *describes* divergence, it does not reconcile it. Two items in the diff are genuine editorial
signals a human should route — the MTAP abstract over its believed limit, and the ATR package's
unbuilt figure submission format — and **neither is authorised by this bookkeeping**.

## Frozen and parked exposure

⭐ **Zero science exposure.** The five changed manifest rows are `build_submission_pdf.py`,
`lint_consistency.py`, `fusion-partner/emc-fusion-partner-pooling.json`, `submission-metrics.json`
and the campaign shim — **no ASO manuscript, sequence or screen byte changes**, and the ASO rows in
both the packet and the metrics file are unchanged. Endpoint, mortality, biomarker and HLA are not
covered by these inventories at all.

## Named limits

- ⚠ **Short shelf life.** The tree was dirty with other lanes' in-flight edits throughout and HEAD
  advanced once mid-measurement. With the then-uncommitted surface-targets edits applied, metrics
  would carry a **second** over-limit verdict. Whoever commits this must re-run step 1 against the
  tree they actually have.
- The venue limits are search-derived and could not be verified — one publisher serves a bot
  challenge and another blocks the address. ⛔ No retry was made.
- The manifest's clean-tree state could not be demonstrated green, because that requires committing
  the first two steps, which this lane was forbidden to do.
- The claim-coverage census belongs to another lane; it appears nowhere in this manifest's payload,
  so the two do not perturb each other.
