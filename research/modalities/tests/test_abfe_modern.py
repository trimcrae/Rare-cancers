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
