from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from hashlib import sha256
from datetime import datetime, timezone
from collections import Counter
import re, json, unicodedata, difflib
from pypdf import PdfReader

REPO = Path('C:/Users/mcrae/.codex/worktrees/emc-fo-figure4-20260909/EMC-Research')
BASE = REPO / 'research/release-candidates/retained-20260918'
OUT = Path(__file__).parent
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W = '{' + NS['w'] + '}'

def digest(p):
    return sha256(p.read_bytes()).hexdigest()

def norm(s):
    # Only Unicode compatibility and whitespace. Preserve punctuation and all digits.
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', s).replace('\u00ad', '').replace('\u200b', '').replace('\ufeff', ''))

def pdf_clean(s):
    # Only a standalone terminal number equal to that PDF page's ordinal.
    return '\f'.join(re.sub(r'(?m)^\s*' + str(i) + r'\s*\Z', '', p) for i,p in enumerate(s.split('\f'),1))

def para_text(p):
    items = []
    for t in p.iter():
        if t.tag == W + 't': items.append(t.text or '')
        elif t.tag in (W + 'tab', W + 'br', W + 'cr'): items.append(' ')
        elif t.tag == W + 'noBreakHyphen': items.append('\u2011')
        elif t.tag == W + 'softHyphen': items.append('\u00ad')
    return ''.join(items)

def blocks(p):
    result, features = [], {}
    with ZipFile(p) as z:
        parts = [n for n in z.namelist() if n == 'word/document.xml' or re.match(r'word/(footnotes|endnotes|header\d+|footer\d+)\.xml$', n)]
        for part in parts:
            root = ET.fromstring(z.read(part))
            parent = {c: e for e in root.iter() for c in e}
            for i, para in enumerate(root.findall('.//w:p', NS), 1):
                text = para_text(para)
                if not text.strip(): continue
                anc, table = para, False
                while anc in parent:
                    anc = parent[anc]
                    table = table or anc.tag == W+'tc'
                result.append({'part': part, 'paragraph': i, 'kind': 'table_cell_paragraph' if table else 'paragraph', 'text': text})
            features[part] = {'tables': len(root.findall('.//w:tbl', NS)), 'drawings': len(root.findall('.//w:drawing', NS)), 'symbols': len(root.findall('.//w:sym', NS)), 'deleted_runs': len(root.findall('.//w:del', NS)), 'textboxes': len(root.findall('.//w:txbxContent', NS)), 'alt_chunks': len(root.findall('.//w:altChunk', NS)), 'math_text': len([e for e in root.iter() if e.tag.endswith('}t') and e.tag != W+'t']), 'note_references': len(root.findall('.//w:footnoteReference', NS))+len(root.findall('.//w:endnoteReference', NS))}
    return result, features

