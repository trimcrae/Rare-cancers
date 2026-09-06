
CIF_resolve <- function(S, t.risk, n.risk, nevent=NULL,ndeath=NULL,ticks=NULL,totaltime=NULL, totaltime_power=1, c.event=NULL,t.event=NULL,optmethod="approx",nsub=NULL, ltrunc=FALSE,control=control.CIFresolve()) {
  #S should be a list containing $time: times at which the CIF extracted, either $cif: a matrix of CIF values at those times or $Haz: a matrix of cumulative hazard values at those times
  #t.risk = vector of times at which number at risk is known
  #n.risk = vector of numbers at risk
  #nevent = vector of number of events of each type (can be omitted)
  #ndeath = total number of events/deaths across all types (can be omitted)
  #ticks = optional vector of locations of tick marks representing censoring times
  #totaltime = observed/inferred total time at risk or total transformed times at risk (sum t_{i}^pow)
  #totaltime_power = the power by which each of the individual times has been raised in the calculation of totaltime, defaults to 1, potentially useful if the MLEs of the Weibull rate and shape parameters are known.
  #c.event = optional vector or matrix of cumulative number of events; should either be a vector (in which case is interpreted as the cumulative total events) or a matrix where each column represents a given risk
  #t.event = optional vector of times at which number of cumulative events is supplied, if NULL makes t.event=t.risk
  #optmethod = Method of finding the solution: "approx" - solve the continuous QP and then do integer rounding or "miqp" - use full mixed integer QP optimization using Rcplex
  #nsub = total number of subject in the dataset (not equal to n.risk[1] for left truncated data)
  #ltrunc = whether data includes left-truncated observations.
  #control = list of control parameters as specified by control.CIFresolve.
  cumhaz <- !is.null(S$Haz)
  if (!is.null(S$cif) & !is.null(S$Haz)) {
    warning("It is only necessary to supply either the cumulative incidence curves or the cumulative hazards. Haz matrix ignored")
    cumhaz <- FALSE
  }
  if (is.null(S$cif) & !is.null(S$Haz)) {
    S$cif <- S$Haz
  }

  if (!inherits(control,"CIFresolve_control")) {
    if (is.list(control)) {
      if (any(!names(control)%in%names(formals(control.CIFresolve)))) stop("Invalid control argument. See ?control.CIFresolve for details")
      control <- do.call(control.CIFresolve, args=control)
    }else{
      stop("control must be a list containing valid control parameters. See ?control.CIFresolve for details.")
    }
  }
  #Extract all the control parameters out of the control list...
  strict_tick<-control$strict_tick
  strict_dec <- control$strict_dec
  cen_penalty <- control$cen_penalty
  trun_penalty <- control$trun_penalty
  constr_tol <- control$constr_tol
  nprobe <- control$nprobe
  epagap <- control$epagap
  epgap <- control$epgap
  tilim <- control$tilim
  trace <- control$trace
  ttol <- control$ttol
  cen_max <- control$cen_max
  ceventinc <- control$ceventinc
  timeunit <- control$timeunit
  maxdp <- control$maxdp

  if (!is.null(totaltime) & optmethod!="miqp") warning("Total time constraint may not be met in the integer solution when the approximate integer rounding method is used. Use MIQP, if required.")
  if (is.data.frame(S)) stop("S should be a list not a data frame")
  if (!"time"%in%names(S)) stop("S needs to include a component named time")
  if (!"cif"%in%names(S)) stop("S needs to include a component named cif or Haz")

  #Add in some sanity checks
  #####
  S$time <- round(S$time, maxdp)
  if (length(unique(S$time))!=length(S$time)) stop("The time component of S contains duplicate values")
  #####
  if (length(S$time)>1) {
    if (min(diff(S$time))<0) stop("Digitized CIF time points are not in increasing order.")
    for (i in 1:dim(S$cif)[2]) {
      if (max(diff(S$cif[,i]))<0) stop("Digitized CIF curves must be increasing with time.")
    }
  }
  if (!is.null(nsub) & !ltrunc) warning("nsub only relevant for left truncated survival data - argument ignored. Use n.risk at t.risk=0 to define the total number of subjects.")

  origS <- S
  if (!optmethod%in%c("approx","miqp")) stop("Optimization method must either be approx or miqp")

  if (length(unique(n.risk))!=length(n.risk) & !ltrunc) {
    g <- sapply(unique(n.risk), function(x) max(which(n.risk==x)))
    n.risk <- n.risk[g]
    t.risk <- t.risk[g]
  }
  myapproxfun <- function(x,y, method) { suppressWarnings(approxfun(x,y,method=method))}


  if (!is.null(nevent) & !is.null(ndeath)) {
    if (sum(nevent)!=ndeath) stop("nevent disagrees with ndeath: ndeath should give total number of events of all types.")
  }
  if (min(n.risk)>0) {
    #Impute an extra time with zero at risk
    cmax <- max(t.risk)
    mtime <- max(S$time,t.risk,ticks)+timeunit
    t.risk <- c(t.risk,mtime)
    n.risk <- c(n.risk,0)
    if (!is.null(ticks)) {
      if (max(ticks) < cmax) {
        #Add an extra tick point
        ticks <- c(ticks,mtime)
      }
    }
    warning(paste("Number at risk at final time not equal to zero. An additional censoring time was added at time", round(mtime,3),sep=" "))
  }
  last_time <- max(S$time,t.risk,ticks)

  ncomp <- dim(S$cif)[2]
  if (!is.null(nevent)) {
    if (min(nevent)<0) stop("Number of events cannot be negative!")
    if (max(abs(nevent - floor(nevent)))>1e-6) stop("nevent should be integers")
    if (length(nevent)!=ncomp) stop("nevent should give number of events of each type")
  }

  extraS <- list()
  for (i in 1:ncomp) {
    extraS[[i]]<-myapproxfun(c(0,S$time,last_time),c(0,S$cif[,i],max(S$cif[,i])),method="constant")(t.risk)
  }
  miss <- which(!t.risk%in%S$time) #Should work if there are duplicates...
  if (length(miss)>0) {
    S$time <-c(S$time,t.risk[miss])
    CIFmiss <- array(0,c(length(miss),ncomp))
    for (i in 1:ncomp) CIFmiss[,i] <- extraS[[i]][miss]
    S$cif <- rbind(S$cif, CIFmiss)
    S$cif <- S$cif[order(S$time),,drop=FALSE]
    S$time <- sort(S$time)
  }
  if (!is.null(ticks)) {
    extraS2 <- list()
    for (i in 1:ncomp) {
      extraS2[[i]]<-myapproxfun(c(0,S$time,max(ticks,S$time)),c(0,S$cif[,i],max(S$cif[,i])),method="constant")(ticks)
    }
    miss2 <- which(!ticks%in%S$time)
    if (length(miss2)>0) {
      S$time <-c(S$time,ticks[miss2])
      CIFmiss2 <- array(0,c(length(miss2),ncomp))
      for (i in 1:ncomp) CIFmiss2[,i] <- extraS2[[i]][miss2]
      S$cif <-rbind(S$cif, CIFmiss2)
      S$cif <- S$cif[order(S$time),,drop=FALSE]
      S$time <- sort(S$time)
    }
  }

  if (ltrunc) {
    mats <- make_Mats_LT(S, t.risk, n.risk, nsub, nevent, ndeath, ticks, t.event, c.event, totaltime, totaltime_power, ttol, constr_tol, cen_penalty,trun_penalty, strict_tick, strict_dec, ceventinc, cen_max, last_time, ncomp,cumhaz)
  }else{
    mats <- make_Mats(S, t.risk, n.risk, nevent, ndeath, ticks, t.event, c.event, totaltime, totaltime_power, ttol, constr_tol, cen_penalty,strict_tick, strict_dec, ceventinc, cen_max, last_time, ncomp,cumhaz)
  }

  matRed <- reduce_constraints(mats$A,mats$bvec,mats$ncon1 + length(mats$wval) + dim(mats$Aeq)[1])
  #matRed <- reduce_constraints0(mats$A,mats$bvec,mats$ncon1 + length(mats$wval2) + dim(mats$Aeq)[1])
  mats$Astar <- Astar <- matRed$Astar
  mats$bstar <-bstar <- matRed$bstar
  mats$nstar <-nstar <- matRed$nstar

  dvec <- mats$dvec



  Dmat2 <- mats$Q

  Obs <- mats$Obs
  S <- mats$S
  chunk_total <- mats$chunk_total

  if (optmethod=="miqp") {
    #Remove zero constrained variables to reduce total number of variables for Rcplex
    EqCon <- Astar[1:nstar, ]
    bvCon <- bstar[1:nstar]
    numUsed <- apply(EqCon,1,function(x) sum(x!=0))
    canremove <- which(bvCon == 0 & numUsed==1)
    if (length(canremove)>0) {
    varcanremove <- apply(Astar[canremove,],1,function(x) which(x!=0))
    retain <- (1:length(dvec))[-varcanremove]
    dvec2 <- dvec[-varcanremove]
    Astar2 <- (Astar[-canremove,-varcanremove])
    bstar2 <- bstar[-canremove]
    Dmat3 <- Dmat2[-varcanremove,-varcanremove]
    nremov <- length(canremove)
    }else{
    retain <- 1:length(dvec)
    dvec2<-dvec
    Astar2 <- Astar
    bstar2 <- bstar
    Dmat3 <- Dmat2
    nremov <- 0
    }
    qpobj <- Rcplex::Rcplex(cvec=-c(dvec2),Amat=-Astar2,bvec=-bstar2,Qmat=Dmat3,sense=rep(c("E","L"),c(nstar - nremov, length(bstar) - nstar)),lb=0,vtype="I",control=list(round=1,probe=as.integer(nprobe),epagap=epagap,epgap=epgap,tilim=tilim,trace=trace))
    intsol <- solution <- rep(0,length(dvec))
    intsol[retain] <- solution[retain] <- qpobj$xopt

    nevent <- array(0,c(length(S$time),ncomp))
    for (j in 1:ncomp) {
      nevent[,j] <- solution[(1:length(S$time) + (j-1)*length(S$time))]
    }
    intcenevent <- solution[(1+ncomp*length(S$time)):((ncomp+1)*length(S$time))]
    if (ltrunc) inttrunevent <- solution[(1+(ncomp+1)*length(S$time)):((ncomp+2)*length(S$time))]
    int_obj <- qpobj$obj
  }
  if (optmethod=="approx") {
    qpobj <- tryCatch(quadprog::solve.QP(Dmat=Dmat2,dvec=t(dvec),Amat = t(Astar),bvec = bstar,meq=nstar),error=function(e) return(NA))

    if (!is.list(qpobj)) {
      sc <- norm(Dmat2,"2")
      qpobj <- tryCatch(quadprog::solve.QP(Dmat=Dmat2/sc,dvec=t(dvec)/sc,Amat = t(Astar),bvec = add_slack(1e-6,bstar,nstar),meq=nstar),error=function(e) return(NA))
      if (!is.list(qpobj)) stop("Unable to find a feasible solution of QP. Check input data or try increasing constr_tol value.")
    }

    solution <- qpobj$solution
    if (ltrunc) {
      intsol <- integer_round_LT(solution, S, chunk_total, ncomp)
    }else{
      intsol <- integer_round(solution, S, chunk_total, ncomp)
    }
    nevent <- array(0,c(length(S$time),ncomp))
    for (j in 1:ncomp) {
      nevent[,j] <- intsol[(1:length(S$time) + (j-1)*length(S$time))]
    }
    intcenevent <- intsol[(1+ncomp*length(S$time)):((ncomp+1)*length(S$time))]
    if (ltrunc) inttrunevent <- intsol[(1+(ncomp+1)*length(S$time)):((ncomp+2)*length(S$time))]
    int_obj <- -dvec%*%intsol + 0.5*t(intsol)%*%Dmat2%*%intsol
  }
  pen <- 0.5*cen_penalty*sum(intcenevent^2)
  if (ltrunc) {
    data <- data.frame(time=S$time, nevent = nevent, ncen = intcenevent, nenter=inttrunevent, tevent=apply(nevent,1,sum))
    data$nrisk <- cumsum(data$nenter) - c(0,cumsum(data$nevent + data$ncen))[1:length(data$ncen)]
  }else{
    data <- data.frame(time=S$time, nevent = nevent, ncen = intcenevent, tevent=apply(nevent,1,sum))
    data$nrisk <- sum(data$tevent+data$ncen) - cumsum(c(0,data$tevent+data$ncen))[1:dim(data)[1]]
  }
  attr(data,"use_ticks") <- 1*(!is.null(ticks))
  attr(data,"S") <- origS
  attr(data,"c.event") <- !is.null(c.event)
  attr(data,"events") <- data.frame(t.event=t.event, c.event=c.event)
  attr(data,"risks") <- data.frame(t.risk=t.risk,n.risk=n.risk)
  attr(data,"Obs")<-Obs
  attr(data,"object") <- qpobj
  attr(data,"int_obj") <- int_obj
  attr(data,"int_obj_wpen") <- int_obj - pen
  attr(data,"intsol") <- intsol
  attr(data,"mats") <- mats
  attr(data,"ltrunc") <- ltrunc
  attr(data,"cumhaz") <- cumhaz
  class(data) <- "CIFresolve"
  return(data)
}


