---
id: DOC-ASO-CONSOLIDATION-CLAIMS-CHANGE-MAP-20261002
title: Source and change map for the consolidated ASO manuscript draft
kind: memo
status: live
level: cross-cutting
purpose: Specify how each materially changed manuscript claim is supported and how the older outgoing package differs from the consolidated draft.
scope: >
  Integration map for manuscript-draft.md against the pinned outgoing journal
  article, accepted catalogue and continuation report. Source inspection only;
  not a full paper review or outgoing-artifact rebuild. Complete exact-witness recovery was integrated after its passing cloud receipt;
  the independent ultra review remains pending.
audience: [maintainers, collaborators, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

# Integration decision

`manuscript-draft.md` is a complete replacement narrative draft, not an edit to the accepted article or public archive. It retains the original project's design–reference comparison–experimental falsification structure while making the source-qualified catalogue and reference expansion the quantitative center. It deliberately leaves the historical 190-design analyses in their frozen archive instead of copying a large, separately scoped methods/results block into a paper centered on 215 designs. No source tables, controls, deposited records or generated outgoing documents have been altered.

The starting outgoing source is `research/manuscripts/aso/fusion-junction-aso-journal-article.md` at `dece8fd886f554641a6c32276b00731af0d05438`. Its frontmatter identifies it as the journal-submission form. The larger `fusion-junction-aso-research-article.md` and working record were not independently reviewed. Current PDF/DOCX build correspondence, submission status and public journal acceptance were not verified. “Accepted catalogue” means the frozen research catalogue supplied for this task, not journal acceptance.

## Claim and change map

| Original anchor or new claim | Concrete draft treatment | Exact source or remaining limitation |
| --- | --- | --- |
| Title and Abstract: two reagents and 190 designs | Reframe as a catalogue and fixed-target reference-coverage comparison; retain proposed chemistry and experimental falsification | Original journal source; accepted catalogue README/CATALOGUE; continuation report |
| Abstract: “That junction is in no normal transcript”; Introduction: “the one feature ... in no normal cell” | Replace with explicit distinction between a fusion junction and uniqueness of its short 16-mer | 19 exact-positive targets in `results/aso-transcriptome.json`; independent exact census |
| Introduction: indication-specific method and established precedent | Retain application contribution; avoid a first-in-literature claim or assertion that search methods are novel | Original source and accepted README's PFRED DOI; no refreshed comprehensive literature search performed |
| Methods: 190 designs at 38 in-frame exon-3 junctions | Define new 215 records/43 junctions, 201 distinct16mers and 5 separate annotation-error controls | Frozen `a916dab...` catalogue and pinned continuation report; old190 denominator never silently changed |
| Source-evidence population | Specify25 deposited-sequence designs,5 coordinate reconstructions,5 construct-description reconstructions,180 hypothetical designs | Accepted catalogue; evidence category is not patient count or therapeutic validation |
| 5-LNA/6-DNA/5-LNA architecture | Preserve fixed proposal and target core positions6–11; no optimization or validated chemistry claim | Catalogue design target/antisense rows; unchanged architecture |
| Earlier five screens and10-base liability criterion | Move earlier screens to explicitly historical scope; new ranking uses two ordered descriptors with no biological threshold | Catalogue analysis plan/order; distinct from old prevalence/gap-margin selection |
| New corpus size and ambiguity counts | State85 archived records/78distinct sequences and670670GENCODErecords; full unambiguous16window eligibility | AcceptedREADME; pinned discovery JSON corpus metadata; union-certificate census agrees |
| 212 longer gap maxima;213 lower Hamming distances | State as215design-record paired comparison | Discovery JSON summary and per-design rows; no inference testing or independent-patient CI |
| Nineteen exact-positive targets | State17hypothetical+2deposited; all19sequences distinct; reconstruction categories0 | Per-design target/evidence class/union_hamming fields; independent census |
| Minimum Hamming distribution19/165/31 | State distances0/1/2, resolved union bounds | Pinned continuation report and result rows |
| Rank stability | Report42primary and41final changed sets alongside15primary and23final disjoint sets | Pinned continuation report and saved rankings; change is not removal of every previous choice |
| DepositedTCF12d9 | Retain target/antisense,22exactoccurrences,RBBP8-AS1; archived primary[9,10],final[9] become[6] | Exact source design and ranking rows; distinguishes previously selected design |
| DepositedEWSR1e7/e2d6 | Retain target/antisense,1exactoccurrence,ANKRD11P1; archived[7,8]/[7] become[7,8,9,10] | Exact source design and ranking rows; d6was not selected |
| Earlier “The reagents” two sequences | Keep as historical nominated designs, not current synthesis recommendations; show their accepted archive and expanded descriptors | EWSR1e12d8 GGGCATATCATCAAAC:11→14gap,3→1Hamming; TAF15e6d8 GGGCATATCTTGTGTG:9→14gap,3→2Hamming |
| Earlier Table1 parent values8/9 | Do not overwrite old table as though it used85records; explain first reagent's original6-parent value8 differs from accepted85record value11 | Original journal tables vs accepted catalogue/per-design rows; numerical scopes differ |
| Nominee choice sets | EWSR1 archived final[9,10]→[7,8,9,10]; TAF15[8]→[6] | Saved rankings; older190-panel nominees and later215catalogue final sets are explicitly distinct |
| Earlier “Selection from a panel of190”:87/61/93/8/45, nulls, geometry and thermodynamic results | Retain only as separately scoped archive evidence, not pooled into current215results | No new rerun or applicability claim; eight old full-duplex sites are not the prior count of these19targets |
| “Test articles”: USZ20/22 inferred correspondence from exon/protein reasoning | Replace with accepted USZ20coordinate reconstruction and USZ22unresolved status; require nucleotide-level model confirmation | AcceptedREADME/CATALOGUE. EWSR1e13/e2is annotation-error control, not USZ20 assignment. No new patient junction sequence invented |
| Old scramble controls | Keep historical provenance; state they were not included in this220design expansion | Two experimental scrambles are distinct from five annotation-error control designs |
| “The falsification experiment” | Preserve proposed fusion/wild-typeNR4A3dose-response ratio; mark cutoff5and variance/power as assumptions, and require other matched transcripts to be assessed | Original study; no new calculated power result, clinical threshold or acceptor-only safety inference |
| Independent verification | Separate440exactcount checks from220union-extrema certificates; note shared Hamming-neighborhood mathematics | Committed `extrema-confirmation/results/extrema-confirmation.json` read atdece8fd; executable revisione4e41...,run37017553101; no individual-stratum nonzero certificate claim |
| Annotation | Report complete134 occurrences/63transcripts/12gene IDs with frozen GENCODE50 header biotypes; six additional occurrences are three transcripts | Recovery run37021819798 at909b149...; all128saved matched; pinned Ensembl116 snapshot agrees for60transcripts, three unavailable; no expression inference |
| Declarations/data availability | Keep oldDOI explicitly historical; pin new Git sources; require author/AI disclosure reconciliation | Deposit-state `published` records DOI10.5281/zenodo.22229096at4fd4698...; not evidence newcontinuation is in that archive |
| References | Use stable source links for new computational results; existing literature context routed to original cited source | Not a fully typeset NATbibliography. Do not claim every new draft citation has received a fresh primary-literature audit |
| Tables/Figure1 | Newdraft two inline source-bound tables; old generatedtables/figure retain oldscope | No outgoingDOCX/PDF/table generator rebuilt. New corpus figure remains separately generated/QA-controlled |
| Submission status | Mark wholeconsolidation asdraft; required independentultra review not completed/runtimeverified | Passing computation is not paper review or publication authority |

## Material status differences to resolve at integration

1. The outgoing journal manuscript still carries the earlier190design narrative and oldmodel interpretation. It is not source-equivalent to the September30catalogue or October2report. Preserve those frozen originals and integrate only into a clearly identified revised package.
2. The old archive DOI names the September1published515-file archive. Newcatalogue/continuation inclusion in that DOI has not been established and must not be implied by an unchanged blanket data-availability statement.
3. The manuscript draft reads an actual committed passing union-certificate receipt. It does not independently rerun that computation, and the focused static certificate review is not the required independent ultra manuscript pass.
4. Root incorporated the successful uncapped134witness/GENCODEv50biotype recovery after reviewing its summary, exact tables and receipt. Six recovered occurrences involve three transcripts; snapshot comparison remains limited to60IDs. Source headers provide all63frozen biotypes.
5. The author has already recorded self-funding, no external funding and no competing financial interests; these known declarations are retained without requesting reconfirmation. The Claude-only AI disclosure requires a factual update to include this Codex-assisted continuation. No unperformed reference audit or independent ultra review is implied.
6. This task did not classify or add unrelated cell-line aliases. No material test-article identity was upgraded: USZ20remains reference reconstruction, USZ22unresolved, and the historical annotation-error designs remain excluded from215target counts.

## Deliverable limits

Only small private text files were created. Accepted repository files and public deposits remain untouched. The next relevant checks are integration-specific source verification of materially new prose, outgoing package/citation generation and the required independent ultra review of the resulting manuscript. This memo neither requests publication nor claims those checks occurred.
