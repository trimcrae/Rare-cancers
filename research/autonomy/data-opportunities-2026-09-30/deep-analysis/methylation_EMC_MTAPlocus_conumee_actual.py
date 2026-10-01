#!/usr/bin/env python3
import gzip,hashlib,json,os,pathlib,shutil,subprocess,tarfile,urllib.request,zipfile
OUT=pathlib.Path('campaign-output/methylation-emc-MTAP');OUT.mkdir(parents=True,exist_ok=True)
manifest=OUT/'source-and-IDAT-manifest.json';rawzip=OUT/'targeted-EMC-and-FFPE-reference-IDATs.zip'
if not manifest.exists() or not rawzip.exists():raise FileNotFoundError('restore completed acquisition artifact before analysis')
m=json.loads(manifest.read_text());assert m['complete_query_pairs']==10 and m['complete_reference_pairs']==18,'individual IDAT recovery is incomplete; archive recovery remains runnable'
idats=OUT/'uncompressed-idats';idats.mkdir(exist_ok=True)
with zipfile.ZipFile(rawzip) as z:
 for r in m['raw_profiles']:
  for c in r['channels']:
   b=z.read('idats/'+c['file']);assert hashlib.sha256(b).hexdigest()==c['compressed_sha256']
   raw=gzip.decompress(b);assert hashlib.sha256(raw).hexdigest()==c['uncompressed_sha256'] and raw[:4]==b'IDAT'
   (idats/c['file'].removesuffix('.gz')).write_bytes(raw)
receipts=[]
def run(args,timeout,env=None):
 p=subprocess.run(args,timeout=timeout,env=env);receipts.append({'command':args,'returncode':p.returncode})
 if p.returncode:raise RuntimeError('command failed; preserve receipts and fix exact package/runtime error')
if not shutil.which('Rscript'):
 run(['sudo','apt-get','update','-qq'],600)
 run(['sudo','apt-get','install','-y','--no-install-recommends','r-base','r-base-dev','libcurl4-openssl-dev','libssl-dev','libxml2-dev','libzstd-dev','libbz2-dev','liblzma-dev','libpcre2-dev','libpng-dev','libjpeg-dev','libtiff-dev','libfontconfig1-dev','libfreetype6-dev','gfortran'],1200)
lib=OUT/'R-library';lib.mkdir(exist_ok=True);env=os.environ.copy();env['R_LIBS_USER']=str(lib.resolve());env['MAKEFLAGS']='-j2'
commit='cc1caffa49143ef06fde5036b434846649542623';url='https://codeload.github.com/hovestadt/conumee/tar.gz/'+commit
with urllib.request.urlopen(url,timeout=120) as r:b=r.read(2000001);status=r.status
assert status==200 and len(b)<=2000000
archive=OUT/'conumee-pinned-source.tar.gz';archive.write_bytes(b);src=OUT/'conumee-source';src.mkdir(exist_ok=True)
with tarfile.open(archive,'r:gz') as t:
 for member in t.getmembers():
  if not member.isfile():continue
  target=src/member.name
  if not target.resolve().is_relative_to(src.resolve()):raise ValueError('invalid source archive path')
  target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(t.extractfile(member).read())
packages=list(src.glob('*/DESCRIPTION'));assert len(packages)==1;package=packages[0].parent
setup=OUT/'install-R-dependencies.R'
req=['minfi','DNAcopy','rtracklayer','GenomicRanges','IRanges','GenomeInfoDb','IlluminaHumanMethylation450kmanifest','IlluminaHumanMethylation450kanno.ilmn12.hg19','IlluminaHumanMethylationEPICmanifest','IlluminaHumanMethylationEPICanno.ilm10b2.hg19','org.Hs.eg.db','TxDb.Hsapiens.UCSC.hg19.knownGene','jsonlite']
setup.write_text('options(repos=c(CRAN="https://cloud.r-project.org"),timeout=900)\nif(!requireNamespace("BiocManager",quietly=TRUE))install.packages("BiocManager")\npkgs <- '+json.dumps(req).replace('[','c(').replace(']',')')+'\nmissing <- pkgs[!vapply(pkgs,requireNamespace,logical(1),quietly=TRUE)]\nif(length(missing))BiocManager::install(missing,ask=FALSE,update=FALSE,Ncpus=2)\nstopifnot(all(vapply(pkgs,requireNamespace,logical(1),quietly=TRUE)))\ninstall.packages('+json.dumps(str(package.resolve()))+',repos=NULL,type="source",INSTALL_opts=c("--no-docs","--no-html","--no-multiarch"))\nstopifnot(as.character(packageVersion("conumee"))=="1.6.0")\n')
source_receipt={'source_commit':commit,'source_url':url,'source_archive_bytes':len(b),'source_archive_sha256':hashlib.sha256(b).hexdigest(),'source_files':[{'path':str(p.relative_to(src)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(src.rglob('*')) if p.is_file()]}
(OUT/'conumee-package-source-receipt.json').write_text(json.dumps(source_receipt,indent=2)+'\n')
with zipfile.ZipFile(OUT/'conumee-pinned-source.zip','w',compression=zipfile.ZIP_STORED) as z:z.write(archive,archive.name)
try:
 run(['Rscript',str(setup)],2700,env)
 script=pathlib.Path(__file__).with_name('methylation_EMC_MTAPlocus_conumee.R');run(['Rscript',str(script)],1800,env)
finally:
 (OUT/'R-command-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
