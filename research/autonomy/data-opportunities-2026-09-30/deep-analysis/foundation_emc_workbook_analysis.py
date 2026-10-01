import ast,hashlib,io,json,math,zipfile
from collections import Counter,defaultdict
from pathlib import Path
P=Path('research/autonomy/data-opportunities-2026-09-30/deep-analysis/foundation_legacy_workbook_analysis.py');rawcode=P.read_bytes();tree=ast.parse(rawcode);nodes=[]
for z in tree.body:
 if isinstance(z,(ast.Import,ast.ImportFrom)):nodes.append(z)
 elif isinstance(z,ast.FunctionDef) and z.name in ('get','load_sheets','canon'):nodes.append(z)
 elif isinstance(z,ast.Assign) and all(isinstance(t,ast.Name) and t.id=='CAP' for t in z.targets):nodes.append(z)
g={'__name__':'frozen_primary_workbook_helpers_only'};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(P),'exec'),g);OUT=Path('campaign-output/foundation-emc-primary');OUT.mkdir(parents=True,exist_ok=True)
R=dict(schema='foundation-emc-primary-workbook-analysis/1',helperSHA256=hashlib.sha256(rawcode).hexdigest(),sources=[],errors=[],limits=['Primary final diagnosis partly assigned using genomic events: fusion/diagnosis concordance is not independent validation','De-identified source IDs, not export row-ordinal IDs','Observed reported calls, not individually callable negative prevalences','No patient-specific gene panel/modality manifest in workbook','CN0 indicates a reported zero-copy call, not absence inferred from missing row','Original alteration_type SV is short variant; RE is rearrangement','No functional drug sensitivity or clinical benefit inferred','No survival/treatment endpoints in primary workbook'])
TARGET=['RET','ALK','CDKN2A','CDKN2B','MTAP','ATRX','TP53','RB1','PTEN','PIK3CA'];ALLTARGET=['NR4A3','EWSR1','TAF15']+TARGET
def ident(v):
 if isinstance(v,float):assert v.is_integer();return str(int(v))
 return str(v).strip()
def num(v):
 try:x=float(v);return x if math.isfinite(x) else None
 except (ValueError,TypeError):return None
