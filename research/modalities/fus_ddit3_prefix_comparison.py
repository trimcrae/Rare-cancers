"""Conditional native FUS prefixes; local committed inputs, no fusion reconstruction.

Run with the configured Python interpreter from any directory. Only the companion
JSON and Markdown are written. No network, external libraries or census imports.
"""

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUTS = (
    "research/autonomy/evidence-fus-ddit3-2026-09-05/primary-junctions.json",
    "research/modalities/emc-fet-construct-designs.json",
    "research/modalities/emc-fet-idr-census.json",
    "research/modalities/fet-sequences-cache.json",
)
OUTPUT_STEM = "research/modalities/fus-ddit3-prefix-comparison"
MODEL_CHECKS = (
    "exon_lengths_sum_equals_cdna",
    "coding_nt_sum_equals_cds",
    "cdna_slice_at_utr5_equals_cds",
    "cds_translation_equals_protein",
    "first_transcript_exon_is_coding",
)
MAPPING = (
    "Assume the reported literature exon ranks correspond to committed "
    "ENST00000254108 and that FUS is retained from its native start through "
    "the end of the named exon. This correspondence has not been established "
    "by accession-version sequence alignment."
)
LIMITS = [
    "Exploratory secondary sequence arithmetic on three sourced exon-level variants; "
    "not experimental or biological validation.",
    "No fusion nucleotide sequence is supplied. Junction codons, junction residues, "
    "DDIT3 sequence and the whole-fusion RG count remain unresolved.",
    "A zero native-prefix RG count does not prove zero RG in a whole fusion. "
    "A positive internal prefix count persists regardless of the unresolved junction "
    "under the explicit mapping assumption.",
    "The separate ATM mechanism experiment's exact FUS::CHOP construct/variant "
    "is not established by this input; these rows do not validate a mechanism positive control.",
    "No ATM mechanism, ATR response, safety, efficacy or clinical-stratification "
    "conclusion follows. The existing census precondition and acceptance rule are unchanged.",
]


class InputError(ValueError):
    """The supplied inputs do not support the conditional arithmetic."""


def require(condition, message):
    if not condition:
        raise InputError(message)


def integer(value, name, minimum=0):
    require(type(value) is int and value >= minimum, f"Invalid {name}: {value!r}")
    return value


def rg_pairs(sequence):
    """Every matching adjacent pair, with both coordinates 1-based and inclusive."""
    return [[i + 1, i + 2] for i in range(len(sequence) - 1)
            if sequence[i:i + 2] == "RG"]


def native_prefix(protein, coding_nt):
    """Exclude a partial codon and all dipeptides crossing the complete prefix."""
    integer(coding_nt, "retained coding_nt")
    require(coding_nt <= 3 * len(protein), "Retained coding_nt exceeds native protein")
    complete, residual = divmod(coding_nt, 3)
    prefix = protein[:complete]
    pairs, total = rg_pairs(prefix), len(rg_pairs(protein))
    return {
        "complete_native_residues": complete,
        "residual_native_nucleotides": residual,
        "native_prefix_sequence": prefix,
        "native_terminal_residue": prefix[-1] if prefix else None,
        "rg_pairs_1based": pairs,
        "rg_count": len(pairs),
        "total_native_fus_rg_count": total,
        "retained_rg_fraction": {
            "numerator": len(pairs), "denominator": total,
            "exact": str(Fraction(len(pairs), total)) if total else None,
        },
        "native_prefix_meets_zero_rg_rule": len(pairs) == 0,
        "junction": {
            "codon_status": "unresolved_partial_codon" if residual else "at_codon_boundary",
            "first_unresolved_residue_position": complete + 1,
            "unresolved_partial_codon_position": complete + 1 if residual else None,
            "residue": None,
            "ddit3_sequence": None,
            "whole_fusion_rg_count": None,
            "rg_crossing_complete_prefix_boundary_possible": prefix.endswith("R"),
            "boundary_scope": "Only a terminal R could start an RG crossing the complete "
            "prefix boundary. The next residue is unknown; further junction/downstream "
            "RGs are not assessed. The native continuation is not a fusion sequence.",
        },
    }


