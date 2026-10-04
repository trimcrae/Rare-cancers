"""Independent worker's platform coverage audit, not proof of exhaustive literature novelty."""
import urllib.request,gzip,re,hashlib,json
from pathlib import Path
u='https://ftp.ncbi.nlm.nih.gov/geo/platforms/GPLnnn/GPL96/annot/GPL96.annot.gz'
b=urllib.request.urlopen(u,timeout=45).read();s=gzip.decompress(b).decode()
terms=['TMEM266','C15orf27','FLJ38190','123591','NM_152335','1552400_a_at']
receipt={'url':u,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'probe_rows':sum(bool(re.match(r'^\d+.*_at\t',x)) for x in s.splitlines()),'matches':{t:[x.split('\t')[:4] for x in s.splitlines() if re.search(r'(?<![A-Za-z0-9])'+t+r'(?![A-Za-z0-9])',x,re.I)] for t in terms}}
p=Path('research/modalities/_s4_lane_inputs/GPL570_id2gene.json.gz');j=json.loads(gzip.decompress(p.read_bytes()))['id2gene']
receipt['GPL570_matches']={k:v for k,v in j.items() if v.get('symbol')=='TMEM266'};receipt['GPL570_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
receipt['interpretation']='Filion2009 used U133A/GPL96,22215probes. No currently annotated TMEM266 measurement found on that platform. This excludes that assay as a source of a TMEM266-specific prior finding, not every historical publication or possible unannotated cross-hybridization.'
Path(__file__).with_name('round2-prior-art-coverage.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
assert receipt['probe_rows']==22215 and all(not v for v in receipt['matches'].values())
print(json.dumps(receipt,indent=2))
