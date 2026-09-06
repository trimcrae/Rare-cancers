\name{pignot_data}
\alias{pignot_data}
\docType{data}
\title{
Extracted data points on disease-free and overall survival for Type 2 Papilliary RCC patients in Pignot et al (2007)
}
\description{
Manually extracted values of the Kaplan-Meier estimate of disease-free survival and overall survival and the corresponding marked censoring times (tick points). To be used as an example input for the PFS_OS_resolve function.
}
\usage{data("pignot_data")}
\format{
  A list with two components, \code{dfs_data} and \code{os_data}, each consisting of a list with components:
\describe{
   \item{times}{Time in months of extracted decrement points}
   \item{surv}{Corresponding Kaplan-Meier estimate values}
   \item{ticks}{Extracted times of the marked censoring times from the plot.}
   \item{nrisk}{Vector of periodically reported numbers at risk}
   \item{trisk}{Times at which number of patients at risk is reported}
   \item{ndeath}{Total number of events reported}
 }
}
\keyword{datasets}
