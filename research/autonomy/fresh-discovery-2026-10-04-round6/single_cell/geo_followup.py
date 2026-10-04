"""Authenticate series-level aliases and broader single-cell GEO metadata."""
import json,urllib.parse,time
from source_followup import repo,ROOT

BASE='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
QUERY='sarcoma AND ("single cell" OR "single-cell" OR "single nucleus" OR "spatial transcriptomics" OR "scRNA-seq") AND gse[ETYP] AND ("1900/01/01"[PDAT] : "2026/10/04"[PDAT])'
if __name__=='__main__':
 rec=[];outs={}
 ids=json.loads((ROOT/'sources/geo_alias_search.json').read_text())['esearchresult']['idlist']
 selected=[x for x in ids if x.startswith('200')]
 rec.append(repo('geo_broad_sc_search',BASE+'esearch.fcgi?'+urllib.parse.urlencode({'db':'gds','term':QUERY,'retmode':'json','retmax':1000}),2*1024*1024))
 if 'error' not in rec[-1]:
  b=json.loads((ROOT/rec[-1]['path']).read_text());print('broad_geo',b['esearchresult']['count']);newids=b['esearchresult']['idlist']
 else:newids=[]
 for label,ls in [('aliases',selected),('broad_sc',newids)]:
  for i in range(0,len(ls),80):
   time.sleep(.4)
   r=repo(f'geo_{label}_summary_{i//80}',BASE+'esummary.fcgi?'+urllib.parse.urlencode({'db':'gds','id':','.join(ls[i:i+80]),'retmode':'json'}),2*1024*1024);rec.append(r)
   if 'error' not in r:
    obj=json.loads((ROOT/r['path']).read_text()).get('result',{})
    outs.update({k:v for k,v in obj.items() if k!='uids'})
 (ROOT/'GEO-FOLLOWUP-RECEIPTS.json').write_text(json.dumps(rec,indent=2)+'\n')
 # Summary fields needed for eligibility; no expression or source-result selection.
 keep=('accession','title','summary','n_samples','taxon','gdsType','entryType','samples','pubmedids','pdat','suppfile')
 extract={k:{f:v.get(f) for f in keep} for k,v in outs.items()}
 (ROOT/'GEO-SERIES-ELIGIBILITY.json').write_text(json.dumps({'query':QUERY,'series':extract},indent=2)+'\n')
 print('metadata_entries',len(extract))
 for v in extract.values():
  t=(v.get('title') or '')+' '+(v.get('summary') or '')
  if any(x in t.lower() for x in ['extraskeletal','myxoid chondrosarcoma','nr4a3']):print(v.get('accession'),v.get('n_samples'),v.get('title'))
