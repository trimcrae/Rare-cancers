import csv,hashlib,json
from pathlib import Path
p=Path(__file__).parent
rows=list(csv.DictReader((p/'archive-readme.txt').open(encoding='utf-8'),delimiter='\t'))
fastas=[r for r in rows if r['TYPE']=='FASTA']
results=[r for r in rows if r['TYPE']=='RESULT']
fid={r['ID'] for r in fastas}
linked=[r for r in results if fid.intersection(r['MAPPINGS'].split(','))]
out=dict(rows=len(rows),fasta_records=fastas,result_records=len(results),results_linked_to_deposited_fasta=len(linked),unlinked_result_names=[r['NAME'] for r in results if r not in linked],readme_sha256=hashlib.sha256((p/'archive-readme.txt').read_bytes()).hexdigest(),scope='Submission README metadata association, not direct audit of every result-file search parameter.')
(p/'metadata-association.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,indent=2))
