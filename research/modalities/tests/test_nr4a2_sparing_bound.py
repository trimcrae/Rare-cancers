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
                     "Marker Type", "Feature Type", "Marker Synonyms (pipe-separated)"]) + "\n" + \
    "MGI:98139\t15\t50.0\t101\t201\t+\tNr4a1\tO\tnuclear receptor 4a1\tGene\tprotein coding gene\tNur77\n" \
    "MGI:1352456\t2\t30.0\t301\t401\t+\tNr4a2\tO\tnuclear receptor 4a2\tGene\tprotein coding gene\tNurr1\n" \
    "MGI:1352457\t4\t20.0\t501\t601\t+\tNr4a3\tO\tnuclear receptor 4a3\tGene\tprotein coding gene\tNor1\n"

VOCAB = ("MP:0011100\tcomplete preweaning lethality\tno homozygotes survive\n"
         "MP:0002082\tpostnatal lethality\tdeath after birth\n"
         "MP:0001262\tdecreased body weight\tlighter\n"
         "MP:0005559\tincreased circulating glucose level\thigher glucose\n")

ALLELES = ("MGI:1857206\tNr4a2<tm1Ddm>\ttargeted mutation 1\tTargeted\tNull/knockout\t9349815\t"
           "MGI:1352456\tNr4a2\n"
           "MGI:1857207\tNr4a1<tm1Jmi>\ttargeted mutation 1\tTargeted\tNull/knockout\t9013867\t"
           "MGI:98139\tNr4a1\n")


def _pg(comp, allele_ids, mp, pmid, marker_ids):
    """One MGI_PhenoGenoMP.rpt line in the real column order (headerless, 7 fields)."""
    return "\t".join([comp, "x", allele_ids, "involves: 129S1/Sv * C57BL/6", mp, pmid, marker_ids])


PHENOGENO = "\n".join([
    # a clean Nr4a2-only homozygous null with a lethality term and a citation
    _pg("Nr4a2<tm1Ddm>/Nr4a2<tm1Ddm>", "MGI:1857206", "MP:0011100", "9349815", "MGI:1352456"),
    _pg("Nr4a2<tm1Ddm>/Nr4a2<tm1Ddm>", "MGI:1857206", "MP:0001262", "9349815", "MGI:1352456"),
    # a clean Nr4a1-only genotype, no lethality
    _pg("Nr4a1<tm1Jmi>/Nr4a1<tm1Jmi>", "MGI:1857207", "MP:0005559", "9013867", "MGI:98139"),
    # the DOUBLE knockout -- must be classified multi_gene and counted nowhere as a single KO
    _pg("Nr4a1<tm1Jmi>/Nr4a1<tm1Jmi>,Nr4a3<tm1Jmi>/Nr4a3<tm1Jmi>", "MGI:1857207,MGI:1857208",
        "MP:0002082", "17515897", "MGI:98139,MGI:1352457"),
    # the TRAP: Nr4a2 alongside an unrelated gene and a cre transgene. Mentions Nr4a2; is not an
    # Nr4a2 single-KO phenotype.
    _pg("Nr4a2<tm1Ddm>/Nr4a2<tm1Ddm>,Pitx3<tm1Rjm>/Pitx3<tm1Rjm>", "MGI:1857206,MGI:9999999",
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
        ids, _ = m.parse_marker_list(MARKERS)
        self.rows, self.n, self.err = m.parse_phenogeno(
            PHENOGENO, {s: ids[s] for s in m.GENES_MOUSE}, m.GENES_MOUSE)

    def test_allele_ids_are_not_mistaken_for_marker_ids(self):
        """The before/after-MP split. Without it a one-gene genotype reads as two."""
        r = self.rows[0]
        self.assertEqual(r["marker_accessions_in_record"], ["MGI:1352456"])
        self.assertEqual(r["allele_accessions_in_record"], ["MGI:1857206"])
        self.assertEqual(r["classification"], "single_gene")

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