control.CIFresolve <- function(strict_tick=TRUE,strict_dec=TRUE,cen_penalty=1e-3,trun_penalty=1e-3,constr_tol=1e-8,nprobe=0,epagap=1e-6,epgap=1e-4,tilim=100,trace=1,ttol=0.001,cen_max=NULL,ceventinc=FALSE,timeunit=1,maxdp=8) {
  #Some basic checks on the control inputs.
  if (!is.logical(strict_tick)) stop("strict_tick must be a logical")
  if (!is.logical(strict_tick)) stop("strict_dec must be a logical")
  if (!is.logical(ceventinc)) stop("ceventinc must be a logical")
  if (!is.numeric(cen_penalty)) stop("cen_penalty must be numeric")
  if (!is.numeric(trun_penalty)) stop("trun_penalty must be numeric")
  if (!is.numeric(constr_tol)) stop("constr_tol must be numeric")
  if (!is.numeric(epagap)) stop("epagap must be numeric")
  if (!is.numeric(epgap)) stop("epgap must be numeric")
  if (!is.numeric(tilim)) stop("tilim must be numeric")
  if (!is.numeric(ttol)) stop("ttol must be numeric")
  if (!is.numeric(cen_penalty)) stop("cen_penalty must be numeric")
  if (!is.numeric(timeunit)) stop("time_unit must be numeric")
  if (cen_penalty <0 ) stop("cen_penalty must be positive")
  if (constr_tol <0 ) stop("constr_tol must be positive")
  if (epagap <0 ) stop("epagap must be positive")
  if (epgap <0 ) stop("epgap must be positive")
  if (tilim <0) stop("tilim must be positive")
  if (ttol <0) stop("ttol must be positive")
  if (timeunit <=0) stop("time_unit must be positive")
  if (!is.null(cen_max)) {
    if (!is.numeric(cen_max)) stop("cen_max must be numeric, if supplied")
    if (cen_max < 1) stop("cen_max must be greater than or equal to 1.")
  }
  if (!is.numeric(maxdp)) stop("maxdp must be numeric")
  if (maxdp <0) stop("maxdp must be positive")
  control_list <- list(strict_tick=strict_tick, strict_dec=strict_dec,cen_penalty=cen_penalty,trun_penalty=trun_penalty,constr_tol=constr_tol,nprobe=nprobe,epagap=epagap,epgap=epgap,tilim=tilim,trace=trace,ttol=ttol,cen_max=cen_max,ceventinc=ceventinc,timeunit=timeunit,maxdp=maxdp)
  class(control_list) <- "CIFresolve_control"
  return(control_list)
}



KM_resolve <- function(S, t.risk, n.risk, ndeath=NULL,ticks=NULL,totaltime=NULL,totaltime_power=1, c.event=NULL, t.event=NULL, optmethod="approx",nsub=NULL, ltrunc=FALSE, control=control.CIFresolve()) {
  #Wrapper function that just uses the CIF method (should be equivalent in the case of one risk)
  #S: a list containing $time: times KM extracted, $surv: KM values at those times
  #t.risk = vector of times at which number at risk is known
  #n.risk = vector of numbers at risk
  #ndeath = total number of events/deaths (can be omitted)
  #ticks = optional vector of locations of tick marks representing censoring times
  #totaltime = observed/inferred total time at risk or total transformed times at risk (sum t_{i}^pow)
  #totaltime_power = the power by which each of the individual times has been raised in the calculation of totaltime, defaults to 1, potentially useful if the MLEs of the Weibull rate and shape parameters are known.
  #c.event = optional vector of cumulative number of events at the t.event values
  #t.event = optional vector of times at which number of cumulative events is supplied, if NULL makes t.event=t.risk
  #optmethod = Method of finding the solution: "approx" - solve the continuous QP and then do integer rounding or "miqp" - use full mixed integer QP optimization using Rcplex
  #nsub = optional scalar specifying the total number of subjects, only used if ltrunc=TRUE
  #ltrunc = logical determining whether the estimate comes from left-truncated data.
  #control = optional list of additional control parameters. See control.CIFresolve for more details.
  if (!inherits(control,"CIFresolve_control")) {
    if (is.list(control)) {
      if (any(!names(control)%in%names(formals(control.CIFresolve)))) stop("Invalid control argument. See ?control.CIFresolve for details")
      control <- do.call(control.CIFresolve, args=control)
    }else{
      stop("control must be a list containing valid control parameters. See ?control.CIFresolve for details.")
    }
  }
  if (is.data.frame(S)) S <- list(time=S$time,surv=S$surv,Haz=S$Haz)
  if (!is.null(ndeath) & !is.null(c.event)) {
    if (max(c.event) > ndeath) {
      stop("Cumulative events in c.event contradict total events in ndeath.")
    }
  }
  #Add some sanity checks to the data inputs:
  if (min(diff(S$time))<0) stop("Digitized survival time points are not in increasing order.")
  cumhaz <- !is.null(S$Haz)
  if (!is.null(S$surv) & !is.null(S$Haz)) {
      warning("Only one of surv or Haz required. Haz will be ignored")
      S$Haz <- NULL
  }
  if (is.null(S$surv) & !is.null(S$Haz)) {
      if (max(diff(S$Haz)) <0) stop("Digitized cumulative hazard curve is not increasing in time.")
      S$Haz <- cbind(S$Haz)
  }
  if (is.null(S$Haz) & !is.null(S$surv)) {
      if (max(diff(S$surv))>0) stop("Digitized survival curve is not decreasing in time.")
      S$cif <- cbind(1- S$surv)
  }
  output <- CIF_resolve(S, t.risk, n.risk, nevent=NULL,ndeath,ticks,totaltime,totaltime_power,c.event, t.event, optmethod,nsub,ltrunc,control)
  #Translate this output into the standard output (need to retain attributes)
  int_obj <- attr(output,"int_obj")
  status <- attr(output,"object")$status
  names(output)[names(output)=="nevent.1"]<-"nevent"
  #output <- output[,-which(names(output)=="tevent")]
  attr(output,"int_obj") <- int_obj
  attr(output,"status") <- status
  class(output) <- "KMresolve"
  return(output)
}




