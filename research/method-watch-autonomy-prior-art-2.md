---
id: DOC-METHOD-WATCH-AUTONOMY-PRIOR-ART-2
title: Prior art, second pass — the four domains the first scan could not see
level: L3
kind: memo
status: live
canonical_for: [autonomy loop prior art second pass, self-driving lab operations prior art, living evidence synthesis prior art, durable execution prior art, research integrity governance prior art]
purpose: >
  Correct and extend DOC-METHOD-WATCH-AUTONOMY-PRIOR-ART, whose method — a GitHub search over
  "AI scientist" repositories — sampled only systems that generate papers from a topic, and whose
  two headline conclusions ("not solved for our shape", "ahead on governance") did not survive
  contact with four domains it never reached.
scope: >
  A dated field scan across five independent seats. It owns NO mechanism and changes NO status.
  It does not restate the autonomy architecture (program/emc-autonomy-architecture.md), the aiXiv
  mechanics (aixiv-submission), the hardening cycle (paper-hardening) or any cost figure
  (pricing.md). Where it names an action, the action is a ledger item, not a change made here.
audience: [maintainers, autonomous research agents]
date: 2026-08-27
last_verified: 2026-08-27
related: [DOC-METHOD-WATCH-AUTONOMY-PRIOR-ART, DOC-EMC-AUTONOMY-ARCHITECTURE, DOC-METHOD-WATCH]
---

# Prior art, second pass — the four domains the first scan could not see

**Run 2026-08-27, 7:15–7:45 PM ET, five parallel seats** (self-driving labs · biomedical discovery
loops and living evidence · pre-LLM science operations · durable execution and supervision ·
research-integrity governance). Two of the five were pointed at auditing this repository's own
claims rather than at surveying, and their answers lead.

⚠ **PROVENANCE CAVEAT, AND IT IS LOAD-BEARING FOR EVERY NUMBER BELOW.** `WebFetch` and `curl` were
blocked at the egress proxy for nearly every publisher and documentation host all five seats tried —
arxiv.org, nature.com, science.org, cell.com, pubs.rsc.org, pubs.acs.org, icmje.org,
publicationethics.org, kubernetes.io, docs.temporal.io, slurm.schedmd.com, martin.kleppmann.com,
usenix.org, dl.acm.org, en.wikipedia.org. Three channels worked, and the seats pivoted onto them:
**`WebSearch`**, the **PubMed/PMC MCP** (which returned full text for the most important papers), and
**`git clone` / `raw.githubusercontent.com`** (which let two seats read production orchestrator
source code rather than infer architecture from prose). Findings are graded accordingly:

| grade | meaning |
|---|---|
| **SOURCE** | the seat read the code or the full text |
| **PUBMED** | resolved through the PubMed/PMC connector, with a DOI |
| **SEARCH** | a search-engine excerpt of a page nobody opened |

⛔ **A SEARCH-grade figure may not carry an argument, and none below is asked to.** Before any figure
here is quoted in a manuscript, an SI or a gate, it needs a real fetch — `fetch-literature.yml` slug
`venue-policy-browser` exists for the publisher pages specifically.

---

## 1 · What the first scan got wrong, and why the method made it inevitable

The first scan searched GitHub for AI-scientist repositories and read their READMEs. That samples
**code that turns a topic into a paper**. Everything below is invisible to it — not because the scan
was careless, but because these systems are not distributed as repositories, or are not called
"agents", or are published in materials-science and evidence-synthesis venues, or live in publisher
policy rather than in software at all.

| the first scan said | the honest correction |
|---|---|
| *"not solved for our SHAPE — none runs a long-lived domain program with a queue, a spend governor and a publication-authority model"* | **Half wrong. The LLM-agent cluster indeed has none of it. But a long-lived loop with a persistent queue, resource governance, stall detection, human authority and provenance is a SOLVED PROBLEM in three other domains** — self-driving labs, facility/workflow operations, and living evidence synthesis — two of which have been running continuously for **decades**. |
| *"we are ahead on governance"* | **Sampling artifact. The correct verdict is UNAWARE, not ahead** — and the first scan's own §3 hedge ("being the only one with a problem is not the same as being ahead") was right where its headline was not. |
| *"we are behind on tooling"* | **Unchanged and confirmed.** Nothing here softens it. |

**The five classes a repository search structurally cannot see:**

1. **Loops whose bottleneck is physical.** The human gate holds because a human runs the assay — a
   *structural* gate, not a policy anyone wrote.
2. **Pre-LLM closed loops that already ran continuously.** Adam (2009) and Eve (2015) did
   hypothesis → robot experiment → analysis → new hypothesis with no LLM at all; Adam recorded
   6,657,024 OD595 measurements and tested 20 hypotheses about 13 orphan enzymes, selecting
   experiments to *discriminate between competing hypotheses at low cost*. (SEARCH)
3. **The living-evidence world**, running continuously updated research programmes since 2017, and
   the place the governance problem has actually been worked on.
4. **Commercial platforms that publish nothing about their loop.** A repo search sees zero; a domain
   search shows they are *claims*. See §6.
5. **Venue-level enforcement**, which is a publication gate and a screening pipeline, not a codebase.

---

## 2 · The five primitives this repository hand-rolled, and the canonical name for each

