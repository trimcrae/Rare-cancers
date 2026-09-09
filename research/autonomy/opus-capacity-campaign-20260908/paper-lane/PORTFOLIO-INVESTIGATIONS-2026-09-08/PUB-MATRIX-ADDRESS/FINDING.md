---
id: DOC-PORTFOLIO-INVESTIGATION-PUB-MATRIX-ADDRESS
title: "PUB-MATRIX-ADDRESS — compartment and accessibility: what public EMC data can actually establish"
level: L4
kind: investigation
status: complete
date: 2026-09-09
last_verified: 2026-09-09
---

# PUB-MATRIX-ADDRESS — compartment / accessibility lane

Worker: portfolio investigation lane, campaign `OPUS-CAPACITY-CAMPAIGN-20260908`.
Checkout `/home/user/Rare-cancers`, branch `claude/confident-bardeen-ji76cd`,
HEAD `41cf1e61f161fa52304cc0002421e4a80e9de927` at 2026-09-09T00:03:30Z (`checks/03-provenance`).
Read-only outside this directory. No network, no CI, no GPU, no paid API, no `preflight.sh`,
no `git add/commit/push`, no subagents.

## 0 · What the endpoint actually holds

`PUB-MATRIX-ADDRESS` has **no `document` field and no manuscript file on disk**; it is
`state: outlined` in `systems/graph/publications.json`, with four contributing routes
(`RT-MATRIX-SYNTHESIS`, `RT-MATRIX-ADDRESS`, `RT-IMMUNOCYTOKINE`, `RT-HYPOXIA-PRODRUG`) and two
files under `research/manuscripts/microenv/` that belong to the hypoxia reading, not to this paper.
Its four route gradings were already verified against their own primary records by the earlier
campaign worker P5 (`paper-lane/P5-PUB-MATRIX-ADDRESS-paper-step.md`), which also drafted a Results
section. **I did not replay that.** This lane takes the endpoint's other half — the compartment and
accessibility premise on which the whole "matrix as an address" framing rests.

## 1 · The concrete question

Every matrix claim in this program is derived from **bulk transcript**. The disease's defining
feature is an abundant *extracellular, acellular* matrix, and the premise that it governs what an
agent can reach is a statement about **compartment composition**, not about transcript.
So: **for a pre-specified panel of compartment markers, which are actually measurable on each EMC
expression instrument this repository holds, and is a compartment fraction even derivable from
that instrument's own value kind?** If the answer is "none of them, on any instrument", then the
compartment premise is not currently testable by public data at all, and that is the finding.

## 2 · Paper-level merit

Patient relevance is indirect but real: three of the four routes this endpoint would carry are
*addressing* routes, and an address is only useful if the compartment carrying it can be reached.
The contribution is non-trivial because it is a statement about **instrument reach** rather than
about EMC, and it generalises: a rare tumour whose defining feature is acellular has an
instrument problem that gene-indexed high-throughput assays do not solve. The evidence is
attainable — coverage is a countable property of committed files, needing no fetch and no bench.
It also converts a hand-waved caveat into a measured one: `research/literature/
ndrg1-kinase-attribution-2026-08-28.json:832` already concedes the readings are "from bulk
archival tissue with no deconvolution", and no file in the tracked corpus quantifies that.

## 3 · The exact evidence gap, and how it differs from completed or held work

* **Different from P5.** P5 verified the four *gradings* against their records. It made no
  compartment statement and took no new measurement. The compartment premise underlying all four
  was never examined.
* **Different from the withdrawn Lane-2 endothelial finding.** Lane 2's endothelial result (W02i)
  and its fibro/ECM `U` were **arm-to-arm statistics on `emc-expression-panels.json`**, both
  withdrawn on 2026-09-08T04:38Z after random 14-gene panels fired the frozen rule at 0.2950 / 0.2075
  against a nominal 0.05, with a gene-set-independent offset between the EMC arm's six arrays and
  comparator arrays and batch/scan-date/processing/cellularity all confounded. **This lane computes
  no arm contrast, no score, no p-value and reads no expression value** — only gene identity and
  per-instrument metadata. It therefore neither restates nor re-opens that closure, and the
  instruction "do not dispatch further lane-2 statistics on `emc-expression-panels.json`" is
  respected literally.
* **Different from held / denied routes.** No new dataset was sought. `GSE24369`'s uncommitted
  series matrix (retrieval DENIED), `GSE28866`/GPL10999's unattempted probe bridge, `GSE243553`
  (W25-held), B1/B2/B4 and R1–R4 were all left untouched; the only files read are already committed.
* **The actual gap:** nobody has ever asked whether the committed instruments *can see* a
  compartment. The inputs are named exactly: `emc-expression-panels-inputs.json` (per-sample gene
  extract and `value_kind` for `GSE24369`/GPL6244 and `GSE4303`/GPL3290) and
  `emc-fourth-cohort-gene-counts.tsv` + `emc-fourth-cohort-quant.json` (`PRJNA1357027`/`SRP640302`).

## 4 · The bounded step taken, and its result

A pre-specified 53-marker census across six compartment panels — endothelial (11), mural/pericyte
(7), immune (10), fibroblast/stromal (9), hyaluronan and matrix turnover (11), transport/barrier
(5) — run against all three committed instruments. Panels were written before any file was opened
and no marker was added or dropped after seeing coverage.

**Measured result (`compartment-readability-census.json`):**

