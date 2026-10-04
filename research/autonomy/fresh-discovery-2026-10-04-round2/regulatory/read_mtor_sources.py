from pathlib import Path
import json,urllib.request,hashlib,xml.etree.ElementTree as E
P=Path(__file__).resolve().parent
R=P.parents[1]/'fresh-discovery-2026-10-04'/'functional'
R=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-functional/research/autonomy/fresh-discovery-2026-10-04/functional')
terms=['rapamycin','everolimus','temsirolimus','ridaforolimus','mTOR','AZD8055','AZD2014','INK128','Torin','PP242','BEZ235','GDC0980','sirolimus','dactolisib']
for name in ['reused-Bangerter-all40-measured-ordinal-and-complete-source-overlap-final.json','reused-Iwata-complete221-screen-and24-IC50-literal-measurements-final.json']:
 a=json.loads((R/name).read_text());print(name,list(a))
 def walk(o,path=''):
  if isinstance(o,dict):
   for k,v in o.items():
    if isinstance(v,(str,int,float)) and any(t.lower() in str(v).lower() for t in terms):print(path,k,str(v)[:6000])
    elif isinstance(v,(dict,list)):walk(v,path+'/'+k)
  elif isinstance(o,list):
   for i,v in enumerate(o):walk(v,path+'/'+str(i))
 walk(a)
u='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9813045/fullTextXML'
try:
 b=urllib.request.urlopen(u,timeout=45).read();(P/'bangerter2022.xml').write_bytes(b)
 x=E.fromstring(b);pars=[' '.join(e.itertext()) for e in x.iter('p')];out=[v for v in pars if any(t.lower() in v.lower() for t in terms+['54','68','Foundation','year old','January','2020','2021'])]
 (P/'bangerter2022-mtor-eligibility.json').write_text(json.dumps({'url':u,'sha256':hashlib.sha256(b).hexdigest(),'paragraphs':out},indent=2));print('BANGERTER',json.dumps(out,ensure_ascii=False))
except Exception as e:print('FETCHERROR',str(e))