#Auxiliary function to do the integer rounding of the continuous solution.
integer_round_LT <- function(solution, S, chunk_total, ncomp) {
  nevent <- array(0,c(length(S$time),ncomp))
  for (j in 1:ncomp) {
    nevent[,j] <- diff(c(0,floor(round(cumsum(solution[(1:length(S$time) + (j-1)*length(S$time))]),5)+0.5)))
  }
  ##############
  ntrunc <- diff(c(0,floor(round(cumsum(solution[(1:length(S$time) + (ncomp+1)*length(S$time))]),5)+0.5)))
  ##############
  tevent <- apply(nevent,1,sum)
  cenevent <- pmax(0,solution[(1+ncomp*length(S$time)):((ncomp+1)*length(S$time))])
  ######

  cen_needed <- chunk_total - tapply(tevent, factor(S$chunk),sum) + sapply(1:max(S$chunk), function(x) sum(ntrunc[S$chunk3==x]))
  #######
  cur_cen <-  round(tapply(cenevent, S$chunk,sum),8)
  newcenevent <- cenevent * rep(cen_needed,table(S$chunk))/rep(cur_cen + 1*(cur_cen==0),table(S$chunk))
  intcenevent <- diff(c(0,floor(round(cumsum(newcenevent),5)+0.5)))
  intsol <- c(nevent,intcenevent,ntrunc)
  return(intsol)
}


make_Mats_LT <- function(S, t.risk, n.risk, nsub, nevent, ndeath, ticks, t.event, c.event, totaltime, totaltime_power, ttol, constr_tol, cen_penalty,trun_penalty, strict_tick, strict_dec, ceventinc, cen_max, last_time, ncomp, cumhaz) {
  #Needs an extra argument nsub to account for the total sample size (here that is definitely not the same as n.risk[1])

  #Version for left-truncated survival/competing risks
  #Assume we have a vector of length: length(S$time)*(ncomp + 2), where the last part corresponds to the number of patients entering at each time.


  #For number at risk assume is number at risk at time t (i.e. before events occurred)
  S$chunk <- sapply(S$time,function(x) sum(t.risk <= x))
  S$chunk3 <- sapply(S$time,function(x) sum(t.risk < x))

  #For cumulative events assume number includes those that happened at time t
  if (last_time%in%ticks) {
    if (S$chunk[length(S$chunk)] > S$chunk[(length(S$chunk)-1)]) S$chunk[length(S$chunk)] <- S$chunk[(length(S$chunk)-1)]
  }
  chunk_total <- -diff(c(n.risk,0))
  if (!is.null(c.event)) {
    if (is.null(t.event)) t.event <- t.risk

    #Set up the chunks for cumulative events
    if (identical(t.event, t.risk) & !ceventinc) {
      S$chunk2 <- S$chunk
    }else{
      if (ceventinc) {
        S$chunk2 <- sapply(S$time,function(x) sum(t.event < x))
      }else{
        S$chunk2 <- sapply(S$time,function(x) sum(t.event <= x))
      }
    }
    if (is.vector(c.event)) {
      chunk_event_totals <- NULL
      chunk_event_total <- diff(c(c.event,c.event[length(c.event)]))
    }else{
      chunk_event_total <- NULL
      chunk_event_totals <- apply(c.event, 2, function(x) diff(c(x,x[length(x)])))
    }
  }else{
    chunk_event_total <- chunk_event_totals <- NULL
  }

  #Need to do something about chunks of zero length
  if (max(S$chunk) < length(chunk_total)) {
    chunk_total <- chunk_total[1:max(S$chunk)]
  }

  if (!is.null(chunk_event_total)) {
    if (max(S$chunk2) < length(chunk_event_total)) {
      chunk_event_total <- chunk_event_total[1:max(S$chunk2)]
    }
  }
  if (!is.null(chunk_event_totals)) {
    if (max(S$chunk2) < dim(chunk_event_totals)[1]) {
      chunk_event_totals <- chunk_event_totals[1:max(S$chunk2),]
    }
  }

  if (!cumhaz) {
  S$surv <- 1 - apply(S$cif,1,sum)

  Obs <- (S$cif - rbind(rep(0,ncomp),S$cif[1:c(dim(S$cif)[1]-1),,drop=FALSE]))/array(c(1,S$surv[1:(length(S$surv)-1)]),dim=dim(S$cif))
  Obs <- replace(Obs,which(is.nan(Obs)),0) #Remove NaN's which should be due to 0s going to 0s.
  }else{
  Obs <-sapply(1:ncomp, function(x) diff(c(0,S$cif[,x])))
  #if (ncomp==1) Obs <- cbind(Obs)
  }

  decs <- which(Obs >0)
  #Set up the objective matrix


  B <- array(0,c(ncomp*length(S$time),(ncomp+2)*length(S$time)))
  for (j in 1:ncomp) {
    #d_ij terms
    B[cbind((1:length(S$time) + (j-1)*length(S$time)),(1:length(S$time) + (j-1)*length(S$time)))]<- -1
    #Entries into the dataset
    B[cbind((1:length(S$time) + (j-1)*length(S$time)),(1:length(S$time) + (ncomp+1)*length(S$time)))]<- Obs[,j]
    for (i in 2:length(S$time)) {
      for (k in 1:(ncomp+1)) {
        B[i + (j-1)*length(S$time),(1:(i-1) + (k-1)*length(S$time))]<- -Obs[i,j]
      }
      #Entries into the dataset
      B[i + (j-1)*length(S$time),(1:(i-1) + (ncomp+1)*length(S$time))]<- Obs[i,j]
    }
  }
  Dmat <- t(B)%*%B
  dvec <- rep(0, (ncomp+2)*length(S$time)) #n.risk[1]* t(c(Obs))%*%B

  event_totals <- nevent
  event_total <- ndeath

  #Five possibilities
  #i) No event info: nchunk
  #ii) Just total deaths: nchunk + 1
  #iii) Total of each event: nchunk + ncomp
  #iv) Chunked total deaths: nchunk + nchunk2
  #v) Chunked total for each event: nchunk + (ncomp)*nchunk2
  chunkscenario <- 1*(is.null(chunk_event_total) & is.null(chunk_event_totals) & is.null(event_totals) & is.null(event_total)) +2*(is.null(chunk_event_total) & is.null(chunk_event_totals) & is.null(event_totals) & !is.null(event_total))+3*(is.null(chunk_event_total) & is.null(chunk_event_totals) & !is.null(event_totals))+4*(!is.null(chunk_event_total) & is.null(chunk_event_totals)) + 5*(!is.null(chunk_event_totals))

  #Set up the constraint matrix:

  #Each chunk needs two constraints
  nchunk <- length(unique(S$chunk))
  if (chunkscenario%in%c(4,5)) {
    nchunk2 <- max(S$chunk2)
  }else{
    nchunk2 <- 0
  }
  nconstrE <- 2 + c(nchunk, nchunk+1,nchunk+ncomp,nchunk+nchunk2,nchunk + (ncomp)*nchunk2)[chunkscenario] #Extra constraint corresponding to l_1=N_0 and l_N=0

  Aeq <- array(0,c(nconstrE,(ncomp+2)*length(S$time)))
  Beq <-rep(0,nconstrE)
  for (i in 1:nchunk) {
    mm <- which(S$chunk==i)
    for (j in 1:ncomp) {
      mm <- c(mm,which(S$chunk==i)+j*length(S$time))
    }
    Aeq[i,mm] <- 1
    ####Add in the truncation entries
    incl <- (which(S$chunk==i) +1)
    incl <- incl[incl <= length(S$time)]
    mm2 <- incl +(ncomp+1)*length(S$time)
    Aeq[i, mm2] <- -1
    Beq[i] <- chunk_total[i]
  }

  if (chunkscenario==2) {

    for (j in 1:ncomp) {
      Aeq[nchunk+1,((1:length(S$time))+(j-1)*length(S$time))]<-1
    }
    Beq[nchunk+1] <- event_total
  }
  if (chunkscenario==3) {
    for (j in 1:ncomp) {
      Aeq[nchunk+j,((1:length(S$time))+(j-1)*length(S$time))]<-1
      Beq[nchunk+j]<-event_totals[j]
    }
  }
  if (chunkscenario==4) {

    for (i in 1:nchunk2) {
      mm <- which(S$chunk2==i)
      if (ncomp >1) {
        for (j in 1:(ncomp-1)) {
          mm <- c(mm,which(S$chunk2==i)+j*length(S$time))
        }
      }
      Aeq[nchunk+i,mm] <- 1
      Beq[nchunk+i] <- chunk_event_total[i]
    }

  }
  if (chunkscenario==5) {

    for (j in 1:ncomp) {
      for (i in 1:nchunk2) {
        mm <- which(S$chunk2==i) + (j-1)*length(S$time)
        Aeq[(nchunk+i+(j-1)*nchunk2),mm] <- 1
        Beq[(nchunk+i+(j-1)*nchunk2)] <- chunk_event_totals[i,j]
      }
    }
  }

  #Note that end up with specifically setting l_1 =R_0
  #The following implicitly assumes that t.risk[1]=0
  Aeq[ (nconstrE-1), 1 + (ncomp+1)*length(S$time)] <- 1
  Beq[(nconstrE-1)] <- n.risk[1]
  #Also want to force there to be no one entering after everyone is supposed to not be at risk...
  Aeq[ nconstrE, (ncomp+2)*length(S$time)] <- 1
  Beq[nconstrE] <- 0

  if (!is.null(nsub)) {
    #Add additional constraints on the total number of events to correspond to the total number of subjects
    AeqA <- array(0, c(2, (ncomp+2)*length(S$time)))
    AeqA[1, 1:((ncomp+1)*length(S$time))] <- 1
    AeqA[2, ((ncomp+1)*length(S$time) + 1:length(S$time))] <-1
    BeqA <- c(nsub,nsub)

    nconstrE <- nconstrE+2
    Aeq <- rbind(Aeq,AeqA)
    Beq <- c(Beq,BeqA)
  }

  #Only penalize the censoring times
  Dmat2 <- Dmat + diag(c(rep(c(0,cen_penalty,0),c(ncomp*length(S$time),length(S$time),length(S$time)))))
  #Also penalize truncation times.
  Dmat2 <- Dmat2 + diag(c(rep(c(0,trun_penalty),c((ncomp+1)*length(S$time),length(S$time)))))

  #Force any points with no observed decrement to have decrement 0.
  excl <- NULL
  for (j in 1:ncomp) {
    wvalj <- which(Obs[,j] == 0)
    if (j==1) {
      Aeq4 <- array(0,c(length(wvalj),(ncomp+2)*length(S$time)))
      Aeq4[cbind(1:length(wvalj),wvalj)]<-1
    }else{
      Aj <- array(0,c(length(wvalj),(ncomp+2)*length(S$time)))
      Aj[cbind(1:length(wvalj),wvalj + (j-1)*length(S$time))]<-1
      Aeq4 <- rbind(Aeq4,Aj)
    }
    excl <- c(excl, wvalj + (j-1)*length(S$time))
  }
  ncon1 <- dim(Aeq4)[1]


  #Need to also assume the total number of patients at risk is greater than 0 at all times
  Aeq7 <- array(0, c(length(S$time), (ncomp+2)*length(S$time)))
  Aeq7[1,1 + (ncomp+1)*length(S$time)] <- 1
  for (i in 2:length(S$time)) {
    for (j in 1:(ncomp+1)) Aeq7[i,(1:(i-1)) + (j-1)*length(S$time)] <- -1
    Aeq7[i, (1:i) + (ncomp+1)*length(S$time)] <-1
  }


  if (!is.null(ticks)) {
    wval2 <- which(!S$time %in% ticks)
    Aeq5 <- array(0,c(length(wval2),(ncomp+2)*length(S$time)))
    Aeq5[cbind(1:length(wval2),(wval2 + ncomp*length(S$time)))]<-1

    Aeq2 <- diag((ncomp+2)*length(S$time))
    Beq2 <- rep(0,dim(Aeq2)[1])

    if (strict_tick) {
      wval3 <- which(S$time %in% ticks)
      Beq2[(wval3 + (ncomp)*length(S$time))] <- 1-constr_tol #avoid method thinking no solution
    }
    excl <- c(excl, wval2 + ncomp*length(S$time))
    decI <- 1*(strict_dec)*(1:((ncomp+2)*length(S$time)) %in% decs)[-excl]
    decS <- pmax(decI*(1-constr_tol), Beq2[-excl])
    Aeq2 <- Aeq2[-excl,]
    Aeq3 <- rbind(Aeq,Aeq2)
    Aeq6 <- rbind(Aeq4,Aeq5,Aeq3,Aeq7)
    Beq3 <- c(rep(0,ncon1+length(wval2)),Beq,decS,rep(0, length(S$time)))
  }else{
    Aeq2 <- diag((ncomp+2)*length(S$time))
    decI <- 1*(strict_dec)*(1:((ncomp+2)*length(S$time)) %in% decs)[-excl]
    Aeq2 <- Aeq2[-excl,]
    wval2 <- NULL
    Aeq3 <- rbind(Aeq,Aeq2)
    Aeq6 <-   rbind(Aeq4,Aeq3,Aeq7)
    Beq3 <- c(rep(0,ncon1),Beq,decI*(1-constr_tol),rep(0, length(S$time))) #Force any decrement to be associated with at least one event
  }


  if (!is.null(totaltime)) {
    if (!is.numeric(totaltime)) stop("totaltime needs to be a numeric scalar corresponding to the total patient time at risk")
    #Need to add two more inequality constraints
    #If ticks supplied assume censoring is at the times themselves.
    #Otherwise take midpoint between the time and the next time
    if (is.null(ticks)) {
      cenpoints <- (S$time + c(S$time,S$time[length(S$time)])[2:(length(S$time)+1)])*0.5
    }else{
      cenpoints <- S$time
    }
    ###NB: total time power won't work properly under left truncation.
    #For now assume the truncation times are exact
    Aeq7 <- rbind(c(rep(S$time^totaltime_power, ncomp),cenpoints^totaltime_power, -S$time^totaltime_power),c(-rep(S$time^totaltime_power, ncomp),-cenpoints^totaltime_power,S$time^totaltime_power))
    Aeq6 <- rbind(Aeq6,Aeq7)
    Beq3 <- c(Beq3, totaltime*(1-ttol), -totaltime*(1+ttol))
  }
  if (!is.null(cen_max)) {
    Aeq8 <- array(0,c(length(S$time)*(ncomp + 1), length(S$time)))
    Aeq8[cbind((ncomp*length(S$time) +1):((ncomp+1)*length(S$time)),1:length(S$time))] <- 1
    Aeq6 <- rbind(Aeq6,Aeq8)
    Beq3 <- c(Beq3, rep(cen_max, length(S$time)))
  }

  return(list(dvec=dvec, Q=Dmat2, A=Aeq6, bvec=Beq3, wval=wval2, ncon1=ncon1, Aeq=Aeq, Obs=Obs, S=S, chunk_total=chunk_total))
}



