import json,pathlib,hashlib,datetime,importlib.util,subprocess
P=pathlib.Path;outdir=P('campaign-output/hagedorn2013-redesigns');outdir.mkdir(parents=True,exist_ok=True)
raw=subprocess.check_output(['git','show','HEAD:research/modalities/junction_aso_thermo.py'])
blob=hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest();assert blob=='500462327ee69b5835ba4d1f798715e71c4765d5'
mp=outdir/'pinned-thermo.py';mp.write_bytes(raw);spec=importlib.util.spec_from_file_location('aso2013_frozen_thermo',mp);model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model);nn,meta=model._nn_table();assert nn is not None
rows=[]
for name,seq,alt,upper in [('seth','TCatggctgcagCT',6.7,None),('r1','TCatggctgcAGC',29.0,None),('r2','ATCatggctgcAGC',None,3.4),('r3','ATCatggctgCAGC',None,3.4)]:
 bases=seq.upper();dna=[i+1 for i,c in enumerate(seq) if c.islower()];lna=[i+1 for i,c in enumerate(seq) if c.isupper()];assert all(c in 'ACGTacgt' for c in seq)
 target=bases.translate(str.maketrans('ACGT','TGCA'))[::-1];dh,ds=model.duplex_enthalpy_entropy(target,nn)
 rows.append({'name':name,'literalSequence':seq,'baseSequence':bases,'length':len(seq),'LNApositions1Based':lna,'DNApositions1Based':dna,'gapDesign':[dna[0]-1,len(dna),len(seq)-dna[-1]],'ALTfoldExactMainProse':alt,'ALTfoldStrictUpperBound':upper,'ALTendpoint':'day16 mouse ALT/saline,5x15mg/kg IV,NMRI,fullyPS;ULN1.7','unmodifiedPerfectTargetSurrogate':{'RNA5to3':target.replace('T','U'),'Tm250nM_C':model._tm(dh,ds,conc_nm=250),'DG37_kcal_mol':model.delta_g37(dh,ds),'chemistryIgnoredByDefinition':True}})
assert [r['gapDesign'] for r in rows]==[[2,10,2],[2,8,3],[3,8,3],[3,7,4]]
assert rows[2]['baseSequence']==rows[3]['baseSequence'] and rows[2]['unmodifiedPerfectTargetSurrogate']==rows[3]['unmodifiedPerfectTargetSurrogate']
rf=[]
for label,counts in [('OOB',[74,18,23,91]),('CVclose',[35,6,7,55]),('CVmedium',[23,6,5,20]),('CVfar',[17,5,10,17]),('doseSelectedValidation',[9,2,4,8])]:
 tp,fp,fn,tn=counts;rf.append({'authorSummary':label,'rowsPredictedHighLow_columnsMeasuredHighLow':[[tp,fp],[fn,tn]],'n':sum(counts),'accuracy':(tp+tn)/sum(counts)})
result={'schema':'exact2013-main-redesign-frozen-proxy/1','executedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':{'PMID':'23952551','PMCID':'PMC3760025','DOI':'10.1089/nat.2013.0436','run_id':36926658121,'job_id':110585637365,'mainHTML_SHA256':'321e2baa5ef304351a867592f3cb4337e7b2ad368c5d23ce1ec94cc616550a4c','Fig4JPEG_SHA256':'d18b76a153798cfa176fdace8637e8b0fb45f6f1022901cbb1dffabc28c26d93','transcription':'MainFig4 sequence/case manually read; exact6.7/29 and strictlowbounds from mainprose; no plotdigitization'},'frozenModelBlob':blob,'tableMetadata':meta,'screenedTotal':236,'extremeALTTrainingSubset':206,'intermediateALTExcluded':30,'independentDoseSelectedValidation':23,'redesignRows':rows,'authorRandomForestSummaryArithmetic':rf,'limits':['4 closely related PTEN redesigns are one sequencefamily, not4 independenttarget tests.','0 measured thermalendpoints in this mainarticle; unmodifiedsurrogates do not validate modifiedTm or predict toxicity.','Both r2/r3 are lowALT; identical proxy here is representational chemistry insensitivity, not demonstrated toxicity misranking.','AuthorRF predictions are author published summaries, not validation of our model.']}
(outdir/'ASO2013-redesign-frozen-proxy.json').write_text(json.dumps(result,indent=2,allow_nan=False))
print('ASO2013_REDIGNS_FROZEN_PROXY_BEGIN');print(json.dumps(result,allow_nan=False));print('ASO2013_REDIGNS_FROZEN_PROXY_END')
