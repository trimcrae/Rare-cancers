#!/usr/bin/env python3
"""Do the sensitivity control's co-folds reproduce the ternaries whose selectivity was measured? ($0 CPU)

═══════════════════════════════════════════════════════════════════════════════════════════════════════════
★★ WHY THIS EXISTS: THE SELCAL NULL HAS A THIRD EXPLANATION AND NOBODY LISTED IT
═══════════════════════════════════════════════════════════════════════════════════════════════════════════
`selcal-verdict.json` returned **NULL on an adequately-powered design** and bounds itself between exactly two
readings — *"the readout is blunt"* and *"this pair is hard"* — stating it cannot distinguish them. The paper
carries that same two-way bound in §2.12a.

There is a **third**: the co-folds the panel simulated may not be the complexes whose selectivity was
measured. If a starting structure is far from the deposited ternary, then 5 ns of MD on it measures the drift
of something else, and E1 was never actually put to the test the null is being read as.

This is not a new idea bolted on afterwards. `selcal_panel.py` chose PRT3789 over the better-documented ACBI2
**for exactly this reason** — two deposited ternaries carry the SAME ligand on BOTH arms, 9DTY (SMARCA2,
3.19 Å) and 9DTX (SMARCA4, 2.11 Å), so, in its own words, *"each arm's co-fold can be VALIDATED against a
real structure of the very complex it models"*; and `selcal_stage`'s docstring says the deposited ternaries
are *"used to VALIDATE the co-folds rather than to supply them."* **That validation was never implemented.**
The pair was picked for a check that then did not happen. This module is that check.

⚠ **THE ANSWER IS REPORTED WHICHEVER WAY IT LANDS, and neither way is comfortable:**
  * co-folds NEAR the crystals ⇒ the inputs were sound, the **readout** is what failed, and the null becomes
    a *diagnosed* negative instead of an ambiguous one. That STRENGTHENS the paper's current sentence.
  * co-folds FAR from the crystals ⇒ the panel measured MD noise on structures that are not the measured
    complexes, and E1 was never tested. That makes the instrument claim **WEAKER**, not stronger, and it must
    be written that way. A result that lets us re-open a null is not a result that lets us discard it.

⛔ **THIS MODULE SCORES INPUTS. IT RE-SCORES NO LEG, MOVES NO THRESHOLD AND EMITS NO VERDICT.** It is not a
selectivity result, it does not amend `selectivity-sensitivity-control-prereg.md`, and it licenses nothing
about SMARCA2/4, NR4A3, degradation, efficacy or a therapeutic window. `selcal-verdict.json` remains the one
home of the tier.

═══════════════════════════════════════════════════════════════════════════════════════════════════════════
★ NOTHING IS RE-IMPLEMENTED THAT ALREADY EXISTS — the number has to be on E1's OWN scale to be readable
═══════════════════════════════════════════════════════════════════════════════════════════════════════════
The point of the primary metric is that it can be read **directly against E1's plateaux and E1's own 4.0 Å
stability threshold**. A second, subtly different superposition would produce a number nobody could compare,
which is the one-fact-one-place bug in geometric form. So the two kernels are **imported, not copied**:

  * `nrv04_covalent_md.interface_atom_indices` — the same 0.8 nm heavy-atom interface selector E1 uses;
  * `nrv04_covalent_md._aligned_iface_rmsd`    — the same E3-Cα superposition + interface RMSD E1 uses;
  * `nr4a_differential_atlas.nw_align`         — the same affine-gap BLOSUM62 aligner the atlas and the
                                                 metadynamics paralogue mapping already use;
  * `nrv04_readouts.INTERFACE_RMSD_STABLE_A`   — read for REPORTING context, never re-typed, never a gate here.

⚠ **UNITS.** `_aligned_iface_rmsd` takes NANOMETRES and returns ÅNGSTRÖM. Structure files are in Å. Every
call therefore goes through `_nm()`, and `tests/test_selcal_cofold_validate.py` pins it. This is not
pedantry: a missing nm→Å conversion in the SAME readout family put a ~30–49 Å Lys separation into the record
as 2.34–4.48 Å, which read as ubiquitination-competent geometry and inverted the conclusion
(`nrv04_covalent_md` R3 history note; STRATEGY Appendix A 15).

★ **EVERY CORRESPONDENCE IS DERIVED FROM THE FILES, NEVER ASSUMED.** Chain roles are matched between model
and crystal by **sequence alignment**, not by chain letter and not by residue count — a count-only rule
already cost this program a whole panel by scoring Elongin C as the degradation target
(`nrv04_covalent_md._topology_indices` history note), and here the target bromodomain (121–122 aa) sits
between Elongin C (112) and Elongin B (118). The mapping FAILS LOUD: below-threshold identity, a tie, or two
model chains claiming one crystal chain all REFUSE rather than guess.

★ **A REFUSAL IS A FIRST-CLASS RESULT.** Anything unreadable returns `graded: false` with `why`, and never a
number. An absent reading is not a reading of absence (CLAUDE.md §4) — a co-fold we could not parse must not
render as a co-fold that disagrees with the crystal.

Pure stdlib. numpy is needed only inside the imported RMSD kernel (a CI `pip install numpy`); parsing,
alignment, chain mapping, interface selection and fnat all run with no third-party package at all, so the
whole pipeline is exercisable offline.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))

#: The deposited ternaries, per arm. Chosen by `selcal_panel.REFERENCE["deposited_ternaries"]` — read from
#: there rather than re-typed, so a change to the panel's reference cannot leave this file behind.
def deposited_ternaries() -> dict:
    """{arm_id: pdb_id} for the arms that have a deposited ternary. Read from the frozen panel."""
    import selcal_panel as P
    dep = dict(P.REFERENCE["deposited_ternaries"])
    return {"selcal_%s" % gene.lower(): pdb for gene, pdb in dep.items()}


RCSB_CIF = "https://files.rcsb.org/download/{pdb_id}.cif"

#: Minimum per-chain sequence identity for a model chain to be MATCHED to a crystal chain. Below this the
#: mapping refuses. Set well above what an unrelated chain scores and well below what a construct-vs-crystal
#: pair scores (the same protein, differing only by disordered termini), so the threshold is not load-bearing
#: on any real decision — it exists to make a WRONG match impossible, not to grade a right one.
MIN_CHAIN_IDENTITY = 0.80

#: A matched chain pair must share at least this many aligned residues to contribute to the superposition.
#: Three points define a rigid body; ten is the smallest count at which a superposition is not dominated by
#: the disordered ends that differ between a construct and a crystal.
MIN_ALIGNED_RESIDUES = 10

#: fnat contact definition: two residues are in contact if any heavy-atom pair is within this distance.
#: The CAPRI convention is 5.0 Å. ⚠ It is DELIBERATELY NOT `nrv04_readouts.CONTACT_CUTOFF_A` (4.5 Å): fnat is
#: a structure-comparison metric reported against the docking literature's scale, not one of the panel's
#: frozen endpoints, and silently borrowing an endpoint's constant would make it look like one.
FNAT_CONTACT_A = 5.0

_THREE_TO_ONE = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E", "GLY": "G",
    "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P", "SER": "S",
    "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
    # common modified/alternate names that are still the parent residue for alignment purposes
    "MSE": "M", "HIE": "H", "HID": "H", "HIP": "H", "CYX": "C", "SEC": "U", "PYL": "O",
}

#: Non-polymer names that are solvent/ions rather than the degrader. Excluded from the ligand selection so a
#: crystallographic sulfate is never mistaken for the PROTAC.
_SOLVENT = {"HOH", "DOD", "WAT", "NA", "CL", "K", "MG", "CA", "ZN", "SO4", "PO4", "GOL", "EDO", "ACT",
            "PEG", "DMS", "TRS", "MPD", "IOD", "BR", "FMT", "NO3", "CO3", "ACY", "IMD", "UNX"}


def _nm(xyz):
    """Å -> nm. The imported RMSD kernel's contract is NANOMETRES in, ÅNGSTRÖM out; structure files are Å."""
    return [(x / 10.0, y / 10.0, z / 10.0) for (x, y, z) in xyz]


