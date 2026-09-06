import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const out=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(out,'../../..');
const packet='research/autonomy/recruiting-treatment-difference-2026-09-06/reader/';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const sort=o=>Array.isArray(o)?o.map(sort):o&&typeof o==='object'?Object.fromEntries(Object.keys(o).sort().map(k=>[k,sort(o[k])])):o;
const assert=(b,m)=>{if(!b)throw Error(m)};
const resolve=(o,p)=>p===''?o:p.slice(1).split('/').reduce((v,k)=>v[k.replace(/~1/g,'/').replace(/~0/g,'~')],o);
const manifest=read(packet+'manifest.json');
let checks=[];
for(const [f,k] of [['protocol.md','protocol_sha256'],['disease-anchors.md','disease_anchors_sha256']]){
 assert(sha(fs.readFileSync(path.join(root,packet+f)))===manifest[k],f+' hash');checks.push(f+' SHA256 PASS');
}
assert(manifest.count===8&&manifest.records.length===8,'eight records');
for(const r of manifest.records){
 const b=fs.readFileSync(path.join(root,packet+r.file)),j=JSON.parse(b);
 assert(b.length===r.bytes&&sha(b)===r.raw_sha256&&sha(JSON.stringify(sort(j)))===r.canonical_sha256,r.case_id+' input hashes');
 assert(j.protocolSection.identificationModule.nctId===r.nct_id,r.case_id+' NCT');
 checks.push(r.case_id+' complete JSON parsed; raw/canonical SHA256, byte count, NCT PASS');
}
const labels=JSON.parse(fs.readFileSync(path.join(out,'independent-labels.json'),'utf8'));
const evidence=JSON.parse(fs.readFileSync(path.join(out,'source-evidence.json'),'utf8'));
assert(labels.cases.length===8&&evidence.cases.length===8,'eight outputs');
const required=['case_id','nct_id','source_raw_sha256','label','bounds','route_category','cohorts_checked','same_cohort_rationale','ordinary_requirements','external_criteria_gap','contradictions','cohort_availability','secondary_disease_scope_compatible','rationale','evidence'];
let excerpts=0;
for(let i=0;i<8;i++){
 const c=labels.cases[i],r=manifest.records[i],e=evidence.cases[i];
 assert(required.every(k=>Object.hasOwn(c,k)),c.case_id+' fields');
 assert(c.case_id===r.case_id&&c.nct_id===r.nct_id&&c.source_raw_sha256===r.raw_sha256,'case identity');
 assert(JSON.stringify(c.bounds)===JSON.stringify({positive:[1,1],negative:[0,0],unresolved:[0,1]}[c.label]),'bounds');
 assert(e.case_id===c.case_id&&JSON.stringify(c.evidence)===JSON.stringify(e.evidence),'evidence mirror');
 for(const x of c.evidence){
  assert(x.file===packet+r.file&&typeof x.pointer==='string'&&x.pointer.startsWith('/'),'source pointer');
  const v=resolve(read(x.file),x.pointer);
  assert(typeof v==='string'&&x.excerpt.length>0&&v.includes(x.excerpt),c.case_id+' exact excerpt '+x.pointer);
  assert(typeof x.supports==='string'&&x.supports.length>0,'support');excerpts++;
 }
 assert(c.cohorts_checked.length>0,'cohorts');
 checks.push(c.case_id+' required fields, bounds, mirrored evidence, RFC6901 pointers/excerpts PASS');
}
const receiptPath=path.join(out,'freeze-receipt.json');
if(fs.existsSync(receiptPath)){
 const receipt=JSON.parse(fs.readFileSync(receiptPath,'utf8'));
 for(const [f,h] of Object.entries(receipt.input_sha256))assert(sha(fs.readFileSync(path.join(root,f)))===h,'frozen input '+f);
 for(const [f,h] of Object.entries(receipt.output_sha256))assert(sha(fs.readFileSync(path.join(out,f)))===h,'frozen output '+f);
 checks.push('Frozen input and output hashes PASS');
}
console.log(JSON.stringify({status:'PASS',verified_at_utc:new Date().toISOString(),complete_records:8,exact_pointer_excerpts:excerpts,checks,limitations:'Mechanical verification establishes source integrity and exact excerpts, not scientific correctness, clinical efficacy, safety, eligibility or current cohort places.'},null,2));
