import io
p='research/manuscripts/repurposing/repurposing-hypotheses.md'
s=open(p,encoding='utf-8').read()
lines=s.split('\n')  # 0-based

# --- extract note verbatim: 1-based 655..672 -> idx 654..671
note='\n'.join(lines[654:672])
assert note.startswith('*Reference completion note.* Author lists'), note[:60]
assert note.endswith('are standard.'), note[-40:]
assert lines[653]=='' and lines[672]=='' and lines[673]=='---', (lines[653],lines[672],lines[673])
assert '-->' not in note and '--' not in note

# --- 1. remove note (idx 654..672 inclusive: note + one trailing blank)
del lines[654:673]

# --- 2. editorial comment first line (idx 31)
assert lines[31]=='<!-- EDITORIAL, NOT FOR SUBMISSION.'
lines[31]=('<!-- EDITORIAL, NOT FOR SUBMISSION. STRIPPED AT SUBMISSION: two things are removed from the\n'
 'submitted manuscript, this editorial comment and Appendix A. Both are retained in the repository\n'
 'copy because this repository keeps one file per deliverable.')

# --- 3. move note into the editorial comment, before its closing -->
assert lines[63]=='read here. -->'
lines[63]=('read here.\n\n'
 'REFERENCE COMPLETION NOTE, relocated here from the body of the manuscript (review response item\n'
 '24). It is editor-facing and states that the reference list is not submission-ready, which is a\n'
 'repository fact rather than a claim a published paper should carry. Verbatim:\n\n'
 + note + '\n-->')

s2='\n'.join(lines)

# --- 4. Appendix A banner
h='## Appendix A. Superseded and corrected values\n'
assert s2.count(h)==1
banner=(h+'\n'
 '> *Stripped at submission.* Appendix A is removed from the submitted manuscript, together with\n'
 '> the editorial HTML comment at the head of this file. Both are retained in the repository copy\n'
 '> because this repository keeps one file per deliverable.\n')
s2=s2.replace(h,banner)
open(p,'w',encoding='utf-8').write(s2)
print('ok')
