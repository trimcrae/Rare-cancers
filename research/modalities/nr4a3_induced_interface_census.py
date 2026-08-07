#!/usr/bin/env python3
"""Measure the INDUCED-INTERFACE SIZE of deposited complexes under the reach sampler's OWN
contact definition, so `BLK-TCIP-INTERFACE-FLOOR` can be argued from coordinates instead of prose.

WHY THIS EXISTS
---------------
`nr4a3_basin_search.PARAMS["min_contact_residues"] = 12` is the floor whose ablation inverts the
RT-TCIP size comparison (0.896 at 12 -> 1.121 at 6 -> 1.254 at 0; one home:
`nr4a3-tcip-reach.json`, decision view `nr4a3-tcip-route-memo.md` section 4(b)). It is a
DEGRADER-derived number - the sampler's own comment is "below this it is a tethered pair, not an
interface". `selectivity-requirement-sizing.md` section 3.1 records that nobody has sized what a
TRANSCRIPTIONAL chemically-induced-proximity system needs, and that the blocker is retired only by
finding a characterised induced interface tied to a transcriptional readout (MISSING-3).

This module does the part of that question that CAN be answered at $0 from deposited coordinates:
given a solved complex in which a small molecule bridges two protein chains, how many contacts does
the sampler's own predicate count across that interface? That converts "12" from an inherited
constant into a number with real complexes either side of it.

WHAT IS AND IS NOT MEASURED
---------------------------
  * MEASURED: the sampler's `n_contact` for a real, deposited, ligand-bridged protein-protein pair.
  * NOT MEASURED: cooperativity, residence time, affinity, or any transcriptional output. A contact
    count is the sampler's PROXY for an interface, and this module can only calibrate the proxy.
    Whether a transcriptional effector needs a given proxy value is exactly what stays open.
  * NOT A CLAIM ABOUT EFFICACY, SELECTIVITY, SAFETY OR CLINICAL READINESS, for any entry here.

THE PREDICATE, TAKEN FROM THE SAMPLER RATHER THAN RESTATED
----------------------------------------------------------
`nr4a3_basin_search.sample_placements` moves an "arm" body against a fixed "target" and, for each of
the arm's QUERY POINTS, takes the distance to the nearest TARGET HEAVY ATOM:

    d < hard_clash_A (3.0)                    -> hard clash (placement rejected outright)
    hard_clash_A <= d < soft_clash_A (3.6)    -> soft clash (at most max_soft_clashes allowed)
    soft_clash_A <= d <= contact_A (6.0)      -> CONTACT, counted into n_contact
    n_contact < min_contact_residues (12)     -> placement rejected: "a tethered pair, not an interface"

and the arm's query points are, per residue, exactly TWO: the CA, and the SIDE-CHAIN CENTROID
(`load_arm_from_registry`: `query = ca_list + cb_list`, `cb` being the centroid of every non-backbone
atom, falling back to CA for glycine). That is a load-bearing detail for reading the floor: 12 query
points is as few as SIX residues if both points of each residue are in contact, which is why this
module reports the residue count beside the point count and never lets the two be confused.

The direction matters and is not symmetric - the arm is sampled against the target, not the reverse -
so every pair here is measured BOTH WAYS and both numbers are reported. No single orientation is
promoted.

INPUT
-----
mmCIF text fetched through `fetch-literature.yml` + `scripts/lit_fetch_urls.py` into the
`literature-cache` branch (RCSB is 403'd at the dev sandbox's egress proxy on CONNECT).
mmCIF rather than PDB ON PURPOSE: `lit_fetch_urls.strip_html` collapses runs of spaces, which
destroys the fixed-column PDB record layout but is harmless to mmCIF, which is whitespace-delimited
by construction. The fetcher's 5-line provenance header is stripped here.

EVERY ENTRY IS VERIFIED FROM ITS OWN FILE. The corpus file names a candidate PDB id; this module
reads `_struct.title`, `_entity.pdbx_description`, `_exptl.method` and the resolution out of the
coordinates themselves and reports them, so a mis-remembered accession shows up as a title that does
not match rather than as a number attributed to the wrong complex.

$0, pure stdlib, CPU only.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import nr4a3_basin_search as BS  # noqa: E402  (PARAMS is the one home of the thresholds)

PARAMS = BS.PARAMS

# The 20 standard residues plus the common modified ones the entries here actually carry. A chain is
# treated as protein when most of its ATOM records are in this set.
AA3 = {
    "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU", "LYS", "MET",
    "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL", "MSE", "SEC", "PYL", "HSD", "HSE", "HSP",
}
BACKBONE = {"N", "CA", "C", "O", "OXT"}

# HETATM components that are never a bridging ligand: solvent, cryoprotectants, buffer and ions.
NOT_A_LIGAND = {
    "HOH", "DOD", "WAT", "SO4", "PO4", "GOL", "EDO", "PEG", "PGE", "1PE", "MPD", "DMS", "ACT",
    "ACY", "FMT", "TRS", "EPE", "MES", "IMD", "CIT", "TLA", "NO3", "CL", "BR", "IOD", "NA", "K",
    "MG", "CA", "ZN", "MN", "FE", "FE2", "NI", "CO", "CU", "CD", "HG", "CS", "RB", "SR", "BA",
    "PB", "AU", "PT", "SM", "YB", "EU", "GD", "UNX", "UNL", "NH4", "AZI", "SCN", "BME", "DTT",
    "P6G", "PG4", "2PE", "12P", "15P", "OLC", "LDA", "BOG", "C8E", "SGM", "MRD", "IPA", "ETX",
}
MIN_BRIDGING_LIGAND_ATOMS = 12      # a drug-like bridging body, not a fragment of buffer
LIGAND_CONTACT_A = 4.5              # a ligand heavy atom this close to a chain touches that chain

# ---------------------------------------------------------------------------------------------
# ⚠ THE ONLY CURATORIAL JUDGEMENT IN THIS FILE, KEPT HERE SO IT CANNOT HIDE INSIDE PROSE.
# Everything above and below is measurement; this dict is an OPINION about what each entry is an
# instance of, and the grouped summary it drives is therefore only as good as it. Each row carries
# the reason, so a reader can disagree with a specific row rather than with a table.
#   `degrader_or_glue`  the modality `min_contact_residues = 12` was inherited FROM.
#   `cid_proximity`     a small molecule bridges two proteins that do not otherwise associate.
#   `induced_transcriptional`  the induced interface's own readout is transcription.
#   `constitutive`      the pair associates without the ligand; present as a contrast, never pooled.
# A structure can be in two classes at once, which is the point of listing classes rather than one
# label — the rapamycin ternary is the canonical CID *and* the one used to drive transcription.
# ---------------------------------------------------------------------------------------------
# ⚠ AND ONE MORE DISTINCTION THE MEASUREMENT CANNOT MAKE FOR ITSELF. Two different things are both
# called an induced interface, and only the first is visible in a single structure:
#   LIGAND-BRIDGED   one molecule touches both partners - a PROTAC, a molecular glue, rapamycin.
#                    Detected here, from the coordinates, by `bridging_ligands`.
#   ALLOSTERIC       the ligand sits inside ONE partner's pocket and never touches the other; the
#                    interface exists because the ligand changed that partner's conformation. An
#                    agonist-bound nuclear receptor recruiting a coactivator NR-box is the archetype,
#                    and it is a chemically induced TRANSCRIPTIONAL interface by any reading - but no
#                    single deposited structure can prove the dependence, so listing one is a CLAIM
#                    about the literature, not a reading of the file. Hence `allosteric_pairs`, which
#                    names the exact chains and the reason, so the claim is attackable per row.
ENTRY_CLASSES = {
    "5T35": {"classes": ["degrader_or_glue"], "why": "PROTAC MZ1 bridging BRD4 BD2 and pVHL"},
    "6HAX": {"classes": ["degrader_or_glue"], "why": "PROTAC 2 bridging SMARCA2 bromodomain and pVHL"},
    "6SIS": {"classes": ["degrader_or_glue"], "why": "macrocyclic PROTAC 1 bridging a BRD4 bromodomain and pVHL"},
    "6BN7": {"classes": ["degrader_or_glue"], "why": "PROTAC dBET23 bridging CRBN and BRD4 BD1"},
    "6BOY": {"classes": ["degrader_or_glue"], "why": "PROTAC dBET6 bridging CRBN and BRD4 BD1"},
    "7Q2J": {"classes": ["degrader_or_glue"], "why": "PROTAC bridging WDR5 and pVHL"},
    "5FQD": {"classes": ["degrader_or_glue"], "why": "lenalidomide molecular glue bridging CRBN and CK1a"},
    "6H0F": {"classes": ["degrader_or_glue"], "why": "pomalidomide molecular glue bridging CRBN and IKZF1 ZF2"},
    "1FAP": {"classes": ["cid_proximity"],
             "why": "FKBP12-rapamycin-FRB, the chemical inducer of dimerization that the "
                    "rapamycin-regulated transcription systems are built on"},
    "3FAP": {"classes": ["cid_proximity"], "why": "FKBP12-rapalog-FRB"},
    "4DRI": {"classes": ["cid_proximity"], "why": "FKBP51-rapamycin-FRB; a paralogue of the same ternary"},
    "2P1Q": {"classes": ["cid_proximity"], "why": "auxin bridging TIR1 and the IAA7 degron"},
    "3KDJ": {"classes": ["cid_proximity"], "why": "abscisic acid: the PYL1-ABI1 CID pair",
             "allosteric_pairs": [["A", "B"]],
             "allosteric_reason": "ABA is buried in PYL1's pocket and the PYL1-ABI1 interface forms "
                                  "through the gate-latch-lock conformational change, so the pair is "
                                  "ligand-DEPENDENT without being ligand-BRIDGED"},
    "3JRQ": {"classes": ["cid_proximity"], "why": "abscisic acid: the PYL1-ABI1 CID pair, second entry",
             "allosteric_pairs": [["A", "B"]], "allosteric_reason": "as 3KDJ"},
    "2ZSH": {"classes": ["cid_proximity"], "why": "gibberellin GA3: the GID1-DELLA CID pair",
             "allosteric_pairs": [["A", "B"]],
             "allosteric_reason": "GA3 is buried in GID1's pocket; the DELLA interface forms on the "
                                  "GA-induced N-terminal lid"},
    "2PRG": {"classes": ["induced_transcriptional"], "why": "rosiglitazone-bound PPARg with an SRC-1 NR box",
             "allosteric_pairs": [["A", "C"], ["B", "C"]],
             "allosteric_reason": "agonist-dependent AF-2 coactivator recruitment; the agonist is in "
                                  "the LBD pocket and does not touch the peptide"},
    "1FM9": {"classes": ["induced_transcriptional"], "why": "ligand-bound PPARg:RXRa with SRC-1 NR boxes",
             "allosteric_pairs": [["D", "E"], ["A", "B"]], "allosteric_reason": "as 2PRG"},
    "3DZY": {"classes": ["induced_transcriptional"], "why": "intact PPARg:RXRa on DNA with an NCOA2 peptide",
             "allosteric_pairs": [["D", "E"], ["A", "G"]], "allosteric_reason": "as 2PRG"},
    "1GWR": {"classes": ["induced_transcriptional"], "why": "oestradiol-bound ERa with the TIF2 NR-box-3 peptide",
             "allosteric_pairs": [["A", "C"], ["B", "D"]], "allosteric_reason": "as 2PRG"},
    "3ERD": {"classes": ["induced_transcriptional"], "why": "DES-bound ERa with the GRIP1 NR-box-II peptide",
             "allosteric_pairs": [["A", "C"], ["B", "D"]], "allosteric_reason": "as 2PRG"},
    "7LWG": {"classes": ["constitutive"],
             "why": "the BCL6 BTB HOMODIMER this route already staged as its effector arm; the dimer "
                    "is constitutive, so its interface is a contrast and is never pooled as induced"},
    "9MZA": {"classes": ["induced_transcriptional", "tcip"],
             "why": "'Chemically Hijacked BCL6-TCIP3-p300 Complex' - the bivalent molecule A1BUC "
                    "(TCIP3, 81 heavy atoms) bridging the BCL6 BTB domain and p300. VERIFIED from "
                    "the deposition's own rcsb_primary_citation, not from the paper: bioRxiv "
                    "10.1101/2025.03.14.643404 / PubMed 40166243, 'A Bivalent Molecular Glue "
                    "Linking Lysine Acetyltransferases to Oncogene-induced Cell Death' (Nix, "
                    "Gourisankar, ... Crabtree), released 2025-04-16 at 2.1 A",
             # ⛔ The bridging ligand ALSO spans the two BCL6 protomers, because the BTB lateral
             # groove is formed BETWEEN them - the same fact `nr4a3_effector_stage` measured when it
             # staged 7LWG as an A+B body. So `bridging_ligands` correctly reports chain A and chain
             # C as ligand-spanned, and that pair is nonetheless the CONSTITUTIVE homodimer, not the
             # induced interface. Pooling it would put a 66-71-point obligate dimer into the induced
             # class and move every summary. Excluded by name, with the cross-check below.
             "exclude_pairs": [["A", "C"]],
             "exclude_reason": "chains A and C are the two protomers of the constitutive BCL6 BTB "
                               "homodimer. The induced interface of this complex is BCL6 against "
                               "p300 (A-D and B-C). Cross-check that this exclusion is right rather "
                               "than convenient: the excluded pair measures 66/71 contact points "
                               "here and the SAME homodimer in the independent entry 7LWG measures "
                               "64/67 - two crystals, one instrument, one number."},
}


# ---------------------------------------------------------------------------------------------
# mmCIF reading
# ---------------------------------------------------------------------------------------------
_FETCH_HEADER = re.compile(r"^SOURCE URL:.*?\n=+\n", re.S)


def strip_fetch_header(text: str) -> str:
    """Drop `lit_fetch_urls.py`'s provenance banner, keeping the mmCIF body."""
    m = _FETCH_HEADER.match(text)
    if m:
        return text[m.end():]
    i = text.find("=" * 40)
    if i >= 0 and text[:i].count("\n") <= 8:
        j = text.find("\n", i)
        return text[j + 1:] if j >= 0 else text
    return text


