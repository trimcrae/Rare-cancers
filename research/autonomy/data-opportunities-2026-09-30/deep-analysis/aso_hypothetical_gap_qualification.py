#!/usr/bin/env python3
import argparse,collections,datetime,hashlib,json,pathlib,re
P=pathlib.Path
ap=argparse.ArgumentParser();ap.add_argument('--input',default='research/autonomy/data-opportunities-2026-09-30/deep-analysis/outputs/primary-supplements-staged.json');ap.add_argument('--output',default='campaign-output/aso-hypothetical-gap-qualification.json');a=ap.parse_args();p=P(a.input)
if not p.exists():
 xs=list(P('.').rglob('primary-supplements-staged.json'));assert len(xs)==1,[str(x) for x in xs];p=xs[0]
b=p.read_bytes();d=json.loads(b)
while 'result' in d and isinstance(d['result'],dict):d=d['result']
s=next(x for x in d['sources'] if x['id']=='ASO_KAMOLA')
def feature(alignment):
 assert re.fullmatch('[ACGTacgt]{16}',alignment);runs=list(re.finditer('[ACGT]+',alignment));best=max((len(x.group()) for x in runs),default=0);mm=[i+1 for i,c in enumerate(alignment) if c.islower()];gap=all(c.isupper() for c in alignment[5:11]);return {'printedAlignment':alignment,'mismatchPositions':mm,'longestPrintedExactRun':best,'hypotheticalPositions6to11Match':gap,'hypothetical5_6_5Flag':gap and best>=10,'conventionalAtMost2MismatchFlag':len(mm)<=2}
def numkd(x):return float(x[:-1]) if re.fullmatch(r'\d+(?:\.\d+)?%',x) else None
def ecnum(x):return float(x) if re.fullmatch(r'\d+(?:\.\d+)?',x) else None
out={'schema':'aso-hypothetical-gap-and-printed-feature-qualification/2','completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceInput':{'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()},'primarySource':s['primarySource'],'tables':[],'limits':['One publishedASO GSK2910546A;5-6-5positions6to11 hypothetical, not recovered experimentalLNA map.','Lowercase query bases mark mismatches, not actual replacementRNA bases.','Narrow feature qualification, not failure of complete off-targetscreening.','NoActivity sourcecategory, not numericzero; possibleactivity/gapped excluded/disclosed.','Printed-pattern equivalence not identical completeRNAs or causalaccessibility.']}
for tid in ['tbl3','tbl4']:
 t=next(x for x in s['tables'] if x['id']==tid);genes=collections.OrderedDict();excluded=[]
 for literal in t['rows'][1:]:
  if tid=='tbl3':
   region,gene,identity,alignment,kd,ec,ti=literal
   if 'G' in identity or kd=='Possible Activity':excluded.append({'literalRow':literal,'reason':'declaredgap or uncertainactivity'});continue
  else:
   gene,alignment,kd,ec,ti=literal
   if gene=='BACH1':excluded.append({'literalRow':literal,'reason':'on-target'});continue
  if not re.fullmatch('[ACGTacgt]{16}',alignment):excluded.append({'literalRow':literal,'reason':'not recoverable16-baseungappedalignment'});continue
  f=feature(alignment)
  if gene not in genes:genes[gene]={'gene':gene,'maxKnockdownReported':kd,'maxKnockdownPercent':numkd(kd),'EC50Reported':ec,'therapeuticIndexReported':ti,'sites':[],'literalRows':[]}
  r=genes[gene]
  if kd:assert r['maxKnockdownReported'] in ['',kd]
  if ec:assert r['EC50Reported'] in ['',ec]
  if f not in r['sites']:r['sites'].append(f)
  r['literalRows'].append(literal)
 for r in genes.values():r['hypotheticalAnySiteFlag']=any(x['hypothetical5_6_5Flag'] for x in r['sites']);r['conventionalAnySiteFlag']=any(x['conventionalAtMost2MismatchFlag'] for x in r['sites'])
 vals=list(genes.values());assert len(vals)==({'tbl3':17,'tbl4':21}[tid]);assert sum(r['hypotheticalAnySiteFlag'] for r in vals)==({'tbl3':9,'tbl4':16}[tid]);assert all(r['conventionalAnySiteFlag'] for r in vals);groups=collections.defaultdict(list)
 for r in vals:
  for f in r['sites']:groups[f['printedAlignment']].append(r)
 equivalences=[]
 for alignment,g in groups.items():
  if len(g)<2:continue
  kd=[r['maxKnockdownPercent'] for r in g if r['maxKnockdownPercent'] is not None];ec=[ecnum(r['EC50Reported']) for r in g];unc=[x for x in ec if x is not None];equivalences.append({'printedAlignment':alignment,'geneAssays':[{'gene':r['gene'],'maxKnockdownReported':r['maxKnockdownReported'],'EC50Reported':r['EC50Reported']} for r in g],'numericKnockdownRangePP':max(kd)-min(kd) if len(kd)==len(g) else None,'uncensoredEC50FoldRange':max(unc)/min(unc) if len(unc)==len(g) and min(unc)>0 else None})
 out['tables'].append({'table':tid,'nValidGeneComparisons':len(vals),'nHypotheticalAnySiteFlag':sum(r['hypotheticalAnySiteFlag'] for r in vals),'nConventionalAnySiteFlag':sum(r['conventionalAnySiteFlag'] for r in vals),'geneComparisons':vals,'excludedRows':excluded,'fixedKnockdownThresholdQualification':{str(c):{'nNumericAtLeast':sum(r['maxKnockdownPercent'] is not None and r['maxKnockdownPercent']>=c for r in vals),'hypotheticalMissedGenes':[r['gene'] for r in vals if r['maxKnockdownPercent'] is not None and r['maxKnockdownPercent']>=c and not r['hypotheticalAnySiteFlag']]} for c in [20,45,50]},'samePrintedFeatureGroups':equivalences})
P(a.output).parent.mkdir(parents=True,exist_ok=True);P(a.output).write_text(json.dumps(out,indent=2));print('ASO_GAP_QUALIFICATION_BEGIN');print(json.dumps(out));print('ASO_GAP_QUALIFICATION_END')
