"""Synthetic source-integrity regressions; no patient measurements are manufactured."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("acquire", Path(__file__).with_name("acquire.py"))
acquire = importlib.util.module_from_spec(spec)
spec.loader.exec_module(acquire)


def source():
    return [
        "^PLATFORM = GPL6244\n", "!platform_table_begin\n",
        "ID\tgene_assignment\n",
        "p1\tNM_synthetic // CHRNA6 // synthetic fixture // 8973\n",
        "!platform_table_end\n", "^SAMPLE = GSM_SYNTHETIC\n",
        "!Sample_platform_id = GPL6244\n",
        "!Sample_title = synthetic sample\n",
        "!Sample_data_processing = synthetic fixture preprocessing\n",
        "#VALUE = RMA log2 signal\n", "!sample_table_begin\n",
        "ID_REF\tVALUE\n", "p1\t4.25\n", "!sample_table_end\n",
    ]


class SourceIntegrity(unittest.TestCase):
    def parse(self, lines):
        return acquire.parse_family(lines, ["GSM_SYNTHETIC"])

    def test_complete_source_and_projection_binding(self):
        p = self.parse(source())
        acquire.check_projection(p)
        self.assertEqual(p["samples"]["GSM_SYNTHETIC"]["values"]["p1"]["value"], 4.25)

    def test_missing_sample_rejected(self):
        with self.assertRaisesRegex(ValueError, "incomplete sample roster"):
            self.parse(source()[:5])

    def test_duplicate_sample_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate sample"):
            self.parse(source() + source()[5:])

    def test_unknown_sample_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown or duplicate sample"):
            self.parse([x.replace("GSM_SYNTHETIC", "GSM_UNKNOWN") for x in source()])

    def test_duplicate_measurement_rejected(self):
        s = source()
        s.insert(-1, "p1\t4.25\n")
        with self.assertRaisesRegex(ValueError, "duplicate sample/probe"):
            self.parse(s)

    def test_missing_probe_rejected(self):
        with self.assertRaisesRegex(ValueError, "incomplete sample/probe"):
            self.parse([x.replace("p1\t4.25", "p2\t4.25") for x in source()])

    def test_nonfinite_measurement_rejected(self):
        for token in ("nan", "inf", "-inf"):
            with self.subTest(token=token), self.assertRaisesRegex(ValueError, "nonfinite"):
                self.parse([x.replace("4.25", token) for x in source()])

    def test_changed_units_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown or changed preprocessing"):
            self.parse([x.replace("RMA log2 signal", "arbitrary units") for x in source()])

    def test_wrong_sample_platform_rejected(self):
        with self.assertRaisesRegex(ValueError, "wrong sample platform"):
            self.parse([x.replace("!Sample_platform_id = GPL6244", "!Sample_platform_id = GPL3290")
                        for x in source()])

    def test_truncated_table_rejected(self):
        with self.assertRaisesRegex(ValueError, "incomplete source tables"):
            self.parse(source()[:-1])

    def test_duplicate_platform_probe_rejected(self):
        s = source()
        s.insert(4, s[3])
        with self.assertRaisesRegex(ValueError, "duplicate or empty platform ID"):
            self.parse(s)

    def test_raw_value_text_binding(self):
        p = self.parse(source())
        p["samples"]["GSM_SYNTHETIC"]["values"]["p1"]["text"] = "p1\t99"
        with self.assertRaisesRegex(ValueError, "value text/fields disagree"):
            acquire.check_projection(p)

    def test_raw_annotation_text_binding(self):
        p = self.parse(source())
        p["CHRNA6_annotation"][0]["fields"]["gene_assignment"] = "invented // OTHER"
        with self.assertRaisesRegex(ValueError, "annotation text/fields disagree"):
            acquire.check_projection(p)

    def test_raw_metadata_text_binding(self):
        p = self.parse(source())
        p["samples"]["GSM_SYNTHETIC"]["metadata"]["processing"] = ["changed"]
        with self.assertRaisesRegex(ValueError, "metadata text/fields disagree"):
            acquire.check_projection(p)


    def test_changed_cached_value_rejected(self):
        p = self.parse(source())
        manifest = {"gene_to_probe": {"CHRNA6": "p1"}}
        with self.assertRaisesRegex(ValueError, "source/cache mismatch"):
            acquire.compare(p, manifest, {"GSM_SYNTHETIC": 9.0}, {
                "GSM_SYNTHETIC": {"title": "synthetic sample", "characteristics_ch1": [], "source_ch1": [],
                                  "source_ch2": [], "processing": ["synthetic fixture preprocessing"],
                                  "VALUE_definition": ["RMA log2 signal"]}
            })

    def test_ambiguous_source_assignment_rejected(self):
        s = [x.replace("synthetic fixture // 8973", "synthetic fixture // 8973 /// NM_other // OTHER // synthetic // 0")
             for x in source()]
        p = self.parse(s)
        with self.assertRaisesRegex(ValueError, "ambiguous gene assignment"):
            acquire.compare(p, {"gene_to_probe": {"CHRNA6": "p1"}}, {}, {})


    def test_coherent_wrong_sample_platform_rejected_offline(self):
        p = self.parse(source())
        row = p["samples"]["GSM_SYNTHETIC"]
        row["metadata"]["platform"] = ["GPL3290"]
        for line in row["metadata_lines"]:
            if line["text"].startswith("!Sample_platform_id"):
                line["text"] = "!Sample_platform_id = GPL3290"
        with self.assertRaisesRegex(ValueError, "wrong projected sample platform"):
            acquire.check_projection(p)

    def test_wrong_top_level_platform_rejected_offline(self):
        p = self.parse(source())
        p["platform"] = "GPL3290"
        with self.assertRaisesRegex(ValueError, "wrong projected platform"):
            acquire.check_projection(p)

    def test_incomplete_projected_table_rejected_offline(self):
        p = self.parse(source())
        p["samples"]["GSM_SYNTHETIC"]["table_complete"] = False
        with self.assertRaisesRegex(ValueError, "incomplete projected sample table"):
            acquire.check_projection(p)


if __name__ == "__main__":
    unittest.main()
