"""Deterministic replay of the root reviewer's Unicode counterexample against `_executable_source`.

Reads the fixture and the expected-at-defect output from the ROOT ORIGINAL
`unicode-comment-counterexample.json` (never retyped here), runs the census helper on it, and
reports whether the executable literal survives and whether the comment basename is erased.
Exit 0 only when the repaired behaviour holds: executable text preserved, comment text blanked.
"""
import ast
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[os.pardir] * 6))
sys.path.insert(0, os.path.join(REPO, "research", "manuscripts"))
import claim_coverage as cc  # noqa: E402

ORIG = os.path.join(HERE, "root-reviewer-originals", "unicode-comment-counterexample.json")
case = json.loads(io.open(ORIG, encoding="utf-8").read())
src = case["fixture"]
code = cc._executable_source(src, ast.parse(src))

literal = src[src.index('"') + 1:src.rindex('"')]          # the executable Unicode string literal
comment = src[src.index("#"):].rstrip("\n")                 # the comment, basename included
basename = comment.split()[-1]

print("fixture repr      :", repr(src))
print("actual repr       :", repr(code))
print("root actual_blank :", repr(case["actual_blank"]))
print("len(src)==len(code):", len(src) == len(code))
print("executable literal preserved:", literal in code)
print("comment basename erased     :", basename not in code)
print("reproduces root's defect output:", code == case["actual_blank"])

ok = len(src) == len(code) and literal in code and basename not in code
print("VERDICT:", "REPAIRED" if ok else "DEFECT REPRODUCED")
sys.exit(0 if ok else 1)
