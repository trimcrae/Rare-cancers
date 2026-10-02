"""Synthetic integrity/normalization tests; no classifier execution or real sources."""
import copy
import unittest
import evaluate_next_slice as e
import registry_literal_extractor as extractor
import literal_audit
import compare_actual_payloads

PATH = '/studies/0/resultsSection/outcomeMeasuresModule/outcomeMeasures/0'

def fixture():
    outcome = {'title':'Synthetic tumor response', 'description':'Synthetic criteria', 'classes':[], 'numeric':1}
    doc = {'studies':[{'protocolSection':{'identificationModule':{'nctId':'NCT00000001'}}, 'resultsSection':{'outcomeMeasuresModule':{'outcomeMeasures':[outcome]}}}]}
    inventory = [{'studyIndex':0,'nctId':'NCT00000001','outcomeCount':1,'resultsSectionPresent':True,'outcomeModulePresent':True,'outcomeArrayPresent':True}]
    family = {'status':'unknown','family':None,'version':None,'modifier':None}
    item = {'sourcePointer':PATH,'studyIndex':0,'nctId':'NCT00000001','outcomeIndex':0,'outcomeSHA256':e.sha(e.canonical(outcome)),'eligibility':'uncertain','reason':'Synthetic uncertainty','evidence':[{'pointer':PATH+'/title','literal':outcome['title']}], 'literalRoles':[], 'confirmationContext':None,'scopeDenominatorReferences':[],'absentEvidence':[], 'family':family}
    gold = {'schema':'registry-next-slice-oracle/1','sourceSHA256':e.sha(e.canonical(doc)),'frozenUTC':'synthetic','reviewer':dict(identity='synthetic',model='synthetic',effort='synthetic',prompt='synthetic',accessExposureAttestation='synthetic only',blindToClassifierAndPredictions=True),'studyInventory':inventory,'outcomes':[item]}
    return doc, gold

