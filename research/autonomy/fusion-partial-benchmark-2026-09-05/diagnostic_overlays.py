from pathlib import Path
from PIL import Image,ImageDraw
import json
root=Path(__file__).resolve().parent
c=json.loads((root/'extraction-coordinates.json').read_text())
for s in c['screens']:
 im=Image.open(root/'inspections'/s['image']).convert('RGB').resize(tuple(v*2 for v in Image.open(root/'inspections'/s['image']).size));d=ImageDraw.Draw(im)
 for b in s['bars']:
  x=b['x_center']*2;y=b['y_mean'];cap=b['y_sd_upper'];col='red' if b['endpoint']=='fusion' else 'magenta'
  if y is None:d.text((x-3,40),'censored',fill='red');continue
  d.line((x-7,y*2,x+7,y*2),fill=col,width=2)
  d.line((x-7,cap*2,x+7,cap*2),fill='orange',width=2)
  d.text((x-3,s['axis_ticks'][0]['y']*2-18),str(b['design_number']),fill=col)
 im.save(root/'inspections'/f"{s['target']}-coordinate-overlay.png")
for a in json.loads((root/'analysis.json').read_text())['associations']:
 print(a['target'],a['endpoint'],a['feature'],round(a['spearman_remaining'],3),[(x['ambiguous_order_pairs'],round(x['sampled_rho_min'],3),round(x['sampled_rho_max'],3)) for x in a['sensitivity']])