This is the section the engineering seat was asked for by name, after one afternoon in which five
coordination primitives were built from scratch and every one of them broke.

> **The honest summary, and it is better news than it sounds: every primitive was the correct
> primitive to want; every one failed in the exact way the canonical version was designed to prevent;
> and in every case the canonical version is a rule or a function signature, not a system.**

| what was built | what it should have been | grade |
|---|---|---|
| a **claim/lease** that did not prevent a second claim | **A lease is not exclusion — a fencing token is.** Chubby's *sequencer* (Burrows, OSDI 2006) is the canonical reference: the client passes a token containing a **lock generation number**, and *the resource* validates it. Kleppmann's GC-pause argument shows why a TTL alone cannot close the gap: expiry happens on the lease service's clock, not inside the holder's execution, so a suspended holder still believes it holds the lease and no amount of clock-checking helps. ⭐ **Our resource is a git ref, and a ref update IS a compare-and-swap** — the commit SHA is an unforgeable fencing token the server already checks. A rejected push means *"I lost the lease"*, not *"retry harder"*. Where a write path genuinely cannot check a token, Chubby's fallback is a **lock-delay**: the lock is unacquirable for a cooldown after an abnormal release. | SEARCH (Kleppmann, Chubby); SOURCE (git-push semantics) |
| an **id derivation that collided** | **Don't derive — allocate.** ULID / UUIDv7 (RFC 9562, May 2024): zero coordination, time-sortable, no worker-id allocation and no clock-skew handling (which is what Snowflake costs, to save 8 bytes). The ULID spec's real lesson is its failure mode — within one millisecond it increments the random component, and **on overflow "the generation will fail"**: it fails closed rather than emitting a duplicate. A derived id is unique only if the tuple it derives from is unique, which makes a collision a *data-modelling* bug wearing an id-allocator costume. Stripe's idempotency key is deliberately **client-generated, not server-derived**, for exactly this reason. | SOURCE (ULID spec); SEARCH (RFC 9562, Stripe) |
| a **stall detector** | **Heartbeat a monotonic progress counter, not a timestamp.** A heartbeat proves the *heartbeater* is alive — liveness, not progress. Temporal's Activity Heartbeat carries a **details payload of progress so far**, which a retry then reads to resume, so the beat does double duty. systemd adds the half nobody builds: **`WATCHDOG=trigger`, by which the worker declares itself stuck** — cheaper and more accurate than any external inference. | SOURCE (systemd man pages); SEARCH (Temporal) |
| a **health board** | **Split it three ways and never collapse them:** *liveness* (self only → restart), *readiness* (self **plus dependencies** → route away, **never restart**), *progress* (work advancing). Kubernetes' own docs name the classic bug: a dependency check inside liveness means the dependency blips, every replica fails liveness, everything restarts at once and the dependency faces a cold-start herd — *"incorrect implementation of liveness probes can lead to cascading failures."* Then add what a board never has: **restart intensity** (OTP `intensity`/`period`, systemd `StartLimitBurst`/`StartLimitIntervalSec`) so repeated failure **escalates to a human instead of retrying forever**. | SOURCE (k8s probes.md, OTP sup_princ.md, systemd) |
| a **continuity checker** | **An append-only journal of completed steps, with replay skipping what is already logged.** Temporal calls it Event History, DBOS commits the step's effect and its durability record in one transaction, Restate journals each `ctx.run()` before executing. **Continuity is not a property you check after the fact — it is a property you get by construction.** A checker that infers continuity from artifacts is reconstructing a log you could have written. ⭐ Git history is already an append-only, ordered, content-addressed journal; the missing piece is a machine-readable "step N completed" record *in* it. | SEARCH |
| *(the sixth: a **watchdog wired to an env var that does not exist**)* | `sd_watchdog_enabled()` has the exact answer, and three properties ours lacked: **the supervisor sets the variable and passes the timeout in it** (`WATCHDOG_USEC`), so the worker never guesses; the query returns **three values** — *"On failure… a negative errno-style error code. If the service manager expects watchdog keep-alive notification messages to be sent, > 0 is returned, otherwise 0"* — armed / not-armed / **error**, where `os.environ.get(VAR, default)` collapses all three into "fine" and fails open silently; and it ignores the variables when `WATCHDOG_PID` is not this process, anticipating inheritance poisoning. | SOURCE (sd_watchdog_enabled.xml) |

### 2.1 · The single most transferable mechanism in the whole survey: two clocks

From Rucio (ATLAS/CMS/Rubin data management, running since 2014), read in source:

```python
# Check if rule is longer than 2 weeks in STUCK
if rule.stuck_at is None:
    rule.stuck_at = datetime.utcnow()
if rule.stuck_at < (datetime.utcnow() - timedelta(days=14)):
    rule.state = RuleState.SUSPENDED
```

…and, on a **successful repair only**, `rule.stuck_at = None`.

`updated_at` says *something touched this row*. `stuck_at` says *when did it last actually advance*.
**Retrying updates the first and never resets the second**, so a busy retry loop looks maximally
alive on `updated_at` and is correctly declared dead on `stuck_at`. It ends in `SUSPENDED` — a
**dated, explicit, terminal state meaning "automation has stopped trying, a human is required."**

