import pathlib,json,hashlib,shutil
B=pathlib.Path(__file__).resolve().parent
checks=[]
def j(n):return json.loads((B/n).read_text())
def c(n,o):checks.append({'check':n,'pass':bool(o)})
for s in j('REUSED-SOURCE-BINDINGS.json')['sources']:
 p=pathlib.Path(s['path']);c('reused '+p.name,p.stat().st_size==s['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256'])
s=j('LOCKED-INPUT-SCHEMAS.json')
for k in ['ARCHS4','USZ23_RefSeq']:
 x=s[k]['source'];p=pathlib.Path(x['path']);c('cachedinput '+k,p.stat().st_size==x['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256'])
c('actualARCHS4headers',s['ARCHS4']['header']==['','GSM2113301','GSM6883080']);c('USZ23actualquantheader',s['USZ23_RefSeq']['header']==['Name','Length','EffectiveLength','TPM','NumReads'])
c('USZ22headerunique',s['USZ22_deposited_rawcounts']['header'].count('USZ-22_EMC2\r')==1);c('USZ22prefixonlyhash',s['USZ22_deposited_rawcounts']['full_source_hash'] is None);c('NMFHduplicatepreserved',s['USZ22_deposited_rawcounts']['header'].count('NMFH-1')==2)
a=j('ANNOTATION-ACCESS.json')+[j('ANNOTATION-SUMMARY-ACCESS.json')]
c('threeannotationonlycalls',len(a)==3)
for x in a:
 p=pathlib.Path(x['cache_path']);c('annotationrawhash '+x.get('name','summary'),p.stat().st_size==x['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']);c('annotation200 '+x.get('name','summary'),x['status']==200 and not x.get('error'))
g=j('OFFICIAL-GENE-LINKAGE.json');c('officialhumanGPNMB',g['gene_identity']['uid']=='10457' and g['gene_identity']['name']=='GPNMB' and g['gene_identity']['organism']['taxid']==9606);c('officiallinkname',g['refseq_linkage']['linkname']=='gene_nuccore_refseqrna')
r=j('CURRENT-GPNMB-REFSEQ-ANNOTATION.json');c('allsevenmetadatarecords',len(r['records'])==7 and len(r['current_human_mRNAs'])==7);c('UIDlistequalofficial',set(x['uid'] for x in r['records'])==set(g['refseq_linkage']['uids']));c('alltitlesexactgene',all('(GPNMB)' in x['title'] and x['taxid']==9606 for x in r['records']));c('twoNMfiveXM',sum(x['accessionversion'].startswith('NM_') for x in r['records'])==2 and sum(x['accessionversion'].startswith('XM_') for x in r['records'])==5)
x=j('ALL-NATIVE-CULTURE-CONDITIONS.json');c('allthreeauthenticplusnativepending',len(x['conditions'])==5 and [z['model'] for z in x['conditions'][:3]]==['V1-34','USZ22','USZ23'])
f=j('READ-SCOPE-AND-PORTABILITY.json');c('zerooutcomequerybodyvalue',f['newexpression_or_sequence_queries']==0 and f['newmatrixbody_reads']==0 and f['newgene_orcellvalues']==0);c('rawunder8MiB',f['newraw_bytes']<=8388608);c('free10GiB',shutil.disk_usage(B).free>=10737418240);d=j('DECISION.json');c('stageoff',d['numerical_stage_authorized'] is False and d['promotion'] is False);c('noexhaustion',d['no_exhaustion'] is True)
(B/'VERIFICATION.json').write_text(json.dumps({'all_pass':all(x['pass'] for x in checks),'checks':checks,'network_calls_in_verifier':0},indent=2)+'\n');assert all(x['pass'] for x in checks);print(str(len(checks))+' source/schema/annotation checks PASS, no network verifier')
