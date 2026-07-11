# Validation-panel genetic dependency (DepMap, CI)

DepMap CRISPR dependency for validation-panel TARGETS across sarcoma (EMC surrogate). Answers: selective dependency vs pan-essential (window = pharmacology). SURROGATE — no EMC line.

Release 24Q4; 1178 lines (91 sarcoma).

| target | group | mean GE | %dep | status | sel(sar-rest) |
|---|---|---|---|---|---|
| PSMB5 | proteasome (carfilzomib/bortezomib) | -1.703 | 0.947 | pan_essential | 0.169 |
| PSMB1 | proteasome (carfilzomib/bortezomib) | -1.726 | 0.997 | pan_essential | -0.023 |
| PSMB2 | proteasome (carfilzomib/bortezomib) | -1.966 | 1.0 | pan_essential | -0.063 |
| HDAC1 | HDAC (panobinostat/romidepsin/entinostat) | -0.155 | 0.04 | non_essential | -0.005 |
| HDAC2 | HDAC (panobinostat/romidepsin/entinostat) | -0.06 | 0.028 | non_essential | 0.108 |
| HDAC3 | HDAC (panobinostat/romidepsin/entinostat) | -0.934 | 0.874 | pan_essential | -0.021 |
| HDAC6 | HDAC (panobinostat/romidepsin/entinostat) | -0.056 | 0.0 | non_essential | 0.028 |
| HDAC8 | HDAC (panobinostat/romidepsin/entinostat) | -0.093 | 0.025 | non_essential | 0.071 |
| HSP90AA1 | HSP90 (PU-H71) | -0.254 | 0.052 | non_essential | -0.026 |
| HSP90AB1 | HSP90 (PU-H71) | -0.281 | 0.124 | non_essential | 0.073 |
| MDM2 | MDM2/p53 (HDM201) | -0.577 | 0.326 | context_dependency | 0.049 |
| MDM4 | MDM2/p53 (HDM201) | -0.183 | 0.121 | non_essential | -0.021 |
| TP53 | MDM2/p53 (HDM201) | 0.379 | 0.003 | non_essential | -0.136 |
| BCL2 | BCL2 (venetoclax) | -0.037 | 0.028 | non_essential | 0.021 |
| BCL2L1 | BCL2 (venetoclax) | -1.06 | 0.846 | pan_essential | -0.2 |
| MCL1 | BCL2 (venetoclax) | -0.798 | 0.707 | context_dependency | 0.139 |
| XPO1 | XPO1 (selinexor) | -1.981 | 1.0 | pan_essential | 0.037 |
| ALK | kinases (pazopanib/sunitinib/brigatinib) | -0.051 | 0.006 | non_essential | -0.012 |
| KIT | kinases (pazopanib/sunitinib/brigatinib) | -0.095 | 0.003 | non_essential | -0.009 |
| KDR | kinases (pazopanib/sunitinib/brigatinib) | -0.126 | 0.005 | non_essential | -0.034 |
| FLT1 | kinases (pazopanib/sunitinib/brigatinib) | 0.001 | 0.0 | non_essential | 0.013 |
| FLT4 | kinases (pazopanib/sunitinib/brigatinib) | 0.01 | 0.001 | non_essential | -0.006 |
| PDGFRA | kinases (pazopanib/sunitinib/brigatinib) | -0.259 | 0.072 | non_essential | 0.045 |
| PDGFRB | kinases (pazopanib/sunitinib/brigatinib) | -0.161 | 0.027 | non_essential | 0.043 |
| RET | kinases (pazopanib/sunitinib/brigatinib) | -0.097 | 0.001 | non_essential | -0.023 |
| FGFR1 | kinases (pazopanib/sunitinib/brigatinib) | -0.123 | 0.093 | non_essential | 0.122 |

Self-validation: POLR2A=not_in_depmap, NR4A3=non_essential, BRD9 synovial={'synovial': -0.13, 'overall_mean': 0.09}.