print.CIFresolve <- function(x,...) {
  print(as.data.frame(lapply(x,as.vector)))
}

print.KMresolve <- function(x,...) {
  print(as.data.frame(lapply(x,as.vector)))
}


plot.CIFresolve <- function(x,...) {
  cumhaz <- attr(x,"cumhaz")
  cif <- x
  S <- attr(cif,"S")
  ncomp <- dim(S$cif)[2]
  opar <- par(no.readonly =TRUE)
  on.exit(par(opar))
  if (attr(cif,"c.event")) {
    par(mfrow=c(1,3))
  }else{
    par(mfrow=c(1,2))
  }
  ylabname <- "CIF"
  ymax <- 1
  if (cumhaz) {
    ylabname <- "H(t)"
    ymax <- max(S$cif)
  }
  plot(S$time,S$cif[,1],xlab="Time",ylab=ylabname,lty=2,type="s",ylim=c(0,ymax))
  if (ncomp > 1) {
    for (j in 2:ncomp) {
      lines(S$time,S$cif[,j],type="s",col=j,lty=2)
    }
  }
  if (!cumhaz) {
    KM_l <- c(1,cumprod(1-cif$tevent/cif$nrisk))[1:length(cif$nrisk)]
    CIF <- list()
    if (ncomp>1) {
      for (j in 1:ncomp) {
        CIF[[j]] <- cumsum(cif[[paste("nevent",j,sep=".")]]/cif$nrisk * KM_l)
        lines(cif$time,CIF[[j]],type="s",col=j)
      }
    }else{
      CIF <- cumsum(cif$nevent/cif$nrisk * KM_l)
      lines(cif$time,CIF,type="s")
    }
  }else{
    ###############
    CIF <- list()
    if (ncomp>1) {
      for (j in 1:ncomp) {
        CIF[[j]] <- cumsum(cif[[paste("nevent",j,sep=".")]]/cif$nrisk)
        lines(cif$time,CIF[[j]],type="s",col=j)
      }
    }else{
      CIF <- cumsum(cif$nevent/cif$nrisk)
      lines(cif$time,CIF,type="s")
    }

  }
  if (!cumhaz) {
  legend("topright",lty=c(1,2),legend=c("Reconstruction","Original"),bty="n")
  }else{
  legend("bottomright",lty=c(1,2),legend=c("Reconstruction","Original"),bty="n")
  }
  plot(cif$time,cif$nrisk,type="s",xlab="Time",ylab="Number at risk")
  points(attr(cif,"risks")$t.risk,attr(cif,"risks")$n.risk,pch=16)

  if (attr(cif,"c.event")) {
    #Additional panel for cumulative events.
    j <- dim(attr(cif,"events"))[2]
    if (j==2) {
      #Plot cumulative total events
      plot(cif$time, cumsum(cif$tevent),type="s",xlab="Time",ylab="Cumulative total events")
      points(attr(cif,"events")$t.event, attr(cif,"events")$c.event,pch=16)
    }else{
      plot(cif$time, cumsum(cif$nevent.1),type="s",xlab="Time",ylab="Cumulative events")
      points(attr(cif,"events")$t.event,attr(cif,"events")[,2],pch=16)
      for (j in 2:ncomp) {
        lines(cif$time, cumsum(cif[[paste("nevent",j,sep=".")]]),type="s",col=j)
        points(attr(cif,"events")$t.event,attr(cif,"events")[,(j+1)],col=j,pch=16)
      }
      #Plot cumulative events for each risk
    }
  }

}


######THESE NEED ADAPTING TO ACCOMMODATE LEFT-TRUNCATION