def exon_arithmetic(model, retained_rank):
    """Independently sum coding lengths, then check both endpoint representations."""
    integer(retained_rank, "retained exon rank", 1)
    utr5 = integer(model["utr5_len"], "utr5_len")
    by_rank = {}
    for exon in model["exons"]:
        rank = integer(exon["transcript_exon_rank"], "exon rank", 1)
        require(rank not in by_rank, f"Duplicate exon rank {rank}")
        by_rank[rank] = exon
    terms, running, previous_end = [], 0, 0
    for rank in range(1, retained_rank + 1):
        require(rank in by_rank, f"Missing exon rank {rank}")
        exon = by_rank[rank]
        nt = integer(exon["coding_nt_in_exon"], f"exon {rank} coding_nt")
        end = integer(exon["cdna_end_exclusive"], f"exon {rank} cDNA end")
        start = integer(exon["cdna_start_0based"], f"exon {rank} cDNA start")
        require(start == previous_end and end > start, f"Exon {rank} cDNA continuity mismatch")
        require(end - start == exon["exon_length_nt"], f"Exon {rank} length mismatch")
        running += nt
        require(running == exon["cumulative_coding_nt_through_exon"],
                f"Exon {rank} cumulative coding arithmetic mismatch")
        require(running == end - utr5,
                f"Exon {rank} cDNA-minus-UTR arithmetic mismatch")
        terms.append({"exon_rank": rank, "coding_nt": nt})
        previous_end = end
    last = by_rank[retained_rank]
    return {
        "coding_nt_terms": terms,
        "coding_nt_sum": sum(term["coding_nt"] for term in terms),
        "model_cumulative_coding_nt": last["cumulative_coding_nt_through_exon"],
        "cdna_end_exclusive": last["cdna_end_exclusive"],
        "utr5_len": utr5,
        "cdna_end_minus_utr5_nt": last["cdna_end_exclusive"] - utr5,
        "three_arithmetic_routes_agree": True,
    }


def validate_model(designs, census, protein):
    model = designs["gene_models"]["FUS"]
    require(model["transcript"] == "ENST00000254108", "Unexpected FUS transcript")
    identity = designs["ensembl_vs_uniprot_sequences"]["FUS"]
    require(identity["identical"] is True, "Committed FUS Ensembl/UniProt identity flag is not true")
    require(designs["gene_model_self_checks_all_pass"] is True, "Committed model aggregate failed")
    checks = model["self_checks"]
    for key in MODEL_CHECKS:
        require(checks[key] is True, f"Committed FUS model self-check failed: {key}")
    require(protein and set(protein) <= set("ACDEFGHIKLMNPQRSTVWY"), "Invalid FUS protein sequence")
    lengths = {"cache": len(protein), "ensembl": identity["ensembl_len"],
               "uniprot": identity["uniprot_len"],
               "census": census["wild_type_annotation"]["FUS"]["length"]}
    require(all(type(n) is int and n == len(protein) for n in lengths.values()),
            "FUS protein lengths disagree")
    exons = model["exons"]
    ranks = [e["transcript_exon_rank"] for e in exons]
    require(all(type(r) is int for r in ranks) and sorted(ranks) == list(range(1, len(exons) + 1)),
            "Missing or duplicate FUS model exon rank")
    require(checks["n_transcript_exons"] == len(exons), "FUS transcript exon count mismatch")
    require(checks["n_coding_exons"] == sum(e["coding_nt_in_exon"] > 0 for e in exons),
            "FUS coding exon count mismatch")
    # The committed model CDS convention includes its terminal stop codon.
    total = sum(integer(e["coding_nt_in_exon"], "model coding_nt") for e in exons)
    require(total == 3 * (len(protein) + 1), "Model coding length versus protein-plus-stop mismatch")
    return {
        "transcript": model["transcript"], "translation": model["translation"],
        "committed_ensembl_uniprot_identical": identity["identical"],
        "committed_fus_self_checks": checks,
        "committed_aggregate_self_checks_all_pass": designs["gene_model_self_checks_all_pass"],
        "protein_lengths_aa": lengths, "protein_lengths_agree": True,
        "all_exon_coding_nt_sum": total,
        "protein_nt_plus_terminal_stop_nt": 3 * len(protein) + 3,
        "verification_scope": "Identity and translation self-checks are committed assertions, "
        "not newly aligned or translated here. Lengths, exon counts and retained-prefix "
        "arithmetic are checked locally from the supplied model and protein cache.",
    }


