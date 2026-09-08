"""Collect and run test_* functions in a module, supplying tmp_path and parametrize cases."""
import importlib.util
import inspect
import pathlib
import sys
import tempfile
import traceback

import pytest  # the shim

mod_path = sys.argv[1]
spec = importlib.util.spec_from_file_location("t_mod", mod_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

passed = failed = skipped = 0
fails = []
for name, fn in sorted(vars(mod).items()):
    if not name.startswith("test_") or not callable(fn):
        continue
    cases = getattr(fn, "_params", [{}])
    for i, kw in enumerate(cases):
        label = name + (f"[{i}]" if len(cases) > 1 else "")
        kw = dict(kw)
        sig = inspect.signature(fn)
        tmp = None
        if "tmp_path" in sig.parameters:
            tmp = tempfile.mkdtemp(prefix="i1-")
            kw["tmp_path"] = pathlib.Path(tmp)
        try:
            fn(**kw)
            passed += 1
            print(f"PASS {label}")
        except pytest.Skipped as e:
            skipped += 1
            print(f"SKIP {label}: {e}")
        except Exception:
            failed += 1
            fails.append((label, traceback.format_exc()))
            print(f"FAIL {label}")

print()
for label, tb in fails:
    print("=" * 70)
    print("FAILED", label)
    print(tb)
print(f"summary: {passed} passed, {failed} failed, {skipped} skipped")
sys.exit(1 if failed else 0)