plot.KMresolve <- function(x,...) {
  km <- x
  S <- attr(km,"S")
  opar <- par(no.readonly =TRUE)
  on.exit(par(opar))
  if (attr(km,"c.event")) {
    par(mfrow=c(1,3))
  }else{
    par(mfrow=c(1,2))
  }
  ylabname <- "S(t)"
  ymax <- 1
  if (attr(x,"cumhaz")) {
    ylabname <- "H(t)"
    ymax <- max(S$cif)
  }

  if (!attr(x,"cumhaz")) {
    plot(S$time,S$surv,xlab="Time",ylab=ylabname,lty=2,type="s",ylim=c(0,ymax))
    KM <- cumprod(1-km$tevent/km$nrisk)
    legend("topright",lty=c(1,2),legend=c("Reconstruction","Original"),bty="n")
  }else{
    plot(S$time,S$Haz,xlab="Time",ylab=ylabname,lty=2,type="s",ylim=c(0,ymax))
    KM <- cumsum(km$tevent/km$nrisk)
    legend("bottomright",lty=c(1,2),legend=c("Reconstruction","Original"),bty="n")
  }
  lines(km$time,KM,type="s")

  plot(km$time,km$nrisk,type="s",xlab="Time",ylab="Number at risk")
  points(attr(km,"risks")$t.risk,attr(km,"risks")$n.risk,pch=16)

  if (attr(km,"c.event")) {
    plot(km$time,cumsum(km$nevent),type="s",xlab="Time",ylab="Cumulative events")
    points(attr(km,"events")$t.event,attr(km,"events")$c.event,pch=16)
  }
}




#Function for creating the correct CIF list from individual cif
align_CIF <- function(..., res_digits=4) {
  #Supply one or more lists containing named vectors "time" and "cif"
  #Will convert into a list with "time" and a matrix "cif"
  lists <- list(...)
  for (i in 1:length(lists)) {
    lists[[i]]$time <- round(lists[[i]]$time,res_digits)
  }
  all_times <- unique(sort(unlist(sapply(lists, function(x) x$time))))
  if (min(all_times) >0) {
    all_times <- c(0,all_times)
  }
  cif <- array(0,c(length(all_times),length(lists)))
  for (i in 1:length(lists)) {
    mm <- sapply(all_times, function(x) sum(lists[[i]]$time <= x))
    cif[cbind(which(mm!=0),i)] <- lists[[i]]$cif[mm[which(mm!=0)]]
  }
  return(list(time=all_times,cif=cif))
}



#Auxiliary function to add in the omitted values to the list
make_S_list <- function(time, surv, t.risk, n.risk, ndeath=NULL, ticks=NULL, totaltime=NULL, totaltime_power=1, c.event=NULL, t.event=NULL) {
  return(list(S=list(time=time,surv=surv, cif=cbind(1-surv)), t.risk=t.risk, n.risk=n.risk, ndeath=ndeath, ticks=ticks, totaltime=totaltime, totaltime_power=totaltime_power, c.event=c.event, t.event=t.event, origS=list(time=time,surv=surv, cif=cbind(1-surv))))
}

