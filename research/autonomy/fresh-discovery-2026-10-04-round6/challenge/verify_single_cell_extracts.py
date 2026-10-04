"""Verify every retrieved original library identity/condition extraction, no matrices."""
import argparse,pathlib,json,re,hashlib,datetime
ap=argparse.ArgumentParser();ap.add_argument('--packet',type=pathlib.Path,required=True);ap.add_argument('--source-dir',type=pathlib.Path);ap.add_argument('--output',type=pathlib.Path,required=True);a=ap.parse_args();P=a.packet;S=a.source_dir or P/'sources'
checked=[];missing=[];mismatch=[];identity_hits=[]
retry=json.load(open(P/'GSM9511154-RETRY-OBSERVATION.json'))
inputs=['GSM-ELIGIBILITY-OBSERVATIONS.json','ADDITIONAL-GSM-ELIGIBILITY-OBSERVATIONS.json']
for fn in inputs:
 j=json.load(open(P/fn))
 for gsm,r in j['libraries'].items():
  if gsm==retry['accession']:r=retry
  files=list(S.glob(gsm+'*.json'));f=next((f for f in files if hashlib.sha256(f.read_bytes()).hexdigest()==r.get('source_sha256')),None)
  if r.get('source_status')!=200 or f is None:
   missing.append({'accession':gsm,'reason':'successful-extraction-or-exact-original-not-available-at-source-dir'});continue
  b=f.read_bytes();h=hashlib.sha256(b).hexdigest();s=b.decode();fields={}
  for line in s.splitlines():
   if line.startswith('!Sample_') and ' = ' in line:
    k,v=line[8:].split(' = ',1);fields.setdefault(k,[]).append(v)
  for k in ['title','source_name_ch1','characteristics_ch1','description']:
   if fields.get(k,[])!=r.get(k,[]):mismatch.append({'accession':gsm,'field':k})
  if h!=r['source_sha256']:mismatch.append({'accession':gsm,'field':'rawhash'})
  if re.search(r'extraskeletal|\bEMC\b|\bEMCS\b|chordoid|chondromyxoid|H.EMC.SS|MUG.EMCS|NCC.EMC|USZ2[023]|myxoid.chondro',s,re.I):identity_hits.append(gsm)
  checked.append(gsm)
o={'date':datetime.datetime.now(datetime.timezone.utc).isoformat(),'meaning':'Independent original SOFT hash and complete four-field extraction check; no expression. Raw identity aliases screened; no implicit disease validation from untyped records.','checked_conditions':len(checked),'checked_accessions':checked,'missing':missing,'mismatch':mismatch,'identity_alias_hits':identity_hits,'input_bindings':[{'path':fn,'sha256':hashlib.sha256((P/fn).read_bytes()).hexdigest()} for fn in inputs+['GSM9511154-RETRY-OBSERVATION.json']]}
a.output.write_text(json.dumps(o,indent=2)+'\n');print({'checked':len(checked),'missing':missing,'mismatch':mismatch,'alias_hits':identity_hits})
