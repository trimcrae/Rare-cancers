"""Canonical SVG/PDF/PNG adapter; frozen draft geometry/statistics preserved.

Render figures only after exact input/script bytes are committed.

No new statistical analysis. Reads completed effect tables and released values.
Default --check validates frozen data and commit readiness WITHOUT rendering.
"""
from pathlib import Path
import argparse,csv,json,hashlib,subprocess,sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
PACKET=REPO/'research/autonomy/atlas-hofvander-validation-2026-09-06'
GENES='CD276 SSTR2 PRAME FAP CD248 CSPG4 MSLN L1CAM GPC3 ALPP CDH17 CHRNA6'.split()
HIST=['Myxoid liposarcoma','Low-grade fibromyxoid sarcoma','Synovial sarcoma']
INPUTS=['all-shared-histology-replication.csv','all-hofvander-contrasts.csv','all-primary-deletions.csv','results/selected-values.json','metadata-manifest.json']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(render=False):
    root=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=HERE,text=True).strip())
    pinned=json.loads((PACKET/'draft/figure-inputs.json').read_text())
    paths=[PACKET/x for x in INPUTS]+[HERE/'plot_emc_tissue_rna.py',PACKET/'draft/figure-inputs.json']
    state=[]
    for p in paths:
        key=p.relative_to(PACKET).as_posix() if p.is_relative_to(PACKET) else p.relative_to(root).as_posix()
        if key in pinned['inputs']:assert sha(p)==pinned['inputs'][key]['sha256'],f'input changed: {key}'
        result=subprocess.run(['git','show','HEAD:'+p.relative_to(root).as_posix()],cwd=root,capture_output=True)
        committed=result.returncode==0 and hashlib.sha256(result.stdout).hexdigest()==sha(p)
        state.append({'file':key,'sha256':sha(p),'exact_HEAD_bytes':committed})
    if render and not all(x['exact_HEAD_bytes'] for x in state):raise RuntimeError('Figure generation requires exact committed input and plotting-script bytes; coordinator must commit first.')
    return state
