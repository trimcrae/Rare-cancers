"""Reproduce tables and descriptive associations. Default verifies retained bytes read-only.
Run --write to regenerate derived outputs inside this directory; never modifies frozen inputs.
Python 3 standard library plus pypdfium2 (table text extraction) and PIL (diagnostic overlays).
"""
from pathlib import Path
import json,csv,io,re,math,random,hashlib,argparse
import pypdfium2 as pdfium
ROOT=Path(__file__).resolve().parent

def dump(v):return (json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode('utf-8')
def ranks(v):
 order=sorted(range(len(v)),key=v.__getitem__);r=[0.]*len(v);i=0
 while i<len(v):
  j=i+1
  while j<len(v) and v[order[j]]==v[order[i]]:j+=1
  for k in order[i:j]:r[k]=(i+j-1)/2+1
  i=j
 return r

def corr(a,b):
 ar=ranks(a);br=ranks(b);am=sum(ar)/len(ar);bm=sum(br)/len(br)
 av=sum((x-am)**2 for x in ar);bv=sum((y-bm)**2 for y in br)
 return sum((x-am)*(y-bm) for x,y in zip(ar,br))/math.sqrt(av*bv) if av*bv else None

def csvbytes(rows):
 s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);return s.getvalue().encode('utf-8')

