"""Seal this working-draft checkpoint after completed checks; no publication."""
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    gate = json.loads((BASE / 'final-normal-preflight-receipt.json').read_text())
    verification = json.loads((BASE / 'verification.json').read_text())
    assert verification['status'] == 'pass'
    # Preserve a failed repository gate honestly; this seals a working draft,
    # not an integration or publication candidate. No acceptance gate is waived.
    gate_log = (BASE / 'final-normal-preflight.log').read_text(encoding='utf8')
    failed_lines = [line for line in gate_log.splitlines() if line.strip().startswith('FAILED --')]
    assert gate['exit_code'] == 1 and len(failed_lines) == 2
    assert 'systems_check.py' in failed_lines[0]
    assert 'emc_systems_map_check.py' in failed_lines[1]
    targeted = json.loads((BASE / 'targeted-systems-recheck.json').read_text())
    assert targeted['exit_code'] == 0
    assert sha(BASE / 'DRAFT.md') == verification['draft_sha256']
    assert sha(BASE / 'SUPPLEMENT.md') == verification['supplement_sha256']
    # Later frontmatter supplies required repository metadata. Scientific bodies
    # must remain byte-identical to the independently reviewed repaired text.
    body_hashes = {}
    for name, expected in [('DRAFT.md', 'e03e0e227b4687d441abbb385016a26bcd63673c180d8231263e371a9f1bc37c'),
                           ('SUPPLEMENT.md', '96cfc645915660c20eb9956b739fd192a92c674271e94f14c38fe2737a972ce6')]:
        text = (BASE / name).read_text(encoding='utf8')
        assert text.startswith('---\n')
        body = text.split('---\n', 2)[2].lstrip('\n')
        body_hashes[name] = hashlib.sha256(body.encode()).hexdigest()
        assert body_hashes[name] == expected
    scripts = sorted(BASE.glob('*.py'))
    for p in scripts:
        compile(p.read_text(encoding='utf-8-sig'), str(p), 'exec')
    completion = {
        'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'Exploratory investigation complete; working draft written and reviewed; shared-registry integration pending',
        'base_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'draft': 'DRAFT.md', 'methods': 'SUPPLEMENT.md', 'handoff': 'HANDOFF.txt',
        'new_finding': 'Upstream TMEM266 coding-region-associated RNA signal in reused EMC tissue arrays; comparative enrichment over LGFMS',
        'not_established': ['malignant-cell localization', 'full-length coding transcript', 'protein',
                            'tumor specificity', 'dependency', 'clinical usefulness'],
        'normal_repository_gate': gate,
        'subsequent_metadata_recheck': targeted,
        'repository_gate_passed': False,
        'remaining_repository_gate': 'Three consumer registrations for a rejected disputed-model route; registry-read-by.patch is prepared but not applied to a differently owned shared registry',
        'reviewed_scientific_body_sha256': body_hashes,
        'scientific_verification': 'verification.json and independent-raw-verification.json',
        'review': 'REVIEW.txt; three independent scopes plus focused repair verification',
        'full_publication_checks_run': False, 'independent_ultra_review_run': False,
        'submission_ready': False, 'publication_or_submission_performed': False,
        'outreach_or_paid_access_performed': False, 'commit_push_or_shared_queue_edit': False,
        'workers': {name: {'status': 'completed', 'read_only': True, 'owned_process_running': False}
                    for name in ['emc_clinical', 'emc_genomics', 'emc_measurements']},
        'task_owned_processes_running_at_checkpoint': [],
        'other_coordinators_processes': 'Not controlled or claimed stopped by this task',
        'new_worktree_or_runtime': False,
        'previous_evidence_preservation': verification['previous_packets_unchanged'],
        'free_bytes_at_checkpoint': shutil.disk_usage(ROOT).free,
        'optional_recovery_script': 'Syntax checked; assembled recipe not rerun end to end',
        'python_syntax_checked': [p.name for p in scripts],
        'next_actions': ['Human review of the working draft',
                         'Shared coordinator integrates the prepared three-entry registry patch, regenerates affected views if required, and reruns the normal gate',
                         'If advancing toward submission, reconcile ownership and prepare a portable public evidence package',
                         'Freeze outgoing files for the required independent ultra review before any submission',
                         'Scientific extension requires authenticated tissue localization/full-length evidence'],
        'authorization_boundary': 'No publication, submission, outreach, paid resources or public record changes authorized'
    }
    (BASE / 'COMPLETION.json').write_text(json.dumps(completion, indent=2) + '\n')
    files = {str(p.relative_to(BASE)).replace('\\', '/'): {'bytes': p.stat().st_size, 'sha256': sha(p)}
             for p in sorted(BASE.rglob('*')) if p.is_file() and p.name != 'MANIFEST.json'}
    out = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'scope': 'Local working-draft checkpoint, not a published release', 'files': files}
    (BASE / 'MANIFEST.json').write_text(json.dumps(out, indent=2) + '\n')
    # Re-read the written manifest and verify all bound files.
    saved = json.loads((BASE / 'MANIFEST.json').read_text())
    for name, expected in saved['files'].items():
        p = BASE / name
        assert p.stat().st_size == expected['bytes'] and sha(p) == expected['sha256']
    total = sum(p.stat().st_size for p in BASE.rglob('*') if p.is_file())
    assert total <= 2_000_000, total
    print(json.dumps({'status': 'complete', 'manifest_files': len(files), 'folder_bytes': total,
                      'gate_exit': gate['exit_code'], 'task_owned_processes_running': [],
                      'draft_sha256': sha(BASE / 'DRAFT.md'), 'free_bytes': shutil.disk_usage(ROOT).free}))


if __name__ == '__main__':
    main()
