import json,sys
from pathlib import Path
p=json.loads(Path('research/autonomy/trial-reference-repair-2026-09-05/review-packet.json').read_text(encoding='utf-8'))
for i,(n,v) in enumerate(p.items()):
 if not int(sys.argv[1])<=i<int(sys.argv[2]):continue
 r=v['record']['protocolSection'];print('\nINDEX',i,n)
 for m in ['identificationModule','statusModule','conditionsModule','designModule','descriptionModule','armsInterventionsModule','eligibilityModule']:
  print(m,json.dumps(r.get(m),ensure_ascii=False))
