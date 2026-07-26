#!/usr/bin/env python3
"""The time-resolved contact-moiety series must tell the three histories apart.

WHY IT EXISTS. The two-frame contact-moiety RMSD established that the binary leg's BOUND moiety moves ~16 Å
(GH run 30202934339: contact max 16.327 Å, median 4.333 Å, 30-52 of 59 heavy atoms in contact; the ternary leg in
the same cycle is clean at 2.835 / 1.653). That is a real measured failure — and it is exactly where a two-frame
comparison stops helping, because `iterations_compared [0, 2000]` is consistent with histories that have different
consequences:

    DISPLACED_AND_STAYED    the ligand left. ΔG_binary is sampling an unbound/misbound state, and
                            ΔΔG_coop = ΔG_ternary - ΔG_binary is NOT recoverable by sampling harder.
    EXCURSION_AND_RETURNED  it went out and came back; the ENDPOINT metric is what misleads, not the sampling.
    JUMP                    a single-frame discontinuity -> suspect bookkeeping (imaging, replica indexing).
                            Nothing physical crosses that distance in one checkpoint interval.

Getting that classification wrong in either direction is costly: calling a real unbinding an "excursion" would
license reusing a broken leg, and calling a bookkeeping jump "physics" would send someone resampling a
non-problem. So each shape is pinned against a synthetic trajectory built to have exactly that shape.

Nothing here feeds a gate — the flag stays with the two-frame value, deliberately, so a classifier heuristic can
never move a verdict. These tests pin the DIAGNOSTIC, and the separate assertion that it stays out of the
pass/fail path is at the bottom.

Pure numpy against the real function via a minimal fake reporter — no openmmtools, no trajectory files.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

try:
    import numpy as np
except ImportError:  # pragma: no cover
    print("SKIP: numpy unavailable")
    sys.exit(0)

import ternary_fep_convergence as cv

N_PROT, N_LIG = 20, 10          # rows 0-19 receptor, 20-24 bound warhead, 25-29 distal
BOUND = list(range(20, 25))


class _State:
    """Duck-types just enough of an openmmtools SamplerState for _replica_coords."""

    class _Q:
        def __init__(self, a):
            self._a = a
            self.unit = "nanometer"

        def value_in_unit(self, _u):
            return self._a

    def __init__(self, xyz):
        self.positions = _State._Q(xyz)
        self.box_vectors = None          # no box -> _min_image is a no-op, which keeps these tests about shape


class _Reporter:
    """Serves a prescribed per-iteration displacement of the BOUND warhead along +x, in nm."""

    def __init__(self, disp_by_iter, n_replicas=1, interval=40):
        self.checkpoint_interval = interval
        self._disp = disp_by_iter
        self._n = n_replicas
        rng = np.random.default_rng(0)
        rec = rng.uniform(-1.0, 1.0, size=(N_PROT, 3)); rec[:, 2] = 0.0
        bound = np.array([[0.1 * i, 0.0, 0.30] for i in range(5)])     # inside the 0.45 nm contact cutoff
        distal = np.array([[0.1 * i, 0.0, 3.00] for i in range(5)])    # never in contact
        self._base = np.vstack([rec, bound, distal])
        self.analysis_particle_indices = list(range(N_PROT + N_LIG))

    def read_sampler_states(self, iteration=0, analysis_particles_only=False):
        if iteration not in self._disp:
            raise KeyError("no frame at %d" % iteration)
        out = []
        for _ in range(self._n):
            x = self._base.copy()
            x[20:25] += np.array([self._disp[iteration], 0.0, 0.0])
            out.append(_State(x))
        return out


def _ident_patch(monkey_rows=None):
    """_contact_pose_timeseries calls _ligand_atoms; give it a deterministic answer."""
    return {"ligand_atom_indices": list(range(N_PROT, N_PROT + N_LIG)),
            "ligand_heavy_indices": list(range(N_PROT, N_PROT + N_LIG)),
            "protein_atom_indices": list(range(N_PROT)),
            "protein_heavy_indices": list(range(N_PROT)),
            "protein_chains": [list(range(N_PROT))]}


def _run(disp_by_iter, n_replicas=1, interval=40):
    orig = cv._ligand_atoms
    cv._ligand_atoms = lambda _r: _ident_patch()
    try:
        rep = _Reporter(disp_by_iter, n_replicas=n_replicas, interval=interval)
        return cv._contact_pose_timeseries(rep, max(disp_by_iter), interval)
    finally:
        cv._ligand_atoms = orig


def test_stable_trajectory_is_STABLE():
    d = {i: 0.0 for i in range(0, 401, 40)}
    r = _run(d)
    assert r["per_replica"][0]["classification"] == "STABLE", r["per_replica"][0]
    assert r["n_replicas_ending_beyond_threshold"] == 0


def test_monotonic_departure_is_DISPLACED_AND_STAYED():
    # 0 -> 1.6 nm (16 A) steadily, ending where it peaked
    d = {i: 1.6 * (i / 400.0) for i in range(0, 401, 40)}
    r = _run(d)
    c = r["per_replica"][0]
    assert c["classification"] == "DISPLACED_AND_STAYED", c
    assert c["max_A"] > cv.LIG_RMSD_MAX_A and c["final_A"] > cv.LIG_RMSD_MAX_A
    assert r["n_replicas_ending_beyond_threshold"] == 1


def test_out_and_back_is_EXCURSION_AND_RETURNED():
    # peaks mid-trajectory at 16 A and comes back to ~0
    d = {}
    for i in range(0, 401, 40):
        f = i / 400.0
        d[i] = 1.6 * (1.0 - abs(2.0 * f - 1.0))
    r = _run(d)
    c = r["per_replica"][0]
    assert c["classification"] == "EXCURSION_AND_RETURNED", c
    assert c["max_A"] > cv.LIG_RMSD_MAX_A
    assert c["final_A"] < 0.4 * c["max_A"]
    # THE POINT: the endpoint metric would have called this stable, and the two-frame flag would have passed it.
    assert r["n_replicas_ending_beyond_threshold"] == 0
    assert c["iteration_at_max"] not in (0, 400), "the peak must be interior for this to be an excursion"


def test_single_frame_discontinuity_is_flagged_as_JUMP():
    # flat, then one frame 16 A out, then flat again at the far value
    d = {i: 0.0 for i in range(0, 401, 40)}
    for i in range(200, 401, 40):
        d[i] = 1.6
    r = _run(d)
    c = r["per_replica"][0]
    assert c["classification"].startswith("JUMP("), c
    assert c["largest_single_frame_step_A"] >= 0.8 * c["max_A"], c


def test_a_gradual_departure_is_NOT_called_a_jump():
    """The JUMP test above only means something if a smooth departure does not also trip it."""
    d = {i: 1.6 * (i / 400.0) for i in range(0, 401, 40)}
    c = _run(d)["per_replica"][0]
    assert "JUMP" not in c["classification"], c


def test_contacts_are_fixed_from_the_reference_frame():
    """A departing warhead must not drop out of the contact set — that would erase its own evidence."""
    d = {i: 1.6 * (i / 400.0) for i in range(0, 401, 40)}
    r = _run(d)
    assert r["reference_iteration"] == 0
    assert r["n_contact_heavy_per_replica"] == [len(BOUND)], r.get("n_contact_heavy_per_replica")
    assert r["per_replica"][0]["n_contact_heavy"] == len(BOUND)


def test_every_replica_is_classified_independently():
    r = _run({i: 1.6 * (i / 400.0) for i in range(0, 401, 40)}, n_replicas=4)
    assert r["n_replicas"] == 4, r
    assert sum(r["class_counts"].values()) == 4


def test_frames_are_subsampled_but_endpoints_kept():
    d = {i: 0.0 for i in range(0, 4001, 40)}      # 101 candidate frames
    r = _run(d)
    assert r["frames_used"] <= cv.TIMESERIES_MAX_FRAMES, r["frames_used"]
    assert r["iterations"][0] == 0, r["iterations"][:3]
    assert r["iterations"][-1] == 4000, r["iterations"][-3:]


def test_no_usable_frame_is_UNAVAILABLE_not_flat():
    class _Empty(_Reporter):
        def read_sampler_states(self, iteration=0, analysis_particles_only=False):
            raise KeyError("none stored")

    orig = cv._ligand_atoms
    cv._ligand_atoms = lambda _r: _ident_patch()
    try:
        r = cv._contact_pose_timeseries(_Empty({0: 0.0}), 400, 40)
    finally:
        cv._ligand_atoms = orig
    assert "per_replica" not in r or not r.get("per_replica")
    assert "UNAVAILABLE" in r.get("status", ""), r.get("status")
    assert "not the same as flat" in r.get("status", "")


def test_the_series_does_NOT_feed_the_pass_fail_path():
    """Deliberate: a classifier heuristic must never be able to move a verdict.

    The gate is `ligand_stable_ok`, computed from `ligand_rmsd_A` (the two-frame contact-moiety value). If a
    future edit wires the timeseries into health_flags or technical_failure, this fails.
    """
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                            "ternary_fep_convergence.py")).read()
    i = src.index("def analyze_leg")
    j = src.index("rec[\"health_flags\"] = flags")
    flag_region = src[i:j]
    assert "timeseries" not in flag_region and "contact_pose_timeseries" not in flag_region, (
        "the time-resolved series must stay OUT of the health-flag computation — it is diagnostic evidence for "
        "reading the flag, not an input to it")




# --- λ ATTRIBUTION -----------------------------------------------------------------------------------
#
# WHY IT MATTERS. Replicas exchange λ, not coordinates, so "replica 7 departed" says nothing on its own about the
# Hamiltonian it departed under. In an OpenFE hybrid-topology RBFE BOTH endpoints are physical (state 0 = ligand A
# fully interacting, state N-1 = ligand B fully interacting) and the softcore region is largest in the INTERIOR.
# So the question is not "weakly coupled or not" — it is:
#
#   exceedances at a PHYSICAL ENDPOINT state -> cannot be blamed on softcore softening. The modelled complex is
#                                               unstable there, i.e. the binary pose/model is wrong.
#   exceedances only in the INTERIOR          -> a protocol artifact; the leg may want a restraint and ΔG may be
#                                               salvageable.
#
# Those prescribe different work, so the attribution has to be right, and an UNAVAILABLE assignment must read as
# unanswered rather than as the benign answer.

class _ReporterL(_Reporter):
    """Adds a prescribed per-iteration λ-state assignment."""

    def __init__(self, disp_by_iter, lam_by_iter, n_replicas=1, interval=40, fail=False):
        super().__init__(disp_by_iter, n_replicas=n_replicas, interval=interval)
        self._lam = lam_by_iter
        self._fail = fail

    def read_replica_thermodynamic_states(self, iteration=0):
        if self._fail:
            raise RuntimeError("not stored")
        return self._lam[iteration]


def _runL(disp, lam, n_replicas=1, interval=40, fail=False):
    orig = cv._ligand_atoms
    cv._ligand_atoms = lambda _r: _ident_patch()
    try:
        rep = _ReporterL(disp, lam, n_replicas=n_replicas, interval=interval, fail=fail)
        return cv._contact_pose_timeseries(rep, max(disp), interval)
    finally:
        cv._ligand_atoms = orig


def test_departure_at_a_physical_endpoint_state_is_attributed_there():
    """The replica sits at state 0 (ligand A fully interacting) the whole time and still leaves."""
    d = {i: 1.6 * (i / 400.0) for i in range(0, 401, 40)}
    lam = {i: [0] for i in range(0, 401, 40)}                   # always the physical endpoint
    r = _runL(d, lam)
    assert r["n_lambda_states"] == 1, r["n_lambda_states"]
    assert r["exceedances_at_physical_endpoint_states"] > 0, r
    assert r["exceedances_at_alchemical_interior_states"] == 0, r
    assert "PHYSICAL ENDPOINT" in r["lambda_verdict"], r["lambda_verdict"]


def test_departure_only_in_the_alchemical_interior_is_attributed_there():
    d = {i: 1.6 * (i / 400.0) for i in range(0, 401, 40)}
    # 12-state ladder; this replica sits at interior state 6 throughout, and state 11 is seen elsewhere so
    # n_states resolves to 12
    lam = {i: [6, 11] for i in range(0, 401, 40)}
    r = _runL(d, lam, n_replicas=2)
    assert r["n_lambda_states"] == 12, r["n_lambda_states"]
    # replica 0 is at interior state 6; replica 1 is at endpoint 11 — both displace identically here, so both
    # buckets fill. What must hold is that the interior frames are NOT counted as endpoint frames.
    assert r["exceedances_at_alchemical_interior_states"] > 0, r
    hist = r["exceedance_lambda_histogram"]
    assert 6 in hist and hist[6] > 0, hist
    assert set(hist) <= {6, 11}, hist


def test_a_stable_replica_contributes_no_exceedances():
    d = {i: 0.0 for i in range(0, 401, 40)}
    lam = {i: [0] for i in range(0, 401, 40)}
    r = _runL(d, lam)
    assert r["exceedances_at_physical_endpoint_states"] == 0
    assert r["exceedances_at_alchemical_interior_states"] == 0
    assert "nothing to attribute" in r["lambda_verdict"], r["lambda_verdict"]


def test_per_replica_lambda_fields_are_populated():
    d = {i: 1.6 * (i / 400.0) for i in range(0, 401, 40)}
    lam = {i: [0 if i < 200 else 5] for i in range(0, 401, 40)}
    rec = _runL(d, lam)["per_replica"][0]
    assert rec["lambda_at_final"] == 5, rec
    assert rec["lambda_states_visited"] == [0, 5], rec
    assert rec["lambda_at_first_exceed"] in (0, 5), rec


def test_unavailable_lambda_is_UNANSWERED_not_benign():
    """A reporter that cannot supply assignments must not read as 'no endpoint problem'."""
    d = {i: 1.6 * (i / 400.0) for i in range(0, 401, 40)}
    r = _runL(d, {}, fail=True)
    assert r.get("exceedances_at_physical_endpoint_states") is None, r.get("exceedances_at_physical_endpoint_states")
    assert "UNAVAILABLE" in r["lambda_verdict"], r["lambda_verdict"]
    assert "NOT answered in the benign direction" in r["lambda_verdict"], r["lambda_verdict"]
    # and the pose series itself must still be produced — a missing λ must not kill the whole diagnostic
    assert r["per_replica"] and r["per_replica"][0]["classification"] == "DISPLACED_AND_STAYED", r["per_replica"]


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except AssertionError as e:
                print("FAIL", name, "\n      ", e)
                fails += 1
            except Exception as e:  # noqa: BLE001
                print("ERROR", name, type(e).__name__, e)
                fails += 1
    print("\n%d failure(s)" % fails)
    sys.exit(1 if fails else 0)
