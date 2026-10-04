"""One normal repository gate using the already-installed native runtime."""
import json,os,subprocess,time
from pathlib import Path
base=Path(__file__).resolve().parent
root=base.parents[2]
runtime=Path('C:/Users/mcrae/.cache/codex-runtimes/codex-primary-runtime/dependencies')
env=dict(os.environ)
env.update(PYTHONHOME=str(runtime/'python'),PYTHONUTF8='1',PYTHONPATH=str(root/'.cache/python-deps'),PIP_NO_INDEX='1',PIP_DISABLE_PIP_VERSION_CHECK='1',MPLCONFIGDIR=str(root/'.cache/matplotlib'))
env['PATH']=os.pathsep.join([str(root/'.cache/full-preflight-runtime/bin'),str(root/'.cache/python-deps/bin'),str(runtime/'python'),str(runtime/'native/git/usr/bin'),str(runtime/'node/bin'),env['PATH']])
for k in ('PREFLIGHT_FULL','PREFLIGHT_TESTS','PREFLIGHT_MODALITIES','PREFLIGHT_PAPER','SKIP_TESTS'):env.pop(k,None)
t=time.monotonic()
with (base/'normal-preflight.log').open('x',encoding='utf-8') as f:
    r=subprocess.run([str(root/'.cache/full-preflight-runtime/bin/bash.exe'),'scripts/preflight.sh'],cwd=root,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
receipt={'mode':'normal','exit_code':r.returncode,'seconds':time.monotonic()-t,'scope':'Normal repository gates only; no publication clearance, no full scientific suites','base_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()}
(base/'normal-preflight-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
