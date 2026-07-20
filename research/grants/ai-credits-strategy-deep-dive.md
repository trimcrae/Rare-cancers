# Deep dive: what $50k of Claude credits would change about how we attack EMC

**Context:** Anthropic AI for Science rare-disease grant = **up to $50,000 in Claude credits** (Opus /
biology-approved models), 6 months, use-it-or-lose-it. This document works out what that actually unlocks,
how it should change *where* we attack, and the concrete 6-month plan. It is the reasoning behind the
strengthened scope in
[anthropic-rare-disease-grant-application.md](./anthropic-rare-disease-grant-application.md).

> Status: living draft. Empirical repurposing grounding (§4) is being filled from a repo-mine + fresh
> literature pass; anything not yet cited is flagged as a hypothesis, not a claim.

---

## 1. TL;DR

- We have been optimizing under **two** constraints but only ever *naming* one. Named: **GPU dollars are
  scarce**, so we ration them. Unnamed: **LLM throughput is rate-limited** on the Max plan, so we serialized
  and hand-curated the LLM-heavy work and stopped seeing it as a constraint at all.
- $50k of Opus credits dissolves the *second* constraint. The non-obvious point: **the highest-leverage use of
  abundant LLM is to make the scarce GPU count** — a rich in-silico triage/verification layer means fewer
  wasted GPU runs, so the credits attack the GPU bottleneck *indirectly*.
- It also changes our **comparative advantage**. A solo, unaffiliated researcher will never out-FEP a pharma
  team. But with abundant LLM we can be the single most comprehensive, continuously-verified
  **reasoning-and-triage engine** over rare-cancer biology — LLM-bound work no individual lab is staffed to do
  and large groups are too siloed to attempt.
- **Honesty correction (2026-07-20, after a repo audit):** repurposing is **not** an unconsidered angle here.
  The repo already has a scored 14-candidate repurposing menu (`research/manuscripts/repurposing-hypotheses.md`),
  DepMap dependency analyses, a TxGNN graph-foundation-model run (which *failed* — clinically implausible
  picks), and a parked 5,988-compound docking screen — and it **deliberately demoted** repurposing to
  "most-ready but generic / evidence-synthesis-not-discovery" after finding an **evidence–novelty
  anti-correlation** (the only EMC-clinically-evidenced drug, imatinib, is non-novel and helps ~4%; every
  *novel* candidate is preclinical-only; the "novel × clinical" cell is empty). So the credits do **not** buy
  "discover a repurposing hit nobody thought of."
