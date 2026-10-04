"""Independent original-OOXML identity/condition extraction; not efficacy inference."""
import json,zipfile,xml.etree.ElementTree as E,re,statistics,hashlib,math
from pathlib import Path
D=Path(__file__).resolve().parent;F=D.parent/'functional'
if not F.exists():F=Path(r'C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-functional/research/autonomy/fresh-discovery-2026-10-04/functional')
p=F/'mendeley-supporting-values.xlsx';raw=p.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='a3eec1dd81423727283939d394e3a51a8c404e2c377a840ba3ccb5946098ec5f'
z=zipfile.ZipFile(p);N={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
rels={x.get('Id'):x.get('Target') for x in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
ss=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',N)]
sheets={}
for sh in E.fromstring(z.read('xl/workbook.xml')).find('s:sheets',N):
 t=rels[sh.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')];t=t.lstrip('/') if t.startswith('/') else 'xl/'+t;c={}
 for el in E.fromstring(z.read(t)).findall('.//s:c',N):
  v=el.find('s:v',N)
  if v is None:continue
  c[el.get('r')]=ss[int(v.text)] if el.get('t')=='s' else float(v.text)
 sheets[sh.get('name')]=c
exactlabel={name:{k:v for k,v in cells.items() if isinstance(v,str) and re.search(r'(?:USZ-23_)?EMC3(?:_|$)|NR4A3',v)} for name,cells in sheets.items()}
exactlabel={k:v for k,v in exactlabel.items() if v}
curves=[];s=sheets['2E-2L']
for h in range(5,76,10):
 assert s['Q'+str(h)]=='USZ-23_EMC3' and 'μM' in s['A'+str(h)]
 drug=s['A'+str(h-1)];pts=[]
 for row in range(h+1,h+7):
  vals=[s[c+str(row)] for c in 'QRS'];dose=s['A'+str(row)];assert all(isinstance(v,float) for v in vals) and isinstance(dose,float)
  pts.append({'source_row':row,'concentration_uM':dose,'replicates':vals,'mean':math.fsum(vals)/3,'sd_technical':statistics.stdev(vals)})
 curves.append({'drug':drug,'sheet':'2E-2L','columns':'Q:S','model':'USZ-23_EMC3','points':pts})
s=sheets['2M-2O'];auc=[]
for row in range(6,14):auc.append({'source_row':row,'drug':s['A'+str(row)],'mean':s['Q'+str(row)],'sd':s['R'+str(row)],'reported_N':s['S'+str(row)]})
other=[]
for sheet,cols,head in [('4D','IJ',5),('4E-F','DEF',5),('5B','F',6)]:
 s=sheets[sheet]
 for col in cols:
  label=s[col+str(head)];assert 'EMC3' in label
  vals=[(k,v) for k,v in s.items() if re.fullmatch(col+r'\d+',k) and int(re.search(r'\d+',k).group())>head and isinstance(v,float)]
  v=[v for k,v in vals]
  other.append({'sheet':sheet,'column':col,'label':label,'source_description':s['A2'],'numeric_cells':dict(vals),'n_numeric_cells':len(v),'mean':statistics.mean(v),'median':statistics.median(v),'sd':statistics.stdev(v),'unit_of_replication':'Unknown experimental hierarchy; fiber/nucleus/cell measurements are NOT independent EMC donors'})
s=sheets['2A'];transcript={s['A'+str(r)]:s['G'+str(r)] for r in range(6,16)}
result={'source_sha256':hashlib.sha256(raw).hexdigest(),'implementation':'stdlib OOXML original bytes','sheet_count':len(sheets),'all_exact_emc_label_occurrences':exactlabel,'drug_curves':curves,'reported_auc':auc,'other_emc_measurements':other,'signature_transcript_counts':transcript,'unresolved_identity_sheets':{'4I':'Cleaved caspase3 but no model label; not attributed to EMC','5E':'pCHK1 western analysis but no model label; not attributed to EMC'},'limits':['Deposit2025 submission versus final2026 article numerical concordance not established.','Dose labels here are raw micromolar, NOT log10 as in2023 workbook.','Drug-duration, fiber-length unit and replicate hierarchy require methods.','AUC N13 is not13independentEMCdonors and not necessarily the3displayedcurvecolumns.','No donor-independent validation or new clinical/target mechanism inferred.']}
(D/'mendeley-independent-values.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'sheet_count':len(sheets),'EMC_sheets':list(exactlabel),'curves':len(curves),'points':sum(len(c['points']) for c in curves),'other':[{k:v for k,v in r.items() if k!='numeric_cells'} for r in other],'limits':result['limits']},indent=2))

