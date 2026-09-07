"""Independent validation against complete downloaded HPA XML/JSON, no worker imports."""
from pathlib import Path
import json,xml.etree.ElementTree as ET,hashlib,collections,datetime,re,html
P=Path('C:/Users/mcrae/.codex/worktrees/8010/EMC-Research/.cache/atlas-normal-context-recovery-20260906');OUT=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
roster=read(P/'fixed-panel-normal-context-roster.json');ihc=read(P/'normal-IHC-cell-records.json');rna=read(P/'normal-RNA-source-records.json')
assert len(roster)==12 and {r['gene'] for r in roster}==set('CD276 SSTR2 PRAME FAP CD248 CSPG4 MSLN L1CAM GPC3 ALPP CDH17 CHRNA6'.split())
checks=0;summary=[];source_hashes={}
for name,v in read(P/'file-manifest.json').items():
    f=P/name;assert f.stat().st_size==v['bytes'] and hashlib.sha256(f.read_bytes()).hexdigest()==v['sha256'];source_hashes[name]=v['sha256']
jsonfields={'rna_tissue_specificity':'RNA tissue specificity','rna_tissue_distribution':'RNA tissue distribution','rna_tissue_specific_nTPM':'RNA tissue specific nTPM','rna_tissue_cell_type_enrichment':'RNA tissue cell type enrichment','rna_single_cell_type_specific_nCPM':'RNA single cell type specific nCPM','protein_classes':'Protein class','antibodies':'Antibody','antibody_RRID':'Antibody RRID'}
levels=collections.Counter();units=collections.Counter()
for rec in roster:
    g=rec['gene'];root=ET.parse(P/(g+'.xml')).getroot();entries=root.findall('entry');assert len(entries)==1;e=entries[0];j=read(P/(g+'.json'))
    assert e.findtext('name')==j['Gene']==g
    assert e.find('identifier').attrib==rec['identifier'] and e.find('identifier').get('id')==j['Ensembl']==rec['ensembl']
    assert rec['xml_entry_version']==e.get('version')=='25' and rec['xml_versioned_url']==e.get('url')
    assert e.find('identifier').get('version')=='109'
    for k,v in jsonfields.items():assert rec[k]==j.get(v);checks+=1
    ts=e.findall('tissueExpression');cs=e.findall('cellExpression');assert len(ts)<=1 and len(cs)<=1
    for elements,prefix,tech in [(ts,'normal_IHC','IHC'),(cs,'ICC_IF','ICC/IF')]:
        x=elements[0] if elements else None
        assert rec[prefix+'_summary']==(x.findtext('summary') if x is not None else None)
        assert rec[prefix+'_reliability']==(x.findtext('verification') if x is not None else None)
        if x is not None:assert x.get('technology')==tech and x.get('source')=='HPA'
    if ts:
        assert ts[0].get('assayType')=='tissue'
        assert rec['normal_IHC_reliability_description']==ts[0].find('verification').get('description')
    actual_locations=[] if not cs else [{'text':n.text,**n.attrib} for n in cs[0].iter('location')]
    assert actual_locations==rec['ICC_IF_locations']
    source_cells=[]
    if ts:
        for idx,d in enumerate(ts[0].findall('data'),1):
            for ci,c in enumerate(d.findall('tissueCell'),1):
                source_cells.append((d.findtext('tissue'),d.find('tissue').get('organ'),d.findtext('level'),c.findtext('cellType'),c.findtext('level'),idx,ci))
    declared=[r for r in ihc if r['gene']==g];assert len(source_cells)==len(declared)==rec['normal_IHC_cell_rows']
    for actual,pub in zip(source_cells,declared):
        expected=(pub['tissue'],pub['organ'],pub['tissue_level'],pub['cell_type'],pub['cell_level'])
        assert actual[:5]==expected and pub['reliability']==rec['normal_IHC_reliability']
        assert pub['source_xml']==g+'.xml' and pub['xml_locator']==f'entry/tissueExpression/data[{actual[5]}]/tissueCell'
        levels[actual[4]]+=1;checks+=1
    source_rna=[]
    for block in e.findall('rnaExpression'):
        if block.get('assayType') not in ['tissue','consensusTissue']:continue
        assert block.get('technology')=='RNAseq'
        for idx,d in enumerate(block.findall('data'),1):
            source_rna.append((block.get('source'),block.get('assayType'),d.findtext('tissue'),d.find('tissue').get('organ'),[n.attrib for n in d.findall('level')],idx))
    declared=[r for r in rna if r['gene']==g];assert len(source_rna)==len(declared)==rec['normal_RNA_tissue_records']
    for actual,pub in zip(source_rna,declared):
        assert actual[:5]==(pub['source'],pub['assay_type'],pub['tissue'],pub['organ'],pub['levels'])
        assert pub['source_xml']==g+'.xml' and pub['xml_locator']==f"entry/rnaExpression[@assayType='{actual[1]}']/data[{actual[5]}]"
        for lv in actual[4]:units[(actual[1],lv.get('unitRNA'))]+=1
        checks+=1
    summary.append({'gene':g,'IHC_rows':len(source_cells),'negative_IHC_rows':sum(r[4]=='not detected' for r in source_cells),'IHC_reliability':rec['normal_IHC_reliability'],'IHC_description':rec['normal_IHC_reliability_description'],'ICC_IF_locations':actual_locations,'RNA_tissue_records':len(source_rna)})
