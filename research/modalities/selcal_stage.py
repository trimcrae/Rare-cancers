#!/usr/bin/env python3
"""ENDPOINT-MD SENSITIVITY CONTROL — staging: the co-fold inputs, and the assembler for one leg.

Two jobs, both $0 CPU, both deliberately OFF the billed host:

  1. `build_cofold_inputs()` — resolve the two arms' constructs and write the Boltz-2 YAMLs. Runs on CI and
     uploads to S3, so the rented GPU downloads a finished input instead of doing network work on a meter.
  2. `assemble_unit()` — turn one co-fold CIF into `<leg>/{complex.pdb, ligand.sdf, chains.json}`, the exact
     three files `nrv04_covalent_md` mounts.

═══════════════════════════════════════════════════════════════════════════════════════════════════════════
★★ NOTHING STRUCTURAL IS TYPED HERE. Sequences, construct boundaries and the ligand all come from a source.
═══════════════════════════════════════════════════════════════════════════════════════════════════════════
  * **Sequences** — fetched from UniProt at build time. A hand-copied 120-residue sequence is a fabrication
    risk with no upside (AGENTS.md).
  * **Construct boundaries** — quoted from the crystallographers' own methods section, via
    `selcal-reference-selectivity.json`. Kofink et al. 2022, verbatim: *"the bromodomains (BDs) of SMARCA2
    (SMARCA2BD; P51531-2, residues 1373-1493 …), SMARCA4 (SMARCA4BD; P51532, residues 1448–1569 …)"*. Using
    the published construct rather than a guessed span is what makes the two arms comparable to each other
    AND to the deposited ternaries that validate them.
  * **Ligand** — the RCSB chemical-component record for the CCD of a DEPOSITED ternary, read out of the
    committed reference artifact. Never a vendor catalogue, never a redrawn structure.

★ WHY BOTH ARMS ARE CO-FOLDED FROM REAL SEQUENCES. Options paper §2-D, precondition 2 and Open decision 9b:
`smarca2_model.py` builds SMARCA2 by homology MUTATION from the 3.73 Å 8G1Q SMARCA4 chain, so a model error
would sit on ONE arm only — the asymmetry this control exists to avoid. Here each arm is co-folded from its
own UniProt sequence with the identical protocol, and the deposited ternaries are used to VALIDATE the
co-folds rather than to supply them.

═══════════════════════════════════════════════════════════════════════════════════════════════════════════
⛔ THE CHAIN SPLIT IS IDENTIFIED, VERIFIED AND FAILS CLOSED — it is not positional and it is not fuzzy
═══════════════════════════════════════════════════════════════════════════════════════════════════════════
`nrv04_covalent_assemble.identify_chains` cannot be reused as-is: it requires the degradation-target chain to
be exactly the 254-residue NR4A LBD, and a ~121-residue bromodomain is not that. It also identifies E3
subunits by residue count alone, and here **the target is 121–122 residues against Elongin C's 112 and Elongin
B's 118** — close enough that a count-only rule is one construct revision away from mis-labelling the target
as an E3 subunit and computing every readout against the wrong interface. That exact defect already cost this
program a whole panel (`nrv04_covalent_md._topology_indices`' history note: Elongin C was silently scored as
the degradation target).

So the split here is derived from the INPUT SPECIFICATION and then VERIFIED against the file: the co-fold YAML
assigns chain ids and the expected residue count of each, that expectation is written beside the co-fold, and
the assembler raises unless every chain matches. Derive the convention from data, never assume it; fail loud,
never silently mis-map (TESTING.md rules 1 and 2).
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
REFERENCE_JSON = os.path.join(HERE, "selcal-reference-selectivity.json")

UNIPROT_FASTA = "https://rest.uniprot.org/uniprotkb/{acc}.fasta"

#: Chain ids in the co-fold YAML. The TARGET IS CHAIN A and the E3 subunits follow — the same layout
#: `nrv04_ternary.run` uses (`proteins = [("A", target)] + e3`), kept identical so the assembler, the driver
#: and every existing audit read the two lanes the same way.
CHAIN_TARGET = "A"
CHAIN_VHL, CHAIN_ELOB, CHAIN_ELOC = "E", "F", "G"

#: The construct spans, quoted from the primary source (see the module docstring). `(uniprot_id, lo, hi)` with
#: 1-based inclusive residue numbers in that accession's own numbering.
#: ⚠ `P51531-2` IS ISOFORM 2, NOT THE CANONICAL ENTRY, and the difference is not cosmetic: isoform numbering
#: shifts the residue indices, so fetching P51531 and slicing 1373-1493 would silently take a different span.
CONSTRUCTS = {
    "SMARCA2": {"accession": "P51531-2", "lo": 1373, "hi": 1493,
                "quote": "the bromodomains (BDs) of SMARCA2 (SMARCA2BD; P51531-2, residues 1373-1493 with "
                         "additional N-terminal SM residues (cloning artefact))",
                "source": "Kofink et al. 2022, Nat Commun, Methods — 10.1038/s41467-022-33430-6"},
    "SMARCA4": {"accession": "P51532", "lo": 1448, "hi": 1569,
                "quote": "SMARCA4 (SMARCA4BD; P51532, residues 1448-1569 with additional N-terminal SM "
                         "residues (cloning artefact))",
                "source": "Kofink et al. 2022, Nat Commun, Methods — 10.1038/s41467-022-33430-6"},
}

#: The N-terminal cloning artefact the crystallographers carried. NOT included: it is an expression tag, not
#: part of the domain, and adding two residues to both arms identically would change nothing except make the
#: construct differ from its UniProt span for no reason. Recorded so the omission is a decision, not a
#: silence.
CLONING_ARTEFACT_OMITTED = "SM (N-terminal, both arms) — an expression artefact, not part of the bromodomain"

#: The ligand. Read from the committed reference artifact by CCD, never typed.
LIGAND_CCD = "A1BB4"
LIGAND_NAME = "PRT3789"
#: Which of RCSB's two canonical SMILES programs to use. Fixed so a re-stage is byte-reproducible; both
#: describe the same molecule and the assembler's graph match is bond-order agnostic.
LIGAND_SMILES_PROGRAM = "OpenEye OEToolkits"


# =============================================================================================================
# sequences and constructs
# =============================================================================================================
def _uniprot_seq(acc: str) -> str:
    """The one-letter sequence for a UniProt accession (isoform ids like `P51531-2` work unchanged)."""
    import urllib.request
    req = urllib.request.Request(UNIPROT_FASTA.format(acc=acc),
                                 headers={"User-Agent": "rare-cancers-selcal/1.0 (research)"})
    with urllib.request.urlopen(req, timeout=90) as r:
        txt = r.read().decode("utf-8", "replace")
    seq = "".join(line.strip() for line in txt.splitlines() if line and not line.startswith(">"))
    if not seq:
        raise RuntimeError("UniProt returned no sequence for %r" % acc)
    return seq


def construct_sequence(gene: str) -> dict:
    """The bromodomain construct for one arm: the published span, sliced out of the published accession.

    Raises rather than truncating if the accession is shorter than the span — a silently short slice would
    produce a chain of the wrong length, and the whole chain-identification argument rests on the length."""
    c = CONSTRUCTS[gene]
    full = _uniprot_seq(c["accession"])
    lo, hi = int(c["lo"]), int(c["hi"])
    if len(full) < hi:
        raise RuntimeError("%s (%s) is %d residues, shorter than the published construct end %d — the "
                           "accession or the isoform is wrong, and slicing anyway would fabricate a construct"
                           % (gene, c["accession"], len(full), hi))
    seq = full[lo - 1:hi]
    return {"gene": gene, "accession": c["accession"], "lo": lo, "hi": hi, "sequence": seq,
            "n_residues": len(seq), "full_length": len(full),
            "construct_quote": c["quote"], "construct_source": c["source"],
            "cloning_artefact_omitted": CLONING_ARTEFACT_OMITTED}


def e3_sequences() -> list:
    """VHL / Elongin B / Elongin C as (chain_id, role, sequence).

    ⛔ THE ACCESSIONS ARE IMPORTED FROM `nrv04_ternary`, NEVER RE-TYPED. One of them was wrong once already —
    Elongin B was recorded as P62258 (14-3-3 epsilon) until the 2026-07-17 correction, and a co-fold batch
    built on it had to be discarded. A second copy of these three strings is a second chance to make that
    mistake."""
    import nrv04_ternary as nt
    return [(CHAIN_VHL, "VHL", nt.VHL), (CHAIN_ELOB, "ElonginB", nt.ELONGIN_B),
            (CHAIN_ELOC, "ElonginC", nt.ELONGIN_C)]


def ligand_smiles(reference_json: str = None) -> dict:
    """The reference ligand's SMILES, read from the committed reference artifact by CCD.

    ⛔ FAILS CLOSED. If the artifact is absent or the CCD is not in it, this RAISES rather than falling back to
    anything — a co-fold built on a guessed structure is a fabricated experiment, and it would be invisible
    downstream because every subsequent step would run perfectly on the wrong molecule."""
    path = reference_json or REFERENCE_JSON
    if not os.path.exists(path):
        raise RuntimeError("%s is missing — run the lane's `refs` mode first. The ligand is never typed here."
                           % os.path.basename(path))
    with open(path) as fh:
        doc = json.load(fh)
    rec = (doc.get("ligands") or {}).get(LIGAND_CCD)
    if not rec or not rec.get("smiles_canonical_by_program"):
        raise RuntimeError("CCD %s carries no SMILES in %s — the reference fetch must be re-run; it is not "
                           "acceptable to supply one from memory" % (LIGAND_CCD, os.path.basename(path)))
    smi = rec["smiles_canonical_by_program"].get(LIGAND_SMILES_PROGRAM)
    if not smi:
        raise RuntimeError("CCD %s has no %s SMILES; programs present: %s"
                           % (LIGAND_CCD, LIGAND_SMILES_PROGRAM,
                              sorted(rec["smiles_canonical_by_program"])))
    return {"ccd": LIGAND_CCD, "name": LIGAND_NAME, "smiles": smi,
            "smiles_program": LIGAND_SMILES_PROGRAM,
            "formula": rec.get("formula"), "formula_weight": rec.get("formula_weight"),
            "_source": rec.get("_source")}


# =============================================================================================================
# the co-fold inputs
# =============================================================================================================
def cofold_yaml(target_seq: str, e3, ligand_smi: str) -> str:
    """Boltz-2 YAML for one arm. Delegates the format to `nr4a3_ternary.boltz_yaml` — one home for the schema,
    so a Boltz version bump moves both lanes together."""
    import nr4a3_ternary as t3
    proteins = [(CHAIN_TARGET, target_seq)] + [(cid, seq) for cid, _role, seq in e3]
    return t3.boltz_yaml(proteins, ligand_smi)


def build_cofold_inputs(out_dir: str, reference_json: str = None) -> dict:
    """Write `<out_dir>/{smarca2,smarca4}.yaml` + `cofold-inputs.json`. Needs network (UniProt); $0 CPU.

    `cofold-inputs.json` is the chain CONTRACT the assembler verifies against — chain id, role and the exact
    residue count each chain must have. That contract is the whole reason the chain split here cannot be
    mis-assigned the way the NR-V04 panel's was."""
    import nrv04_ternary as nt
    import nr4a3_ternary as t3
    os.makedirs(out_dir, exist_ok=True)
    lig = ligand_smiles(reference_json)
    e3 = [(cid, role, t3.fetch_seq(acc)) for cid, role, acc in e3_sequences()]
    acc_by_role = {"VHL": nt.VHL, "ElonginB": nt.ELONGIN_B, "ElonginC": nt.ELONGIN_C}
    out = {"_what": "Boltz-2 co-fold inputs for the endpoint-MD sensitivity control: ONE ligand on BOTH real "
                    "paralogue sequences, identical protocol, identical E3 machinery.",
           "ligand": lig, "arms": {}, "chain_contract": {}}
    for gene, system in (("SMARCA2", "smarca2"), ("SMARCA4", "smarca4")):
        con = construct_sequence(gene)
        yml = cofold_yaml(con["sequence"], e3, lig["smiles"])
        path = os.path.join(out_dir, "%s.yaml" % system)
        with open(path, "w") as fh:
            fh.write(yml)
        contract = {CHAIN_TARGET: {"role": "target", "gene": gene, "n_residues": con["n_residues"]}}
        for cid, role, seq in e3:
            contract[cid] = {"role": role, "accession": acc_by_role[role], "n_residues": len(seq)}
        out["arms"][system] = {"gene": gene, "yaml": os.path.basename(path), "construct": con}
        out["chain_contract"][system] = contract
    # ★ THE CROSS-ARM CHECK, HERE RATHER THAN AFTER THE SPEND. The arms must differ ONLY in the target chain;
    # if an E3 subunit differed between them the panel would not be protocol-matched and a difference in E1
    # could come from the machinery instead of the paralogue.
    c2, c4 = out["chain_contract"]["smarca2"], out["chain_contract"]["smarca4"]
    for cid in (CHAIN_VHL, CHAIN_ELOB, CHAIN_ELOC):
        if c2[cid] != c4[cid]:
            raise RuntimeError("E3 chain %s differs between arms (%s vs %s) — the arms would not be "
                               "protocol-matched" % (cid, c2[cid], c4[cid]))
    counts = {cid: c2[cid]["n_residues"] for cid in c2}
    dupes = [n for n in counts.values() if list(counts.values()).count(n) > 1]
    if dupes:
        raise RuntimeError("two chains share a residue count %s — the count-based verification in "
                           "identify_chains would be ambiguous; the contract must stay a bijection" % dupes)
    with open(os.path.join(out_dir, "cofold-inputs.json"), "w") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")
    print("[selcal-stage] wrote %s: ligand %s (%s, %s), SMARCA2 BD %d aa, SMARCA4 BD %d aa, E3 %s"
          % (out_dir, lig["name"], lig["ccd"], lig["formula"],
             out["arms"]["smarca2"]["construct"]["n_residues"],
             out["arms"]["smarca4"]["construct"]["n_residues"],
             {cid: c2[cid]["n_residues"] for cid in (CHAIN_VHL, CHAIN_ELOB, CHAIN_ELOC)}), flush=True)
    return out


