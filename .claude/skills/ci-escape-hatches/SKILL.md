---
name: ci-escape-hatches
description: How to route work OUT of this dev sandbox instead of deferring it. Load the moment you are about to write or think "I can't run X here", "no GPU/network/pip here", "this is blocked", "I can't test this locally", or you hit a 403 at the egress proxy (NCBI, GEO, PMC, EuropePMC, UniProt, Springer all block CONNECT). Also load before dispatching a GitHub Actions workflow, running a feature branch's CI without merging, timing a CI step, supervising a billing fleet, or setting up a self-wake poller. Covers: the two standing escape hatches (Actions runner for networked/CPU/PDF/pip work, spot GPU for heavy compute); workflow_dispatch with ref=<branch>; why the jobs API lag manufactures fake stalls; why a schedule: cron does not supervise a billing fleet; the fleet-armed heartbeat gate; retiring the non-file half of a feature; background-bash self-wake pollers; and GitHub auth/commit-signature noise that is safe to ignore.
---

# The sandbox is not your execution limit

Extracted from CLAUDE.md §6 on 2026-08-15, **verbatim**. The resident tripwire in CLAUDE.md
is the phrase test ("I can't run X here"); this file is what that tripwire routes to.

⚠ **This file is a `pinned-figures.json` target.**

---

## 0 · ★★ THE LADDER HAS RUNGS BELOW CI, AND IT HAS A STOPPING RULE

**trimcrae, 2026-08-22: *"Whatever part of your Claude.md or skills makes you keep trying CI when
googling is fine needs a priority update."*** This file's framing — *the sandbox is not your
execution limit* — is about **capability**, and it quietly became the **default instrument**. It
answers *can I?* and never asks *is this worth a dispatch?*

**Take the rungs in order. STOP at the first one that answers the question.**

| rung | instrument | when it is the right one |
|---|---|---|
| **0** | **`WebSearch`** | Free, instant, no dispatch, no poll, no branch, no artifact. **Default for orienting**: what a thing is, whether it exists, where to sign up. |
| **0b** | **`WebFetch`** | Same speed — ⚠ but subject to the **same egress allowlist** as the sandbox. Measured 2026-08-22: `arxiv.org`, `huggingface.co`, `science.org`, `monperrus.net` all returned `EGRESS_BLOCKED`. **A blocked fetch is not a blocked question** — rung 0 usually still settles it. |
| **1** | **An Actions runner** (§1 below) | The answer must be a **committed artifact someone will later quote**, or it needs pip / PDF / a real browser / bulk retrieval. |
| **2** | **A new script or workflow step** | Only when rung 1 will be **re-run**. Building one to answer a question once is the tail wagging the dog. |

⛔ **THE STOPPING RULE: ESCALATE ON THE ANSWER'S VALUE, NEVER ON THE PREVIOUS RUNG'S FAILURE.**
A rung that did not work is not a reason to climb — it is a reason to re-ask what the answer is
worth. Climbing reflexively is how a one-line question becomes an afternoon.

**Measured the same day, and the contrast is the lesson — one dispatch was right and the next was
not.** Fetching aiXiv's `openapi.json` to a runner was **correct**: the domain was reachable but the
answer was a 42-path API spec that every later claim would be quoted from, so it belonged on
`literature-cache` as an artifact. Then *"Link me on how to make an account"* got: a CI probe of nine
candidate routes, a nonsense control that correctly proved HTTP status could not discriminate them,
and the beginnings of a Playwright renderer **plus a new workflow step** — for a question whose
honest answer was one URL and one sentence. trimcrae stopped it: ***"How is it this hard. I just need
a link."***

★ **THE TELL IS THE QUESTION'S REGISTER, AND IT IS AVAILABLE BEFORE YOU START.** *"Link me"*,
*"what is X"*, *"does Y exist"* asked conversationally wants an answer **now**, and an honest
*"here's the entry point; I couldn't verify the deeper path"* beats a verified answer an hour later.
A number, an identifier or a claim heading for a manuscript, a gate or the registry wants rung 1 —
that is what §7's "never write an identifier from recollection" is about, and it is a **narrower**
class than "anything I am curious about".

⚠ **This does not weaken §4's "$0 observation" rule — it CORRECTS THE INSTRUMENT.** "Take the free
reading now" was always right; reading it as "dispatch a workflow" made the cheapest observation in
the list cost a build. Rung 0 *is* the $0 observation, most of the time.

---

