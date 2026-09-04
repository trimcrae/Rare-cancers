---
id: DOC-METHOD-WATCH
title: Method-watch — in-silico capabilities we are waiting on
level: —
kind: index
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `index` from its location under research/.
audience: [maintainers, autonomous research agents]
date: 2026-08-05
last_verified: 2026-08-06
_backfilled: true
---
# Method-watch — in-silico capabilities we are waiting on

**Purpose.** This program's bottleneck is *methods*, not ideas: several routes unlock the
moment a specific in-silico capability becomes usable. This file is the **watch config +
trigger table** (what to look for, and what to do when it appears).

> **⭐ 2026-08-26 — CORRECTED: LAYER 1 IS LIVE AGAIN, AND THE BLOCK BELOW IS NOW HISTORY.** A $0
> `list_triggers` read shows the field-scan Routine is **`trig_01KJhjjkD57Ke9F37SayypKd`**, created
> **2026-08-24 via the claude.ai UI**, carrying the `sources: [git_repository trimcrae/Rare-cancers]`
> grant the old one lacked — and it delivered: `research/field-scan-log.md` carries a full dated
> entry for 2026-08-24. **The repair trimcrae was asked for happened; this file never learned**, and
> for two days it told every reader that layer 1 was dead. ⚠ **What is still unverified is the
> CADENCE**: that delivery came from the Routine's creation-time fire, and its first *scheduled* fire
> is Friday 2026-08-28. Per the rule this file itself states, confirm it by reading the artifact, not
> the fire record. The block below is retained unchanged as the diagnosis of the OLD Routine
> (`trig_01X5xHy1cmkLjkATEijZSNJf`), because it is the evidence behind
> [the autonomy architecture](manuscripts/program/emc-autonomy-architecture.md) §2.2 — which
> re-tested the same constraint by experiment on 2026-08-26 and found it still holds for any
> agent-created Routine.
>
> **★ 2026-08-24 — LAYER 1'S NON-DELIVERY HAS A NAMED CAUSE NOW, NOT JUST A SYMPTOM.** This file has
> recorded since 2026-08-03 that the field-scan Routine "has never written an entry" without saying why.
> The discriminating observation is in the Routine's own stored config (`list_triggers`, $0): the weekly
> **newsletter** Routine (`trig_01Rjh49ujsZttmDSbTki58tT`, `created_via: http_api` — the claude.ai UI)
> carries a `sources: [git_repository trimcrae/Rare-cancers]` entry in its session context; the
> **field-scan** Routine (`trig_01X5xHy1cmkLjkATEijZSNJf`, `created_via: meta_mcp` — agent-created)
> carries **no `sources` at all**. Its STEP 0 is `git fetch origin main && git checkout main`, which has
> nothing to check out, so the run dies before it scans anything — which is exactly the ⚠ two sections
> below, the one that says an agent-created Routine does not get the repo grant. It has fired every
> Friday and produced nothing since 2026-07-13, and its `last_run` is a firing, not a delivery.
> ⛔ **A FIRED ROUTINE IS NOT A DELIVERED ONE** — read the artifact it was supposed to write, never its
> fire record. **Fix requires trimcrae:** recreate it from the claude.ai Routines UI with the repo
> attached as a source. Nothing in this repository can grant it.
>
> ⚠ This matters for scope as well as liveness: layer 1 is the layer whose prompt ALREADY covers
> immunotherapy, neoantigen and "any new solid-tumor modality". Had it been running, it — not layer 2 —
> would have been the natural home for the 2026-08-19 INTerpath-001 readout. Layer 2 has been carrying
> the newsletter alone for six weeks, which is why its methods-only scope was load-bearing.

**Three automated layers now run this watch.** ⚠ **AND ONE OF THEM HAS NOT BEEN DELIVERING — checked
2026-08-03, free, from committed history rather than assumed.** Layer 1's Routine is credited in this file and
in `IDEAS.md` with auto-capturing advances to `main`, and **it has never written an entry**:
`research/field-scan-log.md` holds exactly one dated entry, 2026-07-13, committed under the title *"manual
catch-up: automated Routine failed to deliver"*, and the three Fridays after the scope was last widened
(2026-07-17 / 07-24 / 07-31) produced nothing there, in `IDEAS.md`, or in `compute/cheap-gpu-plan.md`. **Layer 2
by contrast has fired on every Friday since its cron went weekly** (public Actions API, `event: schedule`),
1–2 h later than requested — the ordinary throttle CLAUDE.md §6 describes. So: **read layers 2 and 3; do not
assume layer 1 ran.** The claim below describes what the Routine is CONFIGURED to do, not what it has done.
1. **Weekly AI newsletter → EMAILED to trimcrae** (the user-facing one, **and the one not delivering**). Routine
   `trig_01X5xHy1cmkLjkATEijZSNJf` ("Weekly NR4A3 field-scan (newsletter + auto-capture to main)"),
   cron `0 12 * * 5` (**Fridays 8:00 AM ET**), spawns a fresh session that web-searches the past week
   (open-source methods, NR4A/EMC papers, degrader methodology, non-degrader routes, AND — added
   2026-07-14/15 — a **tooling & operating-environment watch**: our software-library releases incl. OpenFE
   & the MD/FEP stack, whether Fable (claude-fable-5) — and any future model at least as capable — has its
   cancer/bio-research restriction relaxed so we could use a top-tier model for this bio work, OpenAI
   Codex phone-without-Remote-Desktop capability, AND **compute-cost / GPU-market** changes — provider price
   drops, new/free-credit GPU providers, and better-FLOPS/$ GPUs for our MD (auto-captured to
   `research/compute/cheap-gpu-plan.md`)), writes a curated newsletter, **emails it**, and **appends
   it + auto-captures advances
   directly to `main`** (`research/field-scan-log.md`, plus append-only captures to this file,
   `IDEAS.md`, and `compute/cheap-gpu-plan.md`). This is the thing you actually read. Manage via the
   claude-code-remote trigger tools (list/update/delete). NB: `update_trigger` cannot edit a Routine's PROMPT —
   to change the scan scope, recreate the trigger (delete + create) as was done 2026-07-14/15.
   ⛔ **BEFORE DELETING IT, DUMP ITS PROMPT — THE PROMPT IS THE ONLY COPY AND DELETION IS FINAL.**
   This exact loss already happened once: the retired daily summary-writer's parameters went with it, and
   [`modalities/daily-email-system.md`](modalities/daily-email-system.md) now tells the reader to dig them
   out of git history. The field-scan prompt has no copy in this repository at all — it lives solely in the
   Routine's stored config. Recover it with the claude-code-remote MCP tool `list_triggers` and read
   `job_config.ccr.events[0].data.message.content` for `trig_01X5xHy1cmkLjkATEijZSNJf`; paste that into the
   new UI-created Routine. **It is not transcribed here on purpose** — a hand-copied 1,500-word prompt is a
   recollection, and §7 says never write one of those down as if it were the source.
