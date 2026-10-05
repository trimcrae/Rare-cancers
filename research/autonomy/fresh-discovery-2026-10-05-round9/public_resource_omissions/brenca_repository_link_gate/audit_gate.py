#!/usr/bin/env python3
"""Verify public source links/provenance/limits; no biological values."""
import datetime,hashlib,json,shutil,urllib.parse
from pathlib import Path
from html.parser import HTMLParser
p=Path(__file__).resolve().parent
def read(n):return json.loads((p/n).read_text())
def h(x):return hashlib.sha256(x.read_bytes()).hexdigest()
def binding(row):
 q=Path(row['path']);assert q.stat().st_size==row['bytes'],q
 assert h(q)==row['sha256'],q
port=read('PORTABILITY.json')
for r in port['new_ignored_originals']:binding(r)
assert sum(x['bytes'] for x in port['new_ignored_originals'])==port['new_raw_total_bytes']<=port['new_raw_soft_cap_bytes']
assert shutil.disk_usage(p).free>=port['minimum_free_bytes']
for r in read('REUSED-INPUT-BINDINGS.json')['bindings']:binding(r)
for r in read('AMENDMENT-02-CORRECTION-REUSE-AND-ACTUAL-LIBRARY-LINK.json')['bindings']:binding(r)
receipts=read('OFFICIAL-METADATA-RECEIPTS.json')+read('REAL-LINK-FOLLOWUP-RECEIPTS.json')+[read('ACTUAL-LIBRARY-PUBLISHING-RESULTS-RECEIPT.json')]
for r in receipts:
 assert urllib.parse.urlparse(r['url']).hostname!='opendocuments.cro.it'
 if 'sha256' in r:
  q=p/r['path'];assert q.stat().st_size==r['bytes'] and h(q)==r['sha256']
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,t,a):
  if t=='a':self.links.extend(v for k,v in a if k=='href')
def links(name,base):
 a=Links();a.feed((p/'source-cache'/name).read_text());return {urllib.parse.urljoin(base,x) for x in a.links}
assert 'https://www.cro.it/it/biblioteca/' in links('CRO-official-home','https://www.cro.it/it/')
assert 'https://www.cro.it/it/biblioteca/pubblicare-risultati.html' in links('CRO-actual-linked-library','https://www.cro.it/it/biblioteca/')
z=links('CRO-actual-linked-publishing-results','https://www.cro.it/it/biblioteca/pubblicare-risultati.html')
assert 'https://www.re3data.org' in z and 'https://journals.plos.org/plosone/s/recommended-repositories' in z
assert not any('opendocuments.cro.it' in x for x in z)
d=read('source-cache/DataCite-related-primary-DOI');assert d['meta']['total']==len(d['data'])==6
for x in d['data']:
 a=x['attributes'];assert 'rhabdomyosarcoma' in a['titles'][0]['title'].lower()
 rel=[r for r in a['relatedIdentifiers'] if r['relatedIdentifier']=='10.1002/path.5284']
 assert rel and all(r['relationType']=='References' for r in rel)
assert read('source-cache/DataCite-related-published-repository-URL')['meta']['total']==0
cr=read('source-cache/Crossref-exact-primary-DOI')['message']
assert any(r['id']=='10.1002/path.5737' for r in cr['relation']['correction'])
old=Path('/workspace/Rare-cancers/research/autonomy/fresh-discovery-2026-10-04-round3/mirna_deposition/RESULTS.txt').read_text()
assert '10.1002/path.5737' in old and 'PRJNA692081' in old
ir=Path('/workspace/emc-r6-single_cell/research/autonomy/fresh-discovery-2026-10-05-round9/rna_processing/intron_retention_gate')
assert h(ir/'MANIFEST.json')=='1e9285c756e806816f0a37926309385114210ad617f44ad0d5b8f8a8f4594c51'
assert json.loads((ir/'DECISION.json').read_text())['intron_retention_outcomes_inspected'] is False
prior={'SCIENCE-FREEZE.json':'73ae0545cde59168163f72315f077560b964a7d4778595a5e5b12edba4254f29','FINAL-FREEZE.json':'ef6700a2bc53a047f835c481a92d8010f94fb25a3b8f02c9e833a5b197c382a2','spatial_protein_immune_gate/SCIENCE-FREEZE.json':'3e2110a005c47d12d7c8630fa12e2e5aad49826bf0a14397b72e138ca2133f96','spatial_protein_immune_gate/FINAL-FREEZE.json':'ea2ec40088bd52bd2827ddcd33a246403dd5b6dcd30376d5934584e794f0306a','igf2_review/FREEZE.json':'4dea2cd980a227b0da9554263027fc81d1a1355261c43d545c01f0599aac5eab'}
for n,v in prior.items():assert h(p.parent/n)==v,n
assert read('DECISION.json')['numeric_RNA_IR_outcomes_inspected'] is False
print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS','new_successful_original_hashes_checked':len(port['new_ignored_originals']),'retrieval_receipts_checked':len(receipts),'reused_bindings_checked':len(read('REUSED-INPUT-BINDINGS.json')['bindings'])+len(read('AMENDMENT-02-CORRECTION-REUSE-AND-ACTUAL-LIBRARY-LINK.json')['bindings']),'all6_datacite_source_relations_checked':True,'actual_official_institution_link_chain_checked':True,'failed_old_endpoint_not_retried':True,'knowncorrigendum_reuse_checked':True,'prior_scientific_freezes_unchanged':prior,'IR_manifest_unchanged':True,'new_raw_bytes':port['new_raw_total_bytes'],'free_bytes':shutil.disk_usage(p).free,'numeric_outcomes_or_sequence_bodies_inspected':False,'limit':'Source/provenance/metadata validity only, no EMC biological finding or allpublic deposition census.'},indent=2))
