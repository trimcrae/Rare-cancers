from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import gzip, hashlib, json

src=Path('C:/Users/mcrae/.codex/worktrees/8010/EMC-Research/.cache/atlas-original-array-recovery-20260906/GSE24369.soft.gz')
out=Path(__file__).resolve().parent/'peerj-validation-source'
digest=hashlib.sha256(src.read_bytes()).hexdigest()
assert digest=='98c83c8ca23b7052cf0d4d0099a7bf1af6c3c972276038c3a633e2a5349b3c37'
rows=[]; row=None; lines=[]
with gzip.open(src,'rt',encoding='utf-8') as handle:
    for line in handle:
        if line.startswith('^SAMPLE = '):
            row={'accession':line.strip().split(' = ',1)[1]}; rows.append(row); lines.append(line)
        elif line.startswith('!Sample_') and row is not None:
            key,sep,value=line.strip().partition(' = ')
            if sep:
                row.setdefault(key.removeprefix('!Sample_'),[]).append(value)
                lines.append(line)
assert len(rows)==42 and len({r['accession'] for r in rows})==42
counts=Counter(tuple(r.get('characteristics_ch1',[])) for r in rows)
result={'utc':datetime.now(timezone.utc).isoformat(),'source':str(src),'source_sha256':digest,'source_url':'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE24nnn/GSE24369/soft/GSE24369_family.soft.gz','sample_count':len(rows),'characteristics_counts':[{'characteristics':list(k),'count':v} for k,v in counts.items()],'samples':rows,'scope':'All original accession sample metadata, no expression analysis or inferred patient identities. The published choice of 36 comparators is not independently identified by sample IDs.'}
(out/'GSE24369-original-sample-metadata.txt').write_text(''.join(lines),encoding='utf-8',newline='\n')
(out/'GSE24369-metadata-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in result.items() if k!='samples'},indent=2))
