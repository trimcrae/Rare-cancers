"""Focused frozen RNA-processing source/QC audit, no expression columns or raw BED."""
import pathlib,json,hashlib,datetime,collections,io,zipfile,re
import pandas as pd
import xml.etree.ElementTree as E
B=pathlib.Path(__file__).parent
O=pathlib.Path('/workspace/emc-r6-single_cell/research/autonomy/fresh-discovery-2026-10-05-round9/rna_processing')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
man=json.loads((O/'MANIFEST.json').read_text());exports=[]
for r in man['artifacts']:
 p=O/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'];exports.append(r)
port=json.loads((O/'PORTABILITY.json').read_text());raw=[]
for r in port['new_cache']:
 p=O/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'];raw.append(r)
# Hashing is byte-integrity only; do not open selected outcome values in shared matrix.
p=pathlib.Path(port['shared_readonly_source']['path']);assert sha(p)==port['shared_readonly_source']['sha256']
qc=json.loads((O/'ALL93-LIBRARY-QC.json').read_text())
with zipfile.ZipFile(O/'raw/Brunner2012-supplements.zip') as z:
 buf=z.read(qc['member']);assert hashlib.sha256(buf).hexdigest()==qc['member_sha256'];s=pd.read_excel(io.BytesIO(buf),sheet_name='Table_S1',header=None)
cols=s.iloc[2].tolist();diagnosis=None;actual=[]
for v in s.iloc[3:].itertuples(index=False,name=None):
 if pd.notna(v[0]):diagnosis=str(v[0])
 if pd.notna(v[1]) and str(v[1]).startswith('STT'):actual.append({'diagnosis':diagnosis,'sample':str(v[1]),**{str(cols[i]):int(v[i]) for i in range(2,7)}})
assert actual==qc['all93_libraries'] and len(actual)==93
emc=[r for r in actual if '(EMC)' in r['diagnosis']];mlps=[r for r in actual if '(MLS)' in r['diagnosis']];ss=[r for r in actual if '(SS)' in r['diagnosis']]
assert len(emc)==4 and len(mlps)==6 and len(ss)==3
heads=json.loads((O/'RAW-BED-ACCESS-GATE.json').read_text())['all_selected_conditions'];ok=[r for r in heads if r.get('status')==200];bad=[r for r in heads if '403' in r.get('error','')]
assert len(heads)==13 and len(ok)==11 and len(bad)==2
size=sum(int(r['headers']['content-length']) for r in ok);assert size==563852456
assert {r['accession'] for r in bad}=={'GSM715472','GSM715483'}
for term,n in [('_EMC',4),('_MLPS',6),('_SS',3)]:
 # Source uses MLS abbreviation, check both spellings for myxoid liposarcoma.
 labels=[r for r in heads if term in r['title'] or (term=='_MLPS' and '_MLS' in r['title'])];assert len(labels)==n
source_passages=[]
terms={'Brunner2012-PMC4053743.xml':['left-most','square root','coding genes if','hg18','two tumor samples had duplicate','27 normal'], 'Beck2010-PMC2808244.xml':['P5 end','two degenerate nucleotides','first 25 bp'], 'MAAPER2021-PMC8356463.xml':['single PAS genes','excluding intronic regions','QuantSeq','PolyA_DB']}
for fn,need in terms.items():
 root=E.parse(O/'raw'/fn).getroot()
 for i,p in enumerate(root.findall('.//p')):
  t=' '.join(p.itertext())
  if any(v.lower() in t.lower() for v in need):source_passages.append({'source':fn,'p_index':i,'source_sha256':sha(O/'raw'/fn),'text':t})
pipe=(O/'raw/Hofvander-RNAseq-pipeline.txt').read_text();assert 'for i in *toTranscriptome.out.genes.results' in pipe and 'transcript_id' in pipe
pas=json.loads((O/'PAS-VERSION-COMPATIBILITY.json').read_text());assert pas['GSE28866_alignment_genome']=='hg18';assert any('hg19' in r['path'] for r in pas['PAS_files']) and any('hg38' in r['path'] for r in pas['PAS_files'])
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owner_commit':'80966f46823b5197ad54947db83e943eaac18c7e','manifest_sha256':sha(O/'MANIFEST.json'),'exports_verified':len(exports),'cache_inputs_verified':len(raw),'sharedmatrix_integrity_verified_notvalues':True,'mismatches':0,'QC_original_rows_fields_equal':True,'all93_library_counts':dict(collections.Counter(r['diagnosis'] for r in actual)),'all4_EMC':emc,'all6_MLPS':mlps,'all3_SS':ss,'technical_replicates':[r['sample'] for r in actual if 'rep' in r['sample']],'source_units':'64unique tumors/66tumorlibraries+27normal libraries=93;13fixed libraries/specimens leave51other unique tumors/53otherlibraries; normal donorindependenceunproved','HEAD_disposition':{'all13':13,'head200':11,'head200_declared_compressed_bytes':size,'head403_pending':[{'gsm':r['accession'],'title':r['title']} for r in bad],'BED_bodies_read':False},'assay_passages_checked':source_passages,'Hofvander_gene_export_code_verified':'Reads*.genes.results; changingheader totranscript_id doesnotcreate isoformquantification','PAS_version':'hg18alignedsource versuscurrenthumanhg19/hg38annotations; novalidatedlift orterminalexoncalibration inferred','numeric_APA_or_sample_expression_columns_inspected':False,'bulk_or_new_retrieval':False,'export_bindings':exports,'cache_bindings':raw}
(B/'SOURCE-QC-AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print('exports',len(exports),'raw',len(raw),'QC',len(actual),'fixed',len(emc)+len(mlps)+len(ss),'HEAD',len(ok),len(bad))
