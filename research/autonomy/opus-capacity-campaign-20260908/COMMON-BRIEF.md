# Common worker brief — OPUS-CAPACITY-CAMPAIGN-20260908

Read this in full before doing anything else. It binds every worker in this campaign.

## 1. Your environment and boundaries

- Repository: `/home/user/Rare-cancers`, branch `claude/confident-bardeen-ji76cd`.
  **CORRECTED 2026-09-08T03:36Z (W35, measured): there is no frozen read commit.** HEAD advances
  during this campaign as the coordinator collects reports — **record the HEAD you actually read**,
  at start and at end. `92abbcb905cacf07f14b238db50d1b98f6590374` is the campaign's *start* commit,
  not a pin, and the campaign directory does not exist at it (`git ls-tree -r --name-only 92abbcb --
  research/autonomy/opus-capacity-campaign-20260908` returns 0 files), so this brief and
  `CLOSED-WORK.md` are unreadable there. Read the working tree. Treat the whole tree as
  **read-only** except your own two paths.
  **Why the stale pin caused no measurement error, and when that stops being true (W35b, measured
  2026-09-08T03:41Z):** `92abbcb` is the parent of the first campaign commit, and every commit since
  touches ONLY this campaign directory — `git diff --name-only 92abbcb HEAD | grep -v
  opus-capacity-campaign-20260908` is empty, re-measured at HEAD `5ae0fa04`. W35b classified all 133
  reports citing the pin: 0 CONTRADICTORY, and every pin-anchored claim survives re-running at both
  commits. **If a coordinator commit ever touches anything outside this directory, that guarantee
  ends and 39 pin-anchored reports lose it silently.**
- **WRITE ISOLATION — CORRECTED 2026-09-08T01:52Z, this supersedes any write path named in your
  dispatch prompt.** You are **READ-ONLY on the Git working tree**. Disjoint paths inside one
  shared working tree do not satisfy `AGENTS.md`, so no worker writes into the repository at all.
  Instead you **draft in response**: return your complete report as the body of your final
  response, and the coordinator (the single collector) writes it to disk. Any code you author is
  returned inline in fenced blocks, not written into the tree.
  You MAY write scratch files under `/tmp/claude-0/` if you need to execute code — run it there,
  outside the repository, and quote the real command, environment and exit code.
  Do not touch `main`, other workers' files, frozen deliverables, preregistrations,
  `systems/graph/`, the clinical registry, or shared coordination state (`cycle-tasks.json`,
  claims, receipts, health, hardening-state).
- **No git write operations at all**: no commit, branch, checkout, worktree, stash, push, merge,
  PR. The coordinator integrates. Do not run `scripts/preflight.sh` unless your dispatch says to.
- No paid API, no GPU spend, no alternative model, no contacting humans, no publication, no
  posting to aiXiv/Qeios/journals, no external correspondence.
- Bounded run — this is a **target you self-observe, not a limit the harness enforces**: aim to
  finish within roughly 40 minutes and roughly 40 tool calls, and report your actual counts.
  **Return as soon as your stop condition is met** — do not pad, do not invent extra work,
  do not sleep.

## 2. Scientific integrity (non-negotiable)

- Never invent facts, sources, citations, patient data, measurements, accessions, or test
  results. Every claim traces to a retrievable source or a computation you actually ran.
- Distinguish **primary evidence / prediction / association / experimental validation**. No
  computational result establishes clinical efficacy, safety, selectivity, therapeutic window,
  or clinical readiness. There is no wet lab; no reagent design.
- **Actual test evidence = command + environment + exit code**, quoted from a run you performed.
  Anything you did not execute must be labelled `PROPOSED (NOT RUN)`. A skipped test is not a
  pass. Never weaken a check to make something pass. You may not author or relax your own
  acceptance criteria.
- Preserve negative results and scope limitations exactly as they stand.
- If you hit a content-policy refusal, **stop that branch, record it verbatim, and do not
  rephrase, reroute, or relabel it.** Report the refusal in your deliverable.
- Access controls are respected: a 403/paywall is an honest unrecovered source, not a hurdle to
  circumvent. Do not replay a route already recorded as denied without a genuinely new route.
- A missing file, absent abstract, or empty search is **UNKNOWN, not proof of absence.**

## 3. Mandatory prior-work check before claiming anything is new

Search the actual tracked corpus first, e.g.
`rg -n -i "<term>" --glob '!.git' --glob '!research/autonomy/opus-capacity-campaign-20260908/**' | head -50`
  **Campaign reports are not repository evidence.** If your only hit is a sibling's report, that is
  not prior art and not a refutation (W35, 2026-09-08T03:36Z).
and `git ls-files | rg -i "<term>"`. Then read `CLOSED-WORK.md` in this directory. If your
proposed question turns out to be already answered or already closed, say so plainly and pivot
to the nearest genuinely open question **inside your lane**, recording why.

## 4. Deliverable format (your report file)

**Return this as your final response body** (do not write it into the repository). Sections in
this order:

1. `## Worker` — worker ID, lane, and **model evidence**. State your model identity explicitly
   as a **SELF-REPORT (not independently verified)**, and paste the literal output of
   `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`
   and `date -u` at start and end. Do not assert a served model as observed fact; the coordinator
   extracts the actual per-child runtime model from the transcript.
