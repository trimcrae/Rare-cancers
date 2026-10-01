#!/usr/bin/env python3
import argparse,collections,hashlib,io,json,pathlib,urllib.request,zipfile
P=argparse.ArgumentParser();P.add_argument('--out',default='campaign-output/immunosarc1-gene-summary');P.add_argument('--text-input',default='campaign-output/clinical-followup/immunosarc1-supp-extracted.txt');A=P.parse_args();O=pathlib.Path(A.out);O.mkdir(parents=True,exist_ok=True)
PDFSHA='144d1141e199260a9709af13e6e96866962ea4da64c1c724f555baac3feb7d43';TEXTSHA='f2364d69c88ace1f8b497f696a56482b33e212a59d570152d95ff071aac8787d'
R={'schema':'immunosarc1-published-gene-summary-arithmetic/1','sources':[],'errors':[],'limits':['Printed aggregate statistics are measured summaries, not individual transcript/outcome data.','Outcome-selected genes were reused for clustering/group comparison; multiplying p cannot establish independent validation.','No four-EMC patient reconstruction from mixed-sarcoma aggregate summaries.','Count mismatch is a source/parser coverage finding, not automatic author error.']}
try:
 p=pathlib.Path(A.text_input)
 if p.exists():
  b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==TEXTSHA;text=b.decode();R['sources'].append({'cachedArtifact':str(p),'bytes':len(b),'sha256':TEXTSHA})
 else:
  u='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7674086/supplementaryFiles'
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'EMC-public-summary-arithmetic/1'}),timeout=90) as f:zbytes=f.read(16*1024*1024+1)
  assert len(zbytes)<=16*1024*1024;z=zipfile.ZipFile(io.BytesIO(zbytes));files=[x for x in z.infolist() if pathlib.PurePosixPath(x.filename).name=='jitc-2020-001561supp001.pdf'];assert len(files)==1;pdf=z.read(files[0]);assert len(pdf)==4269926 and hashlib.sha256(pdf).hexdigest()==PDFSHA
  from pypdf import PdfReader
  reader=PdfReader(io.BytesIO(pdf));pageTexts=[x.extract_text() or '' for x in reader.pages];text='\n'.join(pageTexts);(O/'published-supplement.pdf').write_bytes(pdf);R['sources'].append({'url':u,'archiveBytes':len(zbytes),'archiveSHA256':hashlib.sha256(zbytes).hexdigest(),'member':files[0].filename,'PDFbytes':len(pdf),'PDFsha256':PDFSHA,'pages':len(reader.pages)});R['pageDiagnostics']=[{'page':i+1,'characters':len(t),'table2Mention':'Supplementary Table 2' in t,'textTail':t[-180:]} for i,t in enumerate(pageTexts)]
 R['textCharacters']=len(text);R['textSHA256']=hashlib.sha256(text.encode()).hexdigest();(O/'published-supplement.txt').write_text(text);k=text.find('Supplementary Table 2');assert k>=0;t=text[k:];R['literalCompleteTableRegion']=t
 def num(s):return float(s.replace(',','.'))
 rows=[]
 for line in t.splitlines():
  a=line.split()
  if len(a)==7 and a[-1] in ('UP','DOWN'):
   try:rows.append({'gene':a[0],'statistic':num(a[1]),'dm':num(a[2]),'p':num(a[3]),'FDR':num(a[4]),'Bonferroni':num(a[5]),'direction':a[6],'literalLine':line})
   except ValueError:pass
 assert rows;R['parsedPrintedRows']=len(rows);R['narrativeClaimedRows']=84;R['printedRowsEqualNarrative84']=len(rows)==84;R['uniqueGeneSymbols']=len({x['gene'] for x in rows});R['duplicateSymbols']={k:v for k,v in collections.Counter(x['gene'] for x in rows).items() if v>1};R['directionCounts']=dict(collections.Counter(x['direction'] for x in rows));R['reportedBonferroniBelowPoint05']=sum(x['Bonferroni']<.05 for x in rows);R['pToBonferroniMultiplierRange']=[min(x['Bonferroni']/x['p'] for x in rows),max(x['Bonferroni']/x['p'] for x in rows)];R['arithmeticSensitivityOnly']=[{'multiplicity':m,'rowsWithDisplayedPtimesMBelowPoint05':sum(x['p']*m<.05 for x in rows)} for m in (102,732,2549)];R['literalRows']=rows
except Exception as e:R['errors'].append(type(e).__name__+': '+str(e))
(O/'immunosarc1-gene-summary.json').write_text(json.dumps(R,indent=2));print(json.dumps(R));raise SystemExit(1 if R['errors'] else 0)
