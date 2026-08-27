---
id: DOC-METHOD-WATCH-AUTONOMY-PRIOR-ART
title: Prior art scan — who else is running an autonomous researcher, and what can we take
level: L3
kind: memo
# ⚠ `scan` was declared first and systems_check refused it: the enum is
# [architecture, convention, policy, manuscript, prereg, memo, register, runbook, generated,
# historical, index, incident] and inventing a twelfth kind for one document is how a schema
# stops meaning anything. `memo` is what this is — a dated report that owns no mechanism and
# changes no status, which is exactly what `scope` below already says about it.
status: live
canonical_for: [autonomy loop prior art, external autoresearch ecosystem, agent-accepting venues survey]
purpose: >
  Answer trimcrae's question — "there's no way we're the only people in the world trying to use a
  Claude Max subscription to be an auto researcher" — with checked sources, and say for each finding
  what it would REPLACE in this repository and what adopting it would cost.
scope: >
  A dated field scan. It owns NO mechanism and changes NO status. It does not restate the autonomy
  architecture (that is `program/emc-autonomy-architecture.md`), the aiXiv mechanics (`aixiv-submission`),
  the hardening cycle (`paper-hardening`) or any cost figure (pricing.md).
audience: [maintainers, autonomous research agents]
date: 2026-08-27
last_verified: 2026-08-27
related: [DOC-EMC-AUTONOMY-ARCHITECTURE, DOC-METHOD-WATCH, DOC-NR4A3-PROGRAM-MAP]
---

# Prior art — the autonomous-researcher ecosystem, checked

> ⛔⛔ **TWO OF THIS DOCUMENT'S HEADLINE CONCLUSIONS ARE SUPERSEDED. READ
> [`method-watch-autonomy-prior-art-2.md`](./method-watch-autonomy-prior-art-2.md) FIRST.** A second
> pass on 2026-08-27, five seats wide, was run because trimcrae rejected this one as a survey of the
> field: *"I'm not buying this is real survey of the field if you think that the only people doing
> auto-research are doing it on ML benchmarks."*
>
> **The method is why, and it was not carelessness.** This scan searched GitHub for AI-scientist
> repositories and read their READMEs, which samples *code that turns a topic into a paper*. It
> therefore could not see a loop whose bottleneck is physical, a pre-LLM robot scientist running
> since 2009, the living-evidence world, a commercial platform that publishes nothing about its
> loop, or a venue-level publication gate.
>
> - *"Not solved for our SHAPE"* → **half wrong.** A long-lived loop with a persistent queue,
>   resource governance, stall detection, human authority and provenance is solved in three other
>   domains, two of them running for decades.
> - *"We are ahead on governance"* → **a sampling artifact; the honest verdict is UNAWARE, not
>   ahead.** ⭐ §3 below already hedged this correctly (*"being the only one with a problem is not
>   the same as being ahead"*) — the headline did not.
> - *"We are behind on tooling"* → **unchanged and confirmed.**
>
> Everything else here stands, including the six recommended actions, and the rest of this document
> is retained as written (CLAUDE.md rule 1.2).

**Scan run 2026-08-26, 9:30–10:00 PM ET (2026-08-27 UTC).** Repository metadata (stars, forks, last
push, licence) was read live from the GitHub API through `mcp__github__search_repositories`; READMEs
were read with `WebFetch`; everything else came from `WebSearch` and is marked as such. Several
domains are blocked at this sandbox's egress proxy (`arxiv.org`, `huggingface.co`,
`support.claude.com`, `www.aixiv.co`, `monperrus.net`, `thenewstack.io`) — every claim that depended
on one of those is in the UNKNOWNS list at the bottom rather than stated here.

---

## Headline

**No, we are not alone — and no, this is not a solved problem we should have bought instead of
built.** There is now a large, fast-moving ecosystem of "AI scientist" systems, and as of August 2026
its centre of gravity has moved *off* the 2025-vintage Python frameworks (Sakana's AI-Scientist-v2,
AgentLaboratory, AI-Researcher — all three last pushed between August and December 2025, i.e. **stale
by 8–12 months**) and *onto* markdown-skill packs that run on Claude Code and its clones. That is
exactly the shape of this repository, so the architectural bet was right. **But almost every one of
those systems is pointed at a different problem than ours: they take a topic and produce a paper, on
ML benchmarks, in one sitting.** Not one that I could find runs a *single, long-lived, domain-specific
research program* with a queue, a spend governor, a publication-authority model and an anti-gaming
invariant — the governance half, which is where most of this repo's build effort went. The half we
*have* under-built relative to the field is the plumbing: **this repository has zero MCP servers
configured** (`.mcp.json` does not exist), routes every literature fetch through a GitHub Actions
dispatch, and runs all of its adversarial review seats on one model family. Those three gaps are
where borrowed work pays. The honest summary is: **our loop is ahead on governance, behind on tooling,
and orthogonal on subject matter.**