#Function for reconstructing PFS and OS data in a consistent way, assuming common right censoring.
PFS_OS_resolve <- function( PFS_list, OS_list, optmethod="approx", control=control.CIFresolve()) {

  if (!inherits(control,"CIFresolve_control")) {
    if (is.list(control)) {
      if (any(!names(control)%in%names(formals(control.CIFresolve)))) stop("Invalid control argument. See ?control.CIFresolve for details")
      control <- do.call(control.CIFresolve, args=control)
    }else{
      stop("control must be a list containing valid control parameters. See ?control.CIFresolve for details.")
    }
  }
  #Extract all the control parameters out of the control list...
  strict_tick<-control$strict_tick
  strict_dec <- control$strict_dec
  cen_penalty <- control$cen_penalty
  constr_tol <- control$constr_tol
  nprobe <- control$nprobe
  epagap <- control$epagap
  epgap <- control$epgap
  tilim <- control$tilim
  trace <- control$trace
  ttol <- control$ttol
  cen_max <- control$cen_max
  ceventinc <- control$ceventinc
  timeunit <- control$timeunit


  #PFS_list: List that must contain time, surv, t.risk, n.risk, and can also include ndeath, ticks, totaltime, totaltime_power, c.event, t.event
  #OS_list: As PFS_list
  #Same parameters as before

  myapproxfun <- function(x,y, method) { suppressWarnings(approxfun(x,y,method=method))}


  if (any(!names(PFS_list)%in%names(formals(make_S_list)))) stop("Invalid list names for PFS_list")
  if (any(!names(OS_list)%in%names(formals(make_S_list)))) stop("Invalid list names for OS_list")

  PFS_list <- do.call(make_S_list, args=PFS_list)
  OS_list <- do.call(make_S_list, args=OS_list)
  #Check tick points are admissible
  if (!is.null(PFS_list$ticks) & !is.null(PFS_list$ticks)) {
    if(any(!PFS_list$ticks %in% OS_list$ticks)) {
      stop("The marked censoring times for PFS should be a subset of those for OS")
    }
  }

  if (length(unique(PFS_list$n.risk))!=length(PFS_list$n.risk)) {
    #Retain only the later time with the same numbers at risk.
    g <- sapply(unique(PFS_list$n.risk), function(x) max(which(PFS_list$n.risk==x)))
    PFS_list$n.risk <- PFS_list$n.risk[g]
    PFS_list$t.risk <- PFS_list$t.risk[g]
  }

  if (length(unique(OS_list$n.risk))!=length(OS_list$n.risk)) {
    #Retain only the later time with the same numbers at risk.
    g <- sapply(unique(OS_list$n.risk), function(x) max(which(OS_list$n.risk==x)))
    OS_list$n.risk <- OS_list$n.risk[g]
    OS_list$t.risk <- OS_list$t.risk[g]
  }

  if (!is.null(PFS_list$nevent) & !is.null(PFS_list$ndeath)) {
    if (sum(PFS_list$nevent)!=PFS_list$ndeath) stop("PFS nevent disagrees with ndeath: ndeath should give total number of events of all types.")
  }

  if (!is.null(OS_list$nevent) & !is.null(OS_list$ndeath)) {
    if (sum(OS_list$nevent)!=OS_list$ndeath) stop("PFS nevent disagrees with ndeath: ndeath should give total number of events of all types.")
  }

  pfs_n <- PFS_list$n.risk[sapply(OS_list$t.risk, function(x) min(which(PFS_list$t.risk >= x)))]
  if (any(pfs_n > OS_list$n.risk)) {
    stop("The number of PFS patients at risk should not exceed the number of OS patients at risk for any time.")
  }

  if (!optmethod%in%c("approx","miqp")) stop("Optimization method must either be approx or miqp")

  if (min(PFS_list$n.risk)>0) {
    #Impute an extra time with zero at risk
    PFScmax <- max(PFS_list$t.risk)
    PFS_list$t.risk <- c(PFS_list$t.risk,max(PFS_list$S$time,PFS_list$t.risk,PFS_list$ticks)+1)
    PFS_list$n.risk <- c(PFS_list$n.risk,0)
    if (!is.null(PFS_list$ticks)) {
      if (max(PFS_list$ticks) < PFScmax) {
        #Add an extra tick point
        PFS_list$ticks <- c(PFS_list$ticks,max(PFS_list$S$time,PFS_list$t.risk,PFS_list$ticks)+1)
      }
    }
  }
  if (min(OS_list$n.risk)>0) {
    #Impute an extra time with zero at risk
    OScmax <- max(OS_list$t.risk)
    OS_list$t.risk <- c(OS_list$t.risk,max(OS_list$S$time,OS_list$t.risk,OS_list$ticks)+1)
    OS_list$n.risk <- c(OS_list$n.risk,0)
    if (!is.null(OS_list$ticks)) {
      if (max(OS_list$ticks) < OScmax) {
        #Add an extra tick point
        OS_list$ticks <- c(OS_list$ticks,max(OS_list$S$time,OS_list$t.risk,OS_list$ticks)+1)
      }
    }
  }

  last_time <- max(PFS_list$S$time,PFS_list$t.risk,PFS_list$ticks,OS_list$S$time,OS_list$t.risk,OS_list$ticks)

  #Next need to get both S onto the same time scales

  if (!is.null(PFS_list$nevent)) {
    if (min(PFS_list$nevent)<0) stop("Number of events cannot be negative!")
    if (max(abs(PFS_list$nevent - floor(PFS_list$nevent)))>1e-6) stop("nevent should be integers")
    if (length(PFS_list$nevent)!=1) stop("nevent should give number of events of each type")
  }
  if (!is.null(OS_list$nevent)) {
    if (min(OS_list$nevent)<0) stop("Number of events cannot be negative!")
    if (max(abs(OS_list$nevent - floor(OS_list$nevent)))>1e-6) stop("nevent should be integers")
    if (length(OS_list$nevent)!=1) stop("nevent should give number of events of each type")
  }
  ncomp <- 1

  #All times
  alltimes <- sort(unique(c(PFS_list$S$time,OS_list$S$time,last_time, PFS_list$t.risk, OS_list$t.risk)))
  missPFS <- which(!alltimes%in%PFS_list$S$time)
  missOS <- which(!alltimes%in%OS_list$S$time)
  #print(c(length(missPFS),length(missOS)))
  #Add missing times to PFS
  if (length(missPFS)>0) {
    extraS <- myapproxfun(c(0,PFS_list$S$time,last_time),c(0,PFS_list$S$cif[,1],max(PFS_list$S$cif[,1])),method="constant")(alltimes[missPFS])
    PFS_list$S$time <- c(PFS_list$S$time,alltimes[missPFS])
    PFS <- c(PFS_list$S$cif[,1],extraS)[order(PFS_list$S$time)]
    PFS_list$S$cif <- cbind(PFS)
    PFS_list$S$time <- sort(PFS_list$S$time)
  }
  #Add missing times to OS
  if (length(missOS)>0) {
    extraS <- myapproxfun(c(0,OS_list$S$time,last_time),c(0,OS_list$S$cif[,1],max(OS_list$S$cif[,1])),method="constant")(alltimes[missOS])
    OS_list$S$time <- c(OS_list$S$time,alltimes[missOS])
    OS <- c(OS_list$S$cif[,1],extraS)[order(OS_list$S$time)]
    OS_list$S$cif <- cbind(OS)
    OS_list$S$time <- sort(OS_list$S$time)
    #print(c(length(unique(OS_list$S$time)),length(OS_list$S$time)))
  }
  #Add tick points into the S objects
  if (!is.null(PFS_list$ticks)) {
    common_ticks <- sort(unique(c(PFS_list$ticks, OS_list$ticks)))
    miss2PFS <- which(!common_ticks%in%PFS_list$S$time)
    if (length(miss2PFS)>0) {
      extraS2 <- myapproxfun(c(0,PFS_list$S$time,last_time),c(0,PFS_list$S$cif[,1],max(PFS_list$S$cif[,1])),method="constant")(common_ticks[miss2PFS])
      PFS_list$S$time <- c(PFS_list$S$time,common_ticks[miss2PFS])
      PFS <- c(PFS_list$S$cif[,1],extraS2)[order(PFS_list$S$time)]
      PFS_list$S$cif <- cbind(PFS)
      PFS_list$S$time <- sort(PFS_list$S$time)
    }
  }
  if (!is.null(OS_list$ticks)) {
    common_ticks <- sort(unique(c(PFS_list$ticks, OS_list$ticks)))
    miss2OS <- which(!common_ticks%in%OS_list$S$time)
    if (length(miss2OS)>0) {
      extraS2 <- myapproxfun(c(0,OS_list$S$time,last_time),c(0,OS_list$S$cif[,1],max(OS_list$S$cif[,1])),method="constant")(common_ticks[miss2OS])
      OS_list$S$time <- c(OS_list$S$time,common_ticks[miss2OS])
      OS <- c(OS_list$S$cif[,1],extraS2)[order(OS_list$S$time)]
      OS_list$S$cif <- cbind(OS)
      OS_list$S$time <- sort(OS_list$S$time)
      #print(c(length(unique(OS_list$S$time)),length(OS_list$S$time)))
    }
  }

  ncomp <- 1


  if (!identical(PFS_list$S$time, OS_list$S$time)) stop("Something has gone wrong...")

  if (max(PFS_list$t.risk) < last_time) {
    PFS_list$t.risk <- c(PFS_list$t.risk,last_time)
    PFS_list$n.risk <- c(PFS_list$n.risk,0)
  }

  if (max(OS_list$t.risk) < last_time) {
    OS_list$t.risk <- c(OS_list$t.risk,last_time)
    OS_list$n.risk <- c(OS_list$n.risk,0)
  }

  matsPFS <- make_Mats(PFS_list$S, PFS_list$t.risk, PFS_list$n.risk, PFS_list$nevent, PFS_list$ndeath, PFS_list$ticks, PFS_list$t.event, PFS_list$c.event, PFS_list$totaltime, PFS_list$totaltime_power,ttol, constr_tol, cen_penalty,strict_tick, strict_dec, ceventinc, cen_max, last_time, ncomp,cumhaz=FALSE)
  matsOS <- make_Mats(OS_list$S, OS_list$t.risk, OS_list$n.risk, OS_list$nevent, OS_list$ndeath, OS_list$ticks, OS_list$t.event, OS_list$c.event, OS_list$totaltime, OS_list$totaltime_power,ttol, constr_tol, cen_penalty,strict_tick, strict_dec, ceventinc, cen_max, last_time, ncomp,cumhaz=FALSE)
  PFS_list$S <- matsPFS$S
  OS_list$S <- matsOS$S
  #Make two separate quadratic programs on 2xNs points
  #Then just need to add a load of extra inequality constraints...

  Ns <- dim(matsPFS$Q)[1]/2

  dvecOV <- c(matsPFS$dvec,matsOS$dvec)
  Q_OV <- array(0,c(Ns*4,Ns*4))
  Q_OV[1:(2*Ns),1:(2*Ns)] <- matsPFS$Q
  Q_OV[(2*Ns + 1):(4*Ns), (2*Ns + 1):(4*Ns)] <- matsOS$Q
  #Get the equality constraints from each one first
  meq1 <- matsPFS$ncon1 + length(matsPFS$wval2) +  dim(matsPFS$Aeq)[1]
  meq2 <- matsOS$ncon1 + length(matsOS$wval2) + dim(matsOS$Aeq)[1]
  meq <-  meq1 +  meq2
  Teq1 <- dim(matsPFS$A)[1]
  Teq2 <- dim(matsOS$A)[1]
  Teq <- Teq1 + Teq2
  Amat_OV <- array(0,c(Teq, 4*Ns))
  Amat_OV[1:meq1, 1:(2*Ns)] <- matsPFS$A[1:meq1,]
  Amat_OV[(meq1 + 1):(meq1 + meq2), (1 + 2*Ns):(4*Ns)] <- matsOS$A[1:meq2,]
  Amat_OV[(meq1+meq2 + 1):(Teq1 + meq2), 1:(2*Ns)]  <- matsPFS$A[(meq1+1):Teq1,]
  Amat_OV[(Teq1 + meq2 + 1):(Teq1 + Teq2), (1 + 2*Ns):(4*Ns)]  <- matsOS$A[(meq2+1):Teq2,]
  bvec_OV <- c(matsPFS$bvec[1:meq1],matsOS$bvec[1:meq2],matsPFS$bvec[(meq1+1):Teq1], matsOS$bvec[(meq2+1):Teq2])

  #Now need to add some more inequality constraints
  Amat_C <- array(0,c(Ns, 4*Ns))
  Amat_C[cbind( 1:Ns, (Ns+1):(2*Ns))]<--1
  Amat_C[cbind( 1:Ns, (3*Ns+1):(4*Ns))]<- 1
  Amat_R <- array(0,c(Ns-1, 4*Ns))
  for (i in 1:(Ns-1)) {
    Amat_R[i, 1:i] <- 1
    Amat_R[i, (Ns+1):(Ns+i)] <- 1
    Amat_R[i, (2*Ns + 1):(2*Ns + i)] <- -1
    Amat_R[i, (3*Ns + 1):(3*Ns + i)] <- -1
  }

  Amat_OV <- rbind(Amat_OV,Amat_C,Amat_R)
  bvec_OV <- c(bvec_OV,rep(0,2*Ns -1))


  #Now try to remove any linearly dependent equality constraints
  matRed <- reduce_constraints(Amat_OV,bvec_OV, meq)



  if (optmethod=="approx") {
    qpobj <- tryCatch(quadprog::solve.QP(Dmat=Q_OV,dvec=t(dvecOV),Amat = t(matRed$Astar),bvec = matRed$bstar,meq=matRed$nstar),error=function(e) return("Error"))
    if (identical(qpobj,"Error")) {
      #Rescale the problem and add some additional slack to the inequality constraints.
      sc <- norm(Q_OV,"2")
      qpobj <- tryCatch(quadprog::solve.QP(Dmat=Q_OV/sc,dvec=t(dvecOV)/sc,Amat = t(matRed$Astar),bvec = add_slack(1e-6,matRed$bstar,matRed$nstar),meq=nstar),error=function(e) return("Error"))
      if (identical(qpobj,"Error")) stop("Unable to find a feasible solution of QP. Check input data or try increasing constr_tol value.")
    }
    intsolPFS <- integer_round(qpobj$solution[1:(2*Ns)], PFS_list$S, matsPFS$chunk_total, 1)
    intsolOS <- integer_round(qpobj$solution[(2*Ns + 1):(4*Ns)], OS_list$S, matsOS$chunk_total, 1)
  }else{

    #Remove the zero constrained variables to reduce the total number of parameters
    Astar <- matRed$Astar
    nstar <- matRed$nstar
    bstar <- matRed$bstar

    EqCon <- Astar[1:nstar, ]
    bvCon <- bstar[1:nstar]
    numUsed <- apply(EqCon,1,function(x) sum(x!=0))
    canremove <- which(bvCon == 0 & numUsed==1)
    if (length(canremove)>0) {
      varcanremove <- apply(Astar[canremove,],1,function(x) which(x!=0))
      retain <- (1:length(dvecOV))[-varcanremove]
      dvec2 <- dvecOV[-varcanremove]
      Astar2 <- (Astar[-canremove,-varcanremove])
      bstar2 <- bstar[-canremove]
      Dmat3 <- Q_OV[-varcanremove,-varcanremove]
      nremov <- length(canremove)
    }else{
      retain <- 1:length(dvecOV)
      dvec2<-dvecOV
      Astar2 <- Astar
      bstar2 <- bstar
      Dmat3 <- Q_OV
      nremov <- 0
    }

    qpobj <- Rcplex::Rcplex(cvec=-c(dvec2),Amat=-(Astar2),bvec=-bstar2,Qmat=Dmat3,sense=rep(c("E","L"),c(nstar - nremov, length(bstar)-nstar)),lb=0,vtype="I",control=list(round=1,probe=as.integer(nprobe),epagap=epagap,epgap=epgap,tilim=tilim,trace=trace))
    solution <- rep(0,length(dvecOV))
    solution[retain] <- qpobj$xopt
    intsolPFS <- solution[1:(2*Ns)]
    intsolOS <- solution[(2*Ns + 1):(4*Ns)]
  }

  dataPFS <- data.frame(time=PFS_list$S$time, nevent = intsolPFS[1:Ns], ncen = intsolPFS[(1+Ns):(2*Ns)], tevent = intsolPFS[1:Ns])
  dataPFS$nrisk <- sum(dataPFS$nevent+dataPFS$ncen) - cumsum(c(0,dataPFS$nevent+dataPFS$ncen))[1:dim(dataPFS)[1]]
  attr(dataPFS,"use_ticks") <- 1*(!is.null(PFS_list$ticks))
  attr(dataPFS,"S") <- PFS_list$origS
  attr(dataPFS,"c.event") <- !is.null(PFS_list$c.event)
  attr(dataPFS,"events") <- data.frame(t.event=PFS_list$t.event, c.event=PFS_list$c.event)
  attr(dataPFS,"risks") <- data.frame(t.risk=PFS_list$t.risk,n.risk=PFS_list$n.risk)
  attr(dataPFS,"mats") <- matsPFS
  attr(dataPFS,"cumhaz") <- FALSE
  attr(dataPFS,"ltrunc") <- FALSE
  class(dataPFS) <- "KMresolve"



  dataOS <- data.frame(time=OS_list$S$time, nevent = intsolOS[1:Ns], ncen = intsolOS[(1+Ns):(2*Ns)], tevent = intsolOS[1:Ns])
  dataOS$nrisk <- sum(dataOS$nevent+dataOS$ncen) - cumsum(c(0,dataOS$nevent+dataOS$ncen))[1:dim(dataOS)[1]]
  attr(dataOS,"use_ticks") <- 1*(!is.null(OS_list$ticks))
  attr(dataOS,"S") <- OS_list$origS
  attr(dataOS,"c.event") <- !is.null(OS_list$c.event)
  attr(dataOS,"events") <- data.frame(t.event=OS_list$t.event, c.event=OS_list$c.event)
  attr(dataOS,"risks") <- data.frame(t.risk=OS_list$t.risk,n.risk=OS_list$n.risk)
  attr(dataOS,"mats") <- matsOS
  attr(dataOS,"cumhaz") <- FALSE
  attr(dataOS,"ltrunc") <- FALSE
  class(dataOS) <- "KMresolve"

  return(list(dataPFS=dataPFS, dataOS=dataOS))
}

