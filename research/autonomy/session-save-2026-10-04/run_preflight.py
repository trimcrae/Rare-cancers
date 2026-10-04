"""Normal integration check, reusing installed tools without copying caches."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

packet = Path(__file__).resolve().parent
root = packet.parents[2]
tools_root = Path('C:/Projects/EMC-Research')
runtime = Path('C:/Users/mcrae/.cache/codex-runtimes/codex-primary-runtime/dependencies')
env = dict(os.environ)
env.update(PYTHONHOME=str(runtime / 'python'), PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1',
           PYTHONPATH=str(tools_root / '.cache/python-deps'), PIP_NO_INDEX='1',
           PIP_DISABLE_PIP_VERSION_CHECK='1', MPLCONFIGDIR=str(tools_root / '.cache/matplotlib'))
env['PATH'] = os.pathsep.join([str(tools_root / '.cache/full-preflight-runtime/bin'),
                            str(tools_root / '.cache/python-deps/bin'), str(runtime / 'python'),
                            str(runtime / 'native/git/usr/bin'), str(runtime / 'node/bin'), env['PATH']])
for key in ('PREFLIGHT_FULL', 'PREFLIGHT_TESTS', 'PREFLIGHT_MODALITIES', 'PREFLIGHT_PAPER', 'SKIP_TESTS'):
    env.pop(key, None)
label = sys.argv[1] if len(sys.argv) > 1 else "normal-preflight"
started = time.monotonic()
with (packet / (label + '.log')).open('x', encoding='utf-8') as output:
    result = subprocess.run([str(tools_root / '.cache/full-preflight-runtime/bin/bash.exe'),
                             'scripts/preflight.sh'], cwd=root, env=env, stdout=output,
                            stderr=subprocess.STDOUT, timeout=300)
receipt = {'exit_code': result.returncode, 'seconds': time.monotonic() - started,
           'mode': 'normal', 'base_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
           'scope': 'Normal file/code integration preflight, no UI or publication clearance. Existing native runtime and dependency paths reused.'}
(packet / (label + '-receipt.json')).write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