def _tokens(line: str):
    """CIF value tokenizer: whitespace separated, single/double quotes group."""
    out, i, n = [], 0, len(line)
    while i < n:
        c = line[i]
        if c in " \t":
            i += 1
            continue
        if c in "'\"":
            q = c
            i += 1
            start = i
            while i < n and not (line[i] == q and (i + 1 >= n or line[i + 1] in " \t")):
                i += 1
            out.append(line[start:i])
            i += 1
        else:
            start = i
            while i < n and line[i] not in " \t":
                i += 1
            out.append(line[start:i])
    return out


def _unset(v: str) -> bool:
    return v in (".", "?")


def parse_cif(text: str) -> dict:
    """Return {'meta': {...}, 'atoms': [...]} from mmCIF text. Model 1, altloc '.'/'A', no hydrogens."""
    text = strip_fetch_header(text)
    lines = text.split("\n")
    meta = {"title": None, "method": None, "resolution_A": None, "entities": [],
            "entry_id": None, "chain_descriptions": {}}
    atoms = []

    # --- single-value items we care about. A value may sit on the same line OR in a following
    # semicolon-delimited text block (older entries put the title there), which is why this reads
    # ahead rather than assuming the one-line form — a missing title would otherwise read as an
    # entry with no title rather than as a parser that did not look.
    for li, ln in enumerate(lines):
        s = ln.strip()
        for key, field in (("_struct.title", "title"),
                           ("_exptl.method", "method"),
                           ("_entry.id", "entry_id")):
            if not s.startswith(key):
                continue
            rest = s[len(key):].strip()
            if rest and not _unset(rest):
                meta[field] = rest.strip("'\"")
            elif not rest:
                j = li + 1
                while j < len(lines) and lines[j].strip() == "":
                    j += 1
                if j >= len(lines):
                    continue
                if lines[j].startswith(";"):
                    buf = [lines[j][1:]]
                    j += 1
                    while j < len(lines) and not lines[j].startswith(";"):
                        buf.append(lines[j])
                        j += 1
                    meta[field] = " ".join(x.strip() for x in buf).strip()
                else:
                    tok = _tokens(lines[j].strip())
                    if tok and not _unset(tok[0]) and not tok[0].startswith("_"):
                        meta[field] = tok[0]
        if s.startswith("_refine.ls_d_res_high") or s.startswith("_em_3d_reconstruction.resolution "):
            rest = s.split(None, 1)[1].strip() if len(s.split(None, 1)) > 1 else ""
            try:
                if rest and not _unset(rest):
                    meta["resolution_A"] = float(rest)
            except ValueError:
                pass

    # --- loops
    entity_desc, poly_strand = {}, {}
    i = 0
    n = len(lines)
    while i < n:
        s = lines[i].strip()
        if s != "loop_":
            i += 1
            continue
        i += 1
        headers = []
        while i < n and lines[i].strip().startswith("_"):
            headers.append(lines[i].strip().split()[0])
            i += 1
        # ⚠ A CIF LOOP ROW IS NOT A LINE. One row's values may wrap over several lines, and a value
        # may be a multi-line `;`-delimited block — which is exactly how `_entity.pdbx_description`
        # is usually written. Reading line-by-line therefore drops precisely the field that says
        # WHAT each chain is, leaving a table of "chain A vs chain B" that invites guessing. So the
        # reader is TOKEN-COUNT driven: accumulate until a row has len(headers) values.
        rows, cur = [], []
        while i < n:
            raw = lines[i]
            s2 = raw.strip()
            if not cur and (s2.startswith("_") or s2 == "loop_" or s2.startswith("#")
                            or s2.startswith("data_")):
                break
            if s2 == "":
                i += 1
                continue
            if raw.startswith(";"):
                buf = [raw[1:]]
                i += 1
                while i < n and not lines[i].startswith(";"):
                    buf.append(lines[i])
                    i += 1
                i += 1
                cur.append(" ".join(x.strip() for x in buf).strip())
            else:
                cur.extend(_tokens(s2))
                i += 1
            while len(cur) >= len(headers):
                rows.append(cur[:len(headers)])
                cur = cur[len(headers):]

        if not headers:
            continue
        cat = headers[0].split(".")[0]
        cols = {h.split(".", 1)[1]: k for k, h in enumerate(headers) if "." in h}

        if cat == "_entity":
            for r in rows:
                if len(r) != len(headers):
                    continue
                d = cols.get("pdbx_description")
                t = cols.get("type")
                eid = cols.get("id")
                if d is not None and not _unset(r[d]):
                    meta["entities"].append({"type": r[t] if t is not None else None,
                                             "description": r[d]})
                    if eid is not None:
                        entity_desc[r[eid]] = r[d]
        elif cat == "_entity_poly":
            # auth chain -> what that chain actually IS. Without this a pair reads as "chain A vs
            # chain B", which is unreadable and, worse, invites guessing which chain is the effector.
            sid = cols.get("pdbx_strand_id")
            eid = cols.get("entity_id")
            for r in rows:
                if len(r) != len(headers) or sid is None or eid is None:
                    continue
                for ch in str(r[sid]).split(","):
                    ch = ch.strip()
                    if ch:
                        poly_strand[ch] = r[eid]
        elif cat == "_atom_site":
            need = ("group_PDB", "type_symbol", "label_atom_id", "label_comp_id",
                    "Cartn_x", "Cartn_y", "Cartn_z")
            if any(k not in cols for k in need):
                continue
            first_model = None
            for r in rows:
                if len(r) != len(headers):
                    continue
                mdl = r[cols["pdbx_PDB_model_num"]] if "pdbx_PDB_model_num" in cols else "1"
                if first_model is None:
                    first_model = mdl
                if mdl != first_model:
                    continue
                alt = r[cols["label_alt_id"]] if "label_alt_id" in cols else "."
                if not _unset(alt) and alt != "A":
                    continue
                el = r[cols["type_symbol"]].upper()
                if el in ("H", "D"):
                    continue
                chain = (r[cols["auth_asym_id"]] if "auth_asym_id" in cols
                         else r[cols["label_asym_id"]])
                seq = (r[cols["auth_seq_id"]] if "auth_seq_id" in cols
                       else r[cols.get("label_seq_id", 0)])
                ins = r[cols["pdbx_PDB_ins_code"]] if "pdbx_PDB_ins_code" in cols else "."
                try:
                    xyz = (float(r[cols["Cartn_x"]]), float(r[cols["Cartn_y"]]),
                           float(r[cols["Cartn_z"]]))
                except ValueError:
                    continue
                atoms.append({
                    "het": r[cols["group_PDB"]] == "HETATM",
                    "elem": el,
                    "name": r[cols["label_atom_id"]].strip("'\""),
                    "comp": r[cols["label_comp_id"]],
                    "chain": chain,
                    "seq": seq,
                    "ins": "" if _unset(ins) else ins,
                    "xyz": xyz,
                })
    for ch, eid in poly_strand.items():
        if eid in entity_desc:
            meta["chain_descriptions"][ch] = entity_desc[eid]
    return {"meta": meta, "atoms": atoms}


