#!/usr/bin/env python3
import argparse,collections,csv,datetime,hashlib,io,json,math,pathlib,re,statistics
P=pathlib.Path
ap=argparse.ArgumentParser();ap.add_argument('--input',default='campaign-output/aso-empirical-matched-benchmark.json');ap.add_argument('--out',default='campaign-output/aso-toehold-endpoint.json');a=ap.parse_args();p=P(a.input)
if not p.exists():
 choices=list(P('.').rglob('ASO-matched-duplexes-and-source-data-actual.json'));assert len(choices)==1,[str(x) for x in choices];p=choices[0]
raw=p.read_bytes();doc=json.loads(raw)
while 'result' in doc and isinstance(doc['result'],dict):doc=doc['result']
wb=doc['sourceDataWorkbook'];assert wb['sha256']=='a50312a03357bb3ee9bf31713295dd3ecd1cc30afb0055ce06731d64b82108cc';sheet=next(x for x in wb['sheets'] if x['name']=='Figure 6f');assert sheet['csvSha256']=='801a8fa506ddea994961392a7a30b61373b9275c05c21f2ee6690b2a62c0f2af';cells={}
for row in sheet['rows']:cells.update(row['cells'])
assert cells['A1']=='Relative gene mRNA levels';genes=['apoB','Copg','Mast2','Hltf'];arms=['NT','ssASO','BROC8','BROC9'];labels=['NT','hApo1n','hApo1n/PNA(C8)','hApo1/PNA(C9)'];rows=[]
for i,gene in enumerate(genes):
 assert cells[chr(65+4*i)+'2']==gene
 for k,arm in enumerate(arms):
  col=chr(65+4*i+k);assert cells[col+'3']==labels[k];values=[float(cells[col+str(r)]) for r in [4,5,6]];assert all(math.isfinite(x) for x in values);mean=statistics.mean(values);rows.append({'gene':gene,'arm':arm,'sourceHeader':labels[k],'column':col,'sourceRows':[4,5,6],'nBiologicalReplicates':3,'values':values,'meanResidualRNA':mean,'sampleSDResidualRNA':statistics.stdev(values),'meanReductionPercent':100*(1-mean)})
 assert abs(next(r['meanResidualRNA'] for r in rows if r['gene']==gene and r['arm']=='NT')-1)<1e-10
contrasts=[]
for gene in genes:
 by={r['arm']:r for r in rows if r['gene']==gene}
 for arm in ['BROC8','BROC9']:contrasts.append({'gene':gene,'arm':arm,'meanResidualRNADifferenceVersusSsASO':by[arm]['meanResidualRNA']-by['ssASO']['meanResidualRNA'],'sourceCellPairsDefined':False})
