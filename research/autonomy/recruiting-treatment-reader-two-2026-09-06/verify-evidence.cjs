const fs=require('fs'),path=require('path'),crypto=require('crypto');
const out=__dirname, root=path.resolve(out,'../../..'),packet=path.resolve(out,'../recruiting-treatment-difference-2026-09-06/reader');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const check=(condition,message)=>{if(!condition)throw Error(message);};
const canonical=x=>Array.isArray(x)?x.map(canonical):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,canonical(x[k])])):x;
const m=read(path.join(packet,'manifest.json'));
check(m.count===8&&m.records.length===8,'Expected exactly eight records');
const inputs=['manifest.json','protocol.md','disease-anchors.md',...m.records.map(r=>r.file)].map(file=>({file:'research/autonomy/recruiting-treatment-difference-2026-09-06/reader/'+file,sha256:sha(fs.readFileSync(path.join(packet,file)))}));
for(const [f,k] of [['protocol.md','protocol_sha256'],['disease-anchors.md','disease_anchors_sha256']])check(sha(fs.readFileSync(path.join(packet,f)))===m[k],f+' hash');
const docs={};
for(const r of m.records){const b=fs.readFileSync(path.join(packet,r.file));check(b.length===r.bytes,r.case_id+' bytes');check(sha(b)===r.raw_sha256,r.case_id+' raw hash');const d=JSON.parse(b);check(d.protocolSection.identificationModule.nctId===r.nct_id,r.case_id+' NCT');check(sha(JSON.stringify(canonical(d)))===r.canonical_sha256,r.case_id+' canonical hash');docs[r.case_id]=d;}
const labels=read(path.join(out,'independent-labels.json')),source=read(path.join(out,'source-evidence.json'));
check(labels.cases.length===8&&source.cases.length===8,'Output counts');let evidenceCount=0;
const required=['case_id','nct_id','source_raw_sha256','label','bounds','route_category','cohorts_checked','same_cohort_rationale','ordinary_requirements','external_criteria_gap','contradictions','cohort_availability','secondary_disease_scope_compatible','rationale','evidence'];
for(let i=0;i<8;i++){const r=m.records[i],c=labels.cases[i],s=source.cases[i];check(c.case_id===r.case_id&&s.case_id===r.case_id,'Manifest order');check(c.nct_id===r.nct_id&&c.source_raw_sha256===r.raw_sha256,'Case identity');required.forEach(k=>check(Object.hasOwn(c,k),'Missing '+k));check(JSON.stringify(c.evidence)===JSON.stringify(s.evidence),'Evidence output disagreement');check(JSON.stringify(c.bounds)===JSON.stringify({positive:[1,1],negative:[0,0],unresolved:[0,1]}[c.label]),'Bounds');check(c.cohorts_checked.length>0,'No cohorts');for(const e of c.evidence){check(e.file==='research/autonomy/recruiting-treatment-difference-2026-09-06/reader/'+r.file,'Evidence outside own source');check(e.pointer.startsWith('/'),'RFC6901 pointer');let v=docs[r.case_id];for(const t of e.pointer.slice(1).split('/')){check(!/~(?![01])/.test(t),'Invalid pointer escape');const k=t.replace(/~1/g,'/').replace(/~0/g,'~');check(Object.hasOwn(v,k),'Missing pointer');v=v[k];}check(typeof v==='string'&&v===e.excerpt,'Nonverbatim excerpt');check(e.supports.length>0,'Missing support');evidenceCount++;}}
const receiptPath=path.join(out,'freeze-receipt.json');let freezeVerified=false;
if(fs.existsSync(receiptPath)){const receipt=read(receiptPath);for(const h of [...receipt.input_hashes,...receipt.output_hashes])check(sha(fs.readFileSync(path.resolve(root,h.file)))===h.sha256,'Frozen hash '+h.file);freezeVerified=true;}
const result={status:'PASS',verified_at_utc:new Date().toISOString(),records_parsed:8,raw_hashes_verified:8,canonical_hashes_verified:8,bytes_verified:8,protocol_and_anchor_hashes_verified:true,evidence_items_exactly_resolved:evidenceCount,case_schema_and_bounds_verified:true,matching_evidence_outputs:true,freeze_hashes_verified:freezeVerified,input_hashes:inputs,scope_limit:'Mechanical verification of supplied records, identity, required fields, exact evidence pointers/excerpts and hashes; clinical interpretation is the independent reader judgment, not proven by this script.'};
if(process.argv.includes('--write-result'))fs.writeFileSync(path.join(out,'verification-result.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result,null,2));
