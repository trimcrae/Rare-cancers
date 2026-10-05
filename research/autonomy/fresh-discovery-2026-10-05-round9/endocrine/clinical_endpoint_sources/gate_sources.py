"""Validate source/clock suitability without projecting clinical outcome values."""
import pathlib,json,hashlib,xml.etree.ElementTree as E,re
P=pathlib.Path(__file__).resolve().parent

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 errors=[]
 receipts=json.loads((P/'SOURCE-HASHES.json').read_text())
 for r in receipts['required_inputs']:
  f=pathlib.Path(r['path'])
  if not f.exists():errors.append('cache input absent: '+r['path']);continue
  if f.stat().st_size!=r['bytes'] or digest(f)!=r['sha256']:errors.append('source binding mismatch: '+r['path'])
 a=P/'raw-cache/PMC4015728-bioc.xml'
 if a.exists():
  root=E.parse(a).getroot();tabs=[]
  for ps in root.findall('.//passage'):
   i={x.get('key'):x.text for x in ps.findall('infon')}
   if i.get('type')=='table' and 'xml' in i:tabs.append(E.fromstring(i['xml']))
  if len(tabs)!=1:errors.append('expected one primary case table')
  else:
   rows=tabs[0].findall('.//tbody/tr')
   keys=[''.join(x.findall('./td')[0].itertext()).strip() for x in rows]
   if keys!=json.loads((P/'AGARAM-SCHEMA-ONLY.json').read_text())['case_identifiers']:errors.append('case-key schema mismatch')
   if len(rows)!=26 or any(len(x.findall('./td'))!=16 for x in rows):errors.append('table geometry mismatch')
   for row in rows:
    # Scope is lexical schema only. No recurrence flags or follow-up numbers emitted.
    recurrence=''.join(row.findall('./td')[13].itertext())
    if re.search(r'\d',recurrence):errors.append('recurrence field contains temporal/numeric representation; reopen schema')
 q=pathlib.Path(receipts['required_inputs'][1]['path'])
 if q.exists():
  root=E.parse(q).getroot();tables=root.findall('.//table-wrap')
  if len(tables)!=1:errors.append('PeerJ main-table count mismatch')
  heads=[''.join(x.itertext()) for x in tables[0].findall('.//thead//th')+tables[0].findall('.//thead//td')]
  if heads!=json.loads((P/'PEERJ-SCHEMA-ONLY.json').read_text())['tables'][0]['headers']:errors.append('PeerJ aggregate-header mismatch')
  links=[x.get('{http://www.w3.org/1999/xlink}href') for x in root.findall('.//*') if x.get('{http://www.w3.org/1999/xlink}href')]
  if 'peerj-14-21497-s009.xlsx' not in links:errors.append('Raw Data source link missing')
 decision=json.loads((P/'DECISION.json').read_text())
 if decision['numerical_analysis_launched'] or decision['campaign_exhausted']:errors.append('decision scope violation')
 print(json.dumps({'validation':'PASS' if not errors else 'FAIL','errors':errors,'validated':'exact retained originals, source table geometry/all26casekeys, lexical recurrence-time suitability, aggregatePeerJ schema/raw-data link, numerical-off/no-exhaustion scope','not_claimed':'endpoint analysis, all-public-source completion, biological or prognostic replication'}))
 raise SystemExit(bool(errors))
if __name__=='__main__':main()
