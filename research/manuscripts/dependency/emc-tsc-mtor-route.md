---
id: DOC-EMC-TSC-MTOR-ROUTE
title: TSC2 inactivation in extraskeletal myxoid chondrosarcoma — measured at 1 of 75, and the access routes it opens
level: L3
kind: memo
status: live
canonical_for: []
purpose: >
  Answer, with a measurement rather than an inference, how often extraskeletal myxoid chondrosarcoma
  carries an inactivating TSC1 or TSC2 alteration; say whether a patient in that fraction could reach an
  open trial; and name the paper this route ends in, or say that it names none.
scope: >
  L3. Reads public panel-sequencing cohorts through the cBioPortal API, the Europe PMC and
  ClinicalTrials.gov records, and the openFDA label. Reports no experiment, no drug exposure and no
  patient of our own. Every number it uses is owned by
  research/literature/emc-tsc-mtor-findings-2026-08-24.json and is pointed at from here, never restated.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-24
last_verified: 2026-08-24
related: [DOC-EMC-BIOMARKER-SELECTED]
---

# TSC2 inactivation in EMC — measured, and what it does and does not open

> ⛔ **Nothing here asserts efficacy, safety, selectivity, a therapeutic window or clinical readiness
> for nab-sirolimus, for any rapalog, or for anything else, in EMC or in any disease.** This memo reads
> databases. It reports how often an alteration is present and which doors are open; it does not claim
> that walking through one would help anybody.

**★ Every figure below lives in
[`emc-tsc-mtor-findings-2026-08-24.json`](../../literature/emc-tsc-mtor-findings-2026-08-24.json).**
That file is the one home. This memo carries the argument, not the numbers.

---

## 1 · The question, and why it was worth asking

TSC1 and TSC2 form the brake on mTORC1. An inactivating alteration in either releases it, which makes
the link to an mTOR inhibitor a **mechanistic switch rather than a correlation** — the kind of selecting
feature that lets an ultra-rare disease enter a drug developed for somebody else.

The prompt was one case: a JSMO 2025 conference abstract
([`galitskiy2025emcpembrolizumab`](../../data/emc-clinical-registry.json)) reporting TSC2 gene loss in an
EWSR1::NR4A3 EMC. The finding was never acted on, because the patient was given pembrolizumab and
responded. **It is an unpursued lead inside its own source**, and this repository had never asked what
lay behind it.

⚠ **The case was described as already recorded here. It was not.** No citation, and no handle for it —
author, DOI, sponsor, conference — appeared anywhere in the tree. The retrieval had been done and cached
on `literature-cache` months ago and never promoted, which is exactly the branch-drift shape
[CLAUDE.md §7](../../../CLAUDE.md) names as a data-loss bug. It is now in the registry at
conference-abstract tier.

## 2 · The answer is a number, and it is not zero

The expected outcome was a bounded zero. It is not one.

**EMC is a codable OncoTree type (`EMCHS`)**, which turned a literature question into a counting
question. MSK's public sarcoma cohort holds **75 patients typed as extraskeletal myxoid chondrosarcoma** —
about four times the largest published EMC sequencing series (18 patients), and more than twelve times the
largest this repository already held (six).

Of those 75, **one carries a somatic TSC2 nonsense mutation** and none carries a TSC1 mutation. The rate
and its exact binomial interval are in the findings file under `measurement.rates`.

⭐ **The one positive is the right kind of alteration.** It is a truncating nonsense variant — the
pathogenic inactivating class the trials require, not a variant of unknown significance. A single case is
a single case; but it is not a near-miss. ⚠ Its somatic status is *inferred* rather than demonstrated,
for the reason given in §2.3.

### 2.1 · Why the zeros are readings of absence rather than absent readings

**This is the control, and without it the whole section says nothing.** A count of zero is evidence only
if the genes were on the panel that was run. They were: **TSC1 and TSC2 are on every MSK-IMPACT panel
version**, including the smallest, and every sample in the larger cohort carries both mutation and
copy-number data. See `measurement.the_control_that_makes_a_zero_meaningful`.

### 2.2 · Ten more cohorts, and what two of them add

The 75 came from one institution on one assay, so ten further public cohorts were read. Six contain **no
EMC at all**. Four do, and two of those — China Pan-cancer (OrigiMed) and the NCI Patient-Derived Models
Repository — are **non-MSK and therefore independent** of the original 75.

**Across those independent samples: zero TSC1 or TSC2 mutations.** The control passes in every cohort —
each shows tens to hundreds of TSC1- and TSC2-mutated samples study-wide, so both genes are on each assay.

