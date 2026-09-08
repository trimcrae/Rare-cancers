import importlib.util, json, os, sys
spec = importlib.util.spec_from_file_location("emcfig", "/tmp/claude-0/k1-lane/pre/emc_surface_figure.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
LOCAL="/home/user/Rare-cancers/research/modalities"
m._get = lambda url: json.load(open(os.path.join(LOCAL, url.rsplit("/",1)[-1])))
m.OUT = sys.argv[1]
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
orig = plt.subplots
def patched(*a, **k):
    fig, ax = orig(*a, **k)
    import atexit; atexit.register(lambda: print("XLIM", ax.get_xlim(), "YLIM", ax.get_ylim(), file=sys.stderr))
    return fig, ax
plt.subplots = patched
m.main()
