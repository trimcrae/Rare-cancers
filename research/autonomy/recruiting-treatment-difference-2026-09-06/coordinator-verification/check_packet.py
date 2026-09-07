from pathlib import Path
import json,hashlib,gzip,zipfile,sys,itertools
packet=Path(sys.argv[1]); workspace=Path(sys.argv[2])
sha=lambda b:hashlib.sha256(b).hexdigest()
receipt=json.loads((packet/'integrity-receipt.json').read_bytes())
for name,m in receipt['files'].items():
 b=(packet/name).read_bytes();assert len(b)==m['bytes'] and sha(b)==m['sha256'],name
manifest=json.loads((packet/'coordinator/packet-manifest.json').read_bytes())
reader=json.loads((packet/'reader/manifest.json').read_bytes())
selection=json.loads((Path(__file__).parent/'selection-check.json').read_bytes())
assert manifest['archive_sha256']==selection['archive_sha256']
assert sha((packet/'protocol.md').read_bytes())==receipt['protocol_sha256']
assert sha((packet/'reader/protocol.md').read_bytes())==reader['protocol_sha256']
assert sha((packet/'reader/disease-anchors.md').read_bytes())==reader['disease_anchors_sha256']
assert sha((packet/'coordinator/packet-manifest.json').read_bytes())==receipt['packet_manifest_sha256']
bycase={r['case_id']:r for r in reader['records']};assert len(bycase)==8
h=set(selection['H_only']);a=set(selection['A_only'])
mappings=manifest['membership_and_provenance'];assert {m['nct_id'] for m in mappings}==h|a
archive=workspace/'research/autonomy/trial-frozen-baseline-package-2026-09-06/frozen-experiment.zip'
assert sha(archive.read_bytes())==manifest['archive_sha256']
with zipfile.ZipFile(archive) as z:
 audit=json.loads(z.read('trial-frozen-baseline-2026-09-06/version-audit.json'))
 for m in mappings:
  n=m['nct_id'];assert m['group']==('entrant' if n in a else 'displaced')
  origin=m['selected_source'];stored=z.read(origin['archive_member']);raw=gzip.decompress(stored)
  r=bycase[m['case_id']];b=(packet/'reader'/r['file']).read_bytes()
  assert sha(stored)==origin['page_stored_sha256'] and sha(raw)==origin['page_raw_sha256']
  assert b==raw[origin['byte_start']:origin['byte_end']]
  assert len(b)==r['bytes'] and sha(b)==r['raw_sha256']
  study=json.loads(b);assert study['protocolSection']['identificationModule']['nctId']==n
  obj=json.loads(raw)['studies'][int(origin['json_pointer'].split('/')[-1])];assert obj==study
  canonical=json.dumps(study,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
  assert sha(canonical)==r['canonical_sha256']==audit[n]['selected_record_sha256']
  assert not any(k in r for k in ('group','rank','score','H','A'))
patterns=0
for ints in itertools.product(((0,0),(0,1),(1,1)),repeat=5):
 c,e1,e2,d1,d2=ints
 vals=[(cv+x+y)-(cv+z+w) for cv,x,y,z,w in itertools.product(*(range(lo,hi+1) for lo,hi in ints))]
 assert (e1[0]+e2[0]-d1[1]-d2[1],e1[1]+e2[1]-d1[0]-d2[0])==(min(vals),max(vals))
 patterns+=1
result={'status':'passed','frozen_files':len(receipt['files']),'full_record_slices':8,'bounds_synthetic_patterns':patterns,'source_selection_check':'selection-check.json','scope':'Independent hashes, exact archived source slices, selected membership, masking metadata, and deterministic cancellation bounds. No relevance labels.'}
Path(__file__).with_name('packet-check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
