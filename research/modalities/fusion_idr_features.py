#!/usr/bin/env python3
"""
Sequence-based LLPS / low-complexity propensity of the EWS (and TAF15) low-complexity domain
vs folded and non-prion controls — the first-party CPU step the condensate paper flagged as
deferred (it needs the protein sequence, which the dev sandbox can't fetch; run on GitHub).

WHY: the condensate route's premise is that the fusion's phase-separation capacity is supplied
by the EWS-LC prion-like domain and is ABSENT from wild-type NR4A3. AlphaFold pLDDT already
shows the EWS-LC is disordered; this adds the *compositional/charge* signatures that
distinguish an LLPS-competent prion-like LC domain from generic disorder and from folded
domains — quantified on the patient-relevant sequences.

Descriptors per domain window (all standard, sequence-only, no model fabricated):
  - SYGQ fraction (S+Y+G+Q) and aromatic fraction (F+Y+W) — pi/multivalency drivers of LC-domain LLPS
  - fraction charged (FCR), net charge per residue (NCPR), Pro/Gly fractions
  - fraction disorder-promoting residues (Dunker set: A,R,G,Q,S,P,E,K)
  - Shannon entropy of the amino-acid composition (bits; LOW = low-complexity)
  - SCD = sequence charge decoration (Sawle & Ghosh 2015): (1/N) sum_{i<j} q_i q_j sqrt(j-i)
Controls: NR4A3 LBD (folded), EWSR1 RRM (folded), NR4A3 AF1 (disordered but NOT SYGQ-prion).

INTERNET REQUIRED (UniProt). Runs on a GitHub-hosted runner; output published to
modalities-cache. Graceful: a failed fetch records status="fetch_failed" for that protein.

Output: fusion-idr-features.json
"""
import json
import math
import os
import sys
import urllib.request

OUT = os.path.join(os.path.dirname(__file__), "fusion-idr-features.json")

UNIPROT = "https://rest.uniprot.org/uniprotkb/{acc}.fasta"
POS = "KR"
NEG = "DE"
AROM = "FYW"
DISORDER_PROMOTING = set("ARGQSPEK")   # Dunker disorder-promoting set

# (label, uniprot, 1-based start, end, expected)
WINDOWS = [
    ("EWSR1_LC (prion-like TAD)", "Q01844", 1, 264, "LLPS-competent prion-like LC"),
    ("EWSR1_RRM (folded control)", "Q01844", 361, 442, "folded RNA-binding domain"),
    ("TAF15_LC (alt fusion partner)", "Q92804", 1, 205, "LLPS-competent prion-like LC"),
    ("NR4A3_AF1 (disordered, non-prion)", "Q92570", 1, 260, "disordered but not SYGQ-prion"),
    ("NR4A3_LBD (folded control)", "Q92570", 373, 626, "folded ligand-binding domain"),
    ("NR4A3_DBD (folded control)", "Q92570", 261, 337, "folded zinc-finger DBD"),
]


def fetch_seq(acc, retries=4):
    import time
    for i in range(retries):
        try:
            with urllib.request.urlopen(UNIPROT.format(acc=acc), timeout=60) as r:
                text = r.read().decode()
            return "".join(l.strip() for l in text.splitlines() if not l.startswith(">"))
        except Exception as e:  # noqa
            print(f"  retry {i+1} for {acc}: {e}", file=sys.stderr)
            time.sleep(2 ** i)
    return None


def entropy(seq):
    n = len(seq)
    if not n:
        return 0.0
    from collections import Counter
    return round(-sum((c / n) * math.log2(c / n) for c in Counter(seq).values()), 3)


def scd(seq):
    """Sawle-Ghosh sequence charge decoration."""
    q = [(+1 if a in POS else (-1 if a in NEG else 0)) for a in seq]
    idx = [i for i, qi in enumerate(q) if qi]
    if len(idx) < 2:
        return 0.0
    s = 0.0
    for a in range(len(idx)):
        for b in range(a + 1, len(idx)):
            i, j = idx[a], idx[b]
            s += q[i] * q[j] * math.sqrt(j - i)
    return round(s / len(seq), 4)


