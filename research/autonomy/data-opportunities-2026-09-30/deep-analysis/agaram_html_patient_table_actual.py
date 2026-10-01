import ast,hashlib,json,pathlib
P=pathlib.Path(__file__).parent/'clinical_primary_access_fallthrough.py';tree=ast.parse(P.read_text());allowed=[x for x in tree.body if isinstance(x,(ast.Import,ast.ImportFrom,ast.FunctionDef,ast.ClassDef))];ns={};exec(compile(ast.Module(body=allowed,type_ignores=[]),str(P),'exec'),ns);O=pathlib.Path('campaign-output/agaram-exact-html');O.mkdir(parents=True,exist_ok=True);u='https://pmc.ncbi.nlm.nih.gov/articles/PMC4015728/';R={'schema':'agaram-html-patient-table-actual/1','source':'PMC4015728 DOI10.1016/j.humpath.2014.01.007','errors':[],'limits':['Individual patient rows preserve literal followup/status and fusionannotation. No survival endpoint or pooled cohort inferred before review.']}
R['accessAttempts']=[]
for u in ['https://www.ncbi.nlm.nih.gov/pmc/articles/4015728','https://pmc.ncbi.nlm.nih.gov/articles/PMC4015728/?report=xml','https://pmc.ncbi.nlm.nih.gov/articles/PMC4015728/?report=reader']:
 rec={'url':u};R['accessAttempts'].append(rec)
 try:
  b,ct,f=ns['fetch'](u);rec.update(finalURL=f,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),contentType=ct);p=O/('route-'+str(len(R['accessAttempts'])));p.with_suffix('.html').write_bytes(b);h=ns['HP']();h.feed(b.decode('utf-8','replace'));text=' '.join(' '.join(h.a).split());rec.update(textCharacters=len(text),tableCount=len(h.ts));p.with_suffix('.txt').write_text(text);useful=len(text)>8000 and bool(h.ts) and 'extraskeletal myxoid' in text.lower()
  if useful:
   R.update(receipt=rec,fullText=text,tables=h.ts,textCharacters=len(text),usableFullPrimary=True);R['patientTableCandidates']=[{'tableIndex':i,'rows':t} for i,t in enumerate(h.ts) if any('follow' in ' '.join(row).lower() or 'clinical' in ' '.join(row).lower() or 'taf15' in ' '.join(row).lower() for row in t)];(O/'PMC4015728.html').write_bytes(b);(O/'PMC4015728.txt').write_text(text);break
 except Exception as e:rec['error']=type(e).__name__+': '+str(e)
if not R.get('usableFullPrimary'):R['errors'].append('Prior usable public HTML not recovered through these three recorded routes; no inference from challenges')
(O/'agaram-html-patient-table.json').write_text(json.dumps(R,indent=2));print(json.dumps(R));raise SystemExit(1 if R['errors'] else 0)
