\name{CIF_resolve}
\alias{CIF_resolve}
%- Also NEED an '\alias' for EACH other topic documented here.
\title{
Reconstruct patient-level data from cumulative incidence function estimates.
}
\description{
Outputs estimates of the number of competing risks events and number of censored observation from supplied digitized data points.
}
\usage{
CIF_resolve(S, t.risk, n.risk, nevent= NULL, ndeath = NULL,
ticks = NULL, totaltime=NULL, totaltime_power=1,
c.event=NULL, t.event=NULL, optmethod = "approx",
nsub=NULL, ltrunc=FALSE, control=control.CIFresolve())
}
%- maybe also 'usage' for other objects documented here.
\arguments{
  \item{S}{
 List containing a vector `time` corresponding to the times at which the cumulative incidence curve has been obtained, and either a matrix `cif` giving the corresponding cumulative incidence function values where the number of columns should correspond to the number of risks.  \code{\link{align_CIF}} can be used to help create this matrix. Alternatively an analogous matrix `Haz' containing the Nelson-Aalen estimates of the cumulative cause-specific hazard functions. 
}
  \item{t.risk}{
 Vector containing the timepoints at which the number of patients at risk/under observation is known.
}
\item{n.risk}{Vector containing the number of patients at risk/under observation at the times given in the vector `t.risk`}
\item{nevent}{Vector of number of events of each type (should be of same length as number of risks/number of columns in S$cif). Can be omitted. See also c.event if interim counts are available.}
\item{ndeath}{Vector of total number of events across all types. Can be omitted.}
\item{ticks}{Optional vector of time points where the CIF plot had tick marks representing censoring times}
\item{totaltime}{Total time at risk in the dataset (sum of all patient's follow-up times) or sum of transformed follow-up times (defined by \code{totaltime_power}). Can be omitted.}
\item{totaltime_power}{The power by which each of the individual times has been raised in the calculation of totaltime, defaults to 1, potentially useful if the MLEs of the Weibull rate and shape parameters are known.}
\item{c.event}{Vector or matrix of cumulative number of events; should either be a vector (in which case is interpreted as the cumulative total number of events) or a matrix where each column represents the cumulative number of events of each time. Can be omitted}
\item{t.event}{Vector of times at which number of cumulative events is supplied. If omitted it is assumed t.event=t.risk}
\item{optmethod}{Character string to indicate method of finding solution: `approx` - solve the continuous QP and then perform integer rounding. `miqp` - use full mixed integer QP optimization using Rcplex. Default is `approx`}
\item{nsub}{Optional scalar indicating the total number of subjects in the dataset. Only needed for left truncated data.}
\item{ltrunc}{Logical to indicate whether the survival curve is estimated from left-truncated data. Default is \code{FALSE}.}
\item{control}{Optional list of additional control parameters. See \link{control.CIFresolve} for details.}
}
\details{
The \code{CIF_resolve} function is used to reconstruct pseudo patient-level data from a set of digitized cumulative incidence function curves (estimated via the Aalen-Johansen estimator). For more information on the methodology see Titman (2026).
}
\value{
Returns a data frame containing the table of estimated numbers at risk, numbers of events and number of censorings at time points.
}

\examples{
data(cif_elgalay)
fitB <- CIF_resolve(S=cif_elgalay,t.risk=cif_elgalay$trisk,
n.risk=cif_elgalay$nrisk,ticks=cif_elgalay$ticks)
plot(fitB)
pIPD2 <- make_data(fitB)
}


\author{
Andrew Titman \email{a.titman@lancaster.ac.uk}
}

\references{
 Titman AC. Using Quadratic Programming to Reconstruct Data from Published Survival and Competing Risks Analyses. \emph{Statistics in Medicine}, 2026. DOI: 10.1002/sim.70474.
}


\seealso{
\code{\link{KM_resolve}}, \code{\link{plot.CIFresolve}}, \code{\link{make_data}}, \code{\link{control.CIFresolve}}, \code{\link{align_CIF}}}
