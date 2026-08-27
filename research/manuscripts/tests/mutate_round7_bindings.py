"""Mutation-test the round-7 bindings. Clone, never the working tree (paper-hardening §8b.1).

Every mutation is asserted LANDED (occurrence count + digest) BEFORE the gate's answer is read —
a mutation that never applies reports exactly what a guard that never fires reports.
"""
import hashlib, json, os, shutil, subprocess, sys, tempfile

REPO = "/home/user/Rare-cancers"
DOC = "research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md"
TEST = "research/manuscripts/tests/test_fusion_partner_prose_matches_its_artifact.py"
PYTEST = "/root/.local/share/uv/tools/pytest/bin/python3"

MUTATIONS = [
    ("M1 abstract ≈20 %",
     "an interval that **contains** the ≈20 % this document's own cited sources state",
     "an interval that **contains** the ≈21 % this document's own cited sources state"),
    ("M2 §5 bullet ≈20 %",
     "that **contains** the ≈20 % this document's own cited sources state ([4], [12])",
     "that **contains** the ≈21 % this document's own cited sources state ([4], [12])"),
    ("M3 §3.5 'both put it at about 20 %'",
     "both put it at about 20 %", "both put it at about 21 %"),
    ("M4 A30 'both give about 20 %'",
     "both give about 20 %", "both give about 21 %"),
    ("M5 A30 quote of reference [4]",
     "less frequently (about 20% of cases) to the transactivation domain of TAF15",
     "less frequently (about 21% of cases) to the transactivation domain of TAF15"),
    ("M6 A30 quote of reference [12]",
     "less frequently (approximately 20%) to TAF15",
     "less frequently (approximately 21%) to TAF15"),
    ("M7 abstract 29.2 %",
     "sits below the\n29.2 % of the single referral-centre series",
     "sits below the\n29.3 % of the single referral-centre series"),
    ("M8 §5 bullet 29.2 %",
     "sits\n  below the 29.2 % of the single referral-centre series",
     "sits\n  below the 29.3 % of the single referral-centre series"),
    ("M9 A30 referral cohort's 29.2 %",
     "the location of the referral cohort's 29.2 % within it",
     "the location of the referral cohort's 29.3 % within it"),
]


def clone():
    d = tempfile.mkdtemp(prefix="mut-", dir="/tmp/claude-0/-home-user-Rare-cancers/d7d91fcf-a4c9-5428-8bee-755ea5e0712d/scratchpad")
    dst = os.path.join(d, "repo")
    subprocess.run(["cp", "-al", REPO, dst], check=True)
    return dst


def run_guard(root):
    r = subprocess.run([PYTEST, "-m", "pytest", TEST, "-q", "--no-header"],
                       cwd=root, capture_output=True, text=True)
    if "No module named pytest" in r.stdout + r.stderr:
        raise SystemExit("HARNESS ERROR: pytest not importable — a missing runner must never read "
                         "as a test result")
    return r.returncode, (r.stdout or "")[-400:]


def main():
    root = clone()
    try:
        rc, out = run_guard(root)
        print(f"POSITIVE CONTROL (unmutated clone): rc={rc}")
        if rc != 0:
            print(out); raise SystemExit("harness red on an unmutated tree — stop")
        caught, missed = [], []
        p = os.path.join(root, DOC)
        pristine = open(p, encoding="utf-8").read()
        for name, old, new in MUTATIONS:
            n = pristine.count(old)
            if n != 1:
                missed.append(f"{name}: NOT APPLIED (anchor occurs {n}x, need exactly 1)")
                continue
            text = pristine.replace(old, new)
            tmp = p + ".mut"
            with open(tmp, "w", encoding="utf-8") as fh:
                fh.write(text)
            os.replace(tmp, p)          # breaks the shared inode
            landed = open(p, encoding="utf-8").read()
            assert landed.count(new) == 1 and landed.count(old) == 0, name
            assert hashlib.sha256(landed.encode()).hexdigest() != \
                   hashlib.sha256(pristine.encode()).hexdigest(), name
            rc, out = run_guard(root)
            (caught if rc != 0 else missed).append(name if rc != 0 else f"{name}: SURVIVED")
            with open(p + ".mut", "w", encoding="utf-8") as fh:
                fh.write(pristine)
            os.replace(p + ".mut", p)
        print(json.dumps({"mutations": len(MUTATIONS), "caught": len(caught),
                          "missed": missed}, indent=1))
        print("RESULT:", "ALL CAUGHT" if not missed else "GAPS FOUND")
    finally:
        shutil.rmtree(os.path.dirname(root), ignore_errors=True)


main()
