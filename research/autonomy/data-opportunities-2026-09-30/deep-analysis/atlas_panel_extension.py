import sys,json,gzip,io,datetime,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from fusion_external_actual import h,contrast,boot,deletions,EMC,PRIMARY,CONTEXT
GROUPS={
'gag_linker_tetrasaccharide':['XYLT1','XYLT2','B4GALT7','B3GALT6','B3GAT3'],
'cs_backbone_polymerisation':['CSGALNACT1','CSGALNACT2','CHSY1','CHSY3','CHPF','CHPF2'],
'cs_sulfotransferases_4O':['CHST11','CHST12','CHST13','CHST14'],
'cs_sulfotransferases_6O':['CHST3','CHST7'],
'cs_sulfotransferases_other':['CHST15','UST'],
'dermatan_epimerase':['DSE','DSEL'],
'paps_module':['PAPSS1','PAPSS2','SLC35B2','SLC35B3','BPNT1'],
'cs_proteoglycan_core_proteins':['CSPG4','ACAN','VCAN','BCAN','NCAN','BGN','DCN','CSPG5','SRGN'],
'hyaluronan_contrast':['HAS1','HAS2','HAS3','HYAL1','HYAL2','CD44','HMMR'],
'gag_catabolism_chondroitinase_context':['ARSB','GALNS','GUSB','HEXA','HEXB'],
'NR2F_receptors':['NR2F1','NR2F2','NR2F6'],
'nr2f1_dormancy_context_only':['SOX9','RARB','NANOG','SOX2']}
GROUPS['dependency_context_only']=['MTAP','PRMT5','MAT2A','CDK7','CDK9','HSP90AA1','HSP90AB1','CDC37','ASS1','MDM2','EZH2','SMARCB1','POLQ','BCL2','BCL2L1','MCL1','PSMB5','CDKN2A']
NR_GENES=GROUPS['NR2F_receptors']+GROUPS['nr2f1_dormancy_context_only']
BOOT_GROUPS=['gag_linker_tetrasaccharide','cs_backbone_polymerisation','cs_sulfotransferases_4O','cs_sulfotransferases_6O','paps_module']
def run(matpath,metapath,outpath):
    wire=Path(matpath).read_bytes()
    raw=gzip.decompress(wire) if wire.startswith(b'\x1f\x8b') else wire
    assert hashlib.sha256(raw).hexdigest()=='b0d665d1bd1d96ace1faf66cc5a4d7ab7e41cb487c8f0f61734f102a1f9a7af3'
    frame=pd.read_csv(io.BytesIO(raw),sep='\t',index_col=0)
    mb=Path(metapath).read_bytes();assert hashlib.sha1(b'blob '+str(len(mb)).encode()+b'\x00'+mb).hexdigest()=='2998ce73eaca2e86507fa86dd38d924948d28d0c'
    metadata=json.loads(mb);rows=[r for r in metadata['samples'] if r['eligible']]
    assert frame.index.is_unique and frame.columns.is_unique
    assert len({r['patient_group'] for r in rows})==len(rows)
    assert all(r['sample_id'] in frame.columns for r in rows)
    V=frame[[r['sample_id'] for r in rows]].to_numpy(dtype=float);assert np.isfinite(V).all() and (V>=0).all()
    ranks=rankdata(V,method='average',axis=0)/len(V);symbols=frame.index.astype(str).tolist();lookup={g:i for i,g in enumerate(symbols)};rng=np.random.default_rng(2026100102)
    eis=[i for i,r in enumerate(rows) if r['diagnosis']==EMC];assert len(eis)==9
    records={};grouprecords={}
    for g in sorted(set(sum(GROUPS.values(),[]))):
        if g not in lookup:records[g]={'readable':False,'reason':'No exact symbol row; not biological absence'};continue
        v=V[lookup[g]]
        rec={'readable':True,'primary':contrast(v,rows),'context':contrast(v,rows,CONTEXT),'EMC_TPM':dict(zip([rows[i]['sample_id'] for i in eis],map(float,v[eis]))),'EMC_nonzero_TPM_count':int(np.sum(v[eis]>0)),'EMC_median_TPM':float(np.median(v[eis])),'EMC_TPM_range':[float(np.min(v[eis])),float(np.max(v[eis]))]}
        if g in NR_GENES:rec.update({'bootstrap_conditional_95':boot(v,rows,rng),'deletions':deletions(v,rows)})
        records[g]=rec
    for name,members in GROUPS.items():
        present=[g for g in members if g in lookup];missing=[g for g in members if g not in lookup]
        rec={'frozen_membership':members,'present':present,'missing':missing,'coverage':len(present)/len(members),'scoring':'mean within-specimen midrank /19116 genes, equal positive weights'}
        if missing:rec['score_omitted_reason']='Incomplete frozen membership; no partial substitution'
        else:
            scores=ranks[[lookup[g] for g in members]].mean(axis=0);rec.update({'primary':contrast(scores,rows),'context':contrast(scores,rows,CONTEXT),'EMC_scores':dict(zip([rows[i]['sample_id'] for i in eis],map(float,scores[eis])))})
            if name in BOOT_GROUPS:rec.update({'bootstrap_conditional_95':boot(scores,rows,rng),'deletions':deletions(scores,rows)})
        grouprecords[name]=rec
    out={'schema':'emc-atlas-matrix-nr2f-actual/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input_sha256':{'matrix_input':h(matpath),'matrix_uncompressed':hashlib.sha256(raw).hexdigest(),'metadata':h(metapath)},'matrix_shape':list(frame.shape),'eligible_patients':len(rows),'EMC_n':len(eis),'frozen_panel_source':'research/modalities/emc_expression_panels.py blob e48f8b38fba17237ea5985088f9e2e340a70042c; NG2 alias maps to CSPG4 once','route_ids':['PUB-MATRIX-ADDRESS','PUB-NR-OUTSIDE-NR4A3'],'genes':records,'groups':grouprecords,'limitations':['Bulk transcript abundance only; no glycan epitope, sulfation pattern, donor limitation, enzymatic activity, dormancy state, agonist response or delivery effect measured','Nonzero TPM is quantification, not malignant-cell protein localization','No new-value selection or exploratory inferential discovery claim; compositional ranks are not fold changes','Nine overlap-reduced EMC; four unique EMC support exact-year primary contrasts; bootstrap conditional on small observed cells','RNAseq may resolve unreadable array NR2F1 but not receptor activity or therapy fit','Equal positive group coefficients are annotations, not validated activity signatures']}
    Path(outpath).parent.mkdir(parents=True,exist_ok=True);Path(outpath).write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print('EMC_ATLAS_PANEL_RESULT_BEGIN');print(json.dumps(out,separators=(',',':')));print('EMC_ATLAS_PANEL_RESULT_END')
if __name__=='__main__':run(*sys.argv[1:4])
