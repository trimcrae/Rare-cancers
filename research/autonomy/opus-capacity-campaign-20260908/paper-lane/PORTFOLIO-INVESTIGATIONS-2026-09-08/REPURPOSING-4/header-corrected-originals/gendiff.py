import difflib,sys
a,b,path,out=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
A=open(a).readlines(); B=open(b).readlines()
d=list(difflib.unified_diff(A,B,fromfile="a/"+path,tofile="b/"+path,n=3))
open(out,'w').writelines(d)
print(out,"hunks:",sum(1 for l in d if l.startswith("@@")))
