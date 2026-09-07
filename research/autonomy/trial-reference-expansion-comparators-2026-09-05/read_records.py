import json,sys
from pathlib import Path
out=Path(__file__).resolve().parent
packet=json.loads((out.parent/'trial-reference-expansion-emc-2026-09-05/source-packet.json').read_text())
order=json.loads((out/'work-order.json').read_text())
for i in map(int,sys.argv[1:]):
 row=order[i-1];ps=packet[row['nct_id']]['copies'][0]['record']['protocolSection']
 print(json.dumps(row))
 for m in ['identificationModule','conditionsModule','descriptionModule','eligibilityModule','armsInterventionsModule','designModule','statusModule']:
  print(m+': '+json.dumps(ps.get(m),ensure_ascii=False))
