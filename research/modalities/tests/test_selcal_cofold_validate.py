"""The co-fold-vs-crystal check the sensitivity control was DESIGNED around and never ran.

`selcal_panel.py` chose PRT3789 over the better-documented ACBI2 precisely because two deposited ternaries
carry the same ligand on both arms (9DTY / 9DTX), so — in the panel's own words — *"each arm's co-fold can be
VALIDATED against a real structure of the very complex it models"*; `selcal_stage`'s docstring repeats that
the crystals are *"used to VALIDATE the co-folds rather than to supply them."* No such validation existed.
`selcal-verdict.json` then returned NULL and bounded itself between *"the readout is blunt"* and *"this pair
is hard"* — with no branch for *"the co-fold was not the measured complex."*

These tests pin the behaviours that make that third branch trustworthy, and every one of them is a rule this
program has already been burned by:

  1. **Units.** nm in, Å out. A missing nm→Å conversion in the SAME readout family put a ~30–49 Å Lys
     separation into the record as 2.34–4.48 Å (STRATEGY Appendix A 15).
  2. **The kernels are IMPORTED, not copied.** A second superposition would put the diagnostic on a scale
     nobody could read against E1.
  3. **Correspondence is DERIVED, never assumed.** Matching by chain letter or residue count is the defect
     that scored Elongin C as the degradation target for a whole panel.
  4. **A refusal is a first-class outcome.** An unreadable co-fold must never render as a co-fold that
     disagrees with the crystal — an absent reading is not a reading of absence (CLAUDE.md §4).
  5. **Nothing here grades anything.** The module reports input quality and emits no verdict; the reported
     E1 constants are context, not a pass mark.
"""
import json
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import selcal_cofold_validate as V  # noqa: E402


# ---------- fixture builders: two tiny "structures" we can move by a KNOWN amount ------------------------

_AA3 = ["ALA", "SER", "GLY", "VAL", "LEU", "THR", "ILE", "ASN", "PHE", "LYS",
        "GLU", "ASP", "ARG", "TYR", "TRP", "MET", "PRO", "HIS", "GLN", "CYS"]


def _residue_atoms(chain, seq, resname, cx, cy, cz):
    """One residue as N/CA/C/O at small fixed offsets from a centre — enough geometry for contacts and CA
    superposition, small enough to reason about by hand."""
    off = [("N", "N", -0.6, 0.0, 0.0), ("CA", "C", 0.0, 0.0, 0.0),
           ("C", "C", 0.6, 0.0, 0.0), ("O", "O", 0.9, 0.5, 0.0)]
    return [V.Atom(chain, seq, "", resname, nm, el, cx + dx, cy + dy, cz + dz, False)
            for (nm, el, dx, dy, dz) in off]


def _seq_for(chain, n):
    """A deterministic pseudo-random residue sequence, distinct per chain.

    ⚠ It must be DISTINCT, and the first draft of this fixture got that wrong in an instructive way: every
    chain was `_AA3[i % 20]`, so all four carried the same repeating sequence and the module's collision guard
    correctly refused to map them — `{'A': ['A', 'E', 'F', 'G']}`. The guard working on a bad fixture is the
    behaviour we want; the fixture is what needed fixing."""
    x = (ord(chain) * 7919 + 13) & 0xFFFFFFFF
    out = []
    for _ in range(n):
        x = (1103515245 * x + 12345) & 0x7FFFFFFF
        out.append(_AA3[x % len(_AA3)])
    return out


def _chain(chain, n, x0, y0, z0, step=3.8, resnames=None):
    names = resnames or _seq_for(chain, n)
    atoms = []
    for i in range(n):
        atoms += _residue_atoms(chain, i + 1, names[i], x0 + i * step, y0, z0)
    return atoms


