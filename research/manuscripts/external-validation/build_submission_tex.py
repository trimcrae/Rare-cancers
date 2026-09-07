"""Render the canonical comment as editable LaTeX without rewriting its content.

Compile the resulting source with standard LaTeX packages, for example Tectonic 0.17.0.
The explicit mapping preserves the manuscript's six algebra expressions; unknown code
math raises KeyError rather than being silently dropped. No publisher sources are embedded.
"""
from pathlib import Path
import argparse, re

def esc(s):
 return ''.join({'&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}','\\':r'\textbackslash{}'}.get(c,c) for c in s)
MATH={'z_C(x_i) = (x_i - mean_C(x)) / s_C(x)':r'z_C(x_i) = \frac{x_i-\operatorname{mean}_C(x)}{s_C(x)}','a*x_i + b':r'a x_i + b','a > 0':r'a > 0','a*mean_C(x) + b':r'a\operatorname{mean}_C(x)+b','a*s_C(x)':r'a s_C(x)','z_C(a*x_i + b) = z_C(x_i)':r'z_C(a x_i+b)=z_C(x_i)'}
def inline(s):
 pattern=r'(`[^`]+`|\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|\*[^*]+\*)'
 out=[]
 for t in re.split(pattern,s):
  if t.startswith('`'): out.append(r'\('+MATH[t[1:-1]]+r'\)')
  elif re.fullmatch(r'\[[^\]]+\]\([^)]+\)',t):
   label,url=re.fullmatch(r'\[([^\]]+)\]\(([^)]+)\)',t).groups(); out.append(r'\href{'+url+'}{'+esc(label)+'}')
  elif t.startswith('**'): out.append(r'\textbf{'+esc(t[2:-2])+'}')
  elif t.startswith('*'): out.append(r'\emph{'+esc(t[1:-1])+'}')
  else: out.append(esc(t))
 return ''.join(out)
def convert(src):
 body=re.sub(r'\A---\r?\n.*?\r?\n---\r?\n','',src,flags=re.S).strip()
 chunks=re.split(r'\n\s*\n',body); out=[]; refs=False
 for chunk in chunks:
  c=' '.join(chunk.splitlines())
  if c.startswith('# '): out.append(r'{\LARGE\bfseries '+inline(c[2:])+r'\par}\vspace{1em}')
  elif c.startswith('## '):
   out.append(r'\section*{'+esc(c[3:])+'}')
   refs=c=='## References'
  elif re.fullmatch(r'`[^`]+`\.',c): out.append(r'\['+MATH[c[1:-2]]+r'.\]')
  elif refs:
   for line in chunk.splitlines():
    m=re.fullmatch(r'(\d+)\. (.*)',line); assert m,line
    out.append(r'\noindent\hangindent=1.5em\hangafter=1 '+m[1]+'. '+inline(m[2])+r'\par\smallskip')
  else: out.append(inline(c)+r'\par')
 return r'''\documentclass[11pt]{article}
\usepackage[a4paper,margin=25mm]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath}
\usepackage{microtype}
\usepackage[colorlinks=true,urlcolor=blue,linkcolor=blue]{hyperref}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.65em}
\setlength{\emergencystretch}{3em}
\begin{document}
'''+ '\n\n'.join(out)+'\n\\end{document}\n'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    default=Path(__file__).with_name('emc-external-validation-comment.md')
    parser.add_argument('--input',type=Path,default=default)
    parser.add_argument('--output',type=Path,default=default.with_suffix('.tex'))
    args=parser.parse_args()
    source=args.input.read_text(encoding='utf-8-sig')
    args.output.write_text(convert(source),encoding='utf-8',newline='\n')
    print(str(args.output))

if __name__=='__main__':
    main()
