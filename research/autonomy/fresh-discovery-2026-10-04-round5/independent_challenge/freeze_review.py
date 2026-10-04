"""Bind the actual reviewed clinical results and freeze this local packet."""
from pathlib import Path
import hashlib, json, datetime, shutil

ROOT = Path(__file__).resolve().parent
OWNER = Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-genomics/research/autonomy/fresh-discovery-2026-10-04-round5/fapi_imaging')

def item(path):
    b = path.read_bytes()
    return {'path': str(path), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
review = {
    'utc': now,
    'reviewed_owner_final_files': [item(OWNER/x) for x in ['RESULTS.txt', 'COVERAGE.txt', 'COVERAGE.json']],
    'reproduced_sources_and_identities': item(ROOT/'clinical-eligibility-evaluation.json'),
    'decision': 'Agree with scoped shelving. No new EMC finding; no absence or exhaustive-coverage claim.',
    'material_points': [
        'Koerber Table2, not Table1 alone, accounts for15; sarcomaNOS remains unresolved.',
        'Ferdinandus TS1 all21 and conventional-chondrosarcoma primary context independently confirmed; cases2/11 unresolved.',
        'Novruzov sole supplement is acquisition protocol; all6 genericSTS remain unresolved.',
        'Zhang generic high-gradefibrosarcoma1 unresolved, no EMC label is not authenticated exclusion.',
        'Dynamic2021 all6 and Diagnostics2025 all48 category accounting verified.',
        'Four Koerber cases and nine Ferdinandus cases are reported previously by the clinical owner; no donor independence or pooling inferred.',
        'Kessler/Lanzafame/Pabst/Kratochwil and staged broad clinical evidence remain incomplete as owner records; no advancement around these gaps.',
        'Interrupted FAP tissue task not retried, read further, or certified complete.'
    ],
    'scientific_value': 'A coverage correction or known broad-sarcoma illustration does not constitute useful new EMC biology or imaging knowledge.',
    'running_owned_processes': [],
    'git_actions': 'No commits/push/merge/PR; local uncommitted output only.'
}
(ROOT/'FINAL-REVIEW.json').write_text(json.dumps(review, indent=2)+'\n', encoding='utf-8')
files = sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name not in ['MANIFEST.json', 'FREEZE.json'])
entries = [{'path': str(p.relative_to(ROOT)).replace('\\','/'), 'bytes': p.stat().st_size,
            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
manifest = {'utc': now, 'entries': entries, 'payload_files': len(entries), 'payload_bytes': sum(x['bytes'] for x in entries)}
(ROOT/'MANIFEST.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
receipt = {'utc': now, 'manifest': item(ROOT/'MANIFEST.json'), 'payload_files':len(entries),
           'payload_bytes': manifest['payload_bytes'], 'free_bytes': shutil.disk_usage(ROOT).free,
           'floor_bytes': 10*1024**3, 'worker_cap_bytes': 10*1024**2,
           'running_owned_processes': [], 'scientific_scope': 'Clinical review scoped shelving; tissue review interrupted/incomplete.'}
assert receipt['free_bytes'] >= receipt['floor_bytes']
assert receipt['payload_bytes'] < receipt['worker_cap_bytes']
(ROOT/'FREEZE.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
print(json.dumps(receipt, indent=2))