2. **Mechanical BROAD digest** (raw feed). `scripts/method-watch.mjs` via
   [`.github/workflows/method-watch.yml`](../.github/workflows/method-watch.yml) — a keyword scan of
   EBI/GitHub/grants.gov that commits a dated digest to the `method-watch-cache` branch and emails it.
   NOT synthesized; it's the comprehensive raw-hit backstop the weekly newsletter can consult, not a
   deliverable.
   ⭑ **It now also carries a CLINICAL / TREATMENT-NEWS watch, and that is its FIRST section (2026-08-24).**
   Until then its only sources were Europe PMC, eight GitHub release feeds and grants.gov, so a Phase 3
   readout announced by press release — not a paper, not a tool, not a grant — **could not appear in it by
   any query**. The Merck/Moderna INTerpath-001 topline (2026-08-19) is the measured case: the first
   positive Phase 3 for an individualized neoantigen therapy, direct precedent for this repo's own
   junction-vaccine route, absent from the 2026-08-21 newsletter. The watch adds two layers of different
   kind — **ClinicalTrials.gov API v2** (structured, dated, citable; catches status flips and posted
   results) and **dated RSS/Atom feeds** (the only layer that carries a same-day topline) — scoped to the
   modality classes this program actually pursues **plus a deliberately broad oncology catch-all**, which
   is the row whose absence lost INTerpath-001. ⚠ **A news hit is a LEAD, NOT EVIDENCE**: it may prompt
   reading the primary source and may never itself be cited as a medical fact (CLAUDE.md §7). The scope
   is shared with two prompts that filter this digest before Tristan sees it, and **the narrowest of the
   three decides what he reads** — one home for that accounting:
   [`modalities/daily-email-system.md`](modalities/daily-email-system.md). ⚠ **Its cadence has ONE home — the `schedule:` block in that workflow file — and this line
   used to restate it, wrongly**: it read *"Monthly … (cron `0 7 1 * *`)"* long after the workflow went
   weekly, which is exactly the copy-drift CLAUDE.md §1 exists to stop. *(Superseded, retained: "Monthly
   mechanical digest … cron `0 7 1 * *`".)*
3. **Mechanical NARROW scan — the reopening triggers, searched by name.** ⭑ **Added 2026-08-03, and it is
   the layer this file was missing.** Layers 1 and 2 search *topics*; the table below and
   [`nr4a3-program-map.md` §6b](manuscripts/nr4a3-program-map.md#6b--parked--failed-with-todays-tools-with-a-named-trigger-to-reopen)
   name *specific capabilities*, and nothing was searching for those names — so a paper that satisfied a
   named trigger arrived in the digest indistinguishable from background, and the reader had to re-derive
   paper→parked-row by hand every week. The queries now have a machine home in
   [`research/method-watch-triggers.json`](method-watch-triggers.json) (one entry per named trigger, with the
   routes/requirements/blockers it would reopen), run by
   [`scripts/trigger_scan.py`](../scripts/trigger_scan.py) via
   [`.github/workflows/method-watch-triggers.yml`](../.github/workflows/method-watch-triggers.yml), and every
   hit is reported **with the consequence attached**. Board:
   [`research/method-watch-trigger-scan.md`](method-watch-trigger-scan.md) — its "Last run" date is what tells
   you whether the scan fired at all. ⚠ **Division of labour, so neither file drifts:** *this* table is the
   one home for **what a landed capability unlocks in prose**; the JSON is the one home for **how to search
   for it**; §6b is the one home for **which parked row it belongs to**. Do not copy any of the three into
   either of the others.

**Operating assumption (trimcrae, standing).** In-silico drug-discovery capability is on a
**steep, rising frontier** — the limits of today are not the limits in 6–12 months — and this is
a **long-lived, revisitable project that rides that frontier even if a wet-lab partner never
materialises** (regime: `emc-treatment-strategy.md → "Operating regime (2026-07-01)"`). So this
watch has **two jobs, not one**: (1) *unblock* stalled/parked routes when a capability lands
(the trigger table below), and (2) prompt a **re-grade of even *completed* work** as methods
improve — a cleared route or a shipped result is a *snapshot at a capability level*, worth
re-running when the frontier moves. Nothing here is "dead"; parked = "revisit when X lands."
**Integrity guardrail:** a coming capability justifies waiting and re-running — it never licenses
claiming the result before the method can support it.

**This file IS the "breadth" half of "state of the art."** Per the codified principle
(`CLAUDE.md → "WHAT 'STATE OF THE ART' MEANS = BREADTH-FIRST, STANDARD-DEPTH"`), a *new technique* that
opens a new evidence axis (rows below) is **default-worth-adding**; but *deepening a test we've already
run to field standard* (more FEP sampling, extra force fields, more replicates, HREX-when-independent-
windows-suffice) is **default-NO** unless the standard result is genuinely ambiguous and decision-relevant.
Adding a row here (breadth) beats over-optimizing an existing test (depth-past-standard).

> **Read the latest auto-digest:**
> `git fetch origin method-watch-cache`
> `git show origin/method-watch-cache:research/method-watch-digest.md`
> (or run `node scripts/method-watch.mjs` locally, hosts `www.ebi.ac.uk`, `api.github.com` + `api.grants.gov`).
> ⚠ *Superseded, retained: a two-host list. `api.grants.gov` was added by the 2026-07-22 funding watch this
> same file documents below, and the host list was never updated — so a reader allow-listing from here would
> have had the funding half fail silently.*

**How to use it:** the digest surfaces newest papers / tool releases per capability. A hit is
a *prompt to check this table*, not a decision. If a "🆕" line genuinely crosses a trigger
below, do the paired action and open the follow-up; otherwise no action.

> **🗺 AND THE MACHINE-READABLE TRIGGER SET THIS TABLE DOES NOT YET CARRY:
> [`manuscripts/emc-systems-map.json`](manuscripts/emc-systems-map.json) → `revival_triggers`,
> rendered as a leverage-ordered watch list in
> [`manuscripts/emc-systems-map.md`](manuscripts/emc-systems-map.md) §9 (2026-08-03).** Every closed
> or parked route and instrument there carries an enumerated **`closure_kind`** — so a fact about a
> sequence (*never revivable*) is filed apart from a limitation of today's methods (*the most
> revivable kind, and where most of this program's failures actually sit*) — and every non-permanent
> closure names, in **searchable** words, what has to land and **which routes come back with it**.
> ⚠ **Most of those triggers are NOT rows in the table below, and that is no longer a backlog.**
> ⛔ *Superseded, retained: "the map's own checker WARNs on each one it cannot find here — so treat that
> warning list as the backlog of capabilities nobody is currently scanning for."* That warning list is
> gone, because it was wrong: `[Z5]` read only this file and reported 15 triggers as unwatched when 12
> of them named a machine `scan_trigger` query that `[Z8]`, three lines below it, was already
> resolving. Of 22 revival triggers, **18 carry a query**; the four that carry neither are
> `internal_work`/`authorization`, which a LITERATURE watch list structurally cannot carry. The
> checker now reads the query as evidence and reports 0 `[Z5]`. This table stays the one home of the **capability → action** pairing; the
> map owns the **closure → trigger → what-it-reopens** graph, and neither restates the other.

## How an item gets from a feed to a document

Three layers, and they are not interchangeable. **The feeds** (this file's watched topics, run by
`scripts/method-watch.mjs`) are broad and catch what a query was never written for. **The
reopening-trigger scan** ([`method-watch-triggers.json`](method-watch-triggers.json)) is narrow,
deterministic and free, and answers *"did the specific named capability we are parked on arrive?"*.
**The matcher** ([`scripts/news_match.py`](../scripts/news_match.py), added 2026-08-28) is one model
call over the week's headlines and `what_it_would_claim` for all 32 rows of
[`publications.json`](../systems/graph/publications.json), and answers the question neither of the
others could — *"which of OUR documents does this bear on?"*

⛔ **The matcher proposes; nothing cites automatically.** It has seen a headline, not a paper. Its
output is `research/literature/news-match-queue.json`, an unvalidated queue — **not linked here
because it does not exist until the first CI run writes one**, and seeding it by hand would be a
plausible-looking record of a model run that never happened. Rows that survive a human read become
`open` rows in
[`citation-debt.json`](literature/citation-debt.json), which refuses a row that names no
`blocked_on`. ⚠ **It reports `supports` against `complicates` and prints the census**, because a
watch list kept by people who want these routes to work under-reports the results that cut against
them — the count is what makes that question askable.

⭐ **THE JUDGE IS A SCHEDULED CLAUDE SESSION, NOT AN API CALL** (trimcrae, 2026-08-28: *"Why on
earth would I use an additional API key from a Claude code session. Obviously use a scheduled
session"*). The first build called `api.anthropic.com` with `secrets.ANTHROPIC_API_KEY` — a second
bill for a capability this project already pays for. It was also inert: that secret does not exist,
which the first CI run
([33215625481](https://github.com/trimcrae/Rare-cancers/actions/runs/33215625481)) showed by
printing `ANTHROPIC_API_KEY:` **empty** beside `GITHUB_TOKEN: ***` for a secret that is defined.
⚠ **Three call sites still reference that secret** — `email_digest.py`'s summary fallback and
`daily-degrader-email.yml` — so the API fallback in both emails has almost certainly never fired
once. Nobody noticed because the newsletter's summary comes from the `email-outbox` branch, written
by a scheduled session, so the fallback was never reached. Same shape as the SES branch documented
in `mailer.py`: a code path that looked like coverage and had never run. Recorded, not fixed —
that is trimcrae's call, and the matcher no longer needs it.
⭐ **The session was the better mechanism anyway, not just the cheaper one**: a session can read the
source, and the API judge only ever saw a headline. Steps:
[`news-match-routine-prompt.md`](routines/news-match-routine-prompt.md).

⭐ **THE ROUTINE IS SCHEDULED, AND IT WAS CREATED PROGRAMMATICALLY — IN TWO CALLS, NOT ONE.**
`create_trigger` alone spawns a session with **no repository** (`session_context.sources` absent):
tested 2026-08-28, it ran 26 minutes reporting `RUNNING` and ended `FAILED`, which is the same
defect that left the field-scan Routine delivering nothing for six weeks. But `create_session` takes
`source_url`, and `create_trigger` can bind to an existing session — so the working path is
`create_session` (repo attached, model pinned) then `create_trigger(persistent_session_id=…)`.
⭐ **Proven end to end 2026-08-29:** a scheduled firing reached the bound repo-attached runner, on
the pinned Opus, with `sources` intact. ⛔ **A manual `fire_trigger` does NOT** — it ignores the
binding and spawns a fresh unattached Sonnet session, so it is not a valid test of the schedule
and reading it as one gives the opposite answer. Probe a schedule with a schedule (`run_once_at`).
⚠ **The discriminating field is `session_context.sources`, readable the moment a session is created
and long before anything runs. Check it before binding a schedule to anything** — a Routine firing
into an empty container looks healthy for as long as it flails. Both routes, the evidence table and
the model-pinning note: [`news-match-routine-prompt.md`](routines/news-match-routine-prompt.md).

⭐ **Validated end to end 2026-08-28, by a session doing exactly what the Routine will do**: 47 fresh
headlines against 32 publication claims → 15 distinct stories matched, 19 explicitly bearing on
nothing, 0 unreached, 0 verdicts rejected. Running it also found a defect no amount of design would
have: one Phase 3 readout arrived from **eleven outlets**, so the census counted eleven `supports`
where there was one story. `duplicate_of` now collapses a story to one row and excludes the copies
from the census — the bias instrument counts stories, not headlines, or it inflates the exact number
it exists to watch, in the exact direction it is watching for.

⚠ **Why the matcher is not inside the trigger scan.** That scan's bottleneck is its Europe PMC
*query*, not its title filter: the API returns only what the query asked for, so a model placed
downstream of a narrow query still never sees the paper the query missed. The newsletter's feeds are
broad, and are the layer that actually caught PMID 42570981.

## Capability → action trigger table
| When this capability becomes usable | …do this |
|---|---|
| virtual-cell / perturbation model predicts held-out **knockdown phenotype** | test EMC **EWSR1::NR4A3 fusion-dependence** — the degrader/ASO make-or-break |
| open **AF3-class ternary-complex** prediction **[⚠ PARTIALLY FIRED 2026-07-13]** — open tools now exist: **DeepTernary** (SE(3)-equivariant GNN, GitHub youqingxiaozhua/DeepTernary, "TernaryDB" ~20k structures — verify that set; PDB has few true PROTAC ternaries), **FKSFold** (Feynman–Kac-steered diffusion for molecular-glue ternaries) | **DECIDED (reviewer-AI, Option A\*): adopt DeepTernary as a SECOND, conditional architecture GENERATOR alongside Boltz** — union of pose clusters, concordance as a weak `R_gen` prioritization annotation (NOT in `S_d`, NOT a hard filter), never replace Boltz, generator scores never rank selectivity. Full qualification sequence + concordance def + case risks + adoption criteria: **[deepternary-qualification-protocol.md](modalities/deepternary-qualification-protocol.md)**. NB: it predicts *structure* not cooperativity, and PROPAGATES the assumed cmpd-19 binary pose (rigid-body); ranking crux stays with physics + the **reframed NR-V04 FUNCTIONAL gate** (NR-V04 has NO deposited ternary structure → end-to-end degradation-outcome test, NOT architecture reproduction) |
| reliable **structure-based generative + selectivity** scoring | design the **NR4A3 warhead** at the `nr4a-selectivity.json` divergent handles |
| a **validated PROSPECTIVE molecular-glue design**, or a **glue-interface selectivity predictor scored on held-out interfaces** — ⛔ **the test is prospective; a retrospective rationalisation of a glue somebody already found does NOT fire this row**, because that is exactly what the field has always done | **re-grade [route 10](manuscripts/program/target-route-options.md) from "⏸ watch, do not build"** — that route's own text names this row as the right action and it did not exist until 2026-08-07. ⭐ **Why a glue is the one modality worth a standing watch rather than a build:** on the programme's own thesis it is the BEST mechanistic match — close-paralogue degrader selectivity *"is created at the induced target–E3 interface … not at the conserved warhead pocket"* — and it fails on the thesis's **second** clause, that in every landmark case selectivity was *"**discovered then rationalized** by a solved ternary structure, never predicted blind"*. So the route is not blocked by anything this repo could build; it is blocked by a capability that must arrive from **someone else's screen**. ⚠ **What firing this does NOT license.** A glue has no linker, so it has **no covalent axis and no designed exit vector**: the two mechanisms the PROTAC route carries besides pocket shape both vanish, and the claim collapses onto a single induced-interface ΔΔG of the ~1 kcal/mol size **no instrument in this program resolves** ([`instrument-census.json`](modalities/instrument-census.json) → `coverage`, `R7`/`R11`). Firing this row reopens a **route**, never a result. Searchable form + what it reopens: [`method-watch-triggers.json`](method-watch-triggers.json) → `TRG-GLUE-PROSPECTIVE-DESIGN` (registry `TR-GLUE-DESIGN-PREDICTOR`, route `RT-GLUE`, blockers `BLK-INDUCED-COMPLEX` / `BLK-PARALOGUE-DDG`) |
| robust **cryptic-pocket** prediction | re-grade the NR4A3 LBD **undruggability** prior without GPU MD |
| **cheap generative conformational-ensemble** model (BioEmu / AlphaFlow / subsampled-MSA AlphaFold) **validated against known cryptic pockets** — i.e. it recovers CryptoSite/PocketMiner benchmark sites without GPU-days of MD **[✅ (a) FIRED 2026-07-24 — BioEmu v1.4.1]** | **(a)** re-grade the NR4A3 LBD cryptic-pocket ensemble at near-zero cost as a cross-check on the metadynamics **— DONE: BioEmu (sequence-only) detects Pocket-5 in 68% of frames and opens it to druggable (≥D\*=0.53) in 12.5% (7/56), well below metad 0.68 / release 0.587 but concordant with the experimental 8XTT NMR ensemble (0.15). Independent-method corroboration of the site + an unbiased population estimate that tempers the biased-metad fraction; see [modalities/nr4a3-bioemu-crosscheck-findings.md](modalities/nr4a3-bioemu-crosscheck-findings.md). Integrity: apo is BioEmu's weakest regime (~50% recall) + uncalibrated on rare-open populations (JCTC 6c00135) → qualitative cross-check, not a population estimate;** **(b)** flips the **cryptic-pocket druggability atlas for neglected targets** (`IDEAS.md` Platform/vision #4) from focused-target-class-only to **proteome-scale feasible** — the per-target "open the pocket" step collapses from GPU-days to pennies. Integrity guardrail: a cheap ensemble is a hypothesis generator; a druggable-pocket claim still needs the fpocket/energetics gate, and each atlas entry stays an unvalidated, confidence-calibrated hypothesis benchmarked on held-out known cryptic sites |
| cheaper / more reliable **free-energy (FEP or ML free-energy)** on **cryptic / induced-fit** pockets | run the **denovo_401 selectivity FEP** currently SKIP-ped as ceiling-bound + least-reliable-here, and re-grade the binder-selectivity claim against it |
| turnkey / maintained **alchemical protein-mutation (relative selectivity) FEP** **AND** a favourable NR4A3-vs-NR4A1/2 **pocket-homology** assessment (few divergent pocket-lining residues; similar *opened* backbones) | run **alchemical-mutation FEP as a confirmatory cross-check** on the ABFE selectivity ΔΔG — a *direct* ΔΔG with built-in error cancellation would harden (or refute) the binder-selectivity claim now carried by the ABFE-difference. Precursor = the pocket-homology check itself (align NR4A3/1/2 opened Pocket-5, count differing lining residues + backbone RMSD): if pockets are highly similar, mutation-FEP becomes attractive; if they diverge conformationally, that *itself justifies* the per-receptor ABFE choice (`nr4a3-degrader-paper.md` §4 "Why absolute (ABFE), not relative/mutation, FEP") |
| better **induced-fit / conformational-ensemble docking or ML affinity** | re-score denovo_401 (and the de-novo pool) against the *dynamic* NR4A3 pocket instead of single/few frames — tightens the frame-dependent margin (+12.83 release vs +7.44 metad) |
| **in-silico oligonucleotide/nanoparticle tumour-delivery** predictor (biodistribution / endosomal escape / PBPK / ML tumour-penetration) | score the **B7-H3-targeted junction-siRNA / AOC** delivery in-silico and **re-grade the ASO route feasibility** (delivery is the route's gate) |
| **oligonucleotide tumour-delivery TECHNOLOGY / candidate** — an AOC/conjugate, tumour-penetrating-peptide, or ligand-targeted-LNP platform that reaches **non-hepatic solid tumours**, OR a **characterised EMC-enriched surface antigen** (the AOC's targeting arm) | **propose a concrete junction-oligo delivery *candidate*** (not just an in-silico test) and re-grade the ASO route's dominant gate — this is the watch for a real *way to do delivery*, distinct from the predictor row above |
| **vector tumour-delivery TECHNOLOGY / candidate** — an AAV, lentiviral or non-viral **vector** platform with demonstrated biodistribution to a **non-hepatic solid tumour**, carrying a transcriptional or nuclease payload | re-grade the three **vector-gated** nucleic-acid routes (`RT-CRISPR-CAS13`, `RT-RIBOZYME`, `RT-SYNPROMOTER`). ⚠ **ADDED 2026-08-06 by the route framing audit, and it is a SPLIT, not a new idea:** all three were pointed at the **oligonucleotide** row above, so an AOC or LNP landing would have read as reopening a route that needs a vector. `BLK-DELIVERY` and `BLK-VECTOR-DELIVERY` are separate blockers precisely because the evidence clearing one need not clear the other |
| calibrated **ASO off-target / RNase-H cleavage-activity** predictor | **retire the conservative "gap-mismatch ⇒ non-cleaving" heuristic** in the junction-ASO specificity screen (`fusion-junction-aso-working-record.md` §3a-quater) and re-grade predicted specificity with a calibrated model |
| improved **ASO/siRNA efficacy + target-site-accessibility** predictor | **re-rank the junction designs for potency** and replace the local-fold accessibility proxy (`fusion-junction-aso-working-record.md` §3a-bis iii) |
| new **patient-derived EMC / FET-fusion-sarcoma model** (cell line / organoid / PDX) | **enables the decisive wet-lab experiment** — junction-ASO knockdown + parental-sparing in EMC cells (`fusion-junction-aso-working-record.md` §4) — and a fusion-dependence readout |
| improved **perturbation / DepMap-transfer** models | re-test synthetic-lethal / nominate new EMC dependencies |
| **remote-controlled / cloud robotic wet lab** a solo researcher can rent by the experiment (Emerald Cloud Lab, Strateos/Transcriptic-class, or an autonomous "self-driving"/lab-in-the-loop service) reaches solo-affordable, EMC-runnable scope | **re-grade the whole "no wet lab" operating regime** — the wet-lab-gated experiments become *runnable by us*, not just by a hypothetical collaborator. Scope + price the **cheapest decisive experiment** (junction-ASO knockdown + parental-sparing in an EMC/FET-fusion line — ASO paper §4) and the degrader/delivery validations; ask trimcrae before committing spend. **Honest caveat:** a cloud lab unlocks *robotic execution*, not the *reagents/biology* — you still need the EMC cell line or organoid (couples to the patient-derived-model row) and antibodies/oligos, so this flips the *execution* gate, not automatically the *material* gate. |
| a **second independent phase-behaviour force field** (Mpipi or a CALVADOS successor) shown to resolve differences between closely related disordered sequences **finer than 0.06 in the Flory scaling exponent ν**, OR a published **EMC condensate measurement stratified by 5′ fusion partner** (EWSR1 vs TAF15 vs TCF12) rather than pooled | **re-grade the shelved condensate arm.** It ran to its prespecified standard on 2026-08-24 — 55 CPU runs, both controls passing — and returned a bounded null: no partner window separated from any other, nor from wild-type NR4A3's own disordered region. It was shelved on expected value, not on failure. ⛔ **A re-run of the same arm with more sampling does NOT fire this row** — that arm's own prespecification forbids extending it after seeing the numbers, and the reason to reopen is *resolution*, not repetition. Searchable form: [`method-watch-triggers.json`](method-watch-triggers.json) → `TRG-CONDENSATE-PARTNER-RESOLUTION` (registry `TR-CONDENSATE-PARTNER-SIGNAL`, instrument `INS-CALVADOS-SINGLE-CHAIN`, capability `TECH-CONDENSATE-RESOLUTION` — what a hit lands on). ⛔ **AND THAT SEARCHABLE FORM WAS A NAME WITH NOTHING BEHIND IT UNTIL 2026-08-28**: the trigger was `scan_enabled: true` with **no `search` block at all**, so it rendered on every board as a watched row while searching for nothing. `trigger_scan.py --check` had been reporting it and no gate ran `--check`; both halves are fixed — the queries exist now, and `scripts/preflight.sh` runs the checker in the ordinary commit loop. Evidence: [`emc-condensate-calvados-findings.md`](modalities/emc-condensate-calvados-findings.md) |
| ⛔ **NOT AN IN-SILICO CAPABILITY — A FREE ROUTE TO THE SIX CLOSED EMC SERIES.** Any of `meisKindblom1999` (n=117), `ussc2022` (n=60), `uMich2023`, `china2016`, `stacchiotti2019pazopanib` or `stacchiotti2014sunitinib` becoming readable at no cost — an author manuscript or repository deposit appearing, a publisher opening its archive, or an institutional route this project gains. ⚠ It fires only on a copy that is genuinely free or genuinely licensed; it is never a licence to route around a paywall | **Read that series' survival figures and its SITE table.** ⭐ The site tables are the half that has already moved a route — they gave RT-LIMB-PERFUSION its extremity fraction — and they are printed by series whose curves are useless, so a paper that fails the Kaplan-Meier test can still be worth reading. Searchable form: [`method-watch-triggers.json`](method-watch-triggers.json) → `TRG-CLOSED-EMC-SERIES-ACCESS`. ⚠ `scan_enabled: false` deliberately — a literature scan cannot see this, and the discriminating observation is a $0 Unpaywall re-check of six known DOIs |
| any direct **chemical/biological matter against NR4A3** or the fusion | fold into the relevant route memo immediately |
| a **human clinical readout for a therapy aimed at a fusion BREAKPOINT** — any fusion, any cancer, any modality that targets the junction sequence itself (peptide or mRNA vaccine, TCR-T, soluble TCR/ImmTAC, adoptive transfer). ⛔ **This is an OUTCOME IN A PERSON and it is NOT the predictor row the three antigen routes are otherwise parked on** — a tool would let us COMPUTE something we cannot; a readout moves the PRIOR on whether the class does anything, supplying no method at all | **Grade it on three axes before any artifact moves**: which fusion (EMC, a sibling FET fusion, or unrelated); n and whether there was a control arm; immunologic readout or clinical one — because the headline word *clinical* inflates into efficacy at the slightest encouragement. Then write it into every path in the trigger's `cite_into` and record the outcome in [`citation-debt.json`](literature/citation-debt.json). ⛔ **A NEGATIVE READOUT FIRES THIS ROW TOO**, and is the direction a watch list kept by people who want the route to work will quietly under-report. ⚠ **PARTIALLY FIRED — the fired half is n = 1.** PMID 42570981: an off-the-shelf multi-peptide vaccine spanning the type 1 EWSR1-FLI1 breakpoint, de novo polyfunctional CD4⁺ responses against all four fusion-derived peptides persisting beyond two years, in ONE patient, uncontrolled, after multimodal therapy. It raises the prior and clears nothing: `BLK-ANTIGEN-COLD` is a claim about how much junction peptide-HLA an EMC cell displays, which no peripheral T-cell readout measures. The counterweight is carried at equal weight — the modality's largest human series (PMID 22726592, n = 21, SYT-SSX) has a published evaluation reporting no robust immune response to the target epitope. Searchable form: [`method-watch-triggers.json`](method-watch-triggers.json) → `TRG-FUSION-JUNCTION-CLINICAL` (routes `RT-VACCINE` / `RT-JUNCTION-NEOANTIGEN` / `RT-TCR-IMMTAC` / `RT-VACCINE-COMBINATION`, capability `TECH-JUNCTION-CLINICAL-PRECEDENT`). ⚠ **ADDED 2026-08-28 BECAUSE NOTHING COULD SEE THIS CLASS.** The word *vaccine* appeared in ZERO of the 38 trigger queries; `TRG-JUNCTION-PHLA` missed PMID 42570981 twice over (its query is anchored on TITLE:neoantigen / peptide-HLA / pMHC / immunopeptidome, and its title filter on the same terms — none of which is in that title). The paper reached this repository through the clinical/treatment-news feed instead, four days after that feed was built |

The **delivery** rows are load-bearing: the ASO/siRNA route is gated by tumour delivery, which
we cannot solve in-silico today. There are **two distinct ways this unblocks**, so there are two
delivery rows:
1. **An in-silico delivery *predictor*** (biodistribution / endosomal escape / PBPK / ML
   tumour-penetration) → the proposed B7-H3-AOC/junction-siRNA design (see
   `manuscripts/program/emc-treatment-roadmap.md` → ASO "Delivery strategy") becomes computationally
   *testable*, moving the route off "delivery-limited" **in-silico**.
2. **A delivery *technology/candidate*** — an AOC/conjugate, tumour-penetrating peptide, or
   ligand-targeted LNP that actually reaches non-hepatic solid tumours, or a characterised
   EMC-enriched surface antigen to serve as the targeting arm → lets us **name a concrete delivery
   candidate**, moving the route off "delivery-limited" **in reality**. This is the more important
   of the two: the honest bottleneck is not "we can't simulate delivery," it is "no validated way
   to deliver an oligo to an EMC tumour exists yet." A single characterised EMC surface antigen or a
   working soft-tissue-sarcoma AOC would change the route's standing more than any predictor.

### The one row that is NOT in-silico: remote robotic wet lab
Every other row above extends what *in-silico* can do. The **remote-controlled robotic wet lab**
row is different in kind, and load-bearing enough to call out: it is the only watched capability
that could **flip the project's founding constraint** — *"No wet lab is available, so every next step
must be publish-to-convince or in-silico"* (`CLAUDE.md`). The current regime routes every wet-lab-gated
route (the decisive junction-ASO knockdown + parental-sparing readout; degrader cellular validation;
delivery) through a hypothetical *funded collaborator/foundation*, because a solo researcher has no
bench. A **cloud lab** — where you design an experiment in software and a remote robotic facility runs
it, billed per run (Emerald Cloud Lab, Strateos/Transcriptic-class, or an autonomous self-driving-lab /
"lab-in-the-loop" service) — is the scenario where *we* could run those experiments ourselves.

**Why it's a watch, not an action yet (be honest):** today this is gated on (1) *cost* — solo-affordable
per-experiment pricing that fits the operating regime, not an enterprise contract; (2) *scope* — the
service must actually offer the cell-based assays EMC needs (transfection/knockdown, immunostaining,
qPCR/RNA-seq readout), not just chemistry/liquid-handling; and (3) *material* — a cloud lab supplies
robots and generic reagents, **not** the EMC/FET-fusion cell line, which stays coupled to the
patient-derived-model row. So the trigger is "a cloud lab reaches *solo-affordable, EMC-assay-capable*
scope," and even then the cell-line/reagent gate is separate.

**⭐ GATE (1) NOW HAS A NUMBER, AND GATE (3) IS UNMOVED BY IT — measured 2026-08-23, $0.**
[`wet-lab-contracting-costs.md`](manuscripts/modality-census/wet-lab-contracting-costs.md) prices the
experiments this row exists for, bottom-up from published academic core-facility rate cards
([`wetlab-contracting-costs.json`](modalities/wetlab-contracting-costs.json) owns every figure —
**do not restate one here**). Three things this row needs to carry:

- **Cost, gate (1).** The decisive junction-ASO experiment this row names prices in the **tens of
  thousands**, and the portfolio's smallest ask is roughly a fifth of that. Not enterprise money — and
  not solo money either, against the ~$1,000 filter `what-a-civilian-can-buy.md` applies.
- **⛔ Automation moves gate (1) part-way and gate (3) not at all.** Hourly technician time is
  **60.9%** of the modelled total and **82–85%** of the plate experiments — genuinely the layer a
  robotic lab removes, and ECL's own comparison replaces four technicians with none. But with hands
  entirely **FREE**, **no costed experiment falls below $2,000**, and the cell-engineering ones
  (an isogenic knock-in, a degron line) **do not move at all**, because a fixed clonal-selection
  project fee is not billed by the hour and a faster pipettor does not make cells divide faster.
  **So the arithmetic agrees with what this row already said**: a cloud lab flips the *execution*
  gate, not the *material* gate.
- **⚠ And the tier is still quote-only — re-checked, not assumed.** `what-a-civilian-can-buy.md` §4.7
  flagged the cloud lab as *"the one item worth re-checking if the model ever becomes self-serve."*
  **Re-checked 2026-08-23: it has not.** Emerald Cloud Lab's own documentation states its displayed
  prices *"are only for the sake of example and do not represent actual prices"*, and its pricing
  function still bills **`PriceOperatorTime`** as a line item beside `PriceInstrumentTime` — a robotic
  lab still bills a human. Its vocabulary is `team`, `notebook` and *financing team*: an
  organisation's shape, not an individual's. **This row does not fire.** **Integrity guardrail (same as every
row):** the arrival of a way to *run* the experiment never licenses reporting an outcome before the
experiment is actually run.

## Watched topics (kept in sync with `scripts/method-watch.mjs`)
- virtual-cell / perturbation prediction (scGPT / Geneformer / State / Arc Virtual Cell)
- AF3-class structure & ternary complex (AlphaFold3 / Boltz / Chai / RoseTTAFold)
- de-novo selective small-molecule / binder design (RFdiffusion / ProteinMPNN / diffusion SBDD)
- cryptic-pocket / dynamics-based druggability (PocketMiner, metadynamics)
- **cheap generative conformational-ensemble models** (BioEmu, AlphaFlow, subsampled-MSA AlphaFold /
  distributional structure prediction) — the capability that could collapse the per-target enhanced-sampling
  cost and unlock the neglected-target cryptic-pocket druggability atlas (`IDEAS.md` Platform/vision #4)
- **in-silico oligo/nanoparticle tumour-delivery prediction** (AOC, siRNA delivery, LNP,
  endosomal escape, tumour penetration — ML / PBPK / computational)
- **oligo tumour-delivery TECHNOLOGY / candidate** (AOC / antibody-oligonucleotide conjugate,
  tumour-penetrating peptide, ligand-targeted LNP for non-hepatic solid tumours; EMC-enriched
  surface antigen for a targeting arm) — the watch for a real *way to do delivery*, not a predictor
- **vector tumour-delivery TECHNOLOGY / candidate** (AAV / lentiviral / non-viral vector reaching a
  non-hepatic solid tumour with a transcriptional or nuclease payload) — split from the oligo row
  2026-08-06; the three vector-gated routes need this one, not the oligonucleotide one
- **ASO/gapmer off-target & RNase-H cleavage prediction** (ASO-paper next step: retire the
  gap-mismatch heuristic — §3a-quater)
- **ASO/siRNA design, efficacy & target-accessibility prediction** (ASO-paper next step:
  potency ranking + better accessibility than the local-fold proxy — §3a-bis iii)
- **patient-derived EMC / FET-fusion-sarcoma functional models** (ASO-paper next step: unblocks
  the decisive knockdown + parental-sparing experiment — §4)
- **remote-controlled / cloud robotic wet lab** — solo-affordable, per-experiment remote execution
  (Emerald Cloud Lab, Strateos / Transcriptic-class, autonomous "self-driving lab" / lab-in-the-loop
  services) with cell-based assay scope (transfection/knockdown, immunostaining, qPCR/RNA-seq) — the
  one watch that could flip the "no wet lab" constraint and unlock the whole wet-lab-gated sector
- NR4A3 / EWSR1::NR4A3 direct EMC advances
- **Funding watch (grants.gov, added 2026-07-22)** — currently-open federal **AI / compute**
  solicitations, flagging the subset open to **individuals** (grants.gov eligibility 25) or
  **unrestricted** (99) that a solo unaffiliated researcher could apply to for **GPU/compute**
  funding. Context: the OSTP **"Science: A New Golden Age"** directive (2026-07-21) redirects
  federal R&D toward AI and toward *individual scientists*, but shipped as a directive with **no
  applyable program** — the money surfaces later as ordinary NSF/DOE/NIH/DARPA/ARPA-H
  solicitations, which this watch catches as they post. Not a capability-unlock trigger; a
  funding-availability watch. **Integrity guardrail:** a grants.gov hit is a prompt to *read the
  solicitation* — the detail page's eligibility is authoritative over the coarse keyword+eligibility
  filter; never assert an opportunity is applicable without reading it.

> **ASO-paper coverage.** The last three rows above (plus the delivery row) are the
> fusion-junction ASO paper's specific next-step gates, mirroring how the degrader paper's
> gates (ternary modelling, warhead design, cryptic-pocket) are watched. Each maps to a
> concrete in-paper action so a digest "🆕" can be triaged straight to a section to update.

*Design principle (from `emc-treatment-strategy.md` Q3): keep this a periodic digest + this
table. Do not over-engineer a "capability detector"; pipelines are kept modular so a new
model swaps in cheaply.*

## Open follow-ups from digests (triage log)
Hits that crossed (or are warming) a trigger. A new session should action or clear these.

- **[2026-07-24] Cheap-ensemble-generator trigger FIRED — BioEmu v1.4.1 (Microsoft, released 2026-07-20) →
  action (a) DONE.** Ran a near-zero-cost orthogonal cross-check of the NR4A3 LBD cryptic-pocket ensemble
  (`weekly newsletter` prompt). BioEmu (learned equilibrium-ensemble diffusion emulator) generated 64 samples of
  the apo LBD **from sequence alone**, HPacker side-chain reconstruction, then the **identical** harmonized
  Pocket-5 detector used for metad/release. Result (56 frames): **Pocket-5 site detected in 68% (38/56); druggable
  ≥D\*=0.53 in 12.5% (7/56)** — well below metadynamics (0.68) and unbiased release (0.587), but **concordant with
  the experimental 8XTT NMR ensemble (0.15)**. Reading: independent-method corroboration of the *site's*
  existence/openability + an unbiased population estimate suggesting the biased-metad fraction may *over*-represent
  the open state (two unbiased sources, BioEmu 0.125 and NMR 0.15, agree on a minority-open population).
  **Integrity:** apo is BioEmu's weakest regime (~50% recall) and it is not calibrated on rare-open populations
  (JCTC 10.1021/acs.jctc.6c00135) → this is a *qualitative* cross-check, not a population estimate, and does not
  replace the physics. Full write-up: [modalities/nr4a3-bioemu-crosscheck-findings.md](modalities/nr4a3-bioemu-crosscheck-findings.md);
  data [modalities/nr4a3-bioemu-crosscheck.json](modalities/nr4a3-bioemu-crosscheck.json); pipeline
  `nr4a3_bioemu_{pocket,prepare,vast_launch}.py` + `Dockerfile.bioemu` + `fusion-cpu-extras.yml`
  (bioemu_bake/run/collect/status/stop). **Also strengthens `IDEAS.md` Platform/vision #4** (proteome-scale
  cryptic-pocket druggability atlas): the per-target "open the pocket" step is now demonstrably **minutes on one
  GPU for ~$0.15**, on the NR4A3 exemplar. Trigger action (b) [atlas feasibility] correspondingly de-risked.
  Status: **FIRED / done; folding the cross-check into the degrader paper §2 druggability discussion.**

- **[2026-07-22] Funding watch added to the weekly newsletter (trimcrae ask — "build this into our
  weekly newsletter").** Prompted by the WSJ/OSTP **"Science: A New Golden Age"** directive
  (2026-07-21), which redirects federal R&D toward AI and toward *individual scientists* but is a
  directive with **nothing to apply to yet** — applyable funding will surface later as ordinary
  agency solicitations. Rather than a separate cron, folded the watch into the existing mechanical
  digest: `scripts/method-watch.mjs` now polls the **grants.gov Search2 API** for currently-open
  AI/compute opportunities (three queries: AI + individuals/unrestricted, HPC/compute +
  individuals/unrestricted, AI firehose/early-warning), rendered as a **"Funding watch"** section in
  the digest and surfaced in the emailed TL;DR (`email_digest.py` SYSTEM prompt updated). This rides
  the weekly Method-watch email — no new schedule. Eligibility codes: 25 = Individuals, 99 =
  Unrestricted. Status: **live** (validated on a runner; grants.gov is proxy-blocked from the dev
  sandbox, so it degrades to a "query failed" line there and runs for real in CI). Next: when a 🆕
  individual/unrestricted AI/compute opportunity appears, read its detail page and, if applicable,
  decide whether to apply for GPU funding. **Eligibility finding:** the open opportunities require an
  eligible *organization* (a bare individual can't submit); a **single-member US LLC** is an eligible
  applicant type on both NSF 26-512 and the DoD Rare Cancers IDA — documented as a parked future path
  in [compute/cheap-gpu-plan.md](compute/cheap-gpu-plan.md#possible-future-path--form-a-us-llc-to-become-grant-eligible-funds-real-gpu--not-just-free-credits).
  Reusable eligibility check: `method-watch.yml` with `probe_grants=<oppId>`
  (`scripts/fetch-grants-eligibility.mjs`).

- **[2026-07-05] PocketMiner was watched as a *style*, never RUN as an orthogonal cross-check — closing that gap
  (trimcrae catch).** We built our cryptic-pocket case with our OWN metadynamics + fpocket ("PocketMiner-*style*"
  transient-pocket detection in `nr4a3_md.py`/design-spec), but never ran the actual `bowman-lab/PocketMiner`
  GNN. As a cheap, orthogonal, published-method cross-check it is textbook breadth-first default-yes and we left
  it on the table. **Action (task #15):** run PocketMiner on the **apo** AF2 NR4A3 LBD (AF-Q92570, 373–626 — the
  pre-metadynamics structure; feeding it the metad-*opened* structure would be circular) → compare its top
  cryptic-pocket residues vs our fpocket Pocket-5 lining set → if they overlap, fold an independent-corroboration
  line into the degrader paper's druggability section and flip this row's status. PocketMiner is a small GNN
  (CPU-runnable) so it does NOT compete with the ABFE g5 fleet. Note the honest limit: PocketMiner is a
  *predictor* (per-residue propensity), so it corroborates the *site/existence*, not the *opened geometry or
  druggability* — those still come from our MD. Status: **DONE (2026-07-05)** — ran on the apo AF2 LBD
  (`pocketminer_src/` → `gpu-pocketminer-aws.yml`, ml.c5.2xlarge). **Positive, honestly moderate:** Pocket-5
  mean cryptic-pocket score 0.64 vs 0.47 LBD background (1.36× enrichment), 8/10 pocket residues ≥0.5, 4/10
  ≥0.7 (incl. 3 selectivity handles); caveat — the absolute top residues are an N-terminal truncation-edge
  artifact, so we rest on the enrichment. Folded into `nr4a3-degrader-paper.md` §2.1;
  data `modalities/nr4a3-pocketminer-result.json`.
- **[2026-07-05] Cheap-ensemble-generator trigger + a new Platform/vision route (cryptic-pocket druggability
  atlas).** Prompted by the PocketMiner discussion: PocketMiner-class *predictors* don't produce opened structures
  or druggability, so a **druggability-scored cryptic-pocket resource for neglected disease targets** is a genuine
  gap (prior deep-MD cryptic-pocket campaigns = SARS-CoV-2 only; static-pocket DBs miss dynamics). Captured as
  `IDEAS.md` Platform/vision #4 (post-first-two-papers; feasible now only as a *focused target class*). Added the
  paired **cheap generative conformational-ensemble** trigger row + watched topic above: if BioEmu/AlphaFlow-class
  models validate against known cryptic pockets, the per-target compute wall collapses and the proteome-scale atlas
  becomes feasible. Status: **watching** (no validated hit yet) + **idea captured**.

- **[2026-07-05] Remote/cloud robotic wet lab added as a watch — the one trigger that could flip the
  "no wet lab" constraint (trimcrae ask).** Added a trigger-table row, a dedicated "not-in-silico"
  callout, a watched topic, and a matching `scripts/method-watch.mjs` TOPICS query for a
  remote-controlled / cloud robotic wet lab that a solo researcher can rent per-experiment (Emerald
  Cloud Lab, Strateos/Transcriptic-class, or an autonomous self-driving-lab / lab-in-the-loop service).
  Rationale: every other row extends *in-silico*; this is the only watched capability that could let
  **us** run the wet-lab-gated experiments (junction-ASO knockdown + parental-sparing, aso-paper §4;
  degrader/delivery validation) instead of routing them through a hypothetical funded collaborator —
  i.e. it could unlock the whole wet-lab-gated sector. Trigger = *solo-affordable* pricing **AND**
  *cell-based-assay* scope; the EMC cell line/reagents stay a **separate** (material) gate coupled to
  the patient-derived-model row, so a hit flips *execution*, not *biology*. Status: **watching** (no
  hits yet). Same integrity guardrail as every row: a way to *run* an experiment never licenses
  reporting its outcome before it is run.

- **[2026-07-03] EMC-line real-data probe — new lines NOT public; GSE4303 tumour microarray IS.** A probe
  (`modalities/emc_line_data_probe.py` → `emc-line-data-probe.json`) for real-EMC surface/expression data found:
  (1) the two new patient-derived lines **have not deposited transcriptomes** — USZ-EMC [Bangerter 2022/2023] is
  "available on request", NCC-EMC1-C1 [Iwata 2025] is paywalled (abstract has no accession); the USZ OA text
  mentions **EGFR/KIT** (unverified as surface IHC). (2) A public **real-EMC *tumour* microarray, `GSE4303`**
  ("Gene expression profile of EMC"; Subramanian-type), plus scattered EMC tumour samples, DOES exist. **Action
  options (open):** (a) re-point/ cross-check the surfaceome scan against `GSE4303` — real EMC *tumour*, but old
  microarray, bulk-tumour stromal dilution, small n, possibly two-colour ratio data (may not give absolute
  surface-antigen levels — verify platform first); (b) **obtain the USZ/NCC line data by contacting the authors**
  (better data, but a human/wet-lab-adjacent action, not in-silico); (c) leave the DepMap surrogate as the
  published basis and cite `GSE4303`/line-existence as the upgrade path. **Decision (trimcrae, 2026-07-03): DO
  BOTH (a)+(b).** (a) built + run: `modalities/emc_gse4303_crosscheck.py` → `emc-gse4303-crosscheck.json` —
  **outcome: GSE4303 is UNUSABLE** (two-colour cDNA-clone array; log-ratios not absolute expression; probes
  lack gene symbols → 0 shortlist genes resolved; the platform gate correctly flagged it). Public-data route
  exhausted → author-held line data is the only real unlock. **A surface-antigen scaffold paper was spun out**
  ([`manuscripts/surface-targets/emc-surface-target-landscape.md`](manuscripts/surface-targets/emc-surface-target-landscape.md), gated on that
  data). (b) queued: the
  ASO paper §4 now names the **USZ (Zurich)** and **NCC (Japan)** groups as recipients, with the
  delivery-directed ask for their EMC lines' surface immunophenotype/RNA-seq (preprint-stage outreach).
  Status: **actioned.**

- **[2026-07-03] Delivery watch split into predictor + technology/candidate (trimcrae ask).** The
  ASO route's dominant gate is tumour delivery. The watch now has **two** delivery rows/topics: (1)
  an in-silico delivery *predictor* (makes the AOC/siRNA design computationally testable), and (2) a
  delivery *technology/candidate* — an AOC, tumour-penetrating peptide, or ligand-targeted LNP for
  non-hepatic solid tumours, or a **characterised EMC-enriched surface antigen** (the AOC's targeting
  arm). Row (2) is the one most likely to actually move the route, because the real bottleneck is the
  absence of a delivery *route*, not the absence of a *simulator*. Status: **watching** (no hits yet).
  Companion GPU-experiment to-do (RNase-H1 cleavage-discrimination MD) is tracked in the ASO paper §9
  and IDEAS.md — that firms up *specificity*; it does **not** touch delivery.

- **[2026-06-26] ASO-paper next-step gates added to the watch.** The fusion-junction ASO paper
  now has its own watched capabilities (three new literature topics in `scripts/method-watch.mjs`
  + trigger-table rows above): (1) ASO off-target / RNase-H cleavage prediction → retire the
  §3a-quater gap-mismatch heuristic; (2) ASO/siRNA efficacy & accessibility prediction → re-rank
  designs and replace the §3a-bis(iii) local-fold proxy; (3) patient-derived EMC / FET-fusion-sarcoma
  models → unblock the §4 decisive experiment. Status: **watching** (no hits triaged yet — re-check on
  the next monthly digest). Delivery (the route's dominant gate) was already watched.

- **[2026-06-24] AF3-class ternary modelling is now usable** (tool watch: AlphaFold3 v3.0.3,
  Boltz v2.2.1, Protenix v2.0.0; + a wave of fresh PROTAC-degrader papers). This crosses the
  *"open AF3-class ternary-complex prediction"* trigger → **model the NR4A3–PROTAC–E3 ternary
  complex** (degradability geometry / accessible-lysine check) with Boltz/Protenix. Status:
  ✅ **FIRED AND GRADED — it is no longer waiting for anything.** `gpu-ternary-aws.yml` has 21 runs
  and completed `success` on 2026-07-11 (×2) and 2026-07-24; `gpu-ternary-fep-vast.yml` was still
  succeeding 2026-08-05. A warhead SMILES exists (rung `5b-T` ran from a recorded degrader SMILES).
  ⛔ **And the result is a graded NEGATIVE, which is the part a "waiting" status hides:** `V12` sits in
  `RT-DEGRADER`'s `disclosed_failing` set (target↔E3 DockQ 0.023–0.046, fnat 0.000), and rung `5b-T`'s
  pre-registered three-arm gate returns **`NO-GO`** — deepened 2026-08-05 by the `V1` read over all 16
  models per arm, which finds zero sequence-encoded discriminating contacts in zero of them.
  One home for the state: [nr4a3-program-map.md](./manuscripts/nr4a3-program-map.md).
  ⚠ *Superseded, retained: "pipeline BUILT, awaiting GPU … Runs the moment AWS GPU access lands; the
  real ternary completes when a warhead SMILES exists." All three conditions were met weeks ago; the
  row went on reading as a queued item while the work it describes had run and failed.*
  Built from `nr4a3_ternary.py` (CPU prep + CRBN+lenalidomide positive control) +
  `nr4a3_ternary_sagemaker.py` + `boltz_src/entry.py` + `gpu-ternary-aws.yml`. See degrader spec point 3.
- **[2026-06-24] Degrader precedent in a sibling FET-fusion sarcoma — VERIFY BEFORE CITING.**
  Digest title only: *"Discovery and characterization of YSA64, a RBM39 degrader with in vivo
  efficacy and potent cellular activity in pediatric Ewing sarcoma A673"* (Europe PMC MED/42085934,
  2026-05). Relevance: shows degrader-modality efficacy in an EWS-fusion sarcoma — **but it targets
  the RBM39 dependency, not the fusion itself**, so it supports *"degraders deliver in FET-fusion
  sarcoma"*, NOT *"the fusion was degraded."* Action: fetch + read (CI `fetch-literature.yml`),
  confirm claims, then cite in the degrader spec/roadmap with that precise framing. Status: **open,
  unverified** (do not assert in a manuscript until read).
- **[2026-06-24] Virtual-cell target discovery warming up** — *"Discovery of candidate therapeutic
  targets with Geneformer"* (MED/42026145, 2026-04). Not yet a held-out-knockdown predictor, but the
  capability behind the EMC fusion-dependence trigger is maturing; keep watching. Status: **watch**.

## Open-source landscape snapshot (2026-07-13, web scan)

The state-of-the-art we can actually RUN (closed IsoDDE / "AlphaFold 4" is inaccessible, so it does not
count). Captured so a future session doesn't re-derive it; the weekly newsletter keeps it current.
- **Co-fold / structure (generation):** **Boltz-2** (MIT, open, affinity head — we already use it);
  **Protenix** (ByteDance, **v2.0.0, 2026-04-07**, **Apache-2.0**, claims >AF3 — benchmark vs Boltz);
  ⚠ *Superseded, retained: "v1 Feb 2026". This sits in the section that claims to be KEPT CURRENT, and an
  earlier dated entry above already said v2.0.0 — so the later-dated snapshot named the older version.*
  **Chai-1** (drug-opt, semi-open); **OpenFold3** (fully-open AF3 reimpl).
- **Ternary / degrader (generation):** **DeepTernary** (open GNN, SOTA ternary structure — evaluate as a
  generation axis); **FKSFold** (glue-ternary diffusion). Both predict *structure*, not cooperativity ranking.
- **Binary affinity / FEP (warhead):** **OpenFE** (MIT RBFE, ~commercial accuracy, 1700+ ligands — we use it);
  **FEP-SPell-ABFE** (open ABFE); ML+active-learning-FEP for cost.
- **Honest gap vs closed IsoDDE:** no OPEN model yet gives FEP-level affinity *without* a starting
  structure; Boltz-2's affinity head is the closest open analog but not validated to that bar. And nothing
  open solves *ternary cooperativity/selectivity ranking* — the crux the NR-V04 control gates.

## 🔄 Auto-captured (weekly field-scan)

Appended automatically by the weekly field-scan Routine (and manual scans). Items here are NEW methods/tools/
triggers not yet integrated into the curated sections above — review + fold in. Dated + sourced; no fabrication.

- **2026-07-13 — Ternary/glue cooperativity FEP prior art (Track B benchmark set).** JCTC `5c00736`
  (induced-PPI + cooperative-solvation decomposition, pathway-independent) and JCTC `5c00064` (glue
  cooperativity vs experiment). Direct prior art our ΔG_coop method must cite + benchmark against.
  https://pubs.acs.org/doi/10.1021/acs.jctc.5c00736 · https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12159975/
- **2026-07-13 — IntFold (arXiv 2507.02025).** Controllable co-folding foundation model — add to the
  breadth-first architecture-proposal generator list (alongside Boltz-2, Protenix, DeepTernary); never a ranker.
  https://arxiv.org/pdf/2507.02025
- **2026-07-13 — Boltz 2.1 is closed-source but API-ACCESSIBLE.** Not ruled out: usable via the Boltz-hosted
  API (inference-only). Open Boltz-1/-2 suffice for our co-fold role; recommend the 2.1 API (not self-hosting)
  only if a fast affinity pre-filter is ever wanted — physics stays the ranker. https://rowansci.com/tools/boltz-2
- **2026-07-13 — Independent Boltz-2 reliability eval (arXiv 2603.05532).** Strong binary classifier, weak
  quantitative ranking — reinforces "generator scores never enter S_d." https://arxiv.org/html/2603.05532v1
- **2026-08-19 — OpenMM 8.6.0: native `ReplicaExchangeSampler` + `ExpandedEnsembleSampler`.** New multistate-
  sampling primitives usable to accelerate/validate the warhead RBFE and physics-ensemble ΔG_coop legs — a new
  axis of evidence per the breadth-first rule (§CLAUDE.md), not a depth-past-standard add. Evaluate before the
  next sampling campaign. https://github.com/openmm/openmm/releases/tag/8.6.0
- **2026-08-24 (dated ~2026, exact issue date unverified) — Riepenhausen et al., "AI-Based Prediction of
  PROTAC- and Molecular Glue-Mediated Ternary Complexes: A Comparative Evaluation of AlphaFold 3 and Boltz-2,"
  Archiv der Pharmazie, e70225.** Head-to-head benchmark of AF3 vs Boltz-2 on 40 resolved ternary complexes (25
  PROTAC + 15 glue) — directly informs which co-fold engine to trust for our ternary GENERATION step; read
  before the next ternary rebuild. https://onlinelibrary.wiley.com/doi/10.1002/ardp.70225
- **2026-08-11 — DegradeQuery (arXiv 2608.10595).** Counterfactual-tuple pretraining that exploits unlabeled
  molecule–target–E3 records in PROTAC databases for degradation-activity prediction (AUROC 0.907 / accuracy
  0.85 on PROTAC-8K). A candidate weak prioritization signal only — same guardrail as DeepTernary/FKSFold:
  generator/predictor scores never enter `S_d`, physics stays the ranker. https://arxiv.org/abs/2608.10595
- **2026-08-05 — DCAF11-dependent molecular glue activated by glutathionylation (Nature, Dana-Farber).**
  First-in-kind *metabolically activated* molecular glue (prodrug M12, turned "on" by GST-mediated
  glutathionylation in oxidative-stress-high cancer cells), discovered via a new systematic degrader-discovery
  platform that broadens usable E3 ligases beyond CRBN/VHL. New axis: conditional/context-dependent degrader
  activation + a non-CRBN/VHL E3 discovery route — worth a look if the DCAF11 handle is ever relevant to a
  paralogue-selectivity design. https://www.nature.com/articles/s41586-026-10873-1 ·
  https://www.dana-farber.org/newsroom/news-releases/2026/dana-farber-investigators-develop-protein-degrader-discovery-platform-and-find-first-in-kind-metabolically-activated-molecular-glue-degrader
- **2026-08-12/2026-08-01 — Two stack releases landed, specifics UNKNOWN (egress-blocked from docs sites this
  scan; follow up via CI escape hatch before relying on either for a numeric change): OpenFF toolkit 0.19.0**
  (https://github.com/openforcefield/openff-toolkit/releases/tag/0.19.0) **and RDKit 2026.03.5**
  (https://github.com/rdkit/rdkit/releases/tag/Release_2026.03.5, a patch on 2026.03.4). OpenFE, gufe,
  openmmtools, Kartograf and LOMAP2 had no new release in this window (last: OpenFE v1.12.0 2026-07-01, gufe
  v1.12.0 2026-06-23, openmmtools v0.26.0 2026-01-07, Kartograf v2.0.0 2026-06-23, LOMAP2 v3.3.0 2026-06-15) —
  all just outside or already inside the prior baseline. No new open-weight Boltz release (still v2.2.1,
  2025-09-08); Boltz 2.1 stays closed/API-only, already-tracked. No new DeepTernary or FKSFold release found.
- **2026-08-24 — Frontier-model access re-confirmed, no restriction, no supersession.** Claude Opus 5
  (released 2026-07-24) remains the current top generally-available tier for this bio work: same ASL-3
  protections as Opus 4.8, CB-1 (non-novel weapons synthesis) not CB-2, and blocked Fable-5 biology requests
  route to Opus 5 rather than being refused — matches the 2026-08-24 CLAUDE.md correction. No newer/more-
  capable model found since 2026-07-13 that out-measures Opus 5 for scientific/biology reasoning (xAI Grok 4.6
  and Alibaba Qwen3.5-Max shipped in-window with no head-to-head showing them ahead; treat as UNKNOWN, not
  inferior). https://www.anthropic.com/news/claude-opus-5
- **2026-08-28 — RDKit 2026.03.6 (released today).** Adds a "synthon space shape search" feature, a BertzCT
  descriptor speed-up (no value change, safely re-runnable) and bug fixes (numpy dtype handling, Boost 1.92
  build compat). No default-affecting change to numbers we've already produced; the shape-search feature is a
  candidate to evaluate for de-novo/warhead-pool work. https://github.com/rdkit/rdkit/releases/tag/Release_2026_03_6
- **2026-08-24 — VERAXA/Secarna AOC alliance: positive in-vitro proof-of-concept.** A conjugated
  oligonucleotide candidate showed greater potency than the naked oligo, reported as validating VERAXA's
  click-chemistry conjugation platform (platform's stated primary focus is solid tumors, though this specific
  readout is an immunology indication). A second AOC delivery-TECHNOLOGY data point alongside TAC-001 for the
  fusion-junction ASO route's dominant delivery gate — not EMC-specific, and not yet a candidate named for our
  route. https://www.biospace.com/press-releases/veraxa-biotech-and-secarna-pharmaceuticals-achieve-research-milestone-in-antibody-oligonucleotide-conjugate-aoc-alliance
- **2026-09-01 — Claude Fable 5.1 / Claude Mythos 5.1 released — the first model found to out-measure Opus 5
  on this program's frontier-model watch since the 2026-08-24 CLAUDE.md correction retired the "restricted"
  framing.** Fable 5.1 "finishes ahead of Opus 5 on every category Anthropic published," including roughly
  doubling the agentic-scientific-research benchmark Terminal-Bench-Science 0.1 (52.6% vs Fable 5's 24.7%);
  biology safeguards fire ~85% less often on benign medical/biology questions, which matters for a program
  that has previously hit refusals on legitimate bio-research prompts. **Mythos 5.1** is the same model with
  lighter safeguards, gated to vetted organizations via a new Life Sciences Verification Program (US-only,
  currently not a lane this program has access to) — Fable 5.1 itself is the generally-available tier this
  row is actually about. ⚠ **UNKNOWN, and directly actionable: whether these research sessions are already
  running on Fable 5.1 or still on the Opus-5 fallback** — check `/status` before assuming either way; if not
  yet on it, this is a free capability upgrade for every future research session, not a hypothetical.
  https://www.anthropic.com/claude/fable
