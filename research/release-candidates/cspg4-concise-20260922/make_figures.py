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
    step=13.3; h=124+step*len(selected);d=Drawing(950,h)
    d.add(Rect(0,0,950,h,fillColor=colors.white,strokeColor=None))
    x0=385;x1=857;top=h-82
    text(d,15,h-20,title,14,bold=True)
    text(d,15,h-67,'Original diagnosis',10,bold=True);text(d,363,h-67,'n',10,anchor='end',bold=True);text(d,938,h-67,'Median TPM',10,anchor='end',bold=True)
    text(d,15,h-38,'* Source-classified Intermediate categories; included in the broader 489-specimen reference.',10.8)
    text(d,15,h-52,'Other non-EMC rows form the 393-specimen Malignant-category reference. EMC is highlighted.',10.8)
    maximum=max(float(r['max_TPM']) for r in selected);maxlog=math.ceil(math.log2(maximum+1))
    def pos(v):return x0+(x1-x0)*math.log2(v+1)/maxlog
    for k in range(0,maxlog+1,2):
        x=x0+(x1-x0)*k/maxlog;line(d,x,45,x,top+6,'#e1e6eb');text(d,x,30,str(2**k-1),9.7,'middle')
    for i,r in enumerate(selected):
        y=top-i*step;emc=r['original_diagnosis']=='Extraskeletal myxoid chondrosarcoma'; col='#111111' if emc else '#333333'
        if emc:d.add(Rect(9,y-7,932,step,fillColor=colors.HexColor('#e8e8e8'),strokeColor=None))
        label=name(r['original_diagnosis'])
        if len(label)>60:
            # One source-defined combined label; full wording remains in Table S3.
            if 'Myxoinflammatory' in label or 'Hem' in label:label='MIFS / HFLT'
        if r['source_class']=='Intermediate':label+=' *'
        text(d,15,y-3,label,11.1,bold=emc,color=col);text(d,363,y-3,r['n'],11.4,'end');text(d,938,y-3,f"{median([Decimal(str(v)) for _,v in samples[r['original_diagnosis']]]):.2f}",11.4,'end',bold=emc)
        for sid,v in samples[r['original_diagnosis']]:
            jitter=((int(hashlib.sha256(sid.encode()).hexdigest()[:8],16)%1001)/1000-.5)*7
            d.add(Circle(pos(v),y+jitter,1.75,strokeColor=None,fillColor=colors.HexColor('#555555' if emc else '#aaaaaa')))
        line(d,pos(float(r['q1_TPM'])),y,pos(float(r['q3_TPM'])),y,col,2.5)
        xm=pos(float(r['median_TPM']));line(d,xm,y-5,xm,y+5,col,1.7)
    text(d,(x0+x1)/2,11,'CSPG4 TPM  (log2[1 + TPM] spacing)',10.5,'middle')
    save(d,n)

selected=[r for r in rows if r['source_class'] in {'Malignant','Intermediate'} and r['original_diagnosis'] not in {'Melanoma','Spindle cell tumor NOS'}]
assert len(selected)==38 and sum(int(r['n']) for r in selected)==498
atlas(selected,'figure-1','CSPG4 RNA across sarcoma and related tumor categories')
comparisons=[('LGFMS',17,13,.9658119658119658),('MFS',6,60,.8537037037037037),('SFT',5,11,.8787878787878788),('Desmoid',6,11,1.)]
d=Drawing(950,390);d.add(Rect(0,0,950,390,fillColor=colors.white,strokeColor=None))
text(d,15,365,'Direct EMC contrasts shared across RNA sequencing and arrays',17,bold=True)
text(d,15,341,'A = probability of higher EMC expression, with half-weight for ties',12)
text(d,15,305,'Comparator',12,bold=True);text(d,672,305,'RNA sequencing',12,bold=True);text(d,830,305,'Arrays',12,bold=True)
text(d,672,286,'EMC / reference n; A',10.5);text(d,830,286,'EMC / reference n; A',10.5)
x0=190;x1=610
for a in [.5,.6,.7,.8,.9,1.]:
 x=x0+(x1-x0)*(a-.5)/.5;line(d,x,85,x,273,'#e1e6eb');text(d,x,67,f'{a:.1f}',11,'middle')
for i,(label,na,nh,a) in enumerate(comparisons):
 y=255-i*50;text(d,15,y-4,label,14,bold=True)
 xx=x0+(x1-x0)*(a-.5)/.5
 d.add(Circle(xx,y+5,4,fillColor=colors.HexColor('#333333'),strokeColor=None))
 d.add(Rect(x1-4,y-13,8,8,fillColor=colors.HexColor('#777777'),strokeColor=None))
 text(d,672,y-4,f'9 / {nh}; {a:.3f}',12);text(d,830,y-4,f'6 / {na}; 1.000',12)
text(d,(x0+x1)/2,43,'Within-source probability-of-superiority A',12,'middle')
d.add(Circle(20,18,4,fillColor=colors.HexColor('#333333'),strokeColor=None));text(d,33,14,'Hofvander RNA sequencing',11)
d.add(Rect(315,14,8,8,fillColor=colors.HexColor('#777777'),strokeColor=None));text(d,334,14,'GSE24369 arrays',11)

save(d,'figure-2')
manifest={'inputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in I.glob('*.csv')},'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in O.iterdir() if p.suffix in ['.svg','.pdf']},'figure1_labels':38,'figure1_specimens':498,'figure2_shared_comparisons':comparisons,'note':'Source measurements unchanged; newly computed sensitivity/intervals are separately supplied. Supplemental figures retained from accepted inputs.'}
(O/'FIGURE-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'figure1_labels':38,'figure1_n':498,'figure2_rows':4}))
