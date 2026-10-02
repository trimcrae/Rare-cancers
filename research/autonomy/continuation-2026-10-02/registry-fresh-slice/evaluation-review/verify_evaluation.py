"""Independent synthetic integrity checks; no companion import or execution."""
import copy, hashlib, json, socket, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).parent
TARGET=HERE.parent/'checkpoint08-registry-evaluation-prepare'
network=[]
def blocked(*args,**kwargs):
    network.append('attempt')
    raise AssertionError('Network prohibited')
socket.create_connection=blocked
socket.socket.connect=blocked
socket.socket.connect_ex=blocked
sys.path.insert(0,str(TARGET))
import evaluate_next_slice as e
from test_evaluate_next_slice import fixture, PATH

class Independent(unittest.TestCase):
    def test_pin_rejects_before_import_even_self_hashed_substitute(self):
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            base=Path(tmp); code=base/'substitute.py'
            code.write_text("raise AssertionError('must never execute')")
            entry={'path':code.name,'sha256':e.sha(code.read_bytes())}
            with patch.object(e.importlib.util,'spec_from_file_location',side_effect=AssertionError('import attempted')):
                with self.assertRaisesRegex(ValueError,'Fixed implementation'):
                    e.load_code(base,entry,'companion')
                entry['sha256']=e.PINS['companion']
                with self.assertRaisesRegex(ValueError,'hash mismatch'):
                    e.load_code(base,entry,'companion')

    def test_assemble_rejects_changed_metadata_before_any_code(self):
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            base=Path(tmp)
            protocol={'identificationModule':{'nctId':'NCT00000001'},'statusModule':{'resultsFirstPostDateStruct':{'date':'2026-09-01'}},'conditionsModule':{'conditions':['synthetic']}}
            def bound(name,value):
                raw=e.canonical(value);(base/name).write_bytes(raw)
                return {'path':name,'sha256':e.sha(raw)}
            meta=bound('meta.json',{'NCT00000001':protocol})
            selection={'status':'metadata_frame_frozen','cutoffTieComplete':True,'selectedMetadataSHA256':meta['sha256'],'selected':[{'nctId':'NCT00000001','resultsFirstPostDate':'2026-09-01','metadataSHA256':e.sha(e.canonical(protocol))}]}
            study={'protocolSection':copy.deepcopy(protocol)}
            source=bound('source.json',study);source['nctId']='NCT00000001'
            manifest={'schema':'registry-next-slice-inputs/1','frozenUTC':'synthetic','selectionReceipt':bound('selection.json',selection),'selectedMetadata':meta,'rawSources':[source],'assembledSourceSHA256':e.sha(e.canonical({'studies':[study]}))}
            self.assertEqual(e.assemble(base,manifest),{'studies':[study]})
            for mutation in ('date','null'):
                altered=copy.deepcopy(study)
                if mutation=='date':altered['protocolSection']['statusModule']['resultsFirstPostDateStruct']['date']='2026-09-02'
                else:altered['protocolSection']['conditionsModule']['extra']=None
                manifest['rawSources']=[dict(bound('changed.json',altered),nctId='NCT00000001')]
                manifest['assembledSourceSHA256']=e.sha(e.canonical({'studies':[altered]}))
                with self.assertRaisesRegex(ValueError,'metadata drift'):e.assemble(base,manifest)

    def test_mixed_eligibility_denominators_and_exclusions(self):
        doc,gold=fixture();original=gold['outcomes'][0]
        oracle={};pred=[]
        for i,eligibility in enumerate(('eligible','uncertain','excluded','eligible')):
            item=copy.deepcopy(original);item['sourcePointer']=PATH[:-1]+str(i);item['eligibility']=eligibility
            oracle[item['sourcePointer']]=item
            view=copy.deepcopy(item['family'])
            if i==3:view['status']='ambiguous'
            pred.append({'sourcePointer':item['sourcePointer'],'view':view})
        result=e.compare(oracle,pred,gold['studyInventory'])
        self.assertEqual(result['strata']['eligible']['outcomes'],2)
        self.assertEqual(result['strata']['eligible']['jointAgreements'],1)
        self.assertFalse(result['strata']['eligible']['studyAllOutcomesJointAgreement']['NCT00000001'])
        self.assertEqual(result['strata']['uncertain']['outcomes'],1)
        self.assertEqual(result['screeningCounts']['excluded'],1)
        self.assertNotIn('jointAgreement',result['comparisons'][2])

    def test_unicode_span_and_null_not_absence(self):
        doc,gold=fixture();o=doc['studies'][0]['resultsSection']['outcomeMeasuresModule']['outcomeMeasures'][0]
        o['title']='A\U0001f9ecB';o['presentNull']=None
        e.evidence({'pointer':PATH+'/title','decodedStringStart':1,'decodedStringEndExclusive':2,'literal':'\U0001f9ec'},doc,PATH)
        with self.assertRaisesRegex(ValueError,'False absence'):
            e.evidence({'pointer':PATH+'/presentNull','sourceFieldPresent':False,'value':None},doc,PATH)

    def test_fully_empty_slice_is_retained(self):
        doc,gold=fixture();doc={'studies':[]};gold.update(sourceSHA256=e.sha(e.canonical(doc)),studyInventory=[],outcomes=[])
        oracle,inventory=e.validate_oracle(gold,doc,gold['sourceSHA256'])
        result=e.compare(oracle,[],inventory)
        self.assertEqual(result['studyInventory'],[])
        self.assertEqual(result['strata']['eligible']['outcomes'],0)
        self.assertEqual(result['strata']['uncertain']['studies'],0)

suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(Independent),unittest.defaultTestLoader.discover(str(TARGET),pattern='test_evaluate_next_slice.py')])
result=unittest.TextTestRunner(verbosity=1).run(suite)
assert result.wasSuccessful() and not network
report={'testsPassed':result.testsRun,'independentTests':5,'authorTests':12,'liveNetworkAttempts':len(network),'classifierImports':0,'classifierExecutions':0,'files':{name:e.sha((TARGET/name).read_bytes()) for name in ('evaluate_next_slice.py','evaluation-schema.json','test_evaluate_next_slice.py','registry_literal_extractor.py','literal_audit.py','compare_actual_payloads.py')},'scope':'Synthetic validators and existing literal auditors only; no run() or predict() classifier workflow executed.'}
(HERE/'evaluation-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
