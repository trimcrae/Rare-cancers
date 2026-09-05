from pathlib import Path
from PIL import Image
import json
root=Path('research/autonomy/fusion-partial-benchmark-2026-09-05')
for f,box in [('Fig-2-p1-image24.png',(70,52,1090,357)),('Fig-3-p1-image29.png',(635,41,1470,354))]:
 im=Image.open(root/'inspections'/f).convert('RGB')
 for k in ['parent','fusion']:
  def color(c):
   r,g,b=c
   if f.startswith('Fig-2'):return b>r+20 and b>g+10 and ((r>100) if k=='parent' else (r<100))
   return g>r+8 and g>b+10 and ((r>140) if k=='parent' else (r<140))
  xs=[]
  for x in range(box[0],box[2]):
   if sum(color(im.getpixel((x,y))) for y in range(box[1],box[3]))>=5:xs.append(x)
  groups=[]
  for x in xs:
   if not groups or x>groups[-1][-1]+1:groups.append([x])
   else:groups[-1].append(x)
  bars=[]
  for group in groups:
   if len(group)<4:continue
   xx=group[len(group)//2]; tops=[]
   for x in group[1:-1]:
    yy=[y for y in range(box[1],box[3]) if color(im.getpixel((x,y)))]
    if yy:tops.append(min(yy))
   tops.sort();bars.append({'x_left':group[0],'x_right':group[-1],'x_center':xx,'y_top':tops[len(tops)//2],'top_spread':[min(tops),max(tops)]})
  print(f,k,bars)
