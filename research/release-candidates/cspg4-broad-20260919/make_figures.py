"""Plot retained exact values; no inferential recomputation. Commit before execution."""
from pathlib import Path
from collections import defaultdict
import csv, hashlib, json, math
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
        text(d,15,y-3,label,11.4,bold=emc);text(d,363,y-3,r['n'],11.4,'end');text(d,938,y-3,f"{float(r['median_TPM']):.2f}",11.4,'end',bold=emc)
        for sid,v in samples[r['original_diagnosis']]:
            jitter=((int(hashlib.sha256(sid.encode()).hexdigest()[:8],16)%1001)/1000-.5)*7
            d.add(Circle(pos(v),y+jitter,1.75,strokeColor=None,fillColor=colors.HexColor('#be6980' if emc else '#89aab7')))
        line(d,pos(float(r['q1_TPM'])),y,pos(float(r['q3_TPM'])),y,col,2.5)
        xm=pos(float(r['median_TPM']));line(d,xm,y-5,xm,y+5,col,1.7)
    text(d,(x0+x1)/2,11,'CSPG4 TPM  (log2[1 + TPM] spacing)',10.5,'middle')
    save(d,n)
atlas([r for r in rows if int(r['reference_n'])>0 or r['original_diagnosis']=='Extraskeletal myxoid chondrosarcoma'],'figure-1','CSPG4 RNA in EMC and the defined malignant reference')
atlas([r for r in rows if not (int(r['reference_n'])>0 or r['original_diagnosis']=='Extraskeletal myxoid chondrosarcoma')],'figure-S1','CSPG4 RNA in the other eligible tumor contexts')
lms=read('external-LMS-reference.csv'); cols=sorted({(r['resource'],r['cohort']) for r in lms}); diagnoses=sorted({r['diagnosis'] for r in lms})
short={'malignant peripheral nerve sheath tumor':'Malignant peripheral nerve sheath tumor','undifferentiated pleomorphic sarcoma':'Undifferentiated pleomorphic sarcoma','dermatofibrosarcoma protuberans':'Dermatofibrosarcoma protuberans'}
display={}
for resource,cohort in cols:
    if resource=='Treehouse25.01': display[(resource,cohort)]='TH '+('TCGA' if 'TCGA' in cohort else next((p for p in cohort.split('|') if p.startswith('SRP')),cohort))
    elif resource=='Boudin2022':display[(resource,cohort)]='B '+cohort
    else:display[(resource,cohort)]=resource
cell=47; left=353;bottom=75;step=18;h=bottom+len(diagnoses)*step+150;d=Drawing(950,h)
d.add(Rect(0,0,950,h,fillColor=colors.white,strokeColor=None))
text(d,15,h-22,'Within-source CSPG4 ordering against leiomyosarcoma',14,bold=True)
text(d,15,h-43,'A = probability of higher expression than LMS, with half-weight for ties',11)
for j,c in enumerate(cols):
    x=left+j*cell
    group=Group(String(0,0,display[c],fontName='Helvetica',fontSize=10.5,fillColor=colors.HexColor('#20262d')))
    angle=math.pi/4;group.transform=(math.cos(angle),math.sin(angle),-math.sin(angle),math.cos(angle),x+8,h-140);d.add(group)
lookup={(r['diagnosis'],r['resource'],r['cohort']):r for r in lms}
def color(a):
    # blue below LMS, white at 0.5, rust above LMS; symmetric perceptual cue.
    target=(39,106,140) if a<.5 else (174,61,60);t=abs(2*a-1)
    return colors.Color(*[(246*(1-t)+v*t)/255 for v in target])
for i,diag in enumerate(diagnoses):
    y=bottom+(len(diagnoses)-1-i)*step
    text(d,15,y+5,short.get(diag,diag[0].upper()+diag[1:]),11.4)
    for j,c in enumerate(cols):
        x=left+j*cell;r=lookup.get((diag,*c));v=float(r['A_type_above_LMS']) if r else None
        d.add(Rect(x,y,cell-2,step-1,fillColor=colors.HexColor('#eeeeee') if v is None else color(v),strokeColor=None))
        if r:text(d,x+(cell-2)/2,y+4,f'{v:.2f}',10.3,'middle','#ffffff' if abs(v-.5)>.29 else '#20262d')
for j in range(100):d.add(Rect(left+j*2.2,38,2.3,10,fillColor=color(j/99),strokeColor=None))
for a in [0,.5,1]:text(d,left+a*220,24,str(a),9.7,'middle')
text(d,left+245,38,'Blank: fewer than 5 profiles in either group',10)
text(d,15,7,'B = published Boudin cohort; TH = Treehouse source. Each column is a separate comparison.',10)
save(d,'figure-2')
manifest={'inputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in I.glob('*.csv')},'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in O.iterdir() if p.suffix in ['.svg','.pdf']},'malignant_categories':29,'other_categories':31,'LMS_cells':len(lms),'LMS_columns':len(cols),'LMS_diagnoses':len(diagnoses),'note':'Visual presentation only; accepted source values and statistics unchanged.'}
(O/'FIGURE-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest))