# =============================================================================================================
# the assembler
# =============================================================================================================
def chain_census(pdb_path: str) -> list:
    """Per-chain residue counts from a PDB, in FILE ORDER. Measured from the real file, never assumed."""
    counts, order = {}, []
    with open(pdb_path) as fh:
        for line in fh:
            if not line.startswith(("ATOM", "HETATM")):
                continue
            ch, resseq = line[21], line[22:27]
            if ch not in counts:
                counts[ch] = set()
                order.append(ch)
            counts[ch].add(resseq)
    return [{"chain": c, "residues": len(counts[c])} for c in order]


def identify_chains(pdb_path: str, contract: dict) -> dict:
    """Resolve target vs E3 against the co-fold's own chain CONTRACT, verifying every chain. Raises on any
    disagreement.

    Two independent facts must agree for each chain — the id the YAML assigned and the residue count the
    construct implies. Requiring both is what makes this robust to the failure that hit the NR-V04 lane: an
    id-only rule breaks silently if Boltz ever renames chains, and a count-only rule breaks silently the day
    a construct revision brings the target within a few residues of Elongin C. Either alone is a guess; the
    pair is a check."""
    census = chain_census(pdb_path)
    by_chain = {c["chain"]: c["residues"] for c in census}
    missing = [cid for cid in contract if cid not in by_chain]
    extra = [cid for cid in by_chain if cid not in contract]
    if missing or extra:
        raise ValueError("co-fold chains do not match the contract: missing=%s unexpected=%s census=%s "
                         "contract=%s" % (missing, extra, census, sorted(contract)))
    bad = [(cid, by_chain[cid], contract[cid]["n_residues"]) for cid in contract
           if by_chain[cid] != int(contract[cid]["n_residues"])]
    if bad:
        raise ValueError("co-fold chain lengths disagree with the contract (chain, found, expected): %s. "
                         "A chain of the wrong length means the co-fold is not the system that was "
                         "specified; assembling it anyway would produce readouts about something else."
                         % bad)
    target = [cid for cid, spec in contract.items() if spec.get("role") == "target"]
    if len(target) != 1:
        raise ValueError("the contract must name exactly one target chain, found %s" % target)
    e3 = sorted(cid for cid in contract if cid != target[0])
    return {"target_chain": target[0], "e3_chains": e3, "census": census,
            "e3_roles": {cid: contract[cid]["role"] for cid in e3},
            "verified_against": "cofold-inputs.json chain_contract",
            "target_gene": contract[target[0]].get("gene")}


