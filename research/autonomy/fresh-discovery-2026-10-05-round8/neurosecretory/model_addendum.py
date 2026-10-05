"""All three prespecified transporter genes in known accessible authentic culture sources."""
from pathlib import Path
import csv,gzip,hashlib,io,json,urllib.request,datetime,zipfile,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
ARCHS4=Path('/workspace/Rare-cancers/research/autonomy/tmem266-all-cultures-2026-10-04/archs4-subset.zip')
QUANT=Path('/workspace/emc-r6-diagnostic/research/autonomy/fresh-discovery-2026-10-05-round8/surface_targets/source-cache/USZ23-RefSeq.quant.sf.gz')
GENES={'SLC6A2':'6530','SLC18A1':'6570','SLC18A2':'6571'}
XML=ROOT/'raw-cache/transporter-current-Gene.xml'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert sha(ARCHS4)=='f0bcd17e0c56ec038ea47ee14b7b57700333b46790d2cfb18a555cbf70ea4446'
 assert sha(QUANT)=='d49822e6ca79a18c186b00c4faa4087b8582bbb72c0be218fcea2e997565507f'
 receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=gene&id=6530,6570,6571&retmode=xml','method':'ordinary official Gene API; current gene/RefSeq identifiers only'}
 if not XML.exists():
  with urllib.request.urlopen(receipt['url'],timeout=35) as r:b=r.read(12000001);receipt['http_status']=r.status
  assert len(b)<=12000000;XML.write_bytes(b)
 receipt.update(sha256=sha(XML),bytes=XML.stat().st_size);ROOT.joinpath('MODEL-GENE-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
 access={}
 for gene in ET.parse(XML).getroot().iter('Entrezgene'):
  sym=gene.findtext('.//Gene-ref_locus');gid=gene.findtext('.//Gene-track_geneid')
  assert sym in GENES and gid==GENES[sym],(sym,gid)
  access[sym]=sorted(set(e.text for e in gene.iter('Gene-commentary_accession') if e.text and e.text.startswith(('NM_','NR_','XM_','XR_'))))
 assert set(access)==set(GENES)
 selected={g:[] for g in GENES};sums={};n=0
 with zipfile.ZipFile(ARCHS4) as z:
  with io.TextIOWrapper(z.open('matrix.tsv')) as f:
   r=csv.reader(f,delimiter='\t');cols=next(r)[1:];sums={c:0 for c in cols}
   for row in r:
    n+=1;vs=list(map(int,row[1:]));
    for c,v in zip(cols,vs):sums[c]+=v
    if row[0] in GENES:selected[row[0]].append(dict(zip(cols,vs)))
 assert n==67186 and sums=={'GSM2113301':40794510,'GSM6883080':28727977}
 with gzip.open(QUANT,'rt') as f:q=list(csv.DictReader(f,delimiter='\t'))
 rows={}
 for g in GENES:
  ss=[r for r in q if r['Name'].split('.')[0] in access[g]]
  rows[g]={'ARCHS4_exact_symbol_rows':selected[g],'ARCHS4_row_count':len(selected[g]),'USZ23_current_accessions':access[g],'USZ23_rows':ss,'USZ23_mapped_sum_TPM':sum(float(r['TPM']) for r in ss) if ss else None}
 out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_genes':list(GENES),'source_hashes':{'ARCHS4':sha(ARCHS4),'USZ23_quant':sha(QUANT),'current_GeneXML':sha(XML)},'ARCHS4_allrow_denominators':sums,'culture_conditions':['V1-34/GSM2113301','USZ22/GSM6883080','USZ23/GSM9037837'],'rows':rows,'limits':['Existing authentic source-model identities reused; each is one cultured library, not patients/technical replication.','USZ23 independence fromUSZ20 unresolved. No pooling tissue/culture/source quantities.','ARCHS4 rounded estimated counts, not TPM; all-row denominators are not literal library read depth.','Current official gene mapping does not reconcile every historical/retired RefSeq accession; zero mapped rows not full gene/protein absence.','RNA is not transporter protein/localization/MIBG uptake/benefit.'],'decision':'Completeness check only; no scientific-value rescue or common uptake claim.'}
 ROOT.joinpath('MODEL-ADDENDUM.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({g:{'ARCHS4':v['ARCHS4_exact_symbol_rows'],'USZ23_mapped_sum':v['USZ23_mapped_sum_TPM']} for g,v in rows.items()}))
if __name__=='__main__':main()
