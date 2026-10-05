import pathlib,json,csv,io,hashlib,subprocess,datetime,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator,FuncFormatter
P=pathlib.Path(__file__).parent
SRC=pathlib.Path('/workspace/emc-r6-diagnostic/research/autonomy/fresh-discovery-2026-10-05-round9/public_resource_omissions/gpnmb_exploratory_analysis_results')
REPLAY=pathlib.Path('/workspace/emc-r6-single_cell/research/autonomy/fresh-discovery-2026-10-05-round9/rna_processing/gpnmb_numeric_replay/INDEPENDENT-FIXED-CELLS.json')
PREFIX='research/autonomy/fresh-discovery-2026-10-05-round9/public_resource_omissions/gpnmb_exploratory_analysis_results/'
COMMIT='708f1d5e5b1b03fe5da0402214f41113c208ed41'
checks=[];bindings=[]
def ck(name,truth):
 checks.append({'check':name,'pass':bool(truth)})
 if not truth:raise RuntimeError(name)
def original(name):
 b=subprocess.check_output(['git','-C','/workspace/emc-r6-diagnostic','show',COMMIT+':'+PREFIX+name]);current=(SRC/name).read_bytes();ck('original_commit_bytes:'+name,b==current);bindings.append({'path':str(SRC/name),'original_commit':COMMIT,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()});return b
b=original('MEASUREMENTS.tsv');ck('measurement_sha',hashlib.sha256(b).hexdigest()=='ea14de5aab1022a4b99431786e7e054456e87f704592d4e5a6f08636f4775cab')
rows=list(csv.DictReader(io.StringIO(b.decode()),delimiter='\t'));h=json.loads(original('HOFVANDER-RESULTS.json'))['all_conditions']['Low-grade fibromyxoid sarcoma'];a=json.loads(original('GSE24369-RESULTS.json'))['primary_LGFMS'];ind=json.load(open(REPLAY));bindings.append({'path':str(REPLAY),'bytes':REPLAY.stat().st_size,'sha256':hashlib.sha256(REPLAY.read_bytes()).hexdigest()})
panels=[];plotrows=[]
for ds,result,feature,unit,nn in [('Hofvander',h,'GPNMB','TPM',(13,13)),('GSE24369',a,'8131844','RMA log2',(6,17))]:
 groups=[]
 for group,ids,n in [('EMC',result['EMC_ids'],nn[0]),('LGFMS',result['comparator_ids'],nn[1])]:
  ck(ds+group+':declared_n',len(ids)==n);points=[]
  for sid in ids:
   hits=[r for r in rows if r['dataset']==ds and r['condition_id']==sid and r['feature']==feature];ck(ds+sid+':unique_cell',len(hits)==1);r=hits[0];v=float(r['value']);ck(ds+sid+':unit',r['unit']==unit);ck(ds+sid+':finite',math.isfinite(v));ck(ds+sid+':gene',r['gene']=='GPNMB')
   ih=[x for x in ind[ds] if (x.get('sample_id') or x.get('gsm'))==sid];ck(ds+sid+':independent_unique',len(ih)==1);ck(ds+sid+':independent_exact_value',ih[0]['value']==v)
   source_label=ih[0].get('source_label') or ih[0].get('title');point={'panel':'A' if ds=='Hofvander' else 'B','dataset':ds,'group':group,'condition_id':sid,'source_label':source_label,'feature':feature,'value_lexeme':r['value'],'unit':unit,'highlight':'LR5081-14' if ds=='Hofvander' and sid=='5081-14' else ''};points.append(point);plotrows.append(point)
  ck(ds+group+':point_n',len(points)==n);summary=result['EMC' if group=='EMC' else 'comparator'];ck(ds+group+':frozen_n',summary['finite_n']==n and summary['missing_n']==0);groups.append({'name':group,'points':points,'frozen_median':summary['median'],'n':n})
 panels.append({'dataset':ds,'unit':unit,'groups':groups,'scale':'log10 display of originalTPM' if ds=='Hofvander' else 'depositedRMAlog2'})