def frac(seq, chars):
    return round(sum(seq.count(c) for c in chars) / len(seq), 4) if seq else 0.0


def features(seq):
    n = len(seq)
    pos = sum(seq.count(c) for c in POS)
    neg = sum(seq.count(c) for c in NEG)
    return {
        "length": n,
        "frac_SYGQ": frac(seq, "SYGQ"),
        "frac_aromatic_FYW": frac(seq, AROM),
        "frac_charged_FCR": round((pos + neg) / n, 4) if n else 0.0,
        "net_charge_per_residue_NCPR": round((pos - neg) / n, 4) if n else 0.0,
        "frac_Pro": frac(seq, "P"),
        "frac_Gly": frac(seq, "G"),
        "frac_disorder_promoting": round(
            sum(1 for a in seq if a in DISORDER_PROMOTING) / n, 4) if n else 0.0,
        "shannon_entropy_bits": entropy(seq),    # max ~4.32 for 20 aa; low => low-complexity
        "SCD": scd(seq),
    }


def main():
    cache = {}
    out_windows = []
    for label, acc, start, end, expected in WINDOWS:
        if acc not in cache:
            cache[acc] = fetch_seq(acc)
        full = cache[acc]
        rec = {"window": label, "uniprot": acc, "range_1based": [start, end],
               "expected": expected}
        if not full or len(full) < end:
            rec["status"] = "fetch_failed" if not full else "range_out_of_bounds"
        else:
            seg = full[start - 1:end]
            rec["status"] = "ok"
            rec["features"] = features(seg)
        out_windows.append(rec)

    ok = [w for w in out_windows if w.get("status") == "ok"]
    interp = None
    if any(w["window"].startswith("EWSR1_LC") and w.get("status") == "ok" for w in out_windows):
        ews = next(w for w in out_windows if w["window"].startswith("EWSR1_LC"))
        interp = (
            "Compare EWSR1_LC vs the folded controls (RRM, NR4A3 LBD/DBD) and vs NR4A3_AF1 "
            "(disordered but non-prion). The LLPS signature is: HIGH frac_SYGQ + frac_aromatic, "
            "HIGH frac_disorder_promoting, LOW shannon_entropy (low-complexity), and low FCR. "
            "If EWSR1_LC and TAF15_LC show that signature while the folded controls do not AND "
            "NR4A3_AF1 shows disorder WITHOUT the SYGQ/aromatic prion signature, the data support "
            "the paper's claim that LLPS capacity is an EWS/TAF15-specific, fusion-emergent "
            "property absent from wild-type NR4A3.")

    result = {
        "_note": ("Sequence-based LLPS / low-complexity propensity descriptors (composition, "
                  "charge patterning, entropy). These are sequence-derived PROXIES for "
                  "phase-separation propensity, not a phase-diagram measurement — consistent "
                  "with the condensate paper's emerging-field caveats."),
        "n_windows": len(out_windows),
        "n_ok": len(ok),
        "windows": out_windows,
        "interpretation": interp,
    }
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
    print("wrote", OUT, file=sys.stderr)
    for w in out_windows:
        if w.get("status") == "ok":
            f = w["features"]
            print(f"  {w['window']:<34} SYGQ={f['frac_SYGQ']:.3f} arom={f['frac_aromatic_FYW']:.3f} "
                  f"FCR={f['frac_charged_FCR']:.3f} disP={f['frac_disorder_promoting']:.3f} "
                  f"H={f['shannon_entropy_bits']:.2f} SCD={f['SCD']}")
        else:
            print(f"  {w['window']:<34} {w['status']}")


if __name__ == "__main__":
    main()
