"""Read-only independent current-association and authentic-culture projection."""
import argparse,csv,gzip,hashlib,io,json,pathlib,zipfile
import numpy as np
HERE=pathlib.Path(__file__).resolve().parent
ROOT=pathlib.Path('/workspace/Rare-cancers/research/autonomy')
GENES=['ERBB2','TACSTD2','NECTIN4','FOLR1','F3','MET']
ALIASES={g:g for g in GENES}|{'PVRL4':'NECTIN4'}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def eq(a,b,label):
 if isinstance(a,(int,float)) and isinstance(b,(int,float)):assert np.isclose(a,b,atol=1e-12,rtol=1e-11),(label,a,b)
 else:assert a==b,(label,a,b)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--peer',type=pathlib.Path,required=True);ap.add_argument('--freeze',default='SCIENCE-FREEZE.json');ap.add_argument('--freeze-sha',required=True);ar=ap.parse_args();peer=ar.peer
 assert sha(peer/ar.freeze)==ar.freeze_sha;freeze=json.loads((peer/ar.freeze).read_text())
 entries=freeze['files'].items() if isinstance(freeze['files'],dict) else [(r['path'],r) for r in freeze['files']]
 for n,r in entries:assert sha(peer/n)==(r['sha256'] if isinstance(r,dict) else r),n
 result=json.loads((peer/'MODEL-RESULTS.json').read_text());annotation=json.loads((HERE/'MODEL-ANNOTATION-GATE.json').read_text());assert annotation['verdict'].startswith('PASS')
 for path,h in annotation['owner_source_bindings'].items():assert sha(pathlib.Path(path))==h
 transcripts={g:{r['RefSeq_accessionversion'].split('.')[0] for r in annotation['rows'] if r['gene']==g and r['accepted_mRNA']} for g in GENES}
 arch=ROOT/'tmem266-all-cultures-2026-10-04/archs4-subset.zip';quant=HERE.parent/'source-cache/USZ23-RefSeq.quant.sf.gz';assert sha(arch)==result['source_hashes']['ARCHS4'];assert sha(quant)==result['source_hashes']['USZ23_quant'];rows={g:[] for g in GENES};denom={}
 with zipfile.ZipFile(arch) as z:
  with z.open('matrix.tsv') as f:
   reader=csv.reader(io.TextIOWrapper(f),delimiter='\t');cols=next(reader)[1:];denom={c:0 for c in cols}
   for r in reader:
    vv=dict(zip(cols,map(int,r[1:])))
    for c,v in vv.items():denom[c]+=v
    if r[0] in ALIASES:rows[ALIASES[r[0]]].append({'source_symbol':r[0],'values':vv})
 eq(denom,result['allrow_denominators'],'ARCHS4 all source rows denominator')
 qrows={g:[] for g in GENES}
 with gzip.open(quant,'rt') as f:
  for r in csv.DictReader(f,delimiter='\t'):
   base=r['Name'].split('.')[0]
   for g,accs in transcripts.items():
    if base in accs:qrows[g].append(r)
 compact={}
 for g in GENES:
  rr=result['panel'][g];eq(rr['ARCHS4_rows'],rows[g],g+'ARCHS4');eq(rr['row_count'],len(rows[g]),g+'ARCHS4 row count');eq(rr['USZ23_source_rows'],qrows[g],g+'all matched quant rows')
  total=sum(float(r['TPM']) for r in qrows[g]);eq(rr['USZ23_current_mRNA_mapped_sum_TPM'],total,g+'USZ23 sum')
  compact[g]={'ARCHS4_counts':rows[g],'current_linked_mRNAs':len(transcripts[g]),'matched_quant_rows':len(qrows[g]),'current_mapped_TPM_sum':total}
 out={'schema':'emc-independent-ADC-culture-review/1','owner_freeze_sha256':ar.freeze_sha,'model_results_sha256':sha(peer/'MODEL-RESULTS.json'),'model_annotation_gate_sha256':sha(HERE/'MODEL-ANNOTATION-GATE.json'),'read_only_source_bindings':{str(arch):sha(arch),str(quant):sha(quant)}|annotation['owner_source_bindings'],'arithmetic_status':'passed','all_condition_scope':['V1-34/GSM2113301','USZ22/GSM6883080','USZ23/GSM9037837'],'results':compact,'limits':'Current official mRNA-associated accessions mapped by accession base, not all retired/historical transcript reconstruction; no mapped-row zero is whole-gene protein absence. Counts and TPM differ in units/assay and models are not independent clinical cohorts. Preliminary GeneID→AllFields results invalid and superseded before freeze. No culture rescue of failed tissue gate.','identity_scope':'Previously verified authentic model identities reused; disputed MUG/HEMCS and generic chondrosarcoma models not substituted.'}
 (HERE/'MODEL-ARITHMETIC-REVIEW.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'arithmetic_status':out['arithmetic_status'],'model_sha256':out['model_results_sha256'],'matched_quant_rows':{g:r['matched_quant_rows'] for g,r in compact.items()}}))
if __name__=='__main__':main()