def stats(v):
 q=sorted(z for z in v if z is not None);n=len(q);return dict(n=n,minimum=q[0] if n else None,median=(q[(n-1)//2]+q[n//2])/2 if n else None,maximum=q[-1] if n else None)
def exact_p(a,b,c,d):
 N=a+b+c+d;K=a+c;n=a+b
 def prob(k):return math.comb(K,k)*math.comb(N-K,n-k)/math.comb(N,n)
 p=prob(a);return min(1.,sum(prob(k) for k in range(max(0,n-(N-K)),min(n,K)+1) if prob(k)<=p*(1+1e-12)))
try:
 u='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9200814/supplementaryFiles';b=g['get'](u);R['sources'].append(dict(url=u,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),scope='Observed container hash; may differ across requests'));z=zipfile.ZipFile(io.BytesIO(b));member=next(n for n in z.namelist() if Path(n).name=='41467_2022_30496_MOESM2_ESM.xls');b=z.read(member);assert len(b)==4812800 and hashlib.sha256(b).hexdigest()=='88c1a0bab7509ffe3bcff955b89f3d60ddb58a68311cd4c56ca4b0c78506b475';f=OUT/'primary.xls';f.write_bytes(b);R['workbookReceipt']=dict(path=str(f),bytes=len(b),sha256=hashlib.sha256(b).hexdigest());sheets={name:rows for name,rows,reader in g['load_sheets'](b)}
 def records(name):
  rows=sheets[name];headers=[str(v).strip() for v in rows[0]];assert len(headers)==len(set(headers));return [dict(zip(headers,list(v)+['']*(len(headers)-len(v))),sourceExcelRow=i+2,sourceSheet=name) for i,v in enumerate(rows[1:])]
 ss=records('samples_table_final_for_supplem');vs=records('variants_table_final_for_supple');sm={ident(v['de-identified ID']):v for v in ss};assert len(ss)==len(sm)==7494
 by=defaultdict(list)
 for v in vs:by[ident(v['de-identified ID'])].append(v)
 emc={k:v for k,v in sm.items() if str(v['final_diagnosis']).strip().casefold()=='extraskeletal myxoid chondrosarcoma'};assert len(emc)==75
 R['sourceDimensions']=dict(clinicalRows=len(ss),variantRows=len(vs),distinctVariantIdentifiers=len(by),variantIDsAbsentFromClinical=sorted(set(by)-set(sm)),alterationTypeCounts=dict(Counter(str(v['alteration_type']) for v in vs)));R['emcPatients']=[];groups={};nr_other=[]
 for k,p in sorted(emc.items(),key=lambda z:int(z[0])):
  calls=by[k];nr=[v for v in calls if v['alteration_type']=='RE' and 'NR4A3' in (v['gene'],v['partner_gene'])];partners=sorted({str(v['partner_gene'] if v['gene']=='NR4A3' else v['gene']) for v in nr});canonical=[z for z in partners if z in ('EWSR1','TAF15')];group=canonical[0] if len(canonical)==1 else 'requires-partner-adjudication';groups[k]=group;R['emcPatients'].append(dict(sourceId=k,clinicalLiteral=p,NR4A3RearrangementRows=nr,partnerLiterals=partners,canonicalPartner=group,allReportedAlterationRows=calls))
 for v in vs:
  if v['alteration_type']=='RE' and 'NR4A3' in (v['gene'],v['partner_gene']) and ident(v['de-identified ID']) not in emc:nr_other.append(dict(variantLiteral=v,clinicalLiteral=sm.get(ident(v['de-identified ID']))))
 R['NR4A3RowsOutsideEMC']=nr_other;R['canonicalPartnerCounts']=dict(Counter(groups.values()));R['EMCwithNoNR4A3Rows']=[v['sourceId'] for v in R['emcPatients'] if not v['NR4A3RearrangementRows']];R['clinicalDescriptive']=dict(initialDiagnosisCounts=dict(Counter(str(p['initial_diagnosis']) for p in emc.values())),tissueCounts=dict(Counter(str(p['tissue']) for p in emc.values())),genderCounts=dict(Counter(str(p['gender']) for p in emc.values())),ageYears=stats([num(p['age [0-89]']) for p in emc.values()]),msiStatusLiteralCounts=dict(Counter(str(p['msi_status']) for p in emc.values())),primaryMutationLoadPerMb=stats([num(p['mutation_load_per_mb']) for p in emc.values()]),knownPrimaryMutationLoadAtLeast10=sum(num(p['mutation_load_per_mb']) is not None and num(p['mutation_load_per_mb'])>=10 for p in emc.values()),mutationLoadScope='Primary assay definition, not cBio nonsynonymous export. Missing status excluded; no immunotherapy prediction.');R['targetCalls']=[];R['exploratoryPartnerContrasts']=[]
 for gene in ALLTARGET:
  globalrows=[v for v in vs if gene in (v['gene'],v['partner_gene'])];erows=[v for k in emc for v in by[k] if gene in (v['gene'],v['partner_gene'])];cn=[v for v in erows if v['alteration_type']=='CN' and v['gene']==gene];zero=[v for v in cn if num(v['copy_number'])==0];sv=[v for v in erows if v['alteration_type']=='SV' and v['gene']==gene];R['targetCalls'].append(dict(gene=gene,allStudyLiteralTypeCounts=dict(Counter(str(v['alteration_type']) for v in globalrows)),EMCReportedRows=erows,EMCReportedUniqueSourceIDs=len({ident(v['de-identified ID']) for v in erows}),EMCCNRows=cn,EMCCNcopyNumberLiteralCounts=dict(Counter(str(v['copy_number']) for v in cn)),EMCCNzeroCopySourceIDs=sorted({ident(v['de-identified ID']) for v in zero}),EMCShortVariantSourceIDs=sorted({ident(v['de-identified ID']) for v in sv}),negativeCallability='Not established from absence of reported row'))
  if gene not in TARGET:continue
  for kind,chosen,globaltype in [('reported-any-alteration',erows,globalrows),('reported-short-variant',sv,[v for v in globalrows if v['alteration_type']=='SV' and v['gene']==gene]),('reported-CN0',zero,[v for v in globalrows if v['alteration_type']=='CN' and v['gene']==gene])]:
   if not globaltype:continue
   ids={ident(v['de-identified ID']) for v in chosen};a=sum(k in ids for k in emc if groups[k]=='TAF15');c=sum(k in ids for k in emc if groups[k]=='EWSR1');nT=sum(v=='TAF15' for v in groups.values());nE=sum(v=='EWSR1' for v in groups.values());R['exploratoryPartnerContrasts'].append(dict(gene=gene,reportedEvent=kind,TAF15=dict(reported=a,sourceIDs=nT),EWSR1=dict(reported=c,sourceIDs=nE),fisherTwoSided=exact_p(a,nT-a,c,nE-c),scope='Unreported does not mean individually tested negative; descriptive exploratory reported-call contrast, modality/panel confounding unresolved'))
 q=R['exploratoryPartnerContrasts'];order=sorted(range(len(q)),key=lambda i:q[i]['fisherTwoSided']);last=1.
 for rank in range(len(order),0,-1):i=order[rank-1];last=min(last,q[i]['fisherTwoSided']*len(q)/rank);q[i]['BHq']=last
 for name,rows in [('clinical',ss),('all-variants',vs)]:(OUT/(name+'.json')).write_text(json.dumps(rows,separators=(',',':'))+'\n')
except Exception as e:R['errors'].append(dict(type=type(e).__name__,message=str(e)))
Path('campaign-output/foundation-emc-primary-workbook-analysis.json').write_text(json.dumps(R,indent=2)+'\n');print('EMC_FOUNDATION_PRIMARY_RESULT_BEGIN');print(json.dumps(R,separators=(',',':')));print('EMC_FOUNDATION_PRIMARY_RESULT_END')
if R['errors']:raise SystemExit(1)