# ---------------------------------------------------------------------------------------------
# geometry — exact distances via a cell hash (no clamped field: this is a census, not a sampler)
# ---------------------------------------------------------------------------------------------
class CellHash:
    def __init__(self, points, cell: float):
        self.cell = float(cell)
        self.d = {}
        for p in points:
            k = (int(math.floor(p[0] / self.cell)),
                 int(math.floor(p[1] / self.cell)),
                 int(math.floor(p[2] / self.cell)))
            self.d.setdefault(k, []).append(p)

    def min_dist(self, p, ceiling: float) -> float:
        """Exact distance to the nearest source point, or `ceiling` if none is within it."""
        r = int(math.ceil(ceiling / self.cell))
        ci = int(math.floor(p[0] / self.cell))
        cj = int(math.floor(p[1] / self.cell))
        ck = int(math.floor(p[2] / self.cell))
        best = ceiling * ceiling
        px, py, pz = p
        for i in range(ci - r, ci + r + 1):
            for j in range(cj - r, cj + r + 1):
                for k in range(ck - r, ck + r + 1):
                    for (qx, qy, qz) in self.d.get((i, j, k), ()):
                        dd = (qx - px) ** 2 + (qy - py) ** 2 + (qz - pz) ** 2
                        if dd < best:
                            best = dd
        return math.sqrt(best)


