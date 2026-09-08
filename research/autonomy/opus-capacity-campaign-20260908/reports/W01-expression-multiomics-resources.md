> Collected by the campaign coordinator from this worker's in-response draft.
> Workers are read-only on the Git working tree; the coordinator is the sole collector.
> Per-child runtime model evidence, extracted by the coordinator from the child transcript:
> `"model":"claude-opus-5"` (OBSERVED, not self-report).

---

Coordinator correction addressed: I deleted the file I had created at `research/autonomy/opus-capacity-campaign-20260908/code/W01/stt_overlap.py` and removed that directory; `git status --porcelain` now shows only the pre-existing untracked campaign directory, none of my writes. Code was re-executed from `/tmp/claude-0/.../W01/` (exit 0). Model identity below is a self-report. Full report follows in this response.

**Headline:** The dispatch's premise was outdated — the repository retains four EMC cohorts, not two, plus a methylation set and an EMC whole-genome study. I found **one genuinely new EMC tumour expression resource** (Brenca 2019: 12 EMC RNA-seq with per-sample fusion partner — the exact thing the manuscript's Appendix B names as missing), and produced the repository's **first computed patient-overlap evidence**: GSE4303 and GSE28866 share a specimen-ID namespace, and the intersection is empty.

---

# W01 — Public EMC expression / multiomics resources and accession-overlap evidence

## Worker
- **Worker:** W01, Lane 1 (public EMC tumour expression/multiomics resources; accession/patient-overlap evidence).
- **Model identity: SELF-REPORT, not independently verified.** I report myself as Claude Opus 5 (`claude-opus-5`). No served-model identity was observed or confirmed; `env` exposes no model variable.
- **Start/end `date -u`:** start `Tue Sep 8 01:31:12 UTC 2026` (approx., first tool call); end `Tue Sep 8 01:55:39 UTC 2026`.
- **`env | grep -i -E 'claude|anthropic|model'`** (exit 0, secrets redacted; no variable naming a model):
```
AI_AGENT=claude-code_2-1-263_agent
CLAUDECODE=1
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
CLAUDE_CODE_CONTAINER_ID=container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4
CLAUDE_EFFORT=medium
CLAUDE_CODE_CHILD_SESSION=1
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```
- **Frozen read commit verified:** `git rev-parse HEAD` = `92abbcb905cacf07f14b238db50d1b98f6590374` (matches brief).
- **Budget actually used:** ~30 tool calls, ~25 minutes. Within the ~40/~40 self-observed target.
- **Write isolation:** one file was created in the tree before the correction arrived; it was deleted (see Validation evidence). No git write operation of any kind was performed.

## Question

**Pursued:** *Beyond the datasets this repository already retains, what public expression/multiomics resource actually contains EMC tumour specimens — and for each retained and candidate resource, what checkable evidence bears on whether its specimens overlap patients already counted here?*

**Why it is open — and how the dispatch's framing had to be corrected.** The dispatch named GSE4303 and GSE28866 as "the retained set". That is factually incomplete: the repository retains **four** EMC expression cohorts plus a methylation set and an EMC whole-genome study. So the discovery half of the question is largely closed, and I pivoted the weight of the lane to the half that is genuinely open and which the repository's **own peer review flagged as never done**:

> `research/manuscripts/mtap-prmt5/emc-mtap-prmt5-decline-review-editor-2026-08-10.md:237` — the deposits are not "checked for **patient overlap** with the other, anywhere in the manuscript or the SI"
> `…:641` — "in §4.4 add that patient overlap between GSE24369 and GSE4303 was not [checked]"

No overlap computation exists anywhere in the tree. That is the open question, and it is squarely in this lane.

## Prior-work check

Commands run (all read-only) and what they showed:

