---
id: DOC-OPUS-CAMPAIGN-PREFLIGHT-RESULT-6186189A
title: "PREFLIGHT_FULL result for the ATR candidate commit 6186189a"
level: L4
kind: memo
status: live
purpose: >
  Record the actual outcome of the authorised CI PREFLIGHT_FULL run against the ATR candidate
  commit, and name exactly what failed.
scope: >
  L4. A result record. It fixes nothing, weakens no gate, and claims no green state.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# ⛔ PREFLIGHT_FULL FAILED on `6186189a` — run 34250066740

**The run is complete and its conclusion is `failure`.** Started 2026-09-08T16:16:42Z, finished
17:22:38Z, one attempt, no duplicate dispatched and no polling worker used.

- **Pinned sha:** `6186189abf5291fabdd45819ae42474eecb5ee74`.
- **Published log:** `research/autonomy/preflight-logs/6186189abf5291fabdd45819ae42474eecb5ee74.log`
  on `main`, ending `PREFLIGHT FAILED -- do not commit.` and `EXIT=1`.
- ⛔ **NO RECEIPT EXISTS.** `research/autonomy/preflight-receipts/6186189a….json` is absent on `main`,
  which is correct: `record_bar_evidence.py` refuses to write a passing receipt when the log's
  `EXIT=` marker is not 0. **`publish_bar`'s `preflight_full_green` clause therefore has no evidence
  for this commit.** No green gate is claimed or implied anywhere.

## The measured result

**11 failed, 1780 passed, 1 skipped, 20 subtests passed, in 118.19s.**

⭐ **Not one failure is in a manuscript, a producer or a paper guard.** All eleven are repo-state
checks, and every one of them is tripped by files inside this campaign's own record directory,
`research/autonomy/opus-capacity-campaign-20260908/`:

| failing check | what it is actually flagging |
|---|---|
| `test_repo_state_is_clean`, `test_every_document_id_resolves_to_exactly_one_file` | `DOC-CLOSED-ROUTES-NEGATIVE-RECORD` is claimed by **three** files: the live manuscript plus CR1's retained `BEFORE-` and `AFTER-` evidence copies |
| `test_every_hand_written_document_has_frontmatter`, `test_the_document_schema_is_actually_applied` | `opus-capacity-campaign-20260908/MANIFEST.md` is missing `scope` and `audience` |
| `test_no_new_broken_links`, `test_a_link_checker_that_strips_the_fragment_proves_the_cheaper_half` | `reports/W51-lint-consistency-coverage.md` links to an anchor in itself that no heading makes |
| `test_every_cited_and_absent_artifact_is_classified`, `test_a_withdrawal_notice_is_not_a_citation` | `coverage-scan.json` is cited by `reports/W57-graph-vs-artifact-stale-watchers.md`, is absent, and no lane claims it |
| `test_a_dead_code_pointer_still_fires_after_the_external_allowance`, `test_no_committed_document_names_a_dead_hook` | `acceptor_blast_radius.py` is named by `reports/W03b-acceptor-blast-radius.md` and exists in none of the code directories |
| `test_cli_check_exits_zero` | the aggregate `systems_check` exit, which the above make non-zero |

## What this means, stated plainly

The ATR candidate's own content is not what failed. The campaign's evidence and report files are
tripping the repository's document-identity, frontmatter, link and artifact-citation gates, and those
gates are correct to fire: a duplicate document id, a dead anchor and a dead code pointer are real
defects in committed text.

⛔ **No fix is applied here, and three constraints govern any fix.** The `BEFORE-`/`AFTER-` copies are
**retained campaign evidence** and are not to be deleted or edited to clear an id collision; no gate,
guard or test may be weakened to pass; and none of the four cited-absent or dead-pointer findings may
be silenced with a clearance phrase. The tractable subset is administrative metadata on `MANIFEST.md`
and the self-anchor in W51; the id collision and the two citation findings need an owner decision
about how retained evidence copies are represented to the document model.

⛔ Until a green `PREFLIGHT_FULL` receipt exists for a candidate commit, the final-candidate gate
coverage that release requires is **absent, which is unknown rather than passed**.
