# EMC atlas — outreach: send-ready package + runbook

> **This is the outreach for trimcrae to send.** It names real recipients (public corresponding
> authors), gives the contact route for each, provides finalized emails with only the **sender fields**
> left to fill, and ends with a **numbered runbook of exactly what you do next**. Nothing here is sent
> automatically and nothing impersonates anyone — you send, under your own name, to public academic
> contacts. Pair each email with `collaborator-brief.md`.
>
> **The one thing only you can supply:** your identity as the named human sender (`[YOUR NAME]`,
> `[affiliation or "independent researcher"]`, `[email]`, `[link to the shared atlas]`). Everything else
> is filled in.

---

## Recipients (real, verified) and how to reach each

| # | Recipient | Role / why | Contact route (confirm the exact email from the source) | Program |
|---|---|---|---|---|
| 1 | **Dr. Chantal Pauli** — Dept. of Pathology & Molecular Pathology, University Hospital Zurich (USZ) | Built the two USZ EMC models (USZ20-EMC1 EWSR1, USZ22-EMC2 TAF15) | Email **chantal.pauli@usz.ch** (corresponding author, Bangerter 2023, PMC9813045) | 1 — proteostasis panel |
| 2 | **Dr. Tadashi Kondo** — Division of Rare Cancer Research, National Cancer Center Research Institute, Tokyo | Built NCC-EMC1-C1; ran the 221-drug screen | Corresponding author, Iwata 2025 (PMID 40580361) — **copy his exact email from the paper's correspondence line**; lab page: ncc.go.jp/en/ri/division/rare_cancer_research/member/kondo.html | 1 — proteostasis panel |
| 3 | **Dr. Silvia Stacchiotti** — Adult Mesenchymal & Rare Tumor Unit, Fondazione IRCCS Istituto Nazionale dei Tumori, Milan | Led essentially all EMC systemic-therapy evidence (pazopanib, sunitinib, IMMUNOSARC II) incl. the EWSR1-vs-TAF15 differential | Corresponding author, Stacchiotti 2019 (Lancet Oncol, PMID 31331701) — **copy her exact email from the paper**; ResearchGate profile confirms affiliation | 2 — antiangiogenic biomarker + response cohort |

**Secondary (approach after a primary reply, or in parallel if you have bandwidth):**
- **Antigen / immunopeptidomics** — easiest via a primary contact's network (Pauli/USZ or Stacchiotti/INT both have immuno-oncology groups); or a dedicated sarcoma-immunopeptidomics lab. Ask the primary contact for an introduction rather than cold-emailing.
- **Structural Genomics Consortium (SGC)** — thesgc.org — for the long-horizon NR4A3-ligand/direct-fusion route (chemical-probe collaboration). Contact via the site's "collaborate" route.
- **Funding / tissue-network foundations** — Sarcoma Foundation of America (curesarcoma.org, research grants) and the Rare Cancer Research Foundation / Count Me In patient-derived-model network (pattern.org / joincountmein.org). Verify current URLs before use.

> Note on emails: I've given the **verified** address where a search surfaced it (Pauli) and the exact
> **source** to copy it from otherwise (Kondo, Stacchiotti) — do not guess an address; open the cited
> paper's correspondence line and copy it. Corresponding-author emails are printed in every paper.

---

## Email 1 → Dr. Pauli (USZ models — proteostasis panel)

> **To:** chantal.pauli@usz.ch
> **Subject:** Ready-to-run validation panel for your USZ EMC models — full computational support, no cost to your lab
>
> Dear Dr. Pauli,
>
> I'm `[YOUR NAME]`, `[an independent computational researcher / affiliation]`. I've built an open,
> reproducible **EMC Open Target & Drug Atlas** that integrates every usable EMC dataset, model, and
> drug screen with a transparent, provenance-checked evidence score — and your USZ20-EMC1 and
> USZ22-EMC2 models are central to its single strongest preclinical hypothesis.
>
> Your screen and the independent NCC screen converge on a **proteostasis–chromatin vulnerability**
> (proteasome/carfilzomib, HSP90/PU-H71, HDAC/panobinostat–romidepsin). I've assembled a
> **12-compound / 6-combination, class-vs-compound validation panel** with pre-registered go/no-go
> criteria and concentrations chosen against achievable human exposure (I compiled the label
> pharmacokinetics for the panel). A public DepMap analysis I ran shows these targets are pan-essential,
> so the decisive question is a therapeutic-window/pharmacology one — which this panel is built to
> answer, in both fusion subtypes you have.
>
> I would provide **all** experimental design, analysis, and manuscript support. Would your lab consider
> running the panel in the USZ models (with the controls specified)? A two-page evidence brief,
> plate-map-ready panel, and draft figure set are attached, and the full atlas is here: `[LINK]`.
>
> With thanks and admiration for the models you've built,
> `[YOUR NAME]` · `[email]` · `[link]`

## Email 2 → Dr. Kondo (NCC model — proteostasis panel)

