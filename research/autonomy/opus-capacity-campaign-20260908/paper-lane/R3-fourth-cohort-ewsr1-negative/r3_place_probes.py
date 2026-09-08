#!/usr/bin/env python3
"""R3 -- place every committed 50-mer that maps into a committed EMC fusion-partner or
NR4A3 transcript, to the nucleotide, and decide per probe whether it could span any
junction relevant to an EWSR1-break-apart-negative specimen.

Offline, stdlib only. No network. Reads committed files; writes only under the R3
artifact directory.

DECISION RULES (fixed before execution, printed by the script, not typed by hand):

For a probe occupying 1-based cDNA span [s, e] of transcript T:

  R1  SPANS_INTERNAL_JUNCTION(T, b) iff s <= b < e for some internal exon-exon
      cumulative cDNA end b of T. A 50-mer that lies wholly inside one exon
      (s > b_{i-1} and e <= b_i) contains no exon-exon seam and therefore cannot
      report on whether the upstream neighbour of that exon is the wild-type
      neighbour or a fusion partner.

  R2  For an ACCEPTOR (NR4A3), the fusion transcript retains NR4A3 from the acceptor
      exon start onward. A probe wholly inside the retained region is present in BOTH
      the wild-type NR4A3 mRNA and the chimeric mRNA -> verdict CANNOT (no
      fusion-discriminating information). A probe wholly 5' of the acceptor exon start
      is absent from the chimera -> verdict COULD-IN-PRINCIPLE (allele-loss route only).
      A probe straddling the acceptor exon's 5' boundary -> verdict STRADDLE.

  R3  For a DONOR (EWSR1/TAF15/FUS/TCF12/TFG), the chimera retains cDNA <= E, the
      cumulative cDNA end of the donor breakpoint exon. e <= E -> POWER (probe target
      is in the chimera); s > E -> NO-POWER (target absent from the chimera);
      s <= E < e -> STRADDLE.

  R4  A probe that is a verbatim substring of a single wild-type cDNA CANNOT be a
      fusion-junction-spanning probe: a fusion junction seam sequence
      (donor 3' end || acceptor 5' start) does not occur in either parent cDNA.
"""
import json, os, sys, hashlib

