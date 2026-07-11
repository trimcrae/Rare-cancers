# EMC atlas — outreach: strategy, send-ready emails, and runbook (unaffiliated-researcher edition)

> **For Tristan D. McRae, independent researcher.** Being unaffiliated with no existing collaborator
> lowers cold-email response rates — so the plan below does not rely on credentials. It relies on the
> **artifact carrying the legitimacy**: a public, citable, provenance-checked resource, a *graduated*
> (low-commitment-first) ask, and starting with the audiences most receptive to independent researchers.
> Send under your own name; nothing here is sent automatically or impersonates anyone.

## How being unaffiliated changes the plan (the honest version)

1. **The credential is the work, made citable.** The single highest-leverage move is to publish the
   atlas as a **citable preprint / dataset with a DOI** *before* the direct asks. The repo is already
   wired for this (`.zenodo.json`, `CITATION.cff` → a GitHub release mints a Zenodo DOI). Then you email
   as "author of [DOI], which builds on your work," not as an unknown. Also get a free **ORCID**
   (orcid.org, ~5 min) — a real identity signal for independents.
2. **Lead with value, ask small first (graduated ask).** Do **not** open with "run my 12-compound
   panel" (high commitment to a stranger). Open with the resource + a flattering, near-zero-commitment
   ask ("I built on your models/data; did I represent them correctly? / I'd value your view"). That gets
   a reply and starts a relationship; the concrete collaboration is offered only once they engage.
3. **Start with the most receptive audiences, not the busiest PI.** Patient foundations and
   patient-partnered model/tissue networks actively *want* engaged researchers and are far more
   responsive to independents than a senior clinical PI's inbox — and they can broker the introductions
   and the academic co-author that most raise your legitimacy. Run that track in parallel from day one.
4. **Recruit ONE academic co-author/sponsor — the biggest single multiplier.** One willing named
   collaborator converts every subsequent email from "unaffiliated stranger" to "the team that built
   [DOI]." Realistic routes: (a) a foundation introduction; (b) engagement on the posted preprint; (c) a
   more accessible mid-career or computational sarcoma researcher who values a ready-made rigorous
   package. Treat this as a first-class goal, not an afterthought.
5. **Expect a numbers game.** Even done well, unaffiliated cold-email reply rates are low (often single
   digits). The DOI + soft framing + foundation route materially improve it, but plan for volume,
   patience, and one polite follow-up — not a single perfect email.

**Net effect on sequence:** (0) post the DOI'd atlas + get an ORCID → (1) foundations / model-and-data
networks + co-author hunt, in parallel → (2) soft-entry emails to the model owners and the clinical
group → (3) escalate to the concrete validation/re-analysis offer only with those who engage.

---

## Recipients (real, verified) and how to reach each

| # | Recipient | Why | Contact route (copy the exact email from the source) | Program |
|---|---|---|---|---|
| 1 | **Dr. Chantal Pauli** — Pathology & Molecular Pathology, University Hospital Zurich (USZ) | Built the two USZ EMC models (USZ20-EMC1 EWSR1, USZ22-EMC2 TAF15) | **chantal.pauli@usz.ch** (corresponding author, Bangerter 2023, PMC9813045) | 1 — proteostasis panel |
| 2 | **Dr. Tadashi Kondo** — Division of Rare Cancer Research, National Cancer Center Research Institute, Tokyo | Built NCC-EMC1-C1; ran the 221-drug screen | Corresponding author, Iwata 2025 (PMID 40580361) — copy exact email from the paper; lab: ncc.go.jp/en/ri/division/rare_cancer_research/member/kondo.html | 1 — proteostasis panel |
| 3 | **Dr. Silvia Stacchiotti** — Adult Mesenchymal & Rare Tumor Unit, Fondazione IRCCS Istituto Nazionale dei Tumori, Milan | Led essentially all EMC systemic-therapy evidence + the EWSR1-vs-TAF15 differential | Corresponding author, Stacchiotti 2019 (Lancet Oncol, PMID 31331701) — copy exact email from the paper | 2 — antiangiogenic biomarker + cohort |