def load(name):
    with (PACKET/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def render(output):
    provenance=check(True)
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import TwoSlopeNorm
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':10,'axes.labelsize':9,'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','savefig.dpi':300})
    output.mkdir(parents=True,exist_ok=True)
    initial=load('all-hofvander-contrasts.csv');rep=load('all-shared-histology-replication.csv')
    lg={r['gene']:r for r in rep if r['histology']==HIST[1]};primary={(r['gene'],r['histology']):r for r in initial if r['group']=='primary'}
    mats=[np.array([[float(lg[g][k]) for k in ['array_A','Hof_A','Hof_matched_A']] for g in GENES])]+[np.array([[float(primary[g,h][mode+'_A']) for h in HIST] for g in GENES]) for mode in ['marginal','matched']]
    fig,axes=plt.subplots(1,3,figsize=(10,6),sharey=True,layout='constrained')
    titles=['A  LGFMS across cohorts','B  Hofvander: marginal','C  Hofvander: year matched']
    labels=[['Array\n6 EMC\n17 LGFMS','TPM\n9 EMC\n13 LGFMS','Matched TPM\n3 EMC\n12 LGFMS'],['MLPS\nn=14','LGFMS\nn=13','Synovial\nn=18'],['MLPS\n3 EMC','LGFMS\n3 EMC','Synovial\n3 EMC']]
    norm=TwoSlopeNorm(vmin=0,vcenter=.5,vmax=1)
    for ax,mat,title,xlabels in zip(axes,mats,titles,labels):
        im=ax.imshow(mat,cmap='RdBu_r',norm=norm,aspect='auto')
        ax.set_title(title,loc='left');ax.set_xticks(range(3),xlabels);ax.set_yticks(range(len(GENES)),[g+(' (control)' if g=='CHRNA6' else '') for g in GENES]);ax.tick_params(length=0)
        ax.axhline(10.5,color='black',lw=1.2)
        for i in range(12):
            for j in range(3):ax.text(j,i,f'{mat[i,j]:.2f}',ha='center',va='center',fontsize=8,color='white' if mat[i,j]<.2 or mat[i,j]>.8 else 'black')
    fig.colorbar(im,ax=axes,shrink=.7,label='A = P(EMC > comparator) + 0.5 P(tie)')
    for ext in ['pdf','png','svg']:fig.savefig(output/('surface-tissue-rna-figure1.'+ext))
    plt.close(fig)
    meta=json.loads((PACKET/'metadata-manifest.json').read_text())['samples'];vals=json.loads((PACKET/'results/selected-values.json').read_text())['CSPG4'];emc='Extraskeletal myxoid chondrosarcoma';groups=[emc]+HIST
    rows=[r for r in meta if r['eligible'] and r['diagnosis'] in groups];years=sorted({r['sequencing_year'] for r in rows});colors={y:plt.get_cmap('tab10')(i%10) for i,y in enumerate(years)}
    fig,axes=plt.subplots(1,2,figsize=(10,4.6),layout='constrained',gridspec_kw={'width_ratios':[1.25,1]})
    ax=axes[0]
    for i,g in enumerate(groups):
        records=sorted([r for r in rows if r['diagnosis']==g],key=lambda r:(r['sequencing_year'],r['sample_id']))
        offsets=np.linspace(-.2,.2,len(records))
        for off,r in zip(offsets,records):ax.scatter(i+off,np.log2(1+vals[r['sample_id']]),color=colors[r['sequencing_year']],s=29,edgecolor='white',linewidth=.3)
    ax.set_xticks(range(4),['EMC\nn=9','MLPS\nn=14','LGFMS\nn=13','Synovial\nn=18']);ax.set_ylabel('CSPG4 log2(1 + TPM)');ax.set_title('A  Every retained primary specimen',loc='left');ax.spines[['top','right']].set_visible(False)
    for y in years:ax.scatter([],[],c=[colors[y]],label=y,s=25)
    ax.legend(title='Sequencing year',fontsize=7,title_fontsize=8,ncol=4,loc='upper center',bbox_to_anchor=(.5,-.17),frameon=False)
    deleted=[r for r in load('all-primary-deletions.csv') if r['gene']=='CSPG4' and r['deletion_type']=='year']
    full=sum(float(primary['CSPG4',h]['matched_A']) for h in HIST)/3
    ax=axes[1];labels2=['Full data']+['Without '+r['deleted'] for r in deleted];effects=[full]+[float(r['matched_A']) if r['matched_A'] else np.nan for r in deleted]
    for i,(label,x) in enumerate(zip(labels2,effects)):ax.scatter(x,i,color='#b2182b' if label=='Without 2019' else '#2166ac',s=45)
    ax.axvline(.5,color='black',ls='--',lw=.9);ax.axvline(full,color='#2166ac',alpha=.35,lw=.8);ax.set_yticks(range(len(labels2)),labels2);ax.invert_yaxis();ax.set_xlim(0,1);ax.set_xlabel('Year-matched equal-histology A');ax.set_title('B  Sequencing-year deletion sensitivity',loc='left');ax.spines[['top','right']].set_visible(False)
    for ext in ['pdf','png','svg']:fig.savefig(output/('surface-tissue-rna-figure2.'+ext),bbox_inches='tight')
    plt.close(fig)
    record={'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),'inputs':provenance,'matplotlib':matplotlib.__version__,'numpy':np.__version__,'figures':{p.name:sha(p) for p in output.glob('surface-tissue-rna-figure*') if p.suffix in {'.pdf','.png','.svg'}},'scope':'descriptive source values and completed estimates; no uncertainty bars in these figures'}
    (output/'surface-tissue-rna-figure-provenance.json').write_text(json.dumps(record,indent=2)+'\n')
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--render',action='store_true');a.add_argument('--output',type=Path,default=HERE.parent/'figures');v=a.parse_args()
    if v.render:render(v.output)
    else:print(json.dumps({'rendered':False,'commit_readiness':check()},indent=2))
