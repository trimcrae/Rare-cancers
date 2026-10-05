"""Offline exact official Gene-to-RefSeqRNA association; all frozen ADC genes/cultures.
Rejected ESearch numeric AllFields query preserved in MODEL-MAPPING-QA-CORRECTION.
Current linked mRNAs are a bounded annotation scope, not all historical transcripts.
"""
from pathlib import Path
import csv,gzip,hashlib,io,json,datetime,zipfile
ROOT=Path(__file__).resolve().parent
ARCH=Path('/workspace/Rare-cancers/research/autonomy/tmem266-all-cultures-2026-10-04/archs4-subset.zip')
QUANT=Path('/workspace/emc-r6-diagnostic/research/autonomy/fresh-discovery-2026-10-05-round8/surface_targets/source-cache/USZ23-RefSeq.quant.sf.gz')
GENES=['ERBB2','TACSTD2','NECTIN4','FOLR1','F3','MET']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 assert sha(ROOT/'PLAN-FROZEN.json')=='c00a4970c111998d62342194aff062513b38041cb92eecf523439d585782bbaf'
 assert sha(ARCH)=='f0bcd17e0c56ec038ea47ee14b7b57700333b46790d2cfb18a555cbf70ea4446'
 assert sha(QUANT)=='d49822e6ca79a18c186b00c4faa4087b8582bbb72c0be218fcea2e997565507f'
 linkpath=ROOT/'source-cache'/'ADC-gene-RefSeqRNA-elink.json';summarypath=ROOT/'source-cache'/'ADC-RefSeqRNA-summaries.json'
 assert sha(linkpath)=='484c7a69272f774f5522132ad8c5612818cdbf37fe68ee631e2b6a5df2c4ff27'
 assert sha(summarypath)=='dc533350c396bfb7f57fc75642bb4a9d421dff696eddfb9956f8074b5da18b1c'
 universe=json.loads((ROOT/'FDA-UNIVERSE-FROZEN.json').read_text());links=json.loads(linkpath.read_text())['linksets'];summaries=json.loads(summarypath.read_text())['result']
 gid_map={v['gene_id']:g for g,v in universe['official_gene_mapping'].items()};assert {s['ids'][0] for s in links}==set(gid_map)
 uidunion={uid for s in links for d in s['linksetdbs'] for uid in d['links']};assert uidunion==set(summaries['uids']) and len(uidunion)==58
 annotation={}
 for s in links:
  assert s['dbfrom']=='gene' and len(s['ids'])==1 and len(s['linksetdbs'])==1
  d=s['linksetdbs'][0];assert d['dbto']=='nuccore' and d['linkname']=='gene_nuccore_refseqrna'
  g=gid_map[s['ids'][0]];accepted=[];excluded=[]
  for uid in d['links']:
   q=summaries[uid];assert q['taxid']==9606 and q['uid']==uid
   a=q['accessionversion'];record={'nuccore_uid':uid,'accessionversion':a,'title':q['title'],'taxid':q['taxid']}
   (accepted if a.startswith(('NM_','XM_')) else excluded).append(record)
  annotation[g]={'gene_id':s['ids'][0],'official_linked_mRNA':accepted,'excluded_linked_non_mRNA':excluded}
 selected={g:[] for g in GENES};n=0
 with zipfile.ZipFile(ARCH) as z:
  with io.TextIOWrapper(z.open('matrix.tsv')) as f:
   r=csv.reader(f,delimiter='\t');cols=next(r)[1:];sums={c:0 for c in cols}
   for row in r:
    n+=1;vs=list(map(int,row[1:]))
    for c,v in zip(cols,vs):sums[c]+=v
    target=row[0] if row[0] in GENES else 'NECTIN4' if row[0]=='PVRL4' else None
    if target:selected[target].append({'source_symbol':row[0],'values':dict(zip(cols,vs))})
 assert n==67186 and sums=={'GSM2113301':40794510,'GSM6883080':28727977}
 with gzip.open(QUANT,'rt') as f:quant=list(csv.DictReader(f,delimiter='\t'))
 out={}
 for g in GENES:
  bases={r['accessionversion'].split('.')[0] for r in annotation[g]['official_linked_mRNA']};matched=[x for x in quant if x['Name'].split('.')[0] in bases]
  out[g]={'ARCHS4_rows':selected[g],'row_count':len(selected[g]),'currentRefSeq_mapping_status':'evaluated_official_Gene_RefSeqRNA_linked_mRNA','USZ23_source_rows':matched,'USZ23_current_mRNA_mapped_sum_TPM':sum(float(x['TPM']) for x in matched) if matched else None,'missing_is_not_zero':not matched,'annotation':annotation[g]}
 result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_hashes':{'ARCHS4':sha(ARCH),'USZ23_quant':sha(QUANT),'official_Gene_RefSeqRNA_ELink':sha(linkpath),'official_nuccore_UID_accession_summary':sha(summarypath)},'condition_map':{'GSM2113301':'V1-34','GSM6883080':'USZ22','GSM9037837':'USZ23'},'allrow_denominators':sums,'panel':out,'limits':['All three known accessible authentic cultures; one library each; unknown USZ23/USZ20 overlap, not independent patients/tissues.','ARCHS4 rounded estimated counts not TPM or literal reads; scales not pooled.','Official current linked human RefSeq mRNAs exclude retired/ncRNA/other annotations; unrepresented target is not absence, mapped zero not complete gene/protein absence.','RNA not accessible protein/dependency/ADC benefit; model condition cannot validate tissue allocation or normal safety.','USZ20/NCC other data source availability/condition crosswalks remain pending; disputed models not authenticated EMC.']}
 ROOT.joinpath('MODEL-RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({g:{'USZ23_TPM':v['USZ23_current_mRNA_mapped_sum_TPM'],'n_matched':len(v['USZ23_source_rows']),'n_official':len(v['annotation']['official_linked_mRNA'])} for g,v in out.items()}))