def chain_residues(atoms, chain):
    """Ordered residues of one chain: {key: {'comp':..., 'atoms':[(name,xyz)]}} for ATOM records."""
    order, res = [], {}
    for a in atoms:
        if a["chain"] != chain or a["het"]:
            continue
        key = (a["seq"], a["ins"])
        if key not in res:
            res[key] = {"comp": a["comp"], "atoms": []}
            order.append(key)
        res[key]["atoms"].append((a["name"], a["xyz"]))
    return order, res


def query_points(atoms, chains):
    """The sampler's arm query points, built the same way `load_arm_from_registry` builds them:
    per residue, the CA and the SIDE-CHAIN CENTROID (CA again when there is no side chain).
    Returns (points, residue_index) where residue_index[i] identifies which residue point i came from."""
    ca_pts, ca_owner, cb_pts, cb_owner = [], [], [], []
    for ch in chains:
        order, res = chain_residues(atoms, ch)
        for key in order:
            r = res[key]
            if r["comp"] not in AA3:
                continue
            cav = next((xyz for nm, xyz in r["atoms"] if nm == "CA"), None)
            if cav is None:
                continue
            side = [xyz for nm, xyz in r["atoms"] if nm not in BACKBONE]
            cb = (sum(p[0] for p in side) / len(side),
                  sum(p[1] for p in side) / len(side),
                  sum(p[2] for p in side) / len(side)) if side else cav
            ca_pts.append(cav); ca_owner.append((ch,) + key)
            cb_pts.append(cb);  cb_owner.append((ch,) + key)
    pts = ca_pts + cb_pts
    owner = ca_owner + cb_owner
    return pts, owner