**Most-receptive first track (start here):**
- **Rare Cancer Research Foundation (RCRF)** — rarecancer.org (+ its External Cancer Model Resources page;
  CancerModels.org) — **the strongest foundation lead: RCRF actually *generates* patient-derived cell-line
  models from donated tumors**, which is exactly what EMC lacks. Natural partner to connect the atlas to
  model generation + tissue, and to broker introductions. Contact via the site.
- **Count Me In** — joincountmein.org (Broad/Dana-Farber) — patient-partnered data/samples with rare-cancer/
  sarcoma projects; a route to patient-contributed EMC data and a receptive community.
- **Sarcoma Foundation of America (SFA)** — curesarcoma.org; tel (301) 253-8687; grants via proposalCENTRAL
  (~$75k/yr). **Eligibility note: SFA grants require an MD/DO/PhD (or intl. equivalent) as PI** — so for an
  unaffiliated non-PhD applicant this is a **"route via a collaborator who applies,"** not a direct grant;
  still a legitimate network/introducer.
- **Structural Genomics Consortium (SGC)** (thesgc.org): for the long-horizon NR4A3-ligand/direct-fusion route (open chemical-biology collaboration).

---

## Emails (Tristan's name filled; only the DOI/repo link `[LINK]` remains once you cut the release)

### Email A1 → Rare Cancer Research Foundation (send FIRST — the model-generation lead)

> **To:** `[contact route via rarecancer.org]`
> **Subject:** Open EMC drug atlas + the model gap — can we connect it to your model-generation program?
>
> Dear RCRF team,
>
> I'm Tristan McRae, an independent researcher. I've openly released the **EMC Open Target & Drug Atlas**
> (`[DOI/LINK]`) — a reproducible, provenance-checked integration of every usable extraskeletal myxoid
> chondrosarcoma (EMC) dataset, model, drug screen, and clinical cohort, with a transparent evidence
> score and a wet-lab-ready validation package, all from public data.
>
> EMC's single biggest bottleneck is models and tissue — exactly what RCRF generates. I'd love to explore
> two things: (a) connecting the atlas's validation package to your patient-derived-model program so any
> EMC tumor donations become high-value functional experiments, and (b) an introduction to the EMC
> model-owning labs and, ideally, a clinician/scientist collaborator. Could we set up a short call?
>
> With gratitude for what RCRF does,
> Tristan McRae · `[email]` · `[DOI/LINK]`

### Email A2 → Sarcoma Foundation of America (network + collaborator route)

> **To:** `[contact via curesarcoma.org; tel (301) 253-8687]`
> **Subject:** Open EMC evidence atlas from an independent researcher — seeking a sarcoma-research connection
>
> Dear SFA team,
>
> I'm Tristan McRae, an independent researcher. I've openly released the **EMC Open Target & Drug Atlas**
> (`[DOI/LINK]`), a public, citable resource that turns the scattered EMC evidence into a ranked,
> wet-lab-ready program for this ultra-rare sarcoma.
>
> I understand SFA research grants require an MD/DO/PhD PI, so I'm not writing to apply directly — rather,
> as an unaffiliated researcher, I'm looking to connect with a sarcoma investigator in your network who
> might partner on it (and could carry a grant), and to make the resource available to your research
> community. Might you be able to point me to the right people?
>
> Thank you for your work in sarcoma,
> Tristan McRae · `[email]` · `[DOI/LINK]`

### Email B → Dr. Pauli (soft entry; USZ models)