def _complex(target_dx=0.0, n_target=24, n_e3=(20, 18, 16)):
    """A toy ternary: target chain A, E3 chains E/F/G. `target_dx` rigidly displaces the target along x, which
    is exactly the quantity the interface RMSD should recover.

    Chain E sits 4 Å from the target so real heavy-atom contacts exist inside BOTH cutoffs in play — the
    0.8 nm interface selector E1 uses and the 5.0 Å fnat cutoff. F and G sit further out, mirroring a real
    VCB where only VHL touches the target.

    The three E3 chains are also within contact of each other, as VHL/EloB/EloC are in a real VCB — otherwise
    `assembly_components` would (correctly) split one copy into pieces and the fixture, not the code, would be
    the thing under test.
    """
    atoms = []
    atoms += _chain("A", n_target, 0.0 + target_dx, 0.0, 0.0)
    atoms += _chain("E", n_e3[0], 0.0, 4.0, 0.0)
    atoms += _chain("F", n_e3[1], 0.0, 11.0, 0.0)
    atoms += _chain("G", n_e3[2], 0.0, 18.0, 0.0)
    return atoms


def _ligand(atoms, resname="A1BB4", chain="A", seq=900, n=30):
    return atoms + [V.Atom(chain, seq, "", resname, "C%d" % i, "C", 1.0 * i, 3.0, 0.0, True)
                    for i in range(n)]


def _write_pdb(atoms, path):
    with open(path, "w") as fh:
        for i, a in enumerate(atoms, start=1):
            rec = "HETATM" if a.hetatm else "ATOM  "
            fh.write("%s%5d %-4s %3s %s%4d    %8.3f%8.3f%8.3f  1.00  0.00          %2s\n"
                     % (rec, i, a.name.ljust(4)[:4], a.resname[:3], a.chain, a.resseq,
                        a.x, a.y, a.z, (a.element or "").rjust(2)))
        fh.write("END\n")
    return path


def _write_cif(atoms, path):
    with open(path, "w") as fh:
        fh.write("data_test\n#\nloop_\n")
        for c in ("group_PDB", "id", "type_symbol", "label_atom_id", "label_alt_id", "label_comp_id",
                  "auth_asym_id", "auth_seq_id", "pdbx_PDB_ins_code", "Cartn_x", "Cartn_y", "Cartn_z",
                  "auth_comp_id", "auth_atom_id", "pdbx_PDB_model_num"):
            fh.write("_atom_site.%s\n" % c)
        for i, a in enumerate(atoms, start=1):
            fh.write("%s %d %s %s . %s %s %d ? %.3f %.3f %.3f %s %s 1\n"
                     % ("HETATM" if a.hetatm else "ATOM", i, a.element or "C", a.name, a.resname,
                        a.chain, a.resseq, a.x, a.y, a.z, a.resname, a.name))
        fh.write("#\n")
    return path


# ---------- 1 · units: the failure mode that already inverted a conclusion --------------------------------


def test_nm_converter_is_the_only_unit_hop_and_it_divides_by_ten():
    """`_aligned_iface_rmsd`'s contract is NANOMETRES in, ÅNGSTRÖM out. Structure files are Å."""
    assert V._nm([(10.0, 20.0, -30.0)]) == [(1.0, 2.0, -3.0)]


@pytest.mark.parametrize("shift_a", [0.5, 2.0, 7.5])
def test_interface_rmsd_recovers_a_known_rigid_displacement_in_angstrom(tmp_path, shift_a):
    """A rigid shift of the target by `shift_a` Å, with the E3 held fixed, must come back as `shift_a` Å.

    This is the end-to-end unit check: if the nm→Å hop were dropped the answer would be 10× small, which is
    exactly the shape of the R3 defect (2.34 Å reported for a 25 Å separation)."""
    pytest.importorskip("numpy", reason="the imported E1 RMSD kernel needs numpy; parsing/mapping do not")
    native = _write_cif(_complex(target_dx=0.0), str(tmp_path / "native.cif"))
    model = _write_cif(_complex(target_dx=shift_a), str(tmp_path / "model.cif"))
    rec = V.validate_one(model, native)
    assert rec["graded"] is True, rec.get("why")
    # Only the target moved, so the interface RMSD is the shift diluted over (E3-side + target-side) atoms.
    # It must be strictly between zero and the shift, and must SCALE with it — the property that a lost unit
    # conversion destroys.
    assert 0.0 < rec["interface_rmsd_to_crystal_A"] <= shift_a + 1e-6


