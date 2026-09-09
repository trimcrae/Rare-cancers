#!/usr/bin/env python3
"""Recursive, order- and type-sensitive comparison of two km-risk-row-detection documents.

Written independently of IPD-SURVIVAL-2's compare_reproduced.py. It walks EVERY key of both
documents (nothing is whitelisted away except the provenance strings that are passed in on the
command line and therefore cannot match by construction), and reports:
  * missing / extra keys, in either direction,
  * value differences, with the exact JSON path,
  * type changes and list-order changes,
  * separately, the set of verdict differences.

Usage: deep_compare.py A.json B.json [--new-keys-ok k1,k2,...]
`--new-keys-ok` names keys that are ALLOWED to appear only in B (the additive-change test). Any
such key is reported in `additive_keys_seen` but is not counted as a difference; a key allowed but
absent, or any OTHER new key, is still a difference.
"""
import json, sys

# Provenance strings supplied on the command line; they describe the run, not the measurement.
CLI_PROVENANCE = {"$.inputs.page_rasters"}


def walk(a, b, path, out, new_ok, seen_new):
    if type(a) is not type(b) and not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
        out.append({"path": path, "kind": "type", "a": str(type(a)), "b": str(type(b))})
        return
    if isinstance(a, dict):
        ka, kb = list(a.keys()), list(b.keys())
        for k in ka:
            if k not in b:
                out.append({"path": f"{path}.{k}", "kind": "missing_in_b", "a": a[k]})
        for k in kb:
            if k not in a:
                if k in new_ok:
                    seen_new.append(f"{path}.{k}")
                else:
                    out.append({"path": f"{path}.{k}", "kind": "extra_in_b", "b": b[k]})
        # key ORDER over the shared keys must also be preserved
        sa = [k for k in ka if k in b]
        sb = [k for k in kb if k in a]
        if sa != sb:
            out.append({"path": path, "kind": "key_order", "a": sa, "b": sb})
        for k in ka:
            if k in b:
                walk(a[k], b[k], f"{path}.{k}", out, new_ok, seen_new)
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append({"path": path, "kind": "length", "a": len(a), "b": len(b)})
        for i in range(min(len(a), len(b))):
            walk(a[i], b[i], f"{path}[{i}]", out, new_ok, seen_new)
    else:
        if a != b:
            if path in CLI_PROVENANCE:
                out.append({"path": path, "kind": "cli_provenance_expected", "a": a, "b": b})
            else:
                out.append({"path": path, "kind": "value", "a": a, "b": b})


def verdicts(doc):
    v = {}
    for s in doc["sources"]:
        for i, f in enumerate(s["figures"]):
            # `page`+`arm` is NOT unique (chiusole2020 prints two figures per page), so the key
            # carries the figure's ordinal position within its source as well.
            v[f"{s['source_id']}|#{i}|p{f.get('page')}|{f.get('arm')}|{f.get('caption_head','')[:40]}"] = f.get("verdict")
    return v


def main():
    A, B = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
    new_ok = set()
    if len(sys.argv) > 3 and sys.argv[3] == "--new-keys-ok":
        new_ok = set(sys.argv[4].split(","))
    out, seen_new = [], []
    walk(A, B, "$", out, new_ok, seen_new)
    real = [d for d in out if d["kind"] != "cli_provenance_expected"]
    va, vb = verdicts(A), verdicts(B)
    vdiff = {k: [va.get(k), vb.get(k)] for k in set(va) | set(vb) if va.get(k) != vb.get(k)}
    res = {
        "a": sys.argv[1], "b": sys.argv[2],
        "n_field_differences": len(real),
        "field_differences": real,
        "cli_provenance_differences": [d for d in out if d["kind"] == "cli_provenance_expected"],
        "n_verdict_differences": len(vdiff),
        "verdict_differences": vdiff,
        "n_figures_compared": len(va),
        "additive_keys_allowed": sorted(new_ok),
        "additive_keys_seen": len(seen_new),
        "additive_key_paths_sample": seen_new[:5],
        "totals_a": A["_totals"], "totals_b": B["_totals"],
    }
    print(json.dumps(res, indent=2))
    return 0 if not real and not vdiff else 1


if __name__ == "__main__":
    sys.exit(main())
