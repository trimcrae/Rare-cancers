"""Write the bounded round's durable decision and manifest; no Git operations."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
P=Path(__file__).resolve().parent
def append_once(name,marker,txt):
 p=P/name;old=p.read_text(encoding='utf8')
 if marker not in old:p.write_text(old+'\n'+marker+'\n'+txt.strip()+'\n',encoding='utf8')
append_once('RESULTS.txt','Final bounded protein/spatial/H19 extension, 4 October 2026', '''
Decision: shelve standalone protein/regulatory/H19 papers; no newly demonstrated
EMC biology. The final source batch ended at identity and scientific-value gates.
Burns2023 all11 histology categories exhaust321 tumors without an EMC category.
Sarquarium2024 DatasetEV1 enumerates all17 models, none authenticated as EMC.
Tang2024 all272 clinical rows were evaluated, including all8 otherFS:7 identify
other entities, while SS-5 has unspecified subtype and remains unresolved.
No protein-expression ranking was performed in these non-authenticated cohorts.
Ngo2025 spatial/single-cell measurements concern epithelioid sarcoma; the EMC
mention concerns an external bulk comparison, not an EMC spatial measurement.
ProCan2021 poster and PanAtlas2025 still have unresolved sample-level eligibility.
Those are visible incomplete coverage, not evidence that public EMC proteomics
does not exist. No global discovery-exhaustion claim follows from this round.

The H19 study(DOI10.1002/cam4.71305) describes EMC in two TMA sets, but its reported
tissue analysis pools rare entities into Others(26/150) with no individual EMC
identities, scores or outcomes. Its data statement links CCLE rather than the
individual tissue observations, and the public fullXML contains no supplements.
Gapmer experiments are restricted to SW872/SW982. Its MUG-EMCS label conflicts
with the model creator's explicit extraskeletal mesenchymal chondrosarcoma label.
No NR4A3 authentication recovered; this model cannot establish EMC H19 dependence.
These are source/identity limits, not evidence of H19 absence in authentic EMC.

Contrary mTOR evidence reported by the independent genomic worker is retained:
the Foundation paper already displayed its2/75 TSC2 frequency, and BostonGene's
SITC2024 EMC poster(n10) displays3 combinedTSC1/2 mutation/loss EVENTS, not3 proven
TSC2-mutant patients. ExactQ955* is exon-sensitive and classified germlineVUS in
the evaluated ClinVar record, not established tumor-specific functional loss.
The separate genomic packet binds these primary sources; this lane has not
independently counted the poster. Do not state absence of other public mTOR events.
No source supplies a paired TSC2-genotype and authentic EMC drug-response bridge.

Independent H1FX challenge appended after regulatory source batch
review_h1fx.py verified raw H1FX RNA and probe8090555 values plus17 contrasts,
and independently counted all105 GSE6481 labels(19 MLPS, no explicit EMC).
The primary PeerJ21497 paper already reports no enrichment versus soft-tissue
sarcomas and specifically frames its positive lineage claim versus cartilaginous
tumors. New lower MLPS/LGFMS comparisons do not test that central contrast.
Decision: shelve standalone biological paper; preserve serious provenance finding.
The intended19-case source remains unidentified. RNA year2021 has a high EMC
specimen opposite to pooled direction; tiny batch strata cannot be explained away.
No prognostic, protein, dependency or universal-low-expression inference.

Reopening needs actual new measurements addressing the stated question: individual
authenticated EMC H19 tissue observations, a usable EMC protein/spatial cohort with
a consequential hypothesis, or the true cartilaginous comparator behind H1FX.
Resolving a source inventory alone does not establish a worthwhile paper.
''')
append_once('COVERAGE.txt','FINAL SOURCE EXTENSION — evaluated 4 October 2026', '''
Reproducible source audit: evaluate_protein_sources.py -> protein-spatial-eligibility.json.
Retrieval URLs/bytes/SHA in protein-scout-retrievals.json, final-source-retrievals.json
and final-supplement-retrievals.json. Source retrieval alone is not biological analysis.

EVALUATED / DEMONSTRABLY UNSUITABLE FOR AUTHENTIC EMC BIOLOGY
Burns2023 DOI10.1038/s41467-023-39486-2, fullXML + SupplementaryData1: all11
histologies/n sum to321 with no residual Other group or EMC. Actual aggregate
eligibility evaluation, not a claim of specimen-level molecular reauthentication.
Sarquarium2024 DOI10.1038/s44320-023-00004-7, fullXML+DatasetEV1: all17 model
culture/genetic labels inspected. A204,G401,HS729,HT1080,KHOS-240S,KHOS-NP,MES-SA,
RD,RD-ES,SK-ES-1,SK-LMS-1,SW1353,SW684,SW872,SW982,SYO-1,VA-ES-BJ. No authentic
EMC. SW1353 is not a substitute for EMC; shared KHOS origin is not2donors.
Tang2024 DOI10.1038/s41467-024-45306-y: all272 clinical rows inspected, including
all8 otherFS. Seven specific labels:4adult fibrosarcoma,2inflammatory myofibroblastic
tumor,1low-grade myofibroblastoma. SS-5 specific histologyNA remains unresolved.
SS-81 has shifted source columns but identifiable synovial labels; retained intact.
No protein/phosphoprotein values read for a biological comparison. Complete source
workbook retained24,908,570bytes within75MBbudget; amendment precedes values.
Ngo2025 DOI10.1002/cac2.70077: EMC mention is bulk external expression context;
the spatial/single-cell experiment is epithelioid sarcoma. No new EMC spatial result.
PRIDE extraskeletal search returns2calciprotein-particle projects, not EMC;
NR4A3 search returnsempty. These keyword results do not exclude hidden EMC samples.

VERIFIED PRIOR EVALUATION REUSED / FRESH PRIMARY ABSTRACT CHECK
Noguchi paired-proteomics2025 DOIs10.14889/jpdm.2025.0007(35pairs,PXD061872) and
10.14889/jpdm.2025.0006(31pairs,PXD061874): primary model lists do not include
NCC-EMC1-C1. Prior repository exclusion reused after checking original lists.
Older audit accessionPXD061813 must not silently replace current sourcePXD061874.
Willems2010 DOI10.1002/path.2771 imagingMS concerns MFS/MLPS, not EMC. No new values.
Previously excluded ADC/protein panels and Gijsels2026 ct m2.70722 not rerun.

EVALUATED SOURCE WITH UNAVAILABLE EMC-SPECIFIC MEASUREMENTS
H19 DOI10.1002/cam4.71305, fullXML/4clinical tables/source creator resource:
two TMA sets name EMC, but final Others26/150 are not separable into EMC cases.
No public per-EMC score/outcome/denominator or TMA-overlap crosswalk recovered.
No supplementary-material inXML; data availability onlyCCLE, not newTMA values.
MUG-EMCS qPCR not eligible as authentic EMC without NR4A3 authentication; primary
model-creator resource https://www.medunigraz.at/en/team-beate-rinner explicitly
describes mesenchymal chondrosarcoma, contrary to H19 article's myxoid label.
No authenticated EMC Gapmer perturbation measured. No H19 absence/dependency claim.
ProCan2021 primary poster(ANZSA,Connolly): title205 versus methods203samples/178patients,
>30histologies. Raregroups<5 removed from displays; chondrosarcoma unsubtyped.
All available postertext evaluated, no individual EMC values/labels recovered.
No disease absence conclusion; potential EMC specimens remain unidentified.

PENDING ACCESSIBLE ELIGIBILITY / STAGED GAP, NOT EXCLUSION
PanAtlas2025 PXD054790 DOI10.1016/j.ccell.2025.05.003: metadata evaluated,
999primary tumors22cancers1129total samples. Individualsoft-tissue histology
manifest not evaluated. Publisher page403 inthispass; publicrepository remains
potentialroute. CPTAC-SAR88patientimagingcollection is another sample-identity
lead with no protein measurement or exactEMC crosswalk evaluated here. These
block any complete-public-proteomics claim, which is not advanced.
GSE140686 methylation, possible newmyoepithelial case21array, GSE179720 actual7EMC
RNA crosswalk, incomplete mTORclinical conditions and olderEMC arrays remain as
above. No suitable accessible source is relabelled unsuitable for resource reasons.

INDEPENDENT H1FX CHALLENGE
review_h1fx.py/h1fx-independent-challenge.json bind exact leadplan,amendment,
analysis,result,primaryGEOlabels and PeerJXML. RawH1FX values re-extracted from
TPMmatrix and originalSOFT and17 contrasts independentlychecked. Scope/value
stop is not completeclaimcoverage: olderarrays suchasGSE4303 and actual intended
19-case cartilaginous-comparison source remain pending/unresolved. No additional
sourceprocessing needed to shelve, but reopening must carry these gaps forward.

Independent genomic worker reports new BostonGene TSC1/2 events; see its final
round2 source receipt for alleles/units limitations. This lane evaluated the
model bridge, not every genetic lesion. Do not infer lack of other mTOR lesions.
''')
search={'date':'2026-10-04','scope':'Bounded primary-source discovery; not exhaustive field absence claim',
 'families':['EMC/EMCS/ESMCS and extraskeletal myxoid chondrosarcoma','NR4A3/TEC/CHN/NOR1 EWSR1/TAF15 fusion perturbation,chromatin,ChIP,ATAC,methylation,splicing','authentic USZ20/22/23,NCC-EMC1-C1 mTOR,everolimus,temsirolimus,rapamycin','EMC proteome,proteomics,single-cell,spatial,methylome; pan-cancer/sarcoma artifact manifests'],
 'recorded_queries':['"extraskeletal myxoid chondrosarcoma" "proteomic"','"extraskeletal myxoid chondrosarcoma" "single-cell"','"extraskeletal myxoid chondrosarcoma" "spatial transcriptomics"','"extraskeletal myxoid chondrosarcoma" "methylome"','"NCC-EMC1-C1" proteome OR mass OR spectrometry OR PXD','"sarcoma" "mass spectrometry" "myxoid chondrosarcoma"','"sarcoma" "single cell" "NR4A3" -T-cell -Treg','"ProCan" "extraskeletal"','"CPTAC-SAR" "chondrosarcoma"','"PXD054790" "sarcoma"','"MUG-EMCS" "mesenchymal"','"Clinical Significance and Therapeutic Potential" "H19" supplemental'],
 'method':'Primary studies/fullXML, citation trails, supplements, GEO/ENA, PRIDE metadata and model-creator resource. Search families summarize other queries not preserved verbatim; do not represent this as a complete machine query log.',
 'limits':'ProCan/PanAtlas/CPTAC-SAR unresolved identity; all promotion blocked for any claim needing unevaluated relevant source. Bounded round ends by explicit scientific-value decisions, not corpus-size exception.'}
(P/'search-record.json').write_text(json.dumps(search,indent=2),encoding='utf8')
(P/'HANDOFF.txt').write_text('''4 October 2026 — functional/regulatory worker, round2 integration checkpoint
Decision: SHELVE standalone regulatory, mTOR-response, protein/spatial and H19
papers. Zero surviving newly demonstrated EMC disease findings from this lane.
H1FX independent challenge agrees SHELVE biological paper; preserve provenance error.
This is the end of this bounded round, not global discovery exhaustion. No manuscript.

Read RESULTS.txt and COVERAGE.txt before reuse. Original SCOPE, MTOR-PLAN,
PROTEIN-SPATIAL-SCOPE and dated amendment are preserved. No TMEM266/DDR revival.
New source recovery: valid Zullow clinicalS1all11 EMC rows, full Bangertermethods,
all30myoepithelial rows, publicprotein cohortmanifests and H19fullXML. Recovery
does not establish new disease biology. Allsource hashes/reproducible counts retained.

Material gaps/reopening: map Zullow7RNA to11clinical cases and originalvalues;
obtain authenticated perturbation/chromatin/isoform/methylation with newquestion;
resolve myoepithelialcase21deposit; establish TSC2 loss/function and matchedEMC
response rather than assume rapalog sensitivity; recover individualH19EMC TMA
values and authenticate MUG-EMCS; authenticate PanAtlas/ProCan/CPTAC-SAR potential
EMC specimens if a worthwhile protein question emerges. H1FX needs actual19case
source/truecartilaginous contrast plus completeeligibleEMCevidence. Olderarrays,
GSE140686 and ambiguousclinicalmTOR exposures remain visible pending/unavailable.

Independent reviews completed: clinical Oliveira all23rows and conditional risk;
H1FX originalsource and17arithmetic contrasts, validity versus scientificvalue.
Independent genomic worker challenged TSC2value and added contraryBostonGene
event evidence; its ownsource receipt remains authoritative for that poster.

Actual scripts run successfully: source_scout.py, parse_html.py,
evaluate_eligibility.py, analyze_eligibility.py, fetch_mtor.py,
read_mtor_sources.py, review_clinical.py, scout_final_sources.py,
evaluate_protein_sources.py, review_h1fx.py, finalize_packet.py.
Ad-hoc bounded urllib retrievals also saved source receipts. A preliminaryH1FX
parser expected a space after Histology:, failed its count assertion, was fixed
to stripoptional whitespace, then passed. No failedcheck disguised as PASS.
Two mistaken earlyretrievals are explicit in retrieval-identity-corrections.json.

Writer: C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-functional
Only research/autonomy/fresh-discovery-2026-10-04-round2/regulatory modified.
Round1 preserved. Worker made no commits, pushes, PRs or external record changes.
BaseHEAD373a430957178c1ce76cab89b3ae21b337cb3fc0. Files remain local/uncommitted
until lead integration; do not describe as merged. Parent owns sharedqueue/lock.
No owned UI/browser/headless jobs. All source retrievals and Python commands
completed; no continuing owned process. Daily06–10ET restriction passed onward.
No runtime installation; packet below75MB, C free staysabove10GiB.
MANIFEST.json records all files except itself with exactbytes/SHA256.
''',encoding='utf8')
files=[p for p in P.rglob('*') if p.is_file() and p.name!='MANIFEST.json']
entries=[{'path':str(p.relative_to(P)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)]
out={'utc':datetime.now(timezone.utc).isoformat(),'files':entries,'total_bytes_excluding_manifest':sum(r['bytes'] for r in entries),'C_free_bytes':shutil.disk_usage('C:/').free,'base_HEAD':'373a430957178c1ce76cab89b3ae21b337cb3fc0','worker_commit_push_status':'no worker commits or pushes; local uncommitted packet','owned_processes_running':False}
assert out['total_bytes_excluding_manifest']<75*1024**2
assert out['C_free_bytes']>10*1024**3
(P/'MANIFEST.json').write_text(json.dumps(out,indent=2),encoding='utf8')
for e in entries:assert hashlib.sha256((P/e['path']).read_bytes()).hexdigest()==e['sha256']
print(json.dumps({'files':len(entries)+1,'bytes_including_manifest':out['total_bytes_excluding_manifest']+(P/'MANIFEST.json').stat().st_size,'manifest_sha256':hashlib.sha256((P/'MANIFEST.json').read_bytes()).hexdigest(),'C_free_bytes':out['C_free_bytes'],'verified':'all file hashes'}))