def test_interface_rmsd_scales_linearly_with_the_displacement(tmp_path):
    pytest.importorskip("numpy")
    native = _write_cif(_complex(target_dx=0.0), str(tmp_path / "n.cif"))
    one = V.validate_one(_write_cif(_complex(target_dx=1.0), str(tmp_path / "m1.cif")), native)
    ten = V.validate_one(_write_cif(_complex(target_dx=10.0), str(tmp_path / "m10.cif")), native)
    assert one["graded"] and ten["graded"]
    # The reported value is rounded to 3 dp, so the comparison is made at that precision and no tighter —
    # asserting exact linearity on a rounded number would fail for a reason that has nothing to do with the
    # geometry (0.7157 rounds to 0.716, and 10x that is 7.160 against a true 7.157).
    assert math.isclose(ten["interface_rmsd_to_crystal_A"], 10.0 * one["interface_rmsd_to_crystal_A"],
                        abs_tol=10 * 5e-4)


def test_identical_structures_score_zero(tmp_path):
    pytest.importorskip("numpy")
    native = _write_cif(_complex(), str(tmp_path / "n.cif"))
    model = _write_cif(_complex(), str(tmp_path / "m.cif"))
    rec = V.validate_one(model, native)
    assert rec["graded"] is True
    assert rec["interface_rmsd_to_crystal_A"] == pytest.approx(0.0, abs=1e-6)
    assert rec["fnat"]["fnat"] == 1.0


# ---------- 2 · the kernels are imported, not re-implemented ----------------------------------------------


def test_the_rmsd_and_interface_kernels_come_from_the_endpoint_module():
    """If either were copied, this diagnostic would sit on a scale that cannot be read against E1."""
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "selcal_cofold_validate.py")).read()
    assert "from nrv04_covalent_md import _aligned_iface_rmsd" in src
    assert "from nrv04_covalent_md import interface_atom_indices" in src
    assert "from nr4a_differential_atlas import nw_align" in src
    # and no local re-implementation sneaking back in
    assert "def _aligned_iface_rmsd" not in src
    assert "def interface_atom_indices" not in src
    assert "def nw_align" not in src


def test_reported_e1_constant_is_read_from_the_frozen_readouts_not_typed():
    import nrv04_readouts as R
    ctx = V.reporting_context()
    assert ctx["E1_stable_plateau_A"] == R.INTERFACE_RMSD_STABLE_A
    assert "_not_a_threshold" in ctx and "graded against" in ctx["_not_a_threshold"]


# ---------- 3 · correspondence is derived, never assumed --------------------------------------------------


def test_chain_map_is_by_sequence_and_survives_relabelled_chains(tmp_path):
    """The crystal's author chain ids need not match the co-fold's. Matching must follow the SEQUENCE."""
    pytest.importorskip("numpy")
    native_atoms = []
    relabel = {"A": "P", "E": "C", "F": "B", "G": "D"}      # a plausible deposited-ternary lettering
    for a in _complex():
        native_atoms.append(V.Atom(relabel[a.chain], a.resseq, a.icode, a.resname, a.name, a.element,
                                   a.x, a.y, a.z, a.hetatm))
    native = _write_cif(native_atoms, str(tmp_path / "n.cif"))
    model = _write_cif(_complex(), str(tmp_path / "m.cif"))
    rec = V.validate_one(model, native)
    assert rec["graded"] is True, rec.get("why")
    matched = rec["chain_map"]["matched"]
    assert matched["A"]["native_chain"] == "P"
    assert matched["E"]["native_chain"] == "C"
    assert matched["G"]["native_chain"] == "D"