assert dict(levels)=={'not detected':695,'low':112,'medium':173,'high':74}
assert [r['gene'] for r in summary if r['IHC_rows']==0]==['GPC3','CHRNA6']
bygene={r['gene']:r for r in roster}
assert all(bygene[g]['normal_IHC_reliability']=='uncertain' for g in ['SSTR2','FAP'])
assert 'multiple genes' in bygene['ALPP']['ICC_IF_summary']
assert 'cytoplasmic' in bygene['CSPG4']['normal_IHC_summary'] and 'plasma membrane' in bygene['CSPG4']['ICC_IF_summary']
def txt(name):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]*>',' ',(P/name).read_text(encoding='utf-8'))))
license=txt('hpa-license.html');tissue=txt('hpa-tissue-methods.html');download=txt('hpa-download.html');cell=txt('hpa-subcellular-methods.html')
assert 'Creative Commons Attribution 4.0 International License for all copyrightable parts' in license
assert 'third-party constraints' in license
assert 'version 25.1' in download and 'Ensembl version 109' in tissue
assert 'maximum nTPM value for each gene in the two data sources' in tissue and 'maximum of all sub-tissues' in tissue
assert 'immunofluorescently stained cells' in cell
out={'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'pass','worker_code_imported':False,'gene_count':12,'source_field_row_checks':checks,'normal_IHC_cell_rows':len(ihc),'IHC_level_counts':dict(levels),'RNA_tissue_block_rows':len(rna),'RNA_units_by_block':{str(k):v for k,v in units.items()},'gene_summaries':summary,'source_hashes':source_hashes,'material_source_errors':[],'limitations':['Tissue IHC reliability description is distinct from categorical reliability; CSPG4 approved still carries low RNA/staining consistency.','ICC/IF is a separate cell-based assay; membrane tags cannot supersede tissue staining or establish EMC accessibility.','GPC3/CHRNA6 tissue IHC absent in these XML bytes, not normal protein absence.','Consensus RNA uses maxima across sources/subtissues; distinct RNA units preserved, no cross-study ratio.','XML entry25 versus current methods25.1; JSON lacks explicit release identifier.','HPA CC-BY4.0 applies to copyrightable database parts; third-party constraints remain.']}
(OUT/'verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['status','gene_count','source_field_row_checks','normal_IHC_cell_rows','IHC_level_counts','RNA_tissue_block_rows','material_source_errors']},indent=2))
