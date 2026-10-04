"""Frozen upstream-region pilot; exact Calvin ranges, no raw files saved."""
import concurrent.futures
import csv
import gzip
import hashlib
import json
from pathlib import Path
import struct
import sys
import urllib.request
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
sys.path.insert(0,str(ROOT/'.cache/python-deps'))
import numpy as np
import scipy.stats as st

class Calvin:
 def __init__(self,url):self.url=url;self.ranges=[];self.total=0;self.filesize=None
 def read(self,start,n):
  if self.filesize is not None:n=min(n,self.filesize-start)
  assert 0<n<=5_000_000
  req=urllib.request.Request(self.url,headers={'Range':f'bytes={start}-{start+n-1}','Accept-Encoding':'identity'})
  with urllib.request.urlopen(req,timeout=45) as r:
   b=r.read(n+1)
   assert r.status==206 and len(b)==n,(r.status,len(b),n)
   assert r.headers.get('Content-Range','').startswith(f'bytes {start}-{start+n-1}/')
   self.filesize=int(r.headers['Content-Range'].split('/')[-1])
  self.ranges.append({'start':start,'bytes':n,'sha256':hashlib.sha256(b).hexdigest()})
  self.total+=n
  return b
class B:
 def __init__(self,b):self.b=b;self.p=0
 def num(self,f):
  x=struct.unpack_from('>'+f,self.b,self.p)[0];self.p+=struct.calcsize('>'+f);return x
 def s(self,wide=False):
  n=self.num('i');assert 0<=n<1_000_000
  v=self.b[self.p:self.p+n*(2 if wide else 1)];self.p+=len(v)
  return v.decode('utf-16-be' if wide else 'utf8')
 def params(self):
  out={}
  for _ in range(self.num('i')):
   k=self.s(True);n=self.num('i');v=self.b[self.p:self.p+n];self.p+=n;t=self.s(True)
   out[k]={'type':t,'hex':v.hex()}
  return out
 def generic(self):
  q={'type':self.s(),'id':self.s(),'date':self.s(True),'locale':self.s(True),'parameters':self.params()}
  q['parents']=[self.generic() for _ in range(self.num('i'))]
  return q
def headers(c):
 h=B(c.read(0,65536));magic=h.num('B');version=h.num('B');ng=h.num('i');gp=h.num('I')
 assert (magic,version)==(59,1)
 g=h.generic();groups=[]
 for _ in range(ng):
  h=B(c.read(gp,4096));gp=h.num('I');sp=h.num('I');ns=h.num('i');name=h.s(True);datasets=[]
  for _ in range(ns):
   h=B(c.read(sp,4096));dp=h.num('I');sp=h.num('I');sn=h.s(True);pa=h.params();cols=[]
   for _ in range(h.num('I')):cols.append({'name':h.s(True),'type':h.num('B'),'size':h.num('i')})
   nr=h.num('I');datasets.append({'name':sn,'data_offset':dp,'rows':nr,'columns':cols,'parameters':pa})
  groups.append({'name':name,'datasets':datasets})
 return {'type':g['type'],'parameters':{k:v for k,v in g['parameters'].items() if k in ['affymetrix-cel-rows','affymetrix-cel-cols']},'groups':groups}

mp=BASE/'probe-map.csv'
rows=list(csv.DictReader(mp.open()))
for r in rows:
 for k in r:
  if k!='sequence':r[k]=int(r[k])
