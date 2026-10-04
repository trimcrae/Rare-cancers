"""Append final source-completeness challenge, preserving the provisional receipt."""
from pathlib import Path
import json,hashlib,datetime
P=Path(__file__).resolve().parent
I=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-microenvironment/research/autonomy/fresh-discovery-2026-10-04-round3/immune')
files=['RESULTS.md','COVERAGE.md','HANDOFF.md','AMENDMENT-20261004.txt','pollack2020.xml','PMC7489365-jamaoncol-e203689-s002.pdf','pollack2020-supp-text.txt','pollack-archive-followup.json','pollack-supp-7.png','pollack-supp-14.png','pollack-supp-16.png','pollack2020-figure.jpg','kelly2020.html','kelly-supp1-followup.json','kelly-cdn-receipt.json']
files=[n for n in files if (I/n).exists()]
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'previous_receipt_sha256':hashlib.sha256((P/'independent-immune-review.json').read_bytes()).hexdigest(),'decision':'Agree with scoped shelving; no new EMC immune-state/response claim is supported. This is not a claim that immunotherapy fails or that every possible public linkage was excluded.','additional_evaluation':[
'Directly inspected Pollack sourceTable1:3conventionalchondrosarcomas,1clearcellchondrosarcoma and1EMC. VisualeFigure4 Chondrotrajectories have no subtypeIDs, so cannot assign any individual trajectory or even bestSD toEMC. Mainwaterfall pools allotherhistologies.',
'VisualPollack eTable2 contains aggregate29IHCscores with headingAllPatientsn33; no case IDs or subtypecrosswalk. eTable4 is pan-cohort association output, not patient-levelNanoString matrix. SuccessfulS2recovery closes the named supplement check, but doesnotcreate EMC immune-response measurements.',
'Kelly relevant supplementaryfile isS1, notS2protocol. Worker corrected this and retained explicit failurereceipts:PMCchallengeHTML, EPMC403, legacyNCBI404 andpublisher/CDN403. The CDNfilename was a labelled inference, not a verifieddownload. No bypass or alternate identity inference attempted. Its eTable4 is material to linkage but was not recovered; keep unavailable-after-bounded-attempts, not evaluatednegative.',
'Rechecked finalRESULTS/COVERAGE: sameNCT03277924extension and no demonstrateddonorindependence preserved; Starzer case7 authorshistology only; possibleVienna/MSKtrial overlap; threepairedRNA andthreebloodEMC subsets not assumedsame. Additional identified trial/case sources pending remain manuscript blockers if a claim is revived.',
'No missing numerical EMC immunevalue was exposed in the specific retrieved supplements inspected here. Broader exhausted-source or biological-inefficacy conclusions would be overclaims. Reopening with exact authenticatedpatient-assay-outcome linkage remains scientifically appropriate.'], 'files':[{'path':str(I/n),'bytes':(I/n).stat().st_size,'sha256':hashlib.sha256((I/n).read_bytes()).hexdigest()} for n in files]}
(P/'independent-immune-review-final.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('Bound final review',len(files),'source/result files')
