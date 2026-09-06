"""Bounded exact check before reusing a published signed-Z switch rule."""
import itertools
import json
import time
from fractions import Fraction as F
from pathlib import Path


def score(word):
    a=sum(v<2 for v in word);b=len(word)-a;u=v=F(0)
    for item in word:
        if item%2==0:
            # Group 1 is item 2/3, matching O in the inspected theorem.
            u+=F(item>=2)-F(b,a+b)
            if a+b>1:v+=F(a*b,(a+b)**2)
        if item<2:a-=1
        else:b-=1
    return u,v


def leq_z(before,after):
    u,v=before;w,z=after
    assert v>0 and z>0
    if u<=0<=w:return True
    if w<0<u:return False
    if u>=0 and w>=0:return u*u*z<=w*w*v
    return u*u*z>=w*w*v


def main():
    start=time.monotonic();comparisons=0;words=0;finding=None
    for n in range(4,9):
        if finding:break
        for word in itertools.product(range(4),repeat=n):
            if sum(x<2 for x in word)<2 or sum(x>=2 for x in word)<2:continue
            words+=1;before=score(word)
            if not before[1]:continue
            for i in range(n-1):
                if not (word[i]<2<=word[i+1]):continue
                swapped=word[:i]+(word[i+1],word[i])+word[i+2:];after=score(swapped)
                if not after[1]:continue
                comparisons+=1
                if not leq_z(before,after):
                    finding=dict(n=n,before=word,after=swapped,adjacent_index=i,
                                 before_u=str(before[0]),before_v=str(before[1]),
                                 after_u=str(after[0]),after_v=str(after[1]),
                                 before_q=str(before[0]**2/before[1]),after_q=str(after[0]**2/after[1]))
                    break
            if finding:break
    out=dict(definition={'0':'G0 event','1':'G0 censor','2':'G1 event','3':'G1 censor'},
             rule='At rho=0 and no ties, swapping adjacent G0 then G1 observations should not decrease signed Z for group1.',
             design='Deterministic exhaustive words n4 through n8, at least2 records per group; skip zero variance; stop at first counterexample. No frequency claim.',
             words_checked=words,positive_variance_switches_checked=comparisons,counterexample=finding,
             elapsed_seconds=time.monotonic()-start)
    Path('.cache/logrank-switch-check.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(out))


if __name__=='__main__':main()
