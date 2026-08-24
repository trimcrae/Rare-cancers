---
id: DOC-OPERATING-ENV-BACKFILL-2026-08
title: Operating-environment backfill, 2026-06-15 → 2026-08-24
level: —
kind: memo
status: live
canonical_for: []
purpose: >-
  Answers the three operating-environment questions the weekly field-scan Routine was scoped to watch
  and did not deliver between 2026-06-15 and 2026-08-24 — the frontier-tier bio/cancer-research
  restriction, new frontier models, and phone-drivable coding agents — from live readings taken on
  2026-08-24.
scope: >-
  Covers ONLY the operating-environment half of the field-scan watch (Fable/frontier-model
  restrictions, new frontier models, Codex mobile control). It deliberately does NOT cover the
  science half of that watch — NR4A/EMC literature, degrader methodology, non-degrader routes, the
  software-library releases or the GPU-market watch — none of which was read for this backfill.
audience: [maintainers, autonomous research agents]
date: 2026-08-24
last_verified: 2026-08-24
related: [DOC-METHOD-WATCH, DOC-FIELD-SCAN-LOG]
---
# Operating-environment backfill, 2026-06-15 → 2026-08-24

> **What this is.** The weekly field-scan Routine carries a **tooling & operating-environment watch**
> ([`field-scan-log.md`](field-scan-log.md), scope added 2026-07-14/15). It has delivered nothing since
> its **2026-07-13** baseline entry, and the named cause is in
> [`method-watch.md`](method-watch.md): the Routine has no repo grant and dies at its own `git checkout`.
> Roughly **ten weeks** of that watch went unread. This file reads the three operating-environment
> questions and nothing else.
>
> **⛔ EVERY LINE BELOW IS A DATED OBSERVATION, NOT A FACT.** Per CLAUDE.md §4, a remembered reading
> about any AI system is stale and biased toward UNDERSTATING what is now possible. Every claim here
> carries the **date it was taken** and a **primary link**, or it says **UNKNOWN**. Re-take these
> readings before letting any of them carry an argument — especially a negative one. All readings in
> this file were taken **2026-08-24** unless a line says otherwise.
>
> **⚠ Retrieval caveat, stated once and applying throughout.** `www.anthropic.com`,
> `support.claude.com`, `developers.openai.com` and `openai.com` are all **blocked at this sandbox's
> egress proxy**, so no page below was fetched directly. Primary-source content reached this file
> through `WebSearch`'s rendering of those pages. The URLs are the real primary sources and the
> content is attributed to them; the **retrieval path was indirect**, which is why no reading below is
> graded higher than **A−**. Anyone with direct network access should re-read the A− rows at their
> source before quoting them outward.

**Evidence grades used below.**

| Grade | Meaning |
|---|---|
| **A−** | The vendor's own announcement, docs or help centre, retrieved indirectly (see the caveat above). The highest grade this sandbox can produce. |
| **B** | Secondary reporting, corroborated by two or more independent outlets, consistent with an A− source. |
| **C** | A single secondary or aggregator source, uncorroborated. Treat as a lead, not evidence. |
| **UNKNOWN** | Not established. An honest unknown costs nothing; a remembered figure costs the route. |

---

## 1 · The frontier-tier bio / cancer-research restriction — **CHANGED, and the question is now the wrong question**

**Short answer.** The restriction **changed on 2026-08-07** — but *not* for the class of work this
program does, which remains restricted. That would be the whole answer, except a second reading
makes it mostly moot: **the capability gap the restriction was costing us has closed independently.**
The repo's framing — *"the bio restriction blocks us from the most capable tier"* — is **no longer
true**, and it stopped being true for a reason unrelated to the restriction.

### 1a · What actually changed (reading taken 2026-08-24)