#Auxiliary function to do the integer rounding of the continuous solution.
integer_round <- function(solution, S, chunk_total, ncomp) {
  nevent <- array(0,c(length(S$time),ncomp))
  for (j in 1:ncomp) {
    nevent[,j] <- diff(c(0,floor(round(cumsum(solution[(1:length(S$time) + (j-1)*length(S$time))]),5)+0.5)))
  }
  tevent <- apply(nevent,1,sum)
  cenevent <- pmax(0,solution[(1+ncomp*length(S$time)):((ncomp+1)*length(S$time))])
  cen_needed <- chunk_total - tapply(tevent, factor(S$chunk),sum)
  cur_cen <-  round(tapply(cenevent, S$chunk,sum),8)
  newcenevent <- cenevent * rep(cen_needed,table(S$chunk))/rep(cur_cen + 1*(cur_cen==0),table(S$chunk))
  intcenevent <- diff(c(0,floor(round(cumsum(newcenevent),5)+0.5)))
  intsol <- c(nevent,intcenevent)
  return(intsol)
}


make_data_ltrunc <- function(object,cen_method=NULL,trun_method=NULL) {

  #Turn this into a function called if the object contains left-truncation,

  if (is.null(cen_method)) {
    if (attr(object, "use_ticks") == 1) {
      cen_method <- "start"
    }
    else {
      cen_method <- "mid"
    }
  }
  #Default for truncation is that subjects entered mid-way through the previous interval.
  if (is.null(trun_method)) trun_method <- "mid"

  l <- length(object$time)
  if (trun_method=="mid") {
    trun_times <- object$time - c(0,diff(object$time))/2
  }else{
    trun_times <- object$time - 1e-6 #Place just before the event
  }
  if (cen_method == "mid") {
    #Need to add in times corresponding to the midpoint of the interval
    cen_times <- object$time + diff(c(object$time,object$time[l]))/2
  }else{
    cen_times <- object$time
  }

  event_times <- object$time


  all_times <- sort(unique(c(event_times,cen_times,trun_times)))
  ncen0 <- tapply(object$ncen,cen_times,sum)
  ntrun0 <- tapply(object$nenter,trun_times,sum)
  ncen <- ntrun <- nevent <- rep(0,length(all_times))
  nevent[match(event_times,all_times)] <- object$nevent
  ncen[match(cen_times,all_times)] <- ncen0
  ntrun[match(trun_times,all_times)] <- ntrun0

  events <- data.frame(time=all_times,enter=ntrun,cen=ncen,event=nevent)
  events <- events[(events$enter>0 | events$cen>0 | events$event >0 ),]

  l2 <- dim(events)[1]
  tstart <- events$time[1:(l2-1)]
  tstop <- events$time[2:l2]
  nevent <- events$event[2:l2]
  nrisk <- (cumsum(events$enter) - cumsum(events$cen) - cumsum(events$event))[1:(l2-1)]
  final_time <- data.frame(tstart=tstart,tstop=tstop,nrisk=nrisk,nevent=nevent)
  #Convert to weighted data
  final_timeW <- data.frame(tstart=rep(tstart,2),tstop=rep(tstop,2),event=rep(0:1,each=length(tstop)),weight=c(nrisk-nevent, nevent))
  final_timeW <- final_timeW[final_timeW$weight >0,]
  return(final_timeW)
}



make_data <- function(cif, cen_method=NULL, trunc_method=NULL) {

  if (attr(cif,"ltrunc")) return(make_data_ltrunc(cif,cen_method,trunc_method))

  #cif: CIFresolve or KMresolve object
  #cen_method: Convention for censoring events if ticks not supplied;
  # "start": Censor at the start of the interval
  # "mid": Censor at the middle of the potential interval
  if (is.null(cen_method)) {
    if (attr(cif,"use_ticks")==1) {
      cen_method <-"start"
    }else{
      cen_method <- "mid"
    }
  }
  if (attr(cif,"use_ticks")==1 & cen_method=="mid") {
    warning("Mid-interval censoring only makes sense for pseudo-IPD without supplied tick marks.")
    cen_method <- "start"
  }
  if (!inherits(cif, "CIFresolve") & !inherits(cif,"KMresolve")) stop("Should supply an object made by CIF_resolve or KM_resolve")
  times<-event<-NULL
  if (inherits(cif,"CIFresolve") & length(cif)>5) {
    ncomp <- length(cif)-4
    for (i in 1:ncomp) {
      times <- c(times,rep(cif$time,unlist(cif[paste("nevent",i,sep=".")])))
      event <- c(event,rep(i,sum(unlist(cif[paste("nevent",i,sep=".")]))))
    }
  }else{
    times <- rep(cif$time,cif$nevent)
    event <- rep(1,sum(cif$nevent))
  }
  if (cen_method=="start") {
    times <- c(times,rep(cif$time,cif$ncen))
  }else{
    mids <- (cif$time + c(cif$time[2:length(cif$time)],cif$time[length(cif$time)]))/2
    times <- c(times,rep(mids,cif$ncen))
  }
  event <- c(event,rep(0,sum(cif$ncen)))
  data.frame(time=times,event=event)
}



