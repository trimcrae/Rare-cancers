from pathlib import Path
from decimal import Decimal
import json, math, sys, hashlib

root=Path('C:/Projects/EMC-Research')
worker=Path(sys.argv[1])
expected=json.loads((root/'.cache/research-cycle/independent_expected.json').read_text())
actual=json.loads((worker/'research/modalities/surface-address-sensitivity.json').read_text())
parent=json.loads((root/'research/modalities/emc-expression-panels.json').read_text())
assert actual['provenance']['parent_sha256']==expected['parent_sha256']
assert set(actual['addresses'])==set(expected['results'])
checked=0
missing_no_effect=0
for gene,matrices in expected['results'].items():
    for matrix,exp in matrices.items():
        row=actual['platforms'][matrix]['addresses'][gene]
        assert row['readable']==exp['readable'],(gene,matrix,'readability')
        if not exp['readable']:
            assert row['status']=='unreadable'
            assert row['baseline']['delta'] is None
            for mode in ('leave_one_EMC_out','leave_one_comparator_histology_out'):
                assert all(not r['eligible'] and r['delta'] is None for r in row[mode]['rows'])
            continue
        assert math.isclose(row['baseline']['delta'],float(exp['baseline']),rel_tol=0,abs_tol=1e-12)
        assert row['baseline']['counts']['EMC']['available_n']==exp['n_EMC']
        assert row['baseline']['counts']['comparator']['available_n']==exp['n_comparator']
        assert row['parent_baseline_comparison']['status']=='match'
        assert round(Decimal(exp['baseline']),4)==Decimal(exp['parent_delta'])
        for mode,key,flipkey in [('leave_one_EMC_out','EMC_deletions','EMC_flips'),('leave_one_comparator_histology_out','histology_deletions','histology_flips')]:
            deletion={r['deleted_id']:r for r in row[mode]['rows']}
            expected_rows=dict(exp[key])
            if mode=='leave_one_EMC_out':
                for sample in parent['gene_reads'][gene][matrix]['per_sample']:
                    if sample['class']=='EMC' and sample.get('z_vs_array') is None:
                        expected_rows[sample['gsm']]=exp['baseline']; missing_no_effect+=1
            assert set(deletion)==set(expected_rows),(gene,matrix,mode,'coverage')
            for identity,value in expected_rows.items():
                got=deletion[identity]
                assert got['eligible']
                assert math.isclose(got['delta'],float(value),rel_tol=0,abs_tol=1e-12),(gene,matrix,mode,identity)
                checked+=1
            summary=row[mode]['summary']
            assert set(summary['sign_flip_ids'])==set(exp[flipkey])
            assert set(summary['sign_change_ids'])==set(exp[flipkey])
            assert math.isclose(summary['min_delta'],min(float(x) for x in expected_rows.values()),abs_tol=1e-12)
            assert math.isclose(summary['max_delta'],max(float(x) for x in expected_rows.values()),abs_tol=1e-12)
        unstable=bool(exp['EMC_flips'] or exp['histology_flips'])
        expected_status='unstable' if unstable else 'stable_positive' if Decimal(exp['baseline'])>0 else 'stable_negative'
        assert row['status']==expected_status
print(json.dumps({'status':'passed','readable_baselines_checked':19,'unreadable_combinations_checked':3,'eligible_deletion_rows_checked':checked,'missing_EMC_deletion_with_no_numerical_effect':missing_no_effect,'arithmetic_tolerance':1e-12,'method':'Independent Decimal expected values; does not import worker implementation','json_sha256':hashlib.sha256((worker/'research/modalities/surface-address-sensitivity.json').read_bytes()).hexdigest()},indent=2))
