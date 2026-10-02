"""Small synthetic tests only; no real transcriptome reads or network."""
from collections import Counter
import io
import unittest
from recover_exact_hits import (positions,parse_header,fasta_records,recover,reconcile,compare_annotations)
T="ACGTCAGGATCCTAGC"
def header(tx="ENST00000000001.2",gene="OTHER",length=16,biotype="lncRNA"):
    return f"{tx}|ENSG00000000001.7|-|-|OTHER-201|{gene}|{length}|{biotype}|"
def design(ident="d",parent=0,other=1,genes=("OTHER",)):
    return dict(design_id=ident,strata={
        "gencode_parent":dict(min_hamming=0 if parent else 1,nearest_occurrences=parent,nearest_genes=["FUS"] if parent else []),
        "gencode_other":dict(min_hamming=0 if other else 1,nearest_occurrences=other,nearest_genes=list(genes) if other else [])})
class Tests(unittest.TestCase):
    def test_overlaps_and_no_twenty_hit_cap(self):
        hs,anns,meta=recover([(header(length=40),"A"*40)],{"d":"A"*16})
        self.assertEqual(len(hs),25)
        self.assertEqual([r["start_0based"] for r in hs],list(range(25)))
        self.assertEqual(hs[-1]["end_0based_exclusive"],40)
    def test_terminal_windows(self):
        for seq,starts in ((T,[0]),("NN"+T,[2]),(T+"NN",[0]),(T+T,[0,16])):
            hs,_,_=recover([(header(length=len(seq)),seq)],{"d":T})
            self.assertEqual([r["start_0based"] for r in hs],starts)
    def test_N_windows_not_exact(self):
        for p in range(16):
            seq=T[:p]+"N"+T[p+1:]
            self.assertEqual(recover([(header(),seq)],{"d":T})[0],[])
    def test_normalization_and_final_no_newline(self):
        text=">"+header(length=18)+"\n N "+T.lower().replace("t","u")[:8]+"\n"+T.lower().replace("t","u")[8:]+" N"
        hs,_,_=recover(fasta_records(io.StringIO(text)),{"d":T})
        self.assertEqual(len(hs),1);self.assertEqual(hs[0]["start_0based"],1)
    def test_no_cross_record_window(self):
        records=[(header(length=8),T[:8]),(header(tx="ENST00000000002.1",length=8),T[8:])]
        self.assertEqual(recover(records,{"d":T})[0],[])
    def test_alias_targets_preserved(self):
        hs,anns,_=recover([(header(),T)],{"a":T,"b":T})
        self.assertEqual(Counter(r["design_id"] for r in hs),{"a":1,"b":1})
        self.assertEqual(len(anns),1)
    def test_duplicate_transcript_and_length_fail(self):
        with self.assertRaises(ValueError):
            recover([(header(),T),(header(),T)],{"d":T})
        with self.assertRaises(ValueError):
            recover([(header(length=17),T)],{"d":T})
    def test_header_schema_and_versioned_gene(self):
        a=parse_header(header())
        self.assertEqual(a["gene_id"],"ENSG00000000001.7")
        self.assertEqual(a["transcript_biotype_gencode50"],"lncRNA")
        for bad in (header().replace("ENSG00000000001.7","ENSG00000000001"),
                    header().replace("lncRNA|",""),header()+"extra|"):
            with self.assertRaises(ValueError):parse_header(bad)
    def test_reconciliation_saved_subset_and_mutated_coordinate(self):
        hs,_,_=recover([(header(length=32),T+T)],{"d":T})
        saved=[dict(hs[0])]
        extra=reconcile(hs,saved,[design(other=2)])
        self.assertEqual([r["start_0based"] for r in extra],[16])
        bad=dict(saved[0],start_0based=1)
        with self.assertRaises(ValueError):reconcile(hs,[bad],[design(other=2)])
    def test_counts_genes_fields_and_duplicates_fail(self):
        hs,_,_=recover([(header(),T)],{"d":T})
        for ds in ([design(other=2)],[design(genes=("WRONG",))]):
            with self.assertRaises(ValueError):reconcile(hs,[],ds)
        for saved in ([dict(hs[0],window_5to3="A"*16)],[dict(hs[0],gene="WRONG")],[hs[0],hs[0]]):
            with self.assertRaises(ValueError):reconcile(hs,saved,[design()])
    def test_parent_stratum_and_multidesign_transcript_count(self):
        hs,anns,_=recover([(header(gene="FUS"),T)],{"a":T,"b":T})
        reconcile(hs,[],[design("a",parent=1,other=0),design("b",parent=1,other=0)])
        self.assertEqual(len(hs),2);self.assertEqual(len(anns),1)
    def test_annotation_agreement_disagreement_missing_and_versions(self):
        a=parse_header(header());anns={a["transcript"]:a}
        b=dict(id="ENST00000000001",version=2,Parent="ENSG00000000001",
               biotype="lncRNA",length=16,display_name="OTHER-201")
        r=compare_annotations(anns,{b["id"]:b})[0]
        self.assertTrue(r["version_matches"]);self.assertTrue(r["biotype_matches"]);self.assertTrue(r["gene_stable_id_matches"])
        r=compare_annotations(anns,{b["id"]:dict(b,biotype="protein_coding")})[0]
        self.assertTrue(r["version_matches"]);self.assertFalse(r["biotype_matches"])
        r=compare_annotations(anns,{b["id"]:dict(b,version=3)})[0]
        self.assertEqual(r["comparison_status"],"version_mismatch")
        self.assertEqual(compare_annotations(anns,{})[0]["comparison_status"],"not_in_pinned_release116_snapshot")
    def test_invalid_sequence_and_empty_corpus(self):
        with self.assertRaises(ValueError):list(fasta_records(io.StringIO("ACGT\n")))
        with self.assertRaises(ValueError):recover([],{"d":T})
        with self.assertRaises(ValueError):recover([(header(),T)],{"d":"N"*16})
if __name__=="__main__":
    unittest.main()

