"""Evaluate every deposited specimen's eligibility; retain original labels."""
from pathlib import Path
import re,json,collections,xml.etree.ElementTree as E
B=Path(__file__).resolve().parent
out={}
for filename in ['gse213065.txt','gse212527.txt','gse212526.txt']:
 rows=[]
 for rec in re.split(r'(?=\^SAMPLE = )',(B/filename).read_text()):
  if not rec.strip():continue
  data={}
  for ln in rec.splitlines():
   if ' = ' in ln:
    k,v=ln.split(' = ',1);data.setdefault(k,[]).append(v)
  props={}
  for x in data.get('!Sample_characteristics_ch1',[]):
   if ': ' in x: k,v=x.split(': ',1);props[k]=v
  rows.append(dict(gsm=data['!Sample_geo_accession'][0],title=data['!Sample_title'][0],properties=props,eligible_explicit_EMC=bool(re.search(r'extraskeletal|NR4A3|EMCS?',props.get('tissue',''),re.I))))
 ids=[r['properties'].get('individual') for r in rows]
 out[filename]=dict(n_records=len(rows),n_explicit_EMC=sum(r['eligible_explicit_EMC'] for r in rows),histologies=dict(collections.Counter(r['properties'].get('tissue','UNKNOWN') for r in rows)),n_individuals=len(set(ids)) if all(ids) else None,n_unique_titles=len({r['title'] for r in rows}),donor_note='Only explicit individual field is counted; distinct specimen titles are not independent donors.',records=rows)
(B/'geo-eligibility.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
for k,v in out.items():print(k,{x:v[x] for x in v if x!='records'})
old=B.parents[1]/'fresh-discovery-2026-10-04-round2'/'clinical'/'immunosarc2020.xml'
root=E.parse(old).getroot(); portions=[]
for el in root.iter():
 if el.tag in ('p','supplementary-material'):
  txt=' '.join(''.join(el.itertext()).split())
  if re.search(r'HTG|biops|immune|GSE|supplement|availab',txt,re.I):portions.append(dict(tag=el.tag,text=txt,links=[dict(e.attrib) for e in el.iter() if e.tag in ('ext-link','media')]))
(B/'immunosarc-methods-extract.json').write_text(json.dumps(portions,indent=2),encoding='utf-8')
print('IMMUNOSARC methods extracted',len(portions))
