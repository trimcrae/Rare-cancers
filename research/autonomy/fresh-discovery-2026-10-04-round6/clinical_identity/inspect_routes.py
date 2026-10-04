from fetch_sources import D,get
from pypdf import PdfReader
import json
links=[]
for page in PdfReader(D/'interobserver2023.pdf').pages:
 for a in page.get('/Annots',[]):
  o=a.get_object(); action=o.get('/A',{})
  if action.get('/URI'):links.append(str(action['/URI']))
(D/'interobserver-pdf-links.json').write_text(json.dumps(links,indent=2))
print('PDF links:',links)
r=get(('hirmas2023-openalex.json','https://api.openalex.org/works/https://doi.org/10.2967/jnumed.122.264689'))
(D/'openalex-fetch-receipt.json').write_text(json.dumps(r,indent=2))
print(r)
if 'sha256' in r:print(json.dumps(json.loads((D/r['file']).read_text()).get('locations'),indent=2))
