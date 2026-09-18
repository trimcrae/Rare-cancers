from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from hashlib import sha256
from datetime import datetime, timezone
import json, re, unicodedata
from pypdf import PdfReader

REPO=Path('C:/Users/mcrae/.codex/worktrees/emc-fo-figure4-20260909/EMC-Research')
BASE=REPO/'research/release-candidates/retained-20260918'
OUT=Path(__file__).parent
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
NS={'w':W[1:-1]}
def digest(p): return sha256(p.read_bytes()).hexdigest()
def norm(s): return re.sub(r'\s+','',unicodedata.normalize('NFKC',s).replace('\u00ad','').replace('\u200b','').replace('\ufeff',''))
def clean(s): return '\f'.join(re.sub(r'(?m)^\s*'+str(i)+r'\s*\Z','',p) for i,p in enumerate(s.split('\f'),1))
def text(p):
    return ''.join((e.text or '') if e.tag==W+'t' else (' ' if e.tag in (W+'tab',W+'br',W+'cr') else ('\u2011' if e.tag==W+'noBreakHyphen' else '')) for e in p.iter())
def blocks(path):
    result=[]; tables=[]
    with ZipFile(path) as z:
        for part in [n for n in z.namelist() if n=='word/document.xml' or re.match(r'word/(footnotes|endnotes|header\d+|footer\d+)\.xml$',n)]:
            root=ET.fromstring(z.read(part)); parent={c:e for e in root.iter() for c in e}; ts=root.findall('.//w:tbl',NS)
            for ti,t in enumerate(ts,1):
                parentt=parent[t]; preceding=list(parentt)[:list(parentt).index(t)]
                caption=[text(e) for e in preceding if e.tag==W+'p' and text(e).strip()]
                tables.append({'part':part,'table':ti,'preceding_paragraphs':caption[-2:],'rows':[[text(c) for c in r.findall('w:tc',NS)] for r in t.findall('w:tr',NS)]})
            for pi,p in enumerate(root.findall('.//w:p',NS),1):
                value=text(p)
                if not value.strip(): continue
                anc=p; chain=[]
                while anc in parent:
                    anc=parent[anc]; chain.append(anc)
                tc=next((e for e in chain if e.tag==W+'tc'),None)
                tr=next((e for e in chain if e.tag==W+'tr'),None)
                tbl=next((e for e in chain if e.tag==W+'tbl'),None)
                row={'part':part,'paragraph':pi,'kind':'table_cell_paragraph' if tc is not None else 'paragraph','source_text':value,'source_text_sha256':sha256(value.encode()).hexdigest()}
                if tbl is not None: row.update(table=ts.index(tbl)+1,row=tbl.findall('w:tr',NS).index(tr)+1,column=tr.findall('w:tc',NS).index(tc)+1)
                result.append(row)
    return result,tables

rp=BASE/'rendered/RENDER-RECEIPT.json'; receipt=json.loads(rp.read_text('utf-8'))
lp=BASE/'rendered/FO/figures/LABEL-CORRECTION-RECEIPT.json'; labels=json.loads(lp.read_text('utf-8'))
result={'schema':'emc-fo-docx-pdf-text-audit/1','checked_at_utc':datetime.now(timezone.utc).isoformat(),'source_commit':receipt['source_commit'],'render_receipt':str(rp),'render_receipt_sha256':digest(rp),'label_receipt':str(lp),'label_receipt_sha256':digest(lp),'method':'All source Word paragraphs and table cells; independent pypdf text and retained PDF text; NFKC, soft-hyphen/zero-width/BOM/whitespace normalization; only terminal page-number equal to page ordinal removed. Initial mismatches retained verbatim. No prose/science reevaluation.','documents':[]}
for d in receipt['documents']:
    if d['paper']!='FO':continue
    src=BASE/labels['docx_path'] if d['role']=='main' else REPO/d['input']
    expected=labels['docx_sha256'] if d['role']=='main' else d['sha256']
    pdf=REPO/d['pdf']; pt=pdf.parent/'pdf-text.txt'
    reader=PdfReader(pdf); direct='\f'.join(p.extract_text() or '' for p in reader.pages); retained=pt.read_text('utf-8')
    corpora={'retained':norm(clean(retained)),'direct':norm(clean(direct))}; raw={'retained':norm(retained),'direct':norm(direct)}
    rows,tables=blocks(src); cursor={k:0 for k in corpora}
    for b in rows:
        q=norm(b['source_text']); b['raw_match']={k:q in v for k,v in raw.items()}; b['match']={k:q in v for k,v in corpora.items()}
        locs={k:v.find(q,cursor[k]) for k,v in corpora.items()}; b['ordered_match']={k:v>=0 for k,v in locs.items()}
        for k,v in locs.items():
            if v>=0:cursor[k]=v+len(q)
    counts={'blocks':len(rows),'table_cell_paragraphs':sum(b['kind']=='table_cell_paragraph' for b in rows),'exact_retained':sum(b['match']['retained'] for b in rows),'exact_direct':sum(b['match']['direct'] for b in rows),'ordered_retained':sum(b['ordered_match']['retained'] for b in rows),'ordered_direct':sum(b['ordered_match']['direct'] for b in rows)}
    entry={'role':d['role'],'docx':str(src),'docx_sha256':digest(src),'docx_matches_correct_receipt':digest(src)==expected,'source_hash_authority':'LABEL-CORRECTION-RECEIPT.docx_sha256' if d['role']=='main' else 'RENDER-RECEIPT.documents.sha256','original_input_hash_in_render_receipt':d['sha256'],'pdf':str(pdf),'pdf_sha256':digest(pdf),'pdf_matches_receipt':digest(pdf)==d['pdf_sha256'],'pdf_text':str(pt),'pdf_text_sha256':digest(pt),'pages':len(reader.pages),'pages_match_receipt':len(reader.pages)==d['pages'],'counts':counts,'blocks':rows,'tables':tables,'missing_in_both':[b for b in rows if not any(b['match'].values())]}
    result['documents'].append(entry)
    print(json.dumps({'role':d['role'],'hash_match':entry['docx_matches_correct_receipt'] and entry['pdf_matches_receipt'],'counts':counts,'missing_in_both':[{k:v for k,v in b.items() if k in ('paragraph','table','row','column','source_text')} for b in entry['missing_in_both']]},ensure_ascii=False))
result['status']='MISMATCHES_REQUIRE_ADJUDICATION' if any(d['counts']['blocks']!=d['counts']['exact_direct'] or d['counts']['blocks']!=d['counts']['exact_retained'] for d in result['documents']) else 'ALL_SOURCE_BLOCKS_PRESENT'
dest=OUT/'FO-INITIAL-EXPORT-AUDIT.json'
with dest.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