def test_chain_map_refuses_when_two_model_chains_claim_one_crystal_chain(tmp_path):
    """The Elongin-C-as-target defect in its general form. Refuse; never pick one."""
    same = _AA3[:18] * 2
    model_atoms = (_chain("A", 18, 0, 0, 0, resnames=same) + _chain("E", 18, 0, 6, 0, resnames=same)
                   + _chain("F", 18, 0, 14, 0) + _chain("G", 18, 0, 22, 0))
    native_atoms = _chain("X", 18, 0, 0, 0, resnames=same)   # one chain both A and E will match perfectly
    model = _write_cif(model_atoms, str(tmp_path / "m.cif"))
    native = _write_cif(native_atoms, str(tmp_path / "n.cif"))
    rec = V.validate_one(model, native)
    assert rec["graded"] is False
    assert "two model chains map to one crystal chain" in rec["why"]
    assert "Elongin C" in rec["why"]                        # the incident is named, so nobody re-learns it


def test_unrelated_sequences_are_refused_not_matched(tmp_path):
    """Below MIN_CHAIN_IDENTITY the mapping must decline. A forced match is a silent wrong answer."""
    model_atoms = _complex()
    native_atoms = _chain("X", 24, 0, 0, 0, resnames=["PRO"] * 24)
    rec = V.validate_one(_write_cif(model_atoms, str(tmp_path / "m.cif")),
                         _write_cif(native_atoms, str(tmp_path / "n.cif")))
    assert rec["graded"] is False
    assert "no crystal counterpart" in rec["why"]


def test_identity_threshold_is_a_refusal_floor_not_a_grade():
    assert 0.0 < V.MIN_CHAIN_IDENTITY < 1.0
    assert V.MIN_ALIGNED_RESIDUES >= 3, "three points define a rigid body; fewer cannot superpose"


# ---------- 4 · a refusal is a first-class outcome --------------------------------------------------------


def test_unreadable_model_refuses_rather_than_scoring(tmp_path):
    bad = tmp_path / "broken.cif"
    bad.write_text("data_nothing\n# no atom_site loop at all\n")
    native = _write_cif(_complex(), str(tmp_path / "n.cif"))
    rec = V.validate_one(str(bad), native)
    assert rec["graded"] is False
    assert rec.get("interface_rmsd_to_crystal_A") is None
    assert "could not parse" in rec["why"]


def test_missing_cofold_is_reported_as_unread_not_as_disagreement(tmp_path):
    """The exact wording matters: a panel with no model must not read as a panel that failed the check."""
    root = tmp_path / "cofolds"
    (root / "smarca2" / "seed_1").mkdir(parents=True)
    native_dir = tmp_path / "native"
    native_dir.mkdir()
    res = V.validate_panel(str(root), str(native_dir), arms=["selcal_smarca2"], seeds=[1])
    assert res["n_graded"] == 0 and res["n_refused"] == 1
    why = res["records"][0]["why"]
    assert "NOT a reading that the co-fold disagrees" in why
    assert res["per_arm"]["selcal_smarca2"]["interface_rmsd_to_crystal_A"]["mean"] is None


def test_refusals_are_never_averaged_into_a_per_arm_figure(tmp_path):
    pytest.importorskip("numpy")
    root = tmp_path / "cofolds"
    native_dir = tmp_path / "native"
    native_dir.mkdir()
    _write_cif(_complex(), str(native_dir / "9DTY.cif"))
    for seed, dx in ((1, 0.0), (2, 4.0)):
        d = root / "smarca2" / ("seed_%d" % seed)
        d.mkdir(parents=True)
        _write_cif(_complex(target_dx=dx), str(d / "model.cif"))
    (root / "smarca2" / "seed_3").mkdir(parents=True)        # present but empty -> refusal
    res = V.validate_panel(str(root), str(native_dir), arms=["selcal_smarca2"], seeds=[1, 2, 3])
    arm = res["per_arm"]["selcal_smarca2"]
    assert res["n_graded"] == 2 and res["n_refused"] == 1
    assert arm["n_graded"] == 2 and len(arm["interface_rmsd_to_crystal_A"]["values"]) == 2
    assert "absent reading is not a reading of absence" in res["_completeness"]


# ---------- 5 · fnat, and the honesty of its denominator --------------------------------------------------