class IntegrityTests(unittest.TestCase):
    def validate(self,doc,gold): return e.validate_oracle(gold,doc,e.sha(e.canonical(doc)))

    def test_complete_synthetic_uncertain_case(self):
        doc,gold=fixture()
        oracle,inventory=self.validate(doc,gold)
        result=e.compare(oracle,[{'sourcePointer':PATH,'view':gold['outcomes'][0]['family']}],inventory)
        self.assertEqual(1,result['strata']['uncertain']['outcomes'])
        self.assertEqual(0,result['strata']['eligible']['outcomes'])
        self.assertTrue(result['strata']['uncertain']['studyAllOutcomesJointAgreement']['NCT00000001'])

    def test_missing_and_duplicate_outcomes_fail(self):
        for outcomes in ([],2):
            doc,gold=fixture()
            gold['outcomes']=[] if outcomes==[] else gold['outcomes']*2
            with self.assertRaises(ValueError): self.validate(doc,gold)

    def test_scalar_type_drift_is_not_python_numeric_equality(self):
        doc,gold=fixture()
        gold['outcomes'][0]['evidence']=[{'pointer':PATH+'/numeric','value':True}]
        with self.assertRaisesRegex(ValueError,'value/type'): self.validate(doc,gold)

    def test_negative_and_incomplete_spans_rejected(self):
        for span in ({'decodedStringStart':-1,'decodedStringEndExclusive':2},{'decodedStringStart':0}):
            doc,gold=fixture()
            gold['outcomes'][0]['evidence'][0].update(span)
            with self.assertRaises(ValueError): self.validate(doc,gold)

    def test_false_absence_rejected(self):
        doc,gold=fixture()
        gold['outcomes'][0]['absentEvidence']=[{'pointer':PATH+'/title','sourceFieldPresent':False,'value':None}]
        with self.assertRaisesRegex(ValueError,'absence'): self.validate(doc,gold)

    def test_evidence_cannot_bind_other_outcome(self):
        doc,gold=fixture()
        gold['outcomes'][0]['evidence'][0]['pointer']='/studies/0/protocolSection/identificationModule/nctId'
        with self.assertRaisesRegex(ValueError,'boundary'): self.validate(doc,gold)

    def test_outcome_digest_drift_rejected(self):
        doc,gold=fixture()
        doc['studies'][0]['resultsSection']['outcomeMeasuresModule']['outcomeMeasures'][0]['classes']=[{}]
        gold['sourceSHA256']=e.sha(e.canonical(doc))
        with self.assertRaisesRegex(ValueError,'outcome hash'): self.validate(doc,gold)

    def test_only_null_empty_normalize(self):
        a={'status':'unknown','family':None,'version':'','modifier':None}
        b=dict(a,version=None)
        self.assertEqual(e.family_view(a),e.family_view(b))
        self.assertNotEqual(e.family_view(a),e.family_view(dict(a,version=' ')))
        with self.assertRaises(ValueError): e.family_view(dict(a,version=False))
        del a['version']
        with self.assertRaises(ValueError): e.family_view(a)

    def test_empty_study_inventory_preserves_absence(self):
        doc,gold=fixture()
        del doc['studies'][0]['resultsSection']
        gold.update(sourceSHA256=e.sha(e.canonical(doc)),outcomes=[],studyInventory=[{'studyIndex':0,'nctId':'NCT00000001','outcomeCount':0,'resultsSectionPresent':False,'outcomeModulePresent':False,'outcomeArrayPresent':False}])
        self.validate(doc,gold)
        gold['studyInventory'][0]['outcomeArrayPresent']=True
        with self.assertRaisesRegex(ValueError,'inventory'): self.validate(doc,gold)

    def test_prediction_coverage_and_disagreement(self):
        doc,gold=fixture(); oracle,inventory=self.validate(doc,gold)
        with self.assertRaisesRegex(ValueError,'coverage'):e.compare(oracle,[],inventory)
        differing=dict(gold['outcomes'][0]['family'],status='ambiguous')
        result=e.compare(oracle,[{'sourcePointer':PATH,'view':differing}],inventory)
        self.assertEqual(0,result['strata']['uncertain']['jointAgreements'])

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(ValueError):e.parse(b'{"a":1,"a":2}')

    def test_reused_literal_audits_catch_measurement_and_denominator_mutation(self):
        doc,gold=fixture()
        outcome=doc['studies'][0]['resultsSection']['outcomeMeasuresModule']['outcomeMeasures'][0]
        outcome.update(groups=[{'id':'G1'}],denoms=[{'units':'Participants','counts':[{'groupId':'G1','value':'2'}]}],classes=[{'title':'Synthetic','categories':[{'title':'Synthetic category','measurements':[{'groupId':'G1','value':'1'}]},{'title':'Empty','measurements':[]}]}])
        raw=e.canonical(doc)
        source,receipt=extractor.load_verified(raw,e.sha(raw),{'kind':'synthetic'})
        literals=extractor.extract(source,receipt)
        literal_audit.audit(doc,literals)
        for mutate in ('measurement','denominator'):
            broken=copy.deepcopy(literals)
            if mutate=='measurement': broken['rows'][0]['measurements'][0]['measurementLiteral']['value']='999'
            else:broken['rows'][0]['denominators']['outcomeEntries'][0]['countLiteral']['value']='999'
            with self.assertRaises(ValueError):literal_audit.audit(doc,broken)
        row=literals['rows'][0]
        carried={'unit':[row['outcomeKey'][2],row['outcomeKey'][4],row['classIndex'],row['groupId']], 'acceptedRowUnchanged':copy.deepcopy(row),'acceptedRowSHA256':e.sha(e.canonical(row))}
        self.assertEqual(1,compare_actual_payloads.verify(doc,literals,[carried])['companionRows'])
        carried['acceptedRowUnchanged']['classLiteral']['title']='Changed'
        with self.assertRaises(ValueError):compare_actual_payloads.verify(doc,literals,[carried])

if __name__=='__main__':unittest.main()
