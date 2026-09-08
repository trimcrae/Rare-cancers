# RUN-04 — exit 0, all 17 checks PASS, but SUPERSEDED by RUN-06

RUN-04 is preserved as the run that happened. Its outputs were nevertheless replaced, because
reading the RUN-04 VALUES (not any failing check) exposed a parsing defect in v2's own
`verify_leaf_claim`: it split a leaf's recovered arm labels on ";" only. The four delivered leaves
are not uniform — `LEAF-QD-group0.tsv` uses "; " while `LEAF-QD-group1/2/3.tsv` use "|". Nine rows
(NCT04020185 x8, NCT04387071 x1) whose leaf claimed several real registered arms separated by "|"
were therefore read as ONE label that is absent from the record and mis-stated as CONTESTED /
LEAF_CLAIMED_ARM_LABEL_ABSENT_FROM_THIS_RECORD, when the honest state is UNRESOLVED /
LEAF_CLAIMS_MULTIPLE_ARMS with all candidate arms preserved.

Fix for RUN-06: split on both separators; new guard
`multi_arm_leaf_claims_are_split_not_read_as_one_absent_label`; new value test T3d.
No check was weakened. RUN-04's stdout, exit code and note remain on the record.

One row is NOT affected and keeps LEAF_LABEL_ABSENT_FROM_RECORD honestly: NCT02566993, whose leaf
recovered the composed string 'Control Arm 1 + Control Arm 2'. That string is not a registered arm
label in the record; "+" is deliberately NOT treated as a separator because it occurs inside real
registered labels (e.g. 'Placebo+Chemo').
