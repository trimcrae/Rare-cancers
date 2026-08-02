#!/usr/bin/env python3
"""A durable, append-only ANALYSIS-ATOM trajectory for endpoint-MD drivers.

WHY THIS EXISTS — it is the implementation of a requirement this repo adopted and then did not wire up.
nr4a3-program-map.md RUNG 3 records, as *"the highest-leverage infrastructure change for the whole ternary program
(adopted as a requirement, 2026-07-25): every MD driver must persist a strided heavy-atom TRAJECTORY"*,
because the NR-V04 covalent panel produced **three independent data-invalidating analysis defects** — a
positional chain split that measured the Elongin-C interface instead of the target one, a chain-blind reactive-
cysteine search, and an R3 readout in nanometres wearing an Ångström label — and **not one of them could be
corrected without re-running the MD**, since the driver reduces each frame in-loop and discards positions
(`nrv04_result_forensics` → `trajectory_objects_found: 0`). Each defect was a *post-hoc analysis* bug over
coordinates that had existed and been thrown away.

WHAT IT PERSISTS, AND WHY NOT EVERY HEAVY ATOM. A ~466k-atom solvated assembly is ~2.8 MB per frame at full
heavy-atom float32, which is hundreds of MB per leg — outside the "tens of MB against the ~112 MB System XML
the driver already uploads" the requirement was costed at. The selection below is instead the **closure of the
atoms every readout in this lane consumes**:

    * every protein **CA**      -> chain identity, per-chain geometry, interface RMSD, ANY re-derivation of a
                                   chain split (defect 1) or of which chain a residue sits on
    * every cysteine **SG**     -> the reactive-cysteine search, on any chain, at any distance (defect 2)
    * every lysine **NZ**       -> ubiquitin-transfer presentation, in whatever unit the reader chooses
                                   (defect 3 was a unit conversion, i.e. exactly a re-derivable one)
    * every non-polymer heavy atom (ligand / warhead / recruiter), waters and monatomic ions excluded

Measured against this lane's own systems that is ~1k atoms, ~12 kB/frame, single-digit MB per leg — 20-40x
under budget — and **all three defects above become $0 re-derivations**. ⚠ **Stated honestly: this is not a
full heavy-atom trajectory and will not support an analysis nobody anticipated over sidechains it drops.** It
is the cheap 95%, not the complete record; `select_analysis_atoms(..., all_heavy=True)` widens it for a leg
that can afford the bytes.

FORMAT — append-only, because the alternative loses the file to the failure it exists to survive. Frames are
raw little-endian float32 triples in a `.f32` blob opened `"ab"`; a sidecar `.json` manifest carries the atom
index list, labels, units and cadence. There is no header to rewrite and no container to re-serialise, so a
kill -9 mid-frame truncates the blob to a whole number of frames and loses at most one — `read_frames` derives
the frame count from the file SIZE and ignores a torn tail rather than raising. Positions are stored in the
driver's native **nanometres** and the manifest says so, since a silent unit was defect 3.

⚠ THE UPLOAD IS THE POINT, NOT THE WRITE. CLAUDE.md's checkpoint rule is "upload as they are written" — a file
that only reaches S3 at clean exit is lost to exactly the preemption/crash this guards. `TrajWriter.mirror()`
is called from the driver's existing per-checkpoint S3 hook.
"""
import json
import os
import struct

# Residues that are solvent/bulk rather than a molecule an analysis would ever ask about.
SOLVENT_RESNAMES = frozenset({"HOH", "WAT", "TIP3", "SOL", "NA", "CL", "K", "MG", "ZN", "CA2", "SPC"})
# The per-atom picks that make each historical defect re-derivable. name -> why (kept next to the selection so
# a future reader can tell an intentional pick from an accident).
BACKBONE_PICK = {"CA": "chain identity / interface geometry"}
SIDECHAIN_PICKS = {("CYS", "SG"): "reactive-cysteine search",
                   ("LYS", "NZ"): "ubiquitin-transfer presentation"}
