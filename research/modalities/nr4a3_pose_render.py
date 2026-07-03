#!/usr/bin/env python3
"""
Publication render of the warhead pose in the NR4A3 LBD — the "how the degrader fits" figure (PyMOL, headless).

HONEST SCOPE (put in the caption): this is a **screening-grade DOCKED pose** of the de-novo warhead
`denovo_401` in an **AF2-derived, metadynamics-opened NR4A3 LBD model** — a computational model, NOT an
experimental complex. It illustrates the predicted fit (shape complementarity, pocket burial), not a measured
binding mode.

Renders: protein as cartoon, the ligand as element-coloured sticks, the pocket-lining residues (side chains
within 5 Å of the ligand) as thin sticks, and a translucent surface over those pocket residues so the ligand
reads as buried in its cavity. Ray-traced, white background.

Run headless:  pymol -cq nr4a3_pose_render.py -- <receptor.pdb> <docked.sdf> <lig_name> <out.png>
"""
import sys


def _extract_ligand(sdf, name, out):
    """Pull the single named record out of a multi-molecule docked SDF (title == name) into its own SDF."""
    recs, cur = [], []
    for line in open(sdf):
        cur.append(line)
        if line.strip() == "$$$$":
            recs.append("".join(cur))
            cur = []
    for block in recs:
        if block.splitlines()[0].strip() == name:
            open(out, "w").write(block if block.endswith("\n") else block + "\n")
            return out
    have = [b.splitlines()[0].strip() for b in recs][:8]
    raise SystemExit(f"ligand '{name}' not in {sdf} (have: {have})")


def main():
    from pymol import cmd
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    rec_pdb, docked_sdf, lig_name, out_png = args[:4]
    lig_sdf = "/tmp/lig_pose.sdf"
    _extract_ligand(docked_sdf, lig_name, lig_sdf)

    cmd.load(rec_pdb, "rec")
    cmd.load(lig_sdf, "lig")
    cmd.remove("solvent")
    cmd.remove("hydro")                       # cleaner sticks; cartoon/surface don't need H
    cmd.dss("rec")                            # assign secondary structure for the cartoon
    cmd.hide("everything")

    # protein cartoon (soft, recessive)
    cmd.show("cartoon", "rec")
    cmd.color("grey70", "rec")
    cmd.set("cartoon_transparency", 0.15, "rec")

    # ligand — element-coloured sticks, carbons a clear accent
    cmd.show("sticks", "lig")
    cmd.set("stick_radius", 0.22, "lig")
    cmd.color("marine", "lig and elem C")
    cmd.util.cnc("lig")

    # pocket-lining side chains within 5 A of the ligand
    cmd.select("pocket", "byres (polymer within 5 of lig)")
    cmd.show("sticks", "pocket and (sidechain or name CA)")
    cmd.set("stick_radius", 0.13, "pocket")
    cmd.color("wheat", "pocket and elem C")
    cmd.util.cnc("pocket")

    # translucent cavity surface over the pocket → ligand reads as buried
    cmd.set("surface_quality", 1)
    cmd.show("surface", "pocket")
    cmd.set("transparency", 0.55, "pocket")
    cmd.set("surface_color", "grey80", "pocket")

    # framing
    cmd.orient("lig")
    cmd.zoom("lig", 7)
    cmd.turn("y", 20)
    cmd.turn("x", -8)

    # render
    cmd.bg_color("white")
    cmd.set("ray_shadows", 1)
    cmd.set("ray_shadow_decay_factor", 0.1)
    cmd.set("ambient", 0.45)
    cmd.set("specular", 0.25)
    cmd.set("antialias", 2)
    cmd.set("ray_trace_mode", 1)              # subtle black outlines (publication look)
    cmd.set("ray_trace_color", "grey30")
    cmd.ray(1800, 1350)
    cmd.png(out_png, dpi=300)
    print("wrote", out_png, file=sys.stderr)


main()
