from pathlib import Path
import json,hashlib,datetime,subprocess,shutil
P=Path(__file__).resolve().parent
result='''Functional-model discovery pilot — 4 October 2026

Decision: SHELVE THE STANDALONE DDR PAPER. No surviving new EMC finding.
Observations below are original authors' public measurements reanalyzed here.
They show compound, exposure and endpoint specificity; they do not establish
an unpublished EMC vulnerability or blanket DDR resistance.

2023 source evaluation
Original Figure5 and expanded FigureEV5 numerical workbooks recovered. All
eligible USZ-22_EMC2 curves evaluated:4day oxaliplatin/doxorubicin/trabectedin,
8day olaparib/niraparib/adavosertib,12day the same inhibitors. All11same-assay
models retained including UWB1.289 positive control:99curves/748source rows.
USZ22 is source-authenticated TAF15::NR4A3, sourceHRDscore2, the same culture as
Bangerter2022. Technical columns are not patients; unlabelled rows stay unlabelled.

Selected source response means, one EMC model:
Doxorubicin4day:23.69400 at10uM,35.20095 at1uM,56.69872 at0.1uM.
Trabectedin4day:52.00481 at0.1uM; preceding unlabelled row has no assigned dose.
Oxaliplatin4day:67.57365 at200uM,93.11509 at100uM.
Olaparib8day:80.6274/88.8947/98.2498 at20/10/1uM;
12day:83.04954/88.27718/101.33746 at the same concentrations.
Niraparib8day:0.5144/65.3247/95.3253 at20/10/1uM;
12day:0.17747/5.09361/90.47295 at the same concentrations.
Adavosertib8day:3.6757/56.9031/77.8309 at20/10/1uM;
12day:0.17442/47.72182/76.37952 at the same concentrations.
All concentrations/replicates in ddr-results.json. Original figures already show
these differences. No PARP-class vulnerability, repair defect, clinical window or
causal time effect follows. EV5H-K combination panels measure REA1/LG1, not EMC;
all four workbook names and original figure labels resolve reviewer eligibility.

2025 numerical deposit and 2026 publication
Final discovery refresh located Mendeley10.17632/3fy2pj3cr6.1,28May2025, with the
2026paper's title/authors. Its description explicitly says Cell Reports Medicine
submission. It is not assumed numerically identical to final Cancer Letters2026:
panel numbers differ and final supplementary heatmap includes additional models.
XLSX115056bytes verified SHA256:
a3eec1dd81423727283939d394e3a51a8c404e2c377a840ba3ccb5946098ec5f.
All26sheets screened; every explicitly identified EMC measurement evaluated:
8dose curves/48dose points/144technical cells,8sourceAUCsummaries,5fiber-condition
columns including separate controls,3pATR-positive-nuclei summaries,10signature
counts. All comparators in those six eligible sheet sets were included:48curves/
288points,48AUCsummaries,30fibercolumns,6pATRmodels and6transcriptmodels.

Counterexample to blanket ATR resistance: USZ23 source response to berzosertib
averages5.8473 at1uM and0.04968 at10uM versus100mean vehicle control. At1uM,
camonsertib84.9385,ceralasertib122.9148,elimusertib84.3231,rabusertib126.6417,
prexasertib115.6126,azenosertib175.1058,adavosertib89.9373 differ substantially.
All technical ranges and doses remain in mendeley-analysis.json, including high
dispersion/nonmonotonicity. No IC50 fit or drug-as-donor inference. AUC sourceN=13
is retained as reported and is not13patients; its exact construction is unresolved.

Fiber measurements also preclude an all-endpoint nonresponse claim. Sheet4D:
EMC3mean fiber length29.8027DMSO versus16.3460camonsertib,150fibers/condition.
Separate sheet4E-F:13.9520DMSO,13.8680rabusertib,15.8440adavosertib,150fibers each.
The differing control baselines cannot be pooled across assays. Physical units,
dose, exposure and replicate hierarchy remain unknown without methods. This is
descriptive source evaluation, not proof of target engagement, dependency or a
therapeutic window. No fiber-level p-value or donorCI was manufactured. pATR source
summaries2.59/2.86/7.10 are retained; low/zero signature transcript counts do not
measure a functional HR defect or knockout.

The final2026ten-page supplement was fully inspected as text and rendered pages.
SupplFig4C includesUSZ23 under all8ATR/CHK1/WEE1agents with the HRDlow group.
Text alone misses the image-only EMC label. Its transformedAUC legend includes
negative values; none were digitized. Qualitative heatmap clustering cannot erase
the compound-specific positive numerical responses. Earlier missing numerical
source gap is partly resolved by the2025deposit. Remaining gaps: final2026methods,
deposit-to-final concordance, unlabelled sheets4I(caspase3)/5E(pCHK1) model identity,
additional possible main-figure EMC conditions andUSZ23vsUSZ20donor independence.

Other prior art and value
Bangerter40drug/selected two-model combinations and Iwata221screen/24IC50 complete
prior extractions retained from immutableGit5d2f2e2116, with fresh primary checks.
Carfilzomib, combinations, brigatinib,panobinostat,romidepsin leads already published.
No pooled potency/fusion-partner inference across incompatible methods. Gracilla2026
full text and patentWO2024226662A2 broad embodiments supply no authenticated EMC
experiment. DisputedHEMCSS/pan-cancer lines cannot substitute for EMC. No important
existing EMC-specific claim was identified that these source measurements overturn.

This evidence guardrail does not clear the user's new-disease-knowledge bar.
Reopening requires compatible, authenticated independent EMC measurements or a
consequential EMC-specific existing claim that complete evidence can challenge.
Merely obtaining methods, replotting published curves or narrowing a title does
not create novelty. No standalone manuscript should be drafted.

Verification: analyze_ddr.py extracts2023data; verify_ddr.py independently parses
rawOOXML and passes99curves/748points. analyze_mendeley.py extracts the2025deposit;
independent genomic worker parsed rawOOXML for every EMC condition. Arithmetic
and coverage checks do not establish scientific value. No external record changes,
outreach, paid resource, manuscript or publication occurred.
'''
(P/'RESULTS.txt').write_text(result,encoding='utf-8')
c=(P/'COVERAGE.txt').read_text(encoding='utf-8')
c=c.replace('All six EMC drug curves in Figure5E/F/G/I/J/K evaluated with every reported\nconcentration/technical column and unlabelled rows preserved. Positive control\nUWB1.289 and all HRDhigh/low sarcoma comparison curves included,66total. Other\nFig5 combination panels contain no EMC model.','All nine EMC drug curves in Figure5E/F/G/I/J/K andEV5A/B/C evaluated with every\nconcentration/technical column and unlabelled rows preserved:99model-curves/748rows.\nPositive controlUWB1.289 and every HRDhigh/low comparator included. Figure5 and\nEV5H-K combination panels contain no EMC; exact workbook labels and original\nimage distinguish REA1/LG1 from the broaderHRDlow group. EV5E-G sourceAUCsummaries\nare retained as summaries of measured curves, not additional independent samples.')
c=c.replace('9.SOURCE-GATE EVALUATED;NO DDR RESPONSE: XenoSarc2019,DOI10.1158/1535-7163.MCT-18-0892\n(verify DOI before reuse),publisherTable2','9.SOURCE-GATE EVALUATED;NO DDR RESPONSE: XenoSarc2019,publisherTable2')
c=c.split('\n\nDATED UPDATE2026-10-04')[0]
c+='''

DATED UPDATE2026-10-04 following independent discovery refresh; supersedes the
earlier numerical-data gap where specified, not the original frozen question.
11.EVALUATED: Mendeley10.17632/3fy2pj3cr6.1,2025submission source version for the
Planas-Paz ATR title/authors,https://data.mendeley.com/datasets/3fy2pj3cr6/1.
Landing metadata, file manifest and source XLSX retained with matching publicSHA.
All26sheets screened by names/headers/cells. Eligible EMC sheet sets:
2A:10signature transcript counts, all6models; source callsUSZ23SARC-HRDlow,
  not evidence that low/zero counts produce functional HR deficiency.
2E-2L:all8drugs,6concentrations includingvehicle,3sourcecolumns,all6models.
2M-2O:all8sourceAUCmean/SD/Nsummaryrows for all6models. N=13meaning unresolved;
  no assumption of13patients or independent biological repeats.
4D:all150values in EMC3DMSO/camonsertib and all6modelconditions.
4E-F:all150values in EMC3DMSO/rabusertib/adavosertib and all6modelconditions.
5B:all3EMCpATR-positive-nuclei source summaries and all6models.
Analyzed in mendeley-analysis.json; original values in XLSX and cell snapshot.
Strong berzosertib response and camonsertib fiber change preserved, preventing
blanket ATR/DDR-resistance claims. Different fiber control baselines not pooled.
No target-engagement/dependency/clinical inference from these endpoint changes.
Remaining sheets with explicit sample labels identify other sarcomas, including
all combination/sphere panels; 'gemcitabine' substring is not anEMCsample.

12.PENDING IDENTIFICATION / UNAVAILABLE METHODS: deposit4Icleavedcaspase3 and5E
pCHK1 have measurements but no model label. Cannot mark either as EMC or as
an EMC-negative condition without the source main captions/methods. This is an
explicit coverage gap. Final2026mainmethods remain inaccessible through tested
public routes; May2025deposit versus2026publication quantitative concordance not
established. Published supplementaryheatmap has9models vs6in deposited maincurves.
USZ23donor crosswalk also unresolved. These block comprehensive quantitative or
mechanistic claims; the numerical deposit is usable evidence with version limits.

13.PRIMARY PATENT EVALUATED FOR ELIGIBILITY: WO2024226662A2 listsEMC andEWSR1::NR4A3/
TAF15::NR4A3 in broad embodiments, but recovered experimental methods useU2OS,
293T,A673,TC71,ES8,SU-CCS-1,HCC364. Independent microenvironment reviewer found
no authenticated EMC experimental measurement. Patent scope is not an empirical
EMC vulnerability to refute. https://patents.google.com/patent/WO2024226662A2/en

Independent omission/numeric challenge: genomic_clinical identifiedEV5followup;
microenvironment challenged compound interpretation/novelty and addedpatent.
Lead discovery refresh found numerical Mendeley source. Contrary positive data
changed the scope of permissible wording, not the no-new-discovery decision.

Independent Mendeley rawOOXML crosscheck passed all48EMCdosepoints/144technical
cells,8AUCrows,750fiber measurements,3pATRvalues,10signaturecounts; maximum
summarydifference2.84e-14. Receipt: sibling genomics/mendeley-crosscheck-receipt.json.
Additional numerical2023AUCsource evaluation:ev5-auc-evaluation.json retains all
99model-condition sourceAUC/SE/CI values and evaluatesEMCagainst every same-drug
comparator. These summarize alreadymeasured curves and are not extra donors;
sourceCI must not be presented asEMCpopulation uncertainty or pooled acrossdrugs.
Root's boundedOpenAlex/EuropePMClookup found DOIonly, no repositoryPDF/author
manuscript; PMID41651400inPMC=N,inEPMC=N,hasPDF=N,authMan=N. Stop access attempts.
'''
(P/'COVERAGE.txt').write_text(c,encoding='utf-8')
handoff='''4October2026 functional worker handoff
Decision: SHELVE STANDALONE DDR PAPER; zero surviving newly demonstrated findings.
Read RESULTS.txt/COVERAGE.txt before reusing favorable or negative numbers.
No inherited ranking, no TMEM266 reopening, no manuscript.

Submitted CSPG4 reference actually read from immutableGit097f863ab83d242022e05637da39bafbad03b4f2:
research/release-candidates/preprint-short-formats-20260924/cspg4-figure1-revision/letter.md.
It reports9EMCvs393malignantreferences,A=.846; all12/13attenuate; GIST/DFSP higher;
bulkRNA and possible historicalcohort overlap limit interpretation. It served as
an empirical EMC contribution benchmark, not inherited priority or publication bar.

Completed:2023all9EMCdrugcurves with99comparator-curves/748source rows independently
verified; final2026all8inhibitor EMC heatmap cells qualitatively evaluated; newly
located2025Mendeley full26sheet numericaldeposit screened with every identified
EMC condition evaluated:8drugcurves/8AUCrows/5fiberconditioncolumns/3pATRvalues/
10signaturecounts and all matching comparators. Original40/221drug analyses reused.
USZ23berzosertib response and camonsertib fiber change forbid broad ATRresistance.
Authors' original measured findings do not become new knowledge by re-extraction.

Remaining:2026mainmethods; olddeposit/finalpublication concordance; unidentified
model in4I/5E; any additional eligible mainfigure EMC conditions; USZ23donorcrosswalk;
historical disputedlineidentity. No unmeasured/inaccessible condition callednegative.
Reopen only for substantive independent compatible EMC evidence or an important
existing EMC-specific claim contradicted by complete public evidence; methodsalone
or a narrower title do not create novelty. No new clinical/targetdependence claim.

Reproduction uses installedPython withPYTHONPATH=C:/Projects/EMC-Research/.cache/python-deps
andPYTHONDONTWRITEBYTECODE=1. analyze_ddr.py is offline except immutablegitreads;
verify_ddr.py checksrawOOXML. inspect_mendeley.py preservesallcells;
analyze_mendeley.py summarizes alleligibleconditions/comparators withoutpvalues.
Review receipts from genomic worker use independentlyparsedrawOOXML. Retrieval
scripts/metadata/hashes preserve primaryURLs. FailedPMCZIPHTMLchallenge is labelled
asfailure, not data. The2026PDF neededPowerShellGET afterurllib403; textscriptUTF8
fix addressedstdoutonly and did not change saved sourcecontent.

Independent micro review: microenvironment-independent-challenge.json and
review_micro_mapping.py. Actual-column manifest confirms22537full50ntprobes,
no forward/RC duplicates; all12rawsample/run receipts match. Gate75% is workflow
allocation, not assayinvalidity; pendingraw+unvalidatedclinicalcrosswalk preclude
biology. No additional countstreams started for this challenge.

Ownership only/root/functional_models within this packet. Writer:
C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-functional.
BaseHEAD373a430957178c1ce76cab89b3ae21b337cb3fc0. No workercommit/push/PR/merge.
Files remain uncommitted/untracked until parentexplicitly integrates. Coordinator
owns integration; do not call localfilesmerged. No owned processes, browsers,
automation, paidrequests,outreach orpublication remain running at handoff.

Standing06-10America/New_YorknoUIrestriction preserved; allrequests quietAPI/files.
PDFsourcerendering began after12:04local withtimecheck. No app/window/browser UI.
Packet budget<=50MB,freeC>=10GiB. MANIFEST.json binds finalfiles exceptitself.
'''
(P/'HANDOFF.txt').write_text(handoff,encoding='utf-8')
# Manifest written only after prose and deterministic analysis packets settle.
manifest={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_head':subprocess.check_output(['git','-C',str(P.parents[3]),'rev-parse','HEAD'],text=True).strip(),'status':'worker files uncommitted; no commit/push','free_bytes_C':shutil.disk_usage('C:/').free,'files':[]}
for p in sorted(P.iterdir()):
    if p.is_file() and p.name!='MANIFEST.json':
        manifest['files'].append({'path':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
manifest['total_bytes']=sum(x['bytes'] for x in manifest['files'])
assert manifest['total_bytes']<50*1024*1024 and manifest['free_bytes_C']>=10*1024**3
(P/'MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in manifest.items() if k!='files'},indent=2))
