"""Extract embedded raster images and audit object types, without altering source PDFs."""
from pathlib import Path
import pypdfium2 as p,json
from collections import Counter
root=Path(__file__).resolve().parent;rec=[]
for n in ['2','3']:
 d=p.PdfDocument(root/f'inputs/crt-2022-910-Supplementary-Fig-{n}.pdf')
 for i,page in enumerate(d):
  obs=list(page.get_objects());r={'file':f'crt-2022-910-Supplementary-Fig-{n}.pdf','page':i+1,'object_types':dict(Counter(o.type for o in obs)),'images':[]}
  for j,o in enumerate(obs):
   if o.type==3:
    name=f'Fig-{n}-p{i+1}-image{j}.png';o.get_bitmap().to_pil().save(root/'inspections'/name)
    r['images'].append({'object_index':j,'bounds_pdf':o.get_bounds(),'pixel_size':o.get_px_size(),'file':name})
  rec.append(r)
(root/'inspections/pdf-object-audit.json').write_text(json.dumps(rec,indent=2)+'\n')
