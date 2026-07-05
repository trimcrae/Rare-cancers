import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import nr4a3_abfe as abfe  # noqa: E402


def test_lambda_schedule_shape_and_endpoints():
    sched = abfe.lambda_schedule()
    assert len(sched) == abfe.N_WINDOWS
    assert sched[0] == (1.0, 1.0)          # fully coupled
    assert sched[-1] == (0.0, 0.0)         # fully decoupled
    # electrostatics must reach 0 before sterics start turning off (decouple elec first)
    elec = [e for e, s in sched]
    first_sterics_off = next(i for i, (e, s) in enumerate(sched) if s < 1.0)
    assert elec[first_sterics_off] == 0.0, "sterics began before elec fully off"


def test_assemble_ukn_square_and_counts():
    # 3 states, samples: 2 from state0, 1 from state1, 3 from state2; each sample has 3 energies (u at each λ)
    we = [
        [[0.0, 1.0, 2.0], [0.1, 1.1, 2.1]],
        [[3.0, 0.0, 3.0]],
        [[4.0, 4.0, 0.0], [4.1, 4.1, 0.1], [4.2, 4.2, 0.2]],
    ]
    u_kn, N_k = abfe.assemble_ukn(we)
    assert N_k == [2, 1, 3]
    assert len(u_kn) == 3 and all(len(row) == 6 for row in u_kn)   # 3 states × 6 total samples
    # column 0 = first sample of window 0 → its energies at states [0,1,2] = [0.0,1.0,2.0]
    assert [u_kn[j][0] for j in range(3)] == [0.0, 1.0, 2.0]
    # last column = 3rd sample of window 2 → [4.2,4.2,0.2]
    assert [u_kn[j][5] for j in range(3)] == [4.2, 4.2, 0.2]


def test_assemble_ukn_rejects_wrong_width():
    we = [[[0.0, 1.0]]]                     # 1 window but sample has 2 energies (expected 1)
    try:
        abfe.assemble_ukn(we)
        assert False, "should have raised on mismatched sample width"
    except ValueError:
        pass


def test_append_reduced_potentials_writes_jsonl():
    import json
    d = tempfile.mkdtemp()
    abfe.append_reduced_potentials(d, 3, 0, [0.0, 1.0, 2.0])
    abfe.append_reduced_potentials(d, 3, 1, [0.1, 1.1, 2.1])
    p = os.path.join(d, "window_03.jsonl")
    lines = [json.loads(l) for l in open(p)]
    assert len(lines) == 2
    assert lines[0]["w"] == 3 and lines[0]["iter"] == 0 and lines[0]["u"] == [0.0, 1.0, 2.0]
    assert lines[1]["iter"] == 1


def test_boresch_ssc_reference_value():
    # Independently hand-computed (Boresch 2003 eq.32) reference: r0=5 Å, both anchor angles = 90°
    # (sin=1), K_r=10 kcal/mol/Å², all five angular K=100 kcal/mol/rad², T=300 K.
    #   RT=0.59616123; num=8π²·1660.5395·√(10·100^5); den=25·(2π·RT)^3  →  ΔG° = -10.294 kcal/mol
    import math
    dg = abfe.boresch_standard_state_correction(
        r0_A=5.0, thetaA0_rad=math.pi / 2, thetaB0_rad=math.pi / 2,
        K_r=10.0, K_thetaA=100.0, K_thetaB=100.0, K_phiA=100.0, K_phiB=100.0, K_phiC=100.0,
        temperature_K=300.0)
    assert abs(dg - (-10.294060536)) < 1e-4, dg


def test_boresch_ssc_stronger_restraint_more_negative():
    # A tighter restraint (larger force constants, smaller r0) confines the ligand more → the free-energy
    # cost of releasing it to the standard-state volume is larger, so ΔG° must become MORE negative.
    import math
    base = dict(thetaA0_rad=math.pi / 2, thetaB0_rad=math.pi / 2, temperature_K=300.0)
    loose = abfe.boresch_standard_state_correction(
        r0_A=5.0, K_r=10.0, K_thetaA=100.0, K_thetaB=100.0,
        K_phiA=100.0, K_phiB=100.0, K_phiC=100.0, **base)
    tight = abfe.boresch_standard_state_correction(
        r0_A=2.5, K_r=40.0, K_thetaA=400.0, K_thetaB=400.0,
        K_phiA=400.0, K_phiB=400.0, K_phiC=400.0, **base)
    assert tight < loose, (tight, loose)


def test_combine_legs_arithmetic_and_sign():
    # ΔG_bind = ΔG_dec_solv − ΔG_dec_cplx − SSC. Strong binder: complex much harder to decouple than solvent.
    # SSC = -10.0 (favourable release). ΔG_bind = 30 − 60 − (−10) = -20 → negative (binds), restraint penalty
    # (+10) makes it LESS negative than the raw 30−60=−30.
    dg, se = abfe.combine_legs(complex_decouple_dg=60.0, complex_decouple_se=0.5,
                               solvent_decouple_dg=30.0, solvent_decouple_se=0.4,
                               restraint_standard_state_dg=-10.0)
    assert abs(dg - (-20.0)) < 1e-9, dg
    assert abs(se - (0.5 ** 2 + 0.4 ** 2) ** 0.5) < 1e-9, se
    # restraint correction weakens binding: without it ΔG would be −30, with it −20 (less favourable)
    raw = 30.0 - 60.0
    assert dg > raw, (dg, raw)