def contact_profile(target_heavy_xyz, arm_points, arm_owner, params=PARAMS):
    """The sampler's own three-way classification, evaluated exactly.

    Returns the point counts (`n_contact` is the quantity `min_contact_residues` is compared to)
    AND the residue counts, which are NOT the same number and must never be swapped for each other.
    """
    hard = params["hard_clash_A"]
    soft = params["soft_clash_A"]
    contact = params["contact_A"]
    ch = CellHash(target_heavy_xyz, cell=max(contact, 6.0))
    n_hard = n_soft = n_contact = 0
    res_contact, res_any = set(), set()
    for p, own in zip(arm_points, arm_owner):
        d = ch.min_dist(p, contact + 0.001)
        if d < hard:
            n_hard += 1
            res_any.add(own)
        elif d < soft:
            n_soft += 1
            res_any.add(own)
        elif d <= contact:
            n_contact += 1
            res_contact.add(own)
            res_any.add(own)
    return {
        "n_contact_points": n_contact,
        "n_soft_points": n_soft,
        "n_hard_points": n_hard,
        "n_residues_with_a_contact_point": len(res_contact),
        "n_residues_within_contact_A": len(res_any),
        "n_query_points": len(arm_points),
    }


# ---------------------------------------------------------------------------------------------
# per-entry census
# ---------------------------------------------------------------------------------------------
def protein_chains(atoms):
    counts, aa = {}, {}
    for a in atoms:
        if a["het"]:
            continue
        counts[a["chain"]] = counts.get(a["chain"], 0) + 1
        if a["comp"] in AA3:
            aa[a["chain"]] = aa.get(a["chain"], 0) + 1
    return sorted(c for c in counts if aa.get(c, 0) >= 0.5 * counts[c] and aa.get(c, 0) >= 40)


