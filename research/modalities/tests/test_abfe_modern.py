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
