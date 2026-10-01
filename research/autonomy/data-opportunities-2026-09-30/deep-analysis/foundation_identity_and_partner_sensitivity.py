import ast,hashlib,io,json,math,zipfile
from collections import Counter,defaultdict
from pathlib import Path
P=Path('research/autonomy/data-opportunities-2026-09-30/deep-analysis/foundation_legacy_workbook_analysis.py');nodes=[]
for z in ast.parse(P.read_bytes()).body:
 if isinstance(z,(ast.Import,ast.ImportFrom)):nodes.append(z)
 elif isinstance(z,ast.FunctionDef) and z.name in ('get','load_sheets','canon','lfs'):nodes.append(z)
 elif isinstance(z,ast.Assign) and all(isinstance(t,ast.Name) and t.id=='CAP' for t in z.targets):nodes.append(z)
g={'__name__':'helpers_only','R':{'sources':[]}};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(P),'exec'),g)
O=Path('campaign-output/foundation-identity-partner');O.mkdir(parents=True,exist_ok=True);R=dict(schema='foundation-identity-partner-sensitivity/1',sources=[],errors=[],limits=['Reported calls only: unreported is not individually tested negative','Source EMC diagnosis partly genomically assigned; no independent classification validation','No matched normal: reported known/likely-pathogenic calls may be germline','Fraction-read sensitivity is descriptive, not validated clonality/validity filtering','No clinical outcome/efficacy or patient-specific panel manifest'])
def sid(x):
 if isinstance(x,float):assert x.is_integer();return str(int(x))
 return str(x).strip()
def fisher(a,b,c,d):
 n=a+b;K=a+c;N=n+c+d
 def p(x):return math.comb(K,x)*math.comb(N-K,n-x)/math.comb(N,n)
 v=p(a);return min(1,sum(p(x) for x in range(max(0,n-(N-K)),min(n,K)+1) if p(x)<=v*(1+1e-12)))
def num(x):
 try:v=float(x);return v if math.isfinite(v) else None
 except (ValueError,TypeError):return None
def records(n,r):return [dict(zip([str(h).strip() for h in r[0]],v),sourceExcelRow=i+2,sourceSheet=n) for i,v in enumerate(r[1:])]
def unwrap(x):
 if isinstance(x,str):
  try:return unwrap(json.loads(x))
  except (ValueError,TypeError):return None
 if isinstance(x,dict):
  if x.get('schema')=='emc-foundation-public-reanalysis/1':return x
  for v in x.values():
   z=unwrap(v)
   if z is not None:return z
 if isinstance(x,list):
  for v in x:
   z=unwrap(v)
   if z is not None:return z
 return None