⚠ **But count patients, not samples, and the independence is much thinner than it looks.** The nine EMC
"samples" in the model repository are **nine derivative models of one tumour** — an originator, an
organoid, a PDC and several sublines, all from patient P-194179. By patients the independent evidence is
**0 of 3**, not 0 of 11. Three patients with no event is consistent with a low rate and is not replication
of anything.

⭐ **The same check strengthens the main result, though.** `sarcoma_msk_2022`'s 75 EMC samples are **75
distinct patients**. The principal denominator is 75 people, not 75 specimens.

⛔ **The cohorts must never be added together.** `sarcoma_msk_2022` uses anonymised study-prefixed sample
ids while `msk_impact_50k_2026` uses real MSK P-ids, so the MSK cohorts **cannot be deduplicated against
each other**. Only the non-MSK ones are independent of the 75.

⚠ **And independence cuts one way only here.** Eleven more samples with no event raise confidence that the
rate is low; they do nothing to confirm that EMC *ever* carries TSC2 inactivation. **There is still exactly
one positive sample, ever.** That is the limitation that matters for what this route can claim.

### 2.3 · The one positive, checked rather than trusted

The entire frequency rests on one sample, so it was verified against the record. Two independent histology
fields agree — on it and on the whole denominator: 75 by `ONCOTREE_CODE=EMCHS`, 75 by
`CANCER_TYPE_DETAILED`, intersection 75, **symmetric difference 0**. The patient's diagnosis was *revised*
from chondrosarcoma to EMC, so the label is a considered call rather than a default. Tumour purity 77%,
four mutations, TMB 0.13 — consistent with EMC's quiet genome, and not a low-fraction artefact.

⛔ **Its real caveat, recorded rather than smoothed over: the sample is `MATCHED_STATUS = Unmatched`.** The
variant record says `Somatic`, but without a matched normal that status is **inferred by filtering rather
than demonstrated**. A germline TSC2 Q955* would mean tuberous sclerosis, which is clinically conspicuous,
so the germline reading is unlikely — **but unlikely is not excluded**, and the single data point this
frequency rests on is somatic-by-inference. The NR4A3 structural-variant check that would have confirmed
the histology a third way is recorded as **not done** (three candidate endpoint shapes returned 404), not
as a negative.

### 2.4 · Is the rate biased downward? — and the comparison that answers it better

The positive sample is `MATCHED_STATUS = Unmatched`, and checking the rest showed **the whole cohort is**:
all 7,494 samples. That is the bias direction that would matter, because unmatched pipelines filter out
variants that look germline and **TSC1/TSC2 truncating variants are exactly that class** — recurrent
germline pathogenic variants in tuberous sclerosis. A rate depressed by filtering would make "the route is
closed because the rate is low" an artefact rather than a finding.

**The cohort's own numbers bound the worry.** If the filter were suppressing the class wholesale there
would be almost no TSC calls at all; instead there are 37 TSC1- and 66 TSC2-mutated samples across the
7,494 — a plausible pan-sarcoma rate.

⭐ **And that internal comparison is a better statement of the result than the bare 1-of-75.**

| | EMC | whole cohort |
|---|---|---|
| TSC2 mutated | 1 of 75 (1.33%) | 66 of 7,494 (0.88%) |
| TSC1 mutated | 0 of 75 (0%) | 37 of 7,494 (0.49%) |

Same assay, same pipeline, same institution, same filtering — so the comparison cancels all of them.
**EMC's TSC2 rate is indistinguishable from the pan-sarcoma background.** EMC is not an outlier-low
histology for this gene; it is unremarkable, and it looked like an absence only because nobody had counted.
⚠ With one event the comparison cannot be pushed further than "indistinguishable"; it does not show
enrichment, and no test is quoted for it.

### 2.5 · ⛔ The gap between what was measured and what the case reported

The index case reports TSC2 **loss**. What was measured is **mutation** in 75 patients and **homozygous
deletion** in the 15 that have copy-number data. The discrete copy-number profile stores only homozygous
deletion and amplification; **there is no single-copy state in it at all.** So if the case's "loss" is a
single-copy deletion, this measurement would not have counted it, and the true frequency of
*TSC2-inactivating events of every kind* is higher than the number above by an unknown amount.

That is the largest single limitation here, and it is not a reason to discount the measurement — it is a
reason to read it as **a floor on mutation and a floor on deep deletion, not a ceiling on inactivation.**

⚠ **The first attempt to close this gap produced a zero that was not one.** Asking the 50K cohort's
copy-number profile for single-copy loss returned **zero records study-wide** — across all 54,331 samples
and every gene, not just EMC. That is not "no EMC has single-copy TSC2 loss"; it is proof that **the
profile stores no single-copy state at all.** Reading only the EMC count would have yielded the wrong
conclusion, confidently.

