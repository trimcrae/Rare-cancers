---
id: DOC-EPITOPE-BENCHMARK-2-FINDING
title: "EPITOPE-BENCHMARK-2 — the manuscript's cited EWSR1::FLI1 primary is the paper VACCINE-PATH-2 read, and it does not move n = 15"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# EPITOPE-BENCHMARK-2 — reference [20] read directly: no delta to n = 15, and two over-strong sentences in VACCINE-PATH-2 corrected

Writes confined to this directory. Nothing added, committed or pushed; `scripts/preflight.sh` not
run; no manuscript, graph entry, producer, guard, gate, pin or test touched; no subagents; no GPU,
no paid API, no publication act, no outreach; no direct HTTP attempted; no large download; cost $0.
`NEOANTIGEN-3` was **not** edited and its `assert len(VALIDATED) == 15` was **not** removed.

⛔ **No immunogenicity, presentation, tolerance, efficacy, safety, selectivity, therapeutic-window
or clinical-readiness claim is made or implied here, in either direction.** "Admissible" below is a
statement about a **record's fit to a benchmark's inclusion rule** — bookkeeping — never about a
peptide, a tumour or a patient. Route B9 (PMID 22592656) and B1/B2/B4/B8 stayed closed; no HLA-C
data was fetched, derived or relabelled.

## 1 · Question

> What does the vaccine-path manuscript's **own cited** *EWSR1*::*FLI1* primary — reference [20] as
> printed — actually report, is it in fact that paper, and does it change the validated class I
> junction-epitope count of **15**?

EPITOPE-BENCHMARK (limitation iii) and NEOANTIGEN-3 (§8.3) both stopped here because PubMed **term
mapping** never surfaced the record. The new move, per FOLLOWTHROUGH-DISCOVERY **rank 7 (P7)**, is
to read the **cited primary directly** instead of re-searching by term.

## 2 · Merit

An unresolved discrepancy between a manuscript sentence and a literature census is exactly what a
reviewer finds. The 34-vs-37 sufficiency adjudication rested on an **unread citation**. Resolving it
either moves a preregistered count — which would be loud, because NEOANTIGEN-3 asserts on it — or
retires the discrepancy decisively. Patient relevance is indirect and honest: this settles what one
sentence of a manuscript is entitled to say, and nothing else.

## 3 · Evidence gap, and the boundary against VACCINE-PATH-2

VACCINE-PATH-2 completed while this lane was being planned and reports the same paper. **This lane
is not a repetition of it**: VACCINE-PATH-2 *began from the printed PMID* and judged admissibility
in prose. The gap it left open is the one this lane closes — **whether PMID 42570981 is in fact
reference [20]**, or a different paper that merely resembles it. NEOANTIGEN-3's unresolved E38
discrepancy is **prediction-only** (`evidence == ["PREDICTION"]`, `hla: "none"`, `len: null`,
PMID 36900411) and supports neither side; re-verified in `checks/06-`.

## 4 · Step taken

**(a) The citation was resolved without its PMID.** `lookup_article_by_citation` was given only the
bibliographic fields printed at line 1498 — author `Calukovic`, journal `npj Precision Oncology`
(and its abbreviation), year `2026`, volume `10`, first page `305`. **The printed PMID was withheld.**
Both forms returned **PMID 42570981**. Independently and in the reverse direction,
`convert_article_ids` on the printed DOI `10.1038/s41698-026-01642-4` returned **PMID 42570981 /
PMCID PMC13452805**. Printed PMID, DOI, journal, year, volume and first page are **mutually
consistent**. Reference [20] **is** that paper. It is **not** a different paper.

