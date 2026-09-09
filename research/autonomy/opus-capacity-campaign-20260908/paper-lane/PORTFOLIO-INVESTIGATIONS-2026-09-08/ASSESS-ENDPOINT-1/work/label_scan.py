import re,ast
src=open("/home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/ASSESS-ENDPOINT-1/work/rederive_claims.py").read()
tree=ast.parse(src)
COMPUTE=(ast.Call,ast.BinOp,ast.ListComp,ast.GeneratorExp,ast.Compare,ast.UnaryOp,ast.IfExp)
def is_pure_lookup(n):
    """True if the expression is only subscripts/attributes/names/constants -- i.e. a read-back."""
    for sub in ast.walk(n):
        if isinstance(sub, COMPUTE): return False
    return True
suspect=[]; ok=0
for node in ast.walk(tree):
    if isinstance(node,ast.Call) and getattr(node.func,'id',None)=='rec' and len(node.args)>=7:
        rid=node.args[0].value if isinstance(node.args[0],ast.Constant) else '?'
        derived=node.args[6]; level=node.args[7].value if len(node.args)>7 and isinstance(node.args[7],ast.Constant) else '?'
        if level!='RECOMPUTED': continue
        # a list of pure lookups is still a read-back
        parts=derived.elts if isinstance(derived,(ast.List,ast.Tuple)) else [derived]
        if all(is_pure_lookup(p) for p in parts):
            suspect.append((rid, ast.unparse(derived)[:150]))
        else: ok+=1
print("rows labelled RECOMPUTED whose derived expression contains NO computation (pure key lookup):")
for r,e in suspect: print("  SUSPECT", r, "::", e)
print()
print("RECOMPUTED rows with genuine computation:", ok, " suspect:", len(suspect))
