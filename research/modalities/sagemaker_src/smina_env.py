"""Shared helper: isolate smina in its own conda env behind a PATH wrapper.

WHY. Since ~2026-07 on conda-forge, current **rdkit** builds require libboost >=1.86 while **smina**
requires libboost <=1.82, so smina + rdkit can no longer be solved into a SINGLE conda env (the historical
pattern in every docking entry script here). Symptom: `conda create ... smina rdkit ...` fails with an
unsatisfiable libboost conflict -> the SageMaker job dies with AlgorithmError exit 1 before doing any work.

FIX. Every entry script that needs BOTH now: (1) creates its rdkit/analysis env WITHOUT smina; (2) calls
`setup_smina_env(conda)` to build a minimal `sm` env with just smina + a /usr/local/bin/smina wrapper that
runs smina INSIDE `sm` (so it loads its own boost libs); (3) prepends /usr/local/bin to the run env PATH.
The docking code finds smina via `_which("smina")` on PATH, so this is transparent to
nr4a3_dock / nr4a3_warhead. Validated end-to-end on the matrix Gate-2 benchmark (2026-07-11).
"""
import os
import subprocess

WRAPPER_DIR = "/usr/local/bin"


def setup_smina_env(conda, env_name="sm"):
    """Create a minimal conda env with smina + a PATH wrapper that runs it there. Returns WRAPPER_DIR
    (prepend it to the run env PATH). Call AFTER creating your rdkit env (smina must NOT be in it)."""
    subprocess.run([conda, "create", "-y", "-n", env_name, "-c", "conda-forge", "smina"], check=True)
    os.makedirs(WRAPPER_DIR, exist_ok=True)
    wrapper = os.path.join(WRAPPER_DIR, "smina")
    with open(wrapper, "w") as f:
        f.write('#!/bin/bash\nexec %s run --no-capture-output -n %s smina "$@"\n' % (conda, env_name))
    os.chmod(wrapper, 0o755)
    print("[smina_env] smina isolated in env `%s`; wrapper -> %s" % (env_name, wrapper), flush=True)
    return WRAPPER_DIR


def path_with_wrapper(env=None):
    """PATH string with WRAPPER_DIR prepended (so `_which('smina')` finds the wrapper). Pass the run env
    (or None -> os.environ)."""
    base = (env or os.environ).get("PATH", "")
    return WRAPPER_DIR + os.pathsep + base if base else WRAPPER_DIR
