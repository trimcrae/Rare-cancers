---
id: DOC-OPUS-CAMPAIGN-SMALL-ORIGINALS-20260908
title: "Campaign small originals, 2026-09-08 — shipped archive and manifest"
level: L4
kind: index
status: live
purpose: >
  Describe the bounded archive of ACTUAL original campaign evidence shipped alongside this file, so a
  collector can verify every member by hash before issuing a receipt.
scope: >
  L4. Original bytes, not a narrative. It covers the small execution and candidate originals only;
  the large worker sandboxes are named as still outstanding and are NOT included.
audience: [maintainers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Small originals, shipped

`campaign-small-originals-20260908.tar.gz` — 2,761,659 bytes,
sha256 `bbb87bdc32b2a5a616c57cb6873c0ec63b31fbf20010a908b0540385649f82f2`.

166 members, of which **147 regular files** totalling **7,830,653 file-bytes**. Verified before
shipping: every member path is relative, none contains `..`, and none is a symlink, device or other
non-regular entry. No symlink was dereferenced; `SYMLINK-TARGETS.txt` inside the archive records that
the staged set contained none. Per-member hashes are in
`campaign-small-originals-20260908.SHA256MANIFEST.txt` beside this file (146 entries) and again
inside the archive at `./SHA256MANIFEST.txt`.

⛔ **Verify every member against the manifest before any cleanup. This is not deletion
authorisation**, and the lanes it was copied from remain in place, untouched.

## What is inside

| path in archive | what it is |
|---|---|
| `lanes/m1-lane/` | M1 figure rebuild: `originals/` (the untouched pre-rebuild PNG, PDF and provenance JSON with `SHA256SUMS.txt`), `generator-run.log` (the FAILED import, as captured), `generator-run-success.log`, `run-timestamp.txt`, `RUNTIME-EVIDENCE.txt` |
| `lanes/atr-ultra-intake/` | the ultra-review capsule as received: `capsule.zip`, `manifest.json`, and `extracted/` holding all four members |
| `lanes/hw2-lane/` | HW2's exact correction outputs, `MODEL-ENV.txt`, `INPUT-HASHES-start/end.txt` and its editing scripts |
| `lanes/hw1-lane/` | HW1's HLA candidate and `NOTES.md` |
| `lanes/fo2-lane/` | FO2's `PAIRS.md`, `pairs.json`, `build_pairs.py`, `DRYRUN-result.md` |
| `lanes/mc2-lane/` | MC2's `PAIRS.md` and dry-run result |
| `lanes/st-dg-a/`, `st-si/`, `st-mm/`, `st-pd/`, `st-mp/` | the five stood-down style lanes, including withdrawn candidates and the stand-down records |
| `lanes/rr1-lane/`, `lanes/rd1-lane/` | **top-level files only** — the final diffs (`CANDIDATE.diff`, `METADATA.diff`, `ENDPOINT-ROLE-PROPOSAL.diff`, `FINAL-blockerA1.diff`, `FINAL-blockerA1+A2.diff`, `NOT-A-CANDIDATE-frontmatter-probe.diff`), the literal `run1`–`run6` outputs, `probe.py`, and the start/end state records. Their multi-gigabyte manuscript sandboxes are deliberately excluded |
| `child-jsonl/` | the ORIGINAL JSONL transcripts and `.meta.json` for this cycle's eleven children, 3,330,811 bytes |
| `parent-transcript/` | literal tool_use/tool_result extracts, below |

## Parent transcript extracts — literal, not paraphrase

`parent-transcript/M1-literal-extracts.md` and `APPLIED-REPAIRS-literal-extracts.md` are exported
verbatim from the parent session JSONL. Each block carries the original `tool_use` id, both record
uuids, the tool_use and tool_result timestamps, the `is_error` flag as recorded, and the command and
result text unedited. They cover the M1 pre-run stamp mismatch, the failed generator import, **both**
pip failures, the interpreter survey, the per-interpreter import test, the uv-archive ABI check, the
cached-runtime import, the successful generator run, the provenance check and the runtime evidence;
and, for the applied repairs, the ATR U1 sequence derivation and apply, the three MF1 batches, and
all five PR2 stages.

⛔ These replace the earlier §4 of `COLLECTION-d357-onward.md`, which paraphrased them. Nothing here
was re-run to produce it.

## Served-model verification

Each child's served model was read from its own original JSONL, not inferred from its report:
`grep -o '"model":"[^"]*"'` over `child-jsonl/agent-<id>.jsonl` returns `claude-opus-5` and nothing
else, for every child checked.

## What is NOT here, stated plainly

- The large worker sandboxes: `rr1-lane` (66 MB), `rd1-lane` (331 MB), `pr1-lane` (9 MB),
  `pr2-lane` (66 MB) and `b2-lane` below their top level. These are duplicated repository trees;
  shipping them would transport a gigabyte of copies of files this repository already holds. They
  remain in place on the container and are unclaimed by this archive. A later recovery should
  reference already-committed Git blobs for the unchanged inputs and archive only unique original
  file bodies, retaining symlink targets as metadata without dereferencing them.
- `fo1-lane`, `mc1-lane` and `mf1-lane` — present on disk but EMPTY. Their workers' outputs survive
  only as the child JSONLs shipped here.
- **Production print QA for the figure.** No print-size legibility check has been performed. That is
  a required check that was never run, and it is named here as outstanding rather than implied by the
  screen-resolution visual QA that was done.
- B2's lane, which is not terminal: it is mid-run and spans a pre-restart and a post-restart episode.
  Both episodes are preserved in place and neither has been overwritten; it ships when it is terminal.