def compare(evidence, designs, census, sequences):
    protein = sequences["FUS"]
    model_checks = validate_model(designs, census, protein)
    annotation = census["wild_type_annotation"]["FUS"]
    native_pairs = rg_pairs(protein)
    require(bool(native_pairs), "FUS has no native RGs; frozen first-RG comparison unsupported")
    first, ceiling = annotation["first_RG_dipeptide_at"], annotation["rgg_free_ceiling"]
    require(first == native_pairs[0][0], "Frozen first RG disagrees with direct sequence scan")
    require(ceiling == first - 1, "Frozen RGG-free ceiling disagrees with first RG")
    require(evidence["fusion"] == "FUS::DDIT3", "Unexpected source fusion")
    require(bool(evidence["junctions"]), "No sourced junctions")
    rows, seen = [], set()
    for junction in evidence["junctions"]:
        label = junction["reported_type"]
        require(label and label not in seen, "Missing or duplicate source variant label")
        seen.add(label)
        require(junction["five_prime_gene"] == "FUS" and junction["three_prime_gene"] == "DDIT3",
                f"Unexpected genes for type {label}")
        integer(junction["three_prime_exon"], "DDIT3 exon rank", 1)
        arithmetic = exon_arithmetic(designs["gene_models"]["FUS"], junction["five_prime_exon"])
        prefix = native_prefix(protein, arithmetic["coding_nt_sum"])
        q = prefix["complete_native_residues"]
        zero = prefix["native_prefix_meets_zero_rg_rule"]
        comparison = {
            "frozen_first_RG_dipeptide_at": first,
            "frozen_rgg_free_ceiling": ceiling,
            "complete_prefix_at_or_below_frozen_ceiling": q <= ceiling,
            "first_native_rg_wholly_inside_prefix": first + 1 <= q,
            "direct_count_agrees_with_first_rg": zero == (q < first + 1),
            "direct_count_agrees_with_frozen_ceiling_classification": zero == (q <= ceiling),
            "boundary_note": "At a cut on the first R itself, its following G is outside "
            "the prefix: zero internal RG can extend one residue beyond the frozen ceiling. "
            "This comparison does not redefine the frozen ceiling or the count-based rule.",
        }
        rows.append({"source_variant": junction, "arithmetic": arithmetic,
                     **prefix, "frozen_census_consistency": comparison})
    return {
        "schema": "emc-fus-ddit3-conditional-native-prefix/1",
        "question": "Do all sourced FUS::DDIT3 native FUS prefixes meet rg_count == 0?",
        "analysis_class": "exploratory_secondary_sequence_arithmetic",
        "mapping_assumption": MAPPING,
        "accession_version_alignment_established": False,
        "source": evidence["source"],
        "source_mapping_status": evidence["mapping_status"],
        "source_remaining_gaps": evidence["remaining_gaps"],
        "model_checks": model_checks,
        "native_fus_rg_pairs_1based": native_pairs,
        "total_native_fus_rg_count": len(native_pairs),
        "zero_rg_rule": "rg_count == 0; evaluated only on the completely encoded native FUS prefix",
        "frozen_census_verdict_criterion": census["_operational_definitions"]["verdict_criterion"],
        "variants": rows,
        "all_native_prefixes_meet_zero_rg_rule": all(r["native_prefix_meets_zero_rg_rule"] for r in rows),
        "limitations": LIMITS,
    }


def build(root=ROOT):
    documents, provenance = [], []
    for relative in INPUTS:
        raw = (root / relative).read_bytes()
        documents.append(json.loads(raw))
        provenance.append({"path": relative, "sha256": hashlib.sha256(raw).hexdigest()})
    try:
        result = compare(*documents)
    except (KeyError, TypeError) as exc:
        raise InputError(f"Missing or malformed required input field: {exc}") from exc
    result["input_provenance"] = provenance
    return result