try:
 files=[Path('campaign-output/foundation-emc-primary/primary.xls'),Path('campaign-output/foundation-original/41467_2022_30496_MOESM2_ESM.xls')];b=next((p.read_bytes() for p in files if p.exists()),None)
 if b is None:
  u='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9200814/supplementaryFiles';a=g['get'](u);R['sources'].append(dict(url=u,bytes=len(a),sha256=hashlib.sha256(a).hexdigest()));z=zipfile.ZipFile(io.BytesIO(a));b=z.read(next(x for x in z.namelist() if Path(x).name=='41467_2022_30496_MOESM2_ESM.xls'))
 assert len(b)==4812800 and hashlib.sha256(b).hexdigest()=='88c1a0bab7509ffe3bcff955b89f3d60ddb58a68311cd4c56ca4b0c78506b475';R['workbookSHA256']=hashlib.sha256(b).hexdigest();sh=dict((n,r) for n,r,_ in g['load_sheets'](b));vs=records('variants_table_final_for_supple',sh['variants_table_final_for_supple']);ps=records('samples_table_final_for_supplem',sh['samples_table_final_for_supplem']);sm={sid(x['de-identified ID']):x for x in ps};assert len(sm)==7494
 re=[x for x in vs if x['alteration_type']=='RE'];ex=g['lfs']('d9fc3fc8073104c3f364825972921f271b5e8793eefcf71331c3cff7d3882701',180393);R['sources']+=g['R']['sources'];m=dict(sourceRows=len(re),exportRows=len(ex),exactOrderedGenePairMatches=0,unorderedOnlyMatches=0,ordinalIDMatches=0,mismatches=[],mapping=[]);R['REmapping']=m
 def norm(x):return '' if str(x).strip().upper() in ('','NA','N/A','NAN') else str(x).strip()
 for j in range(max(len(re),len(ex))):
  v=re[j] if j<len(re) else None;e=ex[j] if j<len(ex) else None
  if v is None or e is None:m['mismatches'].append(dict(ordinal=j+1,source=v,export=e));continue
  a=(norm(v['gene']),norm(v['partner_gene']));c=(norm(e.get('Site1_Hugo_Symbol')),norm(e.get('Site2_Hugo_Symbol')));eid=str(e.get('Sample_Id',''));s=eid.rsplit('-',1)[-1];exact=a==c;ordinal=s.isdigit() and int(s)==j+1;m['exactOrderedGenePairMatches']+=exact;m['unorderedOnlyMatches']+=sorted(a)==sorted(c) and not exact;q=dict(REordinal=j+1,sourceID=sid(v['de-identified ID']),sourceExcelRow=v['sourceExcelRow'],exportSampleID=eid,sourceGenePair=a,exportGenePair=c,orderedMatch=exact,ordinalIDMatch=ordinal);m['mapping'].append(q)
  if not(exact and ordinal):m['mismatches'].append(q)
 m['allRowsExactlyPreserveSourceREOrderWithOrdinalExportID']=len(re)==len(ex)==3771 and m['exactOrderedGenePairMatches']==3771 and m['ordinalIDMatches']==3771
 emc={k:v for k,v in sm.items() if str(v['final_diagnosis']).casefold()=='extraskeletal myxoid chondrosarcoma'};assert len(emc)==75;by=defaultdict(list)
 for v in vs:by[sid(v['de-identified ID'])].append(v)
 R['perEMC']=[];genes=defaultdict(list)
 for k in sorted(emc,key=int):
  calls=by[k];p={str(v['partner_gene'] if v['gene']=='NR4A3' else v['gene']) for v in calls if v['alteration_type']=='RE' and 'NR4A3' in(v['gene'],v['partner_gene'])};partner=sorted(p&{'EWSR1','TAF15'});assert len(partner)==1;sv=[v for v in calls if v['alteration_type']=='SV'];cn=[v for v in calls if v['alteration_type']=='CN'];low=[v for v in sv if num(v['fraction_reads']) is not None and num(v['fraction_reads'])<.05];hi=[v for v in sv if num(v['fraction_reads']) is not None and num(v['fraction_reads'])>=.05];R['perEMC'].append(dict(sourceID=k,partner=partner[0],clinicalLiteral=emc[k],reportedNonfusionRows=len(sv)+len(cn),shortVariantRows=len(sv),CNRows=len(cn),fractionReadBelowPoint05=len(low),fractionReadAtLeastPoint05=len(hi),fractionReadUnknown=sum(num(v['fraction_reads']) is None for v in sv),lowFractionReadLiteralRows=low))
  for v in calls:genes[(str(v['gene']),str(v['alteration_type']))].append(v)
 R['geneTypeCalls']=[dict(gene=k[0],alterationType=k[1],rows=len(a),uniqueSourceIDs=sorted({sid(x['de-identified ID']) for x in a},key=int),literalRows=a) for k,a in sorted(genes.items())];R['partnerSummary']={}
 for p in ('EWSR1','TAF15'):
  q=[x for x in R['perEMC'] if x['partner']==p];R['partnerSummary'][p]=dict(sourceIDs=len(q),nonfusionReportedSpecimens=sum(x['reportedNonfusionRows']>0 for x in q),nonfusionReportedRows=sum(x['reportedNonfusionRows'] for x in q),lowFractionReadRows=sum(x['fractionReadBelowPoint05'] for x in q),CNReportedSpecimens=sum(x['CNRows']>0 for x in q),shortVariantReportedSpecimens=sum(x['shortVariantRows']>0 for x in q),shortVariantAtLeastPoint05Specimens=sum(x['fractionReadAtLeastPoint05']>0 for x in q))
 q=[]
 for f in ('reportedNonfusionRows','shortVariantRows','CNRows','fractionReadAtLeastPoint05'):
  a=sum(x[f]>0 for x in R['perEMC'] if x['partner']=='TAF15');c=sum(x[f]>0 for x in R['perEMC'] if x['partner']=='EWSR1');q.append(dict(reportedField=f,TAF15=dict(reported=a,totalSourceIDs=12),EWSR1=dict(reported=c,totalSourceIDs=63),FisherTwoSided=fisher(a,12-a,c,63-c)))
 order=sorted(range(len(q)),key=lambda i:q[i]['FisherTwoSided']);last=1.
 for rank in range(len(order),0,-1):i=order[rank-1];last=min(last,q[i]['FisherTwoSided']*len(order)/rank);q[i]['BHq']=last
 R['exploratoryFourContrastFamily']=q;R['sourceAssayLimitation']='Primary publication explicitly states MTAP is not covered; incidental partner rearrangements do not establish MTAP CN callability.'
 cp=Path('research/autonomy/data-opportunities-2026-09-30/deep-analysis/results/clinical-foundation-actual.json');cb=cp.read_bytes();cq=unwrap(json.loads(cb));assert cq is not None;a=Counter((k,'MRE11A' if v['gene']=='MRE11' else v['gene']) for k in emc for v in by[k] if v['alteration_type']=='SV');e=Counter((v['Tumor_Sample_Barcode'].rsplit('-',1)[-1],v['Hugo_Symbol']) for v in cq['emcMutationRowsLiteral']);assert a==e and sum(a.values())==43;R['shortVariantIdentityControl']=dict(inputArtifact=str(cp),inputSHA256=hashlib.sha256(cb).hexdigest(),primaryRows=sum(a.values()),exportRows=sum(e.values()),allSourceIDGeneMultiplicitiesMatch=True,explicitAlias={'MRE11':'MRE11A'},scope='Source-ID and gene multiplicity only; not full allele/coordinate normalization validation',exportSomaticLabels=sum(v['Mutation_Status']=='Somatic' for v in cq['emcMutationRowsLiteral']),sourceOriginCaveat='Primary source is agnostic to germline/somatic origin and lacks matchednormal')
except Exception as e:R['errors'].append(dict(type=type(e).__name__,message=str(e)))
(O/'identity-and-partner-sensitivity.json').write_text(json.dumps(R,indent=2)+'\n');print(json.dumps(R,separators=(',',':')))
if R['errors']:raise SystemExit(1)
