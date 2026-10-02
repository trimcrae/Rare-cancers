"""Synthetic negative controls for actual-payload validation."""
import copy, hashlib, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"registry"))
from registry_literal_extractor import extract
from compare_actual_payloads import verify, canonical

class ActualPayloadTests(unittest.TestCase):
    def fixture(self):
        o={"title":"Synthetic count","groups":[{"id":"A"},{"id":"B"}],
           "classes":[{"title":"Synthetic class","denoms":[{"units":"Participants","counts":[{"groupId":"A","value":"5"},{"groupId":"B","value":"0"}]}],
             "categories":[{"title":"CR","measurements":[{"groupId":"A","value":"2","comment":"literal qualifier"}]}]}]}
        source={"studies":[{"protocolSection":{"identificationModule":{"nctId":"SYNTHETIC"}},"resultsSection":{"outcomeMeasuresModule":{"outcomeMeasures":[o]}}}]}
        e=extract(source,{"kind":"synthetic","sha256":"0"*64})
        companions=[]
        for row in e["rows"]:
            companions.append({"unit":[row["outcomeKey"][2],row["outcomeKey"][4],row["classIndex"],row["groupId"]],
                               "acceptedRowUnchanged":copy.deepcopy(row),"acceptedRowSHA256":hashlib.sha256(canonical(row)).hexdigest()})
        return source,e,companions
    def test_full_payload_and_empty_group(self):
        result=verify(*self.fixture())
        self.assertEqual((result["literalRows"],result["sourceMeasurements"]),(2,1))
    def test_lost_empty_group_fails(self):
        s,e,c=self.fixture();e["rows"]=e["rows"][:1]
        with self.assertRaises(ValueError):verify(s,e,c)
    def test_changed_measurement_qualifier_fails(self):
        s,e,c=self.fixture();e["rows"][0]["measurements"][0]["measurementLiteral"]["comment"]="different"
        with self.assertRaises(ValueError):verify(s,e,c)
    def test_changed_denominator_fails(self):
        s,e,c=self.fixture();e["rows"][0]["denominators"]["classEntries"][0]["countLiteral"]["value"]="99"
        with self.assertRaises(ValueError):verify(s,e,c)
    def test_companion_accepted_payload_mutation_fails(self):
        s,e,c=self.fixture();c[0]["acceptedRowUnchanged"]["normalizationStatus"]="invented"
        with self.assertRaises(ValueError):verify(s,e,c)
if __name__=="__main__":unittest.main()
