"""Recover the public USCAP2026 abstract; read-only POST is a retrieval endpoint."""
import urllib.request,urllib.parse,json,html,re,hashlib,datetime
from pathlib import Path
bdir=Path(__file__).resolve().parent
p={'source':'9427052B-EB87-B001-574B51E4E8F34C4B','cid':'379','SessionID':'14801','AbID':'50619','ProgramID':'55212','pgid':'5167','ajax':'1'}
u='https://my.uscap.org/uscap/proxy.cfm?public_program_details=1'
b=urllib.request.urlopen(u,data=urllib.parse.urlencode(p).encode(),timeout=45).read()
j=json.loads(b);s=html.unescape(re.sub('<[^>]+>',' ',j[0]['return_text']))
s=re.sub(r'[ \t]+',' ',s)
(bdir/'round2-caris-abstract.txt').write_text(s,encoding='utf-8')
receipt={'url':u,'parameters':p,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(b),'raw_json_sha256':hashlib.sha256(b).hexdigest(),'discovery_url':'https://2026am.uscap.org/schedule/','doi':'10.1016/j.labinv.2025.104344','interpretation':'Original authors finding, not a new analysis. No patient-level or denominator-resolved gene table recovered; cross-cohort independence unverified.'}
(bdir/'round2-caris-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt))
