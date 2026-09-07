.libPaths(normalizePath('.cache/R-library'));library(CIFresolve);library(jsonlite)
x<-fromJSON('research/autonomy/ipd-published-baselines-2026-09-06/toy-release.json');out<-list()
for(arm in c('a','b'))for(tol in c(1e-8,1e-6,1e-4,1e-3,1e-2)) {
 a<-x[[arm]];S<-list(time=c(0,a$km[,1],a$tau),surv=c(1,a$km[,2],tail(a$km[,2],1)))
 out[[paste(arm,tol)]]<-tryCatch({f<-KM_resolve(S,a$risk_times,a$risks,ndeath=a$total_events,control=list(constr_tol=tol));list(status='success',fit=unclass(f),ipd=make_data(f))},error=function(e)list(status='failure',error=conditionMessage(e)))
}
write_json(out,'research/autonomy/ipd-published-baselines-2026-09-06/toy-cif-tolerance.json',auto_unbox=TRUE,pretty=TRUE,digits=17)
print(lapply(out,function(x)x[c('status','error')]))
