---
id: DOC-ROUTINE-FIELD-SCAN-PROMPT
title: Archived prompt — weekly NR4A3 field-scan Routine
level: L4
kind: memo
status: live
canonical_for: [field-scan Routine prompt]
purpose: The verbatim prompt of the weekly field-scan Routine, archived so recreating the Routine does not depend on reading a config that recreation destroys.
scope: The prompt text only. What the Routine is FOR, and why it has never delivered, live in research/method-watch.md — not restated here.
audience: [maintainers, autonomous research agents]
date: 2026-08-24
last_verified: 2026-08-24
---
# Archived prompt — weekly NR4A3 field-scan Routine

**Why this file exists.** The field-scan Routine (`trig_01X5xHy1cmkLjkATEijZSNJf`, Fridays 8:00 AM ET) has
fired every week since 2026-07-13 and delivered nothing: it was agent-created, so it carries no repo source,
and its own STEP 0 `git checkout main` has nothing to check out. The fix is to **recreate it from the
claude.ai Routines UI with `trimcrae/Rare-cancers` attached as a source** — and recreating means deleting,
at which point the prompt, which lived only in the Routine's stored config, would be gone.

**That exact loss already happened once**, to the retired daily summary-writer, and
[`../modalities/daily-email-system.md`](../modalities/daily-email-system.md) now tells the reader to dig its
parameters out of git history. Archiving it here ends that.

⚠ **Copied verbatim from the Routine's stored config** (`list_triggers` →
`job_config.ccr.events[0].data.message.content`, read 2026-08-24). It is reproduced as it stands, including
anything in it that is now stale — **this is an ARCHIVE, not a corrected version.** Two things in it are
known to be out of date as of 2026-08-24 and should be fixed when recreating, not silently carried over:

- **Section 5(b), the Fable restriction.** The premise has changed: Opus 5 (2026-07-24) measures at or above
  Fable 5, carries no equivalent biology restriction, and is the tier these sessions already run on. The
  mechanism was also a *fallback*, not a refusal. Evidence:
  [`../operating-environment-backfill-2026-08.md`](../operating-environment-backfill-2026-08.md).
- **Section 5(c), Codex phone control.** Answered YES, and it predates the row's own baseline.

**Recreate it in the UI, not with `create_trigger`.** An agent-created Routine does not get the
`mcp__github__*` grant, which is the whole defect being fixed. See `research/method-watch.md`.

---

## The prompt, verbatim

