// node immunosarc_availability.mjs PatientSourceData.txt SampleSourceData.txt
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
function analyzeImmuno(patientText,sampleText) {
 const parse=t=>{const ls=t.trimEnd().split(/\r?\n/),h=ls.shift().split("\t");return ls.map((l,i)=>{const v=l.split("\t");if(v.length!==h.length)throw Error("TSV width "+i);return Object.fromEntries(h.map((k,j)=>[k,v[j]]));});};
 const p=parse(patientText),s=parse(sampleText),unique=v=>new Set(v).size,num=v=>v!==""&&v!=="NA"&&Number.isFinite(Number(v));
 if(unique(p.map(r=>r.Subject))!==p.length||unique(s.map(r=>r.SampleID))!==s.length)throw Error("Duplicate ID");
 if(unique(s.map(r=>r.Subject+"|"+r.SampleTimepoint))!==s.length)throw Error("Duplicate patient-timepoint");
 const pm=new Map(p.map(r=>[r.Subject,r]));
 for(const r of s){const c=pm.get(r.Subject);if(!c)throw Error("Unlinked sample");for(const k of ["PatientID","Cohort","BestResponse","PFSCensor"])if(r[k]!==c[k])throw Error("Join mismatch "+k);if(Math.abs(Number(r["PFS.days"])-Number(c["PFS.days"]))>1e-8)throw Error("PFS mismatch");}
 const immune=["T-cell","T-cell (CD8)","NK cell","B-cell","Macrophage/Monocyte","Myeloid dendritic cell","Neutrophil","Endothelial cell","Cancer-associated fibroblast"], pathways=["Allograft Rejection","Apical Junction","Bile Acid Metabolism","Cholesterol Homeostasis","Complement","Epithelial Mesenchymal Transition","Fatty Acid Metabolism","Hedgehog Signaling","Il6 Jak Stat3 Signaling","Interferon Alpha Response","Kras Signaling Dn","Myc Targets V2","Myogenesis","Peroxisome","Xenobiotic Metabolism"];
 const ihc=["PDL1.IHCquart","CD8.IHCquart","CD68.IHCquart","FOXP3.IHCquart","PD-1.IHCquart"];
 const pred={AnySourceRow:r=>true,RNAImmuneScore:r=>immune.every(k=>num(r[k])),RNAPathwayScore:r=>pathways.every(k=>num(r[k])),CD8IHCQuartile:r=>num(r["CD8.IHCquart"]),AnyIHCQuartile:r=>ihc.some(k=>num(r[k])),AllFiveIHCQuartiles:r=>ihc.every(k=>num(r[k])),WESTMB:r=>num(r.TMB),TCRBetaDiversity:r=>num(r.diversity_TRB)};
 const av=Object.fromEntries(Object.entries(pred).map(([k,f])=>[k,p.map(r=>{const rows=s.filter(x=>x.Subject===r.Subject),b=rows.some(x=>x.SampleTimepoint==="Baseline"&&f(x)),o=rows.some(x=>x.SampleTimepoint==="On-Treatment"&&f(x));return {subject:r.Subject,cohort:r.Cohort,response:r.BestResponse,pfsDays:Number(r["PFS.days"]),event:r.PFSCensor==="1",baseline:b,on:o,paired:b&&o,progression:rows.some(x=>x.SampleTimepoint==="Progression"&&f(x))};})]));
 const count=rs=>({n:rs.length,baseline:rs.filter(r=>r.baseline).length,on:rs.filter(r=>r.on).length,paired:rs.filter(r=>r.paired).length,progression:rs.filter(r=>r.progression).length,baselineWithoutOn:rs.filter(r=>r.baseline&&!r.on).length,onWithoutBaseline:rs.filter(r=>!r.baseline&&r.on).length});
 const assays=Object.fromEntries(Object.entries(av).map(([k,v])=>[k,count(v)]));
 const groups=field=>[...new Set(p.map(r=>r[field]))].sort().map(value=>({[field]:value,n:p.filter(r=>r[field]===value).length,assays:Object.fromEntries(Object.entries(av).map(([k,v])=>[k,count(v.filter(r=>(field==="Cohort"?r.cohort:r.response)===value))]))}));
 const early=av.AnySourceRow.filter(r=>r.event&&r.pfsDays<=21+1e-8);
 const onRNA=av.RNAImmuneScore.filter(r=>r.on),times=[...new Set(onRNA.filter(r=>r.event).map(r=>r.pfsDays))];
 const risk=(t,d)=>onRNA.filter(r=>r.pfsDays-d>=t-d-1e-8).map(r=>r.subject).sort().join(",");
 return {schema:"immunosarc-published-value-audit/1",source_revision:"b71c3373bc182f9c647a6f7bc1fbd641d24db917",scope:"Published analyzable values, not proof assay nonperformance; no identified EMC cohort",integrity:{patientRows:p.length,sampleRows:s.length,matchedSampleRows:s.length,linkedPatientIDs:p.filter(r=>r.PatientID!=="NA").length,duplicates:0,mismatches:0},assayCounts:assays,byCohort:groups("Cohort"),byResponse:groups("BestResponse"),earlyEventsExploratoryDay21:early,hypotheticalCommonShift:[14,21].map(d=>({offsetDays:d,n:onRNA.length,positiveFollowup:onRNA.every(r=>r.pfsDays>d),riskSetsIdentical:times.every(t=>risk(t,0)===risk(t,d))})),assayFlagsUPS:p.filter(r=>r.Cohort==="UPS/MFH/High Grade MFS").map(r=>({subject:r.Subject,IHC:r.IHC})),limitations:["Individual biopsy dates absent; day21 is exploratory, not observed biopsy date.","No causal, efficacy or classifier inference.","Original enrolled84; only77 clinical source rows audited."]};
}
function input(path,expected){const b=readFileSync(path);const actual=createHash("sha1").update(Buffer.from("blob "+b.length+"\0")).update(b).digest("hex");if(actual!==expected)throw Error("Git blob mismatch "+path);return b.toString("utf8");}
console.log(JSON.stringify(analyzeImmuno(input(process.argv[2],"8e65abf4208c2e6d9b96d8271752bfde4c85f443"),input(process.argv[3],"c3d9ee850299eb8930788468c87754b58d5a67f8")),null,2));