targets=[r['physical_probe_id'] for r in rows]
assert all(r['physical_probe_id']==r['x']+1050*r['y']+1 for r in rows)
# Frozen before intensities; manufacturer annotation deduplicated physical IDs.
control_ids=[
[1041549,809915,468140,455109,930652,437681,57715,697856,16735,103152],
[113366,632492,10175,29022,420365,259740,707597,506586,744106,1037913],
[760840,100564,599754,455171,787712,618633,108183,821554,973259,461748],
[708278,160572,952352,963419,34721,516967,207639,474931,1074082,801887],
[839895,30517,746280,956305,254958,363134,417743,197832,250685,821269],
[536666,957353,1004887,634259,554919,981198,1040584,1062149,26521,565870],
[923250,131963,275630,823549,591770,281097,625222,181218,214840,1083305],
[30167,987880,10762,394918,670436,222363,193616,330819,47161,483471],
[975477,179542,422471,20765,281334,743789,1007823,266530,110693,744820],
[346943,876562,426350,61266,513146,239016,978168,719886,326497,492326],
[26683,426349,612859,463506,458242,975336,510043,906589,266091,1069590],
[1085970,429539,211109,543860,614219,64192,337304,266827,783698,577631],
[624374,815152,555852,430276,68883,139571,1091182,183788,518219,123777],
[212420,195858,117319,958846,111533,1099385,20000,194888,1053545,930168],
[661518,804781,420561,113279,166539,461189,155575,1027018,1096310,147526],
[985158,582493,939743,629885,97382,463837,884348,192030,225377,839311],
[492961,441946,679451,335347,833468,861660,1037367,284879,390137,931205],
[406269,765150,681961,297282,954058,874969,832318,414645,810485,834405],
[687589,193189,1057338,874362,113303,976434,889497,41423,25454,368716],
[297652,479447,658745,721662,254568,473415,786386,420108,387074,677685],
[645668,373111,423494,879440,145060,888135,584594,825951,479683,703206],
[173216,840255,1015945,507340,901397,1019514,1047406,12742,420488,664626],
[24885,238226,344785,518394,423718,124081,970922,781673,214999,108716],
[453789,1003437,475749,773213,1098569,950163,268837,664451,107815,173421],
[391216,21335,397649,1001683,498155,1008402,981344,108391,836758,237991],
[25744,817661,911347,789443,898290,676880,523098,325073,472138,492110],
[577455,616382,292173,599556,679823,696635,1034660,845680,1032483,1065444],
[910822,765102,649273,908836,756372,69230,670773,508952,748270,148348],
[708592,272284,484915,883383,226572,49079,218888,728933,550119,492665],
[1047654,537934,493835,128173,719544,160496,656309,698937,959510,819442]]
controls=[{'target':r['physical_probe_id'],'gc':r['sequence'].count('G')+r['sequence'].count('C'),'controls':c} for r,c in zip(rows,control_ids)]
assert len(controls)==30 and all(not(set(c['controls'])&set(targets)) for c in controls)
meta_path=ROOT/'research/autonomy/atlas-primary-provenance-2026-09-06/GSE24369.soft.gz'
meta=gzip.open(meta_path,'rt',encoding='utf8').read()
sample_ids=['GSM'+str(i) for i in range(600934,600957)]+['GSM600968','GSM600969']
samples=[]
for block in meta.split('^SAMPLE = ')[1:]:
 lines=block.splitlines();acc=lines[0]
 if acc not in sample_ids:continue
 url=next(l.split(' = ',1)[1] for l in lines if l.startswith('!Sample_supplementary_file = '))
 title=next(l.split(' = ',1)[1] for l in lines if l.startswith('!Sample_title = '))
 file=url.rsplit('/',1)[1][:-3]
 samples.append({'acc':acc,'title':title,'url':'https://ftp.ebi.ac.uk/biostudies/fire/E-GEOD-/369/E-GEOD-24369/Files/'+file})
assert [s['acc'] for s in samples]==sample_ids
assert all('Extraskeletal myxoid chondrosarcoma' in s['title'] for s in samples[:6])
assert all('Low-grade fibromyxoid sarcoma' in s['title'] for s in samples[6:23])

def run(s):
 c=Calvin(s['url']);h=headers(c)
 assert all(int(v['hex'][:8],16)==1050 for v in h['parameters'].values())
 ds={d['name']:d for g in h['groups'] for d in g['datasets']}
 d=ds['Intensity'];assert d['rows']==1102500 and d['columns']==[{'name':'Intensity','type':6,'size':4}]
 b=c.read(d['data_offset'],d['rows']*4)
 a=np.frombuffer(b,dtype='>f4').astype(float);finite=np.isfinite(a);den=int(finite.sum())
 ranks=np.full(len(a),np.nan);ranks[finite]=st.rankdata(a[finite],method='average')/den
 flagsets={};flagcounts={}
 for name in ['Mask','Outlier']:
  d=ds[name];flagcounts[name]=d['rows']
  if d['rows']:
   assert d['columns']==[{'name':'X','type':2,'size':2},{'name':'Y','type':2,'size':2}]
   b=c.read(d['data_offset'],d['rows']*4)
   xy=np.frombuffer(b,dtype='>i2').reshape((-1,2))
   flagsets[name]=set((xy[:,0]+1050*xy[:,1].astype(int)+1).tolist())
  else:flagsets[name]=set()
 selected=[]
 for r,ctrl in zip(rows,controls):
  i=r['physical_probe_id']-1;ci=np.array(ctrl['controls'])-1
  selected.append({'id':i+1,'raw':float(a[i]),'percentile':float(ranks[i]),
    'mask':i+1 in flagsets['Mask'],'outlier':i+1 in flagsets['Outlier'],
    'gc_control_mean_raw':float(a[ci].mean()),'gc_control_mean_percentile':float(ranks[ci].mean())})
 return {**s,'file_size':c.filesize,'bytes_retrieved':c.total,'finite_features':den,
    'nonfinite_features':len(a)-den,'array_quantiles':np.quantile(a[finite],[0,.25,.5,.75,1]).tolist(),
    'flag_counts':flagcounts,'selected':selected,'ranges':c.ranges}