```text
WEEKLY FIELD-SCAN + AUTO-CAPTURE — automated newsletter AND strategy-doc updater for the NR4A3 program. Fresh scheduled session, no prior context; everything you need is below + in the repo trimcrae/rare-cancers.

CONTEXT: entirely in-silico research program (NO wet lab) to design an NR4A3-SELECTIVE targeted degrader for extraskeletal myxoid chondrosarcoma (EMC / EWSR1::NR4A3 fusion). Degrader pipeline: warhead (binary RBFE via OpenFE) -> ternary GENERATION (Boltz/AF3-type co-fold + DeepTernary) -> ternary SELECTIVITY RANKING (physics ensemble ΔG_coop, validated against the NR-V04 retrospective positive control) -> synthesis-ready degrader matrix. Selectivity is expected at the TERNARY layer, not the warhead. The program is MULTI-ROUTE: also fusion-junction ASO (gate = delivery), fusion-neoantigen immunotherapy, and other fusion-selective modalities. Read these BEFORE searching so you know what is already tracked and can report the DELTA: research/method-watch.md, research/IDEAS.md (the route/idea board), research/field-scan-log.md (prior weekly entries), research/compute/cheap-gpu-plan.md (the compute-provider plan).

STEP 0 — WORK ON main + READ PRIOR STATE (do this first):
  git fetch origin main && git checkout main && git reset --hard origin/main
  Then READ research/field-scan-log.md (most recent dated entry = last week's baseline), research/IDEAS.md, research/method-watch.md, research/compute/cheap-gpu-plan.md. Your job is to report and capture what is NEW since the last entry (the DELTA), not restate what is already logged/tracked.

STEP 1 — SCAN (web-search tool; use today's REAL date; roughly the past week). Cover, in priority order:
  1) METHOD-WATCH TRIGGERS (top): any new/updated method we could run or that changes the plan — cofolding/structure predictors, ternary/PROTAC/molecular-glue tools, binding-affinity/FEP/ML-potential tools, paralogue-selectivity methods; or a closed model gaining ternary/cooperativity capability. NOTE: a closed model that is API-ACCESSIBLE is NOT ruled out — if it is useful, recommend using their API rather than self-hosting, and say why.
  2) NR4A / EMC: NR4A1/2/3, NR4A, EWSR1-NR4A3, extraskeletal myxoid chondrosarcoma (biology, structure, ligands, degraders, selectivity).
  3) Degrader methodology broadly: PROTAC / molecular glue, cooperativity, ternary prediction, E3-ligase ligands, degrader ML.
  4) NON-DEGRADER / other routes (IMPORTANT — do not skip): ASO / oligonucleotide DELIVERY advances (the fusion-junction ASO route's gate); IMMUNOTHERAPY / fusion-neoantigen / TCR-T / cell therapy relevant to fusion-driven sarcomas; and ANY new general solid-tumor modality we may not have considered (e.g. transcriptional chemical-induced proximity / bivalent fusion-TF rewiring, RNA therapeutics, condensate/PPI approaches). For each, note whether it could apply to EMC / EWSR1::NR4A3.
  5) TOOLING & OPERATING-ENVIRONMENT WATCH (infrastructure that affects HOW we work, not the science — always include this section, even if the only honest answer is "no change this week"):
     a) OUR SOFTWARE-LIBRARY / DEPENDENCY UPDATES — check for new releases or changelogs of the in-silico stack this program actually runs: OpenFE (docs.openfree.energy / GitHub OpenFreeEnergy/openfe releases + CHANGELOG), OpenMM, openmmtools, gufe, the OpenFF toolkit + openff-nagl, LOMAP2 / Kartograf, RDKit, and any FEP/MD/co-fold engine we depend on (Boltz too). Report version bumps that: change DEFAULTS that affect our numbers (e.g. OpenFE v1.7.0 raised the RBFE time_per_iteration default from 1.0 -> 2.5 ps, ~2x speedup, maintainer-validated as accuracy-neutral), add a feature we could adopt, fix a bug that could affect our results, or change accuracy/performance/cost. One line per notable release + a link to the release notes / changelog. If nothing shipped, say "no relevant library releases this week." Plan-relevant library changes should ALSO be auto-captured to method-watch.md in STEP 2.
     b) FABLE (AND ANY MORE-CAPABLE FUTURE MODEL) BIO/CANCER-RESEARCH RESTRICTION — the model Fable (claude-fable-5) currently REFUSES / is restricted from cancer-research and biology problems, which blocks us from using it for this NR4A3/EMC in-silico program. WATCH SPECIFICALLY for any change that RELAXES or lifts that restriction so Fable can be used for cancer/bio research — AND apply the same watch to ANY FUTURE FRONTIER MODEL at least as capable as Fable (i.e. the most powerful available Claude/Anthropic tier and its successors): do they permit cancer/bio-research use for a legitimate in-silico academic program like ours? Check Anthropic's usage policy, model cards / system cards, release notes, and safety/RSP announcements; a hands-on note ("Fable still declines cancer-research prompts as of <date>" / "now permitted") is also valid evidence. Report the CURRENT state (still restricted vs relaxed) for Fable and for the top-tier model, with a primary link. WHY IT MATTERS: the moment a top-tier model is cleared for our bio work, we want to switch to it — it is the single biggest available capability upgrade for this program. If materially changed, capture it as a flagged "⚠ operating-environment change — for human review" line per STEP 2.
     c) OPENAI CODEX MOBILE / PHONE CONTROL — check whether OpenAI Codex has gained the ability to be run and driven from a PHONE WITHOUT a Remote Desktop (i.e. a native mobile app or mobile web control surface that lets you kick off / steer agentic coding runs remotely, the way Claude Code can be operated from the Claude mobile app). Note the current state + link to the announcement/docs. This matters because trimcrae wants a phone-drivable coding agent as an operational option. If no change, say so.
     d) COMPUTE-COST / GPU-MARKET WATCH — the program's ONLY real cost is GPU/compute DOLLARS (a Claude Max flat-rate covers all engineering time), so cheaper compute directly buys more and bigger runs (bigger fleets, more replicates, the ternary fan-out). Check for: (i) PRICE DROPS on GPU providers we use or could use — AWS EC2/SageMaker spot + on-demand, Modal, Salad, Vast.ai, RunPod, Lambda Labs, Together, Crusoe, CoreWeave, etc. — especially the instance types we run (A10G / g5, A100, H100, L40S), spot and on-demand; (ii) NEW GPU cloud providers, or new free-credit / academic-allocation offers relevant to MD/FEP (e.g. ACCESS, NAIRR, cloud research credits); (iii) NEW GPUs with better FLOPS/$ or better $/ns-of-MD for our OpenMM/OpenFE workloads (new NVIDIA/AMD datacenter or prosumer cards, or a provider adding them). Frame each item as its impact on OUR cost — cheaper triage/short-sampling tier, or cheaper terminal full-sampling legs. One line per item + a REAL link. If nothing material changed this week, say "no material GPU-cost/provider changes." Plan-relevant provider/price/hardware changes should ALSO be auto-captured to research/compute/cheap-gpu-plan.md in STEP 2 (flagged for human review — provider choice is a trimcrae decision).

RULES: one line per item = what-it-is + why-it-matters-to-us + a REAL working link. Prefer primary sources (journal/preprint/GitHub/official docs/policy page/provider pricing page) over blog reposts. If the week is quiet, SAY SO briefly — do NOT pad, do NOT fabricate; only report real, findable sources, flag anything you could not verify, never invent papers/results/releases/prices (repo medical-integrity rule).

STEP 2 — AUTO-CAPTURE INTO THE STRATEGY DOCS (this is why the run exists — capture advances so the plan stays current without manual work). For every genuinely NEW, plan-relevant item that is not already tracked:
  - research/method-watch.md: APPEND the item (dated, sourced) under the existing section headed "## 🔄 Auto-captured (weekly field-scan)" (create it at the end of the file if it does not exist). New methods/tools/triggers go here — INCLUDING plan-relevant software-library updates from STEP 1.5(a).
  - research/IDEAS.md: for a new candidate ROUTE/modality or a material advance to an existing route, APPEND a dated, sourced bullet under the existing section headed "## 🔄 Auto-captured field-scan advances (review + integrate into the board above)" (create it at the end if absent).
  - research/compute/cheap-gpu-plan.md: for a material COMPUTE-COST / provider / GPU-hardware change from STEP 1.5(d), APPEND a dated, sourced, 1-2 line bullet under the existing section headed "## 🔄 Auto-captured field-scan compute-cost updates (review + integrate above)" (create it at the END of the file if absent), flagged "⚠ for human review" since provider choice is a trimcrae decision.
  - Operating-environment items from 1.5(b)/(c) (Fable/top-model bio-restriction, Codex mobile) do NOT need a strategy-doc capture — report them in the newsletter only, UNLESS one materially changes what we are allowed/able to do (e.g. Fable or the top model CLEARED for cancer/bio research), in which case capture it as a flagged "⚠ operating-environment change — for human review" line in method-watch.md.
  SAFETY (critical — this commits to main): ONLY APPEND to those dedicated sections. NEVER rewrite, reorder, or delete curated prose elsewhere in these files, and NEVER change a strategic DECISION or route ranking yourself — if an item suggests a decision change, capture it as a flagged item ("⚠ may warrant re-ranking X — for human review") in the auto-captured section. De-duplicate: if the item is already in the doc (curated or previously auto-captured), skip it. Keep each capture to 1-2 lines + link. Append-only keeps the change safe + low-conflict.

STEP 3 — COMMIT DIRECTLY TO main: append the dated newsletter to research/field-scan-log.md, then commit + push to main, rebasing if main moved:
  git add -A && git commit -m "weekly field-scan <YYYY-MM-DD>: newsletter + auto-captured advances"
  for i in 1 2 3; do git pull --rebase origin main && git push origin main && break; echo "retry $i"; sleep 5; done
  Run `node scripts/validate.mjs` before committing; it must pass. If validate fails or ANY git step ultimately fails, DO NOT abort silently — continue to STEP 4 and include a "⚠ commit/push to main failed: <error>" line at the very end of the newsletter so the failure is visible. (You ARE authorized to push to main for this weekly capture — that is the whole point of this Routine.)

STEP 4 — EMAIL (the deliverable): YOUR FINAL MESSAGE MUST BE THE NEWSLETTER ITSELF (it is emailed to the owner verbatim). Make it self-contained, tight, scannable, DELTA-focused. Open with a 1-2 sentence "This week's takeaway." Include a short "Tooling & operating-environment" section covering the STEP 1.5 items (library updates / Fable + top-model bio-restriction status / Codex mobile / compute-cost + GPU-market) even if the entry is "no change." End with a short "Captured to main this week:" list naming exactly which items you appended to method-watch.md / IDEAS.md / cheap-gpu-plan.md (or "nothing new to capture"). Do NOT end on a tool call or a status line — the last thing you output is the newsletter.
```
