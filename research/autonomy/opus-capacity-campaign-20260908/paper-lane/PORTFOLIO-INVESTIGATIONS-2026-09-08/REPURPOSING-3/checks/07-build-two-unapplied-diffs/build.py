import sys, io
SRC="/home/user/Rare-cancers/research/manuscripts/repurposing/repurposing-hypotheses.md"
t=open(SRC,encoding="utf-8").read()
n=0
def sub(old,new,label):
    global t,n
    c=t.count(old)
    if c!=1:
        print("FAIL anchor %s matched %d times (expected 1)"%(label,c)); sys.exit(3)
    t=t.replace(old,new); n+=1
    print("ok  %s"%label)

# --- E1: [2] chemotherapy / disease-specific survival, section 1.1 ---
sub("""retrieved for this manuscript. Clinical
next-generation sequencing""",
"""retrieved for this manuscript. A second cited series bears on the same point from a different
direction: among 58 EMCs confirmed by fluorescence in situ hybridization, the administration of
chemotherapy was one of the factors that portended shorter univariate disease-specific survival,
and it did not remain prognostically independent alongside size greater than 10 cm and metastasis
at presentation [2]. That series names no regimen and reports no response assessment, and an
association of this shape is confounded by indication, because chemotherapy is given to the
patients whose disease is already behaving worse. It is recorded here as a further absence of
established systemic benefit, and not as evidence of harm. Clinical
next-generation sequencing""","E1 sec1.1 chemotherapy/DSS from [2]")

# --- E2: the two CD117 figures are not measured to the same threshold ---
sub("""53% in one series and approximately 84% of 31 cases in another [2,8]. That distinction matters""",
"""53% in one series and approximately 84% of 31 cases in another [2,8]. Those two figures are not
measured to the same threshold and should not be read as a single range: the first counts
moderate-to-strong immunoreactivity among 48 assessed cases [2], the second counts positivity that
its authors define as focal or diffuse [8]. That distinction matters""","E2 sec1.1 CD117 threshold mismatch")

# --- E3a: Table 2 CDK4 row, positivity threshold ---
sub("""Genomic and immunohistochemical: CDK4 positive in 100% of a 31-case series, with *CDKN2A*/*CDKN2B* loss, and no functional test [8,5]""",
"""Genomic and immunohistochemical: CDK4 positive, at a threshold its authors define as focal or diffuse staining, in 100% of a 31-case series, with *CDKN2A*/*CDKN2B* loss, and no functional test [8,5]""","E3a Table 2 CDK4 threshold")

# --- E3b: section 4 tranche table, same figure ---
sub("""CDK4 positive in 100% of a 31-case series with *CDKN2A*/*CDKN2B* loss [8,5], which is expression and genomic rather than functional""",
"""CDK4 positive, at a focal-or-diffuse staining threshold, in 100% of a 31-case series with *CDKN2A*/*CDKN2B* loss [8,5], which is expression and genomic rather than functional""","E3b tranche table CDK4 threshold")

# --- E4: section 3.3, why [12] is unread ---
sub("""*EWSR1* fusion. That paper is not open access and its full text has not been retrieved here, so
whether the mouse experiment used the same line is unknown and cannot be stated in either
direction.""",
"""*EWSR1* fusion. That paper has a PubMed Central record, PMC10054153, but the record returns an
abstract and no machine-readable body, so its full text has not been retrieved here. The abstract
names H-EMC-SS for the in-vitro work only and calls the animal work "a mouse model of extraskeletal
myxoid chondrosarcoma" without naming a line, so whether the mouse experiment used the same line is
unknown and cannot be stated in either direction.""","E4 sec3.3 [12] retrieval status")

# --- E5: Appendix A row, same correction ---
sub("""Whether the mouse experiment used the same line is **unread**, because the paper is not open access and its full text has not been retrieved here""",
"""Whether the mouse experiment used the same line is **unread**, because the paper's PubMed Central record (PMC10054153) returns an abstract but no machine-readable body, so its full text has not been retrieved here; its abstract names H-EMC-SS for the in-vitro work only and names no line for the animal work""","E5 Appendix A [12] retrieval status")

# --- E6: editor-facing reference-completion note, retrieval provenance for the five ---
sub("""([`carfilzomib-class-clinical-2026-08-28.json`](../../literature/carfilzomib-class-clinical-2026-08-28.json)). The
full text of reference 16 was retrieved and read.""",
"""([`carfilzomib-class-clinical-2026-08-28.json`](../../literature/carfilzomib-class-clinical-2026-08-28.json)).
References 2, 8, 9, 12 and 14 are also abstract-level only, as checked against PubMed on 2026-09-09:
references 2, 8, 9 and 14 have no PubMed Central record at all, by both the identifier converter and
the PubMed-to-PMC link database, and reference 12's record, PMC10054153, returns an abstract and an
empty body. Every statement attributed to any of those five above is taken from its PubMed abstract,
and their methods, results, tables and figures are unread rather than absent. The
full text of reference 16 was retrieved and read.""","E6 reference-completion note provenance")

open("/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/rep3/AFTER.md","w",encoding="utf-8").write(t)
print("all %d anchors matched exactly once"%n)
