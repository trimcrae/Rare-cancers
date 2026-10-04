"""Integrate only unchanged-baseline instruction files; retain recovery and verification."""
import ast
import datetime
import difflib
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

packet = Path(__file__).resolve().parent
root = packet.parents[2]
writer = Path('C:/Users/mcrae/.codex/review-workspaces/emc-scientific-reevaluation-20261004')
digest = lambda data: hashlib.sha256(data).hexdigest()
now = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
baseline = json.loads((packet / 'starting-files.json').read_text())
before, after = {}, {}
assert shutil.disk_usage(root).free >= 10 * 1024**3
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip() == '3d550114538a1545e1eab03e1a93f69566da47de'
for rel, meta in baseline.items():
    before[rel] = (root / rel).read_bytes()
    assert digest(before[rel]) == meta['sha256'], f'Concurrent primary change: {rel}'
    after[rel] = (writer / rel).read_bytes()
amendment = 'research/autonomy/amendments.jsonl'
assert after[amendment].startswith(before[amendment])
assert len(after[amendment].splitlines()) == len(before[amendment].splitlines()) + 1
changed = [rel for rel in baseline if before[rel] != after[rel]]
assert len(changed) == 5
archive = packet / 'writer-recovery.zip'
with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as z:
    for rel, data in after.items():
        z.writestr(rel, data)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert all(z.read(rel) == data for rel, data in after.items())
patch = ''.join(''.join(difflib.unified_diff(before[rel].decode().splitlines(True), after[rel].decode().splitlines(True), fromfile='before/' + rel, tofile='after/' + rel)) for rel in changed)
(packet / 'incremental-methodology.patch').write_text(patch, encoding='utf-8')
for rel in changed:
    assert (root / rel).read_bytes() == before[rel]
    (root / rel).write_bytes(after[rel])
    assert (root / rel).read_bytes() == after[rel]
receipt = {'utc': now(), 'changed_files': changed, 'files': {rel: {'before_sha256': digest(before[rel]), 'after_sha256': digest(after[rel]), 'bytes': len(after[rel])} for rel in baseline}, 'worktree': str(writer), 'branch': 'codex/scientific-reevaluation-20261004', 'recovery_zip_sha256': digest(archive.read_bytes()), 'scope': 'Explicit user-directed instruction maintenance; preserve prior local edits. No shared queue or ownership records edited; no commit, push, PR or public mutation.'}
(packet / 'integration.json').write_text(json.dumps(receipt, indent=2) + '\n')

preserved = {}
for name in ['discovery-2026-10-03', 'tmem266-tissue-2026-10-03', 'tmem266-prepublication-2026-10-03', 'tmem266-questions-2026-10-04', 'tmem266-all-cultures-2026-10-04', 'scientific-reassessment-2026-10-04']:
    prior = packet.parent / name
    manifest = prior / ('MANIFEST-CURRENT.json' if name.startswith('discovery') else 'MANIFEST.json')
    entries = json.loads(manifest.read_text())['files']
    for rel, meta in entries.items():
        data = (prior / rel).read_bytes()
        assert digest(data) == meta['sha256'] and len(data) == meta['bytes'], str(prior / rel)
    preserved[name] = len(entries)

tree = ast.parse((root / 'scripts/research_run.py').read_text(encoding='utf-8'))
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'task_prompt')
namespace = {}
exec(compile(ast.Module(body=[fn], type_ignores=[]), 'actual_task_prompt', 'exec'), namespace)
protocol = (root / 'research/autonomy/OPERATING_PROTOCOL.md').read_text(encoding='utf-8')
prompts = []
for read_only in (True, False):
    prompt = namespace['task_prompt']('Bounded source audit', protocol, 'process:methodology', read_only)
    assert prompt.count(protocol) == 1
    prompts.append({'read_only': read_only, 'full_protocol_injected_once': True, 'sha256': digest(prompt.encode())})
diff = subprocess.run(['git', 'diff', '--check'], cwd=root, capture_output=True, text=True)
assert diff.returncode == 0, diff.stdout + diff.stderr
verification = {'utc': now(), 'status': 'passed', 'all_integrated_files_match': True, 'prior_packet_files_preserved': preserved, 'actual_prompt_composition_no_dispatch': prompts, 'diff_check_exit_code': diff.returncode, 'scope': 'Instruction integration, frozen-packet preservation and existing runtime prompt composition. This is not an automated scientific completeness detector.'}
(packet / 'verification.json').write_text(json.dumps(verification, indent=2) + '\n')
shutil.copyfile(packet.parent / 'scientific-reassessment-2026-10-04/run_preflight.py', packet / 'run_preflight.py')
print(json.dumps({'changed_files': changed, 'verification': verification}))
