"""Offline CHRNA6 readiness inventory; reads only six pinned Git blobs.

No expression arithmetic is performed. --write generates the JSON and memo;
--check checks them byte-for-byte without writing. Counts are identifier/set or
structural counts, never estimates of expression or independent patients.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = "8c1f292536b7d725186491b42c19c87c0b6c855c"
FILES = {
    "panels": "research/modalities/emc-expression-panels.json",
    "arrays": "research/modalities/emc-expression-panels-inputs.json",
    "search": "research/modalities/emc-cohort-search.json",
    "quant": "research/modalities/emc-fourth-cohort-quant.json",
    "seq": "research/modalities/emc-fourth-cohort-quant-inputs.json",
    "primary": "research/autonomy/portfolio-2026-09-05/primary-marker-evidence.json",
}
OUT = ROOT / "research/modalities/expression-validation-readiness"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()


def escape(key):
    return str(key).replace("~", "~0").replace("/", "~1")


def resolve(document, pointer):
    value = document
    if pointer:
        if not pointer.startswith("/"):
            raise ValueError(pointer)
        for part in pointer[1:].split("/"):
            part = part.replace("~1", "/").replace("~0", "~")
            value = value[int(part)] if isinstance(value, list) else value[part]
    return value


class Audit:
    def __init__(self):
        self.docs, self.manifest, self.sources = {}, {}, {}
        for key, path in FILES.items():
            raw = subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)
            self.docs[key] = json.loads(raw)
            self.manifest[key] = {"path": path, "sha256": sha(raw), "bytes": len(raw)}

    def ref(self, key, pointer):
        value = resolve(self.docs[key], pointer)
        name = key + "#" + pointer
        source = {"file": FILES[key], "file_sha256": self.manifest[key]["sha256"],
                  "json_pointer": pointer, "value_sha256": sha(canonical(value))}
        if isinstance(value, (dict, list)):
            source.update(container_type=type(value).__name__, length=len(value))
        else:
            source["value"] = value
        self.sources[name] = source
        return name

    def fact(self, value, refs, method="source_value", status="known"):
        return {"value": value, "status": status, "method": method,
                "evidence": [self.ref(*r) for r in refs]}

    def direct(self, key, pointer):
        value = resolve(self.docs[key], pointer)
        refs = [(key, pointer)]
        if isinstance(value, list):
            refs.extend((key, pointer + "/" + str(i)) for i in range(len(value)))
        return self.fact(value, refs, status="unknown" if value is None else "known")

    def unknown(self, reason, refs):
        return self.fact(None, refs, reason, "unknown")

    def count(self, values, refs, method="count_distinct_exact_identifiers"):
        return self.fact(len(set(values)), refs, method)

    def array(self, matrix):
        p, t = "/platforms/" + escape(matrix), "/targets/" + escape(matrix)
        panel, target = resolve(self.docs["panels"], p), resolve(self.docs["arrays"], t)
        samples, annotations = target["samples"], panel["sample_annotations_verbatim"]
        assert [x["gsm"] for x in samples] == [x["gsm"] for x in annotations]
        emc, comp = panel["EMC_gsms"], panel["comparator_gsms"]
        assert not set(emc) & set(comp)
        assert len(set(emc)) == panel["n_EMC"] and len(set(comp)) == panel["n_comparator"]
        assert len(samples) == panel["n_samples"] == target["n_samples"]
        assert Counter(x["class"] for x in annotations) == panel["class_counts"]
        assert set(emc) == {x["gsm"] for x in annotations if x["class"] == "EMC"}
        assert set(emc + comp) <= {x["gsm"] for x in samples}
        rows = []
        for j, (sample, ann) in enumerate(zip(samples, annotations)):
            sp, ap = t + f"/samples/{j}", p + f"/sample_annotations_verbatim/{j}"
            rows.append({
                "sample_id": self.fact(sample["gsm"], [("arrays", sp + "/gsm"), ("panels", ap + "/gsm")]),
                "unit": "GEO_sample_record_not_verified_patient",
                "title": self.direct("arrays", sp + "/title"),
                "annotation": self.direct("panels", ap + "/annotation"),
                "class": self.direct("panels", ap + "/class"),
                "arm": self.fact("EMC" if sample["gsm"] in emc else "comparator" if sample["gsm"] in comp else "excluded_from_cached_contrast",
                                 [("panels", p + "/EMC_gsms"), ("panels", p + "/comparator_gsms")], "exact_identifier_membership"),
            })
        genes = target["genes"]
        # Cache coverage is distinct from platform coverage. The supplied mapping
        # diagnostics contain no exhaustive probe-to-CHRNA6 annotation table.
        present = "CHRNA6" in genes
        assert not present, "Changed CHRNA6 inputs require a new bounded assessment"
        assert "CHRNA6" not in self.docs["panels"]["gene_reads"]
        assert "CHRNA6" not in target["background_reads_block"]["z"]
        assert "CHRNA6" not in self.docs["arrays"]["genes_wanted"]
        probe_discrepancies = []
        for symbol, gene in genes.items():
            assert len(gene["values"]) == len(samples)
            if len(gene["probe_ids"]) != gene["n_probes_mapping"]:
                gp = t + "/genes/" + escape(symbol)
                probe_discrepancies.append({
                    "gene": self.fact(symbol, [("arrays", gp)], "object_key"),
                    "listed_probe_ID_count": self.fact(len(gene["probe_ids"]), [("arrays", gp + "/probe_ids")], "list_length"),
                    "reported_mapping_count": self.direct("arrays", gp + "/n_probes_mapping"),
                    "interpretation": "Listed probe IDs do not exhaust reported mapping; preserve discrepancy without assuming its cause",
                })
        series = panel["series"]
        excluded_annotations = [x["annotation"] for x in annotations if x["gsm"] not in emc + comp]
        excluded_categories = dict(sorted(Counter(
            "Solitary fibrous tumor" if "Solitary fibrous tumor" in text else
            "pooled RNA" if "pooled RNA" in text else "other_unclassified"
            for text in excluded_annotations).items()))
        return {
            "cohort": self.direct("panels", p + "/series"),
            "platform": self.fact(panel["platform"], [("panels", p + "/platform"), ("arrays", t + "/platform")]),
            "assay_units": self.direct("arrays", t + "/value_kind"),
            "sample_records": rows,
            "counts": {
                "cached_sample_records": self.count([x["gsm"] for x in samples], [("arrays", t + "/samples")]),
                "EMC_sample_records": self.count(emc, [("panels", p + "/EMC_gsms"), ("panels", p + "/n_EMC")]),
                "comparator_sample_records": self.count(comp, [("panels", p + "/comparator_gsms"), ("panels", p + "/n_comparator")]),
                "excluded_sample_records": self.count([x["gsm"] for x in samples if x["gsm"] not in emc + comp], [("arrays", t + "/samples"), ("panels", p + "/EMC_gsms"), ("panels", p + "/comparator_gsms")], "exact_ID_set_difference"),
                "class_counts": self.fact(dict(sorted(Counter(x["class"] for x in annotations).items())), [("panels", p + "/sample_annotations_verbatim"), ("panels", p + "/class_counts")], "count_records_by_cached_class"),
                "series_search_reported_samples": self.direct("search", "/candidates/" + series + "/n_samples"),
                "series_reported_minus_cached_records": self.fact(self.docs["search"]["candidates"][series]["n_samples"] - len(set(x["gsm"] for x in samples)), [("search", "/candidates/" + series + "/n_samples"), ("arrays", t + "/samples")], "reported_series_total_minus_exact_cached_GSM_count;_not_verified_comparators"),
                "excluded_annotation_counts": self.fact(excluded_categories, [("panels", p + "/sample_annotations_verbatim"), ("panels", p + "/EMC_gsms"), ("panels", p + "/comparator_gsms")], "exact_ID_exclusion_then_verbatim_substring_categories_Solitary_fibrous_tumor_or_pooled_RNA_else_other"),
                "unique_specimens": self.unknown("GSMs and titles do not establish one distinct specimen per record", [("arrays", t + "/samples")]),
                "unique_patients": self.unknown("No patient crosswalk supplied", [("arrays", t + "/samples")]),
                "sequencing_runs": self.unknown("Not a sequencing-run inventory", [("arrays", t + "/value_kind")]),
            },
            "CHRNA6": {
                "platform_coverage": self.fact("not_assessed", [("arrays", t + "/probe_symbol_mapping")], "No exhaustive CHRNA6 annotation in allowed inputs; mapping diagnostics are insufficient"),
                "selected_gene_cache_present": self.fact(present, [("arrays", t + "/genes"), ("panels", "/gene_reads"), ("arrays", "/genes_wanted")], "exact_CHRNA6_key_or_member_lookup"),
                "background_cache_present": self.fact(False, [("arrays", t + "/background_reads_block/z")], "exact_CHRNA6_key_lookup"),
                "probe_ids": self.unknown("No CHRNA6 row or complete annotation; null is not zero probes", [("arrays", t + "/genes"), ("arrays", t + "/probe_symbol_mapping")]),
            },
            "existing_values": {
                "probe_ID_count_discrepancies": probe_discrepancies,
                "gene_rows": self.fact(len(genes), [("arrays", t + "/genes")], "dictionary_length"),
                "multi_probe_gene_rows": self.fact(sum(len(g["probe_ids"]) > 1 for g in genes.values()), [("arrays", t + "/genes")], "count_gene_rows_with_more_than_one_probe_ID"),
                "representation": self.fact("One aggregated values vector per gene; probe IDs retained, separate per-probe value vectors absent from these gene rows", [("arrays", t + "/genes"), ("panels", p + "/genome_wide_null/_the_statistic_is_the_panel_s_own")], "inspect_gene_row_schema_and_recorded_aggregation_method"),
                "processed_matrix_locator": self.direct("arrays", t + "/url"),
                "raw_assay_files": self.unknown("Only processed matrix locator is supplied; raw files and current remote availability not assessed", [("arrays", t + "/url")]),
            },
            "independence": "within-study patient identity and cross-study identity unresolved, including overlap with the published reference",
            "decision": "no_go_current_inputs",
            "later_comparison": "CHRNA6 within-platform EMC versus the explicitly enumerated cached comparator arm; requires compatible CHRNA6 observations first",
            "missing_inputs": ["Complete platform CHRNA6 probe annotation and sample-aligned per-probe values with preprocessing/missingness metadata", "Run/sample/specimen/patient crosswalk and reference-study overlap documentation before independent-validation claims", "Pre-specified probe handling and comparator definition; review reference-pool compatibility for two-colour data"],
        }

    def metadata_cohort(self, series):
        p = "/known_cohorts/" + series
        row = {
            "cohort": self.fact(series, [("search", p)], "object_key"),
            "description": self.direct("search", p),
            "platform": self.direct("search", "/candidates/GSE28866/gpl") if series == "GSE28866" else self.unknown("No platform annotation supplied for alias", [("search", p)]),
            "CHRNA6": {"platform_coverage": self.fact("not_assessed", [("search", p)], "Metadata only; no gene annotation or CHRNA6 values in allowed inputs")},
            "decision": "no_go_current_inputs",
            "comparator_count": self.unknown("No enumerated, labelled comparator arm or expression matrix; do not subtract EMC from series total", [("search", p)]),
            "unique_specimens": self.unknown("No specimen crosswalk supplied", [("search", p)]),
            "unique_patients": self.unknown("No patient crosswalk supplied", [("search", p)]),
            "raw_data": self.unknown("No raw or processed matrix locator in this cohort-search entry", [("search", p)]),
            "existing_values": "metadata_only_in_allowed_inputs",
            "missing_inputs": ["Sample-level EMC and comparator identities and annotations", "Platform/gene annotation and CHRNA6 expression matrix with units and processing provenance", "Documented specimen/patient crosswalk, including reference-study overlap"],
        }
        if series == "GSE28866":
            cp = "/candidates/" + series
            row["reported_counts"] = {k: self.direct("search", cp + "/" + k) for k in ["n_samples", "n_gsm_read", "n_samples_naming_emc"]}
            row["reported_counts_scope"] = "source-reported metadata counts, not independently enumerable complete sample roster"
            row["sample_ID_examples"] = [self.direct("search", cp + f"/gsm_overlap_examples/{i}") for i in range(len(resolve(self.docs["search"], cp + "/gsm_overlap_examples")))]
            row["sample_ID_examples_scope"] = "overlap examples only; not identified as EMC and not the complete roster"
            row["independence"] = "cross-study patient identity unresolved; alias relationship separately documented as a source assertion"
        else:
            row["alias_of"] = self.fact("GSE28866", [("search", p)], "explicit_source_assertion_not_independently_reconstructed")
            row["independence"] = "source explicitly reports same deposit/publication/four EMC samples; not a separate validation cohort; exact alias sample crosswalk unavailable"
        return row

    def sequencing(self):
        q, s = self.docs["quant"], self.docs["seq"]
        table = s["run_table"]["rows"]
        run_ids = [x["run_accession"] for x in table]
        assert set(run_ids) == set(s["runs"]) == set(q["per_run"])
        assert len(run_ids) == len(set(run_ids)) == q["n_runs_read"] == q["n_runs_in_deposit"]
        rows, discrepancies = [], []
        for j, r in enumerate(table):
            p = f"/run_table/rows/{j}"
            run = r["run_accession"]
            row = {k: self.direct("seq", p + "/" + k) for k in ["run_accession", "experiment_accession", "sample_accession", "sample_alias", "library_name", "study_accession", "instrument_platform", "instrument_model", "library_strategy", "experiment_title", "fastq_ftp", "fastq_bytes", "fastq_md5"]}
            for k in ["state", "sample_alias", "prognosis", "stopped_because"]:
                row["quant_" + k] = self.direct("quant", "/per_run/" + run + "/" + k)
            row["unit"] = "run_linked_to_BioSample_record_not_verified_patient"
            rows.append(row)
            if r["sample_alias"] != r["library_name"]:
                discrepancies.append(self.fact({"run": run, "sample_alias": r["sample_alias"], "library_name": r["library_name"]}, [("seq", p + "/run_accession"), ("seq", p + "/sample_alias"), ("seq", p + "/library_name")], "exact_string_disagreement_preserved_not_merged"))
        mp = s["probe_map"]
        single = [probe for probe, gene in mp["probe_to_gene"].items() if gene == "CHRNA6"]
        multi = [probe for probe, genes in mp["probe_to_several_genes"].items() if "CHRNA6" in genes]
        assert not single and not multi, "Changed CHRNA6 mapping requires a new bounded assessment"
        assert len(mp["probe_to_gene"]) == mp["n_probes_assigned_to_one_gene"]
        assert len(mp["probe_to_several_genes"]) == mp["n_probes_matching_several_genes"]
        assert len(set(mp["probe_to_gene"].values())) == q["n_genes_with_at_least_one_assigned_probe"]
        assert mp["n_probes_offered"] == len(mp["probe_to_gene"]) + len(mp["probe_to_several_genes"]) + mp["n_probes_unassigned"]
        return {
            "cohort": self.direct("seq", "/bioproject"), "sra_study": self.direct("seq", "/sra_study"),
            "platform": self.direct("quant", "/depositor_assay_description"), "sample_records": rows,
            "counts": {
                "runs": self.count(run_ids, [("seq", "/run_table/rows"), ("quant", "/n_runs_read")]),
                "BioSample_records": self.count([r["sample_accession"] for r in table], [("seq", "/run_table/rows")]),
                "experiments": self.count([r["experiment_accession"] for r in table], [("seq", "/run_table/rows")]),
                "unique_specimens": self.unknown("BioSample accessions are not proof of distinct biological specimens", [("seq", "/run_table/rows")]),
                "unique_patients": self.unknown("No patient linkage provided", [("seq", "/run_table/rows")]),
                "prognosis_label_counts": self.fact(dict(sorted(Counter(r["prognosis"] for r in q["per_run"].values()).items())), [("quant", "/per_run"), ("quant", "/sample_labels")], "count_raw_B_G_labels_without_interpreting_outcomes"),
                "non_EMC_comparator_runs": self.fact(0, [("seq", "/run_table/rows"), ("quant", "/why_no_differential_expression")], "all_deposit_runs_described_as_EMC;_no_non_EMC_arm_supplied"),
            },
            "alias_discrepancies": discrepancies,
            "CHRNA6": {
                "platform_coverage": self.fact("not_assessed", [("quant", "/depositor_assay_description"), ("seq", "/probe_map")], "No manufacturer/design annotation; inferred partial observed-probe map cannot establish absent assay coverage"),
                "uniquely_assigned_observed_probes": self.fact(single, [("seq", "/probe_map/probe_to_gene")], "exact_symbol_lookup_in_inferred_mapping"),
                "ambiguously_assigned_observed_probes": self.fact(multi, [("seq", "/probe_map/probe_to_several_genes")], "exact_symbol_membership_in_inferred_mapping"),
                "usable_gene_values": self.fact(False, [("seq", "/probe_map/probe_to_gene"), ("quant", "/gene_counts_n_rows")], "No CHRNA6 assigned probe; referenced TSV contents outside the six-input audit"),
            },
            "existing_values": {
                "assigned_probes": self.fact(len(mp["probe_to_gene"]), [("seq", "/probe_map/probe_to_gene")], "dictionary_length"),
                "assigned_genes": self.fact(len(set(mp["probe_to_gene"].values())), [("seq", "/probe_map/probe_to_gene"), ("quant", "/n_genes_with_at_least_one_assigned_probe")], "distinct_mapped_symbols"),
                "multi_gene_probes": self.fact(len(mp["probe_to_several_genes"]), [("seq", "/probe_map/probe_to_several_genes")], "dictionary_length"),
                "unassigned_probes": self.direct("seq", "/probe_map/n_probes_unassigned"),
                "offered_probes": self.direct("seq", "/probe_map/n_probes_offered"),
                "mapping_limits": self.direct("seq", "/probe_map/\u26a0 unassigned_means"),
                "per_probe_table_reference": self.direct("quant", "/probe_counts_written_to"),
                "per_probe_table_reported_rows": self.direct("quant", "/probe_counts_n_rows"),
                "per_probe_table_reported_sha256": self.direct("quant", "/probe_counts_sha256"),
                "aggregated_gene_table_reference": self.direct("quant", "/gene_counts_written_to"),
                "aggregated_gene_table_reported_rows": self.direct("quant", "/gene_counts_n_rows"),
                "aggregated_gene_table_reported_sha256": self.direct("quant", "/gene_counts_sha256"),
                "gene_units": self.direct("quant", "/\u26d4 gene_counts_units"),
                "probe_zero_limits": self.direct("quant", "/\u26d4 a_zero_in_the_probe_table"),
                "raw_data_status": "FASTQ locators/bytes/MD5 and completed historical stream records supplied per run; no raw files downloaded or current remote availability verified",
                "table_scope": "TSV names, hashes and row counts are source-reported only; no TSV contents audited",
            },
            "independence": "within-study patient identity and cross-study identity unresolved, including the published reference",
            "decision": "no_go_current_inputs",
            "later_comparison": "No current EMC-versus-mimic comparison: absent non-EMC arm and absent usable CHRNA6 mapping. B/G is not a mimic comparison.",
            "missing_inputs": ["Authoritative assay design/probe-to-CHRNA6 mapping and sample-aligned compatible CHRNA6 measurements", "Compatible non-EMC comparator observations and specimen/patient linkage", "Resolve alias discrepancy before any sample-label analysis; define B/G from primary methods for any separately authorized outcome question"],
        }

    def build(self):
        cohorts = {self.docs["panels"]["platforms"][m]["series"]: self.array(m) for m in sorted(self.docs["arrays"]["targets"])}
        for series in ["GSE28866", "GSE170983"]:
            cohorts[series] = self.metadata_cohort(series)
        cohorts["PRJNA1357027"] = self.sequencing()
        observation = self.docs["primary"]["sources"][0]["observation"]
        match = re.search(r"includes (\d+) EMC and (\d+) mimics", observation)
        if not match:
            raise ValueError("Reference abstract count wording changed")
        reference = {k: self.direct("primary", "/sources/0/" + k) for k in ["pmid", "doi", "url", "observation", "evidence_type", "does_not_establish"]}
        reference["scope"] = self.direct("primary", "/scope")
        reference["reported_counts"] = {label: self.fact(int(match.group(n)), [("primary", "/sources/0/observation")], "regex_capture_in_abstract_level_observation;_not_sample_enumeration") for label, n in [("EMC", 1), ("mimics", 2)]}
        reference["missing"] = "No full text, supplement, sample roster, numerical CISH threshold or discovery/validation crosswalk supplied; do not reconstruct them"
        # Retain the negative search as a dated inventory, never as a current
        # proof that the later SRA deposit does not exist.
        search_rows = {}
        for accession, entry in sorted(self.docs["search"]["candidates"].items()):
            p = "/candidates/" + escape(accession)
            search_rows[accession] = {"accession": self.fact(accession, [("search", p)], "object_key")}
            for field in ["entrytype", "grade", "excluded_because", "n_samples", "n_samples_naming_emc", "n_gsm_read", "gpl", "gsm_overlap_examples"]:
                if field in entry:
                    search_rows[accession][field] = self.direct("search", p + "/" + field)
        array_sets = [{r["sample_id"]["value"] for r in cohorts[k]["sample_records"]} for k in ["GSE24369", "GSE4303"]]
        overlap = self.fact(sorted(array_sets[0] & array_sets[1]), [("arrays", "/targets/" + escape(m) + "/samples") for m in sorted(self.docs["arrays"]["targets"])], "exact_GSM_intersection_only;_empty_does_not_prove_patient_independence")
        return {
            "schema_version": 1, "resource": "paper:PUB-SURFACE-TARGETS", "base_revision": BASE,
            "question": "Which committed EMC cohorts can test the published CHRNA6 reference signal?",
            "decision": "no_go_for_expression_comparison_with_current_allowed_inputs",
            "scope": "Six committed JSON inputs only; no network, expression analysis or manuscript. No assertion of publication readiness.",
            "runtime_context": {"model": "gpt-6-astra", "reasoning_effort": "medium", "timeout_seconds": 1800, "remaining_seconds_at_dispatch": 1775.484, "dispatch_number": 1, "max_dispatches": 1, "max_rounds": 1, "effective_dispatch_limit": 1, "authentication": "saved-chatgpt", "python_executable": "C:\\Users\\mcrae\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe", "elapsed_seconds": None, "usage": None, "remaining_subscription_capacity": None, "unknown_note": "Elapsed time and usage not measured by this deterministic artifact; budget is not elapsed time"},
            "source_manifest": self.manifest,
            "reference_signal": reference, "cohorts": cohorts,
            "identity_policy": "Exact identifiers deduplicated within their namespace only. No fuzzy title matching, patient-count sums or independence inference. Documented alias is retained separately, not added as a cohort.",
            "array_exact_ID_overlap": overlap,
            "unknown_policy": "null with status unknown means unavailable, not zero. not_assessed means assay coverage unestablished. Zero cache matches are not missing platform coverage. Metadata counts remain reported counts when IDs are absent.",
            "historical_search": {"generated_utc": self.direct("search", "/generated_utc"), "verdict": self.direct("search", "/verdict/headline"), "scope": self.direct("search", "/_what_a_negative_bounds"), "candidate_count": self.fact(len(search_rows), [("search", "/candidates")], "dictionary_length"), "entries": search_rows, "interpretation": "Preserved dated search exclusions, not reapplied as acceptance rules and not evidence against the later sequencing deposit"},
            "sources": self.sources,
        }


def memo(d):
    c = d["cohorts"]
    lines = ["# CHRNA6 expression validation readiness", "",
             "**No-go with the six committed inputs.** They contain no usable CHRNA6 expression comparison. This completes the bounded readiness audit; it does not assess publication readiness.", "",
             "The source-keyed [JSON matrix](expression-validation-readiness.json) records exact RFC 6901 pointers, committed-file SHA256 and canonical pointed-value SHA256. Its `sources` keys resolve every fact below; all sample IDs are retained there. [The audit script](expression_validation_readiness.py) reads pinned Git blobs, not mutable input files.", "",
             "| Cohort | Enumerated or reported observations | CHRNA6 and decision |", "|---|---|---|"]
    for k in ["GSE24369", "GSE4303"]:
        counts = c[k]["counts"]
        lines.append(f"| {k} / {c[k]['platform']['value']} | {counts['cached_sample_records']['value']} exact GSMs: {counts['EMC_sample_records']['value']} EMC, {counts['comparator_sample_records']['value']} cached comparators, {counts['excluded_sample_records']['value']} excluded | Not selected in the gene cache; full annotation unavailable, coverage `not_assessed`. No current comparison. |")
    lines += ["| GSE28866 | Source reports 99 sample records and 4 naming EMC; complete IDs and comparator labels absent | Metadata only; coverage `not_assessed`; comparator count unknown, not 95. |",
              "| GSE170983 | Source describes an alias of GSE28866 and the same four EMC samples | Retain the documented alias; no additional validation cohort. Exact alias crosswalk unavailable. |",
              "| PRJNA1357027 / SRP640302 | 12 exact runs, 12 BioSample records, 12 experiments; raw B/G labels 6/6; no non-EMC comparator runs supplied | No CHRNA6 assignment in the partial inferred map; assay design coverage `not_assessed`. No EMC-versus-mimic comparison. |", "",
              "Array details are in `cohorts.GSE24369` and `cohorts.GSE4303`. The first comparator arm has 17 LGFMS, 6 desmoid fibromatosis and 6 cached `fibrosarcoma` labels (verbatim annotations say myxofibrosarcoma). Its 7 exclusions retain 5 solitary fibrous tumors and 2 pooled skeletal-muscle RNA records; these are not silently added as controls. The second arm has 3 DFSP and 3 GIST records. The search reports 36 samples for the entire GSE4303 series, whereas the supplied GPL3290 cache has 16; the other 20 are not a verified comparator arm.", "",
              "Unique patients and biological specimens remain unknown. Different GSMs or BioSamples do not establish independent patients. The two array GSM sets have no exact overlap; cross-study identity, including overlap with the published reference, remains unresolved. The sequencing run SRR35940654 has sample alias Si22 but library name Si21; both are preserved, without merging or guessing the correct label. B/G meanings are not inferred from the six/six split.", "",
              "The abstract-level reference (`reference_signal`, primary input `/sources/0/observation`) reports CHRNA6 RNA CISH in 25 EMC and 685 mimics. These are reported study counts, not enumerated independent patients. No full text, supplementary table, numeric threshold, discovery roster or validation crosswalk is supplied. The expression caches cannot reproduce a tissue CISH interpretation threshold, and no independence or clinical claim follows from this audit.", "",
              "Existing array data have one gene-level values vector with probe IDs retained; multi-probe rows are aggregated, not separate per-probe observations. The GPL3290 GAPDH row lists 12 probe IDs but reports 384 mappings; this discrepancy is retained, so listed IDs cannot be assumed exhaustive. The processed matrix URLs are catalogued, but raw array files are not documented in the allowed inputs. Sequencing JSON references per-probe and summed raw gene-count TSVs, with reported hashes/row counts; those TSVs were not opened. The inferred map contains 906 single-gene probe assignments to 862 genes, 77 ambiguous assignments and 662 unassigned probes out of 1,645 offered. Neither mapping contains CHRNA6. Partial mapping and lossy persistence cannot prove absent assay coverage or absent expression. FASTQ locators and historical completed-stream records are retained; remote availability was not checked.", "",
              "A later specified comparison could ask whether CHRNA6 differs between EMC and the enumerated comparator arm within each array platform. First supply authoritative CHRNA6 probe annotation, aligned per-probe measurements and preprocessing/missingness metadata; specify probe handling and comparator inclusion. For the two-colour array, resolve reference-pool compatibility before comparing groups. For an independent validation claim, also supply a specimen/patient crosswalk against the reference study and other cohorts. GSE28866 additionally needs its full labelled expression roster and matrix. The sequencing deposit needs an authoritative CHRNA6 design mapping, compatible measurements and a non-EMC comparator arm. No current input supports proceeding to expression statistics.", "",
              "The historical cohort-search exclusions and unreadable/unknown metadata are retained in `historical_search`; its earlier negative GEO search is not evidence that the later SRA deposit is absent. No equivalent complete readiness mapping was found in the committed readiness/validation inventory and CHRNA6 outcome search; existing evidence was reused without recomputing expression.", "",
              "Reproduce with the runner-supplied Python executable and `research/modalities/expression_validation_readiness.py --write`; verify with `--check`. The check covers source readability, exact array arm/sample counts, cached vector dimensions, sequencing identifier consistency, inferred mapping counts and deterministic JSON/memo bytes. A separate stdin verifier (not importing the generator) passed all 6 file hashes, 1,175 source pointers/value hashes, direct fact values, array arms, sequencing IDs and label counts, mapping cardinalities, alias discrepancy and 56 search entries. A focused separate check passed the excluded-annotation counts and series-minus-cache counts. The initial generator check exposed the GAPDH discrepancy; the audit was corrected to preserve it. This is scoped audit verification; repository preflight and publication suites were not run. Coordinator collection remains downstream.", "",
              f"Base: `{BASE}`. Configured model `gpt-6-astra`, effort `medium`, one dispatch, total budget 1,800 seconds; dispatch-time remaining 1,775.484 seconds. Elapsed time, token usage and remaining subscription capacity are unknown. No network, downloads, installs, paid compute, additional agents, commits or publication actions.", ""]
    return '---\nid: DOC-EXPRESSION-VALIDATION-READINESS\ntitle: CHRNA6 expression validation readiness\nkind: memo\nstatus: generated\ngenerator: research/modalities/expression_validation_readiness.py\ndate: 2026-09-05\nlast_verified: 2026-09-05\npurpose: Identify which committed EMC cohorts support a CHRNA6 expression comparison.\nscope: Six-input readiness audit; no new expression or clinical inference.\naudience: [maintainers, autonomous research agents]\n---\n\n' + "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    audit = Audit()
    data = audit.build()
    outputs = {OUT.with_suffix(".json"): json.dumps(data, ensure_ascii=True, indent=2, sort_keys=True) + "\n", OUT.with_suffix(".md"): memo(data)}
    for path, content in outputs.items():
        if args.write:
            path.write_bytes(content.encode("utf-8"))
        elif path.read_bytes() != content.encode("utf-8"):
            raise SystemExit(f"FAIL: stale or modified artifact: {path.relative_to(ROOT)}")
    print(json.dumps({"status": "PASS", "mode": "write" if args.write else "check", "base_revision": BASE, "input_files": len(FILES), "source_pointers": len(audit.sources), "cohort_rows_including_alias": len(data["cohorts"]), "decision": data["decision"], "output_sha256": {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in outputs}}, sort_keys=True))


if __name__ == "__main__":
    main()
