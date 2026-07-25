#!/usr/bin/env python3
"""
NR-V04 covalent panel — WHY does no co-fold seat celastrol at NR4A1 C551, and can it be steered there?

THE OBSERVATION THIS EXPLAINS. `nrv04_covalent_input_audit` measured prereg criterion A1 on every co-fold model
in the bucket. All 7 clean models put the celastrol electrophilic carbon **28.4-39.1 A** from NR4A1 Cys551 --
the experimentally established covalent site (Zhang et al., *Chem. Commun.* 2018, doi:10.1039/C8CC06140H,
PMID 30376017: celastrol is positioned by specific noncovalent interactions next to the C551 thiol and forms a
*reversible* covalent bond; of the six Nur77-LBD cysteines C475/C505/C534 are buried, C465/C566 partially
exposed, and **C551 highly exposed**). The spread over five independent diffusion seeds and four prefixes is
28-39 A, i.e. the miss is SYSTEMATIC, not seed noise.

TWO HYPOTHESES, and this script is the observation that discriminates them:

  H1  The TERNARY ARRANGEMENT is what pushes the warhead off-site. In the ternary co-folds the celastrol moiety
      makes more heavy-atom contacts with the E3 machinery than with its own target (measured: 40-135 vs 32-44),
      so the predictor may be draping the warhead over the VHL-NR4A1 interface. If so, a BINARY co-fold with no
      E3 present should recover the C551 site, and a pocket-steered ternary re-fold is worth paying for.
  H2  The PREDICTOR DOES NOT KNOW THIS SITE. Celastrol's engagement of the NR4A1 LBD is contested in the
      literature the repo already cites (Munoz-Tello 2020 protein-NMR footprinting finds NO direct celastrol
      binding to the NR4A LBD, while Zhang 2018 reports subnanomolar covalent engagement at C551), there is no
      deposited celastrol-NR4A1 structure, and an MSA-based predictor has no evidence for a specific
      celastrol pose. If so, the binary co-fold misses C551 too, and re-folding -- constrained or not -- cannot
      manufacture the input.

SYSTEMS (each over a seed ensemble; measurement is done afterwards, for $0, by
`nrv04_covalent_input_audit.py --prefixes <this run's prefix>`, using exactly the code that scores A1):

  binary_free      NR4A1-LBD + celastrol, UNCONSTRAINED       -> discriminates H1 from H2
  binary_pocket    the same + a Boltz `pocket` constraint on the C551 residue -> can it be steered at all, and
                   is the steered pose sterically sane?
  ternary_pocket   NR4A1-LBD + VHL/EloB/EloC + NR-V04 + the same pocket constraint -> the CANDIDATE admissible
                   input, if and only if the two binary systems say steering works

HONESTY, stated in the output and to be carried into any write-up: a pocket-constrained prediction is a
**steered** prediction. Its confidence scores do not evidence the pose -- the pose was imposed. Constraining is
the standard way to build a covalent-complex input when the site is known experimentally, but the resulting
structure is an ASSUMPTION MADE EXPLICIT, never a prediction that celastrol binds there.

Runs on a GPU box via the existing Vast co-fold lane (`nrv04_vast_launch.py` mode=cofold with
TERNARY_SCRIPT=nrv04_celastrol_site_probe.py). Prepares YAMLs and skips inference gracefully with no GPU, so CI
can validate the YAML shape for $0.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import nr4a3_ternary as t3  # noqa: E402  -- fetch_seq / lbd_seq / boltz_yaml / run_boltz / have_gpu
import nrv04_ternary as nt  # noqa: E402  -- E3 accessions, ligand SMILES loaders
from nrv04_covalent_assemble import NR4A_LBD_RESIDUES  # noqa: E402
from nrv04_covalent_panel import TARGET_COV_RESNUM  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("OUTPUT_DIR", os.path.join(HERE, "celastrol_site_out"))

# NR4A1 P22736 is 598 aa and the frozen construct is its C-terminal 254 residues, so full-length C551 is
# co-fold residue 551 - (598 - 254) = 207. Recomputed from the fetched sequence at run time and asserted to be
# a cysteine -- a hardcoded index is exactly the kind of thing that silently drifts.
POCKET_MAX_DISTANCE_A = float(os.environ.get("BOLTZ_POCKET_MAX_DIST", "6.0"))


def cov_residue_index(nr4a1_seq_full):
    """1-based residue index of C551 within the frozen LBD construct, verified to be a cysteine."""
    idx = TARGET_COV_RESNUM - (len(nr4a1_seq_full) - NR4A_LBD_RESIDUES)
    lbd = nr4a1_seq_full[-NR4A_LBD_RESIDUES:]
    if not (1 <= idx <= len(lbd)):
        raise SystemExit(f"[site-probe] C{TARGET_COV_RESNUM} falls outside the {NR4A_LBD_RESIDUES}-residue LBD "
                         f"construct of a {len(nr4a1_seq_full)}-residue NR4A1")
    if lbd[idx - 1] != "C":
        raise SystemExit(f"[site-probe] LBD residue {idx} is {lbd[idx - 1]!r}, not the expected Cys — the "
                         f"construct definition or the UniProt entry has changed; refusing to steer to the "
                         f"wrong residue")
    return idx


def yaml_with_pocket(proteins, ligand_smiles, contact_chain, contact_resid, max_distance=None):
    """Boltz-2 YAML with a `pocket` constraint tying the ligand to one residue.

    Built by appending to `t3.boltz_yaml` rather than by re-implementing it, so the protein/ligand block of a
    steered prediction is byte-identical to the unsteered lane's."""
    y = t3.boltz_yaml(proteins, ligand_smiles).rstrip("\n")
    lines = [y, "constraints:", "  - pocket:", "      binder: L",
             f"      contacts: [[{contact_chain}, {contact_resid}]]"]
    if max_distance:
        lines.append(f"      max_distance: {max_distance}")
    return "\n".join(lines) + "\n"


