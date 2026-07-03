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
    cmd.remove("hydro")                       # cleaner sticks
    cmd.dss("rec")                            # assign secondary structure for the cartoon
    cmd.hide("everything")
    cmd.set("cartoon_side_chain_helper", 1)   # side-chain sticks don't fight the cartoon backbone

    # protein cartoon — soft, so the FOLD reads without competing with the ligand
    cmd.show("cartoon", "rec")
    cmd.color("teal", "rec")
    cmd.set("cartoon_transparency", 0.12, "rec")

    # the warhead — thick sticks, WARM carbons for high contrast against the teal fold (the visual focus)
    cmd.show("sticks", "lig")
    cmd.set("stick_radius", 0.27, "lig")
    cmd.color("orange", "lig and elem C")
    cmd.util.cnc("lig")

    # pocket-lining side chains within 4.5 A of the ligand — recessive grey, mark the site without competing
    cmd.select("pocket", "byres (polymer within 4.5 of lig)")
    cmd.show("sticks", "pocket and sidechain")
    cmd.set("stick_radius", 0.12, "pocket")
    cmd.color("grey80", "pocket and elem C")
    cmd.util.cnc("pocket")

    # framing: centre the warhead with enough fold context to read the LBD helical bundle (no surface — it
    # ray-traces to an opaque blob in outline mode; cartoon + sticks reads cleaner and shows the fit).
    cmd.orient("lig")
    cmd.zoom("lig", 11)
    cmd.turn("y", 25)

    # render — smooth shaded molecular look (no cel outline; that clashed with the pocket sticks)
    cmd.bg_color("white")
    cmd.set("ray_shadows", 1)
    cmd.set("ray_shadow_decay_factor", 0.15)
    cmd.set("ambient", 0.5)
    cmd.set("specular", 0.2)
    cmd.set("antialias", 2)
    cmd.set("ray_trace_mode", 0)
    cmd.ray(1800, 1350)
    cmd.png(out_png, dpi=300)
    print("wrote", out_png, file=sys.stderr)


main()
