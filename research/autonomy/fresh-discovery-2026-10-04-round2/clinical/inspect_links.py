from pathlib import Path
import re,json
BASE=Path(__file__).resolve().parent
for key in ['ogura2012-full','paioli2021-full','mri2025-full']:
 txt=(BASE/(key+'.xml')).read_text(encoding='utf8')
 links=sorted(set(x for x in re.findall(r'(?:href|src)=["\x27]([^"\x27]+)',txt) if any(p in x.lower() for p in ['/tables/','/figures/','supp','esm','moesm','download'])) )
 print(key,json.dumps(links))
 (BASE/(key+'-links.json')).write_text(json.dumps(links,indent=2))
