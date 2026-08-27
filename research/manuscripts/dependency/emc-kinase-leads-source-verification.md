---
id: DOC-EMC-KINASE-LEADS-SOURCES
title: Three of the four kinase leads, verified against their primary records
level: L3
kind: memo
status: live
canonical_for: ["the primary-source verification behind RT-RET, RT-DNAPK and RT-ALK-HIT as PUB-KINASE-LEADS will report them"]
purpose: >
  Read the sources behind three of PUB-KINASE-LEADS' four leads, state what each one actually says
  in its own words, and record whether the route's registered framing survives contact with it.
  Written so the paper can be assembled from records that were read rather than from route prose
  that was summarised.
scope: >
  L3. Covers RT-RET, RT-DNAPK and RT-ALK-HIT. RT-SGK1, the fourth lead, is NOT covered and is not
  graded here. Asserts nothing about efficacy, safety, a therapeutic window or clinical readiness in
  any disease. Graph corrections arising from it are applied to systems/graph/routes.json in the
  same change and are listed in the appendix.
audience: [maintainers, autonomous research agents, external reviewers]
date: 2026-08-27
last_verified: 2026-08-27
---

# Three of the four kinase leads, verified against their primary records

> ⛔ **NOTHING HERE ASSERTS EFFICACY, SAFETY, A THERAPEUTIC WINDOW OR CLINICAL READINESS, FOR EMC OR
> FOR ANY OTHER DISEASE.** No EMC patient has received a selective RET inhibitor, a DNA-PK inhibitor
> or brigatinib in any report read here. Every measurement quoted below was made in vascular or
> pulmonary smooth muscle, in DNA-repair cell biology, in one patient-derived cell line, or in small
> clinical series of this disease — none larger than twenty cases.

> **Attribution.** Bibliographic metadata, abstracts and PubMed Central full texts below were
> retrieved from **PubMed** (NCBI) on 2026-08-27 through the PubMed MCP connector. PubMed's terms
> require attribution and a DOI link wherever its metadata travels, so every record carries its DOI
> as a link.

---

## 0 · What "read" means in this file

| tag | meaning |
|---|---|
| **[FT]** | PubMed Central full text retrieved and read in this session |
| **[API]** | PubMed structured record — title, authors, journal, DOI, abstract — read in this session. The body was **not** reachable |
| **[ARTIFACT]** | read from a committed file in this repository, named at the point of use |

⛔ **No sentence below is reconstructed from a search snippet.** Where a body could not be reached
the file says **UNREACHABLE** and says what was tried, because a confident paraphrase of a source
nobody opened is the one failure this repository will not ship.

---

## 1 · RET — the lead the route calls its strongest, and its cautionary case

### 1a · What the source actually says