def assemble_unit(cif_path: str, leg_id: str, contract: dict, out_dir: str,
                  reference_json: str = None) -> dict:
    """`<out_dir>/<leg_id>/{complex.pdb, ligand.sdf, chains.json}` from one co-fold CIF.

    The two heavy lifts — pulling the posed ligand out of the CIF with correct bond orders, and the CIF->PDB
    chain surgery — are `nrv04_covalent_assemble`'s, imported rather than re-written. Only the chain
    IDENTIFICATION differs, for the reason in the module docstring."""
    from nrv04_covalent_assemble import extract_ligand_from_cif, write_complex_pdb
    lig = ligand_smiles(reference_json)
    leg_out = os.path.join(out_dir, leg_id)
    os.makedirs(leg_out, exist_ok=True)
    n_lig = extract_ligand_from_cif(cif_path, lig["smiles"], os.path.join(leg_out, "ligand.sdf"))
    complex_pdb = os.path.join(leg_out, "complex.pdb")
    write_complex_pdb(cif_path, sorted(contract), complex_pdb)
    chains = identify_chains(complex_pdb, contract)
    chains["ligand"] = {k: lig[k] for k in ("ccd", "name", "smiles_program", "formula", "_source")}
    chains["ligand"]["heavy_atoms"] = n_lig
    with open(os.path.join(leg_out, "chains.json"), "w") as fh:
        json.dump(chains, fh, indent=2)
    return {"leg": leg_id, "ligand_atoms": n_lig, "out": leg_out, "chains": chains}