**Checking every cohort for that same defect showed how narrow the ground is.** Four of the five
copy-number profiles read carry only `0`, `-2` and `2` — **no single-copy state anywhere** — and the
seventy-five-patient cohort has no copy-number profile at all. Exactly one cohort can answer the question,
and it holds **one** EMC patient.

**In that patient, TSC2 is diploid**: `GISTIC 0` across all nine derivative samples, log2 ratio −0.18 to
+0.07. TSC1 shows no loss either, if anything a slight gain.

So the position is: **homozygous deletion is measured across roughly thirty EMC patients and is zero
everywhere; single-copy loss has been looked for in one patient and was absent.** The alteration class the
index case actually reported is still the least-measured half of this question — narrowed, not closed.

## 3 · What the published record contains, as a count

⭐ **The two answers do not merely coexist — the measured rate explains the literature's silence.** At
roughly one in seventy-five, a series of six patients sees a TSC2 event about 8% of the time and a series
of eighteen about 21%. **Every published EMC sequencing series is small enough that reporting nothing is
the expected outcome**, so the field's silence was never evidence the alteration is absent. It is what a
rare event looks like through small series — which is exactly why the count was worth taking, and why "the
EMC genome is quiet beyond the fusion" needs reading as a statement about sample sizes. (The
probabilities, the series they refer to, and the caveat that they inherit a wide interval are in the
findings file under `why_no_published_series_reports_it`.)

It is worth saying how the literature side was bounded, because a hitCount alone would have misled.

Europe PMC returns 41 records co-mentioning EMC and TSC1/TSC2 — but Europe PMC indexes open-access **full
text**, so a hit can be a paper naming EMC in one table and TSC1 in another. The discriminating test is
whether both appear in the **abstract**, and there the count is **zero** — as it is for EMC and an mTOR
agent. **The same test returns three for EMC-and-PEComa**, which is the positive control proving the test
is not simply returning zero for everything.

Beneath that: none of eleven pan-sarcoma comprehensive-genomic-profiling full texts links EMC to
TSC1/TSC2 or to mTOR, and the one purpose-built study — *Secondary Genetic Alterations in Extraskeletal
Myxoid Chondrosarcoma*, 18 patients on the same MSK-IMPACT panel — names only TP53 as recurrent and does
not name TSC. ⚠ **That study is very likely inside the 75 patients counted above**, being the same
institution and the same assay, so it is the same evidence seen twice rather than two independent
readings.

## 4 · Reachability — the premise this probe started from was wrong

The probe began from the belief that PRECISION 1 was the route, and that if it had closed the
reachability argument was moot. **PRECISION 1 is indeed closed to accrual. The argument is not moot.**

| route | status | matches TSC1/TSC2 → mTOR inhibitor? | open? |
|---|---|---|---|
| PRECISION 1 | active, not recruiting | yes | **no** |
| **TAPUR**, "Group 6 (mTOR, TSC)" | recruiting, 181 US sites | **yes** | **yes** |
| **MD Anderson gemcitabine + nab-sirolimus** | recruiting | **yes**, names soft-tissue sarcoma with TSC1/TSC2 loss-of-function | **yes** |
| CAPTUR, temsirolimus arm | arm explicitly closed | — | no |
| MOST, everolimus arm | closed cohort | — | no |
| expanded access for ABI-009 | record 4 years stale | yes on paper | **unknown** |

The two closed arms are listed **because they are routes that do not work** — a reader who checked only
whether the parent trial was recruiting would have counted them, and been wrong. Identifiers, eligibility
quotes and update dates are in `reachability.routes`.

**And nab-sirolimus is an approved drug** — for malignant PEComa only, on a label that carries no
tumour-agnostic TSC indication. That is a fact about the door, not a recommendation to open it.

## 5 · How strong is the biomarker, honestly

Everything known about TSC2-and-rapalog response comes from **PEComa**, and the strongest evidence is the
AMPECT trial's exploratory biomarker analysis. Its figures are quoted verbatim in
`how_good_is_the_biomarker` — including three things that a summary of it usually drops:

- At final analysis the split is **8 of 9 with a TSC2 alteration versus 1 of 5 with a TSC1 alteration**,
  with median duration of response 51.7 months against 5.6. But the trial **cannot explain why**, and
  says so — n=5 for TSC1 — and its own conclusion is that "responses and prolonged disease control were
  also observed in patients with differing tumor genotypes".
- ⭐ **Both complete responders had a TSC2 alteration and one of them was a homozygous deletion**, so the
  qualifying class is not mutation alone. That matters here: the index case reported *loss*, and deletion
  is the half of the EMC measurement that is least well covered (§2.5).
