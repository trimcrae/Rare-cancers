import json,zipfile,hashlib,re,datetime,xml.etree.ElementTree as ET,io
from pathlib import Path
import peerj_expression_diagnostic_actual as p
import spatial_marker_followthrough_actual as sm
OUT=sm.OUT;NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def rec(path):return {'saved':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def main():
 OUT.mkdir(parents=True,exist_ok=True);path,receipt=p.get();r={'schema':'emc-PeerJ-source-metadata/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_workbook':receipt,'source_archives':[]}
 with zipfile.ZipFile(path) as z:
  names=z.namelist();root=ET.fromstring(z.read('xl/workbook.xml'));r['all_workbook_parts']=names;r['all_sheets']=[{'literal_name':v.attrib.get('name'),'state':v.attrib.get('state','visible'),'attributes':v.attrib} for v in root.findall('m:sheets/m:sheet',NS)];r['all_defined_names']=[{'attributes':v.attrib,'literal_formula':v.text} for v in root.findall('m:definedNames/m:definedName',NS)];r['metadata_properties']={name:z.read(name).decode(errors='replace') for name in names if name in ['docProps/core.xml','docProps/app.xml','docProps/custom.xml']};r['external_link_parts']=[name for name in names if name.startswith('xl/externalLinks/')];r['custom_xml_parts']=[name for name in names if name.startswith('customXml/')];r['sheet_dimensions']={name:ET.fromstring(z.read(name)).find('m:dimension',NS).attrib if ET.fromstring(z.read(name)).find('m:dimension',NS) is not None else None for name in names if re.fullmatch(r'xl/worksheets/sheet\d+\.xml',name)}
 for ap in sorted({ap for root in [OUT,Path('restored-artifacts'),Path('restored-artifacts-extra'),Path('restored-artifacts-third')] for ap in root.rglob('*.zip')}):
  try:
   with zipfile.ZipFile(ap) as z:
    hits=[name for name in z.namelist() if Path(name).name==p.NAME]
    if not hits:continue
    assert len(hits)==1 and hashlib.sha256(z.read(hits[0])).hexdigest()==p.PIN;ar={'source_archive_receipt':rec(ap),'frozen_workbook_member':hits[0],'all_members':[{'name':m.filename,'bytes':m.file_size} for m in z.infolist()],'all_DOCX_table_text':[]}
    for name in z.namelist():
     if not name.lower().endswith('.docx'):continue
     raw=z.read(name)
     with zipfile.ZipFile(io.BytesIO(raw)) as dz:doc=ET.fromstring(dz.read('word/document.xml'));text=' '.join(doc.itertext())
     ar['all_DOCX_table_text'].append({'member':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'literal_text':text})
    r['source_archives'].append(ar)
  except zipfile.BadZipFile:continue
 assert r['source_archives'],'Restore completed PeerJ rawZIP artifact; no closure onmissingrestoration'
 r['outcome_metadata_disposition']={'expression_sheet_header':['symbol']+p.IDS,'public_gene_expression_rows':9500,'matched_individual_time_event_outcomes_reconstructed':False,'rule':'Report actualsheet/definedname/customproperty/archivecontents; no samplegroup inference from clustering/columnorder; DOCXaggregateCoxresults are not specimenoutcomes'};dest=OUT/'PeerJ-source-metadata-actual.json';dest.write_text(json.dumps(sm.clean(r),allow_nan=False));print('EMC_PEERJ_SOURCE_METADATA_BEGIN');print(json.dumps(sm.clean(r),allow_nan=False));print('EMC_PEERJ_SOURCE_METADATA_END')
if __name__=='__main__':main()