def test_selectivity_ddg_sign_and_error():
    # NR4A3 binds tighter (−12) than NR4A1 (−8) → ΔΔG = −12 − (−8) = −4 (negative ⇒ target-selective)
    ddg, se = abfe.selectivity_ddg(-12.0, 0.6, -8.0, 0.8)
    assert abs(ddg - (-4.0)) < 1e-9, ddg
    assert abs(se - (0.6 ** 2 + 0.8 ** 2) ** 0.5) < 1e-9, se


def test_geometry_helpers_known_values():
    import math
    # right angle at origin: (1,0,0)-(0,0,0)-(0,1,0) = 90°
    assert abs(abfe._ang3((1, 0, 0), (0, 0, 0), (0, 1, 0)) - math.pi / 2) < 1e-9
    # classic +90° dihedral: a=(1,0,0), b=(0,0,0), c=(0,0,1), d=(0,1,1)
    dih = abfe._dih4((1, 0, 0), (0, 0, 0), (0, 0, 1), (0, 1, 1))
    assert abs(abs(dih) - math.pi / 2) < 1e-9, dih


def test_select_boresch_anchors_geometry_and_guards():
    import math
    # Ligand atoms 0,1,2 near origin; receptor atoms 3,4,5 offset ~0.5 nm along +x (in-pocket window).
    coords = [
        (0.00, 0.00, 0.00),   # 0 ligand (centroid-ish → L0)
        (0.20, 0.00, 0.00),   # 1 ligand (farthest from L0 → L1)
        (0.00, 0.20, 0.05),   # 2 ligand (off the L0-L1 line → L2)
        (0.50, 0.00, 0.00),   # 3 receptor (nearest L0 at 0.5 nm → R0)
        (0.80, 0.30, 0.00),   # 4 receptor
        (0.80, 0.00, 0.40),   # 5 receptor
    ]
    sel = abfe.select_boresch_anchors(coords, ligand_atoms=[0, 1, 2], receptor_atoms=[3, 4, 5])
    assert sel["ligand_anchors"][0] == 0                    # L0 = nearest centroid
    assert set(sel["ligand_anchors"]) == {0, 1, 2}         # all three distinct ligand anchors
    assert sel["receptor_anchors"][-1] == 3                 # R0 = nearest receptor to L0
    assert len(set(sel["receptor_anchors"])) == 3          # three distinct receptor anchors
    assert abs(sel["r0_A"] - 5.0) < 1e-6                    # |R0-L0| = 0.5 nm = 5 Å
    # all reported angles must be inside the safe non-degenerate window (30–150°)
    for key in ("thetaA0_rad", "thetaB0_rad"):
        assert math.radians(30) <= sel[key] <= math.radians(150), (key, sel[key])
    # dihedrals must be finite and in (−π, π]
    for key in ("phiA0_rad", "phiB0_rad", "phiC0_rad"):
        assert -math.pi - 1e-9 <= sel[key] <= math.pi + 1e-9, (key, sel[key])


def test_select_boresch_anchors_raises_when_no_receptor_in_window():
    # all receptor atoms > r_max from the ligand → no valid R0
    coords = [(0, 0, 0), (0.2, 0, 0), (0, 0.2, 0.05), (5.0, 0, 0), (5.3, 0.3, 0), (5.3, 0, 0.4)]
    try:
        abfe.select_boresch_anchors(coords, ligand_atoms=[0, 1, 2], receptor_atoms=[3, 4, 5])
        assert False, "should have raised when no receptor anchor is within the distance window"
    except ValueError:
        pass


def test_select_boresch_anchors_avoids_collinear_thetaB():
    import math
    # Ligand atom 1 is the FARTHEST from L0 but COLLINEAR with R0 & L0 on the x-axis. A naive "L1 = farthest"
    # would give thetaB = angle(R0,L0,L1) = 0° (degenerate → the SSC's sin θB → 0 → blows up). The selector must
    # instead pick a non-collinear L1 (atom 2). Regression for the bug the smoke round-trip caught.
    coords = [
        (0.00, 0.00, 0.00),   # 0 ligand L0
        (0.20, 0.00, 0.00),   # 1 ligand — farthest from L0 but collinear with R0 & L0
        (0.00, 0.18, 0.03),   # 2 ligand — off-axis (valid L1)
        (0.50, 0.00, 0.00),   # 3 receptor R0 (nearest L0; on the x-axis)
        (0.62, 0.30, 0.05),   # 4 receptor
        (0.55, -0.22, 0.25),  # 5 receptor
        (0.72, 0.08, -0.20),  # 6 receptor
    ]
    sel = abfe.select_boresch_anchors(coords, ligand_atoms=[0, 1, 2], receptor_atoms=[3, 4, 5, 6])
    assert sel["ligand_anchors"][0] == 0
    assert sel["ligand_anchors"][1] != 1, "L1 must not be the collinear atom 1"
    assert math.radians(30) <= sel["thetaB0_rad"] <= math.radians(150), math.degrees(sel["thetaB0_rad"])