- An **immunohistochemical** marker of mTORC1 output, pS6, was an independent predictor — no patient
  whose tumour lacked it responded. **The genotype was not the only discriminator.**
- The only multicentre attempt to reproduce the genotype effect found no difference — but on 2 TSC1 and
  12 TSC2 patients, so it is **underpowered and is weak evidence, not counter-evidence.**

⛔ **Transferability to EMC is not established by anything here.** AMPECT's TSC2-mutant responders had
primaries in retroperitoneum, kidney, uterus, liver and small bowel — PEComa sites, none of them an EMC
site. Whether a TSC2-inactivated EMC behaves like a TSC2-inactivated PEComa is open.

## 6 · The speculative thread, graded and withdrawn as support

mTORC1 drives HIF1A and VEGF; EMC's most reproducible clinical signal is sensitivity to antiangiogenic
TKIs; our own read had HIF1A at the 98th percentile. That is suggestive, and it does not survive contact
with the second platform.

Across both series the **direction** replicates for RPS6, HIF1A and VEGFA and **flips** for MTOR and
AKT1 — the output genes read modestly higher, the pathway-core genes give no consistent signal.
⚠ **And the percentile framing was misleading, so it is withdrawn here:** the comparator arm sits at the
97th percentile on the same array where EMC sits at the 98th, and on the other platform EMC sits at the
42nd. The striking number was a property of the array, not of the disease.

**It cannot bear on this route in either direction.** Abundance is not activation, a transcript is not a
phosphoprotein, and no transcript reading can establish an inactivating DNA alteration — which is
precisely what the trials require. Note that AMPECT's own output-axis predictor was a **phospho-protein
stain**, which is not what RPS6 transcript abundance measures. The thread is recorded as bounded and is
not carried forward.

⚠ **Adding TSC1/TSC2 to the expression panel is cheap and is not worth doing for this question.** It
would produce a transcript reading that could not answer the DNA question, which has now been answered
directly and better.

## 7 · The route's paper

**PUB-EMC-TSC — *A one-in-seventy-five biomarker: TSC2 inactivation in extraskeletal myxoid
chondrosarcoma, and the access routes it already opens.*** Unwritten.

> **The one sentence, written so a reader can disagree with it.** Extraskeletal myxoid chondrosarcoma
> carries TSC2-inactivating mutations in about one of seventy-five sequenced patients and TSC1 mutations
> in none of them — rare enough to explain why no EMC series has ever reported either gene, but not
> zero — and a patient in that fraction can today enter a recruiting tumour-agnostic trial arm that
> matches the genotype to an mTOR inhibitor, so the binding constraint on this route is neither the drug
> nor the trial but whether EMC patients are sequenced on a panel that already contains both genes.

**What is missing from it**, stated plainly so the row is honest:

1. **The single-copy question** (§2.5), now answered for exactly one patient and open for everyone else,
   because only one public cohort carries a copy-number profile fine-grained enough to ask it.
2. **A second positive, and genuine independence.** The independent evidence is three patients (§2.2),
   which supports the rate being low and **confirms nothing about the numerator**. There is still exactly
   one positive sample in the world as far as this probe can see, and it is somatic-by-inference (§2.3).
   This is the item that matters most.
3. ~~Patients, not samples.~~ **Discharged.** Every cohort's sample-to-patient ratio was checked: the
   principal denominator is 75 distinct patients, and the one place where samples badly overstated
   patients (nine to one) is now handled in §2.2.
4. **Any evidence that a TSC2-inactivated EMC responds like a TSC2-inactivated PEComa.** There is none,
   and there is no route to it here that does not involve a patient.

⭐ **Why this is a paper and not a note.** The measurement is small but it is the first of its kind for
this disease, and the interesting half is not the number. It is two things the number makes visible.

**First, the rate explains the silence.** At one in seventy-five, every published EMC series is too small
to expect an event — so "the EMC genome is quiet beyond the fusion" has been a statement about sample
sizes that the field reads as a statement about the genome. **That inference error is not specific to
TSC2**, and correcting it for one gene shows how to correct it for the rest.

**Second, the bottleneck sits upstream of everything this route needs.** The drug exists, trial arms are
recruiting, and both genes are already on the panel every major centre runs. Nothing between an eligible
patient and an open trial is missing except the test result — an unusual place for an ultra-rare disease's
obstacle to sit, and worth saying out loud.

⛔ **What this route is NOT.** It is not a lead family, it is not a degrader competitor, and it does not
belong in `systems/graph/` on the strength of one positive sample until item 2 above is discharged —
a populated field is not a measured one, and a route with n=1 supporting it would read in the portfolio
as far more than it is.
