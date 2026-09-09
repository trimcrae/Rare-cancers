#!/usr/bin/env python3
"""Render systems/views/** into THIS LANE without touching the tracked tree.

Imports systems/systems_check.py and calls its own all_views(derive(load_graph())).
It never calls write_views(), whose VIEWS constant points at the tracked directory.
"""
import os, sys, importlib.util

REPO = "/home/user/Rare-cancers"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "regenerated")

spec = importlib.util.spec_from_file_location("systems_check", os.path.join(REPO, "systems", "systems_check.py"))
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)

g = sc.derive(sc.load_graph())
views = sc.all_views(g)
n = 0
for rel, body in views.items():
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(body)
    n += 1
print(f"rendered {n} views to {OUT}")
