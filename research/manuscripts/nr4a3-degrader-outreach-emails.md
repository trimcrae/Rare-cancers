# NR4A3-degrader — outreach emails (send after the preprint is posted)

> **Purpose.** Ready-to-send cold emails to get the NR4A3/EMC in-silico work in front of people with wet labs
> (validation / hand-off / collaboration) and rare-cancer foundations. Part of the operating regime
> (`emc-treatment-strategy.md → "Operating regime (2026-07-01)"`): **publish AND nudge** — a niche preprint is
> too easily missed, so a handful of targeted notes is the cheap multiplier.
>
> **When to send:** the day the preprint goes up (ChemRxiv). Fill in `[PREPRINT_URL]` + `[PREPRINT_DOI]` +
> `[REPO_URL]` + your name/contact first. Personalise the one bracketed sentence per recipient — that single
> specific line ("because you did X") is what gets a cold email read.
>
> **Etiquette (keep it this way):** short (~150 words), one clear low-friction ask, honest that it's in-silico
> (predicted, not validated), offer generous terms (their choice of collaboration/hand-off/co-authorship).
> Never overclaim — "computationally designed / predicted," never "we found a drug."

## Who to contact (build the list; find current contacts before sending)
- **NR4A / nuclear-receptor structural & pocket-dynamics labs** — esp. the **de Vera group** (published the
  Nurr1 canonical/"breathing" pocket, *Structure* 2019 — the closest precedent and a natural adopter/reviewer;
  look up current affiliation + email). Plus other NR-LBD MD / cryptic-pocket groups.
- **SGC (Structural Genomics Consortium)** — open-science, targets understudied proteins incl. nuclear
  receptors; could put an NR4A3 LBD through a structural/biophysical pipeline.
- **Sarcoma / EMC translational labs** — groups working on EWSR1/FET-fusion sarcomas and EWSR1::NR4A3 biology.
- **Rare-cancer / sarcoma foundations & patient-advocacy orgs** — e.g. Sarcoma Foundation of America and
  EMC/soft-tissue-sarcoma-focused funds; they connect leads to labs and sometimes fund validation.
> Verify every name/affiliation/email at send time — do not send to stale or guessed addresses.

---

## Template 1 — NR4A / nuclear-receptor structural lab (general)
**Subject:** Cryptic druggable pocket in NR4A3 — preprint + a designed selective candidate

Dear Prof. [LAST NAME],

I'm an independent researcher. I've just posted a preprint on the computational druggability of **NR4A3** — the
NR4A paralogue with no experimental structure, and the driver of extraskeletal myxoid chondrosarcoma (EMC) and
acinic cell carcinoma. I'm sharing it because [**your work on NR-LBD pocket dynamics / cryptic pockets is
directly relevant** — personalise].

Briefly: well-tempered metadynamics plus an unbiased "release" run show NR4A3's occluded orthosteric pocket
**breathes into a metastable, druggable induced-fit cavity** (~24% of unbiased frames), paralleling the Nurr1
breathing pocket. A pocket-conditioned de-novo campaign then produced a candidate (**denovo_401**) that survives
a full control battery — multi-snapshot MM-GBSA **above a like-for-like decoy null**, plus a state-matched
re-dock — as a predicted NR4A3-selective (vs NR4A1/2) binder.

It's entirely in-silico (no wet lab), so the candidate is a **prediction, not a validated molecule** — which is
exactly where I'd value your read. If any of it looks worth a wet-lab test (even a thermal-shift or SPR binding
check against the NR4A LBDs), I'd gladly share all structures/data and collaborate on whatever terms suit you.

Preprint: [PREPRINT_URL] · Data & code: [REPO_URL]

Thanks for your time,
[YOUR NAME / CONTACT]

---

## Template 2 — the de Vera group (specific; the Nurr1-pocket precedent)
**Subject:** NR4A3's breathing pocket — a computational follow-on to your Nurr1 work

Dear Dr. de Vera,

Your 2019 *Structure* paper defining Nurr1's dynamic canonical pocket was the direct inspiration for a
computational study I've just posted as a preprint, and I'd be grateful for your eye on it.

