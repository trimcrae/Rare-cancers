"""Utilities for measured full-CpG transfer benchmark; no classifier execution on import."""
import hashlib,io,json,pathlib,time,urllib.request
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold,StratifiedKFold
from sklearn.preprocessing import OneHotEncoder
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'outputs'/'methylation';CACHE=OUT/'download-cache'
SEED=2601001
MD='https://raw.githubusercontent.com/qtran1/MeQTrack_app/578bb615e0e89858ffb02cbe1da87680c74a01ba/reference/GSE140686_sarcoma_methylation_labels.csv'
MD_SHA='c3b102c078a1035f4589952ea8b50ff3a8fbbb63ed8edd425aed2ea343119a19'
START=time.time()
def digest(b):return hashlib.sha256(b).hexdigest()
def bounded_get(url,limit):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Rare-cancers-reproducible-public-analysis/1'}),timeout=120) as r:b=r.read(limit+1)
    if len(b)>limit:raise ValueError('download exceeds bound')
    return b
def write_json(name,obj):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n');return p
def save_tsv(name,frame):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);frame.to_csv(p,sep='\t',index=False,lineterminator='\n');return p
def freeze_splits(md):
    y=md.Meth_Class.to_numpy();n=np.zeros((len(md),1));schemes={}
    schemes['sample']=list(StratifiedKFold(n_splits=5,shuffle=True,random_state=SEED).split(n,y))
    for field in ['Supplier','chip']:schemes[field.lower()]=list(StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=SEED).split(n,y,groups=md[field]))
    counts=md.Meth_Class.value_counts();eligible=[];support=[]
    for cls in sorted(counts.index):
        row={'class':cls,'n':int(counts[cls])};good=counts[cls]>=10
        for scheme,splits in schemes.items():
            tr=[int(np.sum(y[a]==cls)) for a,b in splits];te=[int(np.sum(y[b]==cls)) for a,b in splits]
            row[scheme+'_train_counts']=tr;row[scheme+'_test_counts']=te;good=good and min(tr)>=5
        row['common_panel_eligible']=bool(good);support.append(row)
        if good:eligible.append(cls)
    if len(eligible)<2:raise ValueError('too few supported classes')
    rows=[]
    for scheme,splits in schemes.items():
        fold=np.full(len(md),-1,int)
        for k,(a,b) in enumerate(splits):
            assert not set(a)&set(b)
            if scheme!='sample':
                field='Supplier' if scheme=='supplier' else 'chip'
                assert not set(md.iloc[a][field])&set(md.iloc[b][field])
            fold[b]=k
        assert np.all(fold>=0)
        for i,x in md.iterrows():rows.append({'scheme':scheme,'IDAT':x.IDAT,'ID':x.ID,'class':x.Meth_Class,'supplier':x.Supplier,'chip':x.chip,'fold':int(fold[i]),'common_panel':x.Meth_Class in eligible})
    return schemes,eligible,support,pd.DataFrame(rows)
def select_train(a,b,y):
    im=SimpleImputer(strategy='median',keep_empty_features=True)
    at=im.fit_transform(a).astype(np.float32);bt=im.transform(b).astype(np.float32)
    f,_=f_classif(at,y);f=np.nan_to_num(f,nan=-np.inf,posinf=np.finfo(float).max,neginf=-np.inf)
    cols=np.argsort(-f,kind='stable')[:min(500,at.shape[1])]
    return at[:,cols],bt[:,cols],cols
def metrics(probs,y,classes):
    ci={c:i for i,c in enumerate(classes)};truth=np.array([ci[c] for c in y]);pred=probs.argmax(1)
    truep=probs[np.arange(len(y)),truth];brier=(probs*probs).sum(1)-2*truep+1;high=probs.max(1)>=.9
    recall=[float(np.mean(pred[truth==i]==i)) for i in range(len(classes)) if np.any(truth==i)]
    m={'n_profiles':len(y),'n_classes':len(classes),'accuracy':float(np.mean(pred==truth)),'macro_recall':float(np.mean(recall)),'multiclass_brier_sum_convention':float(np.mean(brier)),'vote_0.9_coverage':float(np.mean(high)),'vote_0.9_assigned_n':int(high.sum()),'vote_0.9_errors':int(np.sum((pred!=truth)&high)),'vote_0.9_error_fraction':float(np.mean(pred[high]!=truth[high])) if np.any(high) else None}
    return m,truth,pred,brier
