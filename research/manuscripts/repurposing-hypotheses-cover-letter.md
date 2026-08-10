---
id: DOC-REPURPOSING-HYPOTHESES-COVER-LETTER
title: "Cover letter — graded repurposing candidate menu for extraskeletal myxoid chondrosarcoma"
level: L3
kind: memo
status: live
canonical_for: []
purpose: >
  Hold the ready-to-send cover letter accompanying repurposing-hypotheses.md to Critical Reviews in
  Oncology/Hematology, with the fit statement, the scope disclosure, the preprint note and the
  integrity declarations a journal expects at submission.
scope: >
  The cover letter only. It is a submission document, not a scientific record; every result it
  refers to lives in the review and its artifacts.
audience: [maintainers, external reviewers, collaborators]
related: [DOC-REPURPOSING-HYPOTHESES]
date: 2026-08-10
last_verified: 2026-08-10
---

# Cover letter

*Ready to send. Before submitting: fill the bracketed date, confirm the editor addressee on the
journal's current masthead, and publish under the subscription model so no article publishing charge
is incurred. The Highlights the submission system requires are carried in the manuscript immediately
after the abstract.*

---

**To:** The Editor-in-Chief, *Critical Reviews in Oncology/Hematology*

**From:** Tristan D. McRae, independent researcher, unaffiliated — trimcrae@gmail.com

**Date:** [DATE]

**Re:** Submission of a Review — *"Repurposing in an ultra-rare sarcoma: evidence and novelty are anti-correlated in extraskeletal myxoid chondrosarcoma, and two computational routes added no candidate"*

Dear Editor,

I submit the manuscript above for consideration as a Review in *Critical Reviews in
Oncology/Hematology*. Extraskeletal myxoid chondrosarcoma is an ultra-rare *NR4A3*-rearranged
sarcoma with an indolent but relentlessly metastasising course, no established effective systemic
therapy, and a genome in which clinical sequencing recovers no recurrent actionable mutation beyond
the fusion, so repurposing agents that already carry human safety data is the rational search. The
review maps the disease's documented molecular and microenvironmental vulnerabilities to agents not
yet reported in it and grades every resulting hypothesis on an explicit evidence tier. The
structure of the resulting menu is the finding: evidence strength and novelty are anti-correlated,
and the cell that would hold an untried agent with EMC clinical evidence is empty.

The review also reports what each of its three generation approaches actually yielded, which is not
an even split. Literature-driven curation produced 12 of the 14 candidates. A reproducible
target-to-drug enumeration over nine genes contributed 2, reaching three of the eight vulnerability
axes and adding nothing outside the kinase and nuclear-receptor axes. A pretrained graph foundation
model, run zero-shot, contributed none. I have written the paper around that split rather than
around a claim of triangulation, because it is the more useful result for anyone deciding how to
spend a year on this problem.

The fit with the journal is the register rather than the disease. This is a critical review with a
reproducible method and a mandatory account of its own weaknesses, not an enthusiastic survey. It
reports the negatives at the same weight as the positives: a graph foundation model run as an
independent check diverged from both other methods, was stress-tested against the obvious
explanation of EMC's rarity and was not rescued by it, and contributed no candidate; and the two
in-silico rationales advanced here for the highest-profile lead, a proteasome inhibitor, were both
pre-specified, both run, and both returned negative on the contrast each was written to grade, with
one further module scored as pre-declared context reported alongside them rather than folded into
either verdict. That lead stays on the menu because it rests on somebody else's ex-vivo measurement
rather than on our argument, and the review says so in those terms. The manuscript also reports and
corrects a defect in its own code, which had matched queried agents to the model's output by
substring and so attributed three ranks to the wrong molecule. Readers of this journal are the people who have to decide what a graded menu of untested
hypotheses in a rare tumour is worth.

The work is entirely computational and literature-based. It involved no wet-laboratory experiment,
no clinical observation and no patient contact; every input is published literature or a public
database, no new patient data were generated, and no ethics approval was required. No efficacy is
claimed for any agent, no treatment recommendation is made including a negative one, and a firewall
described in the manuscript keeps every hypothesis below direct EMC clinical evidence out of
patient-facing material.

The principal limitation is the one section 6 lists first: only one of the fourteen candidates,
imatinib in the *KIT*-mutant minority, rests on direct EMC clinical evidence, and it rests on a
single published case, so nothing in the menu reaches the top evidence tier and every genuinely
untried candidate rests on preclinical, in-vitro or model-screen data. The size of that minority is
itself uncertain: the two reported *KIT* variant classes are not equivalent, and only the exon-11
class, found in 1 of 20 EMCs in one series, is characterised as imatinib-sensitive. Target-level
plausibility does not guarantee clinical activity. A sarcoma clinician has not reviewed the menu,
and the manuscript recommends that review before any clinical-facing use of it, naming the three
items it would have to cover: the tier assignments, the size of the addressable *KIT*-mutant
population, and every entry in the column of Table 4 that states what experiment comes next.

I intend to deposit the manuscript as a preprint on bioRxiv, consistent with the publisher's
preprint policy, and will link the preprint to the published version. I am the sole author, an
unaffiliated independent researcher with no institutional address; no ORCID accompanies this
submission. AI tools were used for literature aggregation, the target-to-drug enumeration, the
graph-model run, the two pre-specified in-silico tests, reference verification and drafting, which
is disclosed in the manuscript; no AI tool is an author, and I take full responsibility for the
content.

The work is original, has not been published, and is not under consideration elsewhere. I have no
competing interests and received no funding.

Should it help the editors, appropriate reviewer expertise would include sarcoma medical oncology,
drug repurposing methodology, and computational target-to-drug inference.

Thank you for considering this manuscript.

Yours sincerely,

Tristan D. McRae
Independent Researcher
trimcrae@gmail.com
