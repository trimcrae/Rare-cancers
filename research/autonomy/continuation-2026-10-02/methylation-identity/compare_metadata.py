"""Replay the bounded sample-identity join from captured primary metadata only."""
import csv, hashlib, io, json, re
from collections import Counter, defaultdict
from pathlib import Path
import openpyxl
R=Path(__file__).resolve().parent
receipts=json.loads((R/'retrieval-receipts.json').read_text())
PINS={'41467_2020_20603_MOESM4_ESM.xlsx':'85a148285ef1812d6ca8d68c839a2d64f73cebb6f8ebfa95844e3d85b5c03bb9',
      '41467_2020_20603_MOESM6_ESM.xlsx':'605dd1ba7af9845e53f5db51c11b8d7e36b0076ade3dd5ba97edccbdf32ceb36',
      'E-MTAB-9875.sdrf.txt':'c6ffc854493f95d3b1c70bc18e0862abf269ea889e7ca2db153d435c80adc216'}
for name,expected in PINS.items():
    if hashlib.sha256((R/name).read_bytes()).hexdigest()!=expected: raise ValueError('Pinned metadata mismatch '+name)
for r in receipts:
    if r.get('status')==200:
        b=(R/r['file']).read_bytes()
        if len(b)!=r['bytes'] or hashlib.sha256(b).hexdigest()!=r['sha256']: raise ValueError('Receipt mismatch '+r['file'])
def cohort(n,label):
    ws=openpyxl.load_workbook(R/f'41467_2020_20603_MOESM{n}_ESM.xlsx',read_only=True,data_only=True).worksheets[0]
    rows=list(ws.iter_rows(values_only=True)); hdr=[str(x or '') for x in rows[0]]
    out=[]
    for row in rows[1:]:
        if not row or not isinstance(row[0],str) or not row[0].startswith(label+'_SAMPLE '): continue
        d=dict(zip(hdr,row)); d['profile_id']=row[0]; out.append(d)
    return hdr,out
rh,refs=cohort(4,'REFERENCE'); vh,vals=cohort(6,'VALIDATION')
assert len(refs)==1077 and len(vals)==428
assert len({r['IDAT'] for r in refs})==1077 and len({r['IDAT'] for r in vals})==428
with (R/'E-MTAB-9875.sdrf.txt').open(encoding='utf-8-sig',newline='') as f:
    sdrf=list(csv.DictReader(f,delimiter='\t')); sh=list(sdrf[0])
arrays=defaultdict(list)
for row in sdrf:
    m=re.fullmatch(r'(\d+_R\d\dC\d\d)_(Grn|Red)\.idat',row['Array Data File'])
    if not m: raise ValueError('Unexpected IDAT basename')
    arrays[m[1]].append(row)
assert len(sdrf)==1972 and len(arrays)==986
for ident,rows in arrays.items():
    assert len(rows)==2 and len({r['Characteristics[individual]'] for r in rows})==1
    assert {r['Array Data File'].split('_')[-1] for r in rows}=={'Red.idat','Grn.idat'}
individuals=defaultdict(set)
for ident,rows in arrays.items(): individuals[rows[0]['Characteristics[individual]']].add(ident)
cross=[]
for cohort_name,rows in [('reference',refs),('validation',vals)]:
    for row in rows:
        if row['IDAT'] in arrays:
            a=arrays[row['IDAT']][0]
            cross.append(dict(koelsche_cohort=cohort_name,koelsche_profile=row['profile_id'],IDAT=row['IDAT'],
                emtab_source=a['Source Name'],emtab_individual=a['Characteristics[individual]'],emtab_disease=a['Characteristics[disease]'],
                koelsche_diagnosis=row.get('Diagnosis',row.get('Institutional diagnosis','')),
                koelsche_supplier=row.get('Supplier',row.get('Supplier study',''))))
with (R/'cross-accession-array-overlap.tsv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['koelsche_cohort','koelsche_profile','IDAT','emtab_source','emtab_individual','emtab_disease','koelsche_diagnosis','koelsche_supplier'],delimiter='\t');w.writeheader();w.writerows(cross)
refids={x['IDAT'] for x in refs};valids={x['IDAT'] for x in vals}
summary=dict(reference_profiles=len(refs),validation_profiles=len(vals),reference_validation_array_overlap=len(refids&valids),
    emtab_assay_rows=len(sdrf),emtab_arrays=len(arrays),emtab_individual_labels=len(individuals),
    emtab_repeated_individuals={k:sorted(v) for k,v in individuals.items() if len(v)>1},
    emtab_reference_array_overlap=len(refids&set(arrays)),emtab_validation_array_overlap=len(valids&set(arrays)),
    overlap_by_diagnosis=dict(Counter(r['emtab_disease'] for r in cross)),
    reference_fields=rh,validation_fields=vh,emtab_fields=sh,
    patient_linkage_caveat='E-MTAB individual labels are accession-local; no shared patient identifier is present in the Koelsche workbook columns. Exact array reuse is not proof of additional different-array patient overlap or nonoverlap.')
(R/'identity-results.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
with (R/'profile-array-crosswalk.tsv').open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['dataset','role','profile_or_source_id','IDAT','accession_local_individual_label'])
    for role,cohort_rows in [('reference',refs),('validation',vals)]:
        for r in cohort_rows: w.writerow(['GSE140686_primary_supplement',role,r['profile_id'],r['IDAT'],'not_provided'])
    for ident,rr in sorted(arrays.items()):
        w.writerow(['E-MTAB-9875','external_validation',rr[0]['Source Name'],ident,rr[0]['Characteristics[individual]']])
print(json.dumps(summary))
