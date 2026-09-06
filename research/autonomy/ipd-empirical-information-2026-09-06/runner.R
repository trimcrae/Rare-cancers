# Actual published package calls; no reconstruction algorithm is reimplemented.
args <- commandArgs(trailingOnly=TRUE)
if (length(args)!=3) stop('usage: Rscript runner.R library-path release.json result.json')
.libPaths(normalizePath(args[1]))
suppressPackageStartupMessages(library(IPDfromKM))
library(CIFresolve)
library(jsonlite)
# survival 3.8.6 leaks an explicit timefix argument into model.frame.
# Change ONLY the default in a local function copy; installed body is identical.
survdiff_exact <- survival::survdiff
formals(survdiff_exact)$timefix <- FALSE
stopifnot(identical(body(survdiff_exact),body(survival::survdiff)))
x <- fromJSON(args[2],simplifyVector=FALSE)
asnum <- function(x) as.numeric(unlist(x))
prepare <- function(a) {
 if(x$schema!='empirical-numerical-release-v1')stop('Unsupported schema')
 list(time=asnum(a$time),surv=asnum(a$surv),trisk=asnum(a$trisk),nrisk=asnum(a$nrisk),n=a$n,events=a$events)
}
inputs<-lapply(list(a=x$a,b=x$b),prepare)
results<-list()
for (method in c('IPDfromKM','CIFresolve')) {
 warns<-character(); start<-proc.time()[['elapsed']]
 ans<-tryCatch(withCallingHandlers({
  ipds<-list(); fit_details<-list()
  for (arm in names(inputs)) {
   d<-inputs[[arm]]
   if(method=='IPDfromKM') {
    prep<-preprocess(data.frame(time=d$time,surv=d$surv),trisk=d$trisk,nrisk=d$nrisk,totalpts=d$n,maxy=1)
    fit<-getIPD(prep,armID=match(arm,names(inputs)),tot.events=d$events)
    ipd<-data.frame(time=fit$IPD$time,event=fit$IPD$status,arm=arm)
    fit_details[[arm]]<-list(preprocessed=prep$preprocessdat,riskmat=fit$riskmat,precision=fit$precision)
   } else {
    fit<-KM_resolve(list(time=d$time,surv=d$surv),t.risk=d$trisk,n.risk=d$nrisk,ndeath=d$events,optmethod='approx')
    dat<-make_data(fit)
    ipd<-data.frame(time=dat$time,event=dat$event,arm=arm)
    fit_details[[arm]]<-unclass(fit)
   }
   if(nrow(ipd)==0||anyNA(ipd)||any(!is.finite(ipd$time))||any(ipd$time<0)||any(!ipd$event %in% c(0,1)))stop('Invalid reconstructed records')
   ipds[[arm]]<-ipd
  }
  joined<-do.call(rbind,ipds)
  lr<-survdiff_exact(Surv(time,event)~arm,data=joined,rho=0)
  if(any(!is.finite(lr$var))||lr$var[1,1]<=0||!is.finite(lr$chisq)||!is.finite(pchisq(lr$chisq,df=1,lower.tail=FALSE)))stop('Unevaluable zero-variance or nonfinite logrank result')
  list(status='success',ipd=joined,logrank_chisq=unname(lr$chisq),logrank_p=pchisq(lr$chisq,df=1,lower.tail=FALSE),fit_details=fit_details)
 },warning=function(w){warns<<-c(warns,conditionMessage(w));invokeRestart('muffleWarning')}),error=function(e)list(status='failure',error=conditionMessage(e)))
 ans$warnings<-warns;ans$elapsed_seconds<-proc.time()[['elapsed']]-start
 results[[method]]<-ans
}
out<-list(schema='published-baseline-results-v1',input_file=args[2],input_schema=x$schema,package_versions=list(IPDfromKM=as.character(packageVersion('IPDfromKM')),CIFresolve=as.character(packageVersion('CIFresolve')),quadprog=as.character(packageVersion('quadprog')),survival=as.character(packageVersion('survival'))),R=R.version.string,inputs=inputs,methods=results)
write_json(out,args[3],pretty=TRUE,auto_unbox=TRUE,digits=17,null='null',na='null')
cat('Output:',args[3],'\n');print(lapply(results,function(v)v[c('status','logrank_p','error','warnings','elapsed_seconds')]))