> **To:** `[copy exact email from Iwata 2025, PMID 40580361]`
> **Subject:** NCC-EMC1-C1 — a class-vs-compound follow-up to your 221-drug screen (full analysis support)
>
> Dear Dr. Kondo,
>
> I'm `[YOUR NAME]`, `[independent computational researcher / affiliation]`. I've built a reproducible
> **EMC Open Target & Drug Atlas**, and your NCC-EMC1-C1 screen (brigatinib, panobinostat, romidepsin)
> is one of its two pillars. Cross-referenced with the USZ screen, the signal points to a
> **proteostasis–chromatin** dependency rather than any single nominal target — for example, your two
> HDAC hits suggest the effect tracks the target, and public DepMap data indicate brigatinib's activity
> is unlikely to be ALK-dependent (ALK is non-essential in sarcoma lines).
>
> I've designed a **class-vs-compound validation panel** (≥2 members per class, exposure-matched
> concentrations, pre-registered go/no-go, target-engagement readouts) to test this rigorously. I would
> provide all design, analysis, and manuscript support. Might your group run it in NCC-EMC1-C1 (plus
> controls)? Two-page brief and panel attached; full atlas at `[LINK]`.
>
> Respectfully,
> `[YOUR NAME]` · `[email]` · `[link]`

## Email 3 → Dr. Stacchiotti (antiangiogenic biomarker + response cohort)

> **To:** `[copy exact email from Stacchiotti 2019, Lancet Oncol, PMID 31331701]`
> **Subject:** EWSR1-vs-TAF15 antiangiogenic biomarker in EMC — a growth-rate-adjusted re-analysis proposal
>
> Dear Dr. Stacchiotti,
>
> I'm `[YOUR NAME]`, `[independent computational researcher / affiliation]`. Your group generated
> essentially all the systemic-therapy evidence in EMC, and your sunitinib data explicitly report that
> responders carried EWSR1::NR4A3 while refractory cases carried TAF15::NR4A3 — a fusion-subtype
> biomarker that could sharpen treatment selection today.
>
> I've built a reproducible EMC atlas and a response-linked common data model with
> **growth-rate-adjusted endpoints** (pre- vs on-treatment growth, growth-modulation index,
> time-to-next-treatment), because in an indolent disease stable disease alone overstates activity. I
> propose a re-analysis testing whether the EWSR1-vs-TAF15 signal predicts *growth-rate-adjusted*
> benefit and survives leave-one-patient-out, plus a kinome-level comparison of the active TKIs to
> nominate the next agent to trial.
>
> Your institution would own consent, ethics, and de-identification throughout; I would provide the data
> model, statistical plan, and analysis. Would you be open to discussing a de-identified,
> fusion-annotated, response-linked dataset? Two-page brief and the data model are attached; full atlas
> at `[LINK]`.
>
> With respect for your work in this disease,
> `[YOUR NAME]` · `[email]` · `[link]`

---

## SEND RUNBOOK — exactly what you do next

**Step 0 — Decide how you'll identify yourself (5 min).** Fill `[YOUR NAME]`, `[affiliation or
"independent researcher"]`, `[email]` in all three emails. *Optional but strongly recommended:* recruit
one **named sarcoma clinician/scientist co-author** first — a cold email lands far better with an
academic name attached. If you have one, add "and my collaborator `[Name, institution]`" to the sender line.

**Step 1 — Make the evidence shareable (10 min).** The recipients need to open the package:
  - **Repo link `[LINK]`:** either (a) make `trimcrae/rare-cancers` public, or (b) create a read-only
    share, or (c) skip the link and rely on attachments. If public, link straight to `research/atlas/`.
  - **Attachment:** export `research/atlas/collaborator-brief.md` to PDF (any Markdown→PDF tool). Optionally
    also attach `evidence_score.json`'s `validation_panel` as the plate-map-ready panel, and one figure.

**Step 2 — Confirm the two exact emails (5 min).** Pauli's is verified (chantal.pauli@usz.ch). For **Kondo**
open Iwata 2025 (PMID 40580361) and copy the corresponding-author email; for **Stacchiotti** open
Stacchiotti 2019 (PMID 31331701) and copy hers. Do **not** guess an address.

**Step 3 — Send, in this order (staggered by a few days):**
  1. **Pauli (Email 1)** and **Kondo (Email 2)** first — they own the models the strongest program needs.
     Send both; they're not competitors for this and either yes unlocks Program 1.
  2. **Stacchiotti (Email 3)** — the clinical-cohort program; can go same day or a few days later.
  Send from a real, monitored inbox; attach the brief PDF; paste the repo link.

**Step 4 — When someone replies "interested":**
  - Offer a 30-min call. Bring the plate map, the pre-registered go/no-go, and the analysis commitment.
  - For Stacchiotti specifically: the data flow is *their* institution → de-identified extract → your
    analysis; make clear you are not asking to hold identifiable data.
  - Send the full `research/atlas/` and the relevant program doc (`collaborator-brief.md` +
    `antiangiogenic-mechanism.md` for Stacchiotti; the validation panel for Pauli/Kondo).

**Step 5 — If no reply in ~2 weeks:** one polite follow-up, then move to the secondary list (SGC for the
ligand route; foundations for funding/tissue; ask a primary contact for an immunopeptidomics introduction).

**Pre-send checklist (tick before Step 3):**
- [ ] Sender name/affiliation/email filled in all three emails; a named human is the sender.
- [ ] (Recommended) a sarcoma clinician/scientist co-author named.
- [ ] Repo link works or the brief PDF is attached.
- [ ] The brief's `verification_level` caveats are intact — no over-claiming (USZ hit IDs are
      secondary-source; HDM201 is not a confirmed hit; surrogate reads are labelled).
- [ ] Kondo's and Stacchiotti's exact emails copied from their papers (not guessed).
- [ ] You are not requesting identifiable patient data directly (the institution owns it).
