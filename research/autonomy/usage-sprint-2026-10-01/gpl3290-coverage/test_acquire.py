"""Synthetic source-cohort/channel integrity cases; no empirical expression tests."""
import copy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("audit", Path(__file__).with_name("acquire.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
EXPECTED = {"GSM1": "EMC fixture", "GSM2": "DFSP fixture"}

def fixture():
    rows = ["^SERIES = GSE4303", "^PLATFORM = GPL999",
      "!platform_table_begin", "ID\tGB_ACC", "outside\tOUTSIDE", "!platform_table_end",
      "^PLATFORM = GPL3290", "!Platform_title = Synthetic custom cDNA platform",
      "!platform_table_begin", "ID\tGB_ACC", "p1\tU62435", "p2\tAK298798", "!platform_table_end"]
    for sid, title in EXPECTED.items():
        rows.extend(["^SAMPLE = " + sid, "!Sample_title = " + title,
          "!Sample_platform_id = GPL3290", "!Sample_channel_count = 2",
          "!Sample_source_name_ch1 = CRH-mRNA", "!Sample_molecule_ch1 = polyA RNA",
          "!Sample_label_ch1 = Cy3", "!Sample_source_name_ch2 = " + title,
          "!Sample_molecule_ch2 = polyA RNA", "!Sample_label_ch2 = Cy5",
          "!Sample_data_processing = Synthetic log ratio protocol",
          "#VALUE = Synthetic log ratio", "!sample_table_begin", "ID_REF\tVALUE",
          "p1\tINVALID_NUMERIC_TOKEN_MUST_BE_IGNORED", "!sample_table_end"])
    rows.extend(["^SAMPLE = GSM999", "!Sample_platform_id = GPL999",
                 "!sample_table_begin", "ID_REF\tVALUE", "x\tNAN", "!sample_table_end"])
    return "\n".join(rows) + "\n"

def projection():
    return m.parse_family(fixture().splitlines(keepends=True), EXPECTED)

class CohortIntegrity(unittest.TestCase):
    def parse_bad(self, text):
        with self.assertRaises(ValueError):
            m.parse_family(text.splitlines(keepends=True), EXPECTED)
    def check_bad(self, p):
        with self.assertRaises((ValueError, KeyError, TypeError)):
            m.check_projection(p, EXPECTED)
    def test_correct_target_and_metadata_only(self):
        p = projection()
        m.check_projection(p, EXPECTED)
        self.assertEqual(p["platform_table_rows"], 2)
        self.assertEqual(set(p["samples"]), set(EXPECTED))
        self.assertFalse(p["expression_values_parsed"])
        self.assertNotIn("values", p["samples"]["GSM1"])
        self.assertEqual(p["literal_CHRNA6_annotation_rows"], [])
    def test_other_platform_sample_stays_outside_cached_arm(self):
        p = projection()
        self.assertIn("GSM999", p["observed_series_sample_ids"])
        self.assertNotIn("GSM999", p["samples"])
    def test_changed_series_refused(self):
        self.parse_bad(fixture().replace("GSE4303", "GSE4304"))
    def test_changed_cached_platform_refused(self):
        self.parse_bad(fixture().replace("!Sample_platform_id = GPL3290", "!Sample_platform_id = GPL6244", 1))
    def test_duplicate_cached_sample_refused(self):
        self.parse_bad(fixture().replace("^SAMPLE = GSM2", "^SAMPLE = GSM1"))
    def test_missing_cached_sample_refused(self):
        self.parse_bad(fixture().replace("^SAMPLE = GSM2", "^SAMPLE = GSM3"))
    def test_two_colour_declaration_required(self):
        self.parse_bad(fixture().replace("!Sample_channel_count = 2", "!Sample_channel_count = 1", 1))
    def test_missing_second_channel_refused(self):
        self.parse_bad(fixture().replace("!Sample_molecule_ch2 = polyA RNA\n", "", 1))
    def test_empty_protocol_retained_as_empty_not_invented(self):
        p = m.parse_family(fixture().replace("Synthetic log ratio protocol", "").splitlines(keepends=True), EXPECTED)
        self.assertEqual(p["samples"]["GSM1"]["metadata"]["!Sample_data_processing"], [""])
    def test_source_cache_title_mismatch_refused(self):
        self.parse_bad(fixture().replace("!Sample_title = EMC fixture", "!Sample_title = other title"))
    def test_ragged_target_annotation_refused(self):
        self.parse_bad(fixture().replace("p1\tU62435", "p1\tU62435\textra"))
    def test_duplicate_target_probe_refused(self):
        self.parse_bad(fixture().replace("p2\tAK298798", "p1\tAK298798"))
    def test_target_annotation_missing_refused(self):
        self.parse_bad(fixture().replace("^PLATFORM = GPL3290", "^PLATFORM = GPL888"))
    def test_truncated_source_table_refused(self):
        self.parse_bad(fixture().rsplit("!sample_table_end", 1)[0])
    def test_coherent_wrong_platform_projection_refused(self):
        p = projection()
        s = p["samples"]["GSM1"]
        s["metadata"]["!Sample_platform_id"] = ["GPL6244"]
        for row in s["metadata_lines"]:
            row["text"] = row["text"].replace("GPL3290", "GPL6244")
        self.check_bad(p)
    def test_parsed_channel_without_raw_binding_refused(self):
        p = projection()
        p["samples"]["GSM1"]["metadata"]["!Sample_source_name_ch1"] = ["UHR"]
        self.check_bad(p)
    def test_coherent_channel_removal_refused(self):
        p = projection()
        s = p["samples"]["GSM1"]
        del s["metadata"]["!Sample_molecule_ch2"]
        s["metadata_lines"] = [r for r in s["metadata_lines"] if not r["text"].startswith("!Sample_molecule_ch2")]
        self.check_bad(p)
    def test_coherent_one_channel_mutation_refused(self):
        p = projection()
        s = p["samples"]["GSM1"]
        s["metadata"]["!Sample_channel_count"] = ["1"]
        for r in s["metadata_lines"]:
            r["text"] = r["text"].replace("!Sample_channel_count = 2", "!Sample_channel_count = 1")
        self.check_bad(p)
    def test_descriptor_group_mutation_refused(self):
        p = projection()
        p["reference_descriptor_groups"][0]["sample_ids"].append("GSM999")
        self.check_bad(p)
    def test_distinct_descriptors_make_groups_without_pool_identity_claim(self):
        p = m.parse_family(fixture().replace("!Sample_source_name_ch1 = CRH-mRNA",
                     "!Sample_source_name_ch1 = UHR", 1).splitlines(keepends=True), EXPECTED)
        m.check_projection(p, EXPECTED)
        self.assertEqual(len(p["reference_descriptor_groups"]), 2)
        self.assertIn("unestablished", p["reference_interpretation"])
    def test_false_expression_analysis_marker_refused(self):
        p = projection()
        p["expression_values_parsed"] = True
        self.check_bad(p)
    def test_annotation_raw_binding_refused(self):
        p = projection()
        p["annotation_examples"][0]["fields"]["GB_ACC"] = "WRONG"
        self.check_bad(p)
    def test_literal_chrname_row_preserved_without_assignment_inference(self):
        src = fixture().replace("ID\tGB_ACC", "ID\tGene Symbol").replace("p1\tU62435", "p1\tCHRNA6")
        p = m.parse_family(src.splitlines(keepends=True), EXPECTED)
        m.check_projection(p, EXPECTED)
        self.assertEqual(len(p["literal_CHRNA6_annotation_rows"]), 1)
        self.assertIn("unestablished", p["coverage_interpretation"])
    def test_deadline_is_not_swallowed_by_request(self):
        with patch.object(m.urllib.request, "build_opener") as builder:
            builder.return_value.open.side_effect = m.CycleDeadline("synthetic deadline")
            with self.assertRaises(m.CycleDeadline):
                m.request(m.URL, Path("not-created"), 100)
    def test_source_redirect_refused(self):
        with self.assertRaises(ValueError):
            m.NoRedirect().redirect_request(None, None, None, None, None, "https://example.org")

if __name__ == "__main__":
    unittest.main()
