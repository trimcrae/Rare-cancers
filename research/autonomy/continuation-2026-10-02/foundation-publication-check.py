"""Artifact-only preparation/FULL validation; never pushes or publishes."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

ROOT = Path.cwd()
OUT = Path('/tmp/foundation-publication')
OUT.mkdir(exist_ok=True)
TOKEN = ROOT / 'research/autonomy/continuation-2026-10-02/foundation-publication-token.json'
MODE = json.loads(TOKEN.read_text())['mode']
assert MODE in {'prepare', 'render', 'full', 'evaluate'}
SHA = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
RECEIPT = {'revision': SHA, 'run_id': os.environ['GITHUB_RUN_ID'], 'mode': MODE, 'steps': []}

def restricted():
    return 6 <= dt.datetime.now(ZoneInfo('America/New_York')).hour < 10

def run(name, command, seconds=600, guarded=False, extra_env=None, pinned=False):
    if guarded and restricted():
        raise RuntimeError('Daily06-10America/New_York restriction: ' + name)
    assert shutil.disk_usage(ROOT).free >= 10.5*1024**3
    log = OUT / (name + '.log')
    start = time.monotonic()
    env = os.environ.copy()
    env.pop('PREFLIGHT_PAPER', None)
    env.pop('SKIP_TESTS', None)
    env.update(extra_env or {})
    forced = None
    with log.open('w') as stream:
        if pinned:
            stream.write('PINNED_SHA=' + SHA + '\n')
            stream.flush()
        p = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT,
                             start_new_session=True, env=env)
        while p.poll() is None:
            if shutil.disk_usage(ROOT).free < 10.5*1024**3:
                forced = 'storage reserve'
            elif time.monotonic()-start > seconds:
                forced = 'time budget'
            elif guarded and restricted():
                forced = 'daily computer-use restriction'
            if forced:
                os.killpg(p.pid, signal.SIGTERM)
                try:
                    p.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(p.pid, signal.SIGKILL)
                    p.wait()
                break
            time.sleep(1)
        code = 124 if forced else p.returncode
        if pinned:
            stream.write('EXIT=' + str(code) + '\n')
    RECEIPT['steps'].append({'name': name, 'command': command, 'exit_code': code,
                            'forced_stop': forced, 'elapsed_seconds': time.monotonic()-start,
                            'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest()})
    print(name, 'exit', code, 'last lines:', '\n'.join(log.read_text(errors='replace').splitlines()[-15:]))
    return code

def keep(path):
    src = ROOT / path
    if src.is_file():
        dest = OUT / 'files' / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

result = 1
try:
    assert run('base-dependencies', [sys.executable, '-m', 'pip', 'install', '--no-cache-dir',
               'pyyaml', 'jsonschema>=4.18', 'referencing', 'pypdf', 'pdfplumber', 'uv'], 300) == 0
    if MODE in {'prepare', 'render'}:
        if MODE == 'prepare':
            assert run('extend-derived-ids', [sys.executable, 'research/autonomy/derived_ids.py', '--extend']) == 0
            assert run('derive-views', [sys.executable, 'systems/systems_check.py', '--write-views']) == 0
            changed = subprocess.check_output(['git', 'diff', '--name-only'], text=True).splitlines()
            changed += subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], text=True).splitlines()
            for path in changed:
                assert path.startswith('systems/views/') or path == 'research/autonomy/derived-ledger-ids.json', path
                keep(path)
            assert run('check-systems', [sys.executable, 'systems/systems_check.py', '--check']) == 0
            assert run('check-derived-ids', [sys.executable, 'research/autonomy/derived_ids.py', '--check']) == 0
        assert run('render-manuscript', [sys.executable, 'research/manuscripts/build_submission_pdf.py',
                   '--paper', 'foundation-identity', '--style', 'preprint'], 300, guarded=True) == 0
        for path in (ROOT / 'research/manuscripts/foundation').glob('*'):
            if path.suffix != '.md':
                keep(str(path.relative_to(ROOT)))
        pdf = ROOT / 'research/manuscripts/foundation/source-identity-correspondence-preprint.pdf'
        extract = ('from pathlib import Path; from pypdf import PdfReader; '
                   'pages=PdfReader('+repr(str(pdf))+').pages; '
                   'Path('+repr(str(OUT/'rendered-text.txt'))+').write_text("\\n\\n".join(p.extract_text() for p in pages)); '
                   'print("PDF_PAGES="+str(len(pages)))')
        assert run('extract-rendered-text', [sys.executable, '-c', extract], 90) == 0
    elif MODE == 'full':
        assert run('development-dependencies', ['bash', 'scripts/dev-setup.sh', '--if-needed'], 900, guarded=True) == 0
        assert subprocess.check_output(['git', 'status', '--porcelain'], text=True).strip() == ''
        result = run('preflight-full', ['bash', 'scripts/preflight.sh'], 3600, guarded=True,
                     extra_env={'PREFLIGHT_FULL': '1'}, pinned=True)
        recorder = run('derive-full-receipt', [sys.executable, 'research/autonomy/record_bar_evidence.py',
                       'preflight', '--sha', SHA, '--log', str(OUT/'preflight-full.log')])
        keep('research/autonomy/preflight-logs/' + SHA + '.log')
        keep('research/autonomy/preflight-receipts/' + SHA + '.json')
        keep('scripts/selector-validation.json')
        assert result == 0 and recorder == 0
    else:
        # Evaluation is performed on the exact current content pin; no main-writing helper.
        candidate = json.loads(TOKEN.read_text())['candidate_sha']
        result = run('publish-bar', [sys.executable, 'research/autonomy/publish_bar.py',
                     '--paper', 'PUB-FOUNDATION-IDENTITY', '--sha', candidate,
                     '--venue', 'journal', '--act', 'submit', '--json'], 600)
        # A nonzero journal-authority result is retained, never rewritten as permission.
        RECEIPT['publication_permission_not_granted'] = True
    if MODE != 'evaluate':
        result = 0
except Exception as exc:
    RECEIPT['exception'] = type(exc).__name__ + ': ' + str(exc)
    result = 1
finally:
    RECEIPT['exit_code'] = result
    RECEIPT['finished_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    RECEIPT['free_bytes_after'] = shutil.disk_usage(ROOT).free
    RECEIPT['files'] = [{'path': str(p.relative_to(OUT)), 'bytes': p.stat().st_size,
                         'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                        for p in sorted((OUT/'files').rglob('*')) if p.is_file()]
    (OUT/'receipt.json').write_text(json.dumps(RECEIPT, indent=2)+'\n')
    print(json.dumps(RECEIPT, indent=2))
sys.exit(result)