- **★★ "I can't run X here" is NEVER a reason to defer (trimcrae, 2026-07-12, after I repeatedly declared work
  undoable while holding two standing escape hatches).** No GPU, no MD stack, no compiler, no network to a host,
  a **403 at the egress proxy** (NCBI/GEO, PMC, EuropePMC, UniProt, Springer all block CONNECT) — none of these
  is a dead end. Route it out:
  1. **Networked / data / light-CPU / PDF / scraping / needs pip** → a **GitHub Actions runner** (free,
     unrestricted internet, `pip`/`apt` allowed). Write it **pure-stdlib** where you can, add a
     `workflow_dispatch` (`permissions: contents: write`) that commits outputs back to the triggering branch,
     dispatch it, then poll with a background poller. Exemplars, all verified to exist 2026-08-05:
     `emc-expression-datasets.yml` + `atr_hrd_sarcoma_series.py` (**GEO**, and it is also where a GEO series
     gets characterised before anything is built on it); `fetch-literature.yml` + `scripts/lit_fetch_urls.py`
     + `scripts/fetch-paper.mjs` (**Europe PMC / PDF**, publishing to `literature-cache`; ⚠ its
     `query` path — the Europe PMC search — was DECORATIVE until 2026-08-05: the header claimed it,
     `fetch-paper.mjs` implemented it, and the workflow never invoked it, so a dispatch with a query
     searched for nothing and reported success. Wired up in the same session that wrote this line);
     `fusion-cpu-extras.yml` (→ `modalities-cache` branch).
     ⚠ *Superseded, retained: `atlas-data.yml` + `expression_reprocess.py` + `fulltext_verify.py`. Measured
     2026-08-05: **none of the three exists on this branch, on `main`, on `modalities-cache`, or anywhere in
     history.** They survived because a backticked `.py`/`.yml` name falls outside `ARTIFACT_CITE`'s
     `.json|.jsonl|.png|.csv` scope, so nothing checked them — in the rule that tells every session where to
     route work it cannot do here, which is the worst possible place for a dead pointer.*
  2. **GPU / MD / FEP / heavy compute** → a spot GPU job. Validate-first: `mode=smoke` → one real leg → fleet.
  3. **"I can't TEST it here"** → that is what the smoke / single-shard shakeout is for. Untestable-in-sandbox
     ≠ untestable. Writing hundreds of lines you can't exercise locally is **fine**; you exercise them out there.
  Reserve "deferred" for a **real** external dependency (a spend past the review gate, data only trimcrae has, a
  capability that does not exist yet) — never because the dev sandbox lacks a tool.
- **RUN A FEATURE BRANCH'S CI WITHOUT MERGING — dispatch an ON-main `workflow_dispatch` with `ref=<branch>`**
  (verified 2026-07-11). A *new* workflow file on a feature branch 404s (dispatch requires it on the default
  branch), but an **already-on-main** workflow dispatched with `ref=<branch>` runs **that branch's version of the
  file and its code**. So: edit an existing on-main workflow on your branch (or pass `git_ref=<branch>` to a job
  that clones), then dispatch with `ref=<branch>`. No merge to main required.
  - **AND A `type: choice` OPTION THAT EXISTS ONLY ON THE BRANCH IS ACCEPTED (measured 2026-08-08).** The
    input SCHEMA is read from the dispatched ref too, not just the code — `mode=cohort-search` was added to
    the `options:` list of `emc-expression-datasets.yml` on a feature branch and dispatched at that branch
    ref, and GitHub queued it (run `31256827584`). So a new mode needs **no** fallback of smuggling itself
    into an existing mode's arm, which is what a plan had budgeted for on the assumption that the default
    branch validates inputs. ⚠ The **file** must still be on `main` — this loosens the input rule, not the
    404 rule above it.
- **⏱ TIME A CI STEP FROM ITS *COMPLETED RECORD*, NEVER FROM A LIVE POLL (measured 2026-07-27, two misreads
  in one day).** The jobs API **lags**: it reported a finished 3-minute step as `in_progress` for ~18 minutes,
  and a finished 4.0-minute run as `in_progress` for ~50 minutes. Polling it while a run is live therefore
  manufactures a stall that is not there — and §4 says unexpected slowness must be investigated, so a fake one
  burns a real diagnostic. Read `started_at`/`completed_at` **after** the step completes. (The measured
  per-submit figure this rule came from has its one home in `congeneric_fanout_vast.mode_launch`, next to the
  per-rental ledger save it justifies — do not re-type it here.)
