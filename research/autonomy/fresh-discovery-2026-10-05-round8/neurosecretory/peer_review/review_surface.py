"""Independent original-source surface-panel arithmetic/coverage challenge, no downloads/edits."""
from pathlib import Path
import csv,gzip,hashlib,io,json,statistics,zipfile,datetime,xml.etree.ElementTree as ET
from scipy.stats import mannwhitneyu
ROOT=Path(__file__).resolve().parent
PACK=Path('/workspace/emc-r6-diagnostic/research/autonomy/fresh-discovery-2026-10-05-round8/surface_targets')
SHARED=Path('/workspace/Rare-cancers')
GENES=['DLL3','SEZ6','NCAM1']
HIST=['Myxoid liposarcoma','Low-grade fibromyxoid sarcoma','Synovial sarcoma']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def A(x,y):return sum((a>b)+.5*(a==b) for a in x for b in y)/(len(x)*len(y)) if x and y else None
def close(a,b):assert abs(a-b)<1e-12,(a,b)
def main():
 freeze=PACK/'FREEZE.json';assert sha(freeze)=='5315fde004ab1c306209c96e871ee106efe31308d1ca036b2aafae737c2830d3';fr=json.loads(freeze.read_text())
 for n,h in fr['files'].items():assert sha(PACK/n)==(h.get('sha256') if isinstance(h,dict) else h),n
 results=json.loads((PACK/'RESULTS.json').read_text());locks=json.loads((PACK/'SOURCE-HASHES.json').read_text());bound={}
 for r in locks['sources']:
  p=SHARED/r['path'];assert sha(p)==r['sha256'];bound[r['path']]=r['sha256']
 meta=json.loads((SHARED/'research/autonomy/atlas-hofvander-validation-2026-09-06/metadata-manifest.json').read_text())['samples'];byid={r['sample_id']:r for r in meta};vals={}
 with gzip.open(SHARED/'research/autonomy/atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz','rt') as f:
  rows=csv.reader(f,delimiter='\t');hdr=next(rows)[1:];assert set(hdr)==set(byid) and len(hdr)==704
  for row in rows:
   if row[0] in GENES:assert row[0] not in vals;vals[row[0]]=dict(zip(hdr,map(float,row[1:])))
 emcs=[r for r in meta if r['diagnosis']=='Extraskeletal myxoid chondrosarcoma'];primary=[r for r in emcs if r['eligible']];assert len(emcs)==13 and len(primary)==9
 known=[r['sample_id'] for r in emcs if r['known_overlap']];assert set(known)=={'104-92','168-97','536-00'}
 iut={};checked=[]
 for g in GENES:
  obs=results['RNA'][g];x=[vals[g][r['sample_id']] for r in primary]
  assert obs['primary_emc_values']=={r['sample_id']:vals[g][r['sample_id']] for r in primary};close(statistics.median(x),obs['primary_median']);assert obs['primary_range']==[min(x),max(x)]
  assert obs['n_ge1']==sum(v>=1 for v in x) and obs['n_ge5']==sum(v>=5 for v in x);ps=[]
  for hist in HIST:
   cc=[r for r in meta if r['eligible'] and r['diagnosis']==hist];y=[vals[g][r['sample_id']] for r in cc];v=obs['primary_contrasts'][hist]
   close(A(x,y),v['A']);close(statistics.median(y),v['median_comparator']);assert len(y)==v['n_comparator']
   w=0;tot=0
   for yr in sorted(set(r['sequencing_year'] for r in primary)):
    xx=[vals[g][r['sample_id']] for r in primary if r['sequencing_year']==yr];yy=[vals[g][r['sample_id']] for r in cc if r['sequencing_year']==yr]
    if xx and yy:w+=A(xx,yy)*len(xx)*len(yy);tot+=len(xx)*len(yy)
   close(w/tot,v['year_matched_A']);close(A([vals[g][r['sample_id']] for r in emcs],y),v['all13_emc']['A'])
   assert len(v['emc_deletion_A'])==9
   for i,d in enumerate(v['emc_deletion_A']):close(A(x[:i]+x[i+1:],y),d)
   tie=len(set(x+y))!=len(x+y);p=float(mannwhitneyu(x,y,alternative='greater',method='asymptotic' if tie else 'exact').pvalue);close(p,v['exploratory_one_sided_p']);ps.append(p)
  iut[g]=max(ps);close(iut[g],obs['IUT_p']);checked.append(g)
 holm={};prev=0
 for i,g in enumerate(sorted(GENES,key=lambda g:iut[g])):prev=max(prev,min(1,iut[g]*(3-i)));holm[g]=prev;close(prev,results['RNA'][g]['Holm3_exploratory_IUT_p'])
 zp=SHARED/'research/autonomy/atlas-original-array-source-2026-09-06/original-source-recovery.zip';maps={g:[] for g in GENES}
 with zipfile.ZipFile(zp) as z:
  roster=json.loads(z.read('sample-rosters.json'));ar=[r for r in roster if r['gse']=='GSE24369'];old=[r for r in roster if r['gse']=='GSE4303'];assert len(ar)==42 and len(old)==16
  with io.TextIOWrapper(z.open('GPL6244-original-annotation.tsv')) as f:
   for r in csv.DictReader(f,delimiter='\t'):
    syms=set(x.split(' // ')[1].strip() for x in r['gene_assignment'].split(' /// ') if len(x.split(' // '))>1)
    for g in syms&set(GENES):
     if syms=={g}:maps[g].append(r['ID'])
 rev={p:g for g,probes in maps.items() for p in probes};data={};sid=None;table=False;head=False
 with gzip.open(SHARED/'research/autonomy/atlas-primary-provenance-2026-09-06/GSE24369.soft.gz','rt') as f:
  for l in f:
   l=l.rstrip('\r\n')
   if l.startswith('^SAMPLE = '):sid=l.split(' = ')[1];data[sid]={}
   elif l=='!sample_table_begin':table=True;head=True
   elif l=='!sample_table_end':table=False
   elif table:
    if head:head=False;continue
    b=l.split('\t')
    if b[0] in rev:data[sid][b[0]]=float(b[1])
 arrchecks={}
 for g in GENES:
  assert maps[g]==results['array'][g]['features'];vv={r['gsm']:statistics.median(data[r['gsm']][p] for p in maps[g]) for r in ar};ee=[r for r in ar if 'extraskeletal' in r['title'].lower()];assert len(ee)==6
  for hist,needle in [('Low-grade fibromyxoid sarcoma','low-grade'),('Myxofibrosarcoma','myxofibro'),('Desmoid','desmoid'),('Solitary fibrous tumor','solitary')]:
   cc=[r for r in ar if needle in r['title'].lower()];v=results['array'][g]['contrasts'][hist];close(A([vv[r['gsm']] for r in ee],[vv[r['gsm']] for r in cc]),v['A']);assert len(cc)==v['n_comparator']
  arrchecks[g]={'LGFMS_A':results['array'][g]['contrasts']['Low-grade fibromyxoid sarcoma']['A'],'features':maps[g]}
 measurements=list(csv.DictReader((PACK/'MEASUREMENTS.tsv').open(),delimiter='\t'));assert len(measurements)==2302
 assert sum(r['assay']=='Hofvander_TPM' and r['diagnosis']=='Extraskeletal myxoid chondrosarcoma' for r in measurements)==39
 assert sum(r['assay']=='GSE24369_RMA_log2' for r in measurements)==126
 oldEMC=[r for r in measurements if r['assay']=='GSE4303_log2_tumor_reference' and 'chondrosarcoma' in r['diagnosis'].lower()];assert len(oldEMC)==40
 assert sum(r['value']=='' for r in oldEMC if r['gene']=='DLL3')==5;assert sum(r['value']=='' for r in oldEMC if r['gene']=='SEZ6')==4
 # Check every retained model source and exact current official mapping locally.
 mc=json.loads((PACK/'MODEL-CONTEXT.json').read_text())
 for r in mc['sources']:
  p=Path(r['path']);p=p if p.is_absolute() else Path('/workspace/emc-r6-diagnostic')/p
  assert sha(p)==r['sha256'];bound[str(p)]=r['sha256']
 with gzip.open(PACK/'source-cache/USZ23-RefSeq.quant.sf.gz','rt') as f:q=list(csv.DictReader(f,delimiter='\t'))
 for g in GENES:
  xml=ET.parse(PACK/f'source-cache/{g}-gene.xml').getroot();acc=sorted(set(x.text for x in xml.iter('Gene-commentary_accession') if x.text and x.text.startswith(('NM_','NR_','XM_','XR_'))));assert acc==mc['panel'][g]['USZ23_current_accessions'];rr=[r for r in q if r['Name'].split('.')[0] in acc];assert rr==mc['panel'][g]['USZ23_current_identifier_rows'];close(sum(float(r['TPM']) for r in rr),mc['panel'][g]['USZ23_current_mapped_sum_TPM'])
 # Additive coverage check prospectively specified in peer PLAN: all4 existing3SEQ EMC, fixed3genes.
 src=ROOT.parent/'raw-cache/GSE28866_normalized.txt.gz';assert sha(src)=='11dae64b2d6b6e77846c3f14971fc9a313da86eb52a4b8b83df96c23eedc0ffd';peaks={g:[] for g in GENES}
 with gzip.open(src,'rt') as f:
  r=csv.DictReader(f,delimiter='\t');hdr=r.fieldnames;cols=hdr[7:];ec=[c for c in cols if c.startswith('EMC_')];ml=[c for c in cols if c.startswith('MLPS_')];ss=[c for c in cols if c.startswith('SS_')];nn=[c for c in cols if '_normal_' in c];assert len(ec)==4
  for row in r:
   if row['gene_symbol'] in GENES:peaks[row['gene_symbol']].append({**{k:row[k] for k in hdr[:7]},'values':{c:float(row[c]) for c in ec+ml+ss+nn}})
 add={}
 for g,rr in peaks.items():
  values={c:sum(r['values'][c] for r in rr) for c in ec+ml+ss+nn} if rr else {};add[g]={'exact_symbol_peaks':len(rr),'peaks':rr,'EMC_sums':{c:values[c] for c in ec} if rr else {},'limits':'No exact peak is assay unavailability, not transcript/protein absence;3SEQ units differ; normal panel unmatched; unknown donor overlap.','comparators':{k:{'n':len(cc),'median':statistics.median(values[c] for c in cc),'A':A([values[c] for c in ec],[values[c] for c in cc])} for k,cc in [('MLPS',ml),('SS',ss),('normal_context',nn)]} if rr else {}}
 (ROOT/'SURFACE-3SEQ-ADDENDUM.json').write_text(json.dumps({'source_sha256':sha(src),'source_path':str(src),'panel':GENES,'all_EMC_conditions':ec,'genes':add,'decision':'No clinical/protein inference; additive source coverage only, sourceunits not pooled.'},indent=2)+'\n')
 out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewed_commit':'ba6f0841b4adbc50d768d73ccbfc7db5b496235d','reviewed_freeze_sha256':sha(freeze),'all_frozen_artifact_hashes_verified':len(fr['files']),'bound_source_hashes':bound,'actual_checks':['All704 RNA originals, all13EMC/9primary-after-known-exclusions, rankA/yearcells/all13sensitivity/all9deletions/one-sided p/IUT/Holm reproduced independently.','All42original array specimens/exactsource annotation and6EMC-versus-four-comparator A reproduced independently.','MEASUREMENTS2302cells incl39RNA EMC,126array cells,40olderEMC gene/spot observations; fiveDLL3/fourSEZ6missing retained.','CurrentUSZ23 transcript rows/mapped sums and allretained model source hashes checked.','All4source-authenticated3SEQ EMC condition projection for frozen3gene panel added without download or rawcopy.'],'array_checks':arrchecks,'Holm_IUT':holm,'high_SEZ6_preserved':{r['sample_id']:vals['SEZ6'][r['sample_id']] for r in emcs if vals['SEZ6'][r['sample_id']]>=5},'coverage_validity':'Original packet explicitly pending other datasets/prior supplement lists/identity gaps; it is a scoped shelved checkpoint, not complete-coverage certificate. Additive3SEQ closes that source only.','value_judgment':'No standalone useful finding survives: NCAM1/CD56 already published, unfavorable LGFMS/synovial contrasts; DLL3/SEZ6 fail appreciable common expression/relevant cross-assay gate. HighSEZ6 observations remain real, not proteinabsence or subgroup/actionability proof.','decision':'PASS bounded negative/shelved checkpoint, with additive3SEQ coverage; no publication/novelty/clinical approval.','limits':['Bootstrap algorithm/conditional interpretation reviewed; this review does not independently reproduce every10000draw CI.','ARCHS4 model exact rows/source hashes checked by original worker offline replay; currentGene mapping not historical fullgene coverage.','No protein/accessibility/binding/dependency/response or proven nine globally independent donors; no global exhaustion.']}
 (ROOT/'SURFACE-REVIEW.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'decision':out['decision'],'RNAgenes':checked,'allfrozenhashes':len(fr['files']),'3SEQgenes':{g:v['EMC_sums'] for g,v in add.items()}}))
if __name__=='__main__':main()