> **To:** chantal.pauli@usz.ch
> **Subject:** Built an open EMC atlas on your USZ models — did I represent them correctly?
>
> Dear Dr. Pauli,
>
> I'm Tristan McRae, an independent researcher. I've openly released an **EMC Open Target & Drug Atlas**
> (`[DOI/LINK]`) that integrates the EMC evidence base with a transparent, provenance-checked evidence
> score — and your USZ20-EMC1 and USZ22-EMC2 models are central to it. Before I take it further, I'd
> genuinely value a quick sanity check that I've represented your models and screen correctly (the
> relevant entries are in `research/atlas/`).
>
> If it's useful: the atlas's strongest preclinical signal is a **proteostasis–chromatin** vulnerability
> converging across your screen and the NCC screen, and I've designed a ready-to-run, class-vs-compound
> validation panel with pre-registered go/no-go and exposure-matched concentrations — all analysis and
> manuscript support provided, at no cost to your lab. I'd be glad to share it if you're interested.
>
> With admiration for the models you've built,
> Tristan McRae · `[email]` · `[DOI/LINK]`

### Email C → Dr. Kondo (soft entry; NCC model)

> **To:** `[copy exact email from Iwata 2025, PMID 40580361]`
> **Subject:** Open EMC atlas built on NCC-EMC1-C1 — a quick correctness check, and a possible follow-up
>
> Dear Dr. Kondo,
>
> I'm Tristan McRae, an independent researcher. I've openly released an **EMC Open Target & Drug Atlas**
> (`[DOI/LINK]`); your NCC-EMC1-C1 screen is one of its two pillars. I'd value a brief check that I've
> represented your line and screen accurately. Cross-referencing your screen with the USZ one points to a
> **proteostasis–chromatin** dependency rather than any single nominal target (e.g. your two HDAC hits;
> and public DepMap data suggest brigatinib's activity is unlikely to be ALK-dependent).
>
> If of interest, I've designed a class-vs-compound validation panel to test this rigorously and would
> provide all design and analysis. Happy to share.
>
> Respectfully,
> Tristan McRae · `[email]` · `[DOI/LINK]`

### Email D → Dr. Stacchiotti (soft entry; antiangiogenic biomarker)

> **To:** `[copy exact email from Stacchiotti 2019, PMID 31331701]`
> **Subject:** Open EMC atlas built on your trials — a growth-rate-adjusted biomarker idea
>
> Dear Dr. Stacchiotti,
>
> I'm Tristan McRae, an independent researcher. I've openly released an **EMC Open Target & Drug Atlas**
> (`[DOI/LINK]`) that integrates the EMC evidence base — much of which is your group's work. Your
> sunitinib data's EWSR1-responsive / TAF15-refractory finding is the anchor of a proposal I'd value your
> view on: a re-analysis using **growth-rate-adjusted** endpoints (growth-modulation index,
> time-to-next-treatment) to test whether that fusion-subtype signal predicts real benefit rather than
> the indolent natural history, plus a kinome comparison to nominate the next TKI.
>
> If worth pursuing, your institution would own all consent/ethics/de-identification; I would provide the
> data model, statistical plan, and analysis of a de-identified extract. I'd welcome a short conversation.
>
> With respect for your work in this disease,
> Tristan McRae · `[email]` · `[DOI/LINK]`

### Email E → Structural Genomics Consortium (secondary; long-horizon direct-fusion route)

> **To:** `[collaborate route via thesgc.org]`
> **Subject:** Orphan nuclear receptor NR4A3 as a target in EMC — an open resource + a ligandability question
>
> Dear SGC team,
>
> I'm Tristan McRae, an independent researcher. I've openly released the **EMC Open Target & Drug Atlas**
> (`[DOI/LINK]`) for extraskeletal myxoid chondrosarcoma, a sarcoma driven by an NR4A3 fusion. The
> highest-specificity (but least tractable) route is targeting the fusion directly — blocked today by the
> lack of a validated small-molecule ligand for the orphan nuclear receptor NR4A3.
>
> Given the SGC's work on chemical probes and understudied targets, I wanted to put NR4A3 on your radar
> with a fully worked-up disease rationale, and ask whether a chemical-probe / ligandability
> collaboration around NR4A3 would be of interest. All computational characterization is in the atlas.
>
> With appreciation for the open-science model you champion,
> Tristan McRae · `[email]` · `[DOI/LINK]`

---

## SEND RUNBOOK — exactly what you do next

**Step 0 — Mint the credential (do this FIRST; ~1 hr, mostly waiting). Exact steps:**
  1. **Get an ORCID (5 min).** Go to https://orcid.org → "Register now" → fill name/email → you get an ID
     like `0000-0002-1825-0097`. Copy it.
  2. **Add the ORCID to the metadata (2 min).** In the repo, edit two files and uncomment/fill the ORCID line:
     - `CITATION.cff` → under `authors:` set `orcid: "https://orcid.org/<your-id>"`
     - `.zenodo.json` → (optional) add `"orcid": "<your-id>"` to the creator.
     Commit to `main`. *(Tell me and I'll make this edit for you once you have the ID — it's self-doable for me.)*
  3. **Connect Zenodo to GitHub (one-time, 5 min).** Sign in at https://zenodo.org **with GitHub** →
     top-right menu → **GitHub** → find `trimcrae/Rare-cancers` in the repository list → flip the toggle
     **ON**. (Only releases created *after* the toggle get a DOI.)
  4. **Cut the release (5 min + a minute for Zenodo).** On GitHub: **Actions → "Release — citable roadmap
     snapshot" → Run workflow**, from **`main`**, with a `version` like **`v2026.07.11`**. It tags the commit,
     creates the GitHub Release, and Zenodo automatically archives it and mints a **DOI**. (Per
     `deploy/release-doi.md`. This is permanent and outward-facing — a DOI can't be un-minted — so do it only
     after the reviewer-AI sign-off below.)
  5. **Grab the DOI** from the new Zenodo record and paste it as `[DOI/LINK]` in the emails.
  6. *(Optional)* export `collaborator-brief.md` to PDF (any Markdown→PDF tool) to attach.
  - *Alternative if you'd rather not mint a DOI yet:* make `trimcrae/rare-cancers` **public**
    (GitHub → Settings → General → Change visibility) and link `research/atlas/` — weaker signal than a DOI,
    but works.

**Step 1 — Parallel track: most-receptive audiences + co-author hunt (week 1).**
  Send **Email A1** to the Rare Cancer Research Foundation (the model-generation lead) and **Email A2** to the
  Sarcoma Foundation of America; also look at Count Me In (joincountmein.org) for patient-contributed data.
  Explicitly ask for introductions and for a clinician/scientist co-author. This track is where an
  independent most realistically gains a sponsor.

**Step 2 — Soft-entry academic emails (week 1–2).**
  Send **Email B (Pauli)** and **Email C (Kondo)** — model owners, low-commitment "did I represent this
  correctly?" opener. A few days later, **Email D (Stacchiotti)**. Copy Kondo's and Stacchiotti's exact
  emails from their papers (Pauli's is confirmed). Do not guess an address.

**Step 3 — When someone engages:** thank them, offer a 30-min call, and only then send the concrete
  package — the validation panel + `collaborator-brief.md` (Pauli/Kondo), or `antiangiogenic-mechanism.md`
  + the CRF (Stacchiotti). Make clear you provide all analysis; for Stacchiotti, that her institution owns
  the data and you analyze a de-identified extract only.

**Step 4 — No reply in ~2 weeks:** one polite follow-up each, then broaden (SGC for the ligand route; ask a
  foundation or an engaged contact for an immunopeptidomics introduction).

**Pre-send checklist:**
- [ ] ORCID created and added to CITATION.cff/.zenodo.json.
- [ ] DOI minted (or repo public) → `[DOI/LINK]` filled in every email.
- [ ] `[email]` filled; you are sending from a real, monitored inbox under your own name.
- [ ] Kondo's and Stacchiotti's exact emails copied from their papers (not guessed).
- [ ] Brief's `verification_level` caveats intact — no over-claiming (USZ hit IDs secondary-source;
      HDM201 not a confirmed hit; surrogate reads labelled).
- [ ] You are not requesting identifiable patient data directly (the institution owns it).

> **The one genuinely outward-facing, irreversible step is pressing send / cutting the release** — that's
> yours. Everything up to it is prepared above.