---

## 1 · Ranked adoptable items

Ranked by what would actually save *this* program work. ⛔ Star counts are not evidence; the
"verified" column says what I could actually check.

| # | What | URL | Verified (2026-08-27) | What it replaces / saves HERE | Cost to adopt | Licence |
|---|---|---|---|---|---|---|
| **1** | **Anti-Autoresearch** — reviewer-side integrity forensics. 61 signals: **46 verdict-bearing hack-patterns in 8 families (A–H)**, 13 zero-weight AI-writing-style impressions, 2 advisory. Architecture is deterministic ledger → LLM auditors propose findings → **deterministic adjudicator writes the verdict, never the model**. | https://github.com/wanshuiyin/Anti-Autoresearch | 142★, MIT, created 2026-06-26, **last push 2026-08-26** (yesterday). README read in full; families and run modes confirmed. | Gives `paper-hardening`'s blind seats a **named catalogue of defect classes** they currently do not have — families A (numeric self-consistency: "Table 2 never exceeds 84.7% but abstract claims 85.3%"), D (experiment integrity: phantom results, code that does not match numbers), E (citation integrity), H (evaluation design: leakage, unvalidated LLM judges). Its deterministic core is pure stdlib Python and is a preflight-gate shape, not a skill shape. | Read + port the pattern catalogue; optionally vendor `tools/build_claim_ledger.py` + `tools/adjudicate_findings.py`. No auth, no money, no uptime dependency. ⚠ It audits *papers*, not *loops* — it does not touch §10.4. | **MIT** |
| **2** | **ARIS (Auto-Research-In-Sleep)** — 81 markdown skills + 54 helper tools for unattended overnight research. Two mechanisms worth taking: a **fail-closed cross-model jury** (no model acquits its own work; Claude Code executes, a different model family reviews) and a **watchdog on empty iterations** (empty round → re-plan; **four empty rounds → escalate to a human**). Retries 429/5xx via `ARIS_STREAM_RETRY`. | https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep | 15,294★, 1,340 forks, MIT, created 2026-03-10, **last push 2026-08-26**, 82 releases v0.4.5→v0.4.24 in ~4 months. README read in full. | The cross-model jury is the one real hole in our review design: **every blind seat in `paper-hardening` runs on the same model family as the author.** The four-empty-rounds rule is a sharper version of `health.py`'s `advancing_live_work` (3 receipts with `route_advanced: none`) applied *within* a cycle rather than across cycles. | Reading is free. The jury is **not** free: it needs a second provider (a Codex/GPT or Gemini seat) — either metered dollars or a second subscription. That is a spend decision, not an adoption. | **MIT** |
| **3** | **pubmed-mcp-server** — PubMed + Europe PMC + PMC/EPMC/Unpaywall full text, citations, MeSH, over MCP (STDIO or Streamable HTTP). | https://github.com/cyanheads/pubmed-mcp-server | 140★, Apache-2.0, created 2025-05-24, **last push 2026-08-21**. Metadata verified; server not run. | Would put literature retrieval **in the session** instead of behind a `fetch-literature.yml` dispatch + a `literature-cache` branch round-trip. This repo has **no MCP servers at all** — the largest single tooling gap found. | An `.mcp.json` + a Node runtime. ⚠ **Blocked on an unknown**: NCBI is blocked at this sandbox's egress proxy, and I have not checked whether MCP server traffic takes the same path. See UNKNOWN 1 — settle that before doing any work here. | **Apache-2.0** |
| **4** | **awesome-autoresearch** — the maintained index of this whole ecosystem. 99 entries when I read it, organised by function (benchmarks, deep-research agents, end-to-end systems, skill libraries, venues). | https://github.com/AI4Scientist/awesome-autoresearch | 152★, no licence file, **last push 2026-08-26**. Full contents read. | Replaces an ad-hoc field scan for autonomy tooling. It is the single highest-yield URL in this document — it is where I found ARIS, Agon, Anti-Autoresearch and AiraXiv. | One `method-watch-triggers.json` row of `trigger_kind: venue`-style shape, pointed at its commit log. Free. ⚠ No licence file, so nothing in it may be vendored on the strength of the list itself. | **none stated** |
| **5** | **scientific-agent-skills (K-Dense)** — 163 validated skills across bioinformatics, drug discovery, clinical research. The largest such library by adoption. | https://github.com/K-Dense-AI/scientific-agent-skills | **34,749★**, MIT, created 2025-10-19, **last push 2026-08-24**. Metadata verified; skills not audited. | Narrow but real value: structure/omics workflow skills and figure generation. ⛔ **Most of it is bench-adjacent and this program has no wet lab**, so the honest take is "mine it for two or three skills", not "adopt the library". | Free to read; MIT so individual skills may be vendored with attribution. Adopting wholesale would bloat the skill surface, which CLAUDE.md §6's tripwire table is already carefully sized. | **MIT** |
| **6** | **AiraXiv** — a second AI-agent-accepting preprint platform, with a **FastMCP MCP server exposing 13 tools** (account, paper submission/revision, review access, community feedback) so an agent submits programmatically. ACL 2026 demo track. | https://airaxiv.com/ · paper: https://aclanthology.org/2026.acl-demo.63/ | Existence and MCP surface from search results + the ACL Anthology listing; **site not fetched** (see UNKNOWN 6). | A second outward channel besides aiXiv. ⛔⛔ **This is NOT an adoption — it is a question for trimcrae.** CLAUDE.md §3 and `publication-authority.json` scope his standing grant to **aiXiv only**, and `granted_against` names "aiXiv only — no other venue, ever". Posting here without asking is the exact inference §3 forbids. | Free to evaluate. Any use requires a fresh, named grant. | unknown |
| **7** | **claudewatch** — AgentOps for Claude Code: error-loop and drift detection, cost-per-commit, session analytics, hooks + MCP tools, SQLite. | https://github.com/blackwell-systems/claudewatch | **9★**, 1 fork, Go, last push 2026-07-12. Metadata verified only. | *Would* cover the "8 consecutive reads with zero writes" class of stall that receipts cannot see. | ⛔ **Listed for completeness, not recommended.** 9 stars and one fork is one author's project; adopting it makes our health board depend on unmaintained third-party code. Read it for the idea, do not take the dependency. | unknown |

