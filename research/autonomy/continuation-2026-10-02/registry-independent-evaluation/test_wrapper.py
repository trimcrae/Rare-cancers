"""Synthetic wrapper checks only; no scientific inputs or classifier execution."""
import unittest
from evaluate import oracle_view, prediction_view, verify_oracle_evidence
from literal_audit import pointer

class WrapperTests(unittest.TestCase):
    def test_escaped_pointer(self):
        self.assertEqual(pointer({'a/b':{'~x':[7]}}, '/a~1b/~0x/0'), 7)

    def test_literal_and_offset_fail_closed(self):
        document={'description':'abc xyz','count':{'value':'001'}}
        verify_oracle_evidence({'pointer':'/description','literal':'xyz','decodedStringStart':4,'decodedStringEndExclusive':7},document)
        verify_oracle_evidence({'pointer':'/count','value':{'value':'001'}},document)
        with self.assertRaises(ValueError):
            verify_oracle_evidence({'pointer':'/description','literal':'xyz','decodedStringStart':3,'decodedStringEndExclusive':6},document)
        with self.assertRaises(ValueError):
            verify_oracle_evidence({'pointer':'/count','value':{'value':1}},document)

    def test_missing_modifier_and_unknown(self):
        expected=oracle_view({'status':'unknown','family':None,'version':None,'modifier':None})
        predicted=prediction_view({'status':'unknown','criteriaVersion':None,'mentions':[]})
        self.assertEqual(expected,predicted)
        assigned=prediction_view({'status':'assigned','criteriaVersion':'1.1','mentions':[{'explicitAssessmentContext':True,'baseName':'RECIST','modifier':'modified'}]})
        self.assertEqual(assigned,{'status':'assigned','family':'RECIST','version':'1.1','modifier':'modified'})

if __name__=='__main__': unittest.main()
