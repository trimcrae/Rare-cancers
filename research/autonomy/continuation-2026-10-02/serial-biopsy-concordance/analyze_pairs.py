"""Frozen-plan, standard-library paired CD8 descriptive analysis. No fitting."""
import csv, hashlib, io, json, math, sys
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

def number(x):
    try:
        d = Decimal(str(x))
        return d if d.is_finite() else None
    except InvalidOperation:
        return None

def ranks(values):
    return [1 + sum(w < v for w in values) + (sum(w == v for w in values)-1)/2 for v in values]

def spearman(x, y):
    if len(x) < 2: return None
    a, b = ranks(x), ranks(y)
    ma, mb = sum(a)/len(a), sum(b)/len(b)
    cov = sum((u-ma)*(v-mb) for u,v in zip(a,b))
    den = math.sqrt(sum((u-ma)**2 for u in a)*sum((v-mb)**2 for v in b))
    return cov/den if den else None

def sign(v): return 'positive' if v > 0 else 'negative' if v < 0 else 'zero'

def analyze(rows, cells):
    samples, patients, subjects = {}, {}, {}
    for row in rows:
        pid, tp, sid, sub = (row[k] for k in ('PatientID','SampleTimepoint','SampleID','Subject'))
        assert sid == pid+';'+tp, 'SampleID mismatch'
        assert sid not in samples, 'Duplicate patient/timepoint'
        assert pid not in patients or patients[pid] == (sub,row['Cohort']), 'Patient identity mismatch'
        assert sub not in subjects or subjects[sub] == pid, 'Subject identity mismatch'
        samples[sid] = row; patients[pid] = (sub,row['Cohort']); subjects[sub] = pid
    ihc = {}
    for cell in cells:
        if cell['field'] != 'CD8': continue
        sid = cell['sampleKey']
        assert sid in samples, 'IHC key absent'
        row = samples[sid]
        assert (str(cell['subject']),cell['timepoint'],cell['cohort']) == (row['Subject'],row['SampleTimepoint'],row['Cohort']), 'IHC identity mismatch'
        assert sid not in ihc, 'Duplicate IHC cell'
        vals = {number(v) for v in cell['distinctNumericValues']}
        vals.discard(None)
        assert len(vals) <= 1, 'Conflicting IHC values'
        ihc[sid] = next(iter(vals)) if vals else None
    ledger, paired = [], []
    for pid,(sub,cohort) in sorted(patients.items()):
        item = dict(patient_id=pid,subject=sub,histology=cohort)
        vals = {}
        for label,tp in [('baseline','Baseline'),('on','On-Treatment')]:
            sid = pid+';'+tp
            vals['rna_'+label] = number(samples[sid]['T-cell (CD8)']) if sid in samples else None
            vals['ihc_'+label] = ihc.get(sid)
            item['sample_'+label] = sid if sid in samples else None
        item.update({k:str(v) if v is not None else None for k,v in vals.items()})
        item['missing'] = [k for k,v in vals.items() if v is None]
        item['included'] = not item['missing']
        if item['included']:
            dr = vals['rna_on']-vals['rna_baseline']; di = vals['ihc_on']-vals['ihc_baseline']
            item.update(rna_change=str(dr),ihc_change_percentage_points=str(di),rna_direction=sign(dr),ihc_direction=sign(di))
            paired.append(item)
        ledger.append(item)
    directions = {a+'/'+b:sum(p['rna_direction']==a and p['ihc_direction']==b for p in paired) for a in ('negative','zero','positive') for b in ('negative','zero','positive')}
    same = sum(p['rna_direction']==p['ihc_direction'] and p['rna_direction']!='zero' for p in paired)
    nonzero = sum(p['rna_direction']!='zero' and p['ihc_direction']!='zero' for p in paired)
    hist = {h:{'included':sum(p['included'] and p['histology']==h for p in ledger),'excluded':sum(not p['included'] and p['histology']==h for p in ledger)} for h in sorted({p['histology'] for p in ledger})}
    return dict(registered_patients=len(ledger),shared_pairs=len(paired),direction_table_rna_then_ihc=directions,same_nonzero_direction=same,nonzero_pairs=nonzero,same_over_nonzero=same/nonzero if nonzero else None,same_over_all=same/len(paired) if paired else None,spearman_changes=spearman([Decimal(p['rna_change']) for p in paired],[Decimal(p['ihc_change_percentage_points']) for p in paired]),histology=hist,missingness_patterns=dict(Counter('|'.join(p['missing']) or 'complete' for p in ledger)),patients=ledger)

def main(folder):
    folder = Path(folder)
    source = folder/'SampleSourceData.txt'; numeric = folder/'numeric-ihc.json'
    expected={source:'66d1f6bf39becc76f82d194ef2bf7b1784689c6d01177a319c717e208427e625',numeric:'7fd0b176fa688c49f98aa21177f687e608e4de02739dd6a155eab430a9b2b51a'}
    for path,digest in expected.items():
        if hashlib.sha256(path.read_bytes()).hexdigest()!=digest: raise ValueError('Pinned input mismatch: '+path.name)
    data = json.loads(numeric.read_text(encoding='utf-8'),parse_float=Decimal)
    if data['result']['errors'] or data['result']['unmatchedPublishedRows']: raise ValueError('Frozen IHC extraction has unresolved errors')
    result = analyze(list(csv.DictReader(io.StringIO(source.read_text(encoding='utf-8')),delimiter='\t')),data['result']['numericCells'])
    result['input_sha256'] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,numeric,folder/'plan.md',Path(__file__)]}
    result['interpretation_scope'] = 'Within-patient descriptive changes; no causal, efficacy, survival or EMC-specific inference. RNA score units and IHC percentage points are different scales.'
    (folder/'results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    with (folder/'patient-ledger.tsv').open('w',encoding='utf-8',newline='') as handle:
        fields=list(dict.fromkeys(k for row in result['patients'] for k in row))
        writer=csv.DictWriter(handle,fieldnames=fields,delimiter='\t'); writer.writeheader();writer.writerows(result['patients'])
    print(json.dumps({k:v for k,v in result.items() if k!='patients'},indent=2))

if __name__ == '__main__': main(sys.argv[1])
