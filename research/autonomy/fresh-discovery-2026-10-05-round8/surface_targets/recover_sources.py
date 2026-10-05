"""Recover only this packet's missing public cache inputs with exact hash checks.

Shared original inputs use their recorded legacy recovery receipts; this does
not create fresh copies of those much larger originals or handle authentication.
"""
import argparse, hashlib, json, pathlib, urllib.request
BASE=pathlib.Path(__file__).resolve().parent
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--recover',action='store_true');args=ap.parse_args()
 records=[]
 for name in ['PRIOR-ART-SEARCH.json','FOCUSED-PRIOR-ART-SEARCH.json']:
  data=json.loads((BASE/name).read_text());items=data.get('queries',[]) if isinstance(data,dict) else data
  for r in items:
   if 'sha256' in r:records.append((r['key']+'.json',r['url'],r['sha256']))
 for r in json.loads((BASE/'DLL3-SEZ6-FULLTEXT-GATE.json').read_text())['sources']:
  if 'sha256' in r:records.append((r['pmcid']+'.xml',r['url'],r['sha256']))
 for r in json.loads((BASE/'MODEL-CONTEXT.json').read_text())['sources']:
  if 'url' in r and 'sha256' in r:records.append((pathlib.Path(r['path']).name,r['url'],r['sha256']))
 for name,url,expected in records:
  p=BASE/'source-cache'/name
  if not p.exists():
   if not args.recover: print(name,'missing; rerun --recover only if required');continue
   b=urllib.request.urlopen(url,timeout=45).read()
   if hashlib.sha256(b).hexdigest()!=expected:raise ValueError(f'{name}: live bytes changed; explicit new source-version amendment required')
   p.write_bytes(b)
  assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,name
  print(name,'hash verified')
if __name__=='__main__': main()
