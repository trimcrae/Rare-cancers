"""Offline campaign verification with existing dependencies; no remote calls."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

P = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(script, outputs, args=()):
    before = {str(p.relative_to(P)): sha(p) for p in outputs}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1',
               PYTHONPATH='C:/Projects/EMC-Research/.cache/python-deps')
    proc = subprocess.run([sys.executable, str(script), *args], cwd=P,
                          env=env, capture_output=True, text=True, timeout=90)
    after = {str(p.relative_to(P)): sha(p) for p in outputs}
    result = {'script': str(script.relative_to(P)), 'exit_code': proc.returncode,
              'outputs_identical': before == after, 'before': before, 'after': after}
    if proc.returncode:
        result['error_tail'] = (proc.stderr or proc.stdout)[-2000:]
    assert proc.returncode == 0, result
    assert before == after, result
    return result

def main():
    syntax = []
    for p in sorted(P.rglob('*.py')):
        ast.parse(p.read_text(encoding='utf-8-sig'), filename=str(p))
        syntax.append(str(p.relative_to(P)))
    parsed = []
    for p in sorted(P.rglob('*.json')):
        json.loads(p.read_text(encoding='utf-8-sig'))
        parsed.append(str(p.relative_to(P)))
    checks = [
        run(P/'genomics/analyze_pilot.py', [P/'genomics/results.json', P/'genomics/all_emc_samples.csv', P/'genomics/analysis_manifest.json']),
        run(P/'lead/analyze_hla.py', [P/'lead/hla-results.json']),
        run(P/'functional/analyze_ddr.py', [P/'functional/ddr-results.json']),
        run(P/'functional/verify_ddr.py', [P/'functional/verification.json']),
        run(P/'functional/analyze_mendeley.py', [P/'functional/mendeley-analysis.json']),
        run(P/'microenvironment/bcell_pilot.py', [P/'microenvironment/bcell-pilot-results.json']),
        run(P/'functional/review_micro_mapping.py', [P/'functional/microenvironment-independent-challenge.json']),
    ]
    out = {'status': 'pass', 'scope': 'Offline reproduction of saved numerical outputs, source-cell arithmetic, syntax and JSON integrity. Not a scientific novelty or publication gate.',
           'python_files_parsed': syntax, 'json_files_parsed': parsed, 'checks': checks,
           'network_retrieval_or_raw_library_streaming': False}
    (P/'VERIFICATION.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({'status': out['status'], 'scripts_reproduced': len(checks),
                      'python_parsed': len(syntax), 'json_parsed': len(parsed)}))

if __name__ == '__main__':
    main()