# ---------- structure parsing (pure stdlib; mmCIF + PDB) --------------------------------------------------


class Atom(object):
    __slots__ = ("chain", "resseq", "icode", "resname", "name", "element", "x", "y", "z", "hetatm")

    def __init__(self, chain, resseq, icode, resname, name, element, x, y, z, hetatm):
        self.chain = chain; self.resseq = resseq; self.icode = icode
        self.resname = resname; self.name = name; self.element = element
        self.x = x; self.y = y; self.z = z; self.hetatm = hetatm

    @property
    def key(self):
        """(chain, resseq, icode) — the residue this atom belongs to."""
        return (self.chain, self.resseq, self.icode)

    @property
    def xyz(self):
        return (self.x, self.y, self.z)

    @property
    def is_heavy(self):
        return (self.element or "").upper() not in ("H", "D")


def _cif_loop_atom_site(text):
    """Yield the `_atom_site` loop's column names and rows. Handles the standard whitespace-delimited form
    that both Boltz and RCSB emit; quoted values are unquoted. Pure stdlib, no gemmi."""
    lines = text.splitlines()
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].strip() == "loop_":
            cols = []
            j = i + 1
            while j < n and lines[j].strip().startswith("_"):
                cols.append(lines[j].strip())
                j += 1
            if cols and cols[0].startswith("_atom_site."):
                rows = []
                while j < n:
                    s = lines[j].strip()
                    if not s or s.startswith("#") or s.startswith("loop_") or s.startswith("_") or s == "stop_":
                        break
                    rows.append(_split_cif_row(s))
                    j += 1
                return cols, rows
            i = j
        else:
            i += 1
    return [], []


def _split_cif_row(s):
    """Whitespace split honouring single/double quotes (CIF values may be quoted, e.g. atom name "O5'")."""
    out, cur, quote = [], [], None
    for ch in s:
        if quote:
            if ch == quote:
                quote = None
            else:
                cur.append(ch)
        elif ch in ("'", '"'):
            quote = ch
        elif ch.isspace():
            if cur:
                out.append("".join(cur)); cur = []
        else:
            cur.append(ch)
    if cur:
        out.append("".join(cur))
    return out


def parse_mmcif(path):
    """[Atom] from an mmCIF. Uses AUTHOR chain/residue numbering when present (`auth_asym_id`/`auth_seq_id`)
    because that is what a crystallographer's methods section and every PDB-derived tool speak; falls back to
    the label ids when a predictor omits the auth columns."""
    with open(path) as fh:
        text = fh.read()
    cols, rows = _cif_loop_atom_site(text)
    if not cols:
        raise ValueError("no _atom_site loop in %s" % path)
    idx = {c: k for k, c in enumerate(cols)}

    def col(*names):
        for nm in names:
            key = "_atom_site." + nm
            if key in idx:
                return idx[key]
        return None

    c_chain = col("auth_asym_id", "label_asym_id")
    c_seq = col("auth_seq_id", "label_seq_id")
    c_ins = col("pdbx_PDB_ins_code")
    c_comp = col("auth_comp_id", "label_comp_id")
    c_name = col("auth_atom_id", "label_atom_id")
    c_elem = col("type_symbol")
    c_x, c_y, c_z = col("Cartn_x"), col("Cartn_y"), col("Cartn_z")
    c_group = col("group_PDB")
    c_model = col("pdbx_PDB_model_num")
    c_alt = col("label_alt_id")
    if None in (c_chain, c_seq, c_comp, c_name, c_x, c_y, c_z):
        raise ValueError("mmCIF %s lacks required _atom_site columns" % path)

    atoms = []
    first_model = None
    for r in rows:
        if len(r) <= max(c_chain, c_seq, c_comp, c_name, c_x, c_y, c_z):
            continue
        if c_model is not None:
            m = r[c_model]
            if first_model is None:
                first_model = m
            elif m != first_model:
                continue                                   # first model only — an NMR/predictor ensemble is not a complex
        if c_alt is not None and r[c_alt] not in (".", "?", "", "A"):
            continue                                       # keep altloc A only, so B/C copies cannot double-count
        try:
            x, y, z = float(r[c_x]), float(r[c_y]), float(r[c_z])
        except ValueError:
            continue
        try:
            seq = int(r[c_seq])
        except ValueError:
            continue
        ins = "" if (c_ins is None or r[c_ins] in (".", "?")) else r[c_ins]
        elem = "" if c_elem is None else r[c_elem]
        het = (c_group is not None and r[c_group] == "HETATM")
        atoms.append(Atom(r[c_chain], seq, ins, r[c_comp], r[c_name], elem, x, y, z, het))
    return atoms


