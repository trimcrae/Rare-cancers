import argparse,datetime,hashlib,io,json,pathlib,re,shutil,subprocess,time,urllib.request,zipfile
A=[('13577_2022_818_MOESM1_ESM.pdf',91157,'ccdf1a764b744fa322f8ad0636084ccb'),('13577_2022_818_MOESM2_ESM.pdf',110337,'9469b4108a7de5f38e8b2e0645232e84')]
def get(url):
 r=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMC-public-source-analysis/1.0'}),timeout=90);b=r.read(20*1024*1024+1)
 if len(b)>20*1024*1024:raise ValueError('20MiB bound')
 return b,r.geturl(),r.headers.get('Content-Type','')
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',default='campaign-output/bangerter-genotypes');a=p.parse_args();d=pathlib.Path(a.out);d.mkdir(parents=True,exist_ok=True);result={'schema':'bangerter-exact-genotype-supplement/1','startedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'PMC9813045 DOI10.1007/s13577-022-00818-x','attachmentDeclarations':A,'retrievals':[],'attachments':[],'errors':[],'interpretation':'Reported variants only. Missing rows not coverage/absence/WT. Main up to406DNA/up to265rearrangement genes; specimen manifest separately verified.'};payloads={};u='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9813045/supplementaryFiles'
 for attempt in range(2):
  try:
   b,url,ctype=get(u);result['retrievals'].append({'requestedUrl':u,'finalUrl':url,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'contentType':ctype,'attempt':attempt+1});z=zipfile.ZipFile(io.BytesIO(b));result['archiveMembers']=[{'name':i.filename,'bytes':i.file_size} for i in z.infolist()]
   for name,n,md in A:
    matches=[i for i in z.infolist() if pathlib.PurePosixPath(i.filename).name==name]
    if len(matches)==1:payloads[name]=z.read(matches[0])
   (d/'declared-supplements.zip').write_bytes(b);break
  except Exception as e:
   result['retrievals'].append({'requestedUrl':u,'attempt':attempt+1,'error':type(e).__name__+': '+str(e)})
   if attempt==0:time.sleep(2)
 for name,n,md in A:
  if name not in payloads:
   u='https://static-content.springer-cdn.com/esm/art%3A10.1007%2Fs13577-022-00818-x/MediaObjects/'+name
   try:b,url,ctype=get(u);payloads[name]=b;result['retrievals'].append({'requestedUrl':u,'finalUrl':url,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'contentType':ctype})
   except Exception as e:result['retrievals'].append({'requestedUrl':u,'error':type(e).__name__+': '+str(e)})
  if name not in payloads:result['errors'].append({'file':name,'error':'No declared public PDF'});continue
  b=payloads[name];r={'filename':name,'bytes':len(b),'md5':hashlib.md5(b).hexdigest(),'sha256':hashlib.sha256(b).hexdigest(),'matchesPrimaryDeclaredBytesAndMD5':len(b)==n and hashlib.md5(b).hexdigest()==md};result['attachments'].append(r)
  if not r['matchesPrimaryDeclaredBytesAndMD5'] or not b.startswith(b'%PDF'):r['error']='Identity mismatch/notPDF';result['errors'].append({'file':name,'error':r['error']});continue
  f=d/name;f.write_bytes(b)
  try:
   if shutil.which('pdftotext'):txt=subprocess.check_output(['pdftotext','-layout',str(f),'-'],text=True);r['parser']='pdftotext-layout'
   else:
    from pypdf import PdfReader
    pdf=PdfReader(io.BytesIO(b));txt='\n\n'.join(x.extract_text() or '' for x in pdf.pages);r['parser']='pypdf';r['pages']=len(pdf.pages)
   (d/(name+'.txt')).write_text(txt);r['extractedCharacters']=len(txt);r['textSha256']=hashlib.sha256(txt.encode()).hexdigest();r['fullExtractedText']=txt;genes=['MTAP','SMARCB1','POLQ','CDKN2A','CDKN2B','TP53','MLL3','KMT2C','KDM5C','FANCA','NR4A3','EWSR1','TAF15','MDM4','MYC','EGFR','MET'];r['literalGeneMentions']={g:len(re.findall(r'(?<![A-Za-z0-9])'+re.escape(g)+r'(?![A-Za-z0-9])',txt,re.I)) for g in genes}
  except Exception as e:r['error']=type(e).__name__+': '+str(e);result['errors'].append({'file':name,'error':r['error']})
 result['finishedUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(d/'bangerter-genotype-supplement.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));return 1 if result['errors'] else 0
if __name__=='__main__':raise SystemExit(main())
