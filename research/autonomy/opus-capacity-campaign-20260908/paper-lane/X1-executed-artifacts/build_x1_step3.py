#!/usr/bin/env python3
"""X1 step 3 - supplementary section (S1, S2, S3) and editorial counts."""
import pathlib, re
L = pathlib.Path("/tmp/claude-0/x1-lane")
F = L / "PROPOSED-X1-emc-atr-collaborator-package.md"
t = F.read_text(); edits = []
def rep(tag, old, new, count=1):
    global t
    n = t.count(old); assert n == count, f"{tag}: found {n}"
    t = t.replace(old, new); edits.append(tag)

moved = (L / "MOVED-TABLES-SOURCE-BLOCKS.md").read_text()
tbl2 = moved[moved.index("**Table 2.**"):moved.index("**Table 7.**")].rstrip()
tbl7 = moved[moved.index("**Table 7.**"):].rstrip()
tbl2 = tbl2.replace("**Table 2.** Reference gene models", "**Supplementary Table S1.** Reference gene models", 1)
tbl7 = tbl7.replace("**Table 7.** Wild-type controls", "**Supplementary Table S2.** Wild-type controls", 1)

s3 = (L / "INPUTS/W1/PROPOSED-supplementary-table-s3.md").read_text()
s3_body = s3[s3.index("| Field |"):s3.index("## Limits, copied verbatim")].rstrip()

SUPP = f"""
---

## 9. Supplementary tables

Three supplementary tables are proposed. S1 and S2 carry content moved from the main text without
change. S3 is new to this revision and is assembled from one committed artifact; it introduces no
construct that the artifact does not already hold.

{tbl2}

{tbl7}

**Supplementary Table S3.** Per-junction assembly coordinates for each reported junction with a
sourced transcript-level breakpoint. Every cell is a verbatim copy of a recorded leaf of
[`emc-fet-construct-designs.json`](../../modalities/emc-fet-construct-designs.json)
(sha256 `726aae02ae38b41c34d4398363e3581cfc9e4602d0fe9d65906a4fba79c2048b`), a fixed column label,
or `UNRESOLVED`. No value in this table was derived, inferred, rounded or interpolated, and no new
construct is proposed by it.

{s3_body}

Genomic breakpoint coordinates are `UNRESOLVED` for all four junctions because the input carries
transcript and cDNA coordinates only; they are not back-derived from exon ranks. FUS::NR4A3 and
TCF12::NR4A3 appear in no column because the input records no transcript-level junction for either
— TCF12 is reported at genomic resolution only, in intron 5, and TCF12 has several alternatively
spliced isoforms. That is a limit of the sourcing and not evidence about the fusions.
"""
rep("S3a-supplementary", "\n\n## 8. References\n", SUPP + "\n\n## 8. References\n")
# move the supplementary section after the references for reading order
sup_i = t.index("\n---\n\n## 9. Supplementary tables")
sup_j = t.index("\n\n## 8. References\n")
sup = t[sup_i:sup_j]
t = t[:sup_i] + t[sup_j:].rstrip() + "\n" + sup.rstrip() + "\n"
edits.append("S3b-supplementary-after-references")

rep("S3c-display-counts",
    """built to the tighter of those: the abstract is 227 words as a single paragraph; the main text
(sections 1-7, excluding abstract, tables, references and appendix) is 2,722 words, or 3,467 words
with the seven tables counted in; and there are 7 display items and 8 references. Confirm the real
limits before submission and cut section 5 first if a shorter type is chosen. These counts drift
whenever the text is edited and were measured rather than remembered.""",
    """built to the tighter of those. THE COUNTS BELOW WERE MEASURED ON THIS REVISION AND MUST BE
RE-MEASURED AFTER ANY FURTHER EDIT. This revision carries FIVE numbered tables in the main text
(Tables 1 to 5) and ONE figure, so SIX main-text display items, plus THREE supplementary tables
(S1, S2, S3) and 10 references. The count is five main tables because Table 2 (gene models) and
Table 7 (wild-type controls) of the input moved to S1 and S2; it is not the "six tables" an earlier
plan recorded, and the actual count was taken rather than the planned one. Confirm the real limits
before submission and cut section 5 first if a shorter type is chosen.""")

rep("S3d-title-editorial",
    """TITLE. The frontmatter `title` now matches the H1. systems_check.py reads that field back out of
this file to render systems/views/L3-publications.md, so the committed view is stale until someone
runs `python3 systems/systems_check.py --write-views`. That regeneration is required in any case:
three sibling manuscripts were retitled in the same window and the view is stale on their rows too.""",
    """TITLE. PROPOSED, NOT APPLIED ANYWHERE ELSE. The frontmatter `title` matches the H1 in this file
only. No shared file, view or graph field has been changed to match it, and no view has been
regenerated. The dependent references that would need updating if this title is adopted are listed
in X1-COVER-LETTER-AND-TITLE-PROPOSALS.md in this lane; regenerating
systems/views/L3-publications.md is the coordinator's step, not this revision's.""")

F.write_text(t)
words = len(re.findall(r"\b[\w'-]+\b", t))
print("STEP3 EDITS:", len(edits)); [print("  ", e) for e in edits]
print("tables in main text:", re.findall(r"\*\*Table (\d)\.\*\*", t))
print("supp tables:", re.findall(r"\*\*Supplementary Table (S\d)\.\*\*", t))
print("figures:", re.findall(r"\*\*Figure (\d)\.\*\*", t))
print("total words in file:", words)
