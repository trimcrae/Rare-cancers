import sys, hashlib
p = "/tmp/claude-0/v1-lane/V1-CANDIDATE-repurposing-hypotheses.md"
s = open(p, encoding="utf-8").read()
orig = s

EDITS = []

# 1 - Section 2.2 tier definitions: occupancy sentence (R2 Candidate A text, retained unchanged)
EDITS.append((
"""is, not the expected effect size.
""",
"""is, not the expected effect size. On the evidence assembled here, no candidate reaches T3: the
strongest EMC-specific clinical evidence in the menu is a single published case report, which these
definitions place at T2. T3 is therefore defined but unoccupied, and is retained to mark what a
prospective or substantial EMC clinical result would look like.
"""))

# 2 - Section 2.6 firewall prose
EDITS.append((
"""or removed, and an automated check enforces zero unresolved claims. A firewall separates these
hypotheses from any patient-facing material: only a candidate reaching direct EMC clinical evidence
may migrate into the project's cited clinical registry, and then only after clinician review
(section 5). Figure 1 shows the three-method design and the firewall.""",
"""or removed, and an automated check enforces zero unresolved claims. A firewall is intended to
separate these hypotheses from any patient-facing material, and its admission criterion is stated
here unchanged: only a candidate reaching direct EMC clinical evidence may migrate into the
project's cited clinical registry, and then only after clinician review (section 5). We describe
this as the stated and intended criterion rather than as one we have verified to be met. Section 5
states the same criterion in tier terms, as tier T3; under the T2 grade adopted here for imatinib
(section 2.2), the existing imatinib entry in the project's cited clinical registry falls below that
stated criterion, and registry conformance is therefore unresolved (sections 4 and 5). Figure 1
shows the three-method design and the firewall."""))

# 3 - Figure 1 alt text
EDITS.append((
"""contributing no candidate. A firewall governs what may reach patient-facing material, admitting only tier T3 after clinician review.]""",
"""contributing no candidate. A firewall governs what may reach patient-facing material; its stated admission criterion is tier T3 after clinician review, and conformance of the existing imatinib registry listing with that criterion is unresolved.]"""))

# 4 - Figure 1 printed caption
EDITS.append((
"""foundation model is reported as a limitation and contributed no candidate. The firewall governs
what may reach patient-facing material.""",
"""foundation model is reported as a limitation and contributed no candidate. The firewall governs
what may reach patient-facing material; its stated admission criterion is direct EMC clinical
evidence at tier T3 after clinician review, and the conformance of the existing imatinib registry
listing with that criterion is unresolved (sections 4 and 5)."""))

# 5 - Section 4, Tranche 1
EDITS.append((
"""*Tranche 1, biomarker-matched and near-term.* Imatinib in the *KIT*-mutant subset is the only
candidate at T3, resting on direct EMC clinical evidence: a *KIT* exon-11-mutant patient with 3
years of disease stabilisation [7]. It is approved, well characterised and biomarker-defined. The""",
"""*Tranche 1, biomarker-matched and near-term.* Imatinib in the *KIT*-mutant subset is the only
candidate resting on any direct EMC clinical evidence, and is graded T2: that evidence is a
case-level signal in EMC, one published *KIT* exon-11-mutant patient with 3 years of disease
stabilisation [7]. The assembled record supplies a case-level signal and does not establish the
prospective or substantial EMC clinical evidence that this paper's definitions require for T3. It
is approved, well characterised and biomarker-defined. The"""))

EDITS.append((
"""attributed to the same case report [7], which the entry itself describes as a single case. What
remains open is the clinical route set out above, not admission to the registry.""",
"""attributed to the same case report [7], which the entry itself describes as a single case. Under
the T2 grade adopted here, that existing listing falls below the firewall's stated admission
criterion of tier T3 after clinician review (sections 2.6 and 5). We disclose this mismatch and do
not resolve it: the criterion is unchanged, the registry entry is unchanged here, no clinician
review or authorised exception is asserted, and registry conformance is unresolved. What remains
open is the clinical route set out above, together with that registry-conformance question; what is
not open is admission, because the entry already exists."""))

# 6 - Section 5 first limitation
EDITS.append((
"""First, most candidates are supported by preclinical, in-vitro or model-screen data rather than by
EMC clinical evidence, only imatinib reaching T3, and the dominant rationale is lineage and fusion
biology because the EMC genome is recurrently quiet. Target-level plausibility does not guarantee
clinical activity.""",
"""First, most candidates are supported by preclinical, in-vitro or model-screen data rather than by
EMC clinical evidence. No candidate reaches T3; the strongest EMC clinical evidence in the menu is
the single case report supporting imatinib, which is graded T2. The dominant rationale is lineage
and fusion biology because the EMC genome is recurrently quiet. Target-level plausibility does not
guarantee clinical activity."""))

# 7 - Section 5 ethics firewall
EDITS.append((
"""We address this structurally. A firewall keeps
hypotheses graded T0 to T2 out of all patient-facing material; only a candidate reaching direct EMC
clinical evidence at T3 may migrate into the project's cited clinical registry, and then only after
clinician review. Any clinical step,""",
"""We address this structurally. The firewall's stated
admission criterion is unchanged and is not relaxed here: hypotheses graded T0 to T2 are kept out of
all patient-facing material; only a candidate reaching direct EMC clinical evidence at T3 may
migrate into the project's cited clinical registry, and then only after clinician review. We state
this as the intended criterion and do not claim that it is currently enforced in full. Under the T2
grade adopted here for imatinib (sections 2.2 and 4), the existing imatinib entry in the project's
cited clinical registry falls below that criterion. We disclose the mismatch rather than resolve it:
no clinician review, authorised exception or prospective-only scope is asserted for that entry, the
registry is not altered by this paper, and the conformance of the registry with the stated criterion
is unresolved and remains for the responsible clinical review to settle. Any clinical step,"""))

for i, (old, new) in enumerate(EDITS, 1):
    if s.count(old) != 1:
        sys.exit("EDIT %d matched %d times" % (i, s.count(old)))
    s = s.replace(old, new)

open(p, "w", encoding="utf-8").write(s)
print("edits applied:", len(EDITS))
print("baseline lines:", orig.count("\n"), "candidate lines:", s.count("\n"))
