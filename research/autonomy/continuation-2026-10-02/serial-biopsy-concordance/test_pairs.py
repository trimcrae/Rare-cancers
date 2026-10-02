import unittest
from analyze_pairs import analyze, number, ranks, spearman, sign
from decimal import Decimal

class Checks(unittest.TestCase):
    def fixture(self):
        rows=[];cells=[]
        for p,rv,iv in [('A',[0,2],[1,3]),('B',[3,1],[4,1]),('C',[1,1],[0,2])]:
            for tp,r,i in zip(['Baseline','On-Treatment'],rv,iv):
                sid=p+';'+tp
                rows.append(dict(PatientID=p,Subject=p,SampleID=sid,SampleTimepoint=tp,Cohort='H',**{'T-cell (CD8)':str(r)}))
                cells.append(dict(sampleKey=sid,subject=p,timepoint=tp,cohort='H',field='CD8',distinctNumericValues=[i]))
        return rows,cells
    def test_zero_missing(self):
        self.assertEqual(number('0'),0)
        for v in ['NA','NaN','Infinity','']: self.assertIsNone(number(v))
    def test_midranks(self):
        self.assertEqual(ranks([3,1,1]),[3,1.5,1.5])
        self.assertAlmostEqual(spearman([1,1,3],[3,3,1]),-1)
        self.assertIsNone(spearman([1,1],[1,2]))
    def test_directions(self):
        out=analyze(*self.fixture())
        self.assertEqual((out['shared_pairs'],out['same_nonzero_direction'],out['nonzero_pairs']),(3,2,2))
        self.assertEqual(out['direction_table_rna_then_ihc']['zero/positive'],1)
        self.assertEqual(sign(Decimal('.3')-Decimal('.30')),'zero')
    def test_duplicates(self):
        rows,cells=self.fixture()
        with self.assertRaisesRegex(AssertionError,'Duplicate'): analyze(rows+rows[:1],cells)
    def test_identity(self):
        rows,cells=self.fixture();cells[0]['subject']='OTHER'
        with self.assertRaisesRegex(AssertionError,'identity'): analyze(rows,cells)
    def test_conflict(self):
        rows,cells=self.fixture();cells[0]['distinctNumericValues']=[1,2]
        with self.assertRaisesRegex(AssertionError,'Conflicting'): analyze(rows,cells)
    def test_missing_independent(self):
        rows,cells=self.fixture();rows[0]['T-cell (CD8)']='NA';cells[2]['distinctNumericValues']=[]
        out=analyze(rows,cells)
        self.assertEqual(out['shared_pairs'],1)
        self.assertEqual(out['missingness_patterns'],{'rna_baseline':1,'ihc_baseline':1,'complete':1})

if __name__=='__main__': unittest.main()