def build_systems(with_vbc=True):
    """(name -> (yaml_text, description)) for every probe system. Network: UniProt/AFDB sequence fetches."""
    nr4a1_full = t3.fetch_seq(nt.TARGETS["NR4A1"]["acc"])
    cov_idx = cov_residue_index(nr4a1_full)
    lbd = nr4a1_full[-NR4A_LBD_RESIDUES:]
    celastrol = (json.load(open(nt.SPEC)).get("control_ligand_negatives") or {}) \
        .get("free_celastrol", {}).get("smiles")
    if not celastrol:
        raise SystemExit("[site-probe] no free_celastrol SMILES in nrv04-ternary-benchmark.json")
    nrv04, _src = nt.load_nrv04_smiles()

    binary = [("A", lbd)]
    ternary = [("A", lbd)] + nt.e3_chains(with_vbc)
    return cov_idx, len(nr4a1_full), {
        "binary_free": (t3.boltz_yaml(binary, celastrol),
                        "NR4A1-LBD + celastrol, UNCONSTRAINED — does the predictor place the warhead at C551 "
                        "when no E3 is present? Discriminates 'the ternary arrangement pushed it off-site' "
                        "from 'the predictor does not know this site'."),
        "binary_pocket": (yaml_with_pocket(binary, celastrol, "A", cov_idx, POCKET_MAX_DISTANCE_A),
                          f"NR4A1-LBD + celastrol, STEERED to contact LBD residue {cov_idx} (= full-length "
                          f"C{TARGET_COV_RESNUM}) — can it be steered at all, and is the steered pose sane? "
                          f"A steered pose is an assumption made explicit, not a prediction."),
        "ternary_pocket": (yaml_with_pocket(ternary, nrv04, "A", cov_idx, POCKET_MAX_DISTANCE_A),
                           f"NR4A1-LBD + VHL/EloB/EloC + NR-V04, STEERED to contact LBD residue {cov_idx} — the "
                           f"CANDIDATE A1-admissible input, worth running only if the binary systems show "
                           f"steering works."),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Probe why no co-fold seats celastrol at NR4A1 C551.")
    ap.add_argument("--run", action="store_true", help="run Boltz inference (needs GPU); else prep YAMLs only")
    ap.add_argument("--systems", default=os.environ.get("PROBE_SYSTEMS", ""),
                    help="comma-sep subset (binary_free,binary_pocket,ternary_pocket); blank = all")
    ap.add_argument("--seeds", default=os.environ.get("SEEDS", "1,2,3"))
    ap.add_argument("--with-vbc", default=os.environ.get("WITH_VBC", "1"))
    ap.add_argument("--diffusion-samples", default=os.environ.get("DIFFUSION_SAMPLES", "1"))
    args = ap.parse_args(argv)

    seeds = [int(x) for x in str(args.seeds).split(",") if x.strip()]
    with_vbc = str(args.with_vbc).strip() not in ("0", "", "false", "no")
    os.makedirs(OUT_DIR, exist_ok=True)

    cov_idx, full_len, systems = build_systems(with_vbc)
    wanted = [s.strip() for s in args.systems.split(",") if s.strip()] or list(systems)
    for s in wanted:
        if s not in systems:
            raise SystemExit(f"unknown system {s!r}; known: {list(systems)}")

    out = {
        "_note": ("Root-cause probe for prereg criterion A1: every clean co-fold puts the celastrol "
                  "electrophile 28.4-39.1 A from NR4A1 C551. Measurement of these predictions is done "
                  "afterwards for $0 by nrv04_covalent_input_audit.py, with the same code that scores A1."),
        "_honesty": ("A pocket-constrained prediction is STEERED. Its confidence scores do not evidence the "
                     "pose — the pose was imposed. This builds an input from an experimentally established "
                     "site; it never claims the predictor found that site."),
        "covalent_site": {"fulllen_resnum": TARGET_COV_RESNUM, "lbd_resnum": cov_idx,
                          "nr4a1_full_len": full_len, "construct": f"C-terminal {NR4A_LBD_RESIDUES} residues",
                          "reference": "Zhang et al., Chem. Commun. 2018, doi:10.1039/C8CC06140H (PMID 30376017)"},
        "pocket_max_distance_A": POCKET_MAX_DISTANCE_A,
        "seeds": seeds, "with_vbc": with_vbc, "systems": {}, "status": {},
    }
    for name in wanted:
        y, desc = systems[name]
        path = os.path.join(OUT_DIR, f"{name}.yaml")
        open(path, "w").write(y)
        out["systems"][name] = {"yaml": f"{name}.yaml", "description": desc,
                                "constrained": "pocket" in y}
    json.dump(out, open(os.path.join(OUT_DIR, "celastrol-site-probe-prep.json"), "w"), indent=2)
    print(json.dumps(out, indent=2), flush=True)

    if args.run:
        for name in wanted:                        # cheapest (binary) first; continuous upload keeps partials
            out["status"][name] = nt.run_ensemble(os.path.join(OUT_DIR, f"{name}.yaml"),
                                                  os.path.join(OUT_DIR, name), seeds,
                                                  int(args.diffusion_samples))
            json.dump(out, open(os.path.join(OUT_DIR, "celastrol-site-probe-prep.json"), "w"), indent=2)
        failed = [(k, v) for k, st in out["status"].items() for v in st.values()
                  if v not in (0, None, "resumed")]
        if failed:
            raise SystemExit(f"Boltz inference FAILED: {failed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