I asked whether **NR4A3** — the uncrystallised paralogue driving EMC and acinic cell carcinoma — has the same
"breathing" behaviour. Metadynamics plus an unbiased release run say yes: its occluded orthosteric pocket is
**metastable and druggable in ~24% of unbiased frames** (an induced-fit cavity, not a static pocket), and a
de-novo campaign produced a predicted NR4A3-selective candidate that clears a decoy-null specificity control.

It's in-silico only, so it stands or falls on wet-lab follow-up. Given your NR4A biophysics, I wanted to offer
the whole package (structures, trajectories, candidate) — to validate, build on, or simply critique. Happy to
collaborate on any terms.

Preprint: [PREPRINT_URL] · Data & code: [REPO_URL]

With appreciation,
[YOUR NAME / CONTACT]

---

## Template 3 — SGC (Structural Genomics Consortium)
**Subject:** Understudied nuclear receptor NR4A3 — computational druggability + candidate for a structural pipeline

Dear [SGC contact / target-nomination team],

NR4A3 is an understudied, "undruggable"-reputation nuclear receptor with **no experimental structure**, yet it
drives two cancers (EMC; acinic cell carcinoma) by gain of NR4A3. I've posted a preprint characterising its
druggability computationally — a cryptic, induced-fit orthosteric pocket (metadynamics + unbiased release run)
and a de-novo, decoy-null-validated selective candidate.

This seems a natural fit for the SGC's understudied-protein, open-science model. Would NR4A3's ligand-binding
domain be a candidate for your **structural / biophysical pipeline** (LBD production + a binding/thermal-shift
screen against the candidate, with NR4A1/2 as selectivity counter-screens)? I'll share everything openly and
contribute the computational side however is useful.

Preprint: [PREPRINT_URL] · Data & code: [REPO_URL]

Thank you,
[YOUR NAME / CONTACT]

---

## Template 4 — sarcoma / EMC translational lab
**Subject:** A druggable-pocket + degrader hypothesis for the EWSR1::NR4A3 fusion (EMC) — preprint

Dear Prof. [LAST NAME],

Given your work on [**FET-fusion sarcomas / EMC biology** — personalise], I wanted to share a preprint proposing
a **tractable therapeutic angle for EMC's EWSR1/TAF15::NR4A3 driver**.

The fusion retains a near-intact NR4A3 ligand-binding domain. Computationally, that domain's "occluded" pocket
**breathes into a druggable induced-fit cavity**, and I designed a predicted NR4A3-selective (NR4A1/2-sparing)
binder as a degrader warhead starting point — sparing NR4A1 matters because NR4A1/NR4A3 co-loss is
leukaemogenic. It's in-silico only; the make-or-break next step is exactly your domain — an acute-degradation
(dTAG) or knockdown test of NR4A3 dependence in EMC cells, and a binding check of the candidate.

If this is worth pursuing, I'd share all data and collaborate on any terms.

Preprint: [PREPRINT_URL] · Data & code: [REPO_URL]

Best regards,
[YOUR NAME / CONTACT]

---

## Template 5 — rare-cancer / sarcoma foundation or patient-advocacy org
**Subject:** A new computational lead for extraskeletal myxoid chondrosarcoma (EMC) — seeking a wet-lab partner

Dear [ORG / contact],

I'm an independent researcher who has spent the last while on the computational biology of **extraskeletal
myxoid chondrosarcoma (EMC)** — an ultra-rare sarcoma with no targeted therapy, driven by the EWSR1/TAF15::NR4A3
fusion. I've just posted a preprint that (1) makes a computational case that NR4A3, long considered
"undruggable," is in fact druggable through a hidden pocket, and (2) proposes a specific designed molecule as a
starting point for removing the cancer's driver.

Everything so far is computer modelling — the essential next step is a lab test, which I can't do alone. I'm
writing to ask whether you could **connect me with a sarcoma/NR4A research lab**, or point me to any small
validation funding. I'll share all of it openly; my only goal is to get this into hands that can move it toward
patients.

Preprint (plain-language summary inside): [PREPRINT_URL]

With thanks for the work you do,
[YOUR NAME / CONTACT]

---

## After sending — track responses
Keep a simple log here (who / date / response / next step) so a future session can follow up without
re-deriving the outreach state.

| contacted | date | channel | response | next step |
|-----------|------|---------|----------|-----------|
| _(fill in)_ | | | | |