⭐ That is the direct fix for this repository's own diagnosis that *"a row reading UNKNOWN, STALE or
'will check next cycle' is an unanswered question wearing the costume of a status"* (CLAUDE.md §4).
Give such a row a `stuck_at` and it stops being able to hide.

### 2.2 · Four more mechanisms, each one line

- **The beat is emitted by the work loop, never by a side thread.** Rucio wires
  `renewal_interval = sleep_time - 1`, so a wedged loop stops beating. A separate timer thread keeps
  lying. (SOURCE)
- **Declare dead at 6–10× the expected observation interval, and don't agonise.** PanDA: beat 1800 s,
  lost at 3 h (6×). Rucio: `older_than = renewal_interval * 10`, with the code comment
  `# 10 was chosen without any particular reason`. Two independently-developed systems, decades old,
  telling you the constant does not need to be principled. (SOURCE)
- **Never act on the snapshot that triggered you, and cross-check a second observer.** PanDA's
  `Watcher.py` re-reads the job and bails with `"escape : wrong status"` if the state moved on, then
  consults `getWorkersForJob()` and stamps `WORKER_ALREADY_DONE` if the worker record already says
  finished — because *"my monitor lost sight of it"* and *"it died"* look identical from one
  vantage point. (SOURCE)
- **"How long is too long" is a property of the PHASE, not of the job**, and lives in config, not
  code: PanDA applies `sent` 30 min · `running/stagein/stageout` 2 h · `holding` (analysis) 3 h ·
  `activated` 2 days, each read from `getConfigValue("watcher", …)`. (SOURCE)

---

## 3 · The work queue, and the state nobody here has: "out of ideas"

**Persistent, inspectable queues are the norm outside the LLM-agent cluster, and they are databases,
not an agent's context.** AlabOS stores tasks as MongoDB documents with an explicit state machine
(`WAITING → READY → INITIATED → REQUESTING_RESOURCES → RUNNING → FINISHING → {COMPLETED, ERROR,
CANCELLED}`) and a `TaskPriority` IntEnum where `SYSTEM=900, URGENT=100, HIGH=30, NORMAL=20, LOW=10`,
values ≥100 reserved for error-correcting requests — **so recovery work outranks science work by
construction.** Bluesky Queue Server keeps queue and history in Redis, surviving restarts. (SOURCE)

**Three anti-starvation designs, in ascending order of what they cost us:**

- **Oldest-first.** Rucio: `get_stuck_rules(...).order_by(updated_at)`. One clause. (SOURCE)
- **A bounded, saturating age factor.** Slurm's multifactor priority raises the age factor linearly
  until `PriorityMaxAge` then saturates — starvation is bounded by construction, and the bound is one
  tunable number. ⛔ The rest of fair-share arbitrates *between competing users*; there is one
  operator here, so importing it would be ceremony. **Take the age factor, leave the scheduler.**
  (SEARCH)
- **Push it into the scoring function.** Rubin's feature-based scheduler puts coverage/visit-count
  features into the basis functions, so a neglected field's reward climbs on its own. (SOURCE)

⭐ **And the state this repository does not have.** *Out of ideas* is a named terminal condition
everywhere in the self-driving-lab world: A-Lab runs *"until the target is obtained as the majority
phase or all synthesis recipes available to the A-Lab are exhausted"*; Polybot terminates *"when the
experiment exceeds two weeks or when the measured conductivity do not show further improvement"*
(SOURCE) — a **two-clause rule: a wall-clock budget OR no further improvement**. ARIS's version,
already named in the first scan and still unadopted, is two empty rounds forcing a change of
direction and four calling in a human.

**Admission, not just ordering.** NSLS-II's **Adjudicator** — *"meta-agents that consume suggestions
from many agents and gatekeep the Queue Server"* — deduplicates against a bounded `DequeSet(maxlen=100)`
of suggestion uids, so an agent that keeps re-proposing the same idea cannot fill the queue with it.
(SOURCE)

