import json,concurrent.futures,re,pathlib,urllib.parse
from fetch_sources import D,get
JOBS={f'jci2023-table{i}.jpg':f'https://df6sxcketz7bb.cloudfront.net/manuscripts/170000/170324/medium/jci.insight.170324.t{i}.jpg' for i in [1,2,3]}
JOBS.update({
 'pride-PXD046803.json':'https://www.ebi.ac.uk/pride/ws/archive/v2/projects/PXD046803',
 'pride-PXD027309.json':'https://www.ebi.ac.uk/pride/ws/archive/v2/projects/PXD027309',
 'pride-search-chondrosarcoma.json':'https://www.ebi.ac.uk/pride/ws/archive/v2/search/projects?keyword=chondrosarcoma&pageSize=100&page=0',
 'pride-search-extraskeletal.json':'https://www.ebi.ac.uk/pride/ws/archive/v2/search/projects?keyword=extraskeletal&pageSize=100&page=0',
 'pride-search-NR4A3.json':'https://www.ebi.ac.uk/pride/ws/archive/v2/search/projects?keyword=NR4A3&pageSize=100&page=0'
})
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: out=list(pool.map(get,JOBS.items()))
 for page in range(1,5):
  if sum(p.stat().st_size for p in D.iterdir() if p.is_file())>7*1024**2: break
  name=f'pride-search-sarcoma-page{page}.json';rec=get((name,f'https://www.ebi.ac.uk/pride/ws/archive/v2/search/projects?keyword=sarcoma&pageSize=100&page={page}'));out.append(rec)
  if 'error' in rec:break
  if len(json.loads((D/name).read_text()))<100:break
 (D/'last-metadata-fetch-receipts.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
