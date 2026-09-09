#!/usr/bin/env python3
"""Pull the load-bearing quantities out of THIS lane's regenerated genre-stratified-rates.json
and print them at full precision, so each can be compared digit for digit with MORTALITY-2's
reported values. Read-only."""
import json, pathlib
d = json.loads(pathlib.Path(__file__).with_name("genre-stratified-rates.json").read_text())
def walk(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items(): yield from walk(v, f"{p}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from walk(v, f"{p}[{i}]")
    else: yield p, o
flat = dict(walk(d))
want = ["fisher", "p_two_sided", "p_one_sided", "mh_odds", "standard", "n_flag", "n_sent", "rate"]
for k, v in flat.items():
    if any(w in k.lower() for w in want): print(f"{k} = {v!r}")
