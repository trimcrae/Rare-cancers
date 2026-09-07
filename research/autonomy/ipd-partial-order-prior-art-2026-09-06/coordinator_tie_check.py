"""Recompute the tie example; it does not contradict the published no-ties theorem."""
import json
from fractions import Fraction as F
from pathlib import Path


def main():
    packet=json.loads((Path(__file__).parent/'coordinator-tie-extension-check.json').read_text())
    qs={}
    for item in packet['checks']:
        a=[(F(t),e) for t,e in item['a']];b=[(F(t),e) for t,e in item['b']]
        u=v=F(0)
        for t in sorted({x for x,e in a+b if e}):
            ya,yb=[sum(x>=t for x,e in rows) for rows in (a,b)]
            da,db=[sum(x==t and e for x,e in rows) for rows in (a,b)]
            y,d=ya+yb,da+db
            u+=da-F(d*ya,y)
            if y>1:v+=F(ya*yb*d*(y-d),y*y*(y-1))
        q=u*u/v
        assert (str(u),str(v),str(q))==(item['u_group_a'],item['variance'],item['q'])
        qs[item['case']]=q
    assert qs['tied']==2 and qs['untied']==F(25,17)
    print(json.dumps({'verified':True,'tied_q':str(qs['tied']),'untied_q':str(qs['untied']),
                      'interpretation':'No-ties extrema cannot automatically cover these true ties; no claim of a counterexample to the no-ties theorem.'}))


if __name__=='__main__':main()
