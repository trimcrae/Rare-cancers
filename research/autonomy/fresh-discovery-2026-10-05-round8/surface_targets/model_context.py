"""Offline replay of fixed accessible model context; never use disputed models."""
import csv, gzip, hashlib, io, json, pathlib, zipfile
import xml.etree.ElementTree as ET
BASE=pathlib.Path(__file__).resolve().parent
ROOT=pathlib.Path('/workspace/Rare-cancers')
PANEL=['DLL3','SEZ6','NCAM1']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def replay():
 frozen=json.loads((BASE/'MODEL-CONTEXT.json').read_text())
 assert sha(BASE/'AMENDMENT-01.txt')==frozen['amendment_sha256']
 for source in frozen['sources']:
  if 'path' in source: assert sha(pathlib.Path(source['path']))==source['sha256'],source['path']
 zp=ROOT/'research/autonomy/tmem266-all-cultures-2026-10-04/archs4-subset.zip'
 out={};sums={};n=0;selected={g:[] for g in PANEL}
 with zipfile.ZipFile(zp) as z:
  with z.open('matrix.tsv') as f:
   r=csv.reader(io.TextIOWrapper(f),delimiter='\t');cols=next(r)[1:];sums={sid:0 for sid in cols}
   for row in r:
    n+=1;vs=list(map(int,row[1:]));assert all(v>=0 for v in vs)
    for sid,v in zip(cols,vs):sums[sid]+=v
    if row[0] in PANEL:selected[row[0]].append(dict(zip(cols,vs)))
 for g,vs in selected.items():
  out[g]={'ARCHS4_exact_symbol_rows':vs,'row_count':len(vs),'CPM_only_if_unique':{sid:vs[0][sid]/sums[sid]*1e6 for sid in cols} if len(vs)==1 else None}
 with gzip.open(BASE/'source-cache/USZ23-RefSeq.quant.sf.gz','rt') as f: quants=list(csv.DictReader(f,delimiter='\t'))
 for g in PANEL:
  xml=ET.parse(BASE/f'source-cache/{g}-gene.xml').getroot()
  accs=sorted({e.text for e in xml.iter('Gene-commentary_accession') if e.text and e.text.startswith(('NM_','NR_','XM_','XR_'))})
  sel=[r for r in quants if r['Name'].split('.')[0] in accs]
  out[g]['USZ23_current_identifier_rows']=sel;out[g]['USZ23_current_accessions']=accs
  out[g]['USZ23_current_mapped_sum_TPM']=sum(float(r['TPM']) for r in sel) if sel else None
  for k in out[g]: assert out[g][k]==frozen['panel'][g][k],(g,k)
 assert n==67186 and sums=={'GSM2113301':40794510,'GSM6883080':28727977}
 return {'status':'source-bound offline replay agrees','matrix_rows':n,'denominators':sums,'panel':out,'limitations':'No biological replication, full historical mapping, protein or efficacy inferred.'}
if __name__=='__main__': print(json.dumps({k:v for k,v in replay().items() if k!='panel'},indent=2))