- **★★ A `schedule:` CRON DOES NOT SUPERVISE A BILLING FLEET — AN AGENT HAS BEEN DOING IT BY HAND (measured
  2026-07-27).** State this plainly to trimcrae rather than letting "there's a cron for it" stand: on the day
  it was measured, **25 of the last 30** step-1 autoscale runs were `workflow_dispatch`, not `schedule`. GitHub
  throttles this repo's schedules to a small fraction of what the cron asks for, so the automation is **not
  self-sustaining** — the gap between scheduled ticks has in practice been covered by an agent remembering to
  dispatch, and when the agent stopped, supervision stopped and nothing said so. Consequences, all binding:
  **(1)** never plan a fleet's safety around a cron interval, and never reassure from one; **(2)** a
  `*/N`-minute cron comment is a REQUEST, not a cadence — the delivered gaps are MEASURED at runtime and
  printed by [`fleet-supervision-alarm.yml`](.github/workflows/fleet-supervision-alarm.yml), the **only
  measurement** of them (per rule 1, do not re-type a remembered figure into a workflow comment — that is
  exactly how a stale "~55-65 min" survived into two files and made a normal silence look like an outage;
  ✅ both were closed 2026-08-05, over a week after the alarm's own header recorded that they were stale.
  ⚠ *Superseded, retained: "which is their one home." The dated 2026-07-27 measurement is narrated in
  `fleet_supervision_alarm.py` and quoted in three workflow headers, so "one home" was false of the
  historical figures; it is true only of the live reading, which is what the rule is actually about.*);
  **(3)** while any fleet
  is billing, **you** are the supervisor — dispatch the tick yourself on the cadence the work needs.
- **★★ A SUPERVISOR WITH NOTHING TO SUPERVISE MUST NOT HEARTBEAT (trimcrae, 2026-08-06: *"Why would we need
  supervision for tests that aren't running? That seems like a terrible system"*).** Measured that day:
  **1,476 commits to `main` in 24 h, 1,438 of them CI ticks, 703 saying in their own subject line that they
  did nothing**, while the account census read `n_instances: 0`. The churn was DELIBERATE — the commit trail
  was chosen as the liveness channel because a `git diff --quiet` guard had once frozen three lanes'
  artifact dates and made healthy reapers look stopped — but the design had no **OFF** state, so it
  heartbeat identically whether or not a fleet existed. **Proof-of-life for a watchman guarding nothing is
  worth nothing:** a reaper that dies over an empty account costs $0, which is exactly when you do not need
  to hear from it. One home: [`fleet_armed.py`](./research/modalities/fleet_armed.py), opted into per lane
  via `PUBLISH_HEARTBEAT_LANE` in [`publish_artifacts.sh`](./research/compute/publish_artifacts.sh).
  Three properties, all load-bearing: **(a)** what is gated is the **COMMIT, never the work** — every cron
  still fires and every lane still ACTS, so a reap that needs to happen still happens; **(b)** the census
  lane is **exempt**, so idle still leaves one hourly commit trail and "no commits at all" stays a real
  signal; **(c)** **FAIL-ARMED** — a census that is missing, unreadable, stale or short a field publishes as
  before, and idle exits `10` rather than `1` so a traceback can never be read as "nothing to supervise".
  - **★★ (b) WAS INERT FOR 8.9 HOURS AND THE EXEMPTION PROTECTED NOTHING (measured 2026-08-06, hours
    after the rule above was written).** `fleet_armed.CENSUS_LANE` is `account-census`, and **no workflow
    passed that name.** The repository's only writer of the account census — the `reps-diag` job in
    `gpu-ternary-fep-vast.yml` — published it under `ternary-reps-forensic`, which IS gated. So on an
    empty account the sequence was: write a fresh census → `fleet_armed` reads **that fresh census** →
    `n_instances: 0` → IDLE → publish skipped → **the fresh census is discarded.** The committed copy
    then aged past `account_orphan_alarm.py`'s 45-minute threshold, which suppresses **every lane
    verdict** — so the account-keyed alarm printed `CENSUS-STALE`, `lanes: null`, `orphans: null`, and
    the repository could not say whether any host was billing. That is precisely the 2026-08-01 failure
    the alarm was built for, reintroduced by the guard meant to make silence meaningful.
    **Measured:** last census commit `01:46Z`; at `10:31Z` a dispatched `reps-diag` wrote a fresh census,
    reported `success`, and threw it away — the file on `main` still read `01:44:58Z`.
    ⛔ **THE GATE WAS OBEYING ITS INPUT. THE DEFECT WAS A STRING** — documented in three places, wired to
    a name nothing used, so the design read as safe while the one artifact it existed to protect was the
    one being dropped. **A property asserted in prose about a value passed by a caller is not a
    property; it is a hope.** The census now publishes in its own call under the exempt lane and the
    forensic stays gated, and the WIRING is asserted rather than described —
    `tests/test_fleet_armed.py::test_the_exempt_census_lane_is_actually_used_by_the_census_writer`
    fails the build if any census writer stops using the exempt lane, or smuggles the census back into a
    gated publish.
  - **★★ "EXEMPT" MEANS EXEMPT FROM THE FLEET GATE, NOT FROM ALL JUDGEMENT — SEPARATE THE READING FROM
    THE COMMIT (trimcrae, 2026-08-06: *"Why do we even need the census to be always on?"*).** It does
    not, and the fix above over-corrected — ⚠ *superseded, retained: "its own **unconditional** call".*
    Two things were being conflated, and only one of them is unconditional:
    **THE READING must be** — it is the ONLY detector of a host our own launch records do not know
    about, one left by a lane that died or from an earlier session. **You cannot gate it on "did we
    launch something", because the case it catches is precisely "a host exists that our launch records
    missed"** — which is why the account-keyed alarm is account-keyed.
    **THE COMMIT need not be.** A commit saying *"still zero"* carries no information — the original
    complaint, and correct. What it carries is **proof the detector is alive**, needed once per
    staleness window, not once per tick. ⛔ **And that proof cannot be dropped either:** *"stale census
    whose last reading was zero"* would have to read as fine, which makes a **dead detector
    indistinguishable from one that keeps reading zero** — the fail-quiet direction, the same failure in
    a new costume. So the lane commits on `n > 0`, on a failed read, or when the **published** copy is
    about to age past the alarm's window (`CENSUS_KEEPALIVE_S` = 30 min against the alarm's 45), and is
    otherwise silent.
    ⚠ **And the published copy, never the working-tree one** — by the time the gate runs, the tree
    already holds this tick's fresh reading, so its age is ~0 every time and the question always answers
    "no". ⛔ **The first implementation of that lookup resolved `git show HEAD:<path>` against
    `research/` instead of the repo root, so every lookup failed — and because the failure is
    FAIL-ARMED, the lane published on every tick exactly as before. A broken guard that no-ops into the
    previous behaviour produces NO SYMPTOM, and every keep-alive test missed it because they all
    monkeypatched the seam.** `test_the_committed_census_lookup_works_against_the_real_repo` exercises
    the real function against the real checkout for that reason. **Mock the thing under test and you
    test the mock.**
