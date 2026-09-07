"""Actions wrapper around independently reviewed minimal repair; no release push."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

HELPER_SHA = 'b266f35284710e3caa20d42be98a00d6f6e2799babb73ac602e5d97191e41a77'
SOURCE_REF = 'refs/heads/codex/ci-stage/emc-public-source-20260907'
REPAIR_REF = 'refs/heads/codex/ci-stage/emc-provenance-repaired-20260907'
TREE = '98b79afe943fe7590e1d91c1a06b5b95a7b47ba9'

def git(*args):
    return subprocess.check_output(['git', *args]).decode().strip()

def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true'
    assert os.environ.get('GITHUB_REPOSITORY') == 'trimcrae/Rare-cancers'
    temp = Path(os.environ['RUNNER_TEMP'])
    source = json.loads((temp / 'emc-public-source-receipt.json').read_text())
    s = source['source_commit']
    assert source['source_tree'] == TREE and source['public_ref'] == SOURCE_REF
    assert git('ls-remote', 'origin', SOURCE_REF).split() == [s, SOURCE_REF]
    assert not git('ls-remote', 'origin', REPAIR_REF), 'Preserve existing repair ref'
    helper = Path('.ci-bridge/prepare_manifest_provenance.py').resolve()
    assert hashlib.sha256(helper.read_bytes()).hexdigest() == HELPER_SHA
    tracking = 'refs/remotes/origin/' + SOURCE_REF.removeprefix('refs/heads/')
    git('fetch', '--no-tags', 'origin', SOURCE_REF+':'+tracking)
    work = temp / 'emc-provenance-source'
    evidence = temp / 'emc-provenance-evidence'
    assert not work.exists() and not evidence.exists()
    git('worktree', 'add', '--detach', str(work), s)
    subprocess.run([sys.executable, '-B', str(helper), '--repo', str(work),
                    '--source-sha', s, '--source-ref', SOURCE_REF,
                    '--evidence-dir', str(evidence)], check=True)
    result = json.loads((evidence / 'result.json').read_text())
    assert result['status'] == 'prepared_unverified' and result['parent_sha'] == s
    r = result['candidate_sha']
    assert git('show', '-s', '--format=%P', r) == s
    assert git('rev-parse', r+'^{tree}') == result['candidate_tree']
    assert result['candidate_tree'] != TREE
    expected = ['research/manuscripts/aso/fusion-junction-aso-archive-manifest.json',
                'research/release-candidates/PUB-SURFACE-TARGETS/2026-09-06/public-export/aso-manifest-provenance-correction.json']
    assert sorted(git('diff-tree', '--no-commit-id', '--name-only', '-r', r).splitlines()) == expected
    assert len(result['outgoing']) == 8
    assert {x['path']:x['sha256'] for x in result['outgoing']} == {x['path']:x['sha256'] for x in source['outgoing']}
    git('push', '--force-with-lease='+REPAIR_REF+':', 'origin', r+':'+REPAIR_REF)
    assert git('ls-remote', 'origin', REPAIR_REF).split() == [r, REPAIR_REF]
    receipt = {'schema':'emc-public-repair-ref/1', 'utc':datetime.now(timezone.utc).isoformat(),
               'source_sha':s, 'source_tree':TREE, 'candidate_sha':r,
               'candidate_tree':result['candidate_tree'], 'public_ref':REPAIR_REF,
               'helper_sha256':HELPER_SHA, 'github_run_id':os.environ.get('GITHUB_RUN_ID'),
               'scope':'Minimal two-file provenance repair only; no tests or release dispatch, FULL not yet run.'}
    (temp / 'emc-public-repair-ref.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt))

if __name__ == '__main__':
    main()