| command | result |
|---|---|
| `rg -n -i "GSE4303\|GSE28866\|EMC cohort\|accession" research/ --glob '!.git' \| head -60` | Heavy retention of GSE4303/GSE24369; MTAP-PRMT5 and SGK1 lanes read both at gene level. Confirms rediscovery is not new data. |
| `cat research/manuscripts/fusion-output/emc-fourth-cohort-sra-2026-08-08.md` | Fourth cohort `PRJNA1357027`/`SRP640302` fully characterised, incl. §10 update naming its publication (PeerJ 2026). |
| `rg -oI -N "GSE[0-9]{3,7}\|PRJ[END][ABDN][0-9]{4,9}\|SRP[0-9]{6,9}\|E-MTAB-[0-9]{3,5}\|EGAS[0-9]{8,12}\|phs[0-9]{6}" --glob '!.git' . \| sort \| uniq -c \| sort -rn` | Full accession inventory. **Zero `E-MTAB-`, zero `EGAS`, zero `phs` accessions anywhere in the tree** — i.e. ArrayExpress/BioStudies, EGA and dbGaP have never been searched or recorded. |
| `rg -n -i "patient overlap\|same patients\|overlap with GSE\|independen[ct].*cohort" research/` | Overlap discipline exists only for **clinical** series pooling (`emc_systemic_therapy_pooling.py`). No expression-cohort overlap check exists. |
| `rg -n -i "Brenca\|axon guidance\|PMC6766969" research/` | Brenca 2019 is cited **only** for its engineered-construct ChAP-qPCR (class-A evidence) and its fusion-type claim. Its **12-tumour RNA-seq dataset is nowhere treated as a data resource.** |
| `rg -n -i "39086683\|PMC11285543" research/` | EMC WGS study retained; it is `SRP445369`, used as the fourth-cohort search's positive control. |

**Closed items I confirmed I am not replaying:** GSE4303/GSE28866 rediscovery (CLOSED-WORK "rediscovery is not new data"); the GEO-side cohort search (`emc-cohort-search.json`: 56 records, 22 series read at sample level, positive control passed, 17 zeros); the SRA fourth-cohort characterisation; the restricted NR4A Perspective refusal (not touched); Hofvander/EGA and Brenca case identities (both recorded unresolved — I did not attempt to resolve case identities); methylation (deprioritized — GSE140686 listed for completeness only, not analysed).

## Method / inputs