MAGIC = "nr4a3-analysis-traj/1"


def _is_solvent(resname):
    return (resname or "").strip().upper() in SOLVENT_RESNAMES


def select_analysis_atoms(atoms, all_heavy=False):
    """Pick the atoms to persist. PURE — `atoms` is any iterable of records with `.index`, `.name`,
    `.residue.name`, `.residue.chain.id` and `.element` (an OpenMM Topology satisfies this; so does the
    lightweight stand-in the tests use).

    Returns `(indices, labels)` with `indices` ASCENDING — the caller slices positions by it, so a stable,
    sorted order is part of the contract and the manifest records it. `labels` are `"<chain>:<resname><?>:<atom>"`
    strings, one per index, so a reader never has to re-derive the topology to know what a column is.

    `all_heavy=True` widens the pick to every non-solvent heavy atom (drops hydrogens only). That is the
    literal reading of the requirement and costs ~40x the bytes; the default is the analysis closure.
    """
    picked = []
    for a in atoms:
        resname = (getattr(a.residue, "name", "") or "").upper()
        if _is_solvent(resname):
            continue
        elem = getattr(a, "element", None)
        symbol = (getattr(elem, "symbol", None) or "").upper()
        if symbol == "H":                       # never persist hydrogens under either policy
            continue
        name = (a.name or "").upper()
        keep = all_heavy or name in BACKBONE_PICK or (resname, name) in SIDECHAIN_PICKS
        if not keep and not _is_polymer_residue(resname):
            keep = True                         # a non-polymer heavy atom: ligand / warhead / recruiter
        if keep:
            chain = getattr(getattr(a.residue, "chain", None), "id", "?")
            picked.append((int(a.index), f"{chain}:{resname}:{name}"))
    picked.sort(key=lambda t: t[0])
    return [i for i, _ in picked], [lab for _, lab in picked]


_AA3 = frozenset("ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL "
                 "HID HIE HIP CYX CYM ASH GLH LYN ACE NME NMA".split())
_NUC = frozenset("A C G U T DA DC DG DT ADE CYT GUA URA THY".split())


def _is_polymer_residue(resname):
    return resname in _AA3 or resname in _NUC