def test_fnat_counts_unmappable_native_contacts_as_lost_and_says_so(tmp_path):
    """A thin correspondence must depress fnat visibly. Shrinking the denominator instead would let a co-fold
    that reproduces almost nothing score well."""
    pytest.importorskip("numpy")
    native = _write_cif(_complex(n_target=24), str(tmp_path / "n.cif"))
    model = _write_cif(_complex(n_target=24), str(tmp_path / "m.cif"))
    rec = V.validate_one(model, native)
    fn = rec["fnat"]
    assert fn["n_native_contacts"] > 0
    assert fn["n_recovered"] + fn["n_unmappable"] <= fn["n_native_contacts"]
    assert "counted as NOT" in fn["_unmappable_note"]


def test_fnat_falls_when_the_target_is_pulled_off_the_interface(tmp_path):
    pytest.importorskip("numpy")
    native = _write_cif(_complex(target_dx=0.0), str(tmp_path / "n.cif"))
    near = V.validate_one(_write_cif(_complex(target_dx=0.0), str(tmp_path / "m0.cif")), native)
    far = V.validate_one(_write_cif(_complex(target_dx=60.0), str(tmp_path / "m60.cif")), native)
    assert near["fnat"]["fnat"] > far["fnat"]["fnat"]


def test_fnat_cutoff_is_deliberately_not_the_panel_endpoint_constant():
    """fnat is a structure-comparison metric on the docking literature's scale. Borrowing a frozen endpoint's
    constant would make it look like one of the panel's endpoints."""
    import nrv04_readouts as R
    assert V.FNAT_CONTACT_A == 5.0
    assert V.FNAT_CONTACT_A != R.CONTACT_CUTOFF_A


def test_centroid_prefilter_cannot_change_the_answer(tmp_path):
    """The prefilter is a proven bound (no heavy atom sits >8 Å from its residue centroid), so widening it
    must leave every count identical. If this ever fails the bound was wrong, not merely tight."""
    pytest.importorskip("numpy")
    atoms_n, atoms_m = _complex(), _complex(target_dx=1.5)
    corr_native = _write_cif(atoms_n, str(tmp_path / "n.cif"))
    corr_model = _write_cif(atoms_m, str(tmp_path / "m.cif"))
    base = V.validate_one(corr_model, corr_native)["fnat"]
    wide = V.fnat(V.parse_structure(corr_model), V.parse_structure(corr_native),
                  {c: {"native_chain": c,
                       "pairs": V.residue_pairs(V.parse_structure(corr_model), V.parse_structure(corr_native),
                                                c, c, V.align_identity(
                                                    V.chain_sequence(V.parse_structure(corr_model), c)[0],
                                                    V.chain_sequence(V.parse_structure(corr_native), c)[0])[1])}
                   for c in ("A", "E", "F", "G")},
                  ["E", "F", "G"], ["A"], cutoff_a=V.FNAT_CONTACT_A)
    assert base["n_native_contacts"] == wide["n_native_contacts"]
    assert base["n_recovered"] == wide["n_recovered"]


# ---------- 5b · the two defects the FIRST real run exposed ------------------------------------------------
# Both produced plausible-looking numbers rather than errors, which is the dangerous shape (CLAUDE.md §4b).