def main():
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:arrays=list(ex.map(run,samples))
 assert sum(a['bytes_retrieved'] for a in arrays)<120000000
 reg=[r['child_probeset'] for r in rows]
 raw=np.array([[p['raw'] for p in a['selected']] for a in arrays])
 percent=np.array([[p['percentile'] for p in a['selected']] for a in arrays])
 log=np.where(raw>0,np.log2(raw),np.nan)
 ctrl=np.array([[p['gc_control_mean_percentile'] for p in a['selected']] for a in arrays])
 def meanregion(m,regions):
  return np.mean([m[:,[i for i,r in enumerate(reg) if r==g]].mean(axis=1) for g in regions],axis=0)
 def A(x,y):
  return float(((x[:,None]>y).sum()+.5*(x[:,None]==y).sum())/(len(x)*len(y)))
 def stat(x):
  return {'EMC':x[:6].tolist(),'LGFMS':x[6:23].tolist(),'muscle':x[23:].tolist(),
     'A':A(x[:6],x[6:23]),'EMC_median':float(np.median(x[:6])),'LGFMS_median':float(np.median(x[6:23]))}
 summary={}
 groups={'upstream':list(range(7985069,7985075)),'downstream':[7985076,7985077,7985078],
         'UTR':[7985067,7985068,7985079],'antisense_shared':[7985075]}
 for name,rs in groups.items():
  summary[name]={'percentile':stat(meanregion(percent,rs)),'log2raw':stat(meanregion(log,rs)),
                 'GC_control_percentile':stat(meanregion(ctrl,rs))}
 summary['strict_current_CDS']={'percentile':stat(meanregion(percent,list(range(7985070,7985075)))),
                               'log2raw':stat(meanregion(log,list(range(7985070,7985075))))}
 for name in ['upstream','strict_current_CDS']:
  x=np.array(summary[name]['percentile']['EMC']);y=np.array(summary[name]['percentile']['LGFMS'])
  rng=np.random.default_rng(20261004)
  boot=[A(rng.choice(x,len(x),replace=True),rng.choice(y,len(y),replace=True)) for _ in range(2000)]
  summary[name]['bootstrap_A95']=np.quantile(boot,[.025,.975]).tolist()
 regionstats={str(g):{'percentile':stat(meanregion(percent,[g])),
                     'log2raw':stat(meanregion(log,[g]))} for g in sorted(set(reg))}
 probe_stats=[{'id':p,'region':reg[i],'percentile':stat(percent[:,i]),'log2raw':stat(log[:,i])} for i,p in enumerate(targets)]
 passed=summary['upstream']['percentile']['A']>=.8 and summary['upstream']['bootstrap_A95'][0]>.5 and sum(regionstats[str(g)]['percentile']['A']>.5 for g in groups['upstream'])>=4
 out={'scope':'Post-discovery reused-cohort upstream RNA-region pilot; no full-length, localization, protein, diagnostic or isoform claim',
      'map_sha256':hashlib.sha256(mp.read_bytes()).hexdigest(),'metadata_sha256':hashlib.sha256(meta_path.read_bytes()).hexdigest(),
      'controls':controls,'arrays':arrays,'summary':summary,'regions':regionstats,'probes':probe_stats,
      'support_rule_pass':bool(passed),'total_bytes_retrieved':sum(a['bytes_retrieved'] for a in arrays),
      'raw_zero_or_negative_count':int((raw<=0).sum())}
 (BASE/'raw-array-results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
 print(json.dumps({'saved':'raw-array-results.json','arrays':len(arrays),'bytes_retrieved':out['total_bytes_retrieved'],
       'upstream_A':summary['upstream']['percentile']['A'],'strict_A':summary['strict_current_CDS']['percentile']['A'],
       'support_rule_pass':bool(passed)}),flush=True)

if __name__=='__main__':main()
