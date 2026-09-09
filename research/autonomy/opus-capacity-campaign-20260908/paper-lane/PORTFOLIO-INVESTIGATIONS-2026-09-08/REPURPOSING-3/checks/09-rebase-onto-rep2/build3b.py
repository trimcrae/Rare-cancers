import sys
SRC="/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/rep3/reb/AFTER_R.md"
t=open(SRC,encoding="utf-8").read(); n=0
def sub(old,new,label):
    global t,n
    c=t.count(old)
    if c!=1: print("FAIL %s matched %d"%(label,c)); sys.exit(3)
    t=t.replace(old,new); n+=1; print("ok  %s"%label)

# Z1: section 3.3 -- parent-histology clinical exposure of the motivating agent
sub("""and nothing here asserts efficacy for pioglitazone, zaltoprofen or any thiazolidinedione in EMC.
""",
"""and nothing here asserts efficacy for pioglitazone, zaltoprofen or any thiazolidinedione in EMC.
One further record bounds the novelty of this axis in the parent histology, in the same way that
reference [9] does for histone deacetylase. The group that ran the EMC animal experiment had
earlier reported a single patient with a grade 2 cervical chondrosarcoma who was treated with
zaltoprofen and was free from disease progression for more than two years, with enhanced PPARγ and
reduced MMP2 expression on post-treatment histopathology [23]. That patient did not have EMC, the
report is an uncontrolled single case within a laboratory paper, and no efficacy, safety or
therapeutic-window conclusion is drawn from it in either histology. It means only that zaltoprofen,
the agent that motivates this arm, has been given to a chondrosarcoma patient and is therefore not
clinically untried in the parent histology, while remaining untried in EMC.
""","Z1 sec3.3 zaltoprofen parent-histology exposure")

# Z2: Table 2 novelty column for the zaltoprofen/pioglitazone row
sub("""the in-vitro half of that result used a line whose EMC identity the curated record does not support (section 3.3) | Yes |""",
"""the in-vitro half of that result used a line whose EMC identity the curated record does not support (section 3.3) | Yes for EMC; zaltoprofen itself is not clinically untried in the parent histology [23] |""","Z2 Table 2 novelty column")

# Z3: section 4 tranche table, "why it qualifies as untried"
sub("""| PPARγ agonism with pioglitazone, motivated by zaltoprofen | not a deliberate trial in EMC, but not untried either: one EMC patient took it for diabetes [5]; targets EMC lineage""",
"""| PPARγ agonism with pioglitazone, motivated by zaltoprofen | not a deliberate trial in EMC, but not untried either: one EMC patient took it for diabetes [5], and zaltoprofen itself has been given to one chondrosarcoma patient [23]; targets EMC lineage""","Z3 tranche table untried column")

# Z4: reference list
sub("""22. Boklan J, Langevin AM, Bielamowicz K, Neville K, Trippett T, Brown V, et al. A Phase I Study of Carfilzomib with Cyclophosphamide and Etoposide in Relapsed and Refractory Leukemia and Solid Tumors. *Cancers (Basel).* 2025;17(17):2924. doi 10.3390/cancers17172924. PMID 40941020. PMC12428389.
""",
"""22. Boklan J, Langevin AM, Bielamowicz K, Neville K, Trippett T, Brown V, et al. A Phase I Study of Carfilzomib with Cyclophosphamide and Etoposide in Relapsed and Refractory Leukemia and Solid Tumors. *Cancers (Basel).* 2025;17(17):2924. doi 10.3390/cancers17172924. PMID 40941020. PMC12428389.
23. Higuchi T, Takeuchi A, Munesue S, Yamamoto N, Hayashi K, Kimura H, et al. Anti-tumor effects of a nonsteroidal anti-inflammatory drug zaltoprofen on chondrosarcoma via activating peroxisome proliferator-activated receptor gamma and suppressing matrix metalloproteinase-2 expression. *Cancer Med.* 2018;7(5):1944-1954. doi 10.1002/cam4.1438. PMID 29573200. PMC5943440.
""","Z4 reference list adds [23]")

open("/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/rep3/reb/AFTER_R2.md","w",encoding="utf-8").write(t)
print("all %d anchors matched exactly once"%n)