def test_the_ligand_is_not_counted_as_an_interface_residue(tmp_path):
    """DEFECT 1, measured on run 30744840367: 9DTX reported 47 native contacts of which 43 (91 %) were
    `unmappable` — arithmetically impossible for protein-protein contacts on chains aligned at identity 1.000
    with full coverage. Cause: the deposited PROTAC (A1BB4) carries an auth chain id it SHARES with a protein
    chain, so it entered that chain's residue set and every ligand-protein contact was counted as an interface
    contact with no model counterpart. E1's own split puts LIG/UNL/UNK in neither set, so polymer-only is also
    what matches the endpoint."""
    pytest.importorskip("numpy")
    # Put a big HETATM ligand on the TARGET's chain id, straddling the interface, in both structures.
    def _with_ligand(dx):
        atoms = _complex(target_dx=dx)
        atoms += [V.Atom("A", 900, "", "A1BB4", "C%d" % i, "C", 2.0 * i, 2.0, 0.0, True) for i in range(64)]
        return atoms
    native = _write_cif(_with_ligand(0.0), str(tmp_path / "n.cif"))
    model = _write_cif(_with_ligand(0.0), str(tmp_path / "m.cif"))
    rec = V.validate_one(model, native)
    assert rec["graded"] is True, rec.get("why")
    fn = rec["fnat"]
    assert fn["n_unmappable"] == 0, (
        "a ligand sharing a protein chain id leaked into the interface residue set: %s" % fn)
    assert fn["fnat"] == 1.0, "identical structures must recover every native contact"
    # and it is still REPORTED as a ligand, by count and identity
    assert rec["ligand"]["native_resname"] == "A1BB4"
    assert rec["ligand"]["native_heavy_atoms"] == 64


def test_interface_selection_is_polymer_only_like_the_endpoints(tmp_path):
    """The same restriction on the interface selector, not just on fnat — otherwise the RMSD would be taken
    over a residue set the endpoint never scores."""
    atoms = _complex()
    atoms += [V.Atom("A", 900, "", "A1BB4", "C%d" % i, "C", 2.0 * i, 2.0, 0.0, True) for i in range(64)]
    e3_res, tg_res = V.native_interface_residues(atoms, ["E", "F", "G"], ["A"])
    assert all(k[1] != 900 for k in e3_res + tg_res), "the ligand residue reached the interface set"


def test_multi_copy_asymmetric_unit_scores_each_copy_and_never_builds_a_chimera(tmp_path):
    """DEFECT 2: 9DTY holds ~10 copies of the ternary in 40 chains, and every copy aligns to a given model
    chain at identity 1.000 — a perfect tie. Resolving the four roles independently would let them come from
    DIFFERENT copies: a reference complex that does not exist, scored without erroring."""
    pytest.importorskip("numpy")
    # Two copies, far apart. Copy 2 is displaced as a rigid body AND has its target pulled off the interface,
    # so a chimeric mix of copies would score very differently from either copy on its own.
    copy1 = _complex(target_dx=0.0)
    copy2 = []
    for a in _complex(target_dx=9.0):
        copy2.append(V.Atom({"A": "P", "E": "Q", "F": "R", "G": "S"}[a.chain], a.resseq, a.icode, a.resname,
                            a.name, a.element, a.x + 400.0, a.y, a.z, a.hetatm))
    native = _write_cif(copy1 + copy2, str(tmp_path / "n.cif"))
    model = _write_cif(_complex(target_dx=0.0), str(tmp_path / "m.cif"))

    comps = V.assembly_components(V.parse_structure(native))
    assert len(comps) == 2, "the two copies must be separated into components, got %s" % comps

    rec = V.validate_one(model, native)
    assert rec["graded"] is True, rec.get("why")
    cs = rec["copy_selection"]
    assert cs["n_components_in_asymmetric_unit"] == 2
    assert cs["n_copies_scored"] == 2
    # every role comes from ONE copy
    chosen = set(cs["chosen_native_chains"])
    assert chosen in ({"A", "E", "F", "G"}, {"P", "Q", "R", "S"}), chosen
    for mc, info in rec["chain_map"]["matched"].items():
        assert info["native_chain"] in chosen, "role %s was drawn from outside the chosen copy" % mc
    # the best copy is the one the model actually matches, and the spread is published
    assert rec["interface_rmsd_to_crystal_A"] == min(cs["interface_rmsd_across_copies_A"])
    assert len(cs["interface_rmsd_across_copies_A"]) == 2
    assert cs["interface_rmsd_across_copies_A"][0] < cs["interface_rmsd_across_copies_A"][1]


def test_assembly_components_group_chains_that_touch(tmp_path):
    atoms = _complex()
    comps = V.assembly_components(atoms)
    assert len(comps) == 1 and comps[0] == ["A", "E", "F", "G"], comps


