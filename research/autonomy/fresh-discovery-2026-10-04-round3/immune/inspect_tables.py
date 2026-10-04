from pathlib import Path
import pypdf,openpyxl,json,re,collections
B=Path(__file__).resolve().parent
reader=pypdf.PdfReader(B/'moura2024.pdf')
pages=[p.extract_text() for p in reader.pages]
(B/'moura2024-text.txt').write_text('\n\n'.join(f'PAGE {i+1}\n{p}' for i,p in enumerate(pages)),encoding='utf-8')
for i,p in enumerate(pages):
 for m in re.finditer(r'GSE\d+|[Dd]ata availability|[Ee]xtraskeletal|[Gg]eo',p):print('PAGE',i+1,p[max(0,m.start()-100):m.end()+220])
w=openpyxl.load_workbook(B/'subramanian2024-tables.xlsx',read_only=True,data_only=True)
out={}
for s in w:
 rows=list(s.values)
 hits=[dict(row=i+1,values=list(r)) for i,r in enumerate(rows) if re.search(r'extraskeletal|chondro|NR4A3|\bEMC\b',' '.join(map(str,r)),re.I)]
 out[s.title]=dict(rows=len(rows),cols=s.max_column,first_rows=[list(r) for r in rows[:4]],candidate_hits=hits)
(B/'subramanian-table-eligibility.json').write_text(json.dumps(out,indent=2,default=str),encoding='utf-8')
print('SUPPLEMENT',json.dumps({k:dict(rows=v['rows'],cols=v['cols'],hits=v['candidate_hits']) for k,v in out.items()},default=str))
