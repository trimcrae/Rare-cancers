# Lane runner: executes the repo figure script with _get redirected to the
# committed local JSONs (no network). No repo file is modified by this runner.
import importlib.util, json, os, sys
SPEC_PATH = "/home/user/Rare-cancers/research/modalities/emc_surface_figure.py"
LOCAL = "/home/user/Rare-cancers/research/modalities"
spec = importlib.util.spec_from_file_location("emcfig", SPEC_PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
def _local(url):
    name = url.rsplit("/", 1)[-1]
    with open(os.path.join(LOCAL, name)) as f:
        return json.load(f)
m._get = _local
m.main()
