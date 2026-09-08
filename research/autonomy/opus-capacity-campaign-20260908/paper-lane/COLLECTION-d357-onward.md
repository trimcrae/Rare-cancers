# Original-evidence collection record, d3578362 onward

Written 2026-09-08 by the parent (sole shared-integration owner). This is an INDEX of originals that
exist locally and awaits a directory-specific collector receipt for each path named. It is **not** a
substitute for those originals and nothing below authorises deleting any of them.

## 1 · Worker lane originals, retained intact

Measured `find -type f | wc -l` and `du -sb` at 2026-09-08T14:45Z. Every one of these is an ORIGINAL
worker lane, not a copy made at collection time.

| lane | worker and what it holds | files | bytes |
|---|---|---:|---:|
| `/tmp/claude-0/rr1-lane` | RR1 renderer registration: `CANDIDATE.diff`, `METADATA.diff`, `ENDPOINT-ROLE-PROPOSAL.diff`, `NOT-A-CANDIDATE-frontmatter-probe.diff`, `run1`–`run6` literal outputs, `ENV-MODEL.txt`, `END-STATE.txt`, build sandbox | 774 | 66,851,125 |
| `/tmp/claude-0/rd1-lane` | RD1 renderability: `FINAL-blockerA1.diff`, `FINAL-blockerA1+A2.diff`, `probe.py`, six manuscript sandboxes | 3,790 | 330,712,647 |
| `/tmp/claude-0/b2-lane` | B2 raster-image builder candidate — interrupted by the container restart, relaunched against the same lane | 8,919 | 664,575,993 |
| `/tmp/claude-0/hw1-lane` | HW1 HLA coverage candidate + `NOTES.md` (records six intermediate build fragments deleted BY HW1 before delivery) | 10 | 170,844 |
| `/tmp/claude-0/hw2-lane` | HW2 six-correction pass: corrected candidate, `MODEL-ENV.txt`, `INPUT-HASHES-start/end.txt`, `apply-corrections.py`, `patch2.py`, `patch3.py` | 15 | 242,108 |
| `/tmp/claude-0/pr1-lane` | PR1 endpoint-regime repair, including the 114-symlink sandbox the push guard refused | 258 | 9,374,073 |
| `/tmp/claude-0/pr2-lane` | PR2 fusion-partner generator repair: `before.json`, `prose.bak`, full patched `repo/` sandbox | 761 | 66,349,122 |
| `/tmp/claude-0/fo2-lane` | FO2 correction pairs: `PAIRS.md`, `pairs.json`, `build_pairs.py`, `DRYRUN-result.md`, `FO1-transcript-flat.txt` | 5 | 738,950 |
| `/tmp/claude-0/mc2-lane` | MC2 census pairs: `PAIRS.md`, `DRYRUN-cancer-modality-census.md` | 2 | 52,030 |
| `/tmp/claude-0/st-dg-a` | ST-DG-A stood-down style lane: `STANDDOWN.md`, withdrawn `after.md`, `fix_bold.py`, findings dumps, the markup-only identity proof | 10 | 1,454,976 |
| `/tmp/claude-0/st-si` | ST-SI stood-down: `before.md`, two discarded candidates, `debold.py`/`debold2.py`/`debold3.py` | 10 | 349,243 |
| `/tmp/claude-0/st-mm` | ST-MM stood-down: `MANIFEST.txt`, `diff.patch`, `fix_bold.py` (the heading-corruption finding), `fix_bold2.py` | 15 | 425,600 |
| `/tmp/claude-0/st-pd` | ST-PD stood-down: `DISCARDED-after.md.txt`, `lint-ci-noargs.txt`, `pass1.py` | 11 | 280,084 |
| `/tmp/claude-0/st-mp` | ST-MP no-edit determination: `before.md`, `lint-before.txt`, `DECISION.txt` | 3 | 117,740 |
| `/tmp/claude-0/m1-lane` | M1: untouched original figure directory, both generator logs, run timestamp | 14 | 505,211 |
| `/tmp/claude-0/atr-ultra-intake` | ATR ultra capsule byte intake (§3) | 6 | 57,068 |

