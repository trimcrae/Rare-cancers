from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E,datetime
D=Path(__file__).resolve().parent
L=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-lead/research/autonomy')
P=Path('C:/Projects/EMC-Research')
reused=[
L/'fresh-discovery-2026-10-04-round2/regulatory/brenca2019.xml',
L/'fresh-discovery-2026-10-04-round2/regulatory/filion2009.html',
L/'fresh-discovery-2026-10-04-round2/regulatory/filion2009-source-evaluation.json',
P/'research/autonomy/tmem266-tissue-2026-10-03/SOURCE-AUDIT.txt',
P/'research/manuscripts/aso/fusion-junction-aso-data-sources.json',
P/'research/modalities/junction-transcript-sensitivity.json',
P/'research/modalities/nr4a3-fusion-junction-atlas.json',
L/'fresh-discovery-2026-10-04-round3/mirna_deposition/AMENDMENT-01.txt',
L/'fresh-discovery-2026-10-04-round6/nr4a3_regulatory/RESULTS.txt',
]
receipts=[]
for p in reused:
 if p.exists(): receipts.append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'use':'Prior source/identity or assay-scope evaluation only; no prior ranking imported.'})
 else: receipts.append({'path':str(p),'status':'not present at this path; not represented as verified reuse'})
(D/'reused-source-receipts.json').write_text(json.dumps(receipts,indent=2),encoding='utf8')
text=lambda x:' '.join(''.join(x.itertext()).split())
b=E.parse(reused[0]).getroot()
t=b.find('.//table-wrap[@id="path5284-tbl-0001"]')
rows=[[text(c) for c in r] for r in t.findall('.//tr')]
out={'source_sha256':receipts[0]['sha256'],'specimen_table':rows,'relevant_paragraphs':[text(p) for p in b.findall('.//p') if any(k in text(p).lower() for k in ['cryptic','frozen material','two major taf15','centrally reviewed'])], 'assessment':{'n_patient_tumors':12,'EWSR1':7,'TAF15':5,'matched_frozen_conditions':{'n':5,'EWSR1':4,'TAF15':1,'mapping':'not identified individually in main text; results data not shown'},'engineered_cultures':'Separate from patient tumors. Prior raw-deposit audit:11 engineered libraries, including4E-N,4T-N,3NR4A3; eightE-N/T-N mapped, remaining15records not individually mapped. Do not infer23patients.','prior_art':'Two human tumor-detected TAF15 acceptors explicitly already reported; engineered variants indistinguishable for colony formation under conditions tested.','measurement_gap':'No donor-by-junction abundance or native/fusion isoform-balance table exposed in inspected original article; gene-selected S1/S2 cannot establish one.'}}
(D/'brenca-source-evaluation.json').write_text(json.dumps(out,indent=2),encoding='utf8')
r=json.loads((D/'racanelli-extraction.json').read_text())
rows=[row for table in r['tables'] for row in table['emc_rows']]
ids=[row[0] for row in rows]
assert ids==['7','12','55','56','57','58','59','60','61','62','63','64','65','100'],ids
assert len(set(ids))==14
out={'source_sha256':r['source_sha256'],'emc_record_ids':ids,'n_source_records':14,'independent_donors':'Not assumed from case numbers; no Brenca cross-source overlap map is released.','reported_partners':{'EWSR1-NR4A3':12,'TAF15-NR4A3':1,'NR4A3_FISH_positive_fusion_not_detected':1},'conditions':[{'case':'7','assays':'RT-qPCR; AMP-FPS Illumina positive; TS-Fusion and TS-PanCancer native default calls NFD; alternative algorithms investigated by original authors.'},{'case':'12','assays':'RT-qPCR; AMP-FPS Thermo positive; TS-Fusion positive; TS-PanCancer not done.'},{'case':'55–65','assays':'AMP-FPS Illumina; initial FISH or RT-qPCR as recorded; all11 named fusions detected; only58TAF15.'},{'case':'100','assays':'NR4A3FISH rearrangement; AMP-FPS Illumina NFD. Missing probes/unusual junctions/other technical or biological alternatives remain.'}], 'interpretation':'Detection validation and incomplete ascertainment. Neither NFD nor absence of an alternative variant is zero expression. OneTAF15 cannot establish a recurrent partner-group phenotype. No novel effect computed.'}
(D/'acc-emc-sample-audit.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('Source audit passed:',len(ids),'ACC records;',len(rows),'rows.')
print('Reuse receipts:',len(receipts))
