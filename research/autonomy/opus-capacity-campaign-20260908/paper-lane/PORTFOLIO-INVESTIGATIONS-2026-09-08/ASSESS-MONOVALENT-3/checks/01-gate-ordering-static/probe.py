"""Static ordering probe: does GATE A really complete before ANY experimental chain is read?
Read-only on the lane's script. Reports line numbers of the load-bearing statements."""
import re
P = ("/home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
     "PORTFOLIO-INVESTIGATIONS-2026-09-08/MONOVALENT-3/cutoff_sweep_closure.py")
src = open(P).read().splitlines()
pats = {
 "CRYSTALS dict defined":        r"^CRYSTALS\s*=",
 "read_text() def":              r"^def read_text",
 "GATE A banner":                r"# GATE A",
 "GATE A reach_one_frame(model)":r"r_m = LCR\.reach_one_frame",
 "GATE A mismatch loop":         r"for c in committed_cells:",
 "GATE A return 2":              r"^\s+return 2$",
 "GATE B banner":                r"# GATE B",
 "GATE B expected const":        r"^GATE_B_EXPECTED",
 "GATE B comparison":            r"gate_b_ok = ",
 "GATE B return 3":              r"^\s+return 3$",
 "FIRST experimental read (read_text on CRYSTALS)": r"text = read_text\(path\)",
 "experimental parse_chain call": r"residues, atoms = parse_chain\(text, ch\)",
 "experimental reach_one_frame":  r"r = LCR\.reach_one_frame\(moved, placements",
}
for name, p in pats.items():
    hits = [i+1 for i, l in enumerate(src) if re.search(p, l)]
    print("%-50s %s" % (name, hits))
print()
# any read of the crystal files anywhere before the gate returns?
first_exp = min(i+1 for i,l in enumerate(src) if "text = read_text(path)" in l)
gate_b_ret = max(i+1 for i,l in enumerate(src) if l.strip()=="return 3")
print("first experimental structure read at line %d; GATE B hard-exit at line %d" % (first_exp, gate_b_ret))
print("ORDERING OK (gates strictly precede any experimental read):", gate_b_ret < first_exp)
# does anything in the gate-A block touch CRYSTALS?
ga = src[[i for i,l in enumerate(src) if "# GATE A" in l][0]: first_exp-1]
print("CRYSTALS referenced between GATE A banner and first experimental read:",
      [i for i,l in enumerate(ga) if "CRYSTALS" in l])
