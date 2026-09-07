"""Read-only complete module display by frozen one-based work position."""
import json,sys
from pathlib import Path
O=Path(__file__).resolve().parent
p=json.loads((O/'source-packet.json').read_text(encoding='utf-8'))
w=json.loads((O/'work-order.json').read_text())
for row in w[int(sys.argv[1])-1:int(sys.argv[2])]:
    n=row['nct_id']; x=p[n]; print('\nPOSITION',row['position'],n)
    seen=set()
    for c in x['copies']:
        if c['record_sha256'] in seen: continue
        seen.add(c['record_sha256']); print('SOURCE',c['source'],c['pointer'],c['source_sha256'])
        r=c['record']['protocolSection']
        for m in ['identificationModule','conditionsModule','descriptionModule','eligibilityModule','armsInterventionsModule','designModule','statusModule']:
            if len(sys.argv)>3 and m not in sys.argv[3:]: continue
            print(m, json.dumps(r.get(m),ensure_ascii=False,indent=2))