receipt_path = BASE / 'rendered/CSPG4-ASO-RENDER-RECEIPT.json'
receipt = json.loads(receipt_path.read_text('utf-8'))
result = {'schema': 'emc-docx-pdf-text-audit/1', 'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'source_commit': receipt['source_commit'], 'render_receipt': str(receipt_path), 'render_receipt_sha256': digest(receipt_path), 'method': 'All nonempty Word paragraphs including table-cell paragraphs, headers/footers and foot/endnotes checked against retained pdf-text and independent pypdf extraction; NFKC, soft hyphen/zero-width/BOM removal and whitespace removal only; punctuation and digits otherwise retained. Only terminal standalone printed page numbers equal to the PDF page ordinal removed at form-feed boundaries in both retained and direct text. Sequential matching uses each exact paragraph occurrence once in source order.', 'documents': []}
for d in receipt['documents']:
    if d['paper'] not in ('CSPG4','ASO'): continue
    src, pdf = REPO / d['input'], REPO / d['pdf']
    txt = pdf.parent / 'pdf-text.txt'
    reader = PdfReader(pdf)
    pages = [p.extract_text() or '' for p in reader.pages]
    direct = '\f'.join(pages)
    retained = txt.read_text('utf-8')
    source_blocks, features = blocks(src)
    corpora = {'retained': norm(pdf_clean(retained)), 'direct': norm(pdf_clean(direct))}
    raw_direct = norm(direct)
    positions = {k:0 for k in corpora}
    rows, counts = [], Counter()
    for b in source_blocks:
        needle = norm(b['text'])
        found = {k: needle in v for k,v in corpora.items()}
        ordered_found = {k: v.find(needle,positions[k]) for k,v in corpora.items()}
        for k, location in ordered_found.items():
            if location >= 0: positions[k] = location + len(needle)
        counts['blocks'] += 1
        counts[b['kind']] += 1
        counts['exact_retained'] += found['retained']
        counts['exact_direct'] += found['direct']
        counts['exact_either'] += any(found.values())
        counts['ordered_retained'] += ordered_found['retained']>=0
        counts['ordered_direct'] += ordered_found['direct']>=0
        row = {k:b[k] for k in ('part','paragraph','kind')}
        row.update({'text_sha256': sha256(b['text'].encode()).hexdigest(), 'characters': len(b['text']), 'match':found, 'ordered_match':{k:v>=0 for k,v in ordered_found.items()}, 'raw_direct_match': needle in raw_direct})
        if not all(found.values()) or not all(v>=0 for v in ordered_found.values()) or needle not in raw_direct:
            row['source_text'] = b['text']
        if not any(found.values()):
            # Largest exact anchor with local context, for bounded human adjudication.
            sm = difflib.SequenceMatcher(None, needle, corpora['direct'], autojunk=False)
            anchor = sm.find_longest_match()
            start = max(0, anchor.b-anchor.a-100)
            row['direct_candidate_compact'] = corpora['direct'][start:start+len(needle)+250]
        rows.append(row)
    author_lines = [b['text'] for b in source_blocks if re.search(r'ORCID|Correspond|Tristan|preprint|Qeios|aiXiv|aixiv|zenodo|previously|prior.publication|funding|competing|Declaration|Claude|GPT-', b['text'], re.I)]
    removed_numbers = {k:[i for i,p in enumerate(s.split('\f'),1) if re.search(r'(?m)^\s*'+str(i)+r'\s*\Z', p)] for k,s in {'retained':retained,'direct':direct}.items()}
    report = {'paper':d['paper'], 'role':d['role'], 'docx':str(src), 'docx_sha256':digest(src), 'docx_matches_render_receipt':digest(src)==d['sha256'], 'pdf':str(pdf), 'pdf_sha256':digest(pdf), 'pdf_matches_render_receipt':digest(pdf)==d['pdf_sha256'], 'pdf_text':str(txt), 'pdf_text_sha256':digest(txt), 'pages':len(pages), 'pages_match_receipt':len(pages)==d['pages'], 'source_xml_features':features, 'removed_printed_page_numbers':removed_numbers, 'counts':dict(counts), 'blocks':rows, 'author_preprint_declaration_source_blocks':author_lines, 'raw_extraction_mismatch_adjudication': [{'paragraph': r['paragraph'], 'reason': 'Source paragraph crosses a printed page boundary. Exact contiguous match restored solely by removal of terminal page number equal to page ordinal; digits and punctuation inside source paragraph unchanged.'} for r in rows if not r['raw_direct_match']]}
    result['documents'].append(report)
    print(json.dumps({'paper':d['paper'],'role':d['role'],'hashes_match':report['docx_matches_render_receipt'] and report['pdf_matches_render_receipt'], 'pages':len(pages),'counts':dict(counts), 'mismatches':[x for x in rows if not any(x['match'].values())]}, ensure_ascii=False))
result['combined_pdfs'] = []
for c in receipt['combined']:
    if c['paper'] not in ('ASO','CSPG4'): continue
    combined = REPO / c['path']
    reader = PdfReader(combined)
    expected = []
    for comp in c['components']:
        expected.extend(p.extract_text() or '' for p in PdfReader(REPO/comp['path']).pages)
    actual = [p.extract_text() or '' for p in reader.pages]
    row = {'paper':c['paper'], 'path':str(combined), 'sha256':digest(combined), 'matches_render_receipt':digest(combined)==c['sha256'], 'pages':len(actual), 'pages_match_receipt':len(actual)==c['pages'], 'page_text_identical_to_components_in_order':actual==expected, 'component_order':c['component_order']}
    if c.get('embedded_csv'):
        name = c['embedded_csv']['name']
        attachments = reader.attachments[name]
        local_csv = BASE/'inputs'/c['paper']/name
        row['embedded_csv'] = {'name':name,'instances':len(attachments),'sha256':[sha256(b).hexdigest() for b in attachments],'bytes':[len(b) for b in attachments],'receipt_and_input_byte_identical':len(attachments)==1 and sha256(attachments[0]).hexdigest()==c['embedded_csv']['sha256'] and attachments[0]==local_csv.read_bytes()}
    result['combined_pdfs'].append(row)
    print(json.dumps(row))
result['scope_limits'] = ['Read-only textual export completeness; no rendering, UI, downloads, scientific reevaluation or source-to-Word rereview.', 'Raster figure text is covered by existing layout/figure review, not by Word body XML comparison.', 'Author identity and preprint metadata checked for preservation/internal consistency against accepted source and retained inventory, not independently revalidated externally.']
result['metadata_adjudication'] = [
    {'paper':'CSPG4','status':'no_export_induced_or_current_critical_error_found','details':'Name, unaffiliated status, email, ORCID, responsibility, financial/nonfinancial interest, funding and public-data ethics wording preserved exactly. Cover acknowledges both existing Research Square and aiXiv preprints. Original Research Square title remains explicitly a historical reference, not a stale current title.'},
    {'paper':'ASO','status':'no_export_induced_or_current_critical_error_found','details':'Name, unaffiliated status, email, ORCID, author responsibility, self-funding, financial/nonfinancial interests and AI declaration preserved exactly. Cover acknowledges Qeios version 4 and historical Zenodo provenance. No aiXiv posting claimed in these first-run files; retained prior inventory had no ASO aiXiv ID. Before future journal submission, add any newly successful aiXiv posting to preprint disclosure; this is contingent later metadata maintenance, not an existing export omission.'}
]
result['status'] = 'PASS_TEXTUAL_EXPORT_COMPLETENESS'
assert all(d['docx_matches_render_receipt'] and d['pdf_matches_render_receipt'] and d['pages_match_receipt'] and d['counts']['blocks']==d['counts']['ordered_retained']==d['counts']['ordered_direct'] for d in result['documents'])
assert all(c['matches_render_receipt'] and c['pages_match_receipt'] and c['page_text_identical_to_components_in_order'] and c.get('embedded_csv',{}).get('receipt_and_input_byte_identical',True) for c in result['combined_pdfs'])
assert all(not any(f[k] for k in ('symbols','deleted_runs','textboxes','alt_chunks','math_text','note_references')) for d in result['documents'] for f in d['source_xml_features'].values())
(OUT / 'DOCX-PDF-TEXT-AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