**Stacchiotti S, Pantaleo MA, Astolfi A, Dagrada GP, Negri T, Dei Tos AP, Indio V, Morosi C,
Gronchi A, Colombo C, Conca E, Toffolatti L, Tazzari M, Crippa F, Maestro R, Pilotti S, Casali PG.
"Activity of sunitinib in extraskeletal myxoid chondrosarcoma." *Eur J Cancer* 2014;50(9):1657-64.
PMID 24703573,
[DOI](https://doi.org/10.1016/j.ejca.2014.03.013).** **[API]**

⛔ **UNREACHABLE.** `convert_article_ids` returns **no PMCID** for this record on 2026-08-27, so no
PubMed Central body exists to fetch; the Elsevier text is paywalled. Everything below is the
abstract, verbatim.

| what the paper reports | verbatim |
|---|---|
| the cohort | *"From July 2011, 10 patients with progressive metastatic translocated EMC have been consecutively treated with sunitinib 37.5mg/day, on a named-use basis."* |
| the qualifier on the molecular work | *"Moreover, transcriptome, immunohistochemical and biochemical analyses of **a limited set of samples** were performed focusing on some putative targets of sunitinib."* |
| **the whole activation claim** | *"Among putative sunitinib targets, only RET was expressed and activated in analysed samples."* |
| the authors' own conclusion | *"Involvement of RET deserves further investigation."* |

⛔ **Four things are not recoverable and the paper does not contain them in its abstract:** how many
samples were in the *limited set*; how many of them were positive; which of the three named assays
produced the word *activated*; and whether tumour cellularity was controlled. That is not a
criticism of the report — it is a description of what a one-sentence abstract statement can carry.

### 1b · The finding that redirects this lead, and it was in a paper the route had never read

**Urbini M, Indio V, Astolfi A, Tarantino G, Renne SL, Pilotti S, Dei Tos AP, Maestro R, Collini P,
Nannini M, Saponara M, Murrone L, Dagrada GP, Colombo C, Gronchi A, Pession A, Casali PG,
Stacchiotti S, Pantaleo MA. "Identification of an Actionable Mutation of KIT in a Case of
Extraskeletal Myxoid Chondrosarcoma." *Int J Mol Sci* 2018;19(7):1855. PMID 29937513, PMC6073125,
[DOI](https://doi.org/10.3390/ijms19071855).** **[FT]**

⭐ **This is the same group.** Stacchiotti, Casali, Pantaleo, Dei Tos, Maestro, Dagrada and Pilotti
are authors of both papers. Its abstract states, verbatim:

> *"Recently, we reported on the therapeutic activity of sunitinib in a series of EMC cases,
> **however the molecular target of sunitinib in EMC is unknown**."*

Its introduction restates the observation in the same paper that calls the target unknown:

> *"EMC tumor specimens showed RET proto-oncogene expression and activation, while no other
> predictive biological markers of response were identified."*

⛔ **THE ORIGINATING AUTHORS DID NOT TREAT THEIR OWN OBSERVATION AS IDENTIFYING THE TARGET.** Four
years after the 2014 report, in a paper of their own, they wrote that the molecular target of
sunitinib in this disease is unknown. So the route's framing — that the report cannot carry the
weight put on it — is right about the weight and **wrong about who put it there.**

⭐ **And the same paper supplies a scale bound this programme did not have.** Its western-blot arm
is described verbatim as *"At the protein level, KIT was found to be expressed in all **three** EMC
samples tested, while a mild phosphorylation of KIT was detected only in the KIT mutated case."*
That is what a phospho-receptor measurement in this disease looks like when a denominator is stated:
**three samples.**
⚠ **It is a bound on the scale of such work in EMC, not a recovery of the 2014 paper's n.** Nothing
here says how many samples the 2014 *limited set* contained, and this file must not be read as
implying three.

The 2018 paper's own verdict on its own finding, verbatim: the KIT exon 11 deletion was found in
*"one out of 20 EMC cases analyzed"* and *"cannot explain the EMC sensitivity to sunitinib."*

### 1c · Where the drift actually is, at one named identifier

**Davis EJ, Wu YM, Robinson D, Schuetze SM, Baker LH, Athanikar J, Cao X, Kunju LP, Chinnaiyan AM,
Chugh R. "Next generation sequencing of extraskeletal myxoid chondrosarcoma." *Oncotarget*
2017;8(13):21770-21777. PMID 28423517, PMC5400622,
[DOI](https://doi.org/10.18632/oncotarget.15568).** **[FT]**

Its introduction renders the 2014 observation as:

> *"Immunohistochemical and biochemical analyses did not reveal any significant predictive markers;
> however, analysis of receptor tyrosine kinase (RTK) activity demonstrated elevated expression and
> activation of RET, a known target of sunitinib."*

⛔ **The qualifier is gone.** *"A limited set of samples"* does not survive into the paraphrase, and
what was a statement about some analysed samples reads as a statement about the disease. Its
discussion then adds a therapeutic framing on top: *"particularly understanding the effect of [RET]
expression as [RET] is clinically targetable."*

⚠ **Its own measurement is abundance, and it says so.** *"The expression levels of sunitinib
targeted-kinases were measured by transcriptome sequencing for KDR, PDGFRA/B, KIT, RET, FLT1, and
FLT4."* Result: *"Only [RET] expression was significantly greater in patients with EMC relative to
other types of sarcomas excluding liposarcoma (p<0.0002, by student t-test)."* Transcriptome
sequencing measures mRNA, so this corroborates expression and is silent on activation.

⭐ **Recovered on this reading and previously recorded as absent:** the comparator's **histology mix
is stated** — the Figure 3 legend enumerates seventeen subtypes, from extraskeletal myxoid
chondrosarcoma through to GIST. **The comparator n is still not stated**, per subtype or in total.
Cohort: six patients, all male, all with metastatic disease, five fresh metastatic biopsies plus one
archived frozen specimen; the fusion was detected by sequencing in five of six and in the sixth by
fluorescence in situ hybridisation on the archived primary.

### 1d · How much downstream weight exists — measured, and partly UNKNOWN

⛔ **No citation count for PMID 24703573 is reachable at $0 through any instrument this repository
has.** The PubMed connector exposes similarity links, not cited-by links, and Europe PMC's host is
refused at the egress proxy. So the phrase *"a decade of citation"* is **UNKNOWN as a volume claim**
and must not be written as if it were measured.

What **was** measured, PubMed, 2026-08-27, query
`("extraskeletal myxoid chondrosarcoma"[Title/Abstract] OR "EWSR1-NR4A3"[Title/Abstract] OR
"EWSR1::NR4A3"[Title/Abstract]) AND (RET OR sunitinib OR selpercatinib OR pralsetinib)[Title/Abstract]`:
**five records in all of PubMed**, and the newest is 2018.

| PMID | what it is | DOI |
|---|---|---|
| 23058004 | the same group's two preceding patients | [DOI](https://doi.org/10.1186/2045-3329-2-22) |
| 24555529 | a soft-tissue-sarcoma therapy overview naming EMC among sunitinib indications | [DOI](https://doi.org/10.1586/14737140.2014.885840) |
| 24703573 | the activation report itself | [DOI](https://doi.org/10.1016/j.ejca.2014.03.013) |
| 28423517 | the transcriptome corroboration, and the paraphrase of §1c | [DOI](https://doi.org/10.18632/oncotarget.15568) |
| 29937513 | the same group's own *the target is unknown* | [DOI](https://doi.org/10.3390/ijms19071855) |

⚠ **A co-mention search is not a citation count.** A paper can cite the 2014 report without naming
EMC or RET in its title or abstract, so this bounds the EMC-specific literature and nothing wider.

### 1e · Verdict on the route's framing

| the framing said | verdict |
|---|---|
| *the one kinase reported activated in this disease* | ✅ **SURVIVES.** No other kinase is reported activated in EMC in any record read here |
| *reading the source shows the report cannot carry the weight* | ✅ **SURVIVES, AND IS BETTER EVIDENCED THAN THE ROUTE KNEW** — the source's own authors said the target is unknown |
| *the weight a decade of citation has put on it* | ⛔ **NOT SUPPORTED AS WRITTEN.** The volume is UNKNOWN; the demonstrated drift is at **one** identifier; and the originating group is not the party that overstated it |
| *the kinase paper's strongest lead* | ◐ **WEAKER THAN THE WORD SUGGESTS.** It is the only lead with a reported activation, and the group that reported it declined to call it the target |

---

## 2 · DNA-PK — where the route's own framing is wrong on a word

### 2a · The registered next action, taken apart

The route's registered action was: *read the queued sarcoma dependency prior for the kinase and its
two partner subunits, then report the lead with its wild-type, single-source, non-sarcoma provenance
stated plainly.* It has three parts and they have three different answers.

**(1) The dependency prior — HALF READ, AND THE OTHER HALF IS NOT AVAILABLE.**
[`depmap-sarcoma-dependency.json`](../../modalities/depmap-sarcoma-dependency.json) **[ARTIFACT]**,
group `DNA-PK heterotrimer`, DepMap 24Q4:

| gene | sarcoma mean gene effect | fraction dependent | screened sarcoma lines |
|---|---|---|---|
| `XRCC5` (Ku80) | **-1.324** | **1.000** | 91 |
| `XRCC6` (Ku70) | **-1.766** | **1.000** | 91 |
| `PRKDC` (the catalytic subunit) | — | — | **absent from the group entirely** |

⛔ **The two partner subunits are read and they are pan-essential in this tissue class.** A gene
required in every screened line argues against there being a window to exploit.
⚠ **The kinase itself returned no reading, and that is an instrument gap, not a result.** `PRKDC`
carries no row in this artifact because no matching column was found in the gene-effect table. **An
absent reading is not a reading of absence** — nothing here says `PRKDC` is or is not a dependency.

⭐ **AND THE ROUTE'S OWN OPEN QUESTION IS HALF-ANSWERED, FROM DATA THAT WAS ALREADY ON DISK.** The
route said re-running against a different DepMap release *"or checking the column naming"* would
close this at $0. **The column-naming half is ruled out on two counts, both read here rather than
assumed:**

1. [`depmap_sarcoma_dependency.py`](../../modalities/depmap_sarcoma_dependency.py) normalises every
   column with the same `c.split(" (")[0]`, and that splitter found `XRCC5` and `XRCC6` on the same
   run. It is not failing on DepMap's `SYMBOL (ENTREZ)` format.
2. [`fet_ddr_axis_scan.py`](../../modalities/fet_ddr_axis_scan.py) carries the direct measurement in
   a source comment: *"POLR2A and PRKDC are NOT in the 24Q4 CRISPRGeneEffect column set (measured,
   not assumed — they came back absent on run 30848356798)"*, which is why that scan's pan-essential
   control was changed to `RPL5`. A second instrument, a different code path, a named run.

⛔ **So `PRKDC` is absent from the release's column set rather than lost by this repository's
parsing**, and the only remaining $0 step is a different DepMap release — a networked fetch, so a CI
runner rather than the dev sandbox. ⚠ It is still an absent reading, and this paragraph says nothing
about whether `PRKDC` is a dependency in sarcoma.

**(2) *Wild-type* and *non-sarcoma* — SURVIVE.**

**Medunjanin S, Daniel JM, Weinert S, Dutzmann J, Burgbacher F, Brecht S, Bruemmer D, Kähne T,
Naumann M, Sedding DG, Zuschratter W, Braun-Dullaeus RC. "DNA-dependent protein kinase (DNA-PK)
permits vascular smooth muscle cell proliferation through phosphorylation of the orphan nuclear
receptor NOR1." *Cardiovasc Res* 2015;106(3):488-97. PMID 25852083,
[DOI](https://doi.org/10.1093/cvr/cvv126).** **[API]** — `convert_article_ids` returns **no PMCID**;
the body is **UNREACHABLE** at $0.

Verbatim from the abstract: the system is *"Cultured human aortic SMC"*; the mechanism is
*"Mutational analysis and kinase assays demonstrated that NOR1 is a substrate of DNA-PK and is
phosphorylated **in the N-terminal domain**. Phosphorylation resulted in post-transcriptional
stabilization of the protein through prevention of its ubiquitination"*; the interaction is
*"Co-immunoprecipitation studies from VSM cell lysates demonstrated that DNA-PK forms a complex with
NOR1."* The words *fusion*, *EWSR1* and *sarcoma* do not appear.

⛔ **The residue is still not pinned, and now on two instruments rather than one.** The abstract
localises the site only to the N-terminal domain, and no body text is reachable for this record. Any
sentence naming a residue would be inventing it.

**(3) *Single-source* — WRONG, AND THIS REPOSITORY'S OWN COMMITTED MEMO ALREADY SAID SO.**

[`emc-dnapk-nr4a3-lane-assessment.md`](emc-dnapk-nr4a3-lane-assessment.md), committed 2026-08-07 —
**two days before the route was graded** — names four primary papers on this axis. All four were
re-verified against PubMed on 2026-08-27 and every title, journal and year matched:

| PMID | what it adds | verification | DOI |
|---|---|---|---|
| 25852083 | the paper UniProt cites; human aortic smooth muscle | [API] | [DOI](https://doi.org/10.1093/cvr/cvv126) |
| 36114572 | an independent group, human pulmonary artery smooth muscle, same direction | [API] | [DOI](https://doi.org/10.1186/s12931-022-02171-x) |
| 21979916 | **four years earlier**, and about the NR4A **family** rather than NR4A3 | [API] | [DOI](https://doi.org/10.1101/gad.16872411) |
| 30784586 | the PAR-binding pocket in all NR4A members, and paralogue redundancy | [API] | [DOI](https://doi.org/10.1016/j.celrep.2019.01.083) |

⭐ **What is single-source is the UniProt ANNOTATION. The axis is not.** Those are different objects
and the route's action text collapsed them.

### 2b · Two things the four papers say that a *single-source* framing hides

⚠ **The two smooth-muscle papers disagree on the mechanism.** 2015 says stabilisation by prevented
ubiquitination, above. **Liu YY, Zhang WY, Zhang ML, Wang YJ, Ma XY, Jiang JH, Wang R, Zeng DX.
"DNA-PKcs participated in hypoxic pulmonary hypertension." *Respir Res* 2022;23(1):246. PMID
36114572, PMC9479248, [DOI](https://doi.org/10.1186/s12931-022-02171-x)** **[API]** says, verbatim:
*"DNA-PKcs affected proliferation by regulating **NOR1 protein synthesis** followed by the
expression of cyclin D1."* A degradation brake and a synthesis effect are different claims about
where in the protein's lifecycle the kinase acts, and only the first is the one this route's logic
needs. Neither paper adjudicates the other.

⛔ **And the family-level papers point away from selectivity.** **Malewicz M, Kadkhodaei B, Kee N,
Volakakis N, Hellman U, Viktorsson K, Leung CY, Chen B, Lewensohn R, van Gent DC, Chen DJ, Perlmann
T. "Essential role for DNA-PK-mediated phosphorylation of NR4A nuclear orphan receptors in DNA
double-strand break repair." *Genes Dev* 2011;25(19):2031-40. PMID 21979916, PMC3197202,
[DOI](https://doi.org/10.1101/gad.16872411)** **[API]** states verbatim that *"**NR4A proteins**
interact with the DNA-PK catalytic subunit"* and that *"NR4As represent an entirely novel component
of DNA damage response and are substrates of DNA-PK."* The subject is the family.
**Munnur D, Somers J, Skalka G, Weston R, Jukes-Jones R, Bhogadia M, Dominguez C, Cain K, Ahel I,
Malewicz M. "NR4A Nuclear Receptors Target Poly-ADP-Ribosylated DNA-PKcs Protein to Promote DNA
Repair." *Cell Rep* 2019;26(8):2028-2036.e6. PMID 30784586, PMC6381605,
[DOI](https://doi.org/10.1016/j.celrep.2019.01.083)** **[API]** locates the binding function in a
pocket of the **DNA-binding domain**, which all three paralogues share: *"NR4A DBD is bi-functional
and can bind poly-ADP-ribose (PAR) through a pocket localized in the second zinc finger."*

⚠ **UNREACHABLE, and it bounds the two rows above.** `get_full_text_article` was called on
**PMC3197202** on 2026-08-27 and returned an **empty full-text body** — the identifier resolves and
the abstract comes back, the body does not. So the 2011 paper remains read at abstract level, which
is what its row says. The 2019 paper's own full text was read in the 2026-08-07 memo and its two
decisive sentences are quoted there; they are not re-quoted here from a body this session did not
open.

### 2c · An instrument note the paper should carry

PubMed, 2026-08-27, query `(NR4A3 OR NOR1 OR "NOR-1") AND (PRKDC OR "DNA-PK" OR "DNA-PKcs" OR
"DNA-dependent protein kinase")` over titles and abstracts returns **two records** — 25852083 and
36114572. ⛔ **The two papers that decide this route are invisible to that query**, because they say
*NR4A*, not *NR4A3* or *NOR1*. A gene-symbol-keyed literature search on this axis returns the
smooth-muscle pair and misses the family biology entirely.

### 2d · Verdict on the route's framing

| the framing said | verdict |
|---|---|
| *read the queued dependency prior for the kinase and its two partner subunits* | ◐ **PARTLY IMPOSSIBLE.** The two subunits are read; the kinase has no column, and that is a collector gap to fix, not a reading to take |
| *wild-type* | ✅ **SURVIVES** |
| *non-sarcoma* | ✅ **SURVIVES** |
| *single-source* | ⛔ **WRONG.** Four primary papers, and the repository's own memo had already listed them two days before the grade was written |

---

## 3 · The ex-vivo screen hit — the framing survives, with one addition and one hard limit

### 3a · What the source actually says

**Iwata S, Noguchi R, Osaki J, Adachi Y, Shiota Y, Osaki S, Nishino S, Yoshida A, Ohtori S, Kawai A,
Kondo T. "Establishment and characterization of NCC-EMC1-C1: a novel patient-derived cell line of
extraskeletal myxoid chondrosarcoma." *Hum Cell* 2025;38(4):122. PMID 40580361,
[DOI](https://doi.org/10.1007/s13577-025-01250-7).** **[API]**

⛔ **UNREACHABLE.** `convert_article_ids` returns **no PMCID** for this record on 2026-08-27. The
screen's body is not readable at $0.

Verbatim: *"High-throughput screening of 221 anticancer drugs using NCC-EMC1-C1 identified three
candidates, **brigatinib, panobinostat, and romidepsin**, that demonstrated low IC50 values."*

⛔ **The IC50 values themselves, the assay, the concentration range and any comparator line are all
outside the abstract and are therefore UNKNOWN.** *Low* is the source's own unquantified word. The
paper must not be cited as if a potency were known.

### 3b · The class attribution, read from curated target records

From [`nr4a3-repurpose-candidates.json`](../../modalities/nr4a3-repurpose-candidates.json), this
repository's Broad Drug Repurposing Hub extract **[ARTIFACT]** — read, not recalled:

| agent | curated `moa` | curated `target` |
|---|---|---|
| brigatinib | `ALK tyrosine kinase receptor inhibitor\|EGFR inhibitor` | `ALK\|EGFR` |
| panobinostat | `HDAC inhibitor` | `HDAC1\|HDAC2\|HDAC3\|HDAC4\|HDAC6\|HDAC7\|HDAC8\|HDAC9` |
| romidepsin | `HDAC inhibitor` | `HDAC1\|HDAC2\|HDAC3\|HDAC4\|HDAC5\|HDAC6\|HDAC7\|HDAC8\|HDAC9` |

⭐ **Two of the screen's three hits are the same class**, and it is a class this board already holds
and has closed on selectivity rather than on activity. The one-agent framing that raised this route
could not show that; the hit list itself does.

⚠ **The curated record does not name ROS1 for brigatinib**, although the lead calls this the
ALK/ROS1-class hit. That is a statement about **the curated record**. It is not a measurement of
what the agent inhibits, and nothing here tested that.

### 3c · Why the arrays cannot settle it, and what the dependency panel adds

From [`census-route-expression-grading.json`](../../modalities/census-route-expression-grading.json)
**[ARTIFACT]**: `ALK` and `ROS1` have **no probe** on either `GPL6244` or `GPL3290`, so the target
group reaches no coverage floor and emits no score. ⛔ **That is an instrument statement and never a
biological negative.** The one readable named target, `EGFR`, is lower in EMC on both platforms.

From [`depmap-sarcoma-dependency.json`](../../modalities/depmap-sarcoma-dependency.json)
**[ARTIFACT]**, group `Drug-screen hit targets`, across the **91 screened** sarcoma lines of DepMap
24Q4:

| gene | sarcoma mean | sarcoma fraction dependent | non-sarcoma mean | non-sarcoma fraction dependent |
|---|---|---|---|---|
| `ALK` | -0.040 | **0.000** | -0.052 | 0.006 |
| `ROS1` | +0.112 | **0.000** | +0.093 | 0.000 |
| `EGFR` | -0.146 | 0.011 | -0.306 | 0.205 |
| `HDAC1` | -0.151 | 0.033 | -0.156 | 0.040 |
| `HDAC2` | -0.159 | 0.088 | -0.051 | 0.023 |
| `HDAC3` | **-0.915** | **0.824** | -0.936 | 0.878 |
| `HDAC6` | -0.082 | 0.000 | -0.054 | 0.000 |

⭐ **Neither named kinase is a dependency in a single screened sarcoma line**, which points the same
way as the hit list.

⭐ **AND THE ADDITION THE ROUTE'S GRADE DOES NOT MAKE: the HDAC signal is not sarcoma-selective
either.** `HDAC3` is a dependency in 82.4% of screened sarcoma lines and in **87.8% of everything
else**, with a mean gene effect of -0.915 inside and -0.936 outside. So the class the screen actually
favoured is close to pan-essential on this axis, and inherits no window argument from it. ⛔ **That
is a statement about knockout dependency in a public panel. It is not a statement about this disease,
which has no line in that panel.**

⚠ **What none of this settles, and the paper must say so.** A gene-effect score is a knockout
phenotype and an inhibitor's IC50 is not, so this does not establish that the hit was off-target for
the named kinase in the line it ran on — and NCC-EMC1-C1 is not in the DepMap panel. The screen also
ran on **one** line. Attribution needs a knockdown or a target-selective agent in that model, and
that needs a bench.

### 3d · Verdict on the route's framing

| the framing said | verdict |
|---|---|
| *the screen's dominant signal is a class the board already holds* | ✅ **SURVIVES** — two of three hits, from curated target records |
| *the arrays structurally cannot attribute the kinase hit* | ✅ **SURVIVES** — no probe for either named kinase on either platform |
| — | ⭐ **ADD:** the favoured class is not sarcoma-selective in the dependency panel either |
| — | ⛔ **ADD:** the hit's magnitude is UNKNOWN; the screen's full text is UNREACHABLE at $0 |

---

## 4 · A defect that runs across two of the three leads

⛔ **BOTH DEPENDENCY-CITING GRADES CARRIED THE WRONG DENOMINATOR, AND THIS REPOSITORY HAD ALREADY
CORRECTED IT SOMEWHERE ELSE.** RT-DNAPK's grade said the Ku subunits are dependencies in *"100% of
176 sarcoma lines"* and RT-ALK-HIT's said *"Across 176 sarcoma lines"*. **176 is the number of
sarcoma MODELS in DepMap 24Q4. Only 91 of them carry CRISPR gene-effect data**, and every per-gene
row in the artifact reads `n_sarcoma: 91`.

The mechanism, read from the producing code rather than inferred:
[`depmap_sarcoma_dependency.py`](../../modalities/depmap_sarcoma_dependency.py) computes
`n_sarcoma` per gene as the length of that gene's non-null sarcoma column, while `n_sarcoma_models`
at the top level is the length of the sarcoma model list. Two different quantities, one of which
sits at the top of the file where a reader reaches for it.

⚠ **The percentages and gene effects are unchanged** — they were always computed on the screened
subset. What was wrong is the denominator they were attributed to, and it overstated the evidence
base by almost double.

⭐ **The identical error was found and corrected in the MTAP/PRMT5 manuscript on 2026-08-09/10**, and
its correction register describes it in those words: *"across 176 sarcoma cell lines"* became
*"across the 91 screened sarcoma cell lines"*, called there **a real error, in the direction that
overstated the evidence base**, present in four places including that paper's abstract. The routes
were graded 2026-08-09. **The correction never reached the graph.** Both grades are fixed in the
same change as this file.

⛔ **AND IT IS STILL LIVE ELSEWHERE.** `176 sarcoma lines` remains in
`research/modalities/census_route_expression_grading.py` and its generated
`census-route-expression-grading.json` (three places each, for the PRMT5/MAT2A, CDK7/CDK9 and
MCL1/BCL2L1 rows) and in
[`emc-transcriptional-proteostatic-dependency.md`](emc-transcriptional-proteostatic-dependency.md).
Those belong to other routes and to a generated artifact that must be regenerated rather than
hand-edited, so they are **named here and deliberately not touched** — a separate item, not this
one's.

---

## 5 · Is any of this stale? Measured, not assumed

The three routes were graded 2026-08-09. Three PubMed searches on 2026-08-27, queries as written:

| query | records | newest |
|---|---|---|
| EMC × (RET OR sunitinib OR selpercatinib OR pralsetinib), title/abstract | 5 | 2018 |
| (NR4A3 OR NOR1 OR NOR-1) × (PRKDC OR DNA-PK OR DNA-PKcs OR DNA-dependent protein kinase), title/abstract | 2 | 2022 |
| EMC × (brigatinib OR ALK OR ROS1 OR HDAC OR panobinostat OR romidepsin OR drug screen OR cell line), title/abstract | 4 | 2025 (PMID 40580361, already held) |

⭐ **Nothing has appeared since the grading that any of these three leads would have to answer.** The
newest EMC-and-RET record in PubMed is eight years old.
⚠ **These are title/abstract co-mention counts over PubMed only.** They bound what a keyword search
reaches; they are not citation counts and not a statement about the whole literature.

---

## 6 · What this file could not settle

- ⛔ **The 2014 report's denominator.** How many samples were in the *limited set*, how many were
  positive, and which assay produced *activated*. The body is paywalled and has no PMCID. This is an
  external dependency, not a sandbox limitation.
- ⛔ **The citation volume behind that report.** No cited-by instrument is reachable at $0. **UNKNOWN.**
- ⛔ **The DNA-PK phosphosite on NR4A3.** PMID 25852083 has no PMCID; PMC3197202 resolves but returns
  an empty body. **UNREACHABLE on two instruments.**
- ◐ **`PRKDC`'s own sarcoma dependency.** Still an absent reading — but §2a narrows it: the
  column-naming explanation is ruled out on two instruments, so the remaining step is a different
  DepMap release, which is a networked fetch and belongs on a CI runner.
- ⛔ **The screen's IC50 values.** No PMCID; abstract only.
- ⛔ **RT-SGK1**, the fourth lead. Not in this file's scope and not graded here.

---

## Appendix · Corrections applied in the same change

| where | superseded | now | why |
|---|---|---|---|
| `systems/graph/routes.json` → RT-DNAPK grade | "dependencies in 100% of 176 sarcoma lines" | "dependencies in 100% of the 91 SCREENED sarcoma lines" | §4 |
| `systems/graph/routes.json` → RT-ALK-HIT grade | "Across 176 sarcoma lines" | "Across the 91 SCREENED sarcoma lines" | §4 |
| `systems/graph/routes.json` → RT-DNAPK `next.best_next_action` | "report the lead with its wild-type, single-source, non-sarcoma provenance" | the word *single-source* removed, and the still-open half named as the catalytic subunit's dependency | §2a(3) |
| `systems/graph/routes.json` → RT-DNAPK `remaining_unknowns` | — | the four primary papers added, with the annotation-versus-axis distinction stated | §2a(3) |
| `systems/graph/routes.json` → RT-DNAPK `remaining_unknowns` | "checking the column naming would close it and is $0" | that half ruled out on two instruments; the remaining step named as a different DepMap release on a CI runner | §2a(1) |
| `systems/graph/routes.json` → RT-RET grade | — | PMID 29937513 added, with the originating group's own *the target is unknown*, and the citation-volume claim marked UNKNOWN | §1b, §1d |

⚠ **The route grades' own dated wording is left in place and appended to rather than rewritten**, so
that what was believed on 2026-08-09 stays readable beside what was measured on 2026-08-27.
