#!/usr/bin/env python3
"""Unit tests for the row-26 gate: MGI + HPA -> how much NR4A2 sparing is required.

★ WHAT THESE TESTS ARE FOR. Not the parsing (the parsers are exercised too), but the two ways this
gate could produce a WRONG verdict cheaply and invisibly:

  1. counting a genotype that mentions Nr4a2 alongside four other mutations as an "Nr4a2 single-KO
     phenotype" -- the exact shape of the false PROCEED `pmx_mutation_reference` returned off a
     promiscuous name match; and
  2. reporting STILL_UNBOUNDED when a source simply failed to load, which is an absent reading
     wearing a reading of absence's costume (CLAUDE.md section 4).

Both are asserted directly. No network.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nr4a2_sparing_bound as m  # noqa: E402

# --- MGI fixtures, in the real report shapes -------------------------------------------------------
MARKERS = "\t".join(["MGI Accession ID", "Chr", "cM Position", "genome coordinate start",
                     "genome coordinate end", "strand", "Marker Symbol", "Status", "Marker Name",
                     "Marker Type", "Feature Type", "Marker Synonyms (pipe-separated)"]) + "\n" + "".join([
    # a WITHDRAWN duplicate of Nr4a1 FIRST: the official Gene row below must win, not whichever
    # came first. A symbol resolving to an accession the phenotype report never uses is silent.
    "MGI:98139\t15\t50.0\t101\t201\t+\tNr4a1\tW\twithdrawn\tGene\tprotein coding gene\t\n",
    "MGI:1352454\t15\t50.0\t101\t201\t+\tNr4a1\tO\tnuclear receptor 4a1\tGene\tprotein coding gene\tNur77\n",
    "MGI:1352456\t2\t30.0\t301\t401\t+\tNr4a2\tO\tnuclear receptor 4a2\tGene\tprotein coding gene\tNurr1\n",
    "MGI:1352457\t4\t20.0\t501\t601\t+\tNr4a3\tO\tnuclear receptor 4a3\tGene\tprotein coding gene\tNor1\n",
    "MGI:97742\t19\t10.0\t701\t801\t+\tPitx3\tO\tpaired-like homeodomain 3\tGene\tprotein coding gene\t\n",
])

VOCAB = ("MP:0011100\tcomplete preweaning lethality\tno homozygotes survive\n"
         "MP:0002082\tpostnatal lethality\tdeath after birth\n"
         "MP:0001262\tdecreased body weight\tlighter\n"
         "MP:0005559\tincreased circulating glucose level\thigher glucose\n")

ALLELES = ("MGI:1857206\tNr4a2<tm1Ddm>\ttargeted mutation 1\tTargeted\tNull/knockout\t9349815\t"
           "MGI:1352456\tNr4a2\n"
           "MGI:1857207\tNr4a1<tm1Jmi>\ttargeted mutation 1\tTargeted\tNull/knockout\t9013867\t"
           "MGI:98139\tNr4a1\n")


#: ⚠ THIS IS THE REAL COLUMN LAYOUT, TAKEN FROM THE LIVE REPORT (run 30776301160), NOT FROM MEMORY.
#: There is no Allele-ID column before the MP pivot, and the TRAILING column is an MGI **GENOTYPE**
#: accession — also `MGI:`-prefixed. Parsing it as a second marker is what made all 122 real NR4A
#: records classify as `ambiguous` and made the gate publish a negative off a parse that had read
#: nothing. The fixture carries the genotype accession so that failure cannot silently return.
def _pg(comp, mp, pmid, marker_ids, genotype_id="MGI:3037447"):
    """One MGI_PhenoGenoMP.rpt line in the real column order (headerless)."""
    return "\t".join([comp, "x", "involves: 129S1/Sv * C57BL/6", mp, pmid, marker_ids, genotype_id])


PHENOGENO = "\n".join([
    # a clean Nr4a2-only homozygous null with a lethality term and a citation
    _pg("Nr4a2<tm1Ddm>/Nr4a2<tm1Ddm>", "MP:0011100", "9349815", "MGI:1352456"),
    _pg("Nr4a2<tm1Ddm>/Nr4a2<tm1Ddm>", "MP:0001262", "9349815", "MGI:1352456"),
    # a clean Nr4a1-only genotype, no lethality
    _pg("Nr4a1<tm1Jmi>/Nr4a1<tm1Jmi>", "MP:0005559", "9013867", "MGI:1352454"),
    # the DOUBLE knockout -- must be classified multi_gene and counted nowhere as a single KO
    _pg("Nr4a1<tm1Jmi>/Nr4a1<tm1Jmi>,Nr4a3<tm1Jmi>/Nr4a3<tm1Jmi>",
        "MP:0002082", "17515897", "MGI:1352454,MGI:1352457"),
    # the TRAP: Nr4a2 alongside an unrelated gene. Mentions Nr4a2; is not an Nr4a2 single-KO.
    _pg("Nr4a2<tm1Ddm>/Nr4a2<tm1Ddm>,Pitx3<tm1Rjm>/Pitx3<tm1Rjm>",
        "MP:0011100", "12345678", "MGI:1352456,MGI:97742"),
]) + "\n"

TEXTS = {"markers": MARKERS, "mp_vocab": VOCAB, "alleles": ALLELES, "phenogeno": PHENOGENO}

HPA = "Gene\tGene name\tTissue\tnTPM\n" + "\n".join([
    "ENSG00000123358\tNR4A1\tliver\t12.0",
    "ENSG00000153234\tNR4A2\tliver\t0.2",
    "ENSG00000119508\tNR4A3\tliver\t4.0",
    "ENSG00000123358\tNR4A1\tmidbrain\t0.3",
    "ENSG00000153234\tNR4A2\tmidbrain\t44.0",
    "ENSG00000119508\tNR4A3\tmidbrain\t0.1",
    "ENSG00000123358\tNR4A1\tadipose tissue\t30.0",
    "ENSG00000153234\tNR4A2\tadipose tissue\t6.0",
    "ENSG00000119508\tNR4A3\tadipose tissue\t9.0",
]) + "\n"


class TestCompositionParse(unittest.TestCase):
    def test_single_gene_homozygote(self):
        self.assertEqual(m.genes_in_composition("Nr4a2<tm1Ddm>/Nr4a2<tm1Ddm>"), ["Nr4a2"])

    def test_double_knockout_is_two_genes(self):
        self.assertEqual(
            m.genes_in_composition("Nr4a1<tm1Jmi>/Nr4a1<tm1Jmi>,Nr4a3<tm1Jmi>/Nr4a3<tm1Jmi>"),
            ["Nr4a1", "Nr4a3"])

    def test_transgene_is_not_invisible(self):
        got = m.genes_in_composition("Nr4a2<tm1Ddm>/Nr4a2<tm1Ddm>,Tg(Th-cre)1Tmd<Tg/0>")
        self.assertIn("Nr4a2", got)
        self.assertEqual(len(got), 2, "a cre transgene must make the genotype multi-locus, not "
                                      "silently disappear: %s" % got)


class TestPhenoGenoClassification(unittest.TestCase):
    def setUp(self):
        ids, self.acc2sym, _ = m.parse_marker_list(MARKERS)
        self.rows, self.n, self.err = m.parse_phenogeno(
            PHENOGENO, {s: ids[s] for s in m.GENES_MOUSE}, m.GENES_MOUSE, acc2sym=self.acc2sym)

    def test_a_trailing_genotype_accession_is_not_a_second_marker(self):
        """⛔ THE MEASURED REGRESSION (run 30776301160). The report's last column is an MGI GENOTYPE
        accession, also `MGI:`-prefixed. Counting it as a marker made every one of the 122 real NR4A
        records `ambiguous`, and the gate then published a negative off a parse that read nothing."""
        r = self.rows[0]
        self.assertEqual(r["marker_accessions_in_record"], ["MGI:1352456"])
        self.assertEqual(r["non_marker_mgi_ids_in_record"], ["MGI:3037447"])
        self.assertEqual(r["genes_named_by_the_marker_column"], ["Nr4a2"])
        self.assertEqual(r["classification"], "single_gene")

    def test_official_gene_row_wins_over_a_withdrawn_duplicate_symbol(self):
        ids, _acc2sym, _err = m.parse_marker_list(MARKERS)
        self.assertEqual(ids["Nr4a1"], "MGI:1352454")

    def test_double_knockout_is_not_a_single_ko(self):
        dko = [r for r in self.rows if r["genes_parsed_from_composition"] == ["Nr4a1", "Nr4a3"]]
        self.assertTrue(dko)
        self.assertEqual(dko[0]["classification"], "multi_gene")

    def test_compound_genotype_mentioning_nr4a2_is_not_counted_as_a_single_ko(self):
        """⛔ THE FALSE-PROCEED SHAPE. A row that MENTIONS Nr4a2 is not an Nr4a2 single-KO record."""
        trap = [r for r in self.rows if "Pitx3" in r["allelic_composition"]]
        self.assertTrue(trap, "fixture missing the compound genotype")
        self.assertNotEqual(trap[0]["classification"], "single_gene")


class TestGate(unittest.TestCase):
    def _doc(self, texts=None, hpa=HPA):
        return m.run(out_path=None, mgi_texts=texts if texts is not None else TEXTS, hpa_text=hpa)

    def test_bounded_when_a_cited_lethality_term_exists(self):
        doc = self._doc()
        self.assertEqual(doc["verdict"]["decision"], "BOUNDED")
        b2 = doc["verdict"]["gates"]["B2_lethality_claim_resolved_to_a_citation"]
        self.assertTrue(b2["met"])
        self.assertEqual(b2["survival_or_viability_terms_found"][0]["pubmed_ids"], ["9349815"])

    def test_nr4a2_single_ko_count_excludes_the_compound_genotype(self):
        doc = self._doc()
        n2 = doc["mgi"]["single_gene"]["Nr4a2"]
        self.assertEqual(n2["n_single_gene_annotations"], 2,
                         "the Pitx3 compound genotype must not be counted")

    def test_partially_bounded_when_phenotyped_but_no_lethality_term(self):
        pg = "\n".join(l for l in PHENOGENO.splitlines() if "MP:0011100" not in l) + "\n"
        doc = self._doc(dict(TEXTS, phenogeno=pg))
        self.assertEqual(doc["verdict"]["decision"], "PARTIALLY_BOUNDED")

    def test_still_unbounded_when_no_nr4a2_only_record_exists(self):
        pg = "\n".join(l for l in PHENOGENO.splitlines() if "Nr4a2" not in l) + "\n"
        doc = self._doc(dict(TEXTS, phenogeno=pg))
        self.assertEqual(doc["verdict"]["decision"], "STILL_UNBOUNDED")

    def test_an_all_ambiguous_parse_is_a_LOAD_FAILURE_not_an_absence(self):
        """⛔ THE GUARD THE MEASURED BUG NEEDED. A classifier that rejects 100% of its input has not
        measured an absence; it has failed to read. Simulated by withholding the marker report, so
        the curated cross-check can never agree."""
        # every record's curated marker column names a DIFFERENT gene than its composition, so
        # nothing can be classified — the live shape of the measured bug.
        bad = "\n".join(_pg("Nr4a2<tm1Ddm>/Nr4a2<tm1Ddm>", mp, "1", "MGI:97742")
                         for mp in ("MP:0011100", "MP:0001262")) + "\n"
        doc = self._doc(dict(TEXTS, phenogeno=bad))
        self.assertEqual(doc["mgi"]["n_records_touching_nr4a"], 2)
        self.assertEqual(doc["mgi"]["n_classified_records"], 0)
        self.assertFalse(doc["mgi"]["loaded"])
        self.assertEqual(doc["verdict"]["decision"], "UNDETERMINED")
        self.assertTrue(any("PARSE FAILURE" in e for e in doc["mgi"]["errors"]),
                        doc["mgi"]["errors"])

    def test_unresolved_markers_are_a_load_failure_too(self):
        doc = self._doc(dict(TEXTS, markers=MARKERS.splitlines()[0] + "\n"))
        self.assertEqual(doc["verdict"]["decision"], "UNDETERMINED")

    def test_load_failure_is_UNDETERMINED_not_a_negative(self):
        """⛔ An absent reading is not a reading of absence."""
        doc = self._doc(dict(TEXTS, phenogeno=""))
        self.assertEqual(doc["verdict"]["decision"], "UNDETERMINED")
        doc2 = self._doc(hpa="")
        self.assertEqual(doc2["verdict"]["decision"], "UNDETERMINED")

    def test_offline_never_emits_a_scientific_verdict(self):
        doc = m.run(out_path=None, offline=True)
        self.assertEqual(doc["verdict"]["decision"], "UNDETERMINED")

    def test_caveat_travels_and_names_the_developmental_limit(self):
        doc = self._doc()
        c = doc["verdict"]["caveat_that_must_travel_with_any_result"]
        self.assertIn("DEVELOPMENTAL", c)
        self.assertIn("TRANSIENT", c)


class TestOverlap(unittest.TestCase):
    def test_overlap_counts_are_derived_from_the_table(self):
        per, err = m.parse_hpa_tsv(HPA)
        self.assertEqual(err, [])
        ov = m.hpa_overlap(per)
        self.assertEqual(ov["n_tissues_with_all_three_measured"], 3)
        c = ov["counts"]
        # midbrain: NR4A2 44.0 with both paralogues below 1.0 -> unbuffered and dominant
        self.assertEqual(ov["nr4a2_unbuffered_tissues"], ["midbrain"])
        self.assertEqual(c["nr4a2_dominant"], 1)
        # adipose tissue is the only place NR4A2 and NR4A3 are both above the cut
        self.assertEqual(c["nr4a2_and_nr4a3_co_expressed"], 1)


class TestMapEdits(unittest.TestCase):
    def test_every_edit_carries_the_fields_the_coordinator_asked_for(self):
        doc = m.run(out_path=None, mgi_texts=TEXTS, hpa_text=HPA)
        edits = doc["map_edits_required"]
        self.assertTrue(edits)
        for e in edits:
            for k in ("section", "anchor", "current_text", "proposed_text", "why", "artifact"):
                self.assertIn(k, e)
            self.assertTrue(e["artifact"].startswith("research/modalities/"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
