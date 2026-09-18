from pathlib import Path
import json, re, unicodedata, difflib
from hashlib import sha256
from pypdf import PdfReader
OUT=Path(__file__).parent
audit=json.loads((OUT/'FO-INITIAL-EXPORT-AUDIT.json').read_text('utf-8'))
def norm(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',s).replace('\u00ad','').replace('\u200b','').replace('\ufeff',''))
def clean(s):return '\f'.join(re.sub(r'(?m)^\s*'+str(i)+r'\s*\Z','',p) for i,p in enumerate(s.split('\f'),1))
for d in audit['documents']:
    if not d['missing_in_both']:continue
    reader=PdfReader(d['pdf']); page_text=[p.extract_text() or '' for p in reader.pages]; corpus=norm(clean('\f'.join(page_text)))
    print(json.dumps({'role':d['role'],'tables':[{k:v for k,v in t.items() if k in ('table','preceding_paragraphs')} for t in d['tables']]}))
    for b in d['missing_in_both']:
        if d['role']=='supplement-2' and b.get('table')==6:continue
        src=norm(b['source_text']); a=difflib.SequenceMatcher(None,src,corpus,autojunk=False).find_longest_match()
        start=max(0,a.b-a.a); candidate=corpus[start:start+len(src)+12]
        changes=[{'operation':op,'source':src[x1:x2],'pdf':candidate[y1:y2]} for op,x1,x2,y1,y2 in difflib.SequenceMatcher(None,src,candidate,autojunk=False).get_opcodes() if op!='equal']
        print(json.dumps({'paragraph':b['paragraph'],'table':b.get('table'),'row':b.get('row'),'column':b.get('column'),'source':b['source_text'],'candidate':candidate,'changes':changes},ensure_ascii=False))
    if d['role']=='supplement-2':
        table=next(t for t in d['tables'] if t['table']==6)
        print(json.dumps({'S14_source_rows':table['rows']},ensure_ascii=False))
        for pi,p in enumerate(page_text,1):
            if 'S14' in p or 'SRX1653202' in p or '27,470' in p:
                print(json.dumps({'PDF_page':pi,'text':p},ensure_ascii=False))
