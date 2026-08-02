#!/usr/bin/env python3
"""Audit the EWSR1::NR4A3 junction model — which protein does this repo think it is drugging?

WHY THIS EXISTS
---------------
Two committed objects disagree about where NR4A3 resumes in the chimera, and nobody reconciled
them (found 2026-08-02, `manuscripts/target-route-options.md` finding 3):

  * `fusion_cofold.py`      -- EWS_CUT = 264 :: "NR4A3 resumed at res 2".  Keeps NR4A3's AF1,
                               its zinc-finger DBD, the hinge and the LBD.  Its own sibling
                               module calls this "an assumption, not a sourced breakpoint".
  * `fusion-breakpoint-neoantigens.json` -- 7 in-frame junctions derived from Ensembl exon
                               structure, whose NR4A3 resume points are residues 318 / 361 / 419.
                               Every one of those deletes the AF1 and truncates or deletes the
                               C4 zinc finger, which begins at NR4A3 **C292**.

They cannot both be right, and the repo's own cited functional evidence bears against the second
as written: the fusion binds a response element in the PPARG promoter and transactivates it
(Filion 2009, PMC4429309 -- `manuscripts/nr4a3-emc-biology-evidence.md` hypothesis 2, pillar 2),
which is a DNA-binding-domain-dependent function.

⛔ WHY IT MATTERS ENOUGH TO SPEND A CI RUN ON.  Roadmap requirement `R13` ("the modelled object is
the real biological object") has no lane, no rung and no row.  It is not merely unscheduled --
**the object is undefined**, by ~360 residues.  Which model holds decides (a) whether NR4A3's
C166 exists in the disease protein at all (the roadmap's branch 1 records it as a real residue
the LBD construct boundary removes from the design space), and (b) the position of the seam every
predicted junction neoepitope spans.

WHAT THIS DOES
--------------
It does NOT guess.  It recomputes the exon->residue map from Ensembl for the canonical NR4A3 and
EWSR1 transcripts and reports, per exon:

  1. the transcript exon **rank** (what the literature means by "NR4A3 exon 3") beside the
     **coding-exon index** (what `fusion_breakpoints.py` actually indexes with `offsets[n-2]`).
     If the first transcript exon is non-coding these differ, and every junction label in
     `fusion-breakpoint-neoantigens.json` is shifted against the literature's numbering.
  2. the first protein residue each exon encodes.
  3. whether a fusion resuming at that exon retains the zinc-finger DBD (anchored on the C4 motif,
     found in the sequence rather than assumed) and the LBD.

and then states which of the two models the exon structure is compatible with.

⛔ SCOPE.  Exon arithmetic and sequence motifs only.  This does not establish the EMC breakpoint --
that needs a primary breakpoint report, and the artifact says so.  What it CAN do is show whether
the exon-derived junction set was built with a correct resume index, which is the cheaper half of
the question and the half that is a bug if it is wrong.  No structural, binding, degradation,
activity, tolerability or clinical claim follows.

NETWORK.  Ensembl REST.  The dev sandbox 403s at CONNECT, so this runs on a GitHub Actions runner
(CLAUDE.md section 6).  Pure stdlib, no pip.

Run:  python3 research/modalities/nr4a3_exon_audit.py
Out:  research/modalities/nr4a3-exon-audit.json
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "nr4a3-exon-audit.json")
ENS = "https://rest.ensembl.org"

# The C4 zinc-finger motif that opens every nuclear-receptor DBD. Found, not assumed -- the
# AlphaFold-confidence DBD boundary in nr4a3-structure-assessment.json (261-337) is offset from
# the actual fingers, which is exactly the kind of near-miss this audit exists to avoid.
ZF_MOTIF = re.compile(r"C..C.{10,20}C..C")

# The LBD boundary as the repo already calls it (nr4a3-structure-assessment.json -> regions).
NR4A3_LBD_START = 373

# What fusion_breakpoints.py sweeps, reproduced so the audit can speak about the same objects.
EWSR1_EXON_WINDOW = range(6, 15)
NR4A3_EXON_WINDOW = range(2, 5)

CODON = {
    'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L', 'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
    'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M', 'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
    'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S', 'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
    'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T', 'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
    'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*', 'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K', 'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
    'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W', 'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
    'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R', 'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
}


def _fetch(url: str, ctype: str):
    last = None
    for i in range(4):
        try:
            req = urllib.request.Request(
                url, headers={"Content-Type": ctype, "User-Agent": "rare-cancers/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read().decode()
            return json.loads(raw) if ctype.endswith("json") else raw
        except Exception as exc:  # noqa: BLE001
            last = exc
            print(f"  retry {i + 1} {url}: {exc}", file=sys.stderr)
            time.sleep(2 ** i)
    raise RuntimeError(f"failed: {url}: {last}")


def get(url):
    return _fetch(url, "application/json")


def get_text(url):
    return _fetch(url, "text/plain")


def translate(cds: str) -> str:
    aa = []
    for i in range(0, len(cds) - 2, 3):
        c = CODON.get(cds[i:i + 3], 'X')
        if c == '*':
            break
        aa.append(c)
    return "".join(aa)


def exon_map(symbol: str):
    """Per-exon coding map for the canonical transcript, with BOTH numbering schemes."""
    look = get(f"{ENS}/lookup/symbol/homo_sapiens/{symbol}?expand=1")
    tr = next((t for t in look["Transcript"] if t.get("is_canonical") == 1), None) or look["Transcript"][0]
    strand = tr["strand"]
    exons = sorted(tr["Exon"], key=lambda e: e["start"], reverse=(strand == -1))
    trans = tr["Translation"]
    cds_lo, cds_hi = trans["start"], trans["end"]

    rows = []
    cum = 0
    coding_index = 0
    for rank, ex in enumerate(exons, start=1):
        cstart = max(ex["start"], cds_lo)
        cend = min(ex["end"], cds_hi)
        clen = max(0, cend - cstart + 1)
        row = {
            "transcript_exon_rank": rank,
            "coding_nt_in_exon": clen,
            "is_coding": bool(clen),
        }
        if clen:
            row["first_coding_nt"] = cum + 1
            row["first_protein_residue"] = cum // 3 + 1
            cum += clen
            row["cumulative_coding_nt_through_exon"] = cum
            coding_index += 1
            row["coding_exon_index_1based"] = coding_index
        rows.append(row)

    cds = get_text(f"{ENS}/sequence/id/{tr['id']}?type=cds").replace("\n", "").upper()
    protein = get_text(f"{ENS}/sequence/id/{trans['id']}?type=protein").replace("\n", "")

    offsets = [r["cumulative_coding_nt_through_exon"] for r in rows if r["is_coding"]]
    checks = {
        "offsets_sum_equals_cds_length": offsets[-1] == len(cds),
        "cds_translation_equals_ensembl_protein":
            translate(cds) == protein.replace("*", "").rstrip("X"),
        "n_transcript_exons": len(rows),
        "n_coding_exons": len(offsets),
        "first_transcript_exon_is_coding": rows[0]["is_coding"],
    }
    return {
        "symbol": symbol,
        "transcript": tr["id"],
        "translation": trans["id"],
        "strand": strand,
        "protein_length": len(protein),
        "protein": protein,
        "exons": rows,
        "coding_offsets": offsets,
        "self_checks": checks,
    }


def audit():
    nr4 = exon_map("NR4A3")
    ews = exon_map("EWSR1")

    prot = nr4["protein"]
    zf = ZF_MOTIF.search(prot)
    zf_start = zf.start() + 1 if zf else None

    coding_rows = [r for r in nr4["exons"] if r["is_coding"]]

    # --- the numbering question -----------------------------------------------------------
    # fusion_breakpoints.py resumes NR4A3 at `offsets[n - 2]` for label n, i.e. at the start of
    # the n-th CODING exon. If transcript exon 1 is non-coding, the n-th coding exon is transcript
    # exon n+1, and every junction label in the artifact is shifted by one against the literature.
    offset_shift = 0 if nr4["exons"][0]["is_coding"] else 1
    label_map = []
    for n in NR4A3_EXON_WINDOW:
        if n - 2 < 0 or n - 1 > len(coding_rows):
            continue
        resumed = coding_rows[n - 1] if n - 1 < len(coding_rows) else None
        label_map.append({
            "fusion_breakpoints_label": f"NR4A3_exon_start={n}",
            "resumes_at_coding_exon_index": n,
            "resumes_at_transcript_exon_rank": (resumed or {}).get("transcript_exon_rank"),
            "first_protein_residue": (resumed or {}).get("first_protein_residue"),
            "literature_exon_number_this_actually_is":
                ((resumed or {}).get("transcript_exon_rank")),
            "label_matches_transcript_rank":
                (resumed or {}).get("transcript_exon_rank") == n,
        })

    # --- domain retention per candidate resume point ---------------------------------------
    retention = []
    for r in coding_rows:
        first = r["first_protein_residue"]
        retention.append({
            "transcript_exon_rank": r["transcript_exon_rank"],
            "coding_exon_index": r["coding_exon_index_1based"],
            "fusion_would_start_NR4A3_at_residue": first,
            "retains_zinc_finger_DBD": (zf_start is not None and first <= zf_start),
            "retains_LBD": first <= NR4A3_LBD_START,
            "retains_C166": first <= 166,
        })
    dbd_ok = [x["transcript_exon_rank"] for x in retention if x["retains_zinc_finger_DBD"]]

    # --- verdict ----------------------------------------------------------------------------
    committed = json.load(open(os.path.join(HERE, "fusion-breakpoint-neoantigens.json")))
    committed_resumes = sorted({j["nr4_cds_nt"] // 3 + 1 for j in committed["junctions"]})

    verdict = {
        "zinc_finger_first_cysteine_residue": zf_start,
        "transcript_exons_whose_start_retains_the_DBD": dbd_ok,
        "committed_artifact_resume_residues": committed_resumes,
        "any_committed_resume_retains_the_DBD":
            any(res <= (zf_start or 0) for res in committed_resumes),
        "fusion_breakpoints_label_is_transcript_exon_rank":
            all(x["label_matches_transcript_rank"] for x in label_map) if label_map else None,
        "_how_to_read": (
            "If `any_committed_resume_retains_the_DBD` is false, then EVERY junction in "
            "fusion-breakpoint-neoantigens.json models a chimera without an intact zinc-finger "
            "DBD -- which is incompatible with the fusion transactivating the PPARG response "
            "element (Filion 2009, PMC4429309). That does NOT by itself establish the EMC "
            "breakpoint; it establishes that the exon-derived junction set cannot be the "
            "disease protein, so `fusion_cofold.py`'s model (NR4A3 from residue 2) is the only "
            "one of the two still standing -- and it is self-declared an assumption, so R13's "
            "object remains undefined until a primary breakpoint report pins it."
        ),
        "_what_this_does_not_settle": (
            "The actual EMC breakpoint. Ensembl gives the exon structure; only a primary "
            "breakpoint report gives the junction. This audit bounds which models are "
            "arithmetically possible, nothing more."
        ),
    }

    # Drop the full protein sequences from the artifact -- they have a home already
    # (nr4a-sequences-cache.json) and invariant 6 says one fact, one place.
    for g in (nr4, ews):
        g.pop("protein", None)

    return {
        "_title": "EWSR1::NR4A3 junction model audit -- exon->residue map, both numbering schemes, and which fusion model survives",
        "_owner": "research/manuscripts/target-route-options.md finding 3; roadmap requirement R13",
        "_method": (
            "Ensembl REST, canonical transcript, pure stdlib. Per-exon coding length and first "
            "encoded residue, reported under BOTH the transcript exon rank (what the literature "
            "means) and the coding-exon index (what fusion_breakpoints.py indexes). The DBD is "
            "anchored on the C4 zinc-finger motif found in the sequence, not on the "
            "AlphaFold-confidence boundary, which is offset from the actual fingers."
        ),
        "_limits": [
            "Exon arithmetic and sequence motifs only. No structure, binding, degradation, activity, tolerability or clinical claim.",
            "This does NOT establish the EMC breakpoint -- that needs a primary breakpoint report.",
            "Canonical transcript only. A different transcript would give a different exon->residue map, and EMC breakpoints are reported against specific transcripts.",
        ],
        "NR4A3": nr4,
        "EWSR1": ews,
        "coding_vs_transcript_numbering": {
            "_question": "Does fusion_breakpoints.py's `offsets[n-2]` resume at TRANSCRIPT exon n or CODING exon n?",
            "nr4a3_first_transcript_exon_is_coding": nr4["exons"][0]["is_coding"],
            "implied_label_shift_vs_transcript_rank": offset_shift,
            "label_map": label_map,
        },
        "domain_retention_by_resume_exon": retention,
        "verdict": verdict,
    }


def main():
    result = audit()
    with open(OUT, "w") as fh:
        fh.write(json.dumps(result, indent=1) + "\n")
    v = result["verdict"]
    print(f"wrote {OUT}")
    print(f"  zinc finger starts at NR4A3 residue {v['zinc_finger_first_cysteine_residue']}")
    print(f"  committed artifact resumes at residues {v['committed_artifact_resume_residues']}")
    print(f"  any committed resume retains the DBD: {v['any_committed_resume_retains_the_DBD']}")
    print(f"  label == transcript rank: {v['fusion_breakpoints_label_is_transcript_exon_rank']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
