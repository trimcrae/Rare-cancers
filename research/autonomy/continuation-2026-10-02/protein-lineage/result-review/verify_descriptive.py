"""Independent stdlib verification from saved family/gene measurements only."""
import argparse, hashlib, json, math, sys
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path
EXPECTED='bfbd5bee8d88053565af54f7f0dea225cb55fed71f688cb4b6cab6f922bc0dbb'
def require(ok,message):
    if not ok: raise ValueError(message)
def finite(x): return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)
def ranks(values):
    # Pairwise counting, without scipy/pandas/sorting-based rank helpers.
    return [F(1+sum(v<x for v in values))+F(sum(v==x for v in values)-1,2) for x in values]
def centered(a):
    mean=sum(a)/len(a)
    return [x-mean for x in a]
def product(a,b): return sum(x*y for x,y in zip(a,b))
def rho(rows):
    if len(rows)<3: return None
    a=centered(ranks([r['rna'] for r in rows]));b=centered(ranks([r['protein8498'] for r in rows]))
    den=math.sqrt(float(product(a,a)*product(b,b)))
    return float(product(a,b))/den if den else None
def close(a,b,label):
    require((a is None and b is None) or (a is not None and b is not None and abs(a-b)<1e-12),label)
def main():
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    raw=a.source.read_bytes();actual=hashlib.sha256(raw).hexdigest()
    exact=actual==EXPECTED
    extra_lf=not exact and raw.endswith(b'\n') and hashlib.sha256(raw[:-1]).hexdigest()==EXPECTED
    require(exact or extra_lf,'Unexpected source bytes beyond recognized single appended LF')
    j=json.loads(raw);ms=j['measurements'];require(len(ms)==122,'Expected122measurement rows')
    require(len({(r['gene'],r['relatedGroup']) for r in ms})==122,'Family/gene duplication')
    require(len(j['primaryModels'])==61,'Primary model count')
    genes=sorted({r['gene'] for r in ms});hist=sorted({r['Cancer_type'] for r in ms})
    require(len(genes)==2 and len(hist)==6,'Gene/histology scope')
    model_hist={r['relatedGroup']:r['Cancer_type'] for r in j['primaryModels']}
    require(len(model_hist)==61,'Duplicate primary family')
    for r in ms:
        require(model_hist[r['relatedGroup']]==r['Cancer_type'] and r['primarySarcomaTest']==1,'Family/histology membership')
        for value,flag in [('rna','rnaAvailable'),('protein6692','protein6692Available'),('protein8498','protein8498Available')]:
            require(finite(r[value])==r[flag],'Availability flag')
        require(r['support']==('original' if finite(r['protein6692']) else 'added'),'Support membership')
        require(r['paired']==(finite(r['rna']) and finite(r['protein8498'])),'Paired flag')
    cells={};defined=0
    for gene in genes:
        for h in hist:
            for support in ['original','added']:
                rows=[r for r in ms if (r['gene'],r['Cancer_type'],r['support'])==(gene,h,support)]
                paired=[r for r in rows if finite(r['rna']) and finite(r['protein8498'])]
                c=dict(gene=gene,histology=h,support=support,n=len(paired),rho=rho(paired),familiesWithSupportStatus=len(rows),
                       rnaAvailable=sum(finite(r['rna']) for r in rows),protein8498Available=sum(finite(r['protein8498']) for r in rows),
                       distinctRNA=len({r['rna'] for r in paired}),distinctProtein=len({r['protein8498'] for r in paired}))
                cells[gene,h,support]=c;defined+=c['rho'] is not None
    require(len(j['cells'])==len(cells)==24,'Cell count')
    seen=set()
    for c in j['cells']:
        key=c['gene'],c['histology'],c['support']; require(key not in seen,'Duplicate cell');seen.add(key)
        calc=cells[key]
        for field in ['n','familiesWithSupportStatus','rnaAvailable','protein8498Available','distinctRNA','distinctProtein']:
            require(c[field]==calc[field],'Cell count '+field)
        close(c['rho'],calc['rho'],'Cell rho')
    output=[]
    for gene in genes:
        for support in ['original','added']:
            rows=[r for r in ms if r['gene']==gene and r['support']==support and finite(r['rna']) and finite(r['protein8498'])]
            x=ranks([r['rna'] for r in rows]);y=ranks([r['protein8498'] for r in rows]);cx=centered(x);cy=centered(y)
            den=math.sqrt(float(product(cx,cx)*product(cy,cy)));mx=sum(x)/len(x);my=sum(y)/len(y)
            groups=defaultdict(list)
            for i,r in enumerate(rows):groups[r['Cancer_type']].append(i)
            within=F(0);between=F(0);strata=[]
            for h,idx in sorted(groups.items()):
                xx=[x[i] for i in idx];yy=[y[i] for i in idx];gx=sum(xx)/len(xx);gy=sum(yy)/len(yy)
                w=product(centered(xx),centered(yy));b=len(idx)*(gx-mx)*(gy-my);within+=w;between+=b
                strata.append(dict(histology=h,n=len(idx),withinComponent=float(w)/den,betweenComponent=float(b)/den))
            require(within+between==product(cx,cy),'Exact rational covariance identity')
            calculated=dict(gene=gene,support=support,n=len(rows),rho=float(product(cx,cy))/den,
                            withinComponent=float(within)/den,betweenComponent=float(between)/den,strata=strata)
            matches=[d for d in j['decompositions'] if d['gene']==gene and d['support']==support];require(len(matches)==1,'Decomposition identity')
            old=matches[0];require(old['n']==len(rows),'Decomposition n')
            for k in ['rho','withinComponent','betweenComponent']:close(old[k],calculated[k],'Decomposition '+k)
            require(len(old['strata'])==len(strata),'Strata count')
            for s in strata:
                os=[z for z in old['strata'] if z['histology']==s['histology']];require(len(os)==1 and os[0]['n']==s['n'],'Stratum identity')
                close(os[0]['withinContribution'],s['withinComponent'],'Within stratum');close(os[0]['betweenContribution'],s['betweenComponent'],'Between stratum')
            output.append(calculated)
    require(len(j['decompositions'])==len(output)==4,'Decomposition count')
    paired=[]
    for gene in genes:
        for h in hist:
            o=cells[gene,h,'original'];n=cells[gene,h,'added']
            if o['rho'] is not None and n['rho'] is not None:
                paired.append(dict(gene=gene,histology=h,original_n=o['n'],added_n=n['n'],original_rho=o['rho'],added_rho=n['rho'],sign_reversal=o['rho']*n['rho']<0))
    require(len(paired)==4 and sum(x['sign_reversal'] for x in paired)==2,'Paired-cell support')
    result=dict(status='passed',method='Independent pairwise midranks and exact Fraction covariance partition; no model fits',
                source_sha256=actual,expected_original_sha256=EXPECTED,source_bytes=len(raw),single_appended_LF=extra_lf,
                python=sys.version,measurements=122,primary_families=61,cells_checked=24,defined_cell_correlations=defined,
                decompositions=output,paired_supported_combinations=paired,
                limits=['Checks saved measurements and summaries, not primary mass-spectrometry extraction or mapping.',
                        'Within/between terms use subset-global ranks and are not within-cell Spearman coefficients.',
                        'Descriptive partition is not causal attribution or a fixed-composition counterfactual.',
                        'Cells with two pairs contribute covariance despite the n>=3 reporting rule for cell rho.'])
    a.out.mkdir(parents=True,exist_ok=True);(a.out/'review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'passed','source_sha256':actual,'single_appended_LF':extra_lf,'cells':24,'decompositions':4,'paired_supported_combinations':paired}))
if __name__=='__main__': main()
