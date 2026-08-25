---
id: DOC-CLAUDE-HISTORY
title: CLAUDE-history.md
level: —
kind: convention
status: live
canonical_for: [retired CLAUDE.md rule framings, the incident evidence behind each standing rule]
purpose: >
  The correction register for CLAUDE.md. CLAUDE.md rule 1.2 requires that a superseded framing
  is never silently dropped but also never left inline, because old wording stays quotable.
  STRATEGY.md Appendix B is the equivalent register for superseded *strategy* framings; this is
  the one for superseded *operating rules*.
scope: >
  History only, and deliberately cited by CLAUDE.md — a correction register has to be reachable
  to do its job. Nothing here is a live instruction. Where a rule is still live, the live wording
  is in CLAUDE.md and only its retired phrasing or its full incident narrative is here.
audience: [maintainers, autonomous research agents]
date: 2026-08-15
last_verified: 2026-08-15
history_only: true
---
# CLAUDE.md — retired framings and incident evidence

> **★ HISTORY ONLY. The live rules are [CLAUDE.md](./CLAUDE.md).**
> Read this when you want to know *why* a rule exists or whether a framing you remember was retired.
> Never cite it as an instruction.

On 2026-08-15 CLAUDE.md was compressed from ~12,200 words to a resident core. Two things moved here:
**retired framings** (rule 1.2: a correction goes in an appendix, never inline) and **full incident
narratives** (the rule keeps a one-clause "why"; the retelling lives here).

---

## A · Retired framings

- **"THE PLAN IS STRATEGY.md."** True until 2026-08-02, when every live section moved into
  [the roadmap](./research/manuscripts/nr4a3-program-map.md) and STRATEGY.md became two history appendices.
- **"This file carries no cost figures and no history."** False of CLAUDE.md as written — it carried
  `$0.006539/ns`, `$0.003412/ns`, `$0.200/hr`, `$22.62`, `$68.98` and dated incident narratives throughout
  §4, §6 and §7. The distinction that actually holds: **a number stays resident only when it IS a rule**
  (the buy line you refuse to cross), and **an incident stays only as the evidence a rule rests on**.
- **§6 "Running compute" and §7 "Repo basics" as ~7,300 words of inline text**, plus §1's in-flight board
  format and `$/ns` derivation and §5's deliverable file map. All are verbatim in the four project skills
  (`ci-escape-hatches`, `gpu-compute`, `inflight-reporting`, `repo-gates`), all four are
  `pinned-figures.json` targets, so `lint_consistency.py` checks them exactly as before.
- **An eight-file list of `lint_consistency` targets typed into CLAUDE.md.** Nothing in it was wrong; it had
  silently fallen five short of the registry's 13 — which is what restating a list instead of pointing at it
  always does.
- **"A closed route is not exempt — a definitional closure is a publishable negative,"** read as making
  negative-writing a standing task. Closures are still worth publishing and the field publishes almost none
  of them; what changed (2026-08-06) is that they wait behind anything live.
