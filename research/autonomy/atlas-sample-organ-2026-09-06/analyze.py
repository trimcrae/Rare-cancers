"""Deterministic fixed-panel reanalysis; see frozen protocol.md. Python standard library."""
from pathlib import Path
from decimal import Decimal
from collections import Counter, defaultdict
import csv, gzip, hashlib, json, re, sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PANEL = 'CHRNA6 CD276 SSTR2 PRAME FAP CD248 CSPG4 MSLN L1CAM GPC3 ALPP CDH17'.split()
SARCOMAS = 'ESS EWS GIST LMS MLPS DDLPS SS'.split()
SOURCE = HERE / 'GSE28866_36048_normalized_peaks_cancer_and_normal.txt.gz'
URL = 'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE28nnn/GSE28866/suppl/' + SOURCE.name
EXPECTED = '11dae64b2d6b6e77846c3f14971fc9a313da86eb52a4b8b83df96c23eedc0ffd'
ANNOTATIONS = ['peak','hg18_coords','classification','gene_id','gene_symbol','peak_exon_gene_symbol','differentially_expressed_cancer_type']
PAIRS = {'ESS_STT5520': ['ESS_STT5520_rep1','ESS_STT5520_rep2'], 'LMS_STT516':['LMS_STT516_rep1','LMS_STT516_rep2']}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def tokens(s): return sorted(set(t for t in re.split(r'[,;|/\s]+', s.strip()) if t))
def med(vals):
    a = sorted(x for x in vals if x is not None)
    return None if not a else a[len(a)//2] if len(a)%2 else (a[len(a)//2-1]+a[len(a)//2])/2

def delta(a,b): return None if a is None or b is None else a-b
def sign(v): return 'missing' if v is None else 'positive' if v>0 else 'negative' if v<0 else 'zero'
def enc(o):
    if isinstance(o,Decimal): return str(o)
    raise TypeError(type(o).__name__)
def dump(p,obj): p.write_text(json.dumps(obj,indent=2,sort_keys=True,default=enc)+'\n',encoding='utf-8')

def main():
    assert sha(SOURCE)==EXPECTED
    seriespath=ROOT/'research/modalities/geo-gse28866-brunner-series.json'
    series=json.loads(seriespath.read_text(encoding='utf-8'))
    with gzip.open(SOURCE,'rt',newline='') as f:
        reader=csv.reader(f,delimiter='\t'); header=next(reader)
        assert header[:7]==ANNOTATIONS and len(header)==100 and len(set(header))==100
        rows=list(reader)
    assert len(rows)==36048 and all(len(r)==100 for r in rows)
    columns=[]
    for i,name in enumerate(header[7:],7):
        stt=re.search(r'STT\d+',name).group()
        normal=re.fullmatch(r'STT\d+_(Adult|Fetal)_normal_(.+)',name)
        hist=name.split('_STT')[0] if not normal else None
        stage,organ=normal.groups() if normal else (None,None)
        unit=re.sub(r'_rep[12]$','',name)
        candidates=[s for s in series['samples'] if re.search(r'(?<!\w)'+stt+r'(?!\d)',s['title'])]
        # STT appears at title start; underscore is retained after identifier.
        if len(candidates)>1 and name.endswith(('_rep1','_rep2')):
            rep=name[-4:]
            exact=[s for s in candidates if rep in s['title']]
            if exact: candidates=exact
        columns.append(dict(index_zero_based=i,header=name,stt=stt,unit=unit,histology=hist,stage=stage,organ=organ,
            role='EMC' if hist=='EMC' else 'sarcoma' if hist in SARCOMAS else 'normal' if normal else 'other_cancer',
            geo_candidates=[{'accession':s['accession'],'title':s['title'],'characteristics':s['characteristics']} for s in candidates],
            mapping_status='unique_metadata_match' if len(candidates)==1 else 'ambiguous_metadata_match' if candidates else 'missing_metadata_match'))
    assert Counter(c['role'] for c in columns)=={'EMC':4,'sarcoma':32,'normal':27,'other_cancer':30}
    assert Counter(c['stage'] for c in columns if c['role']=='normal')=={'Adult':17,'Fetal':10}
    units=defaultdict(list)
    for c in columns: units[c['unit']].append(c)
    assert {k:[c['header'] for c in v] for k,v in units.items() if len(v)>1}==PAIRS
    assert len(units)==91
    strata={}
    for h in SARCOMAS: strata['sarcoma:'+h]=[u for u,cs in units.items() if cs[0]['histology']==h]
    strata['sarcoma:pooled']=[u for u,cs in units.items() if cs[0]['role']=='sarcoma']
    for stage in ['Adult','Fetal']:
        for organ in sorted({c['organ'] for c in columns if c['stage']==stage}):
            strata[stage.lower()+':'+organ]=[u for u,cs in units.items() if cs[0]['stage']==stage and cs[0]['organ']==organ]
        strata[stage.lower()+':pooled']=[u for u,cs in units.items() if cs[0]['stage']==stage]
    strata['normal:adult_fetal_pooled']=[u for u,cs in units.items() if cs[0]['role']=='normal']
    emc=[u for u,cs in units.items() if cs[0]['role']=='EMC']
    assert emc==['EMC_STT5525','EMC_STT5526','EMC_STT5527','EMC_STT5592']
    selected=[]; annotations=[]; result=[]; missing=[]; mapping=[]
    for row in rows:
        ann=dict(zip(ANNOTATIONS,row[:7])); annotations.append(ann)
        sym1=tokens(ann['gene_symbol']); sym2=tokens(ann['peak_exon_gene_symbol']); syms=sorted(set(sym1+sym2))
        matched=[g for g in PANEL if g in syms]
        if not matched: continue
        selected.append(row)
        raw={}
        for c in columns:
            try:
                v=Decimal(row[c['index_zero_based']]); v=v if v.is_finite() else None
            except Exception: v=None
            raw[c['header']]=v
            if v is None: missing.append({'peak':ann['peak'],'column':c['header'],'raw':row[c['index_zero_based']]})
        # If a documented pair is incomplete, do not silently use only one replicate.
        values={u:sum(raw[c['header']] for c in cs)/len(cs) if all(raw[c['header']] is not None for c in cs) else None for u,cs in units.items()}
        reps={u:{'raw':{c['header']:raw[c['header']] for c in units[u]},'collapsed':values[u],
            'range':[min(raw[c['header']] for c in units[u]),max(raw[c['header']] for c in units[u])] if values[u] is not None else None} for u in PAIRS}
        e={u:values[u] for u in emc}; em=med(e.values())
        peakcontrasts=[]
        for s,us in strata.items():
            available=[values[u] for u in us if values[u] is not None]; cm=med(available)
            indiv={u:delta(v,cm) for u,v in e.items()}
            peakcontrasts.append(dict(stratum=s,coverage_complete=all(v is not None for v in e.values()) and len(available)==len(us),n_emc_available=sum(v is not None for v in e.values()),n_comparator_available=len(available),n_comparator_total=len(us),emc_median=em,comparator_median=cm,delta=delta(em,cm),direction=sign(delta(em,cm)),individual_emc_deltas=indiv,individual_directions={u:sign(v) for u,v in indiv.items()},minimum_emc_minus_maximum_comparator=delta(min(v for v in e.values() if v is not None) if any(v is not None for v in e.values()) else None,max(available) if available else None)))
        sensitivity=[]; base=delta(em,med(values[u] for u in strata['sarcoma:pooled']))
        for u in emc:
            d=delta(med(v for k,v in e.items() if k!=u),med(values[k] for k in strata['sarcoma:pooled']))
            sensitivity.append(dict(family='leave_one_EMC_out',deleted=u,delta=d,direction=sign(d),sign_changed=sign(d)!=sign(base)))
        for h in SARCOMAS:
            d=delta(em,med(values[u] for u in strata['sarcoma:pooled'] if u not in strata['sarcoma:'+h]))
            sensitivity.append(dict(family='leave_one_histology_out',deleted=h,delta=d,direction=sign(d),sign_changed=sign(d)!=sign(base)))
        for g in matched:
            m=dict(gene=g,peak=ann['peak'],gene_symbol_tokens=sym1,peak_exon_gene_symbol_tokens=sym2,union_tokens=syms,strict_mapping=syms==[g],fields_disagree=bool(sym1 and sym2 and sym1!=sym2))
            mapping.append(m)
            result.append(dict(gene=g,peak=ann['peak'],mapping=m,annotations=ann,emc_values=e,unit_values=values,technical_replicates=reps,contrasts=peakcontrasts,sensitivity=sensitivity))
    with (HERE/'selected-source-rows.tsv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n'); w.writerow(header); w.writerows(selected)
    with (HERE/'all-peak-annotations.tsv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=ANNOTATIONS,delimiter='\t',lineterminator='\n'); w.writeheader(); w.writerows(annotations)
    summary=[]
    for g in PANEL:
        rs=[r for r in result if r['gene']==g]
        for mode in ['all_attributable','strict_only']:
            subset=[r for r in rs if mode=='all_attributable' or r['mapping']['strict_mapping']]
            out=dict(gene=g,mapping_mode=mode,n_peaks=len(subset),status='represented' if subset else 'no_mapping_not_expression_absence',strata={})
            for s in strata:
                cs=[c for r in subset for c in r['contrasts'] if c['stratum']==s]
                out['strata'][s]={'peak_directions':dict(Counter(c['direction'] for c in cs)), 'individual_directions':dict(Counter(d for c in cs for d in c['individual_directions'].values())), 'complete_peak_contrasts':sum(c['coverage_complete'] for c in cs), 'incomplete_peak_contrasts':sum(not c['coverage_complete'] for c in cs), 'all_four_EMC_above_comparator_median_peaks':sum(c['coverage_complete'] and all(d=='positive' for d in c['individual_directions'].values()) for c in cs), 'strict_all_EMC_above_all_comparators_peaks':sum(c['coverage_complete'] and sign(c['minimum_emc_minus_maximum_comparator'])=='positive' for c in cs)}
            out['sensitivity_sign_changes']=sum(x['sign_changed'] for r in subset for x in r['sensitivity'])
            summary.append(out)
    dump(HERE/'column-mapping.json',dict(columns=columns,units={u:[c['header'] for c in cs] for u,cs in units.items()},strata=strata,emc_units=emc))
    dump(HERE/'results.json',dict(decimal_encoding='exact base-10 strings; sign uses Decimal arithmetic',panel=PANEL,mapping=mapping,missing_cells=missing,peaks=result,summary=summary))
    inputs=[SOURCE,seriespath,HERE/'protocol-frozen.md.txt',ROOT/'research/modalities/gse28866-tumour-vs-normal.json',ROOT/'research/modalities/gse28866_tumour_vs_normal.py',ROOT/'research/modalities/surface-address-sensitivity.md',ROOT/'research/modalities/atlas-independent-normal-feasibility.md',ROOT/'research/autonomy/cycle-outcomes/20260905T133448Z-6bd43b913c/atlas-primary-matrix-availability.json']
    dump(HERE/'provenance.json',dict(base_revision='95b30a620c45f459463a032a2044b253112b2d4a',source_url=URL,methods_url='https://link.springer.com/article/10.1186/gb-2012-13-8-r75',inputs=[dict(path=str(p.relative_to(ROOT)).replace('\\','/'),sha256=sha(p),bytes=p.stat().st_size) for p in inputs],script_sha256=sha(Path(__file__)),outputs=[dict(path=p.name,sha256=sha(p),bytes=p.stat().st_size) for p in [HERE/'selected-source-rows.tsv',HERE/'all-peak-annotations.tsv',HERE/'column-mapping.json',HERE/'results.json']]))
    print(json.dumps({'selected_unique_rows':len(selected),'gene_peak_assignments':len(result),'missing_selected_cells':len(missing),'columns':len(columns),'units':len(units),'panel_mapping_counts':{g:sum(r['gene']==g for r in result) for g in PANEL}}))

if __name__=='__main__': main()

