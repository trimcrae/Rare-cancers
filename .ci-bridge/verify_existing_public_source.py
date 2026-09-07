"""Recheck the exact source ref recovered through the authorized GitHub connector."""
import hashlib, json, os, subprocess
from pathlib import Path
from datetime import datetime, timezone
S='17a958ecb47fdef602501c81c0025a9f484c6581'
TREE='98b79afe943fe7590e1d91c1a06b5b95a7b47ba9'
PARENT='eb149dda9fe816a4c36450d1138ac4a99d4d1951'
REF='refs/heads/codex/ci-stage/emc-public-source-20260907'
def git(*args):return subprocess.check_output(['git',*args])
def main():
    assert os.environ.get('GITHUB_ACTIONS')=='true'
    assert os.environ.get('GITHUB_REPOSITORY')=='trimcrae/Rare-cancers'
    recovery=json.loads(Path('.ci-bridge/recovery-source.json').read_text())
    assert recovery=={'source_commit':S,'source_tree':TREE,'public_parent':PARENT,'materialization_run':34073405113}
    spec=json.loads(Path('.ci-bridge/loader-input.json').read_text())
    assert spec['tree']==TREE and spec['parent']==PARENT and len(spec['outgoing'])==8
    assert git('ls-remote','origin',REF).decode().strip().split()==[S,REF]
    git('fetch','--no-tags','origin',REF+':refs/remotes/origin/codex/ci-stage/emc-public-source-20260907')
    assert git('rev-parse',S+'^{tree}').decode().strip()==TREE
    assert git('show','-s','--format=%P',S).decode().strip()==PARENT
    assert len(git('ls-tree','-r','--name-only',S).splitlines())==9752
    verified=[]
    for item in spec['outgoing']:
        raw=git('show',S+':'+item['path'])
        assert hashlib.sha256(raw).hexdigest()==item['sha256']
        verified.append({'path':item['path'],'sha256':item['sha256'],'bytes':len(raw)})
    receipt={'schema':'emc-public-source-materialization/2','utc':datetime.now(timezone.utc).isoformat(),'source_commit':S,'source_tree':TREE,'public_parent':PARENT,'public_ref':REF,'pack_sha256':spec['pack_sha256'],'path_count':9752,'outgoing':verified,'github_run_id':os.environ['GITHUB_RUN_ID'],'prior_materialization_run':34073405113,'scope':'Existing exact-tree source independently reverified after connector ref recovery; prior Actions push failure preserved. No FULL pass claimed.'}
    (Path(os.environ['RUNNER_TEMP'])/'emc-public-source-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))
if __name__=='__main__':main()
