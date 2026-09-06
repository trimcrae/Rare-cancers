\name{KM_resolve}
\alias{KM_resolve}
\title{
Reconstruct patient-level data from Kaplan-Meier estimates.
}
\description{
Outputs estimates of the number of events and number of censored observation from supplied digitized data points.
}
\usage{
KM_resolve(S, t.risk, n.risk, ndeath = NULL, ticks = NULL,
totaltime=NULL, totaltime_power=1, c.event=NULL, t.event=NULL,
optmethod = "approx", nsub=NULL, ltrunc=FALSE,
control=control.CIFresolve())
}
\arguments{
  \item{S}{
 List containing a vector `time` corresponding to the times at which the Kaplan-Meier estimate has been obtained, and either a vector `surv` corresponding to the Kaplan-Meier estimate of the survival function at those time points or a vector `Haz` corresponding to the Nelson-Aalen estimate of the cumulative hazard function.
}
  \item{t.risk}{
 Vector containing the timepoints at which the number of patients at risk/under observation is known.
}
  \item{n.risk}{
Vector containing the number of patients at risk/under observation at the times given in the vector `t.risk`
}
  \item{ndeath}{
Vector of total number of events across all types. Can be omitted.
}
  \item{ticks}{
Optional vector of time points where the Kaplan-Meier plot had tick marks representing censoring times
}
\item{totaltime}{Total time at risk in the dataset (sum of all patient's follow-up times) or sum of transformed follow-up times (defined by \code{totaltime_power}). Can be omitted.}
\item{totaltime_power}{The power by which each of the individual times has been raised in the calculation of totaltime, defaults to 1, potentially useful if the MLEs of the Weibull rate and shape parameters are known.}
\item{c.event}{Vector of cumulative number of events. Can be omitted}
\item{t.event}{Vector of times at which number of cumulative events is supplied. If omitted it is assumed t.event=t.risk}
\item{optmethod}{Character string to indicate method of finding solution: `approx` - solve the continuous QP and then perform integer rounding. `miqp` - use full mixed integer QP optimization using Rcplex. Default is `approx`}
\item{nsub}{Optional scalar indicating the total number of subjects in the dataset. Only needed for left truncated data.}
\item{ltrunc}{Logical to indicate whether the survival curve is estimated from left-truncated data. Default is \code{FALSE}.}
\item{control}{Optional list of additional control parameters. See \link{control.CIFresolve} for details.}
}
\details{
The \code{KM_resolve} function is used to reconstruct pseudo patient-level data from a set of digitized Kaplan-Meier function curves. Note that this is a special case of reconstructing from cumulative incidence curves so the function is a wrapper function for \code{CIF_resolve}. For more information on the methodology see Titman (2026).
}
\value{
Returns a data frame containing the table of estimated numbers at risk, numbers of events and number of censorings at time points.
}

\examples{
data(pfs_elgalay)
fitA <- KM_resolve(S=pfs_elgalay,t.risk=pfs_elgalay$trisk,
n.risk=pfs_elgalay$nrisk,ticks=pfs_elgalay$ticks)
plot(fitA)
pIPD <- make_data(fitA)

data(hendricks_data)
fitB <- KM_resolve(S=hendricks_data,t.risk=hendricks_data$trisk,
n.risk=hendricks_data$nrisk, t.event=hendricks_data$trisk,
c.event=hendricks_data$cevent,
ltrunc=TRUE,control=list(trun_penalty=1e-5))
plot(fitB)
pCPD <- make_data(fitB)
}


\author{
Andrew Titman \email{a.titman@lancaster.ac.uk}
}


\references{
 Titman AC. Using Quadratic Programming to Reconstruct Data from Published Survival and Competing Risks Analyses. \emph{Statistics in Medicine}, 2026. DOI: 10.1002/sim.70474.
}

%% ~Make other sections like Warning with \section{Warning }{....} ~

\seealso{
\code{\link{CIF_resolve}}, \code{\link{plot.KMresolve}}, \code{\link{make_data}}, \code{\link{control.CIFresolve}}}