make_Mats <- function(S, t.risk, n.risk, nevent, ndeath, ticks, t.event, c.event, totaltime, totaltime_power, ttol, constr_tol, cen_penalty,strict_tick, strict_dec, ceventinc, cen_max, last_time, ncomp, cumhaz=FALSE) {

  #For number at risk assume is number at risk at time t (i.e. before events occurred)
  S$chunk <- sapply(S$time,function(x) sum(t.risk <= x))
  #For cumulative events assume number includes those that happened at time t
  if (last_time%in%ticks) {
    if (S$chunk[length(S$chunk)] > S$chunk[(length(S$chunk)-1)]) S$chunk[length(S$chunk)] <- S$chunk[(length(S$chunk)-1)]
  }
  chunk_total <- -diff(c(n.risk,0))
  if (!is.null(c.event)) {
    if (is.null(t.event)) t.event <- t.risk

    #Set up the chunks for cumulative events
    if (identical(t.event, t.risk) & !ceventinc) {
      S$chunk2 <- S$chunk
    }else{
      if (ceventinc) {
        S$chunk2 <- sapply(S$time,function(x) sum(t.event < x))
      }else{
        S$chunk2 <- sapply(S$time,function(x) sum(t.event <= x))
      }
    }
    if (is.vector(c.event)) {
      chunk_event_totals <- NULL
      chunk_event_total <- diff(c(c.event,c.event[length(c.event)]))
    }else{
      chunk_event_total <- NULL
      chunk_event_totals <- apply(c.event, 2, function(x) diff(c(x,x[length(x)])))
    }
  }else{
    chunk_event_total <- chunk_event_totals <- NULL
  }

  #Need to do something about chunks of zero length
  if (max(S$chunk) < length(chunk_total)) {
    chunk_total <- chunk_total[1:max(S$chunk)]
  }

  if (!is.null(chunk_event_total)) {
    if (max(S$chunk2) < length(chunk_event_total)) {
      chunk_event_total <- chunk_event_total[1:max(S$chunk2)]
    }
  }
  if (!is.null(chunk_event_totals)) {
    if (max(S$chunk2) < dim(chunk_event_totals)[1]) {
      chunk_event_totals <- chunk_event_totals[1:max(S$chunk2),]
    }
  }

  if (!cumhaz) {
  S$surv <- 1 - apply(S$cif,1,sum)

  Obs <- (S$cif - rbind(rep(0,ncomp),S$cif[1:c(dim(S$cif)[1]-1),,drop=FALSE]))/array(c(1,S$surv[1:(length(S$surv)-1)]),dim=dim(S$cif))
  Obs <- replace(Obs,which(is.nan(Obs)),0) #Remove NaN's which should be due to 0s going to 0s.
  }else{
  Obs <-sapply(1:ncomp, function(x) diff(c(0,S$cif[,x])))
  #if (ncomp==1) Obs <- cbind(Obs)
  }

  decs <- which(Obs >0)
  #Set up the objective matrix
  B <- array(0,c(ncomp*length(S$time),(ncomp+1)*length(S$time)))
  for (j in 1:ncomp) {
    B[cbind((1:length(S$time) + (j-1)*length(S$time)),(1:length(S$time) + (j-1)*length(S$time)))]<-1
    for (i in 2:length(S$time)) {
      for (k in 1:(ncomp+1)) {
        B[i + (j-1)*length(S$time),(1:(i-1) + (k-1)*length(S$time))]<- Obs[i,j]
      }
    }
  }
  Dmat <- t(B)%*%B
  dvec <- n.risk[1]* t(c(Obs))%*%B

  event_totals <- nevent
  event_total <- ndeath

  #Five possibilities
  #i) No event info: nchunk
  #ii) Just total deaths: nchunk + 1
  #iii) Total of each event: nchunk + ncomp
  #iv) Chunked total deaths: nchunk + nchunk2
  #v) Chunked total for each event: nchunk + (ncomp)*nchunk2
  chunkscenario <- 1*(is.null(chunk_event_total) & is.null(chunk_event_totals) & is.null(event_totals) & is.null(event_total)) +2*(is.null(chunk_event_total) & is.null(chunk_event_totals) & is.null(event_totals) & !is.null(event_total))+3*(is.null(chunk_event_total) & is.null(chunk_event_totals) & !is.null(event_totals))+4*(!is.null(chunk_event_total) & is.null(chunk_event_totals)) + 5*(!is.null(chunk_event_totals))

  #Set up the constraint matrix:

  #Each chunk needs two constraints
  nchunk <- length(unique(S$chunk))
  if (chunkscenario%in%c(4,5)) {
    nchunk2 <- max(S$chunk2)
  }else{
    nchunk2 <- 0
  }
  nconstrE <- c(nchunk, nchunk+1,nchunk+ncomp,nchunk+nchunk2,nchunk + (ncomp)*nchunk2)[chunkscenario]

  Aeq <- array(0,c(nconstrE,(ncomp+1)*length(S$time)))
  Beq <-rep(0,nconstrE)
  for (i in 1:nchunk) {
    mm <- which(S$chunk==i)
    for (j in 1:ncomp) {
      mm <- c(mm,which(S$chunk==i)+j*length(S$time))
    }
    Aeq[i,mm] <- 1
    Beq[i] <- chunk_total[i]
  }

  if (chunkscenario==2) {

    for (j in 1:ncomp) {
      Aeq[nchunk+1,((1:length(S$time))+(j-1)*length(S$time))]<-1
    }
    Beq[nchunk+1] <- event_total
  }
  if (chunkscenario==3) {
    for (j in 1:ncomp) {
      Aeq[nchunk+j,((1:length(S$time))+(j-1)*length(S$time))]<-1
      Beq[nchunk+j]<-event_totals[j]
    }
  }
  if (chunkscenario==4) {

    for (i in 1:nchunk2) {
      mm <- which(S$chunk2==i)
      if (ncomp >1) {
        for (j in 1:(ncomp-1)) {
          mm <- c(mm,which(S$chunk2==i)+j*length(S$time))
        }
      }
      Aeq[nchunk+i,mm] <- 1
      Beq[nchunk+i] <- chunk_event_total[i]
    }

  }
  if (chunkscenario==5) {

    for (j in 1:ncomp) {
      for (i in 1:nchunk2) {
        mm <- which(S$chunk2==i) + (j-1)*length(S$time)
        Aeq[(nchunk+i+(j-1)*nchunk2),mm] <- 1
        Beq[(nchunk+i+(j-1)*nchunk2)] <- chunk_event_totals[i,j]
      }
    }
  }

  #Only penalize the censoring times
  Dmat2 <- Dmat + diag(c(rep(c(0,cen_penalty),c(ncomp*length(S$time),length(S$time)))))

  excl <- NULL
  for (j in 1:ncomp) {
    wvalj <- which(Obs[,j] == 0)
    if (j==1) {
      Aeq4 <- array(0,c(length(wvalj),(ncomp+1)*length(S$time)))
      Aeq4[cbind(1:length(wvalj),wvalj)]<-1
    }else{
      Aj <- array(0,c(length(wvalj),(ncomp+1)*length(S$time)))
      Aj[cbind(1:length(wvalj),wvalj + (j-1)*length(S$time))]<-1
      Aeq4 <- rbind(Aeq4,Aj)
    }
    excl <- c(excl, wvalj + (j-1)*length(S$time))
  }
  ncon1 <- dim(Aeq4)[1]




  if (!is.null(ticks)) {
    wval2 <- which(!S$time %in% ticks)
    Aeq5 <- array(0,c(length(wval2),(ncomp+1)*length(S$time)))
    Aeq5[cbind(1:length(wval2),(wval2 + ncomp*length(S$time)))]<-1

    #Is it really necessary to add in the 0 constraints??
    Aeq2 <- diag((ncomp+1)*length(S$time))
    Beq2 <- rep(0,dim(Aeq2)[1])
    ####################################################
    if (strict_tick) {
      wval3 <- which(S$time %in% ticks)
      Beq2[(wval3 + (ncomp)*length(S$time))] <- 1-constr_tol #avoid method thinking no solution
    }
    excl <- c(excl, wval2 + ncomp*length(S$time))
    decI <- 1*(strict_dec)*(1:((ncomp+1)*length(S$time)) %in% decs)[-excl]
    decS <- pmax(decI*(1-constr_tol), Beq2[-excl])
    Aeq2 <- Aeq2[-excl,]
    Aeq3 <- rbind(Aeq,Aeq2)
    Aeq6 <- rbind(Aeq4,Aeq5,Aeq3)
    #Beq3 <- c(rep(0,ncon1+length(wval2)),Beq,Beq2[-excl])
    Beq3 <- c(rep(0,ncon1+length(wval2)),Beq,decS)
  }else{
    Aeq2 <- diag((ncomp+1)*length(S$time))
    decI <- 1*(strict_dec)*(1:((ncomp+1)*length(S$time)) %in% decs)[-excl]
    Aeq2 <- Aeq2[-excl,]
    wval2 <- NULL
    Aeq3 <- rbind(Aeq,Aeq2)
    Aeq6 <-   rbind(Aeq4,Aeq3)
    Beq3 <- c(rep(0,ncon1),Beq,decI*(1-constr_tol)) #Force any decrement to be associated with at least one event
  }


  if (!is.null(totaltime)) {
    if (!is.numeric(totaltime)) stop("totaltime needs to be a numeric scalar corresponding to the total patient time at risk")
    #Need to add two more inequality constraints
    #If ticks supplied assume censoring is at the times themselves.
    #Otherwise take midpoint between the time and the next time
    if (is.null(ticks)) {
      cenpoints <- (S$time + c(S$time,S$time[length(S$time)])[2:(length(S$time)+1)])*0.5
    }else{
      cenpoints <- S$time
    }
    Aeq7 <- rbind(c(rep(S$time^totaltime_power, ncomp),cenpoints^totaltime_power),c(-rep(S$time^totaltime_power, ncomp),-cenpoints^totaltime_power))
    Aeq6 <- rbind(Aeq6,Aeq7)
    Beq3 <- c(Beq3, totaltime*(1-ttol), -totaltime*(1+ttol))
  }
  if (!is.null(cen_max)) {
    Aeq8 <- array(0,c(length(S$time)*(ncomp + 1), length(S$time)))
    Aeq8[cbind((ncomp*length(S$time) +1):((ncomp+1)*length(S$time)),1:length(S$time))] <- 1
    Aeq6 <- rbind(Aeq6,Aeq8)
    Beq3 <- c(Beq3, rep(cen_max, length(S$time)))
  }

  return(list(dvec=dvec, Q=Dmat2, A=Aeq6, bvec=Beq3, wval=wval2, ncon1=ncon1, Aeq=Aeq, Obs=Obs, S=S, chunk_total=chunk_total))
}


reduce_constraints <- function(A,bvec, neq) {
  Aeq <- A[1:neq,]
  beq <- bvec[1:neq]
  QR <- qr(t(Aeq))
  rank <- QR$rank
  keep <- QR$pivot[1:rank]
  Aeq_red <- Aeq[keep,, drop=FALSE]
  Astar <- rbind(Aeq_red, A[-(1:neq),])
  bstar <- c(beq[keep],bvec[-(1:neq)])
  list(Astar=Astar,bstar=bstar,nstar=rank)
}

reduce_constraints0 <- function(A,bvec,neq) {
  list(Astar=A,bstar=bvec,nstar=neq)
}

add_slack <- function(d,b,n) {
  l <- length(b)
  if (n < l) {
  b[(n+1):l] <- b[(n+1):l] + d
  }
  return(b)
}