⚠ `fo1-lane`, `mc1-lane` and `mf1-lane` are present but **empty** (0 files). Their workers' outputs
survive as this session's task-output transcripts and as the parent's applied diffs; the lane
directories themselves hold nothing and no claim is made that they do.

## 2 · M1 — the exact failed stage, preserved

⛔ The first M1 attempt FAILED and nothing here reports it as anything else. Its evidence:

- `/tmp/claude-0/m1-lane/generator-run.log` — the original captured stderr, 553 bytes, written
  2026-09-08 14:16 UTC. Full traceback, ending `ModuleNotFoundError: No module named 'matplotlib'`,
  raised at `emc_fusion_frame_figure.py:87` inside `draw()`. Recorded exit code 1.
- **Both pip attempts are parent-transcript excerpts, not files** — they were run in the parent shell
  and their stderr was not redirected at the time. They are quoted here as they appeared and are NOT
  re-runs; no speculative retry was performed to produce them.
  1. `python3 -m pip install --quiet matplotlib` → `pip._vendor.urllib3.exceptions.ReadTimeoutError:
     HTTPSConnectionPool(host='files.pythonhosted.org', port=443): Read timed out.`, exit 1.
  2. `timeout 280 python3 -m pip install --quiet --timeout 120 --retries 3 matplotlib` → the same
     `ReadTimeoutError` on the same host, exit 1.
  Interpreter for both: `/usr/bin/python3` (3.11). `pypi.org` and `files.pythonhosted.org` are in this
  environment's `no_proxy`, so pip went direct; `$HTTPS_PROXY/__agentproxy/status` recorded no policy
  denial for either host.
- `/tmp/claude-0/m1-lane/originals/` — the untouched original `emc-fusion-frame-fig1.png`
  (`fa94675f…07a7`, 360,656 B), `.pdf` (`0d9aff26…8701`, 83,262 B) and
  `emc-atr-figure-provenance.json` (`05132490…2774`, 836 B), with `SHA256SUMS.txt`.

The later successful run is a **separate** stage and does not overwrite that record:
`/tmp/claude-0/m1-lane/run-timestamp.txt` (2026-09-08 14:41:56 UTC) and
`generator-run-success.log` (exit 0). It succeeded because matplotlib 3.11.1 was found already
unpacked in the uv archive cache at the cpython-311 ABI, not because the pip route was retried.

## 3 · ATR ultra capsule — byte intake, acknowledged

Fetched through the existing Git route from `refs/heads/codex/opus-cloud-inputs-20260908` at
`2ec269aaa2e1849fd82b90abc30106bf3d9fb91d`. ⛔ The input branch was **not** merged into this
scientific branch and its contents are **not** committed here; only this acknowledgment is.

Copied with binary-safe `git show`, verified, and extracted to
`/tmp/claude-0/atr-ultra-intake/` — relative regular-file members only, no absolute paths, no `..`,
no non-regular members.

| file | bytes | sha256 | verdict |
|---|---:|---|---|
| `atr-final-ultra-original-inputs.zip` | 15,024 | `6d31d890a25b895bd3d507373bdc2e2fd92f201623be33a70b22c52f58d3e184` | matches delivered |
| `…-manifest.json` | 761 | `7508804a01ca0022a7eaded7ff4eccf0c7e2eda8d870bb6c950356de2d84d394` | matches delivered |
| `atr-final-ultra-review.md` | 22,416 | `51c586e8d32737c2f19ff80edb8099a77fe74f7799f1207a9c1f003609851800` | matches delivered AND internal manifest |
| `lightweight-checks.json` | 12,788 | `45d0c5dd659ec61d91bb622e9168962efa2041aa0ba90e879108f0331eb24e22` | matches delivered AND internal manifest |
| `lightweight-checks.ps1` | 4,920 | `44ae6958072f201d0ce6e8db4b584f27422c87d8ef7d058c52a4342c811954a3` | matches delivered AND internal manifest |
| `input-manifest.json` (4th member) | 1,159 | `a7380e6220035c6f719f2348ad21be9015f4fc04572f6ead0f0009458d3bb0e0` | the capsule's own manifest |