### Explicitly rejected, with the reason

- **citecheck** (https://github.com/jhlee0619/citecheck, `npx -y @jhlee0619/citecheck`) — an MCP server that verifies references against PubMed, Crossref, arXiv and Semantic Scholar and repairs the manuscript, with a paper behind it. **Do not adopt: 1 star, 0 forks, and its JOSS submission (openjournals/joss-reviews#10224, submitted 2026-03-17) is labelled `pre-review` and `rejected` with no editor ever assigned.** That is a README with a preprint attached, not a running system. ⭐ **The idea is still worth taking internally**: `lint_citations.py --verify-online` currently checks **Europe PMC only**, and `--report` today says **130 of 213 ledger entries are still `unverified_at_baseline`** against 82 verified. Adding Crossref and OpenAlex to that one function is a few hours of our own code and would let that count fall much faster — that is an internal change, not an adoption.
- **mcp-refchecker** (0★) and **refcheck** (3★) — same category, same verdict, less behind them.
- **Claude-Code-Usage-Monitor** (https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor, 8,657★, MIT) and **claude-code-statusline** (9★) — **do not adopt.** Both *infer* quota from local session JSONL. The autonomy architecture §9.1 already reads `external_metadata.rate_limit_info` (`status`, `rateLimitType`, `resetsAt`, `isUsingOverage`) directly from `get_session` at $0. **Reading beats inferring**; adopting these would be a downgrade.
- **Agon** (https://github.com/AutoResearch-Factory/Agon, 43★, 4 forks, MIT, last push 2026-08-24) — the closest thing found to "a Claude Code plugin that runs a research loop": four tick commands (`/idea-tick`, `/proposal-tick`, `/experiment-tick`, `/deep-lit-tick`), file-based handoffs so "a run is recoverable, auditable, and reusable", launched with `claude --plugin-dir ../Agon --dangerously-skip-permissions`. **Nothing here we do not already have**, and its recoverability story is weaker than ours (files in a workspace vs. state committed to git). Worth one reading, no more.
- **karpathy/autoresearch** (https://github.com/karpathy/autoresearch) — **94,756★ and 13,361 forks, and it is three files.** `prepare.py`, `train.py`, `program.md` — all three live in that external repo, not ours, and are named here only to describe its shape; the agent may edit only `train.py`; each experiment gets a fixed 5-minute training budget; the metric is `val_bpb`; ~12 experiments/hour. There is **no scheduler, no health board, no stall detection, no budget governor** — the loop is kicked off by a human saying "have a look at program.md". ⭐ **This is the clearest single datum in the scan**: the most-starred autonomous-research repository in the world is architecturally trivial next to this one, and its star count measures the author, not the design.

---

## 2 · What the ecosystem has that this repo does NOT

1. **MCP servers, at all.** Verified locally: `.mcp.json` does not exist and `.claude/settings.json` declares hooks only. The ecosystem's scientific pipeline is now largely MCP-shaped — PubMed/Europe PMC (https://github.com/cyanheads/pubmed-mcp-server), arXiv (https://github.com/blazickjp/arxiv-mcp-server, 3,076★, Apache-2.0, pushed 2026-08-26), Zotero (https://github.com/54yyyu/zotero-mcp, 4,797★, updated 2026-08-27), multi-source distillation (https://github.com/Eclipse-Cj/paper-distill-mcp, AGPL-3.0). We do all of this through Actions dispatches.
2. **Cross-model adversarial review.** ARIS's fail-closed invariant — *no model acquits its own work* — has no equivalent here. Our blind seats are blind to the authoring **context**; they are not blind to the authoring **model**.
3. **External benchmarks for research agents.** AIRS-Bench (https://github.com/facebookresearch/airs-bench), MLGym (https://github.com/facebookresearch/MLGym), BixBench (https://github.com/Future-House/BixBench), aviary (https://github.com/Future-House/aviary, 276★, Apache-2.0, pushed 2026-08-26), ScholarEval (https://github.com/skai-research/ScholarEval, 21★, MIT — but last push 2025-10-28, i.e. stale). **This loop has no external calibration of any kind**: `health.py` grades the loop against rules we wrote.

   > **⭐ CORRECTED 2026-08-27 — THE STRONGEST ITEM IN THIS ROW ARRIVED THE DAY AFTER THIS SCAN RAN, AND IT IS THE SUCCESSOR TO THE BixBench LISTED ABOVE.** **BixBench3** (arXiv:2608.25286v1, 26 Aug 2026, Edison Scientific) grades 13 frontier models on 20 research-study-scale computational-biology tasks — raw public data in, 138 programmatically graded artifacts out, 1,794 artifact evaluations — which is a direct external measurement of the operation this loop performs. **The sentence above stays true and is now narrower:** `health.py` still grades this loop against rules we wrote, and this loop is still not *run* on any external benchmark. What changed is that a dated external measurement of the underlying capability now exists, and mapping its ten-tag failure vocabulary onto CLAUDE.md's own dated incidents lands **seven of ten** — the first outside evidence that this repository's incident log is the field's failure surface rather than a local quirk. ⭐ It also carries the one reading that is about the model we run: **Claude Opus 5 placed 7th at 0.406**, rising to **0.455 (second)** once the three tasks it lost on output-format contract violations are excluded from every model — an instruction-following deficit on artifact schemas, not a scientific one. Full grading, the trigger non-fire, and the two items it filed: [method-watch-bixbench3-calibration.md](method-watch-bixbench3-calibration.md).
4. **A published literature-QA system with measured accuracy.** PaperQA2 (https://github.com/Future-House/paper-qa, 9,105★, Apache-2.0, pushed 2026-08-26). We have `fetch-literature.yml` and human reading.
5. **A named vocabulary for gate-gaming.** SpecBench (arXiv 2605.21384, "Measuring Reward Hacking in Long-Horizon Coding Agents"), "Reward Hacking as Equilibrium under Finite Evaluation" (arXiv 2603.28063 — argues that under finite evaluation *any* optimised agent systematically under-invests in quality dimensions its evaluator does not cover, which is a formal statement of exactly what §10.4 guards against), and BadScientist (arXiv 2510.18003, "Can a Research Agent Write Convincing but Unsound Papers that Fool LLM Reviewers?"). ⚠ arXiv is egress-blocked from this sandbox; these identifiers come from search results and **were not resolved** — see UNKNOWN 9.
6. **An end-to-end discovery result with wet-lab confirmation.** FutureHouse's Robin (https://github.com/Future-House/robin, 684★, Apache-2.0) published in *Nature* on 2026-05-19 (https://www.nature.com/articles/s41586-026-10652-y): the system generated every hypothesis, experiment design, analysis and figure, and **humans executed the physical experiments**, arriving at ripasudil as a candidate for dry AMD. That is the strongest "AI scientist produced a real result" datum in the field — **and it is not reachable by us**, because the human hands are the part we do not have.
7. **Automated scientific figure skills** — https://github.com/BAIKEMARK/happy-figure-skill (122★).
8. **A skill-library ecosystem an order of magnitude larger than ours.** 34.7k★ (K-Dense), 12.1k★ (https://github.com/Orchestra-Research/AI-Research-SKILLs, MIT), 1,048★ (https://github.com/wu-yc/LabClaw). We have eight skills.

### What the 2025-generation frameworks actually produced

Asked plainly, because "AI Scientist" is a phrase that carries more than its evidence:

| System | Repo | Live? | What it actually produced |
|---|---|---|---|
| **AI-Scientist-v2** (Sakana) | https://github.com/sakanaai/ai-scientist-v2 | 7,050★ but **last push 2025-12-19 — 8 months stale**; licence NOASSERTION | **One** workshop paper accepted at an ICLR 2025 workshop, scores 6/7/6, out of **three** submitted, then **withdrawn by prior agreement**. Workshop acceptance rate ~32.6%. (Per search results + Sakana's own announcement; the underlying paper is at pub.sakana.ai.) Real, and much narrower than the phrase "AI scientist" suggests. |
| **AgentLaboratory** | https://github.com/SamuelSchmidgall/AgentLaboratory | 5,809★, MIT, **last push 2025-08-20 — 12 months stale** | Demos + a follow-on paper (AgentRxiv). No accepted-paper record found. |
| **AI-Researcher** (HKUDS) | https://github.com/HKUDS/AI-Researcher | 5,701★, **no licence**, **last push 2025-10-16 — 10 months stale** | NeurIPS 2025 paper about the system. Commercialised as novix.science. |
| **Robin** (FutureHouse) | https://github.com/Future-House/robin | 684★, Apache-2.0, pushed 2026-04-21 | ⭐ The real one — *Nature*, 2026-05-19, with wet-lab execution by humans. |
| **RD-Agent** (Microsoft) | https://github.com/microsoft/RD-Agent | 14,342★, MIT, pushed 2026-08-04 | Live and maintained; industrial R&D framing, not paper-producing. |
| 2026 generation | AutoResearchClaw (14,250★, MIT, pushed 2026-08-19), EvoScientist (4,501★), InternAgent (1,415★), scientify (2,098★, **no licence**), Curie (371★) | all pushed within the last month | Demos and leaderboard claims. **I found no accepted-paper record for any of them.** |

⛔ **Read that table as the field's honest scoreboard: one withdrawn workshop paper and one wet-lab
Nature result, against tens of thousands of stars.** Nothing in it argues we should have bought
instead of built.

---

## 3 · What this repo appears to have that the ecosystem does NOT

⚠ Written sceptically, because "we are unique" is the most self-flattering possible conclusion and
the search that produces it is the search that stopped early. Every individual mechanism below exists
somewhere out there. **What I could not find is any of them wired together into a governed, long-lived,
single-program loop.**

- **Receipts as the liveness primitive, with a fired-Routine-is-not-a-delivered-one rule.** The
  dead-man's-switch pattern is standard operations practice and was independently restated in
  everything I read on stall detection: *"Don't wait for a completion signal — verify the output file
  exists and is valid."* ARIS has a watchdog on empty iterations. **What I did not find anywhere is a
  health board whose every condition declares what its red DOES to the loop** (`blocks` / `redirects`
  / `advises`, `health.py`'s `CONDITION_ON_RED`). That distinction was added here on 2026-08-27 after
  an any-red rule killed the loop with two permanently-red retrospective conditions — a failure mode
  nobody else appears to have hit yet, because nobody else's loop has run long enough to accumulate
  immutable history conditions.
- **The anti-gaming invariant — "a bar may not be changed by the cycle that bar just blocked" — as a
  mechanical check reading a receipt and a diff together.** The *literature* on this is now large
  (SpecBench, the finite-evaluation equilibrium result). Anti-Autoresearch has the closest engineering
  answer: the adjudicator is deterministic and *never* the model. But that constrains what the auditor
  may conclude, not what the audited agent may edit. **I found no other implementation of a
  temporal restriction on an agent's own goalposts.**
- **An append-only amendment log with an answered `self_serving_check` field.** Several systems log
  changes. None I found requires the agent to answer *"did this change make my own work easier?"* as a
  gating field, with an unanswered field as a red health condition.
- **A citation-provenance *ledger that counts down* rather than a pass/fail checker.** Every citation
  tool found (citecheck, refcheck, mcp-refchecker, Anti-Autoresearch family E) answers "is this
  reference real". `lint_citations.py` answers a different and, for an unattended agent, more useful
  question — *did this identifier get here by a retrieval or by a model typing it* — and enumerates
  the ones nobody has checked (130 today) so the number can fall honestly. I found nothing else with
  this shape.
- **A bar-scoped publication authority recorded with the backdrop it was granted against**
  (`publication-authority.json`'s `granted_against`, and the rule that if any of the three backdrop
  facts changes the grant must be re-asked). The ecosystem's approach to publication authority is
  either "a human clicks submit" or "the agent posts to aiXiv". No middle layer found.
- **A program that is not about ML.** Every end-to-end system in the catalogue optimises an ML metric
  or writes an ML paper. Their evaluation environments are ML training runs. **A sustained, no-wet-lab,
  ultra-rare-disease in-silico program with a route portfolio and a patient-path objective function is
  not a thing the ecosystem is doing** — which also means none of its benchmarks would grade us.

⛔ **The one thing this section must not be read as saying** is that our governance is *better*. It
is *unusual*, and it is unusual largely because our loop has to survive months on one subscription
with one human, which is a constraint nobody publishing in this space has. Being the only one with a
problem is not the same as being ahead.

---

## 4 · Answering the question as asked

> *"there's no way we're the only people in the world trying to use a Claude Max subscription to be an
> auto researcher."*

**Correct — a great many people are, and one repository proves it at scale**: ARIS ships 81 markdown
skills specifically so that "Claude Code does research while you sleep", has 15.3k stars and 1.3k
forks, and shipped 82 releases in four months. The subscription-backed unattended agent is a
mainstream 2026 pattern, not an exotic one.

**Two things about that pattern that bear directly on this program, and both are risks rather than
opportunities:**

1. **The subscription's terms for programmatic use have been moved once already and could move again.**
   Per search results (primary source egress-blocked — UNKNOWN 2): Anthropic announced on 2026-05-14
   that from 2026-06-15 the Agent SDK, `claude -p`, Claude Code GitHub Actions and third-party
   Agent-SDK apps would move off subscription rate limits onto a separate ~$200/month credit metered
   at API list prices; on 2026-06-15 that change was **cancelled**, and programmatic usage continues to
   draw from Pro/Max limits. Separately, Anthropic is reported to have cut Pro/Max subscription access
   for one third-party agent CLI ("Openclaw") on 2026-04-04. ⛔ **`autonomy-architecture` §9's whole
   budget model assumes the flat-rate subscription. That assumption has a date on it and should be a
   `method-watch` trigger row, not a background belief.**
2. **The venue question is moving too.** arXiv tightened CS submissions in October 2025 (no reviews or
   position papers without prior peer review) and then rolled out an endorsement requirement site-wide;
   the OSF generalist preprint service stopped accepting submissions in August 2025 over quality. ICMJE's
   January 2026 Recommendations added a dedicated **Section V** on AI, requiring disclosure in **both**
   the cover letter and the manuscript, author verification of all AI-generated content, and full author
   responsibility — and, unchanged, **AI may not be an author**. Nature Portfolio and Science/AAAS
   require the same disclosure. **None of that blocks this program**: trimcrae is the human author,
   which is precisely the shape the policies were written for. It does mean the disclosure text is a
   deliverable the submission checklist must own.

---

## 5 · UNKNOWNS — and the single observation that settles each

| # | Unknown | The observation that settles it | Cost |
|---|---|---|---|
| 1 | **Does MCP server traffic from this sandbox go through the same egress proxy that blocks NCBI, arXiv and Europe PMC?** Recommendation 3 is worthless if it does. | Add one trivial MCP server to `.mcp.json`, restart, call one tool that hits an external host. | $0, minutes |
| 2 | **The current, primary-source rule for programmatic usage against a Max subscription.** `support.claude.com` is blocked here; the "cancelled on 2026-06-15" reading is from secondary coverage only. | Fetch `support.claude.com/en/articles/11145838-...` from an Actions runner (`ci-escape-hatches` rung 1), or trimcrae opens the page. | $0 |
| 3 | **Which host aiXiv actually lives on and whether it is the same project as the aiXiv paper.** `www.aixiv.co` is blocked here; `aixiv-submission` targets a different hostname. | One Actions fetch of both hosts, compared. ⚠ Do this before quoting anything about aiXiv from *this* file — `aixiv-submission` is canonical for aiXiv, not this document. | $0 |
| 4 | **Whether ARIS's watchdog and cross-model jury actually work.** 15.3k stars and 82 releases are evidence of activity, not of function. I read the README, not the code. | `git clone` it and read `tools/`; or run one throwaway overnight loop and read what the watchdog wrote. | $0 (clone) |
| 5 | **Whether Anti-Autoresearch's deterministic core really runs offline with no dependencies**, as its README claims — that claim is the whole reason it could live in preflight. | Clone it, run `python3 tools/build_claim_ledger.py` + `tools/adjudicate_findings.py` against a committed manuscript, in CI. | $0 |
| 6 | **Whether AiraXiv is live and accepting submissions, and what its MCP server actually exposes.** | Fetch `airaxiv.com` from a runner; read the ACL demo paper. ⛔ Do not submit anything — no grant exists (§1 row 6). | $0 |
| 7 | **karpathy/autoresearch's licence.** README says MIT; GitHub's licence field is unset in the API response. | Read `LICENSE` in the repo. Only matters if we vendor from it, which we should not. | $0 |
| 8 | **Whether anyone is running an unattended, subscription-backed, *disease-specific* research loop.** I searched for it several ways and found none. **Absence of a search result is not absence of the thing** — CLAUDE.md §4. | No cheap observation settles this. Re-grade on a schedule via the `awesome-autoresearch` commit log (§1 row 4). | $0/scan |
| 9 | **The arXiv identifiers cited in §2 item 5 and the hallucinated-citation audit numbers** (reported as 17,842 ACL/NAACL/EMNLP papers screened, 295 with hallucinated references, rising 0.28% → 2.59% between 2024 and 2025). All from search-result snippets; `arxiv.org` is egress-blocked so **none was resolved**. | Resolve each from an Actions runner before any of these numbers or identifiers is quoted in a manuscript. ⛔ Until then they are search snippets, not citations. | $0 |
| 10 | **What "OpenClaw" is, exactly.** It appears as the target of dozens of ecosystem skill packs and as the subject of the 2026-04-04 subscription cutoff, but I did not verify it directly. | One fetch of its repository. Low value unless we consider a second-model jury seat (§1 row 2). | $0 |

---

## 6 · Recommended next actions (all $0, none taken here)

This document changes nothing. In priority order, the actions it implies:

1. **Settle UNKNOWN 1** — it gates the single largest tooling gap.
2. **Read Anti-Autoresearch's 46 hack-patterns** and port the ones that bind on a no-wet-lab in-silico
   paper into `paper-hardening`'s seat prompts. Free, and the highest-value item found.
3. **Add a `method-watch` trigger row for the subscription's programmatic-usage terms** (UNKNOWN 2 /
   §4 item 1). A silent change to that term breaks §9's budget governor.
4. **Add a `method-watch` trigger row pointed at `awesome-autoresearch`'s commit log** — it is the
   ecosystem's own index and it moved yesterday.
5. **Extend `lint_citations.py --verify-online` beyond Europe PMC** to Crossref and OpenAlex, to work
   the 130 `unverified_at_baseline` entries down. Our own code, not an adoption.
6. **Put the AiraXiv question to trimcrae** if and when a second venue is ever wanted. Not before.

---

## Addendum, 2026-08-27 — one UNKNOWN narrowed, and one connector actually found

⭐ **The report's blocking unknown was "whether MCP traffic uses the same egress proxy that blocks
NCBI here", with the note that recommendation 3 is worthless if it does. Measured, both halves, the
same minute:**

| path | call | result |
|---|---|---|
| sandbox shell | `curl https://eutils.ncbi.nlm.nih.gov/...` | **HTTP 000, curl exit 56** — the CONNECT block |
| harness-side tool | `WebSearch "PMC12376927 extraskeletal myxoid chondrosarcoma"` | **returned the paper**, from `pmc.ncbi.nlm.nih.gov` |

So the asymmetry is real and measured: **a harness-side tool reaches NCBI content that this
container cannot.** ⚠ **That is evidence, not proof, for MCP specifically** — `WebSearch` and a remote
MCP server are both harness-side but they are not the same transport, and the honest reading is that
the block lives in the container's egress, which an MCP server does not traverse. **The observation
that would settle it is unchanged and still costs one connector: enable an authless MCP server and
call one tool.**

⭐ **AND THE CONNECTOR ALREADY EXISTS IN THE USER'S OWN REGISTRY, WHICH THE SCAN DID NOT COVER
BECAUSE IT WAS POINTED AT GITHUB.** Searching the connector registry and the plugin catalogue from
inside the session found:

- **PubMed** (`directoryUuid 81cc5080-…`) — **`isAuthless: true`**, tools `search_articles`,
  `get_article_metadata`, `find_related_articles`, `lookup_article_by_citation`,
  `convert_article_ids`, `get_full_text_article`, `get_copyright_status`. Not installed.
- **bio-research** (`plugin_01DZdK2sP1iWnY1hRYRcFc9W`, marketplace `knowledge-work-plugins`) — bundles
  MCP servers for `pubmed`, `biorxiv`, `c-trials`, `chembl`, `consensus`, `ot` (Open Targets),
  `synapse`, `wiley`, `benchling`, `biorender`, plus a `scientific-problem-selection` skill.
  Not enabled.
- Also present, not installed: **bioRxiv** (authless), **alphaXiv**, **Consensus**, **Firecrawl**,
  **Tavily**.

⛔ **THIS CHANGES THE PRIORITY ORDER OF RECOMMENDATION 3.** The scan proposed vendoring a third-party
`pubmed-mcp-server` from GitHub (140★, Apache-2.0, one maintainer). A first-party authless connector
in the user's own registry is strictly better on every axis that matters here — no vendoring, no
maintenance, no dependency on one author's uptime — and the GitHub option becomes the fallback if the
connector proves unusable.

★ **WHY THIS IS THE HIGHEST-VALUE ITEM IN THE WHOLE SCAN, AND IT IS NOT THE FETCHING.**
`lint_citations` can only check that an identifier is ANCHORED in a tracked artifact, and its own
header says so in those words: *"an ANCHORED identifier is not thereby verified either… This gate
raises the floor; it is not a truth oracle."* On 2026-08-26 that gap cost this repository a
medical-integrity defect that survived two cycles — a national-registry cohort and two single-patient
case reports cited as "the review literature", every identifier real, every one anchored, the gate
green throughout. `get_article_metadata` and `convert_article_ids` resolve an identifier to its
actual title, authors and type, which is the one thing that would have caught it.

⛔ **BLOCKED ON trimcrae:** connectors enable at the account level. Recommended order — **PubMed
first** (authless, closes the provenance gap, settles the transport unknown in the same act), then
the **bio-research** bundle if `c-trials`, `chembl` and Open Targets earn their place.

⚠ **AND THE PROCESS FINDING IS WORTH MORE THAN THE CONNECTOR.** This repository built
`fetch-literature.yml`, a `literature-cache` branch and a whole CI escape-hatch discipline around an
egress block, over two days, without once searching the connector registry that was available from
inside every session. The scan above was pointed at GitHub because that is where the question was
aimed; the answer was one tool call away in the harness. **`method-watch` gains a standing row: check
the connector registry and plugin catalogue before building infrastructure to work around a
limitation.**

---

## Addendum 2, 2026-08-27 — the connector is live, and the unknown is CLOSED

trimcrae enabled the PubMed connector. Both open questions settled in two calls.

**1. TRANSPORT — SETTLED, NOT INFERRED.** `convert_article_ids` resolved four PMCIDs from this
container, in the same session in which `curl https://eutils.ncbi.nlm.nih.gov/...` returns HTTP 000 /
exit 56. **A remote MCP connector does not traverse the container's egress proxy.** The addendum
above called this "evidence, not proof"; it is now proof, and the observation cost one tool call.

⛔ **WHAT THAT MEANS FOR `ci-escape-hatches`.** That skill's opening line is *"the moment you are
about to write 'I can't run X here' … a 403 at the egress proxy (NCBI, GEO, PMC, EuropePMC, UniProt,
Springer all block CONNECT)"* — and its answer is always **dispatch a GitHub Actions run**. For
PubMed-reachable content that answer is now second-best: a connector is synchronous, needs no
workflow, no cache branch and no commit. **The skill needs a rung 0.5 between WebSearch and CI.**
⚠ It does NOT retire the CI hatch: Actions still owns everything the connector cannot reach
(EuropePMC full text, ClinicalTrials.gov v2, publisher PDFs behind an anti-bot edge) and everything
that must run on a schedule without a session.

**2. THE PROVENANCE GAP HAS A ONE-FIELD ANSWER.** `get_article_metadata` returns `article_types`.
Measured on the four identifiers of the 2026-08-26 medical-integrity defect:

| PMCID | PMID | `article_types` | what the prose called it |
|---|---|---|---|
| PMC7563993 | 32967265 | `Journal Article`, **`Review`** | review literature ✅ |
| PMC12398172 | 40885991 | `Journal Article` (registry cohort, n=171) | review literature ⛔ |
| PMC12376927 | 40831041 | `Journal Article`, **`Case Reports`** | review literature ⛔ |
| PMC9131214 | 35665108 | **`Case Reports`**, `Journal Article` | review literature ⛔ |

**Exactly one of four is a Review.** A gate comparing a prose type-claim against `article_types`
fails that instantly. Filed as **AUT-PROP-007**.

⛔ **THE GATE MUST CACHE, NOT CALL.** `preflight.sh` is offline and deterministic by design; making a
linter depend on a live connector would put a commit gate at the mercy of somebody's uptime. The
connector is the FETCHER; a tracked artifact is what the gate reads.

⚠ **AND THE TOOL'S TERMS TRAVEL WITH THE DATA.** The PubMed tool requires attribution and a DOI link
wherever its metadata is used. Any cache artifact must carry that, and so must anything rendered from
it. Recorded here so the guard is built with it rather than retrofitted.

★ **THE STANDING ROW THIS EARNS, and it is the generalisable half:** *before building infrastructure
to work around a limitation, search the connector registry.* Two days of CI escape-hatch work was
spent on a block that a first-party authless connector steps around, and the search that found it
took one tool call from inside the same session that was building the workaround.
