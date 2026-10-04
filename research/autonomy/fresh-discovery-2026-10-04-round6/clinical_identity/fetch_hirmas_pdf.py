import json
from fetch_sources import get,D
r=get(('hirmas2023.pdf','https://jnm.snmjournals.org/content/jnumed/64/5/711.full.pdf'))
(D/'hirmas-pdf-receipt.json').write_text(json.dumps(r,indent=2));print(r)