- **★ WHEN YOU RETIRE A FEATURE, ASK WHAT PART OF IT IS NOT A FILE (measured 2026-08-06).** The
  patient-facing site was deleted on 2026-08-05 — HTML, assets, templates and the deploy workflow all gone,
  and `ls .github/workflows/ | grep -i page` returns nothing. **Pages kept building anyway: 52 of the last
  100 Actions runs repo-wide.** GitHub Pages has two independent switches and only one is a file; the other
  is the repository **setting** (Settings → Pages → Source), which lives in no branch and survives every
  commit. Its runs carry `path=dynamic/pages/…` — the `dynamic/` prefix is the tell that no workflow file
  produced them. ⛔ **A retirement sweep that greps the repo can only find the half of a feature that lives
  in the repo**; Pages, branch protection, Actions permissions, secrets and environments are invisible to
  every checker here. Accounting: [`systems/MIGRATION.md`](./systems/MIGRATION.md) → Phase 2 (a).
- **Self-wake = a BACKGROUND-BASH POLLER, not cron** (verified 2026-06-30; a sibling session ran 48 h this way).
  Launch the loop with `run_in_background: true`; its exit delivers a `<task-notification>` that re-invokes you —
  that completion *is* the wake-up, with no user message. Poll the public Actions API (no auth for a public repo,
  ~60 req/h so `sleep 70`) and exit early:
  ```
  for i in $(seq 1 60); do
    s=$(curl -s "https://api.github.com/repos/trimcrae/Rare-cancers/actions/runs/<RUN_ID>" \
        | python3 -c "import sys,json;print(json.load(sys.stdin).get('status'))")
    [ "$s" = completed ] && { echo DONE; break; }; sleep 70
  done
  ```
  On wake: read the output, act, launch a FRESH poller on the next run id. Restart-resilient — all state is in
  the repo/S3. Get a new run id via `curl .../actions/workflows/<wf>.yml/runs?per_page=1`. **`CronCreate` is NOT
  reliable** (vanished twice within ~25 min even with `durable:true`); **`ScheduleWakeup` did not fire** outside
  `/loop` dynamic mode.


## Environment noise to ignore


- **GITHUB AUTH "EXPIRED" IS A FALSE ALARM — retry, never escalate (2026-07-09).** On any `mcp__github__*`
  "requires re-authorization / token expired", assume **you** are wrong: it refreshes itself. Retry the same
  call; if it still fails, wait (`run_in_background` sleep 60–120 s, foreground short sleeps are blocked) and
  loop several times over a few minutes. Do not tell trimcrae the connection is down, do not halt, do not ask
  them to reconnect. Only consider surfacing after many spaced retries across tens of minutes.
- **COMMIT-SIGNATURE / "Unverified" WARNINGS ARE FINE TO IGNORE (2026-07-10).** The repo is configured for SSH
  commit signing but the private key is not mounted, so commits land unsigned. The committer identity is already
  correct, so the hook's suggested `--amend --reset-author` / `rebase --exec` fixes change nothing, and
  force-rewriting shared history for a signature you cannot generate is strictly harmful. **Commit normally and
  move on.**