class TrajWriter:
    """Append frames to `<prefix>.f32` and keep `<prefix>.traj.json` beside it.

    FAILS SOFT BY DESIGN. This is a diagnostic aid attached to a billed GPU leg: a trajectory-write error must
    never be the thing that kills a leg that is otherwise producing its result. Every method swallows OSError
    and records it in `self.errors`, which the driver folds into its result JSON so a silent non-write is
    still visible. (`enabled=False` makes the whole object a no-op for smoke runs.)
    """

    def __init__(self, prefix, indices, labels, *, units="nm", frame_stride_steps=None, dt_ps=None,
                 stride_frames=1, enabled=True, s3_prefix=None, extra=None):
        self.prefix, self.indices, self.labels = prefix, list(indices), list(labels)
        self.stride_frames = max(1, int(stride_frames or 1))
        self.enabled = bool(enabled) and bool(self.indices)
        self.s3_prefix, self.errors, self.n_written = s3_prefix, [], 0
        self.blob_path, self.manifest_path = prefix + ".f32", prefix + ".traj.json"
        self.manifest = {"_format": MAGIC, "units": units, "dtype": "<f4", "n_atoms": len(self.indices),
                         "atom_indices": self.indices, "atom_labels": self.labels,
                         "frame_stride_steps": frame_stride_steps, "dt_ps": dt_ps,
                         "stride_frames": self.stride_frames, "blob": os.path.basename(self.blob_path),
                         "_read_with": "md_analysis_traj.read_frames(prefix)",
                         "_not_a_full_trajectory": "analysis-atom closure (CA + Cys SG + Lys NZ + non-polymer "
                                                   "heavy atoms); hydrogens, solvent and other sidechain atoms "
                                                   "are NOT persisted"}
        if extra:
            self.manifest.update(extra)

    def _record(self, exc, where):
        self.errors.append(f"{where}: {type(exc).__name__}: {exc}")

    def start(self, resume_frames=0):
        """Write the manifest and truncate the blob to `resume_frames` whole frames.

        The truncation is what makes a RESUME correct rather than corrupt: a preempted leg re-enters the
        production loop at its checkpoint's frame count, so any frames the blob holds beyond that were written
        after the last checkpoint and would otherwise be duplicated by the replay."""
        if not self.enabled:
            return self
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.blob_path)), exist_ok=True)
            want = self.frame_bytes * (max(0, int(resume_frames)) // self.stride_frames)
            if os.path.exists(self.blob_path):
                if os.path.getsize(self.blob_path) != want:
                    with open(self.blob_path, "r+b") as fh:
                        fh.truncate(want)
            else:
                open(self.blob_path, "ab").close()
            self.n_written = want // self.frame_bytes
            json.dump(self.manifest, open(self.manifest_path, "w"), indent=1)
        except OSError as e:
            self._record(e, "start")
        return self

    @property
    def frame_bytes(self):
        return 12 * len(self.indices)                      # 3 float32 per atom

    def append(self, positions, frame_index):
        """Persist one frame. `positions` is the driver's full per-atom list of (x, y, z); only `indices` are
        stored. A frame not on the stride is skipped, which is the only reason this returns False on success."""
        if not self.enabled or (frame_index % self.stride_frames):
            return False
        try:
            buf = bytearray()
            for i in self.indices:
                x, y, z = positions[i]
                buf += struct.pack("<3f", float(x), float(y), float(z))
            with open(self.blob_path, "ab") as fh:
                fh.write(buf)
            self.n_written += 1
            return True
        except (OSError, IndexError, TypeError, ValueError) as e:
            self._record(e, f"append@{frame_index}")
            return False

    def mirror(self, s3_cp):
        """Push blob + manifest to S3 with the driver's own copier. Called from the per-checkpoint hook, so the
        durable copy tracks the run instead of appearing only at clean exit."""
        if not self.enabled or not self.s3_prefix:
            return False
        ok = True
        for p in (self.blob_path, self.manifest_path):
            try:
                if os.path.exists(p):
                    s3_cp(p, f"{self.s3_prefix}/{os.path.basename(p)}")
            except Exception as e:                          # noqa: BLE001 — an upload must never kill a leg
                self._record(e, f"mirror:{os.path.basename(p)}")
                ok = False
        return ok

    def summary(self):
        return {"written_frames": self.n_written, "n_atoms": len(self.indices),
                "bytes": self.frame_bytes * self.n_written, "stride_frames": self.stride_frames,
                "blob": os.path.basename(self.blob_path), "enabled": self.enabled,
                "errors": self.errors or None}


def read_frames(prefix):
    """Read back `(manifest, frames)`; `frames[k][j]` is the (x, y, z) of `manifest['atom_indices'][j]`.

    A TORN TAIL IS IGNORED, NOT RAISED. The blob is append-only and the process writing it can be killed
    mid-frame, so the frame count comes from `size // frame_bytes` and a partial trailing frame is dropped.
    Refusing to read a checkpointed file because its last frame is short would recreate, in the reader, the
    all-or-nothing loss this module exists to prevent."""
    manifest = json.load(open(prefix + ".traj.json"))
    n = int(manifest["n_atoms"])
    fb = 12 * n
    blob = prefix + ".f32"
    if not os.path.exists(blob) or fb == 0:
        return manifest, []
    total = os.path.getsize(blob) // fb
    out = []
    with open(blob, "rb") as fh:
        for _ in range(total):
            vals = struct.unpack("<%df" % (3 * n), fh.read(fb))
            out.append([(vals[3 * j], vals[3 * j + 1], vals[3 * j + 2]) for j in range(n)])
    return manifest, out
