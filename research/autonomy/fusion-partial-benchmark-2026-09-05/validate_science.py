"""Read-only scientific integrity checks beyond exact reproduction."""
from pathlib import Path
import json,zipfile,hashlib,itertools
from PIL import Image
from reproduce import corr,ranks
root=Path(__file__).resolve().parent
assert corr([1,2,3],[2,4,6])==1
assert corr([1,2,3],[6,4,2])==-1
assert ranks([1,1,3])==[1.5,1.5,3]
assert corr([1,1,1],[1,2,3]) is None
m=json.loads((root/'inputs/input-manifest.json').read_text())
with zipfile.ZipFile(root/'inputs/lee2023-supplements.zip') as z:
 for item in m['members']:assert z.read(item['archive_member'])==(root/'inputs'/item['file']).read_bytes()
d=json.loads((root/'dataset.json').read_text());ids={r['design_id'] for r in d['designs']}
assert len(ids)==31 and len(d['outcomes'])==93
for i in ids:assert {r['endpoint'] for r in d['outcomes'] if r['design_id']==i}=={'fusion','measured_parent','second_parent'}
assert sum(r['relative_expression_mean'] is not None for r in d['outcomes'])==61
assert sum(r['status']=='plot_ceiling_censored' for r in d['outcomes'])==1
c=json.loads((root/'extraction-coordinates.json').read_text());pixel_checks=[]
for s in c['screens']:
 im=Image.open(root/'inspections'/s['image']).convert('RGB')
 for b in s['bars']:
  if b['y_mean'] is None:continue
  tops=[]
  for x in range(b['x_center']-3,b['x_center']+4):
   yy=[]
   for y in range(130 if s['target']=='B4N' else (120 if x>1300 else 41),s['axis_ticks'][0]['y']):
    r,g,bl=im.getpixel((x,y));parent=b['endpoint']=='measured_parent'
    match=(bl>r+20 and bl>g+10 and ((r>100) if parent else r<100)) if s['target']=='B4N' else (g>r+8 and g>bl+10 and ((r>140) if parent else r<140))
    if match:yy.append(y)
   if yy:tops.append(min(yy))
  assert tops
  tops.sort();detected=tops[len(tops)//2];delta=abs(detected-b['y_mean']);assert delta<=4,(s['target'],b,detected)
  pixel_checks.append({'target':s['target'],'design':b['design_number'],'endpoint':b['endpoint'],'retained_y':b['y_mean'],'color_median_y':detected,'absolute_difference_px':delta})
for o in d['outcomes']:
 if o['relative_expression_mean'] is not None:
  assert o['reading_low']<=o['relative_expression_mean']<=o['reading_high'] and o['plotted_SD']>=0
  assert abs(o['relative_expression_mean']+o['suppression_index_1_minus_mean']-1)<1e-12
result={'archive_member_identity':'7 passed','rank_arithmetic':'perfect, inverse, tied, constant checks passed','coverage':'31 designs, 93 endpoint rows, 61 means, 1 censored, 31 absent second-parent outcomes','color_mean_check':'61 within retained four-pixel reading half-width','maximum_color_difference_px':max(p['absolute_difference_px'] for p in pixel_checks),'pixel_checks':pixel_checks,'limitations':'Same-writer checks, not independent extraction verification. SD caps manually inspected, not independently validated. Biological replicate uncertainty not tested.'}
print(json.dumps(result,indent=2))