- What the credits *actually* buy is regime-change on the **LLM-bound layer** the repo's own discipline
  demands but can't scale by hand: **(W1)** *complete, verify, and add the missing axes to* the existing
  repurposing/mechanism track (finish the parked screens' interpretation, add the absent
  **connectivity-map/LINCS** axis, resolve flagged-open mechanistic questions like the PPARγ agonist-vs-
  antagonist direction, close primary-citation gaps); **(W2)** a **GPU-triage** reasoning layer (buys back GPU
  dollars); **(W3)** a continuous **adversarial-verification** engine (scales the repo's red-team + `zero
  unresolved claims` rule to the whole corpus) — plus three natural fits for the grant's stated examples:
  **(W4)** a definitive **natural-history** meta-analysis, **(W5)** **patient-hub** scale-out, **(W6)** a
  **rare-disease reasoning eval**.

## 2. The two-constraint reframe

Our whole operating regime (see `CLAUDE.md`, `research/manuscripts/emc-treatment-strategy.md`) was built around
two facts:

| Constraint | How we adapted | Is it real? |
|---|---|---|
| **GPU/AWS dollars are scarce** (each FEP/ABFE/ternary run costs real $, gated at >$50) | Spend-gated ladder, pilot-one-leg-first, cheapest-decisive-first ordering | Yes — named and managed |
| **LLM throughput is rate-limited** (Max flat-rate; "engineering is free" but *bandwidth* is not) | Serial red-teams, hand-curated atlas, one careful synthesis pass at a time, single-threaded agent work | Yes — but **never named**, so never optimized against |

The second constraint is invisible precisely because we adapted so well: every workflow assumes LLM work is
done a little at a time by hand or by one agent. $50k of credits is ~a **step-change in parallel LLM
throughput** for 6 months — enough to run large multi-agent fan-outs (the `Workflow` pattern: dozens of agents)
more or less continuously. The question "what haven't we considered because we lacked LLM bandwidth?" has a
real answer: **anything requiring massive parallel agent orchestration** — which we have implicitly rationed to
near-zero.

## 3. Capacity: what $50k of Opus actually buys

Order-of-magnitude, hedged (Opus-tier pricing ≈ $15/M input, $75/M output; prompt-caching can cut cached input
~10×; agent workloads are input-heavy with moderate output → effective blended ≈ $10–25 per M tokens):

- **≈ 0.7 – 3 billion tokens** over the grant period.
- Illustratively: enough to **read and structure every paper that has ever touched EMC / NR4A / EWS-fusion
  biology several times over** and still have most of the budget left; **or** run **thousands** of
  medium fan-out `Workflow` runs (each a few M tokens across a dozen agents); **or** keep a continuous
  verification + curation pipeline live for the full 6 months.

The exact number matters less than the regime change: LLM work stops being something we do sparingly and
becomes something we do **exhaustively and in parallel**. That is the whole ballgame.

## 4. The repurposing thesis (W1) — empirical grounding

*(All external citations below are snippet-verified from a literature pass; the egress proxy blocked full-text
fetch, so every quantitative claim is flagged for full-text re-verification before it enters any outward-facing
document. Repo facts are cited to their files.)*

### 4a. What is already established (do NOT re-pitch as new)

- **EMC already has an active repurposing track in this repo**, deliberately demoted: a scored 14-candidate
  menu (`research/manuscripts/repurposing-hypotheses.md`), DepMap dependency analyses, a TxGNN
  graph-foundation-model run that **failed** (EMC's actually-active drugs ranked bottom-quartile), and a
  parked 5,988-compound docking screen (`research/modalities/nr4a3-repurpose-*`). The repo's own verdict: an
  **evidence–novelty anti-correlation** — the "novel × clinically-evidenced" cell is empty — so repurposing is
  "most-ready but generic / evidence-synthesis-not-discovery," and the NR4A3 degrader is deliberately the
  flagship. The BRD9/ncBAF synthetic-lethal shortcut was **downgraded** by a DepMap transfer prior
  (`research/manuscripts/degrader-vs-synthetic-lethal.md`). *We must not re-litigate these.*
- **EMC does have a real near-term clinical reality — antiangiogenic TKIs** — the strongest clinical signal in
  the disease, unusual for a sarcoma: **pazopanib** prospective phase 2 (PR ~18%, SD ~73%; *Lancet Oncol*
  2019, PMID ~31331699 — verify); **sunitinib** series (6/10 PR; *Ann Oncol* 2014, PMID 24703573), with a
  hypothesis-generating **EWSR1-fusion-only** response signal; **sunitinib + nivolumab** IMMUNOSARC II
  prospective phase 2 (PR 9%, SD 82%; *J Clin Oncol* 2025;43:11513). EMC is otherwise relatively
  chemo-resistant (modest anthracycline activity; *Clin Sarcoma Res* 2013, PMID 24345066). So the program does
  **not** "lack a near-term angle" — the honest gap is a *novel, mechanism-anchored* one.

### 4b. The fusion's druggable nodes — with evidence class (the honesty axis)

The central integrity problem in existing EMC "precision-oncology" reports is **expression-without-alteration**
hooks over-called as targets. Grading is the value-add:

| Node | Evidence class | Repurposing hook | Confidence |
|---|---|---|---|
| **PPARG** — directly transactivated via a promoter response element; overexpressed in fusion+ EMC (PMC4429309; repo `nr4a3-emc-biology-evidence.md`) | **Promoter-level fusion target** (strongest) | Approved **glitazones** (pioglitazone/rosiglitazone) — but **agonize-vs-antagonize direction UNRESOLVED** | Med (biology solid; direction untested) |
| **VEGFR/Notch program** — upregulated in pazopanib-sensitive tumors | Transcriptomic within trial | Approved **pazopanib/sunitinib**; possible Notch/γ-secretase combos | Med-High |
| **SGK1 / NDRG2** — upregulated (Tumor Biol 2012) | Expression | SGK1 inhibitors **preclinical only** | Med / Low-Med |
| **RET, KIT, NTRK2/3** | **Expression only** (no activating alteration, apart from n=1 KIT-mutant imatinib responder) | Approved RET/KIT/TRK inhibitors — but rationale is weak absent an alteration | **Low — must be labeled as expression-only** |
| IGF1R / integrated-stress-response | **No primary EMC evidence found** | — | Do **not** assert |

### 4c. The genuinely open, bandwidth-gated additions (this is what the credits buy)

1. **A signature-reversal (CMap/LINCS) repurposing analysis has never been published for EMC** — and the input
   transcriptomic datasets already exist (Oncotarget 2017 PMID 28423517; Front Oncol 2020 PMID 32612944;
   Brenca *J Pathol* 2019 PMID 31020999, incl. GEO series). Connecting EMC (and **fusion-subtype**) signatures
   to perturbation libraries is a clean, self-executable, novel contribution. *(Snippet-level absence —
   confirm "first-ever" against full text before claiming it.)*
2. **Subtype-stratified repurposing (EWSR1 vs TAF15 vs TCF12/PGR).** The axon-guidance/semaphorin switch
   between EWSR1- and TAF15-fusion tumors + the sunitinib EWSR1-only signal imply fusion-partner-specific drug
   matching — **no repurposing effort has stratified by variant.**
3. **Direction-of-effect resolution on the PPARG hook** — a testable hypothesis around an *approved* drug
   class, currently unresolved.
4. **Adversarial evidence-class verification** — separating promoter-level fusion targets from expression-only
   hooks (RET/KIT/NTRK) — produces a more honest, fundable target list than the anecdote-driven precision
   reports that concluded most EMC variants were "of unknown significance." *This is the distinguishing
   feature*, and it is exactly what abundant, parallel, adversarial LLM throughput does well.

So W1 is **not** "discover a repurposing hit." It is: *complete and honestly re-grade the existing track, add
the missing CMap/LINCS + subtype axes, resolve the PPARG direction, and verify every hook's evidence class* —
terminating in a decision-ready, cited, subtype-stratified target/repurposing map. Only its top structural
questions (e.g. is the parked dock screen worth finishing?) get handed to the GPU-triage layer (W2). This is
the artifact the grant's first example project ("propose and rank mechanistic links… that share a
gene/pathway") describes.

## 5. The full workstream portfolio

Each item: what it is · why it was bandwidth-gated · deliverable · how it couples to GPU · grant fit.

### W1 — Complete + re-grade the repurposing/mechanism track, add the missing axes
- **Not** "discover a hit" — the repo already did and demoted repurposing (§4a). This is: finish the parked
  screens' *interpretation*, **add the never-published CMap/LINCS signature-reversal axis** and the
  **fusion-subtype (EWSR1 vs TAF15) stratification**, resolve the **PPARG direction**, and **verify every
  hook's evidence class** (promoter-level target vs expression-only).
- **Bandwidth-gated because:** exhaustive, adversarial, evidence-class-graded reasoning over
  mechanism × drug-universe × subtype is a huge parallel reasoning job no solo human completes by hand.
- **Deliverable:** a cited, subtype-stratified, evidence-graded target/repurposing map for EMC (public);
  a decision on the parked dock screen.
- **GPU coupling:** only the top *structural* questions go to W2.
- **Grant fit:** direct hit on example #1 (mechanistic links across a shared gene/pathway).

### W2 — GPU-triage reasoning layer
- **What:** before any FEP / ternary / ABFE spend, an adversarial agent panel scores what deserves GPU and
  predicts likely-failure modes (bad conformer, futile paralogue, strained linker).
- **Bandwidth-gated because:** doing this *well* means many independent reasoning passes per candidate — we
  currently eyeball it.
- **Deliverable:** a triage rubric + per-candidate go/no-go memos that gate the spend ladder in `STRATEGY.md`.
- **GPU coupling:** *this is the buy-back* — fewer wasted runs ⇒ the real (GPU) budget stretches further.
- **Grant fit:** indirect, but it's what makes the whole program efficient.

### W3 — Continuous adversarial-verification engine
- **What:** every claim in every manuscript continuously attacked by independent agent panels; citation flags
  flipped only when a claim survives.
- **Bandwidth-gated because:** we red-team by hand, serially — it doesn't scale to the whole corpus.
- **Deliverable:** a living verification pass over all manuscripts; a public integrity log.
- **GPU coupling:** none directly; it's the guardrail that keeps W1/W4 honest at volume (see §7 risks).
- **Grant fit:** supports the eval example (#3) and the program's credibility.

### W4 — Definitive EMC natural-history meta-analysis
- **What:** exhaustively find, extract, reconcile-for-cohort-overlap, and pool every published EMC cohort
  (and 1–2 adjacent rare sarcomas) using the repo's fixed method (denominator-weighted proportions + Wilson
  95% CIs, non-overlapping cohorts only; see `METHODOLOGY.md`).
- **Bandwidth-gated because:** it's pure extraction/reconciliation drudgery across scattered papers.
- **Deliverable:** an updated, fully-cited natural-history resource + the patient-facing hub data.
- **Grant fit:** direct hit on example #2 (curate patient-org data → improve natural-history studies).

### W5 — Patient-hub scale-out
- **What:** extend the shelved zero-dependency rare-cancer info site from EMC to dozens/hundreds of rare
  cancers, each rigorously cited.
- **Bandwidth-gated because:** each page is a real cited-curation job; one at a time by hand is the current
  rate.
- **Deliverable:** a public-good natural-history resource at scale.
- **Grant fit:** direct public-good match to the program's intent.

### W6 — Rare-disease reasoning eval
- **What:** an open eval measuring model performance on rare-disease tasks — mechanism recall,
  citation-grounded synthesis, natural-history estimation, refusal-of-fabrication under our medical-integrity
  standard.
- **Bandwidth-gated because:** building + running an eval at scale is itself LLM-heavy.
- **Deliverable:** open eval + leaderboard-style report; internally, it tells us *when to trust the model's*
  biology/chemistry reasoning (which is what makes W1–W3 defensible).
- **Grant fit:** direct hit on example #3 (build evals for rare-disease tasks).

## 6. How it changes allocation

| | Today | With credits |
|---|---|---|
| Primary lane | ~70–80% GPU-degrader / method-dev | Degrader **stays** the long-horizon flagship, but is now **fed and gated by** the LLM engine |
| LLM work | Rationed, serial, hand-curated | Exhaustive, parallel, continuously verified |
| Patient-facing timeline | Long-horizon only (degrader → wet lab someday) | **Adds a near-term angle** via repurposing (W1) |
| GPU efficiency | Eyeballed triage | Adversarial triage (W2) — every run pre-justified |
| Rigor | Hand red-teams | Continuous corpus-wide verification (W3) |
| Public good | Atlas + one hub page | Natural-history meta-analysis (W4) + hub scale-out (W5) + open eval (W6) |

The degrader program is **not** demoted; its *dependency structure* changes — it becomes the downstream
confirmation arm of an LLM-driven hypothesis-and-triage engine, instead of the thing the whole solo effort
waits on.

## 7. Risks & guardrails (must be designed in, not bolted on)

- **Volume × hallucination.** More generation without proportional verification just manufactures more
  unverified claims — a direct violation of the repo's medical-integrity rule. **Mitigation:** a large share
  of the bandwidth goes into **W3 (verification)**, not generation; nothing clinical enters a manuscript or
  the hub without surviving an adversarial pass + citation.
- **Use-it-or-lose-it, 6 months, Opus-only.** The credits cannot rescue slow, GPU-gated timelines. **Design
  the plan around what the credits can actually spend** — high-throughput LLM work — not around GPU-bound
  deliverables.
- **Hypothesis backlog.** Generating 500 GPU-worthy ideas we can't afford to test is a failure mode.
  **Mitigation:** every LLM workstream must terminate in a **decision-ready, GPU-free-or-GPU-cheap
  conclusion**; W1's output is a *shortlist*, not a wish-list.
- **Scope drift on "rare genetic disease."** EMC is a rare *cancer* with a genetic fusion driver — lead with
  the mechanism/pathway and natural-history framing that maps cleanly onto the grant's examples.

## 8. 6-month sequencing (mapped to credit spend)

1. **Weeks 1–3 — stand up W3 (verification engine) first.** Rigor infrastructure before volume, so everything
   downstream is trustworthy at scale.
2. **Weeks 2–8 — W1 repurposing screen + W2 triage layer** (run together; W2 gates any GPU follow-up from W1).
3. **Weeks 6–14 — W4 natural-history meta-analysis** (extraction-heavy; overlaps W1).
4. **Weeks 10–20 — W5 hub scale-out** (uses W4's curated data).
5. **Weeks 12–24 — W6 eval** build + release; continuous W3 throughout.
6. **Throughout — public outputs:** preprint(s), open data, open eval; outreach to NR4A / nuclear-receptor
   labs, sarcoma/EMC foundations, and patient organizations.

## 9. Open decisions for trimcrae

- **Is the repurposing angle (W1) worth making the flagship of the credit spend?** It adds a near-term,
  patient-facing direction the program currently lacks — but it *is* a genuine shift in where we attack.
- **Application framing:** lead with W1+W4 (mechanistic links + natural history, cleanest grant fit) and carry
  W2/W3/W6 as method/infrastructure — or foreground the eval (W6)?
- **Submission** (outward-facing) stays a trimcrae decision; everything up to it is prepared.