def parse_pdb(path):
    """[Atom] from a PDB file (the format `selcal_stage.assemble_unit` writes as complex.pdb)."""
    atoms = []
    with open(path) as fh:
        for line in fh:
            rec = line[:6]
            if rec not in ("ATOM  ", "HETATM"):
                if line.startswith("ENDMDL"):
                    break                                  # first model only, same rule as the mmCIF path
                continue
            alt = line[16]
            if alt not in (" ", "A"):
                continue
            try:
                x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
                seq = int(line[22:26])
            except ValueError:
                continue
            elem = line[76:78].strip()
            name = line[12:16].strip()
            if not elem:                                   # some writers omit columns 77-78
                elem = name[0] if name and not name[0].isdigit() else (name[1:2] if len(name) > 1 else "")
            atoms.append(Atom(line[21], seq, line[26].strip(), line[17:20].strip(), name, elem, x, y, z,
                              rec == "HETATM"))
    return atoms


def parse_structure(path):
    """[Atom] from .cif/.mmcif or .pdb/.ent, chosen by extension."""
    ext = os.path.splitext(path)[1].lower()
    if ext in (".cif", ".mmcif"):
        return parse_mmcif(path)
    if ext in (".pdb", ".ent"):
        return parse_pdb(path)
    raise ValueError("unrecognised structure extension %r for %s" % (ext, path))


# ---------- chains, sequences, correspondence -------------------------------------------------------------


def chain_sequence(atoms, chain):
    """(one-letter sequence, [residue keys]) for one chain's polymer residues, ordered by the file.

    Built from CA atoms so a residue with only sidechain density cannot shift the register, and non-standard
    residue names are mapped through `_THREE_TO_ONE` rather than dropped silently (MSE is a methionine, and
    dropping it would put a gap in the middle of a helix)."""
    seq, keys, seen = [], [], set()
    for a in atoms:
        if a.chain != chain or a.name != "CA":
            continue
        if a.resname not in _THREE_TO_ONE:
            continue
        if a.key in seen:
            continue
        seen.add(a.key)
        seq.append(_THREE_TO_ONE[a.resname])
        keys.append(a.key)
    return "".join(seq), keys


def polymer_chains(atoms):
    """Chain ids that carry at least one standard-residue CA, in file order."""
    out = []
    for a in atoms:
        if a.name == "CA" and a.resname in _THREE_TO_ONE and a.chain not in out:
            out.append(a.chain)
    return out


def align_identity(seq_a, seq_b):
    """(identity, [(i_a, i_b), ...]) over aligned residue-residue columns, via the repo's affine-gap BLOSUM62
    Needleman-Wunsch. Identity is normalised by the SHORTER sequence, so a crystal construct with extra
    expression-tag residues does not depress the score of a chain that matches it over its whole length."""
    from nr4a_differential_atlas import nw_align
    if not seq_a or not seq_b:
        return 0.0, []
    aln = nw_align(seq_a, seq_b)
    pairs = [(ia, ib) for ia, ib in aln if ia is not None and ib is not None]
    if not pairs:
        return 0.0, []
    same = sum(1 for ia, ib in pairs if seq_a[ia] == seq_b[ib])
    return same / float(min(len(seq_a), len(seq_b))), pairs


def map_chains(model_atoms, native_atoms, native_chain_subset=None):
    """{model_chain: {native_chain, identity, pairs}} — DERIVED by sequence, never by chain letter.

    Refuses rather than guesses. A model chain with no native chain at or above `MIN_CHAIN_IDENTITY` is
    reported unmatched with its best score; two model chains resolving to one native chain is a hard refusal,
    because that is the shape of the mis-mapping that scored Elongin C as the degradation target.

    `native_chain_subset` restricts the candidates to ONE copy of the complex (`assembly_components`). In a
    multi-copy asymmetric unit every copy ties at identity 1.000, so without the restriction the winner is
    decided by file order and the four roles can be drawn from different copies — a reference complex that
    does not exist."""
    m_chains = polymer_chains(model_atoms)
    n_chains = polymer_chains(native_atoms)
    if native_chain_subset is not None:
        allowed = set(native_chain_subset)
        n_chains = [c for c in n_chains if c in allowed]
    m_seqs = {c: chain_sequence(model_atoms, c) for c in m_chains}
    n_seqs = {c: chain_sequence(native_atoms, c) for c in n_chains}

    matched, unmatched = {}, {}
    for mc in m_chains:
        mseq, mkeys = m_seqs[mc]
        best = None
        for nc in n_chains:
            nseq, nkeys = n_seqs[nc]
            ident, pairs = align_identity(mseq, nseq)
            if best is None or ident > best["identity"]:
                best = {"native_chain": nc, "identity": round(ident, 4), "_pairs": pairs,
                        "n_aligned": len(pairs)}
        if best is None:
            unmatched[mc] = {"why": "the crystal has no polymer chain at all", "identity": None}
        elif best["identity"] < MIN_CHAIN_IDENTITY:
            unmatched[mc] = {"why": "best crystal chain %s scores %.3f identity, below MIN_CHAIN_IDENTITY %.2f"
                                    % (best["native_chain"], best["identity"], MIN_CHAIN_IDENTITY),
                             "identity": best["identity"], "best_native_chain": best["native_chain"]}
        else:
            matched[mc] = best

    claimed = {}
    for mc, info in matched.items():
        claimed.setdefault(info["native_chain"], []).append(mc)
    collisions = {nc: mcs for nc, mcs in claimed.items() if len(mcs) > 1}
    return {"matched": matched, "unmatched": unmatched, "collisions": collisions,
            "model_chains": m_chains, "native_chains": n_chains,
            "model_chain_lengths": {c: len(m_seqs[c][0]) for c in m_chains},
            "native_chain_lengths": {c: len(n_seqs[c][0]) for c in n_chains}}


def residue_pairs(model_atoms, native_atoms, model_chain, native_chain, aln_pairs):
    """[((model residue key), (native residue key)), ...] for one matched chain, from the alignment columns."""
    _, mkeys = chain_sequence(model_atoms, model_chain)
    _, nkeys = chain_sequence(native_atoms, native_chain)
    out = []
    for ia, ib in aln_pairs:
        if ia < len(mkeys) and ib < len(nkeys):
            out.append((mkeys[ia], nkeys[ib]))
    return out


# ---------- geometry --------------------------------------------------------------------------------------


