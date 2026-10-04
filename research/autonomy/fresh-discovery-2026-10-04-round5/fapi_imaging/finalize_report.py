import pathlib,json,datetime,hashlib,shutil,subprocess
D=pathlib.Path(__file__).resolve().parent
p=D/'write_gate_report.py';s=p.read_text(encoding='utf-8-sig').replace("'doi':'10.1007/s00259-022-05775-5'","'doi':'10.1007/s00259-022-05700-4'").replace("# The initial guessed Gu DOI is deliberately not authoritative; bound reviewer will supply verified DOI.","# Bind independently authenticated source DOI; metadata only, no new outcome evaluation.").replace("x.pop('doi');x['status']","x['status']")
p.write_text(s,encoding='utf-8')
p=D/'COVERAGE.json';j=json.loads(p.read_text());
for x in j['sources']:
 if x['source']=='Gu2022': x['doi']='10.1007/s00259-022-05700-4';x['source_sha256']='5529103dd806780784cb5c9b2b23714f330316d68b031a2f5d788642da66016f'
 if x['source']=='Zhang2022':x['preprint_sha256']='47ccc6ffb43f3ee600049ffb605abae67a740d366d51022653948d2ec866b830'
p.write_text(json.dumps(j,indent=2),encoding='utf-8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat();W=D.parents[3]
head=subprocess.check_output(['git','-C',str(W),'rev-parse','HEAD'],text=True).strip()
text=f'''Clinical FAPI-imaging handoff {now}
Decision: SHELVE standalonepaper atthis boundedgate; no demonstratedEMCfinding. Sourceeligibility and dataaccess notsolved; broadexhaustion isNOTclaimed. NoEMCquantitativepilot executed, because no sourceauthenticatedaneligibleEMCpair. OriginalPLAN/PILOTandAMENDMENT01preserved.

Remaining exactquestions: Kessler47 SupplementalTable1 +Table6; Lanzafame200SupplementalTable3 pluspatientvalues; Pabst155appendixp5; Novruzovall6STSsubtypecrosswalk; KoerberNOS; Ferdinanduscase2fibrosarcoma/case11spindle. Alsoeachstagedclinical sourceinCOVERAGE. YanggenericnasalCHSfullpathology and Liu22individualhistologies remainunresolved. Genericfibrosarcoma inZhangpreprint isnotmolecularEMCexclusion.

Reopeningconditions: publicauthenticatedEMCcase-to-scan/lesionmapping, pairedclinicalFAPI/FDGmeasurements/treatmentchronology and independentlesionverification sufficient to answer a new diseasequestion beyondpublishedaggregate results. Evaluateall eligibleEMCscans includingnegative/treatedconditions and deduplicatestudies; then executepreservedplan ordatedamendment. NoTMEM266/surfaceRNA rescue. No outreach authorized.

Actual scriptsrun: fetch_sources.py, fetch_fulltext.py, fetch_clinical_followup.py, fetch_2026.py, fetch_supplement.py, fetch_last_gate.py, fetch_citation_trail.py, fetch_second_order_gate.py; evaluate_sources.py, evaluate_supplements.py, evaluate_citation_trail.py, read_clinical_checks.py, evaluate_second_order.py, validate_eligibility.py; write_gate_report.py andfinalize_report.py. PDFPabst retrievedwithordinaryWindowscurl.exeafterurllibcertificateerror, noTLSbypass. Allrequests/output receiptskept. No supportedbrowser/UI/headless/screenshots or renderperformed. Reproductionuses installedPython andPYTHONPATH C:/Projects/EMC-Research/.cache/python-deps, PYTHONDONTWRITEBYTECODE=1. Allsourcefileshashbound inMANIFEST.

Validation: originalXML/DOCX identityrosters parsed; completecategory/rowcounts asserted; no inferencefromnumericaltherapytables. Independentfunctionalreview supports scopedSHELVE and sourcecounts; reviewreceipt boundseparately. Everydatasetfileisactualsourceorexplicitextraction, notsyntheticpatients.

Ownership/status: onlynewround5/fapi_imagingwritten; R1–R4earlierpackets untouched. WorktreeHEAD {head}. No commits orpushes made bythisworker; thispacketis uncommitted/untracked localwork, notmerged. Rootowns integrationandsharedcoordination. Noownedprocess/session/browser/automationhandlesrunning; allcommands completed synchronously. No externalrecordwrite. Freebyteswhenhandoffsaved {shutil.disk_usage(D).free}; retainedcap10MiB.

Separate restriction: R5tissue worker stoppedwithplatformcontent-accesssafetyerror; notread/retried/takenover, notordinarynegative data. R4blockedtasks unchanged. Thisclinical lane didnotreceiveplatformsafetydenial; ordinarysourceHTTPaccess failures preserved.
'''
(D/'HANDOFF.txt').write_text(text,encoding='utf-8')
print(head,now)
