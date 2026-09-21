"""Plot retained exact values; no inferential recomputation. Commit before execution."""
from pathlib import Path
from collections import defaultdict
import csv, hashlib, json, math
from decimal import Decimal
from statistics import median
from reportlab.graphics.shapes import Drawing, String, Line, Rect, Circle, Group
from reportlab.graphics import renderSVG, renderPDF
from reportlab.lib import colors
W=Path(__file__).resolve().parent
I=W/'figure-inputs'; O=W/'figures'; O.mkdir(exist_ok=True)
def read(n):return list(csv.DictReader((I/n).open(encoding='utf8')))
def text(d,x,y,s,size=10.6,anchor='start',color='#20262d',bold=False):
    d.add(String(x,y,s,fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=size,textAnchor=anchor,fillColor=colors.HexColor(color)))
def line(d,x,y,x2,y2,color='#c9d0d6',width=0.5):d.add(Line(x,y,x2,y2,strokeColor=colors.HexColor(color),strokeWidth=width))
def save(d,n):
    renderSVG.drawToFile(d,str(O/(n+'.svg'))); renderPDF.drawToFile(d,str(O/(n+'.pdf')))
    p=O/(n+'.svg');p.write_text(p.read_text().replace('font-family: Helvetica;', 'font-family: Arial;').replace('font-family: Helvetica-Bold;', 'font-family: Arial; font-weight: bold;'),encoding='utf8')
def name(s):
    return {'Extraskeletal myxoid chondrosarcoma':'Extraskeletal myxoid chondrosarcoma (EMC)',
    'Myxoinflammatory fibroblastic sarcoma/Hemosiderotic fibrolipomatous tumor':'MIFS / HFLT',
    'Myxoinflammatory fibroblastic sarcoma / Hemosiderotic fibrolipomatous tumor':'MIFS / HFLT'}.get(s,s)
samples=defaultdict(list)
for r in read('selected-panel-values.csv'):samples[r['original_diagnosis']].append((r['sample_id'],float(r['CSPG4_TPM'])))
rows=read('CSPG4-by-type.csv')
def atlas(selected,n,title):
    selected=sorted(selected,key=lambda r:float(r['median_TPM']),reverse=True)
    step=15.7; h=104+step*len(selected);d=Drawing(950,h)
    d.add(Rect(0,0,950,h,fillColor=colors.white,strokeColor=None))
    x0=385;x1=857;top=h-56
    text(d,15,h-20,title,14,bold=True)
    text(d,15,h-39,'Original diagnosis',10,bold=True);text(d,363,h-39,'n',10,anchor='end',bold=True);text(d,938,h-39,'Median TPM',10,anchor='end',bold=True)
    maximum=max(float(r['max_TPM']) for r in selected);maxlog=math.ceil(math.log2(maximum+1))
    def pos(v):return x0+(x1-x0)*math.log2(v+1)/maxlog
    for k in range(0,maxlog+1,2):
        x=x0+(x1-x0)*k/maxlog;line(d,x,45,x,top+6,'#e1e6eb');text(d,x,30,str(2**k-1),9.7,'middle')
    for i,r in enumerate(selected):
        y=top-i*step;emc=r['original_diagnosis']=='Extraskeletal myxoid chondrosarcoma'; col='#9c2d49' if emc else '#1d647d'
        if emc:d.add(Rect(9,y-7,932,step,fillColor=colors.HexColor('#fbeaf0'),strokeColor=None))
        label=name(r['original_diagnosis'])
        if len(label)>60:
            # One source-defined combined label; full wording remains in Table S3.
            if 'Myxoinflammatory' in label or 'Hem' in label:label='MIFS / HFLT'
        text(d,15,y-3,label,11.4,bold=emc);text(d,363,y-3,r['n'],11.4,'end');text(d,938,y-3,f"{median([Decimal(str(v)) for _,v in samples[r['original_diagnosis']]]):.2f}",11.4,'end',bold=emc)
        for sid,v in samples[r['original_diagnosis']]:
            jitter=((int(hashlib.sha256(sid.encode()).hexdigest()[:8],16)%1001)/1000-.5)*7
            d.add(Circle(pos(v),y+jitter,1.75,strokeColor=None,fillColor=colors.HexColor('#be6980' if emc else '#89aab7')))
        line(d,pos(float(r['q1_TPM'])),y,pos(float(r['q3_TPM'])),y,col,2.5)
        xm=pos(float(r['median_TPM']));line(d,xm,y-5,xm,y+5,col,1.7)
    text(d,(x0+x1)/2,11,'CSPG4 TPM  (log2[1 + TPM] spacing)',10.5,'middle')
    save(d,n)

atlas([r for r in rows if not (int(r['reference_n'])>0 or r['original_diagnosis']=='Extraskeletal myxoid chondrosarcoma')],'figure-S1','CSPG4 RNA in the other eligible tumor contexts')