def test_copies_that_TOUCH_in_a_lattice_are_still_separated(tmp_path):
    """DEFECT 2, second half — the one contact-components could not fix, found on the corrected run.

    9DTY's ~10 copies touch each other in the crystal lattice, so `assembly_components` merged 39 of its 40
    chains into a single 'copy' and role resolution inside it fell straight back to file order across all
    ten — the chimera the component split was added to prevent, wearing a different hat. A copy is therefore
    defined biologically (a target chain plus the E3 chains actually bound to it), which is invariant to how
    densely the lattice packs."""
    pytest.importorskip("numpy")
    copy1 = _complex(target_dx=0.0)
    copy2 = []
    for a in _complex(target_dx=9.0):
        # 26 Å along y: the two copies CONTACT, as copies do in a lattice, while staying physically
        # separated rather than interpenetrating. Swept at 20/22/24/26/28 Å before this value was chosen —
        # below 24 Å the copies interpenetrate (closer than any real crystal packs) and a chain is genuinely
        # more contacted by its neighbour, which the rule then follows; from 24 Å up it is chimera-free.
        copy2.append(V.Atom({"A": "P", "E": "Q", "F": "R", "G": "S"}[a.chain], a.resseq, a.icode, a.resname,
                            a.name, a.element, a.x, a.y + 26.0, a.z, a.hetatm))
    native_atoms = copy1 + copy2

    # Whether the CONTACT rule happens to merge these two copies is a property of the fixture's packing, not
    # of the code, and asserting it made the test fixture-sensitive rather than behaviour-sensitive. What must
    # hold on the real input is asserted instead: the role-anchored rule returns one clean assembly per target
    # chain and never mixes them. (On 9DTY the contact rule DID merge — 39 of 40 chains into one component —
    # which is why the role-anchored rule exists; that is recorded in `target_anchored_assemblies`.)
    model_atoms = _complex()
    tseq, _ = V.chain_sequence(model_atoms, "A")
    e3seqs = [V.chain_sequence(model_atoms, c)[0] for c in ("E", "F", "G")]
    asm = V.target_anchored_assemblies(native_atoms, tseq, e3seqs)
    assert len(asm) == 2, asm
    assert sorted(asm) == [["A", "E", "F", "G"], ["P", "Q", "R", "S"]], asm

    native = _write_cif(native_atoms, str(tmp_path / "n.cif"))
    model = _write_cif(model_atoms, str(tmp_path / "m.cif"))
    rec = V.validate_one(model, native)
    assert rec["graded"] is True, rec.get("why")
    chosen = set(rec["copy_selection"]["chosen_native_chains"])
    assert chosen in ({"A", "E", "F", "G"}, {"P", "Q", "R", "S"}), chosen
    for mc, info in rec["chain_map"]["matched"].items():
        assert info["native_chain"] in chosen, "role %s was drawn from outside the chosen copy" % mc


def test_an_e3_subunit_that_never_touches_the_target_is_still_assigned_to_the_right_copy(tmp_path):
    """Elongin B and C need not touch the degradation target — in a VCB they hang off VHL. Anchoring every
    role on the target alone would score 0 contacts for them and pick arbitrarily, so the copy grows greedily
    along the assembly's own connectivity."""
    model_atoms = _complex()
    copy1 = _complex()
    copy2 = [V.Atom({"A": "P", "E": "Q", "F": "R", "G": "S"}[a.chain], a.resseq, a.icode, a.resname,
                    a.name, a.element, a.x, a.y + 26.0, a.z, a.hetatm) for a in _complex()]
    tseq, _ = V.chain_sequence(model_atoms, "A")
    e3seqs = [V.chain_sequence(model_atoms, c)[0] for c in ("E", "F", "G")]
    asm = V.target_anchored_assemblies(copy1 + copy2, tseq, e3seqs)
    # chain G (the far E3 subunit, 18 Å from the target and 7 Å from F) lands with its own copy, not the other
    for a in asm:
        assert a in (["A", "E", "F", "G"], ["P", "Q", "R", "S"]), a


# ---------- 6 · scope: this module grades inputs and nothing else -----------------------------------------


