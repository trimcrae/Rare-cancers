#!/usr/bin/env python3
"""One-shot helper: append this seat's two amendment entries to amendments.jsonl."""
import json
import os

REPO = "/home/user/Rare-cancers/.claude/worktrees/agent-a4027037beeede805"

entries = [
    {
        "cycle_id": "AUT-COV-001-seat",
        "utc": "2026-08-28T14:43:43Z",
        "path": "research/manuscripts/tests/test_fusion_partner_prose_matches_its_artifact.py",
        "old_value": "_CENSUS_STATS matched four notations (n=N cohort size, p-value in both printed "
                      "forms, HR, cm/months); the SEMA3C 1.8x/1.7x GSE28866 ratios and the n=4 EMC "
                      "library count sat in DECLARED_NOT_ARTIFACT_OWNED as class \"foreign-artifact\"",
        "new_value": "_CENSUS_STATS gained a fifth notation, a printed x-fold-change "
                      "(\\d+(?:\\.\\d+)?×); the two DECLARED rows for the SEMA3C ratios and the "
                      "library count are removed and replaced by two real BINDINGS that open "
                      "research/modalities/gse28866-tumour-vs-normal.json directly and check the "
                      "prose against ratio_calibration.per_gene.SEMA3C and "
                      "per_gene.values.SEMA3C._n_emc_libs",
        "what_changed": "AUT-COV-001's blind-spot audit of claim_coverage.py's pattern set found that "
                         "a x-fold-change (\"1.8× normal tissue and 1.7× other sarcomas\") is "
                         "a reusable notation shape (confirmed by grep across 40+ manuscript files) "
                         "the census cannot see at all -- the same class of gap CYC-0013 closed for "
                         "n=, p-values, HR and cm/months. Added the shape to _CENSUS_STATS. Separately, "
                         "the two DECLARED_NOT_ARTIFACT_OWNED rows that had been excusing this "
                         "document's own two instances of that notation were upgraded to real "
                         "bindings: the artifact that owns them (GSE28866) was never loaded because "
                         "bind()'s value callable only ever received the fusion-partner pooling "
                         "artifact, not because the numbers were unbindable -- verified against "
                         "ratio_calibration.per_gene.SEMA3C (emc_over_normal=1.8175, "
                         "emc_over_sarcoma=1.6622, both round to the prose's 1.8/1.7) and "
                         "_n_emc_libs=4. Measured coverage moved from 83/270 to 84/270 sentences "
                         "(82/201 to 83/201 numbered) on this document; claim-coverage.json "
                         "regenerated to match. 5 new mutations added to mutate_fusion_partner_guard.py "
                         "(a companion, separately-declared amendment) and 94/94 mutations caught, "
                         "positive control green.",
        "why": "Closing AUT-COV-001: even a document with a numbers guard can have sentences unread "
                "because the guard's own pattern set has notation blind spots, and separately, a "
                "figure declared not-artifact-owned because its artifact is a DIFFERENT file than the "
                "one bind() already has open is a weaker instrument than a real binding once that "
                "second file can be shown to actually contain the value -- 'one fact, one place, "
                "verified' beats 'declared and merely accounted for'.",
        "self_serving_check": "ANSWERED: NO. This is process/hardening work claimed from the ledger "
                                "(AUT-COV-001), not a gate blocking this cycle's own progress. The "
                                "change makes the guard strictly stricter: it adds a new alternative "
                                "to the census pattern (which can only ADD unbound-figure findings, "
                                "never hide one) and converts two weak DECLARED exemptions into real, "
                                "artifact-checked BINDINGS that can now fail if the numbers drift -- "
                                "the opposite direction from loosening a bar to pass a blocked cycle.",
    },
    {
        "cycle_id": "AUT-COV-001-seat",
        "utc": "2026-08-28T14:43:43Z",
        "path": "research/manuscripts/tests/mutate_fusion_partner_guard.py",
        "old_value": "89 mutations",
        "new_value": "94 mutations (5 added: F.5, the fold-change notation and its two promoted "
                      "bindings)",
        "what_changed": "Added 5 mutations under a new 'F.5' section: two single-arm drifts of the "
                         "SEMA3C-vs-normal-tissue and SEMA3C-vs-other-sarcomas fold-change ratios, one "
                         "arm-swap of the pair (every digit on the page stays correct), one drift of "
                         "the GSE28866 EMC library count binding, and one unbound-fold-change control "
                         "(writes an unwitnessed '3.0x' into the prose, mirroring the existing unbound "
                         "n=99 control for the n= notation) that targets the census predicate directly "
                         "rather than any single binding.",
        "why": "A binding or a census pattern that has never been mutated is a coverage claim nobody "
                "has tried to break (paper-hardening's mutation-testing standard, and this repo's own "
                "measured history of guards that reported full coverage while binding nothing). The "
                "two bindings and the census's new fold-change alternative added by this cycle "
                "(companion amendment on test_fusion_partner_prose_matches_its_artifact.py) needed the "
                "same standard every other binding in this file already meets.",
        "self_serving_check": "ANSWERED: NO. All 5 new mutations were run against the working tree "
                                "(python3 research/manuscripts/tests/mutate_fusion_partner_guard.py "
                                "--working-tree) and every one was CAUGHT (94/94 total, positive "
                                "control green) before this amendment was written -- the mutations "
                                "were not adjusted to make a failing run pass; they are the evidence "
                                "that the new bindings and pattern actually fire.",
    },
]

path = os.path.join(REPO, "research/autonomy/amendments.jsonl")
with open(path, "a", encoding="utf-8") as fh:
    for e in entries:
        fh.write(json.dumps(e, ensure_ascii=False) + "\n")
print("appended", len(entries), "entries to", path)
