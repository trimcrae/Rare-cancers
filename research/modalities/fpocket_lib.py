"""
Pure, unit-tested parsing for fpocket output. No I/O, no external deps — every function takes text /
plain data and returns plain data, so it is fully testable locally (tests/test_fpocket_lib.py).

WHY THIS EXISTS. nr4a3_structure.py mapped fpocket residue files to pockets by *assuming* the file
index equalled the info.txt pocket number (`pocket{N}_atm.pdb` for "Pocket N"). fpocket's file
indexing is not guaranteed to match info.txt's 1-based numbering, so that assumption silently
mis-attributed a 0.495 druggability to the wrong residues in nr4a3-structure-assessment.json. Here the
mapping is DERIVED from the data (alpha-sphere fingerprints) and asserted bijective; ambiguity raises
rather than guessing. Conventions are never assumed.
"""
import re


def parse_info(info_text):
    """Parse <name>_info.txt -> {pocket_number(1-based int): {"druggability": float|None,
    "alpha_spheres": int|None}}."""
    pockets, pid = {}, None
    for line in info_text.splitlines():
        m = re.match(r"\s*Pocket\s+(\d+)\s*:", line)
        if m:
            pid = int(m.group(1))
            pockets[pid] = {"druggability": None, "alpha_spheres": None}
        elif pid is not None and "Druggability Score" in line:
            v = re.search(r"([0-9]*\.?[0-9]+)", line.split(":", 1)[1])
            if v:
                pockets[pid]["druggability"] = float(v.group(1))
        elif pid is not None and "Number of Alpha Spheres" in line:
            v = re.search(r"(\d+)", line.split(":", 1)[1])
            if v:
                pockets[pid]["alpha_spheres"] = int(v.group(1))
    return pockets


def parse_atm_residues(atm_text):
    """Residue sequence numbers lining a pocket, from a pocket{N}_atm.pdb body (sorted unique ints)."""
    res = set()
    for line in atm_text.splitlines():
        if line.startswith(("ATOM", "HETATM")):
            try:
                res.add(int(line[22:26]))
            except (ValueError, IndexError):
                pass
    return sorted(res)


def pqr_sphere_coords(pqr_text, ndigits=2):
    """Alpha-sphere coordinates from a pocket{N}_vert.pqr (a frozenset of rounded (x,y,z) tuples).

    PQR is whitespace-delimited; the last two numeric fields are charge and radius, so x,y,z are the
    three fields before them. Robust to an optional chain column."""
    coords = set()
    for line in pqr_text.splitlines():
        if not line.startswith(("ATOM", "HETATM")):
            continue
        toks = line.split()
        if len(toks) < 5:
            continue
        try:
            x, y, z = (round(float(toks[-5]), ndigits),
                       round(float(toks[-4]), ndigits),
                       round(float(toks[-3]), ndigits))
        except (ValueError, IndexError):
            continue
        coords.add((x, y, z))
    return frozenset(coords)


def out_pdb_sphere_coords(out_pdb_text, sphere_resname="STP", ndigits=2):
    """{pocket_number(int): frozenset((x,y,z))} from <name>_out.pdb alpha-sphere (STP) records, where
    each sphere atom's residue sequence number IS its (1-based) pocket number. Fixed PDB columns."""
    by_pocket = {}
    for line in out_pdb_text.splitlines():
        if not line.startswith(("ATOM", "HETATM")):
            continue
        if line[17:20].strip() != sphere_resname:
            continue
        try:
            pid = int(line[22:26])
            x, y, z = (round(float(line[30:38]), ndigits),
                       round(float(line[38:46]), ndigits),
                       round(float(line[46:54]), ndigits))
        except (ValueError, IndexError):
            continue
        by_pocket.setdefault(pid, set()).add((x, y, z))
    return {pid: frozenset(c) for pid, c in by_pocket.items()}


def map_files_to_pockets(info, file_sphere_counts, file_sphere_coords=None, out_sphere_coords=None):
    """Derive {file_index: pocket_number} WITHOUT assuming a 0/1-based file convention.

    Primary key: alpha-sphere count (info.txt vs per-file vert.pqr). When counts are unique this is
    unambiguous. For pockets sharing a count, disambiguate by matching the file's sphere COORDINATES
    to the per-pocket spheres in <name>_out.pdb. Any non-bijective / unresolved mapping raises
    ValueError (fail loud — never silently mis-map).

    info: {pocket_number: {"alpha_spheres": int}}
    file_sphere_counts: {file_index: int}
    file_sphere_coords / out_sphere_coords: optional, required only to break count ties.
    """
    if len(info) != len(file_sphere_counts):
        raise ValueError(f"pocket-count mismatch: info.txt has {len(info)} pockets but "
                         f"{len(file_sphere_counts)} residue files")
    counts = {pid: v["alpha_spheres"] for pid, v in info.items()}
    if any(c is None for c in counts.values()):
        raise ValueError("info.txt is missing 'Number of Alpha Spheres' for at least one pocket")

    # group pocket numbers by their alpha-sphere count
    pockets_by_count = {}
    for pid, c in counts.items():
        pockets_by_count.setdefault(c, []).append(pid)

    mapping = {}
    used = set()
    for fidx, c in file_sphere_counts.items():
        candidates = [p for p in pockets_by_count.get(c, []) if p not in used]
        if not candidates:
            raise ValueError(f"residue file {fidx} ({c} alpha spheres) matches no unused pocket "
                             "in info.txt")
        if len(candidates) == 1:
            pid = candidates[0]
        else:
            pid = _disambiguate_by_coords(fidx, candidates, file_sphere_coords, out_sphere_coords)
        mapping[fidx] = pid
        used.add(pid)

    if len(set(mapping.values())) != len(mapping) or len(mapping) != len(info):
        raise ValueError("file->pocket mapping is not bijective")
    return mapping


def _disambiguate_by_coords(fidx, candidates, file_sphere_coords, out_sphere_coords):
    if not file_sphere_coords or not out_sphere_coords:
        raise ValueError(f"residue file {fidx} ties on alpha-sphere count with pockets {candidates}; "
                         "coordinate data required to disambiguate but was not provided")
    fcoords = file_sphere_coords.get(fidx)
    matches = [p for p in candidates if out_sphere_coords.get(p) == fcoords]
    if len(matches) != 1:
        raise ValueError(f"could not uniquely match residue file {fidx} to a pocket by coordinates "
                         f"(candidates {candidates}, {len(matches)} coordinate matches)")
    return matches[0]


def select_druggable_lbd_pocket(pockets, lbd_first, lbd_last):
    """Highest-druggability pocket having >=1 residue in [lbd_first, lbd_last]. `pockets` is a list of
    dicts with 'druggability' (float|None) and 'residues' (list[int]). Returns the dict or None."""
    lbd = [p for p in pockets if any(lbd_first <= r <= lbd_last for r in p["residues"])]
    if not lbd:
        return None
    return max(lbd, key=lambda p: (p["druggability"] or 0.0))
