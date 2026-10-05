"""Source/schema replay only: no gene/count rows or biological outcomes."""
import hashlib,json,zlib
from pathlib import Path
p=Path(__file__).resolve().parent
prefix=(p/'raw/processed-counts-compressed-prefix.bin').read_bytes()
d=zlib.decompressobj(16+zlib.MAX_WBITS)
out=bytearray(); used=0
for x in prefix:
 used+=1
 pending=bytes([x])
 while pending:
  b=d.decompress(pending,1)
  pending=d.unconsumed_tail
  if b:
   out.extend(b)
   if b==b'\n':break
  if not pending:break
 if out.endswith(b'\n'):break
assert out.endswith(b'\n')
header=bytes(out[:-1]).decode()
old=json.loads((p/'PROCESSED-FILE-HEADER.json').read_text())
assert old['header']==header
columns=header.rstrip('\r').split('\t')[1:]
source=p.parent/'native_culture_fidelity_gate/GSE221532-IDENTITY-CONDITION-ROSTER.json'
rows=json.loads(source.read_text())['rows']
titles={r['fields']['title'][0]:r['GSM'] for r in rows}
links=[]
for i,label in enumerate(columns,1):
 links.append({'column_index':i,'literal_alias':label,'GSM_title_match':titles.get(label),'mapping_status':'unique exact title correspondence, histotype requires separate source authentication' if columns.count(label)==1 and label in titles else 'ambiguous repeated label; no donor/replicate/reassignment inferred'})
result={'scope':'First newline only; no numeric gene row decompressed in this replay. Exact alias/condition mapping only.','compressed_bytes_consumed':used,'header_bytes_including_newline':len(out),'prefix_sha256':hashlib.sha256(prefix).hexdigest(),'columns':links,'missing_source_titles':sorted(set(titles)-set(columns)),'repeated_labels':sorted({x for x in columns if columns.count(x)>1}),'source_samples':len(rows),'data_columns':len(columns),'gene_header':header.split('\t')[0],'normalization':'Source methods describe tximport raw gene counts; header alone does not authenticate annotation/version/effective lengths or TPM comparability.'}
(p/'HEADER-CONDITION-REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'pass':True,'compressed_bytes_consumed':used,'header_bytes':len(out),'source_samples':len(rows),'data_columns':len(columns),'missing_source_titles':result['missing_source_titles'],'repeated_labels':result['repeated_labels']}))