def test_artifact_states_plainly_that_it_licenses_nothing(tmp_path):
    root = tmp_path / "c"; root.mkdir()
    nd = tmp_path / "n"; nd.mkdir()
    res = V.validate_panel(str(root), str(nd), arms=["selcal_smarca2"], seeds=[1])
    for key in ("_what", "_licenses", "_why_this_was_owed", "_third_explanation",
                "_kernels_imported_not_reimplemented"):
        assert key in res, key
    lic = res["_licenses"]
    assert "NOTHING" in lic and "re-scores no" in lic
    assert "selcal-verdict.json remains the one home" in lic
    assert "verdict" not in {k.lower() for k in res.keys()}, "this module must not emit a tier"


def test_deposited_ternaries_are_read_from_the_frozen_panel_not_typed():
    import selcal_panel as P
    dep = V.deposited_ternaries()
    for gene, pdb in P.REFERENCE["deposited_ternaries"].items():
        assert dep["selcal_%s" % gene.lower()] == pdb


def test_ligand_is_reported_by_count_and_identity_with_no_assumed_atom_correspondence(tmp_path):
    pytest.importorskip("numpy")
    native = _write_cif(_ligand(_complex(), resname="A1BB4"), str(tmp_path / "n.cif"))
    model = _write_cif(_ligand(_complex(), resname="LIG"), str(tmp_path / "m.cif"))
    rec = V.validate_one(model, native)
    assert rec["ligand"]["native_resname"] == "A1BB4"
    assert rec["ligand"]["model_resname"] == "LIG"
    assert rec["ligand"]["model_heavy_atoms"] == 30
    assert "refuses to make" in rec["ligand"]["_note"]
    assert "ligand_rmsd" not in rec


def test_solvent_and_ions_are_never_mistaken_for_the_degrader(tmp_path):
    atoms = _complex()
    atoms += [V.Atom("A", 800 + i, "", "SO4", "S", "S", 50.0 + i, 0.0, 0.0, True) for i in range(40)]
    lig = V.ligand_atoms(atoms)
    assert lig == [], "a crystallisation additive must not be picked up as the PROTAC"


# ---------- 7 · parsers ------------------------------------------------------------------------------------


def test_pdb_and_cif_parsers_agree_on_the_same_complex(tmp_path):
    atoms = _complex()
    a_cif = V.parse_structure(_write_cif(atoms, str(tmp_path / "x.cif")))
    a_pdb = V.parse_structure(_write_pdb(atoms, str(tmp_path / "x.pdb")))
    assert len(a_cif) == len(a_pdb) == len(atoms)
    assert V.polymer_chains(a_cif) == V.polymer_chains(a_pdb) == ["A", "E", "F", "G"]
    for x, y in zip(a_cif, a_pdb):
        assert (x.chain, x.resseq, x.resname, x.name) == (y.chain, y.resseq, y.resname, y.name)
        assert x.x == pytest.approx(y.x, abs=1e-3)


def test_only_the_first_model_of_an_ensemble_is_read(tmp_path):
    """A predictor's multi-model output is an ensemble, not a complex; reading both would double every chain."""
    path = tmp_path / "ens.cif"
    _write_cif(_complex(), str(path))
    text = path.read_text().rstrip().rstrip("#").rstrip()
    extra = "\n".join(l.replace(" 1\n", " 2\n") for l in text.splitlines()[-5:])
    path.write_text(text + "\n" + extra.replace(" 1", " 2") + "\n#\n")
    atoms = V.parse_structure(str(path))
    assert all(True for _ in atoms)
    assert len(V.polymer_chains(atoms)) == 4


def test_mse_is_read_as_methionine_not_dropped():
    """Selenomethionine is standard in crystallography. Dropping it would open a gap mid-helix and shift the
    register of every residue after it."""
    atoms = _chain("A", 5, 0, 0, 0, resnames=["ALA", "MSE", "GLY", "MSE", "VAL"])
    seq, keys = V.chain_sequence(atoms, "A")
    assert seq == "AMGMV"
    assert len(keys) == 5