**(b) The record was read.** According to PubMed: metadata for PMID 42570981 and full text for
PMC13452805 ([DOI](https://doi.org/10.1038/s41698-026-01642-4)). Verbatim, from its own Methods:
*"four overlapping **17-mer** peptides by a sliding-window approach, limiting contiguous residues
from either fusion partner to a maximum of ten"*; *"To ensure broad applicability, the vaccine was
designed **without HLA restriction**"*; *"The sequences (E1–E4) are listed in Table"* (that table is
**not** carried in the PMC body text); and, of the monitoring assay, *"detects functional,
non-anergic memory T-cells in an **HLA-independent** manner"*.

**(c) The inclusion rule was re-applied IN CODE, not by eye.** `ewsr1_fli1_resolution.py` copies
EPITOPE-BENCHMARK's rule **verbatim**, first **calibrates** it against the committed census
(`epitope-records.json`, sha256 `2ac4c8a1…95a4e`) — it returns **exactly 15**, `assert` enforced —
then applies it to four candidate records built only from what [20] reports.

| candidate | len | HLA named | sequence | eligible | predicates failed |
|---|---|---|---|---|---|
| C01 (E1) | 17 | none | UNKNOWN | **no** | `seq_known`, `classI_window_8_11`, `classI_restricted` |
| C02 (E2) | 17 | none | UNKNOWN | **no** | same three |
| C03 (E3) | 17 | none | UNKNOWN | **no** | same three |
| C04 (E4) | 17 | none | UNKNOWN | **no** | same three |

**n_before = 15 · admitted from [20] = 0 · n_after = 15 · delta = 0.**

## 5 · ⚠ The count does NOT change — and that is stated deliberately, not by omission

**n = 15 stands.** NEOANTIGEN-3's `assert len(VALIDATED) == 15` is **not** tripped. Had it moved,
this section would say so in these words; it did not. EPITOPE-BENCHMARK's search did not *miss*
four class I epitopes — there are **no class I *EWSR1*::*FLI1* junction epitopes in [20]** to have
missed. Limitation (iii) is resolved in the direction that leaves the census intact.

## 6 · VACCINE-PATH-2 independently confirmed — and two of its sentences corrected

**Confirmed** from the record itself: the four peptides are 17-mers; "designed without HLA
restriction" is verbatim; the assay is HLA-independent, verbatim; responses are polyfunctional CD4⁺
against all four; the E1–E4 sequences are in a table absent from the PMC body; the peptides are
inadmissible to a class I benchmark; n = 15 unchanged.

**Checked here that VACCINE-PATH-2 did not check:** (i) that the citation resolves from
bibliographic fields **alone** with the printed PMID withheld, and from the DOI in reverse — i.e.
that PMID 42570981 *is* reference [20] rather than being assumed to be; (ii) the rule applied **in
code**, calibrated first to reproduce 15, with per-record predicate failures enumerated; (iii)
`check_consistency.py` re-run **unmodified**; (iv) the six negative controls re-tested for
discrimination.

**Two corrections — wording, not verdict. Digit for digit:**

1. VACCINE-PATH-2 writes *"no class I measurement exists to admit."* The Results actually say:
   *"**Although a single CD8⁺ response was transiently detectable**, the vaccine-induced immunity
   was dominated by durable CD4⁺ T-cell activity."* The ICS flow panel includes **CD8**, and cells
   were gated into CD4⁺ **and CD8⁺** subsets. A CD8⁺ observation therefore **does** exist in the
   record. It changes **nothing** about admissibility — it is tied to no named class I allotype, the
   assay is explicitly HLA-independent, no peptide is 8–11 residues, and no sequence is recoverable
   — but "no class I measurement exists" is **over-strong as written**.
2. VACCINE-PATH-2 attributes the absence of CD8⁺ reactivity to *"the class II binding properties of
   the selected peptides."* The Discussion actually reads: *"The dominance of CD4⁺ responses and the
   **relative** absence of CD8⁺ reactivity **may reflect** the class II binding properties of the
   selected peptides **and limited class I presentation in Ewing sarcoma**."* The authors hedge, say
   *relative* absence, and offer a **second** explanation the paraphrase drops.

Its verdict — inadmissible, n = 15 stands — is **correct and independently reproduced**.

## 7 · Artifact · validation · provenance · limitations · stop condition

* **Artifact.** `ewsr1-fli1-discrepancy-resolution.json` (citation as printed, resolution evidence,
  what the retrieved record reports, per-record verdicts, delta), `ewsr1_fli1_resolution.py`,
  `negative_control_discrimination.py`, and `checks/` — **six attempts, all preserved, none failed.**
* **Validation.** (i) The rule is calibrated to a known answer before use: run over the committed
  census it returns **exactly the 15** EPITOPE-BENCHMARK reported (`assert`, `checks/04-`).
  (ii) `../EPITOPE-BENCHMARK/check_consistency.py` re-run **UNMODIFIED and in place** — exit **0**,
  byte-identical before and after (`diff` clean), reporting `n=15 eligible, 6 MS-eluted, 3
  prediction-only, 7 binding-only, 6 negative controls, 9 fusions, Wilson 93/78/60/37, verdict
  INSUFFICIENT` (`checks/05-`). (iii) The **six negative-control rows still discriminate**: all six
  `spans_junction == "no"` rows (E05, E28, E35, E36, E39, E40) are rejected, **zero admitted**, and
  the rule additionally rejects the anchor-modified row (E27), all 7 binding-only, all 3
  prediction-only and all 19 sequence-unknown rows (`checks/06-`, exit 0). It is not a rule that
  says yes.
* **Provenance.** PubMed/PMC MCP server — the admitted route — 2026-09-09:
  `lookup_article_by_citation` (bibliographic fields only), `convert_article_ids` (DOI→PMID/PMCID),
  `get_article_metadata` (PMID 42570981), `get_full_text_article` (PMC13452805). According to
  PubMed. [DOI](https://doi.org/10.1038/s41698-026-01642-4).
  `research/manuscripts/neoantigen/emc-vaccine-development-path.md` lines 48, 156, 559, 689 and
  reference 20 at line 1498. `../EPITOPE-BENCHMARK/{epitope-records.json, tabulate_epitopes.py,
  check_consistency.py}` read-only. **No direct HTTP was attempted, so no refusal was encountered
  or worked around.** Supplementary information not retrieved.
* **Carried-forward arbitration.** **34, not 37**, is the correct Wilson figure at sensitivity 0.9
  (k=round and k=ceil both give 34; k=floor gives 38). `check_consistency.py` still pins the
  pre-arbitration **37** and was run **UNMODIFIED** here — **that pin is EPITOPE-BENCHMARK's to
  change, not this lane's, and this lane did not touch it.** Recorded, not repaired.
* **Limitations.** (i) E1–E4 **sequences are UNKNOWN** to this lane — unknown, not zero, not empty;
  the table is not in the PMC body. A 17-mer is outside the 8–11 window whatever it spells, so
  recovery cannot change the verdict. (ii) Admissibility is judged **as reported**; no cited assay
  was re-verified. (iii) `n = 15` is a **lower bound**, bounded by EPITOPE-BENCHMARK's search recall.
  (iv) `get_article_metadata` returned **no page/elocation field**; the printed first page `305` is
  corroborated only by the citation match, not by a returned page field. (v) Nothing here is
  evidence about IEDB, which was never reached.
* **Stop condition.** **Reached: the record was read** through the admitted route. This lane stops.

## 8 · Next credible independent work (not done here, not authorised here)

1. EPITOPE-BENCHMARK's `check_consistency.py` pins `"0.9":37`, which the parent arbitration
   superseded with **34**. That is a one-line owner decision in **EPITOPE-BENCHMARK's** lane; no
   diff is proposed from here and the guard was not weakened.
2. Recover E1–E4 sequences from [20]'s supplementary table on the CI runner — completeness only; it
   cannot change the verdict.
3. VACCINE-PATH-2's §7 proposed prose replacement for §B1 should be amended before any owner uses
   it, to carry §6's two corrections: a transient CD8⁺ response **was** reported, and the authors'
   attribution is hedged and two-part.
