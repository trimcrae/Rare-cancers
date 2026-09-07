"""Behavioral checks for selection, source extraction, ties, bounds and frozen packet."""
import copy,itertools,json,unittest
from pathlib import Path
import build_packet as b

class Semantics(unittest.TestCase):
    def test_byte_slices_unicode_and_nested_studies_key(self):
        raw='{"note":{"studies":[0]},"studies":[{"name":"é😀"},{"name":"two"}]}'.encode()
        pieces=list(b.study_slices(raw))
        self.assertEqual([x[1]['name'] for x in pieces],['é😀','two'])
        for _,obj,text,start,end in pieces:
            offset=len(text[:start].encode()); data=raw[offset:offset+len(text[start:end].encode())]
            self.assertEqual(json.loads(data),obj)
    def test_rank_tie_corruption_rejected(self):
        rows=[{'nct_id':n,'methods':{'O':{'score':1,'rank':i,'rank_min':1,'rank_max':2,'midrank':1.5}}} for i,n in enumerate(['a','b'],1)]
        self.assertEqual(b.check_ranks(rows,'O')[0]['nct_id'],'a')
        rows[0]['methods']['O']['rank_max']=1
        with self.assertRaises(ValueError):b.check_ranks(rows,'O')
    def test_version_date_then_retrieval_then_path(self):
        def c(date,time,path):return ({'protocolSection':{'statusModule':{'lastUpdatePostDateStruct':{'date':date}}}},{'retrieved_at_utc':time,'file':path},b'',{})
        old=c('2026-01-01','2026-03-01T00:00:00Z','a')
        new=c('2026-02-01','2026-02-01T00:00:00Z','b')
        self.assertIs(b.select_version([old,new]),new)
        later=c('2026-02-01','2026-02-02T00:00:00Z','c')
        tie=c('2026-02-01','2026-02-02T00:00:00Z','a')
        self.assertIs(b.select_version([new,later,tie]),tie)
    def test_signed_bounds_exhaustive(self):
        h={'d','common'};a={'e','common'}
        for e,d in itertools.product([(0,0),(0,1),(1,1)],repeat=2):
            bounds={'e':e,'d':d};lo,hi=b.difference_bounds(h,a,bounds)
            vals=[x-y for x in range(e[0],e[1]+1) for y in range(d[0],d[1]+1)]
            self.assertEqual((lo,hi),(min(vals),max(vals)))
        with self.assertRaises(ValueError):b.difference_bounds(h,a,{'e':(0,1)})
    def test_packet_complete_and_masked(self):
        m=json.loads((b.HERE/'reader/manifest.json').read_bytes())
        self.assertEqual(m['count'],8);self.assertEqual(len({r['nct_id'] for r in m['records']}),8)
        for r in m['records']:
            raw=(b.HERE/'reader'/r['file']).read_bytes();s=json.loads(raw)
            self.assertEqual(b.sha(raw),r['raw_sha256']);self.assertEqual(len(raw),r['bytes'])
            self.assertEqual(s['protocolSection']['identificationModule']['nctId'],r['nct_id'])
            self.assertEqual(s['protocolSection']['statusModule']['overallStatus'],'RECRUITING')
            self.assertEqual(s['protocolSection']['designModule']['designInfo']['primaryPurpose'],'TREATMENT')
            self.assertFalse(set(r)&{'group','rank','score','query','H','A','O'})
        self.assertFalse(set(m)&{'group','rank','score','query','H','A','O','shuffle'})
        self.assertEqual(m['protocol_sha256'],b.sha((b.HERE/'reader/protocol.md').read_bytes()))
        self.assertEqual(m['disease_anchors_sha256'],b.sha((b.HERE/'reader/disease-anchors.md').read_bytes()))
    def test_filter_positive_order_from_archived_scores(self):
        import zipfile
        with zipfile.ZipFile(b.PACKAGE/'frozen-experiment.zip') as z: rows=json.loads(z.read(b.F+'rankings-EMC.json'))
        rows=[r for r in rows if r['status']=='RECRUITING' and r['primary_purpose']=='TREATMENT']
        self.assertEqual(len(rows),737)
        tops={m:{r['nct_id'] for r in sorted((r for r in rows if r['methods'][m]['score']>0),key=lambda r:(-r['methods'][m]['score'],r['nct_id']))[:100]} for m in ['O','H','A']}
        self.assertEqual([len(tops[m]) for m in ['O','H','A']],[77,100,100])
        self.assertEqual(len(tops['H']&tops['A']),96)
        packet=json.loads((b.HERE/'coordinator/packet-manifest.json').read_bytes())
        self.assertEqual({r['nct_id'] for r in packet['membership_and_provenance']},tops['H']^tops['A'])
        for m in ['H','A']:self.assertFalse(packet['tie_boundaries'][m]['crosses_cutoff'])

if __name__=='__main__':unittest.main(verbosity=2)
