---
id: DOC-DEGRADER-METHODS-FAILURE-RECORD
title: "A retrospective audit of one computation-only degrader program's instrument records: what the methods did and did not establish about paralogue selectivity"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: What can be said, from this program's own retained instrument records, about which of its paralogue-selectivity statements its methods supported and which they did not — reported at the scope those records actually reach.
scope: A retrospective audit of the instrument records enumerated in §5 and in the supplementary per-instrument inventory, together with the quantitative results reproduced in §4. It is an audit of retained records, not a re-execution of the program. It makes no claim about EMC treatment.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-06
last_verified: 2026-09-08
---
# A retrospective audit of one computation-only degrader program's instrument records: what the methods did and did not establish about paralogue selectivity

**Preprint draft — not submitted, not posted.**

**Tristan D. McRae**

Independent researcher, unaffiliated. Correspondence: trimcrae@gmail.com. ORCID 0000-0002-1823-1451.

*Study type: a retrospective audit of a computation-only research program's own instrument records, read
from committed computational artifacts and public structural and literature records. No experiment was
performed and no wet-lab work of any kind was carried out. Full declarations:
[§12](#12--declarations).*

> **Revision note, 2026-09-08.** This draft is the coherent correction batch required by an independent
> final scientific review of the frozen manuscript (commit `0b965a1279c81c10d9edc054842a33446e87762e`,
> main SHA-256 `a9058b6c40e32549f878347b2d4f8c0ed3f8593320ce417ef29367179a7d0fe2`) and by the
> adjudication that accepted all twelve of its findings. The earlier formulation claimed an
> adequately-powered null, a causal effect bound, a uniquely diagnosed calibration failure, a complete
> whole-program ascertainment, a within-repository false-positive rate, an excluded design class and a
> refutation of an external publication. Each of those is withdrawn or narrowed here, with the retained
> measurement kept and the interpretation corrected. The finding-by-finding response matrix is
> `research/autonomy/opus-capacity-campaign-20260908/paper-lane/MF1-repair/F01-F12-response-matrix.md`.
> ⛔ **No original execution record, result file or protocol history was rewritten.** The corrections are
> made in this manuscript and in explicitly dated corrective interpretations; the original bytes stand.
>
> **Residual revision note, 2026-09-08 (second batch).** A single focused verification of that correction
> batch closed four of its findings and returned five finite residuals, which root admitted and this
> revision carries: **R1** the supplement's current claim scope and the roadmap → census → extraction →
> supplement dependency (§3, §2); **R2** the withdrawal of pre-outcome chronology as fact and of literal
> shared structural inputs (§3, §6.1, §6.2, §9.6); **R3** the register's benchmark identities and values,
> the E1 exclusion stages, and the generated-versus-authored boundary (§4.1a, §4.2, §11); **R4** the
> per-prefix result-object count (§9.4); **R5** the ligand boundary of the single-hydrogen-bond mechanism
> (§6.3). ⛔ **None of this is a new measurement, a new review, a new source or a re-run experiment**, and
> none of it lifts any scientific hold. The residual closure map and its evidence are at
> `research/autonomy/opus-capacity-campaign-20260908/paper-lane/MF1-residual/`.

---

## 1 · Abstract (draft)

Computational drug-discovery programs report the funnels that worked. This paper reports the retained
instrument records of one that did not, as an **instrument-by-instrument retrospective audit** of a
specified set of records rather than a survey of a field or of a method.

The worked system is the nuclear receptor NR4A3 and a hypothesised bivalent degrader against it; the
paper's subject is the **record**, not the target. The audit universe is fixed in §3 and its
ascertainment limits are stated there: this is what one program retained, not what every program does.

**The register's shape.** The route record this paper cites partitions **twenty** instruments into
**four** carried as `support` and **sixteen** carried under the single administrative label
`disclosed_failing` — a route bookkeeping word that covers materially different facts and is **not** a
scientific failure rate (§5). The numbered instrument census carries **twenty-two** entries; `V2` and
`V18` sit in the census and outside this route's partition, and the two counts are never summed. A
complete per-instrument inventory, separating **control type**, **execution and eligibility**,
**inferential outcome** and **claim scope**, is in the supplement.

**Three recorded attempts at a positive control for paralogue-selectivity detection**, assembled
retrospectively from the record rather than planned as a series: an alchemical ternary cooperativity
calibrator that recovered the **wrong sign**; an endpoint-MD sensitivity control that **executed and did
not meet its registered directional criterion**; and a biological retrospective that was
**covalency-confounded** and therefore ineligible at any sample size. ⚠ They share code, structural
assumptions and selection decisions, and two of them are applications of the same instrument, so they are
**three recorded attempts, not three independent validations**. None succeeded. A fourth known-answer
test for this axis, `V4`, is built and staged, carries no result key, was never completed and is not
authorised. The consequence carried in the program's own record is that **every paralogue-selectivity
statement the program can make is an unvalidated prediction**.

**What the endpoint-MD control actually returned.** It executed with **6 versus 5** admitted model means
and zero technical failures in either arm, gave a difference of **+0.4373 Å** in the direction opposite to
the one its criterion required, and **p = 0.746753** on its exact one-sided permutation test. Its
reference set of 462 label assignments has an attainable p-value **floor of 1/462**. ⛔ That floor is a
**discreteness property of the reference set and not statistical power**: no effect size is established
for this observable, the panel's own record states that the readout has no established quantitative link
to degradation selectivity, and the co-fold input validation the panel assumed had not been implemented
before it ran. The recorded outcome is a tier of `NULL` with a register control state of `fails` — an
**executed calibration attempt that did not meet its criterion**, which is neither an absent control nor a
powered demonstration of insensitivity.

**Infrastructure defects, separated.** A chain-assignment defect caused a completed covalent feasibility
panel's interface readouts to describe the wrong protein pair; two of its legs additionally tethered the
electrophile to the wrong cysteine, which is a wrongly simulated physical system rather than a
post-processing error; an nm/Å unit error and a chain-blind reactive-cysteine search sit alongside them;
and a **separate** set of descriptive and shakeout co-folds was contaminated with the wrong E3 subunit,
while the completed covalent panel's inputs were clean of that contamination. The existing tests **missed**
these defects. A retained object census over two named storage prefixes finds no multi-frame coordinate
file, so the corrected-interface readouts cannot be recomputed. ⚠ Persisted trajectories would have
permitted that rescoring; they could **not** have repaired the legs that simulated the wrong tether.

The transferable prescription is **two rules, not one**: test every instrument against a known answer
*and* persist inputs, identities, code and parameter versions, and trajectories appropriate to the
observable. The second is the more expensive rule and the one this program was missing.

⛔ This paper makes **no** claim of proteome-wide selectivity, **no** efficacy claim for extraskeletal
myxoid chondrosarcoma or any other disease, **no** safety or therapeutic-window claim, and asserts **no**
clinical readiness. Nothing here is a treatment candidate. It also makes no claim that in-silico
selectivity prediction fails in general, that any design class is impossible, or that any external
publication is defective.

---

## 2 · The claim, stated once

> From one computation-only program's retained instrument records, it is possible to state which of its
> paralogue-selectivity statements its methods were graded as supporting and which they were not, with
> each instrument's control type, execution state, inferential outcome and claim scope reported
> separately — and the enumerated failures, with the evidence that is retained for each, are the
> transferable result.

**What the claim does NOT include, and it matters.** It is not a claim that in-silico selectivity
prediction does not work. It is a claim about **one** program's instruments, on **one** target family, run
by **one** author, and the honest generalisation is *"here is what happened when one program's records
were audited this way"*, never *"this is what happens"*
([§10.1](#101--n--1-and-the-paper-must-say-so-in-the-abstract)). It also does not claim that each failure
has a uniquely identified cause: where the retained evidence does not separate candidate causes, the paper
says so.

⭐ **The disclosed divergence, updated 2026-09-08.** The endpoint register
[`systems/graph/publications.json`](../../../systems/graph/publications.json) → `PUB-METHODS` carried the
superseded formulation — *"exactly which"* and *"each with its diagnosed mechanism"* — which this revision
does not support. ⭐ **That patch has now been applied** by the parent integrator at commit
`a6a21fc591d2451038cdf53449b91e3990d59cfb`, together with the nine roadmap edits filed with it; the
`what_it_would_claim` and `outcome_potential_why` fields now carry the scoped wording, and the instrument
census and three generated views were regenerated from those sources.

⭐ **The four remaining cells have since been applied too, 2026-09-09.** An earlier version of this
paragraph said four current cells still diverged and that an exact **unapplied** patch was filed for them.
That status is superseded: the parent integrator applied all four at commit
`91609d30fdc672f4dbc9eb191e6342a7ddd4f61d` and regenerated the instrument census from the corrected
roadmap. The four were the census `V11.result` (which had read *"NULL, adequately powered"*), the census
`V16.result`, the census `V16.scope_limit` and the census `V20.scope_limit`; the roadmap dependency row's
*"with a quantified bound"* clause was removed in the same integration. At the bound census revision
(`instrument-census.json`, 31,770 B, SHA-256
`f484afe4bb5795283dab8131cf47d3fe2d4204b401c559a41ad406366228526a`) each of those cells carries its own
dated 2026-09-08 correction at source, so a reader arriving at the shared register no longer meets a
withdrawn reading. ⛔ **The filed patch set is retained as the historical record of what was proposed and
must not be reapplied.** Shared files remain not this manuscript's to edit.

---

## 3 · Audit methods

**The audit universe.** The instruments audited here are the numbered instrument register — `V1` to `V22`
— as carried by [`instrument-census.json`](../../modalities/instrument-census.json) /
[`instrument-census.md`](../../modalities/instrument-census.md), generated from
[roadmap §3.1](../nr4a3-program-map.md#31--the-instrument-table) and §3.2, together with the route
partition [`systems/graph/routes.json`](../../../systems/graph/routes.json) → `RT-METHODS-PAPER.instruments`,
which selects the twenty of them this paper cites. Time cutoff: records as they stand on the commit named
in [§11](#11--provenance-versioned-locators-and-the-dependency-manifest).

⛔ **Ascertainment, stated as a limit rather than as a strength.** The register is generated from the
program's graph, so it is consistent with that graph; that is **not** evidence that every method the
program ever used was discovered, registered or entered into it. The numbered census was itself added
retrospectively, and it records that `V21` had been quoted for months before it acquired a row. The audit
is therefore **complete with respect to the enumerated records** and makes **no claim of complete
whole-program ascertainment**. The earlier draft's claim that the missing-failures objection is
*"answerable by construction"* is withdrawn.

**Retrospective, not prospective.** The audit was assembled after the runs it describes. ⚠ **Corrected
2026-09-08 (R2).** Several of its gates and criteria carry an explicit pre-run freeze assertion, so **the
retained protocol describes those rules as prespecified** — that attribution is what the record supports,
and the earlier affirmative statement that they *were* frozen before their own runs is withdrawn. A
current freeze flag and a current version-control pin do not by themselves establish which rule existed
before outcome access, and no chronology audit was run for this revision. Where a retained pre-outcome
revision or amendment is identifiable it is named; otherwise the paper says only that the retained
protocol describes the rule as prespecified. Two preregistration files carry
backfilled metadata, and that is disclosed at the claims that depend on them (§6.4, §9.6).

**Handling of contradictory and superseded records.** Where a narrative annotation in the program roadmap
disagrees with the primary artifact it cites, this paper follows the **primary artifact** and records the
disagreement. Four such disagreements are carried in §9 and in the corrective-interpretation note filed
with this revision.

⚠ **The display chain, stated because it was previously misread (R1, 2026-09-08).** The reader-facing
displays are not independent of the shared registers. The actual dependency runs **roadmap §3.1/§3.2 →
[`instrument-census.json`](../../modalities/instrument-census.json) → the MF1 extraction → the
per-instrument inventory and the supplement.** The extraction does not read the roadmap directly, but it
reads the census that is generated from it, so a roadmap correction does not reach the supplement until
the census is regenerated and the extraction is re-run. ⛔ **The earlier patch instruction that the MF1
extraction needed no regeneration because it does not read the roadmap was wrong and is withdrawn**; a
dated supersession is filed beside it at
`research/autonomy/opus-capacity-campaign-20260908/paper-lane/MF1-residual/`.

⛔ **Supersession is dated, and history is not rewritten.** Where a current row a reader reaches still
carries a claim this revision withdraws, the withdrawal is dated at the row and the old wording is kept
verbatim beside it rather than deleted. ⭐ **Corrected 2026-09-09:** this sentence previously described
the supplement's adjacent inventory column as an explicitly labelled *"superseded historical
annotation"*. Since the four shared cells were applied at `91609d30fdc672f4dbc9eb191e6342a7ddd4f61d`,
that label is wrong: the column is now **the census `scope_limit` as it reads at the bound census
revision**, printed beside this paper's author-current claim scope so the two can be compared. An
author-current override existing for a row does not by itself make the census cell superseded — see the
supplement's inventory. ⚠ **No wholesale rewrite of the historical roadmap
is performed, proposed or authorised**; only the current statements a reader actually arrives at are
corrected or explicitly superseded. Original raw execution outputs, result files and protocol histories are treated as
**immutable evidence**: nothing in this batch rewrites them, and every correction is made either in this
manuscript or in an explicitly dated corrective interpretation beside the original.

**Deterministic extraction, and its boundary.** The supplementary per-instrument inventory and the
separate results file are generated by
`research/autonomy/opus-capacity-campaign-20260908/paper-lane/MF1-repair/extract_mf1_inventory.py`, which
reads the named committed records and copies named fields. ⭐ **Corrected 2026-09-09: that script writes
FOUR outputs, and the supplement is one of them** — the results file, the inventory, the dependency
manifest and `degrader-methods-failure-record-SI.md` itself. It runs no simulation, docking, co-fold,
fetch or re-analysis. ⚠ **Not every number in its outputs is parsed at runtime.** Most are read from a
named field of a named committed input or counted in one, but a few are **authored constants transcribed
from retained evidence** — the E1 design figures **24** declared and **2** excluded-before-execution legs
(from `selectivity-sensitivity-control-prereg.md` AMENDMENT 1; only the admitted **22** is read, from
`selcal-verdict.json`), and the benchmark and `1/462` figures quoted inside the author-current scope
prose. Each such source is in the script's input list and is therefore hashed into the manifest, so a
reader can check a transcribed constant against the bound source; the script does not check it. ⛔ **One
display omission is labelled rather than silent:** the `V5` result cell is a source excerpt with the
fragment *"~34× the statistical uncertainty"* omitted, because the record supplies no estimand for that
ratio (§4.2, C5); the original field is unedited at its source and no replacement multiplier is adopted. ⚠ **It also carries an explicit author classification** — the four separated audit axes,
the reading notes and the author-current scope column of §S2 — written out in the script so a reader can
check the mapping rather than trust it. **The prose of this manuscript is authored, not generated.** Its
input manifest, with sizes, SHA-256 digests of the bytes actually read, version-control blob identities
and the recorded result of comparing the two, is `MF1-dependency-manifest.json` in the same directory.

⚠ **What this paper does NOT assert is any claim about how often the field publishes negatives.** The
earlier framing rested on the clause *"the field publishes almost none of them"*, and on the residual
phrase *"in the form the field is short of"*, neither of which this repository can support with a
measurement or a citation. Both are removed. The first is preserved as a superseded standing view in
[`CLAUDE-history.md`](../../../CLAUDE-history.md); no bibliometric survey was run, none is proposed, and
nothing in the argument depends on one.

---

## 4 · The quantitative record

⭐ **This section reverses the earlier draft's deliberate omission of its own numbers.** The previous
version restated no figure, on the reasoning that a second copy is where a number goes stale. That
reasoning is sound about drift and wrong about a preprint: a reader could not check a quantitative
methodological argument without traversing a 616-kilobyte roadmap and a set of registers with different
denominators, some of which contradict the artifacts they cite. The table below is therefore **read from
the named artifacts by the extraction script rather than typed**, and each row carries the interpretive
limit that travels with its number.

⚠ **Corrected 2026-09-08 (R3) — what is generated and what is authored.** The earlier claim that this
material *"cannot drift"* is withdrawn, and the boundary is drawn where it actually falls. The
**supplement** and the separate results file are **deterministic extraction** of named fields from named
committed inputs, **plus explicit author classification** — the script also carries hard-coded axis
labels, descriptions and interpretive sentences, which is permissible author synthesis and not
self-updating evidence. The **prose of this section is authored synthesis**, not generated output: the
extraction writes the results file and the supplement, not these paragraphs. What replaces "cannot drift"
is a **verifiable binding**: every input's path, byte count, SHA-256 of the bytes actually read, the
version-control blob identity of the same path, and whether those two agree, are recorded in
`MF1-dependency-manifest.json`. ⛔ A working-tree read plus a `HEAD` blob identity is **not** sufficient
binding unless the bytes actually read match that blob, so the manifest now records that comparison
explicitly instead of assuming it. The 17-versus-18 count corrected at §9.4 is a concrete instance of
drift between authored prose and extracted display.

The full table, with every column, is
[`MF1-quantitative-results.md`](../../autonomy/opus-capacity-campaign-20260908/paper-lane/MF1-repair/MF1-quantitative-results.md);
it is reproduced in the supplement. The columns are: control/reference identity · operational criterion ·
unit · eligible, excluded, failed and unrun counts · estimate · uncertainty type · actual result ·
interpretive limit · source. The ten records it covers are the endpoint-MD sensitivity calibration, the
5a-KS double difference, the valB_mini calibration and its closure triangle, the decoy pass-through, the
generation-frame druggability gate, the `V1` descriptor over the generated ternaries, the cross-method
pose attribution, the anti-target self-control, the covalent-panel object census, and the external
benchmark preparation record.

### 4.1 · The four quantities the argument turns on

**(a) The endpoint-MD sensitivity control (`V11`).** Recorded in
[`selcal-verdict.json`](../../modalities/selcal-verdict.json): arms of **6** and **5** admitted model
means, **22** legs admitted, **0** rejected records, **0** technical failures in either arm; statistic
**+0.4373 Å** (the sign opposite to the one the criterion required); exact one-sided permutation
**p = 0.746753** over **462** arrangements, mirror **p = 0.255411**; recorded tier **`NULL`**; register
control state **`fails`**. The reference set's attainable minimum p-value is **1/462 ≈ 0.0021645**.

⚠ **The exclusion account, completed 2026-09-08 (R3) — three different stages, reported separately.** The
earlier text gave "22 admitted, 0 rejected records, 0 technical failures" without its excluded model, so
the denominator read as if nothing had been excluded. The retained pre-registration's **AMENDMENT 1**
records the stages explicitly
([`selectivity-sensitivity-control-prereg.md`](../../modalities/selectivity-sensitivity-control-prereg.md)
`:26–31`): the frozen design is **24 legs**; **one co-fold model, SMARCA4 seed 3 — 2 legs — was excluded
before execution on a measured static input fault**, under a clause the document states was frozen in
advance; the **admissible panel is 22 legs**, which is what executed. ⛔ **`rejected_records` = 0 is a
collector-stage count and is a different stage from that model-level exclusion**; 0 technical failures is
a third. ⚠ The sampling unit of the reported statistic is the **model mean** (6 versus 5), not the leg.
⛔ This states an exclusion the record already holds; it makes no new eligibility decision, and the
attribution that the excluding clause was frozen in advance is the retained protocol's, not an
established chronology (§9.6).

⛔ **What the floor is and is not.** It is the smallest p-value this design can produce, a property of
the number of label arrangements. It is **not** power. No power calculation against an effect size was
performed, and none is manufactured here from the observed effect. Three further limits are on the
record and belong beside the number: the panel's own module states that this observable has **no
established quantitative link to degradation selectivity**; the reference the criterion text names
(**ACBI2**, Kofink *et al.* 2022) is not the reference the panel's own `reference` block establishes
direction from (**PRT3789**, Cancer Research 2026, `doi:10.1158/0008-5472.can-25-1141`, not open access,
so no magnitude is quotable); and the promised co-fold-versus-crystal validation of the panel's inputs
**had not been implemented before the panel ran**, with all twelve scored co-folds recording low-quality
target↔E3 placement. ⚠ The identity correction is made **here and in current summaries**; the original
historical bytes of `selcal-verdict.json` and `selcal_panel.py` are unchanged and stand as the record of
what was actually run.

**(b) The 5a-KS ligand-side double difference `S` (`V16`).** Recorded in
[`nr4a3-5aks-reduction.json`](../../modalities/nr4a3-5aks-reduction.json): **S = −0.1297 kcal/mol**, with
a dispersion of **0.3264 kcal/mol** whose recorded kind is **`replicate_sd`** — a **two-seed** between-seed
spread per arm, combined across arms. ⛔ **That is not a confidence interval, an equivalence test, a
likelihood bound or a calibrated physical-effect bound**, and the earlier claim that this quantity
excludes effects of roughly 0.65 kcal/mol at "2σ" is withdrawn. `S` is an **exploratory conditional
estimate compatible with zero at the observed precision**, and its design's operational completion
condition (seeds per arm) was met.

⚠ Two assumptions have to travel with it. First, **comparability**: the record flags
`system_identity_problems` on particle count across the four legs. Differing water counts do not by
themselves prove invalid physics, and cross-species systems need not have identical counts — but the
manuscript may not treat the calculation as an unqualified bound while that flag is open. Second,
**modelled causality and reference state**: the intervention here is on the **modelled ligand Hamiltonian,
conditional on the chosen structures**. It is not a biological causal test of degradation or of covalent
selectivity, and the first-order cancellation of the opening penalty inside a relative matched-pair
quantity (§8.2 item 2) holds only under a common reference state and ensemble, which is an argument and is
recorded as one. `V16` has **no known-answer calibrator at all**, so `S ≈ 0` cannot separate *"there is no
wedge effect"* from *"this method cannot resolve the wedge effect"*.

**(c) The valB_mini calibration and its closure triangle (`V5`).** The calibration recovered the **wrong
sign** in every one of three replicates, at an absolute error of **1.543 kcal/mol**
([`valb-failure-propagation.json`](../../modalities/valb-failure-propagation.json)). That is the retained
result and it stands: a **repeated wrong-sign operational calibration failure**.

⛔ **What the closure triangle does not add.** The single-seed triangle
([`valb-triangle-reduction.json`](../../modalities/valb-triangle-reduction.json)) reports
**R_ternary = −0.0312**, **R_binary = −0.2440**, **R = +0.2128 kcal/mol**, with the record's own error-bar
field reading `NONE QUOTED AT n=1`. The earlier draft, and the roadmap entry it follows, read a small
residual as showing that the miss is an endpoint-state error and that more sampling will not fix it. That
inference does not hold, for three reasons that are on the record. (i) The residual is **one linear
contrast of six edge errors**: errors of 1, 2 and 3 on the three oriented edges close exactly while every
edge is wrong, and a conservatively structured bias from shared incomplete sampling can telescope the same
way. (ii) The closure artifact
([`valb-triangle-closure.json`](../../modalities/valb-triangle-closure.json)) itself states that
endpoint-state errors are **invisible** to closure — which makes it blind to that class, not diagnostic of
it. (iii) The propagation record gives power ≈ **0.63** to detect an r0-sized path error at its own
measured upper noise bound, which is not a clean exclusion; and its "upper bound" on the per-leg sigma
from three replicates is not a confidence bound on the underlying variance. **Repetition of a wrong sign
strengthens the observed calibration failure and does not identify its cause.** The claims of unique
localisation, of excluded sampling error, and of no remediation by sampling are withdrawn from this paper
and from the current summaries it asks a reader to treat as authoritative.

⚠ **Nor is convergence established.** The retained diagnostic account for this lane reports binary-arm
ligand departure and a convergence state of `MEASURED_FAILURE`. A passed closure or forward/reverse
antisymmetry statistic is a selected diagnostic, not a general convergence certificate, and the earlier
draft's *"converged sampling … all present"* is corrected accordingly.

**(d) The decoy pass-through (`V20`).** The archived canonical output
(`results/nr4a3-decoy/-mmgbsa/nr4a3-mmgbsa.json`, the one of three archived MM-GBSA arms that reproduces
the committed constant) records **22 of 38** selected unrelated marketed drugs scoring a positive minimum
margin against the closer paralogue under single-snapshot MM-GBSA. ⛔ **That is a positive-call rate among
these selected decoys under this scoring configuration.** It is **not** a measured biological
false-positive rate: the archive supplies computed scores and computational labels, not measured NR4A
negative labels. The calibration module states that the distribution depends on the receptor frames used,
and the same background is used elsewhere to identify an above-background candidate — so the finding is
evidence **against reading `margin > 0` alone as a selectivity verdict**, and not evidence that no
downstream method can extract useful information.

### 4.2 · The benchmark identities, reference values and results already in the register

⭐ **Added 2026-09-08 (R3).** The earlier draft reported the *grades* of the known-answer benchmarks —
"recovered within the accepted band", "large absolute bias", "approximately recovered", "recovered a large
effect" — without the identities and numbers that let a reader judge them, although the frozen register
already held both. They are copied here with their provenance.

| instrument | benchmark identity, as the register names it | reference / known answer | result as recorded | discrepancy, as recorded | uncertainty type |
|---|---|---|---|---|---|
| `V5` | reproduce a known ternary cooperativity | **+0.944** kcal/mol | **−0.599** kcal/mol | absolute error **1.543**; **wrong sign in all 3 replicates** | ⚠ **unknown** — no uncertainty term is attached to either value in this row |
| `V6` | TYK2 `ejm_31→ejm_42` relative-FEP benchmark ΔΔG | **−0.24** | **+0.37** | absolute error **0.61**, inside its operational **≈1 kcal/mol** band | ⚠ **unknown** |
| `V7` | T4-lysozyme L99A + benzene, absolute binding free energy | **−5.2** kcal/mol (experimental) | **+1.90 ± 0.09** | under-binding by **≈ +7.1** kcal/mol | ⚠ a ± is quoted on the result only; **its kind is not established in the cited record** |
| `V8` | methane hydration free energy (FreeSolv) | **+2.0** | **+1.60 ± 0.04** | *"approximately reproduced"* | ⚠ a ± is quoted on the result only; **its kind is not established in the cited record** |
| `V10` | barnase–barstar Y29A interface mutation, against a published ΔΔG | **+3.4** | **+4.42 ± 1.08** | recovered a large effect | ⚠ a ± is quoted on the result only; **its kind is not established in the cited record** |

**Provenance, stated exactly.** Every cell is copied from
[`instrument-census.json`](../../modalities/instrument-census.json), fields `known_answer_test` and
`result` of the named instrument — `V5` at `:69` and `:71`, `V6` at `:84` and `:86`, `V7` at `:98` and
`:100`, `V8` at `:112` and `:114`, `V10` at `:140` and `:142` — and that census is itself generated from
[roadmap §3.1](../nr4a3-program-map.md#31--the-instrument-table).

⛔ **What these are and are not.** They are **retained register values**, not new measurements and not an
independent verification of the primary experiments behind them. No benchmark was rerun, no primary
benchmark source was retrieved, and no uncertainty was recomputed. Where the kind of a ± term is not
established in the record it is marked **unknown** rather than named. ⛔ **The `V5` row's further phrase
*"~34× the statistical uncertainty"* is deliberately omitted**: the register does not carry the estimand
such a ratio would need, and the related SD-over-SE multiplier is withdrawn in C5 of the corrective
interpretations. ⚠ A recovered benchmark still licenses nothing beyond its own scope — the fourth column
of §5.2 and the supplement's claim-scope column are part of each of these rows.

---

## 5 · The register, its two denominators, and what its labels mean

⭐ **ONE HOME for the machine-readable register:**
[`systems/views/registers/instruments.md`](../../../systems/views/registers/instruments.md), generated
from `systems/graph/*.json`; the annotated register is
[roadmap §3.1](../nr4a3-program-map.md#31--the-instrument-table). This section states the architecture and
the counting rules; the per-instrument detail is in the supplementary inventory.

**The register's governing rule, and the paper's methodological thesis in one sentence:**

> An instrument that has never recovered a known answer **cannot support a claim, however good its output
> looks.** An instrument whose control **failed** and one that has **no control** are different facts — and
> **neither is support.**

Two corollaries a reader can take away directly:

- ⛔ **A `PASSES` means the instrument recovered *that* known answer. It never means the instrument
  supports the claim the register points it at.** A structural descriptor that recovers one contact in one
  crystal pair has recovered one contact in one crystal pair.
- ⛔ **The claim-ceiling rule.** A requirement may never be claimed above the validation status of the
  weakest instrument that produces it. An instrument with no result sets the ceiling at *unvalidated
  prediction*; one whose control failed sets it lower
  ([roadmap §2.3](../nr4a3-program-map.md#23--the-claim-ceiling-rule-stated-so-it-can-be-checked)).

### 5.1 · Two denominators, an inclusion rule, and one administrative word

The route record `RT-METHODS-PAPER.instruments` partitions the instruments **this paper cites** into two
lists: **four** as `support` (`V1`, `V6`, `V8`, `V10`) and **sixteen** as `disclosed_failing` (`V3`, `V4`,
`V5`, `V7`, `V9`, `V11`, `V12`, `V13`, `V14`, `V15`, `V16`, `V17`, `V19`, `V20`, `V21`, `V22`).

⚠ **The inclusion rule, stated so the denominator can be checked.** A numbered instrument enters this
partition when the route cites it. **`V2` and `V18` are in the numbered census and outside this
partition** — `V2` is the ternary generator given both sites, which is relevant to the assembly-route
examples §7 discusses and was never pointed at this program's own system; `V18` is a set-membership screen
with no control of any kind. So the numbered census carries **twenty-two** entries and the route partition
**twenty**. ⛔ **The two counts are read from their own sources and are never added or subtracted to make
a third.**

⛔ **`disclosed_failing` is an administrative route label, not a scientific failure total.** It covers at
least five materially different facts, and the supplementary inventory separates them on four independent
axes — control type and availability, execution and eligibility, inferential outcome, and claim scope —
because the earlier draft's four-row table mixed those axes and lost information:

| the fact underneath the label | examples | what it actually says |
|---|---|---|
| **a known-answer control that DID NOT RECOVER** | `V5`, `V7`, `V12`, `V17`, `V21` | the instrument was put to an independently established answer and did not return it |
| **a control that RAN AND DID NOT RESOLVE** | `V3` (inconclusive by its own rule), `V22`'s known-answer arm (zero gradeable of twelve listed) | the test executed and returned a third outcome |
| **a NONDETECTION under a registered operational criterion** | `V11` | the instrument ran, nothing broke, and it did not separate the pair at its criterion — an executed calibration attempt, not an absent control and not a demonstration of insensitivity |
| **a failed MECHANISM HYPOTHESIS, or a NEGATIVE control, which is not a known answer** | `V13` (a two-state opening hypothesis), `V15` (permutation nulls), `V19` (the scrambled-objective arm) | not a failed recovery of an independently established truth; `V19` additionally has one arm executed and its decisive generative arm **unrun**, which a single row cannot carry |
| **no control EXISTS** | `V9` (a self-consistency diagnostic), `V14`, `V16` | nothing has ever graded it, which is a hole and not a failure |
| **the control was never RUN** | `V4` — the *selectivity* free-energy known-answer test, built and staged with no result key, never completed and not authorised | ⛔ the single most uncomfortable row in the register: the one test designed to grade selectivity free energy directly is the one that was never bought |

⚠ **`V22` is the row the earlier draft got wrong, and it is instructive.** Saying *"no control exists"*
for it is imprecise: a known-answer panel of twelve apo/holo pairs was **attempted** and returned **zero
gradeable cases**, for four distinct recorded reasons (§7.2). An attempted control that returns no grade
is a different fact from an absent control, and both are different from a control that returned an answer.

⭐ **Naming `V4` in the paper is not self-flagellation; it is the audit's integrity check.** A register
that listed only the tests that ran would be exactly the selective reporting this audit is written
against.

### 5.2 · The four that recovered their known answer, and what each does not cover

The support column is short and every entry is narrow. Stating the narrowness is what makes the rest of
the record credible.

| id | what it recovered | ⛔ what that does **not** cover |
|---|---|---|
| `V1` | a published interface hydrogen bond, unaided, from two crystals | **one contact in one pair, under one polar-contact descriptor**, and the criterion was corrected after an initial miss on that same known answer, so it is an in-sample development and harness check. It grades no NR4A3 prediction and it does not grade the endpoint readout `V11` |
| `V6` | a public relative-FEP benchmark, inside the field's accepted band | a **relative** quantity **within one pocket**, on **one charge model**. It is not a selectivity validation, and it does not transfer to the ternary or endpoint lanes, which run a different charge model |
| `V8` | a hydration free energy | a solvation smoke test. It says nothing about a protein site |
| `V10` | a published interface-mutation ΔΔG | a **large** effect. No benchmark in the register probes the regime that matters here — resolving a paralogue-scale difference between two closely related receptor states |

⛔ **The `V6` line is the one most likely to be misread by a reader and was misread inside the program.**
The published accuracy of the underlying protocol was established on one charge model; the ternary and
endpoint lanes run another, and the split is physically forced rather than sloppiness. **The accuracy
control for that second lane is `V5` — whose calibration failed.**

---

## 6 · ⛔ THE SPINE — outcomes that are routinely summed into one

**This is the section the paper exists to write, and getting it wrong would be worse than not writing
it.** Five results in this program are routinely confused with one another. Summing them into
*"everything came back null"* is a category error; so is summing them into *"everything failed"*.

⭐ **The numbers for every row below are in [§4](#4--the-quantitative-record) and in the generated
results table.** This section states the taxonomy and the argument.

| # | result | instrument | outcome word | why it has that word |
|---|---|---|---|---|
| 1 | **valB_mini** — the alchemical ternary cooperativity calibrator | `V5` | ❌ **CONTROL DID NOT RECOVER** | it returned the **wrong sign** of a known cooperativity in every preregistered replicate, at 1.543 kcal/mol absolute error. An accuracy failure. ⚠ Its **cause is not identified**: closure cannot localise it (§4.1c) |
| 2 | **selcal SMARCA2/4** — the endpoint-MD sensitivity control | `V11` | ⚠ **EXECUTED CALIBRATION ATTEMPT, CRITERION NOT MET** | it ran with no technical failures in either arm and did not separate a pair whose selectivity a primary source reports, at p = 0.746753 with the difference in the opposite direction. ⛔ **Not** an adequately-powered null: no effect size is established and the p-floor is discreteness, not power |
| 3 | **NR-V04 retrospective** — the biological holdout | `V11` | ⚠ **INELIGIBLE, and never a candidate control** | it returned `DISCORDANT`. It is also **covalency-confounded** — the published selectivity is attributed to a covalent bond at a cysteine the other two paralogues lack — so a geometry readout would have passed for the wrong reason **at any sample size** |
| 4 | **RUNG 5a-KS** — the causal matched-pair test | `V16` | ⚠ **EXPLORATORY ESTIMATE, THE OUTCOME ITS RETAINED PROTOCOL DESCRIBES AS PREREGISTERED** | ⚠ the retained protocol **describes** this outcome as registered in advance as the likely one and explicitly not a stop; the chronology itself is unestablished (§9.6). Its operational completion condition was met. ⛔ It returned an **estimate compatible with zero at two-seed dispersion**, **not** a bound and **not** proof of an absent wedge |
| — | **apo pose recovery** — the blind-docking benchmark | `V3` | ⚠ **INCONCLUSIVE by its own preregistered rule** | the protocol's own ceiling missed, so the run measured the **site selection** rather than the docking. A test that cannot resolve is a distinct outcome and this one has been mis-read as a failure |

### 6.1 · Why #4 is not a failure — and why it is not a bound either

The distinction has to survive a hostile reading, so it is made on the instrument's construction rather
than on intent.

The Tier-3 quantity `S` is an ordinary **non-covalent** alchemical double difference. **It models no bond
in either leg.** The paralogue claim the program actually rests on is *categorical* — a chemistry present
in one paralogue and absent in the others — so `S` is **structurally incapable of testing it**. What `S`
can see is the *marginal* wedge, whose expected magnitude ⚠ **the retained protocol describes as
registered in advance** as likely to be unresolvable at the design's sampling. ⚠ **Corrected 2026-09-08
(R2):** that is an attribution to the retained protocol, not an established chronology (§9.6).

⛔ **And the honest half of the same paragraph, corrected.** A recorded rule saying that a null is likely
and is not a stop is a **decision rule**, not an equivalence result. It does not convert an uncalibrated estimator
into a bound, and it does not establish that the marginal wedge is absent. What the design bought is a
recorded estimate and its between-seed dispersion, reportable as such. `V16` has **no known-answer
calibrator at all** and buying one is on nobody's rung; the program's own ruling is that `S` may not be
reported as calibrated, and this revision adds that it may not be reported as a bound either.

### 6.2 · What IS bad — and it is #1–#3 together, not #4

After **three recorded attempts** there is **no working positive control for paralogue-selectivity
detection**. The fourth candidate, `V4`, is **built and staged with no result** — never completed, not
authorised (§5.1) — which is a different state from "not staged" and changes the claim ceiling by nothing.
That, and not the preregistered estimate, is why every paralogue-selectivity statement the program makes
is an **unvalidated prediction** — a consequence carried in
[`selectivity-resolution-options.md`](../../modalities/selectivity-resolution-options.md) §4 and
machine-carried by `selcal_gate.NEXT_STEP_BY_TIER`. ⚠ **Corrected 2026-09-08 (R2):** the retained
protocol **describes** that consequence sentence as written before the deciding run; this paper does not
present the revision, amendment-timing or first-outcome-access records that would establish it, and the
earlier affirmative *"before the deciding run"* wording is withdrawn (§9.6). ⛔ **The reading of `S` and
the program's stop decision do not depend on that chronology.**

⚠ **#1 and #2 are DIFFERENT INSTRUMENTS and neither invalidates the other's numbers.** One is alchemical
ternary FEP; the other is endpoint-MD interface stability. They also fail differently: one returns a known
answer *backwards*, the other does not separate a known pair at its criterion. Reading them as a single
finding would overstate both.

⛔ **But different instruments do not make three independent validations.** #2 and #3 are both `V11`
applications sharing an E1 readout and a scorer; the alchemical and E1 lanes are different instruments and
still share this program's code, its structural **assumptions** and its selection decisions — ⚠ **not, as
the earlier wording implied, one co-folding route or identical structural input artifacts (§9.6, corrected
2026-09-08)**. They are **three recorded attempts assembled retrospectively**, and the paper does not label
them independent confirmations of a single scientific proposition. §9.6 gives the shared dependencies
explicitly.

### 6.3 · What the SMARCA2/4 result does not license

⛔ **First, what the recorded word NULL is doing, because it invites exactly the wrong reading.**
[`selcal-verdict.json`](../../modalities/selcal-verdict.json) records `tier: "NULL"` with *p* = 0.746753
and `technical_failures` of **0** in both arms. That label describes the **statistical result**: the
instrument ran, nothing broke, and it did not separate the two paralogues at its criterion. ⛔ **That is a
control that was executed and did not meet its criterion, not an absent one** — the register's control
state for `V11` is `fails`, not `none`. Reading it as "no result" would quietly move this instrument into
the no-control-exists row of §5.1, where it does not belong. ⛔ **And reading it as a powered demonstration
of insensitivity would move it into a row that does not exist**, which is what the earlier draft did.

Four bindings, all reproduced here because a methods paper that reports a negative without its limits is
doing the thing this paper criticises:

1. ⛔ **It does not distinguish "the readout is blunt" from "this pair is hard."** The record does not
   separate an insensitive E1 readout from an unsuitable or structurally narrow test, and the validity of
   the panel's inputs is unresolved besides (point 3). ⚠ **Corrected 2026-09-08 (R5): the earlier sentence
   *"the published selectivity turns on a single hydrogen bond"* is withdrawn at this point of use.** The
   panel's own module attributes that single-hydrogen-bond statement to a mechanism citation about the
   **SMARCA2BD/SMARCA4BD pair against VCB** (Kofink *et al.* 2022, `doi:10.1038/s41467-022-33430-6`,
   PMC9551036) and records in the same field that it is *"NOT a claim about the reference ligand"* —
   i.e. not about **PRT3789**, which is the reference this panel's `reference` block actually establishes
   direction from (§6.4, `selcal_panel.py`). ⛔ **Transferring that mechanism to the PRT3789 panel is an
   unestablished mechanistic rationale, not a finding**, no expected structural magnitude is inferred, and
   the primary body of the PRT3789 reference was not retrieved.
2. ⛔ **It does not establish sensitivity, because no effect size is established for this observable.**
   The panel's own module states that this readout has no established quantitative link to degradation
   selectivity. An attainable p-floor of 1/462 says the design *could* have produced a small p-value; it
   says nothing about the probability of detecting a relevant alternative.
3. ⛔ **A third reading, measured afterwards, is worse for the instrument than either registered one.**
   Both registered readings assumed the simulated complexes were the complexes whose selectivity was
   published. Scored against the deposited ternaries the panel was designed around, the co-folds reproduce
   the internal E3 machinery well and the degradation-target↔E3 interface **not at all** — so the endpoint
   was never exercised on the complexes in question, and the failing stage is ternary **generation** rather
   than ranking. ⚠ A technically clean MD leg does not establish a physically correct input or an
   adequately sampled observable. That makes this result **weaker** evidence about the readout, and it is
   **not** a route to reopening any selectivity statement.
4. ⛔ **The remediation is that there is none to buy.** The follow-on re-panel was **retired unrun**,
   because its own power section already showed it underpowered against the separations this program has
   measured. A gate that fails and returns "spend nothing further" is a legitimate outcome and is reported
   as one.

### 6.4 · The reference identity, corrected in place

The panel's criterion text names **ACBI2** (Kofink *et al.* 2022) as the source of the difference to be
detected, while the panel's own `reference` block establishes direction from **PRT3789**
(`doi:10.1158/0008-5472.can-25-1141`) and separates a mechanism citation about the SMARCA2/SMARCA4 pair
from a claim about PRT3789. ⛔ **The correction is made here and in the current summaries, and the
historical bytes are preserved.** The primary publication is not open access, so no magnitude, DC50 pair
or fold window is quoted anywhere in this paper, and the panel's own record forbids importing one from a
secondary source.

---

## 7 · The 2026-08-03 sweep — three instruments assembled and assessed in one day

A methods paper benefits from showing the audit *running*, not only its accumulated output. On a single
day, **three instruments** were assessed for the first time — one put to its own never-run self-control,
one given the independent comparator it had never had, one pointed at the receptor frame it had never been
pointed at — and a fourth, preregistered gate landed alongside them. **All four returned a negative**, and
the three instrument tests each ran at zero cost on free CPU. That is the practical argument of the whole
paper: **the audit is cheap, and the program had simply not been running it.**

⚠ This is also the clearest single piece of evidence for §3's ascertainment limit: three instruments that
had been in use acquired their first grade on one day, and one of them — `V21` — had been quoted for
months without a row in the census.

### 7.1 · `V21`, the anti-target docking panel — does not recover its own cognate ligands

Each panel receptor's own crystallographic ligand was re-docked through the identical protocol and graded
against the pose-recovery criterion the program had already frozen elsewhere — **read from the existing
module, not chosen for this test**. **7 of 10** receptors recover; `CYP3A4`, `PXR` and `PPARG` do not, and
the artifact grades `panel_readable: false`. Because every published clause built on this panel is a
*maximum* or an *every-survivor* statement over the whole panel, **one unreadable receptor changes all of
them**. ⛔ **This reaches print** — the affected clauses are in the program's own SI. ⛔ **And the frozen
rule holds:** a failing target may not be dropped, its box may not be re-centred, and no band may be
lowered. The repair that was attempted was a *receptor-completeness* repair applied uniformly to passing
and failing targets alike, and it did not restore readability. ⚠ The inability to justify whole-panel
extrema from a panel with three unreadable members is the finding; it is scoped to this panel and licenses
nothing else.
One home: [`antitarget-selfcontrol.json`](../../modalities/antitarget-selfcontrol.json).

### 7.2 · `V22` against `V3` — two pose methods with disjoint scoring disagree

The primary docking instrument had no independent comparator at all, which is why its INCONCLUSIVE could
not be attributed. A scoring-independent second method was run beside it, at the same boxes, graded by the
same kernel. **No system agrees within the recovery band.**

⛔ **The earlier draft's decomposition was wrong and is corrected.** It read the disagreement as *same
location, different orientation*, from small centroid separations. The retained cavity attribution
([`r5-cross-method-cavity-attribution.json`](../../modalities/r5-cross-method-cavity-attribution.json),
consistent with [`pose-conditionality-census.json`](../../modalities/pose-conditionality-census.json))
measures **six systems, of which five are gradeable: four same-cavity and one different-cavity**, with the
sixth ungradeable and therefore excluded from the denominator rather than scored as agreement. The site
itself is two overlapping sub-pockets 9.853 Å apart, both inside the search sphere both engines were
given. **The cavity call is receptor-conformer dependent**, so neither an orientation-only nor a
location-only reading holds across the census. The requirement it serves is recorded `R5_resolved: false`.

⚠ **What this does not license:** not that the pose is wrong, not that either method is wrong, and not
that agreement would have meant correctness. Both methods are docking searches into a fixed receptor, so a
shared receptor-conformer error survives both.

⚠ **And the known-answer half of that comparator produced ZERO GRADEABLE PAIRS.** The panel lists twelve
apo/holo pairs, and ⛔ **twelve listed pairs are not twelve completed docking runs** — every one carries a
recorded disposition short of a grade, and they are four different dispositions, not one:

| n | disposition, as recorded |
|---:|---|
| 2 | excluded by the pre-registered rule **R2b** — the holo ligand is covalently linked (5Y41, 5YD6), and a non-covalent dock cannot reproduce a covalent pose |
| 6 | `second_method._status: "UNRUN — rDock's dock.prm is not readable"` |
| 1 | **fetch** refusal, 1RXR→9QX6 — HTTP 404, no legacy PDB-format file is served for that entry, which the record itself flags as a file-format bias toward older entries rather than a scientific result |
| 3 | **alignment** refusals — 1RXR→6LB4, 1DSZ→9GFE, 1DSZ→3KMR |

⛔ **The unreadable-`dock.prm` cause belongs to the six UNRUN entries and to no others.** The remaining
four did not fail for that reason, and an earlier version of this paragraph said they did. A zero gradeable
is therefore not evidence that the arm was never attempted, and it is equally not evidence that twelve
docking runs were performed and came back empty. ⚠ **Six actual cross-method pose comparisons did
execute**, which is why *"the method never ran"* would also be false. Nothing was re-run to establish any
of this; the dispositions above are read from the retained record as it stands.

Two homes: [`pose-second-method.json`](../../modalities/pose-second-method.json) and
[`pose-conditionality-census.json`](../../modalities/pose-conditionality-census.json).

### 7.3 · The generation-frame druggability gate

The *exact receptor frame the de-novo campaign generated into* was scored under the harmonized detector
and returns **0.259** against the program's own preregistered threshold **D\* = 0.53**, verdict
`GATE_A_FAIL_BELOW_DSTAR`. ⛔ **The transferable reading, stated at its actual scope: this is the failure
of one operational screening gate on one receptor frame.** It is not a demonstration that nothing binds
this pocket, not a statement about ligand-induced states, and not a theorem about every molecule generated
there. The earlier draft's one-line reading — *"a candidate cannot be better than the pocket it was
designed into"* — is withdrawn as a universal claim; what the record supports is that **this program's own
gate refused this frame**.
One home: [`r3-generation-frame-harmonized.json`](../../modalities/r3-generation-frame-harmonized.json) →
`verdict`.

### 7.4 · The ternary rebuild's preregistered three-arm gate returned `NO-GO`

The assembly-route ternaries do not discriminate the target from its paralogues: of the three registered
arms, the sequence-encoded arm passes, the reproducibility arm is INDETERMINATE with no column passing,
and both tether-geometry conventions fail. ⛔ Whatever it says is **structural** — no free energy is
computed, and nothing about affinity, degradation, efficacy or safety follows.
One home: [`nr4a3-5bt-gate.json`](../../modalities/nr4a3-5bt-gate.json) → `verdict` / `sentence`.

### 7.5 · The deepening of §7.4, scoped to its descriptor

The instrument used is `V1`. Run over every model of the focus arm, it finds **no qualifying
sequence-variable discriminating contact in any of the 16 NR4A3 models**.

⛔ **The scope of that sentence is the whole of its content, and the earlier draft overstated it.** The
descriptor is explicitly a **heavy-atom polar-contact proxy** — an N/O pair within 3.5 Å on a side-chain
polar atom, at an aligned position where the residue itself differs — and not a measured hydrogen bond.
Its known-answer recovery is **one contact in one crystal pair**, and the criterion was corrected after an
initial miss on that same known answer, which makes it an in-sample development and harness check with a
narrow scope. So the supported statement is: **these generated structures provide no contact-based
justification, under this descriptor, for a selectivity claim.** ⛔ It is **not** established that no
discriminating contact of any kind exists, that the descriptor is sensitive to hydrophobic contacts or
energies, or that this is the "strongest" negative in the record — the earlier draft's unmeasured ranking
is removed. ⚠ The structures themselves come from a co-folding route that scores DockQ 0.023–0.046 on the
one system where a crystal exists to check it.
One home: [`nr4a3-5bt-signature.json`](../../modalities/nr4a3-5bt-signature.json) →
`sentence_replicated`.

---

## 8 · What this program's records establish about the boundary

The paper's second contribution is a **boundary**, drawn from this program's own retained records rather
than argued from first principles. ⛔ **Every item below is a statement about what these records show, not
about what any method can do in other hands.**

### 8.1 · What the records show a program CAN do

1. **Grade its own instruments, cheaply.** A known-answer test costs close to nothing and, in this
   program, repeatedly changed what could be claimed — every instrument in §6's table was reclassified by
   the test it was put to rather than by an argument about it. ⚠ **And the honest limit on that lesson,
   from this program's own record: a known-answer test can itself fail to return a grade.** The
   known-answer arm of the second pose method returned **zero gradeable pairs** (§7.2) and `V3`'s control
   returned INCONCLUSIVE by its own rule. A test that returns no grade is cheap and is still not free: it
   buys a disposition, not a verdict.
2. **Refute an operational rule on evidence.** Pushing 38 unrelated marketed drugs through the identical
   funnel showed that **22 of 38** score a positive margin, which retires `margin > 0` as a selectivity
   verdict in this pipeline. ⛔ **Stated at its scope:** that is a positive-call rate among selected decoys
   under this scoring configuration, not a measured biological false-positive rate, and it does not
   exclude a design class or show that a downstream method cannot extract information from these scores.
   The earlier draft's *"exclude a design class"* and *"a signal smaller than its own noise is not
   recoverable by any downstream method"* are withdrawn.
3. **Report a conditional estimate with its dispersion.** A preregistered test that meets its operational
   completion condition returns a recorded estimate and a recorded spread, which is a quantitative
   statement and not an absence — ⛔ and, without a calibrator or an uncertainty analysis, is **not** a
   bound (§6.1).
4. **Calibrate a screen against a measured background.** A categorical screen was, until recently, an
   enrichment over an *unmeasured* background. Pushing unrelated close paralogue pairs through the
   identical pipeline converts *"the categorical gate fired"* into *"the categorical gate fired against a
   measured background"*. ⚠ The background so measured is a **nuclear-receptor** background, not a
   proteome one, and the artifact states that as a limit. ⛔ With the caveat that travels with it: the
   program's headline residue falls outside one of the two preregistered scopes, and a preregistered
   window may **not** be widened after seeing what fell outside it.

⛔ **Withdrawn from this list: "refute a published method's claim from that method's own released data."**
See §9.5. The retained pointer does not establish the comparison that claim requires, so the claim is not
made.

### 8.2 · What the records show a program CANNOT do — and the first item is permanent

1. ⛔ **Answer whether anything binds.** The requirement `R4` has **no in-silico instrument** in this
   program; a bench measurement is the only answer. Under a permanent no-wet-lab regime that is a
   **structural** limit, not a scheduling one, and every conditional statement in the program inherits it.
   ⚠ Stated as this program's position and not as a theorem about all computation.
2. ⛔ **Supply the opening penalty.** Selectivity computed only in matched pre-opened pockets can **miss
   or reverse** the true ordering, because each paralogue may pay a different price to open. The
   defensible position is to report everything **explicitly conditional on the chosen open states**. ⚠ One
   narrowing, carried because it is a real methodological point: the opening penalty cancels to first
   order inside a **relative** matched-pair quantity — **under a common reference state and a common
   ensemble**, which are assumptions and are recorded as such, not measurements. It blocks the absolute
   route and not the conditional relative one.
3. ⛔ **Convert a within-run precision diagnostic into accuracy.** A closed thermodynamic cycle and
   forward/reverse antisymmetry were both recorded on the calibrator that returned the **wrong sign**.
   Closure is identically zero for endpoint-state error, so it returns clean whether or not that defect
   exists. ⚠ **And the converse does not follow:** a clean closure does not identify the cause, does not
   exclude shared sampling bias, does not certify convergence, and does not show that more sampling cannot
   help (§4.1c).
4. ⛔ **Test a categorical mechanism with a non-covalent double difference** ([§6.1](#61--why-4-is-not-a-failure--and-why-it-is-not-a-bound-either)).
5. ⛔ **Say anything proteome-wide.** The only off-target breadth this program holds is a ten-receptor
   panel, and that panel is currently unreadable (§7.1). ⛔ **No proteome-wide selectivity claim is made or
   implied anywhere in this paper.**

### 8.3 · One requirement-level lesson worth its own paragraph

The program stated its selectivity requirement **symmetrically** — *"selective over both paralogues"* —
for months, and the retained genetic evidence is **asymmetric**. ⛔ **The asymmetry is named, and it is not
the one the program had been reading.**

- **NR4A1** is the hard constraint: the combined `Nr4a1`/`Nr4a3` loss genotype carries a postnatal
  lethality annotation with a primary citation (PMID 17515897; corroborated at PMID 29343483), and a
  degrader that is not selective against NR4A1 raises a **concern about combined loss**. ⚠ It does **not**
  "reconstitute a knockout genotype": no pharmacological equivalence between a germline null and adult
  transient partial degradation is measured anywhere in this record, and that wording is withdrawn.
- **NR4A2** is **no longer unbounded**. Complete germline `Nr4a2` loss has a phenotyped, primary-cited
  survival consequence (neonatal lethality, complete penetrance; PMID 9092472, PMID 9608532), so there is
  a floor under how much sparing is required
  ([`nr4a2-sparing-bound.json`](../../modalities/nr4a2-sparing-bound.json)).

⛔ **The caveat that travels with both.** A germline mouse knockout bounds **developmental, complete,
lifelong** loss of a gene; a degrader is an **adult, transient, incomplete** loss of a protein, and no
source read here measures that. A knockout phenotype sets a ceiling of concern, never the expected effect
of a molecule; and an absent knockout record is an absence of evidence, not evidence of tolerability.
**Nothing here licenses degrading anything, and no safety statement is made.** The transferable point is
that **a requirement written as one clause with two comparators hid a design target for months**, which is
a cheap error for any program to repeat.

---

## 9 · The infrastructure incidents, separated

The earlier draft merged four distinct defects into one "largest retraction" and drew an incorrect
universal lesson from the merger. ⛔ **They are separated here, each with the panel it actually affected**,
because separating input, execution and analysis defects is the distinction this audit exists to teach.
The word *largest* is removed: no measure of magnitude is defined for it.
Primary source: [`nrv04-cofold-chain-forensics-2026-07-24.md`](../../modalities/nrv04-cofold-chain-forensics-2026-07-24.md).

### 9.1 · Contaminated inputs — the descriptive and shakeout co-folds, NOT the completed panel

A module constant supplied the wrong UniProt accession, so co-folds built on 2026-07-11 carry **14-3-3ε in
place of Elongin B**. The forensic record measures this per prefix: the `nrv04-descriptive-v3` and
`nrv04-shakeout` assemblies are **affected**; the **completed covalent feasibility panel's inputs,
regenerated on 2026-07-22 after the constant was corrected, are clean of this defect**. ⛔ **The earlier
draft attributed the contamination to the completed panel. The retained source establishes the
opposite**, and the claim is corrected here. What the contamination does cost is the exploratory co-fold
ternary benchmark's *positive* paralogue separation, which is not supportable as stated from those
assemblies.

### 9.2 · A wrong interface — post-processing, on the completed panel

A positional chain-split rule selected the last protein chain in sorted order and therefore took **Elongin
C** as the degradation target. The completed panel's R1 (interface RMSD), R2 (recruitment) and R3 (lysine
presentation) consequently describe the **Elongin C↔rest** interface rather than the intended VHL↔target
interface, and R3 counted Elongin C's lysines. ⚠ The arithmetic reproduces exactly from the landed
plateaus; **it is the interface being measured that is wrong**, which is the definition of a
post-processing defect. Its GO verdict does not survive as stated. An nm/Å **unit error** and a chain-blind
reactive-cysteine search sit in the same class.

### 9.3 · A wrongly simulated physical system — the warhead-only legs

Two `warhead_only` legs tethered the electrophile to an **Elongin C cysteine 12.4 Å away**, because no
nearer Sγ existed: the co-fold had not posed free celastrol in the target pocket at all. ⛔ **This is not a
post-processing defect.** Those legs simulated a different physical system from the intended one, and no
amount of retained coordinate data converts a trajectory of the wrong system into the counterfactual
trajectory of the intended one.

### 9.4 · What persistence would and would not have repaired

A read-only census over two named object prefixes finds **17 final per-leg readout records under
`nrv04-covalent-results/` and 1 under `nrv04-covalent-results-chainfix/` — 18 stored result objects across
both — and zero multi-frame coordinate objects in either survey**: every persisted object is a single
frame or a scalar already reduced against the chain split that was used
([`nrv04-result-forensics.json`](../../modalities/nrv04-result-forensics.json), `by_class.leg_result.n`
and `recompute_verdict.trajectory_objects_found` in each survey). ⛔ **Erratum, 2026-09-08 (R4): the
earlier text reported 17 for the combined two-prefix census. 17 is the first-prefix count; the combined
total is 18, and the supplement's 18 was right.** ⛔ **These are 18 stored result objects, not 18
independent experiments and not 18 originally intended panel legs.** The erratum, and its attribution to
the reviewer's and the adjudication's records rather than to the author alone, is
`research/autonomy/opus-capacity-campaign-20260908/paper-lane/MF1-residual/DENOMINATOR-ERRATUM.md`. ⚠ The
count correction changes nothing about the absent-coordinate conclusion and implies no newly discovered
trajectory. ⚠ **That conclusion is a retrospective one about the surveyed prefixes**, not a proof about
every possible external copy of the data.

⛔ **Two corrections to the lesson the earlier draft drew.**

- **The claim that no known-answer test can catch these defects is withdrawn.** The forensic source says
  the **existing** tests did not catch them, which is a different statement — and the fixes it lists are
  precisely such tests: chain-identity matching by composition, an explicit contaminant-rejection
  signature, a written-out chain split consumed by the driver, per-leg recording of the split actually
  used, and regression tests pinning all of it. A known fixture with reordered chain identifiers, a
  unit-scaled geometry fixture, or a verified chain-sequence reference detects exactly these errors.
- **Persistence is not a universal repair.** Persisted trajectories would have permitted the §9.2
  readouts to be **rescored** for the corrected interface. They would **not** have repaired §9.3.
  Persistence must therefore cover inputs, chain and molecular identities, code and parameter versions,
  *and* trajectories appropriate to the observable; trajectory storage alone is not sufficient.

### 9.5 · The external benchmark claim, withdrawn

The earlier draft claimed that this audit refuted a published method's claim from that method's own
released data — that a benchmark's *unbound* protocol supplied information its label implied it withheld.
The roadmap entry behind that claim asserts an identity of shipped and native ligand coordinates over 66
atoms and points at [`selcal-deepternary-frame.json`](../../modalities/selcal-deepternary-frame.json). The
actual fixed file is a **single SMARCA2 preparation record with 64 degrader atoms**, recording
superposition, snapping and file readability — **not** the asserted 66-atom equality on a released
benchmark case.

⛔ **The refutation is therefore withdrawn.** A mismatch between one user's interpretation of a label and
the released inputs is not, by itself, a refutation of a publication's explicit claim, and the
released-case coordinate comparison and primary protocol statement that such a claim would require were
⚠ **not identified in the retained evidence used here** — corrected 2026-09-08 (R3) from the earlier
repository-wide phrasing, which asserted a global absence this audit did not establish. The scope of that
statement is the evidence actually inspected, and nothing follows about material elsewhere in this
repository or outside it. ⚠ What survives is a finding about **this program's own assumed input
protocol** and the consequent relabelling of the arms built on it, and the in-set positive control's scope
— **memorisation-permitting by construction**, since the case sits inside the model's training horizon.
**Reopening condition:** the exact already-retained released-case comparison, with pinned file identities
and the primary text's statement of what the method withholds. No new source retrieval was performed or
authorised for this revision.

### 9.6 · The chronology and the shared dependencies, stated as a limit

The abstract of the earlier draft said every method used to support a selectivity statement was **first**
put to a test whose answer was already known. ⛔ **That is contradicted by this paper's own history and is
withdrawn.** The actual mixture is: instruments assessed for the first time in August after months of use
(§7); `V9`, `V14`, `V16` and `V18` with no known-answer calibrator at all; `V22` with an attempted panel
that returned no gradeable case; and `V4` never run. What the record supports is that **the audit
retrospectively assembled the grades that exist and enumerated the ones that do not**.

**Shared dependencies of the three recorded attempts**, stated so a reader can judge independence: two of
the three are `V11` applications sharing an E1 readout and the same permutation scorer; the third is a
different instrument in the alchemical lane, and it shares **this program's assumptions, its selection
decisions and its code base**. ⚠ **Corrected 2026-09-08 (R2): shared assumptions and shared code are not
literal identical structural inputs, and the earlier wording *"shares this program's structural inputs,
co-folding route"* overstated the demonstrated relation.** The retained forensic account distinguishes
them at the level of the actual inputs: the valB lane **resolves its chains from RCSB `8G1Q`**, while the
NR-V04 assemblies come from a **different co-fold source**, whose Elongin B sequence was fetched from a
module constant
([`nrv04-cofold-chain-forensics-2026-07-24.md`](../../modalities/nrv04-cofold-chain-forensics-2026-07-24.md),
the `e3-provenance-correction.json` passage). Exact common inputs are stated only where the record
identifies them. ⛔ **This does not restore any independence claim: different instruments or systems alone
do not establish statistical or failure-mode independence.**

**Preregistration, reported only at the attribution the record supports.** ⚠ **Corrected 2026-09-08
(R2).** Several criteria carry explicit pre-run freeze assertions and the consequence sentence for the
endpoint-MD result is recorded in `selectivity-resolution-options.md` §4 — so **the retained protocol
describes these rules, outcomes and consequences as prespecified.** The affirmative claims that they
*were* frozen before their own runs, that an expected magnitude *was* registered in advance, and that the
consequence sentence *was* written before the deciding run are withdrawn as facts and kept only as that
attribution. ⚠ **Current freeze booleans and a current version-control pin do not establish which rule
existed before outcome access.** One preregistration file carries a backfilled date of 2026-08-05 against
an outcome timestamp of 2026-08-02 in the corresponding verdict, and this paper does not present the
individual freeze revisions, amendment timings or first-outcome-access records that a reader would need to
check any chronological claim. ⛔ **This is not evidence of post hoc registration**, and it is not claimed
to be; the actual chronology is **unestablished**, which is a gap in what this paper can demonstrate.
**Reopening condition:** identifiable pre-outcome rule versions, amendments and outcome-access bindings
that are already retained, plus an explicit independence argument for the particular inferential claim.
⛔ **No new chronology audit was run or is proposed, and missing documentation is not a licence for one.**

---

## 10 · Honest scope and limitations

### 10.1 · n = 1, and the paper must say so in the abstract

**One pipeline, one target family, one author.** The audit is complete *within the enumerated records* and
generalises no further. The claim is *"here is what happened when one program's records were audited this
way"*, and the paper must not slide into *"this is what happens"*. **Every instrument verdict is a
statement about this program's implementation of a method, never about the method's published accuracy in
other hands.**

### 10.2 · The unsupported premise, removed 2026-09-08

The sentence *"the field publishes almost none of them"* was carried as a position rather than a
measurement. ⭐ **2026-09-08: it came out** — of this paper's prose and of its endpoint's
`what_it_would_claim` field — rather than being kept open indefinitely against a survey nobody was going
to run. The residual phrase *"in the form the field is short of"* is removed in this revision for the same
reason. The clause is preserved as a superseded standing view in
[`CLAUDE-history.md`](../../../CLAUDE-history.md), labelled historical there; it is not asserted anywhere
in the current text. Nothing else in the paper depends on it.

### 10.3 · Two registers, two denominators

⚠ **The two registers do not share a denominator and must not be summed:** the census counts the
instruments the roadmap's tables carry (22), and §5.1's four/sixteen split counts only the instruments
`RT-METHODS-PAPER` cites (20). Each count is read from its own source. The per-instrument supplement gives
the mapping between them explicitly, including the two census entries outside the route partition.

### 10.4 · The decoy chain's provenance, and what verification bought

The margins are committed in a constant, and more than one MM-GBSA arm was archived — so a file merely
sitting in `results/` would not have said which arm the paper quotes.
[`decoy-null-provenance.json`](../../modalities/decoy-null-provenance.json), generated by
[`decoy_null_provenance.py`](../../modalities/decoy_null_provenance.py), records which committed file the
quoted margins come from and verifies that it reproduces the constant. ⭐ **The verification is the
deliverable, not the copy.** This chain can be inspected end to end from its retained run outputs.

### 10.5 · The unresolved limits, listed rather than dissolved

⛔ These are the questions this paper leaves open, each with the reason it stays open.

1. **The cause of the wrong-sign calibration failure is not identified.** Closure cannot separate the
   candidate causes, and the retained evidence does not contain a discriminating measurement. Reopening
   requires retained evidence that separates the proposed causes.
2. **No effect size is established for the E1 observable**, so no statement about the sensitivity of that
   readout is available at any sample size in this record.
3. **`S` has no calibrator**, so its value cannot be read as evidence about the physical wedge in either
   direction.
4. **The corrected-interface readouts of the covalent panel cannot be recomputed** from what was retained
   under the surveyed prefixes, and two of its legs cannot be repaired by any retained data.
5. **Whole-program ascertainment is not established** (§3), so no failure *rate* over the program is
   reported.
6. **The chronology of prespecification is unestablished** from the retained files: what the record
   supports is that **the retained protocol describes these rules as prespecified** (§9.6). No chronology
   audit was run and none is proposed.
7. **No external publication is assessed** (§9.5), and the absence of the comparison such an assessment
   would need is scoped to the evidence actually inspected, not asserted repository-wide.
8. **`V4` is unrun and unauthorised**, so the selectivity free-energy axis has never been graded directly.
9. ⭐ **CLOSED 2026-09-09 — the four shared-register cells were applied.** This item previously read
   *"Four current shared-register cells still carry withdrawn readings"*. The parent integrator applied
   all four at commit `91609d30fdc672f4dbc9eb191e6342a7ddd4f61d` and regenerated the census, so a reader
   arriving at those cells now meets the dated correction rather than a withdrawn statement (§2). ⚠ What
   remains a limit is narrower and is not dissolved: the manuscript still cannot edit shared registers, so
   any *future* divergence between this paper and the shared census would again have to be named rather
   than fixed here.
10. **The benchmark uncertainty types in §4.2 are unknown** where the record does not establish them, so
    no ± term there may be read as a standard error, a standard deviation or a confidence interval.

### 10.6 · What this paper does not claim

- ⛔ **No** proteome-wide selectivity claim, and no claim of selectivity against anything outside the
  paralogue family and the ten-receptor panel — which is itself currently unreadable.
- ⛔ **No** efficacy claim for extraskeletal myxoid chondrosarcoma or any other disease. Nothing here is a
  treatment candidate and none of it is evidence of benefit.
- ⛔ **No** safety claim, **no** therapeutic-window claim, **no** assertion of clinical readiness.
- ⛔ **No** claim that any molecule discussed binds anything. `R4` is unanswered and cannot be answered by
  this program's instruments.
- ⛔ **No** claim that any design class is impossible, that any pocket cannot be bound, or that any
  downstream method is incapable of extracting information from a scoring distribution.
- ⛔ **No** claim about an external publication's protocol or released data.
- ⚠ **Novelty is incremental, and no field-frequency premise is asserted.** Alchemical ternary-cooperativity
  free-energy calculation is an active published area; the contribution here is the **audit of one
  program's records**, not the method. This draft does not survey prior art and does not claim priority
  over it.
- ⚠ Every quantity in the record is conditional on a hypothesised binary pose and a chosen receptor frame —
  a *double* conditionality that the manuscript states wherever it reports a number.

---

## 11 · Provenance, versioned locators and the dependency manifest

**Version pin.** Every quantity in §4 and in the supplement is read from a committed artifact at the
commit recorded in
[`MF1-dependency-manifest.json`](../../autonomy/opus-capacity-campaign-20260908/paper-lane/MF1-repair/MF1-dependency-manifest.json),
which lists each input's repository path, byte size, the SHA-256 digest **of the bytes the extraction
actually read**, the version-control blob identity of the same path at the recorded commit, and
⭐ **`bytes_match_head_blob`, the explicit result of comparing the two** — added 2026-09-08 (R3), because
a working-tree read plus a blob identity is not a binding unless the read bytes and the blob agree, and
the earlier manifest recorded both without ever comparing them.
⛔ **That manifest describes identities in this repository, not an accessible public archive.** No
immutable repository or archive release has been checked or published for this manuscript, and none is
claimed; the earlier draft's data-availability statement pointed only at relative paths and is corrected
in [§12](#12--declarations).

**Distinguishing the classes of record.** Four kinds of thing are cited in this paper and are not
interchangeable: **original raw execution outputs** (leg records, run objects, verdict files as written by
the run that produced them); **retained reductions** (reducer outputs such as the closure and
5a-KS records); **narrative annotations** (the program roadmap and register views, which interpret the
first two and in four identified places contradict them); and **new author extraction** (the generated
results table, the per-instrument inventory and the dependency manifest of this revision, produced by the
extraction script named in §3). Where a narrative annotation and a primary artifact disagree, this paper
follows the artifact.

**Primary references supported by retained sources.** `doi:10.1158/0008-5472.can-25-1141` (the
SMARCA2-selective degradation reference the endpoint-MD panel's own record establishes direction from; not
open access, so no magnitude is quoted); PMID 17515897 and PMID 29343483 (the combined NR4A1/NR4A3 loss
genotype); PMID 9092472 and PMID 9608532 (complete germline Nr4a2 loss). ⚠ The register's benchmark known
answers for `V6`, `V7`, `V8` and `V10` are cited in this repository through their retained benchmark
records rather than through primary literature identifiers, and this paper does not assert primary
citations it has not retrieved.

**The registers this draft is built from:**

- [`nr4a3-program-map.md`](../nr4a3-program-map.md) — the scoreboard, the control table, §2.3 the
  claim-ceiling rule, §2.4 the asymmetric requirement, §3.1 the annotated instrument table. ⚠ Four of its
  current interpretations are superseded by this revision (§4.1b, §4.1c, §7.2, §9.5); those patches were
  **applied** by the parent integrator at `a6a21fc591d2451038cdf53449b91e3990d59cfb`. ⭐ **The second
  patch set is no longer unapplied (corrected 2026-09-09):** the four cells that commit did not reach —
  census `V11.result`, `V16.result`, `V16.scope_limit`, `V20.scope_limit` — and the roadmap dependency
  row's *"with a quantified bound"* clause were applied by the same integrator at
  `91609d30fdc672f4dbc9eb191e6342a7ddd4f61d`, with the census regenerated from the corrected roadmap. The
  filed patches at
  `research/autonomy/opus-capacity-campaign-20260908/paper-lane/MF1-residual/patches/` are retained as the
  historical proposal and are not to be reapplied.
- [`systems/views/registers/instruments.md`](../../../systems/views/registers/instruments.md) — the
  generated instrument register and its `allocate` relation.
- [`systems/graph/routes.json`](../../../systems/graph/routes.json) `RT-METHODS-PAPER` ·
  [`systems/graph/publications.json`](../../../systems/graph/publications.json) `PUB-METHODS`.
- [`instrument-census.json`](../../modalities/instrument-census.json) /
  [`instrument-census.md`](../../modalities/instrument-census.md) — the 22-entry numbered census.
- Artifacts, each verified present on this branch 2026-09-08:
  [`selcal-verdict.json`](../../modalities/selcal-verdict.json) ·
  [`nrv04-retro-verdict.json`](../../modalities/nrv04-retro-verdict.json) ·
  [`nrv04-retro-secondaries.json`](../../modalities/nrv04-retro-secondaries.json) ·
  [`nr4a3-5aks-reduction.json`](../../modalities/nr4a3-5aks-reduction.json) ·
  [`antitarget-selfcontrol.json`](../../modalities/antitarget-selfcontrol.json) ·
  [`pose-second-method.json`](../../modalities/pose-second-method.json) ·
  [`r3-generation-frame-harmonized.json`](../../modalities/r3-generation-frame-harmonized.json) ·
  [`nr4a3-5bt-gate.json`](../../modalities/nr4a3-5bt-gate.json) ·
  [`nr4a3-5bt-signature.json`](../../modalities/nr4a3-5bt-signature.json) ·
  [`valb-triangle-closure.json`](../../modalities/valb-triangle-closure.json) ·
  [`valb-triangle-reduction.json`](../../modalities/valb-triangle-reduction.json) ·
  [`valb-failure-propagation.json`](../../modalities/valb-failure-propagation.json) ·
  [`selcal-cofold-vs-crystal.json`](../../modalities/selcal-cofold-vs-crystal.json) ·
  [`selcal-cofold-dockq.json`](../../modalities/selcal-cofold-dockq.json) ·
  [`selcal-deepternary-frame.json`](../../modalities/selcal-deepternary-frame.json) ·
  [`selcal-deepternary-poscontrol.json`](../../modalities/selcal-deepternary-poscontrol.json) ·
  [`step1-fanout-map.json`](../../modalities/step1-fanout-map.json) ·
  [`categorical-decoy-null.json`](../../modalities/categorical-decoy-null.json) ·
  [`categorical-decoy-null-lbd.json`](../../modalities/categorical-decoy-null-lbd.json) ·
  [`nr4a2-sparing-bound.json`](../../modalities/nr4a2-sparing-bound.json) ·
  [`selcal-dockq-decoy-scale.json`](../../modalities/selcal-dockq-decoy-scale.json) ·
  [`selcal-interface-signature.json`](../../modalities/selcal-interface-signature.json) ·
  [`nrv04-cys-conservation.json`](../../modalities/nrv04-cys-conservation.json) ·
  [`nrv04-result-forensics.json`](../../modalities/nrv04-result-forensics.json) ·
  [`nrv04-cofold-chain-forensics-2026-07-24.md`](../../modalities/nrv04-cofold-chain-forensics-2026-07-24.md) ·
  [`apo-pose-recovery.json`](../../modalities/apo-pose-recovery.json) ·
  [`apo-pose-site-in-regime.json`](../../modalities/apo-pose-site-in-regime.json) ·
  [`pose-conditionality-census.json`](../../modalities/pose-conditionality-census.json) ·
  [`r5-cross-method-cavity-attribution.json`](../../modalities/r5-cross-method-cavity-attribution.json) ·
  [`nr4a-safety-genetics.json`](../../modalities/nr4a-safety-genetics.json) ·
  [`ternary-env-parity.json`](../../modalities/ternary-env-parity.json) ·
  [`decoy-null-provenance.json`](../../modalities/decoy-null-provenance.json) ·
  [`selectivity_calibration.py`](../../modalities/selectivity_calibration.py).

⛔ No statement in this draft asserts NR4A3 selectivity, EMC efficacy, safety, a therapeutic window or
clinical readiness. Every predicted quantity is labelled a prediction, and every instrument verdict is
reported at the scope its own known-answer control earned.

---

## 12 · Declarations

**Funding.** None. No grant, contract, sponsor or institutional support of any kind supported this work.

**Competing interests.** None.

**Ethics.** This work is an analysis of public data and of this repository's own committed computational
artifacts, together with public structural and literature records. It involved **no new recruitment, no new
sampling and no intervention**. No ethics approval was sought and none was obtained; no institutional
determination of exemption was requested or issued, and none is reported here.

**Use of artificial intelligence.** Claude (Anthropic) and OpenAI models were used, under the author's
direction, to write and check the analysis code, to run the checks, and to draft this manuscript. The
author directed the work, reviewed the outputs and is responsible for the content, including any error.

**Author contributions.** Sole author: conception, direction of the analyses, verification of the outputs
and writing.

**Data and code availability.** Every quantity in this manuscript is read from a committed artifact in
this repository. §11 names those artifacts and the dependency manifest gives each one's path, byte size,
SHA-256 digest and version-control blob identity at a named commit, together with the extraction script
that produced the derived displays. ⛔ **No immutable public archive or repository release has been created
or verified for this manuscript, and none is claimed to be accessible.** No new data were generated for
this draft; the derived tables in §4 and the supplement are new author extraction from existing records.
The original trajectories of the covalent feasibility panel do not exist under the surveyed prefixes
(§9.4), which limits the class of conclusion that can be independently checked for that panel and is
stated at the claims it limits rather than globally.

**Scope.** ⛔ This is a retrospective audit of what one computation-only program's instruments did and did
not recover, over the records enumerated in §3. It makes **no** claim of binding, potency, selectivity,
efficacy, safety, therapeutic window or clinical readiness for any molecule or any disease, and a
computational failure reported here is **not** evidence that a molecule or a route is impossible.