def bridging_ligands(atoms, chains):
    """Ligands with >= MIN_BRIDGING_LIGAND_ATOMS heavy atoms, and which chains each one touches."""
    groups = {}
    for a in atoms:
        if not a["het"] or a["comp"] in NOT_A_LIGAND or a["comp"] in AA3:
            continue
        groups.setdefault((a["chain"], a["seq"], a["ins"], a["comp"]), []).append(a["xyz"])
    out = []
    per_chain = {c: CellHash([a["xyz"] for a in atoms if a["chain"] == c and not a["het"]], 5.0)
                 for c in chains}
    for key, pts in groups.items():
        if len(pts) < MIN_BRIDGING_LIGAND_ATOMS:
            continue
        touched = {}
        for c in chains:
            k = sum(1 for p in pts
                    if per_chain[c].min_dist(p, LIGAND_CONTACT_A + 0.001) <= LIGAND_CONTACT_A)
            if k:
                touched[c] = k
        out.append({"het_code": key[3], "chain": key[0], "seq": key[1],
                    "n_heavy_atoms": len(pts), "chains_touched": touched,
                    "spans": sorted(c for c, k in touched.items() if k >= 3)})
    return out


def census_entry(pdb_id: str, text: str, params=PARAMS) -> dict:
    st = parse_cif(text)
    atoms = st["atoms"]
    rec = {
        "pdb_id": pdb_id,
        "title": st["meta"]["title"],
        "method": st["meta"]["method"],
        "resolution_A": st["meta"]["resolution_A"],
        "entry_id_in_file": st["meta"]["entry_id"],
        "entities": [e["description"] for e in st["meta"]["entities"]],
        "chain_descriptions": st["meta"]["chain_descriptions"],
        "n_atoms_model1": len(atoms),
    }
    if not atoms:
        rec["status"] = "NO_COORDINATES"
        return rec
    chains = protein_chains(atoms)
    rec["protein_chains"] = chains
    ligs = bridging_ligands(atoms, chains)
    rec["ligands"] = ligs
    spanning = [l for l in ligs if len(l["spans"]) >= 2]
    rec["ligand_bridged_chain_pairs"] = [
        list(p) for p in sorted({tuple(sorted((a, b))) for l in spanning
                                 for a in l["spans"] for b in l["spans"] if a < b})]

    heavy_by_chain = {c: [a["xyz"] for a in atoms if a["chain"] == c and not a["het"]]
                      for c in chains}
    pairs = []
    for a, b in [(x, y) for i, x in enumerate(chains) for y in chains[i + 1:]]:
        pa, oa = query_points(atoms, [a])
        pb, ob = query_points(atoms, [b])
        if not pa or not pb:
            continue
        ab = contact_profile(heavy_by_chain[b], pa, oa, params)   # a's body against b as target
        ba = contact_profile(heavy_by_chain[a], pb, ob, params)   # b's body against a as target
        if ab["n_contact_points"] == 0 and ba["n_contact_points"] == 0:
            continue
        bridged = [l["het_code"] for l in spanning if a in l["spans"] and b in l["spans"]]
        desc = st["meta"]["chain_descriptions"]
        pairs.append({
            "pair": [a, b],
            "what": [desc.get(a), desc.get(b)],
            "n_residues": [sum(1 for _ in range(len(pa) // 2)), sum(1 for _ in range(len(pb) // 2))],
            "ligand_bridged_by": sorted(set(bridged)),
            "arm_is_%s" % a: ab,
            "arm_is_%s" % b: ba,
            "n_contact_points_min": min(ab["n_contact_points"], ba["n_contact_points"]),
            "n_contact_points_max": max(ab["n_contact_points"], ba["n_contact_points"]),
            "clears_the_committed_floor_both_ways":
                min(ab["n_contact_points"], ba["n_contact_points"]) >= params["min_contact_residues"],
        })
    pairs.sort(key=lambda p: -p["n_contact_points_max"])
    rec["chain_pairs"] = pairs
    rec["status"] = "OK"
    return rec


def induced_pairs(entry: dict) -> list:
    """The pairs that count as INDUCED, each tagged with HOW that was decided.

    Ligand-bridged pairs are read off the coordinates. Allosteric ones come from `ENTRY_CLASSES`
    and are marked `curated`, never silently mixed in — a reader must be able to recompute the
    table without the curated rows and see what changes.

    Pairs that merely touch (a constitutive dimer, a CRL scaffold contact, a lattice neighbour) are
    excluded: the floor is a statement about the interface a bivalent molecule CREATES, and pooling
    a constitutive interface into it would answer a different question with the same number.
    """
    spec = ENTRY_CLASSES.get(entry["pdb_id"], {})
    allo = {tuple(sorted(p)) for p in spec.get("allosteric_pairs", [])}
    drop = {tuple(sorted(p)) for p in spec.get("exclude_pairs", [])}
    out = []
    for p in entry.get("chain_pairs", []):
        key = tuple(sorted(p["pair"]))
        if key in drop:
            continue
        if p.get("ligand_bridged_by"):
            out.append(dict(p, induced_basis="ligand_bridged_measured"))
        elif key in allo:
            out.append(dict(p, induced_basis="allosteric_curated",
                            induced_basis_reason=spec.get("allosteric_reason", "")))
    return out


def summarise(entries: list, params=PARAMS) -> dict:
    """Group the induced pairs by `ENTRY_CLASSES` and report the range each class spans.

    Reported as MIN-OVER-DIRECTIONS and MAX-OVER-DIRECTIONS separately, never as a single number:
    the sampler moves ONE body against the other, so which protein is the arm changes the count, and
    a mean would hide exactly the asymmetry that decides whether a real complex would have been
    accepted or rejected by the floor.
    """
    floor = params["min_contact_residues"]
    out = {}
    for e in entries:
        if e.get("status") != "OK":
            continue
        spec = ENTRY_CLASSES.get(e["pdb_id"], {"classes": ["unclassified"], "why": ""})
        for p in induced_pairs(e):
            for cls in spec["classes"]:
                row = out.setdefault(cls, {
                    "n_induced_pairs": 0, "n_ligand_bridged_measured": 0, "n_allosteric_curated": 0,
                    "entries": [], "mins": [], "maxs": [],
                    "pairs_below_floor_in_at_least_one_direction": 0,
                    "pairs_below_floor_in_both_directions": 0})
                row["n_induced_pairs"] += 1
                row["n_ligand_bridged_measured" if p["induced_basis"] == "ligand_bridged_measured"
                    else "n_allosteric_curated"] += 1
                if e["pdb_id"] not in row["entries"]:
                    row["entries"].append(e["pdb_id"])
                lo, hi = p["n_contact_points_min"], p["n_contact_points_max"]
                row["mins"].append(lo)
                row["maxs"].append(hi)
                if lo < floor:
                    row["pairs_below_floor_in_at_least_one_direction"] += 1
                if hi < floor:
                    row["pairs_below_floor_in_both_directions"] += 1
    for cls, row in out.items():
        row["min_direction_range"] = [min(row["mins"]), max(row["mins"])] if row["mins"] else None
        row["max_direction_range"] = [min(row["maxs"]), max(row["maxs"])] if row["maxs"] else None
        row["entries"].sort()
        row["_why"] = {pid: ENTRY_CLASSES[pid]["why"] for pid in row["entries"] if pid in ENTRY_CLASSES}
        del row["mins"], row["maxs"]
    return {
        "floor_under_test": floor,
        "_reading": "min_direction_range is the range, over this class's induced pairs, of the "
                    "SMALLER of the two directional contact counts; a pair whose smaller count is "
                    "below the floor is one the sampler would reject in at least one of the two "
                    "orientations it could be posed in.",
        "by_class": out,
    }


def load_corpus(dirpath: str) -> dict:
    """{pdb_id: text} from a fetched literature corpus directory (files named cif_<PDBID>.txt)."""
    out = {}
    for fn in sorted(os.listdir(dirpath)):
        m = re.match(r"^cif_([0-9A-Za-z]{4})\.txt$", fn)
        if not m:
            continue
        with open(os.path.join(dirpath, fn), "r", encoding="utf-8", errors="replace") as fh:
            out[m.group(1).upper()] = fh.read()
    return out


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(__doc__)
        print("usage: nr4a3_induced_interface_census.py <corpus-dir> [out.json]")
        return 2
    corpus = argv[0]
    out_path = argv[1] if len(argv) > 1 else os.path.join(HERE, "nr4a3-induced-interface-census.json")
    texts = load_corpus(corpus)
    entries = []
    for pdb_id, text in texts.items():
        try:
            entries.append(census_entry(pdb_id, text))
        except Exception as exc:  # noqa: BLE001 - one bad entry is one bad row, never a dead run
            entries.append({"pdb_id": pdb_id, "status": "PARSE_FAILED", "error": repr(exc)})
    doc = {
        "_what": "Induced-interface size of deposited complexes, measured under "
                 "nr4a3_basin_search.PARAMS' own contact predicate.",
        "_floor_under_test": {
            "min_contact_residues": PARAMS["min_contact_residues"],
            "contact_A": PARAMS["contact_A"],
            "soft_clash_A": PARAMS["soft_clash_A"],
            "hard_clash_A": PARAMS["hard_clash_A"],
            "note": "min_contact_residues counts QUERY POINTS, and there are two per residue "
                    "(CA + side-chain centroid), so 12 points is as few as 6 residues.",
        },
        "_not_measured": ["cooperativity", "residence time", "affinity", "transcriptional output",
                          "efficacy", "selectivity", "safety", "clinical readiness"],
        "_source": "mmCIF fetched in CI to the literature-cache branch; RCSB is 403'd from the dev "
                   "sandbox at the egress proxy on CONNECT.",
        "n_entries": len(entries),
        # Named for what it actually contains: the ligand-bridged pairs AND the curated allosteric
        # ones. Calling it "ligand_bridged" while it carries curated rows would be a mislabelled
        # record, which is worse than a missing one because nothing inside contradicts the name.
        "summary_over_induced_pairs": summarise(entries),
        "entries": sorted(entries, key=lambda e: e["pdb_id"]),
    }
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2)
        fh.write("\n")
    print(f"wrote {out_path}: {len(entries)} entries")
    for e in doc["entries"]:
        if e.get("status") != "OK":
            print(f"  {e['pdb_id']}  {e.get('status')}  {e.get('error', '')}")
            continue
        best = e["chain_pairs"][0] if e["chain_pairs"] else None
        print(f"  {e['pdb_id']}  {str(e.get('resolution_A')):>6}  "
              f"pairs={len(e['chain_pairs']):2d}  "
              f"top_contact_points={best['n_contact_points_max'] if best else 0:4d}  "
              f"{str(e.get('title'))[:70]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