Three originals total 40,124 bytes. The internal manifest records the reviewed commit
`1a0ce07f…` and main sha256 `75b2189e…0be5a`, and identifies the execution as `gpt-6-astra`,
`reasoning_effort ultra`, agent `/root/atr_final_ultra`.

⛔ **This is byte intake only.** `lightweight-checks.ps1` was NOT executed and no reviewer check was
repeated. The capsule's own qualification is carried forward: the raw model service transcript is not
part of this three-file directory, and the coordinator owns the actual ultra execution record.

## 4 · Parent execution extracts for the applied repairs

These are the commands the parent actually ran and their actual results, as recorded in this
session's transcript. Nothing was re-run to produce them.

**ATR U1–U4 / E1 / E2** (commit `f4a47c3f`). The U1 derivation was executed against the cached TAF15
sequence and returned, verbatim: first complete RG at 1-based residues `(175, 176)`; prefix 1-161 = 0
complete RG; 1-174 = 0; 1-175 = 0; 1-176 = 1; residues 173-178 = `DNRGYG`. Post-apply measurement:
`submission_metrics.measure(...)` → `{'main_words': 6569, 'abstract_words': 245, 'figures': 1,
'tables': 5, 'display_items': 6, 'references': 10}`; `lint_style` 0 ERROR across 15 files exit 0;
`lint_consistency` 0 ERROR exit 0; `test_pinned_figures_every_home` 292 passed. ⚠ Two style errors
were introduced by the first pass of this edit and removed before commit; that is recorded here
rather than hidden.

**MF1** (commits `c7a1d468`, `d1c4de02`). `V4` read from `systems/graph/instruments.json`:
`known_answer_control.state = "none"`, note "built and staged with no result key; never completed;
not authorized". `systems_check.py --check | grep -c B5` → 6, none naming `RT-METHODS-PAPER`. The
twelve-attempted record read from `pose-conditionality-census.json`: `n_pairs_attempted 12`,
`n_gradeable 0`, `n_excluded_by_a_pre_registered_rule 2`, `n_pairs_carrying_an_unrun_status 6`. Quote
alignment verified by reconstructing the §2 blockquote and comparing to
`PUB-METHODS.what_it_would_claim`: `MATCH: True`.

**PR2** (commits `4d8fa9e3`, `94af5aa8`, `8c76f51b`). Three producer runs, each once, each exit 0,
each followed by a parent-computed leaf comparison. Run 1: 1142/1142 leaves, no key/type change, zero
non-string leaves changed, 4 changed strings. Run 2: same, 2 changed strings. Run 3: same, **521
numeric and 52 boolean leaves all equal**, 3 changed strings. `--check` OK exit 0 after each;
`pytest` over both fusion-partner guards 146 passed exit 0, from a measured baseline of 5 failed /
132 passed.

## 5 · Scope caveats carried forward unchanged

- ⚠ **The 907 and 2394 figures are not comparable as an error-identity statement.** 907 was recorded
  from ONE tracked-stash comparison in which error identity was never compared. 2394 is the count
  `systems_check.py --check` reports now, measured identical with and without this session's changes
  by stashing them. Equal totals would not have been identity verification either, and neither number
  is offered as one.
- ⚠ `lint_citations` still fails repo-wide, pre-existing and untouched.
- ⚠ `lint_claims` reports 1 ERROR / 183 WARN across 137 files, byte-identical with and without this
  session's changes, in a paper none of these batches edited.
- ⚠ HW1's `NOTES.md` §8 records six intermediate build fragments deleted **by HW1** before delivery.
  Their content is contained in the delivered files, but embedded content is not proof the original
  bytes survive. They were not recovered and were deliberately not recreated.
- ⚠ "Everything demonstrated is in the transcript" is a limited claim. It does not establish that
  every original scratch byte was retained, and it is not offered as doing so.