def global_expression():
 def read(name,expected,n):
  s=next(x for x in wb['sheets'] if x['name']==name);assert s['csvSha256']==expected;path=P(s['savedAllCellsCSV'])
  if not path.exists():
   candidates=list(P('.').rglob(path.name));assert len(candidates)==1,[str(x) for x in candidates];path=candidates[0]
  b=path.read_bytes();assert hashlib.sha256(b).hexdigest()==expected;byrow=collections.defaultdict(dict)
  for c in csv.DictReader(io.StringIO(b.decode())):col=re.sub(r'\d+$','',c['cell']);byrow[int(c['row'])][col]=c['value']
  assert byrow[1]['B']=='ExpMean' and byrow[1]['C']=='log2FC';out=[];bad=[]
  for i,r in sorted(byrow.items()):
   if i==1:continue
   try:e=float(r['B']);f=float(r['C']);assert math.isfinite(e) and math.isfinite(f);out.append({'row':i,'gene':r['A'],'ExpMean':e,'log2FC':f})
   except Exception as ex:bad.append({'row':i,'cells':r,'error':str(ex)})
  assert len(out)==n and not bad,(name,len(out),n,bad[:5]);groups=collections.defaultdict(list)
  for r in out:groups[r['gene']].append(r)
  dup={g:rs for g,rs in groups.items() if len(rs)>1};unique={g:rs[0] for g,rs in groups.items() if len(rs)==1};return unique,{'sheet':name,'path':str(path),'sha256':expected,'nRows':len(out),'nUniqueSingleRowSymbols':len(unique),'duplicateSymbols':dup,'parseErrors':bad}
 ss,sr=read('Figure 3b','560255018f48b1d4f7cadc4e096951bf957b229790cab2470923ddebbc432b4f',18065);bro,br=read('Figure 3c','148528c74cc1bc803ab230e87af8071300b49cc83220df88ff80c20b1b11d971',17630);common=sorted(set(ss)&set(bro));joined=[]
 for g in common:joined.append({'gene':g,'ssExpMean':ss[g]['ExpMean'],'ssLog2FC':ss[g]['log2FC'],'broExpMean':bro[g]['ExpMean'],'broLog2FC':bro[g]['log2FC']})
 path=P('campaign-output/aso-global-expression-joined.csv');path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=['gene','ssExpMean','ssLog2FC','broExpMean','broLog2FC']);w.writeheader();w.writerows(joined)
 b=path.read_bytes();out={'sourceSheets':[sr,br],'nExactSymbolIntersection':len(common),'nSsOnly':len(set(ss)-set(bro)),'nBroOnly':len(set(bro)-set(ss)),'ssOnlySymbols':sorted(set(ss)-set(bro)),'broOnlySymbols':sorted(set(bro)-set(ss)),'savedAllJoinedRows':{'path':str(path),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()},'fixedExpressionFloorSensitivity':[],'literalGeneRows':{g:{'ssASO':ss.get(g),'BRO':bro.get(g)} for g in ['Pcsk9','Nr4a3','Nr4a2','Cdkn1a','Mlkl','Slpi','Saa1','Saa2']},'limits':['Released gene-level ExpMean/log2FC summaries only; adjustedPvalues and individual RNAseq counts absent.','Exact gene-symbol joins; duplicates excluded/disclosed, missing arm not zero-filled.','mPCS1 ssASO and mPCS1/PNA(C8) BRO mouse-liver observations72h after100nmol/kg; no EMC model.','Fold-change threshold counts descriptive, not differentially-expressed-gene calls.','RNA changes may be downstream stress and do not establish direct cleavage.','Floors0/1/5/10/50 fixed before replay; not fitted to significance.']}
 for floor in [0,1,5,10,50]:
  sub=[r for r in joined if r['ssExpMean']>=floor and r['broExpMean']>=floor]
  if not sub:out['fixedExpressionFloorSensitivity'].append({'floor':floor,'n':0});continue
  s=[abs(r['ssLog2FC']) for r in sub];b=[abs(r['broLog2FC']) for r in sub];out['fixedExpressionFloorSensitivity'].append({'floor':floor,'n':len(sub),'medianAbsLog2FC_ss':statistics.median(s),'medianAbsLog2FC_BRO':statistics.median(b),'medianWithinGeneAbsDifference_BROminusSs':statistics.median(y-x for x,y in zip(s,b)),'nAbsAttenuated':sum(y<x for x,y in zip(s,b)),'nAbsIncreased':sum(y>x for x,y in zip(s,b)),'nAbsEqual':sum(y==x for x,y in zip(s,b)),'nOppositeSigns':sum(r['ssLog2FC']*r['broLog2FC']<0 for r in sub),'fixedFoldChangeCounts':{str(t):{'ss':sum(x>=t for x in s),'BRO':sum(x>=t for x in b),'both':sum(x>=t and y>=t for x,y in zip(s,b))} for t in [1,2]}})
 return out
out={'schema':'aso-toehold-source-endpoint/2','completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputPath':str(p),'inputSha256':hashlib.sha256(raw).hexdigest(),'primaryDOI':'10.1038/s41467-023-43714-0','primaryPMCID':'PMC10693639','workbookMember':wb['member'],'workbookSha256':wb['sha256'],'sheet':'Figure 6f','sheetCsvSha256':sheet['csvSha256'],'assay':'Huh-7,CEM,1micromolar,24hours,3biologicalsamples per source caption','rows':rows,'descriptiveArmContrasts':contrasts,'thermodynamicQualification':doc['toehold'],'globalExpressionAudit':global_expression(),'limits':['Already normalized residualRNA; no rawCt reconstruction.','C9 literal header omits n; primaryFigure6f identifies hApo1n/PNA(C9).','Source rows do not establish paired treatment replicate identities.','Abovecontrol values and negative reductions retained.','Descriptive only; no new safetywindow or EMC efficacy.','Authors established PNA intervention and off-target suppression; modelqualification/sourceanalysis.']};P(a.out).parent.mkdir(parents=True,exist_ok=True);P(a.out).write_text(json.dumps(out,indent=2));print('ASO_TOEHOLD_ENDPOINT_BEGIN');print(json.dumps(out));print('ASO_TOEHOLD_ENDPOINT_END')
