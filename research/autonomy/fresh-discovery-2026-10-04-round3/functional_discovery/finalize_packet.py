"""Bind source reuse, independent challenge and final packet without git mutation."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[3]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, obj):
    (ROOT/name).write_text(json.dumps(obj, indent=2), encoding="utf8")

prior = [
    ROOT.parents[1]/"fresh-discovery-2026-10-04"/"functional"/"COVERAGE.txt",
    ROOT.parents[1]/"fresh-discovery-2026-10-04"/"functional"/"RESULTS.txt",
    ROOT.parents[1]/"fresh-discovery-2026-10-04"/"functional"/"reused-Bangerter-all40-measured-ordinal-and-complete-source-overlap-final.json",
    Path("C:/Projects/EMC-Research/research/autonomy/discovery-2026-10-03/ROUND2-SOURCE-AUDIT.txt"),
]
save("reused-evidence-receipts.json", [{"path": str(p), "sha256": sha(p), "bytes": p.stat().st_size} for p in prior])
reviewed = {
    "panPDO-all220-identity-rows.json": "22e69cd7d26e9de5ad705cae6282f30a095e6e7ca2620086903d54e52d3f4b18",
    "panPDO2026-supp-pages.json": "a34ba37a20cd84a4f778816cd83640a568274086bbc709a5ec4313211c15c1ba",
    "ncc2015-pages.json": "6bad5c76ace668708dd8447b252e3d6917c59f65c9d61a356a6264712f66c0c7",
}
for name, expected in reviewed.items():
    assert sha(ROOT/name) == expected, name
save("independent-review.json", {
    "reviewer": "/root/genomic_clinical", "date": "2026-10-04", "source": "Delivered collaboration message after reading original retained data; no new retrieval requested",
    "bound_sources": reviewed,
    "conclusion": "Scoped shelving supported; no eligible new EMC functional measurement identified.",
    "checks": [
        "All 220 panPDO rows have no EMC aliases; 215 is literal ID labels, not donors.",
        "Ten missing OncoTree codes mostly benign/normal plus WCM2968 invasive ductal carcinoma, not hidden annotated EMC; three CUP rows remain unresolved.",
        "NCC2015 p159 names EMC among29 transplantation attempts and9 aggregate successes; p160 gives no EMC-specific establishment or drug measurement.",
        "Generic chondrosarcoma/NOS culture rows cannot establish absence or presence of EMC without a crosswalk."
    ]})
head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=WORKTREE, text=True).strip()
free = shutil.disk_usage(ROOT).free
assert free >= 10*1024**3
save("EXECUTION.json", {"date_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "worker_head": head,
    "commits_created": 0, "pushed": False, "integration": "Uncommitted worker packet; parent owns verification/integration",
    "owned_running_processes": [], "free_bytes": free, "retained_limit_bytes": 10*1024**2,
    "executed_persisted_scripts": ["fetch_primary.py", "evaluate_eligibility.py", "fetch_scoped_pdf_text.py NCC", "finalize_packet.py"],
    "additional_execution": "Inline source retrieval/parsing commands with retained receipts; panPDO reproduction option not rerun"})
files = [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha(p)} for p in sorted(ROOT.iterdir()) if p.is_file() and p.name != "MANIFEST.json"]
total = sum(p['bytes'] for p in files)
assert total < 10*1024**2
save("MANIFEST.json", {"files": files, "listed_file_count": len(files), "listed_bytes": total, "manifest_excluded_from_own_hash": True})
print(json.dumps({"files_including_manifest": len(files)+1, "bytes_including_manifest": total+(ROOT/'MANIFEST.json').stat().st_size,
                  "manifest_sha256": sha(ROOT/'MANIFEST.json'), "head": head, "free_bytes": free}))