ck('all49points',len(plotrows)==49);ck('unique49sourcekeys',len({(r['dataset'],r['condition_id'],r['feature']) for r in plotrows})==49);ck('highLRexact_once',sum(r['highlight']=='LR5081-14' for r in plotrows)==1);ck('RNA_log_positive',all(float(r['value_lexeme'])>0 for r in plotrows if r['dataset']=='Hofvander'))
with open(P/'PLOT-DATA.tsv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['panel','dataset','group','condition_id','source_label','feature','highlight','unit','value_lexeme'],delimiter='\t');w.writeheader();w.writerows(plotrows)
(P/'PLOT-SPECIFICATION.json').write_text(json.dumps({'panels':panels,'no_new_estimates':True,'source_medians_only':True,'total_points':49},indent=2)+'\n')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,'axes.labelsize':10,'svg.hashsalt':'GPNMB-Stage12-all49','axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,2,figsize=(8.3,4.6),layout='constrained');colors={'EMC':'#376B8D','LGFMS':'#C67A28'}
for ax,panel,letter,title in zip(axes,panels,['A','B'],['Hofvander RNA sequencing','GSE24369 microarray']):
 for xi,group in enumerate(panel['groups']):
  n=group['n']
  for k,r in enumerate(group['points']):
   offset=0 if n==1 else -.12+.24*k/(n-1);y=float(r['value_lexeme']);marked=bool(r['highlight']);ax.scatter(xi+offset,y,s=58 if marked else 34,marker='D' if marked else 'o',color=colors[group['name']],edgecolor='#202020' if marked else 'white',linewidth=.85 if marked else .45,zorder=3)
   if marked:ax.annotate('LR5081-14',(xi+offset,y),xytext=(-.18,455),ha='left',va='center',fontsize=9,arrowprops={'arrowstyle':'-','color':'#303030','lw':.8})
  ax.plot([xi-.22,xi+.22],[group['frozen_median']]*2,color='#202020',lw=2,zorder=2)
 ax.set_xticks([0,1],[f"{g['name']}\nn = {g['n']}" for g in panel['groups']]);ax.set_xlim(-.35,1.35);ax.set_title(title,pad=12);ax.text(-.14,1.04,letter,transform=ax.transAxes,fontweight='bold',fontsize=13);ax.grid(axis='y',color='#e0e0e0',lw=.55,zorder=0)
 if panel['dataset']=='Hofvander':ax.set_yscale('log',base=10);ax.set_ylim(1.5,650);ax.yaxis.set_major_locator(FixedLocator([2,5,10,20,50,100,200,500]));ax.yaxis.set_major_formatter(FuncFormatter(lambda v,pos:f'{v:g}'));ax.set_ylabel('GPNMB RNA (TPM; log10 axis)')
 else:ax.set_ylim(5.2,11.8);ax.set_ylabel('GPNMB signal (RMA log2)')
fig.suptitle('GPNMB RNA in native EMC and LGFMS',fontsize=13)
fig.savefig(P/'GPNMB-CORE-EVIDENCE.svg',metadata={'Date':None,'Creator':'Committed Stage12 GPNMB source measurements; post-outcome illustration'})
(P/'preview').mkdir(exist_ok=True);fig.savefig(P/'preview/GPNMB-CORE-EVIDENCE.png',dpi=180);plt.close(fig)
(P/'SOURCE-BINDINGS.json').write_text(json.dumps({'sources':bindings,'source_replay_scope':'49 exact authorized oldcells only, not raw matrix/genome/sourcebody access','original_values_unchanged':True},indent=2)+'\n')
(P/'VALIDATION.json').write_text(json.dumps({'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'n_checks':len(checks),'failed_checks':[x for x in checks if not x['pass']],'checks':checks,'point_counts':{'Hofvander_EMC':13,'Hofvander_LGFMS':13,'GSE24369_EMC':6,'GSE24369_LGFMS':17},'total_rendered_specimen_markers':49,'median_bars':4,'new_statistics':0,'status':'PASS'},indent=2)+'\n')
print(json.dumps({'checks':len(checks),'points':len(plotrows),'svg':str((P/'GPNMB-CORE-EVIDENCE.svg').resolve()),'preview':str((P/'preview/GPNMB-CORE-EVIDENCE.png').resolve())}))