| Reading | State | Grade | Source |
|---|---|---|---|
| Anthropic retuned Fable 5's biology safeguards on **2026-08-07**, cutting biology-related fallbacks by **~85%** across product surfaces | **CHANGED** | **A−** | [anthropic.com/news/improving-fable-5-s-biology-safeguards](https://www.anthropic.com/news/improving-fable-5-s-biology-safeguards) |
| Total fallbacks fell **~67% on Claude.ai, ~55% on Cowork, ~17% on Claude Code, ~7% on the Claude Platform** | **CHANGED** | **A−** | same |
| Fable 5 **continues to block dual-use professional biology and drug-development queries**; **virology, toxicology and molecular design** still fall back | **UNCHANGED for us** | **A−** | same, corroborated by [thenextweb.com](https://thenextweb.com/news/anthropic-claude-fable-5-biology-safeguards-fallbacks-dual-use) and [unite.ai](https://www.unite.ai/anthropic-retunes-fable-5s-biology-safeguards-cutting-blocked-queries-85/) |
| The restriction is a **fallback, not a refusal**: a blocked Fable 5 request is **re-run on Opus 5** in the same conversation and charged at Opus rates | **CORRECTION to the repo's framing** | **A−** | [support.claude.com — Why Claude switched models …](https://support.claude.com/en/articles/15363606-why-claude-switched-models-in-your-conversation-with-fable-5) |
| Fallback target is **Opus 5** for biology / chemistry / life-sciences, **Opus 4.8** for offensive-cyber | **NEW** | **A−** | same |

**⛔ The 85% is a false-positive fix, not a scope expansion.** The published framing is explicit that
the update *"was designed to reduce false positives in the safety classifier rather than expand
capabilities in restricted areas."* The examples given for what now passes are **everyday health and
educational** questions — reading lab results, understanding symptoms, learning biology. This
program's queries are **molecular design and early-stage drug development against a named oncology
target**, which is the category the announcement names as still restricted. **For this program's
query class the answer is: still restricted, as of 2026-08-24.**

**⚠ And note which surface benefited least.** The API surface (**Claude Platform, ~7%**) and the agent
surface (**Claude Code, ~17%**) saw far smaller total-fallback reductions than the chat surfaces
(~67% / ~55%). This program runs entirely on the agent and API surfaces. Even the part of the
loosening that *is* real is largely not on our surfaces.

### 1b · Why this no longer matters much — **the tier gap closed on 2026-07-24**

The repo records the restriction as blocking *"the most capable tier"*. That premise is now stale.

| Reading | Grade | Source |
|---|---|---|
| **Claude Opus 5 released 2026-07-24**, described by Anthropic as approaching Fable 5's frontier intelligence at a lower price | **A−** | [anthropic.com/news/claude-opus-5](https://www.anthropic.com/news/claude-opus-5) |
| On the Artificial Analysis Intelligence Index, **Opus 5 (max) ≈ 61 vs Fable 5 (max) ≈ 60** — Opus 5 narrowly the most intelligent model on that index, top of its Agentic Index, tied first on Coding | **B** | [artificialanalysis.ai/articles/opus-5](https://artificialanalysis.ai/articles/opus-5) · [artificialanalysis.ai/models/claude-opus-5](https://artificialanalysis.ai/models/claude-opus-5) |
| Opus 5 is the model biology / chemistry / life-sciences fallbacks are **routed TO** — it carries no equivalent biology restriction | **A−** | [support.claude.com help article](https://support.claude.com/en/articles/15363606-why-claude-switched-models-in-your-conversation-with-fable-5) |

**★★ So the honest state is: the most capable model available to us on the one public index this
session could read is the model these sessions already run.** Fable 5 is not a capability tier we are
locked out of; on that index it is **not ahead of Opus 5**, and the only thing the restriction denies
us is a model that measures no better for our work. A route that was being carried as *blocked by a
policy* was in fact **overtaken by a release**.

⚠ **This is one benchmark index, and a benchmark is not our task.** It is a leaderboard reading, not
a measurement of in-silico oncology reasoning, and nobody has measured either model on this
program's actual work. The claim above is *"the published capability argument for Fable no longer
holds"*, **not** *"Opus 5 is better for NR4A3 work"* — that second claim is **UNKNOWN** and would
need its own evaluation.

### 1c · A third reason not to build on Fable — it has been pulled once, without notice

| Reading | Grade | Source |
|---|---|---|
| **2026-06-12**: a US government export-control directive forced Anthropic to **disable Fable 5 and Mythos 5 for all customers**, abruptly. Other Claude models unaffected. | **A−** | [anthropic.com/news/fable-mythos-access](https://www.anthropic.com/news/fable-mythos-access) · [CNBC](https://www.cnbc.com/2026/06/12/anthropic-disables-access-to-fable-5-and-mythos-5-to-comply-with-government-directive.html) |
| **~2026-06-30 / 07-01**: controls lifted, Fable 5 redeployed globally after an ~18-day suspension, with new cyber classifiers and a jailbreak-severity framework | **A−** | [anthropic.com/news/redeploying-fable-5](https://www.anthropic.com/news/redeploying-fable-5) |

An 18-day, zero-notice, whole-model outage inside this very window is an **operating-environment fact
about Fable specifically**, and it is a reason to prefer a model without that history for a long-lived
program — independent of any capability or policy argument.

### 1d · Recommendation (evidence only — **nothing was changed**)

**No model-configuration change is warranted, and none was made.** Per this task's hard constraints,
no Routine model, setting or config was touched. The recommendation is:

1. **Do not pursue Fable 5 access for this program.** The capability case has evaporated (§1b), the
   policy case is unchanged for our query class (§1a), and the availability case is now negative (§1c).
2. **Stop carrying "the bio restriction blocks the top tier" as a live blocker.** It is stale on the
   capability half and imprecise on the mechanism half — it is a *fallback to Opus 5*, not a refusal.
   ⚠ [`method-watch.md`](method-watch.md) and [`field-scan-log.md`](field-scan-log.md) both still
   carry the old framing; **this backfill deliberately did not edit either file** (two sibling agents
   were writing nearby, and the watch-scope files are trimcrae's to re-scope). Correcting them is a
   separate, named change.
3. **Keep a re-grade, not a watch.** Per CLAUDE.md §4 the frontier rises, so "still restricted" is a
   claim with a date on it — **2026-08-24**. Re-read the safeguards page and the Intelligence Index
   on the ordinary watch cadence rather than treating either row as settled.

---

## 2 · New and updated frontier models in the window

The window is **2026-06-15 → 2026-08-24**. Entries dated before 2026-06-15 are included only where
the 2026-07-13 baseline never recorded them.

| Model | ID (where a verified ID exists) | Date | In window | Grade | Source |
|---|---|---|---|---|---|
| **Claude Opus 5** — the material one; see §1b | `claude-opus-5` | **2026-07-24** | ✅ | **A−** | [anthropic.com/news/claude-opus-5](https://www.anthropic.com/news/claude-opus-5) · [AWS](https://aws.amazon.com/blogs/machine-learning/introducing-claude-opus-5-on-aws-anthropics-most-capable-opus-model/) |
| **Claude Fable 5 / Mythos 5** — redeployed after the suspension | `claude-fable-5` · `claude-mythos-5` | available again **~2026-07-01** (original launch 2026-06-09) | ✅ | **A−** | [redeploying-fable-5](https://www.anthropic.com/news/redeploying-fable-5) · [claude-fable-5-mythos-5](https://www.anthropic.com/news/claude-fable-5-mythos-5) |
| **Claude Sonnet 5** | `claude-sonnet-5` | reported **2026-06-30** | ✅ | **C** | aggregator only — [scriptbyai timeline](https://www.scriptbyai.com/anthropic-claude-timeline/); **date not verified against a primary source** |
| **OpenAI GPT-5.6 family** (Sol / Terra / Luna tracks) | UNKNOWN — no verified API id | reported **July 2026**; Luna reported as ChatGPT free default in August | ✅ | **C** | aggregator only — [analyticsvidhya](https://www.analyticsvidhya.com/blog/2026/07/july-2026-ai-models-releases/) · [aireleasetracker](https://aireleasetracker.com/latest); **not verified against openai.com** |
| **Google Gemini 3.6 Flash** | UNKNOWN — no verified API id | reported **2026-07-21**, stable GA | ✅ | **C** | aggregator only — same; **not verified against a Google source** |
| **Moonshot Kimi K3** — open weights, reported 2.8T-param MoE | UNKNOWN | reported July–August 2026 | ✅ | **C** | aggregator only — [local-ai-zone roundup](https://local-ai-zone.github.io/blog/july-2026-ai-model-roundup.html) |
| **"Claude Fable 5.1"** | — | — | — | **UNKNOWN** | Speculation only. As of a **2026-08-03** reading there was **no Anthropic announcement, model card or pricing page**. Do not treat as existing. |

**What changes for this program: exactly one row.** Opus 5 (§1b). The GPT / Gemini / Kimi rows are
**grade C and unverified** — recorded so the next session knows a reading was attempted, **not** as
facts to build on. ⛔ **Do not quote a grade-C model id, date or benchmark number outward from this
file.** None of the three was checked against a vendor source, and per CLAUDE.md §7 an identifier
must never be written from recollection or from an aggregator alone.

> **⚠ One unresolved discrepancy, recorded rather than resolved.** The `claude-api` skill bundled with
> this session carries a model table stamped **"cached: 2026-06-24"** that already lists
> `claude-opus-5`, while the public announcement above is dated **2026-07-24**. One of those two dates
> is wrong and this session could not determine which — the cache stamp is not a published artifact and
> the announcement page could not be fetched directly. **Status: UNKNOWN.** It does not affect any
> conclusion here (the model exists and its capability reading stands either way), but a future session
> should not treat 2026-07-24 as a hard date without re-checking.

---

## 3 · OpenAI Codex — phone control without Remote Desktop

**Short answer: YES, it exists, and it has existed since before this backfill window opened** — which
means the watch item was already stale at its own 2026-07-13 baseline, where it was never answered.

| Reading | State | Grade | Source |
|---|---|---|---|
| Codex runs **natively in the ChatGPT mobile app on iOS and Android**, in preview, across all plans including Free, in all supported regions | **CHANGED — capability exists** | **A−** | [openai.com — Work with Codex from anywhere](https://openai.com/index/work-with-codex-from-anywhere/) |
| Rollout began **~2026-05-15** — i.e. **before** the 2026-06-15 window start | **predates window** | **B** | [9to5Mac, 2026-05-14](https://9to5mac.com/2026/05/14/openai-brings-codex-control-to-chatgpt-for-iphone-and-android/) · [testingcatalog](https://www.testingcatalog.com/openai-brings-codex-to-chatgpt-mobile-app-for-ios-and-android/) |
| From the phone: **approve agent decisions, review diffs, redirect running tasks, monitor terminal output, and start new threads** | — | **A−/B** | [developers.openai.com/codex/changelog](https://developers.openai.com/codex/changelog) + the launch post above |
| The mobile app **loads live state** from a connected machine — active threads, approvals, plugins, project context | — | **A−** | [developers.openai.com/codex/changelog](https://developers.openai.com/codex/changelog) |
| **Codex cloud**: tasks run on OpenAI infrastructure, and **web and mobile surfaces start and view cloud tasks** — no host machine in the loop | — | **A−** | [developers.openai.com/codex/cloud](https://developers.openai.com/codex/cloud) |
| Host-connected mode required the **macOS** Codex desktop app at launch; **Windows support was "coming soon"** | **UNKNOWN today** | **B (at launch)** | [openai.com launch post](https://openai.com/index/work-with-codex-from-anywhere/) — **whether Windows has since shipped was not established** |

**So there are two distinct mechanisms, and neither is Remote Desktop:**

1. **Phone as control surface** over Codex running on your own machine (laptop, devbox, remote env).
   Code and credentials stay on the host; only output and approval requests cross the wire.
2. **Codex cloud** — the task itself runs on OpenAI infrastructure and the phone is a first-class
   surface for starting and watching it. This is the mode that needs **no** machine of ours awake.

**Consequence for trimcrae's operational ask.** A phone-drivable coding agent is available on **both**
vendors, not just via the Claude mobile app. This watch row is **answered**, and should be re-scoped
from *"has Codex gained this?"* to *"which phone-drivable agent do we want, and for what?"* — a
choice, not a wait. ⚠ **This file does not edit [`method-watch.md`](method-watch.md) or
[`field-scan-log.md`](field-scan-log.md) to close the row** (out of scope for this task); the
re-scope is a separate named change.

---

## 4 · Incidental finding — a rare-disease grant window opened and closed inside the gap

Not one of the three questions, but it surfaced while reading Anthropic's policy pages, it is
directly on this repository's subject, and burying it would be the failure mode CLAUDE.md §4 names.

| Reading | Grade | Source |
|---|---|---|
| Anthropic launched **AI for Science rare-disease research grants** on ~**2026-07-21**: up to **$50,000 in Claude API credits** over six months, two tracks (researchers; early-stage rare-disease biotech) | **A−** | [anthropic.com/news/rare-disease-research-grants](https://www.anthropic.com/news/rare-disease-research-grants) |
| Application deadline **2026-08-02** — **passed 22 days before this reading** | **B** | [Science Times](https://www.sciencetimes.com/articles/62187/20260721/anthropic-launches-ai-science-rare-disease-grants-offering-50000-claude-credits.htm) · [Clinical Research News](https://www.clinicalresearchnewsonline.com/news/2026/07/21/anthropic-announces-rare-disease-research-claude-grants) |
| A separate **Claude Science** track offered up to **$30,000** in credits to ~50 teams, **explicitly courting independent scientists**; reported deadline 2026-07-15 — also passed | **C** | aggregator only |
| The **general AI for Science program** is reported to evaluate submissions on the **first Monday of each month** — i.e. possibly rolling and still open | **UNKNOWN** | [support.claude.com — AI for Science](https://support.claude.com/en/articles/11199177-anthropic-s-ai-for-science-program) — the page could not be fetched directly and the cadence is **not confirmed** |

**Why this belongs in this file.** EMC is a rare cancer, this program is run by an unaffiliated
independent researcher, and the eligibility language for these tracks reportedly names independent
scientists — the exact profile the [funding watch](method-watch.md) exists to catch. **A watch that
was not delivering is how a matched, dated funding window passes unread.** That is the cost of the
Routine outage, made concrete.

⛔ **No application was made and none will be without instruction** — an application is an
outward-facing act (CLAUDE.md §3) and is trimcrae's alone. **The actionable, still-open question is
whether the general AI for Science program takes rolling applications from unaffiliated individuals.**
That is currently **UNKNOWN** and is worth one direct read of the help-centre page from a machine
whose egress is not blocked.

---

## 5 · What this backfill did NOT establish

Listed so the next session does not mistake silence for coverage.

- **Whether Opus 5 or Fable 5 is actually better at this program's work.** **UNKNOWN.** §1b rests on
  one public leaderboard, not on any in-silico oncology evaluation. Nobody has run one.
- **A hands-on refusal test.** No live Fable 5 request was issued against a representative NR4A3 /
  degrader-design prompt. §1a's *"still restricted for our class"* rests on the **published policy
  statement**, which is A− evidence about the policy and only indirect evidence about behaviour. A
  dated hands-on observation would be strictly better and costs one API call from an authorised
  surface.
- **GPT-5.6, Gemini 3.6 and Kimi K3 details.** All **grade C**. No model id, price, context window or
  benchmark from those rows is usable.
- **Whether Codex host-connected mode now supports Windows.** **UNKNOWN.**
- **Whether the general AI for Science program is currently open to unaffiliated individuals.**
  **UNKNOWN** (§4).
- **The entire science half of the field-scan watch** — NR4A/EMC literature, degrader methodology,
  non-degrader routes, our software-library releases, and the GPU-market watch — for the same ten
  weeks. **This file covers none of it, and that gap is still open.**

---

## Appendix A · Method

Every reading in this file was taken on **2026-08-24** using `WebSearch` (rung 0). Direct `WebFetch`
of `www.anthropic.com`, `support.claude.com`, `developers.openai.com` and `openai.com` was attempted
first and **refused by the egress proxy** in every case (`EGRESS_BLOCKED`), which is why no row is
graded above **A−**; the refusals are the reason for the grade ceiling, not an inference about the
sources. Nothing in this file was written from recollection: where a live reading could not be
obtained, the row says **UNKNOWN** rather than carrying a remembered value.

**Nothing was changed by this backfill.** No model configuration, Routine, or setting was touched;
[`method-watch.md`](method-watch.md), [`field-scan-log.md`](field-scan-log.md), `research/compute/`
and `research/manuscripts/` were all left unedited. This file is evidence and a recommendation.
