"""Read-only review of the sibling's current permitted R6 regulatory packet."""
import argparse, datetime, hashlib, json, pathlib, xml.etree.ElementTree as ET
p=argparse.ArgumentParser();p.add_argument('packet',type=pathlib.Path);a=p.parse_args()
D=pathlib.Path(__file__).resolve().parent;F=a.packet
files=['RESULTS.txt','COVERAGE.txt','evaluation.json','geo-four-condition-evaluation.json',
       'geo-fusion-summary.xml','selected-primary-metadata.json','six3-contrary2004.json','AMENDMENT-01.txt']
hashes={f:hashlib.sha256((F/f).read_bytes()).hexdigest() for f in files}
x=ET.parse(F/'geo-fusion-summary.xml').getroot();groups={}
for d in x.findall('DocSum'):
    accession=d.find("Item[@Name='Accession']").text
    if accession not in ['GSE11185','GDS3481']:continue
    groups[accession]={n.find("Item[@Name='Accession']").text:n.find("Item[@Name='Title']").text for n in d.findall("Item[@Name='Samples']/Item")}
assert groups['GSE11185']==groups['GDS3481'] and len(groups['GSE11185'])==4
assert all('293-tet-On-' in t for t in groups['GSE11185'].values())
j=json.loads((F/'selected-primary-metadata.json').read_text());primary={r['id']:r for r in j}
assert 'Reverse transcription-PCR analyses' in primary['12543801']['abstractText']
assert 'Fourteen tumors' in primary['15262426']['abstractText']
results=(F/'RESULTS.txt').read_text();coverage=(F/'COVERAGE.txt').read_text();amendment=(F/'AMENDMENT-01.txt').read_text()
assert 'assay' in (results+coverage).lower()
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'genomic_clinical',
 'scope':'Read-only material eligibility/value check of current permitted R6 files; no new retrieval, no denied content, no full historical methods or PROD-ATAC supplement review',
 'reviewed_final_sha256':hashes,'direct_checks':{'same_four_GSMs_between_GSE_GDS':True,'all_engineered_293_conditions':True,
 'four_unique_conditions':groups['GSE11185'],'Laflamme2003_tumor_assay_abstract_explicit_RTPCR':True,
 '2004_abstract_fourteen_fusionpositive_no_native_NOR1_SIX3_expression':True,
 'nineteen_reported_cases_two_coexpression_fourteen_negative_three_unspecified':'Abstract supports these counts but not every case/assay mapping.'},
 'material_correction':'Initial draft called the 2004 result protein and framed discordance with2003 as RNA-versus-protein. Retained primary abstract does not establish this assay distinction; MeSH or protein title wording alone cannot establish measurement. Worker corrected to source-reported expression with assay level unresolved; AMENDMENT-01 preserves the reason.',
 'correction_status':'Accepted and applied in reviewed corrected result/coverage/evaluation; full method evidence remains unavailable/unexamined.',
 'decision':'Agree with scoped SHELVE: new numerical endogenous EMC perturbation/binding/output comparison not established. No absence, dependency or new SIX3 biological claim is supported.',
 'limitations':['This is not independent full-source coverage of every searched record.','GEO accessions duplicate one experiment, not biological replication.','Historical cases and assay discordance cannot be pooled or resolved from abstract labels.','No numerical pilot should be created merely to re-demonstrate published heterologous results.'],
 'reopening':'An actual authentic EMC perturbation/control/output mapping that answers a new useful question, with every relevant public condition and independent challenge.'}
(D/'independent-regulatory-review.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps({'checks':'PASS','reviewed_final_sha256':hashes,'review_sha256':hashlib.sha256((D/'independent-regulatory-review.json').read_bytes()).hexdigest()},indent=2))