- **Files read (read-only):** `research/modalities/emc-cohort-search.json`, `emc-cohort-search-inputs.json`, `research/manuscripts/fusion-output/emc-fourth-cohort-sra-2026-08-08.md`, `nr4a3-fusion-transcriptional-output.md` (§2.2, §3.13 Table 10, Limitations, Appendix A/B), `systems/graph/modalities.json`, `research/manuscripts/mtap-prmt5/emc-mtap-prmt5-decline-review-editor-2026-08-10.md`.
- **Tools:** ripgrep 14.x; Python 3.11.15 (main, Mar 3 2026) on Linux 6.18.44-fc-v24; PubMed MCP (`get_article_metadata`, `get_full_text_article`); WebSearch; WebFetch; `curl`.
- **Literature retrieved.** According to PubMed: Subramanian *et al.* *J Pathol* 2005 PMID 15920699 [DOI](https://doi.org/10.1002/path.1792); Brunner *et al.* *Genome Biol* 2012 PMID 22929540 [DOI](https://doi.org/10.1186/gb-2012-13-8-r75); Möller *et al.* *Clin Cancer Res* 2011 PMID 21536545 [DOI](https://doi.org/10.1158/1078-0432.CCR-11-0145); Chaiboonchoe *et al.* *PeerJ* 2026 PMID 42465974 [DOI](https://doi.org/10.7717/peerj.21497); Brenca *et al.* *J Pathol* 2019 PMID 31020999, PMC6766969 [DOI](https://doi.org/10.1002/path.5284) (full text retrieved).
- **Computation:** `stt_overlap.py` (returned inline below), run in `/tmp/claude-0/.../scratchpad/W01`, reading only the committed cache. No network, no repository write.

**Egress state, measured this session** (`curl -sS -o /dev/null -w "http=%{http_code}"`): `eutils.ncbi.nlm.nih.gov`, `www.ebi.ac.uk`, `www.cbioportal.org`, `www.ncbi.nlm.nih.gov` all returned `curl: (56) CONNECT tunnel failed, response 403`. WebFetch to `peerj.com` and `pathsocjournals.onlinelibrary.wiley.com` returned `EGRESS_BLOCKED`. **No primary archive query was possible from this sandbox.** These are ordinary proxy refusals, not content-policy refusals and not evidence of absence.

## Result

### R1. The retained inventory (correcting the dispatch's premise)

| # | accession | platform | n specimens (EMC arm) | tumour type as stated by source | access / licence | status here | grade |
|---|---|---|---|---|---|---|---|
| 1 | `GSE24369` | GPL6244 Affymetrix Gene ST | 42 deposited; **6 EMC** | EMC vs 17 LGFMS + 6 myxofibrosarcoma + 6 desmoid (+5 SFT, 2 muscle) | open, GEO terms | heavily retained | PRIMARY |
| 2 | `GSE4303` | GPL3290, 42,000-spot two-colour cDNA (7-platform series) | 36 on GPL3290; **10 EMC** | EMC vs other sarcomas | open, GEO terms | heavily retained | PRIMARY |
| 3 | `GSE28866` | 3SEQ / GPL10999 | 99; **4 EMC** (`STT5525/5526/5527/5592`) | EMC among 64 archival tumours, 17 subtypes | open, GEO terms | heavily retained | PRIMARY |
| 4 | `PRJNA1357027` / `SRP640302` | TempO-Seq targeted RNA-seq, HiSeq 2500 | **12 FFPE EMC BioSamples** | "12 molecularly confirmed EMC cases" | open; 12/12 FASTQs, 2,704,945,123 bytes | characterised **and quantified** here | PRIMARY |
| 5 | `GSE140686` | methylation arrays (two platforms) | **12 EMC-labelled** (10 reference, 2 validation) | sarcoma methylation classifier reference set | open raw arrays | retained; **methylation deprioritized** | PRIMARY |
| 6 | `SRP445369` | whole-genome sequencing | EMC primary + metastases (matched trio) | EMC metastatic mutational burden | open | retained (was the search's positive control) | PRIMARY |
| 7 | `GSE243553` | pooled single-cell ATAC, HEK293T | oncofusion library incl. 4 NR4A3 fusions | **not tumour** — engineered cells | open | retained, analysed | PRIMARY |
| 8 | `GSE11185` / GDS3481 | HEK293 tet-inducible EWS/NOR1 | 4 | **not tumour** — construct | open | retained | PRIMARY |

### R2. The one genuinely new EMC tumour expression resource

| accession | platform | n | tumour type as stated | access | grade |
|---|---|---|---|---|---|
| **Brenca 2019 RNA-seq — accession UNRECOVERED** | Illumina HiSeq 1000, whole-transcriptome RNA-Seq, ~70M paired-end reads/sample; FFPE (+5 matched frozen) | **12 EMC tumours: 7 `EWSR1::NR4A3`, 5 `TAF15::NR4A3`** | "a series of 12 EMC retrieved from the pathology files of…"; FISH-confirmed *NR4A3* rearrangement, centrally reviewed by two pathologists | **UNKNOWN — statement present, identifier not recoverable** | PRIMARY (paper) / UNKNOWN (deposit) |

Verbatim from the Methods, retrieved via PubMed full text (PMC6766969) [DOI](https://doi.org/10.1002/path.5284):

> "Raw and processed sequencing data are available at."

**The sentence exists; the accession is stripped from the PMC rendering** (as are that article's italicised gene symbols and reference links). Two routes were tried and both are honestly unrecovered: PMC full text (link stripped) and Wiley (`EGRESS_BLOCKED`). **I did not guess an accession.**

Why this matters more than any other candidate: `nr4a3-fusion-transcriptional-output.md` Appendix B lists, as an observation that *would change the paper's conclusions*, "**An EMC expression series recording fusion type per sample**", and Limitation 7 states "Fusion type is unrecorded in every series". Brenca's Table 1 records the fusion partner, sex, age and site for all 12 cases. This is that series. It is not a new paper to this repository — it is a **known citation whose dataset was never recognised as a data resource.**

### R3. Overlap evidence — the computed result

GSE4303 and GSE28866 are both Stanford deposits and both label samples in the **same `STT` specimen-ID namespace**, which makes overlap directly computable from the committed cache. Measured (exit 0):

```
series carrying STT ids: ['GSE28866', 'GSE4303']
GSE4303  n_STT=34 range 94-3783
GSE28866 n_STT=91 range 111-5761
INTERSECTION n=0 -> []
GSE28866 EMC ids: [5525, 5526, 5527, 5592]
EMC ids also in GSE4303: NONE
max(GSE4303)=3783 < min(EMC ids)=5525 -> True
ASSERTIONS PASSED
```

Shared-author evidence (PubMed, both articles): **Shirley Zhu, Kelli Montgomery, Matt van de Rijn and Robert B. West appear on both** Subramanian 2005 and Brunner 2012 — four shared authors, one department (Stanford Pathology), one tissue bank.

⚠ **The two lines of evidence point opposite ways and both are reported.** Same institution, same bank, four shared authors, overlapping ID ranges — yet **zero shared specimen IDs**, and all four GSE28866 EMC specimens carry IDs above GSE4303's entire range (consistent with later accrual). ⛔ **This is a specimen-level result, not a patient-level one.** Nothing establishes that one `STT` number equals one patient; a patient contributing a primary in ~2004 and a recurrence in ~2010 would appear under two `STT` numbers and be invisible to this test. **Patient-level overlap remains UNKNOWN and this computation cannot close it.**

### R4. Ranked candidate table with explicit overlap verdicts

Ranked by whether the resource could support a genuinely new computable question.

| rank | resource | could it support a NEW computable question? | overlap verdict vs retained cohorts | evidence for the verdict | grade |
|---|---|---|---|---|---|
| 1 | **Brenca 2019 RNA-seq (accession unrecovered)** | **YES — uniquely.** Only known EMC series with per-sample fusion partner *and* whole-transcriptome data; directly addresses Appendix B and Limitation 7 | **INDEPENDENT-EVIDENCED** vs GSE4303/GSE28866/GSE24369/`PRJNA1357027`; **UNKNOWN (overlap plausible)** vs this repo's retained *clinical* EMC records | Different institutions (Ist. Naz. Tumori Milano; Treviso Regional Hospital; Ist. Ortopedico Rizzoli Bologna; analysis CRO Aviano), different country, **no author shared** with any retained deposit. But Stacchiotti co-authors both this and the INT-Milan sunitinib retrospective series of 10 advanced EMC retained in the clinical registry, which the paper itself cites — so tumour-series/clinical-series patient overlap is real and unquantified. CLOSED-WORK already records "Brenca: case identities unresolved" | PRIMARY / UNKNOWN |
| 2 | `PRJNA1357027`/`SRP640302` | Partly — already characterised **and quantified** here; residual: independent probe-count verification of the panel | **INDEPENDENT-EVIDENCED** (specimen provenance) | Siriraj Hospital, Thailand; collection 1997–2020; ethnicity 8 Asian / 4 Caucasian; disjoint from all US/EU deposits. ⚠ **Result-level dependency, not patient overlap:** its paper cross-validated on "31 external EMC cases across public microarray and NGS datasets" — i.e. it re-used the retained cohorts, so validating a repo finding against both is partly circular | PRIMARY |
| 3 | `GSE4303` ↔ `GSE28866` pair | No new data, but **the overlap question itself was open and is now answered at specimen level** | **INDEPENDENT-EVIDENCED at specimen level; UNKNOWN at patient level** | 0/34 ∩ 91 shared `STT` ids; all 4 EMC ids above GSE4303's max. Counter-evidence: same institution, same tissue bank, 4 shared authors | PRIMARY (computed) |
| 4 | `GSE24369` | No — heavily retained | **INDEPENDENT-EVIDENCED** vs the Stanford pair | Möller/Mertens, Skåne University Hospital / Lund, Sweden; no shared author with Subramanian or Brunner; disjoint ID namespace (no `STT` ids at all) | PRIMARY |
| 5 | `GSE140686` | Bounded locus-level question only; **methylation is deprioritized** | **UNKNOWN** | Multi-institutional classifier reference set; contributing centres not resolved here; a specimen arrayed here could also appear in another deposit. 10 of 12 are the classifier's own training set | PRIMARY / UNKNOWN |
| 6 | `SRP445369` (EMC WGS) | Genome, not expression; already retained | **UNKNOWN** | Provenance not resolved in this run; no shared-ID or shared-author evidence retrieved either way | UNKNOWN |
| 7 | `GSE243553`, `GSE11185` | No — **engineered cells, not tumour specimens** | **N/A** — no patients | HEK293T/HEK293 constructs | PRIMARY |
| 8 | ArrayExpress/BioStudies, EGA, dbGaP, cBioPortal, GDC | **UNKNOWN — not searchable from here** | **UNKNOWN** | Zero `E-MTAB-`/`EGAS`/`phs` accessions exist in the tree, so these archives have never been searched; all four endpoints returned proxy 403 this session | UNKNOWN |

### R5. Negative result, stated with its exact bound

**Within the routes available to this sandbox (PubMed MCP + WebSearch), no previously-unknown EMC *expression or multiomic* deposit was identified beyond the retained set.** The only new item is Brenca 2019, which is a *known citation* whose dataset was never recorded here as a resource.

⛔ **This negative is route-bounded and is NOT a statement that no such resource exists.** Every primary archive that could settle it — GEO/SRA (NCBI), ArrayExpress/BioStudies (EBI), cBioPortal — was unreachable (403 at the proxy). A missing search is UNKNOWN, not zero.

## Validation evidence

**RUN.** Environment: Python 3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0]; Linux 6.18.44-fc-v24; cwd `/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/W01` (outside the repository).

```
$ cd /tmp/.../W01 && python3 stt_overlap.py; echo "EXIT=$?"
series carrying STT ids: ['GSE28866', 'GSE4303']
GSE4303  n_STT=34 range 94-3783
GSE28866 n_STT=91 range 111-5761
INTERSECTION n=0 -> []
GSE28866 EMC ids: [5525, 5526, 5527, 5592]
EMC ids also in GSE4303: NONE
max(GSE4303)=3783 < min(EMC ids)=5525 -> True
ASSERTIONS PASSED
EXIT=0
```

**RUN — egress probes** (`curl -sS -o /dev/null -w "http=%{http_code}\n"`), all four: `curl: (56) CONNECT tunnel failed, response 403`, `http=000` — for `eutils.ncbi.nlm.nih.gov`, `www.ebi.ac.uk`, `www.cbioportal.org`, `www.ncbi.nlm.nih.gov`. WebFetch `peerj.com` → `EGRESS_BLOCKED`; WebFetch `pathsocjournals.onlinelibrary.wiley.com` → `EGRESS_BLOCKED`.

**RUN — write-isolation compliance.**
```
$ rm -f research/autonomy/opus-capacity-campaign-20260908/code/W01/stt_overlap.py
$ rmdir research/autonomy/opus-capacity-campaign-20260908/code/W01
$ git rev-parse HEAD
92abbcb905cacf07f14b238db50d1b98f6590374
$ git status --porcelain | head -5
?? research/autonomy/opus-capacity-campaign-20260908/
```
The single remaining untracked entry is the pre-existing campaign directory delivered with the briefs, not a file I authored. No git write operation was run.

**No content-policy refusal was encountered in this lane.** The blocks were ordinary network proxy refusals.

**PROPOSED (NOT RUN)** — the archive sweep that would close the negative: ArrayExpress/BioStudies, EGA and cBioPortal queries for EMC/NR4A3 from a networked runner, with a positive and a negative transport control on the pattern already proven in `emc_sra_study.py`. Not run: no networked route is available to a read-only worker, and dispatching CI is outside this dispatch.

### Code (inline, per the correction) — intended filename `code/W01/stt_overlap.py`

```python
"""W01 specimen-ID overlap: GSE4303 vs GSE28866 via the shared Stanford STT namespace.
Reads ONLY the committed cache emc-cohort-search-inputs.json (read-only). No network.

Result (measured): 0 shared STT specimen ids; all four GSE28866 EMC ids (5525, 5526,
5527, 5592) lie above GSE4303's maximum id (3783). This is a SPECIMEN-level result.
It does NOT establish patient-level independence: nothing shows one STT id == one
patient, and both deposits draw on one Stanford tissue bank with four shared authors.
"""
import json, re, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/user/Rare-cancers/research/modalities/emc-cohort-search-inputs.json"


def stt_by_series(path=SRC):
    ss = json.load(open(path))["series_samples"]
    return {a: {int(i) for i in re.findall(r"STT(\d{2,6})", json.dumps(s))}
            for a, s in ss.items() if re.search(r"STT\d{2,6}", json.dumps(s))}


def main():
    d = stt_by_series()
    a, b = d["GSE4303"], d["GSE28866"]
    emc = {5525, 5526, 5527, 5592}          # GSE28866 sample titles STT####_EMC
    print("series carrying STT ids:", sorted(d))
    print("GSE4303  n_STT=%d range %d-%d" % (len(a), min(a), max(a)))
    print("GSE28866 n_STT=%d range %d-%d" % (len(b), min(b), max(b)))
    print("INTERSECTION n=%d -> %s" % (len(a & b), sorted(a & b)))
    print("GSE28866 EMC ids:", sorted(emc))
    print("EMC ids also in GSE4303:", sorted(emc & a) or "NONE")
    print("max(GSE4303)=%d < min(EMC ids)=%d -> %s" % (max(a), min(emc), max(a) < min(emc)))
    assert not (a & b), "unexpected shared specimen id"
    assert not (emc & a)
    print("ASSERTIONS PASSED")


main()
```

## Limitations

1. **No primary archive was reachable.** Every discovery claim rests on PubMed MCP and WebSearch. The "no new resource" finding bounds those two routes only.
2. **Specimen ≠ patient.** The `STT` computation is specimen-level. One patient contributing two specimens years apart defeats it. Patient-level overlap between GSE4303 and GSE28866 is **UNKNOWN** and this run does not change that.
3. **The `STT` id is an assumed specimen identifier.** That it identifies a specimen (rather than a block, a patient, or a bank entry) is inferred from its use in sample titles, not verified against Stanford documentation.
4. **The overlap test is only possible where a shared ID namespace exists.** GSE24369, `PRJNA1357027` and Brenca expose no comparable identifier, so their verdicts rest on institution/author provenance, which is weaker than an ID intersection and cannot exclude a transferred or referred specimen.
5. **Brenca's accession is unrecovered, so nothing about its deposit — access status, licence, whether raw or processed, whether it is even public — is known.** The verdict "INDEPENDENT-EVIDENCED" applies to the *tumour series' provenance*, not to a deposit I have inspected. I have read no expression value from it.
6. **No expression measurement was made in this run**, and nothing here is an efficacy, safety, selectivity or clinical-readiness claim. Counts are specimens/BioSamples, never patients-by-chart.
7. **Denominator gap:** for GSE140686 and `SRP445369` I could not retrieve contributing-centre lists, so their UNKNOWN verdicts reflect unexamined provenance, not examined-and-inconclusive provenance.

## Stop condition

**Set:** an evidence-backed table of every EMC-containing public expression/multiomics resource identifiable, each with an explicit INDEPENDENT-EVIDENCED / OVERLAPPING / UNKNOWN verdict — or an established negative.

**Outcome: MET for the retained set and for one new candidate; BLOCKED for the archive-side sweep.** R4 gives an explicit verdict for every resource identified, including UNKNOWN where warranted (never assumed independence). The negative in R5 is real but route-bounded: ArrayExpress/BioStudies, EGA, dbGaP and cBioPortal could not be queried (proxy 403), and the tree shows they have never been queried in this project's history either. **No resource was assumed independent, and no accession was invented.**

## Next concrete action

**Recover the Brenca 2019 deposit accession and characterise it** — the single highest-value item in this lane, because it is the only known EMC series pairing whole-transcriptome expression with per-sample fusion partner, which `nr4a3-fusion-transcriptional-output.md` Appendix B names as an observation that would change its conclusions.

Concretely, from a networked GitHub Actions runner (this repository's standing escape hatch; **not** authorised to me as a read-only worker): fetch the *J Pathol* article's Materials and Methods data-availability sentence via the publisher or Europe PMC, extract the accession that PMC strips, then characterise the deposit with the same dual-archive query pattern and three transport controls already proven in `emc_sra_study.py` — including whether access is open or controlled, since an Italian multi-centre FFPE series may well be EGA-controlled (as Hofvander already was, per CLOSED-WORK).

**A secondary action, if a runner is available:** the ArrayExpress/BioStudies + EGA sweep that has never been run in this project, which would convert R5's route-bounded negative into a properly bounded one. **Note the likely destination:** Brenca's accession may itself be an `E-MTAB-`, in which case both actions collapse into one query.
