"""Use only the 18+4 committed release fixtures; no generated data or truth inputs."""
import hashlib
import json
import time
from pathlib import Path
from frontier import solve,oracle

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'ipd-bounds-development-2026-09-06'


def main():
    start=time.perf_counter();results=[];inputs=[]
    oracle.threshold_proof()
    for filename in ['development-releases.json','stress-releases.json']:
        source=SOURCE/filename
        inputs.append({'path':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
        for item in json.loads(source.read_text())['cases']:
            result=solve(item['release'],seconds=8,max_transitions=100000,max_states=20000,witness_seconds=2,witness_nodes=50000)
            results.append({'source':filename,'case_id':item['case_id'],'result':result})
            print(json.dumps({'case_id':item['case_id'],**{k:result[k] for k in ['decision','complete_traversal','reason','q_outer','transitions','covered_regions','merged_histories','elapsed_seconds','tracemalloc_peak_bytes','nonempty_proven']}}),flush=True)
            # Save after each completed solve to preserve partial progress if interrupted.
            out={'synthetic':True,'partition':'existing_development_only','inputs':inputs,
                 'protocol_sha256':hashlib.sha256((ROOT/'protocol.md').read_bytes()).hexdigest(),
                 'cases':results,'elapsed_seconds':time.perf_counter()-start}
            (ROOT/'results.json').write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':main()
