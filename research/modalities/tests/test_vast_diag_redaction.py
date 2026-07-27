#!/usr/bin/env python3
"""A diagnostic that dumps an unknown-shaped provider record is a credential-exfiltration primitive.

WHAT HAPPENED (2026-07-27). `nr4a3_5aks_vast_diag` was written to dump the FULL Vast instance record, on the
reasoning that "we do not know which field carries the exit reason, so print all of them". The record embeds
the rendered `onstart` script, and `gpu_backend._vast_onstart` exports the forwarded object-store credentials
into it — so the dump printed a live AWS access key and secret, in plaintext, into a GitHub Actions log on a
PUBLIC repository. The logs were deleted and the key rotated, but neither undoes the window.

THE RULE THIS PINS: print an ALLOW-LIST. A field is emitted because it was named, never because it happened
to be present. "I don't know which field I need" is a reason to print field NAMES, not field VALUES.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "nr4a3_5aks_vast_diag.py")

fails = []


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        fails.append(msg)


src = open(SRC).read()

print("== the diagnostic must never dump a whole provider record")
check("json.dumps(i, indent=1, default=str)" not in src,
      "no full-record dump — that is what leaked the credentials")
check(re.search(r"_HIGHLIGHT\s*=", src) and "for k in _HIGHLIGHT" in src,
      "values are emitted from a named allow-list")

print("== credential-bearing fields are named and withheld")
import re as _re
_nv = _re.search(r"_NEVER_PRINT = \((.*?)\)", src, _re.S)
check(_nv is not None, "the never-print list is parseable")
_never = _re.findall(r'"([^"]+)"', _nv.group(1)) if _nv else []
for field in ("onstart", "jupyter_token", "ssh_key", "api_key", "token"):
    check(field in _never, f"{field!r} is on the never-print list")

print("== the allow-list itself carries no secret-shaped field")
hl = re.search(r"_HIGHLIGHT = \((.*?)\)", src, re.S)
check(hl is not None, "the allow-list is parseable")
if hl:
    names = re.findall(r'"([^"]+)"', hl.group(1))
    bad = [n for n in names if any(b in n.lower() for b in
                                   ("onstart", "token", "key", "secret", "env", "password", "auth"))]
    check(not bad, f"no credential-shaped name in the allow-list (found {bad})")

print("== the scan for an exit signature must not read the raw record")
check("safe_blob" in src and "json.dumps(i, default=str).lower()" not in src,
      "the oom/exit scan runs over the allow-listed fields only, not the whole record")

print()
if fails:
    print(f"FAILED {len(fails)}: {fails}")
    sys.exit(1)
print("all vast_diag redaction tests passed")
