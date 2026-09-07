from pathlib import Path
import json,xml.etree.ElementTree as E,hashlib,shutil,collections
p=Path(__file__).parent;root=p.parents[1]
old=root/'research/modalities/emc-surface-normal-window.json';shutil.copyfile(old,p/'legacy-normal-window.json')
ids=json.loads((p/'gene-identities.json').read_text());roster=[];ihc=[];rna=[]
for g,ensg in ids.items():
    full=E.parse(p/(g+'.xml'));entry=full.find('entry');j=json.loads((p/(g+'.json')).read_text())
    assert entry.findtext('name')==g and j['Gene']==g and j['Ensembl']==ensg
    t=entry.find('tissueExpression');c=entry.find('cellExpression')
    rec={'gene':g,'role':'separate context control' if g=='CHRNA6' else 'fixed11 address','ensembl':ensg,'source_url':'https://www.proteinatlas.org/'+ensg,'xml_entry_version':entry.get('version'),'xml_versioned_url':entry.get('url'),'identifier':entry.find('identifier').attrib,'normal_IHC_summary':t.findtext('summary') if t is not None else None,'normal_IHC_reliability':t.findtext('verification') if t is not None else None,'normal_IHC_reliability_description':t.find('verification').get('description') if t is not None and t.find('verification') is not None else None,'ICC_IF_summary':c.findtext('summary') if c is not None else None,'ICC_IF_reliability':c.findtext('verification') if c is not None else None,'ICC_IF_locations':[{'text':x.text,**x.attrib} for x in c.findall('.//location')] if c is not None else [],'rna_tissue_specificity':j.get('RNA tissue specificity'),'rna_tissue_distribution':j.get('RNA tissue distribution'),'rna_tissue_specific_nTPM':j.get('RNA tissue specific nTPM'),'rna_tissue_cell_type_enrichment':j.get('RNA tissue cell type enrichment'),'rna_single_cell_type_specific_nCPM':j.get('RNA single cell type specific nCPM'),'protein_classes':j.get('Protein class'),'antibodies':j.get('Antibody'),'antibody_RRID':j.get('Antibody RRID'),'evidence_boundary':'HPA normal IHC and cultured-cell ICC/IF, not EMC surface density; RNA annotations do not establish protein localization or cell-of-origin'}
    if t is not None:
        for idx,d in enumerate(t.findall('data'),1):
            tissue=d.find('tissue')
            for cell in d.findall('tissueCell'):
                ihc.append({'gene':g,'tissue':tissue.text if tissue is not None else None,'organ':tissue.get('organ') if tissue is not None else None,'tissue_level':d.findtext('level'),'cell_type':cell.findtext('cellType'),'cell_level':cell.findtext('level'),'reliability':rec['normal_IHC_reliability'],'xml_locator':f'entry/tissueExpression/data[{idx}]/tissueCell','source_xml':g+'.xml'})
    for a in entry.findall('rnaExpression'):
        if a.get('assayType') not in ['consensusTissue','tissue']:continue
        for idx,d in enumerate(a.findall('data'),1):
            tissue=d.find('tissue');lv=d.find('level')
            rna.append({'gene':g,'source':a.get('source'),'assay_type':a.get('assayType'),'tissue':tissue.text if tissue is not None else None,'organ':tissue.get('organ') if tissue is not None else None,'levels':[x.attrib for x in d.findall('level')],'source_xml':g+'.xml','xml_locator':f"entry/rnaExpression[@assayType='{a.get('assayType')}']/data[{idx}]"})
    rec['normal_IHC_cell_rows']=sum(r['gene']==g for r in ihc);rec['normal_RNA_tissue_records']=sum(r['gene']==g for r in rna);roster.append(rec)
(p/'fixed-panel-normal-context-roster.json').write_text(json.dumps(roster,indent=2)+'\n')
(p/'normal-IHC-cell-records.json').write_text(json.dumps(ihc,indent=2)+'\n')
(p/'normal-RNA-source-records.json').write_text(json.dumps(rna,indent=2)+'\n')
summary={'genes':len(roster),'IHC_cell_rows':len(ihc),'RNA_tissue_rows':len(rna),'IHC_levels':dict(collections.Counter(r['cell_level'] for r in ihc)),'no_IHC_rows':[r['gene'] for r in roster if not r['normal_IHC_cell_rows']],'all_gene_identity_checks_passed':True,'no_tumor_expression_files_read':True,'no_cross_source_ratio_or_safety_threshold_computed':True}
(p/'validation.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