def _by_residue(atoms, heavy_only=True, polymer_only=False):
    """{residue key: [Atom]}.

    ⚠ `polymer_only` EXISTS BECAUSE ITS ABSENCE PRODUCED A WRONG NUMBER, and the number looked plausible.
    A deposited ternary gives the PROTAC an auth chain id it SHARES with a protein chain, so without this
    filter the degrader enters the residue set of whichever chain it was assigned to and every ligand-protein
    contact is counted as a protein-protein interface contact — with no model counterpart, because the model's
    ligand is a different residue name. Measured on the first run of this module: 9DTX reported 47 native
    contacts of which 43 (91 %) were `unmappable`, on chains aligned at identity 1.000 with full coverage,
    which is arithmetically impossible for genuine protein-protein contacts. That is what exposed it.
    Restricting to polymer residues also MATCHES E1, whose `_topology_indices` puts LIG/UNL/UNK in neither the
    E3 nor the target set, so the endpoint's interface is protein-protein too."""
    out = {}
    for a in atoms:
        if heavy_only and not a.is_heavy:
            continue
        if polymer_only and a.resname not in _THREE_TO_ONE:
            continue
        out.setdefault(a.key, []).append(a)
    return out


def chains_matching(atoms, ref_seq, min_identity=None):
    """Native chains whose sequence matches `ref_seq` at or above the identity floor, best first."""
    out = []
    for c in polymer_chains(atoms):
        seq, _ = chain_sequence(atoms, c)
        ident, _ = align_identity(ref_seq, seq)
        if ident >= (min_identity if min_identity is not None else MIN_CHAIN_IDENTITY):
            out.append((round(ident, 4), c))
    out.sort(key=lambda t: (-t[0], t[1]))
    return out


