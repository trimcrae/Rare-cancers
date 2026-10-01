import argparse,collections,datetime,hashlib,json,pathlib,re,urllib.request
FROZEN='d9fc3fc8073104c3f364825972921f271b5e8793eefcf71331c3cff7d3882701'
def unwrap(q):
 for _ in range(10):
  if q.get('schema')=='foundation-identity-partner-sensitivity/1':return q
  if isinstance(q.get('result'),dict):q=q['result']
  elif isinstance(q.get('structuredContent'),dict):q=q['structuredContent']
  elif isinstance(q.get('content'),str):q=json.loads(q['content'])
  elif isinstance(q.get('content'),list):q=json.loads(next(x['text'] for x in q['content'] if x.get('type')=='text'))
  else:raise ValueError('Unrecognized durable wrapper')
 raise ValueError('Wrapper bound')
def get(u):
 with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'EMC-identity-source-reuse-audit/1'}),timeout=45) as r:b=r.read(2*1024*1024+1)
 if len(b)>2*1024*1024:raise ValueError('2MiB bound')
 return b
def main():
 p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--out',default='campaign-output/foundation-identity-corrected');a=p.parse_args();d=pathlib.Path(a.out);d.mkdir(parents=True,exist_ok=True);b=pathlib.Path(a.input).read_bytes();q=unwrap(json.loads(b));m=q['REmapping']['mapping'];assert len(m)==3771;assert q['workbookSHA256']=='88c1a0bab7509ffe3bcff955b89f3d60ddb58a68311cd4c56ca4b0c78506b475';assert any(x.get('sha256')==FROZEN for x in q['sources']);offsets=collections.Counter();same=[];diff=[];non=[]
 for x in m:
  s=x['exportSampleID'].rsplit('-',1)[-1]
  if not re.fullmatch(r'\d+',s):non.append(x);continue
  offsets[int(s)-x['REordinal']]+=1;(same if s==x['sourceID'] else diff).append(x)
 R={'schema':'foundation-rearrangement-ID-proof-corrected/1','sourceArtifact':a.input,'sourceArtifactBytes':len(b),'sourceArtifactSHA256':hashlib.sha256(b).hexdigest(),'originalWorkbookSHA256':q['workbookSHA256'],'frozenExportLFSSHA256':FROZEN,'sourceRows':q['REmapping']['sourceRows'],'exportRows':q['REmapping']['exportRows'],'offsetCounts':dict(offsets),'nonNumericExportSuffixRows':non,'all3771SuffixesEqualSourceREOrdinalPlusThree':offsets=={3:3771} and not non,'literalOriginalSourceIDMatches':len(same),'literalOriginalSourceIDDiscordantRows':len(diff),'discordantUniqueOriginalSourceIDs':len({x['sourceID'] for x in diff}),'discordantUniqueExportIDs':len({x['exportSampleID'] for x in diff}),'literalIDMatches':same,'exactOrderedLiteralGenePairMatches':sum(x['orderedMatch'] for x in m),'literalGenePairDifferences':[x for x in m if not x['orderedMatch']],'EMCSourceIDs':len(q['perEMC']),'EMCRearrangementMapping':[x for x in m if x['sourceID'] in {x['sourceID'] for x in q['perEMC']}],'shortVariantIdentityControl':q['shortVariantIdentityControl'],'exploratoryFourContrastFamily':q['exploratoryFourContrastFamily'],'limits':['Constantordinaloffset/originalID discordance measured for all3771;15literal gene differences not silently normalized.','Discordant IDs count events, not necessarily changed diagnoses.','43SV positivecontrol verifies ID/gene multiplicities only.','Reuse/linkage, not closed classification route.'],'errors':[]};assert R['all3771SuffixesEqualSourceREOrdinalPlusThree'] and len(same)==1 and len(diff)==3770
 try:
  api='https://api.github.com/repos/cBioPortal/datahub/commits/master';meta=get(api);c=json.loads(meta);sha=c['sha'];u='https://raw.githubusercontent.com/cBioPortal/datahub/'+sha+'/public/sarcoma_msk_2022/data_sv.txt';pointer=get(u);s=pointer.decode();oid=re.search(r'^oid sha256:([0-9a-f]{64})$',s,re.M);size=re.search(r'^size (\d+)$',s,re.M);R['latestDatahubHEADPointer']={'headCommit':sha,'commitDate':c['commit']['committer']['date'],'commitMetadataURL':api,'commitMetadataSHA256':hashlib.sha256(meta).hexdigest(),'pointerURL':u,'pointerBytes':len(pointer),'pointerSHA256':hashlib.sha256(pointer).hexdigest(),'literalPointer':s,'LFSOID':oid.group(1) if oid else None,'LFSSize':int(size.group(1)) if size else None,'matchesFrozenLFSObject':bool(oid and size and oid.group(1)==FROZEN and int(size.group(1))==180393)}
 except Exception as e:R['latestDatahubHEADPointer']={'error':type(e).__name__+': '+str(e)}
 R['finishedUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(d/'foundation-ID-proof-corrected.json').write_text(json.dumps(R,indent=2));print(json.dumps(R))
if __name__=='__main__':main()
