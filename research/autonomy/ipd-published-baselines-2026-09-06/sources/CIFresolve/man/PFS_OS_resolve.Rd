\name{PFS_OS_resolve}
\alias{PFS_OS_resolve}
\title{
Paired reconstruction of progress-free and overall survival Kaplan-Meier curves.
}
\description{
Outputs estimates of the number of events and number of censored observation from supplied digitized data points for PFS and OS assuming common right-censoring.
}
\usage{
PFS_OS_resolve(PFS_list, OS_list, optmethod = "approx", control=control.CIFresolve())
}
\arguments{
  \item{PFS_list}{
 List of information relating to the PFS Kaplan-Meier curve. Must contain time, surv, t.risk, n.risk, and can also include ndeath, ticks, totaltime, totaltime_power, c.event, t.event. These correspond to arguments to \link{KM_resolve}.
}
  \item{OS_list}{
 List of information relating to the OS Kaplan-Meier curve. Must contain time, surv, t.risk, n.risk, and can also include ndeath, ticks, totaltime, totaltime_power, c.event, t.event. These correspond to arguments to \link{KM_resolve}.
}
  \item{optmethod}{Character string to indicate method of finding solution: `approx` - solve the continuous QP and then perform integer rounding. `miqp` - use full mixed integer QP optimization using Rcplex. Default is `approx`}
\item{control}{Optional list of additional control parameters. See \link{control.CIFresolve} for details.}
}
\details{
The \code{PFS_OS_resolve} function is used to reconstruct pseudo patient-level data from a pair of digitized Kaplan-Meier curves for progression-free survival and overall survival in a way that ensures the resulting sets of pseudo IPD are mutually consistent.
Note that pre-processing may be necessary to ensure the event times for the two curves are aligned and that the tick points for PFS are a subset of those for OS.
}
\value{
Returns a list containing two objects of \code{KMresolve} class, dataPFS and dataOS, corresponding to the PFS and OS reconstructions, respectively.
}

\examples{
data(pignot_data)
fitC <- PFS_OS_resolve(PFS_list=pignot_data$dfs_data, OS_list=pignot_data$os_data, 
          control=list(constr_tol=1e-1, cen_penalty=1e-2))
plot(fitC$dataPFS)
plot(fitC$dataOS)
PFS_dat <- make_data(fitC$dataPFS)
OS_dat <- make_data(fitC$dataOS)
}


\author{
Andrew Titman \email{a.titman@lancaster.ac.uk}
}

\seealso{
\code{\link{KM_resolve}}, \code{\link{plot.KMresolve}}, \code{\link{make_data}}, \code{\link{control.CIFresolve}}}