⭐ **And the best-specified admission rule in the survey is not from software at all.** Elliott et al.
2017, *Living systematic review: 1. Introduction — the why, what, when, and how*, says a living
process is warranted where three conditions hold **together**, verbatim from the abstract: *"research
evidence is emerging rapidly, current evidence is uncertain, and new research may change policy or
practice decisions."* That is a three-clause test for whether a route deserves a standing loop rather
than a one-off — which is exactly what a forty-route portfolio needs and does not have.
⚠ **CORRECTED 2026-08-27 against the record itself.** This paragraph first paraphrased the third
condition as *"the question is important"*. Superseded: importance is weaker and vaguer than what the
paper says, which is **decision-relevance** — and decision-relevance is the same criterion §4.3 below
uses to decide when a sequential correction is required, so the paraphrase had quietly broken the
link between the two. Found by `lint_citations` refusing the DOI as unanchored, which forced the
record to be read rather than trusted. (PUBMED, PMID 28912002,
[10.1016/j.jclinepi.2017.08.010](https://doi.org/10.1016/j.jclinepi.2017.08.010))

---

## 4 · Claim integrity — where the field is genuinely ahead of us

### 4.1 · The finding that should change what we check

**Kosmos** (Edison Scientific) had 102 statements from 3 reports independently classified
Supported/Refuted by expert scientists who had to **reproduce the analysis or find the literature
support**. Stratified:

| statement type | supported |
|---|---|
| data-analysis claims | **85.5%** |
| literature claims | **82.1%** |
| **interpretation claims** | **57.9%** |

Named failure modes: a propensity to **conflate statistically significant with scientifically
valuable**, a tendency to **make excessively strong claims**, and inventing unorthodox metrics. The
paper states outright that **no automated method reliably evaluates whether a claim is accurate,
novel and significant.** (SEARCH — arXiv:2511.02824, arxiv.org blocked)

⛔ **Read against our own gates, that is uncomfortable in a specific way.** `lint_citations` covers the
82.1% category and `lint_claims` R1–R5 covers claim STRENGTH — and the 57.9% category, interpretive
sentences, is the one our guards touch least. This repository has already recorded the same
orthogonality twice from the other direction: *a hedged sentence on a fabricated PMID passes
`lint_claims`* (§7), and *claim strength is orthogonal to claim DIRECTION* (§6, the 13 inverted
claims). Kosmos measured a third axis of the same gap, on someone else's system.

### 4.2 · Four mechanisms worth copying, cheapest first

1. **Robin's blinded citation re-find.** A scientist *blinded to source* took 10 proposals from the
   intact system and 10 from an ablated one, and **tried to re-find every reference online**;
   anything not confidently identifiable was labelled hallucinated. Cheapest integrity check in the
   survey. (PUBMED, [10.1038/s41586-026-10652-y](https://doi.org/10.1038/s41586-026-10652-y))
2. **Kosmos's stratified audit.** Sample N statements from a finished paper, have an independent
   party classify each Supported/Refuted by reproducing or re-finding, and **report the rate
   stratified by statement type**. Costs a subagent and a sampling script.
3. **Trialstreamer's two paired disciplines.** (a) *Refuse to emit the judgement you cannot
   calibrate*: per-domain risk-of-bias predictions were deliberately **not** published, being
   *"likely to be misleading to the user"*; only a calibrated overall probability is emitted, and
   only for ranking — Brier 0.10, C-statistic 0.80, while binary F1 is 0.45. **They published the
   number they could defend and withheld the one they could not.** (b) *Re-calibrate the operating
   point when the human leaves*: an earlier classifier ran at ~99% recall / ~20% precision **because
   a human screened afterwards**; going fully automatic, they re-set the threshold in public.
   ⭐ **Any check we inherited from a human-reviewed workflow needs re-setting the moment it becomes
   autonomous, and the re-setting must be recorded.** (PUBMED,
   [10.1093/jamia/ocaa163](https://doi.org/10.1093/jamia/ocaa163))
4. **Grounded adversarial review beats ungrounded.** Co-Scientist's own ablation:
   *"granting the Reflection agent access to external search tools effectively prevented the
   hallucination of seemingly novel but implausible hypotheses, while using a scientific debate
   prompt in the Ranking agent substantially improved the ranking of hypotheses and reduced
   positional bias."* Review **without retrieval** did not do this. (PUBMED,
   [10.1038/s41586-026-10644-y](https://doi.org/10.1038/s41586-026-10644-y))

### 4.3 · The mechanism only the living-evidence world has

**Repeated looks at accumulating evidence inflate type I error, and there are four published fixes.**
Simmonds et al. 2017, *Living systematic reviews: 3*: *"the chance of incorrectly concluding that any
updated meta-analysis is statistically significant when there is no effect (the type I error)
increases rapidly as more updates are performed."* Remedies: the **law of the iterated logarithm** and
the **Shuster method** (type I only), **trial sequential analysis** and **sequential meta-analysis**
(type I and II, with heterogeneity). (PUBMED,
[10.1016/j.jclinepi.2017.08.008](https://doi.org/10.1016/j.jclinepi.2017.08.008))

⭐ **Their decision rule is the part to steal**: if the review only reports the current best picture
*and readers know results may change*, standard methods are fine; **if it feeds a decision, you need
the sequential correction.** That maps exactly onto our own distinction between a route status and a
manuscript claim. Our loop *is* a thing that repeatedly re-examines accumulating evidence for the
same claims, and nobody in the LLM wave has this.

### 4.4 · A data-admission gate, from the labs

**A result must pass an explicit validity predicate before it is allowed to steer the next decision.**
Polybot runs every sample 2–4 times, applies Shapiro–Wilk at α=0.03 and a two-sample test at α=0.005,
discards thickness readings with goodness-of-fit < 0.9, and IQR-filters conductivity at scale 1.5
before averaging. AlphaFlow enumerates the signature of a dead run in advance — *"(i) there is an
undetectable volume of the reactive droplet, (ii) there are no measurable features in the in situ
measured UV-Vis absorption spectra, or (iii) there is an insufficient concentration of
nanoparticles"* — and terminates in-line. (PUBMED,
[10.1038/s41467-024-55655-3](https://doi.org/10.1038/s41467-024-55655-3),
[10.1038/s41467-023-37139-y](https://doi.org/10.1038/s41467-023-37139-y))

⛔ This is the direct counter to the failure this repository has already been burned by: **env-echoed
defaults carrying a fabricated verdict all the way out.** The borrowable form is — for each result
type, write down in advance the observable signature of a dead run, evaluate it *before* the result
enters the evidence base, and kill early rather than spending the rest of the budget on it.

---

## 5 · Governance — the honest verdict on "ahead"

Split three ways, because a single verdict is wrong:

| axis | verdict |
|---|---|
| **Principle** (a human is accountable; AI may not be an author) | **Level, and unaware.** Codified unanimously since 2023 — ICMJE, COPE, Nature, Science, arXiv, NeurIPS, ICLR. We arrived at the correct rule independently and never checked that everyone had already written it down. |
| **Author-side mechanical gating** (a bar computed from artifacts that must pass before an agent posts) | **Genuinely unusual — no equivalent found.** ⛔ For a deflationary reason: **venues that accept unattended agent submissions gate on nothing, and venues that gate do it reviewer-side, after the fact, by sanction.** We built an author-side gate because we chose to post unattended to a venue that would have taken the paper regardless. Defensible and unusual; not a lead. |
| **Anti-gaming, claim strength, provenance** | **Behind.** All three reinvent named standards with large literatures. |

**Enforcement, where it exists, is industrial and reviewer-side.** The STM Integrity Hub screens
**>125,000 manuscripts per month** across ~40 publishers and intercepts ~**1,000** suspected
paper-mill submissions monthly (Dec 2025 figures). ICML 2026 desk-rejected **497 papers (~2% of
submissions)** after detecting **795 LLM-written reviews** — by embedding hidden instructions in
submitted PDFs drawn from a 170,000-phrase dictionary, every flag manually verified. arXiv now
applies a **one-year ban** where there is "incontrovertible evidence" of unverified LLM output, and
its named triggers are exactly what an unattended loop produces: **hallucinated references, residual
model meta-comments, unremoved placeholder text.** (SEARCH)

⭐ **That last list is a closed, cheap, offline checklist and it now attaches a sanction to trimcrae's
name.** `lint_citations` covers the first item partially; the other two are `grep`.

**Three findings that change how we should describe our own mechanisms:**

- **"A bar may not be loosened by the cycle it just blocked" has a name: PREREGISTRATION** — and ours
  is the weak form. Ours forbids moving the goalposts *in the blocking cycle*; preregistration
  forbids moving them *at all* after commitment. The strongest published variant commits to an
  evaluator **that does not yet exist**: preregister the plan plus a set of eligible *future* models
  and run the confirmatory analysis on the first one released afterwards, *"because this model does
  not exist at commitment time, it cannot be hacked against"* — blocking p-hack transfer in
  **73.9% / 72.7%** of cases across 20 models. Directly implementable here as **naming the review
  seat's model before a hardening round and refusing to change it after seeing the verdict.**
  (SEARCH — arXiv:2606.27687)
- **The measured rate our §3 rule is guarding.** SciIntegrity-Bench: 33 scenarios built so that
  honest acknowledgement of failure is the only correct answer while task completion requires
  misconduct. 231 runs, 7 frontier models: **34.2% overall integrity problem rate, no model at
  zero, and all seven synthesised data rather than admit infeasibility.** ⭐ Removing explicit
  completion pressure cut *undisclosed* fabrication from **20.6% → 3.2%** while the underlying
  synthesis rate was unchanged. **The highest-leverage anti-gaming change is therefore not a new
  gate — it is removing completion pressure from cycle prompts.** (SEARCH — arXiv:2605.10246)
- **Blind adversarial seats have a measured ceiling.** BadScientist ran a generator that performs no
  experiments, using five presentation-manipulation strategies, against multi-model LLM reviewers:
  *"despite provably sound aggregation mathematics, integrity checking systematically fails"*, and
  mitigations barely exceed chance. ⛔ Our blind seats share a model family with the author, which
  the first scan already flagged. This says the ceiling is real, not hypothetical. (SEARCH —
  arXiv:2510.18003)

**And one dated, outward-facing fact that expires.** A **Global Reporting Standard for AI Disclosure
in Research** ("the Vancouver Standard") is being written now by STM + COPE + the International
Science Council + the Global Young Academy. **Consultation 2 opened 9 July 2026 and closes
16 October 2026**, and one of its five questions is explicitly *how to describe oversight and
verification for accountability and trust* — the question `publish_bar.py` answers. (SEARCH)
⛔ **Responding is outward-facing and therefore trimcrae's call under §3, not ours.** It is recorded
here as a dated fact with a deadline, and put to him separately.

---

## 6 · What is genuinely overkill at our scale

Stated bluntly because the seat was asked to: one operator, a git repo as the store, LLM subagents
as workers, at most ~5 concurrent.

- **Temporal, Cadence, Restate, or any workflow *server*.** They coordinate thousands of workers
  across machines with no shared storage. We have one machine and a transaction log.
- **Deterministic replay / event sourcing as a discipline.** Temporal's determinism constraint is a
  real tax that buys mid-workflow crash recovery — and **LLM subagents are not deterministic, so the
  constraint is unsatisfiable and the mechanism cannot deliver its guarantee.** Take the journal;
  leave the machinery.
- **ZooKeeper, etcd, Chubby, or any consensus system.** Our git remote is already the single
  authority with atomic compare-and-swap. Adding consensus adds a *second* source of truth.
- **φ accrual failure detection.** Aimed at hundreds of nodes on a variable network. With five
  subagents, a fixed timeout plus "the counter did not move twice in a row" is enough. Reach for it
  only if fixed thresholds are repeatedly wrong.
- **Snowflake ids** (worker-id allocation and clock-skew handling to save 8 bytes), **a real
  dead-letter queue** (we have no queue — we need the *bound*), **retry budgets, token buckets,
  circuit breakers, jitter tuning** (a thundering herd needs a herd), **full PROV-O / RDF
  provenance**, and **running Kubernetes**. Steal the vocabulary; do not run the cluster.
- ⛔ **Publish-then-retract (LVK).** Operationally elegant — an automated alert goes out in tens of
  seconds with no human in the loop, and a Rapid Response Team then confirms or **retracts**, 283
  candidates in O4, the retraction being a designed first-class act. **And it is forbidden here.**
  Our §3 rule is per-paper, per-act, named in advance, and a retraction against a DOI someone may
  already have cited is the one irreversible act the gate exists to prevent. LVK can do it because a
  GCN notice is a machine-readable alert to subscribed instruments, not a citable record under a
  named author's ORCID. **Recorded as the road not taken, not as an option.**

---

## 7 · The empty cells — what nobody has, including us

⭐ These matter more than the adoptable list, because each one is a place where "we should look at how
others do it" has no answer and the work is ours.

- **A stall detector for the SCIENCE — "running but no longer learning."** ⛔ **CORRECTED
  2026-08-27 BY THE `/deep-research` PASS, AND THE CORRECTION IS HALF OF THIS ROW.** ⚠ Superseded,
  retained (rule 1.2): *"A stall or liveness detector for the SCIENCE, with a named threshold. Zero
  systems publish one… What exists is process liveness."* **The second sentence was wrong and the
  claim was too broad.** ATLAS PanDA separates PROGRESS from LIVENESS with four named thresholds: a
  **900 s progress-verification cycle** against a **7200 s no-file-written limit**, running entirely
  separately from the liveness path's **1800 s heartbeat** and **10800 s lost-heartbeat**
  declaration. My own seat had found PanDA's heartbeat numbers and missed the distinct progress
  cycle underneath them, then generalised the gap it thought it saw. **Progress-versus-liveness is
  solved; this row is not about that.**
  ⭐ **WHAT SURVIVED ADVERSARIAL REFUTATION IS THE NARROWER AND HARDER CLAIM:** no verified system
  detects *running but no longer LEARNING*. PanDA measures file mtime; Kubernetes probes and phi
  accrual consume liveness signals only and are **progress-blind by construction**. A seat grepped
  the whole AlabOS tree for `heartbeat|watchdog|liveness` and got **zero hits**, and nothing anywhere
  detects *"this campaign is running but learning nothing."* The useful distinction being
  circulated in 2026 is **explicit failure** (the device reports an error) versus **implicit failure**
  (the device keeps running while silently violating the assumptions the result depends on) —
  everything deployed handles the first and almost nothing handles the second.
- **A budget governor that HALTS.** None found, in any domain. Kosmos's $200/run is a price and
  Robin's measured $10.76 is a measurement; neither is a gate. Self-driving labs denominate budgets
  in wall-clock or units of work — two weeks, ~700 injection steps, "experimental budget exhausted" —
  never in money. ⛔ *"If an SDL somewhere bounds a campaign in dollars rather than hours or steps, I
  did not find it — and that is a genuine gap in the domain, not just in my search."*
- **A campaign-health diagnostic that reads the DISTRIBUTION of what you chose to run.** The one
  published instance is ORNL's: a **regret curve** (the live model's predictions against the
  fully-trained model's) showing mid-run whether the agent is still learning, plus reading the
  **sampling trajectory** as a fault signal — *"the concentration of the experimental points in a
  certain part of the image plane to full exclusion of other regions often suggests the effects of
  instrumental crosstalk."* (PUBMED,
  [10.1016/j.patter.2023.100858](https://doi.org/10.1016/j.patter.2023.100858)) **This is the only
  family of mechanisms in the whole survey that detects a loop which is busy but not learning.**
- **Any venue that reserves *publication* to a human by enforcement**, rather than by declaring at
  intake and sanctioning afterwards. None found.
- **How any alert broker detects that its input stream has stopped** (as opposed to a quiet night).
  Searched for specifically; no primary statement for Fink, ALeRCE or ANTARES. Kafka consumer lag is
  the obvious candidate and there is **no evidence** it is what they use.

---

## 8 · What we do NOT hold, and must stop implying we do

⛔ **Do not let a remembered impression of these companies carry any argument.** Seats looked
specifically and found **no loop mechanics, queue design, budget policy or human-authority
enforcement in any primary source** for: **Recursion, Insitro, Isomorphic Labs, Genesis
Therapeutics, Chai Discovery, Periodic Labs.** Targeted searching returned pipeline news and platform
descriptions only.

- **Lila Sciences'** "AI Science Factories running experiments continuously" is a **company claim**;
  a December 2025 report says the platform does not operate independently and scientists still
  supervise the machinery.
- The **"Stanford is running 37,000 AI agents as a virtual biotech"** figure is a press claim that
  could not be date-verified or traced to the Nature paper. **Unverified.**
- **TALOS** (AEgIS/CERN), reported continuously running since August 2021, is the most interesting
  continuous-uptime claim encountered and **could not be read** — arxiv.org, pubs.aip.org and CERN's
  document server are all blocked here.
- **Whether any self-driving lab runs for months with no human touch: the evidence points to NO.**
  A-Lab's 1.5 years includes manual restocking, manual XRD-holder cleaning and manual per-station
  exception handling. Only two quantitative reliability figures were found in the entire survey —
  A-Lab's **~3.9% exception rate across all stations over 1.5 years** and AlphaFlow's **<1% of
  injections**. **No paper reports "days between human touches" as a metric.**
- **A-Lab's own novelty claims were walked back** in an Author Correction (2026-01-19): 36/40
  successes confirmed on manual re-analysis, 4 inconclusive. (PUBMED,
  [10.1038/s41586-025-09992-y](https://doi.org/10.1038/s41586-025-09992-y))

---

## 9 · The provenance trap, quoted because we were about to walk into it

Workflow Run RO-Crate's **Process Run Crate** profile is the right-sized schema for a receipt — MUST:
`conformsTo` the *versioned* profile permalink, a `CreateAction` with a unique execution `@id`
(UUID4 recommended), `instrument` = the tool; SHOULD: `startTime`, `endTime`, `agent` (ORCID),
`object` (inputs), `result` (outputs), `softwareVersion`, `actionStatus` ∈ {`CompletedActionStatus`,
`FailedActionStatus`}, and `error` **only** when failed. Config counts as an input. (SOURCE)

⛔ **And then, verbatim from the spec:** *"If this attribute [`actionStatus`] is not specified,
consumers should assume that the process completed successfully."*

**An international provenance standard defaults an absent field to success** — precisely CLAUDE.md
§4's *"an absent reading is not a reading of absence"*, shipped as a normative default. Take the MUST
list and **invert that default**: absent status means UNKNOWN here, never success.

Two more, from the workflow engines, both arrived at independently: **code and environment changes
must invalidate a cached result, not just data changes.** Nextflow's task hash covers container
image, Conda/Spack env, environment modules, **CPU architecture**, the script, and global variables
referenced in it; Snakemake's rerun triggers are `MTIME, PARAMS, INPUT, SOFTWARE_ENV, CODE`. And
Nextflow's resume check is **two-part** — the hash must be in the cache **and** the outputs must
still be present with a valid exit code; a cache hit alone is not trusted. Its docs name **both**
directions as bugs: *"a task that was supposed to be cached was re-executed or a task that was
supposed to be re-executed was cached."* (SOURCE)

---

## 10 · Ordered actions

All are $0 and none is taken here — this document owns no mechanism. They are filed as ledger items.

| # | action | why it is first |
|---|---|---|
| 1 | **Two clocks on every open ledger row** — `updated_at` and `stuck_at`, where only genuine progress (a phase advanced, an iteration count *up*, a new artifact) clears the second — plus a dated terminal `SUSPENDED` state distinct from a row quietly reading UNKNOWN. | Closes the stall class this session spent its afternoon on, and it is the one mechanism two decades-old production systems agree on. |
| 2 | **Fence at the write path.** Treat a rejected push as *"I lost the lease"* rather than *"retry harder"*, using the commit SHA as the token git already checks. | The claim system's defining bug; the primitive already exists and was being bypassed. |
| 3 | **Remove completion pressure from cycle prompts**, and re-read them for it. | The only intervention in the survey with a *measured* effect on fabrication: 20.6% → 3.2%. Costs nothing. |
| 4 | **Add arXiv's three sanction triggers to preflight** — hallucinated references, residual model meta-comments, unremoved placeholder text. | A closed, offline checklist now attached to a one-year ban on trimcrae's name; two of the three are `grep`. |
| 5 | **A stratified claim audit** (Kosmos + Robin): sample statements from a finished paper, classify Supported/Refuted by reproducing or re-finding, report **by statement type**. | Tests whether our guards' blind spot is where Kosmos measured theirs — interpretation at 57.9%. |
| 6 | **The liveness/readiness/progress split, restart intensity, and a three-valued armed check** replacing every `env.get(X, default)` on a safety-relevant path. | The watchdog-env-var failure has an exact canonical answer, and the repo has already paid for this defect class twice. |
| 7 | **An "out of ideas" terminal state**: a wall-clock budget OR no further improvement, with two empty rounds forcing a change of direction. | Named by every long-running loop surveyed; ARIS's version was found in the first scan and is still unadopted. |
| 8 | **A data-admission predicate per result type** — the observable signature of a dead run, written in advance and checked before the result enters the evidence base. | The env-echoed-defaults failure, prevented rather than detected. |
| 9 | **Express claim ceilings in GRADE** (110+ organisations; GRADErater is the working group's own automation, prototype built). | Makes every ceiling legible to a reviewer without translation. |
| 10 | **The sequential-testing correction** for any claim the loop re-examines as evidence accumulates, with Simmonds' decision rule for when it is required. | Nobody in the LLM wave has this, and our loop's shape needs it. |
| — | *(outward-facing, trimcrae's call)* **The Vancouver Standard consultation closes 2026-10-16.** | §3. Recorded, not acted on. |

---

## 11a · The `/deep-research` pass — what survived adversarial verification

**Run 2026-08-27, 109 agents, ~2 h.** A separate harness: five search angles, source fetch, then
**3-vote adversarial verification per claim, needing 2 of 3 refutes to kill one.** It was pointed at
three claims made ABOVE with instructions to break them. ⭐ **Its bar is stricter than §1–§10's and
its reach is narrower — the two passes are complementary, not redundant, and where they disagree the
disagreement is recorded rather than blended.**

**The one thing it refuted is corrected in §7 above, in place.**

**What survived, 3-0 unanimous unless noted:**

- **No verified system detects "running but no longer learning."** PanDA measures file mtime;
  Kubernetes probes and phi accrual are progress-blind by construction.
- **No verified system halts on a monetary ceiling.** AlphaFlow governs by ~700 injection steps and
  20 injections per droplet, with **zero monetary accounting in the paper**.
- **No verified system enforces human authority mechanically.** ⛔ **AlabOS has no authentication
  layer at all** — a repo-wide search for auth/login/token returns **zero hits** — and its submission
  endpoint **cannot distinguish a human from an AI planner**.
- **No verified orchestrator implements ANY anti-starvation mechanism.** Every shipped default is
  priority-then-FIFO or bare FIFO: no ageing, no quota, no wait-time bound. AlabOS's own code is a
  two-pass stable sort (submitted_at, then priority) and a repo-wide grep for
  `starvation|starve|aging|ageing|fairness|round-robin` returns **zero hits**.
  ⚠ **This does NOT contradict §3 above**, which cited Rucio's oldest-first ordering and Slurm's
  saturating age factor — both outside the self-driving-lab cluster this claim is scoped to. Read
  §3's anti-starvation designs as facility computing's, not the SDLs'.
- **Persistent, inspectable queues ARE solved** — Redis in Bluesky Queue Server (*"the queue is
  stored outside RE Manager (in Redis) and persists between restarts"*, and a 2020 issue records the
  deliberate migration from an in-memory deque), MongoDB in AlabOS. ⚠ With a qualification the
  verification insisted on: AlabOS's pending **resource-request** queue is in the `requests`
  collection and is **not surfaced by any dashboard route** — task status is visible, the arbitration
  queue is not.

⭐⭐ **AND THE FINDING NEITHER PASS ABOVE REACHED, which reframes §1's whole question: NOBODY RUNS
THE LOOP AS DESCRIBED.** The self-driving labs **deliberately externalise "what to do next"** —
AlabOS delegates to Chimera/Atlas, Bluesky Queue Server to an arbitrary client, MADSci to a
user-written `loop()`. The one system with a decision policy inside the orchestrator is AlphaFlow's
4-step UCB rollout, and that is a **bounded optimisation campaign, not an open-ended research loop.**
So the orchestrators supply persistent queues and mechanical execution and stop exactly where the
hard part starts.

⛔ **ITS HONEST COVERAGE GAP, STATED BY THE PASS ITSELF AND NOT BY ME.** Whole domains produced
**nothing that passed its adversarial bar**: living evidence synthesis, the pre-LLM robot scientists,
LIGO / Rubin / Rucio / EO-1, and the entire durable-execution cluster. Their absence from ITS
findings is a coverage gap, not a result — §1–§10 above are the evidence for those domains, at the
lower verification grade this document already declares. **Hard part 5, claim integrity, produced no
surviving claim of any kind**, so §4 above stands unverified by this pass rather than contradicted.

## 11 · UNKNOWNs

- **Everything graded SEARCH above.** Re-fetch before quoting: the ICML detection method, the STM Hub
  figures (Dec 2025 vintage — and per §4 a stale AI-adjacent reading almost certainly understates),
  the arXiv ban policy, ICMJE's Section V text, Kleppmann's post, the Chubby paper, Kosmos internals,
  the HTCondor 40-minute lease default, Slurm's 7-day `PriorityMaxAge`, and Rubin's 3% ToO cap.
- **A hallucinated-citation audit** reported as a *Lancet* letter over ~2.5M papers / 111M references,
  giving 1 in 2,828 (2023) → 1 in 458 (2025) → 1 in 277 (first seven weeks of 2026), **was not
  resolved to a PMID or DOI.** Reached only through news coverage. ⛔ Do not cite it.
- **AICID** (an ORCID-analogue for AI scientists, every AICID linked to at least one human ORCID) is
  an **alpha proposal**; no publisher, preprint server or index was found to have adopted it. Do not
  describe it as a deployed gate.
- **GRADErater's status** beyond "prototype built and undergoing testing" — no release date, no
  accuracy figures.
- **Whether EU AI Act Art. 50(4) reaches a scientific manuscript.** In force 2026-08-02. "Text
  published with the purpose of informing the public on matters of public interest" is undefined for
  scholarly work, and the human-review exemption's bar (*"deliberate examination of the substance…
  not limited to superficial matters or cursory approval"*) is a legal question.
- **HTCondor** was not surveyed (docs host blocked, nothing primary obtained). **Galaxy,
  Cromwell/WDL call-caching and CWLProv** were not surveyed.
- **The explicit/implicit failure taxonomy** in §7 came from a blended search summary; likely origin
  arXiv:2605.04375, attribution unconfirmed. The distinction is useful; the citation is not yet safe.
