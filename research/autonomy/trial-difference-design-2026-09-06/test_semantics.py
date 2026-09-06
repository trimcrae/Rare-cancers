"""Synthetic scientific identities and failure cases; never opens empirical labels."""
import itertools
import random
import unittest
import build_packet as b


class DifferenceSemantics(unittest.TestCase):
    def test_exhaustive_common_cancellation(self):
        h={'c1','c2','d1','d2'}; a={'c1','c2','e1','e2'}; ids=sorted(h|a)
        for bits in itertools.product([0,1],repeat=len(ids)):
            labels=dict(zip(ids,bits))
            direct=sum(labels[n] for n in a)-sum(labels[n] for n in h)
            self.assertEqual(b.yield_difference(h,a,labels),direct)
            self.assertEqual(b.yield_difference(a,h,labels),-direct)

    def test_actual_set_sizes_arbitrary_common_labels(self):
        common={f'common{i}' for i in range(83)}
        h=common|{f'd{i}' for i in range(17)}; a=common|{f'e{i}' for i in range(17)}
        rng=random.Random(917)
        exclusive={n:rng.randrange(2) for n in h^a}
        expected=b.yield_difference(h,a,exclusive)
        for pattern in [dict.fromkeys(common,0),dict.fromkeys(common,1)]+[
            {n:rng.randrange(2) for n in sorted(common)} for _ in range(25)]:
            labels={**exclusive,**pattern}
            self.assertEqual(sum(labels[n] for n in a)-sum(labels[n] for n in h),expected)

    def test_all_uncertainty_assignments_are_conservative_and_sharp_without_dependencies(self):
        h={'common','loss1','loss2'}; a={'common','gain1','gain2'}; ids=sorted(h|a)
        for intervals in itertools.product([(0,0),(0,1),(1,1)],repeat=len(ids)):
            bounds=dict(zip(ids,intervals)); outcomes=[]
            choices=[range(lo,hi+1) for lo,hi in intervals]
            for bits in itertools.product(*choices):
                labels=dict(zip(ids,bits))
                outcomes.append(sum(labels[n] for n in a)-sum(labels[n] for n in h))
            self.assertEqual(b.difference_bounds(h,a,bounds),(min(outcomes),max(outcomes)))

    def test_unknown_common_is_one_shared_quantity(self):
        h={'common','loss'}; a={'common','gain'}
        bounds={'common':(0,1),'loss':(0,0),'gain':(1,1)}
        self.assertEqual(b.difference_bounds(h,a,bounds),(1,1))
        # Naively subtracting separate top-set intervals would give [0,2].
        self.assertNotEqual(b.difference_bounds(h,a,bounds),(0,2))

    def test_uncertainty_does_not_become_negative(self):
        h={'loss'}; a={'gain'}
        self.assertEqual(b.difference_bounds(h,a,{'gain':(0,1),'loss':(1,1)}),(-1,0))
        self.assertEqual(b.difference_bounds(h,a,{'gain':(1,1),'loss':(0,1)}),(0,1))
        self.assertEqual(b.difference_bounds(h,a,{'gain':(0,1),'loss':(0,1)}),(-1,1))
        with self.assertRaises(ValueError):
            b.difference_bounds(h,a,{'gain':(1,0),'loss':(0,0)})
        with self.assertRaises(ValueError):
            b.difference_bounds(h,a,{'gain':(1,1)})

    def test_inconsistent_common_labels_break_cancellation(self):
        h={'common','loss'}; a={'common','gain'}
        hierarchy={'common':0,'loss':0}; augmented={'common':1,'gain':0}
        direct=sum(augmented.values())-sum(hierarchy.values())
        exclusive=b.yield_difference(h,a,{'gain':0,'loss':0})
        self.assertEqual(direct,1); self.assertEqual(exclusive,0)

    def test_scope_orthogonal_to_purpose_and_status(self):
        # Same disease-scope judgment; these are synthetic metadata, not eligibility claims.
        cases=[{'scope':1,'purpose':purpose,'status':status} for purpose in ['TREATMENT','DIAGNOSTIC']
               for status in ['RECRUITING','COMPLETED','UNKNOWN']]
        for case in cases:
            self.assertEqual(b.yield_difference({'loss'},{'gain'}, {'gain':case['scope'],'loss':0}),1)

    def test_raw_unicode_object_slices_preserve_original_bytes(self):
        raw=' {"x": 2, "studies" : [ { "n" : "caf\u00e9", "nested":{"a":[1,2]} },\n{"n":"two"} ], "next":null }'.encode()
        got=list(b.study_slices(raw)); self.assertEqual(len(got),2)
        _,obj,text,start,end=got[0]
        part=text[start:end].encode(); self.assertIn(part,raw)
        self.assertEqual(part,b'{ "n" : "caf\xc3\xa9", "nested":{"a":[1,2]} }')
        self.assertNotEqual(part,b.canonical(obj))

    def test_version_precedence_and_missing_timestamp_stop(self):
        def candidate(date,retrieved,path,value):
            return ({'protocolSection':{'statusModule':{'lastUpdatePostDateStruct':{'date':date}}},'v':value},
                    {'retrieved_at_utc':retrieved,'file':path})
        older=candidate('2025-01-01','2026-09-06T02:00:00+00:00','a',1)
        newer=candidate('2025-02-01','2026-09-05T02:00:00+00:00','z',2)
        self.assertEqual(b.select_version([older,newer]),newer)
        later=candidate('2025-02-01','2026-09-05T03:00:00+00:00','z',3)
        self.assertEqual(b.select_version([later,newer]),later)
        pathfirst=candidate('2025-02-01','2026-09-05T03:00:00+00:00','a',4)
        self.assertEqual(b.select_version([later,pathfirst]),pathfirst)
        other=candidate('2025-02-01','2026-09-05T03:00:00+00:00','a',5)
        self.assertEqual(b.select_version([other,pathfirst]),min([other,pathfirst],key=lambda c:b.sha(b.canonical(c[0]))))
        with self.assertRaises((ValueError,TypeError)):
            b.select_version([candidate('','2026-09-05T03:00:00+00:00','a',0)])


if __name__ == '__main__':
    unittest.main(verbosity=2)