def markdown(result):
    lines = [
        "---", "id: DOC-FUS-DDIT3-PREFIX-COMPARISON",
        "title: Conditional native FUS prefixes in sourced FUS::DDIT3 variants",
        "level: L4", "kind: memo", "status: generated",
        "generator: research/modalities/fus_ddit3_prefix_comparison.py",
        'purpose: "Compare the three sourced native FUS prefixes with the existing zero-RG rule."',
        'scope: "Conditional secondary sequence arithmetic; no complete fusion or mechanism validation."',
        "audience: [maintainers, autonomous research agents]",
        "date: 2026-09-05", "last_verified: 2026-09-05", "---", "",
        "# Conditional native FUS prefix comparison", "",
        "**All prefixes meet the zero-RG rule: "
        + ("yes" if result["all_native_prefixes_meet_zero_rg_rule"] else "no") + ".** "
        "The table reports exact native-prefix arithmetic under the assumption below.", "",
        MAPPING, "",
        "The [committed primary-junction record](../autonomy/evidence-fus-ddit3-2026-09-05/primary-junctions.json) "
        "supplies every type and exon rank, from the indexed primary abstract of "
        f"Bode-Lesniewska et al. ({result['source']['year']}; PMID {result['source']['pmid']}; "
        f"DOI {result['source']['doi']}). No new retrieval was performed.", "",
        "For each row, sum `coding_nt_in_exon` from exon 1 through the sourced retained exon; "
        "compare that sum with `cumulative_coding_nt_through_exon` and "
        "`cdna_end_exclusive - utr5_len`. Divide by three: the quotient determines the only "
        "protein slice counted, and the remainder is untranslated here. Scan every adjacent "
        "pair in that slice, including overlapping search windows; both residues must be inside it. "
        "Positions are 1-based, inclusive; lengths are nt or amino-acid residues as labeled. "
        "Three source variants are evaluated; there are no biological replicates or statistical "
        "uncertainty estimates. Uncertainty concerns mapping and the unresolved junction.", "",
        "| Type | FUS exon / DDIT3 exon | Coding-nt sum = stored cumulative | cDNA end - UTR (nt) | Division by 3 | Native terminal residue | Internal RG / native total | Exact fraction | Prefix RG = 0 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in result["variants"]:
        j, a = row["source_variant"], row["arithmetic"]
        lines.append(
            f"| {j['reported_type']} | {j['five_prime_exon']} / {j['three_prime_exon']} | "
            + " + ".join(str(t["coding_nt"]) for t in a["coding_nt_terms"])
            + f" = {a['coding_nt_sum']} | {a['cdna_end_exclusive']} - {a['utr5_len']} = "
            f"{a['cdna_end_minus_utr5_nt']} | {row['complete_native_residues']} aa + "
            f"{row['residual_native_nucleotides']} nt | {row['native_terminal_residue']} | "
            f"{row['rg_count']} / {row['total_native_fus_rg_count']} | "
            f"{row['retained_rg_fraction']['exact']} | "
            + ("yes" if row["native_prefix_meets_zero_rg_rule"] else "no") + " |")
    lines.append("")
    for row in result["variants"]:
        pairs = ", ".join(f"{r}-{g}" for r, g in row["rg_pairs_1based"]) or "none"
        lines.append(f"- Type {row['source_variant']['reported_type']} internal RG positions: {pairs}. "
                     f"First unresolved residue position: {row['junction']['first_unresolved_residue_position']}.")
    checks = result["model_checks"]
    frozen = result["variants"][0]["frozen_census_consistency"]
    lines += ["", f"Native FUS contains {result['total_native_fus_rg_count']} RG dipeptides. "
              "The JSON enumerates all native pairs and every retained prefix sequence. "
              f"The frozen first RG begins at {frozen['frozen_first_RG_dipeptide_at']} and "
              f"`rgg_free_ceiling` is {frozen['frozen_rgg_free_ceiling']}; all three rows agree "
              "with both reference checks. The ceiling is only a consistency reference: an "
              "R at the last complete position cannot count as an internal RG without its G. "
              "The census and its `rg_dipeptides_retained == 0` precondition are unchanged.", "",
              f"The cache, committed Ensembl/UniProt lengths and census length agree at "
              f"{checks['protein_lengths_aa']['cache']} aa. The committed identity flag, FUS "
              "model self-checks and aggregate flag are true. All-exon coding length is "
              f"{checks['all_exon_coding_nt_sum']} nt, consistent with the protein plus one "
              "terminal stop codon. These stored identity/translation assertions were checked "
              "for presence and success; this run did not repeat alignment or translation.", "",
              "Each row leaves one native nucleotide in a partial codon; its amino acid is "
              "unresolved. None of these complete prefixes ends in R, so no RG can start at "
              "its last complete residue and cross the boundary. RGs involving the unresolved "
              "codon or later sequence remain unassessed; no junction residue or DDIT3 sequence "
              "is reconstructed.", ""]
    lines.extend(f"- {limit}" for limit in result["limitations"])
    lines += ["", "Reproduce with the configured Python executable and "
              "`research/modalities/fus_ddit3_prefix_comparison.py`; add `--check` to compare "
              "both outputs without writing. Behavioral tests are in "
              "`tests/test_fus_ddit3_prefix_comparison.py`. Exact input paths and SHA256 hashes "
              "are recorded in [the deterministic JSON](fus-ddit3-prefix-comparison.json). "
              "Stop condition: these conditional rows, this note and arithmetic/boundary tests; "
              "mapping alignment and identifying the ATM experiment construct are separate work.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check both outputs without writing")
    args = parser.parse_args()
    try:
        result = build()
        outputs = {ROOT / (OUTPUT_STEM + ".json"): json.dumps(result, indent=2, ensure_ascii=True) + "\n",
                   ROOT / (OUTPUT_STEM + ".md"): markdown(result)}
        if args.check:
            stale = [p.name for p, content in outputs.items()
                     if not p.exists() or p.read_bytes() != content.encode("utf-8")]
            require(not stale, "Missing or stale outputs: " + ", ".join(stale))
            print("PASS: JSON and Markdown match deterministic regeneration")
        else:
            for path, content in outputs.items():
                path.write_bytes(content.encode("utf-8"))
                print(f"Wrote {path.relative_to(ROOT).as_posix()}")
    except (InputError, OSError, json.JSONDecodeError) as exc:
        parser.exit(1, f"BLOCKED: {exc}\n")


if __name__ == "__main__":
    main()