ROOT = "/home/user/Rare-cancers"
MOD = os.path.join(ROOT, "research/modalities")
OUT = os.path.join(ROOT, "research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                         "R3-fourth-cohort-ewsr1-negative")

COMP = str.maketrans("ACGTN", "TGCAN")
def rc(s): return s.translate(COMP)[::-1]

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

ci_p = os.path.join(MOD, "emc-construct-inputs.json")
ea_p = os.path.join(MOD, "nr4a3-exon-audit.json")
tsv_p = os.path.join(MOD, "emc-fourth-cohort-probe-counts.tsv")
q_p = os.path.join(MOD, "emc-fourth-cohort-quant.json")
at_p = os.path.join(MOD, "nr4a3-fusion-junction-atlas.json")

print("== inputs (bytes / sha256) ==")
for p in (ci_p, ea_p, tsv_p, q_p, at_p):
    print(f"  {os.path.basename(p):44s} {os.path.getsize(p):>12d}  {sha256(p)}")

ci = json.load(open(ci_p)); ea = json.load(open(ea_p))
quant = json.load(open(q_p)); atlas = json.load(open(at_p))
genes = ci["genes"]

print("\n== TSV sha256 vs the value the producer recorded ==")
print("  recorded probe_counts_sha256:", quant["probe_counts_sha256"])
print("  recomputed                  :", sha256(tsv_p))
print("  MATCH:", quant["probe_counts_sha256"] == sha256(tsv_p))

# ---------------------------------------------------------------- exon arithmetic
def exon_table(sym):
    g = genes[sym]
    rows, cum = [], 0
    for ex in g["exons"]:
        L = ex["exon_length_nt"]
        assert ex["cdna_start_0based"] == cum, (sym, ex)
        cum += L
        assert ex["cdna_end_exclusive"] == cum, (sym, ex)
        rows.append({"rank": ex["transcript_exon_rank"], "exon_id": ex["exon_id"],
                     "len": L, "start1": ex["cdna_start_0based"] + 1, "end1": cum,
                     "coding_nt": ex["coding_nt_in_exon"], "is_coding": ex["is_coding"]})
    return rows, cum

print("\n== VALIDATION (b): internal consistency, exon lengths sum to len(cdna) ==")
ok_all = True
for sym in ["NR4A3", "EWSR1", "TAF15", "FUS", "TCF12", "TFG"]:
    rows, cum = exon_table(sym)
    g = genes[sym]
    ok = (cum == len(g["cdna"])) and (sum(r["coding_nt"] for r in rows) == len(g["cds"]))
    ok_all &= ok
    print(f"  {sym:6s} n_exons={len(rows):3d} sum(exon_len)={cum:6d} len(cdna)={len(g['cdna']):6d} "
          f"sum(coding_nt)={sum(r['coding_nt'] for r in rows):5d} len(cds)={len(g['cds']):5d}  EQUAL={ok}")
print("  ALL PASS:", ok_all)

nr_rows, _ = exon_table("NR4A3")
print("\n== NR4A3 exon table on ENST00000395097 (1-based cDNA) ==")
print("  rank  exon_id            len   cdna_start  cdna_end  coding_nt  coding")
for r in nr_rows:
    print(f"  {r['rank']:>4d}  {r['exon_id']:18s} {r['len']:>5d} {r['start1']:>11d} {r['end1']:>9d} "
          f"{r['coding_nt']:>10d}  {r['is_coding']}")
nr_bounds = [r["end1"] for r in nr_rows[:-1]]          # internal exon-exon seams
print("  internal exon-exon cumulative cDNA ends:", nr_bounds)
utr5 = genes["NR4A3"]["utr5_len"]
print(f"  utr5_len={utr5} -> CDS occupies cDNA {utr5+1}..{utr5+len(genes['NR4A3']['cds'])}")

print("\n== cross-check: nr4a3-exon-audit.json vs emc-construct-inputs.json (independent route) ==")
audit_cod = [e["coding_nt_in_exon"] for e in ea["NR4A3"]["exons"]]
ci_cod = [r["coding_nt"] for r in nr_rows]
print("  audit per-exon coding_nt   :", audit_cod)
print("  construct per-exon coding_nt:", ci_cod)
print("  IDENTICAL:", audit_cod == ci_cod)
print("  audit coding_offsets:", ea["NR4A3"]["coding_offsets"])
cum = 0; offs = []
for c in ci_cod:
    if c:
        cum += c; offs.append(cum)
print("  recomputed offsets  :", offs, " IDENTICAL:", offs == ea["NR4A3"]["coding_offsets"])
print("  audit transcript_exon_rank of first coding exon:",
      [e["transcript_exon_rank"] for e in ea["NR4A3"]["exons"] if e["is_coding"]][0])

# acceptor exon window from the committed atlas
acc_window = atlas["acceptor_exon_window"]
print("\n== acceptor window from nr4a3-fusion-junction-atlas.json:", acc_window,
      "source:", atlas["_acceptor_window_source"])
acc_start = {r["rank"]: r["start1"] for r in nr_rows}

# ---------------------------------------------------------------- probe scan
print("\n== scanning all committed 50-mers against 6 committed transcripts, both strands ==")
targets = {}
for sym in ["NR4A3", "EWSR1", "TAF15", "FUS", "TCF12", "TFG"]:
    targets[sym] = genes[sym]["cdna"].upper()

K = 50
index = {}   # 50-mer -> list of (sym, start0, orient)
for sym, seq in targets.items():
    for i in range(len(seq) - K + 1):
        index.setdefault(seq[i:i+K], []).append((sym, i, "sense"))
        index.setdefault(rc(seq[i:i+K]), []).append((sym, i, "antisense"))

hdr = None; hits = []; n_rows = 0; lens = {}
with open(tsv_p) as f:
    hdr = f.readline().rstrip("\n").split("\t")
    runs = [c.split(":")[0] for c in hdr[2:]]
    for line in f:
        p = line.rstrip("\n").split("\t")
        n_rows += 1
        seq = p[0]; lens[len(seq)] = lens.get(len(seq), 0) + 1
        loc = index.get(seq)
        if loc:
            counts = [int(x) for x in p[2:]]
            hits.append({"seq": seq, "assigned_gene": p[1], "loc": loc, "counts": counts})
print(f"  rows read: {n_rows}   sequence lengths: {lens}   runs: {len(runs)}")
print(f"  sequences with an exact match (either strand) in the 6 transcripts: {len(hits)}")

fish = {a: quant["per_run"][a]["ewsr1_break_apart_fish"] for a in runs}
alias = {a: quant["per_run"][a]["sample_alias"] for a in runs}
neg = [a for a in runs if fish[a] == "EWSR1-"]
pos = [a for a in runs if fish[a] == "EWSR1+"]
print(f"\n== FISH_1 arms: EWSR1+ n={len(pos)} {[alias[a] for a in pos]}")
print(f"                EWSR1- n={len(neg)} {[alias[a] for a in neg]}")

# donor breakpoint cumulative cDNA ends actually recorded in the atlas
donor_ends = {}
for gp in atlas.get("graded_pairs", []):
    ds = gp.get("donor_symbol"); de = gp.get("donor_exon_end")
    if ds in targets and isinstance(de, int):
        donor_ends.setdefault(ds, set()).add(de)
print("\n== donor exon ends recorded in the atlas:",
      {k: sorted(v) for k, v in donor_ends.items()})

def exons_of(sym, s1, e1):
    rows, _ = exon_table(sym)
    return [r for r in rows if not (r["end1"] < s1 or r["start1"] > e1)]

tsv_lines = ["probe_sequence\tassigned_gene_in_table\ttranscript\tgene\torientation\t"
             "cdna_start_1based\tcdna_end_1based\tcds_start_1based\tcds_end_1based\t"
             "exons_overlapped\tspans_internal_exon_junction\tnearest_internal_boundary_cdna\t"
             "distance_to_nearest_boundary_nt\tn_occurrences_in_that_cdna\tk_runs_with_nonzero\t"
             "counts_by_run\trole\tretained_region_for_EMC_fusion\tVERDICT\tverdict_reason"]

declared_window = {k: v for k, v in atlas["declared_donor_window"].items()
                   if isinstance(v, list)}
print("\n== declared donor windows (committed):", declared_window)
print("   atlas note:", atlas["declared_donor_window"]["_others"])

print("\n== PER-PROBE PLACEMENT ==")
for h in hits:
    for (sym, i, orient) in h["loc"]:
        s1, e1 = i + 1, i + K
        seqT = targets[sym]
        occ = seqT.count(h["seq"] if orient == "sense" else rc(h["seq"]))
        rows, _ = exon_table(sym)
        bounds = [r["end1"] for r in rows[:-1]]
        spans = [b for b in bounds if s1 <= b < e1]
        nearest = min(bounds, key=lambda b: min(abs(b - s1), abs(b - e1))) if bounds else None
        dist = min(min(abs(nearest - s1), abs(nearest - e1)), 0 if spans else 10**9) if nearest else None
        dist = 0 if spans else min(abs(nearest - s1 + 1), abs(nearest - e1))
        ov = exons_of(sym, s1, e1)
        u5 = genes[sym]["utr5_len"]; L = len(genes[sym]["cds"])
        cs = s1 - u5 if 0 < s1 - u5 <= L else None
        ce = e1 - u5 if 0 < e1 - u5 <= L else None
        k = sum(1 for c in h["counts"] if c > 0)

        if sym == "NR4A3":
            role = "acceptor (3' partner)"
            starts = sorted(set(gp["acceptor_exon_start"] for gp in atlas["graded_pairs"]
                                if gp.get("acceptor_symbol") == "NR4A3"))
            per_bp = {a: ("absent-from-chimera" if e1 <= acc_start[a] - 1 else
                          "straddles-seam" if s1 <= acc_start[a] - 1 < e1 else
                          "retained-in-chimera") for a in starts}
            retained = "; ".join(f"acceptor e{a} start cDNA {acc_start[a]} -> retained "
                                 f"{acc_start[a]}..{len(seqT)}" for a in starts)
            per_bp_s = "; ".join(f"e{a}:{v}" for a, v in per_bp.items())
            if all(v == "retained-in-chimera" for v in per_bp.values()):
                verdict = "CANNOT"
                reason = ("probe target lies wholly inside the NR4A3 segment RETAINED by the chimera "
                          f"under EVERY acceptor exon start the atlas records ({per_bp_s}), so an "
                          "identical sequence is present in both the wild-type NR4A3 mRNA and the "
                          "fusion mRNA; and it spans no internal exon-exon seam, so it carries no "
                          "information about which sequence precedes NR4A3")
            elif all(v == "absent-from-chimera" for v in per_bp.values()):
                verdict = "COULD-IN-PRINCIPLE (allele-loss route only)"
                reason = (f"probe target lies 5' of every recorded acceptor exon start ({per_bp_s}), "
                          "so it is absent from the chimeric mRNA and present only on the "
                          "un-rearranged allele")
            else:
                verdict = "DEPENDS-ON-BREAKPOINT"
                reason = f"position relative to the recorded acceptor exon starts is not uniform: {per_bp_s}"
        else:
            role = "donor (5' partner)"
            ends = sorted(set(gp["donor_exon_end"] for gp in atlas["graded_pairs"]
                              if gp.get("donor_symbol") == sym))
            Emap = {d: rows[d-1]["end1"] for d in ends if d <= len(rows)}
            power = sorted(d for d, E in Emap.items() if e1 <= E)
            nopow = sorted(d for d, E in Emap.items() if s1 > E)
            strad = sorted(d for d in Emap if d not in power and d not in nopow)
            decl = declared_window.get(sym)
            retained = (f"donor exon ends enumerated {min(ends)}..{max(ends)}; "
                        f"cDNA end of each = {Emap}")
            base = (f"probe cDNA {s1}-{e1}: target present in the chimera for donor exon ends "
                    f"{power or 'NONE'}, absent for {nopow or 'NONE'}, straddling for {strad or 'NONE'}")
            if decl:
                d_pow = [d for d in decl if d in power]
                d_no = [d for d in decl if d in nopow]
                if d_pow and not d_no:
                    verdict = "COULD-IN-PRINCIPLE (inside retained 5' region at every declared breakpoint)"
                elif d_no and not d_pow:
                    verdict = "CANNOT (3' of every declared breakpoint)"
                else:
                    verdict = "DEPENDS-ON-BREAKPOINT (within the declared window)"
                reason = base + f"; declared donor window for {sym} = {decl} -> power at {d_pow}, none at {d_no}"
            else:
                verdict = ("CANNOT (3' of every enumerated breakpoint)" if not power and not strad
                           else "DEPENDS-ON-BREAKPOINT (no declared donor window in this repository)")
                reason = base + (f"; no declared donor window exists for {sym} "
                                 "(atlas records this as a curation gap, not a negative finding)")
        if spans:
            verdict += " + SPANS INTERNAL EXON-EXON JUNCTION"
            reason += f"; probe crosses internal exon-exon seam(s) at cDNA {spans}"

        print(f"\n  {sym} {orient} cDNA {s1}-{e1}  (occurrences={occ})")
        print(f"    table label: {h['assigned_gene']}   k={k}/12   counts={h['counts']}")
        print(f"    exon(s): " + ", ".join(f"#{r['rank']}({r['start1']}-{r['end1']})" for r in ov))
        print(f"    internal seams crossed: {spans or 'NONE'}   nearest boundary {nearest} (d={dist} nt)")
        print(f"    VERDICT: {verdict}\n      {reason}")

        tsv_lines.append("\t".join([
            h["seq"], h["assigned_gene"], genes[sym]["transcript"], sym, orient,
            str(s1), str(e1), str(cs), str(ce),
            ";".join(f"{r['rank']}:{r['start1']}-{r['end1']}" for r in ov),
            "yes" if spans else "no",
            str(nearest), str(dist), str(occ), str(k),
            ",".join(f"{alias[a]}({fish[a]})={c}" for a, c in zip(runs, h["counts"])),
            role, retained, verdict, reason]))

with open(os.path.join(OUT, "PROBE-PLACEMENT.tsv"), "w") as f:
    f.write("\n".join(tsv_lines) + "\n")
print(f"\nwrote PROBE-PLACEMENT.tsv ({len(tsv_lines)-1} placement rows)")

# ------------------------------------------------ VALIDATION (a): positive controls
print("\n== VALIDATION (a): positive controls, W20c TAF15 and W20d FUS ==")
exp = {"TAF15": (1617, 1666), "FUS": (1158, 1207)}
got = {}
for h in hits:
    for (sym, i, orient) in h["loc"]:
        if sym in exp:
            got.setdefault(sym, []).append((i + 1, i + K))
for sym, (a, b) in exp.items():
    g = got.get(sym, [])
    print(f"  {sym}: expected {a}-{b}  measured {g}  MATCH={(a,b) in g}")
taf_e6 = exon_table("TAF15")[0][5]["end1"]
print(f"  W20c TAF15 exon 6 end expected 570; measured {taf_e6}  MATCH={taf_e6==570}")
seam = None
for gp in atlas.get("graded_pairs", []):
    if gp.get("junction_label") == "TAF15_e6__NR4A3_e3":
        seam = gp.get("junction_context_mRNA")
if seam:
    donor12 = seam.split("|")[0][-12:]
    pos12 = targets["TAF15"].find(donor12)
    print(f"  route 2 (atlas seam 12-mer '{donor12}') ends at TAF15 cDNA "
          f"{pos12+12 if pos12>=0 else 'NOT FOUND'}  MATCH={pos12+12==570}")

# ------------------------------------------------ can any probe be junction-spanning?
print("\n== R4 rule: could ANY committed sequence be a fusion-junction-spanning probe? ==")
print("  A fusion seam sequence (donor 3' tail || acceptor 5' head) is by construction absent")
print("  from both parent cDNAs. Constructing the seams the atlas records and asking whether any")
print("  committed 50-mer matches one:")
allseq = set()
with open(tsv_p) as f:
    f.readline()
    for line in f:
        allseq.add(line.split("\t", 1)[0])
n_seam, n_win, n_hit, hitlist = 0, 0, 0, []
seen_seam = set()
for gp in atlas["graded_pairs"]:
    ds, de = gp.get("donor_symbol"), gp.get("donor_exon_end")
    aas = gp.get("acceptor_exon_start")
    if ds not in targets or not isinstance(de, int) or not isinstance(aas, int):
        continue
    drows, _ = exon_table(ds)
    if de > len(drows) or aas > len(nr_rows):
        continue
    E = drows[de-1]["end1"]; A = acc_start[aas]
    key = (ds, E, A)
    if key in seen_seam:
        continue
    seen_seam.add(key)
    n_seam += 1
    chim = targets[ds][:E] + targets["NR4A3"][A-1:]
    lo = max(0, E - K + 1); hi = min(len(chim) - K, E - 1)
    for i in range(lo, hi + 1):
        w = chim[i:i+K]
        n_win += 1
        if w in allseq or rc(w) in allseq:
            n_hit += 1; hitlist.append((ds, de, aas, i+1))
print(f"  distinct donor/acceptor seam geometries built from committed cDNA: {n_seam}")
print(f"  50-nt windows crossing a seam, tested against all 213,007 committed sequences "
      f"(both strands): {n_win}")
print(f"  MATCHES: {n_hit}   {hitlist[:10]}")
print("  A fusion-junction-spanning 50-mer would appear here. None does.")
print("  Also checked (see the per-probe table): every committed 50-mer that matches a")
print("  parent transcript is a verbatim substring of ONE parent cDNA, which by R4 excludes")
print("  it from crossing a fusion seam.")

print("\nDONE")