def evaluate(panel_name,mask,schemes,x,md,rows,archive):
    classes=sorted(md.loc[mask,'Meth_Class'].unique());idx=np.flatnonzero(mask);y=md.loc[mask,'Meth_Class'].to_numpy();out={}
    for scheme,splits in schemes.items():
        models={k:np.full((len(md),len(classes)),np.nan,dtype=np.float64) for k in ['methylation','provenance','training_prevalence']};selected=[]
        for k,(train,test) in enumerate(splits):
            a=train[mask[train]];b=test[mask[test]]
            if not len(b):continue
            if set(md.iloc[a].Meth_Class)!=set(classes):raise ValueError('class absent from training')
            ya=md.iloc[a].Meth_Class.to_numpy();at,bt,cols=select_train(x[a],x[b],ya)
            rf=RandomForestClassifier(n_estimators=200,max_features='sqrt',class_weight='balanced_subsample',n_jobs=2,random_state=SEED+k)
            rf.fit(at,ya);assert list(rf.classes_)==classes;models['methylation'][b]=rf.predict_proba(bt)
            selected.append({'fold':k,'train_n':len(a),'test_n':len(b),'selected_probe_count':len(cols),'selected_probe_ids_sha256':digest('\n'.join(archive['probes'][c] for c in cols).encode())})
            enc=OneHotEncoder(handle_unknown='ignore',sparse_output=True);fields=['Supplier','chip','DNA']
            ma=enc.fit_transform(md.iloc[a][fields]);mb=enc.transform(md.iloc[b][fields])
            lr=LogisticRegression(class_weight='balanced',max_iter=2000,solver='lbfgs',random_state=SEED+k)
            lr.fit(ma,ya);assert list(lr.classes_)==classes;models['provenance'][b]=lr.predict_proba(mb)
            n=np.array([np.sum(ya==c) for c in classes],float);models['training_prevalence'][b]=n/n.sum()
            print(json.dumps({'methylation_progress':{'panel':panel_name,'scheme':scheme,'fold':k,'train':len(a),'test':len(b),'seconds':round(time.time()-START,1)}},separators=(',',':')),flush=True)
        out[scheme]={}
        for model,p in models.items():
            p=p[idx]
            if not np.isfinite(p).all() or not np.allclose(p.sum(1),1):raise ValueError('invalid predictions')
            m,t,pr,br=metrics(p,y,classes);perclass=[]
            for j,c in enumerate(classes):
                z=t==j;perclass.append({'class':c,'n':int(z.sum()),'correct':int(np.sum(pr[z]==j)),'recall':float(np.mean(pr[z]==j))})
            m['per_class']=perclass;out[scheme][model]=m;archive['votes'][panel_name+'__'+scheme+'__'+model]=p
            for q,profile in enumerate(idx):
                r=md.iloc[profile]
                rows.append({'panel':panel_name,'scheme':scheme,'model':model,'ID':r.ID,'IDAT':r.IDAT,'truth':y[q],'predicted':classes[pr[q]],'max_vote':float(p[q].max()),'true_class_vote':float(p[q,t[q]]),'brier':float(br[q]),'correct':bool(pr[q]==t[q]),'assigned_vote_0.9':bool(p[q].max()>=.9)})
        out[scheme]['fitting']=selected
    return out,classes,idx
def paired_bootstrap(frame,md,group):
    f=frame[(frame.panel=='common')&(frame.model=='methylation')]
    z=f.pivot(index='IDAT',columns='scheme',values='brier').join(md.set_index('IDAT')[[group]])
    if z[['sample','supplier','chip']].isna().any().any():raise ValueError('unpaired profiles')
    levels=sorted(z[group].unique());blocks=[z[z[group]==g] for g in levels];rng=np.random.default_rng(SEED)
    other='supplier' if group=='Supplier' else 'chip';observed=float((z[other]-z['sample']).mean());boots=[]
    sums=np.array([(b[other]-b['sample']).sum() for b in blocks]);sizes=np.array([len(b) for b in blocks])
    for k in range(1000):
        sampled=rng.integers(0,len(blocks),size=len(blocks));boots.append(float(sums[sampled].sum()/sizes[sampled].sum()))
    return {'contrast':other+' minus sample','endpoint':'paired per-profile multiclass Brier','n_profiles':len(z),'cluster_variable':group,'n_clusters':len(blocks),'difference':observed,'descriptive_cluster_bootstrap_95_percentile':[float(x) for x in np.quantile(boots,[.025,.975])],'bootstrap_draws':1000,'limitation':'resamples saved cross-validation predictions; excludes refitting/training variability; no causal technical effect estimate'}