# =============================================================================================================
# the co-fold input audit — the ONLY thing licensed to exclude a model
# =============================================================================================================
#: The heavy-atom clash distance below which a predicted structure is unusable. DERIVED from the measured
#: incident rather than chosen: `nrv04-descriptive-v4/nr4a3/seed_3` placed two heavy atoms at **0.181 Å** and
#: the Lennard-Jones term diverged to +2.1e15 kJ/mol, which minimization cannot escape and which yields NaN on
#: the first integration step (AMENDMENT 4). Any pair closer than a covalent bond is in that regime; 1.0 Å is
#: comfortably below the shortest real heavy-atom bond (~1.2 Å for C=O) so this cannot reject a real contact.
MIN_HEAVY_ATOM_SEPARATION_A = 1.0


def cofold_input_audit(pdb_path: str, min_sep_a: float = MIN_HEAVY_ATOM_SEPARATION_A) -> dict:
    """Static, pre-MD audit of one assembled complex: the closest heavy-atom pair between DIFFERENT residues.

    ⛔ THIS IS THE ONLY EVIDENCE THAT MAY EXCLUDE A CO-FOLD MODEL (`selcal_panel.EXCLUDED_COFOLD_MODELS`), and
    the reason is the selection-bias argument AMENDMENT 4 had to make: an exclusion is defensible when the
    fault is a STATIC property of the input, provable BEFORE any MD is interpreted. An exclusion justified by
    how a leg's E1 came out is the retune this program forbids.

    Pure numpy + a PDB read, so it runs on any CI runner with no MD stack."""
    import numpy as np
    names, coords = [], []
    with open(pdb_path) as fh:
        for line in fh:
            if not line.startswith(("ATOM", "HETATM")):
                continue
            el = (line[76:78].strip() or line[12:16].strip()[:1]).upper()
            if el == "H":
                continue
            names.append("%s:%s%s:%s" % (line[21], line[17:20].strip(), line[22:27].strip(),
                                         line[12:16].strip()))
            coords.append((float(line[30:38]), float(line[38:46]), float(line[46:54])))
    if len(coords) < 2:
        return {"ok": False, "why": "fewer than two heavy atoms in %s" % os.path.basename(pdb_path)}
    xyz = np.asarray(coords, dtype="f8")
    res = np.asarray([n.rsplit(":", 1)[0] for n in names])
    # blocked pairwise scan — the assembly is ~5k heavy atoms, so a full N^2 distance matrix is ~200 MB and
    # a blocked min is both cheaper and constant-memory.
    best, best_pair = float("inf"), None
    for i0 in range(0, len(xyz), 512):
        blk = xyz[i0:i0 + 512]
        d = np.linalg.norm(xyz[None, :, :] - blk[:, None, :], axis=-1)
        same = res[i0:i0 + 512][:, None] == res[None, :]
        d[same] = np.inf
        j = int(np.argmin(d))
        v = float(d.flat[j])
        if v < best:
            best = v
            a, b = divmod(j, d.shape[1])
            best_pair = (names[i0 + a], names[b])
    ok = best >= float(min_sep_a)
    return {"ok": bool(ok), "min_heavy_atom_sep_A": round(best, 4), "pair": list(best_pair or ()),
            "threshold_A": float(min_sep_a), "n_heavy_atoms": len(xyz),
            "why": ("" if ok else
                    "two heavy atoms in DIFFERENT residues sit %.3f A apart, below the %.2f A floor. The "
                    "Lennard-Jones term diverges from geometry like this and minimization cannot escape it "
                    "(measured on nrv04-descriptive-v4/nr4a3/seed_3: 0.181 A, PE +2.1e15 kJ/mol, NaN on the "
                    "first step). This is a static INPUT fault, provable before any MD is interpreted."
                    % (best, min_sep_a))}


def _cli(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Sensitivity-control staging ($0 CPU).")
    ap.add_argument("--build-cofold-inputs", metavar="OUT_DIR",
                    help="resolve constructs + write the Boltz YAMLs and the chain contract")
    args = ap.parse_args(argv)
    if args.build_cofold_inputs:
        build_cofold_inputs(args.build_cofold_inputs)
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(_cli())
