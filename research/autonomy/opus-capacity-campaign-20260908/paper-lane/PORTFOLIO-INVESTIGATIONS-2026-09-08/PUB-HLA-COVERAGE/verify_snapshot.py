#!/usr/bin/env python3
"""PUB-HLA-COVERAGE lane, 2026-09-08/09.

Question: can the AFND snapshot behind the FROZEN hla-coverage.json be identified post hoc,
and does the live mirror still reproduce the frozen pooled frequencies bit for bit?

Reads nothing from and writes nothing to research/modalities. Writes one JSON to this directory.
"""
import hashlib, json, os, subprocess, sys

REPO = "/home/user/Rare-cancers"
HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = sys.argv[1]
sys.path.insert(0, os.path.join(REPO, "research/modalities"))
import hla_coverage as HC  # noqa: E402

ALLELES = ["HLA-A*01:01", "HLA-B*07:02", "HLA-B*15:01", "DRB1*14:01"]
out = {"_question": "Is the frozen coverage build's upstream AFND snapshot identifiable, and does "
                    "the live mirror still reproduce it?",
       "_run_utc": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True,
                                  text=True).stdout.strip()}

# 1. mirror history (blobless clone made in the checks log)
mirror = os.path.join(SCRATCH, "afnd-mirror")
def git(*a):
    return subprocess.run(["git", "-C", mirror] + list(a), capture_output=True, text=True).stdout.strip()
out["mirror_history"] = {
    "repo": "https://github.com/slowkow/allelefrequencies",
    "afnd_tsv_commits": [l for l in git("log", "--format=%H %cI %s", "--", "afnd.tsv").splitlines()],
    "head": git("rev-parse", "HEAD"),
    "head_date": git("log", "-1", "--format=%cI"),
    "afnd_tsv_blob_at_head": git("rev-parse", "HEAD:afnd.tsv"),
}

# 2. live file hash
live = os.path.join(SCRATCH, "afnd-live.tsv")
b = open(live, "rb").read()
out["live_file"] = {"url": HC.AFND_TSV_URL, "bytes": len(b),
                    "sha256": hashlib.sha256(b).hexdigest(),
                    "git_blob_sha1": hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()}
out["live_file"]["matches_blob_at_head"] = (
    out["live_file"]["git_blob_sha1"] == out["mirror_history"]["afnd_tsv_blob_at_head"])

# 3. re-pool today, live, through the paper's own producer functions
iso = HC.fetch(HC.ISO_JSON_URL)
resolve = HC.build_region_resolver(iso)
ginfo, racc, ok, unassigned = HC.load_afnd(ALLELES, resolve)
out["recomputed"] = {"source_ok": ok, "unassigned": unassigned, "global": ginfo}

frozen = json.load(open(os.path.join(REPO, "research/modalities/hla-coverage.json")))
fg = frozen["global"]["allele_frequencies"]
cmp = {}
for a in ALLELES:
    f, r = fg.get(a), ginfo.get(a)
    cmp[a] = {"frozen": f, "recomputed": r,
              "identical": f == r,
              "fields_differing": sorted(k for k in set(f) | set(r) if f.get(k) != r.get(k))}
out["comparison_global"] = cmp
out["all_global_identical"] = all(v["identical"] for v in cmp.values())

# 4. regional per-allele frequencies, same comparison
reg_diff = {}
for region, fr in frozen["regions"].items():
    got = racc.get(region, {})
    for a, fv in (fr.get("allele_frequencies") or {}).items():
        acc = got.get(a.replace("HLA-", ""))
        info = HC._af_info_from_acc(acc) if acc else None
        if fv is None or info is None:
            # a null leaf is UNKNOWN, never 0; agreement means BOTH are null
            same = (fv is None and info is None)
        else:
            same = abs(info["allele_frequency"] - fv["allele_frequency"]) < 5e-5
        if not same:
            reg_diff.setdefault(region, {})[a] = {"frozen": fv, "recomputed": info}
out["regional_mismatches"] = reg_diff
out["regional_all_match"] = not reg_diff
json.dump(out, open(os.path.join(HERE, "snapshot-identification.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in ("mirror_history", "live_file", "all_global_identical",
                                      "regional_all_match", "recomputed")}, indent=1)[:4000])
