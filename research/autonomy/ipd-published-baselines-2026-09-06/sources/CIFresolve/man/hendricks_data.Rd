\name{hendricks_data}
\alias{hendricks_data}
\docType{data}
\title{
Extracted data points on cumulative incidence of breast cancer via the incident cohort in Hendricks et al (2020)
}
\description{
Manually extracted values of the Kaplan-Meier estimate of cumulative incidence. To be used as an example input for KM_resolve with left-truncated survival data.
}
\usage{data("hendricks_data")}
\format{
  A list with the following components
\describe{
   \item{times}{Time in months of extracted decrement points}
   \item{surv}{Corresponding Kaplan-Meier estimate values (1 minus cumulative incidence)}
   \item{nrisk}{Vector of periodically reported numbers at risk}
   \item{trisk}{Times at which number of patients at risk is reported}
   \item{cevent}{Vector of periodically reported cumulative number of events}
 }
}
\keyword{datasets}
