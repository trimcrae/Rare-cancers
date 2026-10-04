from pathlib import Path
import json,re,hashlib
import html
def clean(x):return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',x))).strip()
P=Path(__file__).resolve().parent
for name in ('zullow2022','filion2009'):
    f=P/(name+'.html');s=f.read_text(encoding='utf-8')
    text=clean(s)
    (P/(name+'-text.txt')).write_text(text,encoding='utf-8')
    chunks=[clean(x) for x in re.findall(r'<(?:p|table)\b.*?</(?:p|table)>',s,re.S)]
    hits=[x for x in chunks if re.search('chondrosarcoma|EMC|RNA-seq|Table S1|adipogen|endogenous|data avail|deidentified',x,re.I)]
    links=[{'text':clean(a),'href':h} for h,a in re.findall(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>',s,re.S) if re.search(r'supp|mmc|NIHMS|GSE',h+' '+a,re.I)]
    (P/(name+'-source-evaluation.json')).write_text(json.dumps({'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'paragraphs':hits,'source_links':links},indent=2),encoding='utf-8')
    print(name,json.dumps({'paragraphs':hits,'source_links':links},ensure_ascii=False)[:17000])
