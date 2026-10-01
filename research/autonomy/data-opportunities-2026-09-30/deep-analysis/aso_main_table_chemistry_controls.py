#!/usr/bin/env python3
import argparse,collections,datetime,hashlib,json,pathlib,re
P=pathlib.Path;ap=argparse.ArgumentParser();ap.add_argument('--input',default='research/autonomy/data-opportunities-2026-09-30/deep-analysis/results/clinical-and-ASO-primary-supplements.json');ap.add_argument('--output',default='campaign-output/aso-main-table-chemistry-controls.json');a=ap.parse_args();p=P(a.input);b=p.read_bytes();d=json.loads(b)
while isinstance(d.get('result'),dict):d=d['result']
src={s['id']:s for s in d['sources']};out={'schema':'aso-main-table-chemistry-controls/1','completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputReceipt':{'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()},'errors':[]}
def number(s):return float(s.replace(' ',''))
def seq(s):
 x=re.sub(r"5[′']|3[′']",'',s);x=re.sub(r'[^ACGTacgtE]','',x);return x.replace('E','C').upper()
def table(s,id):return next(t for t in s['tables'] if t['id']==id)
s=src['ASO_HAGEDORN_TOX'];rows=table(s,'tbl1')['rows'];assert len(rows)==20;molecules=[]
for r in rows[1:]:
 assert len(r)==8;molecules.append({'id':r[0],'alias':r[1],'literalSequence':r[2],'baseSequence':seq(r[2]),'chemistry':r[3],'gene':r[4],'accession':r[5],'onTargetSpecies':r[6],'firstToxicDoseLiteral':r[7],'firstToxicDose_mg_kg':number(r[7].lstrip('>')),'rightCensoredAboveReportedDose':r[7].startswith('>')})
assert len(molecules)==19 and len({r['baseSequence'] for r in molecules})==13;assert collections.Counter(r['chemistry'] for r in molecules)=={'LNA':13,'2’ MOE':3,'cEt':3};groups=collections.defaultdict(list)
for r in molecules:groups[r['baseSequence']].append(r)
matched=[]
for sequence,g in groups.items():
 if len(g)>1:
  assert len(g)==3 and {r['chemistry'] for r in g}=={'LNA','2’ MOE','cEt'};matched.append({'baseSequence':sequence,'molecules':g,'reportedFirstToxicDoses_mg_kg':{r['chemistry']:r['firstToxicDose_mg_kg'] for r in g},'interpretation':'Same bases, different chemistry; reported thresholds are dose-grid summaries, not potency-matched therapeutic margins.'})
assert len(matched)==3;alt=[];current=None;alias=None
for r in table(s,'tbl3')['rows'][2:]:
 assert len(r)==10
 if r[0]:current=r[0];alias=r[1]
 assert current;alt.append({'id':current,'alias':alias,'dose_mg_kg':number(r[2]),'reported96hToxicity':r[3],'ALT_IU_ml':dict(zip(['24','48','72','96'],map(number,r[4:8]))),'sourceReportedTranscriptCounts24h':{'down':int(r[8]),'up':int(r[9])},'literalRow':r})
assert len(alt)==25;controls={r['dose_mg_kg']:r for r in alt if r['id']=='569713'};assert set(controls)=={33,300}
for r in alt:
 c=controls.get(r['dose_mg_kg']);r['controlMatchedByDoseAndTime']=bool(c);r['ALT_ratio_to_published_ASO_control_by_hour']={h:r['ALT_IU_ml'][h]/c['ALT_IU_ml'][h] for h in c['ALT_IU_ml']} if c else None
r33=[r for r in alt if r['dose_mg_kg']==33 and r['id'] in ['569717','569721','569719']];assert len(r33)==3
out['Burel2016']={'pmcid':s['pmcid'],'sourceReceipt':s['primarySource'],'molecules':molecules,'nMolecules':len(molecules),'nDistinctBaseSequences':13,'chemistryCounts':dict(collections.Counter(r['chemistry'] for r in molecules)),'nRightCensoredThresholds':sum(r['rightCensoredAboveReportedDose'] for r in molecules),'sameSequenceChemistryGroups':matched,'doseALTrows':alt,'nDoseALTrows':len(alt),'nTreatmentRowsWithDoseMatchedPublishedASOControl':sum(r['controlMatchedByDoseAndTime'] and r['id']!='569713' for r in alt),'three33mg96hExamples':r33,'limits':['Table3 lists only LNA; no dose-matched cross-chemistry ALT comparison.','ALT means lack row-specific uncertainty/animal measurements.','Table1 records first-toxic-dose300 for MOE but prose describes suppression within range; retain both.','No model fitting or clinical safety inference.']}
s=src['ASO_HAGEDORN_PANEL'];rows=table(s,'tbl1')['rows'];assert len(rows)==7;panel=[]
for r in rows[1:]:
 assert len(r)==7;literal=r[1];modified=[i+1 for i,c in enumerate(literal) if c.isupper()];dna=[i+1 for i,c in enumerate(literal) if c.islower()];assert all(c in 'ACGTEacgt' for c in literal);panel.append({'name':r[0],'literalSequence':literal,'baseSequence':seq(literal),'length':len(literal),'LNApositions1Based':modified,'DNApositions1Based':dna,'gapDesign':{'leftWing':dna[0]-1,'DNAgap':len(dna),'rightWing':len(literal)-dna[-1]},'targetRNA':r[2],'targetSpecies':r[3],'ALTfoldReported':number(r[4]),'hepatotoxicLabelReported':r[5],'theoreticalTm_C':number(r[6]),'TmEvidence':'Explicitly theoretically calculated; not measured duplex thermodynamics.','ALTOriginalSource':'Reference6 Hagedorn2013; not new independent mouse cohort.'})
assert len(panel)==6 and len({r['baseSequence'] for r in panel})==6
out['Dieckmann2018']={'pmcid':s['pmcid'],'sourceReceipt':s['primarySource'],'sixMyd88Rows':panel,'nRows':6,'nMeasuredThermalRows':0,'chemistryMapping':'UppercaseLNA, lowercaseDNA, E5-methylcytosine; E mapsC only for bases. FullyPS compounds.','doseContext':'ALT two weeks after5x15mg/kg IV, relative saline.','limits':['Sixcomplete rows are not236 dataset.','TheoreticalTm cannot join measuredduplex denominator.','No sequence/affinity alone toxicity inference.']}
P(a.output).parent.mkdir(parents=True,exist_ok=True);P(a.output).write_text(json.dumps(out,indent=2));print('ASO_CHEMISTRY_CONTROLS_BEGIN');print(json.dumps(out));print('ASO_CHEMISTRY_CONTROLS_END')