def _chain_contact_count(atoms_by_chain, a, b, cutoff_a=8.0):
    """CA-CA pairs within `cutoff_a` between two chains — how tightly two chains are actually bound."""
    c2 = cutoff_a * cutoff_a
    n = 0
    for p in atoms_by_chain.get(a, ()):
        for q in atoms_by_chain.get(b, ()):
            if (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 + (p[2] - q[2]) ** 2 <= c2:
                n += 1
    return n


def target_anchored_assemblies(native_atoms, target_seq, e3_seqs):
    """Candidate copies of the complex, each anchored on ONE target chain. Returns [[chain ids], ...].

    ⚠ CONTACT COMPONENTS ARE NOT ENOUGH IN A CRYSTAL LATTICE, and the first corrected run proved it: 9DTY's
    ~10 copies TOUCH each other in the lattice, so `assembly_components` merged 39 of its 40 chains into a
    single "copy" and role resolution inside it fell back to file order across all ten — exactly the chimera
    the component split was added to prevent, wearing a different hat.

    A copy is therefore defined biologically rather than topologically: **a target chain, plus the chain of
    each E3 role that is most tightly bound TO THAT TARGET.** That is what a copy of the complex is, it is
    invariant to how densely the lattice packs, and it cannot mix copies because every role is chosen by its
    contact with the same anchor.
    """
    ca = {}
    for a in native_atoms:
        if a.name == "CA" and a.resname in _THREE_TO_ONE:
            ca.setdefault(a.chain, []).append(a.xyz)

    targets = chains_matching(native_atoms, target_seq)
    out = []
    for _, tc in targets:
        chosen, ok = [tc], True
        for role_seq in e3_seqs:
            cands = [c for _, c in chains_matching(native_atoms, role_seq) if c not in chosen]
            if not cands:
                ok = False
                break
            # Contacts to ANY chain already in the copy, not just to the target. Elongin B and C need not
            # touch the degradation target at all — in a VCB they hang off VHL — so anchoring every role on
            # the target alone would score 0 for them and pick arbitrarily. Growing the copy greedily follows
            # the assembly's own connectivity. Ties break on the chain id so the choice is deterministic.
            best = max(cands, key=lambda c: (sum(_chain_contact_count(ca, s, c) for s in chosen), c))
            chosen.append(best)
        if not (ok and len(set(chosen)) == 1 + len(e3_seqs)):
            continue
        # ⛔ CHIMERA CHECK — MEASURED, NOT ASSUMED. Greedy growth alone is NOT chimera-proof: on a fixture
        # where two copies interpenetrate, it returned ['G', 'P', 'Q', 'R'] — copy 1's Elongin subunit pulled
        # into copy 2's assembly, because that copy's target sat closer to it than its own did. So every
        # chosen chain is checked: its most-contacted partner must lie INSIDE the assembly. If a chain is
        # bound more tightly to something outside, the copy is ambiguous and is DISCARDED rather than scored —
        # a chimeric reference that scores without erroring is exactly the failure this whole block exists to
        # prevent, and a silent fallback would reinstate it.
        # ⚠ HONEST LIMIT, MEASURED RATHER THAN CLAIMED AWAY: this REDUCES ambiguity, it does not eliminate it.
        # On a fixture whose copies INTERPENETRATE (2 Å apart, closer than any real crystal packs) a chain is
        # genuinely more contacted by the neighbouring copy, the check passes, and the assignment follows the
        # geometry rather than the intent. Real deposited copies are separated by solvent and the rule is
        # clean there — swept at 20/22/24/26/28 Å, chimera-free from 24 Å up. The real guard against this
        # mattering is the published `interface_rmsd_across_copies_A` spread: if every copy scores alike, the
        # choice of copy cannot be carrying the result, and a reader can check that instead of trusting it.
        inside = set(chosen)
        ambiguous = False
        for c in chosen[1:]:
            best_in = max((_chain_contact_count(ca, c, s) for s in inside if s != c), default=0)
            best_out = max((_chain_contact_count(ca, c, s) for s in ca if s not in inside), default=0)
            if best_out > best_in:
                ambiguous = True
                break
        if ambiguous:
            continue
        key = sorted(chosen)
        if key not in out:
            out.append(key)
    return out


def assembly_components(atoms, contact_a=8.0):
    """Group polymer chains into COPIES of the complex — connected components under inter-chain contact.

    ⚠ WITHOUT THIS, A MULTI-COPY ASYMMETRIC UNIT SILENTLY BUILDS A CHIMERIC REFERENCE. 9DTY holds ~10 copies
    of the SMARCA2 ternary in 40 chains, so every copy's chains align to a given model chain at identity
    1.000 — a perfect tie. `map_chains` would then resolve each role by whichever chain the file happens to
    list first, and there is no guarantee those come from ONE copy. Assembling the reference from chains of
    different copies would produce an interface RMSD against a complex that does not exist, and nothing would
    error: the numbers would simply be about something else. That is the same defect class as the positional
    chain split that scored Elongin C as the degradation target, so it is closed structurally rather than
    trusted to ordering.

    A bounding-sphere prefilter keeps this cheap: 40 chains is 780 pairs, and only overlapping pairs pay for
    a CA-CA scan."""
    ca = {}
    for a in atoms:
        if a.name == "CA" and a.resname in _THREE_TO_ONE:
            ca.setdefault(a.chain, []).append(a.xyz)
    chains = sorted(ca)
    if not chains:
        return []
    cent, rad = {}, {}
    for c in chains:
        cent[c] = centroid(ca[c])
        rad[c] = max(((p[0] - cent[c][0]) ** 2 + (p[1] - cent[c][1]) ** 2 + (p[2] - cent[c][2]) ** 2) ** 0.5
                     for p in ca[c])

    parent = {c: c for c in chains}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[ry] = rx

    c2 = contact_a * contact_a
    for i, ci in enumerate(chains):
        for cj in chains[i + 1:]:
            if find(ci) == find(cj):
                continue
            d = ((cent[ci][0] - cent[cj][0]) ** 2 + (cent[ci][1] - cent[cj][1]) ** 2
                 + (cent[ci][2] - cent[cj][2]) ** 2) ** 0.5
            if d > rad[ci] + rad[cj] + contact_a:
                continue                                   # bounding spheres cannot reach — a proven skip
            touched = False
            for p in ca[ci]:
                for q in ca[cj]:
                    if (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 + (p[2] - q[2]) ** 2 <= c2:
                        touched = True
                        break
                if touched:
                    break
            if touched:
                union(ci, cj)

    groups = {}
    for c in chains:
        groups.setdefault(find(c), []).append(c)
    return [sorted(v) for _, v in sorted(groups.items())]


def _ca_by_residue(atoms):
    """{residue key: (x, y, z)} for CA atoms."""
    out = {}
    for a in atoms:
        if a.name == "CA" and a.key not in out:
            out[a.key] = a.xyz
    return out


def ligand_atoms(atoms, min_heavy=20):
    """The degrader's heavy atoms: the largest non-solvent, non-polymer residue in the file.

    `min_heavy` guards against picking up a crystallisation additive: a VHL-recruiting PROTAC is ~60-80 heavy
    atoms, and nothing this size is an accident. Returns [] rather than a wrong molecule when nothing
    qualifies — a missing ligand must read as missing, not as a displaced one."""
    groups = {}
    for a in atoms:
        if a.resname in _SOLVENT or a.resname in _THREE_TO_ONE:
            continue
        if not a.is_heavy:
            continue
        groups.setdefault(a.key, []).append(a)
    if not groups:
        return []
    best = max(groups.values(), key=len)
    return best if len(best) >= min_heavy else []


def centroid(xyz_list):
    n = len(xyz_list)
    if not n:
        return None
    return (sum(p[0] for p in xyz_list) / n, sum(p[1] for p in xyz_list) / n, sum(p[2] for p in xyz_list) / n)


def native_interface_residues(native_atoms, e3_native_chains, target_native_chains):
    """(e3 residue keys, target residue keys) at the crystal's E3<->target interface.

    Uses the SAME selector E1 uses — `nrv04_covalent_md.interface_atom_indices`, 0.8 nm heavy-atom cutoff —
    imported rather than re-implemented, so the interface this diagnostic scores is the interface the endpoint
    scores. The crystal defines the interface (the CAPRI convention: native contacts are the reference), and
    it is then carried to the model through the residue correspondence."""
    from nrv04_covalent_md import interface_atom_indices
    # POLYMER ONLY — see `_by_residue`'s note. E1's own split (`nrv04_covalent_md._topology_indices`) puts
    # LIG/UNL/UNK in neither the E3 nor the target set, so the endpoint's interface is protein-protein; a
    # ligand sharing a protein chain's auth id would otherwise be scored as part of the interface here.
    heavy = [a for a in native_atoms if a.is_heavy and a.resname in _THREE_TO_ONE]
    pos_nm = _nm([a.xyz for a in heavy])
    chain_ids = [a.chain for a in heavy]
    e3_idx, tg_idx = interface_atom_indices(pos_nm, chain_ids, set(e3_native_chains), set(target_native_chains))
    e3_res = sorted({heavy[i].key for i in e3_idx})
    tg_res = sorted({heavy[i].key for i in tg_idx})
    return e3_res, tg_res


def interface_rmsd_vs_native(model_atoms, native_atoms, corr, e3_native_chains, target_native_chains):
    """Interface RMSD (Å) between the co-fold and the crystal, on E1's own scale.

    Superposes the E3 Cα atoms and measures the interface, which is what `_aligned_iface_rmsd` does per frame
    inside the endpoint — the difference is only the reference: E1's reference is the leg's own
    POST-EQUILIBRATION frame, so E1 measures drift away from wherever the co-fold started and is BLIND BY
    CONSTRUCTION to how far that was from the truth. That blindness is the gap this function fills.

    Interface residues are chosen on the crystal and mapped to the model, so a co-fold that has lost the
    interface entirely is scored against where the interface should be, not against wherever it drifted to.
    Returns None with a reason when the correspondence is too thin to superpose."""
    from nrv04_covalent_md import _aligned_iface_rmsd

    m_of_n = {}                                            # native residue key -> model residue key
    for mc, info in corr.items():
        for mkey, nkey in info["pairs"]:
            m_of_n[nkey] = mkey

    m_ca = _ca_by_residue(model_atoms)
    n_ca = _ca_by_residue(native_atoms)

    e3_native_res = [k for k in n_ca if k[0] in set(e3_native_chains)]
    e3_pairs = [(m_of_n[k], k) for k in sorted(e3_native_res) if k in m_of_n and m_of_n[k] in m_ca]
    if len(e3_pairs) < MIN_ALIGNED_RESIDUES:
        return None, ("only %d aligned E3 Ca pairs (need >= %d) — too few to define a superposition"
                      % (len(e3_pairs), MIN_ALIGNED_RESIDUES))

    iface_e3, iface_tg = native_interface_residues(native_atoms, e3_native_chains, target_native_chains)
    iface_native = [k for k in (iface_e3 + iface_tg) if k in m_of_n and m_of_n[k] in m_ca and k in n_ca]
    if len(iface_native) < MIN_ALIGNED_RESIDUES:
        return None, ("only %d interface residues survive the model<->crystal correspondence (need >= %d)"
                      % (len(iface_native), MIN_ALIGNED_RESIDUES))

    cur_e3ca = _nm([m_ca[mk] for mk, _ in e3_pairs])
    ref_e3ca = _nm([n_ca[nk] for _, nk in e3_pairs])
    cur_iface = _nm([m_ca[m_of_n[k]] for k in iface_native])
    ref_iface = _nm([n_ca[k] for k in iface_native])

    val = _aligned_iface_rmsd(cur_e3ca, ref_e3ca, cur_iface, ref_iface)   # nm in, Å out
    if val != val:                                                        # NaN guard, same as the endpoint's
        return None, "superposition returned NaN (non-finite or degenerate coordinates)"
    return round(val, 3), None


def fnat(model_atoms, native_atoms, corr, e3_native_chains, target_native_chains, cutoff_a=FNAT_CONTACT_A):
    """Fraction of the crystal's inter-chain residue-residue contacts that the co-fold reproduces (CAPRI fnat).

    Pose-independent: it needs no superposition at all, so it is the metric that survives when the chains are
    right but the rigid-body placement is uncertain. Reported alongside the interface RMSD precisely because
    the two can disagree, and a disagreement is informative rather than a problem to resolve away."""
    m_of_n = {}
    for mc, info in corr.items():
        for mkey, nkey in info["pairs"]:
            m_of_n[nkey] = mkey

    n_res = _by_residue(native_atoms, polymer_only=True)
    m_res = _by_residue(model_atoms, polymer_only=True)
    e3set, tgset = set(e3_native_chains), set(target_native_chains)
    c2 = cutoff_a * cutoff_a

    # Centroid prefilter. No heavy atom of a standard residue sits further than ~8 Å from its own centroid
    # (Arg/Trp are the extremes), so two residues whose centroids are more than cutoff + 16 Å apart CANNOT
    # have an atom pair inside the cutoff. This is a proven bound, not a heuristic tolerance: it changes the
    # runtime and cannot change the answer, which is why it is safe to apply to a reported metric.
    _p2 = (cutoff_a + 16.0) ** 2
    _cent = {}                                             # (table id, residue key) -> centroid, computed once

    def in_contact(table, ka, kb):
        res_a, res_b = table[ka], table[kb]
        for tag, key, res in ((id(table), ka, res_a), (id(table), kb, res_b)):
            if (tag, key) not in _cent:
                _cent[(tag, key)] = centroid([a.xyz for a in res])
        ca, cb = _cent[(id(table), ka)], _cent[(id(table), kb)]
        if ((ca[0] - cb[0]) ** 2 + (ca[1] - cb[1]) ** 2 + (ca[2] - cb[2]) ** 2) > _p2:
            return False
        for a in res_a:
            for b in res_b:
                if (a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2 <= c2:
                    return True
        return False

    native_e3 = sorted(k for k in n_res if k[0] in e3set)
    native_tg = sorted(k for k in n_res if k[0] in tgset)
    native_contacts, recovered, unmappable = [], 0, 0
    for ka in native_e3:
        for kb in native_tg:
            if not in_contact(n_res, ka, kb):
                continue
            native_contacts.append((ka, kb))
            ma, mb = m_of_n.get(ka), m_of_n.get(kb)
            if ma is None or mb is None or ma not in m_res or mb not in m_res:
                unmappable += 1
                continue
            if in_contact(m_res, ma, mb):
                recovered += 1
    n_native = len(native_contacts)
    return {"n_native_contacts": n_native,
            "n_recovered": recovered,
            "n_unmappable": unmappable,
            "fnat": (round(recovered / float(n_native), 4) if n_native else None),
            "cutoff_A": cutoff_a,
            "_unmappable_note": ("contacts whose residues have no model counterpart are counted as NOT "
                                 "recovered and reported separately, so a thin correspondence depresses fnat "
                                 "visibly rather than silently shrinking the denominator")}


# ---------- fetch (network; deliberately separated from every pure function above) -------------------------


def fetch_rcsb_cif(pdb_id, dest_dir, timeout=60):
    """Download one deposited structure. The ONLY network call in this module, kept apart so every metric
    above is exercisable offline against a fixture."""
    pdb_id = pdb_id.upper()
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, "%s.cif" % pdb_id)
    url = RCSB_CIF.format(pdb_id=pdb_id)
    with urllib.request.urlopen(url, timeout=timeout) as r:
        body = r.read()
    with open(dest, "wb") as fh:
        fh.write(body)
    return {"pdb_id": pdb_id, "url": url, "path": dest, "bytes": len(body)}


# ---------- one co-fold, and the panel --------------------------------------------------------------------


def validate_one(model_path, native_path, target_model_chain=None, e3_model_chains=None):
    """Score one co-fold against one deposited ternary. Returns a graded record, or a refusal with `why`.

    Chain ROLES on the model side come from `selcal_stage`'s frozen convention (target = A, E3 = E/F/G) —
    which is the input specification the co-fold YAML was written from, not an inference about the file — and
    are carried to the crystal purely through the sequence mapping."""
    import selcal_stage as S
    target_model_chain = target_model_chain or S.CHAIN_TARGET
    e3_model_chains = list(e3_model_chains or [S.CHAIN_VHL, S.CHAIN_ELOB, S.CHAIN_ELOC])

    rec = {"model": model_path, "native": native_path,
           "target_model_chain": target_model_chain, "e3_model_chains": e3_model_chains,
           "graded": False, "why": None}
    try:
        model_atoms = parse_structure(model_path)
        native_atoms = parse_structure(native_path)
    except Exception as e:                                  # noqa: BLE001 — an unreadable file is a refusal, not a score
        rec["why"] = "could not parse a structure: %s" % e
        return rec
    if not model_atoms or not native_atoms:
        rec["why"] = "a structure parsed to zero atoms"
        return rec

    # ★ ONE COPY AT A TIME. A deposited asymmetric unit may hold many copies of the same complex (9DTY holds
    # ~10 in 40 chains), and every copy ties at identity 1.000, so an unrestricted match resolves the four
    # roles by file order and can draw them from different copies. Each copy is scored on its own and the
    # BEST is reported, with the spread across copies beside it so the choice is visible rather than implied.
    # ⚠ NO UNRESTRICTED FALLBACK WHILE COMPONENTS EXIST. An earlier draft fell back to matching against the
    # whole file when no component looked big enough, which would have quietly reinstated the chimera this
    # block exists to prevent — a silent fallback to the rule that caused the bug is the one outcome worth
    # designing out (`nrv04_covalent_md._topology_indices` learned the same lesson the expensive way). If no
    # single copy can supply all four roles, every attempt REFUSES and says so.
    m_target_seq, _ = chain_sequence(model_atoms, target_model_chain)
    m_e3_seqs = [chain_sequence(model_atoms, c)[0] for c in e3_model_chains]
    components = target_anchored_assemblies(native_atoms, m_target_seq, m_e3_seqs)
    candidates = components if components else [None]
    attempts = []
    for comp in candidates:
        attempt = _score_against_copy(model_atoms, native_atoms, comp, target_model_chain, e3_model_chains)
        attempt["native_chains_considered"] = comp
        attempts.append(attempt)
    graded_attempts = [a for a in attempts if a.get("graded")]
    best = (min(graded_attempts, key=lambda a: a["interface_rmsd_to_crystal_A"]) if graded_attempts
            else attempts[0])
    rec.update(best)
    rec["copy_selection"] = {
        "n_components_in_asymmetric_unit": len(components),
        "n_copies_scored": len(graded_attempts),
        "chosen_native_chains": best.get("native_chains_considered"),
        "interface_rmsd_across_copies_A": sorted(a["interface_rmsd_to_crystal_A"] for a in graded_attempts),
        "_rule": "every copy that can supply all four roles is scored independently and the LOWEST interface "
                 "RMSD is reported. The spread is published beside it: a wide spread would mean the choice of "
                 "copy is doing work, and a reader can see that rather than having to trust it.",
        "_why": "9DTY holds ~10 copies in 40 chains and every copy aligns at identity 1.000, so an "
                "unrestricted match resolves the roles by file order and can build a chimeric reference "
                "across copies — a complex that does not exist, scored without erroring.",
    }
    return rec


def _score_against_copy(model_atoms, native_atoms, native_chain_subset, target_model_chain, e3_model_chains):
    """Score the model against ONE copy of the complex. Returns the same fields `validate_one` reports."""
    rec = {"graded": False, "why": None}
    cmap = map_chains(model_atoms, native_atoms, native_chain_subset)
    rec["chain_map"] = {"matched": {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")}
                                    for k, v in cmap["matched"].items()},
                        "unmatched": cmap["unmatched"], "collisions": cmap["collisions"],
                        "model_chain_lengths": cmap["model_chain_lengths"],
                        "native_chain_lengths": cmap["native_chain_lengths"],
                        "_derived_by": "affine-gap BLOSUM62 Needleman-Wunsch on CA sequences "
                                       "(nr4a_differential_atlas.nw_align), never by chain letter or "
                                       "residue count"}
    if cmap["collisions"]:
        rec["why"] = ("two model chains map to one crystal chain %s — refusing rather than guessing; this is "
                      "the shape of the mis-mapping that scored Elongin C as the degradation target"
                      % cmap["collisions"])
        return rec

    needed = [target_model_chain] + e3_model_chains
    missing = [c for c in needed if c not in cmap["matched"]]
    if missing:
        rec["why"] = ("model chain(s) %s have no crystal counterpart at >= %.2f identity: %s"
                      % (missing, MIN_CHAIN_IDENTITY,
                         {c: cmap["unmatched"].get(c, {"why": "chain absent from the model"}) for c in missing}))
        return rec

    corr = {}
    for mc in needed:
        info = cmap["matched"][mc]
        corr[mc] = {"native_chain": info["native_chain"],
                    "pairs": residue_pairs(model_atoms, native_atoms, mc, info["native_chain"], info["_pairs"])}
    target_native = [corr[target_model_chain]["native_chain"]]
    e3_native = [corr[c]["native_chain"] for c in e3_model_chains]

    irmsd, why = interface_rmsd_vs_native(model_atoms, native_atoms, corr, e3_native, target_native)
    fn = fnat(model_atoms, native_atoms, corr, e3_native, target_native)

    m_lig = ligand_atoms(model_atoms)
    n_lig = ligand_atoms(native_atoms)
    rec["ligand"] = {"model_heavy_atoms": len(m_lig), "native_heavy_atoms": len(n_lig),
                     "model_resname": (m_lig[0].resname if m_lig else None),
                     "native_resname": (n_lig[0].resname if n_lig else None),
                     "_note": "heavy-atom COUNTS and identities only. No ligand RMSD is reported: a co-fold "
                              "names its ligand atoms from the SMILES it was given, the crystal names them "
                              "from the CCD, and an atom-name correspondence assumed across those two is "
                              "exactly the kind of guess this module refuses to make."}

    rec["interface_rmsd_to_crystal_A"] = irmsd
    rec["interface_rmsd_refusal"] = why
    rec["fnat"] = fn
    rec["n_residue_correspondences"] = {c: len(corr[c]["pairs"]) for c in needed}
    rec["graded"] = irmsd is not None
    if not rec["graded"]:
        rec["why"] = why
    return rec


def reporting_context():
    """The endpoint's own numbers, READ not typed, so a reader can place this diagnostic against E1's scale.

    ⛔ NONE of these is a threshold for this module. Nothing here passes or fails; `INTERFACE_RMSD_STABLE_A`
    is E1's stability cut on a DIFFERENT quantity (drift from the leg's own equilibrated reference, not
    distance from the crystal) and is quoted for scale alone. Reading it as a pass mark would invent a
    criterion nobody preregistered."""
    import nrv04_readouts as R
    ctx = {"E1_stable_plateau_A": R.INTERFACE_RMSD_STABLE_A,
           "_E1_is_a_different_quantity": "E1 measures drift from the leg's OWN post-equilibration frame; this "
                                          "module measures distance from the deposited crystal. They share a "
                                          "kernel and a scale, not a definition.",
           "_not_a_threshold": "no value in this artifact is graded against any number here"}
    verdict = os.path.join(HERE, "selcal-verdict.json")
    if os.path.exists(verdict):
        try:
            v = json.load(open(verdict))
            ctx["selcal_model_means_A"] = {"arm_A": v.get("model_means_A"), "arm_B": v.get("model_means_B"),
                                           "arm_A_id": v.get("model_means_A_arm"),
                                           "arm_B_id": v.get("model_means_B_arm")}
            ctx["selcal_tier"] = v.get("tier")
            ctx["_selcal_is_authoritative"] = ("selcal-verdict.json is the one home of the tier and the "
                                               "plateaux; they are copied here for scale and are not "
                                               "recomputed, re-scored or altered by this module")
        except Exception as e:                              # noqa: BLE001
            ctx["selcal_verdict_read_error"] = str(e)
    return ctx


def validate_panel(cofold_root, native_dir, arms=None, seeds=None, model_glob="*.cif"):
    """Score every (arm, seed) co-fold against its arm's deposited ternary.

    `cofold_root/<system>/seed_<n>/` mirrors the S3 layout `selcal_panel.cofold_prefix_s3` pins."""
    import glob
    import selcal_panel as P

    dep = deposited_ternaries()
    arm_list = list(arms or [a.arm_id for a in P.ARMS])
    seed_list = list(seeds or P.COFOLD_MODEL_SEEDS)

    out = {
        "_what": "Do the sensitivity control's co-folds reproduce the deposited ternaries the panel's own "
                 "design says they should be validated against? INPUT QUALITY ONLY.",
        "_licenses": "NOTHING about SMARCA2/4, NR4A3, degradation, efficacy or selectivity. It re-scores no "
                     "leg, moves no threshold and emits no verdict; selcal-verdict.json remains the one home "
                     "of the tier.",
        "_why_this_was_owed": "selcal_panel chose PRT3789 over ACBI2 BECAUSE two deposited ternaries carry the "
                              "same ligand on both arms, so 'each arm's co-fold can be VALIDATED against a "
                              "real structure of the very complex it models'. That validation had never been "
                              "implemented; this is it.",
        "_third_explanation": "selcal-verdict.json bounds its NULL between 'the readout is blunt' and 'this "
                              "pair is hard'. A co-fold far from the crystal is a THIRD reading — the panel "
                              "simulated something other than the measured complex — and it is the one this "
                              "artifact can speak to.",
        "_kernels_imported_not_reimplemented": [
            "nrv04_covalent_md.interface_atom_indices (E1's 0.8 nm heavy-atom interface selector)",
            "nrv04_covalent_md._aligned_iface_rmsd (E1's E3-Ca superposition + interface RMSD; nm in, A out)",
            "nr4a_differential_atlas.nw_align (affine-gap BLOSUM62 global alignment)",
        ],
        "deposited_ternaries": dep,
        "reporting_context": reporting_context(),
        "min_chain_identity": MIN_CHAIN_IDENTITY,
        "min_aligned_residues": MIN_ALIGNED_RESIDUES,
        "fnat_contact_A": FNAT_CONTACT_A,
        "records": [], "n_graded": 0, "n_refused": 0,
    }

    for arm_id in arm_list:
        arm = next((a for a in P.ARMS if a.arm_id == arm_id), None)
        system = arm.cofold_system if arm is not None else arm_id
        pdb_id = dep.get(arm_id)
        if not pdb_id:
            out["records"].append({"arm_id": arm_id, "graded": False,
                                   "why": "no deposited ternary is recorded for this arm"})
            out["n_refused"] += 1
            continue
        native_path = os.path.join(native_dir, "%s.cif" % pdb_id.upper())
        for seed in seed_list:
            excluded, why_excl = (P.excluded_cofold(arm_id, seed) if hasattr(P, "excluded_cofold")
                                  else (False, ""))
            sdir = os.path.join(cofold_root, system, "seed_%d" % seed)
            models = sorted(glob.glob(os.path.join(sdir, model_glob))) or \
                sorted(glob.glob(os.path.join(sdir, "**", model_glob), recursive=True))
            if not models:
                out["records"].append({"arm_id": arm_id, "cofold_system": system, "seed": seed,
                                       "native_pdb_id": pdb_id, "graded": False,
                                       "panel_excluded": bool(excluded), "panel_exclusion_why": why_excl,
                                       "why": "no model matching %r under %s — NOT a reading that the co-fold "
                                              "disagrees with the crystal, a reading that it could not be read"
                                              % (model_glob, sdir)})
                out["n_refused"] += 1
                continue
            if not os.path.exists(native_path):
                out["records"].append({"arm_id": arm_id, "cofold_system": system, "seed": seed,
                                       "native_pdb_id": pdb_id, "graded": False,
                                       "why": "deposited structure %s not fetched to %s" % (pdb_id, native_path)})
                out["n_refused"] += 1
                continue
            rec = validate_one(models[0], native_path)
            rec.update({"arm_id": arm_id, "cofold_system": system, "seed": seed, "native_pdb_id": pdb_id,
                        "panel_excluded": bool(excluded), "panel_exclusion_why": why_excl})
            out["records"].append(rec)
            out["n_graded" if rec.get("graded") else "n_refused"] += 1

    graded = [r for r in out["records"] if r.get("graded")]
    out["per_arm"] = {}
    for arm_id in arm_list:
        vals = [r["interface_rmsd_to_crystal_A"] for r in graded if r.get("arm_id") == arm_id]
        fnats = [r["fnat"]["fnat"] for r in graded
                 if r.get("arm_id") == arm_id and r.get("fnat", {}).get("fnat") is not None]
        out["per_arm"][arm_id] = {
            "n_graded": len(vals),
            "interface_rmsd_to_crystal_A": {"values": vals,
                                            "mean": (round(sum(vals) / len(vals), 3) if vals else None),
                                            "min": (min(vals) if vals else None),
                                            "max": (max(vals) if vals else None)},
            "fnat": {"values": fnats, "mean": (round(sum(fnats) / len(fnats), 4) if fnats else None)},
        }
    out["_completeness"] = ("%d graded, %d refused. A refusal is a first-class outcome and is never averaged "
                            "into a per-arm figure; an absent reading is not a reading of absence."
                            % (out["n_graded"], out["n_refused"]))
    return out


def _cli(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Score selcal co-folds against their deposited ternaries ($0 CPU).")
    ap.add_argument("--cofold-root", required=True, help="local root mirroring <prefix>/<system>/seed_<n>/")
    ap.add_argument("--native-dir", default=None, help="where the RCSB cifs live (default: <cofold-root>/_native)")
    ap.add_argument("--fetch", action="store_true", help="download the deposited ternaries first")
    ap.add_argument("--model-glob", default="*.cif")
    ap.add_argument("--out", default=os.path.join(HERE, "selcal-cofold-vs-crystal.json"))
    args = ap.parse_args(argv)

    native_dir = args.native_dir or os.path.join(args.cofold_root, "_native")
    fetched = []
    if args.fetch:
        for pdb_id in sorted(set(deposited_ternaries().values())):
            fetched.append(fetch_rcsb_cif(pdb_id, native_dir))
            print("[selcal-validate] fetched %s" % fetched[-1]["url"], flush=True)

    res = validate_panel(args.cofold_root, native_dir, model_glob=args.model_glob)
    res["native_provenance"] = fetched or {"_note": "structures were not fetched in this run; --fetch to record "
                                                    "provenance"}
    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=False)
    print("[selcal-validate] wrote %s: %d graded, %d refused" % (args.out, res["n_graded"], res["n_refused"]),
          flush=True)
    for r in res["records"]:
        if r.get("graded"):
            print("  %-18s seed %s  iRMSD_vs_%s = %6.3f A   fnat = %s"
                  % (r.get("arm_id"), r.get("seed"), r.get("native_pdb_id"),
                     r["interface_rmsd_to_crystal_A"], r["fnat"]["fnat"]), flush=True)
        else:
            print("  %-18s seed %s  REFUSED — %s" % (r.get("arm_id"), r.get("seed"), r.get("why")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
