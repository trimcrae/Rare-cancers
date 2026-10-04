"""Verify packet identities/completeness of bounded diagnostics and bind artifacts."""
from pathlib import Path
import json,hashlib,csv,shutil,subprocess
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parent
def main():
 b=json.loads((BASE/'bcell-pilot-results.json').read_text())
 d=json.loads((BASE/'mapping-diagnostic-results.json').read_text())
 runs=list(csv.DictReader((BASE/'PRJNA1357027-runs.tsv').open(),delimiter='\t'))
 assert len(runs)==12 and len(d['runs'])==12 and len(b['sample_ids'])==12
 assert set(b['sample_ids'])=={x['sample_alias'] for x in runs}=={x['sample'] for x in d['runs']}
 assert all(x['reads_inspected']==10000 and sum(x['counts'].values())==10000 and x['lengths']=={'50':10000} for x in d['runs'])
 assert all(g in d['manifest']['prespecified_gene_probes'] and d['manifest']['prespecified_gene_probes'][g] for g in b['missing'])
 assert not list(BASE.glob('raw-Si*.json')),'No complete count output expected'
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE,text=True).strip()
 entries=[{'path':str(p.relative_to(BASE)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(BASE.rglob('*')) if p.is_file() and p.name!='MANIFEST.json']
 total=sum(x['bytes'] for x in entries);free=shutil.disk_usage(BASE).free
 assert total<50_000_000 and free>=10*1024**3
 out={'utc':datetime.now(timezone.utc).isoformat(),'head':head,'commit_status':'uncommitted local packet; no worker commit/push/merge/PR','packet_bytes_before_manifest':total,'free_bytes':free,'validation':'12 identities match; each 10000-read diagnostic has reconciled categories; missing processed genes all present in assay; no full-library count output; hashes bound','diagnostic_reads_total':120000,'full_library_counts_complete':False,'additional_100k_read_followup_started':False,'scientific_decision':'shelve standalone contributions; raw evidence remains pending accessible analysis','owned_processes_running':False,'files':entries}
 (BASE/'MANIFEST.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:v for k,v in out.items() if k!='files'}))
if __name__=='__main__':main()