def build():
 manifest=json.loads((ROOT/'inputs/input-manifest.json').read_text())
 for item in manifest['sources']+manifest['members']:
  b=(ROOT/'inputs'/item['file']).read_bytes();assert len(b)==item['bytes'] and hashlib.sha256(b).hexdigest()==item['sha256']
 freeze=json.loads((ROOT/'protocol-freeze.json').read_text());original=(ROOT/'integration-original-protocol.md.txt').read_bytes();assert hashlib.sha256(original).hexdigest()==freeze['sha256'];assert original.split(b'---',2)[2]==(ROOT/'protocol.md').read_bytes().split(b'---',2)[2]
 designs=[]
 for target,n,expected in [('B4N',1,15),('SS',2,16)]:
  name=f'crt-2022-910-Supplementary-Table-{n}.pdf';d=pdfium.PdfDocument(ROOT/'inputs'/name)
  text=d[0].get_textpage().get_text_range()
  matches=re.findall(r'(B4N|SS) siRNA #(\d+)\s+([ACGU]+)\s*(tt)\s+([ACGU]+)(tt)',text)
  assert len(matches)==expected
  for prefix,num,s,ov,a,ov2 in matches:
   assert len(s)==len(a)==19 and s.translate(str.maketrans('ACGU','UGCA'))[::-1]==a
   designs.append({'design_id':f'{target}_{int(num):02d}','target':target,'design_number':int(num),'source_label':f'{prefix} siRNA #{num}','sense_5to3_printed':s+ov,'antisense_5to3_printed':a+ov2,'sense_core_5to3':s,'antisense_core_5to3':a,'core_length_nt':19,'overhang':'3-prime dTdT on both strands (methods); lowercase tt in tables','other_chemistry':'not specified for screening duplexes; not assigned Accell in-vivo chemistry','sequence_source':name,'sequence_source_page':1,'gc_fraction':sum(b in 'GC' for b in a)/19,'terminal_gc_asymmetry':(sum(b in 'GC' for b in a[-4:])-sum(b in 'GC' for b in a[:4]))/4,'junction_score':None,'junction_score_status':'not evaluated: no fully verified exact source breakpoint/alignment for both series'})
 assert len(designs)==31
 coords=json.loads((ROOT/'extraction-coordinates.json').read_text());outcomes=[]
 for screen in coords['screens']:
  target=screen['target'];axis=screen['axis_ticks'];y0=axis[0]['y'];ppu=(y0-axis[1]['y'])/axis[1]['value'];hw=screen['mean_reading_halfwidth_px']/ppu
  for bar in screen['bars']:
   y=bar['y_mean'];mean=(y0-y)/ppu if y is not None else None;sd=(y-bar['y_sd_upper'])/ppu if y is not None else None
   outcomes.append({'design_id':f"{target}_{bar['design_number']:02d}",'target':target,'endpoint':bar['endpoint'],'transcript':('BRD4-NUTM1' if target=='B4N' else 'SS18-SSX1') if bar['endpoint']=='fusion' else ('BRD4' if target=='B4N' else 'SS18'),'cell_line':'HCC2429' if target=='B4N' else 'HS-SY-II','dose_nM':50,'time_h':72,'assay':'qRT-PCR','relative_expression_mean':mean,'reading_low':mean-hw if mean is not None else coords['censoring']['conservative_lower_bound'],'reading_high':mean+hw if mean is not None else None,'suppression_index_1_minus_mean':1-mean if mean is not None else None,'plotted_SD':sd,'SD_reading_low':max(0,sd-screen['sd_reading_halfwidth_px']/ppu) if sd is not None else None,'SD_reading_high':sd+screen['sd_reading_halfwidth_px']/ppu if sd is not None else None,'reported_n':3,'replicate_type':'triplicates; biological versus technical identity not resolved','status':bar['status'],'source_pdf':screen['pdf'],'source_page':1,'source_panel':screen['panel'],'source_image':screen['image'],'x_native_px':bar['x_center'],'y_mean_native_px':y,'y_SD_upper_native_px':bar['y_sd_upper'],'normalization_note':'S5 caption: average Ct value relative to NC; axis says relative mRNA expression. Main Fig2 caption names GUSB internal control. Exact Ct transformation not reported.' if target=='B4N' else 'S6 caption names GUSB internal control; NC plotted near 1. Exact Ct transformation not reported.'})
  for des in [d for d in designs if d['target']==target]:
   missing={key:None for key in outcomes[0]};missing.update(design_id=des['design_id'],target=target,endpoint='second_parent',transcript='NUTM1' if target=='B4N' else 'SSX1',status='not_reported_in_screen',normalization_note='A primer listing does not establish a measured outcome. No second-parent bar in retained qPCR screen.')
   outcomes.append(missing)
 results=[]
 for target in ['B4N','SS']:
  for endpoint in ['fusion','measured_parent']:
   rows=[r for r in outcomes if r['target']==target and r['endpoint']==endpoint and r['relative_expression_mean'] is not None]
   ds={d['design_id']:d for d in designs};y=[r['relative_expression_mean'] for r in rows]
   for feature in ['gc_fraction','terminal_gc_asymmetry']:
    x=[ds[r['design_id']][feature] for r in rows];c=corr(x,y);sens=[]
    for mult in [1,2]:
     rng=random.Random(20260905);vals=[];amb=0
     hw=[(r['reading_high']-r['reading_low'])/2*mult for r in rows]
     for i in range(len(y)):
      for j in range(i):amb+=abs(y[i]-y[j])<=hw[i]+hw[j]
     for _ in range(10000):vals.append(corr(x,[rng.uniform(v-h,v+h) for v,h in zip(y,hw)]))
     sens.append({'reading_halfwidth_multiplier':mult,'ambiguous_order_pairs':amb,'all_pairs':len(y)*(len(y)-1)//2,'sampled_rho_min':min(vals),'sampled_rho_max':max(vals),'draws':10000,'seed':20260905,'interpretation':'Observed simulation range under independent uniform reading perturbations; not a confidence interval or exhaustive bound.'})
    results.append({'target':target,'endpoint':endpoint,'feature':feature,'n_quantitative_designs':len(rows),'n_disclosed_designs':15 if target=='B4N' else 16,'min_relative_expression':min(y),'max_relative_expression':max(y),'spearman_remaining':c,'spearman_suppression_index':-c if c is not None else None,'sensitivity':sens})
 metadata={'study':'Lee et al. 2023','doi':'10.4143/crt.2022.910','pmcid':'PMC10101799','scope':'Retrospective partial-outcome within-study siRNA benchmark; no both-parent/ASO/clinical validation','license':'XML states CC BY-NC 4.0, copyright 2023 Korean Cancer Association; retained for non-commercial attributed research','feature_specification':'protocol.md','extraction_specification':'extraction-coordinates.json','source_manifest':'inputs/input-manifest.json','coverage':{'designs':31,'fusion_means':31,'measured_parent_means':30,'measured_parent_ceiling_censored':1,'second_parent_unknown':31},'uncertainty':'Image-reading ranges and plotted SD are different quantities. No raw replicates or confidence intervals recovered.'}
 return {'designs.csv':csvbytes(designs),'outcomes.csv':csvbytes(outcomes),'dataset.json':dump({'metadata':metadata,'designs':designs,'outcomes':outcomes}),'analysis.json':dump({'metadata':metadata,'associations':results})}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();products=build()
 for name,b in products.items():
  if args.write:(ROOT/name).write_bytes(b)
  else:assert (ROOT/name).read_bytes()==b,f'Reproduction mismatch: {name}'
 print(json.dumps({'mode':'write' if args.write else 'read-only verification','verified_sources':9,'protocol_digest':'passed','duplexes':31,'reverse_complements':'31 passed','outcome_rows':93,'means':61,'products':{n:hashlib.sha256(b).hexdigest() for n,b in products.items()}},indent=2))
if __name__=='__main__':main()
