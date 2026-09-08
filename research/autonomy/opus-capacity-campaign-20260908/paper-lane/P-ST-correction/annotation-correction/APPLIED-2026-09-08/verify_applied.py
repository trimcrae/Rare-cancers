#!/usr/bin/env python3
"""Independent re-verification of the applied P-ST-F03 annotation repair.

Compares the retained BEFORE bytes against the live files. Recomputes, rather than trusting, the
claim that the JSON differs in exactly three keys and the producer in exactly one string literal.
Exit 1 on any disagreement.
"""
import json, collections, hashlib, os, sys, difflib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *[os.pardir] * 7))
JP = os.path.join(ROOT, "research/modalities/gse28866-tumour-vs-normal.json")
PP = os.path.join(ROOT, "research/modalities/gse28866_tumour_vs_normal.py")
BJ = os.path.join(HERE, "BEFORE-gse28866-tumour-vs-normal.json")
BP = os.path.join(HERE, "BEFORE-gse28866_tumour_vs_normal.py")

ALLOWED_KEYS = {"_contrast", "_contrast_superseded_2026-09-08", "_annotation_correction_2026-09-08"}
fail = []


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def leaves(o, path="$"):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, f"{path}[{i}]")
    else:
        yield path, o


def ck(name, ok, detail):
    print(("PASS  " if ok else "FAIL  ") + name + "  " + detail)
    if not ok:
        fail.append(name)


# retained BEFORE bytes must still be the recorded originals
ck("V1_retained_before_json_is_the_recorded_original",
   sha(BJ) == "ac0a17bd81dd8bc2ecc3b5bb380de5ae00921ae2d32b5a9595bd1449720be407",
   "sha256=" + sha(BJ) + " bytes=" + str(os.path.getsize(BJ)))
ck("V2_retained_before_producer_is_the_recorded_original",
   sha(BP) == "6dcea81de63a4dd9ab66f39144b2ba531351efd9f1a8d51b233388456bfbdb78",
   "sha256=" + sha(BP) + " bytes=" + str(os.path.getsize(BP)))

# the live JSON still parses
try:
    after = json.loads(open(JP, "rb").read(), object_pairs_hook=collections.OrderedDict)
    ck("V3_live_json_parses", True, "one JSON document, %d top-level keys" % len(after))
except Exception as e:
    ck("V3_live_json_parses", False, repr(e)); after = None

before = json.loads(open(BJ, "rb").read(), object_pairs_hook=collections.OrderedDict)

if after is not None:
    bl, al = dict(leaves(before)), dict(leaves(after))
    added = sorted(set(al) - set(bl))
    removed = sorted(set(bl) - set(al))
    changed = sorted(k for k in set(bl) & set(al) if bl[k] != al[k])
    touched = added + removed + changed
    ck("V4_json_structural_difference_is_only_the_three_annotation_keys",
       all(t.rsplit(".", 1)[-1] in ALLOWED_KEYS and t.startswith("$.per_gene.") for t in touched)
       and not removed and len(added) == 2 and len(changed) == 1,
       "leaves before=%d after=%d added=%s removed=%s changed=%s"
       % (len(bl), len(al), added, removed, changed))
    # ALL-VALUE INVARIANCE, not a Table S6 spot check: every leaf outside those keys, both ways
    moved = [k for k in set(bl) & set(al)
             if bl[k] != al[k] and k.rsplit(".", 1)[-1] not in ALLOWED_KEYS]
    nonstr = sum(1 for k, v in bl.items() if not isinstance(v, str))
    ck("V5_every_other_leaf_value_is_identical_both_directions",
       not moved and not removed,
       "%d leaves compared (%d non-string), %d moved outside the annotation keys, %d dropped"
       % (len(bl), nonstr, len(moved), len(removed)))
    ck("V6_key_order_and_membership_preserved_outside_per_gene",
       list(before) == list(after) and
       [k for k in before["per_gene"]] == [k for k in after["per_gene"] if k not in
                                           ("_contrast_superseded_2026-09-08",
                                            "_annotation_correction_2026-09-08")],
       "top-level order identical; per_gene gained exactly the two dated keys in place")
    ck("V7_superseded_string_retained_verbatim_in_place",
       after["per_gene"]["_contrast_superseded_2026-09-08"] == before["per_gene"]["_contrast"],
       "the original annotation is still quotable inside the artifact that carried it")

# producer: exactly one contiguous hunk, and it is the _contrast literal
b = open(BP, encoding="utf-8").read().splitlines(keepends=True)
a = open(PP, encoding="utf-8").read().splitlines(keepends=True)
ops = [o for o in difflib.SequenceMatcher(None, b, a, autojunk=False).get_opcodes()
       if o[0] != "equal"]
hunk_lines = [l for o in ops for l in b[o[1]:o[2]] + a[o[3]:o[4]]]
ck("V8_producer_diff_is_one_hunk_and_only_the_contrast_literal",
   len(ops) == 1 and all(('"_contrast"' in l) or l.strip().startswith('"') for l in hunk_lines),
   "changed hunks=%d, before_lines=%d after_lines=%d, all inside the _contrast string literal=%s"
   % (len(ops), ops[0][2] - ops[0][1] if ops else 0, ops[0][4] - ops[0][3] if ops else 0,
      all(('"_contrast"' in l) or l.strip().startswith('"') for l in hunk_lines)))
import ast
try:
    ast.parse(open(PP, encoding="utf-8").read())
    ck("V9_producer_still_parses", True, "ast.parse clean; NOT executed")
except SyntaxError as e:
    ck("V9_producer_still_parses", False, repr(e))

print("\nfailed=%d" % len(fail))
sys.exit(1 if fail else 0)
