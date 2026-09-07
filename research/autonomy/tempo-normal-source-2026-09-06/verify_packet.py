"""Offline integrity/structural recheck of frozen GSE119630 source packet."""
import datetime, hashlib, json, pathlib, subprocess, sys, xml.etree.ElementTree as ET
P=pathlib.Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 m=json.loads((P/'manifest.json').read_text(encoding='utf-8'))
 for r in m['files']:
  assert (P/r['file']).stat().st_size==r['bytes'],r['file']
  assert sha(P/r['file'])==r['sha256'],r['file']
 for r in m['dependencies']:
  assert sha(P.parent/r['file'])==r['sha256'],r['file']
 receipts=json.loads((P/'retrieval.json').read_text())+[json.loads((P/'methods-retrieval.json').read_text())]
 for r in receipts:
  assert r['status']==200 and (P/r['file']).stat().st_size==r['bytes']
  assert sha(P/r['file'])==r['sha256']
 t=ET.parse(P/'article.xml')
 ids={x.attrib['pub-id-type']:x.text for x in t.findall('.//article-meta/article-id')}
 assert ids['pmid']=='30794557' and ids['doi']=='10.1371/journal.pone.0212031'
 # Recompute deterministic artifacts and verify exact bytes against manifest.
 result=subprocess.run([sys.executable,str(P/'inspect_source.py')],capture_output=True,text=True,check=True)
 for r in m['files']: assert sha(P/r['file'])==r['sha256'],r['file']
 receipt={'status':'passed','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest_sha256':sha(P/'manifest.json'),'scope':'source hashes/lengths, primary article identifiers, gzip/CSV integrity, every count finite/nonnegative/integer, unique probe/sample IDs, exact full matrix decoding agreement, human column/GSM mapping, patient/biological/technical replication hierarchy, probe map equality across two matrices, deterministic regeneration and source dependency hashes','structural_output':json.loads(result.stdout),'expression_analysis_run':False,'normal_or_full_gate_run':False,'independent_coordinator_verification':'pending'}
 (P/'verification-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
