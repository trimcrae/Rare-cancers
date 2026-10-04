from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
from datetime import datetime,timezone

base=Path(__file__).parent
source=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-genomics/research/autonomy/fresh-discovery-2026-10-04-round3/dlk1')
out=[]
for name in ['dlk1-rms2013.xml','dlk1-sarcoma2020.xml','dlk1-mpnst2025.xml','filion2009.xml']:
 p=source/name;b=p.read_bytes();root=ET.fromstring(b)
 texts=[]
 for node in root.findall('.//body//p')+root.findall('.//table-wrap'):
  t=' '.join(''.join(node.itertext()).split())
  if any(w in t.casefold() for w in ['dlk1','pref-1','fetal antigen','normal','extraskeletal','splic']):
   texts.append(t)
 out.append({'file':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'title':' '.join(root.findtext('.//article-title','').split()),'selected_primary_paragraphs':texts})
(base/'primary-extracts.json').write_text(json.dumps({'created_utc':datetime.now(timezone.utc).isoformat(),'sources':out},indent=2),encoding='utf8')
for r in out:
 print(r['title'],len(r['selected_primary_paragraphs']))