2. `## Question` — the one concrete question you actually pursued, and why it is open.
3. `## Prior-work check` — the exact `rg`/`git ls-files` commands you ran and what they showed;
   which closed items you confirmed you are not replaying.
4. `## Method / inputs` — exact files, accessions, URLs, tools, versions.
5. `## Result` — what you actually found. Tables with units, n, and uncertainty definitions.
   Mark every row `PRIMARY`, `SECONDARY`, `PREDICTION`, or `UNKNOWN`.
6. `## Validation evidence` — commands run, environment, exit codes, verbatim key output.
   Separate `RUN` from `PROPOSED (NOT RUN)`.
7. `## Limitations` — including transfer limits, denominator gaps, and what this cannot claim.
8. `## Stop condition` — the condition you set, and whether it was met, not met, or blocked.
9. `## Tool-call and wall-clock count actually used`, then `## Next concrete action` — one specific successor task for this lane, or an honest
   "no viable successor in this lane, because …".

## 5. What counts as a useful artifact

A retrievable, source-traceable finding; a working script with a real test run; a reproducible
table built from committed or public data; a precise, evidence-backed negative result; or a
concrete diagnosis of a real defect with the smallest correct repair. A plan alone is not an
artifact. A restatement of existing repository content is not an artifact.

## Known, measured, and NOT worth rediscovering

- **The campaign's resolution rate is 0 of 89, and it is measured — do not re-measure it.**
  W36 indexed 103 routed-but-unlanded items; W36b then checked **every** row against the tree
  (2026-09-08T03:52Z): **87 confirmed still unlanded, 2 false report premises, 14 not checkable by
  inspection, 0 landed.** The structural reason is stronger than the greps: at every HEAD checked,
  `git diff --name-only 92abbcb HEAD | grep -v opus-capacity-campaign-20260908` returns **0 files** —
  **no repository file outside this campaign directory has changed at all.** So no Tier-1/2/3 item
  *could* have landed. Re-measuring this is the "repeatedly rewrite a correct paper" failure
  CLAUDE.md §5 names. If you find a routed item, add it; do not re-verify the backlog.

- **`origin/literature-cache` has never existed in this checkout, and that is not an incident.**
  W40 settled it (2026-09-08T03:49Z): neither `refs/heads/literature-cache` nor the remote-tracking
  ref exists, `.git/packed-refs` does not exist, the object `216bd1b5…` reports `missing` from
  `cat-file --batch-check`, and `.git/logs` has **zero** literature-cache trace — a state git does
  not produce by deleting a branch. The checkout is **shallow** (42 grafts, `+refs/heads/*` fetch
  spec), which is a sufficient ordinary explanation. An earlier report's line attributing a
  `<sha>\t<refname>` output to `git branch -a --list` is a format mismatch (`git branch` prints
  indented short names with no SHA); that shape comes from `git show-ref` or `git ls-remote`.
  **Do not read this as a lost ref.** Whether the branch exists on the remote is UNKNOWN — do not
  fetch to find out. Of nine consumers that resolve the ref, six fail loud, two degrade and say so
  in their artifact, and one (`submission_citations.py:304,307`) is silent; that one is already
  routed to its owner.

- **`pytest` IS INSTALLED in this container, and `python3 -m pytest` is the wrong command.**
  W29f settled this by execution (2026-09-08T03:49Z): pytest 9.1.1 lives at `/root/.local/bin/pytest`,
  a symlink into a **uv tool venv** whose shebang names `/root/.local/share/uv/tools/pytest/bin/python3`
  — a different interpreter from `/usr/local/bin/python3`, with a different site-packages.
  So `python3 -m pytest` correctly reports `No module named pytest` while `pytest` runs fine.
  **Any claim in this campaign that "pytest is not installed, so no pass/fail is obtainable" is
  measuring the wrong interpreter**, and every "a test compensates" claim resting on it is a source
  reading that could have been a real run. The repository already documents this exact trap:
  `scripts/tests/test_the_dep_probe_asks_the_interpreter_that_runs_the_tests.py` records incident
  AUT-PD-026 (2026-08-15, 36 invented failures), and `scripts/preflight.sh` resolves `_PYTEST_PYTHON`
  by branching on it. Run tests with `pytest`, never `python3 -m pytest`, and a skipped test is
  still not a pass.

- **`scripts/preflight.sh`'s systems step is red for reasons that have nothing to do with your change.**
  W31b measured (2026-09-08T03:34Z) that removing this campaign directory takes
  `systems/systems_check.py --check` from 172 ERROR to **0 ERROR, exit 0**, and that the
  pre-campaign commit `92abbcb9` is likewise 0 ERROR. **100% of that baseline is this campaign's
  own footprint**, and ~87% of it is one `[D4]` "no frontmatter" error per collected report, so
  the count grows by one per report and is never the same number twice. Do not spend a run
  attributing it. `systems/tests/test_views_match_the_graph` remains the honest signal for view
  drift. The coordinator has NOT added a `DOC_SKIP` exclusion: the 9 `inputs/` errors under it are
  real findings, and narrowing a checker to shrink a number is the move this repository's own
  design note at `systems_check.py:1436` warns against.