| Instrument | n | value kind | markers readable | coverage universe |
|---|---|---|---|---|
| `GSE24369` / GPL6244 | 42 arrays | single-channel intensity | **45 / 53** | retained 2,415-gene extract |
| `GSE4303` / GPL3290 | 16 arrays | **two-colour log-ratio vs a reference pool** | **44 / 53** | retained 2,415-gene extract |
| `PRJNA1357027` / TempO-Seq | 12 tumours | raw reads per gene | **6 / 53** | **whole instrument (862 genes)** |

The fourth cohort — the EMC-dedicated deposit whose arrival retired `BLK-NO-EMC-DATA` — carries
**0 / 11 endothelial markers, 0 / 5 transport markers, 1 / 10 immune, 1 / 9 fibroblast**. Verified
independently of the script by `cut`/`grep` over the counts table (`checks/02`): `PECAM1`, `CDH5`,
`VWF`, `PTPRC`, `AQP1`, `CAV1`, `ACTA2` all absent; `ACTB` present, so the absence is not a
mis-parse. The file's recorded `gene_counts_sha256` (`8aa3064a97a4…`) matches the measured hash.

**The finding, stated as a bounded no-go with its cause:**

> **No instrument in this repository can support a compartment statement about EMC, and the two
> failure modes are disjoint.** The two arrays *have* the markers (45/53, 44/53) but not an
> admissible comparison: GPL3290's values are two-colour log-ratios against a reference pool, from
> which no fraction is recoverable by construction, and any arm contrast on this substrate is the
> exact statistic measured to be non-specific and withdrawn on 2026-09-08. The EMC-dedicated cohort
> has counts on an admissible scale but, as quantified here, **cannot see the compartment at all**.

That disjointness is the point worth publishing: it is not one dataset being small. It is that the
only public data with the markers cannot make the comparison, and the only public data whose design
could make the comparison does not carry the markers.

**Attribution of the fourth cohort's blindness, honestly bounded.** The depositors describe a
"TempO-Seq whole human transcriptome assay". The committed quantification retains **1,645 probes
common to every read run**, of which 906 assigned to one gene → **862 genes**. So the absence of
`PECAM1` here may arise from the common-probe intersection, from the matcher (662 probes unassigned
— "a statement about this matcher, NOT about the probe", per `probe_map`), or from the panel itself;
**these are not separable from committed files**, and the source's own units field already warns that
an absent gene "is a statement about the panel and the matcher, never about the tumour". I make no
claim about which. Distinguishing them needs the deposit's own probe manifest, which is not committed
here — that is the named next dependency, and it is a retrieval question for whoever owns that route,
not something this lane attempted.

**Second artifact.** `compartment-dataset-requirements.md` — a pre-specified four-condition
admission test (C1 marker readability, C2 value kind admitting a fraction, C3 a calibrated null or
no comparison, C4 compartment resolution or a named reference matrix) that a future dataset must
pass before an EMC compartment question is even askable. Nothing currently held passes. It is
written to be reusable and to stop this question being re-litigated per dataset.

## 5 · Artifact · validation · provenance · limitations · stop condition

**Artifact.** `compartment_readability_census.py` (runnable, deterministic, no network),
`compartment-readability-census.json` (its output), `compartment-dataset-requirements.md`,
`checks/01-census-run`, `checks/02-independent-grep-verify`, `checks/03-provenance` — each with
`command.txt`, `stdout.txt`, `stderr.txt`, `exit_code.txt`. All three attempts exited 0; no
attempt failed, and none was discarded.

**Validation / baseline.** Three independent checks. (i) The script's fourth-cohort membership
calls were re-derived by a separate `cut`/`grep` path that shares no code with the script and agreed
on all 15 genes tested. (ii) `ACTB` present while `GAPDH` absent is a positive control that the
table is being parsed, not silently emptied. (iii) The counts file's SHA-256 recomputed here equals
the hash recorded by its producer, so the file is the one that artifact vouched for.

**Provenance.** Every input is a committed path at HEAD `41cf1e61`, listed in the script's
docstring. No file outside this lane directory was written. No graph, registry, manuscript or
acceptance criterion was touched, and no diff against a shared file is proposed.

**Limitations.** (1) This is a **readability census, not a measurement of EMC**: it establishes what
instruments can be asked, and nothing whatsoever about vessel density, perfusion, interstitial
pressure, matrix volume fraction, or what any agent can reach — no delivery, efficacy, selectivity
or therapeutic-window claim follows from any line of it. (2) For the two arrays, absence means
absence from the **retained 2,415-gene extract**, not from the platform; the platforms are
genome-wide and the full `GSE24369` matrix retrieval is DENIED, so array coverage is a lower bound.
(3) The marker panels are author-specified standard lineage markers, not a validated signature;
a different panel would shift counts, though not the disjointness result, which turns on 0/11
endothelial in a 862-gene instrument and on GPL3290's value kind. (4) No compartment fraction was
estimated and none is estimable from these inputs. (5) The paper-level question of whether
`PUB-MATRIX-ADDRESS` should be written at all is unchanged by this lane and is not mine to decide.

**Stop condition (pre-set, and met).** Stop when, for all three committed instruments, per-panel
marker readability is measured and independently spot-verified, each instrument's value kind is
quoted from its own record, and the result is stated either as an admissible compartment question
or as a bounded no-go with its named missing dependency. Met at 00:35Z. The branch condition
"if any step would require an arm-to-arm statistic on `emc-expression-panels.json`, stop that step
and report it closed" was designed in and never had to fire, because no step needed one.

**Next credible independent work**, for whoever owns it — not attempted here:
resolve the fourth cohort's probe manifest against the deposit, which would say whether its
compartment blindness is the panel, the common-probe intersection or the matcher; and screen public
single-cell / spatial repositories for any EMC or myxoid-sarcoma specimen against C1–C4. Both are
retrieval tasks under their own authorisation.
