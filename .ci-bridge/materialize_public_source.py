"""Actions-only source materialization; no private commits, release push, or tests."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from datetime import datetime, timezone

TREE = '98b79afe943fe7590e1d91c1a06b5b95a7b47ba9'
PARENT = 'eb149dda9fe816a4c36450d1138ac4a99d4d1951'
PACK_SHA = 'a631a7aa18000494657af51b02443481cdca8c7adedc24562aea4aeca2498785'
TARGET = 'refs/heads/codex/ci-stage/emc-public-source-20260907'

def git(*args, data=None, env=None):
    return subprocess.check_output(['git', *args], input=data, env=env)

def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true'
    assert os.environ.get('GITHUB_REPOSITORY') == 'trimcrae/Rare-cancers'
    bridge = Path('.ci-bridge')
    spec = json.loads((bridge / 'loader-input.json').read_text())
    assert spec['tree'] == TREE and spec['parent'] == PARENT
    assert spec['pack_sha256'] == PACK_SHA
    entries_path = bridge / 'candidate-entries-v1.json'
    assert digest(entries_path) == spec['entries_sha256']
    rows = json.loads(entries_path.read_text())
    assert len(rows) == 9752
    paths = [r['path'] for r in rows]
    assert len(set(paths)) == len(paths)
    for r in rows:
        assert r['type'] == 'blob' and r['mode'] in ('100644', '100755', '120000')
        assert not r['path'].startswith('/') and not any(x in ('', '.', '..', '.git') for x in r['path'].split('/'))
        assert '\x00' not in r['path'] and '\n' not in r['path'] and '\t' not in r['path']
    remote = git('ls-remote', 'origin', 'refs/heads/main').decode().strip().split()
    assert remote == [PARENT, 'refs/heads/main'], 'Public main changed: re-assess parent explicitly'
    git('fetch', '--no-tags', 'origin', 'refs/heads/main:refs/remotes/origin/main')
    assert git('cat-file', '-t', PARENT).strip() == b'commit'
    assert not git('ls-remote', 'origin', TARGET).strip(), 'Preserve existing source ref; do not overwrite'
    with tempfile.TemporaryDirectory(prefix='emc-materialize-') as tmp:
        tmp = Path(tmp)
        pack = tmp / 'candidate.pack'
        chunks = spec['chunks']
        assert len(chunks) == 106 and [r['chunk'] for r in chunks] == list(range(106))
        with pack.open('wb') as dst:
            for c in chunks:
                raw = git('cat-file', 'blob', c['git_sha1'])
                assert len(raw) == c['bytes'] and hashlib.sha256(raw).hexdigest() == c['sha256']
                assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == c['git_sha1']
                dst.write(raw)
        assert pack.stat().st_size == 443832854 and digest(pack) == PACK_SHA
        git('index-pack', '--strict', str(pack))
        listing = git('verify-pack', '-v', str(pack.with_suffix('.idx'))).decode().splitlines()
        objects = [line.split() for line in listing if len(line.split()[0]) == 40]
        assert len(objects) == 2153 and all(r[1] == 'blob' for r in objects)
        assert set(r[0] for r in objects) == set(spec['packed_blob_ids'])
        # Ingest only the verified blob pack into the normal repository object database.
        with pack.open('rb') as src:
            subprocess.run(['git', 'index-pack', '--strict', '--stdin'], stdin=src, check=True, stdout=subprocess.PIPE)
        check = git('cat-file', '--batch-check=%(objectname) %(objecttype) %(objectsize)',
                    data=('\n'.join(r['sha'] for r in rows)+'\n').encode()).decode().splitlines()
        assert len(check) == len(rows)
        for r, line in zip(rows, check):
            assert line.split() == [r['sha'], 'blob', str(r['bytes'])]
        env = dict(os.environ, GIT_INDEX_FILE=str(tmp / 'index'))
        git('read-tree', '--empty', env=env)
        index = b''.join((r['mode']+' '+r['sha']+'\t'+r['path']).encode()+b'\0' for r in rows)
        git('update-index', '-z', '--index-info', data=index, env=env)
        assert git('write-tree', env=env).decode().strip() == TREE
        assert len(spec['outgoing']) == 8
        verified = []
        for r in spec['outgoing']:
            raw = git('show', TREE+':'+r['path'])
            assert hashlib.sha256(raw).hexdigest() == r['sha256']
            verified.append({'path': r['path'], 'sha256': r['sha256'], 'bytes': len(raw)})
        commit_env = dict(os.environ, GIT_AUTHOR_NAME='github-actions[bot]',
                          GIT_AUTHOR_EMAIL='41898282+github-actions[bot]@users.noreply.github.com',
                          GIT_COMMITTER_NAME='github-actions[bot]',
                          GIT_COMMITTER_EMAIL='41898282+github-actions[bot]@users.noreply.github.com')
        commit = git('commit-tree', TREE, '-p', PARENT, env=commit_env,
                     data=b'Materialize audited EMC public source snapshot\n\nExact source tree; new public provenance, not original private history. No FULL pass claimed.\n').decode().strip()
        assert git('rev-parse', commit+'^{tree}').decode().strip() == TREE
        assert git('show', '-s', '--format=%P', commit).decode().strip() == PARENT
        git('push', '--force-with-lease='+TARGET+':', 'origin', commit+':'+TARGET)
        assert git('ls-remote', 'origin', TARGET).decode().strip().split() == [commit, TARGET]
        receipt = {'schema':'emc-public-source-materialization/1', 'utc':datetime.now(timezone.utc).isoformat(),
                   'source_commit':commit, 'source_tree':TREE, 'public_parent':PARENT,
                   'public_ref':TARGET, 'pack_sha256':PACK_SHA, 'path_count':len(rows),
                   'outgoing':verified, 'github_run_id':os.environ.get('GITHUB_RUN_ID'),
                   'scope':'New public source S only; no private commits/history exported, no release/main push or FULL claim.'}
        report = Path(os.environ['RUNNER_TEMP']) / 'emc-public-source-receipt.json'
        report.write_text(json.dumps(receipt, indent=2)+'\n')
        print(json.dumps(receipt))

if __name__ == '__main__':
    main()