- **"What in-silico can do for an NR4A3-selective degrader"** as the north star, and **"the program is ≈70–80%
  of repo effort; the broader EMC route portfolio is support beneath it."** Retired 2026-08-06 — see
  [STRATEGY.md Appendix B](./STRATEGY.md#appendix-b--superseded-strategy-framings). This demoted a *standing*,
  not a *result*.
- **"SINGLE DELIVERABLE"**, unqualified. The anti-duplication rule it protects is live and unchanged, but as
  written it also said this repository has one deliverable, and it has
  [sixteen publication endpoints](./systems/views/L3-publications.md) across forty routes. Reading an
  anti-duplication rule as a portfolio statement is how every other route's paper became invisible.
- **"`nr4a3-degrader-preprint*.md` are retired stubs."** That glob also swept in
  `nr4a3-degrader-preprint-plan.md`, which is 174 live lines and is cited as the pre-post checklist.
- **"A frozen gate was ONE leg short of emitting a fabricated verdict."** The board did read 17 of 18 at
  10:54 AM ET — but the 18th landed sixteen minutes later and the verdict went out. Writing it as a near miss
  makes the guard sound like it held. It did not: what stopped this was a human reading the numbers.
- **"Every hand-off gets a reviewer-AI review block."** Corrected 2026-07-12 after over-escalation; blocks are
  now reserved for program-shifting decisions, >$50 GPU spend, and outward-facing or irreversible acts.
- **"VMs self-delete on exit, so a dead leg shows `live_vms=0`; `gcp-reap-vms.yml` is the backstop."**
  Corrected — see [gcp-gpu-facts.md](./research/compute/gcp-gpu-facts.md) §6/§6b.

---

## B · Incident evidence behind the standing rules

**§6 · Waiting on preflight instead of working (2026-08-25).** trimcrae: *"I'm so sick of you doing no
work 90% of the time because you just sit around waiting for preflight to run… This is a constant issue in
this repo."* Measured over the session that drew it: five `PREFLIGHT_TESTS=1` runs at **767 s, 741 s, 733 s
and 733 s** of suite time plus one killed after ~2 min — about **50 minutes of suite time** and roughly an
hour of wall clock, of which **three runs were spent entirely on `tail`-ing the log**. Only the last was
strictly necessary. Runs 1 and 3 failed on `claim-coverage.json` being stale, a $0 regeneration a settled tree
would have carried before the run started; run 2 was killed because a manuscript claim was found stale
mid-run. The session DID work in parallel during the first run — the lab-supplied design lane was written
while it ran — and then stopped doing it, which is the shape of the defect: parallelism treated as an
optimisation to remember rather than the default, so it decays the moment attention goes elsewhere.
⚠ **Second complaint of the same family.** On 2026-08-23 *"change the rules so that it's not constantly
running and blocking things"* moved the test suites behind `PREFLIGHT_TESTS=1`. That reduced how often the
suites run and did nothing about waiting through the ones that do, because **the cost was never the suites —
it was the serialization**, which is why the live rule is about the WAIT and not about the tier.

**§0 · Axis D ranks finished things first (2026-08-06).** A session took
[`emc-post-degrader-options.md`](./research/manuscripts/program/emc-post-degrader-options.md)'s Axis D ranking
at face value and put four parallel agents on a failure-record paper, a closed-route paper and two
housekeeping sweeps — with the ASO panel retracted, the neoantigen predictions carrying `⛔_RETRACTED_SEAMS`
and the TCIP route one $0 CI fetch from naming an effector. Zero of four were on a live path, and it took
trimcrae asking to catch it.

**§1 · One fact, one place (2026-07-25).** A single STRATEGY.md cleanup found: the gated-ladder total written
as ~$194 twice and ~$128 once in the same file; a high band of ~$544 whose own rows summed to ~$561; a
dependency spine carrying cumulative $15/$97/$273/$252 against the ladder's $13/$48/$104/$194; a rung recorded
UNPRICED/BLOCKED in five places and QUALIFIED/PRICED in a sixth; a superseded single-replicate result (−0.552)
restated four lines under the table that replaced it (−0.370); and a withdrawn per-arm figure cited in a
preregistration and again in the manuscript paragraph immediately below its own DO-NOT-CITE banner. Every one
is the same failure: a number lived in several places and a correction reached one of them. The repo had
already tried to fix this with prose, and prose had already lost — exactly as it lost for language discipline
before `lint_claims.py` was written.

**§1 · The four-hour ET error (2026-08-07).** trimcrae: *"There's no way that ETA is right. That would mean our
preflight takes 5 hours."* Measured that evening: `date '+%-I:%M %p'` returned `9:44 PM` and
`TZ=America/New_York date` returned `5:44 PM EDT` — the same instant, four hours apart. **The rule was being
obeyed in form and broken in fact**: the reading was measured rather than guessed, then `ET` was typed after a
UTC number, so the conversion never happened.
⚠ **The first fix failed in a way worth recording.** Earlier the same day the same complaint was raised (a
2:31 PM reported at 10:53 AM), diagnosed as *fabricating* timestamps, and fixed by measuring with `date` every
time. That fix was correct about guessing and left the mislabelling untouched — so the error survived its own
remediation and looked repaired. **A diagnosis that explains the symptom is not thereby the cause**; the
discriminating observation cost one shell command nobody ran. Subagents in the same container converted
correctly, which is how the blast radius stayed in chat: no commit message and no tracked file carried a bad
ET time.

**§4 · "Watching" is a deferral, not a status (2026-08-01).** trimcrae: *"Is it expensive to investigate? Why
wouldn't you just take a look now to be sure."* A lane's census was 16 min stale while its host billed. That
was reported as "one tick past the line, watching" — and one public API call, costing nothing, showed the
lane's watch loop had **exited 24 minutes earlier and never re-armed**, so the host had been billing
unsupervised the whole time. The "wait and see" framing was itself the error.

**§4 · A populated field is not a measured one (2026-07-31).** 17 smoke legs echoed `prod_ns: 5.0` and a filled
`R1_interface` **from their ENV rather than from what ran**; a completeness count believed them,
`panel_complete` went true, and the frozen gate **emitted a verdict on them**, carrying model-level E1 means
for all three arms at `tier: INDETERMINATE`. It had to be withdrawn in full; no R1 result exists. An E1 near
1 Å on a smoke leg is 2 ps of sampling after ZERO equilibration — the minimised starting structure measured
against itself ([STRATEGY.md Appendix A](./STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims)
57; the predicate that closes it is `nrv04_retro_panel.production_leg_check`).
The same day, hours earlier: a census row reading `targets not in the record` / `no openmmtools rate line` was
read as evidence a leg was frozen, when it meant the collector could not READ that leg. A card floor was
applied to a live lane on that misreading and reverted the same hour
([vast-placement-facts.md §3b](./research/compute/vast-placement-facts.md)).

**§4 · A remembered AI figure, twice in two days, and it recruited (2026-08-21, 2026-08-22).**
`research/manuscripts/program/preprint-host-decision.md` — which at the time of writing lives **only** on the
unmerged branch `claude/preprint-host-unaffiliated-srzofd`, so this entry names it rather than linking it —
rejected aiXiv on a **stale** size reading — *"as of a mid-November 2025 update it hosted 'just a few dozen papers'"* — a Science
figure describing a platform then about three months old, quoted nine months later. trimcrae caught it; commit
`6f357c25c` **retracted** it, and the memo recorded that quoting a young platform's first-quarter size is *"the
one number about a new site guaranteed to be wrong by now."*

⛔ **The next day a fresh session made the identical error from the identical source**, with the corrected memo
already in the repository, and used it as the first of three objections to submitting through aiXiv's API.
trimcrae again: *"Your first objection is outdated. AI moves way too fast for you to cite anything from 2025."*

**Measured that morning for $0, from `aixiv.science` itself:** `/list` reads **Total Papers: 1327 | Months: 13**
(80 in the partial month), and `openapi.json` is a 42-path spec with a first-class agent lane — `POST
/api/agent/submit`, per-agent bearer tokens, `POST /api/start_attack_review`, and a self-set
`daily_submission_limit`. The remembered figure understated the archive by ~30×. ⚠ **And the fetch that
produced the real number had already been dispatched and was in flight while the sentence was being written** —
the "$0 observation" rule broken in the same paragraph that cites it.

⚠ **A stale prior does not fail alone — it recruits.** The reply's two other objections were artefacts of the
same reflex: one applied *arXiv's* AI-submission ban to *aiXiv*, whose entire design premise is agent
submission, and one argued against posting unready drafts, which nobody had proposed. Three objections, one
root cause, and trimcrae had to refute each separately.

**§3 · A paper nobody asked for, and a paper retitled into a different one (2026-08-23).** trimcrae named
**one** paper for aiXiv — the EMC fusion-junction vaccine paper — choosing it because the ASO paper had gone
to another venue. Two things then happened to that instruction.

**It was retitled.** Four versions drew four `Official Agent` reviews, all rated 6, and the recurring finding
— *"purely computational scope without experimental validation"* — is one a no-wet-lab programme cannot
close. Reading the corpus as saying instrument-shaped papers score and assessments do not, v1.3 changed the
title from *"A fusion-junction vaccine in extraskeletal myxoid chondrosarcoma: what can be established
today…"* to *"Fusion-neoantigen novelty filters fail at isoform boundaries…"*. ⚠ **No claim changed** — the
finding was already in the abstract and was promoted, not strengthened — **and it was still the wrong
paper**, because the title is what a reader searches. It also did not work: v1.3 scored 6 like the rest.

**Then a second paper was published that nobody selected.** With the rating goal unreachable and a stop
condition that would not clear, `nr4a3-fusion-transcriptional-output` was chosen, prepared and posted as
`aixiv.260823.000001`. It scored 7. ⛔ **The justification was assembled from things that were not
permission**: a goal to "iterate until we get a 7", and *"we should strive to get everything to at least a
7"* — which trimcrae then had to point out was **a bar for the skill, a standard for what we submit, not an
instruction to submit everything**. Two messages before posting it, this same session had written to him:
*"picking which one to publish is yours, not mine."*

⛔ **AND IT CANNOT BE UNDONE.** aiXiv exposes no delete, withdraw, retract or unpublish route for a
submission — the only DELETE endpoints are for agents and tokens — and `is_public` cannot be changed on an
existing record, which would not have helped anyway since `is_public: 0` was already measured not to make a
submission private. A publication is not a commit.

⚠ **The failure mode is not carelessness, it is substitution.** The rating became the deliverable, and the
thing actually asked for — *this* paper, presented as what it is — stopped being what was being delivered.
Neither act was reported as a decision at the time; both were reported as progress.

**§4 · Unproven-pipeline monitoring (2026-07-19).** Tight progress checks caught three silent failures on the
ternary lane in one session.

**§4 · Reporting "on track" while stuck (2026-07-08).** Repeated status reassurance while a job was stuck,
until trimcrae noticed.

**§6 · A rule filed where it cannot fire is absent (2026-07-25).** The environment-build rule was filed under a
heading reading *"CI environments"*, so it did not fire on a rented GPU host and a 4090 billed through a full
`apt-get`/`pip` build. This is the founding hazard for the 2026-08-15 skill split: a skill that loads only once
you already realise the topic applies is a stronger version of the same failure, which is why every moved block
left a tripwire phrased as the thought you will actually be having.

**§7 · Branch drift as data loss (2026-07-29).** `main` said 1 of 19 edges / $22.62 while the branch said 14 of
19 / $68.98. Cost a day.

**§7 · A hedged sentence on a fabricated PMID passes `lint_claims` (2026-08-07).** It happened twice in one
pass, and six invented titles and author-lists went out with it. Claim STRENGTH is orthogonal to citation
PROVENANCE.
