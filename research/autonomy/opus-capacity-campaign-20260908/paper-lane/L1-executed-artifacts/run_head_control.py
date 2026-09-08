# Control: runs the HEAD (pre-fix) copy OUTSIDE the repo; its OUT is beside itself in /tmp.
import importlib.util, json, os
spec=importlib.util.spec_from_file_location("headfig","/tmp/claude-0/l1-lane/pre/HEAD_emc_surface_figure.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
LOCAL="/home/user/Rare-cancers/research/modalities"
m._get=lambda url: json.load(open(os.path.join(LOCAL,url.rsplit("/",1)[-1])))
m.OUT="/tmp/claude-0/l1-lane/png/HEAD_control.png"
m.main()
